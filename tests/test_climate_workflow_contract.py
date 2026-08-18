"""Route-level contracts for the dedicated Climate-FCV workflow."""

import json
import time
from types import SimpleNamespace

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


def _research_result(bundle, manifest=None):
    yield {
        "result": {
            "core_brief": "Compact FCV research.",
            "climate_research": bundle,
            "lens_context_sources": [],
            "climate_grounding": manifest or {
                "bank_status": "unavailable",
                "warning_code": "bank_unavailable",
            },
        }
    }


@pytest.mark.parametrize("endpoint", ["/api/run-stage", "/api/run-express"])
def test_climate_research_failure_continues_with_bank(
    monkeypatch, endpoint, caplog,
):
    # Exercise the retained legacy Climate path; exact Climate-only Express uses v2.
    monkeypatch.setattr(app_module, "_is_verified_climate_express", lambda *_args: False)
    caplog.set_level("INFO")
    manifest = {
        "bank_status": "ok",
        "warning_code": "",
        "schema_version": "1.0.0",
        "content_version": "test-1",
        "country_iso3": "SSD",
        "evidence_ids": ["SSD-E-001"],
        "pathway_ids": ["SSD-P-001"],
    }
    packet = {
        "bank_status": "ok",
        "warning_code": "",
        "content_version": "test-1",
        "country_iso3": "SSD",
        "sources": [{
            "source_id": "SSD-SRC-001",
            "title": "Reviewed source",
            "url": "https://www.sipri.org/example",
        }],
        "evidence_records": [{
            "evidence_id": "SSD-E-001",
            "compact_statement": "Reviewed evidence.",
        }],
        "pathways": [{
            "pathway_id": "SSD-P-001",
            "compact_statement": "Reviewed pathway.",
        }],
    }
    merged = {
        "state": "bank-only",
        "warning_code": "climate_research_failed",
        "research_status": "failed",
        "bank_manifest": manifest,
        "sources": packet["sources"],
        "bank_character_count": 18,
        "selected_item_count": 2,
        "content_version": "test-1",
        "country_iso3": "SSD",
        "bank_evidence_records": [{"secret": "BANK PROSE"}],
        "live_claims": [{"secret": "LIVE CLAIM"}],
        "prompt_context": "SECRET INTERNAL PROMPT",
    }
    model_calls = []

    def stop_after_model_entry(messages, max_tokens, stage, **kwargs):
        model_calls.append(stage)
        if endpoint == "/api/run-stage":
            app_module._stream_stage._last_result = "Stage 1 output."
            return
        raise RuntimeError("intentional test stop after model entry")
        yield  # pragma: no cover

    monkeypatch.setattr(
        app_module, "extract_country_name", lambda text, client: "South Sudan"
    )
    monkeypatch.setattr(
        app_module, "extract_sector_name", lambda text, client: "Fisheries"
    )
    monkeypatch.setattr(app_module, "get_fast_client", lambda: object())
    monkeypatch.setattr(
        app_module,
        "_iter_stage1_research",
        lambda *args, **kwargs: _research_result(
            _failed_research(), manifest
        ),
    )
    monkeypatch.setattr(
        app_module, "load_climate_bank", lambda: object()
    )
    monkeypatch.setattr(
        app_module, "materialize_bank_manifest",
        lambda *args, **kwargs: packet,
    )
    monkeypatch.setattr(
        app_module, "merge_climate_grounding",
        lambda *args, **kwargs: dict(merged),
    )
    monkeypatch.setattr(app_module, "_stream_stage", stop_after_model_entry)
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

    assert any(event.get("status") == "preparing_analysis" for event in events)
    assert model_calls == [1]
    if endpoint == "/api/run-stage":
        assert not any(event.get("error") for event in events)
        assert any(event.get("done") and event.get("stage") == 1 for event in events)
    assert not any(
        event.get("error_code", "").startswith("climate_research")
        for event in events
    )
    outbound_grounding = [
        event["climate_grounding"]
        for event in events
        if isinstance(event.get("climate_grounding"), dict)
    ]
    if endpoint == "/api/run-stage" and not outbound_grounding:
        outbound_grounding = [app_module.climate_grounding_envelope(merged)]
    assert outbound_grounding
    assert all(
        "bank_evidence_records" not in item
        and "live_claims" not in item
        and "prompt_context" not in item
        for item in outbound_grounding
    )
    assert "grounding_state=bank-only" in caplog.text
    if endpoint == "/api/run-express":
        assert "active_lenses=climate" in caplog.text



