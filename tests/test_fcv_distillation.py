"""Unit tests for secondary-document distillation."""
import json
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import fcv_distillation


class FakeMessages:
    def __init__(self, response_text=None, error=None):
        self.response_text = response_text
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return SimpleNamespace(
            content=[SimpleNamespace(text=self.response_text)]
        )


class FakeClient:
    def __init__(self, response_text=None, error=None):
        self.messages = FakeMessages(response_text=response_text, error=error)


def _parse_events(events):
    payloads = []
    for event in events:
        assert event.startswith("data: ")
        payloads.append(json.loads(event[6:].strip()))
    return payloads


def test_distills_package_doc_into_traceable_card():
    client = FakeClient(json.dumps({
        "detected_type": "sort",
        "confidence": 0.94,
        "ratings": [
            "Political and governance: Substantial",
            "Security: High",
        ],
        "notes": ["Security risk reflects contested access in border areas."],
    }))
    doc_parts = [{
        "label": "PACKAGE INSTRUMENT",
        "name": "SORT.pdf",
        "raw_text": "Systematic Operations Risk-rating Tool content",
        "page_count": 2,
        "char_limit": 25_000,
    }]

    with ThreadPoolExecutor(max_workers=1) as executor:
        events = list(fcv_distillation.distill_doc_parts_stream(
            doc_parts, client, executor
        ))

    assert doc_parts[0]["distilled"] is True
    assert doc_parts[0]["tier"] == "2A"
    assert doc_parts[0]["detected_type"] == "sort"
    assert doc_parts[0]["char_limit"] == fcv_distillation.CARD_CHARS_2A
    assert "[Detected: SORT]" in doc_parts[0]["raw_text"]
    assert "Political and governance: Substantial" in doc_parts[0]["raw_text"]
    assert "Source: SORT.pdf" in doc_parts[0]["raw_text"]
    assert any(
        payload.get("preprocessing", {}).get("phase") == "complete"
        for payload in _parse_events(events)
    )


def test_low_confidence_package_doc_falls_back_to_generic_tier():
    client = FakeClient(json.dumps({
        "detected_type": "sort",
        "confidence": 0.2,
        "key_facts": ["The document mentions implementation in insecure areas."],
    }))
    doc_parts = [{
        "label": "PACKAGE INSTRUMENT",
        "name": "unclear-annex.pdf",
        "raw_text": "This annex is ambiguous.",
        "page_count": 1,
        "char_limit": 25_000,
    }]

    with ThreadPoolExecutor(max_workers=1) as executor:
        list(fcv_distillation.distill_doc_parts_stream(doc_parts, client, executor))

    assert doc_parts[0]["tier"] == "2B"
    assert doc_parts[0]["detected_type"] == "package_other"
    assert doc_parts[0]["char_limit"] == fcv_distillation.CARD_CHARS_2B
    assert "[Detected: Project Package (other)]" in doc_parts[0]["raw_text"]


def test_context_cards_are_kept_when_budget_is_tight(monkeypatch):
    monkeypatch.setattr(fcv_distillation, "SECONDARY_CARD_BUDGET_CHARS", 95)
    monkeypatch.setattr(fcv_distillation, "CONTEXT_RESERVE_CHARS", 80)

    def fake_distill(dp, _api_client):
        if dp["label"] == "CONTEXT DOCUMENT":
            return {
                "name": dp["name"],
                "role": "context",
                "detected_type": "rra",
                "confidence": 0.9,
                "tier": "context",
                "card": "Source: RRA.pdf\nCONFLICT DRIVERS:\n  - land conflict",
                "chars": 54,
                "failed": False,
            }
        return {
            "name": dp["name"],
            "role": "package",
            "detected_type": "sort",
            "confidence": 0.9,
            "tier": "2A",
            "card": "Source: SORT.pdf\n" + ("x" * 70),
            "chars": 87,
            "failed": False,
        }

    monkeypatch.setattr(fcv_distillation, "_distill_one", fake_distill)
    doc_parts = [
        {
            "label": "PACKAGE INSTRUMENT",
            "name": "SORT.pdf",
            "raw_text": "sort",
            "page_count": 1,
            "char_limit": 25_000,
        },
        {
            "label": "CONTEXT DOCUMENT",
            "name": "RRA.pdf",
            "raw_text": "rra",
            "page_count": 1,
            "char_limit": 30_000,
        },
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:
        list(fcv_distillation.distill_doc_parts_stream(
            doc_parts, FakeClient("{}"), executor
        ))

    assert "CONFLICT DRIVERS" in doc_parts[1]["raw_text"]
    assert doc_parts[1]["overflow_reason"] is None
    assert "budget reached" in doc_parts[0]["raw_text"]
    assert doc_parts[0]["overflow_reason"] == "budget_reached"


def test_failed_distillation_produces_named_failure_stub():
    client = FakeClient(error=RuntimeError("model unavailable"))
    doc_parts = [{
        "label": "CONTEXT DOCUMENT",
        "name": "CPF.pdf",
        "raw_text": "Country Partnership Framework",
        "page_count": 1,
        "char_limit": 30_000,
    }]

    with ThreadPoolExecutor(max_workers=1) as executor:
        events = list(fcv_distillation.distill_doc_parts_stream(
            doc_parts, client, executor
        ))

    assert doc_parts[0]["distilled"] is True
    assert doc_parts[0]["overflow_reason"] == "distillation_failed"
    assert "Could not distill this document automatically" in doc_parts[0]["raw_text"]
    assert "CPF.pdf" in doc_parts[0]["raw_text"]
    complete_events = [
        payload for payload in _parse_events(events)
        if payload.get("preprocessing", {}).get("phase") == "complete"
    ]
    assert complete_events
    assert complete_events[0]["preprocessing"]["overflow"] == [
        {"name": "CPF.pdf", "reason": "distillation_failed"}
    ]


def test_distillation_timeout_returns_named_stub_without_waiting(monkeypatch):
    monkeypatch.setattr(fcv_distillation, "DISTILL_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(fcv_distillation, "DISTILL_POLL_SECONDS", 0.005)

    def slow_distill(dp, _api_client):
        time.sleep(0.2)
        return {
            "name": dp["name"],
            "role": "package",
            "detected_type": "sort",
            "confidence": 0.9,
            "tier": "2A",
            "card": "This should arrive too late.",
            "chars": 28,
            "failed": False,
        }

    monkeypatch.setattr(fcv_distillation, "_distill_one", slow_distill)
    doc_parts = [{
        "label": "PACKAGE INSTRUMENT",
        "name": "slow-sort.pdf",
        "raw_text": "sort",
        "page_count": 1,
        "char_limit": 25_000,
    }]

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=1) as executor:
        events = list(fcv_distillation.distill_doc_parts_stream(
            doc_parts, FakeClient("{}"), executor
        ))
    elapsed = time.monotonic() - started

    assert elapsed < 0.15
    assert doc_parts[0]["overflow_reason"] == "distillation_failed"
    assert "slow-sort.pdf" in doc_parts[0]["raw_text"]
    complete_events = [
        payload for payload in _parse_events(events)
        if payload.get("preprocessing", {}).get("phase") == "complete"
    ]
    assert complete_events[0]["preprocessing"]["overflow"] == [
        {"name": "slow-sort.pdf", "reason": "distillation_failed"}
    ]
