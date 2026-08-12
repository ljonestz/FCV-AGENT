import json
from pathlib import Path

import app


ROOT = Path(__file__).resolve().parents[1]


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
    "concise_readout": {
        "headline": "A concise headline.",
        "overview": "A concise overview.",
        "strengths": [{"title": "Strength", "text": "A strength."}],
        "priority_intro": "Priority introduction.",
    },
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


def test_both_stage3_sse_paths_return_concise_readout(monkeypatch):
    def fake_lens_context(*_args, **_kwargs):
        return _lens_context([])

    def fake_stream(_messages, _max_tokens, stage, **_kwargs):
        fake_stream._last_result = (
            "Stage 1 output." if stage == 1 else
            "Stage 2 output." if stage == 2 else _STAGE3_OUTPUT
        )
        fake_stream._last_stop_reason = "end_turn"
        yield 'data: {"chunk": "stage"}\n\n'

    monkeypatch.setattr(app, "build_lens_stage_context", fake_lens_context)
    monkeypatch.setattr(app, "_stream_stage", fake_stream)
    step_response = app.app.test_client().post("/api/run-stage", json={
        "stage": 3,
        "history": [{"role": "assistant", "content": "Stage 2 output."}],
        "document_type": "PAD", "doc_type": "PAD", "instrument_type": "IPF",
        "review_mode": "design", "temporal_context": {"processing_track": "standard"},
        "regime_context": {},
    })
    assert step_response.status_code == 200
    step_events = [json.loads(line[6:]) for line in step_response.get_data(as_text=True).splitlines()
                   if line.startswith("data: ")]
    step_done = next(event for event in step_events if event.get("done"))

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
    express_response = app.app.test_client().post("/api/run-express", json={
        "documents": [{"name": "PAD.txt", "type": "text", "docRole": "primary", "content": "Project delivery."}],
        "document_type": "PAD", "instrument_type": "IPF", "review_mode": "design",
    })
    assert express_response.status_code == 200
    express_events = [json.loads(line[6:]) for line in express_response.get_data(as_text=True).splitlines()
                      if line.startswith("data: ")]
    express_done = next(event for event in express_events if event.get("stage_done") == 3)

    expected = {"headline": "A concise headline.", "overview": "A concise overview.",
                "strengths": [{"title": "Strength", "text": "A strength."}],
                "priority_intro": "Priority introduction."}
    assert step_done["concise_readout"] == expected
    assert express_done["concise_readout"] == expected

    follow_on_response = app.app.test_client().post("/api/run-stage", json={
        "stage": 3, "user_message": "Please refine the first priority.",
        "history": [{"role": "assistant", "content": "Stage 2 output."}],
        "document_type": "PAD", "doc_type": "PAD", "instrument_type": "IPF",
        "review_mode": "design", "temporal_context": {"processing_track": "standard"},
        "regime_context": {},
    })
    follow_on_events = [json.loads(line[6:]) for line in follow_on_response.get_data(as_text=True).splitlines()
                        if line.startswith("data: ")]
    assert not [event for event in follow_on_events if "error" in event], follow_on_events
    follow_on_done = next(event for event in follow_on_events if event.get("done"))
    assert follow_on_done["concise_readout"] == expected

    monkeypatch.setattr(
        app, "build_lens_stage_context", lambda *_args, **_kwargs: _lens_context([{"id": "test-lens"}])
    )
    lens_step_response = app.app.test_client().post("/api/run-stage", json={
        "stage": 3, "active_lenses": ["test-lens"],
        "history": [{"role": "assistant", "content": "Stage 2 output."}],
        "document_type": "PAD", "doc_type": "PAD", "instrument_type": "IPF",
        "review_mode": "design", "temporal_context": {"processing_track": "standard"},
        "regime_context": {},
    })
    lens_step_events = [json.loads(line[6:]) for line in lens_step_response.get_data(as_text=True).splitlines()
                        if line.startswith("data: ")]
    lens_step_done = next(event for event in lens_step_events if event.get("done"))

    def lens_express_context(_state, stage, **_kwargs):
        return _lens_context([{"id": "test-lens"}] if stage == 3 else [])

    monkeypatch.setattr(app, "build_lens_stage_context", lens_express_context)
    lens_express_response = app.app.test_client().post("/api/run-express", json={
        "active_lenses": ["test-lens"],
        "documents": [{"name": "PAD.txt", "type": "text", "docRole": "primary", "content": "Project delivery."}],
        "document_type": "PAD", "instrument_type": "IPF", "review_mode": "design",
    })
    lens_express_events = [json.loads(line[6:]) for line in lens_express_response.get_data(as_text=True).splitlines()
                           if line.startswith("data: ")]
    lens_express_done = next(event for event in lens_express_events if event.get("stage_done") == 3)

    assert "concise_readout" not in lens_step_done
    assert "concise_readout" not in lens_express_done


def test_frontend_has_accessible_stage3_view_switch():
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'role="tablist"' in source
    assert 'id="stage3-summary-tab"' in source
    assert 'id="stage3-detailed-tab"' in source
    assert 'aria-selected="true"' in source
    assert "function setStage3View(view" in source


def test_frontend_has_concise_renderers_and_fallback():
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "function renderConciseOverview()" in source
    assert "function getConcisePriority(pr)" in source
    assert "function showConcisePriority(idx)" in source
    assert "concise_readout_unavailable" in source


def test_frontend_defaults_new_stage3_result_to_summary():
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "!isClimateLensActive() && stageConciseReadout ? 'summary' : 'detailed'" in source
    assert "setStage3View(stage3View, false)" in source


def test_frontend_scopes_concise_ui_to_normal_core_route():
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "const supportsConciseStage3 = isLast && !isClimateLensActive() && !_verifiedV2" in source
    assert "supportsConciseStage3 ? stage3ViewToggleHtml() : ''" in source
