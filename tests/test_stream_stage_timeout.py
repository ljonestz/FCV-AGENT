"""Regression tests for backend SSE stage streaming."""
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app


class _HangingTextStream:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    @property
    def text_stream(self):
        while True:
            time.sleep(10)
            yield ""


class _Messages:
    def stream(self, **_kwargs):
        return _HangingTextStream()


class _HangingClient:
    messages = _Messages()


def test_stream_stage_times_out_when_model_stream_hangs(monkeypatch):
    monkeypatch.setattr(app, "get_client", lambda: _HangingClient())

    stream = app._stream_stage(
        [{"role": "user", "content": "stage 3 prompt"}],
        max_tokens=20000,
        stage_num=3,
        max_seconds=0.02,
        keepalive_interval=0.005,
    )

    with pytest.raises(TimeoutError, match="Stage 3 timed out"):
        list(stream)


def test_is_transient_stream_error_matches_overloaded_but_not_hard_errors():
    """Anthropic 'Overloaded' (529) surfaces as a mid-stream error whose string
    contains 'overloaded'; it must be treated as retryable, while genuine client
    errors (bad JSON, auth) must not be."""
    assert app._is_transient_stream_error(
        Exception("{'type': 'error', 'error': {'type': 'overloaded_error', 'message': 'Overloaded'}}")
    )
    assert app._is_transient_stream_error(Exception("Internal server error (500)"))
    # Non-transient: do not retry
    assert not app._is_transient_stream_error(ValueError("malformed json in diagnostic"))
    assert not app._is_transient_stream_error(KeyError("missing field"))


def test_transient_error_friendly_message_is_user_safe():
    msg = app._transient_stream_user_message(
        Exception("{'type': 'overloaded_error', 'message': 'Overloaded'}")
    )
    assert "overloaded" in msg.lower()
    assert "retry" in msg.lower()
    # A non-transient error passes through unchanged (raw detail preserved for debugging).
    raw = "some other failure"
    assert app._transient_stream_user_message(Exception(raw)) == raw
