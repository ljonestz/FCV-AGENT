"""Admission, routing, authority, and ranking for Climate-FCV actions."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from sector_lenses.climate_verified_contracts import ValidationIssue


ROUTING_STATUSES = {
    "verified_existing",
    "verified_with_scope_change",
    "new_vehicle_may_be_needed",
    "team_to_confirm",
    "not_applicable",
}
AUTHORITY_BASES = {
    "project_commitment",
    "policy",
    "directive",
    "procedure",
    "none_verified",
}
RECOMMENDATION_BASES = {
    "project_evidence",
    "country_context",
    "guidance",
    "analytical_judgment",
}
COMPLETION_EVIDENCE_STATUSES = {
    "output",
    "decision_record",
    "updated_section",
    "team_to_define",
}
READINESS_CATEGORIES = {
    "incomplete_climate_screening",
    "document_inconsistency",
    "unresolved_indicator",
    "processing_route_question",
    "missing_operational_home",
    "material_placeholder",
}
REQUIRED_GATES = {
    "connection",
    "residuality",
    "materiality",
    "actionability",
    "timing",
    "distinctiveness",
}


@dataclass(frozen=True)
class RecommendationScore:
    materiality: int
    gap_strength: int
    leverage_urgency: int
    evidence: int
    feasibility: int

    @property
    def total(self) -> int:
        return (
            self.materiality
            + self.gap_strength
            + self.leverage_urgency
            + self.evidence
            + self.feasibility
        )


@dataclass(frozen=True)
class CandidateRecommendation:
    recommendation_id: str
    title: str
    pathway_ids: tuple[str, ...]
    existing_response_ids: tuple[str, ...]
    residual_gap_ids: tuple[str, ...]
    project_anchor_ids: tuple[str, ...]
    decision: str
    minimum_action: str
    enhanced_action: str | None
    enhanced_activation: str | None
    routing_status: str
    instrument_claim_ids: tuple[str, ...]
    responsible_function: str
    authority_basis: str
    recommendation_basis: str
    completion_evidence: str
    completion_evidence_status: str
    confidence: str
    limitation: str
    caution: str
    drafting_language: str | None
    score: RecommendationScore
    gate_results: dict[str, bool]
    rank: int | None = None
    supported_numeric_tokens: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewReadinessFlag:
    flag_id: str
    category: str
    flag: str
    why_it_matters: str
    document_basis_ids: tuple[str, ...]
    suggested_verification: str


def _issue(
    code: str,
    message: str,
    candidate: CandidateRecommendation,
) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        message=message,
        object_id=candidate.recommendation_id,
        blocking=True,
    )


def validate_recommendation(
    candidate: CandidateRecommendation,
    known_ids: set[str],
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    linked_ids = (
        candidate.pathway_ids
        + candidate.existing_response_ids
        + candidate.residual_gap_ids
        + candidate.project_anchor_ids
        + candidate.instrument_claim_ids
    )
    if set(linked_ids) - known_ids:
        issues.append(
            _issue(
                "RECOMMENDATION_REF_INVALID",
                f"{candidate.recommendation_id} has unknown references.",
                candidate,
            )
        )
    if candidate.routing_status not in ROUTING_STATUSES:
        issues.append(
            _issue(
                "ROUTING_STATUS_INVALID",
                f"{candidate.recommendation_id} has invalid routing.",
                candidate,
            )
        )
    if candidate.authority_basis not in AUTHORITY_BASES:
        issues.append(
            _issue(
                "AUTHORITY_BASIS_INVALID",
                f"{candidate.recommendation_id} has invalid authority.",
                candidate,
            )
        )
    if candidate.recommendation_basis not in RECOMMENDATION_BASES:
        issues.append(
            _issue(
                "RECOMMENDATION_BASIS_INVALID",
                f"{candidate.recommendation_id} has invalid basis.",
                candidate,
            )
        )
    if candidate.enhanced_action and not candidate.enhanced_activation:
        issues.append(
            _issue(
                "ENHANCED_ACTIVATION_MISSING",
                f"{candidate.recommendation_id} has no activation condition.",
                candidate,
            )
        )
    if (
        candidate.drafting_language
        and candidate.routing_status
        not in {"verified_existing", "verified_with_scope_change"}
    ):
        issues.append(
            _issue(
                "DRAFTING_ROUTING_UNVERIFIED",
                f"{candidate.recommendation_id} drafting is not safely routed.",
                candidate,
            )
        )
    drafting_tokens = set(
        re.findall(r"\b[a-z]+\b", (candidate.drafting_language or "").casefold())
    )
    if (
        drafting_tokens & {"must", "shall", "required", "mandatory"}
        and candidate.authority_basis
        not in {"project_commitment", "policy", "directive", "procedure"}
    ):
        issues.append(
            _issue(
                "MANDATORY_AUTHORITY_UNVERIFIED",
                (
                    f"{candidate.recommendation_id} uses mandatory language "
                    "without verified authority."
                ),
                candidate,
            )
        )
    if candidate.completion_evidence_status not in COMPLETION_EVIDENCE_STATUSES:
        issues.append(
            _issue(
                "COMPLETION_EVIDENCE_STATUS_INVALID",
                f"{candidate.recommendation_id} has invalid completion evidence.",
                candidate,
            )
        )
    numeric_text = " ".join(
        value
        for value in (
            candidate.decision,
            candidate.minimum_action,
            candidate.enhanced_action,
            candidate.enhanced_activation,
            candidate.completion_evidence,
            candidate.drafting_language,
        )
        if value
    )
    numeric_tokens = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", numeric_text))
    unsupported = numeric_tokens - set(candidate.supported_numeric_tokens)
    if unsupported:
        issues.append(
            _issue(
                "RECOMMENDATION_NUMBER_UNSUPPORTED",
                (
                    f"{candidate.recommendation_id} contains unsupported "
                    f"numeric tokens: {', '.join(sorted(unsupported))}."
                ),
                candidate,
            )
        )
    return tuple(issues)


def admission_failure_codes(
    candidate: CandidateRecommendation,
) -> tuple[str, ...]:
    """Return stable reason codes for deterministic admission failures."""

    codes: list[str] = []
    if candidate.score.total < 6:
        codes.append("ADMISSION_SCORE_BELOW_MIN")
    if candidate.score.materiality < 2:
        codes.append("ADMISSION_MATERIALITY_BELOW_MIN")
    for gate in sorted(REQUIRED_GATES):
        if gate not in candidate.gate_results:
            codes.append(f"ADMISSION_GATE_MISSING_{gate.upper()}")
        elif not candidate.gate_results[gate]:
            codes.append(f"ADMISSION_GATE_FAILED_{gate.upper()}")
    return tuple(codes)


def admit_and_rank(
    candidates: list[CandidateRecommendation],
) -> tuple[CandidateRecommendation, ...]:
    admitted = [
        candidate
        for candidate in candidates
        if candidate.score.total >= 6
        and candidate.score.materiality >= 2
        and REQUIRED_GATES.issubset(candidate.gate_results)
        and all(candidate.gate_results[name] for name in REQUIRED_GATES)
    ]
    ordered = sorted(
        admitted,
        key=lambda item: (
            -item.score.total,
            -item.score.materiality,
            -item.score.evidence,
            item.recommendation_id,
        ),
    )[:3]
    return tuple(
        replace(candidate, rank=index)
        for index, candidate in enumerate(ordered, start=1)
    )


def _normalized_sentence(value: str) -> str:
    return " ".join(value.casefold().split()).rstrip(".")


def admit_readiness_flags(
    flags: list[ReviewReadinessFlag],
    known_project_ids: set[str],
    reserved_statements: set[str],
) -> tuple[ReviewReadinessFlag, ...]:
    reserved = {_normalized_sentence(item) for item in reserved_statements}
    admitted: list[ReviewReadinessFlag] = []
    for flag in flags:
        if flag.category not in READINESS_CATEGORIES:
            continue
        if not flag.document_basis_ids:
            continue
        if set(flag.document_basis_ids) - known_project_ids:
            continue
        if _normalized_sentence(flag.flag) in reserved:
            continue
        admitted.append(flag)
        if len(admitted) == 4:
            break
    return tuple(admitted)
