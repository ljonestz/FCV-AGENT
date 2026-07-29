"""Route-level contracts for the dedicated Climate-FCV workflow."""

import json
import pytest


import app as app_module
from sector_lenses import CLIMATE_NATIVE_SCHEMA_VERSION


def _decode_sse(response):
    events = []
    for chunk in response.get_data(as_text=True).split("\n\n"):
        if not chunk.startswith("data: "):
            continue
        events.append(json.loads(chunk[6:]))
    return events


def _valid_research():
    return {
        "status": "complete",
        "attempts": 1,
        "sources": [
            {"id": "climate-source-1", "url": "https://openknowledge.worldbank.org/example", "title": "Example Country CCDR", "source_type": "ccdr", "publication_date": "2025"},
            {"id": "climate-source-2", "url": "https://ipcc.ch/example", "title": "Peer-reviewed flood projection", "source_type": "scientific", "publication_date": "2024"},
        ],
        "claims": [{
            "id": "climate-claim-1", "claim": "Flooding may disrupt named access roads.",
            "source_ids": ["climate-source-1", "climate-source-2"],
            "geographies": ["Project area"], "project_elements": ["Access-road rehabilitation"],
            "affected_groups": ["Residents"], "systems_or_assets": ["Access roads"],
            "evidence_status": "observed", "confidence": "medium",
            "time_horizons": ["project-lifetime"],
            "evidence_gap": "Site design flood standard not found.",
        }],
        "failure_reason": "",
    }



def _canonical_payload():
    return {
        "schema_version": CLIMATE_NATIVE_SCHEMA_VERSION,
        "fcv_baseline": {
            "sensitivity_rating": "Adequate",
            "responsiveness_rating": "Low",
            "sensitivity_reasoning": "Delivery accounts for access constraints.",
            "responsiveness_reasoning": "The design does not address root causes.",
            "evidence_trail": [{
                "claim": "Access is seasonally constrained.",
                "source_ids": ["climate-source-1"],
                "project_anchor": "Access-road rehabilitation",
            }],
        },
        "lenses": [{
            "lens_id": "climate",
            "applicability": "material",
            "materiality_level": "high",
            "materiality_summary": "Flooding and access constraints interact.",
            "executive_summary": "A climate-native project assessment.",
            "integration_level": "weakly_integrated",
            "integration_summary": "Risks are identified but not operationalized.",
            "integration_rating": "Low",
            "analysis_emphasis": [],
            "evidence": ["Named project evidence"],
            "source_ids": ["climate-source-1"],
            "less_central": "No further material anchor.",
            "sensitivity_evidence": ["Access safeguard"],
            "responsiveness_evidence": ["No root-cause response"],
            "operating_context": {
                "fcv_setting": "Access constraints affect delivery.",
                "climate_setting": "Flooding is material.",
                "intersection": "Flooding may intensify access constraints.",
            },
            "interaction_readout": [
                {
                    "direction_id": "climate-fcv-on-project",
                    "summary": "Flooding could disrupt access.",
                    "narrative": "A mediated interaction.",
                    "mechanisms": ["Road closure"],
                    "project_implications": ["Delayed works"],
                    "positive_effects": [],
                    "adverse_effects": ["Access delay"],
                    "evidence": ["Project road"],
                    "evidence_gap": "",
                    "source_ids": ["climate-source-1"],
                    "pathways": [{
                        "pathway_id": "climate-fcv-on-project-1",
                        "pressure": "Flooding",
                        "mechanism": "Road closure",
                        "project_implication": "Delayed works",
                        "design_response": "Seasonal scheduling",
                        "project_elements": ["Road works"],
                        "geographies": ["Project area"],
                        "affected_groups": ["Residents"],
                        "systems_or_assets": ["Road"],
                        "time_horizons": ["project-lifetime"],
                        "research_claim_ids": ["claim-1"],
                        "confidence": "medium",
                        "evidence_gap": "",
                    }],
                },
                {
                    "direction_id": "project-on-climate-fcv",
                    "summary": "Allocation choices could affect trust.",
                    "narrative": "A mediated interaction.",
                    "mechanisms": ["Perceived exclusion"],
                    "project_implications": ["Lower trust"],
                    "positive_effects": [],
                    "adverse_effects": ["Exclusion"],
                    "evidence": ["Targeting design"],
                    "evidence_gap": "",
                    "source_ids": ["climate-source-2"],
                    "pathways": [{
                        "pathway_id": "project-on-climate-fcv-1",
                        "pressure": "Allocation",
                        "mechanism": "Perceived exclusion",
                        "project_implication": "Lower trust",
                        "design_response": "Transparent criteria",
                        "project_elements": ["Targeting"],
                        "geographies": ["Project area"],
                        "affected_groups": ["Residents"],
                        "systems_or_assets": [],
                        "time_horizons": ["project-lifetime"],
                        "research_claim_ids": ["claim-2"],
                        "confidence": "medium",
                        "evidence_gap": "",
                    }],
                },
            ],
            "strengths_weaknesses": [{
                "side": "gap", "title": "Scheduling", "text": "Triggers are absent.",
            }],
            "reflections": [{
                "question_key": "cq1_interaction",
                "title": "Compound interaction",
                "status_cue": "Material",
                "source": "Project document",
                "text": "Flooding may intensify access constraints.",
            }],
            "supplementary_questions": [{
                "question_id": "cq5-hdp-nexus",
                "title": "Is delivery connected to local coordination?",
                "status_cue": "Unconfirmed",
                "source": "Project document",
                "text": "The coordination route is not specified.",
            }],
            "readout_sections": [{
                "section_id": "invest-in",
                "items": [{
                    "item_id": "livelihoods-opportunity",
                    "status": "potential",
                    "mechanism": "More reliable access could stabilize incomes.",
                    "project_contribution": "Road works improve seasonal access.",
                    "strengthening_action": "Track access by affected group.",
                    "evidence": ["Road component"],
                }],
            }],
            "additional_pathways": [],
            "other_pathways": [],
        }],
        "findings": [],
    }


