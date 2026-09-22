"""Pure text presentation helpers shared by FCV exports."""

from __future__ import annotations

import re
from typing import Any


_PROTECTED_RE = re.compile(r'https?://[^\s<>"\']+|\x60[^\x60\n]+\x60')
_ABBREVIATION_RE = re.compile(r'(?:[A-Za-z]\.){2,}$')
_ABBREVIATIONS = {
    "approx.",
    "dept.",
    "dr.",
    "e.g.",
    "etc.",
    "fig.",
    "i.e.",
    "inc.",
    "jr.",
    "mr.",
    "mrs.",
    "ms.",
    "no.",
    "p.",
    "pp.",
    "prof.",
    "sr.",
    "u.k.",
    "u.s.",
    "vs.",
}


def normalize_display_text(value: Any) -> str:
    """Replace visible em dashes while preserving URLs and code spans."""
    text = str(value)
    protected: list[str] = []

    def protect(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"__FCV_PROTECTED_{len(protected) - 1}__"

    text = _PROTECTED_RE.sub(protect, text)
    text = re.sub(r"[ \t]*\u2014[ \t]*", " - ", text)
    for index, original in enumerate(protected):
        text = text.replace(f"__FCV_PROTECTED_{index}__", original)
    return text


def _protected_spans(text: str) -> list[tuple[int, int]]:
    return [match.span() for match in _PROTECTED_RE.finditer(text)]


def _inside_protected(index: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= index < end for start, end in spans)


def _is_abbreviation(text: str, end: int) -> bool:
    token_match = re.search(r'[A-Za-z][A-Za-z.]*\.$', text[: end + 1])
    if not token_match:
        return False
    token = token_match.group(0).lower()
    return token in _ABBREVIATIONS or bool(_ABBREVIATION_RE.fullmatch(token))


def split_first_sentence(text: str) -> tuple[str, str]:
    """Return (first sentence, remainder) with decimal/URL/abbreviation guards."""
    value = str(text).strip()
    if not value:
        return "", ""

    spans = _protected_spans(value)
    for index, character in enumerate(value):
        if character not in ".!?":
            continue
        if _inside_protected(index, spans):
            continue
        if character == ".":
            previous = value[index - 1] if index else ""
            following = value[index + 1] if index + 1 < len(value) else ""
            if previous.isdigit() and following.isdigit():
                continue
            if _is_abbreviation(value, index):
                continue
        following_index = index + 1
        while (
            following_index < len(value)
            and value[following_index] in (chr(34), chr(39), ")", "]")
        ):
            following_index += 1
        if following_index < len(value) and not value[following_index].isspace():
            continue
        end = following_index
        return value[:end].rstrip(), value[end:].lstrip()
    return value, ""


def bullet_finding_sections(text: str) -> str:
    """Bullet complete prose paragraphs only under strengths/gaps headings."""
    parts = re.split(r"(^#{1,3} .+$)", text, flags=re.MULTILINE)
    selected = False
    for index, part in enumerate(parts):
        if re.match(r"^#{1,3} ", part):
            title = re.sub(r"^#{1,3} ", "", part).strip().lower().rstrip(":")
            selected = title in {"strengths", "gaps", "potential gaps", "key gaps"}
        elif selected:
            blocks = re.split(r"(\n\s*\n)", part)
            for block_index in range(0, len(blocks), 2):
                block = blocks[block_index]
                structured = re.search(
                    r"^\s*(?:[-*+] |\d+[.)] |[#>|]|---)", block, re.MULTILINE
                )
                if block.strip() and not structured:
                    finding = "- " + " ".join(block.strip().splitlines())
                    blocks[block_index] = block.replace(block.strip(), finding, 1)
            parts[index] = re.sub(r"(\S)\n\s*\n(?=- )", r"\1\n", "".join(blocks))
    return "".join(parts)


def strip_watch_heading(value: Any) -> str:
    """Remove only repeated leading section titles; preserve watch subheadings."""
    text = str(value or "").strip()
    pattern = r"^(?:#{1,6}[ \t]+)?(?:\*\*|__)?Watch List for Supervision(?:\*\*|__)?[ \t]*:?[ \t]*(?:\r?\n|$)"
    while re.match(pattern, text, flags=re.IGNORECASE):
        text = re.sub(pattern, "", text, count=1, flags=re.IGNORECASE).lstrip()
    return text
