import pytest

from sector_lenses.climate_verified_contracts import (
    CALL_BUDGETS,
    CLIMATE_VERIFIED_SCHEMA_VERSION,
    EpistemicStatus,
    ExcerptMatchStatus,
    ValidationIssue,
)


def test_verified_schema_and_call_budgets_are_stable():
    assert CLIMATE_VERIFIED_SCHEMA_VERSION == "climate-verified-v2.1"
    assert CALL_BUDGETS["fact_extraction"].input_tokens == 24_000
    assert CALL_BUDGETS["fact_extraction"].output_tokens == 16_000
    assert CALL_BUDGETS["fact_extraction"].timeout_seconds == 300
    assert CALL_BUDGETS["bounded_analysis"].timeout_seconds == 180
    # judgment_review now also emits core_questions (~2 paragraphs x5) and
    # minor_climate_points, so its output budget was raised from 4k to 9k tokens
    # (and timeout 120->240) to avoid max_tokens truncation on the quality model.
    assert CALL_BUDGETS["judgment_review"].timeout_seconds == 240
    assert CALL_BUDGETS["judgment_review"].output_tokens == 9_000
    assert CALL_BUDGETS["recommendation_compiler"].timeout_seconds == 240
    assert CALL_BUDGETS["drafting_compiler"].timeout_seconds == 240
    assert CALL_BUDGETS["drafting_compiler"].output_tokens == 5_000
    assert CALL_BUDGETS["conditional_review"].timeout_seconds == 120


def test_epistemic_and_match_statuses_are_closed_enums():
    assert {item.value for item in EpistemicStatus} == {
        "explicit",
        "confirmed_absence",
        "not_found",
        "not_yet_specified",
        "contradictory",
        "not_applicable",
    }
    assert {item.value for item in ExcerptMatchStatus} == {
        "verbatim",
        "normalized_exact",
        "bounded_fuzzy",
        "unresolved",
    }
    with pytest.raises(ValueError):
        EpistemicStatus("absent")


def test_validation_issue_exposes_machine_reason_code():
    issue = ValidationIssue(
        code="FACT_SOURCE_UNRESOLVED",
        message="PF-017 has no resolvable source block.",
        object_id="PF-017",
        blocking=True,
    )
    assert issue.as_dict() == {
        "code": "FACT_SOURCE_UNRESOLVED",
        "message": "PF-017 has no resolvable source block.",
        "object_id": "PF-017",
        "blocking": True,
    }
