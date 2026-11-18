"""Zero-priority Phase 2 (2026-11-17): retries, format coercion and reviewer-record tolerance."""

from copy import deepcopy

import pytest

import sector_lenses.climate_verified_pipeline as pipeline
from sector_lenses.climate_recommendations import normalize_format_fields
from sector_lenses.climate_review_admission import reconcile_core_reviews
from sector_lenses.climate_verified_pipeline import (
    PipelineClients,
    _is_format_failure,
    run_verified_climate_pipeline,
)
from tests.test_climate_verified_pipeline import (
    FakeClient,
    _arguments,
    _core_review,
    _pass_review_client,
    _responses,
)


def test_format_failure_detection():
    assert _is_format_failure(ValueError(
        "Structured climate output incomplete (stage=x; stop_reason=max_tokens; characters=9)"))
    assert _is_format_failure(ValueError("Expected valid structured JSON (stage=x)"))
    assert not _is_format_failure(ValueError(
        "Structured climate output incomplete (stage=x; stop_reason=refusal; characters=0)"))
    assert not _is_format_failure(ValueError("something else"))


def test_truncated_compiler_reply_is_retried_once_with_a_larger_allowance():
    responses = _responses()
    good = responses[3]
    seen = []

    def truncated(**kwargs):
        seen.append(kwargs["max_output_tokens"])
        raise ValueError("Structured climate output incomplete (stage=recommendation_compiler; "
                         "stop_reason=max_tokens; characters=100)")

    def retried(**kwargs):
        seen.append(kwargs["max_output_tokens"])
        return good

    responses[3:4] = [truncated, retried]
    result = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(FakeClient(responses, []), _pass_review_client()))
    assert len(seen) == 2 and seen[1] > seen[0]
    assert result["priorities"]


def test_empty_compiler_list_with_material_gaps_is_retried_once(monkeypatch):
    monkeypatch.setattr(pipeline, "_EMPTY_RETRY_MIN_GAPS", 1)
    responses = _responses()
    good = deepcopy(responses[3])
    responses[3:4] = [{"recommendation_candidates": [], "readiness_flags": []}, good]
    assessment = FakeClient(responses, [])
    result = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(assessment, _pass_review_client()))
    assert result["priorities"]
    assert "RECOMMENDATIONS_EMPTY_RETRY_ATTEMPTED" in result["validation"]["reason_codes"]
    compiler_calls = [c for c in assessment.calls if c["stage"] == "recommendation_compiler"]
    assert len(compiler_calls) == 2 and "retry_note" in compiler_calls[1]["payload"]


def test_empty_compiler_list_without_enough_gaps_is_not_retried(monkeypatch):
    monkeypatch.setattr(pipeline, "_EMPTY_RETRY_MIN_GAPS", 99)
    responses = _responses()
    responses[3] = {"recommendation_candidates": [], "readiness_flags": []}
    assessment = FakeClient(responses, [])
    result = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(assessment, _pass_review_client()))
    assert result["priorities"] == []
    assert len([c for c in assessment.calls if c["stage"] == "recommendation_compiler"]) == 1


def test_invalid_enum_values_are_coerced_conservatively_not_suppressed():
    responses = _responses()
    candidate = responses[3]["recommendation_candidates"][0]
    candidate.update({"routing_status": "advisory", "authority_basis": "policy_note",
                      "recommendation_basis": "evidence", "completion_evidence_status": "done"})
    result = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(FakeClient(responses, []), _pass_review_client()))
    assert len(result["priorities"]) == 1
    kept = result["priorities"][0]
    assert kept["routing_status"] == "standard_document_advisory"
    assert kept["authority_basis"] == "none_verified"
    assert kept["recommendation_basis"] == "analytical_judgment"
    assert kept["completion_evidence_status"] == "team_to_define"


@pytest.mark.parametrize("enhanced, activation, kept", [("Do more.", None, None), ("Do more.", "If X.", "Do more.")])
def test_enhanced_action_without_activation_is_dropped(enhanced, activation, kept):
    from sector_lenses.climate_verified_pipeline import _candidate
    record = deepcopy(_responses()[3]["recommendation_candidates"][0])
    record.update({"enhanced_action": enhanced, "enhanced_activation": activation})
    candidate, _repairs = normalize_format_fields(_candidate(record))
    assert candidate.enhanced_action == kept


def test_core_record_with_one_real_passage_and_a_fact_id_is_valid():
    review = {"verdict": "pass", "passed_core_ids": ["REC-001"], "core_reviews": [
        {**_core_review(), "source_block_ids": ["B-1", "PF-001"]}]}
    admission = reconcile_core_reviews(review, ["REC-001"], ["B-1"])
    assert admission.passed_core_ids == ("REC-001",) and not admission.invalid_core_ids
    only_facts = {"verdict": "pass", "passed_core_ids": ["REC-001"], "core_reviews": [
        {**_core_review(), "source_block_ids": ["PF-001"]}]}
    assert reconcile_core_reviews(only_facts, ["REC-001"], ["B-1"]).invalid_core_ids == ("REC-001",)
