"""Tests for Workstream 6 — MPA governance_level field (QA Issue 6)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_json_block(governance_level_value):
    payload = {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "s",
        "responsiveness_summary": "r",
        "risk_exposure": {"risks_to": "x", "risks_from": "y"},
        "priorities": [{
            "title": "Priority 1 · Phase 2 targeting",
            "fcv_dimension": "Inclusion",
            "tag": "[S]",
            "refresh_shift": "Shift B: Differentiate",
            "risk_level": "Moderate",
            "the_gap": "gap",
            "why_it_matters": "matters",
            "actions": [{"document_element": "PrDO", "guidance": "g", "suggested_language": "s"}],
            "who_acts": "TTL",
            "when": "Preparation",
            "action_timing": "flag-for-preparation",
            "resources": "Minimal",
            "pad_sections": "n/a",
            "implementation_note": "",
            "cpf_alignment": None,
            "governance_level": governance_level_value,
        }],
    }
    return f"%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%"


def test_required_priority_fields_includes_governance_level():
    from app import _REQUIRED_PRIORITY_FIELDS

    assert "governance_level" in _REQUIRED_PRIORITY_FIELDS


def test_extract_priorities_accepts_valid_governance_level():
    from app import extract_priorities

    result = extract_priorities(_make_json_block("Country Phase"))
    assert result["error"] is False
    assert result["priorities"][0]["governance_level"] == "Country Phase"


def test_extract_priorities_accepts_regional_platform_value():
    from app import extract_priorities

    result = extract_priorities(_make_json_block("Regional Platform"))
    assert result["priorities"][0]["governance_level"] == "Regional Platform"


def test_extract_priorities_nulls_out_invalid_governance_level():
    from app import extract_priorities

    result = extract_priorities(_make_json_block("Some Made Up Value"))
    assert result["priorities"][0]["governance_level"] is None


def test_extract_priorities_defaults_missing_governance_level_to_none():
    payload = {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "s",
        "responsiveness_summary": "r",
        "risk_exposure": {"risks_to": "x", "risks_from": "y"},
        "priorities": [{
            "title": "Priority 1 · Non-MPA case",
            "fcv_dimension": "Inclusion",
            "tag": "[S]",
            "refresh_shift": "Shift B: Differentiate",
            "risk_level": "Moderate",
            "the_gap": "gap",
            "why_it_matters": "matters",
            "actions": [],
            "who_acts": "TTL",
            "when": "Preparation",
            "action_timing": "flag-for-preparation",
            "resources": "Minimal",
            "pad_sections": "n/a",
            "implementation_note": "",
            "cpf_alignment": None,
            # governance_level intentionally omitted — non-MPA case
        }],
    }
    text = f"%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%"
    from app import extract_priorities
    result = extract_priorities(text)
    assert result["priorities"][0]["governance_level"] in (None, '')
