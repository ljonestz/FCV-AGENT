"""Phase 4+5 MPA wrapper + Multi-country / regional regression tests.

Two composable layers on top of the base-instrument modules:
- Multi-country / regional: orthogonal country_scope dimension; per-country
  classification + regional synthesis + cross-border lens + fragility-weighted roll-up.
- MPA wrapper: phase detection + carve-outs + approval-authority + cross-phase FCV drift,
  routing each phase to its base instrument.
All procedural / eligibility / financing-window language stays advisory-only.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_extract_country_set_parses_multi_country_block():
    from app import extract_country_set
    stage1_output = """
    %%%COUNTRY_SET_START%%%
    countries: Ethiopia; Somalia; Kenya
    regional_pdo: true
    implementing_entity: Trade and Development Bank (TDB)
    %%%COUNTRY_SET_END%%%
    """
    parsed = extract_country_set(stage1_output)
    assert parsed["error"] is False
    assert parsed["is_multi_country"] is True
    assert parsed["regional_pdo"] is True
    assert len(parsed["countries"]) == 3
    assert "Somalia" in parsed["countries"]
    assert "TDB" in parsed["implementing_entity"]


def test_extract_country_set_single_country_stays_single():
    from app import extract_country_set
    stage1_output = """
    %%%COUNTRY_SET_START%%%
    countries: Chad
    regional_pdo: false
    implementing_entity: Ministry of Finance
    %%%COUNTRY_SET_END%%%
    """
    parsed = extract_country_set(stage1_output)
    assert parsed["error"] is False
    assert parsed["is_multi_country"] is False
    assert parsed["countries"] == ["Chad"]


def test_extract_country_set_missing_block():
    from app import extract_country_set
    parsed = extract_country_set("No country set block here.")
    assert parsed["error"] is True
    assert parsed["countries"] == []
    assert parsed["is_multi_country"] is False


def test_classify_country_set_flags_fragile_and_spillover():
    from app import classify_country_set
    result = classify_country_set(["Somalia", "Kenya"])
    by_name = {c["name"]: c for c in result}
    assert by_name["Somalia"]["category"] == "Conflict-Affected"
    assert by_name["Kenya"]["spillover_candidate"] is True


def test_weighted_rollup_keeps_fragile_minority_visible():
    from app import weighted_rollup
    country_ratings = [
        {"name": "Somalia", "category": "Conflict-Affected", "sensitivity_score": 0.2, "responsiveness_score": 0.2},
        {"name": "Kenya", "category": None, "sensitivity_score": 0.9, "responsiveness_score": 0.9},
        {"name": "Tanzania", "category": None, "sensitivity_score": 0.9, "responsiveness_score": 0.9},
    ]
    rolled = weighted_rollup(country_ratings)
    flat_avg = (0.2 + 0.9 + 0.9) / 3
    assert rolled["sensitivity_score"] < flat_avg
    assert rolled["responsiveness_score"] < flat_avg


def test_get_regional_slice_injects_crossborder_lens():
    from app import get_regional_slice
    assert get_regional_slice("single") == ""
    slice_multi = get_regional_slice("multi")
    assert "cross-border" in slice_multi.lower()


def test_extract_mpa_context_phase1_is_board_authority():
    from app import extract_mpa_context
    stage1_output = """
    %%%MPA_CONTEXT_START%%%
    is_mpa: true
    phase: Phase 1
    base_instrument: IPF
    regional_mpa: true
    phase_transition_triggers: Utility reaches cost recovery; Grid extended to two regions
    %%%MPA_CONTEXT_END%%%
    """
    parsed = extract_mpa_context(stage1_output)
    assert parsed["error"] is False
    assert parsed["is_mpa"] is True
    assert parsed["base_instrument"] == "IPF"
    assert parsed["regional_mpa"] is True
    assert "Board" in parsed["approval_authority"]
    assert len(parsed["phase_transition_triggers"]) == 2


def test_extract_mpa_context_subsequent_phase_is_rvp():
    from app import extract_mpa_context
    stage1_output = """
    %%%MPA_CONTEXT_START%%%
    is_mpa: true
    phase: Phase 3
    base_instrument: PforR
    regional_mpa: false
    phase_transition_triggers:
    %%%MPA_CONTEXT_END%%%
    """
    parsed = extract_mpa_context(stage1_output)
    assert parsed["is_mpa"] is True
    assert "RVP" in parsed["approval_authority"] or "Management" in parsed["approval_authority"]


def test_mpa_carve_outs_suppress_subsequent_phase_false_positives():
    from app import mpa_carve_outs
    assert mpa_carve_outs("Phase 1") == []
    subsequent = mpa_carve_outs("Phase 3")
    assert "cerc_absence" in subsequent
    assert "esf_program_level" in subsequent
    assert "program_theory_of_change" in subsequent


def test_get_mpa_slice_injects_phase_guidance():
    from app import get_mpa_slice
    assert get_mpa_slice(False) == ""
    slice_mpa = get_mpa_slice(True)
    assert "phase" in slice_mpa.lower()
    assert "MPA" in slice_mpa


def test_analysis_state_activates_multicountry_and_mpa_layers():
    from app import AnalysisState
    state = AnalysisState.from_payload({
        "structured_intake": {
            "instrument": "IPF",
            "doc_type": "PAD",
            "countries": [{"name": "Ethiopia"}, {"name": "Somalia"}, {"name": "Kenya"}],
            "is_mpa": True,
            "phase": "Phase 1",
            "implementing_entity": "TDB",
        }
    })
    assert state.country_scope == "multi"
    assert "multi_country_layer" in state.active_modules
    assert state.is_mpa is True
    assert "mpa_wrapper" in state.active_modules
    assert state.implementing_entity == "TDB"


def test_regional_and_mpa_guides_and_prompts_present():
    import app
    import background_docs
    lens = background_docs.REGIONAL_CROSSBORDER_LENS
    assert "cross-border" in lens.lower()
    assert "spillover" in lens.lower()
    assert "displacement" in lens.lower()
    mpa = background_docs.MPA_MODULE_GUIDE
    assert "phase" in mpa.lower()
    assert "RVP" in mpa
    assert "phase-transition" in mpa.lower() or "phase transition" in mpa.lower()
    assert "advisory" in mpa.lower()
    combined = "\n".join([app.DEFAULT_PROMPTS["1"], app.DEFAULT_PROMPTS["2"], app.DEFAULT_PROMPTS["3"]])
    assert "%%%COUNTRY_SET_START%%%" in combined
    assert "%%%MPA_CONTEXT_START%%%" in combined
    assert "cross-border" in combined.lower()
    assert "regional synthesis" in combined.lower()
    assert "weighted" in combined.lower()


def test_regional_watch_preserved_in_extract_priorities():
    from app import extract_priorities
    payload = {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "Differential fragility across the country set.",
        "responsiveness_summary": "Responsiveness varies by country.",
        "risk_exposure": {"risks_to": "Refugee corridor pressure.", "risks_from": "Cross-border spillover."},
        "regional_watch": ["Track the refugee corridor between Somalia and Kenya as a cross-border priority."],
        "priorities": [
            {
                "title": "Priority 1 - Cross-border displacement corridor",
                "fcv_dimension": "Inclusion",
                "tag": "[S]",
                "refresh_shift": "Shift B: Differentiate",
                "risk_level": "High",
                "priority_scope": "regional",
                "the_gap": "No country owns the refugee-corridor spillover risk.",
                "why_it_matters": "Cross-border displacement is unaddressed by national designs.",
                "actions": [{"document_element": "Regional synthesis", "guidance": "Add a corridor monitoring arrangement.", "suggested_language": "Regional entity tracks displacement flows."}],
                "who_acts": "Regional TTL",
                "when": "Before Board",
                "action_timing": "required-before-board",
                "resources": "Moderate",
                "pad_sections": "Regional synthesis",
                "country_category_relevance": "Conflict-affected Somalia drives the corridor risk.",
                "implementation_note": "Coordinate with the regional implementing entity.",
                "cpf_alignment": None,
            }
        ],
    }
    text = f"%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%"
    parsed = extract_priorities(text)
    assert parsed["error"] is False
    assert parsed["regional_watch"] == payload["regional_watch"]
    assert parsed["priorities"][0]["priority_scope"] == "regional"
