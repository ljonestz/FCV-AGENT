"""Deterministic admission checks for the native conditional-review contract."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sector_lenses.climate_verified_schemas import SEMANTIC_REVIEW_REASON_CODES


_CORE_REVIEW_FIELDS = {
    "recommendation_id",
    "premise_verdict",
    "source_block_ids",
    "reason_codes",
    "explanation",
}
_PREMISE_VERDICTS = {"supported", "qualified", "unsupported"}
_UNRESOLVED = "SEMANTIC_REVIEW_TARGET_UNRESOLVED"


@dataclass(frozen=True)
class CoreReviewAdmission:
    """Per-core result; malformed records never invalidate unrelated cores."""

    passed_core_ids: tuple[str, ...]
    affected_core_ids: tuple[str, ...]
    invalid_core_ids: tuple[str, ...]
    unsupported_core_ids: tuple[str, ...]
    synthesized_issues: tuple[dict[str, object], ...]
    reason_codes: tuple[str, ...]


def _valid_core_record(record: object, known_blocks: set[str]) -> bool:
    if not isinstance(record, dict) or set(record) != _CORE_REVIEW_FIELDS:
        return False
    identifier = record.get("recommendation_id")
    verdict = record.get("premise_verdict")
    blocks = record.get("source_block_ids")
    codes = record.get("reason_codes")
    explanation = record.get("explanation")
    if (
        not isinstance(identifier, str)
        or not isinstance(verdict, str)
        or verdict not in _PREMISE_VERDICTS
        or not isinstance(blocks, list)
        or not blocks
        or not all(isinstance(block, str) for block in blocks)
        or len(blocks) != len(set(blocks))
        or not set(blocks) <= known_blocks
        or not isinstance(codes, list)
        or not all(
            isinstance(code, str) and code in SEMANTIC_REVIEW_REASON_CODES
            for code in codes
        )
        or len(codes) != len(set(codes))
        or not isinstance(explanation, str)
        or not explanation.strip()
    ):
        return False
    return bool(codes) == (verdict == "unsupported")


def reconcile_core_reviews(
    review: object,
    recommendation_ids: Iterable[str],
    known_source_block_ids: Iterable[str],
) -> CoreReviewAdmission:
    """Reconcile explicit premise decisions with pass and issue declarations.

    The helper checks identifiers and structure only. It cannot determine whether
    a cited passage actually supports the reviewer's semantic conclusion.
    """

    ordered_ids = tuple(dict.fromkeys(recommendation_ids))
    known_ids = set(ordered_ids)
    known_blocks = set(known_source_block_ids)
    payload = review if isinstance(review, dict) else {}
    raw_records = payload.get("core_reviews")
    records = raw_records if isinstance(raw_records, list) else []
    by_id: dict[str, list[object]] = {}
    structural_problem = not isinstance(raw_records, list)
    for record in records:
        identifier = record.get("recommendation_id") if isinstance(record, dict) else None
        if not isinstance(identifier, str) or identifier not in known_ids:
            structural_problem = True
            continue
        by_id.setdefault(identifier, []).append(record)

    raw_passed = payload.get("passed_core_ids")
    passed_values = raw_passed if isinstance(raw_passed, list) else []
    structural_problem = structural_problem or not isinstance(raw_passed, list)
    passed_counts: dict[str, int] = {}
    for identifier in passed_values:
        if not isinstance(identifier, str) or identifier not in known_ids:
            structural_problem = True
            continue
        passed_counts[identifier] = passed_counts.get(identifier, 0) + 1

    raw_issues = payload.get("issues")
    issues = raw_issues if isinstance(raw_issues, list) else []
    parent_issue_ids = {
        issue.get("object_id")
        for issue in issues
        if isinstance(issue, dict)
        and isinstance(issue.get("object_id"), str)
        and issue.get("object_id") in known_ids
    }
    object_ids = payload.get("object_ids")
    if isinstance(object_ids, list):
        parent_issue_ids.update(
            identifier for identifier in object_ids
            if isinstance(identifier, str) and identifier in known_ids
        )

    passed: list[str] = []
    affected: list[str] = []
    invalid: list[str] = []
    unsupported: list[str] = []
    synthesized: list[dict[str, object]] = []
    for identifier in ordered_ids:
        candidates = by_id.get(identifier, [])
        record = candidates[0] if len(candidates) == 1 else None
        pass_count = passed_counts.get(identifier, 0)
        if (
            record is None
            or not _valid_core_record(record, known_blocks)
            or pass_count > 1
        ):
            invalid.append(identifier)
            affected.append(identifier)
            structural_problem = True
            continue

        verdict = record["premise_verdict"]
        has_parent_issue = identifier in parent_issue_ids
        if verdict == "unsupported":
            unsupported.append(identifier)
            affected.append(identifier)
            if pass_count:
                structural_problem = True
            if not has_parent_issue:
                synthesized.append({
                    "object_id": identifier,
                    "reason_codes": list(record["reason_codes"]),
                    "explanation": record["explanation"].strip(),
                })
            continue

        if has_parent_issue:
            affected.append(identifier)
            if pass_count:
                structural_problem = True
            continue
        if pass_count == 1:
            passed.append(identifier)
            continue
        invalid.append(identifier)
        affected.append(identifier)
        structural_problem = True

    return CoreReviewAdmission(
        passed_core_ids=tuple(passed),
        affected_core_ids=tuple(affected),
        invalid_core_ids=tuple(invalid),
        unsupported_core_ids=tuple(unsupported),
        synthesized_issues=tuple(synthesized),
        reason_codes=(_UNRESOLVED,) if structural_problem else (),
    )