def test_rejected_bank_manifest_is_not_reattached(monkeypatch):
    invalid_manifest = {
        "bank_status": "ok",
        "warning_code": "",
        "schema_version": "1.0.0",
        "content_version": "wrong-version",
        "country_iso3": "SSD",
        "evidence_ids": ["SSD-E-999"],
        "pathway_ids": [],
    }
    monkeypatch.setattr(app_module, "load_climate_bank", lambda: object())
    monkeypatch.setattr(
        app_module,
        "materialize_bank_manifest",
        lambda *args, **kwargs: {
            "bank_status": "unavailable",
            "warning_code": "bank_manifest_invalid",
        },
    )

    grounding, _ = app_module.resolve_climate_grounding(
        invalid_manifest,
        _failed_research(),
        assessment_id="invalid-manifest",
    )

    assert grounding["bank_manifest"] == {
        "bank_status": "unavailable",
        "warning_code": "bank_manifest_invalid",
    }
    assert "evidence_ids" not in grounding["bank_manifest"]


@pytest.mark.parametrize(
    ("bank_available", "research_available", "expected_state"),
    [
        (True, True, "bank+research"),
        (True, False, "bank-only"),
        (False, True, "research-only"),
        (False, False, "thematic-only"),
    ],
)
def test_grounding_resolver_has_all_four_real_states(
    monkeypatch,
    bank_available,
    research_available,
    expected_state,
):
    manifest = {
        "bank_status": "ok",
        "warning_code": "",
        "schema_version": "1.0.0",
        "content_version": "test-1",
        "country_iso3": "SSD",
        "evidence_ids": ["SSD-E-001"],
        "pathway_ids": [],
    }
    packet = {
        "bank_status": "ok",
        "warning_code": "",
        "content_version": "test-1",
        "country_iso3": "SSD",
        "sources": [{
            "source_id": "SSD-SRC-001",
            "title": "Reviewed source",
            "url": "https://sipri.org/example",
        }],
        "evidence_records": [{
            "evidence_id": "SSD-E-001",
            "compact_statement": "Reviewed evidence.",
            "source_refs": [{"source_id": "SSD-SRC-001"}],
        }],
        "pathways": [],
    }
    unavailable = {
        "bank_status": "unavailable",
        "warning_code": "bank_unavailable",
    }
    monkeypatch.setattr(app_module, "load_climate_bank", lambda: object())
    monkeypatch.setattr(
        app_module,
        "materialize_bank_manifest",
        lambda *args, **kwargs: packet if bank_available else unavailable,
    )
    research = _valid_research() if research_available else _failed_research()

    grounding, accepted_research = app_module.resolve_climate_grounding(
        manifest,
        research,
        assessment_id=f"state-{expected_state}",
    )

    assert grounding["state"] == expected_state
    assert bool(accepted_research["claims"]) is research_available
    envelope = app_module.climate_grounding_envelope(grounding)
    assert "prompt_context" not in envelope
    assert "bank_evidence_records" not in envelope


