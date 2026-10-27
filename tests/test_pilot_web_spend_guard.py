"""Contracts for the explicitly enabled, budgeted Anthropic web-search pilot."""

import json
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from anthropic.types import Message as AnthropicMessage

from pilot_spend_guard import PilotBudgetExceeded, PilotSpendGuard, pilot_http_client


WEB_LIMIT = 15_000_000
_DEFAULT_USAGE = object()


def web_request(**changes):
    body = {
        "model": "claude-haiku-5-5",
        "max_tokens": 1024,
        "stream": False,
        "messages": [{"role": "user", "content": "Check current public information."}],
        "tools": [{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 2,
        }],
        "tool_choice": {"type": "auto"},
    }
    body.update(changes)
    return httpx.Request("POST", "https://api.anthropic.com/v1/messages", json=body)


def web_response(request, *, usage=_DEFAULT_USAGE, status=200, model="claude-haiku-5-5"):
    sdk_shape = usage is _DEFAULT_USAGE and model == "claude-haiku-5-5"
    if usage is _DEFAULT_USAGE:
        usage = {
            "input_tokens": 17,
            "output_tokens": 23,
            "cache_creation": {
                "ephemeral_1h_input_tokens": 0,
                "ephemeral_5m_input_tokens": 0,
            },
            "cache_creation_input_tokens": None,
            "cache_read_input_tokens": None,
            "inference_geo": "global",
            "server_tool_use": {"web_search_requests": 2, "web_fetch_requests": 0},
            "service_tier": "standard",
        }
    body = {
        "id": "msg_pilot_test",
        "type": "message",
        "container": None,
        "role": "assistant",
        "model": model,
        "content": [
            {"type": "server_tool_use", "id": "srvtoolu_1", "name": "web_search",
             "input": {"query": "current public information"}},
            {"type": "web_search_tool_result", "tool_use_id": "srvtoolu_1", "content": [
                {"type": "web_search_result", "url": "https://example.org", "title": "Source",
                 "encrypted_content": "opaque", "page_age": "2026-10-27"},
            ]},
            {"type": "text", "text": "Found two useful sources.", "citations": [
                {"type": "web_search_result_location", "cited_text": "A result.",
                 "encrypted_index": "opaque", "title": "Source", "url": "https://example.org"},
            ]},
        ],
        "stop_reason": "end_turn",
        "stop_sequence": None,
    }
    if usage is not None:
        body["usage"] = usage
    if sdk_shape:
        body = AnthropicMessage.model_validate(body).model_dump(mode="json")
    return httpx.Response(status, json=body, request=request)


def web_guard(path, limit=WEB_LIMIT):
    return PilotSpendGuard(path, limit, allow_web_search=True)


def web_client(guard, transport):
    return httpx.Client(
        transport=transport,
        event_hooks={"request": [guard], "response": [guard.response_hook]},
    )


def test_web_mode_requires_strict_opt_in_and_both_budget_settings(monkeypatch, tmp_path):
    monkeypatch.delenv("FCV_PILOT_ALLOW_WEB_SEARCH", raising=False)
    monkeypatch.delenv("FCV_PILOT_BUDGET_MICROUSD", raising=False)
    monkeypatch.delenv("FCV_PILOT_BUDGET_DB", raising=False)
    assert pilot_http_client() == {}

    monkeypatch.setenv("FCV_PILOT_ALLOW_WEB_SEARCH", "true")
    with pytest.raises(ValueError):
        pilot_http_client()

    monkeypatch.setenv("FCV_PILOT_ALLOW_WEB_SEARCH", "1")
    with pytest.raises(ValueError):
        pilot_http_client()

    monkeypatch.setenv("FCV_PILOT_BUDGET_MICROUSD", str(WEB_LIMIT))
    monkeypatch.setenv("FCV_PILOT_BUDGET_DB", str(tmp_path / "web.sqlite"))
    created = []

    class ClientStub:
        def __init__(self, *, event_hooks):
            self.event_hooks = event_hooks
            created.append(self)

        def close(self):
            pass

    monkeypatch.setattr(httpx, "Client", ClientStub)
    kwargs = pilot_http_client()
    client = kwargs["http_client"]
    try:
        assert set(client.event_hooks) == {"request", "response"}
        assert len(created) == 1
    finally:
        client.close()


def test_fresh_web_ledger_is_separate_from_legacy_and_capped_at_fifteen_dollars(tmp_path):
    legacy_path = tmp_path / "legacy.sqlite"
    PilotSpendGuard(legacy_path, 6_000_000)
    with pytest.raises(ValueError):
        web_guard(legacy_path)

    web_path = tmp_path / "web.sqlite"
    web_guard(web_path)
    with pytest.raises(ValueError):
        PilotSpendGuard(web_path, 6_000_000)
    with pytest.raises(ValueError):
        web_guard(tmp_path / "over-limit.sqlite", WEB_LIMIT + 1)


