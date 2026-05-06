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
