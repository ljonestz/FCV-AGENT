"""User-selected review stage and the due-diligence checklist (Render build).

The upload screen asks where the operation is in the review process. The
answer is optional: an empty answer, or "Not sure", leaves the run exactly as
it is today (document detection plus ``regime_router`` decide the route).

When the user picks a stage, it is treated as their assertion:
- ``apply_review_stage`` pins the preparation regime / processing model that
  drive the regime header, timing vocabulary and reference floors;
- ``review_stage_prompt_block`` adds a short framing block to Stage 2 and 3;
- ``stage_conflict_notice`` returns one neutral sentence when the documents
  look different from the choice.

The checklist question wording follows the FCV due-diligence proposal
(October 2026), Annex I and the seven key questions; cleared for the repo by
the owner on 2026-11-16. The model returns only ``question_id`` and a plain
note; the question text is held here so the model never rewrites it.
"""

from __future__ import annotations

import re

AUTO = ""

# key -> (label, group, column, regime override, processing model override)
# column: which checklist question set applies ("td", "ir", "impl", "key");
# None means no checklist (legacy process).
REVIEW_STAGES: dict[str, dict] = {
    "td": {
        "label": "Technical Design review",
        "group": "new",
        "column": "td",
        "regime": "new_model",
        "processing_model": "two_step",
    },
    "ir": {
        "label": "Implementation Readiness review",
        "group": "new",
        "column": "ir",
        "regime": "new_model",
        "processing_model": "two_step",
    },
    "one_review": {
        "label": "One Review",
        "group": "new",
        "column": "key",
        "regime": "new_model",
        "processing_model": "one_step",
    },
    "concept": {
        "label": "Concept stage (PCN / PID, legacy process)",
        "group": "legacy",
        "column": None,
        "regime": "legacy_transitional",
        "processing_model": None,
    },
    "appraisal": {
        "label": "Appraisal / Decision Review (PAD, legacy process)",
        "group": "legacy",
        "column": None,
        "regime": "legacy_transitional",
        "processing_model": None,
    },
    "af_restructuring": {
        "label": "Additional Financing or Restructuring",
        "group": "either",
        "column": "impl",
        "regime": None,
        "processing_model": None,
    },
}

_ALIASES = {"auto": AUTO, "not_sure": AUTO, "detect": AUTO, "none": AUTO}

CHECKLIST_ELEMENTS: list[tuple[str, str]] = [
    ("context", "Country context and FCV risks"),
    ("design", "Operational design and targeting"),
    ("feasibility", "Implementation and operational feasibility"),
    ("engagement", "Stakeholder engagement and grievance redress"),
    ("risk", "Risk management and adaptation"),
    ("results", "Results framework and monitoring"),
    ("actors", "Security actors, elite structures and non-state actors"),
]