def test_only_server_validated_bank_source_ids_enter_native_context():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"],
    })
    diagnostic = _canonical_payload()
    diagnostic["lenses"][0]["source_ids"] = ["SSD-SRC-001"]

    validated = app_module.build_lens_stage_context(
        state,
        3,
        lens_diagnostic=diagnostic,
        climate_grounding={
            "_validated_bank_source_ids": ["SSD-SRC-001"],
        },
        compose_prompt=False,
    )
    untrusted = app_module.build_lens_stage_context(
        state,
        3,
        lens_diagnostic=diagnostic,
        climate_grounding={
            "bank_sources": [{"source_id": "SSD-SRC-001"}],
            "sources": [{"source_id": "SSD-SRC-001"}],
        },
        compose_prompt=False,
    )

    assert "SSD-SRC-001" in (
        validated["lens_diagnostic"]["lenses"][0]["source_ids"]
    )
    assert "SSD-SRC-001" not in (
        untrusted["lens_diagnostic"]["lenses"][0]["source_ids"]
    )


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

    lens_context_calls = []
    real_build_lens_stage_context = app_module.build_lens_stage_context

    def track_lens_context(*args, **kwargs):
        lens_context_calls.append({
            "stage": args[1] if len(args) > 1 else kwargs.get("stage"),
            "compose_prompt": kwargs.get("compose_prompt"),
        })
        return real_build_lens_stage_context(*args, **kwargs)

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

    monkeypatch.setattr(
        app_module, "build_lens_stage_context", track_lens_context
    )
    monkeypatch.setattr(app_module, "_stream_stage", fake_stream)
    monkeypatch.setattr(app_module, "extract_stage2_ratings", forbidden_generic_parser)
    monkeypatch.setattr(app_module, "extract_under_hood", forbidden_generic_parser)
    monkeypatch.setattr(app_module, "extract_category_lens", forbidden_generic_parser)
    def fake_native_diagnostic(**_kwargs):
        yield {"recovery_status": "repairing", "missing_fields": ["lenses.climate.integration_summary"]}
        yield {"keepalive": True, "recovery_status": "repairing"}
        yield {"result": payload, "recovered": True, "error_code": ""}

    monkeypatch.setattr(
        app_module,
        "_iter_native_climate_stage2_diagnostic",
        fake_native_diagnostic,
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

    assert any(event.get("recovery_status") == "repairing" for event in events)
    assert any(event.get("keepalive") is True for event in events)
    assert done["lens_diagnostic_recovered"] is True
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
    assert {"stage": 2, "compose_prompt": False} in lens_context_calls


def test_express_climate_stage2_uses_native_prompt_and_canonical_output(monkeypatch):
    # Exercise the retained legacy Climate path; exact Climate-only Express uses v2.
    monkeypatch.setattr(app_module, "_is_verified_climate_express", lambda *_args: False)
    payload = _canonical_payload()
    raw_model_output = "%%%LENS_DIAGNOSTIC_START%%%" + json.dumps(payload) + "%%%LENS_DIAGNOSTIC_END%%%"
    calls = []

    lens_context_calls = []
    real_build_lens_stage_context = app_module.build_lens_stage_context

    def track_lens_context(*args, **kwargs):
        lens_context_calls.append({
            "stage": args[1] if len(args) > 1 else kwargs.get("stage"),
            "compose_prompt": kwargs.get("compose_prompt"),
        })
        return real_build_lens_stage_context(*args, **kwargs)

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

    monkeypatch.setattr(
        app_module, "build_lens_stage_context", track_lens_context
    )
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
    def fake_native_diagnostic(**_kwargs):
        yield {"recovery_status": "repairing", "missing_fields": ["lenses.climate.integration_summary"]}
        yield {"keepalive": True, "recovery_status": "repairing"}
        yield {"result": payload, "recovered": True, "error_code": ""}

    monkeypatch.setattr(
        app_module,
        "_iter_native_climate_stage2_diagnostic",
        fake_native_diagnostic,
    )
    response = app_module.app.test_client().post("/api/run-express", json={
        "active_lenses": ["climate"],
        "documents": [{"name": "Project Appraisal Document.txt", "type": "text", "docRole": "primary", "content": "Named project road and access activities. " * 10}],
        "document_type": "PAD", "instrument_type": "IPF", "review_mode": "design",
    })
    events = _decode_sse(response)
    done = next(event for event in events if event.get("stage_done") == 2)
    stage2_call = next(call for call in calls if call["stage"] == 2)
    assert any(event.get("recovery_status") == "repairing" for event in events)
    assert any(event.get("keepalive") is True for event in events)
    assert done["lens_diagnostic_recovered"] is True
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
    assert {"stage": 2, "compose_prompt": False} in lens_context_calls


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



class SlowRecoveryClient:
    def __init__(self, delay_seconds: float):
        self.delay_seconds = delay_seconds
        self.messages = self

    def create(self, **_kwargs):
        time.sleep(self.delay_seconds)
        content = (
            "%%%LENS_DIAGNOSTIC_START%%%"
            + json.dumps(_canonical_payload())
            + "%%%LENS_DIAGNOSTIC_END%%%"
        )
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=content)]
        )


def test_recovery_emits_keepalive_before_slow_result():
    events = list(app_module._iter_climate_diagnostic_recovery(
        primary={"schema_version": "climate-native-v1", "lenses": []},
        missing_fields=["lenses.climate"],
        active_lens_ids=["climate"],
        source_ids_by_lens={"climate": set()},
        readout_schema_by_lens={"climate": {}},
        assessment_id="assessment-recovery",
        client=SlowRecoveryClient(delay_seconds=0.05),
        max_seconds=1,
        keepalive_interval=0.01,
    ))

    assert any(event.get("recovery_status") == "repairing" for event in events)
    assert any(event.get("keepalive") is True for event in events)
    assert "result" in events[-1]



