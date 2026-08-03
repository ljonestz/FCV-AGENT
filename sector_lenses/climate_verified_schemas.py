"""Native JSON schemas for verified Climate-FCV model stages.

The schemas constrain transport shape only. Deterministic domain validation,
reference checks, recommendation admission, and semantic review remain the
authoritative analytical controls.
"""

from __future__ import annotations

from copy import deepcopy


def _object(properties: dict[str, object]) -> dict[str, object]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def _string(description: str = "") -> dict[str, object]:
    schema: dict[str, object] = {"type": "string"}
    if description:
        schema["description"] = description
    return schema


def _nullable_string(description: str = "") -> dict[str, object]:
    schema: dict[str, object] = {"type": ["string", "null"]}
    if description:
        schema["description"] = description
    return schema


def _enum(values: tuple[str, ...]) -> dict[str, object]:
    return {"type": "string", "enum": list(values)}


def _strings(description: str = "") -> dict[str, object]:
    schema: dict[str, object] = {
        "type": "array",
        "items": {"type": "string"},
    }
    if description:
        schema["description"] = description
    return schema


CONFIDENCE = ("high", "medium", "low")


FACT_SCHEMA = _object(
    {
        "claim_id": _string(),
        "claim_type": _string("Short atomic fact type."),
        "subject": _string("45 words or fewer."),
        "predicate": _string("45 words or fewer."),
        "object": _string("45 words or fewer."),
        "epistemic_status": _enum(
            (
                "explicit",
                "confirmed_absence",
                "not_found",
                "not_yet_specified",
                "contradictory",
                "not_applicable",
            )
        ),
        "source_block_ids": _strings(),
        "supporting_excerpt": _nullable_string(
            "A short verbatim excerpt of 60 words or fewer, or null."
        ),
        "confidence": _enum(CONFIDENCE),
    }
)

ASSERTION_SCHEMA = _object(
    {
        "assertion_id": _string(),
        "assertion_type": _string(),
        "statement": _string("45 words or fewer."),
        "input_fact_ids": _strings(),
        "derivation_method": _enum(("deterministic", "semantic")),
        "explanation": _string("45 words or fewer."),
        "confidence": _enum(CONFIDENCE),
        "validation_status": _string(),
    }
)

RESPONSE_SCHEMA = _object(
    {
        "response_id": _string(),
        "project_fact_ids": _strings(),
        "pathway_ids": _strings(),
        "description": _string("45 words or fewer."),
        "limitation": _string("45 words or fewer."),
    }
)

PATHWAY_SCHEMA = _object(
    {
        "pathway_id": _string(),
        "direction": _enum(("climate_to_fcv", "fcv_to_climate")),
        "chain": _strings("Exactly three short elements."),
        "project_anchor_ids": _strings(),
        "evidence_ids": _strings(),
        "confidence": _enum(CONFIDENCE),
    }
)

GAP_SCHEMA = _object(
    {
        "gap_id": _string(),
        "gap_type": _enum(
            (
                "confirmed_omission",
                "partial_response",
                "not_yet_specified",
                "contradictory",
                "evidence_gap",
            )
        ),
        "statement": _string("45 words or fewer."),
        "pathway_ids": _strings(),
        "project_anchor_ids": _strings(),
        "existing_response_ids": _strings(),
        "evidence_ids": _strings(),
        "confidence": _enum(CONFIDENCE),
    }
)


def _judgment(values: tuple[str, ...]) -> dict[str, object]:
    return _object(
        {
            "value": _enum(values),
            "evidence_ids": _strings(),
            "rationale": _string("75 words or fewer."),
        }
    )


SCORE_SCHEMA = _object(
    {
        "materiality": {"type": "integer"},
        "gap_strength": {"type": "integer"},
        "leverage_urgency": {"type": "integer"},
        "evidence": {"type": "integer"},
        "feasibility": {"type": "integer"},
    }
)

GATE_SCHEMA = _object(
    {
        "connection": {"type": "boolean"},
        "residuality": {"type": "boolean"},
        "materiality": {"type": "boolean"},
        "actionability": {"type": "boolean"},
        "timing": {"type": "boolean"},
        "distinctiveness": {"type": "boolean"},
    }
)

