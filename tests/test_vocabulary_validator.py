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


def test_repair_makes_no_llm_call_and_returns_clean_text(monkeypatch):
    """Repair is a deterministic scrub only — it must NOT call the LLM.

    The previous implementation made a blocking, non-streaming rewrite call
    after the SSE stream had ended; for PforR/DPO (whose long Stage 2/3 outputs
    always leak ESS/SEP vocabulary) that silent 1.5-3 min gap pushed the total
    request past the frontend abort budget, timing out Stage 2 and Stage 3.
    """
    from app import repair_vocabulary_violations
    import app as app_module

    calls = {"count": 0}

    def _boom_client():
        calls["count"] += 1
        raise AssertionError("repair must not call the LLM")

    monkeypatch.setattr(app_module, "get_client", _boom_client)

    dirty_text = "The ESCP should include a time-bound SEA/SH Action Plan under ESS4."
    violations = ["ESCP", "ESS4"]
    repaired = repair_vocabulary_violations(dirty_text, "PforR", violations, stage_num=2)

    assert calls["count"] == 0
    assert "ESCP" not in repaired
    assert "ESS4" not in repaired


def test_repair_scrubs_all_banned_terms_including_uncovered_ess(monkeypatch):
    """Every banned term must be scrubbed, including ESS1/3/5-10 and SEP.

    The scrub map previously only covered ESS2/ESS4, so a PforR output citing
    e.g. ESS1, ESS6 or ESS10 would pass through the scrub un-repaired.
    """
    from app import repair_vocabulary_violations, validate_instrument_vocabulary
    import app as app_module

    monkeypatch.setattr(app_module, "get_client",
                        lambda: (_ for _ in ()).throw(AssertionError("no LLM")))

    for instrument in ("PforR", "DPO"):
        dirty = ("Under ESS1, ESS2, ESS3, ESS4, ESS5, ESS6, ESS7, ESS8, ESS9 and "
                 "ESS10 the ESCP and the SEP (Stakeholder Engagement Plan) should "
                 "be strengthened via the Environmental and Social Commitment Plan.")
        violations = validate_instrument_vocabulary(dirty, instrument)
        assert violations  # sanity: dirty text does violate
        repaired = repair_vocabulary_violations(dirty, instrument, violations, stage_num=3)
        assert validate_instrument_vocabulary(repaired, instrument) == [], instrument


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