@pytest.mark.parametrize("endpoint", ["/api/run-stage", "/api/run-express"])
def test_climate_recovery_failure_blocks_both_workflows(monkeypatch, endpoint):
    # Exercise the retained legacy Climate path; exact Climate-only Express uses v2.
    monkeypatch.setattr(app_module, "_is_verified_climate_express", lambda *_args: False)
    model_stages = []

    def fake_stream(messages, max_tokens, stage, **kwargs):
        model_stages.append(stage)
        fake_stream._last_stop_reason = "end_turn"
        if stage == 1:
            fake_stream._last_result = "Stage 1 project extraction."
            yield 'data: {"chunk": "stage1"}\n\n'
            return
        if stage == 2:
            fake_stream._last_result = "%%%LENS_DIAGNOSTIC_START%%%" + json.dumps(_canonical_payload()) + "%%%LENS_DIAGNOSTIC_END%%%"
            yield 'data: {"chunk": "stage2"}\n\n'
            return
        raise AssertionError("Stage 3 must not run after Climate recovery failure")

    def failed_recovery(**_kwargs):
        yield {"recovery_status": "repairing", "missing_fields": ["lenses.climate.integration_summary"]}
        yield {"keepalive": True, "recovery_status": "repairing"}
        yield {"result": {"error": True, "message": "Climate diagnostic repair timed out.", "lenses": [], "findings": []}, "recovered": False, "error_code": "climate_recovery_timeout"}

    monkeypatch.setattr(app_module, "_stream_stage", fake_stream)
    monkeypatch.setattr(app_module, "_iter_native_climate_stage2_diagnostic", failed_recovery)
    monkeypatch.setattr(app_module, "extract_country_name", lambda text, client: "Exampleland")
    monkeypatch.setattr(app_module, "extract_sector_name", lambda text, client: "Transport")
    monkeypatch.setattr(app_module, "get_fast_client", lambda: object())
    monkeypatch.setattr(app_module, "_iter_stage1_research", lambda *a, **k: _research_result(_valid_research()))
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

    request_payload = {"active_lenses": ["climate"], "document_type": "PAD", "instrument_type": "IPF", "review_mode": "design"}
    if endpoint == "/api/run-stage":
        request_payload.update({"stage": 2, "history": [{"role": "assistant", "content": "Stage 1 output."}], "climate_research": _valid_research(), "lens_context_sources": []})
    else:
        request_payload["documents"] = [{"name": "Project Appraisal Document.txt", "type": "text", "docRole": "primary", "content": "Named project road and access activities. " * 10}]

    events = _decode_sse(app_module.app.test_client().post(endpoint, json=request_payload))
    assert any(event.get("recovery_status") == "repairing" for event in events)
    assert any(event.get("keepalive") is True for event in events)
    failure = next(event for event in events if event.get("error_code") == "climate_recovery_timeout")
    assert failure["failed_stage"] == 2
    assert failure["retryable"] is True
    assert failure["fallback"] == "full_fcv"
    assert not any(event.get("done") and event.get("stage") == 2 for event in events)
    assert not any(event.get("stage_done") == 2 for event in events)
    assert 3 not in model_stages



def test_recovery_iterator_times_out_without_exposing_partial_result():
    events = list(app_module._iter_climate_diagnostic_recovery(
        primary={"schema_version": "climate-native-v1", "lenses": []},
        missing_fields=["lenses.climate"],
        active_lens_ids=["climate"],
        source_ids_by_lens={"climate": set()},
        readout_schema_by_lens={"climate": {}},
        assessment_id="assessment-timeout",
        client=SlowRecoveryClient(delay_seconds=0.05),
        max_seconds=0.01,
        keepalive_interval=0.002,
    ))

    assert events[-1]["error_code"] == "climate_recovery_timeout"
    assert events[-1]["recovered"] is False
    assert events[-1]["result"]["error"] is True
    assert not any(
        event.get("result", {}).get("fcv_baseline")
        for event in events
        if isinstance(event.get("result"), dict)
    )



