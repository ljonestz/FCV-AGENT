"""Phase 2 DPF/DPO instrument-module regression tests.

DPF analysis is instrument-true: the unit of analysis is prior actions (not
components), the harm screen is PSIA + the conflict-exception (Paragraph 38-39)
check, and ESF/ESCP/DLI do not apply. Procedural language stays advisory-only.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_extract_prior_actions_parses_block():
    from app import extract_prior_actions

    stage1_output = """
    %%%PRIOR_ACTIONS_START%%%
    financing_source: IDA
    series_position: Programmatic (operation 2 of 3)
    cat_ddo: false
    prior_actions: Remove fuel subsidy and adopt compensatory cash transfer; Restructure the electricity SOE; Adopt a new public financial management law
    indicative_triggers: Publish audited SOE accounts; Expand cash transfer registry to conflict-affected regions
    %%%PRIOR_ACTIONS_END%%%
    """

    parsed = extract_prior_actions(stage1_output)

    assert parsed["error"] is False
    assert parsed["financing_source"] == "IDA"
    assert parsed["is_programmatic"] is True
    assert parsed["cat_ddo"] is False
    assert len(parsed["prior_actions"]) == 3
    assert "Restructure the electricity SOE" in parsed["prior_actions"]
    assert len(parsed["indicative_triggers"]) == 2


def test_extract_prior_actions_detects_cat_ddo_and_ibrd():
    from app import extract_prior_actions

    stage1_output = """
    %%%PRIOR_ACTIONS_START%%%
    financing_source: IBRD
    series_position: Standalone
    cat_ddo: true
    prior_actions: Establish a national disaster risk financing framework
    indicative_triggers:
    %%%PRIOR_ACTIONS_END%%%
    """

    parsed = extract_prior_actions(stage1_output)

    assert parsed["error"] is False
    assert parsed["financing_source"] == "IBRD"
    assert parsed["is_programmatic"] is False
    assert parsed["cat_ddo"] is True
    assert parsed["indicative_triggers"] == []


def test_extract_prior_actions_handles_missing_block():
    from app import extract_prior_actions

    parsed = extract_prior_actions("No prior action block here.")
    assert parsed["error"] is True
    assert parsed["prior_actions"] == []
    assert parsed["cat_ddo"] is False


def test_dpf_rubric_scores_through_generic_scorer():
    from app import DPF_RUBRIC, score_sr

    # DPF rubric is prior-action / PSIA centred, not "% of 12 OST recs".
    assert "prior_action_conflict_sensitivity" in DPF_RUBRIC.dimensions
    assert "psia_adequacy" in DPF_RUBRIC.dimensions
    assert "conflict_exception_adequacy" in DPF_RUBRIC.dimensions

    scored = score_sr(DPF_RUBRIC, {
        "addressed": 3, "partial": 1, "weak": 0, "not_addressed": 1,
        "responsiveness_evidence": "adequate",
    })
    assert scored["rubric"] == DPF_RUBRIC.name
    assert scored["sensitivity_rating"]
    assert scored["responsiveness_rating"]


def test_dpf_module_registry_and_select_module():
    from app import DPF_RUBRIC, select_module

    module = select_module(doc_type="PAD", instrument="DPO", country_scope="single")
    assert module.key == ("PAD", "DPO", "single")
    assert module.rubric is DPF_RUBRIC
    assert module.legacy_instrument == "DPO"
    assert "dpf_prior_action_spine" in module.guardrails
    assert "dpf_no_esf_escp_dli" in module.guardrails
    assert "prior_action" in module.output_fields
    assert "dpf_watch" in module.output_fields


def test_analysis_state_carries_dpf_fields():
    from app import AnalysisState

    state = AnalysisState.from_payload({
        "structured_intake": {
            "instrument": "DPO",
            "doc_type": "PAD",
            "countries": [{"name": "Chad"}],
            "financing_source": "IDA",
            "series_position": "Programmatic (operation 1 of 3)",
            "cat_ddo": False,
        }
    })
    assert state.financing_source == "IDA"
    assert state.series_position == "Programmatic (operation 1 of 3)"
    assert state.cat_ddo is False
    assert "dpf_module" in state.active_modules


def test_get_dpf_slice_injects_prior_action_guidance():
    from app import get_dpf_slice

    slice_ipf = get_dpf_slice("IPF")
    assert slice_ipf == ""

    slice_dpf = get_dpf_slice("DPO")
    assert "prior action" in slice_dpf.lower()
    assert "OPS5.02-POL.120" in slice_dpf


def test_dpf_guides_and_prompts_are_present():
    import app
    import background_docs

    guide = background_docs.DPF_MODULE_GUIDE
    assert "prior action" in guide.lower()
    assert "OPS5.02-POL.120" in guide
    assert "OP 2.30" in guide
    assert "PSIA" in guide
    assert "macroeconomic" in guide.lower()
    assert "Paragraph 38" in guide
    assert "Cat DDO" in guide
    assert "IBRD" in guide and "IDA" in guide
    assert "advisory" in guide.lower()

    checklist = background_docs.DPF_POLICY_AREA_CHECKLIST
    assert "subsid" in checklist.lower()
    assert "social protection" in checklist.lower()

    combined = "\n".join([
        app.DEFAULT_PROMPTS["1"],
        app.DEFAULT_PROMPTS["2"],
        app.DEFAULT_PROMPTS["3"],
    ])
    assert "%%%PRIOR_ACTIONS_START%%%" in combined
    assert "prior action" in combined.lower()
    assert "macroeconomic" in combined.lower()
    assert "IMF" in combined
    assert "PSIA" in combined
    assert "Paragraph 38" in combined
    assert "Cat DDO" in combined


def test_dpf_watch_preserved_in_extract_priorities():
    from app import extract_priorities

    payload = {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "The operation's prior actions are moderately conflict-sensitive.",
        "responsiveness_summary": "Responsiveness remains limited.",
        "risk_exposure": {"risks_to": "Fiscal stress in N'Djamena.", "risks_from": "Subsidy removal grievance."},
        "dpf_watch": [
            "Verify whether the IMF programme remains on track before the second operation.",
            "Confirm the cash-transfer registry reaches conflict-affected regions.",
        ],
        "priorities": [
            {
                "title": "Priority 1 - Sequence subsidy removal with safety nets",
                "fcv_dimension": "Do No Harm",
                "tag": "[S]",
                "refresh_shift": "Shift A: Anticipate",
                "risk_level": "High",
                "the_gap": "The fuel subsidy prior action lacks a sequenced compensatory transfer.",
                "why_it_matters": "Unmitigated price shocks have historically driven unrest.",
                "actions": [
                    {
                        "document_element": "Policy Matrix / Prior Action 1",
                        "guidance": "Sequence the compensatory cash transfer ahead of subsidy removal.",
                        "suggested_language": "Cash transfer operational in affected regions prior to subsidy removal.",
                    }
                ],
                "who_acts": "TTL",
                "when": "Before Board",
                "action_timing": "required-before-board",
                "resources": "Moderate",
                "pad_sections": "Program Description; Poverty and Social Impacts",
                "country_category_relevance": "Conflict-affected fiscal stress raises grievance risk.",
                "implementation_note": "Discuss macro framing with the country economist.",
                "cpf_alignment": None,
            }
        ],
    }
    text = f"%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%"

    parsed = extract_priorities(text)

    assert parsed["error"] is False
    assert parsed["dpf_watch"] == payload["dpf_watch"]
