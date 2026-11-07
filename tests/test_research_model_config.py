"""Research-only model routing tests; all provider calls are local fakes."""

import json
from types import SimpleNamespace

import pytest

import app as app_module


SONNET = "claude-sonnet-5-5"
HAIKU = "claude-haiku-5-5"


class _RecordingClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []
        self.beta = SimpleNamespace(
            messages=SimpleNamespace(create=self._create),
        )

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return next(self.responses)


def _text_response(text="research note", stop_reason="end_turn"):
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text, citations=[])],
        stop_reason=stop_reason,
    )


def _climate_bundle():
    return {
        "status": "complete",
        "sources": [],
        "claims": [],
        "coverage_countries": [],
        "attempts": 0,
    }


def _patch_climate_acceptance(monkeypatch):
    bundle = _climate_bundle()
    monkeypatch.setattr(
        app_module,
        "extract_climate_research_bundle",
        lambda text: (text, dict(bundle)),
    )
    monkeypatch.setattr(
        app_module,
        "verify_climate_research_claims",
        lambda result, provider_content: result,
    )
    monkeypatch.setattr(
        app_module,
        "climate_research_evidence_gate",
        lambda result: {"ok": True, "bundle": result, "code": "ok"},
    )
    monkeypatch.setattr(
        app_module, "log_climate_research_summary", lambda *args, **kwargs: None,
    )


@pytest.mark.parametrize(
    ("configured_model", "expected_model", "thinking"),
    [
        (None, SONNET, None),
        (SONNET, SONNET, None),
        (HAIKU, HAIKU, {"type": "disabled"}),
    ],
)
def test_core_research_uses_default_or_exact_override(
    monkeypatch, configured_model, expected_model, thinking,
):
    if configured_model is None:
        monkeypatch.delenv("FCV_RESEARCH_MODEL", raising=False)
    else:
        monkeypatch.setenv("FCV_RESEARCH_MODEL", configured_model)
    monkeypatch.setattr(
        app_module,
        "normalize_core_research_response",
        lambda *args, **kwargs: {"brief": "ok", "sources": []},
    )
    client = _RecordingClient([SimpleNamespace(content=[])])

    app_module.run_fcv_web_research("Somalia", "Water", client)

    assert len(client.calls) == 1
    assert client.calls[0]["model"] == expected_model
    if thinking is None:
        assert "thinking" not in client.calls[0]
    else:
        assert client.calls[0]["thinking"] == thinking


@pytest.mark.parametrize(
    ("configured_model", "expected_model", "thinking"),
    [
        (None, SONNET, {"type": "between_tools"}),
        (SONNET, SONNET, {"type": "between_tools"}),
        (HAIKU, HAIKU, {"type": "disabled"}),
    ],
)
def test_climate_research_uses_compatible_options_on_primary_and_continuation(
    monkeypatch, configured_model, expected_model, thinking,
):
    if configured_model is None:
        monkeypatch.delenv("FCV_RESEARCH_MODEL", raising=False)
    else:
        monkeypatch.setenv("FCV_RESEARCH_MODEL", configured_model)
    _patch_climate_acceptance(monkeypatch)
    paused_content = [SimpleNamespace(type="server_tool_use", name="web_search")]
    client = _RecordingClient([
        SimpleNamespace(content=paused_content, stop_reason="pause_turn"),
        _text_response(),
    ])

    result = app_module.run_climate_web_research("Somalia", "Water", {}, client)

    assert result["status"] == "complete"
    assert len(client.calls) == 2
    for call in client.calls:
        assert call["model"] == expected_model
        assert call.get("thinking") == thinking
    assert client.calls[1]["messages"] == [
        client.calls[0]["messages"][0],
        {"role": "assistant", "content": paused_content},
    ]


@pytest.mark.parametrize("configured_model", ["", "sonnet", " claude-haiku-5-5"])
def test_invalid_override_fails_closed_without_provider_calls(
    monkeypatch, configured_model,
):
    monkeypatch.setenv("FCV_RESEARCH_MODEL", configured_model)
    core_client = _RecordingClient([])
    climate_client = _RecordingClient([])

    core_result = app_module.run_fcv_web_research(
        "Somalia", "Water", core_client,
    )
    climate_result = app_module.run_climate_web_research(
        "Somalia", "Water", {}, climate_client,
    )

    assert core_result["status"] == "unavailable"
    assert climate_result["status"] == "failed"
    assert climate_result["attempts"] == 0
    assert core_client.calls == []
    assert climate_client.calls == []


def test_research_override_does_not_change_climate_structuring_model(monkeypatch):
    monkeypatch.setenv("FCV_RESEARCH_MODEL", HAIKU)
    _patch_climate_acceptance(monkeypatch)
    monkeypatch.setattr(
        app_module,
        "build_climate_evidence_packet",
        lambda provider_content, project_profile: {"sources": [], "passages": []},
    )
    monkeypatch.setattr(
        app_module, "build_climate_passage_selection_prompt", lambda packet: "select",
    )
    monkeypatch.setattr(
        app_module,
        "resolve_climate_passage_selections",
        lambda selections, packet: _climate_bundle(),
    )
    search_content = [
        SimpleNamespace(type="web_search_tool_result"),
        SimpleNamespace(type="web_search_tool_result"),
        SimpleNamespace(type="text", text="search notes", citations=[]),
    ]
    selection_text = (
        app_module.CLIMATE_RESEARCH_START
        + json.dumps({"selections": []})
        + app_module.CLIMATE_RESEARCH_END
    )
    client = _RecordingClient([
        SimpleNamespace(content=search_content, stop_reason="end_turn"),
        _text_response(selection_text),
    ])

    result = app_module.run_climate_web_research("Somalia", "Water", {}, client)

    assert result["status"] == "complete"
    assert len(client.calls) == 2
    search_call, structuring_call = client.calls
    assert search_call["model"] == HAIKU
    assert search_call["thinking"] == {"type": "disabled"}
    assert structuring_call["model"] == app_module.MODEL_LIGHT
    assert structuring_call["thinking"] == {"type": "disabled"}


@pytest.mark.parametrize(
    ("configured_model", "expected_model"),
    [(None, SONNET), (HAIKU, HAIKU), ("invalid", "invalid")],
)
def test_health_reports_effective_research_model_safely(
    monkeypatch, configured_model, expected_model,
):
    if configured_model is None:
        monkeypatch.delenv("FCV_RESEARCH_MODEL", raising=False)
    else:
        monkeypatch.setenv("FCV_RESEARCH_MODEL", configured_model)
    monkeypatch.setattr(
        app_module,
        "load_verified_climate_runtime",
        lambda: SimpleNamespace(mode="test"),
    )

    response = app_module.app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json()["fcv_research_model"] == expected_model
