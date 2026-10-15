import pytest

from sector_lenses.climate_review_admission import reconcile_core_reviews


CORE_IDS = ("REC-001", "REC-002", "REC-003")
BLOCK_IDS = {"DOC-1-B-1", "DOC-1-B-2"}


def _core(identifier, verdict="supported", *, codes=None, blocks=None):
    return {
        "recommendation_id": identifier,
        "premise_verdict": verdict,
        "source_block_ids": blocks or ["DOC-1-B-1"],
        "reason_codes": (
            ["PROJECT_FACT_UNSUPPORTED"] if verdict == "unsupported"
            else []
        ) if codes is None else codes,
        "explanation": f"Source comparison for {identifier}.",
    }


def _review(*records, passed=None, issues=None):
    return {
        "core_reviews": list(records),
        "passed_core_ids": list(passed or []),
        "issues": list(issues or []),
    }


def test_supported_and_qualified_premises_can_pass():
    result = reconcile_core_reviews(
        _review(
            _core("REC-001"),
            _core("REC-002", "qualified"),
            _core("REC-003"),
            passed=CORE_IDS,
        ),
        CORE_IDS,
        BLOCK_IDS,
    )

    assert result.passed_core_ids == CORE_IDS
    assert result.affected_core_ids == ()
    assert result.invalid_core_ids == ()
    assert result.synthesized_issues == ()


def test_unsupported_premise_targets_parent_even_with_only_draft_issue():
    result = reconcile_core_reviews(
        _review(
            _core("REC-001"),
            _core("REC-002", "unsupported",
                  codes=["RESIDUAL_GAP_UNSUPPORTED"]),
            _core("REC-003"),
            passed=CORE_IDS,
            issues=[{
                "object_id": "REC-002::current_document",
                "reason_codes": ["DRAFTING_SCOPE_UNSUPPORTED"],
                "explanation": "The optional wording broadens the scope.",
            }],
        ),
        CORE_IDS,
        BLOCK_IDS,
    )

    assert result.passed_core_ids == ("REC-001", "REC-003")
    assert result.affected_core_ids == ("REC-002",)
    assert result.invalid_core_ids == ()
    assert result.synthesized_issues == ({
        "object_id": "REC-002",
        "reason_codes": ["RESIDUAL_GAP_UNSUPPORTED"],
        "explanation": "Source comparison for REC-002.",
    },)
    assert "SEMANTIC_REVIEW_TARGET_UNRESOLVED" in result.reason_codes


def test_supported_premise_can_fail_for_a_different_core_reason():
    issue = {
        "object_id": "REC-002",
        "reason_codes": ["RECOMMENDATION_DISPROPORTIONATE"],
        "explanation": "The action exceeds the evidenced need.",
    }
    result = reconcile_core_reviews(
        _review(
            *[_core(identifier) for identifier in CORE_IDS],
            passed=["REC-001", "REC-003"],
            issues=[issue],
        ),
        CORE_IDS,
        BLOCK_IDS,
    )

    assert result.passed_core_ids == ("REC-001", "REC-003")
    assert result.affected_core_ids == ("REC-002",)
    assert result.synthesized_issues == ()


def test_object_id_alone_still_rejects_explicitly_targeted_core():
    review = _review(
        *[_core(identifier) for identifier in CORE_IDS],
        passed=CORE_IDS,
    )
    review["object_ids"] = ["REC-002"]

    result = reconcile_core_reviews(review, CORE_IDS, BLOCK_IDS)

    assert result.passed_core_ids == ("REC-001", "REC-003")
    assert result.affected_core_ids == ("REC-002",)
    assert result.reason_codes == ("SEMANTIC_REVIEW_TARGET_UNRESOLVED",)


def test_one_malformed_core_review_withholds_only_that_core():
    malformed = _core("REC-002")
    malformed["source_block_ids"] = ["DOC-unknown"]
    result = reconcile_core_reviews(
        _review(
            _core("REC-001"), malformed, _core("REC-003"),
            passed=CORE_IDS,
        ),
        CORE_IDS,
        BLOCK_IDS,
    )

    assert result.passed_core_ids == ("REC-001", "REC-003")
    assert result.affected_core_ids == ("REC-002",)
    assert result.invalid_core_ids == ("REC-002",)
    assert result.reason_codes == ("SEMANTIC_REVIEW_TARGET_UNRESOLVED",)


def test_duplicate_missing_and_unknown_reviews_do_not_remove_valid_passes():
    result = reconcile_core_reviews(
        _review(
            _core("REC-001"), _core("REC-001"), _core("REC-unknown"),
            _core("REC-003"), passed=CORE_IDS,
        ),
        CORE_IDS,
        BLOCK_IDS,
    )

    assert result.passed_core_ids == ("REC-003",)
    assert result.affected_core_ids == ("REC-001", "REC-002")
    assert result.invalid_core_ids == ("REC-001", "REC-002")
    assert result.reason_codes == ("SEMANTIC_REVIEW_TARGET_UNRESOLVED",)


def test_malformed_reason_contract_is_local_to_its_core():
    bad_supported = _core(
        "REC-002", codes=["PROJECT_FACT_UNSUPPORTED"],
    )
    result = reconcile_core_reviews(
        _review(
            _core("REC-001"), bad_supported, _core("REC-003"),
            passed=CORE_IDS,
        ),
        CORE_IDS,
        BLOCK_IDS,
    )

    assert result.passed_core_ids == ("REC-001", "REC-003")
    assert result.invalid_core_ids == ("REC-002",)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("premise_verdict", []),
        ("reason_codes", [{}]),
        ("source_block_ids", [{}]),
    ],
)
def test_unhashable_malformed_values_are_withheld_not_raised(field, value):
    malformed = _core("REC-002")
    malformed[field] = value
    result = reconcile_core_reviews(
        _review(
            _core("REC-001"), malformed, _core("REC-003"),
            passed=CORE_IDS,
            issues=[{"object_id": {}, "reason_codes": [], "explanation": "bad"}],
        ),
        CORE_IDS,
        BLOCK_IDS,
    )

    assert result.passed_core_ids == ("REC-001", "REC-003")
    assert result.invalid_core_ids == ("REC-002",)
