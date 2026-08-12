import json

import app


_STAGE3_OUTPUT = "%%%JSON_START%%%" + json.dumps({
    "fcv_rating": "Adequate",
    "fcv_responsiveness_rating": "Low",
    "sensitivity_summary": "Sensitivity summary.",
    "responsiveness_summary": "Responsiveness summary.",
    "risk_exposure": {"risks_to": "Risk to.", "risks_from": "Risk from."},
    "mid_cycle_watch": [], "dpf_watch": [], "p4r_watch": [], "regional_watch": [],
    "priorities": [{
        "title": "Priority", "fcv_dimension": "Inclusion", "tag": "[S]",
        "refresh_shift": "Shift A: Anticipate", "risk_level": "Low",
        "the_gap": "Named group needs support.", "why_it_matters": "Delivery risk.",
        "actions": [], "who_acts": "TTL", "when": "Preparation",
        "action_timing": "flag-for-preparation", "resources": "Minimal",
        "pad_sections": "Project Description", "country_category_relevance": "Relevant.",
        "implementation_note": "Prepare.", "cpf_alignment": None,
        "rra_driver_alignment": None,
    }],
}) + "%%%JSON_END%%%"


def _lens_context(active_lenses):
    return {
        "active_lenses": active_lenses,
        "warnings": [],
        "restart_required": False,
        "prompt": "LENS CONTRACT" if active_lenses else "",
        "lens_diagnostic": {},
        "lens_context_sources": [],
    }


def _capture_run_stage3_prompt(monkeypatch, active_lenses):
    calls = []

    def fake_lens_context(*_args, **_kwargs):
        return _lens_context(active_lenses)

    def fake_stream(messages, _max_tokens, stage, **_kwargs):
        calls.append((stage, messages))
        fake_stream._last_result = _STAGE3_OUTPUT
        fake_stream._last_stop_reason = "end_turn"
        yield 'data: {"chunk": "stage3"}\n\n'

    monkeypatch.setattr(app, "build_lens_stage_context", fake_lens_context)
    monkeypatch.setattr(app, "_stream_stage", fake_stream)
    response = app.app.test_client().post("/api/run-stage", json={
        "stage": 3,
        "active_lenses": [item["id"] for item in active_lenses],
        "history": [{"role": "assistant", "content": "Stage 2 output."}],
        "document_type": "PAD", "doc_type": "PAD", "instrument_type": "IPF",
        "review_mode": "design", "temporal_context": {"processing_track": "standard"},
        "regime_context": {},
    })
    assert response.status_code == 200
    return next(messages for stage, messages in calls if stage == 3)[-1]["content"]


def _capture_express_stage3_prompt(monkeypatch, active_lenses):
    calls = []

    def fake_lens_context(_state, stage, **_kwargs):
        return _lens_context(active_lenses if stage == 3 else [])

    def fake_stream(messages, _max_tokens, stage, **_kwargs):
        calls.append((stage, messages))
        fake_stream._last_stop_reason = "end_turn"
        fake_stream._last_result = "Stage 1 output." if stage == 1 else (
            "Stage 2 output." if stage == 2 else _STAGE3_OUTPUT
        )
        yield 'data: {"chunk": "stage"}\n\n'

    monkeypatch.setattr(app, "build_lens_stage_context", fake_lens_context)
    monkeypatch.setattr(app, "_stream_stage", fake_stream)
    monkeypatch.setattr(app, "extract_country_name", lambda _text, _client: "Exampleland")
    monkeypatch.setattr(app, "extract_sector_name", lambda _text, _client: "Transport")
    monkeypatch.setattr(app, "get_fast_client", lambda: object())
    monkeypatch.setattr(app, "_iter_stage1_research", lambda *_args, **_kwargs: iter(()))
    monkeypatch.setattr(app, "extract_instrument_type", lambda _text: "IPF")
    monkeypatch.setattr(app, "extract_temporal_context", lambda _text: {"processing_track": "standard"})
    monkeypatch.setattr(app, "extract_regime_context", lambda _text, _instrument: {})
    monkeypatch.setattr(app, "extract_country_classification", lambda _text: {"category": "General"})
    monkeypatch.setattr(app, "extract_context_flags", lambda _text: {})
    monkeypatch.setattr(app, "extract_sector_context", lambda _text: {"primary_sector": "Transport"})
    monkeypatch.setattr(app, "extract_change_types", lambda _text: [])
    monkeypatch.setattr(app, "extract_prior_actions", lambda _text: [])
    monkeypatch.setattr(app, "extract_dlis", lambda _text: [])
    monkeypatch.setattr(app, "extract_country_set", lambda _text: {"is_multi_country": False})
    monkeypatch.setattr(app, "extract_mpa_context", lambda _text: {"is_mpa": False})
    monkeypatch.setattr(app, "extract_lens_evidence", lambda *_args: {})
    response = app.app.test_client().post("/api/run-express", json={
        "active_lenses": [item["id"] for item in active_lenses],
        "documents": [{"name": "PAD.txt", "type": "text", "docRole": "primary", "content": "Project delivery."}],
        "document_type": "PAD", "instrument_type": "IPF", "review_mode": "design",
    })
    assert response.status_code == 200
    response.get_data()
    return next(messages for stage, messages in calls if stage == 3)[-1]["content"]


