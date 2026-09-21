"""Phase 1 mid-cycle overlay regression tests."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_extract_change_types_parses_multilabel_block_and_level():
    from app import extract_change_types

    stage1_output = """
    %%%CHANGE_TYPE_START%%%
    change_types: PDO change; results framework change; closing date extension; reallocation
    restructuring_level: Level 2
    rationale: The paper revises the PDO and RF and extends the closing date.
    %%%CHANGE_TYPE_END%%%
    """

    parsed = extract_change_types(stage1_output)

    assert parsed["error"] is False
    assert parsed["restructuring_level"] == "Level 2"
    assert parsed["restructuring_authority"] == "RVP / CD-DD"
    assert "PDO change" in parsed["change_types"]
    assert "Results framework change" in parsed["change_types"]
    assert "Closing-date extension" in parsed["change_types"]
    assert "Reallocation" in parsed["change_types"]


def test_derive_restructuring_level_keeps_pdo_change_at_level_2():
    from app import derive_restructuring_level

    level = derive_restructuring_level(["PDO change"])

    assert level["level"] == "Level 2"
    assert level["authority"] == "RVP / CD-DD"
    assert "PDO" in level["reason"]


def test_derive_restructuring_level_identifies_narrow_level_1_cases():
    from app import derive_restructuring_level

    level = derive_restructuring_level(["Alternative Procurement Arrangements"])

    assert level["level"] == "Level 1"
    assert level["authority"] == "Board"


def test_mid_cycle_temporal_guardrail_is_live_project_tier1_anchored():
    from app import _build_temporal_guardrail

    guardrail = _build_temporal_guardrail(
        {
            "approval_date": "2019-05-30",
            "closing_date": "2027-12-31",
            "safeguards_framework": "ESF",
            "other_temporal_markers": "Level 2 restructuring paper dated May 2026",
            "error": False,
        },
        "Restructuring",
    )

    assert "MID-CYCLE LIVE-PROJECT FRAMING" in guardrail
    assert "Tier-1" in guardrail
    assert "Implementation Progress & Status" in guardrail
    assert "Do NOT invent implementation facts" in guardrail
    assert "Use PREPARATION phase framing throughout" not in guardrail


def test_mid_cycle_registry_and_state_specialize_af_and_restructuring():
    from app import AnalysisState, select_module

    module = select_module(doc_type="AF", instrument="IPF", country_scope="single")
    assert module.key == ("AF", "IPF", "single")
    assert "mid_cycle_overlay" in module.guardrails
    assert "change_type" in module.output_fields

    state = AnalysisState.from_payload({
        "structured_intake": {
            "instrument": "IPF",
            "doc_type": "Restructuring",
            "countries": [{"name": "Suriname"}],
            "change_types": ["PDO change"],
            "restructuring_level": "Level 2",
        }
    })
    assert state.change_types == ["PDO change"]
    assert state.restructuring_level == "Level 2"
    assert "mid_cycle_overlay" in state.active_modules


def test_mid_cycle_priority_fields_and_watch_section_are_preserved():
    from app import extract_priorities

    payload = {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "The restructuring is moderately conflict-sensitive.",
        "responsiveness_summary": "Responsiveness remains limited.",
        "risk_exposure": {"risks_to": "Access disruption in Mopti.", "risks_from": "Exclusion risk in Gao."},
        "mid_cycle_watch": [
            "Verify whether the revised RF still captures displaced households in Mopti."
        ],
        "priorities": [
            {
                "title": "Priority 1 - Preserve FCV targeting in Mopti RF revision",
                "fcv_dimension": "Inclusion",
                "tag": "[S]",
                "refresh_shift": "Shift B: Differentiate",
                "risk_level": "High",
                "change_type": "Results framework change",
                "restructuring_level": "Level 2",
                "priority_scope": "mid-cycle",
                "the_gap": "The revised RF for Mopti and Gao drops displaced-household tracking.",
                "why_it_matters": "Dropping IDP tracking weakens grievance monitoring in Mopti.",
                "actions": [
                    {
                        "document_element": "Results Framework",
                        "guidance": "Restore IDP-disaggregated indicators for Mopti and Gao.",
                        "suggested_language": "Track displaced households receiving services in Mopti and Gao."
                    }
                ],
                "who_acts": "TTL",
                "when": "Before restructuring package finalization",
                "action_timing": "required-before-board",
                "resources": "Minimal",
                "pad_sections": "Results Framework",
                "country_category_relevance": "Conflict-affected access constraints require disaggregated tracking.",
                "implementation_note": "Discuss with OPCS as an advisory procedural point.",
                "cpf_alignment": None,
            }
        ],
    }
    text = f"%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%"

    parsed = extract_priorities(text, document_type="Restructuring")

    assert parsed["error"] is False
    assert parsed["mid_cycle_watch"] == payload["mid_cycle_watch"]
    priority = parsed["priorities"][0]
    assert priority["change_type"] == "Results framework change"
    assert priority["restructuring_level"] == "Level 2"
    assert priority["priority_scope"] == "mid-cycle"


def test_mid_cycle_guides_and_prompts_are_injected():
    import app
    import background_docs

    assert "PDO change" in background_docs.RESTRUCTURING_GUIDE
    assert "Level 2" in background_docs.RESTRUCTURING_GUIDE
    assert "Alternative Procurement Arrangements" in background_docs.RESTRUCTURING_GUIDE
    assert "MS+" in background_docs.AF_GUIDE
    assert "advisory" in background_docs.AF_GUIDE.lower()

    combined_prompts = "\n".join([
        app.DEFAULT_PROMPTS["1"],
        app.DEFAULT_PROMPTS["2"],
        app.DEFAULT_PROMPTS["3"],
    ])
    assert "%%%CHANGE_TYPE_START%%%" in combined_prompts
    assert "two linked checks" in combined_prompts
    assert "context-change since approval" in combined_prompts
    assert "Mid-Cycle FCV Watch" in combined_prompts
    assert "change_type" in combined_prompts
