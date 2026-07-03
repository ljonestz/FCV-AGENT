"""Instrument-aware metadata hygiene (OPCS follow-up, MAI Vietnam DPF2 review).

MAI systemic finding: change_type / restructuring_level / priority_scope are
AF/restructuring/multi-country concepts with no analogue in a single-tranche
DPF (or plain IPF new lending). The Stage 3 prompt fills non-applicable fields
with the placeholder "Not identified", and both render layers (DOCX + frontend
chips) gate on truthiness — so "Not identified" prints as clutter
("Change: Not identified | Restructuring level: Not identified | Scope: Not
identified") on every DPF priority. extract_priorities() must normalise those
null-equivalent placeholders to None so the render layers omit them, while
preserving genuinely meaningful values (including "Unknown" for AF).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_json_block(change_type, restructuring_level, priority_scope):
    payload = {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "s",
        "responsiveness_summary": "r",
        "risk_exposure": {"risks_to": "x", "risks_from": "y"},
        "priorities": [{
            "title": "Priority 1 · Strengthen the PSIA",
            "fcv_dimension": "Inclusion",
            "tag": "[S]",
            "refresh_shift": "Shift B: Differentiate",
            "risk_level": "High",
            "the_gap": "gap",
            "why_it_matters": "matters",
            "actions": [{"document_element": "PSIA", "guidance": "g", "suggested_language": "s"}],
            "who_acts": "TTL",
            "when": "Preparation",
            "action_timing": "next-series",
            "resources": "Minimal",
            "pad_sections": "n/a",
            "implementation_note": "",
            "cpf_alignment": None,
            "change_type": change_type,
            "restructuring_level": restructuring_level,
            "priority_scope": priority_scope,
        }],
    }
    return f"%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%"


def test_dpf_placeholder_metadata_normalised_to_none():
    """A DPF priority with 'Not identified' placeholders -> None (chips omitted)."""
    from app import extract_priorities

    result = extract_priorities(_make_json_block(
        "Not identified", "Not identified", "Not identified"))
    assert result["error"] is False
    pr = result["priorities"][0]
    assert pr["change_type"] is None
    assert pr["restructuring_level"] is None
    assert pr["priority_scope"] is None


def test_other_null_equivalents_normalised():
    from app import extract_priorities

    for placeholder in ("N/A", "None", "not applicable", "", "  Not Identified  "):
        result = extract_priorities(_make_json_block(placeholder, placeholder, placeholder))
        pr = result["priorities"][0]
        assert pr["change_type"] is None, placeholder
        assert pr["restructuring_level"] is None, placeholder
        assert pr["priority_scope"] is None, placeholder


def test_meaningful_af_metadata_preserved():
    """An AF priority keeps its real values, including 'Unknown' restructuring level."""
    from app import extract_priorities

    result = extract_priorities(_make_json_block(
        "AF scale-up / top-up", "Unknown", "mid-cycle"))
    pr = result["priorities"][0]
    assert pr["change_type"] == "AF scale-up / top-up"
    assert pr["restructuring_level"] == "Unknown"
    assert pr["priority_scope"] == "mid-cycle"


def test_multicountry_scope_preserved():
    from app import extract_priorities

    result = extract_priorities(_make_json_block(
        "Not identified", "Not identified", "regional"))
    pr = result["priorities"][0]
    assert pr["change_type"] is None
    assert pr["priority_scope"] == "regional"
