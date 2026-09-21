"""Shared structural extraction primitives for Word documents."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable

from docx.oxml.ns import qn


@dataclass(frozen=True)
class DocxUnit:
    """One visible, ordered unit emitted by the shared DOCX walker."""

    text: str
    heading_path: tuple[str, ...] = ()
    paragraph_index: int | None = None
    table_coordinates: tuple[int, ...] | None = None
    field_name: str | None = None
    field_value: str | None = None
    location: str = ""
    kind: str = "paragraph"
    reader_group: str | None = None


_STRUCTURED_FIELDS = {
    "operation id": "Operation ID",
    "financing instrument": "Financing Instrument",
    "environmental and social risk classification": (
        "Environmental and Social Risk Classification"
    ),
}
_BRACKET_OPTION = re.compile(r"\[\s*(?P<checked>[xX]?)\s*\]")
_OPTION_BOUNDARY = re.compile(r"[;|,\n]")


def _ancestor_sdt_is_unchecked(element: Any) -> bool:
    current = element
    while current is not None:
        if current.tag == qn("w:sdt"):
            checked = current.find(
                ".//" + qn("w14:checkbox") + "/" + qn("w14:checked")
            )
            if checked is not None:
                value = (
                    checked.get(qn("w14:val"))
                    or checked.get(qn("w:val"))
                    or checked.get("val")
                    or "0"
                )
                if str(value).strip().casefold() in {"0", "false", "off", "no"}:
                    return True
        current = current.getparent()
    return False


def _heading_level(paragraph: Any) -> int | None:
    style = paragraph.find("./" + qn("w:pPr") + "/" + qn("w:pStyle"))
    if style is None:
        return None
    value = style.get(qn("w:val")) or ""
    match = re.fullmatch(r"Heading\s*([1-9])", value, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _canonical_field(value: str) -> str:
    key = re.sub(r"\s+", " ", value).strip().rstrip(":").casefold()
    return _STRUCTURED_FIELDS.get(key, "")


def _children(element: Any, tag: str) -> Iterable[Any]:
    """Yield direct or SDT-wrapped children of the requested XML type."""
    expected = qn(tag)

    def visit(container: Any) -> Iterable[Any]:
        for child in container:
            if child.tag == expected:
                yield child
            elif child.tag == qn("w:sdt"):
                content = child.find(qn("w:sdtContent"))
                if content is not None:
                    yield from visit(content)

    return visit(element)


def _strip_unchecked_bracket_options(text: str) -> str:
    """Remove unchecked bracket options without dropping surrounding prose."""
    matches = list(_BRACKET_OPTION.finditer(text))
    if not matches:
        return text
    pieces: list[str] = []
    cursor = 0
    for index, match in enumerate(matches):
        if match.group("checked"):
            continue
        next_option = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )
        boundary = _OPTION_BOUNDARY.search(text, match.end(), next_option)
        end = boundary.start() if boundary is not None else next_option
        pieces.append(text[cursor:match.start()])
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces)


def _visible_paragraph_text(paragraph: Any) -> str:
    if _ancestor_sdt_is_unchecked(paragraph):
        return ""
    pieces: list[str] = []
    for node in paragraph.iter():
        if node.tag == qn("w:del"):
            continue
        if node.tag != qn("w:r") or _ancestor_sdt_is_unchecked(node):
            continue
        if any(parent.tag == qn("w:del") for parent in node.iterancestors()):
            continue
        properties = node.find(qn("w:rPr"))
        if properties is not None and properties.find(qn("w:vanish")) is not None:
            continue
        for descendant in node.iter():
            if descendant.tag == qn("w:instrText"):
                continue
            if descendant.tag == qn("w:t") and descendant.text:
                pieces.append(descendant.text)
            elif descendant.tag == qn("w:tab"):
                pieces.append("\t")
            elif descendant.tag in {qn("w:br"), qn("w:cr")}:
                pieces.append("\n")
    text = _strip_unchecked_bracket_options("".join(pieces))
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\s*\n\s*", "\n", text).strip()


def _ordered_cell_text(cell: Any) -> str:
    """Return visible direct cell paragraphs, excluding nested tables."""
    parts: list[str] = []

    def visit(container: Any) -> None:
        for child in container:
            if child.tag == qn("w:p"):
                text = _visible_paragraph_text(child)
                if text:
                    parts.append(text)
            elif child.tag == qn("w:sdt"):
                if _ancestor_sdt_is_unchecked(child):
                    continue
                content = child.find(qn("w:sdtContent"))
                if content is not None:
                    visit(content)

    visit(cell)
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def extract_docx_units(document: Any) -> list[DocxUnit]:
    """Walk visible Word content in XML order without duplicating nested tables."""
    units: list[DocxUnit] = []
    headings: list[str] = []
    paragraph_index = 0
    table_index = 0

    def table_location(table_id: int, coordinates: tuple[int, ...], suffix: str) -> str:
        path = ":".join(str(item) for item in (table_id,) + coordinates)
        return f"t:{path}:{suffix}"

    def emit_paragraph(
        paragraph: Any,
        *,
        coordinates: tuple[int, ...] | None = None,
        table_id: int | None = None,
        reader_group: str | None = None,
    ) -> None:
        nonlocal paragraph_index, headings
        text = _visible_paragraph_text(paragraph)
        if not text:
            return
        level = _heading_level(paragraph)
        if level is not None:
            headings = headings[: level - 1] + [text]
        if coordinates is None or table_id is None:
            location = f"p:{paragraph_index}"
            kind = "paragraph"
        else:
            location = table_location(table_id, coordinates, f"p:{paragraph_index}")
            kind = "table_cell"
        units.append(
            DocxUnit(
                text=text,
                heading_path=tuple(headings),
                paragraph_index=paragraph_index,
                table_coordinates=coordinates,
                location=location,
                kind=kind,
                reader_group=reader_group,
            )
        )
        paragraph_index += 1

    def walk_container(container: Any, *, coordinate_prefix: tuple[int, ...] = ()) -> None:
        for child in container:
            if child.tag == qn("w:p"):
                emit_paragraph(child)
            elif child.tag == qn("w:tbl"):
                walk_table(child, coordinate_prefix=coordinate_prefix)
            elif child.tag == qn("w:sdt"):
                if _ancestor_sdt_is_unchecked(child):
                    continue
                content = child.find(qn("w:sdtContent"))
                if content is not None:
                    walk_container(content, coordinate_prefix=coordinate_prefix)

    def walk_nested_tables(container: Any, *, coordinate_prefix: tuple[int, ...]) -> None:
        for child in container:
            if child.tag == qn("w:tbl"):
                walk_table(child, coordinate_prefix=coordinate_prefix)
            elif child.tag == qn("w:sdt"):
                if _ancestor_sdt_is_unchecked(child):
                    continue
                content = child.find(qn("w:sdtContent"))
                if content is not None:
                    walk_nested_tables(content, coordinate_prefix=coordinate_prefix)

    def walk_cell(
        container: Any,
        *,
        coordinates: tuple[int, ...],
        nested_prefix: tuple[int, ...],
        table_id: int,
        reader_group: str | None = None,
    ) -> None:
        for child in container:
            if child.tag == qn("w:p"):
                emit_paragraph(
                    child,
                    coordinates=coordinates,
                    table_id=table_id,
                    reader_group=reader_group,
                )
            elif child.tag == qn("w:tbl"):
                walk_table(child, coordinate_prefix=nested_prefix)
            elif child.tag == qn("w:sdt"):
                if _ancestor_sdt_is_unchecked(child):
                    continue
                content = child.find(qn("w:sdtContent"))
                if content is not None:
                    walk_cell(
                        content,
                        coordinates=coordinates,
                        nested_prefix=nested_prefix,
                        table_id=table_id,
                        reader_group=reader_group,
                    )

    def visible_paragraph_count(container: Any) -> int:
        count = 0

        def visit(node: Any) -> None:
            nonlocal count
            for child in node:
                if child.tag == qn("w:p"):
                    if _visible_paragraph_text(child):
                        count += 1
                elif child.tag == qn("w:sdt"):
                    if _ancestor_sdt_is_unchecked(child):
                        continue
                    content = child.find(qn("w:sdtContent"))
                    if content is not None:
                        visit(content)

        visit(container)
        return count

    def walk_table(table: Any, *, coordinate_prefix: tuple[int, ...] = ()) -> None:
        nonlocal table_index, paragraph_index
        current_table = table_index
        table_index += 1
        rows = list(_children(table, "w:tr"))
        consumed_value_rows: set[int] = set()
        for row_index, row in enumerate(rows):
            if row_index in consumed_value_rows:
                continue
            cells = list(_children(row, "w:tc"))
            direct_texts = [_ordered_cell_text(cell) for cell in cells]
            canonical_headers = [_canonical_field(text) for text in direct_texts]
            is_header_row = (
                len(canonical_headers) >= 2
                and all(canonical_headers)
                and row_index + 1 < len(rows)
            )
            if is_header_row:
                value_cells = list(_children(rows[row_index + 1], "w:tc"))
                values = [_ordered_cell_text(cell) for cell in value_cells]
                usable_values = values[:len(canonical_headers)]
                if (
                    len(values) >= len(canonical_headers)
                    and all(not _canonical_field(value) for value in usable_values)
                ):
                    for column_index, (field_name, field_value) in enumerate(
                        zip(canonical_headers, values)
                    ):
                        header_cell = cells[column_index]
                        value_cell = value_cells[column_index]
                        field_index = paragraph_index
                        paragraph_index += (
                            visible_paragraph_count(header_cell)
                            + visible_paragraph_count(value_cell)
                        )
                        coordinates = coordinate_prefix + (row_index, column_index)
                        units.append(
                            DocxUnit(
                                text=(
                                    f"{field_name}: {field_value}"
                                    if field_value
                                    else field_name
                                ),
                                heading_path=tuple(headings),
                                paragraph_index=field_index,
                                table_coordinates=coordinates,
                                field_name=field_name,
                                field_value=field_value,
                                location=table_location(current_table, coordinates, "field"),
                                kind="structured_field",
                            )
                        )
                        for source_cell in (header_cell, value_cell):
                            walk_nested_tables(
                                source_cell,
                                coordinate_prefix=coordinate_prefix
                                + (current_table, row_index, column_index),
                            )
                    consumed_value_rows.add(row_index + 1)
                    continue

            same_row_pairs: dict[int, tuple[int, str, str]] = {}
            consumed_pair_cells: set[int] = set()
            for column_index in range(len(cells) - 1):
                if column_index in consumed_pair_cells:
                    continue
                if column_index > 0 and _canonical_field(direct_texts[column_index - 1]):
                    continue
                pair_field = _canonical_field(direct_texts[column_index])
                pair_value = direct_texts[column_index + 1]
                if pair_field and not _canonical_field(pair_value):
                    same_row_pairs[column_index] = (
                        column_index + 1,
                        pair_field,
                        pair_value,
                    )
                    consumed_pair_cells.update((column_index, column_index + 1))

            if same_row_pairs:
                for column_index, cell in enumerate(cells):
                    pair = same_row_pairs.get(column_index)
                    if pair is not None:
                        value_index, field_name, field_value = pair
                        coordinates = coordinate_prefix + (row_index, column_index)
                        field_index = paragraph_index
                        paragraph_index += (
                            visible_paragraph_count(cell)
                            + visible_paragraph_count(cells[value_index])
                        )
                        units.append(
                            DocxUnit(
                                text=(
                                    f"{field_name}: {field_value}"
                                    if field_value
                                    else field_name
                                ),
                                heading_path=tuple(headings),
                                paragraph_index=field_index,
                                table_coordinates=coordinates,
                                field_name=field_name,
                                field_value=field_value,
                                location=table_location(current_table, coordinates, "field"),
                                kind="structured_field",
                            )
                        )
                        for source_column in (column_index, value_index):
                            walk_nested_tables(
                                cells[source_column],
                                coordinate_prefix=coordinate_prefix
                                + (current_table, row_index, source_column),
                            )
                    elif column_index in consumed_pair_cells:
                        continue
                    else:
                        coordinates = coordinate_prefix + (row_index, column_index)
                        walk_cell(
                            cell,
                            coordinates=coordinates,
                            nested_prefix=coordinate_prefix
                            + (current_table, row_index, column_index),
                            table_id=current_table,
                            reader_group=table_location(
                                current_table, coordinate_prefix + (row_index,), "row"
                            ),
                        )
                continue

            for column_index, cell in enumerate(cells):
                coordinates = coordinate_prefix + (row_index, column_index)
                walk_cell(
                    cell,
                    coordinates=coordinates,
                    nested_prefix=coordinate_prefix
                    + (current_table, row_index, column_index),
                    table_id=current_table,
                    reader_group=table_location(
                        current_table, coordinate_prefix + (row_index,), "row"
                    ),
                )

    walk_container(document.element.body)
    return units


def reader_parts_from_units(units: Iterable[DocxUnit]) -> list[str]:
    """Return reader text from one shared walk while retaining legacy grouping."""
    parts: list[str] = []
    active_group: str | None = None
    active_cell: tuple[int, ...] | None = None
    active_cells: list[str] = []

    def flush() -> None:
        nonlocal active_group, active_cell, active_cells
        if active_cells:
            parts.append(" | ".join(active_cells))
        active_group = None
        active_cell = None
        active_cells = []

    for unit in units:
        if unit.reader_group is not None and unit.kind == "table_cell":
            if active_group != unit.reader_group:
                flush()
                active_group = unit.reader_group
            if active_cell == unit.table_coordinates and active_cells:
                active_cells[-1] += "\n" + unit.text
            else:
                active_cells.append(unit.text)
                active_cell = unit.table_coordinates
            continue
        flush()
        if unit.text:
            parts.append(unit.text)
    flush()
    return parts


def extract_docx_reader_parts(document: Any) -> list[str]:
    """Return reader text while retaining legacy row-cell grouping."""
    return reader_parts_from_units(extract_docx_units(document))