def test_climate_blocking_failure_event_is_exact():
    assert app_module.climate_blocking_failure_event(
        "climate_research_insufficient",
        "Retry the climate research.",
        1,
    ) == {
        "error": "Retry the climate research.",
        "error_code": "climate_research_insufficient",
        "failed_stage": 1,
        "retryable": True,
        "fallback": "full_fcv",
    }


def test_design_stage2_prompt_selects_only_dedicated_climate_builder():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"], "doc_type": "PAD", "instrument": "IPF",
    })
    prompt = app_module.build_design_stage2_prompt(
        state,
        instrument_type="IPF",
        document_type="PAD",
        temporal_guardrail="Use the project lifetime.",
        regime_header="",
        project_signals="roads flood",
        climate_research=_valid_research(),
        priority_questions=[],
    )

    assert "dedicated Climate-FCV Stage 2 assessment" in prompt
    assert "%%%LENS_DIAGNOSTIC_START%%%" in prompt
    assert "%%%UNDER_HOOD_START%%%" not in prompt
    assert "%%%CATEGORY_LENS_START%%%" not in prompt
    assert "RECS_TABLE_START" not in prompt


def test_design_stage2_prompt_returns_empty_for_non_climate():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": [], "doc_type": "PAD", "instrument": "IPF",
    })
    assert app_module.build_design_stage2_prompt(
        state,
        instrument_type="IPF",
        document_type="PAD",
        temporal_guardrail="",
        regime_header="",
        project_signals="",
        climate_research={},
        priority_questions=[],
    ) == ""


def test_canonical_climate_renderer_and_ratings_use_payload_only():
    payload = _canonical_payload()

    rendered = app_module.render_climate_stage2_payload(payload)
    ratings = app_module.climate_stage2_ratings(payload)

    assert "A climate-native project assessment." in rendered
    assert "Flooding and access constraints interact." in rendered
    assert "Scheduling" in rendered
    assert "Triggers are absent." in rendered
    assert "Is delivery connected to local coordination?" in rendered
    assert "Livelihoods and economic opportunity" in rendered
    assert "Track access by affected group." in rendered
    assert "%%%LENS_DIAGNOSTIC" not in rendered
    assert ratings == {
        "sensitivity_rating": "Adequate",
        "responsiveness_rating": "Low",
        "rating_reasoning": (
            "Sensitivity: Delivery accounts for access constraints. "
            "Responsiveness: The design does not address root causes."
        ),
    }


