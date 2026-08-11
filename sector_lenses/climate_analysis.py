"""Bounded Climate-FCV analysis registers and evidence entitlements."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from sector_lenses.climate_verified_contracts import ValidationIssue


ALLOWED_GAP_TYPES = {
    "confirmed_omission",
    "partial_response",
    "not_yet_specified",
    "contradictory",
    "evidence_gap",
}
ALLOWED_DIRECTIONS = {"climate_to_fcv", "fcv_to_climate"}
EVIDENCE_ENTITLEMENTS = {
    "project": {
        "project_design_fact",
        "project_gap",
        "project_commitment",
        "contextual_pathway",
        "site_specific_conclusion",
    },
    "project_package": {
        "project_design_fact",
        "project_gap",
        "project_commitment",
        "contextual_pathway",
    },
    "country": {"contextual_pathway", "materiality_question"},
    "guidance": {"good_practice_option", "indicator_option"},
    "inference": {"analytical_judgment"},
}


@dataclass(frozen=True)
class ContextEvidenceRef:
    evidence_id: str
    evidence_class: str
    scope: str
    statement: str
    source_ref: str
    confidence: str
    source_kind: str = "context"
    context_class: str | None = None
    preview_status: str | None = None


@dataclass(frozen=True)
class ExistingResponse:
    response_id: str
    project_fact_ids: tuple[str, ...]
    pathway_ids: tuple[str, ...]
    description: str
    limitation: str


@dataclass(frozen=True)
class ClimatePathway:
    pathway_id: str
    direction: str
    chain: tuple[str, ...]
    project_anchor_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    confidence: str


@dataclass(frozen=True)
class ResidualGap:
    gap_id: str
    gap_type: str
    statement: str
    pathway_ids: tuple[str, ...]
    project_anchor_ids: tuple[str, ...]
    existing_response_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    confidence: str


def evidence_can_support(
    evidence: ContextEvidenceRef,
    claim_kind: str,
) -> bool:
    return claim_kind in EVIDENCE_ENTITLEMENTS.get(
        evidence.evidence_class,
        set(),
    )


def validate_analysis_registers(
    responses: list[ExistingResponse],
    pathways: list[ClimatePathway],
    gaps: list[ResidualGap],
    known_fact_ids: set[str],
    known_context_ids: set[str],
    confirmed_absence_fact_ids: set[str] | None = None,
) -> tuple[ValidationIssue, ...]:
    if len(gaps) > 8:
        raise ValueError("Residual-gap register may contain at most eight gaps")
    direction_counts = Counter(pathway.direction for pathway in pathways)
    if any(count > 3 for count in direction_counts.values()):
        raise ValueError("Pathways are limited to three in each direction")

    confirmed_absences = confirmed_absence_fact_ids or set()
    response_ids = {response.response_id for response in responses}
    pathway_ids = {pathway.pathway_id for pathway in pathways}
    issues: list[ValidationIssue] = []

    for pathway in pathways:
        if pathway.direction not in ALLOWED_DIRECTIONS:
            issues.append(
                ValidationIssue(
                    "PATHWAY_DIRECTION_INVALID",
                    f"{pathway.pathway_id} has an invalid direction.",
                    pathway.pathway_id,
                    True,
                )
            )
        if len(pathway.chain) < 3:
            issues.append(
                ValidationIssue(
                    "PATHWAY_CHAIN_TOO_SHORT",
                    f"{pathway.pathway_id} needs a mediated chain.",
                    pathway.pathway_id,
                    True,
                )
            )
        if set(pathway.project_anchor_ids) - known_fact_ids:
            issues.append(
                ValidationIssue(
                    "PATHWAY_PROJECT_REF_INVALID",
                    f"{pathway.pathway_id} has an unknown project anchor.",
                    pathway.pathway_id,
                    True,
                )
            )
        if set(pathway.evidence_ids) - known_context_ids:
            issues.append(
                ValidationIssue(
                    "PATHWAY_EVIDENCE_REF_INVALID",
                    f"{pathway.pathway_id} has unknown contextual evidence.",
                    pathway.pathway_id,
                    True,
                )
            )

    for response in responses:
        if set(response.project_fact_ids) - known_fact_ids:
            issues.append(
                ValidationIssue(
                    "RESPONSE_PROJECT_REF_INVALID",
                    f"{response.response_id} has an unknown project fact.",
                    response.response_id,
                    True,
                )
            )
        if set(response.pathway_ids) - pathway_ids:
            issues.append(
                ValidationIssue(
                    "RESPONSE_PATHWAY_REF_INVALID",
                    f"{response.response_id} has an unknown pathway.",
                    response.response_id,
                    True,
                )
            )

    for gap in gaps:
        if gap.gap_type not in ALLOWED_GAP_TYPES:
            issues.append(
                ValidationIssue(
                    "GAP_TYPE_INVALID",
                    f"{gap.gap_id} has an invalid gap type.",
                    gap.gap_id,
                    True,
                )
            )
        if set(gap.pathway_ids) - pathway_ids:
            issues.append(
                ValidationIssue(
                    "GAP_PATHWAY_REF_INVALID",
                    f"{gap.gap_id} has an unknown pathway.",
                    gap.gap_id,
                    True,
                )
            )
        if set(gap.existing_response_ids) - response_ids:
            issues.append(
                ValidationIssue(
                    "GAP_RESPONSE_REF_INVALID",
                    f"{gap.gap_id} has an unknown existing response.",
                    gap.gap_id,
                    True,
                )
            )
        if set(gap.project_anchor_ids) - known_fact_ids:
            issues.append(
                ValidationIssue(
                    "GAP_PROJECT_REF_INVALID",
                    f"{gap.gap_id} has an unknown project anchor.",
                    gap.gap_id,
                    True,
                )
            )
        if (
            gap.gap_type == "confirmed_omission"
            and not set(gap.evidence_ids) & confirmed_absences
        ):
            issues.append(
                ValidationIssue(
                    "CONFIRMED_OMISSION_NOT_EXPLICIT",
                    (
                        f"{gap.gap_id} uses confirmed_omission without "
                        "an explicit negative project fact."
                    ),
                    gap.gap_id,
                    True,
                )
            )
    return tuple(issues)
