"""Pure contracts for the dedicated Climate-FCV route."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

import climate_question_bank

from .research import format_climate_research_context


CLIMATE_NATIVE_SCHEMA_VERSION = "climate-native-v1"
CLIMATE_REQUIRED_DIRECTIONS = {
    "climate-fcv-on-project",
    "project-on-climate-fcv",
}
CLIMATE_REQUIRED_LENS_FIELDS = {
    "materiality_level",
    "materiality_summary",
    "executive_summary",
    "integration_rating",
    "integration_summary",
    "operating_context",
    "interaction_readout",
    "strengths_weaknesses",
    "reflections",
}
_CLIMATE_BASELINE_FIELDS = (
    "sensitivity_rating",
    "responsiveness_rating",
    "sensitivity_reasoning",
    "responsiveness_reasoning",
    "evidence_trail",
)
_CLIMATE_CONTEXT_FIELDS = (
    "fcv_setting",
    "climate_setting",
    "intersection",
)


def _climate_lens(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    lenses = payload.get("lenses")
    if not isinstance(lenses, list):
        return None
    return next(
        (
            item
            for item in lenses
            if isinstance(item, dict) and item.get("lens_id") == "climate"
        ),
        None,
    )


def climate_missing_fields(payload: Any) -> list[str]:
    """Return stable dotted paths absent from a canonical Climate payload."""

    if not isinstance(payload, dict):
        return ["schema_version", "fcv_baseline", "lenses.climate"]

    missing: list[str] = []
    if payload.get("schema_version") != CLIMATE_NATIVE_SCHEMA_VERSION:
        missing.append("schema_version")

    baseline = payload.get("fcv_baseline")
    if not isinstance(baseline, dict):
        missing.append("fcv_baseline")
    else:
        for key in _CLIMATE_BASELINE_FIELDS:
            if not baseline.get(key):
                missing.append(f"fcv_baseline.{key}")

    climate = _climate_lens(payload)
    if climate is None:
        missing.append("lenses.climate")
        return missing

    for key in sorted(CLIMATE_REQUIRED_LENS_FIELDS):
        if not climate.get(key):
            missing.append(f"lenses.climate.{key}")

    operating_context = climate.get("operating_context")
    if isinstance(operating_context, dict):
        for key in _CLIMATE_CONTEXT_FIELDS:
            if not operating_context.get(key):
                missing.append(f"lenses.climate.operating_context.{key}")

    interactions = climate.get("interaction_readout")
    directions = {
        item.get("direction_id")
        for item in interactions
        if isinstance(item, dict)
    } if isinstance(interactions, list) else set()
    for direction in sorted(CLIMATE_REQUIRED_DIRECTIONS - directions):
        missing.append(f"lenses.climate.interaction_readout.{direction}")
    return missing


_MISSING = object()


def _value_at_path(value: Any, path: tuple[str, ...]) -> Any:
    current = value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return _MISSING
        current = current[key]
    return current


def _set_path(
    target: dict[str, Any],
    path: tuple[str, ...],
    value: Any,
) -> None:
    current = target
    for key in path[:-1]:
        child = current.get(key)
        if not isinstance(child, dict):
            child = {}
            current[key] = child
        current = child
    current[path[-1]] = deepcopy(value)


def merge_climate_repair(
    primary: dict[str, Any],
    repair: dict[str, Any],
    requested_fields: list[str],
) -> dict[str, Any]:
    """Deep-copy only explicitly requested canonical Climate paths."""

    result = deepcopy(primary) if isinstance(primary, dict) else {}
    incoming = repair if isinstance(repair, dict) else {}
    allowed = set(requested_fields)

    if "schema_version" in allowed and "schema_version" in incoming:
        result["schema_version"] = deepcopy(incoming["schema_version"])

    repair_baseline = incoming.get("fcv_baseline")
    if "fcv_baseline" in allowed and isinstance(repair_baseline, dict):
        result["fcv_baseline"] = deepcopy(repair_baseline)
    else:
        for requested in sorted(allowed):
            prefix = "fcv_baseline."
            if not requested.startswith(prefix):
                continue
            relative_path = tuple(requested[len(prefix):].split("."))
            incoming_value = _value_at_path(
                repair_baseline, relative_path
            )
            if incoming_value is _MISSING:
                continue
            result_baseline = result.get("fcv_baseline")
            if not isinstance(result_baseline, dict):
                result_baseline = {}
                result["fcv_baseline"] = result_baseline
            _set_path(result_baseline, relative_path, incoming_value)

    raw_result_lenses = result.get("lenses")
    result_lenses = (
        raw_result_lenses
        if isinstance(raw_result_lenses, list)
        else None
    )
    repair_climate = _climate_lens(incoming)
    result_climate = _climate_lens(result)

    if "lenses.climate" in allowed and isinstance(repair_climate, dict):
        replacement_lens = deepcopy(repair_climate)
        if result_lenses is None:
            result_lenses = []
            result["lenses"] = result_lenses
        if result_climate is None:
            result_lenses.append(replacement_lens)
        else:
            climate_index = next(
                index
                for index, item in enumerate(result_lenses)
                if item is result_climate
            )
            result_lenses[climate_index] = replacement_lens
        result_climate = replacement_lens
    else:
        for requested in sorted(allowed):
            prefix = "lenses.climate."
            if not requested.startswith(prefix):
                continue
            direction_prefix = (
                "lenses.climate.interaction_readout."
            )
            if requested.startswith(direction_prefix):
                direction_id = requested[len(direction_prefix):]
                if direction_id not in CLIMATE_REQUIRED_DIRECTIONS:
                    continue
                repair_interactions = (
                    repair_climate.get("interaction_readout")
                    if isinstance(repair_climate, dict)
                    else None
                )
                incoming_interaction = next(
                    (
                        item
                        for item in repair_interactions
                        if isinstance(item, dict)
                        and item.get("direction_id") == direction_id
                    ),
                    None,
                ) if isinstance(repair_interactions, list) else None
                if incoming_interaction is None:
                    continue
                if result_climate is None:
                    if result_lenses is None:
                        result_lenses = []
                        result["lenses"] = result_lenses
                    result_climate = {"lens_id": "climate"}
                    result_lenses.append(result_climate)
                result_interactions = result_climate.get(
                    "interaction_readout"
                )
                if not isinstance(result_interactions, list):
                    result_interactions = []
                    result_climate["interaction_readout"] = (
                        result_interactions
                    )
                existing_index = next(
                    (
                        index
                        for index, item in enumerate(
                            result_interactions
                        )
                        if isinstance(item, dict)
                        and item.get("direction_id") == direction_id
                    ),
                    None,
                )
                if existing_index is None:
                    result_interactions.append(
                        deepcopy(incoming_interaction)
                    )
                else:
                    result_interactions[existing_index] = deepcopy(
                        incoming_interaction
                    )
                continue
            relative_path = tuple(requested[len(prefix):].split("."))
            incoming_value = _value_at_path(
                repair_climate, relative_path
            )
            if incoming_value is _MISSING:
                continue
            if result_climate is None:
                if result_lenses is None:
                    result_lenses = []
                    result["lenses"] = result_lenses
                result_climate = {"lens_id": "climate"}
                result_lenses.append(result_climate)
            _set_path(result_climate, relative_path, incoming_value)

    if not isinstance(result.get("findings"), list):
        result["findings"] = []
    return result

_LENS_DIAGNOSTIC_START = "%%%LENS_DIAGNOSTIC_START%%%"
_LENS_DIAGNOSTIC_END = "%%%LENS_DIAGNOSTIC_END%%%"
_STAGE3_JSON_START = "%%%JSON_START%%%"
_STAGE3_JSON_END = "%%%JSON_END%%%"
_INTEGRATION_SCALE = (
    "Extremely Low", "Very Low", "Low", "Adequate",
    "Well Embedded", "Very Well Embedded",
)


def _selected_instrument_route(instrument_type: str) -> str:
    instrument = str(instrument_type or "").strip().lower()
    if instrument in {"pforr", "p4r", "program-for-results"}:
        return "PforR -> ESSA, PAP, DLIs, and borrower systems"
    if instrument in {"dpf", "dpo", "development policy financing"}:
        return (
            "DPF/DPO -> Program Document, prior actions, PSIA, and "
            "environmental/natural-resource analysis (SORT only where applicable)"
        )
    return "IPF -> ESF instruments and applicable ESS"


def _canonical_stage2_outline() -> dict[str, Any]:
    pathway = {
        "pathway_id": "stable project-specific ID",
        "pressure": "climate or FCV pressure",
        "mechanism": "mediated mechanism",
        "project_implication": "named project implication",
        "design_response": "current response or gap and proportionate adaptation",
        "project_elements": [], "geographies": [], "affected_groups": [],
        "systems_or_assets": [], "time_horizons": [],
        "research_claim_ids": [], "confidence": "high|medium|low",
        "evidence_gap": "",
    }
    return {
        "schema_version": CLIMATE_NATIVE_SCHEMA_VERSION,
        "fcv_baseline": {
            "sensitivity_rating": "", "responsiveness_rating": "",
            "sensitivity_reasoning": "", "responsiveness_reasoning": "",
            "evidence_trail": [{
                "claim": "", "source_ids": [], "project_anchor": "",
            }],
        },
        "lenses": [{
            "lens_id": "climate",
            "applicability": "material|possible|not_applicable",
            "materiality_level": "high|medium|low",
            "materiality_summary": "", "executive_summary": "",
            "integration_level": (
                "well_integrated|partly_integrated|weakly_integrated|"
                "insufficient_evidence"
            ),
            "integration_summary": "",
            "operating_context": {
                "fcv_setting": "", "climate_setting": "", "intersection": "",
            },
            "interaction_readout": [
                {
                    "direction_id": "climate-fcv-on-project",
                    "summary": "", "pathways": [pathway],
                },
                {
                    "direction_id": "project-on-climate-fcv",
                    "summary": "", "pathways": [pathway],
                },
            ],
            "strengths_weaknesses": [
                {"side": "strength|gap", "title": "", "text": ""},
            ],
            "reflections": [{
                "question_key": "cq1_interaction", "title": "",
                "status_cue": "", "source": "", "text": "",
            }],
            "supplementary_questions": [{
                "question_id": "known bank ID", "title": "",
                "status_cue": "", "source": "", "text": "",
            }],
            "readout_sections": [], "additional_pathways": [],
            "other_pathways": [],
        }],
        "findings": [],
    }


def build_climate_stage2_prompt(
    *,
    instrument_type: str,
    document_type: str,
    temporal_guardrail: str,
    regime_header: str,
    project_signals: Any,
    climate_research: Any,
    priority_questions: str,
) -> str:
    """Build the dedicated Climate-FCV assessment prompt."""

    question_plan = climate_question_bank.build_question_plan(project_signals)
    anchors = question_plan["anchors"]
    candidates = question_plan["supplementary_candidates"]
    research_context = format_climate_research_context(climate_research)
    route = _selected_instrument_route(instrument_type)
    schema = json.dumps(
        _canonical_stage2_outline(), ensure_ascii=False, separators=(",", ":")
    )
    question_context = json.dumps(
        {"anchors": anchors, "supplementary_candidates": candidates},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"""You are producing the dedicated Climate-FCV Stage 2 assessment for a World Bank operation.
