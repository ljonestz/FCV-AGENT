import pytest

from sector_lenses.climate_source_blocks import SourceBlock
from sector_lenses.climate_truth import (
    DerivedAssertion,
    ProjectFactClaim,
    TargetedRetrievalRequest,
    match_supporting_excerpt,
    normalize_fact_registry,
    validate_derived_assertions,
)


BLOCK = SourceBlock(
    block_id="DOC-01-B-abc",
    document_id="DOC-01",
    text=(
        "A school feeding feasibility study will be completed in Year 1 "
        "of implementation."
    ),
    normalized_hash="abc",
    heading_path=("Component 1",),
    paragraph_index=12,
)


def _claim(**overrides) -> ProjectFactClaim:
    values = {
        "claim_id": "PF-017",
        "claim_type": "named_instrument",
        "subject": "feasibility study",
        "predicate": "timing",
        "object_value": "Year 1 of implementation",
        "epistemic_status": "explicit",
        "source_block_ids": (BLOCK.block_id,),
        "supporting_excerpt": (
            "A school feeding feasibility study will be completed in Year 1"
        ),
        "confidence": "high",
    }
    values.update(overrides)
    return ProjectFactClaim(**values)


def test_exact_and_normalized_matches_are_automatically_usable():
    exact = match_supporting_excerpt(
        "A school feeding feasibility study will be completed",
        BLOCK,
    )
    normalized = match_supporting_excerpt(
        "A  school feeding feasibility study\nwill be completed",
        BLOCK,
    )
    assert exact.status.value == "verbatim"
    assert exact.automatically_usable is True
    assert normalized.status.value == "normalized_exact"
    assert normalized.automatically_usable is True


def test_fuzzy_or_missing_excerpt_cannot_automatically_support_fact():
    result = match_supporting_excerpt(
        "A fisheries infrastructure feasibility study will be completed",
        BLOCK,
    )
    assert result.status.value in {"bounded_fuzzy", "unresolved"}
    assert result.automatically_usable is False


def test_explicit_fact_requires_resolvable_excerpt():
    result = normalize_fact_registry(
        [_claim(supporting_excerpt="A different study")],
        [BLOCK],
    )
    assert result.blocking_issues[0].code == "FACT_SOURCE_UNRESOLVED"


def test_not_found_is_not_promoted_to_confirmed_absence():
    claim = _claim(
        epistemic_status="not_found",
        source_block_ids=(),
        supporting_excerpt=None,
    )
    result = normalize_fact_registry([claim], [BLOCK])
    assert result.claims[0].epistemic_status == "not_found"
    assert result.blocking_issues == ()


def test_confirmed_absence_requires_explicit_negative_source():
    claim = _claim(
        epistemic_status="confirmed_absence",
        source_block_ids=(),
        supporting_excerpt=None,
    )
    result = normalize_fact_registry([claim], [BLOCK])
    assert result.blocking_issues[0].code == "ABSENCE_NOT_EXPLICIT"


def test_explicit_negative_source_can_confirm_absence():
    negative_block = SourceBlock(
        block_id="DOC-01-B-negative",
        document_id="DOC-01",
        text="The project does not include a site-level conflict study.",
        normalized_hash="negative",
        heading_path=("Scope",),
    )
    claim = _claim(
        epistemic_status="confirmed_absence",
        source_block_ids=(negative_block.block_id,),
        supporting_excerpt=(
            "The project does not include a site-level conflict study."
        ),
    )
    result = normalize_fact_registry([claim], [negative_block])
    assert result.blocking_issues == ()


def test_registry_enforces_hard_fact_limit():
    claims = [
        _claim(
            claim_id=f"PF-{index:03d}",
            epistemic_status="not_found",
            source_block_ids=(),
            supporting_excerpt=None,
        )
        for index in range(101)
    ]
    with pytest.raises(ValueError, match="100"):
        normalize_fact_registry(claims, [BLOCK])


def test_targeted_retrieval_request_is_bounded():
    request = TargetedRetrievalRequest(
        question="Does the document define the study scope?",
        terms=("feasibility study", "scope"),
        maximum_blocks=8,
    )
    assert request.maximum_blocks == 8
    with pytest.raises(ValueError, match="between 1 and 12"):
        TargetedRetrievalRequest("Question", (), maximum_blocks=13)


def test_derived_assertion_requires_existing_inputs_and_explanation():
    valid = DerivedAssertion(
        assertion_id="DA-001",
        assertion_type="timing_comparison",
        statement="The study occurs after the relevant preparation decision.",
        input_fact_ids=("PF-001", "PF-002"),
        derivation_method="deterministic",
        explanation="Implementation Year 1 follows appraisal.",
        confidence="high",
        validation_status="validated",
    )
    invalid = DerivedAssertion(
        assertion_id="DA-002",
        assertion_type="scope_inference",
        statement="The study covers infrastructure siting.",
        input_fact_ids=("PF-999",),
        derivation_method="semantic",
        explanation="",
        confidence="high",
        validation_status="pending",
    )
    issues = validate_derived_assertions(
        [valid, invalid],
        known_fact_ids={"PF-001", "PF-002"},
    )
    assert {issue.code for issue in issues} == {
        "DERIVATION_INPUT_MISSING",
        "DERIVATION_EXPLANATION_MISSING",
    }


def test_derived_assertion_id_cannot_masquerade_as_fact():
    assertion = DerivedAssertion(
        assertion_id="PF-003",
        assertion_type="timing_comparison",
        statement="A derived statement.",
        input_fact_ids=("PF-001",),
        derivation_method="deterministic",
        explanation="Compared two dates.",
        confidence="medium",
        validation_status="validated",
    )
    issues = validate_derived_assertions([assertion], {"PF-001"})
    assert issues[0].code == "DERIVATION_ID_INVALID"
