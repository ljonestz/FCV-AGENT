"""Regression tests for the climate dedicated-module completeness fix.

These guard the v9.19 silent-degradation bug: a usable-but-incomplete climate
diagnostic (interactions present, but reflections/integration missing) must
trigger recovery, the recovery request must ask for the dedicated-module
fields, and a usable primary must never be downgraded by a still-incomplete
recovery.
"""

import json

import app as app_module
from sector_lenses import climate_readout_is_complete
from sector_lenses.pipeline import climate_lens_readout


def _interaction_with_pathway(direction):
    return {
        "direction_id": direction,
        "summary": "Flood and insecurity interact with delivery.",
        "pathways": [{
            "pathway_id": f"{direction}-1",
            "pressure": "Seasonal flood pulse",
            "mechanism": "Access and allocation conditions change.",
            "project_implication": "A named activity faces a distributional risk.",
            "design_response": "Apply a specific access safeguard.",
            "project_elements": ["Landing sites"],
            "geographies": ["Jonglei"],
            "affected_groups": ["Displaced households"],
            "systems_or_assets": [],
            "time_horizons": ["project-lifetime"],
            "research_claim_ids": [],
            "confidence": "medium",
            "evidence_gap": "Site-level evidence remains incomplete.",
        }],
    }


def _climate_entry(*, with_reflections, with_integration, materiality_summary="Base"):
    entry = {
        "lens_id": "climate",
        "applicability": "material",
        "materiality_level": "medium",
        "materiality_summary": materiality_summary,
        "interaction_readout": [
            _interaction_with_pathway("climate-fcv-on-project"),
            _interaction_with_pathway("project-on-climate-fcv"),
        ],
        "readout_sections": [],
        "additional_pathways": [],
    }
    if with_reflections:
        entry["reflections"] = [{
            "question_key": "cq2_maladaptation",
            "title": "Maladaptation and lock-in",
            "status_cue": "partial gap",
            "text": "Siting is treated as engineering, not allocation.",
        }]
    if with_integration:
        entry["integration_level"] = "partly_integrated"
        entry["integration_summary"] = "Aware but allocation untreated."
    return entry


def _diagnostic(entry):
    return {"lenses": [entry], "findings": []}


# ── pipeline completeness helper ─────────────────────────────────────────────

def test_climate_readout_is_complete_requires_reflections_and_integration():
    complete = _climate_entry(with_reflections=True, with_integration=True)
    assert climate_readout_is_complete(complete) is True

    no_reflections = _climate_entry(with_reflections=False, with_integration=True)
    assert climate_readout_is_complete(no_reflections) is False

    no_integration = _climate_entry(with_reflections=True, with_integration=False)
    assert climate_readout_is_complete(no_integration) is False

    interactions_only = _climate_entry(with_reflections=False, with_integration=False)
    assert climate_readout_is_complete(interactions_only) is False

    assert climate_readout_is_complete(None) is False
    # Reflections with no grounded text do not count as complete.
    blank = _climate_entry(with_reflections=True, with_integration=True)
    blank["reflections"] = [{"question_key": "cq1_interaction", "title": "t",
                             "status_cue": "ok", "text": "   "}]
    assert climate_readout_is_complete(blank) is False


# ── recovery prompt requests the dedicated-module contract ───────────────────

def test_recovery_prompt_requests_dedicated_module_fields():
    captured = {}

    class FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)
            text = (
                app_module.LENS_DIAGNOSTIC_START
                + json.dumps({"lenses": [], "findings": []})
                + app_module.LENS_DIAGNOSTIC_END
            )
            return type("Response", (), {
                "content": [type("Text", (), {"text": text})()]
            })()

    client = type("Client", (), {"messages": FakeMessages()})()
    app_module.repair_lens_diagnostic(
        "Visible Stage 2 assessment",
        ["climate"],
        {"climate": set()},
        {"climate": {"invest-in": set(), "deliver-through": set()}},
        client=client,
    )
    prompt = captured["messages"][0]["content"]
    for token in (
        "reflections", "integration_level", "integration_summary",
        "less_central", "sensitivity_evidence", "responsiveness_evidence",
        "cq1_interaction", "cq6_adaptive",
    ):
        assert token in prompt, f"recovery prompt missing {token!r}"
    # Bounded budget must still be requested (not the old 12,000 cap alone).
    assert "16,000 characters" in prompt


