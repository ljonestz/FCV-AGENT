"""Atomic project facts, source matching, and derived assertions."""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass

from sector_lenses.climate_source_blocks import SourceBlock
from sector_lenses.climate_verified_contracts import (
    HARD_FACT_LIMIT,
    EpistemicStatus,
    ExcerptMatchStatus,
    ValidationIssue,
)


@dataclass(frozen=True)
class ProjectFactClaim:
    claim_id: str
    claim_type: str
    subject: str
    predicate: str
    object_value: str
    epistemic_status: str
    source_block_ids: tuple[str, ...]
    supporting_excerpt: str | None
    confidence: str


@dataclass(frozen=True)
class ExcerptMatch:
    status: ExcerptMatchStatus
    score: float
    automatically_usable: bool


@dataclass(frozen=True)
class FactRegistryResult:
    claims: tuple[ProjectFactClaim, ...]
    blocking_issues: tuple[ValidationIssue, ...]


@dataclass(frozen=True)
class TargetedRetrievalRequest:
    question: str
    terms: tuple[str, ...]
    maximum_blocks: int = 8

    def __post_init__(self) -> None:
        if not 1 <= self.maximum_blocks <= 12:
            raise ValueError("maximum_blocks must be between 1 and 12")


@dataclass(frozen=True)
class DerivedAssertion:
    assertion_id: str
    assertion_type: str
    statement: str
    input_fact_ids: tuple[str, ...]
    derivation_method: str
    explanation: str
    confidence: str
    validation_status: str


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _is_explicit_negative(text: str) -> bool:
    normalized = _normalized(text)
    markers = (
        "does not include",
        "do not include",
        "is not included",
        "are not included",
        "no provision",
        "none is provided",
        "will not include",
        "excludes",
    )
    return any(marker in normalized for marker in markers)


def match_supporting_excerpt(
    excerpt: str,
    block: SourceBlock,
) -> ExcerptMatch:
    if excerpt in block.text:
        return ExcerptMatch(ExcerptMatchStatus.VERBATIM, 1.0, True)
    normalized_excerpt = _normalized(excerpt)
    normalized_block = _normalized(block.text)
    if normalized_excerpt in normalized_block:
        return ExcerptMatch(ExcerptMatchStatus.NORMALIZED_EXACT, 1.0, True)
    score = difflib.SequenceMatcher(
        None,
        normalized_excerpt,
        normalized_block,
    ).ratio()
    if score >= 0.72:
        return ExcerptMatch(ExcerptMatchStatus.BOUNDED_FUZZY, score, False)
    return ExcerptMatch(ExcerptMatchStatus.UNRESOLVED, score, False)


def normalize_fact_registry(
    claims: list[ProjectFactClaim],
    blocks: list[SourceBlock],
) -> FactRegistryResult:
    if len(claims) > HARD_FACT_LIMIT:
        raise ValueError(f"Fact registry exceeds hard limit of {HARD_FACT_LIMIT}")
    block_index = {block.block_id: block for block in blocks}
    issues: list[ValidationIssue] = []

    for claim in claims:
        status = EpistemicStatus(claim.epistemic_status)
        resolved_blocks = [
            block_index[block_id]
            for block_id in claim.source_block_ids
            if block_id in block_index
        ]
        supported_matches = [
            (block, match_supporting_excerpt(claim.supporting_excerpt, block))
            for block in resolved_blocks
            if claim.supporting_excerpt
        ]

        if status is EpistemicStatus.CONFIRMED_ABSENCE:
            explicit_negative = any(
                match.automatically_usable
                and _is_explicit_negative(claim.supporting_excerpt or "")
                for _, match in supported_matches
            )
            if not explicit_negative:
                issues.append(
                    ValidationIssue(
                        code="ABSENCE_NOT_EXPLICIT",
                        message=(
                            f"{claim.claim_id} claims confirmed absence "
                            "without an explicit negative source."
                        ),
                        object_id=claim.claim_id,
                        blocking=True,
                    )
                )
        elif status is EpistemicStatus.EXPLICIT:
            if not any(match.automatically_usable for _, match in supported_matches):
                issues.append(
                    ValidationIssue(
                        code="FACT_SOURCE_UNRESOLVED",
                        message=(
                            f"{claim.claim_id} is explicit but its excerpt "
                            "does not resolve exactly."
                        ),
                        object_id=claim.claim_id,
                        blocking=True,
                    )
                )

    return FactRegistryResult(tuple(claims), tuple(issues))


def validate_derived_assertions(
    assertions: list[DerivedAssertion],
    known_fact_ids: set[str],
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for assertion in assertions:
        if not assertion.assertion_id.startswith("DA-"):
            issues.append(
                ValidationIssue(
                    code="DERIVATION_ID_INVALID",
                    message=f"{assertion.assertion_id} must start with DA-.",
                    object_id=assertion.assertion_id,
                    blocking=True,
                )
            )
        missing = set(assertion.input_fact_ids) - known_fact_ids
        if missing:
            issues.append(
                ValidationIssue(
                    code="DERIVATION_INPUT_MISSING",
                    message=(
                        f"{assertion.assertion_id} references missing facts: "
                        + ", ".join(sorted(missing))
                    ),
                    object_id=assertion.assertion_id,
                    blocking=True,
                )
            )
        if not assertion.explanation.strip():
            issues.append(
                ValidationIssue(
                    code="DERIVATION_EXPLANATION_MISSING",
                    message=(
                        f"{assertion.assertion_id} has no derivation explanation."
                    ),
                    object_id=assertion.assertion_id,
                    blocking=True,
                )
            )
        if assertion.derivation_method not in {"deterministic", "semantic"}:
            issues.append(
                ValidationIssue(
                    code="DERIVATION_METHOD_INVALID",
                    message=f"{assertion.assertion_id} has an invalid method.",
                    object_id=assertion.assertion_id,
                    blocking=True,
                )
            )
    return tuple(issues)
