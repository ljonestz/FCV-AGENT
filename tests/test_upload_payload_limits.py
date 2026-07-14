"""Regression tests for oversized upload payload handling."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module


def test_run_express_returns_413_when_json_payload_exceeds_limit(monkeypatch):
    monkeypatch.setitem(app_module.app.config, "MAX_CONTENT_LENGTH", 256)

    payload = {
        "documents": [
            {
                "name": "large.pdf",
                "type": "pdf",
                "docRole": "primary",
                "content": "x" * 1024,
            }
        ]
    }

    with app_module.app.test_client() as client:
        response = client.post(
            "/api/run-express",
            data=json.dumps(payload),
            content_type="application/json",
        )

    assert response.status_code == 413
    body = response.get_json()
    assert "too large" in body["error"].lower()
    assert body["max_mb"] == 0