def test_legacy_mode_still_rejects_web_search_without_reserving(tmp_path):
    guard = PilotSpendGuard(tmp_path / "legacy.sqlite", 6_000_000)
    with pytest.raises(PilotBudgetExceeded):
        guard(web_request())
    assert guard.reserved_microusd() == 0


def test_valid_web_response_settles_actual_cost_once(tmp_path):
    guard = web_guard(tmp_path / "settle.sqlite")
    calls = []

    def transport(request):
        calls.append(request)
        return web_response(request)

    with web_client(guard, httpx.MockTransport(transport)) as client:
        response = client.send(web_request())
        assert response.status_code == 200
        response.read()
        guard.response_hook(response)
        sdk_payload = response.json()

    assert sdk_payload["container"] is None
    assert sdk_payload["usage"]["cache_creation"] == {
        "ephemeral_1h_input_tokens": 0,
        "ephemeral_5m_input_tokens": 0,
    }
    assert sdk_payload["usage"]["cache_creation_input_tokens"] is None
    assert sdk_payload["usage"]["cache_read_input_tokens"] is None

    # High-tier Haiku 5.5 rates: $0.50/M input and $2.50/M output.
    assert guard.reserved_microusd() == (17 * 5 + 23 * 25 + 9) // 10 + 2 * 10_000
    assert len(calls) == 1


def test_web_hold_uses_ten_iterations_and_highest_haiku_rates(tmp_path):
    guard = web_guard(tmp_path / "full-hold.sqlite")
    request = web_request(
        max_tokens=128_000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
    )
    guard(request)

    expected = (10 * 1_000_000 * 5 + 10 * 128_000 * 25 + 9) // 10 + 3 * 10_000
    assert guard.reserved_microusd() == expected == 8_230_000


@pytest.mark.parametrize("usage", [
    None,
    {"input_tokens": -1, "output_tokens": 0,
     "server_tool_use": {"web_search_requests": 0}},
    {"input_tokens": 17, "output_tokens": 23, "server_tool_use": None},
    {"input_tokens": 1, "output_tokens": True,
     "server_tool_use": {"web_search_requests": 0}},
    {"input_tokens": 1, "output_tokens": 1,
     "cache_read_input_tokens": 1,
     "server_tool_use": {"web_search_requests": 0}},
    {"input_tokens": 1, "output_tokens": 1,
     "server_tool_use": {"web_search_requests": 3}},
])
def test_unverifiable_web_usage_keeps_the_full_hold(tmp_path, usage):
    guard = web_guard(tmp_path / f"held-{str(usage is None)}-{abs(hash(json.dumps(usage, sort_keys=True, default=str)))}.sqlite")

    held_during_transport = []

    def transport(request):
        held_during_transport.append(guard.reserved_microusd())
        return web_response(request, usage=usage)

    with web_client(guard, httpx.MockTransport(transport)) as client:
        client.send(web_request())

    assert len(held_during_transport) == 1
    assert held_during_transport[0] > 0
    assert guard.reserved_microusd() == held_during_transport[0]


