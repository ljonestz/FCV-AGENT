"""Regression tests for the climate dedicated-module completeness fix.

These guard the v9.19 silent-degradation bug: a usable-but-incomplete climate
diagnostic (interactions present, but reflections/integration missing) must
trigger recovery, the recovery request must ask for the dedicated-module
fields, and a usable primary must never be downgraded by a still-incomplete
recovery.
"""

import json

import app as app_module
from sector_lenses import (
    CLIMATE_NATIVE_SCHEMA_VERSION,
    climate_readout_is_complete,
    merge_climate_repair,
)
from sector_lenses.pipeline import climate_lens_readout


_BASELINE = {
    "sensitivity_rating": "Adequate",
    "responsiveness_rating": "Low",
    "sensitivity_reasoning": "Conflict-sensitive delivery is explicit.",
    "responsiveness_reasoning": "A root-cause pathway is present.",
    "evidence_trail": [{
        "claim": "Flood access is seasonally constrained.",
        "source_ids": ["climate-source-1"],
        "project_anchor": "Sub-component 1.2 landing sites",
    }],
}


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
        "executive_summary": (
            "Flood access and allocation are the material intersection."
        ),
        "operating_context": {
            "fcv_setting": "Jonglei access is institutionally constrained.",
            "climate_setting": "Flood timing affects landing-site access.",
            "intersection": (
                "Landing-site delivery depends on contested seasonal access."
            ),
        },
        "interaction_readout": [
            _interaction_with_pathway("climate-fcv-on-project"),
            _interaction_with_pathway("project-on-climate-fcv"),
        ],
        "strengths_weaknesses": [{
            "side": "strength",
            "title": "Community delivery",
            "text": "Named institutions support delivery.",
        }],
        "readout_sections": [],
        "additional_pathways": [],
    }
    if with_reflections:
        entry["reflections"] = [{
            "question_key": "cq2_maladaptation",
            "title": "Maladaptation and lock-in",
            "status_cue": "partial gap",
            "source": "Project document",
            "text": "Siting is treated as engineering, not allocation.",
        }]
    if with_integration:
        entry["integration_level"] = "partly_integrated"
        entry["integration_rating"] = "Adequate"
        entry["integration_summary"] = "Aware but allocation untreated."
    return entry


def _diagnostic(entry):
    return {
        "schema_version": CLIMATE_NATIVE_SCHEMA_VERSION,
        "fcv_baseline": _BASELINE,
        "lenses": [entry],
        "findings": [],
    }


# ── pipeline completeness helper ─────────────────────────────────────────────

def test_climate_readout_is_complete_requires_reflections_and_integration():
    complete = _climate_entry(with_reflections=True, with_integration=True)
    assert climate_readout_is_complete(complete, baseline=_BASELINE) is True

    no_reflections = _climate_entry(with_reflections=False, with_integration=True)
    assert climate_readout_is_complete(
        no_reflections, baseline=_BASELINE
    ) is False

    no_integration = _climate_entry(with_reflections=True, with_integration=False)
    assert climate_readout_is_complete(
        no_integration, baseline=_BASELINE
    ) is False

    interactions_only = _climate_entry(with_reflections=False, with_integration=False)
    assert climate_readout_is_complete(
        interactions_only, baseline=_BASELINE
    ) is False

    assert climate_readout_is_complete(None, baseline=_BASELINE) is False
    assert climate_readout_is_complete(complete) is False
    # Reflections with no grounded text do not count as complete.
    blank = _climate_entry(with_reflections=True, with_integration=True)
    blank["reflections"] = [{"question_key": "cq1_interaction", "title": "t",
                             "status_cue": "ok", "text": "   "}]
    assert climate_readout_is_complete(blank, baseline=_BASELINE) is False
def test_completeness_unchanged_with_source_field():
    """A source-bearing reflection remains grounded in a canonical readout."""
    import sector_lenses.pipeline as p

    entry = _climate_entry(with_reflections=True, with_integration=True)
    entry["reflections"][0]["source"] = "X"

    assert p.climate_readout_is_complete(
        entry, baseline=_BASELINE
    ) is True



def _active_climate_lenses():
    state = app_module.AnalysisState.from_payload({"active_lenses": ["climate"]})
    return app_module.build_lens_stage_context(state, stage=2)["active_lenses"]


def _stage2_output(entry):
    return (
        "Visible Stage 2 assessment\n"
        + app_module.LENS_DIAGNOSTIC_START
        + json.dumps(_diagnostic(entry))
        + app_module.LENS_DIAGNOSTIC_END
    )


def test_incomplete_primary_repairs_only_missing_fields(monkeypatch):
    primary_entry = _climate_entry(
        with_reflections=False,
        with_integration=False,
        materiality_summary="PRIMARY materiality",
    )
    primary_entry["executive_summary"] = "PRIMARY executive"
    repair_entry = _climate_entry(
        with_reflections=True,
        with_integration=True,
        materiality_summary="UNREQUESTED materiality",
    )
    repair_entry["executive_summary"] = "UNREQUESTED executive"
    repair = _diagnostic(repair_entry)
    observed = {}

    def fake_recovery(**kwargs):
        observed["missing_fields"] = kwargs["missing_fields"]
        merged = merge_climate_repair(
            kwargs["primary"], repair, kwargs["missing_fields"]
        )
        yield {"result": merged, "recovered": True, "error_code": ""}

    monkeypatch.setattr(
        app_module, "_iter_climate_diagnostic_recovery", fake_recovery
    )
    diagnostic, recovered, failure = app_module.extract_or_repair_lens_diagnostic(
        _stage2_output(primary_entry), _active_climate_lenses(), []
    )

    assert recovered is True
    assert failure == ""
    climate = climate_lens_readout(diagnostic)
    assert climate["integration_summary"] == "Aware but allocation untreated."
    assert climate["executive_summary"] == "PRIMARY executive"
    assert climate["materiality_summary"] == "PRIMARY materiality"
    assert "lenses.climate.integration_summary" in observed["missing_fields"]


def test_incomplete_primary_returns_blocking_failure_when_repair_stays_incomplete(
    monkeypatch,
):
    primary_entry = _climate_entry(
        with_reflections=False, with_integration=False
    )

    def failed_recovery(**_kwargs):
        yield {
            "result": {"error": True, "message": "Repair incomplete.", "lenses": [], "findings": []},
            "recovered": False,
            "error_code": "climate_diagnostic_invalid",
        }

    monkeypatch.setattr(
        app_module, "_iter_climate_diagnostic_recovery", failed_recovery
    )
    diagnostic, recovered, failure = app_module.extract_or_repair_lens_diagnostic(
        _stage2_output(primary_entry), _active_climate_lenses(), []
    )

    assert recovered is False
    assert diagnostic["error"] is True
    assert failure == "Repair incomplete."


def test_complete_climate_primary_skips_field_recovery(monkeypatch):
    def forbidden_recovery(**_kwargs):
        raise AssertionError("complete primary must skip repair")
        yield

    monkeypatch.setattr(
        app_module, "_iter_climate_diagnostic_recovery", forbidden_recovery
    )
    complete = _climate_entry(with_reflections=True, with_integration=True)
    diagnostic, recovered, failure = app_module.extract_or_repair_lens_diagnostic(
        _stage2_output(complete), _active_climate_lenses(), []
    )

    assert recovered is False
    assert failure == ""
    assert climate_lens_readout(diagnostic)["integration_summary"]
