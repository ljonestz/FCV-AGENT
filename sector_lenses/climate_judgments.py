"""Multidimensional Climate-FCV judgments with deterministic coherence."""

from __future__ import annotations

from dataclasses import dataclass

from sector_lenses.climate_verified_contracts import ValidationIssue


ALLOWED = {
    "relevance": {"high", "medium", "low", "unclear"},
    "sensitivity": {"strong", "moderate", "limited", "unclear"},
    "responsiveness": {
        "strong",
        "emerging",
        "limited",
        "not_expected",
        "unclear",
    },
    "operationalization": {
        "embedded",
        "partial",
        "early",
        "not_evidenced",
        "unclear",
    },
}


@dataclass(frozen=True)
class Judgment:
    value: str
    evidence_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class ClimateJudgments:
    relevance: Judgment
    sensitivity: Judgment
    responsiveness: Judgment
    operationalization: Judgment


def validate_judgments(
    judgments: ClimateJudgments,
    known_ids: set[str],
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for dimension in ALLOWED:
        judgment = getattr(judgments, dimension)
        if judgment.value not in ALLOWED[dimension]:
            issues.append(
                ValidationIssue(
                    f"{dimension.upper()}_VALUE_INVALID",
                    f"{judgment.value} is invalid for {dimension}.",
                    dimension,
                    True,
                )
            )
            continue
        if set(judgment.evidence_ids) - known_ids:
            issues.append(
                ValidationIssue(
                    f"{dimension.upper()}_EVIDENCE_INVALID",
                    f"{dimension} references unknown evidence.",
                    dimension,
                    True,
                )
            )
        if not judgment.evidence_ids:
            issues.append(
                ValidationIssue(
                    "JUDGMENT_EVIDENCE_MISSING",
                    f"{dimension} has no resolvable evidence reference.",
                    dimension,
                    True,
                )
            )

    operational = judgments.operationalization
    if operational.value == "embedded" and not any(
        evidence_id.startswith(("ER-", "PF-"))
        for evidence_id in operational.evidence_ids
    ):
        issues.append(
            ValidationIssue(
                "OPERATIONALIZATION_DELIVERY_EVIDENCE_MISSING",
                "Embedded operationalization needs project delivery evidence.",
                "operationalization",
                True,
            )
        )
    return tuple(issues)


def deterministic_summary(judgments: ClimateJudgments) -> str:
    return (
        f"{judgments.relevance.value.capitalize()} Climate-FCV relevance; "
        f"{judgments.sensitivity.value} sensitivity; "
        f"{judgments.responsiveness.value} responsiveness; "
        f"{judgments.operationalization.value} operationalization."
    )
