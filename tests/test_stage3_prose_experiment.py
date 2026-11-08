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
