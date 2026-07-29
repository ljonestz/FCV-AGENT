"""Tests for bounded, validated Climate-FCV research context."""

import json
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace

import anthropic
import httpx

import app as app_module
from sector_lenses.research import (
    CLIMATE_RESEARCH_END,
    CLIMATE_RESEARCH_START,
    build_climate_research_prompt,
    climate_research_evidence_gate,
    extract_climate_research_bundle,
    format_climate_research_context,
    normalize_climate_research_bundle,
)


SOUTH_SUDAN_FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "climate"
    / "south_sudan_dual_use.json"
)


def _valid_bundle():
    return {
        "status": "complete",
        "attempts": 1,
        "sources": [{
            "id": "climate-source-1",
            "source_type": "ccdr",
            "title": "Example Country CCDR",
            "url": "https://openknowledge.worldbank.org/example",
            "publication_date": "2025",
        }],
        "claims": [{
            "id": "climate-claim-1",
            "source_ids": ["climate-source-1"],
            "claim": "Changing flood timing affects landing-site access.",
            "geographies": ["Upper Nile"],
            "project_elements": ["Landing-site rehabilitation"],
            "affected_groups": ["Fishing households"],
            "systems_or_assets": ["Access roads"],
            "evidence_status": "observed",
            "confidence": "medium",
            "time_horizons": ["project-lifetime"],
            "evidence_gap": "No site-level design flood standard was found.",
        }],
    }


def _second_authoritative_source():
    return {
        "id": "climate-source-2",
        "source_type": "scientific",
        "title": "Peer-reviewed flood projection",
        "url": "https://ipcc.ch/example",
        "publication_date": "2024",
    }


def test_climate_research_gate_accepts_two_sources_and_project_claim():
    bundle = _valid_bundle()
    bundle["sources"].append(_second_authoritative_source())
    bundle["claims"][0]["source_ids"].append("climate-source-2")
    decision = climate_research_evidence_gate(bundle)
    assert decision["ok"] is True
    assert decision["code"] == ""
    assert len(decision["bundle"]["sources"]) == 2


def test_climate_research_gate_rejects_one_source():
    decision = climate_research_evidence_gate(_valid_bundle())
    assert decision["ok"] is False
    assert decision["code"] == "climate_research_insufficient"
    assert "two relevant sources" in decision["message"]


def test_climate_research_gate_rejects_claim_without_climate_anchor():
    bundle = _valid_bundle()
    bundle["sources"].append(_second_authoritative_source())
    bundle["claims"][0]["source_ids"].append("climate-source-2")
    bundle["claims"][0]["geographies"] = []
    bundle["claims"][0]["affected_groups"] = []
    bundle["claims"][0]["systems_or_assets"] = []
    decision = climate_research_evidence_gate(bundle)
    assert decision["ok"] is False
    assert decision["code"] == "climate_research_insufficient"


def test_climate_research_gate_rejects_duplicate_cited_source_url():
    bundle = _valid_bundle()
    duplicate = _second_authoritative_source()
    duplicate["url"] = "https://openknowledge.worldbank.org/example/"
    bundle["sources"].append(duplicate)
    bundle["claims"][0]["source_ids"].append("climate-source-2")

    decision = climate_research_evidence_gate(bundle)

    assert decision["ok"] is False
    assert decision["code"] == "climate_research_insufficient"


def test_climate_research_gate_rejects_uncited_second_source():
    bundle = _valid_bundle()
    bundle["sources"].append(_second_authoritative_source())

    decision = climate_research_evidence_gate(bundle)

    assert decision["ok"] is False
    assert decision["code"] == "climate_research_insufficient"


def test_climate_research_bundle_keeps_grounded_project_specific_claims():
    result = normalize_climate_research_bundle(_valid_bundle())

    assert result["status"] == "complete"
    assert result["claims"][0]["id"] == "climate-claim-1"
    assert result["claims"][0]["time_horizons"] == ["project-lifetime"]
    assert "Landing-site rehabilitation" in format_climate_research_context(result)


def test_climate_research_bundle_rejects_generic_or_untrusted_claims():
    raw = {
        "status": "complete",
        "sources": [{
            "id": "climate-source-1",
            "source_type": "blog",
            "title": "Untrusted",
            "url": "http://example.com/post",
        }],
        "claims": [{
            "id": "climate-claim-1",
            "source_ids": [],
            "claim": "Climate change may cause conflict.",
            "geographies": [],
            "project_elements": [],
            "affected_groups": [],
            "systems_or_assets": [],
            "evidence_status": "inferred",
            "confidence": "low",
            "time_horizons": [],
        }],
    }

    result = normalize_climate_research_bundle(raw)

    assert result["sources"] == []
    assert result["claims"] == []
    assert result["status"] == "failed"


