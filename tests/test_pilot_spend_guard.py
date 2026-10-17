"""The pilot must reject a request before its reserved ceiling is exceeded."""
import json
import httpx
import pytest
from pilot_spend_guard import PilotSpendGuard, PilotBudgetExceeded


def request(**changes):
    body = dict(model="claude-sonnet-5-5", max_tokens=1000,
                messages=[{"role": "user", "content": "test"}])
    body.update(changes)
    return httpx.Request("POST", "https://api.anthropic.com/v1/messages", json=body)


def test_reservations_persist_and_retry_is_charged_again(tmp_path):
    path = tmp_path / "ledger.sqlite"
    guard = PilotSpendGuard(path, 100000)
    guard(request())
    spent = guard.reserved_microusd()
    assert 10000 < spent < 50000
    restored = PilotSpendGuard(path, 100000)
    restored(request())
    assert restored.reserved_microusd() == spent * 2
    with pytest.raises(PilotBudgetExceeded):
        restored(request())
    assert restored.reserved_microusd() == spent * 2


@pytest.mark.parametrize("changes", [
    {"model": "unknown"},
    {"mcp_servers": [{"type": "url", "url": "https://example.com/mcp", "name": "external"}]},
    {"messages": [{"role": "user", "content": [{"type": "new_media", "source": "remote"}]}]},
    {"context_management": {"edits": [{"type": "compact_20260112"}]}}, {"tools": [{"type": "web_search_20250305"}]},
    {"max_tokens": 0}, {"max_tokens": True}, {"service_tier": "priority"},
    {"inference_geo": "us"}, {"system": [{"text": "x", "cache_control": {"type": "ephemeral"}}]},
])
def test_unknown_charges_fail_closed(tmp_path, changes):
    guard = PilotSpendGuard(tmp_path / "ledger.sqlite", 5000000)
    with pytest.raises(PilotBudgetExceeded):
        guard(request(**changes))
    assert guard.reserved_microusd() == 0


def test_transport_is_not_called_when_budget_rejected(tmp_path):
    calls = []
    guard = PilotSpendGuard(tmp_path / "ledger.sqlite", 1)
    with httpx.Client(event_hooks={"request": [guard]}, transport=httpx.MockTransport(
        lambda r: calls.append(r) or httpx.Response(200, json={})
    )) as client:
        with pytest.raises(PilotBudgetExceeded):
            client.send(request())
    assert calls == []


def test_cannot_silently_raise_existing_campaign_limit(tmp_path):
    path = tmp_path / "ledger.sqlite"
    PilotSpendGuard(path, 100)
    with pytest.raises(ValueError):
        PilotSpendGuard(path, 10000000)


def test_parallel_requests_cannot_overdraw(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    path = tmp_path / "ledger.sqlite"
    guard = PilotSpendGuard(path, 100000)
    def attempt(_):
        try:
            guard(request())
            return True
        except PilotBudgetExceeded:
            return False
    with ThreadPoolExecutor(max_workers=4) as pool:
        accepted = list(pool.map(attempt, range(8)))
    assert sum(accepted) == 2
    assert 0 < guard.reserved_microusd() <= 100000


def test_all_application_clients_use_guard_and_default_is_off(monkeypatch, tmp_path):
    import app
    from pilot_spend_guard import pilot_http_client
    monkeypatch.delenv("FCV_PILOT_BUDGET_MICROUSD", raising=False)
    monkeypatch.delenv("FCV_PILOT_BUDGET_DB", raising=False)
    assert pilot_http_client() == {}
    monkeypatch.setenv("FCV_PILOT_BUDGET_MICROUSD", "500000")
    monkeypatch.setenv("FCV_PILOT_BUDGET_DB", str(tmp_path / "ledger.sqlite"))
    captured = []
    real_http_client = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kw: real_http_client(
        transport=httpx.MockTransport(lambda r: httpx.Response(200)), **kw))
    monkeypatch.setattr(app.anthropic, "Anthropic", lambda **kw: captured.append(kw) or object())
    for name in ["_client", "_fast_client", "_lens_recovery_client", "_research_client"]:
        monkeypatch.setattr(app, name, None)
    for getter in [app.get_client, app.get_fast_client, app.get_lens_recovery_client, app.get_research_client]:
        getter()
    assert len(captured) == 4
    for kw in captured:
        assert isinstance(kw["http_client"].event_hooks["request"][0], PilotSpendGuard)
        kw["http_client"].close()
