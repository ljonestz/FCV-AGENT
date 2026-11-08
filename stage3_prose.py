"""Detect and repair list-formatted opening sections in core Stage 3 output.

The Stage 3 note's Operational Context, Strengths and Gaps should be connected
analytical prose. The model sometimes falls back to bullet or numbered lists with
bold lead-in labels. This module finds those sections and, when enabled, asks the
model to rewrite only them as prose, then checks that every figure and named
term survived before accepting the rewrite. Anything that fails a check keeps the
original text, so the repair can never remove content.
"""
from __future__ import annotations

import re
from collections.abc import Callable

SECTION_NAMES = ("Operational Context", "Strengths", "Gaps")
_HEADING_RE = re.compile(r"^###\s*(Operational Context|Strengths|(?:Potential |Key )?Gaps)\b[^\n]*\n", re.MULTILINE | re.IGNORECASE)
_LIST_LINE_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S", re.MULTILINE)
_LABEL_LINE_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)?\*\*[^*\n]{2,60}[.:]\*\*", re.MULTILINE)
# A section ends at the next heading or at a Stage 3 delimiter.
_SECTION_END_RE = re.compile(r"\n(?=#{2,3}\s|%%%[A-Z_]+%%%|\*\*FCV Sensitivity Summary)")

REPAIR_INSTRUCTIONS = """You are editing sections of a World Bank FCV support note. Rewrite each
section below as connected analytical prose for an experienced FCV and operations reader.

Rules:
- Keep every fact, figure, name, acronym, caveat, ranking and condition. Do not add new
  facts, figures, examples or recommendations, and do not drop any.
- Turn list items into sentences that are linked to one another, explaining how the points
  relate (cause, consequence, dependency) only where the original already supports it.
- Keep the bold first sentence of each paragraph. Use one or two paragraphs per section.
- No bullet lists, numbered lists or bold lead-in labels. No em dashes. Semicolons sparingly.
- Return the sections in the same order, each starting with its original heading line
  exactly as given, and nothing else.
"""


def find_sections(text: str) -> list[tuple[str, int, int]]:
    """Return (heading, body_start, body_end) for each opening section present."""
    found = []
    for match in _HEADING_RE.finditer(text):
        start = match.end()
        end_match = _SECTION_END_RE.search(text, start)
        end = end_match.start() if end_match else len(text)
        found.append((match.group(0).rstrip("\n"), start, end))
    return found


def _label_count(body: str) -> int:
    # Short bold lead-ins ("**Tariff sequencing.**") are labels; a bold topic sentence
    # that opens a paragraph is normally longer than eight words.
    return sum(1 for m in _LABEL_LINE_RE.finditer(body) if len(m.group(0).strip("*-+ .0123456789)").split()) <= 8)


def is_listy(body: str) -> bool:
    return bool(_LIST_LINE_RE.search(body) or _label_count(body) >= 2)


def listy_sections(text: str) -> list[tuple[str, int, int]]:
    return [s for s in find_sections(text) if is_listy(text[s[1]:s[2]])]


def _figures(text: str) -> set[str]:
    # List numbering ("1.", "2)") is formatting, not a figure.
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)
    return {f.rstrip(".,") for f in re.findall(r"\d[\d,.]*", text)}


def _terms(text: str) -> set[str]:
    # Acronyms and capitalised multi-letter tokens that should survive a rewrite.
    return set(re.findall(r"\b[A-Z][A-Z0-9&/-]{1,}\b", text))


def validate_rewrite(original: str, rewritten: str) -> str:
    """Return '' if the rewrite is acceptable, else a reason."""
    if is_listy(rewritten):
        return "still_listy"
    if "—" in rewritten:
        return "em_dash"
    missing_figures = _figures(original) - _figures(rewritten)
    if missing_figures:
        return "figures_missing:" + ",".join(sorted(missing_figures)[:5])
    missing_terms = _terms(original) - _terms(rewritten)
    if missing_terms:
        return "terms_missing:" + ",".join(sorted(missing_terms)[:5])
    ow, rw = len(original.split()), len(rewritten.split())
    if not (0.8 * ow <= rw <= 1.4 * ow):
        return f"length_changed:{ow}->{rw}"
    return ""


def _split_rewrite(rewritten: str, headings: list[str]) -> list[str] | None:
    bodies = []
    pos = 0
    for i, heading in enumerate(headings):
        idx = rewritten.find(heading, pos)
        if idx < 0:
            return None
        start = idx + len(heading)
        nxt = rewritten.find(headings[i + 1], start) if i + 1 < len(headings) else len(rewritten)
        if nxt < 0:
            return None
        bodies.append(rewritten[start:nxt].strip())
        pos = nxt
    return bodies


def repair(text: str, call_model: Callable[[str], str]) -> tuple[str, dict]:
    """Rewrite list-formatted opening sections. Returns (text, report).

    call_model receives the full repair prompt and returns the model's text.
    On any failure the original text is returned unchanged.
    """
    targets = listy_sections(text)
    report = {"listy": [t[0] for t in targets], "repaired": False, "reason": ""}
    if not targets:
        return text, report
    headings = [t[0] for t in targets]
    originals = [text[t[1]:t[2]].strip() for t in targets]
    prompt = REPAIR_INSTRUCTIONS + "\n\n" + "\n\n".join(f"{h}\n{b}" for h, b in zip(headings, originals))
    try:
        rewritten = call_model(prompt)
    except Exception as exc:  # noqa: BLE001 - repair is best effort; keep the original
        report["reason"] = f"call_failed:{type(exc).__name__}"
        return text, report
    bodies = _split_rewrite(rewritten or "", headings)
    if bodies is None:
        report["reason"] = "headings_missing"
        return text, report
    for original, body in zip(originals, bodies):
        reason = validate_rewrite(original, body)
        if reason:
            report["reason"] = reason
            return text, report
    out = text
    for (heading, start, end), body in sorted(zip(targets, bodies), key=lambda x: x[0][1], reverse=True):
        out = out[:start] + "\n" + body + "\n" + out[end:]
    report["repaired"] = True
    return out, report