CHECKLIST_QUESTIONS: dict[str, dict[str, str]] = {
    "context": {
        "key": ("Does the operation respond to the country context, priority FCV drivers, risks, "
                "resilience factors, or trajectory-shifting opportunities identified through "
                "diagnostics and country engagement?"),
        "td": ("Do current diagnostics identify priority risks, drivers, resilience and political "
               "economy? Do the PDO, Theory of Change and components reflect FCV context and "
               "relevant opportunities?"),
        "ir": ("Have teams validated the FCV analysis and design assumptions against current "
               "conditions before implementation?"),
        "impl": "Have shifts in conflict, displacement, governance or politics changed relevance or assumptions?",
    },
    "design": {
        "key": ("Are project development objectives, Theory of Change, beneficiaries, geographic "
                "targeting, activities, institutional arrangements, and partnerships designed in a "
                "manner that will not exacerbate FCV risks?"),
        "td": ("Are objectives, components, beneficiaries, geography and delivery appropriate, "
               "inclusive, free of exclusion risks and designed to avoid tensions?"),
        "ir": ("Are targeting criteria and delivery arrangements ready to apply the agreed "
               "inclusive, context-appropriate design?"),
        "impl": "Do targeting and delivery remain appropriate for displaced or hard-to-reach groups?",
    },
    "feasibility": {
        "key": ("Can the operation be implemented effectively under FCV conditions, taking into "
                "account governance and institutional capacity, access constraints, security risks, "
                "implementation arrangements, and available FCV operational flexibilities?"),
        "td": ("Have capacity, access, security, data and delivery constraints informed design? Are "
               "Procurement/HEIS, FM and ESF flexibilities justified?"),
        "ir": "Are roles, partners, costs and delivery arrangements feasible and ready for implementation?",
        "impl": "Are capacity, partners, supervision and remote-delivery arrangements still adequate?",
    },
    "engagement": {
        "key": ("Who needs to participate, and what barriers could exclude affected groups? Are "
                "consultation, communication, citizen engagement and grievance mechanisms safe, "
                "accessible and ready to operate?"),
        "td": "Who needs to participate, and what barriers could exclude affected groups?",
        "ir": ("Are consultation, communication, citizen engagement and grievance mechanisms safe, "
               "accessible and ready to operate?"),
        "impl": "Do participation and grievance arrangements remain inclusive and effective?",
    },
    "risk": {
        "key": ("Have FCV-related risks and potential unintended consequences been identified and are "
                "there adequate mitigation and adaptive management measures throughout implementation?"),
        "td": ("What unintended effects and fiduciary, institutional or operational risks could arise? "
               "Do mitigation measures match identified risks and enable adaptation?"),
        "ir": "Are the proposed mitigation, safeguard and accountability arrangements ready to operate?",
        "impl": ("Have risks or unintended effects changed? What adjustments to sequencing or delivery "
                 "are needed?"),
    },
    "results": {
        "key": ("Will the operation be able to monitor, demonstrate, and learn from its contribution to "
                "development outcomes, resilience, and (where relevant) the reduction of FCV drivers or "
                "strengthening of resilience?"),
        "td": "Are results realistic? Is there a plausible opportunity to address FCV drivers or resilience?",
        "ir": ("Are monitoring arrangements ready to track development and relevant FCV outcomes, "
               "changing risks and early warnings?"),
        "impl": "Does timely evidence inform course correction and demonstrate relevant FCV contributions?",
    },
    "actors": {
        "key": ("Could security actors, elite capture or non-state actors affect the operation? Are "
                "partnerships, safeguards and accountability arrangements ready to address interfaces "
                "with these actors and associated risks?"),
        "td": "Could security actors, elite capture or non-state actors affect the operation?",
        "ir": ("Are partnerships, safeguards and accountability arrangements ready to address "
               "interfaces with these actors and associated risks?"),
        "impl": "Have these relationships changed, requiring revised partnerships or mitigation?",
    },
}

COLUMN_LABELS = {
    "td": "Technical Design review",
    "ir": "Implementation Readiness review",
    "impl": "During implementation",
    "key": "Key questions",
}

LEGACY_CHECKLIST_NOTE = (
    "A due-diligence checklist is not needed for this operation: the checklist follows the "
    "new operating model reviews (Technical Design, Implementation Readiness or One Review), "
    "and this operation follows the legacy preparation process."
)

CHECKLIST_MIN_ROWS = 4
CHECKLIST_MAX_ROWS = 6
_NOTE_MAX_CHARS = 420

_REVIEW_FOCUS = {
    "td": ("whether the FCV context, key risks and relevant diagnostics have been identified; whether "
           "the intervention is appropriate given the political, institutional and security context; "
           "whether beneficiary selection and geographic targeting may create risks of exclusion or "
           "tensions; and whether opportunities exist to strengthen resilience or address FCV drivers"),
    "ir": ("whether components and implementation arrangements remain fit for purpose given FCV "
           "realities; whether stakeholder engagement, targeting and grievance mechanisms are adapted to "
           "the context and ready to operate; whether implementation, fiduciary, security, institutional "
           "and operational risks are adequately addressed; and whether results can reasonably be "
           "achieved without exacerbating FCV dynamics"),
    "one_review": ("both design questions (FCV context and diagnostics, appropriateness of the "
                   "intervention, targeting risks, resilience opportunities) and readiness questions "
                   "(arrangements, engagement and grievance mechanisms, and risk measures ready to "
                   "operate), since this single review covers both"),
    "af_restructuring": ("whether FCV risks have evolved since approval; whether geographic targeting, "
                         "implementation arrangements and mitigation measures remain appropriate; and "
                         "what adaptation the changes in conflict, insecurity, displacement, governance "
                         "or political conditions require"),
}