def test_climate_research_extractor_strips_valid_hidden_bundle():
    text = (
        "Visible brief\n"
        + CLIMATE_RESEARCH_START
        + __import__("json").dumps(_valid_bundle())
        + CLIMATE_RESEARCH_END
    )

    visible, result = extract_climate_research_bundle(text)

    assert visible == "Visible brief"
    assert result["claims"][0]["id"] == "climate-claim-1"


def test_climate_research_bundle_is_bounded():
    raw = _valid_bundle()
    raw["claims"] = [
        {
            **raw["claims"][0],
            "id": f"climate-claim-{index}",
        }
        for index in range(1, 20)
    ]

    result = normalize_climate_research_bundle(raw)

    assert len(result["claims"]) == 12


def test_south_sudan_research_fixture_preserves_specific_horizons():
    fixture = json.loads(SOUTH_SUDAN_FIXTURE.read_text(encoding="utf-8"))

    result = normalize_climate_research_bundle(
        fixture["research_bundle"]
    )

    assert result["status"] == "complete"
    assert len(result["claims"]) == 3
    assert {
        horizon
        for claim in result["claims"]
        for horizon in claim["time_horizons"]
    } == set(fixture["expected"]["time_horizons"])
    assert {
        element
        for claim in result["claims"]
        for element in claim["project_elements"]
    } == set(fixture["project_elements"])


class _SequencedResearchClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []
        self.beta = SimpleNamespace(
            messages=SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def _valid_climate_response():
    bundle = _valid_bundle()
    bundle["sources"].append(_second_authoritative_source())
    bundle["claims"][0]["source_ids"].append("climate-source-2")
    return SimpleNamespace(content=[
        SimpleNamespace(
            type="text",
            text=(
                CLIMATE_RESEARCH_START
                + json.dumps(bundle)
                + CLIMATE_RESEARCH_END
            ),
        )
    ])


def test_climate_research_prompt_requires_specific_temporal_claims():
    prompt = build_climate_research_prompt(
        country="South Sudan",
        sector="Natural resources",
        project_profile={
            "locations": ["Upper Nile", "Jonglei"],
            "project_elements": [
                "Landing sites",
                "Community conservancies",
            ],
            "groups": ["Fishing households", "Pastoralists"],
            "assets": ["Access roads"],
        },
        narrow=False,
    )

    assert "public Country Climate and Development Report" in prompt
    assert "Use it only where directly relevant" in prompt
    assert "fill material gaps from authoritative" in prompt
    assert "Upper Nile" in prompt
    assert "asset-system-lifetime" in prompt
    assert CLIMATE_RESEARCH_START in prompt


def test_climate_research_retries_once_with_narrow_query():
    client = _SequencedResearchClient([
        anthropic.APITimeoutError(
            request=httpx.Request(
                "POST", "https://api.anthropic.com/v1/messages"
            )
        ),
        _valid_climate_response(),
    ])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Natural resources",
        {"locations": ["Upper Nile"], "project_elements": ["Landing sites"]},
        client,
    )

    assert result["status"] == "complete"
    assert result["attempts"] == 2
    assert len(client.calls) == 2
    assert "NARROW RETRY" in client.calls[1]["messages"][0]["content"]
    assert client.calls[1]["max_tokens"] == 3200
    assert client.calls[1]["tools"][0]["max_uses"] == 3


def test_climate_retry_requires_remaining_parent_budget():
    client = _SequencedResearchClient([
        anthropic.APITimeoutError(
            request=httpx.Request(
                "POST", "https://api.anthropic.com/v1/messages"
            )
        )
    ])
    ticks = iter([100.0, 100.0, 166.0, 166.0])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Natural resources",
        {"project_elements": ["Landing sites"]},
        client,
        deadline=170.0,
        clock=lambda: next(ticks),
        minimum_retry_seconds=35,
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 1
    assert len(client.calls) == 1


def test_climate_request_timeout_never_exceeds_parent_remaining_time():
    client = _SequencedResearchClient([_valid_climate_response()])
    ticks = iter([200.0, 200.0, 200.0])

    app_module.run_climate_web_research(
        "South Sudan",
        "Natural resources",
        {"project_elements": ["Landing sites"]},
        client,
        deadline=250.0,
        clock=lambda: next(ticks),
    )

    assert client.calls[0]["timeout"] <= 50.0


