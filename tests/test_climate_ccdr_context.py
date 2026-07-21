"""Tests for optional, validated CCDR country context."""

from types import SimpleNamespace

import app as app_module
from sector_lenses.context import (
    CCDR_CONTEXT_END,
    CCDR_CONTEXT_START,
    extract_ccdr_context,
    has_uploaded_ccdr,
)


def test_ccdr_context_accepts_verified_world_bank_metadata():
    text = (
        "Research brief\n" + CCDR_CONTEXT_START +
        '{"available":true,"title":"Country Climate and Development Report",'
        '"publication_date":"2025","url":"https://www.worldbank.org/example",'
        '"location":"Chapter 3","summary":"Drought affects northern livelihoods."}' +
        CCDR_CONTEXT_END
    )

    visible, context = extract_ccdr_context(text, "Exampleland")

    assert visible == "Research brief"
    assert context["id"] == "context-ccdr"
    assert context["lens_id"] == "climate"


def test_ccdr_context_rejects_non_world_bank_url():
    text = CCDR_CONTEXT_START + (
        '{"available":true,"title":"Fake CCDR","publication_date":"2025",'
        '"url":"https://example.com/fake","location":"p. 1","summary":"Text"}'
    ) + CCDR_CONTEXT_END

    visible, context = extract_ccdr_context(text, "Exampleland")

    assert visible == ""
    assert context == {}


def test_uploaded_ccdr_suppresses_public_lookup():
    doc_parts = [{
        "name": "Country Climate and Development Report.pdf",
        "raw_text": "Country Climate and Development Report",
    }]

    assert has_uploaded_ccdr(doc_parts) is True


class _ResearchClient:
    def __init__(self, response_text):
        self.kwargs = None
        self.beta = SimpleNamespace(
            messages=SimpleNamespace(create=self._create)
        )
        self.response_text = response_text

    def _create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(content=[
            SimpleNamespace(type="text", text=self.response_text)
        ])


def test_research_reuses_one_call_and_returns_hidden_ccdr_context():
    response = (
        "Visible research" + CCDR_CONTEXT_START +
        '{"available":true,"title":"Example CCDR","publication_date":"2025",'
        '"url":"https://openknowledge.worldbank.org/example","location":"p. 4",'
        '"summary":"Drought affects project areas."}' + CCDR_CONTEXT_END
    )
    client = _ResearchClient(response)

    result = app_module.run_fcv_web_research(
        "Exampleland", "Water", client, include_ccdr=True
    )

    assert result["brief"] == "Visible research"
    assert result["ccdr_context"]["id"] == "context-ccdr"
    assert client.kwargs["tools"][0]["max_uses"] == 5
    assert CCDR_CONTEXT_START in client.kwargs["messages"][0]["content"]


def test_core_research_keeps_four_searches_and_no_ccdr_instruction():
    client = _ResearchClient("Visible research")

    result = app_module.run_fcv_web_research(
        "Exampleland", "Water", client
    )

    assert result["ccdr_context"] == {}
    assert client.kwargs["tools"][0]["max_uses"] == 4
    assert CCDR_CONTEXT_START not in client.kwargs["messages"][0]["content"]


def test_lookup_gate_requires_active_climate_and_no_uploaded_ccdr():
    climate = [{"id": "climate", "version": "1.0.0"}]
    uploaded = [{
        "name": "Example Country Climate and Development Report.pdf",
        "raw_text": "CCDR",
    }]

    assert app_module.should_include_ccdr_context(climate, []) is True
    assert app_module.should_include_ccdr_context([], []) is False
    assert app_module.should_include_ccdr_context(climate, uploaded) is False


def test_research_cache_separates_core_and_ccdr_runs():
    core = app_module.research_cache_key(" Exampleland ", " Water ", False)
    climate = app_module.research_cache_key("Exampleland", "Water", True)

    assert core == "exampleland::water::ccdr=0"
    assert climate == "exampleland::water::ccdr=1"


def test_ccdr_prompt_context_is_optional_and_labels_context_evidence():
    source = {
        "id": "context-ccdr",
        "title": "Example CCDR",
        "summary": "Drought affects project areas.",
    }

    block = app_module.build_ccdr_prompt_context([source])

    assert "OPTIONAL CCDR CONTEXT" in block
    assert "contextual evidence rather than project evidence" in block
    assert "Drought affects project areas." in block
    assert app_module.build_ccdr_prompt_context([]) == ""
