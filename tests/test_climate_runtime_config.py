from __future__ import annotations

import pytest

from sector_lenses.climate_runtime_config import (
    QUALITY_MODEL,
    SMOKE_MODEL,
    load_verified_climate_runtime,
)


def test_quality_profile_is_the_safe_production_default():
    config = load_verified_climate_runtime({})

    assert config.mode == "quality"
    assert config.assessment_model == QUALITY_MODEL
    assert config.reviewer_model == QUALITY_MODEL


def test_smoke_profile_uses_the_low_cost_model_for_both_calls():
    config = load_verified_climate_runtime({
        "CLIMATE_VERIFIED_RUN_MODE": "smoke",
    })

    assert config.mode == "smoke"
    assert config.assessment_model == SMOKE_MODEL
    assert config.reviewer_model == SMOKE_MODEL


def test_explicit_server_model_overrides_are_honored():
    config = load_verified_climate_runtime({
        "CLIMATE_VERIFIED_RUN_MODE": "smoke",
        "CLIMATE_VERIFIED_ASSESSMENT_MODEL": "assessment-test-model",
        "CLIMATE_VERIFIED_REVIEW_MODEL": "review-test-model",
    })

    assert config.assessment_model == "assessment-test-model"
    assert config.reviewer_model == "review-test-model"


def test_invalid_runtime_mode_is_rejected_instead_of_silently_rerouted():
    with pytest.raises(ValueError, match="CLIMATE_VERIFIED_RUN_MODE"):
        load_verified_climate_runtime({
            "CLIMATE_VERIFIED_RUN_MODE": "cheap-ish",
        })
