"""Env-gated Stage 3 prose experiment switches stay off by default."""
import app


def test_contract_unchanged_by_default(monkeypatch):
    monkeypatch.delenv("FCV_STAGE3_STYLE_EXPERIMENT", raising=False)
    assert app._stage3_contract_text() == app.STANDARD_FCV_STAGE3_OUTPUT_CONTRACT


def test_style_experiment_replaces_only_the_style_paragraph(monkeypatch):
    monkeypatch.setenv("FCV_STAGE3_STYLE_EXPERIMENT", "1")
    text = app._stage3_contract_text()
    assert "plain management language, define acronyms" not in text
    assert "connected\nanalytical prose" in text and "SUMMARY LAYER ONLY" in text
    assert "Do not use bullet lists" in text
    # Everything around the paragraph is preserved.
    assert text.startswith("## STANDARD FCV MANAGEMENT READOUT")
    assert 'In "concise_readout", provide a one-sentence headline' in text
    assert "OUTPUT ORDER OVERRIDE" in text


def test_stage3_model_experiment(monkeypatch):
    monkeypatch.delenv("FCV_STAGE3_MODEL_EXPERIMENT", raising=False)
    assert app._stage_model(3) == app.MODEL_REASONING
    monkeypatch.setenv("FCV_STAGE3_MODEL_EXPERIMENT", "claude-sonnet-5-5")
    assert app._stage_model(3) == "claude-sonnet-5-5"
    assert app._stage_model(2) == app.MODEL_REASONING
    monkeypatch.setenv("FCV_STAGE3_MODEL_EXPERIMENT", "gpt-anything")
    assert app._stage_model(3) == app.MODEL_REASONING


def _build(monkeypatch, **env):
    for key in ("FCV_STAGE3_STYLE_EXPERIMENT", "FCV_STAGE3_ORDER_EXPERIMENT"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return app.append_core_concise_stage3_contract(app.get_prompt_for_stage(3), "PAD", {}, "design", [])


def test_default_prompt_is_unchanged_by_experiment_code(monkeypatch):
    prompt = _build(monkeypatch)
    assert app._GUARDRAIL_STYLE_OLD in prompt
    assert "HOW A STRONG OPENING IS BUILT" not in prompt
    assert "OUTPUT ORDER OVERRIDE" in prompt
    assert "### Opening Assessment (ONE BOLD SENTENCE, 25-35 words)" in prompt


def test_style_v2_applies_specs_guardrail_and_description(monkeypatch):
    prompt = _build(monkeypatch, FCV_STAGE3_STYLE_EXPERIMENT="2")
    assert "HOW A STRONG OPENING IS BUILT" in prompt
    assert app._GUARDRAIL_STYLE_OLD not in prompt and app._GUARDRAIL_STYLE_NEW in prompt
    assert "### Opening Assessment (ONE BOLD SENTENCE, 35-60 words)" in prompt
    assert "### Operational Context (180-240 words, ONE PARAGRAPH)" in prompt
    assert "Do not reuse wording from any example sentence" in prompt


def test_narrative_first_restores_base_order(monkeypatch):
    prompt = _build(monkeypatch, FCV_STAGE3_STYLE_EXPERIMENT="2", FCV_STAGE3_ORDER_EXPERIMENT="narrative_first")
    assert "OUTPUT ORDER OVERRIDE" not in prompt
    assert "The JSON block must come AFTER all narrative text." in prompt


def test_max_tokens_experiment_bounds(monkeypatch):
    monkeypatch.delenv("FCV_STAGE3_MAX_TOKENS_EXPERIMENT", raising=False)
    assert app._stage_output_budget(3) == app.STAGE_MAX_TOKENS[3]
    monkeypatch.setenv("FCV_STAGE3_MAX_TOKENS_EXPERIMENT", "48000")
    assert app._stage_output_budget(3) == 48000 and app._stage_output_budget(2) == app.STAGE_MAX_TOKENS[2]
    monkeypatch.setenv("FCV_STAGE3_MAX_TOKENS_EXPERIMENT", "900000")
    assert app._stage_output_budget(3) == app.STAGE_MAX_TOKENS[3]
