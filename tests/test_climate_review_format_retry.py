"""One resample of a conditional review whose every core record is malformed.

Reproduces the 2026-11-13 ITS QA failure (run esq0pe215y1p): the reviewer said
"pass" but every core record failed the structural contract, so the pipeline
converted the verdict to block and withheld all priorities.
"""
from __future__ import annotations

import json

from sector_lenses.climate_verified_pipeline import (
    REVIEW_FORMAT_RETRY_HEADROOM_SECONDS,
    PipelineClients,
    run_verified_climate_pipeline,
)
from sector_lenses.climate_verified_render import build_reader_model
from sector_lenses.pipeline import normalize_climate_assessment
from tests.test_climate_verified_pipeline import (
    FakeClient,
    _arguments,
    _native_pass_review,
    _responses,
)


def _malformed_pass_review(**kwargs):
    """A 'pass' whose core records cite a fact ID instead of a source block."""
    review = _native_pass_review(**kwargs)
    for record in review["core_reviews"]:
        record["source_block_ids"] = ["PF-001"]
    return review


def _review_calls(client):
    return [call for call in client.calls if call["stage"] == "conditional_review"]


def test_all_invalid_core_records_get_one_resample_that_restores_priorities():
    reviewer = FakeClient([_malformed_pass_review, _native_pass_review], [])
    result = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(FakeClient(_responses(), []), reviewer))

    calls = _review_calls(reviewer)
    assert len(calls) == 2
    assert calls[0]["payload"] == calls[1]["payload"]
    assert len(result["priorities"]) == 1
    diagnostics = result["recommendation_diagnostics"]
    assert diagnostics["reviewer_verdict"] == "pass"
    assert diagnostics["semantic_review_retry"] == {
        "first_invalid_core_ids": ["REC-001"],
        "retry_invalid_core_ids": [],
        "adopted": True,
    }
    assert "RECOMMENDATIONS_ALL_SUPPRESSED" not in diagnostics["reason_codes"]
    assert "semantic_review_excerpt" not in diagnostics
    trace = result["diagnostic_trace"]["semantic_review_retry"]
    assert "PF-001" in trace["first_review"]["json"]


def test_second_malformed_review_keeps_withholding_and_saves_excerpt():
    reviewer = FakeClient([_malformed_pass_review, _malformed_pass_review], [])
    result = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(FakeClient(_responses(), []), reviewer))

    assert len(_review_calls(reviewer)) == 2
    assert result["priorities"] == []
    diagnostics = result["recommendation_diagnostics"]
    assert "RECOMMENDATIONS_ALL_SUPPRESSED" in diagnostics["reason_codes"]
    assert diagnostics["semantic_review_retry"] == {
        "first_invalid_core_ids": ["REC-001"],
        "retry_invalid_core_ids": ["REC-001"],
    }
    excerpt = diagnostics["semantic_review_excerpt"]
    assert len(excerpt) <= 6000
    assert json.loads(excerpt)["core_reviews"][0]["source_block_ids"] == ["PF-001"]


def test_retry_failure_keeps_first_review_without_crashing():
    reviewer = FakeClient([_malformed_pass_review], [])  # second call raises IndexError
    result = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(FakeClient(_responses(), []), reviewer))

    assert result["priorities"] == []
    assert result["recommendation_diagnostics"]["semantic_review_retry"]["failure"] == "IndexError"


def test_retry_is_skipped_when_it_would_starve_the_final_reader():
    reviewer = FakeClient([_malformed_pass_review, _native_pass_review], [])
    result = run_verified_climate_pipeline(
        **{**_arguments(), "wall_clock_seconds": REVIEW_FORMAT_RETRY_HEADROOM_SECONDS - 5},
        clients=PipelineClients(FakeClient(_responses(), []), reviewer))

    assert len(_review_calls(reviewer)) == 1
    assert result["priorities"] == []
    assert result["recommendation_diagnostics"]["semantic_review_retry"]["skipped"] == "deadline"


def test_valid_review_is_never_resampled():
    reviewer = FakeClient([_native_pass_review], [])
    result = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(FakeClient(_responses(), []), reviewer))

    assert len(_review_calls(reviewer)) == 1
    assert "semantic_review_retry" not in result["recommendation_diagnostics"]
    assert result["diagnostic_trace"]["semantic_review_retry"] == {}


def test_reader_annex_carries_support_fields_only_when_present():
    failed = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(
            FakeClient(_responses(), []),
            FakeClient([_malformed_pass_review, _malformed_pass_review], [])))
    annex = build_reader_model(normalize_climate_assessment(failed))["technical_annex"]
    assert annex["semantic_review_retry"]["retry_invalid_core_ids"] == ["REC-001"]
    assert "PF-001" in annex["semantic_review_excerpt"]

    clean = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(
            FakeClient(_responses(), []), FakeClient([_native_pass_review], [])))
    annex = build_reader_model(normalize_climate_assessment(clean))["technical_annex"]
    assert "semantic_review_retry" not in annex
    assert "semantic_review_excerpt" not in annex