CANDIDATE_SCHEMA = _object(
    {
        "recommendation_id": _string(),
        "title": _string("45 words or fewer."),
        "pathway_ids": _strings(),
        "existing_response_ids": _strings(),
        "residual_gap_ids": _strings(),
        "project_anchor_ids": _strings(),
        "decision": _string("45 words or fewer."),
        "minimum_action": _string("45 words or fewer."),
        "enhanced_action": _nullable_string("45 words or fewer, or null."),
        "enhanced_activation": _nullable_string("45 words or fewer, or null."),
        "routing_status": _enum(
            (
                "verified_existing",
                "verified_with_scope_change",
                "new_vehicle_may_be_needed",
                "team_to_confirm",
                "not_applicable",
            )
        ),
        "instrument_claim_ids": _strings(),
        "responsible_function": _string("45 words or fewer."),
        "authority_basis": _enum(
            ("project_commitment", "policy", "directive", "procedure", "none_verified")
        ),
        "recommendation_basis": _enum(
            ("project_evidence", "country_context", "guidance", "analytical_judgment")
        ),
        "completion_evidence": _string("45 words or fewer."),
        "completion_evidence_status": _enum(
            ("output", "decision_record", "updated_section", "team_to_define")
        ),
        "confidence": _enum(CONFIDENCE),
        "limitation": _string("45 words or fewer."),
        "caution": _string("45 words or fewer."),
        "drafting_language": _nullable_string("45 words or fewer, or null."),
        "supported_numeric_tokens": _strings(),
        "score": SCORE_SCHEMA,
        "gate_results": GATE_SCHEMA,
    }
)

READINESS_SCHEMA = _object(
    {
        "flag_id": _string(),
        "category": _enum(
            (
                "incomplete_climate_screening",
                "document_inconsistency",
                "unresolved_indicator",
                "processing_route_question",
                "missing_operational_home",
                "material_placeholder",
            )
        ),
        "flag": _string("45 words or fewer."),
        "why_it_matters": _string("45 words or fewer."),
        "document_basis_ids": _strings(),
        "suggested_verification": _string("45 words or fewer."),
    }
)


STAGE_OUTPUT_SCHEMAS: dict[str, dict[str, object]] = {
    "fact_extraction": _object(
        {
            "schema_version": _enum(("climate-verified-v2",)),
            "facts": {
                "type": "array",
                "items": FACT_SCHEMA,
                "description": "No more than 100 atomic project facts.",
            },
            "derived_assertions": {
                "type": "array",
                "items": ASSERTION_SCHEMA,
                "description": "Only essential derived assertions.",
            },
        }
    ),
    "bounded_analysis": _object(
        {
            "existing_responses": {
                "type": "array",
                "items": RESPONSE_SCHEMA,
                "description": "No more than 12 material existing responses.",
            },
            "pathways": {
                "type": "array",
                "items": PATHWAY_SCHEMA,
                "description": "No more than three pathways in each direction.",
            },
            "residual_gaps": {
                "type": "array",
                "items": GAP_SCHEMA,
                "description": "No more than eight residual gaps.",
            },
            "opportunities_and_unintended_consequences": _strings(
                "No more than four concise items, each 45 words or fewer."
            ),
            "evidence_limitations": _strings(
                "No more than four concise items, each 45 words or fewer."
            ),
        }
    ),
    "judgment_review": _object(
        {
            "executive_readout": _string("Between 500 and 800 words."),
            "relevance": _judgment(("high", "medium", "low", "unclear")),
            "sensitivity": _judgment(
                ("strong", "moderate", "limited", "unclear")
            ),
            "responsiveness": _judgment(
                ("strong", "emerging", "limited", "not_expected", "unclear")
            ),
            "operationalization": _judgment(
                ("embedded", "partial", "early", "not_evidenced", "unclear")
            ),
        }
    ),
    "recommendation_compiler": _object(
        {
            "recommendation_candidates": {
                "type": "array",
                "items": CANDIDATE_SCHEMA,
                "description": "No more than three admitted candidates.",
            },
            "readiness_flags": {
                "type": "array",
                "items": READINESS_SCHEMA,
                "description": "No more than four source-linked readiness flags.",
            },
        }
    ),
    "conditional_review": _object(
        {
            "verdict": _enum(("pass", "revise", "block")),
            "reason_codes": _strings("No more than 12 bounded reason codes."),
            "object_ids": _strings("No more than 12 affected object IDs."),
        }
    ),
}


def stage_output_schema(stage: str) -> dict[str, object]:
    """Return an isolated native output schema for one verified stage."""

    try:
        schema = STAGE_OUTPUT_SCHEMAS[stage]
    except KeyError as error:
        raise ValueError(f"Unsupported verified Climate stage: {stage}") from error
    return deepcopy(schema)