def _failed_research():
    return {
        "status": "failed",
        "attempts": 1,
        "sources": [],
        "claims": [],
        "failure_reason": "Research service unavailable.",
    }


def _research_result(bundle):
    yield {
        "result": {
            "core_brief": "Compact FCV research.",
            "climate_research": bundle,
            "lens_context_sources": [],
        }
    }


@pytest.mark.parametrize("endpoint", ["/api/run-stage", "/api/run-express"])
def test_climate_research_failure_blocks_both_workflows_before_model(
    monkeypatch, endpoint,
):
    model_calls = []

    def forbidden_stream(*args, **kwargs):
        model_calls.append((args, kwargs))
        raise AssertionError("Stage model must not run after climate research failure")
        yield  # pragma: no cover

    monkeypatch.setattr(
        app_module, "extract_country_name", lambda text, client: "Exampleland"
    )
    monkeypatch.setattr(
        app_module, "extract_sector_name", lambda text, client: "Transport"
    )
    monkeypatch.setattr(app_module, "get_fast_client", lambda: object())
    monkeypatch.setattr(
        app_module,
        "_iter_stage1_research",
        lambda *args, **kwargs: _research_result(_failed_research()),
    )
    monkeypatch.setattr(app_module, "_stream_stage", forbidden_stream)
    payload = {
        "active_lenses": ["climate"],
        "documents": [{
            "name": "Project Appraisal Document.txt",
            "type": "text",
            "docRole": "primary",
            "content": "Named project road and access activities. " * 10,
        }],
        "document_type": "PAD",
        "instrument_type": "IPF",
        "review_mode": "design",
    }
    if endpoint == "/api/run-stage":
        payload["stage"] = 1

    response = app_module.app.test_client().post(endpoint, json=payload)
    events = _decode_sse(response)

    decision = app_module.climate_research_evidence_gate(_failed_research())
    assert app_module.climate_blocking_failure_event(
        decision["code"], decision["message"], 1
    ) in events
    assert model_calls == []
    assert not any(event.get("status") == "preparing_analysis" for event in events)
    assert not any(event.get("stage_done") or event.get("done") for event in events)



