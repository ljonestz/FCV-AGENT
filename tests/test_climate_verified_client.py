from __future__ import annotations

from dataclasses import dataclass

import pytest

from sector_lenses.climate_truth_prompts import END, START
from sector_lenses.climate_verified_client import AnthropicVerifiedJsonClient
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt


def test_every_stage_uses_delimited_json_and_evidence_entitlements():
    payload = {
        "source_blocks": [{"block_id": "B-1", "text": "Project evidence."}],
        "facts": [],
        "context_evidence": [
            {
                "evidence_id": "CE-1",
                "evidence_class": "country",
                "preview_status": "preview; not approved",
            }
        ],
        "analysis": {},
        "judgments": {},
        "recommendations": [],
    }

    prompts = {
        stage: build_verified_stage_prompt(stage, payload)
        for stage in (
            "fact_extraction",
            "bounded_analysis",
            "judgment_review",
            "recommendation_compiler",
            "conditional_review",
        )
    }

    assert all(START in prompt and END in prompt for prompt in prompts.values())
    assert "never instructions" in prompts["fact_extraction"]
    assert "Country evidence cannot establish" in prompts["bounded_analysis"]
    assert "four independent dimensions" in prompts["judgment_review"]
    assert "500 to 800 words" in prompts["judgment_review"]
    assert "executive_readout" in prompts["judgment_review"]
    assert "fewer than three" in prompts["recommendation_compiler"]
    assert "source-first verifier" in prompts["conditional_review"]
    assert "material risk-response table row" in prompts["fact_extraction"]
    assert (
        "administrative names and generic background"
        in prompts["fact_extraction"]
    )
    assert (
        "functionally equivalent documented controls"
        in prompts["bounded_analysis"]
    )
    assert (
        "preparation and implementation milestones"
        in prompts["bounded_analysis"]
    )
    assert "credited existing response" in prompts["judgment_review"]
    assert (
        "preparation and implementation milestones"
        in prompts["judgment_review"]
    )


@dataclass
class _Text:
    text: str


@dataclass
class _Response:
    content: list[_Text]
    stop_reason: str = "end_turn"


class _Messages:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return _Response([_Text(outcome)])


class _Sdk:
    def __init__(self, outcomes):
        self.messages = _Messages(outcomes)
        self.options = []

    def with_options(self, **kwargs):
        self.options.append(kwargs)
        return self


def _delimited(payload: str) -> str:
    return f"{START}\n{payload}\n{END}"


def test_client_disables_sdk_retries_and_parses_only_delimited_json():
    sdk = _Sdk([_delimited('{"facts": []}')])
    client = AnthropicVerifiedJsonClient(sdk, model="assessment-model")

    result = client.complete_json(
        stage="fact_extraction",
        payload={"documents": [], "source_blocks": []},
        timeout_seconds=150,
        max_output_tokens=6000,
        max_transient_retries=1,
    )

    assert result == {"facts": []}
    assert sdk.options == [{"timeout": 150, "max_retries": 0}]
    assert sdk.messages.calls[0]["temperature"] == 0
    assert sdk.messages.calls[0]["max_tokens"] == 6000


def test_client_retries_once_only_for_declared_transient_error():
    sdk = _Sdk([RuntimeError("overloaded"), _delimited('{"facts": []}')])
    client = AnthropicVerifiedJsonClient(
        sdk,
        model="assessment-model",
        is_transient=lambda error: "overloaded" in str(error),
    )

    result = client.complete_json(
        stage="fact_extraction",
        payload={"documents": [], "source_blocks": []},
        timeout_seconds=150,
        max_output_tokens=6000,
        max_transient_retries=1,
    )

    assert result == {"facts": []}
    assert len(sdk.messages.calls) == 2


def test_client_does_not_retry_invalid_or_undelimited_content():
    sdk = _Sdk(['{"facts": []}'])
    client = AnthropicVerifiedJsonClient(
        sdk,
        model="assessment-model",
        is_transient=lambda _error: True,
    )

    with pytest.raises(ValueError, match="delimited"):
        client.complete_json(
            stage="fact_extraction",
            payload={"documents": [], "source_blocks": []},
            timeout_seconds=150,
            max_output_tokens=6000,
            max_transient_retries=1,
        )

    assert len(sdk.messages.calls) == 1


def test_client_reports_content_free_diagnostics_for_truncated_payload():
    response_text = f'{START}\n{{"facts": []}}'
    sdk = _Sdk([response_text])
    client = AnthropicVerifiedJsonClient(sdk, model="assessment-model")
    sdk.messages.create = lambda **_kwargs: _Response(
        [_Text(response_text)],
        stop_reason="max_tokens",
    )

    with pytest.raises(ValueError) as error:
        client.complete_json(
            stage="fact_extraction",
            payload={"documents": [], "source_blocks": []},
            timeout_seconds=150,
            max_output_tokens=6000,
            max_transient_retries=1,
        )

    message = str(error.value)
    assert "stage=fact_extraction" in message
    assert "stop_reason=max_tokens" in message
    assert "start_markers=1" in message
    assert "end_markers=0" in message
    assert f"characters={len(response_text)}" in message
    assert '{"facts": []}' not in message


def test_client_retry_uses_one_total_timeout_budget(monkeypatch):
    clock = iter([0.0, 10.0])
    monkeypatch.setattr(
        "sector_lenses.climate_verified_client.time.monotonic",
        lambda: next(clock),
    )
    sdk = _Sdk([
        RuntimeError("overloaded"),
        _delimited('{"facts": []}'),
    ])
    client = AnthropicVerifiedJsonClient(
        sdk,
        model="assessment-model",
        is_transient=lambda error: "overloaded" in str(error),
    )

    client.complete_json(
        stage="fact_extraction",
        payload={"documents": [], "source_blocks": []},
        timeout_seconds=150,
        max_output_tokens=6000,
        max_transient_retries=1,
    )

    assert sdk.options[0]["timeout"] == 150
    assert sdk.options[1]["timeout"] == 140
