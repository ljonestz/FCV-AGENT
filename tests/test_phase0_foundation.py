"""Phase 0 foundation and policy-currency regression tests."""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_fy26_fcs_membership_and_categories():
    from background_docs import FCS_COUNTRIES_CURRENT, FCS_COUNTRY_CATEGORIES

    removed = {
        "Iraq",
        "Libya",
        "Mozambique",
        "Nigeria",
        "Solomon Islands",
    }
    added = {"Suriname"}

    assert len(FCS_COUNTRIES_CURRENT) == 35
    assert not (removed & FCS_COUNTRIES_CURRENT)
    assert added <= FCS_COUNTRIES_CURRENT
    assert FCS_COUNTRY_CATEGORIES["Suriname"] == "Fragility"
    assert FCS_COUNTRY_CATEGORIES["Ukraine"] == "Conflict"
    assert FCS_COUNTRY_CATEGORIES["Afghanistan"] == "Fragility"


def test_classify_country_uses_fy26_fcs_list():
    from app import classify_country

    assert classify_country("Suriname")["category"] == "Conflict-Affected"
    assert classify_country("Nigeria")["category"] is None


def test_policy_currency_strings_are_updated():
    import app
    import background_docs

    combined = "\n".join([
        app.DEFAULT_PROMPTS["1"],
        app.DEFAULT_PROMPTS["2"],
        app.DEFAULT_PROMPTS["3"],
        background_docs.FCV_GUIDE,
        background_docs.FCV_REFRESH_FRAMEWORK,
        background_docs.FCV_INSTRUMENT_CALIBRATION,
        background_docs.WB_INSTRUMENT_GUIDE["DPO"]["description"],
        background_docs.WB_INSTRUMENT_GUIDE["DPO"]["not_applicable"],
        # DNH Principle 9 (SEA/SH) text moved from DEFAULT_PROMPTS["2"] into the
        # instrument-conditional DNH_SEASH_IPF constant in Workstream 1 (v9.14);
        # it is injected into the assembled Stage 2 prompt via {dnh_seash_guidance}.
        background_docs.DNH_SEASH_IPF,
    ])

    assert "WBG FCV Strategy 2026-2030" in combined
    assert "OPS5.02-POL.120" in combined
    assert "DFI2.01-DIR.108" in combined
    assert "Low / Moderate / Substantial / High" in combined
    assert "OP/BP 8.60" not in combined
    assert "Very High" not in combined
    assert not re.search(r"\b8 DNH principles\b", combined)


def test_render_source_provider_returns_verified_and_fallback_entries():
    from app import RenderSourceProvider

    provider = RenderSourceProvider()

    dpf = provider.get_policy("dpf_policy")
    assert dpf.key == "dpf_policy"
    assert dpf.catalogue_id == "OPS5.02-POL.120"
    assert dpf.needs_verification is False

    fallback = provider.get_policy("missing-policy-key")
    assert fallback.needs_verification is True
    assert "Verify with OPCS" in fallback.summary


def test_default_module_and_rubric_preserve_ipf_path():
    from app import Rubric, score_sr, select_module

    module = select_module(doc_type="PAD", instrument="IPF", country_scope="single")
    assert module.key == ("PAD", "IPF", "single")
    assert module.rubric.name == "IPF 12-OST default"
    assert module.legacy_instrument == "IPF"

    result = score_sr(
        module.rubric,
        {
            "addressed": 8,
            "partial": 2,
            "weak": 1,
            "not_addressed": 1,
            "responsiveness_evidence": "limited",
        },
    )
    assert result["sensitivity_rating"] == "Adequate"
    assert result["responsiveness_rating"] == "Low"
    assert isinstance(module.rubric, Rubric)


def test_analysis_state_from_payload_is_backward_compatible():
    from app import AnalysisState

    default_state = AnalysisState.from_payload({})
    assert default_state.instrument == "Unknown"
    assert default_state.doc_type == "Unknown"
    assert default_state.country_scope == "single"
    assert default_state.countries == []
    assert default_state.active_modules == []

    structured_state = AnalysisState.from_payload({
        "structured_intake": {
            "instrument": "IPF",
            "doc_type": "PAD",
            "country_scope": "single",
            "countries": [{"name": "Suriname"}],
            "parent_operation": "P123456",
        }
    })
    assert structured_state.instrument == "IPF"
    assert structured_state.doc_type == "PAD"
    assert structured_state.countries[0]["name"] == "Suriname"
    assert structured_state.parent_operation == "P123456"


def test_reference_docs_do_not_reintroduce_stale_policy_labels():
    checked_paths = [
        REPO_ROOT / "claude.md",
        REPO_ROOT / "docs" / "fcv-agent-knowledge-architecture.html",
        REPO_ROOT / "docs" / "reference" / "reference_prompt_architecture.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in checked_paths)

    assert "35 FY26 FCS" in combined
    assert "39 current FCS" not in combined
    assert "OP/BP 8.60" not in combined
    assert "Very High" not in combined