def test_standard_climate_stage2_uses_native_prompt_and_canonical_output(
    monkeypatch,
):
    payload = _canonical_payload()
    raw_model_output = (
        "%%%LENS_DIAGNOSTIC_START%%%"
        + json.dumps(payload)
        + "%%%LENS_DIAGNOSTIC_END%%%"
    )
    calls = []

    def fake_stream(messages, max_tokens, stage, **kwargs):
        calls.append({
            "messages": messages,
            "max_tokens": max_tokens,
            "stage": stage,
        })
        fake_stream._last_result = raw_model_output
        fake_stream._last_stop_reason = "end_turn"
        yield "data: {\"chunk\": \"model\"}\n\n"

    def forbidden_generic_parser(*args, **kwargs):
        raise AssertionError("generic Stage 2 parser must not run for Climate-FCV")

    monkeypatch.setattr(app_module, "_stream_stage", fake_stream)
    monkeypatch.setattr(app_module, "extract_stage2_ratings", forbidden_generic_parser)
    monkeypatch.setattr(app_module, "extract_under_hood", forbidden_generic_parser)
    monkeypatch.setattr(app_module, "extract_category_lens", forbidden_generic_parser)
    monkeypatch.setattr(
        app_module,
        "extract_or_repair_lens_diagnostic",
        lambda *args, **kwargs: (payload, False, ""),
    )
    request_payload = {
        "stage": 2,
        "active_lenses": ["climate"],
        "history": [{
            "role": "assistant",
            "content": "Stage 1 named the road component and seasonal access risk.",
        }],
        "document_type": "PAD",
        "instrument_type": "IPF",
        "temporal_context": {},
        "regime_context": {},
        "sector_context": {"primary_sector": "Transport"},
        "climate_research": _valid_research(),
        "lens_context_sources": [],
        "review_mode": "design",
        "user_message": "Focus the climate assessment on seasonal access.",
    }

    response = app_module.app.test_client().post(
        "/api/run-stage", json=request_payload
    )
    events = _decode_sse(response)
    done = next(event for event in events if event.get("done"))

    assert len(calls) == 1
    assert calls[0]["stage"] == 2
    assert calls[0]["max_tokens"] == 16000
    assembled = calls[0]["messages"][-1]["content"]
    assert "dedicated Climate-FCV Stage 2 assessment" in assembled
    assert assembled.count("%%%LENS_DIAGNOSTIC_START%%%") == 1
    for marker in (
        "%%%UNDER_HOOD_START%%%",
        "%%%RECS_TABLE_START%%%",
        "%%%DNH_CHECKLIST_START%%%",
        "%%%QUESTIONS_MAP_START%%%",
        "%%%CATEGORY_LENS_START%%%",
        "--- ACTIVE SECTOR LENSES ---",
        "--- WBG FCV Operational Manual",
    ):
        assert marker not in assembled
    rendered = app_module.render_climate_stage2_payload(payload)
    assert done["result"] == rendered
    assert done["display_text"] == rendered
    assert done["sensitivity_rating"] == "Adequate"
    assert done["responsiveness_rating"] == "Low"
    assert done["rating_reasoning"].startswith("Sensitivity: Delivery")
    assert done["under_hood"] == {}
    assert done["category_lens"] == {}
    assert done["parse_error"] is False



def test_express_climate_stage2_uses_native_prompt_and_canonical_output(monkeypatch):
    payload = _canonical_payload()
    raw_model_output = "%%%LENS_DIAGNOSTIC_START%%%" + json.dumps(payload) + "%%%LENS_DIAGNOSTIC_END%%%"
    calls = []

    def fake_stream(messages, max_tokens, stage, **kwargs):
        calls.append({"messages": messages, "max_tokens": max_tokens, "stage": stage})
        fake_stream._last_stop_reason = "end_turn"
        if stage == 1:
            fake_stream._last_result = "Stage 1 project extraction."
            yield "data: {\"chunk\": \"stage1\"}\n\n"
            return
        if stage == 2:
            fake_stream._last_result = raw_model_output
            yield "data: {\"chunk\": \"stage2\"}\n\n"
            return
        raise RuntimeError("stop after verified Stage 2")
        yield

    def forbidden_generic_parser(*args, **kwargs):
        raise AssertionError("generic Stage 2 parser must not run for Climate-FCV")

    monkeypatch.setattr(app_module, "extract_country_name", lambda text, client: "Exampleland")
    monkeypatch.setattr(app_module, "extract_sector_name", lambda text, client: "Transport")
    monkeypatch.setattr(app_module, "get_fast_client", lambda: object())
    monkeypatch.setattr(app_module, "_iter_stage1_research", lambda *args, **kwargs: _research_result(_valid_research()))
    monkeypatch.setattr(app_module, "_stream_stage", fake_stream)
    monkeypatch.setattr(app_module, "extract_instrument_type", lambda text: "IPF")
    monkeypatch.setattr(app_module, "extract_temporal_context", lambda text: {})
    monkeypatch.setattr(app_module, "extract_regime_context", lambda text, instrument: {})
    monkeypatch.setattr(app_module, "extract_country_classification", lambda text: {"category": "General"})
    monkeypatch.setattr(app_module, "extract_context_flags", lambda text: {})
    monkeypatch.setattr(app_module, "extract_sector_context", lambda text: {"primary_sector": "Transport"})
    monkeypatch.setattr(app_module, "extract_change_types", lambda text: [])
    monkeypatch.setattr(app_module, "extract_prior_actions", lambda text: [])
    monkeypatch.setattr(app_module, "extract_dlis", lambda text: [])
    monkeypatch.setattr(app_module, "extract_country_set", lambda text: {"is_multi_country": False})
    monkeypatch.setattr(app_module, "extract_mpa_context", lambda text: {"is_mpa": False})
    monkeypatch.setattr(app_module, "extract_lens_evidence", lambda *args: {})
    monkeypatch.setattr(app_module, "extract_stage2_ratings", forbidden_generic_parser)
    monkeypatch.setattr(app_module, "extract_under_hood", forbidden_generic_parser)
    monkeypatch.setattr(app_module, "extract_category_lens", forbidden_generic_parser)
    monkeypatch.setattr(app_module, "extract_or_repair_lens_diagnostic", lambda *args, **kwargs: (payload, False, ""))
    response = app_module.app.test_client().post("/api/run-express", json={
        "active_lenses": ["climate"],
        "documents": [{"name": "Project Appraisal Document.txt", "type": "text", "docRole": "primary", "content": "Named project road and access activities. " * 10}],
        "document_type": "PAD", "instrument_type": "IPF", "review_mode": "design",
    })
    events = _decode_sse(response)
    done = next(event for event in events if event.get("stage_done") == 2)
    stage2_call = next(call for call in calls if call["stage"] == 2)
    assert stage2_call["max_tokens"] == 16000
    assembled = stage2_call["messages"][-1]["content"]
    assert "dedicated Climate-FCV Stage 2 assessment" in assembled
    assert assembled.count("%%%LENS_DIAGNOSTIC_START%%%") == 1
    for marker in ("%%%UNDER_HOOD_START%%%", "%%%RECS_TABLE_START%%%", "%%%DNH_CHECKLIST_START%%%", "%%%QUESTIONS_MAP_START%%%", "%%%CATEGORY_LENS_START%%%", "--- ACTIVE SECTOR LENSES ---", "--- WBG FCV Operational Manual"):
        assert marker not in assembled
    rendered = app_module.render_climate_stage2_payload(payload)
    assert done["result"] == rendered
    assert done["display_text"] == rendered
    assert done["sensitivity_rating"] == "Adequate"
    assert done["responsiveness_rating"] == "Low"
    assert done["under_hood"] == {}
    assert done["category_lens"] == {}
    assert done["parse_error"] is False