def test_step_by_step_core_prompt_gets_concise_contract_but_lens_prompt_does_not():
    base = app.DEFAULT_PROMPTS["3"]
    core_prompt = app.append_core_concise_stage3_contract(
        base, "PCN", {"processing_track": "standard"}, []
    )
    lens_prompt = app.append_core_concise_stage3_contract(
        base, "PCN", {"processing_track": "standard"}, [{"id": "climate"}]
    )

    assert '"concise_readout"' not in base
    assert '"concise_readout"' in core_prompt
    assert '"concise"' in core_prompt
    assert "same findings, ratings, priority order, and actions" in core_prompt
    assert "700-1,000 words" in core_prompt
    assert '"concise_readout"' not in lens_prompt


def test_express_core_prompt_gets_concise_contract_but_lens_prompt_does_not():
    base = app.DEFAULT_PROMPTS["3"]
    core_prompt = app.append_core_concise_stage3_contract(
        base, "PAD", {"processing_track": "standard"}, []
    )
    lens_prompt = app.append_core_concise_stage3_contract(
        base, "PAD", {"processing_track": "standard"}, [{"id": "agriculture"}]
    )

    assert '"concise_readout"' in core_prompt
    assert "Resolve before the review gate" in core_prompt
    assert '"concise_readout"' not in lens_prompt


def test_run_stage_route_assembles_concise_contract_only_for_resolved_core(monkeypatch):
    core_prompt = _capture_run_stage3_prompt(monkeypatch, [])
    lens_prompt = _capture_run_stage3_prompt(monkeypatch, [{"id": "test-lens"}])

    assert '"concise_readout"' in core_prompt
    assert '"concise_readout"' not in lens_prompt
    assert "LENS CONTRACT" in lens_prompt


def test_express_route_assembles_concise_contract_only_for_resolved_core(monkeypatch):
    core_prompt = _capture_express_stage3_prompt(monkeypatch, [])
    lens_prompt = _capture_express_stage3_prompt(monkeypatch, [{"id": "test-lens"}])

    assert '"concise_readout"' in core_prompt
    assert '"concise_readout"' not in lens_prompt
    assert "LENS CONTRACT" in lens_prompt


def test_concise_lifecycle_context_for_standard_pcn():
    text = app.build_concise_lifecycle_context(
        "PCN", {"processing_track": "standard"}
    )
    assert "Commit in the PCN" in text
    assert "Develop during preparation" in text


def test_concise_lifecycle_context_for_consolidated_pcn():
    text = app.build_concise_lifecycle_context(
        "PCN", {"processing_track": "consolidated_condensed"}
    )
    assert "Resolve by Decision Review" in text
    assert "Complete in parallel" in text


def test_concise_lifecycle_context_for_pad_does_not_defer():
    text = app.build_concise_lifecycle_context(
        "PAD", {"processing_track": "standard"}
    )
    assert "Resolve before the review gate" in text
    assert "Do not defer" in text


def test_concise_lifecycle_context_for_pid_does_not_defer():
    text = app.build_concise_lifecycle_context(
        "PID", {"processing_track": "standard"}
    )
    assert "Resolve before the review gate" in text
    assert "Do not defer" in text


def test_concise_lifecycle_context_unknown_is_conservative():
    text = app.build_concise_lifecycle_context("PCN", {})
    assert "When to address" in text
    assert "do not assert an unverified procedural gate" in text
