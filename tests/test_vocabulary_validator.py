"""Programmatic instrument-vocabulary validator tests (Workstream 2)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_validator_flags_escp_language_for_pforr():
    from app import validate_instrument_vocabulary

    text = "The ESCP should include a time-bound SEA/SH Action Plan under ESS4."
    violations = validate_instrument_vocabulary(text, "PforR")
    assert "ESCP" in violations
    assert "ESS4" in violations


def test_validator_flags_pad_language_for_dpf():
    from app import validate_instrument_vocabulary

    text = "The ESCP commitment should be reflected in the SEP."
    violations = validate_instrument_vocabulary(text, "DPO")
    assert "ESCP" in violations
    assert "SEP" in violations or "Stakeholder Engagement Plan" in violations


def test_validator_passes_clean_pforr_output():
    from app import validate_instrument_vocabulary

    text = "The ESSA identifies SEA/SH risk under Core Principle #6; the PAP commits to strengthening GRM access via the ESMS."
    violations = validate_instrument_vocabulary(text, "PforR")
    assert violations == []


def test_validator_passes_clean_dpf_output():
    from app import validate_instrument_vocabulary

    text = "The PSIA should model distributional impacts of the subsidy reform in the Program Document."
    violations = validate_instrument_vocabulary(text, "DPO")
    assert violations == []


def test_validator_is_a_noop_for_ipf():
    from app import validate_instrument_vocabulary

    text = "The ESCP commits to a SEA/SH Action Plan under ESS4."
    violations = validate_instrument_vocabulary(text, "IPF")
    assert violations == []


def test_validator_handles_empty_and_unknown_instrument():
    from app import validate_instrument_vocabulary

    assert validate_instrument_vocabulary("", "PforR") == []
    assert validate_instrument_vocabulary("some text", "") == []
    assert validate_instrument_vocabulary("some text", "Unknown") == []


def test_validator_does_not_flag_common_words_containing_sep():
    """Word-boundary safety: 'SEP' must not match inside 'separate'/'September'."""
    from app import validate_instrument_vocabulary

    text = "The reform should be sequenced separately in September, per the ESSA."
    violations = validate_instrument_vocabulary(text, "PforR")
    assert violations == []


def test_repair_calls_model_once_and_returns_clean_text(monkeypatch):
    from app import repair_vocabulary_violations
    import app as app_module

    calls = {"count": 0}

    class _FakeContent:
        def __init__(self, text):
            self.text = text

    class _FakeResponse:
        def __init__(self, text):
            self.content = [_FakeContent(text)]

    class _FakeMessages:
        def create(self, **kwargs):
            calls["count"] += 1
            return _FakeResponse(
                "The ESSA identifies SEA/SH risk under Core Principle #6; "
                "the PAP commits to strengthening GRM access via the ESMS."
            )

    class _FakeClient:
        messages = _FakeMessages()

    monkeypatch.setattr(app_module, "get_client", lambda: _FakeClient())

    dirty_text = "The ESCP should include a time-bound SEA/SH Action Plan under ESS4."
    violations = ["ESCP", "ESS4"]
    repaired = repair_vocabulary_violations(dirty_text, "PforR", violations, stage_num=2)

    assert calls["count"] == 1
    assert "ESCP" not in repaired
    assert "ESS4" not in repaired
    assert "ESSA" in repaired


def test_repair_falls_back_to_scrub_when_model_repair_still_dirty(monkeypatch):
    from app import repair_vocabulary_violations
    import app as app_module

    class _FakeContent:
        def __init__(self, text):
            self.text = text

    class _FakeResponse:
        def __init__(self, text):
            self.content = [_FakeContent(text)]

    class _FakeMessages:
        def create(self, **kwargs):
            # Simulate the model failing to remove the banned term.
            return _FakeResponse("The ESCP should include a time-bound SEA/SH Action Plan.")

    class _FakeClient:
        messages = _FakeMessages()

    monkeypatch.setattr(app_module, "get_client", lambda: _FakeClient())

    dirty_text = "The ESCP should include a time-bound SEA/SH Action Plan."
    repaired = repair_vocabulary_violations(dirty_text, "PforR", ["ESCP"], stage_num=2)

    # Deterministic scrub must remove the remaining banned term even when
    # the model repair call did not.
    assert "ESCP" not in repaired


def test_repair_never_raises_on_api_failure(monkeypatch):
    from app import repair_vocabulary_violations
    import app as app_module

    def _boom():
        raise RuntimeError("API unavailable")

    monkeypatch.setattr(app_module, "get_client", _boom)

    dirty_text = "The ESCP should include a time-bound SEA/SH Action Plan."
    # Must not raise — falls back to deterministic scrub of the original text.
    repaired = repair_vocabulary_violations(dirty_text, "PforR", ["ESCP"], stage_num=2)
    assert "ESCP" not in repaired