_REVIEW_TIMING = {
    "td": ("The current gate is the Technical Design review. Time actions as at-TD-review, "
           "between-TD-and-IR, before-IR, before-negotiations, before-Board or "
           "during-implementation-support; do not time actions for a gate already passed "
           "(shortly-after-OIS)."),
    "ir": ("The current gate is the Implementation Readiness review; the Technical Design review has "
           "passed. Time actions as at-IR, before-negotiations, before-Board or "
           "during-implementation-support; do not use before-TD-review, at-TD-review or "
           "between-TD-and-IR."),
    "one_review": ("The current gate is the One Review. Time actions as at-One-Review, "
                   "before-negotiations, before-Board or during-implementation-support; do not use "
                   "TD/IR timing."),
    "concept": ("This is the legacy process at concept stage. Use the legacy timing vocabulary (during "
                "preparation, before appraisal, at Decision Review, before negotiations, before Board, "
                "during implementation). Do not use Technical Design, Implementation Readiness or One "
                "Review timing."),
    "appraisal": ("This is the legacy process at appraisal / Decision Review. Use the legacy timing "
                  "vocabulary (before Decision Review, before negotiations, before Board, during "
                  "implementation). Do not use Technical Design, Implementation Readiness or One Review "
                  "timing."),
    "af_restructuring": ("Time actions as before approval of the Additional Financing or restructuring, "
                         "or during implementation support."),
}


def normalize_review_stage(value) -> str:
    """Return a known stage key, or AUTO ("") for empty / not sure / unknown."""
    key = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    key = _ALIASES.get(key, key)
    return key if key in REVIEW_STAGES else AUTO


def apply_review_stage(regime_context: dict | None, review_stage) -> dict:
    """Return the regime context the run should use.

    AUTO returns the input unchanged (same object contents) so runs without a
    selection are byte-for-byte as today. A selected stage pins the regime and,
    for new-model stages, the processing model. The detected values are kept
    under ``detected_*`` keys for the conflict notice.
    """
    regime = dict(regime_context or {})
    stage = normalize_review_stage(review_stage)
    if stage == AUTO:
        return regime
    spec = REVIEW_STAGES[stage]
    regime.setdefault("detected_preparation_regime", regime.get("preparation_regime", "unresolved_policy_source"))
    regime.setdefault("detected_processing_model", regime.get("processing_model", "unknown"))
    if spec["regime"]:
        regime["preparation_regime"] = spec["regime"]
    if spec["processing_model"]:
        regime["processing_model"] = spec["processing_model"]
    regime["review_stage"] = stage
    return regime


def stage_conflict_notice(regime_context: dict | None, review_stage) -> str:
    """One neutral sentence when the selection and detection materially disagree."""
    stage = normalize_review_stage(review_stage)
    if stage == AUTO:
        return ""
    spec = REVIEW_STAGES[stage]
    regime = regime_context or {}
    detected = str(regime.get("detected_preparation_regime", regime.get("preparation_regime", "")) or "").lower()
    detected_pm = str(regime.get("detected_processing_model", regime.get("processing_model", "")) or "").lower()
    looks = ""
    if spec["group"] == "new" and detected == "legacy_transitional":
        looks = "a legacy-process operation"
    elif spec["group"] == "legacy" and detected == "new_model":
        looks = "a new operating model operation"
    elif stage in {"td", "ir"} and detected == "new_model" and detected_pm in {"one_step", "one_review"}:
        looks = "a one-step (One Review) operation"
    elif stage == "one_review" and detected == "new_model" and detected_pm == "two_step":
        looks = "a two-step (Technical Design and Implementation Readiness) operation"
    if not looks:
        return ""
    return f"The documents look like {looks}; the note is framed for the {spec['label']} as chosen."


def review_stage_prompt_block(review_stage) -> str:
    """Stage 2/3 framing block for a selected stage; "" when nothing was selected."""
    stage = normalize_review_stage(review_stage)
    if stage == AUTO:
        return ""
    spec = REVIEW_STAGES[stage]
    nl = chr(10)
    lines = [
        "REVIEW STAGE (selected by the user)",
        (f"- The user has said this operation is at the {spec['label']}. Frame the advice for that "
         "review. Where the documents suggest a different stage, follow the user's choice and do not "
         "argue the point."),
    ]
    focus = _REVIEW_FOCUS.get(stage)
    if focus:
        lines.append(f"- At this review the advice concentrates on {focus}.")
    lines.append(f"- {_REVIEW_TIMING[stage]}")
    return nl.join(lines) + nl + nl


