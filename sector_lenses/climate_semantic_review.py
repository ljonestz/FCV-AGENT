"""Conditional semantic review and bounded repair policy."""

from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewRisk:
    verified_instrument_name: bool = False
    material_fuzzy_match: bool = False
    contradictory_fact_materially_used: bool = False
    formal_claim: bool = False
    mandatory_language: bool = False
    drafting_language: bool = False
    verified_scope_change: bool = False
    unresolved_routing: bool = False
    derived_number: bool = False
    country_evidence_carries_causal_conclusion: bool = False
    high_materiality_moderate_evidence: bool = False
    deterministic_warning: bool = False


def semantic_review_required(risk: ReviewRisk) -> bool:
    return any(
        (
            risk.material_fuzzy_match,
            risk.contradictory_fact_materially_used,
            risk.formal_claim,
            risk.mandatory_language,
            risk.drafting_language,
            risk.verified_scope_change,
            risk.unresolved_routing,
            risk.derived_number,
            risk.country_evidence_carries_causal_conclusion,
            risk.high_materiality_moderate_evidence,
            risk.deterministic_warning,
        )
    )


def split_repair_actions(
    actions: list[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    deterministic_names = {
        "normalize_enum",
        "sort_ranks",
        "remove_placeholder",
        "drop_invalid_reference",
        "suppress_unsafe_drafting",
    }
    deterministic = tuple(
        action for action in actions if action in deterministic_names
    )
    semantic_candidates = [
        action for action in actions if action not in deterministic_names
    ]
    return deterministic, tuple(semantic_candidates[:1])


def build_reviewer_prompt(
    *,
    source_blocks: list[dict[str, object]],
    fact_registry: list[dict[str, object]],
    analysis: dict[str, object],
    recommendations: list[dict[str, object]],
    warning_codes: list[str],
) -> str:
    payload = json.dumps(
        {
            "source_blocks": source_blocks,
            "fact_registry": fact_registry,
            "analysis": analysis,
            "recommendations": recommendations,
            "warning_codes": warning_codes,
        },
        ensure_ascii=False,
    )
    return f"""Act as a source-first Climate-FCV verifier, not an editor.
Check existing mitigation before residual gaps, evidence entitlement,
recommendation proportionality, routing scope and timing, authority,
rating coherence, duplication, and unintended consequences.
Check current-document and operational-instrument drafting separately for
target existence and scope, representation of existing mitigation, residual
improvement, actor, timing, and authority, and unsupported technical precision.
Return pass, revise, or block with claim IDs and reason codes.
Do not reveal hidden reasoning and do not broadly rewrite the assessment.

REVIEW PACKAGE
{payload}
"""