Instrument: {instrument_type or 'Unknown'}
Document type: {document_type or 'Unknown'}
{regime_header}
{temporal_guardrail}

ARCHITECTURE BOUNDARY
Produce exactly one canonical Climate-FCV payload. It is the single source of truth for all later rendering, repair, export, and Stage 3 priorities; do not create duplicate visible or hidden analytical copies. Do not run, enumerate, or recreate the generic 12 OST / 12 operational standards assessment, DNH-9 / 9 Do No Harm checklist, 25-question map, UNDER_HOOD block, or generic recommendation-by-recommendation machinery. The compact fcv_baseline is the only FCV baseline required.

OUTPUT CONTRACT
Return only one JSON object between {_LENS_DIAGNOSTIC_START} and {_LENS_DIAGNOSTIC_END}. Use schema_version {CLIMATE_NATIVE_SCHEMA_VERSION}. Follow this exact canonical field structure:
{schema}
Populate every required canonical field. Do not add prose outside the delimiter block.

ANALYTICAL DEPTH
Write a concise but substantive executive_summary and operating_context covering the FCV setting, climate setting, and their intersection. Complete both mandatory interaction directions. Every material pathway must trace: pressure -> mediated mechanism -> named project implication -> current response or gap -> proportionate adaptation. Name specific components, subcomponents, activities, locations, beneficiaries, institutions, delivery arrangements, indicators, financing features, and document sections whenever evidence supports them. Do not fabricate a project fact, source, commitment, location, group, institution, or causal claim. Record source IDs and evidence gaps.

