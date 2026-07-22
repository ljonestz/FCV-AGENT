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


def test_downloaded_report_has_climate_readout_and_context_sources():
    from docx import Document

    response = app_module.app.test_client().post("/api/download-report", json={
        "summary": "# Test project\nSummary.",
        "priorities": [],
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Emerging",
        "sensitivity_summary": "The project recognizes key FCV risks and remaining gaps.",
        "responsiveness_summary": "The project could make a stronger contribution to resilience.",
        "risk_exposure": {
            "risks_to": "Core fallback risk to the project.",
            "risks_from": "Core fallback risk from the project.",
        },
        "active_lenses": [{
            "id": "climate", "version": "1.1.0", "position": "primary"
        }],
        "lens_diagnostic": {"lenses": [{
            "lens_id": "climate",
            "applicability": "material",
            "materiality_level": "high",
            "materiality_summary": "Drought and fragility affect delivery.",
            "analysis_emphasis": ["adaptation"],
            "source_ids": ["peace-social-dividends", "context-ccdr"],
            "interaction_readout": [{
                "direction_id": "climate-fcv-on-project",
                "summary": "Drought, insecurity, and weak access could disrupt delivery.",
                "project_implications": ["Remote sites may become inaccessible."],
                "source_ids": ["peace-social-dividends"],
            }, {
                "direction_id": "project-on-climate-fcv",
                "summary": "Benefit rules could strengthen resilience or exclusion.",
                "adverse_effects": ["Seasonal users could be excluded."],
                "source_ids": ["peace-social-dividends"],
            }],
            "readout_sections": [{
                "section_id": "invest-in",
                "items": [{
                    "item_id": "institutional-capacity-legitimacy",
                    "status": "supported",
                    "mechanism": "Transparent allocation can strengthen legitimacy.",
                    "project_contribution": "Community institutions allocate resources.",
                    "strengthening_action": "Map seasonal users before approving rules.",
                    "evidence": ["Community institutions are a project mechanism."],
                    "evidence_gap": "Seasonal users are not mapped.",
                    "trade_off": "Formalization may exclude customary users.",
                    "source_ids": ["peace-social-dividends"],
                }, {
                    "item_id": "social-cohesion-inclusion",
                    "status": "not_material",
                    "project_contribution": "Do not render this pathway.",
                    "strengthening_action": "Do not render this pathway.",
                    "evidence": ["No credible entry point."],
                    "source_ids": ["peace-social-dividends"],
                }],
            }, {
                "section_id": "deliver-through",
                "items": [{
                    "item_id": "flexible-adaptive-delivery",
                    "status": "potential",
                    "mechanism": "Contingent delivery can respond to shocks.",
                    "project_contribution": "The project uses contingent delivery.",
                    "strengthening_action": "Define combined flood and access triggers.",
                    "evidence": ["Contingent delivery is described."],
                    "evidence_gap": "No trigger is defined.",
                    "trade_off": "Flexibility needs accountability.",
                    "source_ids": ["defueling-conflict"],
                }],
            }],
            "additional_pathways": [{
                "section_id": "invest-in",
                "title": "Shared ecosystem restoration",
                "status": "potential",
                "mechanism": "Joint restoration can create collective benefits.",
                "project_contribution": "The project restores shared watersheds.",
                "strengthening_action": "Add joint oversight and dispute resolution.",
                "evidence": ["Watershed restoration is included."],
                "source_ids": ["peace-social-dividends"],
            }],
            "other_pathways": [{
                "pathway": "mitigation-transition",
                "status": "not_material",
                "reason": "No clear transition pathway.",
            }],
        }], "findings": []},
        "lens_context_sources": [{
            "id": "context-ccdr",
            "lens_id": "climate",
            "source_type": "ccdr",
            "country": "Exampleland",
            "title": "Exampleland Country Climate and Development Report",
            "publication_date": "2025",
            "url": "https://www.worldbank.org/example-ccdr",
            "location": "p. 4",
            "summary": "Drought affects project areas.",
        }],
        "metadata": {"date_str": "21 July 2026"},
    })

    assert response.status_code == 200
    document = Document(io.BytesIO(response.data))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert text.index("Climate-focused FCV assessment") < text.index("Summary.")
    assert "High materiality" in text
    assert text.index("FCV Sensitivity") < text.index(
        "How Climate-FCV interactions could affect the project"
    )
    assert text.index("FCV Responsiveness") < text.index(
        "How Climate-FCV interactions could affect the project"
    )
    assert "How the project could influence Climate-FCV dynamics" in text
    assert "Where the project could build climate, peace, and social dividends" in text
    assert "Institutional capacity and legitimacy" in text
    assert "How project design and delivery could strengthen those dividends" in text
    assert "Flexible and adaptive delivery" in text
    assert "Shared ecosystem restoration" in text
    assert "How the project may contribute" in text
    assert "How this could be strengthened" in text
    assert "Do not render this pathway" not in text
    assert "Other pathways considered" not in text
    assert "Core fallback risk to the project" not in text
    assert "Country Climate and Development Report" in text
    assert text.count("Country Climate and Development Report") <= 2