def checklist_column(review_stage, regime_context: dict | None, review_mode: str = "design"):
    """Return ("td"|"ir"|"impl"|"key", None) or (None, note) for the checklist.

    Implementation reviews (MTR/ISR) use the during-implementation questions.
    A selected stage decides the column. Without a selection, a detected new
    model run gets the key questions; a detected legacy run gets the short
    "not needed" note; an unresolved run gets neither.
    """
    if str(review_mode or "").strip().lower() == "implementation":
        return "impl", ""
    stage = normalize_review_stage(review_stage)
    if stage != AUTO:
        column = REVIEW_STAGES[stage]["column"]
        return (column, "") if column else (None, LEGACY_CHECKLIST_NOTE)
    regime = str((regime_context or {}).get("preparation_regime", "") or "").lower()
    if regime == "new_model":
        return "key", ""
    if regime == "legacy_transitional":
        return None, LEGACY_CHECKLIST_NOTE
    return None, ""


def question_id(element: str, column: str) -> str:
    return f"{element}_{column}"


def question_text(qid: str) -> tuple[str, str]:
    """Return (element label, question) for a known id, else ("", "")."""
    element, _, column = str(qid or "").rpartition("_")
    labels = dict(CHECKLIST_ELEMENTS)
    if element in CHECKLIST_QUESTIONS and column in CHECKLIST_QUESTIONS[element]:
        return labels[element], CHECKLIST_QUESTIONS[element][column]
    return "", ""


def checklist_prompt_block(column) -> str:
    """Stage 3 instruction asking for the optional ``dd_checklist`` JSON field."""
    if not column:
        return ""
    nl = chr(10)
    rows = [
        f'- "{question_id(element, column)}" ({label}): {CHECKLIST_QUESTIONS[element][column]}'
        for element, label in CHECKLIST_ELEMENTS
    ]
    return (
        nl + nl + "DUE-DILIGENCE CHECKLIST (one extra top-level field in the same JSON block)" + nl
        + f'Add "dd_checklist": an array of {CHECKLIST_MIN_ROWS} to {CHECKLIST_MAX_ROWS} objects, one for '
        + "each of the most relevant questions below, in the order listed. Leave out a question when the "
        + "analysis has nothing material to say on it (for example, no interface with security or "
        + 'non-state actors). Each object is {"question_id": "<id below>", "note": "<one or two plain '
        + 'sentences>"}.' + nl
        + "The note says what the package shows on that question and where to look (a section of this "
        + "note, a priority, or a named section of the project document). Do not restate the analysis; "
        + "point to it. Where the question repeats one of the FCV Operational Manual's key questions, say "
        + "so in a few words. Write plain notes only: no ratings, scores, yes/no answers, status words "
        + "(such as met, partial, gap, adequate) or labels. Do not copy the question text; the interface "
        + "shows it." + nl
        + "Questions:" + nl + nl.join(rows) + nl
    )


_STATUS_PREFIX = re.compile(
    r"^\s*(?:\*\*)?(?:yes|no|partly|partially|partial|met|not met|gap|adequate|inadequate|"
    r"strong|weak|n/?a)(?:\*\*)?\s*[:.\-–]\s*",
    re.IGNORECASE,
)


def normalize_dd_checklist(raw, column=None) -> list[dict]:
    """Validate the model's ``dd_checklist`` rows.

    Keeps only known question ids (the column's ids when ``column`` is given),
    drops duplicates and empty notes, strips a leading status word, caps the
    note length and the row count, and returns rows in the bank's order with
    the question text attached.
    """
    if not isinstance(raw, list):
        return []
    order = {element: i for i, (element, _) in enumerate(CHECKLIST_ELEMENTS)}
    seen: set[str] = set()
    rows: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        qid = str(item.get("question_id", "") or "").strip()
        element, _, col = qid.rpartition("_")
        if column and col != column:
            continue
        label, question = question_text(qid)
        note = _STATUS_PREFIX.sub("", str(item.get("note", "") or "").strip()).strip()
        if not question or not note or qid in seen:
            continue
        if len(note) > _NOTE_MAX_CHARS:
            cut = note[:_NOTE_MAX_CHARS]
            stop = cut.rfind(". ")
            note = cut[: stop + 1] if stop > 80 else cut.rstrip() + "..."
        seen.add(qid)
        rows.append({"question_id": qid, "element": label, "question": question, "note": note,
                     "_order": order.get(element, 99)})
    rows.sort(key=lambda r: r["_order"])
    for row in rows:
        row.pop("_order", None)
    return rows[:CHECKLIST_MAX_ROWS]