Give detailed, decision-relevant strengths_weaknesses. Address material reflections across the six stable anchors: cq1_interaction, cq2_maladaptation, cq3_dividends, cq4_inclusion, cq5_institutions, cq6_adaptive. Preserve readout_sections, pathways, source IDs, and the six-tier integration scale exactly: {', '.join(_INTEGRATION_SCALE)}.

QUESTION PLAN
The six anchors remain the stable core. The following bank-backed plan is selected from project signals:
{question_context}
Supplementary questions are optional. Surface zero to four only. This is a payload bound, not a coverage target. Include a candidate only when it identifies a distinct, material, project-specific issue not adequately covered under an anchor; use only the known candidate question_id and otherwise omit it.

VALIDATED EXTERNAL CLIMATE-FCV RESEARCH
{research_context or 'No validated research context was supplied; do not invent external evidence.'}
User priority questions:
{priority_questions or 'None supplied.'}
Tie every research claim used to its source ID and named project element.

INSTRUMENT AND OPCS CALIBRATION
Selected instrument route: {route}.
Instrument-route each conclusion before naming a project instrument. IPF -> ESF instruments and applicable ESS. PforR -> ESSA, PAP, DLIs, borrower systems, and never IPF ESS/ESCP/CERC. DPF/DPO -> Program Document, prior actions, PSIA, environmental/natural-resource analysis, and SORT only where applicable. Never apply IPF ESS/ESCP/CERC to standalone PforR or DPF/DPO.

