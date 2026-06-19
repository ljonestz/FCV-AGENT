"""Phase 6 intersection-matrix (multi-dimension composition) regression tests.

Composes the dimensions built in Phases 1-5 into one coherent output:
- base instrument spine (IPF/DPF/P4R) sets the unit of analysis;
- mid-cycle and multi-country are overlays; MPA is a wrapper;
- a single synthesis dedupes and scope-tags priorities, applies precedence rules,
  and bounds overlay injection with disclosure (never silent truncation).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _state(**intake):
    from app import AnalysisState
    return AnalysisState.from_payload({"structured_intake": intake})


def test_composition_plan_plain_ipf_is_backward_compatible():
    from app import build_composition_plan
    plan = build_composition_plan(_state(instrument="IPF", doc_type="PAD", countries=[{"name": "Chad"}]))
    assert plan["overlays"] == []
    assert plan["wrapper"] is None
    assert plan["is_intersection"] is False
    assert "IPF" in plan["spine"]
    assert plan["precedence"]["rating"] == "single-country"
    assert "preparation" in plan["precedence"]["temporal"].lower()


def test_composition_plan_dpf_additional_financing():
    from app import build_composition_plan
    plan = build_composition_plan(_state(
        instrument="DPO", doc_type="AF", countries=[{"name": "Chad"}], restructuring_level="Level 2",
    ))
    assert "DPF" in plan["spine"]
    assert "mid_cycle_overlay" in plan["overlays"]
    assert plan["is_intersection"] is True
    assert "mid-cycle" in plan["precedence"]["temporal"].lower()
    assert "Level 2" in plan["precedence"]["output_register"]


def test_composition_plan_regional_mpa_additional_financing():
    from app import build_composition_plan
    plan = build_composition_plan(_state(
        instrument="PforR", doc_type="AF",
        countries=[{"name": "Ethiopia"}, {"name": "Somalia"}, {"name": "Kenya"}],
        is_mpa=True, phase="Phase 1",
    ))
    assert "P4R" in plan["spine"]
    assert "mid_cycle_overlay" in plan["overlays"]
    assert "multi_country_layer" in plan["overlays"]
    assert plan["wrapper"] == "mpa_wrapper"
    assert plan["precedence"]["rating"].startswith("fragility")
    assert plan["active_layer_count"] >= 4


def test_dedupe_and_scope_priorities():
    from app import dedupe_and_scope_priorities
    priorities = [
        {"title": "Priority 1 - Preserve FCV targeting", "priority_scope": "country-specific"},
        {"title": "Priority 2 - Preserve FCV targeting", "the_gap": "dup"},
        {"title": "Priority 3 - Cross-border corridor", "priority_scope": "regional"},
        {"title": "Priority 4 - New unique item"},
    ]
    result = dedupe_and_scope_priorities(priorities)
    titles = [p["title"] for p in result]
    assert len(result) == 3
    assert "Priority 2 - Preserve FCV targeting" not in titles
    # default scope assigned where missing
    assert result[-1]["priority_scope"] == "country-specific"


def test_bounded_injection_caps_lowest_priority_with_disclosure():
    from app import bounded_injection_plan
    plan = bounded_injection_plan(
        ["instrument_spine", "mid_cycle_overlay", "multi_country_layer"],
        budget=10,
        costs={"instrument_spine": 4, "mid_cycle_overlay": 4, "multi_country_layer": 6},
    )
    assert "instrument_spine" in plan["included"]
    assert "mid_cycle_overlay" in plan["included"]
    assert "multi_country_layer" in plan["dropped"]
    assert plan["disclosure"]  # non-empty disclosure when something is bounded


def test_bounded_injection_within_budget_no_disclosure():
    from app import bounded_injection_plan
    plan = bounded_injection_plan(
        ["instrument_spine", "mid_cycle_overlay"],
        budget=1000,
        costs={"instrument_spine": 4, "mid_cycle_overlay": 4},
    )
    assert plan["dropped"] == []
    assert plan["disclosure"] == ""


def test_bounded_injection_never_drops_instrument_spine():
    from app import bounded_injection_plan
    plan = bounded_injection_plan(
        ["instrument_spine", "multi_country_layer"],
        budget=1,
        costs={"instrument_spine": 50, "multi_country_layer": 50},
    )
    assert "instrument_spine" in plan["included"]
    assert "multi_country_layer" in plan["dropped"]


def test_intersection_guide_and_prompt_present():
    import app
    import background_docs
    guide = background_docs.INTERSECTION_SYNTHESIS_GUIDE
    assert "single" in guide.lower()
    assert "precedence" in guide.lower()
    assert "scope" in guide.lower()
    combined = "\n".join([app.DEFAULT_PROMPTS["1"], app.DEFAULT_PROMPTS["2"], app.DEFAULT_PROMPTS["3"]])
    assert "deduplicat" in combined.lower()
    assert "precedence" in combined.lower()
    assert "single coherent" in combined.lower() or "one coherent" in combined.lower()
