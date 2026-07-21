"""Application contract tests for selector, payload, prompts, and Stage-3 provenance."""

import json
import io
from pathlib import Path

import app as app_module
from sector_lenses import load_registry


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "sector_lenses"


def test_production_catalogue_has_manual_climate_without_suggestions():
    client = app_module.app.test_client()

    response = client.get("/api/sector-lenses")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["warnings"] == []
    assert len(payload["lenses"]) == 1
    climate = payload["lenses"][0]
    assert climate["id"] == "climate"
    assert climate["activation"] == "manual"
    assert [section["id"] for section in climate["readout_sections"]] == [
        "invest-in", "deliver-through",
    ]
    assert app_module.detect_lens_suggestions(
        "Climate resilience adaptation drought mitigation transition",
        app_module.SECTOR_LENS_REGISTRY,
    ) == []


def test_metadata_response_includes_ranked_lens_suggestions(monkeypatch):
    monkeypatch.setattr(app_module, "SECTOR_LENS_REGISTRY", load_registry(FIXTURE_ROOT))
    monkeypatch.setattr(app_module, "detect_document_type_from_text", lambda text, client: "PAD")
    monkeypatch.setattr(app_module, "get_client", lambda: object())
    client = app_module.app.test_client()
    text = ("Irrigation and food security are material project activities. " * 4).strip()

    response = client.post("/api/detect-document-type", json={"doc_text": text})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["document_type"] == "PAD"
    assert payload["lens_suggestions"][0]["lens_id"] == "test-agriculture"
    assert payload["lens_suggestions"][0]["selected_by_default"] is True


def test_lens_detection_failure_does_not_erase_document_metadata(monkeypatch):
    monkeypatch.setattr(app_module, "detect_document_type_from_text", lambda text, client: "PAD")
    monkeypatch.setattr(app_module, "get_client", lambda: object())
    monkeypatch.setattr(
        app_module, "detect_lens_suggestions",
        lambda text, registry: (_ for _ in ()).throw(RuntimeError("detector unavailable")),
    )

    response = app_module.app.test_client().post(
        "/api/detect-document-type", json={"doc_text": "Project text " * 20}
    )

    assert response.status_code == 200
    assert response.get_json()["document_type"] == "PAD"
    assert response.get_json()["lens_suggestions"] == []


def test_payload_and_prompt_context_resolve_authoritative_versions():
    registry = load_registry(FIXTURE_ROOT)
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["test-agriculture", "unknown"],
        "lens_versions": {"test-agriculture": "0.1.0"},
    })

    context = app_module.build_lens_stage_context(state, stage=2, registry=registry)

    assert state.active_lenses == ["test-agriculture", "unknown"]
    assert context["active_lenses"] == [
        {"id": "test-agriculture", "version": "1.2.0", "position": "primary"}
    ]
    assert {item["code"] for item in context["warnings"]} == {
        "unknown_lens", "version_mismatch"
    }
    assert "%%%LENS_DIAGNOSTIC_START%%%" in context["prompt"]
    assert "Agriculture synthesis guidance" in context["prompt"]
    assert context["restart_required"] is True


def test_priority_parser_preserves_valid_lens_badges_and_drops_unknown_values():
    block = {
        "fcv_rating": "Moderate",
        "fcv_responsiveness_rating": "Emerging",
        "sensitivity_summary": "Summary",
        "responsiveness_summary": "Summary",
        "risk_exposure": {"risks_to": "A", "risks_from": "B"},
        "priorities": [{
            "title": "Target access safeguards",
            "the_gap": "Gap",
            "why_it_matters": "Why",
            "evidence": "Evidence",
            "actions": [],
            "lens_ids": ["climate", "energy", 7, "climate"],
            "lens_relevance": "Material overlap with targeting.",
        }],
    }

    parsed = app_module.extract_priorities(
        "%%%JSON_START%%%" + json.dumps(block) + "%%%JSON_END%%%"
    )

    assert parsed["error"] is False
    assert parsed["priorities"][0]["lens_ids"] == ["climate", "energy"]
    assert parsed["priorities"][0]["lens_relevance"] == "Material overlap with targeting."
    restricted = app_module.extract_priorities(
        "%%%JSON_START%%%" + json.dumps(block) + "%%%JSON_END%%%",
        active_lens_ids=["climate"],
    )
    assert restricted["priorities"][0]["lens_ids"] == ["climate"]


def test_no_active_lens_has_no_prompt_or_core_behaviour_change():
    context = app_module.build_lens_stage_context(
        app_module.AnalysisState.from_payload({}), stage=2
    )

    assert context["active_lenses"] == []
    assert context["prompt"] == ""
    assert context["warnings"] == []


def test_downloaded_report_has_sector_source_and_evidence_appendix(monkeypatch):
    from docx import Document

    monkeypatch.setattr(app_module, "SECTOR_LENS_REGISTRY", load_registry(FIXTURE_ROOT))
    response = app_module.app.test_client().post("/api/download-report", json={
        "summary": "# Test project\nSummary.",
        "priorities": [{
            "title": "Target access safeguards",
            "the_gap": "Gap",
            "lens_ids": ["test-agriculture", "invented-lens"],
            "lens_relevance": "Material targeting link.",
        }],
        "active_lenses": [{
            "id": "test-agriculture", "version": "1.2.0", "position": "primary"
        }],
        "lens_diagnostic": {"findings": [{
            "lens_ids": ["test-agriculture"], "status": "partially_addressed",
            "core_mappings": ["dnh:3"], "source_ids": ["agri-guidance"],
            "evidence": ["Water-user groups are used for targeting."],
            "mechanism": "water access grievance",
            "geography": "project area",
            "action_target": "beneficiary targeting",
        }]},
        "metadata": {"date_str": "21 July 2026"},
    })

    assert response.status_code == 200
    document = Document(io.BytesIO(response.data))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "Appendix: Sector-Lens Sources and Evidence" in text
    assert "Agriculture Test Guidance" in text
    assert "Water-user groups are used for targeting." in text
    assert "Sector lenses: test-agriculture" in text
    assert "invented-lens" not in text


def test_frontend_contract_includes_selector_locking_v3_and_lens_rendering():
    html = (Path(app_module.__file__).parent / "index.html").read_text(encoding="utf-8")

    assert 'id="lens-selector"' in html
    assert "version: 3" in html
    assert "active_lenses:activeLenses" in html
    assert "lensSelectionLocked=true" in html
    assert "renderLensDiagnostic()" in html
    assert "pr.lens_ids" in html
    assert "function resumeExpressRun" not in html
    assert "restart Stage 1" in html


def test_final_stage3_lens_prompt_respects_combined_platform_budget():
    registry = load_registry(FIXTURE_ROOT)
    state = app_module.AnalysisState.from_payload({"active_lenses": ["test-agriculture"]})
    huge = {"findings": [{
        "lens_ids": ["test-agriculture"], "evidence": ["x" * 1000],
        "source_ids": ["agri-guidance"], "core_mappings": ["dnh:3"],
        "mechanism": f"mechanism-{index}", "geography": "north",
        "action_target": "targeting", "status": "gap",
    } for index in range(50)]}

    context = app_module.build_lens_stage_context(state, 3, registry, huge)

    assert context["estimated_tokens"] <= 900
    assert context["truncated"] is True
