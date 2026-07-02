"""Ensure Stage 2/3 vocabulary repair is wired into extract/parsing pipeline.

These are unit-level tests against the validator+repair functions combined
with extract_priorities()/extract_under_hood(), not full HTTP round-trips
(the SSE streaming route requires a live Anthropic connection to test
end-to-end; that is exercised by the manual QA re-run instead).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_repaired_stage3_output_still_parses_as_valid_json(monkeypatch):
    import json
    from app import validate_instrument_vocabulary, repair_vocabulary_violations, extract_priorities
    import app as app_module

    dirty_json_block = json.dumps({
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "s",
        "responsiveness_summary": "r",
        "risk_exposure": {"risks_to": "x", "risks_from": "y"},
        "priorities": [{
            "title": "Strengthen SEA/SH provisions",
            "fcv_dimension": "Do No Harm",
            "tag": "[S]",
            "refresh_shift": "Shift A: Anticipate",
            "risk_level": "High",
            "the_gap": "The ESCP does not commit to a SEA/SH Action Plan under ESS4.",
            "why_it_matters": "SEA/SH risk is elevated in this conflict setting.",
            "actions": [{"document_element": "ESCP", "guidance": "Add a commitment.", "suggested_language": ""}],
            "who_acts": "TTL",
            "when": "Before Board",
            "action_timing": "required-before-board",
            "resources": "Moderate",
            "pad_sections": "n/a",
            "implementation_note": "",
            "cpf_alignment": None,
        }],
    })
    dirty_text = f"%%%JSON_START%%%\n{dirty_json_block}\n%%%JSON_END%%%"

    violations = validate_instrument_vocabulary(dirty_text, "PforR")
    assert violations  # ESCP/ESS4 present

    class _FakeContent:
        def __init__(self, text):
            self.text = text

    class _FakeResponse:
        def __init__(self, text):
            self.content = [_FakeContent(text)]

    class _FakeMessages:
        def create(self, **kwargs):
            cleaned_block = dirty_json_block.replace("ESCP", "the PAP").replace("ESS4", "ESSA Core Principle #6")
            return _FakeResponse(f"%%%JSON_START%%%\n{cleaned_block}\n%%%JSON_END%%%")

    class _FakeClient:
        messages = _FakeMessages()

    monkeypatch.setattr(app_module, "get_client", lambda: _FakeClient())

    repaired = repair_vocabulary_violations(dirty_text, "PforR", violations, stage_num=3)
    assert validate_instrument_vocabulary(repaired, "PforR") == []

    parsed = extract_priorities(repaired)
    assert parsed["error"] is False
    assert len(parsed["priorities"]) == 1
