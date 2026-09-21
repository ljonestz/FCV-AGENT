"""Phase 7 — regime header/section injection into the Stage 3 prompt + legacy
byte-for-byte regression guard for the regime-sensitive helpers.

The Stage 3 prompt is normally formatted at the two design-review call sites with a
fixed set of kwargs. These tests format DEFAULT_PROMPTS["3"] the same way to assert
regime-appropriate rendering without booting the Flask app.
"""

import app as app_module


# Mirror the kwargs the two design-review Stage 3 call sites pass to .format().
def _format_stage3(preparation_regime, processing_model, es_regime, instrument="IPF"):
    return app_module.DEFAULT_PROMPTS["3"].format(
        doc_type="PAD",
        timing_emphasis="Preparation",
        playbook_guidance="",
        instrument_guidance="",
        temporal_guardrail="",
        seash_gender_card_guidance="",
        regime_header=app_module.build_regime_header(
            preparation_regime, processing_model, es_regime, instrument
        ),
        minimum_reference_set=app_module.build_minimum_reference_block(
            preparation_regime, es_regime, instrument
        ),
    )


# ── build_regime_header ──────────────────────────────────────────────────────

def test_regime_header_empty_for_legacy_and_unresolved():
    assert app_module.build_regime_header("legacy_transitional", "unknown", "LEGACY_SAFEGUARDS", "IPF") == ""
    assert app_module.build_regime_header("unresolved_policy_source", "unknown", "UNRESOLVED", "IPF") == ""


def test_regime_header_new_model_two_step_names_td_ir_and_label():
    header = app_module.build_regime_header("new_model", "two_step", "ESF_ESS1_TO_ESS10", "IPF")
    assert "Technical Design" in header
    assert "Implementation Readiness" in header
    assert "Project Paper" in header          # regime-rendered document label (Task 3.2)
    assert "before appraisal" not in header.lower()


def test_regime_header_new_model_one_step_names_one_review():
    header = app_module.build_regime_header("new_model", "one_step", "ESF_ESS1_TO_ESS10", "IPF")
    assert "One Review" in header
    assert "before appraisal" not in header.lower()


def test_regime_header_new_model_pforr_uses_program_paper_label():
    header = app_module.build_regime_header("new_model", "two_step", "INSTRUMENT_SPECIFIC", "PforR")
    assert "Program Paper" in header


# ── build_minimum_reference_block ────────────────────────────────────────────

def test_minimum_reference_block_new_model_ipf():
    block = app_module.build_minimum_reference_block("new_model", "ESF_ESS1_TO_ESS10", "IPF")
    low = block.lower()
    assert "project assessment summary" in low
    assert "readiness esrs" in low
    assert "operations manual" not in low     # removed from the new-model universal minimum


def test_minimum_reference_block_legacy_is_verbatim_current_text():
    block = app_module.build_minimum_reference_block("legacy_transitional", "LEGACY_SAFEGUARDS", "IPF")
    # Legacy keeps the existing PAD-stage floor verbatim, including Operations Manual + ESS1.
    assert "MINIMUM INSTRUMENT REFERENCE REQUIREMENT" in block
    assert "Operations Manual" in block
    assert "PAD STAGE ONLY" in block


# ── Assembled Stage 3 prompt ─────────────────────────────────────────────────

def test_new_model_stage3_prompt_names_td_ir_gates():
    prompt = _format_stage3("new_model", "two_step", "ESF_ESS1_TO_ESS10", "IPF")
    assert "Technical Design" in prompt and "Implementation Readiness" in prompt
    assert "Readiness ESRS" in prompt
    assert "before appraisal" not in prompt.lower()


def test_legacy_stage3_prompt_keeps_appraisal_and_legacy_reference_set():
    prompt = _format_stage3("legacy_transitional", "unknown", "LEGACY_SAFEGUARDS", "IPF")
    assert "appraisal" in prompt.lower()               # legacy still speaks appraisal vocabulary
    assert "Operations Manual" in prompt               # legacy minimum reference set intact
    assert "Technical Design" not in prompt            # no new-model gate framing


def test_unresolved_stage3_prompt_matches_legacy_default():
    # The safe default (no regime detected) must render exactly like legacy.
    unresolved = _format_stage3("unresolved_policy_source", "unknown", "UNRESOLVED", "IPF")
    legacy = _format_stage3("legacy_transitional", "unknown", "LEGACY_SAFEGUARDS", "IPF")
    assert unresolved == legacy


# ── Legacy-default regression guard (Task 7.2) ───────────────────────────────

def test_regime_helpers_default_to_legacy_values():
    assert app_module.appraisal_document_label("unresolved_policy_source", "IPF") == "Project Appraisal Document (PAD)"
    assert app_module.appraisal_reference_set("unresolved_policy_source", "UNRESOLVED", "IPF") == \
        app_module.LEGACY_PAD_MINIMUM_REFERENCE_SET
    import regime_router
    assert regime_router.resolve_action_timing(
        "required-before-appraisal", "unresolved_policy_source", "IPF"
    ) == "required-before-appraisal"