def test_climate_research_stops_after_one_failed_retry():
    timeout = lambda: anthropic.APITimeoutError(
        request=httpx.Request(
            "POST", "https://api.anthropic.com/v1/messages"
        )
    )
    client = _SequencedResearchClient([timeout(), timeout()])

    result = app_module.run_climate_web_research(
        "South Sudan", "Water", {}, client
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 2
    assert len(client.calls) == 2


def test_stage1_research_budget_abandons_slow_pass(monkeypatch):
    # A slow research pass must not block Stage 1 past the aggregate budget.
    import time as _time

    def slow_core(*args, **kwargs):
        _time.sleep(5)
        return {"brief": "late brief"}

    monkeypatch.setattr(app_module, "run_fcv_web_research", slow_core)
    monkeypatch.setattr(app_module, "get_research_client", lambda: object())
    plan = {
        "country": "Testland",
        "sector": "Water",
        "core": {"max_tokens": 100, "max_uses": 1},
        "climate": {"enabled": False},
        "project_profile": {},
    }
    started = _time.monotonic()
    events = list(
        app_module._iter_stage1_research(plan, "assess-1", budget_seconds=1)
    )
    elapsed = _time.monotonic() - started

    # Returned well before the slow (5s) pass would have finished.
    assert elapsed < 4
    statuses = [e.get("research_status") for e in events if "result" not in e]
    assert "research_timeout" in statuses
    final = events[-1]
    assert "result" in final
    # Abandoned pass contributed nothing; downstream degrades gracefully.
    assert final["result"]["core_brief"] == ""


def test_stage1_research_budget_completes_fast_pass(monkeypatch):
    import time as _time

    monkeypatch.setattr(
        app_module,
        "run_fcv_web_research",
        lambda *a, **k: {"brief": "quick brief"},
    )
    monkeypatch.setattr(app_module, "get_research_client", lambda: object())
    app_module._research_cache.clear()
    plan = {
        "country": "Fastland",
        "sector": "Energy",
        "core": {"max_tokens": 100, "max_uses": 1},
        "climate": {"enabled": False},
        "project_profile": {},
    }
    events = list(
        app_module._iter_stage1_research(plan, "assess-2", budget_seconds=30)
    )
    statuses = [e.get("research_status") for e in events if "result" not in e]
    assert "research_timeout" not in statuses
    assert events[-1]["result"]["core_brief"] == "quick brief"


def test_parent_passes_same_deadline_to_climate_worker(monkeypatch):
    captured = {}

    def fake_climate(*args, **kwargs):
        captured["deadline"] = kwargs["deadline"]
        return normalize_climate_research_bundle({})

    fixed_now = 1000.0
    monkeypatch.setattr(app_module.time, "monotonic", lambda: fixed_now)
    monkeypatch.setattr(app_module, "run_climate_web_research", fake_climate)
    monkeypatch.setattr(
        app_module, "run_fcv_web_research", lambda *args, **kwargs: {"brief": "core"}
    )
    monkeypatch.setattr(app_module, "get_research_client", lambda: object())
    app_module._research_cache.clear()
    plan = {
        "country": "Testland",
        "sector": "Water",
        "core": {"max_tokens": 100, "max_uses": 1},
        "climate": {"enabled": True},
        "project_profile": {},
    }

    list(app_module._iter_stage1_research(plan, "assessment-deadline", budget_seconds=30))

    assert captured["deadline"] == fixed_now + 30


def test_parent_timeout_discards_pending_climate_research(monkeypatch):
    class ControlledPool:
        def __init__(self):
            self.submissions = 0
            self.core_future = Future()
            self.climate_future = Future()

        def submit(self, *args, **kwargs):
            self.submissions += 1
            if self.submissions == 1:
                self.core_future.set_result({"brief": "core"})
                return self.core_future
            return self.climate_future

        def shutdown(self, **kwargs):
            return None

    pool = ControlledPool()
    ticks = iter([0.0, 0.0, 1.0])
    monkeypatch.setattr(app_module, "ThreadPoolExecutor", lambda **kwargs: pool)
    monkeypatch.setattr(app_module.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(app_module, "run_fcv_web_research", lambda *args, **kwargs: None)
    monkeypatch.setattr(app_module, "run_climate_web_research", lambda *args, **kwargs: None)
    monkeypatch.setattr(app_module, "get_research_client", lambda: object())
    app_module._research_cache.clear()
    plan = {
        "country": "Testland",
        "sector": "Water",
        "core": {"max_tokens": 100, "max_uses": 1},
        "climate": {"enabled": True},
        "project_profile": {},
    }

    events = list(app_module._iter_stage1_research(plan, "assess-climate", budget_seconds=1))
    result = events[-1]["result"]

    assert pool.climate_future.done() is False
    assert result["climate_research"]["status"] == "failed"
    assert result["climate_research"]["attempts"] == 1
    assert result["climate_research"]["failure_reason"] == (
        "Climate research exceeded the assessment deadline."
    )
    assert result["lens_context_sources"] == []


def test_climate_research_telemetry_is_structural_and_private(caplog):
    sentinel = "SECRET PROJECT CLAIM MUST NOT LEAK"
    bundle = _valid_bundle()
    bundle["claims"][0]["claim"] = sentinel
    bundle["sources"][0]["title"] = "SECRET SOURCE TITLE"
    bundle["sources"][0]["url"] = "https://secret.example/private"

    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        app_module.log_climate_research_summary(
            "assessment-1", bundle, elapsed_ms=1234
        )

    assert "assessment-1" in caplog.text
    assert "claims=1" in caplog.text
    assert "sources=1" in caplog.text
    assert "source_types=ccdr" in caplog.text
    assert "elapsed_ms=1234" in caplog.text
    assert sentinel not in caplog.text
    assert "SECRET SOURCE TITLE" not in caplog.text
    assert "secret.example" not in caplog.text


def test_specificity_telemetry_does_not_log_rejected_pathway_text(caplog):
    sentinel = "SECRET GENERIC PATHWAY"

    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        app_module.log_climate_specificity_summary(
            "assessment-1",
            {
                "accepted": 2,
                "rejected": 1,
                "horizon_counts": {
                    "current-near-term": 1,
                    "project-lifetime": 2,
                },
                "rejected_text": sentinel,
            },
        )

    assert "accepted=2" in caplog.text
    assert "rejected=1" in caplog.text
    assert "project-lifetime:2" in caplog.text
    assert sentinel not in caplog.text


def test_priority_link_telemetry_logs_counts_not_priority_content(caplog):
    sentinel = "SECRET PRIORITY CONTRIBUTION"
    priorities = [{
        "title": "SECRET PRIORITY TITLE",
        "climate_links": {
            "status": "linked",
            "contribution": sentinel,
        },
    }, {
        "title": "ANOTHER SECRET TITLE",
        "climate_links": {
            "status": "no-material-pathway",
            "reason": "SECRET REASON",
        },
    }]

    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        app_module.log_climate_priority_summary("assessment-1", priorities)

    assert "linked=1" in caplog.text
    assert "no_material=1" in caplog.text
    assert sentinel not in caplog.text
    assert "SECRET PRIORITY TITLE" not in caplog.text
    assert "SECRET REASON" not in caplog.text


def test_research_client_disables_hidden_sdk_retries(monkeypatch):
    captured = {}
    sentinel = object()

    def fake_client(**kwargs):
        captured.update(kwargs)
        return sentinel

    monkeypatch.setattr(app_module.anthropic, "Anthropic", fake_client)
    monkeypatch.setattr(app_module, "_research_client", None)

    assert app_module.get_research_client() is sentinel
    assert captured["max_retries"] == 0


def test_climate_research_timeout_has_specific_user_message():
    decision = climate_research_evidence_gate(
        normalize_climate_research_bundle({
            "status": "failed",
            "attempts": 1,
            "failure_reason": "Climate research exceeded the assessment deadline.",
        })
    )

    assert decision["code"] == "climate_research_failed"
    assert decision["message"] == (
        "The required Climate-FCV web research timed out before validated "
        "evidence could be returned. Retry the climate assessment."
    )


def test_climate_research_attempt_logging_identifies_response_boundary(caplog):
    secret = "SECRET PROJECT RESPONSE TEXT"
    response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text=secret)]
    )
    client = _SequencedResearchClient([response, response])

    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        result = app_module.run_climate_web_research(
            "Testland", "Water", {}, client, assessment_id="assessment-log"
        )

    assert result["status"] == "failed"
    assert "assessment_id=assessment-log attempt=1 outcome=response" in caplog.text
    assert "block_present=no" in caplog.text
    assert "sources=0 claims=0" in caplog.text
    assert "gate_code=climate_research_failed" in caplog.text
    assert secret not in caplog.text