def test_downloaded_report_scales_low_climate_materiality_without_empty_dividends():
    from docx import Document

    response = app_module.app.test_client().post("/api/download-report", json={
        "summary": "# Low test\nSummary.",
        "priorities": [],
        "sensitivity_summary": "Core sensitivity remains material.",
        "responsiveness_summary": "Core responsiveness remains limited.",
        "active_lenses": [{
            "id": "climate", "version": "1.1.0", "position": "primary"
        }],
        "lens_diagnostic": {"lenses": [{
            "lens_id": "climate",
            "applicability": "possible",
            "materiality_level": "low",
            "materiality_summary": "Climate entry points are limited.",
            "interaction_readout": [{
                "direction_id": "climate-fcv-on-project",
                "summary": "Seasonal rainfall may modestly affect access.",
            }],
            "readout_sections": [],
            "additional_pathways": [],
        }], "findings": []},
        "metadata": {"date_str": "22 July 2026"},
    })

    assert response.status_code == 200
    document = Document(io.BytesIO(response.data))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "limited climate materiality" in text
    assert "Seasonal rainfall may modestly affect access" in text
    assert "Climate, peace and social dividends" not in text


def test_downloaded_report_uses_safe_climate_failure_and_core_risk_fallback():
    from docx import Document

    response = app_module.app.test_client().post("/api/download-report", json={
        "summary": "# Failure test\nSummary.",
        "priorities": [],
        "active_lenses": [{
            "id": "climate", "version": "1.1.0", "position": "primary"
        }],
        "lens_diagnostic": {},
        "risk_exposure": {
            "risks_to": "Insecurity could disrupt delivery.",
            "risks_from": "Exclusion could deepen grievance.",
        },
        "metadata": {"date_str": "22 July 2026"},
    })

    assert response.status_code == 200
    document = Document(io.BytesIO(response.data))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "validated Climate-FCV diagnostic could not be produced" in text
    assert "FCV Risk Exposure" in text
    assert "Insecurity could disrupt delivery" in text
    assert "Climate, peace and social dividends" not in text


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


def test_climate_diagnostic_retains_readouts_and_ccdr_context():
    module_root = Path(app_module.__file__).parent / "sector_lenses" / "modules"
    registry = load_registry(module_root)
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"]
    })
    payload = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "materiality_summary": "Drought affects delivery and livelihoods.",
        "analysis_emphasis": ["adaptation", "resource access"],
        "source_ids": [
            "peace-social-dividends", "context-ccdr", "invented"
        ],
        "readout_sections": [{
            "section_id": "invest-in",
            "items": [{
                "item_id": "institutional-capacity-legitimacy",
                "status": "supported",
                "mechanism": "Transparent allocation can strengthen legitimacy.",
                "evidence": ["Water committees allocate access."],
                "evidence_gap": "Seasonal users are not mapped.",
                "trade_off": "Formalization may exclude customary users.",
                "source_ids": ["peace-social-dividends", "context-ccdr"],
            }],
        }],
        "other_pathways": [{
            "pathway": "mitigation-transition",
            "status": "not_material",
            "reason": "No emissions or transition mechanism is documented.",
        }],
    }], "findings": []}
    sources = [{
        "id": "context-ccdr",
        "lens_id": "climate",
        "source_type": "ccdr",
        "country": "Exampleland",
        "title": "Example CCDR",
        "publication_date": "2025",
        "url": "https://www.worldbank.org/example",
        "location": "p. 4",
        "summary": "Drought affects project areas.",
    }, {
        "id": "context-ccdr",
        "lens_id": "climate",
        "source_type": "ccdr",
        "title": "Untrusted context",
        "url": "https://example.com/not-a-ccdr",
        "summary": "This source must not enter the diagnostic.",
    }]

    context = app_module.build_lens_stage_context(
        state, 3, registry, payload, sources
    )

    assert "Drought affects delivery" in context["prompt"]
    assert "context-ccdr" in context["prompt"]
    assert "invented" not in context["prompt"]
    assert context["lens_context_sources"] == sources[:1]


def test_active_climate_stage2_supersedes_lightweight_core_check():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"]
    })

    context = app_module.build_lens_stage_context(state, 2)

    assert "materiality_summary" in context["prompt"]
    assert "readout_sections" in context["prompt"]
    assert "supersedes the lightweight supplementary Climate-FCV Nexus" in (
        context["prompt"]
    )
    assert "do not produce a duplicate" in context["prompt"]


def test_active_climate_stage2_requests_materiality_interactions_and_pathways():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"]
    })

    prompt = app_module.build_lens_stage_context(state, 2)["prompt"]

    for field in (
        "materiality_level", "interaction_readout", "project_contribution",
        "strengthening_action", "additional_pathways",
    ):
        assert field in prompt
    assert "development project" in prompt
    assert "not its primary objective" in prompt


