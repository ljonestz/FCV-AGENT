"""Runtime bridge from uploaded document parts to ``climate-verified-v2.1``.

Only project and package-instrument uploads can establish project facts.
Context uploads and the country bank cross the boundary as contextual evidence.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from sector_lenses.climate_analysis import ContextEvidenceRef
from sector_lenses.climate_context_adapter import adapt_grounding_evidence
from sector_lenses.climate_source_blocks import (
    DocumentApplicability,
    SourceBlock,
    SourceDocument,
    normalize_block_text,
)
from sector_lenses.climate_verified_pipeline import (
    PipelineClients,
    run_verified_climate_pipeline,
)
from sector_lenses.climate_verified_render import (
    build_reader_model,
    validate_reader_model,
)
from sector_lenses.pipeline import normalize_climate_assessment


DEFAULT_MAXIMUM_SOURCE_CHARS = 85_000
DEFAULT_MAXIMUM_CONTEXT_CHARS = 15_000
_BLOCK_CHARS = 1_800
_ALLOWED_LABELS = {"PROJECT DOCUMENT", "PACKAGE INSTRUMENT"}
_OPERATIONAL_TERMS = (
    "project operations manual",
    "operations manual",
    "escp",
    "esmf",
    "esrs",
    "results framework",
    "security risk management plan",
    "feasibility study",
    "procurement",
    "co-management",
    "indicator",
    "adaptive trigger",
    "site selection",
    "climate",
    "conflict",
    "fragility",
    "flood",
    "drought",
    "displacement",
    "cerc",
)


@dataclass(frozen=True)
class PreparedClimateSources:
    documents: tuple[SourceDocument, ...]
    blocks: tuple[SourceBlock, ...]
    warning_codes: tuple[str, ...]


def resolve_verified_document_context(
    prepared: PreparedClimateSources,
    *,
    doc_type: str,
    instrument_type: str,
) -> tuple[str, str]:
    """Resolve missing routing context from explicit primary-source markers."""

    resolved_document = str(doc_type or "Unknown").strip() or "Unknown"
    resolved_instrument = (
        str(instrument_type or "Unknown").strip() or "Unknown"
    )
    primary_ids = {
        item.document_id
        for item in prepared.documents
        if item.relationship == "primary"
    }
    filenames = " ".join(
        item.filename
        for item in prepared.documents
        if item.document_id in primary_ids
    ).casefold()
    source_text = " ".join(
        item.text
        for item in prepared.blocks
        if item.document_id in primary_ids
    ).casefold()

    if resolved_document.casefold() == "unknown":
        document_markers = (
            (r"\bproject concept note\b|\bpcn\b", "PCN"),
            (r"\bproject appraisal document\b|\bpad\b", "PAD"),
            (r"\bproject information document\b|\bpid\b", "PID"),
        )
        for pattern, value in document_markers:
            full_name_pattern = pattern.split("|")[0]
            if re.search(pattern, filenames) or re.search(
                full_name_pattern,
                source_text,
            ):
                resolved_document = value
                break

    if resolved_instrument.casefold() == "unknown":
        instrument_markers = (
            (r"\binvestment project financing\b|\bipf\b", "IPF"),
            (r"\bprogram(?:-| )for(?:-| )results\b|\bpforr\b|\bp4r\b", "PforR"),
            (r"\bdevelopment policy (?:financing|operation)\b|\bdpo\b", "DPO"),
        )
        for pattern, value in instrument_markers:
            if re.search(pattern, source_text):
                resolved_instrument = value
                break

    return resolved_document, resolved_instrument


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _chunks(text: str, size: int) -> list[str]:
    """Keep logical paragraphs intact while bounding over-large blocks."""

    result: list[str] = []
    paragraphs = re.split(r"\n\s*\n", text)
    for raw in paragraphs:
        value = normalize_block_text(raw)
        while value:
            if len(value) <= size:
                result.append(value)
                break
            window = value[: size + 1]
            sentence_cuts = [
                match.end()
                for match in re.finditer(r"[.!?](?=\s)", window)
            ]
            cut = sentence_cuts[-1] if sentence_cuts else 0
            if cut < max(80, size // 3):
                cut = value.rfind(" ", 0, size + 1)
            if cut < max(80, size // 3):
                cut = size
            result.append(value[:cut].strip())
            value = value[cut:].strip()
    return [item for item in result if item]


def _priority(block: SourceBlock) -> tuple[int, int]:
    lowered = block.text.casefold()
    score = sum(1 for term in _OPERATIONAL_TERMS if term in lowered)
    index = block.paragraph_index if block.paragraph_index is not None else 10**9
    return (-score, index)


def _bounded_blocks(
    blocks: list[SourceBlock],
    maximum_chars: int,
) -> tuple[tuple[SourceBlock, ...], bool]:
    if sum(len(item.text) for item in blocks) <= maximum_chars:
        return tuple(blocks), False

    selected: list[SourceBlock] = []
    remaining = maximum_chars
    for block in sorted(blocks, key=_priority):
        length = len(block.text)
        if length <= remaining:
            selected.append(block)
            remaining -= length
    selected_ids = {item.block_id for item in selected}
    ordered = tuple(item for item in blocks if item.block_id in selected_ids)
    return ordered, True


def prepare_verified_sources(
    doc_parts: object,
    *,
    maximum_chars: int = DEFAULT_MAXIMUM_SOURCE_CHARS,
) -> PreparedClimateSources:
    """Create stable, bounded project-fact sources from extracted uploads."""

    if maximum_chars < 1:
        raise ValueError("maximum_chars must be positive")
    documents: list[SourceDocument] = []
    blocks: list[SourceBlock] = []
    parts = doc_parts if isinstance(doc_parts, list) else []
    block_size = min(_BLOCK_CHARS, maximum_chars)
    primary_count = sum(
        1
        for item in parts
        if isinstance(item, dict)
        and str(item.get("label") or "").strip().upper() == "PROJECT DOCUMENT"
        and str(item.get("raw_text") or "").strip()
    )
    warnings: list[str] = []
    if primary_count > 1:
        warnings.append("PRIMARY_DOCUMENT_PRECEDENCE_UNRESOLVED")
    elif primary_count == 1:
        warnings.append("PRIMARY_APPLICABILITY_USER_DESIGNATED")

    for position, part in enumerate(parts):
        if not isinstance(part, dict):
            continue
        label = str(part.get("label") or "").strip().upper()
        if label not in _ALLOWED_LABELS:
            continue
        raw_text = str(part.get("raw_text") or "")
        if not raw_text.strip():
            continue
        filename = str(part.get("name") or f"upload-{position + 1}").strip()
        digest = _sha256(raw_text)
        identity = _sha256(f"{position}|{label}|{filename}|{digest}")[:16]
        document_id = f"DOC-{identity}"
        is_primary = label == "PROJECT DOCUMENT"
        controls_facts = is_primary and primary_count == 1
        document = SourceDocument(
            document_id=document_id,
            filename=filename,
            sha256=digest,
            applicability=(
                DocumentApplicability.PARTIAL
                if controls_facts
                else DocumentApplicability.UNRESOLVED
            ),
            relationship="primary" if is_primary else "package",
            version_status=(
                "user_designated" if controls_facts else "unresolved"
            ),
            operation_match=(
                "user_designated" if controls_facts else "unresolved"
            ),
            document_type=(
                "project_document_upload" if controls_facts else "unresolved"
            ),
        )
        documents.append(document)
        if not controls_facts:
            if not is_primary:
                warnings.append("PACKAGE_FACT_AUTHORITY_WITHHELD")
            continue
        for paragraph_index, text in enumerate(_chunks(raw_text, block_size)):
            normalized_hash = _sha256(
                f"{document_id}|p:{paragraph_index}|{text}"
            )
            blocks.append(SourceBlock(
                block_id=f"{document_id}-B-{normalized_hash[:12]}",
                document_id=document_id,
                text=text,
                normalized_hash=normalized_hash,
                heading_path=(),
                paragraph_index=paragraph_index,
            ))

    bounded, was_bounded = _bounded_blocks(blocks, maximum_chars)
    if was_bounded:
        warnings.append("SOURCE_BLOCKS_BOUNDED")
    return PreparedClimateSources(
        documents=tuple(documents),
        blocks=bounded,
        warning_codes=tuple(dict.fromkeys(warnings)),
    )


def _uploaded_context_evidence(
    doc_parts: object,
    *,
    maximum_chars: int = DEFAULT_MAXIMUM_CONTEXT_CHARS,
) -> tuple[ContextEvidenceRef, ...]:
    """Keep uploaded context useful without granting project-fact authority."""

    candidates: list[tuple[int, int, ContextEvidenceRef]] = []
    parts = doc_parts if isinstance(doc_parts, list) else []
    for position, part in enumerate(parts):
        if not isinstance(part, dict):
            continue
        if str(part.get("label") or "").strip().upper() != "CONTEXT DOCUMENT":
            continue
        raw_text = str(part.get("raw_text") or "")
        if not raw_text.strip():
            continue
        filename = str(part.get("name") or f"context-{position + 1}").strip()
        document_id = _sha256(f"{position}|{filename}|{_sha256(raw_text)}")[:16]
        for block_index, text in enumerate(_chunks(raw_text, _BLOCK_CHARS)):
            lowered = text.casefold()
            score = sum(1 for term in _OPERATIONAL_TERMS if term in lowered)
            block_id = _sha256(
                f"{document_id}|context:{block_index}|{text}"
            )[:16]
            candidates.append((
                -score,
                block_index,
                ContextEvidenceRef(
                    evidence_id=f"CE-UPLOAD-{block_id}",
                    evidence_class="country",
                    scope="unresolved",
                    statement=text,
                    source_ref=(
                        f"upload-context:{document_id}:{block_index}:{filename}"
                    ),
                    confidence="low",
                    source_kind="uploaded_context",
                    context_class="uploaded_context",
                ),
            ))

    selected: list[ContextEvidenceRef] = []
    remaining = maximum_chars
    for _, _, evidence in sorted(candidates, key=lambda item: (item[0], item[1])):
        if len(evidence.statement) <= remaining:
            selected.append(evidence)
            remaining -= len(evidence.statement)
    return tuple(selected)


def run_verified_from_doc_parts(
    *,
    doc_parts: object,
    climate_grounding: object,
    clients: PipelineClients,
    run_id: str,
    cancel_event: object | None = None,
    doc_type: str = "Unknown",
    instrument_type: str = "Unknown",
    wall_clock_seconds: int = 14 * 60,
) -> dict[str, object]:
    """Run verified-v2 from the final extraction and grounding contracts."""

    prepared = prepare_verified_sources(doc_parts)
    doc_type, instrument_type = resolve_verified_document_context(
        prepared,
        doc_type=doc_type,
        instrument_type=instrument_type,
    )
    context = list(adapt_grounding_evidence(climate_grounding))
    context.extend(_uploaded_context_evidence(doc_parts))
    grounding = climate_grounding if isinstance(climate_grounding, dict) else {}
    assessment = run_verified_climate_pipeline(
        source_documents=list(prepared.documents),
        source_blocks=list(prepared.blocks),
        context_evidence=context,
        clients=clients,
        bank_release_id=str(grounding.get("content_version") or "") or None,
        run_id=run_id,
        cancel_event=cancel_event,
        wall_clock_seconds=wall_clock_seconds,
        doc_type=doc_type,
        instrument_type=instrument_type,
    )
    normalized = normalize_climate_assessment(assessment)
    reader = build_reader_model(normalized)
    reader_issues = validate_reader_model(reader)
    if reader_issues:
        detail_suffix = ""
        if "EXECUTIVE_LENGTH_INVALID" in reader_issues:
            executive_words = len(
                str(reader.get("executive_readout") or "").split()
            )
            detail_suffix = f"; executive_words={executive_words}"
        raise ValueError(
            "READER_INTEGRITY: " + ", ".join(reader_issues) + detail_suffix
        )
    return {
        "assessment": normalized,
        "reader": reader,
        "source_warnings": list(prepared.warning_codes),
    }
