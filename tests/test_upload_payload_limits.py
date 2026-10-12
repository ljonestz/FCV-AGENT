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


def test_upload_cap_is_env_configurable_and_default_is_raised():
    # Default must be a meaningful bump above the old hard 50 MB free-tier value
    # and must drive the Flask request cap one-to-one.
    assert app_module.MAX_UPLOAD_MB >= 100
    assert (
        app_module.app.config["MAX_CONTENT_LENGTH"]
        == app_module.MAX_UPLOAD_MB * 1024 * 1024
    )


def test_sector_lenses_publishes_effective_upload_cap():
    # The frontend pre-submit size warning reads this value so it cannot drift
    # from the backend cap even when IT overrides MAX_UPLOAD_MB by env.
    with app_module.app.test_client() as client:
        response = client.get("/api/sector-lenses")

    assert response.status_code == 200
    body = response.get_json()
    assert body["max_upload_mb"] == app_module.MAX_UPLOAD_MB
