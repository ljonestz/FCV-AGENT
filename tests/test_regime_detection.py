"""Phase 2 — Stage 1 regime detection: parser, strip, and AnalysisState wiring."""

import app as app_module


BLOCK = (
    "Intro text.\n"
    "%%%REGIME_CONTEXT_START%%%\n"
    "ois_creation_date: 2026-05-02\n"
    "preparation_regime_source: OIS datasheet\n"
    "concept_decision_or_equivalent_date: 2022-03-01\n"
    "concept_date_source: Project Datasheet\n"
    "op_bp_4_03_applies: false\n"
    "additional_financing_exception_applies: false\n"
    "op_7_50_screen: true\n"
    "op_7_60_screen: false\n"
    "evidence_markers: Project Paper; Technical Design Review; ANNEX 1: Results Framework\n"
    "conflicting_evidence: none\n"
    "%%%REGIME_CONTEXT_END%%%\n"
    "Body continues."
)


def test_extract_regime_context_classifies_both_axes():
    ctx = app_module.extract_regime_context(BLOCK)
    assert ctx["preparation_regime"] == "new_model"          # OIS 2026-05-02 >= 18 Apr 2026
    assert ctx["es_regime"] == "ESF_ESS1_TO_ESS10"           # Concept 2022 >= 1 Oct 2018
    assert ctx["op_7_50_screen"] is True
    assert ctx["op_7_60_screen"] is False


def test_extract_regime_context_legacy_and_pre_esf():
    block = (
        "%%%REGIME_CONTEXT_START%%%\n"
        "ois_creation_date: 2025-11-01\n"
        "concept_decision_or_equivalent_date: 2017-01-01\n"
        "%%%REGIME_CONTEXT_END%%%\n"
    )
    ctx = app_module.extract_regime_context(block)
    assert ctx["preparation_regime"] == "legacy_transitional"
    assert ctx["es_regime"] == "LEGACY_SAFEGUARDS"


def test_missing_block_defaults_safely():
    ctx = app_module.extract_regime_context("no block here")
    assert ctx["preparation_regime"] == "unresolved_policy_source"
    assert ctx["es_regime"] == "UNRESOLVED"
    assert ctx["verification_flag"] is True


def test_clean_stage1_strips_regime_block():
    cleaned = app_module.clean_stage1_output(BLOCK)
    assert "REGIME_CONTEXT_START" not in cleaned
    assert "ois_creation_date" not in cleaned
    assert "Body continues." in cleaned
    assert "Intro text." in cleaned


# --- Task 2.3: AnalysisState carries regime fields ---------------------------

def test_analysis_state_carries_regime_fields():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": [], "lens_versions": {}, "doc_type": "PAD",
        "regime_context": {
            "preparation_regime": "new_model",
            "es_regime": "ESF_ESS1_TO_ESS10",
            "processing_model": "two_step",
        },
    })
    assert state.preparation_regime == "new_model"
    assert state.es_regime == "ESF_ESS1_TO_ESS10"
    assert state.processing_model == "two_step"


def test_analysis_state_regime_defaults_when_absent():
    state = app_module.AnalysisState.from_payload({"active_lenses": [], "lens_versions": {}, "doc_type": "PAD"})
    assert state.preparation_regime == "unresolved_policy_source"
    assert state.es_regime == "UNRESOLVED"
    assert state.processing_model == "unknown"


# --- Task 2.2: Stage 1 prompt emits the regime block -------------------------

def test_stage1_prompt_requests_regime_block():
    p = app_module.DEFAULT_PROMPTS["1"]
    assert "%%%REGIME_CONTEXT_START%%%" in p
    assert "ois_creation_date" in p
    assert "concept_decision_or_equivalent_date" in p
    assert "18 April 2026" in p or "2026-04-18" in p
    assert "1 October 2018" in p or "2018-10-01" in p
    assert "Published" in p and "Public" in p