def test_standard_non_climate_stage2_retains_generic_contract(monkeypatch):
    calls = []

    def fake_stream(messages, max_tokens, stage, **kwargs):
        calls.append({"messages": messages, "max_tokens": max_tokens, "stage": stage})
        fake_stream._last_result = "Generic FCV Stage 2 output."
        fake_stream._last_stop_reason = "end_turn"
        yield "data: {\"chunk\": \"generic\"}\n\n"

    monkeypatch.setattr(app_module, "_stream_stage", fake_stream)
    monkeypatch.setattr(app_module, "extract_stage2_ratings", lambda text: {
        "sensitivity_rating": "Adequate",
        "responsiveness_rating": "Low",
        "rating_reasoning": "Generic reasoning.",
    })
    monkeypatch.setattr(app_module, "extract_under_hood", lambda text: {
        "display_text": text,
        "recs_table": "table",
        "dnh_checklist": "checklist",
        "questions_map": "questions",
        "evidence_trail": "evidence",
    })
    monkeypatch.setattr(app_module, "extract_category_lens", lambda text: {
        "classification": "General",
    })
    monkeypatch.setattr(
        app_module,
        "extract_or_repair_lens_diagnostic",
        lambda *args, **kwargs: ({}, False, ""),
    )
    response = app_module.app.test_client().post("/api/run-stage", json={
        "stage": 2,
        "active_lenses": [],
        "history": [{"role": "assistant", "content": "Stage 1 output."}],
        "document_type": "PAD",
        "instrument_type": "IPF",
        "review_mode": "design",
    })
    events = _decode_sse(response)
    done = next(event for event in events if event.get("done"))
    assembled = calls[0]["messages"][-1]["content"]

    assert "%%%UNDER_HOOD_START%%%" in assembled
    assert "%%%CATEGORY_LENS_START%%%" in assembled
    assert "--- WBG FCV Operational Manual" in assembled
    assert done["under_hood"]["questions_map"] == "questions"
    assert done["category_lens"]["classification"] == "General"



