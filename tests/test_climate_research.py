"""Tests for bounded, validated Climate-FCV research context."""

import json
from types import SimpleNamespace

import anthropic
import httpx

import app as app_module
from sector_lenses.research import (
    CLIMATE_RESEARCH_END,
    CLIMATE_RESEARCH_START,
    build_climate_research_prompt,
    extract_climate_research_bundle,
    format_climate_research_context,
    normalize_climate_research_bundle,
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
    return SimpleNamespace(content=[
        SimpleNamespace(
            type="text",
            text=(
                CLIMATE_RESEARCH_START
                + json.dumps(_valid_bundle())
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
