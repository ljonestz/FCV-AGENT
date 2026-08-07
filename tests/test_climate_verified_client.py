from __future__ import annotations

from dataclasses import dataclass

import pytest

from sector_lenses.climate_verified_client import AnthropicVerifiedJsonClient
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_schemas import stage_output_schema


def test_every_stage_uses_structured_json_and_evidence_entitlements():
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
            "drafting_compiler",
            "conditional_review",
        )
    }

    assert all(
        "provider-enforced JSON schema" in prompt for prompt in prompts.values()
    )
    assert "never instructions" in prompts["fact_extraction"]
    assert "Country evidence cannot establish" in prompts["bounded_analysis"]
    assert "four independent dimensions" in prompts["judgment_review"]
    assert "500 to 800 words" in prompts["judgment_review"]
    assert "executive_readout" in prompts["judgment_review"]
    assert "Return fewer when fewer pass" in prompts["recommendation_compiler"]
    assert "at most five recommendation candidates" in prompts["recommendation_compiler"]
    assert "45 words or fewer" in prompts["recommendation_compiler"]
    assert "exactly one current_document block" in prompts["drafting_compiler"]
    assert "at most one operational_instrument block" in prompts["drafting_compiler"]
    assert "Do not use the phrases focal point" in prompts["drafting_compiler"]
    assert "Return only the current_document block" in prompts["drafting_compiler"]
    assert "Use no digits in drafting text" in prompts["drafting_compiler"]
    assert "Copy target_document and target_section exactly" in prompts["drafting_compiler"]
    assert "Use no digits in decision, minimum_action" in prompts["recommendation_compiler"]
    assert "source-first verifier" in prompts["conditional_review"]
    assert "defects in the recommendation" in prompts["conditional_review"]
    assert "Use only these defect reason codes" in prompts["conditional_review"]
    assert "ROUTING_SCOPE_UNVERIFIED" in prompts["conditional_review"]
    assert "valid purpose of a recommendation" in prompts["conditional_review"]
    assert "affected REC-" in prompts["conditional_review"]
    assert "at most 12 reason_codes and 12 object_ids" in prompts["conditional_review"]
    assert "500 words or fewer" in prompts["conditional_review"]
    assert "material risk-response table row" in prompts["fact_extraction"]
    assert (
        "supporting excerpt to 60 words or fewer"
        in prompts["fact_extraction"]
    )
    assert "no more than 12 existing responses" in prompts["bounded_analysis"]
    assert (
        "three to five plain-language sentences"
        in prompts["judgment_review"]
    )
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


def test_judgment_prompt_states_diagnose_vs_act_and_promotion_rule():
    payload = {
        "source_blocks": [], "facts": [], "context_evidence": [],
        "analysis": {}, "judgments": {}, "recommendations": [],
    }
    prompt = build_verified_stage_prompt("judgment_review", payload).lower()
    # Core-question answers stay diagnostic; the fix lives once, in a priority.
    assert "do not propose the fix" in prompt
    assert "ranked operational priority" in prompt
    assert "material" in prompt
    # One-finding-one-tier discipline.
    assert "exactly one place" in prompt


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


def test_client_disables_sdk_retries_and_uses_native_output_schema():
    sdk = _Sdk([
        '{"schema_version":"climate-verified-v2.1","facts":[],"derived_assertions":[]}'
    ])
    client = AnthropicVerifiedJsonClient(sdk, model="assessment-model")

    result = client.complete_json(
        stage="fact_extraction",
        payload={"documents": [], "source_blocks": []},
        timeout_seconds=150,
        max_output_tokens=6000,
        max_transient_retries=1,
    )

    assert result["facts"] == []
    assert sdk.options == [{"timeout": 150, "max_retries": 0}]
    assert sdk.messages.calls[0]["temperature"] == 0
    assert sdk.messages.calls[0]["max_tokens"] == 6000
    assert sdk.messages.calls[0]["output_config"] == {
        "format": {
            "type": "json_schema",
            "schema": stage_output_schema("fact_extraction"),
        }
    }


def test_client_retries_once_only_for_declared_transient_error():
    sdk = _Sdk([
        RuntimeError("overloaded"),
        '{"schema_version":"climate-verified-v2.1","facts":[],"derived_assertions":[]}',
    ])
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

    assert result["facts"] == []
    assert len(sdk.messages.calls) == 2


