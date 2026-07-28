"""WBG-source climate-FCV core-question bank and relevance-trigger selector.

The bank is data lifted from the unrestricted climate-FCV frameworks under
docs/climate_module/ (Maximizing the Peace and Social Dividends of Climate
Action; the FCV-Sensitive Climate Action Framework; the Defueling Conflict
series; the Conflict-Sensitive Climate Action Compendium; the CCDR guidance
note). Each question belongs to one of six stable themes, carries a short
source attribution, and fires when its trigger keywords appear in the
project's Stage-1-derived signals. Surfacing stays at the theme level: the
selector returns, per theme, the triggered questions that shape that theme's
answer. Non-climate mode never calls this module.
"""

import re
from typing import Any

# Six stable themes (mirror sector_lenses.pipeline._CLIMATE_REFLECTION_KEYS).
THEMES = (
    "cq1_interaction",
    "cq2_maladaptation",
    "cq3_dividends",
    "cq4_inclusion",
    "cq5_institutions",
    "cq6_adaptive",
)

# id: stable; theme: one of THEMES; question: reader-neutral prompt;
# source: short attribution; triggers: lowercase keyword tokens (any match fires).
CLIMATE_QUESTION_BANK: list[dict[str, Any]] = [
    # cq1 interaction / delivery
    {"id": "cq1-hazard-delivery", "theme": "cq1_interaction",
     "question": "How do the country's material climate hazards interact with conflict/fragility to affect whether the project can be delivered?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["flood", "drought", "cyclone", "heat", "displacement", "conflict", "insecurity", "access"]},
    {"id": "cq1-access-security", "theme": "cq1_interaction",
     "question": "Could climate shocks compound insecurity to cut physical access to project sites, beneficiaries, or markets?",
     "source": "Defueling Conflict",
     "triggers": ["access", "insecurity", "armed", "displacement", "market", "supply", "transport"]},
    # cq2 maladaptation / lock-in
    {"id": "cq2-infra-horizon", "theme": "cq2_maladaptation",
     "question": "Is hard infrastructure sized to future climate regimes rather than the historical record, avoiding stranded-asset lock-in?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["infrastructure", "construction", "asset", "irrigation", "storage", "road", "flood", "coastal"]},
    {"id": "cq2-access-path-dependence", "theme": "cq2_maladaptation",
     "question": "Could siting, registration, or entitlement decisions entrench access patterns that later climate shifts make inequitable or unviable?",
     "source": "Conflict-Sensitive Climate Action Compendium",
     "triggers": ["land", "tenure", "registration", "allocation", "resource", "grazing", "water", "fisher"]},
    # cq3 dividends / root causes
    {"id": "cq3-peace-dividend", "theme": "cq3_dividends",
     "question": "Does the project engage a conflict root cause and create a credible peace or social dividend, not just outputs?",
     "source": "Maximizing the Peace and Social Dividends of Climate Action",
     "triggers": ["governance", "cohesion", "grievance", "resource", "inclusion", "reconciliation", "livelihood"]},
    {"id": "cq3-shared-benefit", "theme": "cq3_dividends",
     "question": "Are benefits structured so that rival or displaced groups share a stake rather than compete?",
     "source": "Maximizing the Peace and Social Dividends of Climate Action",
     "triggers": ["refugee", "host", "displacement", "pastoral", "shared", "benefit", "cross-border"]},
    # cq4 inclusion / vulnerability
    {"id": "cq4-vulnerable-reach", "theme": "cq4_inclusion",
     "question": "Are the most climate- and conflict-vulnerable regions and groups actually reached and protected?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["women", "gender", "youth", "displacement", "refugee", "vulnerable", "food", "poverty"]},
    {"id": "cq4-inclusion-under-stress", "theme": "cq4_inclusion",
     "question": "Will inclusion commitments survive a shock, or erode back to the pre-project pattern when a flood or clash hits?",
     "source": "Conflict-Sensitive Climate Action Compendium",
     "triggers": ["women", "gender", "quota", "displacement", "committee", "community"]},
    # cq5 institutions / HDP
    {"id": "cq5-delivery-institutions", "theme": "cq5_institutions",
     "question": "Is delivery routed through institutions appropriate to the fragility context, with the right balance of community and state?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["community", "government", "institution", "capacity", "co-management", "decentral", "local"]},
    {"id": "cq5-hdp-nexus", "theme": "cq5_institutions",
     "question": "Does the project coordinate across the humanitarian-development-peace nexus where displacement and humanitarian operations overlap?",
     "source": "Defueling Conflict",
     "triggers": ["unhcr", "humanitarian", "refugee", "host", "nexus", "hdp", "displacement"]},
    # cq6 adaptive / horizons
    {"id": "cq6-adaptive-triggers", "theme": "cq6_adaptive",
     "question": "Is the design adaptive to uncertainty, with triggers and monitoring for climate and conflict change rather than a static plan?",
     "source": "CCDR guidance note",
     "triggers": ["monitoring", "adaptive", "trigger", "results framework", "m&e", "uncertainty", "early warning"]},
    {"id": "cq6-time-horizons", "theme": "cq6_adaptive",
     "question": "Does the design account for the different time horizons in play - near-term shock, project-lifetime cycle, asset-lifetime climate shift?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["infrastructure", "asset", "long-term", "projection", "horizon", "flood", "climate projection"]},
]

# Named reader-facing sources for the section intro (order = display order).
BANK_SOURCE_HEADLINE = (
    "Maximizing the Peace and Social Dividends of Climate Action",
    "the FCV-Sensitive Climate Action Framework",
    "the Defueling Conflict (peace and social dividends) series",
)


def _project_signal_blob(project_signals: Any) -> str:
    """Return normalized text for deterministic trigger matching."""

    if isinstance(project_signals, (list, tuple, set)):
        return " ".join(str(signal) for signal in project_signals).lower()
    return str(project_signals or "").lower()


def _triggered_question_ids(project_signals: Any) -> set[str]:
    """Return bank IDs whose complete trigger tokens or phrases occur."""

    blob = _project_signal_blob(project_signals)
    return {
        question["id"]
        for question in CLIMATE_QUESTION_BANK
        if any(
            re.search(rf"(?<!\w){re.escape(trigger)}(?!\w)", blob)
            for trigger in question["triggers"]
        )
    }


def select_triggered_questions(project_signals: Any) -> dict[str, list[dict[str, Any]]]:
    """Return, per theme, the bank questions whose triggers fire for this project.

    project_signals: any object convertible to a lowercase text blob (a string,
    or a list of strings) built from Stage 1 (instrument, sector, hazards,
    components, geography). Matching is boundary-aware and case-insensitive.
    Themes with no fired question are omitted. cq1 always returns its bank set
    even if triggers are thin, because the two interaction directions are
    always answered (the caller guarantees Q1/Q2).
    """

    triggered_ids = _triggered_question_ids(project_signals)

    fired: dict[str, list[dict[str, Any]]] = {}
    for q in CLIMATE_QUESTION_BANK:
        if q["id"] in triggered_ids:
            fired.setdefault(q["theme"], []).append(q)
    # Guarantee cq1 is present (interactions are always answered).
    if "cq1_interaction" not in fired:
        fired["cq1_interaction"] = [
            q for q in CLIMATE_QUESTION_BANK if q["theme"] == "cq1_interaction"
        ]
    return fired


def build_question_plan(project_signals: Any) -> dict[str, Any]:
    """Return stable anchor groups and eligible supplementary questions.

    ``anchors`` retains the existing six-theme trigger selection contract.
    Supplementary candidates are a deterministic shortlist, not a coverage
    target: callers may answer zero to four only when a fired bank question
    identifies a distinct, material project issue not covered by an anchor.
    """

    anchors = select_triggered_questions(project_signals)
    triggered_ids = _triggered_question_ids(project_signals)
    supplementary_candidates: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for question in CLIMATE_QUESTION_BANK:
        question_id = question["id"]
        if question_id not in triggered_ids or question_id in seen_ids:
            continue
        supplementary_candidates.append({
            key: question[key]
            for key in ("id", "theme", "question", "source")
        })
        seen_ids.add(question_id)
    return {
        "anchors": anchors,
        "supplementary_candidates": supplementary_candidates,
    }
