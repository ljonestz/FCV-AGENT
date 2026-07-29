"""Tests for bounded, validated Climate-FCV research context."""

import json
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace

import anthropic
import httpx
from anthropic._exceptions import OverloadedError

import app as app_module
from sector_lenses.research import (
    CLIMATE_EVIDENCE_PACKET_MAX_CHARS,
    CLIMATE_RESEARCH_END,
    CLIMATE_RESEARCH_START,
    build_climate_evidence_packet,
    build_climate_research_prompt,
    climate_research_evidence_gate,
    extract_climate_research_bundle,
    format_climate_research_context,
    normalize_climate_research_bundle,
    summarize_climate_structuring_response,
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


def test_climate_evidence_packet_is_bounded_and_excludes_raw_payloads():
    project_profile = {
        "documents": ["South Sudan PCN.docx"],
        "document_excerpt": "Landing sites and access roads. " * 1000,
    }
    content = [
        SimpleNamespace(
            type="text",
            text="Flood and drought evidence. " * 1000,
            citations=[
                SimpleNamespace(
                    type="web_search_result_location",
                    title="South Sudan Country Climate and Development Report",
                    url="https://www.worldbank.org/example-ccdr",
                    cited_text="Flood timing affects transport access.",
                    page_age="2025",
                ),
                SimpleNamespace(
                    type="web_search_result_location",
                    title="Duplicate CCDR",
                    url="https://www.worldbank.org/example-ccdr/",
                    cited_text="Duplicate citation.",
                    page_age="2025",
                ),
                SimpleNamespace(
                    type="web_search_result_location",
                    title="Untrusted result",
                    url="https://example.com/untrusted",
                    cited_text="Must not survive.",
                    page_age="2026",
                ),
            ],
        ),
        SimpleNamespace(
            type="web_search_tool_result",
            content=[
                SimpleNamespace(
                    type="web_search_result",
                    title="UN climate risk evidence",
                    url="https://www.un.org/example-climate",
                    page_age="2024",
                    encrypted_content="encrypted-secret",
                )
            ],
        ),
    ]

    packet = build_climate_evidence_packet(content, project_profile)
    serialized = json.dumps(packet)

    assert len(serialized) <= CLIMATE_EVIDENCE_PACKET_MAX_CHARS
    assert packet["notes"]
    assert [source["url"] for source in packet["sources"]] == [
        "https://www.worldbank.org/example-ccdr",
        "https://www.un.org/example-climate",
    ]
    assert "encrypted-secret" not in serialized
    assert "example.com/untrusted" not in serialized
    assert packet["project_profile"]["document_excerpt"]


def test_climate_evidence_packet_accepts_dictionary_blocks():
    packet = build_climate_evidence_packet(
        [{
            "type": "text",
            "text": "Observed drought affects water access.",
            "citations": [{
                "type": "web_search_result_location",
                "title": "UN drought evidence",
                "url": "https://www.un.org/drought-evidence",
                "cited_text": "Drought affects rural water systems.",
                "page_age": "2025",
            }],
        }],
        {"documents": ["PCN.docx"], "document_excerpt": "Water systems"},
    )

    assert packet["notes"] == "Observed drought affects water access."
    assert packet["sources"][0]["title"] == "UN drought evidence"
    assert packet["sources"][0]["publication_date"] == "2025"



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



def test_climate_structuring_diagnostic_reports_truncation_without_text():
    secret = "SECRET PROJECT EVIDENCE Upper Nile https://example.invalid"
    text = CLIMATE_RESEARCH_START + '{"status":"partial","sources":[' + secret
    usage = SimpleNamespace(input_tokens=1200, output_tokens=2500)

    summary = summarize_climate_structuring_response(
        text,
        usage=usage,
        stop_reason="max_tokens",
        gate_code="climate_research_failed",
    )

    assert summary == {
        "stop_reason": "max_tokens",
        "input_tokens": 1200,
        "output_tokens": 2500,
        "response_chars": len(text),
        "start_present": True,
        "end_present": False,
        "json_status": "incomplete",
        "top_level_object": False,
        "fields_present": ("status", "sources"),
        "sources_count": -1,
        "claims_count": -1,
        "gate_code": "climate_research_failed",
    }
    assert secret not in repr(summary)


def test_climate_structuring_diagnostic_reports_complete_object_shape():
    payload = {
        "status": "complete",
        "attempts": 1,
        "sources": [{}, {}],
        "claims": [{}, {}, {}, {}],
        "failure_reason": "",
        "SECRET ARBITRARY KEY": "SECRET VALUE",
    }
    text = (
        CLIMATE_RESEARCH_START
        + json.dumps(payload)
        + CLIMATE_RESEARCH_END
    )

    summary = summarize_climate_structuring_response(
        text,
        usage={"input_tokens": 900, "output_tokens": 700},
        stop_reason="end_turn",
        gate_code="",
    )

    assert summary["json_status"] == "valid"
    assert summary["top_level_object"] is True
    assert summary["fields_present"] == (
        "status", "attempts", "sources", "claims", "failure_reason"
    )
    assert summary["sources_count"] == 2
    assert summary["claims_count"] == 4
    assert "SECRET" not in repr(summary)


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


def test_climate_research_uses_one_focused_request():
    client = _SequencedResearchClient([_valid_climate_response()])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Natural resources",
        {"locations": ["Upper Nile"], "project_elements": ["Landing sites"]},
        client,
    )

    assert result["status"] == "complete"
    assert result["attempts"] == 1
    assert len(client.calls) == 1
    call = client.calls[0]
    assert "SEARCH ONLY" in call["messages"][0]["content"]
    assert CLIMATE_RESEARCH_START not in call["messages"][0]["content"]
    assert call["max_tokens"] == 1800
    assert call["tools"][0]["max_uses"] == 2
    assert call["timeout"] == 135


