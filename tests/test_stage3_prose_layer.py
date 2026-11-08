"""Render-only Stage 3 analytical prose layer: on by default, legacy switch restores the old style."""
import app


def _build(monkeypatch, style=None):
    monkeypatch.delenv("FCV_STAGE3_PROSE_STYLE", raising=False)
    if style is not None:
        monkeypatch.setenv("FCV_STAGE3_PROSE_STYLE", style)
    return app.append_core_concise_stage3_contract(app.get_prompt_for_stage(3), "PAD", {}, "design", [])


def test_prose_layer_is_on_by_default(monkeypatch):
    prompt = _build(monkeypatch)
    assert "HOW A STRONG OPENING IS BUILT" in prompt
    assert "NARRATIVE STYLE FOR THE DETAILED NOTE" in prompt
    assert app._GUARDRAIL_STYLE_OLD not in prompt and app._GUARDRAIL_STYLE_NEW in prompt
    assert "Write the narrative in a clear technical report style for management." not in prompt
    assert prompt.rstrip().endswith("write the points as linked sentences instead.")
    # The JSON-first order is kept.
    assert "OUTPUT ORDER OVERRIDE" in prompt


def test_every_section_spec_applies(monkeypatch):
    prompt = _build(monkeypatch)
    for old, new in app._STAGE3_SECTION_SPECS:
        assert old.splitlines()[0] not in prompt
        assert new.splitlines()[0] in prompt


def test_legacy_switch_restores_previous_prompt(monkeypatch):
    prompt = _build(monkeypatch, "legacy")
    assert "HOW A STRONG OPENING IS BUILT" not in prompt
    assert app._GUARDRAIL_STYLE_OLD in prompt
    assert "Write the narrative in a clear technical report style for management." in prompt
    assert "### Opening Assessment (ONE BOLD SENTENCE, 25-35 words)" in prompt
    assert "FINAL FORMAT CHECK" not in prompt


def test_shared_base_prompt_text_is_unchanged():
    # The layer is applied at assembly; DEFAULT_PROMPTS["3"] keeps the shared wording.
    base = app.DEFAULT_PROMPTS["3"]
    assert "### Opening Assessment (ONE BOLD SENTENCE, 25-35 words)" in base
    assert "HOW A STRONG OPENING IS BUILT" not in base


def test_no_example_text_from_owner_notes_in_prompt(monkeypatch):
    prompt = _build(monkeypatch)
    assert "Do not reuse wording from any example sentence" in prompt
    for phrase in ("gender apartheid", "Hirak Rif", "AANES", "Deir ez-Zor"):
        assert phrase not in prompt


def test_stage3_output_budget_and_model():
    assert app._stage_output_budget(3) == 48000
    assert app._stage_output_budget(2) == app.STAGE_MAX_TOKENS[2]
    assert app._stage_model(3) == app.MODEL_REASONING


def test_prose_repair_on_by_default_and_switchable(monkeypatch):
    listy = "### Strengths\n\n**Lead.** Text:\n- one;\n- two.\n"
    calls = []

    def fake_client():
        class Messages:
            def create(self, **kwargs):
                calls.append(kwargs)
                raise RuntimeError("no network in tests")
        class Client:
            messages = Messages()
        return Client()

    monkeypatch.setattr(app, "get_client", fake_client)
    monkeypatch.delenv("FCV_STAGE3_PROSE_REPAIR", raising=False)
    holder = {}
    list(app._stage3_prose_repair_events(listy, "t", holder))
    assert calls and holder["text"] == listy and holder["report"]["reason"].startswith("call_failed")

    calls.clear()
    monkeypatch.setenv("FCV_STAGE3_PROSE_REPAIR", "0")
    holder = {}
    list(app._stage3_prose_repair_events(listy, "t", holder))
    assert not calls and holder["text"] == listy
