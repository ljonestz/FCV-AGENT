"""An incomplete Stage 3 response remains a diagnosable failed run."""

import app


def test_stage3_parse_failure_log_records_stop_metadata_without_response_text(caplog):
    app._stream_stage._last_stop_reason = "max_tokens"
    app._stream_stage._last_output_tokens = 32000
    raw = '%%%JSON_START%%%\n{"secret": "private response text'

    with caplog.at_level("WARNING"):
        app.log_stage3_parse_failure("assessment-123", raw, {"error": True}, 32000)

    message = caplog.records[-1].message
    assert "assessment_id=assessment-123" in message
    assert "stop_reason=max_tokens" in message
    assert "output_tokens=32000" in message
    assert "max_tokens=32000" in message
    assert "json_start=True json_end=False" in message
    assert "private response text" not in message