def test_recovery_does_not_synthesize_requested_materiality():
    primary = json.loads(json.dumps(_canonical_payload()))
    primary["lenses"][0]["materiality_level"] = ""
    repair = json.loads(json.dumps(_canonical_payload()))
    repair["lenses"][0]["materiality_level"] = ""

    class BlankMaterialityClient:
        def __init__(self):
            self.messages = self

        def create(self, **_kwargs):
            content = (
                "%%%LENS_DIAGNOSTIC_START%%%"
                + json.dumps(repair)
                + "%%%LENS_DIAGNOSTIC_END%%%"
            )
            return SimpleNamespace(
                content=[SimpleNamespace(type="text", text=content)]
            )

    events = list(app_module._iter_climate_diagnostic_recovery(
        primary=primary,
        missing_fields=["lenses.climate.materiality_level"],
        active_lens_ids=["climate"],
        source_ids_by_lens={"climate": set()},
        readout_schema_by_lens={"climate": {}},
        assessment_id="assessment-missing-materiality",
        client=BlankMaterialityClient(),
        max_seconds=1,
        keepalive_interval=0.01,
    ))

    assert events[-1]["recovered"] is False
    assert events[-1]["error_code"] == "climate_diagnostic_invalid"



def test_climate_stage3_route_uses_priority_prompt_only(monkeypatch):
    captured = {}

    def capture_prompt(**kwargs):
        captured.update(kwargs)
        return "CLIMATE PRIORITIES ONLY"

    monkeypatch.setattr(app_module, "build_climate_stage3_prompt", capture_prompt)
    diagnostic = {
        "schema_version": "climate-native-v1",
        "fcv_baseline": {
            "sensitivity_rating": "Adequate",
            "responsiveness_rating": "Low",
        },
        "lenses": [{"lens_id": "climate", "integration_summary": "Flood access rules are incomplete."}],
    }
    prompt = app_module.build_design_stage3_prompt(
        state=app_module.AnalysisState.from_payload({"active_lenses": ["climate"]}),
        instrument_type="IPF",
        document_type="Project Paper",
        diagnostic=diagnostic,
        regime_header="ESF.",
    )

    assert prompt == "CLIMATE PRIORITIES ONLY"
    assert captured["diagnostic"] is diagnostic
    assert captured["instrument_type"] == "IPF"


def test_non_climate_stage3_route_keeps_generic_selection(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "build_climate_stage3_prompt",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("climate builder must not run")
        ),
    )
    assert app_module.build_design_stage3_prompt(
        state=app_module.AnalysisState.from_payload({"active_lenses": []}),
        instrument_type="IPF",
        document_type="PAD",
        diagnostic={},
        regime_header="",
    ) == ""



def _climate_priority_output(pathway_id="climate-fcv-on-project-1"):
    payload = {
        "fcv_rating": "Adequate", "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "Delivery accounts for access constraints.",
        "responsiveness_summary": "Root causes are not addressed.",
        "risk_exposure": {"risks_to": "Flood access", "risks_from": "Exclusion"},
        "mid_cycle_watch": [], "dpf_watch": [], "p4r_watch": [], "regional_watch": [],
        "priorities": [{
            "title": "Sequence road works around Project area flooding",
            "fcv_dimension": "Climate-FCV interaction", "tag": "[S+R]",
            "refresh_shift": "Shift A: Anticipate", "risk_level": "High",
            "the_gap": "Seasonal access rules are absent for Project area road works.",
            "why_it_matters": "Flood closure could delay access for residents.",
            "actions": [{"document_element": "POM work plan", "guidance": "Add seasonal sequencing for Project area road works.", "suggested_language": "Sequence works around named flood triggers."}],
            "who_acts": "TTL and PIU", "when": "Before works", "action_timing": "required-before-appraisal",
            "resources": "Existing supervision", "pad_sections": "Implementation arrangements",
            "country_category_relevance": "", "implementation_note": "Track access.",
            "cpf_alignment": None, "rra_driver_alignment": None, "change_type": "",
            "restructuring_level": "", "priority_scope": "", "governance_level": None,
            "policy_status": "advisory", "specialist_referral": None,
            "authority_basis": "reviewer_judgment", "lens_ids": ["climate"],
            "lens_relevance": "Flood access interaction.",
            "climate_links": {"status": "linked", "interaction_pathway_ids": [pathway_id], "dividend_pathway_ids": [], "finding_ids": [], "contribution": "Protects access.", "strengthening_effect": "Improves delivery reliability.", "reason": ""},
        }],
    }
    return "%%%JSON_START%%%" + json.dumps(payload) + "%%%JSON_END%%%"