# ── orchestration: incomplete primary triggers recovery ──────────────────────

def _active_climate_lenses():
    state = app_module.AnalysisState.from_payload({"active_lenses": ["climate"]})
    return app_module.build_lens_stage_context(state, stage=2)["active_lenses"]


def _incomplete_primary_output():
    entry = _climate_entry(
        with_reflections=False, with_integration=False,
        materiality_summary="PRIMARY interactions only",
    )
    return (
        "Visible Stage 2 assessment\n"
        + app_module.LENS_DIAGNOSTIC_START
        + json.dumps(_diagnostic(entry))
        + app_module.LENS_DIAGNOSTIC_END
    )


def test_incomplete_climate_primary_triggers_recovery_and_completes(monkeypatch):
    complete = _diagnostic(
        _climate_entry(with_reflections=True, with_integration=True,
                       materiality_summary="RECOVERED complete")
    )
    calls = {"n": 0}

    def fake_repair(*args, **kwargs):
        calls["n"] += 1
        return complete, True

    monkeypatch.setattr(app_module, "repair_lens_diagnostic", fake_repair)

    diagnostic, recovered, failure = app_module.extract_or_repair_lens_diagnostic(
        _incomplete_primary_output(),
        _active_climate_lenses(),
        [],
    )

    assert calls["n"] == 1, "recovery must fire for an incomplete primary"
    assert recovered is True
    assert failure == ""
    entry = climate_lens_readout(diagnostic)
    assert climate_readout_is_complete(entry) is True
    assert entry["materiality_summary"] == "RECOVERED complete"


def test_incomplete_primary_kept_when_recovery_stays_incomplete(monkeypatch):
    still_incomplete = _diagnostic(
        _climate_entry(with_reflections=False, with_integration=False,
                       materiality_summary="RECOVERED still incomplete")
    )

    def fake_repair(*args, **kwargs):
        return still_incomplete, True

    monkeypatch.setattr(app_module, "repair_lens_diagnostic", fake_repair)

    diagnostic, recovered, failure = app_module.extract_or_repair_lens_diagnostic(
        _incomplete_primary_output(),
        _active_climate_lenses(),
        [],
    )

    # A usable primary must not be downgraded by a still-incomplete recovery.
    assert recovered is False
    assert failure == ""
    entry = climate_lens_readout(diagnostic)
    assert entry["materiality_summary"] == "PRIMARY interactions only"


def test_complete_climate_primary_skips_recovery(monkeypatch):
    complete_entry = _climate_entry(with_reflections=True, with_integration=True)
    stage2_output = (
        "Visible Stage 2 assessment\n"
        + app_module.LENS_DIAGNOSTIC_START
        + json.dumps(_diagnostic(complete_entry))
        + app_module.LENS_DIAGNOSTIC_END
    )
    monkeypatch.setattr(
        app_module,
        "repair_lens_diagnostic",
        lambda *a, **k: (_ for _ in ()).throw(
            AssertionError("recovery should not run for a complete primary")
        ),
    )

    diagnostic, recovered, failure = app_module.extract_or_repair_lens_diagnostic(
        stage2_output,
        _active_climate_lenses(),
        [],
    )
    assert recovered is False
    assert failure == ""
    assert climate_readout_is_complete(climate_lens_readout(diagnostic)) is True


def test_completeness_unchanged_with_source_field():
    """A source-bearing reflection still counts as grounded; completeness keys on
    >=1 grounded reflection + non-empty integration_summary (unchanged contract)."""
    import sector_lenses.pipeline as p
    entry = {"lens_id": "climate",
             "reflections": [{"question_key": "cq2_maladaptation", "title": "t",
                              "status_cue": "gap", "source": "X", "text": "grounded answer"}],
             "integration_summary": "aware but untreated"}
    assert p.climate_readout_is_complete(entry) is True