def test_climate_research_continues_one_pause_turn():
    paused_content = [
        SimpleNamespace(type="server_tool_use", name="web_search")
    ]
    paused = SimpleNamespace(
        content=paused_content,
        stop_reason="pause_turn",
    )
    final = _valid_climate_response()
    final.stop_reason = "end_turn"
    client = _SequencedResearchClient([paused, final])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Water",
        {},
        client,
    )

    assert result["status"] == "complete"
    assert result["attempts"] == 1
    assert len(client.calls) == 2
    assert client.calls[1]["messages"] == [
        client.calls[0]["messages"][0],
        {"role": "assistant", "content": paused_content},
    ]


def test_climate_research_structures_search_notes_without_researching():
    searched_content = [
        SimpleNamespace(type="server_tool_use", name="web_search"),
        SimpleNamespace(type="web_search_tool_result", content=[]),
        SimpleNamespace(type="web_search_tool_result", content=[]),
        SimpleNamespace(type="text", text="Search completed but output was truncated."),
    ]
    truncated = SimpleNamespace(
        content=searched_content,
        stop_reason="end_turn",
    )
    final = _valid_climate_response()
    final.stop_reason = "end_turn"
    client = _SequencedResearchClient([truncated, final])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Water",
        {"locations": ["Upper Nile"]},
        client,
    )

    assert result["status"] == "complete"
    assert result["attempts"] == 1
    assert len(client.calls) == 2
    recovery = client.calls[1]
    assert "tools" not in recovery
    assert "betas" not in recovery
    assert recovery["model"] == "claude-haiku-4-5-20251001"
    assert recovery["max_tokens"] == 2500
    assert [message["role"] for message in recovery["messages"]] == [
        "user", "assistant", "user",
    ]
    assert recovery["messages"][1]["content"] is searched_content
    assert "Do not search again" in recovery["messages"][2]["content"]
    assert CLIMATE_RESEARCH_START in recovery["messages"][2]["content"]
    assert '"source_type"' in recovery["messages"][2]["content"]
    assert '"time_horizons"' in recovery["messages"][2]["content"]


def test_climate_structuring_diagnostic_is_logged_without_content(caplog):
    searched = SimpleNamespace(
        content=[
            SimpleNamespace(type="web_search_tool_result", content=[]),
            SimpleNamespace(type="web_search_tool_result", content=[]),
            SimpleNamespace(type="text", text="Two searches completed."),
        ],
        stop_reason="end_turn",
    )
    secret = "SECRET PROJECT RESPONSE TEXT Upper Nile"
    truncated_text = (
        CLIMATE_RESEARCH_START
        + '{"status":"partial","sources":['
        + secret
    )
    truncated = SimpleNamespace(
        content=[SimpleNamespace(type="text", text=truncated_text)],
        stop_reason="max_tokens",
        usage=SimpleNamespace(input_tokens=1200, output_tokens=2500),
    )
    client = _SequencedResearchClient([searched, truncated])

    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        result = app_module.run_climate_web_research(
            "Testland",
            "Water",
            {},
            client,
            assessment_id="assessment-diagnostic",
        )

    assert result["status"] == "failed"
    assert len(client.calls) == 2
    assert "outcome=structuring_diagnostic" in caplog.text
    assert "assessment_id=assessment-diagnostic" in caplog.text
    assert "stop_reason=max_tokens" in caplog.text
    assert "output_tokens=2500" in caplog.text
    assert "start_present=yes end_present=no" in caplog.text
    assert "json_status=incomplete" in caplog.text
    assert "gate_code=climate_research_failed" in caplog.text
    assert secret not in caplog.text


def test_climate_research_does_not_structure_insufficient_search_results():
    incomplete = SimpleNamespace(
        content=[
            SimpleNamespace(type="web_search_tool_result", content=[]),
            SimpleNamespace(type="text", text="No structured block."),
        ],
        stop_reason="max_tokens",
    )
    client = _SequencedResearchClient([incomplete, _valid_climate_response()])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Water",
        {},
        client,
    )

    assert result["status"] == "failed"
    assert len(client.calls) == 1


def test_climate_request_skips_when_parent_budget_is_exhausted():
    client = _SequencedResearchClient([_valid_climate_response()])
    ticks = iter([100.0, 100.0, 100.0])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Natural resources",
        {"project_elements": ["Landing sites"]},
        client,
        deadline=100.0,
        clock=lambda: next(ticks),
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 0
    assert client.calls == []


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

    assert client.calls[0]["timeout"] == 50.0


def test_climate_research_retries_one_transient_overload(monkeypatch):
    response = httpx.Response(
        529,
        request=httpx.Request(
            "POST", "https://api.anthropic.com/v1/messages"
        ),
    )
    overload = OverloadedError(
        "Service overloaded",
        response=response,
        body={"type": "error", "error": {"type": "overloaded_error"}},
    )
    client = _SequencedResearchClient([overload, _valid_climate_response()])
    delays = []
    monkeypatch.setattr(app_module.time, "sleep", delays.append)

    result = app_module.run_climate_web_research(
        "South Sudan", "Water", {}, client
    )

    assert result["status"] == "complete"
    assert result["attempts"] == 2
    assert len(client.calls) == 2
    assert delays == [2]


def test_climate_research_does_not_duplicate_a_timed_out_request():
    timeout = anthropic.APITimeoutError(
        request=httpx.Request(
            "POST", "https://api.anthropic.com/v1/messages"
        )
    )
    client = _SequencedResearchClient([timeout])

    result = app_module.run_climate_web_research(
        "South Sudan", "Water", {}, client
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 1
    assert len(client.calls) == 1


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