def test_standard_climate_stage3_branches_before_generic_prompt_and_compacts_history(monkeypatch):
    calls = []
    stage3_output = [_climate_priority_output()]
    monkeypatch.setattr(app_module, "build_climate_stage3_prompt", lambda **kwargs: "CLIMATE PRIORITIES ONLY")

    def fake_stream(messages, max_tokens, stage, **kwargs):
        calls.append({"messages": messages, "max_tokens": max_tokens, "stage": stage})
        fake_stream._last_result = stage3_output[0]
        fake_stream._last_stop_reason = "end_turn"
        yield 'data: {"chunk": "priority-json"}\n\n'

    monkeypatch.setattr(app_module, "_stream_stage", fake_stream)
    diagnostic = json.loads(json.dumps(_canonical_payload()))
    for direction in diagnostic["lenses"][0]["interaction_readout"]:
        for pathway in direction["pathways"]:
            pathway["research_claim_ids"] = ["climate-claim-1"]
    lens_sources = app_module.normalize_climate_research_bundle(
        _valid_research()
    )["sources"]
    response = app_module.app.test_client().post("/api/run-stage", json={
        "stage": 3, "active_lenses": ["climate"], "review_mode": "design",
        "history": [{"role": "assistant", "content": "Stage 2 canonical readout."}],
        "document_type": "PAD", "doc_type": "PAD", "instrument_type": "IPF",
        "lens_diagnostic": diagnostic, "lens_context_sources": lens_sources, "regime_context": {},
    })
    done = next(e for e in _decode_sse(response) if e.get("done"))
    stage3_call = next(c for c in calls if c["stage"] == 3)
    assert stage3_call["messages"] == [{"role": "user", "content": "CLIMATE PRIORITIES ONLY"}]
    assert stage3_call["max_tokens"] == 9000
    assert done["result"] == ""
    assert done["lens_diagnostic"]["schema_version"] == "climate-native-v1"
    assert len(done["priorities"]) == 1
    assert done["priorities"][0]["lens_ids"] == ["climate"]
    assert done["fcv_rating"] == diagnostic["fcv_baseline"]["sensitivity_rating"]
    assert done["fcv_responsiveness_rating"] == diagnostic["fcv_baseline"]["responsiveness_rating"]
    assert done["sensitivity_summary"] == diagnostic["fcv_baseline"]["sensitivity_reasoning"]
    assert done["responsiveness_summary"] == diagnostic["fcv_baseline"]["responsiveness_reasoning"]
    assert done["history"][0] == {"role": "assistant", "content": "Stage 2 canonical readout."}
    assert done["history"][-1] == {"role": "assistant", "content": "[Climate-specific priorities generated from validated payload]"}

    calls_before_invalid_diagnostic = len(calls)
    invalid_events = _decode_sse(app_module.app.test_client().post("/api/run-stage", json={
        "stage": 3, "active_lenses": ["climate"], "review_mode": "design",
        "history": [{"role": "assistant", "content": "Stage 2 canonical readout."}],
        "document_type": "PAD", "doc_type": "PAD", "instrument_type": "IPF",
        "lens_diagnostic": {"schema_version": "unsupported"},
        "lens_context_sources": [], "regime_context": {},
    }))
    invalid = next(e for e in invalid_events if e.get("error_code") == "climate_diagnostic_invalid")
    assert invalid["failed_stage"] == 3
    assert len(calls) == calls_before_invalid_diagnostic
    assert not any(e.get("done") for e in invalid_events)

    stage3_output[0] = _climate_priority_output("invented-pathway")
    blocked_events = _decode_sse(app_module.app.test_client().post("/api/run-stage", json={
        "stage": 3, "active_lenses": ["climate"], "review_mode": "design",
        "history": [{"role": "assistant", "content": "Stage 2 canonical readout."}],
        "document_type": "PAD", "doc_type": "PAD", "instrument_type": "IPF",
        "lens_diagnostic": diagnostic, "lens_context_sources": lens_sources, "regime_context": {},
    }))
    blocked = next(e for e in blocked_events if e.get("error_code") == "climate_priority_invalid")
    assert blocked["failed_stage"] == 3
    assert not any(e.get("done") for e in blocked_events)


