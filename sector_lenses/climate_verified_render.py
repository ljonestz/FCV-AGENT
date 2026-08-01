"""One reader model for verified Climate-FCV web and DOCX outputs."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from docx import Document

from sector_lenses.climate_judgments import ALLOWED


DIMENSIONS = (
    ("relevance", "Climate-FCV relevance"),
    ("sensitivity", "FCV sensitivity"),
    ("responsiveness", "FCV responsiveness"),
    ("operationalization", "Operationalization"),
)
HEADINGS = (
    "Executive readout",
    "Climate-FCV judgments",
    "Ranked operational priorities",
    "Review readiness flags for task-team verification",
    "Technical annex",
)
PRIORITY_FIELDS = (
    ("Decision", "decision"),
    ("Minimum action", "minimum_action"),
    ("Enhanced action", "enhanced_action"),
    ("Activation condition", "enhanced_activation"),
    ("Who", "responsible_function"),
    ("Routing status", "routing_status"),
    ("Authority basis", "authority_basis"),
    ("Recommendation basis", "recommendation_basis"),
    ("Project evidence references", "project_anchor_ids"),
    ("Pathway references", "pathway_ids"),
    ("Existing-response references", "existing_response_ids"),
    ("Residual-gap references", "residual_gap_ids"),
    ("Instrument references", "instrument_claim_ids"),
    ("Completion evidence", "completion_evidence"),
    ("Completion evidence status", "completion_evidence_status"),
    ("Confidence", "confidence"),
    ("Limitation", "limitation"),
    ("Caution", "caution"),
    ("Suggested drafting", "drafting_language"),
)
ADVISORY_NOTICE = (
    "This automated screening supports task-team judgment and does not "
    "constitute an institutional adequacy or compliance decision."
)
_PLACEHOLDER = re.compile(
    r"(?:\[\s*(?:tbd|todo|insert|placeholder)[^\]]*\]|"
    r"\b(?:tbd|todo|lorem ipsum|placeholder)\b)",
    re.IGNORECASE,
)


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _records(value: object) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(
        value, list
    ) else []


def _text(value: object) -> str:
    return str(value or "").strip()


def _field_text(value: object) -> str:
    if isinstance(value, (list, tuple)):
        return ", ".join(_text(item) for item in value if _text(item))
    return _text(value)


def _rank(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 999


def build_reader_model(assessment: dict[str, object]) -> dict[str, object]:
    """Project a verified assessment into the only reader-facing structure."""

    raw_judgments = _mapping(assessment.get("judgments"))
    judgments = []
    for key, title in DIMENSIONS:
        judgment = _mapping(raw_judgments.get(key))
        judgments.append({
            "dimension": key,
            "title": title,
            "value": _text(judgment.get("value")),
            "rationale": _text(judgment.get("rationale")),
            "evidence_ids": [
                _text(item)
                for item in judgment.get("evidence_ids", [])
                if _text(item)
            ] if isinstance(judgment.get("evidence_ids"), list) else [],
        })

    priorities = sorted(
        _records(assessment.get("priorities")),
        key=lambda item: (_rank(item.get("rank")), _text(item.get("title"))),
    )[:3]
    flags = _records(assessment.get("review_readiness_flags"))[:4]
    validation = _mapping(assessment.get("validation"))
    executive = _text(assessment.get("executive_readout")) or _text(
        assessment.get("judgment_summary")
    )
    return {
        "executive_readout": executive,
        "judgments": judgments,
        "priorities": [dict(item) for item in priorities],
        "review_readiness_flags": [dict(item) for item in flags],
        "evidence_status": _text(assessment.get("evidence_status")) or "approved",
        "technical_annex": {
            "run_id": _text(assessment.get("run_id")),
            "schema_version": _text(assessment.get("schema_version")),
            "bank_release_id": _text(assessment.get("bank_release_id")),
            "validation_status": _text(validation.get("status")),
        },
        "advisory_notice": ADVISORY_NOTICE,
    }


def _all_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


def validate_reader_model(model: dict[str, object]) -> tuple[str, ...]:
    """Return deterministic reader-integrity reason codes."""

    issues: list[str] = []
    executive = _text(model.get("executive_readout"))
    if executive:
        words = len(executive.split())
        if not 350 <= words <= 600:
            issues.append("EXECUTIVE_LENGTH_INVALID")
        if executive[-1:] not in ".?!":
            issues.append("EXECUTIVE_SENTENCE_INCOMPLETE")

    judgments = _records(model.get("judgments"))
    if [item.get("dimension") for item in judgments] != [
        key for key, _ in DIMENSIONS
    ]:
        issues.append("JUDGMENT_DIMENSIONS_INCOMPLETE")
    for judgment in judgments:
        dimension = _text(judgment.get("dimension"))
        if _text(judgment.get("value")) not in ALLOWED.get(dimension, set()):
            issues.append("JUDGMENT_VALUE_INVALID")
        rationale = _text(judgment.get("rationale"))
        if not rationale or rationale[-1:] not in ".?!":
            issues.append("JUDGMENT_RATIONALE_INCOMPLETE")

    priorities = _records(model.get("priorities"))
    ranks = [_rank(item.get("rank")) for item in priorities]
    if ranks != list(range(1, len(priorities) + 1)):
        issues.append("PRIORITY_RANK_ORDER_INVALID")
    titles = [_text(item.get("title")).casefold() for item in priorities]
    if len(titles) != len(set(titles)):
        issues.append("DUPLICATE_PRIORITY_TITLE")
    required = (
        "recommendation_id",
        "title",
        "decision",
        "minimum_action",
        "confidence",
    )
    if any(not all(_text(item.get(key)) for key in required) for item in priorities):
        issues.append("PRIORITY_FIELD_INCOMPLETE")

    if any(_PLACEHOLDER.search(value) for value in _all_strings(model)):
        issues.append("UNRESOLVED_PLACEHOLDER")
    if any(
        value.rstrip().endswith(("[", "{", "…"))
        for value in _all_strings(model)
        if value.strip()
    ):
        issues.append("TRUNCATED_READER_FIELD")
    return tuple(dict.fromkeys(issues))


def _heading(level: int, text: str) -> str:
    return f"<h{level}>{html.escape(text)}</h{level}>"


def render_reader_html(model: dict[str, object]) -> str:
    """Render escaped HTML from the canonical reader dictionary."""

    parts = ['<article class="climate-verified-assessment">']
    parts.append(_heading(2, HEADINGS[0]))
    parts.append(f"<p>{html.escape(_text(model.get('executive_readout')))}</p>")
    evidence_status = _text(model.get("evidence_status"))
    if evidence_status != "approved":
        parts.append(
            '<p class="climate-evidence-status">'
            + html.escape(evidence_status)
            + "</p>"
        )

    parts.append(_heading(2, HEADINGS[1]))
    for judgment in _records(model.get("judgments")):
        parts.append(
            '<section class="climate-judgment" data-climate-dimension="'
            + html.escape(_text(judgment.get("dimension")))
            + '">'
        )
        parts.append(_heading(3, _text(judgment.get("title"))))
        parts.append(
            "<p><strong>"
            + html.escape(_text(judgment.get("value")).replace("_", " ").title())
            + ":</strong> "
            + html.escape(_text(judgment.get("rationale")))
            + "</p>"
        )
        evidence_refs = _field_text(judgment.get("evidence_ids"))
        if evidence_refs:
            parts.append(
                "<p><strong>Evidence references:</strong> "
                + html.escape(evidence_refs)
                + "</p>"
            )
        parts.append("</section>")

    parts.append(_heading(2, HEADINGS[2]))
    for priority in _records(model.get("priorities")):
        rank = _rank(priority.get("rank"))
        identifier = _text(priority.get("recommendation_id"))
        parts.append('<section class="climate-priority">')
        parts.append(
            _heading(3, f"{rank}. {_text(priority.get('title'))} ({identifier})")
        )
        for label, key in PRIORITY_FIELDS:
            value = _field_text(priority.get(key))
            if value:
                parts.append(
                    f"<p><strong>{html.escape(label)}:</strong> "
                    f"{html.escape(value)}</p>"
                )
        parts.append("</section>")

    parts.append("<details><summary>")
    parts.append(html.escape(HEADINGS[3]))
    parts.append("</summary>")
    for flag in _records(model.get("review_readiness_flags")):
        parts.append(_heading(3, _text(flag.get("flag"))))
        parts.append(
            "<p><strong>Why it matters:</strong> "
            + html.escape(_text(flag.get("why_it_matters")))
            + "</p><p><strong>Document basis:</strong> "
            + html.escape(_field_text(flag.get("document_basis_ids")))
            + "</p><p><strong>Suggested verification:</strong> "
            + html.escape(_text(flag.get("suggested_verification")))
            + "</p>"
        )
    parts.append("</details>")

    parts.append("<details><summary>")
    parts.append(html.escape(HEADINGS[4]))
    parts.append("</summary>")
    for key, value in _mapping(model.get("technical_annex")).items():
        parts.append(
            f"<p><strong>{html.escape(key.replace('_', ' ').title())}:</strong> "
            f"{html.escape(_text(value))}</p>"
        )
    parts.append("</details>")
    parts.append(
        '<p class="climate-advisory">'
        + html.escape(_text(model.get("advisory_notice")))
        + "</p></article>"
    )
    return "".join(parts)


def _docx_field(document: Document, label: str, value: object) -> None:
    text = _field_text(value)
    if not text:
        return
    paragraph = document.add_paragraph()
    paragraph.add_run(f"{label}: ").bold = True
    paragraph.add_run(text)


def write_reader_docx(model: dict[str, object], path: str | Path) -> Path:
    """Write the same reader dictionary to a compact Word document."""

    output = path if hasattr(path, "write") else Path(path)
    document = Document()
    document.add_heading(HEADINGS[0], level=1)
    document.add_paragraph(_text(model.get("executive_readout")))
    if _text(model.get("evidence_status")) != "approved":
        _docx_field(document, "Evidence status", model.get("evidence_status"))

    document.add_heading(HEADINGS[1], level=1)
    for judgment in _records(model.get("judgments")):
        document.add_heading(_text(judgment.get("title")), level=2)
        _docx_field(document, "Judgment", judgment.get("value"))
        _docx_field(document, "Rationale", judgment.get("rationale"))
        _docx_field(
            document, "Evidence references", judgment.get("evidence_ids")
        )

    document.add_heading(HEADINGS[2], level=1)
    for priority in _records(model.get("priorities")):
        rank = _rank(priority.get("rank"))
        identifier = _text(priority.get("recommendation_id"))
        document.add_heading(
            f"{rank}. {_text(priority.get('title'))} ({identifier})",
            level=2,
        )
        for label, key in PRIORITY_FIELDS:
            _docx_field(document, label, priority.get(key))

    document.add_heading(HEADINGS[3], level=1)
    for flag in _records(model.get("review_readiness_flags")):
        document.add_heading(_text(flag.get("flag")), level=2)
        _docx_field(document, "Why it matters", flag.get("why_it_matters"))
        _docx_field(document, "Document basis", flag.get("document_basis_ids"))
        _docx_field(
            document,
            "Suggested verification",
            flag.get("suggested_verification"),
        )

    document.add_heading(HEADINGS[4], level=1)
    for key, value in _mapping(model.get("technical_annex")).items():
        _docx_field(document, key.replace("_", " ").title(), value)
    document.add_paragraph(_text(model.get("advisory_notice")))
    document.save(output)
    return output