This is advisory: flag and point to the responsible process or specialist, but never determine Paris Alignment, CDRS, ESF/ESS/ESRC, climate resilience, or screening adequacy. CCDR is optional evidence where available, not a mandatory process step or routine recommendation.

Use an asset-appropriate design horizon under applicable standards; do not impose a universal 20-50 year projection. Adaptive triggers and actor-level analysis are risk-based analytical good practice unless a formal project or source commitment makes them mandatory. Use conditional compound-risk language such as 'may intensify' and 'could interact with'. Never state that climate will cause conflict, that the project guarantees a peace dividend, or that an operation is maladaptive as a compliance finding.

CERC is relevant only for IPF where there is a named eligible natural-hazard, climate, health, or economic emergency, a plausible government declaration and activation pathway, and a PDO link. Never recommend an IPF-style CERC for standalone PforR or DPF; never make a generic flexibility recommendation.

Treat the FCV-Sensitive Climate Action Framework, Peace and Social Dividends work, Defueling Conflict, the compendium, and CCDRs as analytical / good-practice evidence, not OPCS policy or compliance authority. Separate policy, directive, procedure, and guidance from analytical or reviewer judgment. Use requirement language only where a source establishes an obligation; never present guidance or reviewer judgment as mandatory.
"""


def build_climate_stage3_prompt(
    *,
    instrument_type: str,
    document_type: str,
    diagnostic: dict[str, Any],
    regime_header: str,
) -> str:
    """Build the priorities-only prompt from one canonical diagnostic."""

    route = _selected_instrument_route(instrument_type)
    compact_diagnostic = json.dumps(
        diagnostic if isinstance(diagnostic, dict) else {},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    priority_schema = {
        "fcv_rating": "copy fcv_baseline.sensitivity_rating",
        "fcv_responsiveness_rating": (
            "copy fcv_baseline.responsiveness_rating"
        ),
        "sensitivity_summary": "copy compact baseline reasoning",
        "responsiveness_summary": "copy compact baseline reasoning",
        "risk_exposure": {"risks_to": "", "risks_from": ""},
        "mid_cycle_watch": [], "dpf_watch": [], "p4r_watch": [],
        "regional_watch": [],
        "priorities": [{
            "title": "", "fcv_dimension": "", "tag": "[S]|[R]|[S+R]",
            "refresh_shift": "", "risk_level": "High|Moderate|Low",
            "the_gap": "", "why_it_matters": "", "actions": [{
                "document_element": "", "guidance": "",
                "suggested_language": "",
            }],
            "who_acts": "", "when": "", "action_timing": "",
            "resources": "", "pad_sections": "",
            "country_category_relevance": "", "implementation_note": "",
            "cpf_alignment": None, "rra_driver_alignment": None,
            "change_type": "", "restructuring_level": "",
            "priority_scope": "", "governance_level": None,
            "policy_status": "advisory", "specialist_referral": None,
            "authority_basis": "reviewer_judgment",
            "lens_ids": ["climate"], "lens_relevance": "",
            "climate_links": {
                "status": "linked|no-material-pathway",
                "interaction_pathway_ids": [], "dividend_pathway_ids": [],
                "finding_ids": [], "contribution": "",
                "strengthening_effect": "", "reason": "",
            },
        }],
    }
    schema = json.dumps(
        priority_schema, ensure_ascii=False, separators=(",", ": ")
    )
    return f"""You are producing Climate-FCV Stage 3 priorities only for a World Bank operation.