def test_express_climate_stage3_branches_before_generic_prompt_and_compacts_history(monkeypatch):
    # Exercise the retained legacy Climate path; exact Climate-only Express uses v2.
    monkeypatch.setattr(app_module, "_is_verified_climate_express", lambda *_args: False)
    calls = []
    stage3_output = [_climate_priority_output()]
    express_diagnostic = json.loads(json.dumps(_canonical_payload()))
    for direction in express_diagnostic["lenses"][0]["interaction_readout"]:
        for pathway in direction["pathways"]:
            pathway["research_claim_ids"] = ["climate-claim-1"]

    def fake_stream(messages, max_tokens, stage, **kwargs):
        calls.append({"messages": messages, "max_tokens": max_tokens, "stage": stage})
        fake_stream._last_stop_reason = "end_turn"
        fake_stream._last_result = (
            "Stage 1 project extraction." if stage == 1 else
            "%%%LENS_DIAGNOSTIC_START%%%" + json.dumps(express_diagnostic) + "%%%LENS_DIAGNOSTIC_END%%%" if stage == 2 else
            stage3_output[0]
        )
        yield 'data: {"chunk": "stage"}\n\n'

    monkeypatch.setattr(app_module, "_stream_stage", fake_stream)
    monkeypatch.setattr(app_module, "build_climate_stage3_prompt", lambda **kwargs: "CLIMATE PRIORITIES ONLY")
    monkeypatch.setattr(app_module, "extract_country_name", lambda text, client: "Exampleland")
    monkeypatch.setattr(app_module, "extract_sector_name", lambda text, client: "Transport")
    monkeypatch.setattr(app_module, "get_fast_client", lambda: object())
    monkeypatch.setattr(app_module, "_iter_stage1_research", lambda *a, **k: _research_result(_valid_research()))
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
    response = app_module.app.test_client().post("/api/run-express", json={
        "active_lenses": ["climate"], "review_mode": "design",
        "document_type": "PAD", "instrument_type": "IPF",
        "documents": [{"name": "PAD.txt", "type": "text", "docRole": "primary", "content": "Named road and access activities. " * 10}],
    })
    done = next(e for e in _decode_sse(response) if e.get("stage_done") == 3)
    stage3_call = next(c for c in calls if c["stage"] == 3)
    assert stage3_call["messages"] == [{"role": "user", "content": "CLIMATE PRIORITIES ONLY"}]
    assert stage3_call["max_tokens"] == 9000
    assert done["result"] == ""
    assert done["lens_diagnostic"]["schema_version"] == "climate-native-v1"
    assert len(done["priorities"]) == 1
    assert done["fcv_rating"] == done["lens_diagnostic"]["fcv_baseline"]["sensitivity_rating"]
    assert done["fcv_responsiveness_rating"] == done["lens_diagnostic"]["fcv_baseline"]["responsiveness_rating"]
    assert done["sensitivity_summary"] == done["lens_diagnostic"]["fcv_baseline"]["sensitivity_reasoning"]
    assert done["responsiveness_summary"] == done["lens_diagnostic"]["fcv_baseline"]["responsiveness_reasoning"]
    assert done["history"][-1] == {"role": "assistant", "content": "[Climate-specific priorities generated from validated payload]"}

    stage3_output[0] = _climate_priority_output("invented-pathway")
    blocked_events = _decode_sse(app_module.app.test_client().post("/api/run-express", json={
        "active_lenses": ["climate"], "review_mode": "design",
        "document_type": "PAD", "instrument_type": "IPF",
        "documents": [{"name": "PAD.txt", "type": "text", "docRole": "primary", "content": "Named road and access activities. " * 10}],
    }))
    blocked = next(e for e in blocked_events if e.get("error_code") == "climate_priority_invalid")
    assert blocked["failed_stage"] == 3
    assert not any(e.get("stage_done") == 3 for e in blocked_events)


def test_candidate_preview_manifest_is_preserved_for_display() -> None:
    manifest = {
        "bank_status": "ok",
        "warning_code": "",
        "schema_version": "1.1.0",
        "content_version": "2026.08-preview",
        "country_iso3": "SSD",
        "evidence_ids": ["SSD-E-020"],
        "pathway_ids": [],
        "candidate_preview": True,
    }

    safe = app_module._safe_climate_bank_manifest(manifest)
    assert safe["candidate_preview"] is True
    envelope = app_module.climate_grounding_envelope({
        "state": "bank-only",
        "bank_manifest": manifest,
        "candidate_preview": True,
    })
    assert envelope["candidate_preview"] is True
    assert envelope["bank_manifest"]["candidate_preview"] is True
