"""One reader model for verified Climate-FCV web and DOCX outputs."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from docx import Document

from climate_question_bank import CLIMATE_LITERATURE_REFERENCES
from sector_lenses.climate_judgments import ALLOWED


DIMENSIONS = (
    (
        "relevance",
        "Climate-FCV relevance",
        "How strongly do climate and FCV pressures intersect in this "
        "project's context and objectives?",
    ),
    (
        "sensitivity",
        "Climate & FCV sensitivity",
        "Is the project designed to recognise and avoid worsening climate- "
        "and FCV-related risks (do no harm)?",
    ),
    (
        "responsiveness",
        "Climate & FCV responsiveness",
        "Does the project actively build climate resilience and address the "
        "drivers of fragility, conflict, and violence?",
    ),
    (
        "operationalization",
        "From intent to delivery (operationalization)",
        "Are these intentions turned into concrete requirements, roles, "
        "indicators, and triggers the team can act on?",
    ),
)
NO_RECOMMENDATION_MESSAGE = (
    "No recommendation passed the admission threshold for this run."
)


HEADINGS = (
    "Executive readout",
    "Climate-FCV judgments",
    "Ranked operational priorities",
    "Points to check before the decision meeting",
    "Technical annex",
)
# Lay-comprehensible intro shared by the points-to-check section across all three
# render surfaces (server HTML, DOCX, and the frontend renderer).
POINTS_TO_CHECK_INTRO = (
    "These are smaller things for the team to confirm or consider before the concept "
    "or decision meeting. They are not the main recommendations above, and none is a "
    "reason to stop the project - think of them as a checklist."
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
)
SMOKE_RUNTIME_WARNING = (
    "Smoke test: validates workflow completion only; "
    "not a quality benchmark."
)
ADVISORY_NOTICE = (
    "This automated screening supports task-team judgment and does not "
    "constitute an institutional adequacy or compliance decision."
)
_PLACEHOLDER = re.compile(
    r"(?:\[\s*(?:tbd|todo|insert|placeholder)[^\]]*\]|"
    r"\b(?:tbd|todo|lorem ipsum)\b)",
    re.IGNORECASE,
)
_BARE_PLACEHOLDER = re.compile(
    r"^\s*placeholder(?:\s+text)?[.!]?\s*$",
    re.IGNORECASE,
)


def _scrub_placeholder_text(text: str) -> str:
    """Strip model-emitted placeholder cues from a single reader string.

    A single stray '[insert ...]'/'[tbd]'/bare 'tbd'/'todo' from the model must
    not hard-fail an entire (paid) run at the reader-integrity gate. Remove the
    cue and keep the surrounding prose, mirroring the deterministic
    vocabulary-scrub pattern used elsewhere in the app. Genuinely structural
    problems (empty required fields, truncation) still surface downstream.
    """
    if not text:
        return text
    cleaned = _PLACEHOLDER.sub("", text)
    if _BARE_PLACEHOLDER.fullmatch(cleaned.strip()):
        cleaned = ""
    cleaned = re.sub(r"\(\s*\)", "", cleaned)            # empty parens left behind
    cleaned = re.sub(r"[ \t]+([.,;:!?])", r"\1", cleaned)  # space before punctuation
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)          # collapse space runs (keep newlines)
    return cleaned.strip()


def _scrub_placeholders(value: object) -> object:
    """Recursively scrub placeholder cues from every string leaf in a reader."""
    if isinstance(value, str):
        return _scrub_placeholder_text(value)
    if isinstance(value, dict):
        return {key: _scrub_placeholders(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_scrub_placeholders(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_scrub_placeholders(item) for item in value)
    return value


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


def _no_priority_message(model: dict[str, object]) -> str:
    annex = _mapping(model.get("technical_annex"))
    try:
        admitted = int(annex.get("recommendation_admitted_count", 0))
    except (TypeError, ValueError):
        admitted = 0
    verdict = _text(annex.get("semantic_reviewer_verdict")).casefold()
    if admitted > 0 and verdict in {"revise", "block"}:
        noun = "candidate" if admitted == 1 else "candidates"
        verb = "was" if admitted == 1 else "were"
        return (
            f"{admitted} recommendation {noun} passed deterministic admission "
            f"but {verb} withheld after semantic review. Review outcome: "
            f"{verdict}. See the technical annex."
        )
    return NO_RECOMMENDATION_MESSAGE


def _priority_summary(priorities: list[dict[str, Any]]) -> dict[str, object]:
    titles = [_text(item.get("title")) for item in priorities]
    count = len(titles)
    if count == 0:
        statement = (
            "No final operational priority was admitted after validation and "
            "semantic review."
        )
    else:
        number_word = {1: "One", 2: "Two", 3: "Three"}.get(count, str(count))
        noun = "priority is" if count == 1 else "priorities are"
        statement = (
            f"{number_word} final operational {noun} presented: "
            + "; ".join(titles)
            + "."
        )
    return {"count": count, "titles": titles, "statement": statement}


def build_reader_model(assessment: dict[str, object]) -> dict[str, object]:
    """Project a verified assessment into the only reader-facing structure."""

    raw_judgments = _mapping(assessment.get("judgments"))
    judgments = []
    for key, title, description in DIMENSIONS:
        judgment = _mapping(raw_judgments.get(key))
        judgments.append({
            "dimension": key,
            "title": title,
            "description": description,
            "value": _text(judgment.get("value")),
            "rationale": _text(judgment.get("rationale")),
            "evidence_ids": [
                _text(item)
                for item in judgment.get("evidence_ids", [])
                if _text(item)
            ] if isinstance(judgment.get("evidence_ids"), (list, tuple)) else [],
        })

    priorities = sorted(
        _records(assessment.get("priorities")),
        key=lambda item: (_rank(item.get("rank")), _text(item.get("title"))),
    )[:3]
    flags = _records(assessment.get("review_readiness_flags"))[:4]
    validation = _mapping(assessment.get("validation"))
    diagnostics = _mapping(assessment.get("recommendation_diagnostics"))
    executive = _text(assessment.get("executive_readout")) or _text(
        assessment.get("judgment_summary")
    )
    return _scrub_placeholders({
        "executive_readout": executive,
        "judgments": judgments,
        "priorities": [dict(item) for item in priorities],
        "review_readiness_flags": [dict(item) for item in flags],
        "priority_summary": _priority_summary(priorities),
        "evidence_status": _text(assessment.get("evidence_status")) or "approved",
        "technical_annex": {
            "run_id": _text(assessment.get("run_id")),
            "schema_version": _text(assessment.get("schema_version")),
            "bank_release_id": _text(assessment.get("bank_release_id")),
            "validation_status": _text(validation.get("status")),
            "recommendation_candidate_count": diagnostics.get(
                "raw_candidate_count", 0
            ),
            "recommendation_admitted_count": diagnostics.get(
                "admitted_count", 0
            ),
            "recommendation_final_count": diagnostics.get(
                "final_priority_count", 0
            ),
            "semantic_reviewer_invoked": diagnostics.get(
                "reviewer_invoked", False
            ),
            "live_research_count": _mapping(
                assessment.get("manifest")
            ).get("live_research_count", 0),
            "semantic_reviewer_verdict": _text(
                diagnostics.get("reviewer_verdict")
            ) or "not_invoked",
            "recommendation_reason_codes": diagnostics.get("reason_codes", []),
            "unsupported_numeric_tokens": diagnostics.get(
                "unsupported_numeric_tokens", []
            ),
            "semantic_review_object_ids": [
                _text(item)
                for item in diagnostics.get("semantic_review_object_ids", [])
                if _text(item)
            ][:12] if isinstance(
                diagnostics.get("semantic_review_object_ids"), list
            ) else [],
            "candidate_suppressions": _records(
                diagnostics.get("candidate_suppressions")
            )[:3],
        },
        "advisory_notice": ADVISORY_NOTICE,
    })


_METHODOLOGY_NOTE = (
    "This analysis was produced by a verified pipeline: it extracts atomic "
    "project facts from the uploaded document, maps how climate and FCV "
    "pressures interact through evidence-anchored pathways, judges four "
    "dimensions against that evidence, compiles only recommendations that pass "
    "deterministic admission tests, and applies a conditional review. Every "
    "judgement and recommendation is tied to the references listed below."
)

_ID_TYPE_LABELS = {
    "PF": "Project fact", "RG": "Residual gap", "ER": "Existing response",
    "PW": "Climate-FCV pathway", "CE-LIVE": "Live research", "CE": "Context evidence",
}


def _id_type(identifier: str) -> str:
    if identifier.upper().startswith("CE-LIVE"):
        return "CE-LIVE"
    prefix = identifier.split("-", 1)[0].upper()
    return prefix


def _chain_prose(chain: list) -> str:
    parts = [_text(c) for c in chain if _text(c)]
    if len(parts) >= 3:
        middle = ", ".join(parts[1:-1])
        return f"{parts[0]}, leading through {middle}, to {parts[-1]}."
    return "; ".join(parts) + ("." if parts else "")


def build_evidence_trail(assessment: dict[str, object]) -> dict[str, object]:
    """Project a plain-language evidence trail from the raw verified assessment.

    Deterministic; resolves only IDs actually cited in judgments/priorities.
    Resolution priority for a cited ID: facts > residual gaps > existing
    responses > pathways, then CE-LIVE / CE stubs, then "reference not resolved".
    """
    analysis = _mapping(assessment.get("analysis"))
    facts = {_text(f.get("claim_id")): f for f in _records(assessment.get("facts"))}
    responses = {_text(r.get("response_id")): r
                 for r in _records(analysis.get("existing_responses"))}
    gaps = {_text(g.get("gap_id")): g
            for g in _records(analysis.get("residual_gaps"))}
    pathways_raw = _records(analysis.get("pathways"))
    pathways_by_id = {_text(p.get("pathway_id")): p for p in pathways_raw}

    pathways = []
    for p in pathways_raw:
        direction = _text(p.get("direction"))
        label = ("Climate -> FCV" if direction == "climate_to_fcv"
                 else "FCV -> Climate" if direction == "fcv_to_climate"
                 else direction or "Pathway")
        pathways.append({
            "direction_label": label,
            "chain_prose": _chain_prose(
                p.get("chain") if isinstance(p.get("chain"), list) else []
            ),
            "anchor_ids": [_text(a) for a in p.get("project_anchor_ids", []) if _text(a)]
            if isinstance(p.get("project_anchor_ids"), (list, tuple)) else [],
        })

    cited: list[str] = []
    judgments = _mapping(assessment.get("judgments"))
    for value in judgments.values():
        jm = _mapping(value)
        eids = jm.get("evidence_ids")
        if isinstance(eids, (list, tuple)):
            for eid in eids:
                if _text(eid):
                    cited.append(_text(eid))
    for pr in _records(assessment.get("priorities")):
        for field in ("project_anchor_ids", "pathway_ids", "existing_response_ids",
                      "residual_gap_ids", "instrument_claim_ids"):
            vals = pr.get(field)
            if isinstance(vals, (list, tuple)):
                cited.extend(_text(v) for v in vals if _text(v))

    seen: set[str] = set()
    evidence_key = []
    for cid in cited:
        if cid in seen:
            continue
        seen.add(cid)
        t = _id_type(cid)
        label = _ID_TYPE_LABELS.get(t, "Reference")
        if cid in facts:
            f = facts[cid]
            text = " ".join(
                x for x in (_text(f.get("subject")), _text(f.get("predicate")),
                             _text(f.get("object"))) if x
            ) or _text(f.get("supporting_excerpt"))
        elif cid in gaps:
            text = _text(gaps[cid].get("statement"))
        elif cid in responses:
            text = _text(responses[cid].get("description"))
        elif cid in pathways_by_id:
            text = _chain_prose(
                pathways_by_id[cid].get("chain")
                if isinstance(pathways_by_id[cid].get("chain"), list) else []
            )
        elif t == "CE-LIVE":
            text = "Accepted live-research evidence for this run."
        elif t == "CE":
            text = "Context evidence cited for this run (summary not stored)."
        else:
            text = "Reference not resolved."
        evidence_key.append({"id": cid, "type_label": label, "text": text})

    diag = _mapping(assessment.get("recommendation_diagnostics"))
    manifest = _mapping(assessment.get("manifest"))
    diagnostics = {
        "candidate_count": diag.get("raw_candidate_count", 0),
        "admitted_count": diag.get("admitted_count", 0),
        "final_count": diag.get("final_priority_count", 0),
        "reviewer_verdict": _text(diag.get("reviewer_verdict")) or "not_invoked",
        "live_research_count": manifest.get("live_research_count", 0),
        "bank_release": _text(assessment.get("bank_release_id")),
        "evidence_status": _text(assessment.get("evidence_status")),
    }
    return {
        "methodology_note": _METHODOLOGY_NOTE,
        "pathways": pathways,
        "evidence_key": evidence_key,
        "diagnostics": diagnostics,
    }


def attach_provenance(reader: dict[str, object], assessment: dict[str, object]) -> dict[str, object]:
    """Attach the evidence trail and static literature references to a reader.

    Called after build_reader_model/validate_reader_model so it is additive and
    never affects reader-integrity validation.
    """
    reader["evidence_trail"] = build_evidence_trail(assessment)
    reader["sources"] = [dict(entry) for entry in CLIMATE_LITERATURE_REFERENCES]
    return reader


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
        if not 300 <= words <= 900:
            issues.append("EXECUTIVE_LENGTH_INVALID")
        if executive[-1:] not in ".?!":
            issues.append("EXECUTIVE_SENTENCE_INCOMPLETE")

    judgments = _records(model.get("judgments"))
    if [item.get("dimension") for item in judgments] != [
        key for key, _, _ in DIMENSIONS
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
    drafting_required = (
        "target_document",
        "target_section",
        "drafting_status",
        "text",
        "project_basis_ids",
        "gap_basis_ids",
        "guidance_ids",
    )
    for priority in priorities:
        current = _mapping(priority.get("current_document_drafting"))
        if not current or any(key not in current for key in drafting_required):
            issues.append("CURRENT_DRAFTING_INCOMPLETE")
        optional_value = priority.get("operational_instrument_drafting")
        if optional_value is not None and not isinstance(optional_value, dict):
            issues.append("OPERATIONAL_DRAFTING_MALFORMED")
        for block in (current, _mapping(optional_value)):
            if not block:
                continue
            draft_text = _text(block.get("text"))
            if not draft_text or draft_text[-1:] not in ".?!":
                issues.append("DRAFTING_TEXT_INCOMPLETE")

    if any(not all(_text(item.get(key)) for key in required) for item in priorities):
        issues.append("PRIORITY_FIELD_INCOMPLETE")
    summary = _mapping(model.get("priority_summary"))
    summary_titles = summary.get("titles")
    if (
        summary.get("count") != len(priorities)
        or summary_titles != [_text(item.get("title")) for item in priorities]
        or not _text(summary.get("statement"))
    ):
        issues.append("PRIORITY_SUMMARY_MISMATCH")


    if any(
        _PLACEHOLDER.search(value) or _BARE_PLACEHOLDER.fullmatch(value)
        for value in _all_strings(model)
    ):
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


def _drafting_html(label: str, value: object) -> str:
    block = _mapping(value)
    if not block:
        return ""
    parts = ['<section class="climate-drafting-block">']
    parts.append(_heading(4, label))
    for field_label, key in (
        ("Target document", "target_document"),
        ("Target section", "target_section"),
        ("Drafting status", "drafting_status"),
        ("Guidance basis", "guidance_ids"),
    ):
        field_value = _field_text(block.get(key))
        if field_value:
            parts.append(
                f"<p><strong>{html.escape(field_label)}:</strong> "
                f"{html.escape(field_value)}</p>"
            )
    parts.append(
        '<div class="climate-drafting-text">'
        + html.escape(_text(block.get("text")))
        + "</div>"
    )
    parts.append("</section>")
    return "".join(parts)


def render_reader_html(model: dict[str, object]) -> str:
    """Render escaped HTML from the canonical reader dictionary."""

    parts = ['<article class="climate-verified-assessment">']
    if _text(model.get("runtime_mode")) == "smoke":
        parts.append(
            '<p class="climate-smoke-warning">'
            + html.escape(SMOKE_RUNTIME_WARNING)
            + "</p>"
        )
    parts.append(_heading(2, HEADINGS[0]))
    for _exec_para in re.split(r"\n\s*\n+", _text(model.get("executive_readout")).strip()):
        _exec_para = _exec_para.strip()
        if not _exec_para:
            continue
        _m = re.match(r"^(.*?[.!?])(\s+)([\s\S]*)$", _exec_para)
        if _m:
            parts.append(
                f"<p><strong>{html.escape(_m.group(1))}</strong>"
                f"{html.escape(_m.group(2) + _m.group(3))}</p>"
            )
        else:
            parts.append(f"<p><strong>{html.escape(_exec_para)}</strong></p>")
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
        description = _text(judgment.get("description"))
        if description:
            parts.append(
                '<p class="climate-judgment-desc"><em>'
                + html.escape(description)
                + "</em></p>"
            )
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
    priorities = _records(model.get("priorities"))
    priority_summary = _mapping(model.get("priority_summary"))
    if _text(priority_summary.get("statement")):
        parts.append(
            '<p class="climate-priority-summary">'
            + html.escape(_text(priority_summary.get("statement")))
            + "</p>"
        )
    if not priorities:
        parts.append(f"<p>{html.escape(_no_priority_message(model))}</p>")
    for priority in priorities:
        rank = _rank(priority.get("rank"))
        identifier = _text(priority.get("recommendation_id"))
        parts.append('<section class="climate-priority">')
        parts.append(
            _heading(3, f"{rank}. {_text(priority.get('title'))} ({identifier})")
        )
        narrative = _text(priority.get("narrative"))
        if narrative:
            for para in re.split(r"\n\s*\n+", narrative.strip()):
                para = para.strip()
                if para:
                    parts.append(f"<p>{html.escape(para)}</p>")
        for label, key in PRIORITY_FIELDS:
            value = _field_text(priority.get(key))
            if value:
                parts.append(
                    f"<p><strong>{html.escape(label)}:</strong> "
                    f"{html.escape(value)}</p>"
                )
            if key == "minimum_action":
                parts.append(_drafting_html(
                    "Current document drafting",
                    priority.get("current_document_drafting"),
                ))
                parts.append(_drafting_html(
                    "Operational instrument drafting",
                    priority.get("operational_instrument_drafting"),
                ))
        parts.append("</section>")

    parts.append("<details><summary>")
    parts.append(html.escape(HEADINGS[3]))
    parts.append("</summary>")
    parts.append(f"<p>{html.escape(POINTS_TO_CHECK_INTRO)}</p>")
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

    trail = _mapping(model.get("evidence_trail"))
    if trail:
        sources = model.get("sources") or []
        parts.append('<details class="climate-fold"><summary>How this analysis was produced</summary>')
        parts.append(f'<p>{html.escape(_text(trail.get("methodology_note")))}</p>')
        pathways = _records(trail.get("pathways"))
        if pathways:
            parts.append("<h4>Pathways</h4>")
            parts.append(
                "<p>Pathways are the specific ways climate pressures and fragility feed "
                "into each other in this project. Each one is a short chain from a cause to "
                "an effect.</p><ul>"
            )
            for p in pathways:
                parts.append(
                    f'<li><strong>{html.escape(_text(p.get("direction_label")))}:</strong> '
                    f'{html.escape(_text(p.get("chain_prose")))}</li>')
            parts.append("</ul>")
        key = _records(trail.get("evidence_key"))
        if key:
            parts.append("<h4>Evidence key</h4>")
            parts.append(
                "<p>The evidence key explains every reference code used above (for example "
                "PF- for a project fact, RG- for a residual gap, ER- for an existing "
                "response, PW- for a pathway), so each finding can be traced to its "
                "source.</p><ul>"
            )
            for e in key:
                parts.append(
                    f'<li><strong>{html.escape(_text(e.get("id")))}</strong> '
                    f'({html.escape(_text(e.get("type_label")))}): '
                    f'{html.escape(_text(e.get("text")))}</li>')
            parts.append("</ul>")
        if sources:
            parts.append("<h4>Sources &amp; further reading</h4>")
            parts.append(
                "<p>This analysis draws on the World Bank's core guidance on climate "
                "action in fragile and conflict-affected settings. Linked titles open the "
                "World Bank publication page if you want to read more.</p><ul>"
            )
            for s in sources:
                sm = _mapping(s)
                title = html.escape(_text(sm.get("title")))
                desc = html.escape(_text(sm.get("description")))
                url = sm.get("url")
                if isinstance(url, str) and url.startswith("https://"):
                    label = f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{title}</a>'
                    tail = f" - {desc}" if desc else ""
                else:
                    note = " (reference only; no public link is shown until one is confirmed)"
                    label = title
                    tail = f" - {desc}{note}" if desc else note
                parts.append(f"<li>{label}{tail}</li>")
            parts.append("</ul>")
        d = _mapping(trail.get("diagnostics"))
        if d:
            parts.append('<details class="climate-fold"><summary>Run diagnostics</summary><ul>')
            parts.append(f'<li>Recommendation candidates: {html.escape(str(d.get("candidate_count")))} '
                         f'&rarr; admitted {html.escape(str(d.get("admitted_count")))} '
                         f'&rarr; final {html.escape(str(d.get("final_count")))}</li>')
            parts.append(f'<li>Conditional review: {html.escape(_text(d.get("reviewer_verdict")))}</li>')
            parts.append(f'<li>Live-research items used: {html.escape(str(d.get("live_research_count")))}</li>')
            parts.append(f'<li>Country-bank release: {html.escape(_text(d.get("bank_release")) or "none")}</li>')
            parts.append("</ul></details>")
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


def _docx_drafting(document: Document, label: str, value: object) -> None:
    block = _mapping(value)
    if not block:
        return
    document.add_heading(label, level=3)
    _docx_field(document, "Target document", block.get("target_document"))
    _docx_field(document, "Target section", block.get("target_section"))
    _docx_field(document, "Drafting status", block.get("drafting_status"))
    _docx_field(document, "Guidance basis", block.get("guidance_ids"))
    document.add_paragraph(_text(block.get("text")))


def write_reader_docx(model: dict[str, object], path: str | Path) -> Path:
    """Write the same reader dictionary to a compact Word document."""

    output = path if hasattr(path, "write") else Path(path)
    document = Document()
    if _text(model.get("runtime_mode")) == "smoke":
        paragraph = document.add_paragraph(SMOKE_RUNTIME_WARNING)
        if paragraph.runs:
            paragraph.runs[0].bold = True
    document.add_heading(HEADINGS[0], level=1)
    for _exec_para in re.split(r"\n\s*\n+", _text(model.get("executive_readout")).strip()):
        _exec_para = _exec_para.strip()
        if not _exec_para:
            continue
        _m = re.match(r"^(.*?[.!?])(\s+)([\s\S]*)$", _exec_para)
        _paragraph = document.add_paragraph()
        if _m:
            _paragraph.add_run(_m.group(1)).bold = True
            _paragraph.add_run(_m.group(2) + _m.group(3))
        else:
            _paragraph.add_run(_exec_para).bold = True
    if _text(model.get("evidence_status")) != "approved":
        _docx_field(document, "Evidence status", model.get("evidence_status"))

    document.add_heading(HEADINGS[1], level=1)
    for judgment in _records(model.get("judgments")):
        document.add_heading(_text(judgment.get("title")), level=2)
        description = _text(judgment.get("description"))
        if description:
            paragraph = document.add_paragraph(description)
            if paragraph.runs:
                paragraph.runs[0].italic = True
        _docx_field(document, "Judgment", judgment.get("value"))
        _docx_field(document, "Rationale", judgment.get("rationale"))
        _docx_field(
            document, "Evidence references", judgment.get("evidence_ids")
        )

    document.add_heading(HEADINGS[2], level=1)
    priorities = _records(model.get("priorities"))
    priority_summary = _mapping(model.get("priority_summary"))
    if _text(priority_summary.get("statement")):
        document.add_paragraph(_text(priority_summary.get("statement")))
    if not priorities:
        document.add_paragraph(_no_priority_message(model))
    for priority in priorities:
        rank = _rank(priority.get("rank"))
        identifier = _text(priority.get("recommendation_id"))
        document.add_heading(
            f"{rank}. {_text(priority.get('title'))} ({identifier})",
            level=2,
        )
        narrative = _text(priority.get("narrative"))
        if narrative:
            for para in re.split(r"\n\s*\n+", narrative.strip()):
                para = para.strip()
                if para:
                    document.add_paragraph(para)
        for label, key in PRIORITY_FIELDS:
            _docx_field(document, label, priority.get(key))
            if key == "minimum_action":
                _docx_drafting(
                    document, "Current document drafting",
                    priority.get("current_document_drafting"),
                )
                _docx_drafting(
                    document, "Operational instrument drafting",
                    priority.get("operational_instrument_drafting"),
                )

    document.add_heading(HEADINGS[3], level=1)
    document.add_paragraph(POINTS_TO_CHECK_INTRO)
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

    trail = _mapping(model.get("evidence_trail"))
    if trail:
        document.add_heading("How this analysis was produced", level=1)
        document.add_paragraph(_text(trail.get("methodology_note")))
        pathways = _records(trail.get("pathways"))
        if pathways:
            document.add_heading("Pathways", level=2)
            document.add_paragraph(
                "Pathways are the specific ways climate pressures and fragility feed into "
                "each other in this project. Each one is a short chain from a cause to an "
                "effect."
            )
            for p in pathways:
                document.add_paragraph(
                    f'{_text(p.get("direction_label"))}: {_text(p.get("chain_prose"))}')
        key = _records(trail.get("evidence_key"))
        if key:
            document.add_heading("Evidence key", level=2)
            document.add_paragraph(
                "The evidence key explains every reference code used above (for example "
                "PF- for a project fact, RG- for a residual gap, ER- for an existing "
                "response, PW- for a pathway), so each finding can be traced to its source."
            )
            for e in key:
                document.add_paragraph(
                    f'{_text(e.get("id"))} ({_text(e.get("type_label"))}): {_text(e.get("text"))}')
        sources = model.get("sources") or []
        if sources:
            document.add_heading("Sources & further reading", level=2)
            document.add_paragraph(
                "This analysis draws on the World Bank's core guidance on climate action "
                "in fragile and conflict-affected settings."
            )
            for s in sources:
                sm = _mapping(s)
                title = _text(sm.get("title"))
                desc = _text(sm.get("description"))
                url = sm.get("url")
                if isinstance(url, str) and url.startswith("https://"):
                    tail = f" - {desc}" if desc else ""
                    line = f"{title}{tail} ({url})"
                else:
                    note = " (reference only; no public link is shown until one is confirmed)"
                    line = f"{title} - {desc}{note}" if desc else f"{title}{note}"
                document.add_paragraph(line)
        d = _mapping(trail.get("diagnostics"))
        if d:
            document.add_heading("Run diagnostics", level=2)
            document.add_paragraph(
                f'Recommendation candidates: {d.get("candidate_count")} -> '
                f'admitted {d.get("admitted_count")} -> final {d.get("final_count")}; '
                f'conditional review: {_text(d.get("reviewer_verdict"))}; '
                f'live-research items used: {d.get("live_research_count")}; '
                f'country-bank release: {_text(d.get("bank_release")) or "none"}.')

    document.add_paragraph(_text(model.get("advisory_notice")))
    document.save(output)
    return output
