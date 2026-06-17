"""Phase 3 P4R (Program-for-Results) instrument-module regression tests.

P4R analysis is instrument-true: the unit of analysis is DLIs + verification
protocols (disbursed through a government program), the harm screen is ESSA/ESMS
country systems + GRM functionality (not ESF/ESCP), and the signature FCV finding
is disbursement under conflict (IVA verification access + disbursement cliff).
Procedural / instrument-feasibility language stays advisory-only.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_extract_dlis_parses_block():
    from app import extract_dlis

    stage1_output = """
    %%%DLIS_START%%%
    ipf_component: false
    program_boundary: National electricity access program excluding conflict-affected Tigray
    fcs_status: Fragile State
    dlis: Households connected to the grid; Mini-grids operational in rural woredas; Utility cost-recovery tariff adopted
    verification: Independent Verification Agent verifies connection counts from utility MIS and field spot-checks
    %%%DLIS_END%%%
    """

    parsed = extract_dlis(stage1_output)

    assert parsed["error"] is False
    assert parsed["ipf_component"] is False
    assert parsed["fcs_status"] == "Fragile State"
    assert "conflict-affected Tigray" in parsed["program_boundary"]
    assert len(parsed["dlis"]) == 3
    assert "Mini-grids operational in rural woredas" in parsed["dlis"]
    assert "Independent Verification Agent" in parsed["verification"]


def test_extract_dlis_detects_ipf_component():
    from app import extract_dlis

    stage1_output = """
    %%%DLIS_START%%%
    ipf_component: true
    program_boundary: Energy access program with a technical-assistance IPF window
    fcs_status: Conflict
    dlis: Grid connections verified
    verification: IVA spot-checks
    %%%DLIS_END%%%
    """

    parsed = extract_dlis(stage1_output)

    assert parsed["error"] is False
    assert parsed["ipf_component"] is True
    assert parsed["fcs_status"] == "Conflict"


def test_extract_dlis_handles_missing_block():
    from app import extract_dlis

    parsed = extract_dlis("No DLI block here.")
    assert parsed["error"] is True
    assert parsed["dlis"] == []
    assert parsed["ipf_component"] is False


def test_p4r_rubric_scores_through_generic_scorer():
    from app import P4R_RUBRIC, score_sr

    assert "dli_conflict_sensitivity" in P4R_RUBRIC.dimensions
    assert "dli_verifiability_iva_access" in P4R_RUBRIC.dimensions
    assert "essa_esms_adequacy" in P4R_RUBRIC.dimensions

    scored = score_sr(P4R_RUBRIC, {
        "addressed": 4, "partial": 1, "weak": 0, "not_addressed": 1,
        "responsiveness_evidence": "partial",
    })
    assert scored["rubric"] == P4R_RUBRIC.name
    assert scored["sensitivity_rating"]
    assert scored["responsiveness_rating"]


def test_p4r_module_registry_and_select_module():
    from app import P4R_RUBRIC, select_module

    module = select_module(doc_type="PAD", instrument="PforR", country_scope="single")
    assert module.key == ("PAD", "PFORR", "single")
    assert module.rubric is P4R_RUBRIC
    assert module.legacy_instrument == "PforR"
    assert "p4r_dli_verification_spine" in module.guardrails
    assert "p4r_no_esf_escp" in module.guardrails
    assert "dli" in module.output_fields
    assert "p4r_watch" in module.output_fields


def test_analysis_state_carries_p4r_fields():
    from app import AnalysisState

    state = AnalysisState.from_payload({
        "structured_intake": {
            "instrument": "PforR",
            "doc_type": "PAD",
            "countries": [{"name": "Ethiopia"}],
            "has_ipf_component": True,
            "dlis": ["Households connected", "Tariff adopted"],
        }
    })
    assert state.has_ipf_component is True
    assert state.dlis == ["Households connected", "Tariff adopted"]
    assert "p4r_module" in state.active_modules


def test_get_p4r_slice_injects_dli_guidance():
    from app import get_p4r_slice

    assert get_p4r_slice("IPF") == ""

    slice_p4r = get_p4r_slice("PforR")
    assert "DLI" in slice_p4r
    assert "OPS5.09" in slice_p4r
    assert "IVA" in slice_p4r


def test_p4r_guides_and_prompts_are_present():
    import app
    import background_docs

    guide = background_docs.P4R_MODULE_GUIDE
    assert "DLI" in guide
    assert "OPS5.09" in guide
    assert "OP 7.30" in guide
    assert "ESSA" in guide and "ESMS" in guide
    assert "GRM" in guide
    assert "Independent Verification Agent" in guide or "IVA" in guide
    assert "disbursement" in guide.lower()
    assert "advisory" in guide.lower()

    combined = "\n".join([
        app.DEFAULT_PROMPTS["1"],
        app.DEFAULT_PROMPTS["2"],
        app.DEFAULT_PROMPTS["3"],
    ])
    assert "%%%DLIS_START%%%" in combined
    assert "DLI" in combined
    assert "verification" in combined.lower()
    assert "disbursement" in combined.lower()
    assert "IVA" in combined
    assert "ESSA" in combined


def test_p4r_watch_preserved_in_extract_priorities():
    from app import extract_priorities

    payload = {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "DLI verification access is the binding constraint.",
        "responsiveness_summary": "Responsiveness is limited.",
        "risk_exposure": {"risks_to": "Verification access in Tigray.", "risks_from": "Exclusion of contested woredas."},
        "p4r_watch": [
            "Confirm the IVA can reach conflict-affected woredas before DLI 2 disburses.",
            "Watch the disbursement-cliff risk if results stall under access disruption.",
        ],
        "priorities": [
            {
                "title": "Priority 1 - Make DLI verification robust to access disruption",
                "fcv_dimension": "Do No Harm",
                "tag": "[S]",
                "refresh_shift": "Shift A: Anticipate",
                "risk_level": "High",
                "the_gap": "The verification protocol assumes IVA access to all woredas.",
                "why_it_matters": "If the IVA cannot verify in contested areas, financing does not flow.",
                "actions": [
                    {
                        "document_element": "Verification Protocol / DLI 2",
                        "guidance": "Add remote-verification fallbacks for contested woredas.",
                        "suggested_language": "Third-party monitoring substitutes for field verification where access is constrained.",
                    }
                ],
                "who_acts": "TTL",
                "when": "Before Board",
                "action_timing": "required-before-board",
                "resources": "Moderate",
                "pad_sections": "DLIs and Verification Protocols; ESSA",
                "country_category_relevance": "Conflict-affected access constraints threaten disbursement.",
                "implementation_note": "Discuss IVA arrangements with the verification team.",
                "cpf_alignment": None,
            }
        ],
    }
    text = f"%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%"

    parsed = extract_priorities(text)

    assert parsed["error"] is False
    assert parsed["p4r_watch"] == payload["p4r_watch"]
