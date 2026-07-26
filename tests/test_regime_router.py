"""Unit tests for the pure OPCS regime router (Phase 1 of the dual-regime plan).

Decision tables cited to memory `project_opcs_july2026_process_change.md` and the
spec `docs/superpowers/specs/2026-07-26-dual-regime-process-model-design.md`.
"""

import datetime as dt

import regime_router as rr


# --- Task 1.1: preparation-regime classifier ---------------------------------

def test_preparation_boundary_is_18_april_2026():
    assert rr.PREPARATION_BOUNDARY == dt.date(2026, 4, 18)


def test_ois_on_or_after_boundary_is_new_model():
    assert rr.classify_preparation_regime(dt.date(2026, 4, 18)) == "new_model"
    assert rr.classify_preparation_regime(dt.date(2026, 6, 1)) == "new_model"


def test_ois_before_boundary_is_legacy_transitional():
    assert rr.classify_preparation_regime(dt.date(2026, 4, 17)) == "legacy_transitional"
    assert rr.classify_preparation_regime(dt.date(2024, 1, 1)) == "legacy_transitional"


def test_missing_ois_date_is_unresolved():
    assert rr.classify_preparation_regime(None) == "unresolved_policy_source"


# --- Task 1.2: one/two-step processing-model classifier ----------------------

def test_ipf_first_mpa_phase_is_two_step():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Low", es_risk="Low", is_first_mpa_phase=True,
    ) == "two_step"


def test_ipf_high_risk_is_two_step():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Substantial", es_risk="Moderate",
    ) == "two_step"
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Moderate", es_risk="High",
    ) == "two_step"


def test_ipf_low_moderate_both_is_one_step():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Moderate", es_risk="Low",
    ) == "one_step"


def test_ipf_af_is_one_step_even_if_high_risk():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="High", es_risk="High", is_af=True,
    ) == "one_step"


def test_ipf_small_tf_and_urgent_are_one_step():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="High", es_risk="High", small_tf_retf_le_5m=True,
    ) == "one_step"
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="High", es_risk="High", urgent_need_or_capacity=True,
    ) == "one_step"


def test_fmrf_not_af_is_two_step():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Low", es_risk="Low", is_fmrf=True,
    ) == "two_step"
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Low", es_risk="Low", is_fmrf=True, is_af=True,
    ) == "one_step"  # AF-to-existing-FMRF


def test_dpf_first_in_series_two_step_subsequent_one_step():
    assert rr.classify_processing_model(instrument="DPO", series_position="first") == "two_step"
    assert rr.classify_processing_model(instrument="DPO", series_position="subsequent") == "one_step"
    assert rr.classify_processing_model(instrument="DPO", series_position="standalone") == "two_step"
    assert rr.classify_processing_model(
        instrument="DPO", series_position="subsequent", dpf_supplemental_or_scalable=True,
    ) == "one_review"


def test_pforr_hybrid_needs_ipf_component_low_mod_for_one_step():
    # PforR ratings Low/Mod but IPF-component ESRC High -> two-step.
    assert rr.classify_processing_model(
        instrument="PforR", sort_overall="Moderate", es_risk="Low", hybrid_ipf_component_esrc="High",
    ) == "two_step"
    assert rr.classify_processing_model(
        instrument="PforR", sort_overall="Moderate", es_risk="Low", hybrid_ipf_component_esrc="Moderate",
    ) == "one_step"


def test_missing_risk_data_is_unknown():
    assert rr.classify_processing_model(instrument="IPF") == "unknown"


# --- Task 1.3: E&S-regime classifier + OP 7.50/7.60 screens ------------------

def test_es_non_ipf_is_instrument_specific():
    assert rr.classify_es_regime(instrument="PforR", concept_decision_date=dt.date(2022, 1, 1)) == "INSTRUMENT_SPECIFIC"
    assert rr.classify_es_regime(instrument="DPO", concept_decision_date=dt.date(2010, 1, 1)) == "INSTRUMENT_SPECIFIC"


def test_es_op_bp_4_03_takes_precedence():
    assert rr.classify_es_regime(
        instrument="IPF", concept_decision_date=dt.date(2022, 1, 1), op_bp_4_03_applies=True,
    ) == "PERFORMANCE_STANDARDS_OP_BP_4_03"


def test_es_af_exclusively_cost_overrun_is_legacy():
    assert rr.classify_es_regime(
        instrument="IPF", concept_decision_date=dt.date(2022, 1, 1),
        is_af=True, parent_under_safeguard_policies=True, af_exclusively_cost_overrun_or_gap=True,
    ) == "LEGACY_SAFEGUARDS"


def test_es_af_that_adds_activities_is_not_legacy_exception():
    assert rr.classify_es_regime(
        instrument="IPF", concept_decision_date=dt.date(2022, 1, 1),
        is_af=True, parent_under_safeguard_policies=True, af_exclusively_cost_overrun_or_gap=False,
    ) == "ESF_ESS1_TO_ESS10"


def test_es_concept_decision_on_or_after_2018_10_01_is_esf():
    assert rr.classify_es_regime(instrument="IPF", concept_decision_date=dt.date(2018, 10, 1)) == "ESF_ESS1_TO_ESS10"


def test_es_concept_decision_before_2018_10_01_is_legacy():
    assert rr.classify_es_regime(instrument="IPF", concept_decision_date=dt.date(2018, 9, 30)) == "LEGACY_SAFEGUARDS"


def test_es_missing_date_is_unresolved():
    assert rr.classify_es_regime(instrument="IPF", concept_decision_date=None) == "UNRESOLVED"


def test_op_7_screens_independent_of_es_regime():
    assert rr.op_7_50_screen(mentions_international_waterway=True) is True
    assert rr.op_7_60_screen(mentions_disputed_territory=True) is True
    assert rr.op_7_50_screen(mentions_international_waterway=False) is False


# --- Task 1.4: regime-aware action_timing vocabulary -------------------------

def test_legacy_timing_set_matches_current_enum():
    assert rr.action_timing_vocab("legacy_transitional", "IPF") == (
        "flag-for-preparation", "required-before-appraisal",
        "required-before-board", "next-series", "supervision",
    )


def test_new_model_ipf_timing_has_td_ir_and_no_before_appraisal():
    vocab = rr.action_timing_vocab("new_model", "IPF")
    assert "before-TD-review" in vocab
    assert "before-IR" in vocab
    assert "before-One-Review" in vocab
    assert "required-before-appraisal" not in vocab
    assert not any("appraisal" in v for v in vocab)


def test_resolve_maps_legacy_before_appraisal_to_new_model():
    assert rr.resolve_action_timing("required-before-appraisal", "new_model", "IPF") == "before-TD-review"
    assert rr.resolve_action_timing("required-before-appraisal", "legacy_transitional", "IPF") == "required-before-appraisal"