def test_active_climate_stage3_preserves_option_a_layers_and_gradient():
    state = app_module.AnalysisState.from_payload({"active_lenses": ["climate"]})
    diagnostic = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "materiality_level": "high",
        "materiality_summary": "Flood and FCV pressures are central.",
        "interaction_readout": [{
            "direction_id": "climate-fcv-on-project",
            "summary": "Flood and insecurity could disrupt delivery.",
        }],
        "readout_sections": [],
        "additional_pathways": [],
    }], "findings": []}

    context = app_module.build_lens_stage_context(
        state, 3, lens_diagnostic=diagnostic
    )
    prompt = context["prompt"]

    assert "High, Medium, or Low" in prompt
    assert "executive summary" in prompt
    assert "two-way Climate-FCV interaction" in prompt
    assert "current contribution" in prompt
    assert "how it could be strengthened" in prompt
    assert "not a quota" in prompt
    assert "Flood and insecurity could disrupt delivery" in prompt
    assert context["lens_diagnostic"]["lenses"][0]["materiality_level"] == "high"


def test_high_climate_materiality_warns_when_priorities_drop_provenance(caplog):
    diagnostic = {"lenses": [{
        "lens_id": "climate",
        "materiality_level": "high",
    }]}

    with caplog.at_level("WARNING", logger=app_module.app.logger.name):
        warning = app_module.warn_on_missing_high_climate_priority(
            [{"title": "Core priority", "lens_ids": []}], diagnostic
        )

    assert warning is True
    assert "High Climate-FCV materiality" in caplog.text
    caplog.clear()
    assert app_module.warn_on_missing_high_climate_priority(
        [{"title": "Climate priority", "lens_ids": ["climate"]}], diagnostic
    ) is False
    assert app_module.warn_on_missing_high_climate_priority(
        [{"title": "Core priority", "lens_ids": []}],
        {"lenses": [{"lens_id": "climate", "materiality_level": "medium"}]},
    ) is False


def test_frontend_persists_and_submits_lens_context_sources():
    html = (Path(app_module.__file__).parent / "index.html").read_text(
        encoding="utf-8"
    )

    assert "lensContextSources" in html
    assert "lens_context_sources:lensContextSources" in html
    assert "lens_context_sources: lensContextSources || []" in html


def test_large_climate_readout_respects_stage3_platform_budget():
    state = app_module.AnalysisState.from_payload({"active_lenses": ["climate"]})
    item_ids = [
        "social-cohesion-inclusion",
        "institutional-capacity-legitimacy",
        "livelihoods-opportunity",
    ]
    payload = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "materiality_summary": "m" * 600,
        "analysis_emphasis": ["e" * 100] * 5,
        "evidence": ["v" * 500] * 5,
        "source_ids": ["peace-social-dividends"],
        "readout_sections": [{
            "section_id": "invest-in",
            "items": [{
                "item_id": item_id,
                "status": "supported",
                "mechanism": "x" * 500,
                "evidence": ["y" * 500] * 5,
                "evidence_gap": "z" * 500,
                "trade_off": "t" * 500,
                "source_ids": ["peace-social-dividends"],
            } for item_id in item_ids],
        }],
        "other_pathways": [{
            "pathway": f"pathway-{index}",
            "status": "potential",
            "reason": "r" * 500,
        } for index in range(10)],
    }], "findings": []}

    context = app_module.build_lens_stage_context(state, 3, lens_diagnostic=payload)

    assert context["estimated_tokens"] <= 900
    assert context["truncated"] is True


def test_active_climate_stage3_integrates_opening_and_uses_flexible_mix():
    module_root = Path(app_module.__file__).parent / "sector_lenses" / "modules"
    registry = load_registry(module_root)
    state = app_module.AnalysisState.from_payload({"active_lenses": ["climate"]})
    diagnostic = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "materiality_summary": "Drought and FCV pressures affect delivery.",
        "analysis_emphasis": ["adaptation"],
        "readout_sections": [],
        "other_pathways": [],
    }], "findings": []}

    context = app_module.build_lens_stage_context(
        state, 3, registry, diagnostic, []
    )
    prompt = context["prompt"].lower()

    assert "opening assessment" in prompt
    assert "operational context" in prompt
    assert "maximum of five substantive priorities" in prompt
    assert "not a quota" in prompt
    assert "may contain more climate-linked" in prompt
    assert "single existing priority list" in prompt


def test_core_only_stage3_keeps_four_to_five_rule():
    context = app_module.build_lens_stage_context(
        app_module.AnalysisState.from_payload({}), 3
    )

    assert context["prompt"] == ""
    assert "4-5 priorities total" in app_module.DEFAULT_PROMPTS["3"]
    assert "Climate-FCV Nexus" in app_module.DEFAULT_PROMPTS["2"]