@pytest.mark.parametrize("cache_shape", [
    {"cache_creation": None, "cache_creation_input_tokens": None,
     "cache_read_input_tokens": None},
    {"cache_creation": {"ephemeral_1h_input_tokens": 0,
                         "ephemeral_5m_input_tokens": 0},
     "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
])
def test_null_or_zero_cache_usage_settles(tmp_path, cache_shape):
    guard = web_guard(tmp_path / f"cache-{len(str(cache_shape))}.sqlite")
    usage = {
        "input_tokens": 17,
        "output_tokens": 23,
        "inference_geo": "global",
        "server_tool_use": {"web_search_requests": 1, "web_fetch_requests": 0},
        "service_tier": "standard",
        "speed": "standard",
        "output_tokens_details": {"thinking_tokens": 0},
        **cache_shape,
    }

    with web_client(guard, httpx.MockTransport(
        lambda request: web_response(request, usage=usage),
    )) as client:
        client.send(web_request())

    assert guard.reserved_microusd() == (17 * 5 + 23 * 25 + 9) // 10 + 10_000


@pytest.mark.parametrize("changes", [
    {"cache_creation": {"ephemeral_1h_input_tokens": 0,
                         "ephemeral_5m_input_tokens": 1}},
    {"cache_creation_input_tokens": 1},
    {"cache_read_input_tokens": 1},
    {"service_tier": "priority"},
    {"inference_geo": "us"},
    {"speed": "fast"},
    {"unpriced_usage_field": 1},
])
def test_positive_cache_or_unpriced_usage_keeps_the_full_hold(tmp_path, changes):
    guard = web_guard(tmp_path / f"unpriced-{abs(hash(str(changes)))}.sqlite")
    usage = {
        "input_tokens": 17,
        "output_tokens": 23,
        "cache_creation": {"ephemeral_1h_input_tokens": 0,
                            "ephemeral_5m_input_tokens": 0},
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "inference_geo": "global",
        "server_tool_use": {"web_search_requests": 1, "web_fetch_requests": 0},
        "service_tier": "standard",
        "speed": "standard",
    }
    usage.update(changes)
    held_during_transport = []

    def transport(request):
        held_during_transport.append(guard.reserved_microusd())
        return web_response(request, usage=usage)

    with web_client(guard, httpx.MockTransport(transport)) as client:
        client.send(web_request())

    assert guard.reserved_microusd() == held_during_transport[0] > 0


@pytest.mark.parametrize("response_model", ["claude-sonnet-5-5", None])
def test_response_model_must_match_the_priced_haiku_request(tmp_path, response_model):
    guard = web_guard(tmp_path / f"wrong-model-{response_model}.sqlite")
    held_during_transport = []

    def transport(request):
        held_during_transport.append(guard.reserved_microusd())
        response = web_response(request, model=response_model)
        if response_model is None:
            body = response.json()
            body.pop("model")
            return httpx.Response(200, json=body, request=request)
        return response

    with web_client(guard, httpx.MockTransport(transport)) as client:
        client.send(web_request())

    assert guard.reserved_microusd() == held_during_transport[0] > 0


def test_transport_failure_keeps_full_web_hold(tmp_path):
    guard = web_guard(tmp_path / "transport-failure.sqlite")

    def fail(_request):
        raise httpx.ConnectError("offline")

    with web_client(guard, httpx.MockTransport(fail)) as client:
        with pytest.raises(httpx.ConnectError):
            client.send(web_request())

    assert guard.reserved_microusd() > 0


def test_reported_cost_over_hold_is_recorded_and_blocks_following_requests(tmp_path):
    guard = web_guard(tmp_path / "overrun.sqlite", 6_000_000)
    held_during_transport = []

    def transport(request):
        held_during_transport.append(guard.reserved_microusd())
        return web_response(request, usage={
            "input_tokens": 10_100_000,
            "output_tokens": 1024,
            "server_tool_use": {"web_search_requests": 2},
        })

    with web_client(guard, httpx.MockTransport(transport)) as client:
        with pytest.raises(PilotBudgetExceeded):
            client.send(web_request())

    actual = (10_100_000 * 5 + 1024 * 25 + 9) // 10 + 2 * 10_000
    assert guard.reserved_microusd() == actual > held_during_transport[0]
    with pytest.raises(PilotBudgetExceeded):
        guard(web_request())


@pytest.mark.parametrize("changes", [
    {"model": "claude-sonnet-5-5"},
    {"stream": True},
    {"service_tier": "priority"},
    {"inference_geo": "us"},
    {"tool_choice": {"type": "any"}},
    {"tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 0}]},
    {"tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": True}]},
    {"tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}]},
    {"tools": [{"type": "web_search_20250305", "name": "other", "max_uses": 1}]},
    {"tools": [{"type": "web_search_20260318", "name": "web_search", "max_uses": 1}]},
    {"tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 1,
                 "allowed_domains": ["example.org"], "unknown": True}]},
    {"cache_control": {"type": "ephemeral"}},
    {"unknown_request_field": True},
])
def test_web_mode_rejects_unpriced_request_shapes_before_transport(tmp_path, changes):
    guard = web_guard(tmp_path / f"reject-{len(str(changes))}.sqlite")
    sent = []

    with web_client(guard, httpx.MockTransport(
        lambda request: sent.append(request) or web_response(request),
    )) as client:
        with pytest.raises(PilotBudgetExceeded):
            client.send(web_request(**changes))

    assert sent == []
    assert guard.reserved_microusd() == 0


def test_web_mode_accepts_only_native_web_continuation_blocks(tmp_path):
    guard = web_guard(tmp_path / "continuation.sqlite")
    continuation = web_request(messages=[
        {"role": "user", "content": "Find current evidence."},
        {"role": "assistant", "content": [
            {"type": "thinking", "thinking": "Search for current sources.", "signature": "sig"},
            {"type": "redacted_thinking", "data": "redacted"},
            {"type": "server_tool_use", "id": "srvtoolu_1", "name": "web_search",
             "input": {"query": "current evidence"}},
            {"type": "web_search_tool_result", "tool_use_id": "srvtoolu_1", "content": [
                {"type": "web_search_result", "title": "Source", "url": "https://example.org",
                 "page_age": "2026-10-27", "encrypted_content": "opaque"},
            ]},
            {"type": "text", "text": "Source cited.", "citations": [
                {"type": "web_search_result_location", "cited_text": "A result.",
                 "encrypted_index": "opaque", "title": "Source", "url": "https://example.org"},
            ]},
        ]},
    ])
    guard(continuation)
    assert guard.reserved_microusd() > 0