def test_express_non_climate_stage2_retains_generic_contract(monkeypatch):
    calls = []

    def fake_stream(messages, max_tokens, stage, **kwargs):
        calls.append({"messages": messages, "max_tokens": max_tokens, "stage": stage})
        fake_stream._last_stop_reason = "end_turn"
        if stage == 1:
            fake_stream._last_result = "Stage 1 project extraction."
            yield "data: {\"chunk\": \"stage1\"}\n\n"
            return
        if stage == 2:
            fake_stream._last_result = "Generic FCV Stage 2 output."
            yield "data: {\"chunk\": \"stage2\"}\n\n"
            return
        raise RuntimeError("stop after verified Stage 2")
        yield

    monkeypatch.setattr(app_module, "extract_country_name", lambda text, client: "Exampleland")
    monkeypatch.setattr(app_module, "extract_sector_name", lambda text, client: "Transport")
    monkeypatch.setattr(app_module, "get_fast_client", lambda: object())
    monkeypatch.setattr(app_module, "_iter_stage1_research", lambda *args, **kwargs: _research_result(_valid_research()))
    monkeypatch.setattr(app_module, "_stream_stage", fake_stream)
    monkeypatch.setattr(app_module, "extract_instrument_type", lambda text: "IPF")
    monkeypatch.setattr(app_module, "extract_temporal_context", lambda text: {})
    monkeypatch.setattr(app_module, "extract_regime_context", lambda text, instrument: {})
    monkeypatch.setattr(app_module, "extract_country_classification", lambda text: {"category": "General"})
    monkeypatch.setattr(app_module, "extract_context_flags", lambda text: {})
    monkeypatch.setattr(app_module, "extract_sector_context", lambda text: {"primary_sector": "Transport"})
    monkeypatch.setattr(app_module, "extract_change_types", lambda text: [])
    monkeypatch.setattr(app_module, "extract_prior_actions", lambda text: [])
    monkeypatch.setattr(app_module, "extract_dlis", lambda text: [])
    monkeypatch.setattr(app_module, "extract_country_set", lambda text: {"is_multi_country": False})
    monkeypatch.setattr(app_module, "extract_mpa_context", lambda text: {"is_mpa": False})
    monkeypatch.setattr(app_module, "extract_lens_evidence", lambda *args: {})
    monkeypatch.setattr(app_module, "extract_stage2_ratings", lambda text: {
        "sensitivity_rating": "Adequate", "responsiveness_rating": "Low",
        "rating_reasoning": "Generic reasoning.",
    })
    monkeypatch.setattr(app_module, "extract_under_hood", lambda text: {
        "display_text": text, "recs_table": "table", "dnh_checklist": "checklist",
        "questions_map": "questions", "evidence_trail": "evidence",
    })
    monkeypatch.setattr(app_module, "extract_category_lens", lambda text: {"classification": "General"})
    monkeypatch.setattr(app_module, "extract_or_repair_lens_diagnostic", lambda *args, **kwargs: ({}, False, ""))
    response = app_module.app.test_client().post("/api/run-express", json={
        "active_lenses": [],
        "documents": [{"name": "Project Appraisal Document.txt", "type": "text", "docRole": "primary", "content": "Named project road activities. " * 10}],
        "document_type": "PAD", "instrument_type": "IPF", "review_mode": "design",
    })
    events = _decode_sse(response)
    done = next(event for event in events if event.get("stage_done") == 2)
    stage2_call = next(call for call in calls if call["stage"] == 2)
    assembled = stage2_call["messages"][-1]["content"]

    assert "%%%UNDER_HOOD_START%%%" in assembled
    assert "%%%CATEGORY_LENS_START%%%" in assembled
    assert "--- WBG FCV Operational Manual" in assembled
    assert done["under_hood"]["questions_map"] == "questions"
    assert done["category_lens"]["classification"] == "General"