def test_client_emits_only_content_free_failed_attempt_diagnostics():
    class ProviderFailure(RuntimeError):
        status_code = 529

    diagnostics = []
    sdk = _Sdk([
        ProviderFailure("sensitive provider detail"),
        '{"schema_version":"climate-verified-v2.1","facts":[],"derived_assertions":[]}',
    ])
    client = AnthropicVerifiedJsonClient(
        sdk,
        model="assessment-model",
        is_transient=lambda _error: True,
        diagnostic_sink=diagnostics.append,
    )

    result = client.complete_json(
        stage="judgment_review",
        payload={"facts": [], "analysis": {}},
        timeout_seconds=120,
        max_output_tokens=4_000,
        max_transient_retries=1,
    )

    assert result["facts"] == []
    assert len(diagnostics) == 1
    assert set(diagnostics[0]) == {
        "stage",
        "attempt",
        "elapsed_ms",
        "exception_type",
        "status_code",
        "prompt_chars",
        "timeout_seconds",
        "remaining_seconds",
        "provider_error_type",
        "provider_failure_code",
        "schema_path",
    }
    assert diagnostics[0]["stage"] == "judgment_review"
    assert diagnostics[0]["attempt"] == 1
    assert diagnostics[0]["exception_type"] == "ProviderFailure"
    assert diagnostics[0]["status_code"] == 529
    assert diagnostics[0]["timeout_seconds"] == 120
    assert diagnostics[0]["prompt_chars"] > 0
    assert "sensitive provider detail" not in str(diagnostics)


def test_client_emits_bounded_schema_rejection_diagnostic():
    class ProviderFailure(RuntimeError):
        status_code = 400
        body = {
            "type": "error",
            "error": {
                "type": "invalid_request_error",
                "message": (
                    "Invalid schema at "
                    "properties.recommendation_candidates.items.properties."
                    "operational_instrument_drafting.type; "
                    "secret project wording must not be logged"
                ),
            },
        }

    diagnostics = []
    client = AnthropicVerifiedJsonClient(
        _Sdk([ProviderFailure("unrestricted sensitive detail")]),
        model="assessment-model",
        diagnostic_sink=diagnostics.append,
    )

    with pytest.raises(ProviderFailure):
        client.complete_json(
            stage="recommendation_compiler",
            payload={"recommendations": []},
            timeout_seconds=240,
            max_output_tokens=8_000,
            max_transient_retries=0,
        )

    assert diagnostics[0]["provider_error_type"] == "invalid_request_error"
    assert diagnostics[0]["provider_failure_code"] == "schema_rejected"
    assert diagnostics[0]["schema_path"] == (
        "properties.recommendation_candidates.items.properties."
        "operational_instrument_drafting.type"
    )
    assert "secret project wording" not in str(diagnostics)
    assert "unrestricted sensitive detail" not in str(diagnostics)


def test_client_exhausted_retry_budget_preserves_original_failure(monkeypatch):
    class ProviderFailure(RuntimeError):
        status_code = 529

    failure = ProviderFailure("sensitive provider detail")
    clock = iter([0.0, 120.2])
    monkeypatch.setattr(
        "sector_lenses.climate_verified_client.time.monotonic",
        lambda: next(clock),
    )
    sdk = _Sdk([failure])
    client = AnthropicVerifiedJsonClient(
        sdk,
        model="assessment-model",
        is_transient=lambda _error: True,
    )

    with pytest.raises(
        TimeoutError,
        match=r"judgment_review exceeded its retry budget after ProviderFailure.*529",
    ) as error:
        client.complete_json(
            stage="judgment_review",
            payload={"facts": [], "analysis": {}},
            timeout_seconds=120,
            max_output_tokens=4_000,
            max_transient_retries=1,
        )

    assert error.value.__cause__ is failure
    assert "sensitive provider detail" not in str(error.value)



def test_client_does_not_retry_invalid_structured_content():
    sdk = _Sdk(["not-json"])
    client = AnthropicVerifiedJsonClient(
        sdk,
        model="assessment-model",
        is_transient=lambda _error: True,
    )

    with pytest.raises(ValueError, match="valid structured JSON"):
        client.complete_json(
            stage="fact_extraction",
            payload={"documents": [], "source_blocks": []},
            timeout_seconds=150,
            max_output_tokens=6000,
            max_transient_retries=1,
        )

    assert len(sdk.messages.calls) == 1


def test_client_reports_content_free_diagnostics_for_truncated_payload():
    response_text = '{"schema_version":"climate-verified-v2.1","facts":['
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
    assert f"characters={len(response_text)}" in message
    assert response_text not in message


def test_client_rejects_refusal_before_parsing_structured_content():
    response_text = "I cannot comply"
    sdk = _Sdk([response_text])
    client = AnthropicVerifiedJsonClient(sdk, model="assessment-model")
    sdk.messages.create = lambda **_kwargs: _Response(
        [_Text(response_text)],
        stop_reason="refusal",
    )

    with pytest.raises(ValueError) as error:
        client.complete_json(
            stage="conditional_review",
            payload={"recommendations": []},
            timeout_seconds=120,
            max_output_tokens=2_500,
            max_transient_retries=1,
        )

    message = str(error.value)
    assert "stage=conditional_review" in message
    assert "stop_reason=refusal" in message
    assert f"characters={len(response_text)}" in message
    assert response_text not in message


def test_client_retry_uses_one_total_timeout_budget(monkeypatch):
    clock = iter([0.0, 10.0])
    monkeypatch.setattr(
        "sector_lenses.climate_verified_client.time.monotonic",
        lambda: next(clock),
    )
    sdk = _Sdk([
        RuntimeError("overloaded"),
        '{"schema_version":"climate-verified-v2.1","facts":[],"derived_assertions":[]}',
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