def test_web_continuation_accepts_documented_error_object_content(tmp_path):
    guard = web_guard(tmp_path / "continuation-error.sqlite")
    continuation = web_request(messages=[
        {"role": "user", "content": "Find current evidence."},
        {"role": "assistant", "content": [
            {"type": "server_tool_use", "id": "srvtoolu_1", "name": "web_search",
             "input": {"query": "current evidence"}},
            {"type": "web_search_tool_result", "tool_use_id": "srvtoolu_1",
             "content": {"type": "web_search_tool_result_error",
                         "error_code": "max_uses_exceeded"}},
        ]},
    ])

    guard(continuation)
    assert guard.reserved_microusd() > 0


def test_web_continuation_rejects_nested_cache_control_before_reserving(tmp_path):
    guard = web_guard(tmp_path / "continuation-cache-control.sqlite")
    continuation = web_request(messages=[
        {"role": "user", "content": "Find current evidence."},
        {"role": "assistant", "content": [
            {"type": "text", "text": "Cached continuation.",
             "cache_control": {"type": "ephemeral"}},
        ]},
    ])

    with pytest.raises(PilotBudgetExceeded):
        guard(continuation)

    assert guard.reserved_microusd() == 0


@pytest.mark.parametrize("block", [
    {"type": "image", "source": {"type": "base64", "data": "x"}},
    {"type": "document", "source": {"type": "url", "url": "https://example.org"}},
    {"type": "tool_use", "id": "toolu_1", "name": "client_tool", "input": {}},
    {"type": "mcp_tool_use", "id": "mcp_1", "name": "client_tool", "input": {},
     "server_name": "external"},
    {"type": "web_fetch_tool_result", "tool_use_id": "srvtoolu_1", "content": []},
])
def test_web_continuation_rejects_other_modalities_and_tools_before_reserving(tmp_path, block):
    guard = web_guard(tmp_path / f"continuation-reject-{block['type']}.sqlite")
    request = web_request(messages=[
        {"role": "user", "content": "Find current evidence."},
        {"role": "assistant", "content": [block]},
    ])

    with pytest.raises(PilotBudgetExceeded):
        guard(request)

    assert guard.reserved_microusd() == 0


def test_parallel_web_holds_never_cross_the_ledger_ceiling(tmp_path):
    guard = web_guard(tmp_path / "parallel.sqlite")

    def reserve(_):
        try:
            guard(web_request(max_tokens=128_000,
                              tools=[{"type": "web_search_20250305", "name": "web_search",
                                      "max_uses": 3}]))
            return True
        except PilotBudgetExceeded:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        accepted = list(pool.map(reserve, range(8)))

    assert sum(accepted) == 1
    assert guard.reserved_microusd() <= WEB_LIMIT


def test_all_four_application_clients_register_response_settlement_hook(monkeypatch, tmp_path):
    import app

    monkeypatch.setenv("FCV_PILOT_ALLOW_WEB_SEARCH", "1")
    monkeypatch.setenv("FCV_PILOT_BUDGET_MICROUSD", str(WEB_LIMIT))
    monkeypatch.setenv("FCV_PILOT_BUDGET_DB", str(tmp_path / "all-clients.sqlite"))

    captured = []
    real_client = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: real_client(
        transport=httpx.MockTransport(lambda request: web_response(request)), **kwargs,
    ))
    monkeypatch.setattr(app.anthropic, "Anthropic", lambda **kwargs: captured.append(kwargs) or object())
    for name in ["_client", "_fast_client", "_lens_recovery_client", "_research_client"]:
        monkeypatch.setattr(app, name, None)

    for getter in [app.get_client, app.get_fast_client, app.get_lens_recovery_client,
                   app.get_research_client]:
        getter()

    assert len(captured) == 4
    for kwargs in captured:
        client = kwargs["http_client"]
        assert client.event_hooks["request"]
        assert client.event_hooks["response"]
        client.close()


def test_web_opt_in_leaves_legacy_text_sse_reservation_untouched(tmp_path, capsys):
    guard = web_guard(tmp_path / "text-sse.sqlite")
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages", json={
        "model": "claude-haiku-5-5",
        "max_tokens": 1024,
        "stream": True,
        "messages": [{"role": "user", "content": "Plain text request."}],
    })
    guard(request)
    held = guard.reserved_microusd()

    response = httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        content=b"event: message_stop\ndata: {\"type\":\"message_stop\"}\n\n",
        request=request,
    )
    guard.response_hook(response)

    assert held > 0
    assert guard.reserved_microusd() == held
    assert "PILOT_BUDGET charged_delta_microusd=" in capsys.readouterr().out