Instrument: {instrument_type or 'Unknown'}
Document type: {document_type or 'Unknown'}
{regime_header}
Selected instrument route: {route}.

SOURCE AND SCOPE
The canonical diagnostic is the sole analytical source. Use it without reassessment:
{compact_diagnostic}
Do not regenerate the opening assessment, operating context, strengths/weaknesses, anchor or core questions, wider FCV context, general assessment narrative, or generic FCV priorities. Copy the compact fcv_baseline ratings and reasoning into the output without reassessment.

Generate approximately three priorities; use more only where evidence warrants, with a hard maximum of five. Rank one list by materiality, evidence, actionability, and FCV feasibility. Each priority must cite recognized payload pathway, question, finding, component, location, affected group, institution, or document-section anchors. Use climate_links with only IDs present in the canonical payload. For no material pathway, use status no-material-pathway, empty ID arrays, and a reason.

Instrument-route every action. IPF uses ESF instruments and applicable ESS; PforR uses ESSA/PAP/DLIs/borrower systems and never IPF ESS/ESCP/CERC; DPF/DPO uses the Program Document/prior actions/PSIA/environmental-natural-resource analysis and SORT only where applicable, never IPF machinery.

Keep this advisory: flag, point, and refer; never determine Paris Alignment, CDRS, ESF/ESS/ESRC, resilience, or screening adequacy. Analytical sources are evidence and good practice, not OPCS compliance authority. authority_basis must be exactly policy | directive | procedure | guidance | reviewer_judgment. Use policy/directive/procedure/guidance only where a specific source supports that classification; do not present guidance or reviewer_judgment as mandatory.

CERC may be considered only for IPF with a named eligible emergency, plausible government declaration/activation pathway, and PDO link. Never an IPF-style CERC for standalone PforR or DPF/DPO, and never generic flexibility. For Additional Financing, scope to what the AF finances, not the whole parent operation. Restructuring does not automatically restart CDRS: flag an update only for materially changed or new activities/exposure. Scope MPA recommendations to the relevant MPA phase. Apply existing conditional AF/restructuring/MPA/source guardrails and conditional compound-risk language ('may intensify', 'could interact with'); do not promise conflict reduction or peace dividends.

Return exactly one JSON object between {_STAGE3_JSON_START} and {_STAGE3_JSON_END} using this existing application priority schema:
{schema}
Keep nonapplicable watch arrays empty. Do not add narrative before or after the JSON block.
"""
