"""Tests for bounded, validated Climate-FCV research context."""

import json
import threading
from concurrent.futures import Future
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import anthropic
import httpx
import pytest
from anthropic._exceptions import OverloadedError

import app as app_module
import sector_lenses.research as research_module
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


def _bank_packet_for_search():
    return {
        "bank_status": "ok",
        "content_version": "approved-global-1",
        "country_iso3": "SSD",
        "sources": [{
            "source_id": "SSD-SRC-001",
            "title": "South Sudan climate assessment",
            "organization": "World Bank",
            "publication_date": "2018",
            "publication_date_basis": "published_on",
            "temporal_coverage": "Observations through 2015",
            "url": "https://openknowledge.worldbank.org/ssd-climate",
        }],
        "evidence_records": [{
            "evidence_id": "SSD-E-001",
            "compact_statement": "Observed rainfall is highly variable.",
            "evidence_status": "observed",
            "evidence_class": "climate_observation",
            "scenario": "historical",
            "time_horizons": ["current-near-term"],
            "confidence": "medium",
            "uncertainty": "Station coverage is limited outside major towns.",
            "geographies": ["Jonglei"],
            "affected_groups": ["Rural households"],
            "source_refs": [{
                "source_id": "SSD-SRC-001",
                "locator": "Chapter 2, p. 14",
            }],
        }],
        "pathways": [],
        "country_profile": {
            "coverage": [{
                "topic": "national climate evidence",
                "summary": "National-scale evidence; district coverage varies.",
            }],
            "known_gaps": [{
                "topic": "local flood mapping",
                "summary": "Current district flood mapping was not identified.",
            }],
        },
    }


def _valid_two_source_bundle():
    bundle = _valid_bundle()
    bundle["sources"].append({
        "id": "climate-source-2",
        "source_type": "scientific",
        "title": "Peer-reviewed flood study",
        "url": "https://ipcc.ch/example-flood-study",
        "publication_date": "2024",
    })
    bundle["claims"][0]["source_ids"].append("climate-source-2")
    return bundle


def test_passage_registry_preserves_complementary_quotes_and_owns_proof():
    from sector_lenses.research import resolve_climate_passage_selections
    content = [{"type": "text", "text": "Search narrative", "citations": [
        {"url": "https://www.worldbank.org/report", "title": "Burundi climate report", "cited_text": "Flooding affects access in Burundi."},
        {"url": "https://www.worldbank.org/report", "title": "Burundi climate report", "cited_text": "Drought affects livelihoods in Burundi."},
    ]}]
    packet = build_climate_evidence_packet(content, {"beneficiary_countries": ["Burundi"], "project_elements": ["Landing-site rehabilitation"]})
    assert len(packet["passages"]) == 2
    labels = {key: value for key, value in _valid_bundle()["claims"][0].items()
              if key not in {"id", "claim", "source_ids"}}
    labels["geographies"] = ["Burundi"]
    result = resolve_climate_passage_selections({"selections": [
        {**labels, "passage_id": packet["passages"][1]["id"], "claim": "Invented claim", "url": "https://attacker.example"},
        {**labels, "passage_id": "unknown"},
    ]}, packet)
    # All beneficiaries covered, so complete even though one selection id was invented.
    assert result["status"] == "complete"
    assert len(result["claims"]) == 1
    assert result["claims"][0]["claim"] == "Drought affects livelihoods in Burundi."
    assert result["sources"][0]["url"] == "https://www.worldbank.org/report"
    assert result["coverage_countries"] == ["Burundi"]


def test_passage_registry_does_not_claim_uncovered_country_or_accept_long_proof():
    from sector_lenses.research import resolve_climate_passage_selections
    packet = build_climate_evidence_packet([{"type": "text", "citations": [
        {"url": "https://www.worldbank.org/report", "title": "Burundi climate report", "cited_text": "Flooding affects access in Burundi."},
        {"url": "https://www.worldbank.org/report", "title": "Burundi climate report", "cited_text": "Long " * 320},
    ]}], {"beneficiary_countries": ["Burundi", "DRC"], "project_elements": ["Landing-site rehabilitation"]})
    assert len(packet["passages"]) == 1
    labels = _valid_bundle()["claims"][0]
    labels["geographies"] = ["Burundi"]
    result = resolve_climate_passage_selections({"selections": [
        {**labels, "passage_id": packet["passages"][0]["id"], "coverage_countries": ["DRC"]},
    ]}, packet)
    assert result["status"] == "partial"
    assert result["coverage_countries"] == ["Burundi"]
    assert result["uncovered_countries"] == ["DRC"]


def test_packet_admits_truncated_and_unbalanced_source_quotes():
    # The packet admits any safe cited text; the resolver (below) still refuses
    # truncated or unbalanced excerpts as grounding.
    truncated_gdp = (
        "The largest climate impacts on GDP were heat stress effects on labor, "
        "impacts on livestock production,. and flood impacts on transport "
        "infrastructure...."
    )
    truncated_displacement = (
        "By Q2 2026, however, conflict accounted for\n\n52,661 people, or 80 per "
        "cent of recorded displacement, followed by drought with 11,190 people, "
        "or 17 per..."
    )
    malformed_quotes = [
        truncated_gdp,
        truncated_displacement,
        "In Somalia, reported losses reached 42 per cent (with district variation.",
        "In Somalia, reported losses reached 42 per cent [across districts.",
    ]
    packet = build_climate_evidence_packet([{
        "type": "text",
        "citations": [
            {"url": f"https://www.worldbank.org/report-{index}",
             "title": "Somalia climate report", "cited_text": quote}
            for index, quote in enumerate(malformed_quotes)
        ],
    }], {"beneficiary_countries": ["Somalia"]})

    assert [p["excerpt"] for p in packet["passages"]] == malformed_quotes
    assert "missing_quote" not in packet["passage_diagnostics"]
    assert packet["passage_diagnostics"]["admitted"] == 4


def test_passage_resolver_admits_unbalanced_quote_in_supplied_packet():
    from sector_lenses.research import resolve_climate_passage_selections

    packet = {
        "passages": [{
            "id": "CP-001",
            "url": "https://www.worldbank.org/report",
            "title": "Somalia climate report",
            "publication_date": "2025",
            "excerpt": "In Somalia, modeled GDP losses reach 8 per cent (under SSP5-8.5.",
        }],
        "project_profile": {
            "project_elements": ["Landing-site rehabilitation"],
            "beneficiary_countries": ["Somalia"],
        },
    }
    labels = {key: value for key, value in _valid_bundle()["claims"][0].items()
              if key not in {"id", "claim", "source_ids"}}
    labels["project_elements"] = ["Landing-site rehabilitation"]

    result = resolve_climate_passage_selections({"selections": [{
        **labels, "passage_id": "CP-001", "geographies": ["Somalia"],
    }]}, packet)

    assert [c["claim"] for c in result["claims"]] == [packet["passages"][0]["excerpt"]]
    assert result["passage_diagnostics"] == {
        "received_count": 1,
        "selected_count": 1,
        "invalid_selection_count": 0,
        "admitted_claim_count": 1,
    }


def test_passage_resolver_admits_title_only_geography_and_keeps_controls():
    from sector_lenses.research import resolve_climate_passage_selections

    quotes = [
        ("https://www.worldbank.org/title-only", "Somalia climate report",
         "Under the high-emissions scenario, modeled GDP losses could reach 8 per cent by 2050; this is a projection, not an observed loss."),
        ("https://www.worldbank.org/projection", "Somalia climate report",
         "In Somalia, under the high-emissions scenario (SSP5-8.5), modeled GDP losses could reach 8 per cent by 2050; this is a projection, not an observed loss."),
        ("https://www.un.org/banadir", "Somalia displacement update",
         "In Banadir, Somalia, conflict accounted for 52,661 people, or 80 per cent of recorded displacement in Q2 2026."),
    ]
    packet = build_climate_evidence_packet([{
        "type": "text",
        "citations": [
            {"url": url, "title": title, "cited_text": quote}
            for url, title, quote in quotes
        ],
    }], {
        "beneficiary_countries": ["Somalia"],
        "project_elements": ["Landing-site rehabilitation"],
    })
    labels = {key: value for key, value in _valid_bundle()["claims"][0].items()
              if key not in {"id", "claim", "source_ids"}}
    labels["project_elements"] = ["Landing-site rehabilitation"]
    selections = [{
        **labels,
        "passage_id": passage["id"],
        "geographies": ["Banadir" if "banadir" in passage["url"] else "Somalia"],
        "evidence_status": "projected",
    } for passage in packet["passages"]]

    result = resolve_climate_passage_selections({"selections": selections}, packet)

    assert result["passage_diagnostics"] == {
        "received_count": 3,
        "selected_count": 3,
        "invalid_selection_count": 0,
        "admitted_claim_count": 3,
    }
    assert {claim["claim"] for claim in result["claims"]} == {q[2] for q in quotes}
    assert result["status"] == "complete"


def test_insufficient_proof_is_retained_for_inspection_but_not_admitted_grounding(monkeypatch):
    bundle = _valid_bundle()
    bundle["status"] = "failed"
    bundle["claims"][0]["source_excerpt"] = bundle["claims"][0]["claim"]
    monkeypatch.setattr(app_module, "load_climate_bank", lambda: object())
    monkeypatch.setattr(app_module, "materialize_bank_manifest", lambda *_args: {
        "bank_status": "unavailable", "warning_code": "bank_country_unavailable",
    })
    grounding, retained = app_module.resolve_climate_grounding({}, bundle)
    assert len(retained["claims"]) == 1
    assert retained["status"] == "partial"
    assert retained["warning_code"] == "climate_research_insufficient"
    assert grounding["research_status"] == "rejected"
    assert not grounding.get("context_evidence")
    assert format_climate_research_context(retained) == ""
    state = app_module.AnalysisState.from_payload({"active_lenses": ["climate"]})
    prompt = app_module.build_lens_stage_context(state, 2, climate_research=retained)["prompt"]
    assert retained["claims"][0]["claim"] not in prompt


def test_passage_selection_drops_invented_project_element_and_replaces_invented_geography():
    from sector_lenses.research import resolve_climate_passage_selections
    packet = build_climate_evidence_packet([{"type": "text", "citations": [
        {"url": "https://worldbank.org/report", "title": "Burundi report", "cited_text": "Flooding affects access in Burundi."},
    ]}], {"project_elements": ["Component 3"], "country": "Burundi", "beneficiary_countries": ["Burundi"]})
    labels = {**_valid_bundle()["claims"][0], "passage_id": "CP-001", "geographies": ["Burundi"]}
    # An invented project element is dropped, not admitted and not fatal.
    result = resolve_climate_passage_selections({"selections": [
        {**labels, "project_elements": ["Invented irrigation component"]}]}, packet)
    assert result["status"] == "complete"
    assert result["claims"][0]["project_elements"] == []
    assert result["claims"][0]["geographies"] == ["Burundi"]
    # Relevance follows the project countries; an invented place label is replaced.
    result = resolve_climate_passage_selections({"selections": [
        {**labels, "project_elements": ["Component 3"], "geographies": ["Upper Nile"]}]}, packet)
    assert result["claims"][0]["project_elements"] == ["Component 3"]
    assert result["claims"][0]["geographies"] == ["Burundi"]


def test_invented_geography_label_replaced_by_matched_country():
    packet = _admission_packet("https://www.reuters.com/x", "Floods hit Kenya's Tana River basin.")
    claim = _resolve(packet, geographies=["Uganda", "Tana River"])["claims"][0]
    assert claim["geographies"] == ["Tana River"]
    claim = _resolve(packet, geographies=["Uganda"])["claims"][0]
    assert claim["geographies"] == ["Kenya"]
    context = _admission_packet("https://www.reuters.com/x", "Drought grips East Africa this season.")
    # Context-only material never inherits the project country as its geography.
    assert _resolve(context, geographies=["Uganda"])["claims"][0]["geographies"] == []


def test_normalizer_derives_trust_tier_and_type_from_url_only():
    from live_source_policy import CAUTION_NOTE
    from sector_lenses.research import verify_climate_research_claims
    url = "https://somesite.example/x"
    raw = {"status": "partial",
           "sources": [{"id": "s1", "url": url, "title": "T", "trust_tier": "standard",
                        "source_type": "world-bank"}],
           "claims": [{"id": "c1", "claim": "Floods hit Kenya.", "source_excerpt": "Floods hit Kenya.",
                       "source_ids": ["s1"]}]}
    bundle = normalize_climate_research_bundle(raw)
    assert bundle["sources"][0]["trust_tier"] == "caution"
    assert bundle["sources"][0]["source_type"] == "other"
    content = [SimpleNamespace(type="text", text="n", citations=[SimpleNamespace(
        url=url, title="T", cited_text="Floods hit Kenya.")])]
    kept = verify_climate_research_claims(bundle, content)
    assert len(kept["claims"]) == 1
    assert CAUTION_NOTE in kept["claims"][0]["evidence_gap"]
    wb = normalize_climate_research_bundle({"status": "partial", "sources": [
        {"id": "s1", "url": "https://openknowledge.worldbank.org/x", "title": "T", "source_type": "ccdr"}],
        "claims": raw["claims"]})
    assert wb["sources"][0]["source_type"] == "ccdr"


def test_project_labels_keep_parent_components_before_subcomponents():
    from sector_lenses.research import build_climate_project_elements
    labels = build_climate_project_elements(" ".join(
        [f"Subcomponent 1.{index}" for index in range(1, 15)] + ["Component 3", "Component 1"]))
    assert labels[:2] == ["Component 3", "Component 1"]


def test_source_labels_match_whole_words_and_keep_congo_countries_distinct():
    from sector_lenses.research import _source_label_matches
    assert not _source_label_matches("land", "Floods affect landing sites.")
    assert not _source_label_matches("a", "Burundi climate report")
    assert _source_label_matches("Burundi", "Flooding in Burundi.")
    assert _source_label_matches("DRC", "Democratic Republic of Congo report")
    assert not _source_label_matches("Republic of Congo", "Democratic Republic of Congo report")


def test_country_homepage_cannot_impersonate_a_project_pid():
    raw = _valid_bundle()
    raw["sources"].append({"id": "fake-pid", "source_type": "current-operations",
                           "title": "Project Information Document (P174814)",
                           "url": "https://www.worldbank.org/ext/en/country/burundi",
                           "publication_date": "313 days ago"})
    raw["claims"].append({**raw["claims"][0], "id": "unsupported", "source_ids": ["fake-pid"]})
    result = normalize_climate_research_bundle(raw)
    assert len(result["sources"]) == 1 and len(result["claims"]) == 1


def test_country_homepage_guard_uses_complete_hostname_boundaries():
    cases = [
        ("https://worldbank.org/en/country/burundi", "Project Information Document", False),
        ("https://www.worldbank.org/ext/en/country/burundi", "Project Information Document", False),
        ("https://WWW.WORLDBANK.ORG/en/country/burundi/overview", "Country overview", True),
        # Non-allow-listed hosts are admitted (trust is a label); the homepage
        # guard itself only applies to genuine worldbank.org hostnames.
        ("https://notworldbank.org/en/country/burundi", "Project Information Document", True),
        ("https://worldbank.org.attacker.example/en/country/burundi", "Project Information Document", True),
        ("https://attacker.example/worldbank.org/en/country/burundi", "Project Information Document", True),
        ("https://worldbank.org@attacker.example/en/country/burundi", "Country overview", False),
    ]
    for url, title, accepted in cases:
        raw = _valid_bundle()
        raw["sources"][0].update(url=url, title=title)
        result = normalize_climate_research_bundle(raw)
        assert bool(result["sources"]) is accepted, url
        assert bool(result["claims"]) is accepted, url


def test_relative_page_age_is_not_a_publication_date():
    raw = _valid_bundle()
    raw["sources"][0]["publication_date"] = "313 days ago"
    result = normalize_climate_research_bundle(raw)
    assert result["sources"][0]["publication_date"] == ""


def _climate_bank_plan():
    return {
        "country": "South Sudan",
        "sector": "Fisheries",
        "core": {"max_tokens": 4000, "max_uses": 3},
        "climate": {"enabled": True},
        "project_profile": {
            "documents": ["South Sudan PCN.docx"],
            "document_excerpt": "Jonglei landing sites BFMU seasonal users",
        },
        "country_scope": "single",
        "resolved_country_count": 1,
    }


def test_bank_selection_precedes_live_research(monkeypatch):
    calls = []
    caller_thread = threading.get_ident()
    monkeypatch.setattr(
        app_module,
        "load_climate_bank",
        lambda: calls.append(("load", threading.get_ident())) or object(),
    )
    monkeypatch.setattr(
        app_module,
        "select_bank_manifest",
        lambda *args, **kwargs: (
            calls.append(("select", threading.get_ident()))
            or {
                "bank_status": "ok",
                "warning_code": "",
                "schema_version": "1.0.0",
                "content_version": "test-1",
                "country_iso3": "SSD",
                "evidence_ids": ["SSD-E-001"],
                "pathway_ids": ["SSD-P-001"],
            }
        ),
    )
    monkeypatch.setattr(
        app_module,
        "run_fcv_web_research",
        lambda *args, **kwargs: {"brief": ""},
    )
    monkeypatch.setattr(
        app_module,
        "run_climate_web_research",
        lambda *args, **kwargs: (
            calls.append(("research", threading.get_ident()))
            or _valid_bundle()
        ),
    )
    monkeypatch.setattr(app_module, "get_research_client", lambda: object())
    app_module._research_cache.clear()

    result = list(
        app_module._iter_stage1_research(
            _climate_bank_plan(),
            assessment_id="bank-order",
        )
    )[-1]["result"]

    names = [name for name, _thread_id in calls]
    assert names.index("select") < names.index("research")
    assert result["climate_grounding"]["country_iso3"] == "SSD"
    assert next(
        thread_id for name, thread_id in calls if name == "select"
    ) == caller_thread
    assert next(
        thread_id for name, thread_id in calls if name == "research"
    ) != caller_thread


def test_default_climate_research_uses_bank_and_live_sources(monkeypatch):
    monkeypatch.delenv("CLIMATE_RESEARCH_MODE", raising=False)
    plan = _climate_bank_plan()
    bank = object()
    manifest = {
        "bank_status": "ok",
        "warning_code": "",
        "schema_version": "1.0.0",
        "content_version": "approved-global-1",
        "country_iso3": "SSD",
        "evidence_ids": ["SSD-E-001"],
        "pathway_ids": [],
    }
    bank_packet = _bank_packet_for_search()
    calls = []
    climate_profiles = []
    core_profiles = []

    monkeypatch.setattr(app_module, "_research_cache", {})
    monkeypatch.setattr(app_module, "load_climate_bank", lambda: bank)
    monkeypatch.setattr(
        app_module,
        "select_bank_manifest",
        lambda *_args, **_kwargs: manifest,
    )
    monkeypatch.setattr(
        app_module,
        "materialize_bank_manifest",
        lambda *_args, **_kwargs: bank_packet,
    )
    monkeypatch.setattr(app_module, "get_research_client", lambda: object())

    def fake_core_search(*_args, project_profile=None, **_kwargs):
        calls.append("core")
        core_profiles.append(project_profile)
        return {
            "brief": "Fresh FCV context.",
            "status": "sourced",
            "sources": [{"url": "https://example.org/fcv-context"}],
        }

    def fake_climate_search(
        _country, _sector, project_profile, *_args, **_kwargs
    ):
        calls.append("climate")
        climate_profiles.append(project_profile)
        return _valid_two_source_bundle()

    monkeypatch.setattr(app_module, "run_fcv_web_research", fake_core_search)
    monkeypatch.setattr(
        app_module, "run_climate_web_research", fake_climate_search
    )

    result = list(
        app_module._iter_stage1_research(plan, "default-live-bank")
    )[-1]["result"]
    grounding, accepted = app_module.resolve_climate_grounding(
        manifest, result["climate_research"], assessment_id="default-live-bank"
    )

    assert sorted(calls) == ["climate", "core"]
    assert result["core_brief"] == "Fresh FCV context."
    assert grounding["state"] == "bank+research"
    assert accepted["claims"]
    assert core_profiles == [plan["project_profile"]]
    assert "bank_context" in climate_profiles[0]


def test_bank_only_mode_never_constructs_provider_or_reuses_live_cache(monkeypatch):
    monkeypatch.setenv('CLIMATE_RESEARCH_MODE', 'bank_only')
    plan = _climate_bank_plan()
    cache_key = app_module.research_cache_key(
        plan["country"], plan["sector"], True, plan["project_profile"]
    )
    existing_cache = {
        cache_key: {
            "brief": "stale cached core context",
            "status": "sourced",
            "sources": [{"url": "https://example.org/old"}],
            "cached_at": app_module.time.time(),
        }
    }
    monkeypatch.setattr(app_module, "_research_cache", existing_cache)
    monkeypatch.setattr(app_module, 'get_research_client', lambda: pytest.fail('Provider constructed'))
    monkeypatch.setattr(app_module, 'load_climate_bank', lambda: object())
    monkeypatch.setattr(app_module, 'select_bank_manifest', lambda *a, **kw:
                        {'bank_status': 'ok', 'country_iso3': 'SSD', 'evidence_ids': ['SSD-E-001']})
    result = list(app_module._iter_stage1_research(plan, 'bank-only'))[-1]['result']
    assert result['climate_grounding']['evidence_ids'] == ['SSD-E-001']
    assert result['core_brief'] == ''
    assert result['lens_context_sources'] == []
    assert result['climate_research']['attempts'] == 0
    assert 'disabled' in result['climate_research']['failure_reason']
    assert existing_cache[cache_key]["brief"] == "stale cached core context"


def test_bank_only_mode_does_not_disable_normal_fcv_research(monkeypatch):
    monkeypatch.setenv('CLIMATE_RESEARCH_MODE', 'bank_only')
    monkeypatch.setattr(app_module, '_research_cache', {})
    calls = []
    monkeypatch.setattr(app_module, 'get_research_client', lambda: object())
    monkeypatch.setattr(app_module, 'run_fcv_web_research', lambda *a, **kw:
                        calls.append(True) or {'brief': 'Normal FCV research'})
    plan = _climate_bank_plan()
    plan['climate']['enabled'] = False
    result = list(app_module._iter_stage1_research(plan, 'normal-fcv'))[-1]['result']
    assert calls == [True]
    assert result['core_brief'] == 'Normal FCV research'


def test_bank_selection_failure_is_nonfatal(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "load_climate_bank",
        lambda: (_ for _ in ()).throw(ValueError("bad release")),
    )
    monkeypatch.setattr(
        app_module,
        "run_fcv_web_research",
        lambda *args, **kwargs: {"brief": ""},
    )
    monkeypatch.setattr(
        app_module,
        "run_climate_web_research",
        lambda *args, **kwargs: _valid_bundle(),
    )
    monkeypatch.setattr(app_module, "get_research_client", lambda: object())
    app_module._research_cache.clear()

    result = list(
        app_module._iter_stage1_research(
            _climate_bank_plan(),
            assessment_id="bank-fail-open",
        )
    )[-1]["result"]

    assert result["climate_grounding"] == {
        "bank_status": "unavailable",
        "warning_code": "bank_unavailable",
    }
    assert result["climate_research"]["status"] == "complete"


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
        "https://example.com/untrusted",
        "https://www.un.org/example-climate",
    ]
    assert packet["sources"][1]["trust_tier"] == "caution"
    assert "encrypted-secret" not in serialized
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
                "publication_date": "2025",
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


def test_climate_research_gate_accepts_one_source():
    decision = climate_research_evidence_gate(_valid_bundle())
    assert decision["ok"] is True
    assert decision["code"] == ""
    assert len(decision["bundle"]["sources"]) == 1


def test_climate_research_gate_rejects_bundle_without_claims():
    bundle = _valid_bundle()
    bundle["claims"] = []
    decision = climate_research_evidence_gate(bundle)
    assert decision["ok"] is False
    assert decision["code"] == "climate_research_insufficient"
    assert "cited source passage" in decision["message"]


def test_climate_research_gate_accepts_claim_without_climate_anchor():
    bundle = _valid_bundle()
    bundle["sources"].append(_second_authoritative_source())
    bundle["claims"][0]["source_ids"].append("climate-source-2")
    bundle["claims"][0]["geographies"] = []
    bundle["claims"][0]["affected_groups"] = []
    bundle["claims"][0]["systems_or_assets"] = []
    bundle["claims"][0]["project_elements"] = []
    decision = climate_research_evidence_gate(bundle)
    assert decision["ok"] is True


def test_climate_research_gate_accepts_duplicate_cited_source_url():
    bundle = _valid_bundle()
    duplicate = _second_authoritative_source()
    duplicate["url"] = "https://openknowledge.worldbank.org/example/"
    bundle["sources"].append(duplicate)
    bundle["claims"][0]["source_ids"].append("climate-source-2")

    decision = climate_research_evidence_gate(bundle)

    assert decision["ok"] is True


def test_climate_research_gate_accepts_with_uncited_second_source():
    bundle = _valid_bundle()
    bundle["sources"].append(_second_authoritative_source())

    decision = climate_research_evidence_gate(bundle)

    assert decision["ok"] is True


def test_climate_research_bundle_keeps_grounded_project_specific_claims():
    result = normalize_climate_research_bundle(_valid_bundle())

    assert result["status"] == "complete"
    assert result["claims"][0]["id"] == "climate-claim-1"
    assert result["claims"][0]["time_horizons"] == ["project-lifetime"]
    assert 'Landing-site rehabilitation' in format_climate_research_context(result)
    complete = _valid_bundle()
    complete['sources'].append(_second_authoritative_source())
    complete['claims'][0]['source_ids'].append('climate-source-2')
    assert 'Landing-site rehabilitation' in format_climate_research_context(complete)


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

    assert len(result["claims"]) == 8


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
    quote = bundle["claims"][0]["claim"]
    bundle["claims"][0]["source_excerpt"] = quote
    citations = [SimpleNamespace(url=source["url"], cited_text=quote)
                 for source in bundle["sources"]]
    return SimpleNamespace(content=[
        SimpleNamespace(
            type="text",
            text=(
                CLIMATE_RESEARCH_START
                + json.dumps(bundle)
                + CLIMATE_RESEARCH_END
            ),
            citations=citations,
        )
    ])


def _insufficient_but_structured_climate_response():
    bundle = _valid_bundle()
    quote = bundle["claims"][0]["claim"]
    bundle["claims"][0]["source_excerpt"] = quote
    return SimpleNamespace(content=[
        SimpleNamespace(
            type="text",
            text=(
                CLIMATE_RESEARCH_START
                + json.dumps(bundle)
                + CLIMATE_RESEARCH_END
            ),
            citations=[SimpleNamespace(url=bundle["sources"][0]["url"], cited_text=quote)],
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
        "source_id_valid": -1,
        "source_type_valid": -1,
        "source_title_present": -1,
        "source_url_trusted": -1,
        "source_fully_valid": -1,
        "claims_count": -1,
        "selections_count": -1,
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
    assert summary["source_id_valid"] == 0
    assert summary["source_type_valid"] == 0
    assert summary["source_title_present"] == 0
    assert summary["source_url_trusted"] == 0
    assert summary["source_fully_valid"] == 0
    assert summary["claims_count"] == 4
    assert summary["selections_count"] == -1
    assert "SECRET" not in repr(summary)


def test_climate_structuring_diagnostic_recognizes_current_selections_shape():
    text = (
        CLIMATE_RESEARCH_START
        + json.dumps({
            "selections": [
                {"passage_id": "CP-001", "private": "SECRET ONE"},
                {"passage_id": "CP-002", "private": "SECRET TWO"},
            ]
        })
        + CLIMATE_RESEARCH_END
    )

    summary = summarize_climate_structuring_response(text)

    assert summary["json_status"] == "valid"
    assert summary["top_level_object"] is True
    assert summary["fields_present"] == ("selections",)
    assert summary["selections_count"] == 2
    assert "SECRET" not in repr(summary)


def test_climate_research_normalizes_bounded_numeric_passage_diagnostics():
    bundle = normalize_climate_research_bundle({
        "status": "failed",
        "passage_diagnostics": {
            "received_count": 10_000,
            "selected_count": "4",
            "invalid_selection_count": -2,
            "admitted_claim_count": float("inf"),
            "private": "SECRET SOURCE TEXT",
        },
    })

    assert bundle["passage_diagnostics"] == {
        "received_count": 24,
        "selected_count": 4,
        "invalid_selection_count": 0,
        "admitted_claim_count": 0,
    }
    assert "SECRET" not in repr(bundle)


def test_climate_research_normalizes_model_generated_ids():
    payload = _valid_bundle()
    payload["sources"].append(_second_authoritative_source())
    payload["sources"][0]["id"] = "source_1"
    payload["sources"][1]["id"] = "source_2"
    payload["claims"][0]["id"] = "claim_1"
    payload["claims"][0]["source_ids"] = ["source_1", "source_2"]

    bundle = normalize_climate_research_bundle(payload)

    assert [source["id"] for source in bundle["sources"]] == [
        "climate-source-1",
        "climate-source-2",
    ]
    assert bundle["claims"][0]["id"] == "climate-claim-1"
    assert bundle["claims"][0]["source_ids"] == [
        "climate-source-1",
        "climate-source-2",
    ]


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
    assert "four to six claims" in prompt
    assert "mandatory" not in prompt.casefold()

    search_prompt = research_module.build_climate_search_prompt(
        "South Sudan", "Natural resources", {"beneficiary_countries": ["South Sudan"]}
    )
    selection_prompt = research_module.build_climate_passage_selection_prompt({"passages": []})
    for text in (search_prompt, prompt):
        assert "time window" in text.casefold()
        assert "geographic" in text.casefold()
        assert "denominator" in text.casefold()
        assert "scenario" in text.casefold()
        assert "past tense" in text.casefold()
        assert "publication date" in text.casefold()
        assert "historical" in text.casefold()
    # The selection prompt classifies whole passages: no verbatim/ellipsis/geography-in-excerpt rules.
    assert "past tense" in selection_prompt.casefold()
    assert "publication date" in selection_prompt.casefold()
    assert "up to 8 selections" in selection_prompt
    for dropped in ("ellipses", "unmatched", "verbatim in the selected", "geography must appear"):
        assert dropped not in selection_prompt


def test_legacy_verifier_keeps_truncated_native_quote_and_counts_it():
    quote = (
        "The largest climate impacts on GDP were heat stress effects on labor, "
        "impacts on livestock production,. and flood impacts on transport "
        "infrastructure...."
    )
    bundle = _valid_bundle()
    bundle["sources"][0]["url"] = "https://www.worldbank.org/report"
    bundle["claims"][0]["claim"] = quote
    bundle["claims"][0]["source_excerpt"] = quote
    content = [{"type": "text", "citations": [{
        "url": "https://www.worldbank.org/report",
        "title": "Somalia climate report",
        "cited_text": quote,
    }]}]

    result = research_module.verify_climate_research_claims(bundle, content)

    assert [c["claim"] for c in result["claims"]] == [quote]
    assert result["passage_diagnostics"] == {
        "received_count": 1,
        "selected_count": 1,
        "invalid_selection_count": 0,
        "admitted_claim_count": 1,
    }


def test_legacy_verifier_does_not_require_numeric_geography_inside_excerpt():
    quote = (
        "Under SSP5-8.5, modeled GDP losses could reach 8 per cent by 2050; "
        "this is a projection, not an observed loss."
    )
    bundle = _valid_bundle()
    bundle["sources"][0]["title"] = "Somalia climate report"
    bundle["sources"][0]["url"] = "https://www.worldbank.org/report"
    bundle["claims"][0]["claim"] = quote
    bundle["claims"][0]["source_excerpt"] = quote
    bundle["claims"][0]["geographies"] = ["Somalia"]
    content = [{"type": "text", "citations": [{
        "url": "https://www.worldbank.org/report",
        "title": "Somalia climate report",
        "cited_text": quote,
    }]}]

    result = research_module.verify_climate_research_claims(bundle, content)

    assert len(result["claims"]) == 1
    assert result["passage_diagnostics"]["invalid_selection_count"] == 0


def test_source_context_caveat_is_preserved_and_idempotent_across_gates():
    from sector_lenses.research import resolve_climate_passage_selections

    concrete_gap = "No site-level design flood standard was found."
    quote = "Flood timing affects access in Somalia."
    citation = {
        "url": "https://www.worldbank.org/report",
        "title": "Somalia climate report",
        "cited_text": quote,
    }
    packet = build_climate_evidence_packet([{
        "type": "text", "citations": [citation],
    }], {
        "beneficiary_countries": ["Somalia"],
        "project_elements": ["Landing-site rehabilitation"],
    })
    labels = {key: value for key, value in _valid_bundle()["claims"][0].items()
              if key not in {"id", "claim", "source_ids"}}
    labels.update({
        "evidence_gap": concrete_gap,
        "project_elements": ["Landing-site rehabilitation"],
        "geographies": ["Somalia"],
    })
    source_first = resolve_climate_passage_selections({"selections": [{
        **labels, "passage_id": packet["passages"][0]["id"],
    }]}, packet)
    caveated_gap = source_first["claims"][0]["evidence_gap"]

    assert concrete_gap in caveated_gap
    assert (
        "Received excerpt only; original context may narrow place, time, population or scenario."
        in caveated_gap
    )
    assert "Classification is provisional; check the original source." in caveated_gap
    assert caveated_gap.count("Classification is provisional") == 1

    legacy_input = {
        **source_first,
        "claims": [{**source_first["claims"][0], "evidence_gap": concrete_gap}],
    }
    content = [{"type": "text", "citations": [citation]}]
    legacy_result = research_module.verify_climate_research_claims(legacy_input, content)
    repeated_result = research_module.verify_climate_research_claims(legacy_result, content)

    assert legacy_result["claims"][0]["evidence_gap"] == caveated_gap
    assert repeated_result["claims"][0]["evidence_gap"] == caveated_gap

    overflow_labels = {**labels, "evidence_gap": "x" * 480}
    overflow_result = resolve_climate_passage_selections({"selections": [{
        **overflow_labels, "passage_id": packet["passages"][0]["id"],
    }]}, packet)
    # An oversized model gap is bounded to 500, never a reason to reject the claim.
    assert len(overflow_result["claims"]) == 1
    overflow_gap = overflow_result["claims"][0]["evidence_gap"]
    assert overflow_gap.startswith("x" * 480)
    assert overflow_gap.count("Classification is provisional") == 1
    assert overflow_result["passage_diagnostics"]["invalid_selection_count"] == 0


def test_compact_bank_search_context_keeps_scope_and_fits_whole_rows():
    context = research_module.build_climate_bank_search_context(
        _bank_packet_for_search()
    )
    serialized = json.dumps(
        context, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )

    assert len(serialized) <= 2_500
    assert context["country_profile"]["known_gaps"]
    assert context["country_profile"]["coverage"]
    selected = context["selected_scope"][0]
    assert selected["sources"][0]["publication_date"] == "2018"
    assert selected["sources"][0]["locator"] == "Chapter 2, p. 14"
    assert selected["uncertainty"] == (
        "Station coverage is limited outside major towns."
    )


def test_bank_search_profile_bounds_multiple_coverage_and_gap_rows():
    packet = _bank_packet_for_search()
    packet["country_profile"] = {
        "coverage": [
            {
                "topic": f"coverage topic {index}",
                "summary": "District observations vary by region. " * 5,
            }
            for index in range(8)
        ],
        "known_gaps": [
            {
                "topic": f"gap topic {index}",
                "summary": "Recent local evidence was not identified. " * 5,
            }
            for index in range(8)
        ],
    }

    context = research_module.build_climate_bank_search_context(packet)
    profile = context["country_profile"]
    serialized_profile = json.dumps(
        {"country_profile": profile},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    serialized_context = json.dumps(
        context, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )

    assert len(serialized_profile) <= 900
    assert len(serialized_context) <= 2_500
    assert profile["coverage"]
    assert profile["known_gaps"]
    assert profile["coverage"][0]["topic"] == "coverage topic 0"
    assert profile["known_gaps"][0]["topic"] == "gap topic 0"
    assert {"coverage", "known_gaps"}.issubset(
        profile["truncated_fields"]
    )


def test_bank_search_context_skips_oversized_source_scope_as_a_whole():
    packet = _bank_packet_for_search()
    packet["sources"].extend([
        {
            "source_id": "SSD-SRC-002",
            "title": "Oversized source title " * 1_000,
            "publication_date": "2010",
            "url": "https://example.org/oversized",
        },
        {
            "source_id": "SSD-SRC-003",
            "title": "District flood update",
            "publication_date": "2025",
            "url": "https://example.org/district-flood-update",
        },
    ])
    packet["evidence_records"] = [
        {
            **packet["evidence_records"][0],
            "evidence_id": "SSD-E-002",
            "compact_statement": "Oversized assertion " * 1_000,
            "source_refs": [{
                "source_id": "SSD-SRC-002",
                "locator": "Oversized locator " * 1_000,
            }],
        },
        {
            **packet["evidence_records"][0],
            "evidence_id": "SSD-E-003",
            "compact_statement": "Flood mapping is available for two districts.",
            "source_refs": [{
                "source_id": "SSD-SRC-003",
                "locator": "Table 3",
            }],
        },
    ]

    context = research_module.build_climate_bank_search_context(packet)
    serialized = json.dumps(
        context, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )

    assert len(serialized) <= 2_500
    assert len(context["selected_scope"]) == 1
    assert context["selected_scope"][0]["statement"] == (
        "Flood mapping is available for two districts."
    )
    assert context["selected_scope"][0]["sources"][0]["source_id"] == (
        "SSD-SRC-003"
    )
    assert context["selected_scope_truncated"] is True
    assert "Oversized assertion" not in serialized


def test_climate_search_prompt_uses_current_date_and_bank_gaps():
    project_profile = {
        "beneficiary_countries": ["South Sudan"],
        "bank_context": research_module.build_climate_bank_search_context(
            _bank_packet_for_search()
        ),
    }
    prompt = research_module.build_climate_search_prompt(
        "South Sudan", "Water", project_profile
    )
    normalized_prompt = " ".join(prompt.casefold().split())

    assert f"CURRENT DATE: {date.today().isoformat()}" in prompt
    assert "local flood mapping" in prompt
    assert "2018" in prompt
    assert "publication date" in normalized_prompt
    assert "routine-use approval authorizes the bank" in normalized_prompt
    assert "does not independently verify its sources" in normalized_prompt
    assert "prioritize the known gaps" in normalized_prompt
    assert "omitted items are unknown" in normalized_prompt


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
    assert call["max_tokens"] == 3000
    assert call["thinking"] == {"type": "between_tools"}
    assert call["tools"][0]["max_uses"] == 3
    assert "allowed_domains" not in call["tools"][0]
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


def test_climate_research_structures_search_notes_without_researching(caplog):
    searched_content = [
        SimpleNamespace(
            type="server_tool_use",
            name="web_search",
            raw_payload="original-search-secret" * 1000,
        ),
        SimpleNamespace(
            type="web_search_tool_result",
            content=[SimpleNamespace(
                type="web_search_result",
                title="South Sudan CCDR",
                url="https://www.worldbank.org/south-sudan-ccdr",
                page_age="2025",
                encrypted_content="encrypted-secret" * 1000,
            )],
        ),
        SimpleNamespace(
            type="web_search_tool_result",
            content=[SimpleNamespace(
                type="web_search_result",
                title="UN flood evidence",
                url="https://www.un.org/south-sudan-floods",
                page_age="2024",
            )],
        ),
        SimpleNamespace(
            type="text",
            text="Search completed with two relevant sources. " * 1000,
            citations=[SimpleNamespace(url=url, title=title,
                cited_text='Changing flood timing affects landing-site access in South Sudan.')
                for url, title in [('https://www.worldbank.org/south-sudan-ccdr', 'South Sudan CCDR'),
                                   ('https://www.un.org/south-sudan-floods', 'South Sudan flood evidence')]],
        ),
    ]
    searched = SimpleNamespace(
        content=searched_content,
        stop_reason="end_turn",
    )
    labels = _valid_bundle()['claims'][0]
    labels['geographies'] = ['South Sudan']
    final = SimpleNamespace(stop_reason='end_turn', content=[SimpleNamespace(type='text',
        text=CLIMATE_RESEARCH_START + json.dumps({'selections': [
            {**labels, 'passage_id': 'CP-001'}, {**labels, 'passage_id': 'CP-002'},
        ]}) + CLIMATE_RESEARCH_END)])
    client = _SequencedResearchClient([searched, final])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Water",
        {
            "documents": ["South Sudan PCN.docx"],
            "beneficiary_countries": ["South Sudan"],
            "project_elements": ["Landing-site rehabilitation"],
            "document_excerpt": "Upper Nile landing sites. " * 1000,
        },
        client,
    )

    assert result["status"] == "complete"
    assert result["attempts"] == 1
    assert len(client.calls) == 2
    recovery = client.calls[1]
    assert "tools" not in recovery and "betas" not in recovery and "tool_choice" not in recovery
    assert recovery["model"] == "claude-haiku-5-5"
    assert recovery["max_tokens"] == 4000
    # Thinking disabled so Haiku 5.5's adaptive thinking can't consume the output
    # budget and truncate the research JSON (the 4.6-era budget assumed no thinking).
    assert recovery["thinking"] == {"type": "disabled"}
    assert [message["role"] for message in recovery["messages"]] == ["user"]
    request_text = recovery["messages"][-1]["content"]
    assert "EVIDENCE PACKET" in request_text
    assert "original-search-secret" not in request_text
    assert "encrypted-secret" not in request_text
    assert CLIMATE_RESEARCH_START in request_text
    assert "passage_id" in request_text
    assert "time_horizons" in request_text
    assert len(request_text) < 20_000
    assert "original-search-secret" not in caplog.text
    assert "encrypted-secret" not in caplog.text


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
    assert result["failure_reason"] == (
        "Climate evidence structuring was truncated before valid JSON completed."
    )
    decision = climate_research_evidence_gate(result)
    assert "structured" in decision["message"].lower()
    assert "two relevant sources" not in decision["message"].lower()
    assert len(client.calls) == 2
    assert "outcome=structuring_diagnostic" in caplog.text
    assert "Climate research passage admission" in caplog.text
    assert "'retained': 0" in caplog.text
    assert "assessment_id=assessment-diagnostic" in caplog.text
    assert "stop_reason=max_tokens" in caplog.text
    assert "output_tokens=2500" in caplog.text
    assert "start_present=yes end_present=no" in caplog.text
    assert "json_status=incomplete" in caplog.text
    assert "gate_code=climate_research_failed" in caplog.text
    assert "source_checks=id:-1,type:-1,title:-1,url:-1,valid:-1" in caplog.text
    assert secret not in caplog.text


def test_rejected_passage_counts_survive_failed_research_and_are_logged(caplog):
    searched = SimpleNamespace(
        content=[
            SimpleNamespace(type="web_search_tool_result", content=[]),
            SimpleNamespace(type="web_search_tool_result", content=[]),
            SimpleNamespace(
                type="text",
                text="Search completed.",
                citations=[SimpleNamespace(
                    url="https://www.worldbank.org/burundi-climate",
                    title="Burundi climate report",
                    cited_text="Flooding affects access in Burundi.",
                )],
            ),
        ],
        stop_reason="end_turn",
    )
    rejected = SimpleNamespace(
        content=[SimpleNamespace(
            type="text",
            text=(
                CLIMATE_RESEARCH_START
                + json.dumps({"selections": [{
                    "passage_id": "CP-999",
                    "project_elements": ["Invented activity"],
                    "geographies": ["Burundi"],
                    "evidence_status": "observed",
                    "confidence": "medium",
                    "time_horizons": ["project-lifetime"],
                    "private": "SECRET CLASSIFIER TEXT",
                }]})
                + CLIMATE_RESEARCH_END
            ),
        )],
        stop_reason="end_turn",
    )
    # Zero admitted claims now triggers one retry, so both attempts are supplied.
    client = _SequencedResearchClient([searched, rejected, searched, rejected])

    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        result = app_module.run_climate_web_research(
            "Burundi",
            "Transport",
            {
                "beneficiary_countries": ["Burundi"],
                "project_elements": ["Landing-site rehabilitation"],
            },
            client,
            assessment_id="assessment-rejected-passages",
        )

    assert result["status"] == "failed"
    assert result["passage_diagnostics"] == {
        "received_count": 1,
        "selected_count": 1,
        "invalid_selection_count": 1,
        "admitted_claim_count": 0,
    }
    assert len(client.calls) == 4
    assert "fields_present=selections" in caplog.text
    assert "selections_count=1" in caplog.text
    assert (
        "passage_checks=received:1,selected:1,invalid:1,admitted:0"
        in caplog.text
    )
    assert "Flooding affects access" not in caplog.text
    assert "SECRET CLASSIFIER TEXT" not in caplog.text


def test_failed_grounding_retains_only_bounded_passage_diagnostics(monkeypatch):
    monkeypatch.setattr(app_module, "load_climate_bank", lambda: object())
    monkeypatch.setattr(app_module, "materialize_bank_manifest", lambda *_args: {
        "bank_status": "unavailable", "warning_code": "bank_country_unavailable",
    })
    failed = normalize_climate_research_bundle({
        "status": "failed",
        "failure_reason": "No passage survived validation.",
        "passage_diagnostics": {
            "received_count": 3,
            "selected_count": 2,
            "invalid_selection_count": 2,
            "admitted_claim_count": 0,
        },
    })

    _, retained = app_module.resolve_climate_grounding({}, failed)

    assert retained["passage_diagnostics"] == failed["passage_diagnostics"]
    assert retained["sources"] == []
    assert retained["claims"] == []


def test_admitted_claim_needs_no_retry_and_malformed_selection_logs_unknown_counts(caplog):
    searched = SimpleNamespace(
        content=[
            SimpleNamespace(type="web_search_tool_result", content=[]),
            SimpleNamespace(type="web_search_tool_result", content=[]),
            SimpleNamespace(
                type="text",
                text="Search completed.",
                citations=[SimpleNamespace(
                    url="https://www.worldbank.org/burundi-climate",
                    title="Burundi climate report",
                    cited_text="Flooding affects access in Burundi.",
                )],
            ),
        ],
        stop_reason="end_turn",
    )
    labels = {
        key: value for key, value in _valid_bundle()["claims"][0].items()
        if key not in {"id", "claim", "source_ids"}
    }
    labels["geographies"] = ["Burundi"]
    partial = SimpleNamespace(
        content=[SimpleNamespace(
            type="text",
            text=(
                CLIMATE_RESEARCH_START
                + json.dumps({"selections": [{
                    **labels,
                    "passage_id": "CP-001",
                }]})
                + CLIMATE_RESEARCH_END
            ),
        )],
        stop_reason="end_turn",
    )
    malformed = SimpleNamespace(
        content=[SimpleNamespace(
            type="text",
            text=CLIMATE_RESEARCH_START + '{"selections":' + CLIMATE_RESEARCH_END,
        )],
        stop_reason="end_turn",
    )
    client = _SequencedResearchClient([searched, partial])

    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        result = app_module.run_climate_web_research(
            "Burundi",
            "Transport",
            {
                "beneficiary_countries": ["Burundi"],
                "project_elements": ["Landing-site rehabilitation"],
            },
            client,
            assessment_id="assessment-retry-diagnostics",
        )

    # One admitted claim passes the gate, so there is no second attempt.
    assert result["status"] == "complete"
    assert result["attempts"] == 1
    assert len(client.calls) == 2
    assert result["passage_diagnostics"] == {
        "received_count": 1,
        "selected_count": 1,
        "invalid_selection_count": 0,
        "admitted_claim_count": 1,
    }
    diagnostic_logs = [
        message for message in caplog.messages
        if "outcome=structuring_diagnostic" in message
    ]
    assert len(diagnostic_logs) == 1
    assert "passage_checks=received:1,selected:1,invalid:0,admitted:1" in diagnostic_logs[0]

    caplog.clear()
    malformed_client = _SequencedResearchClient([searched, malformed, searched, malformed])
    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        app_module.run_climate_web_research(
            "Burundi", "Transport",
            {"beneficiary_countries": ["Burundi"],
             "project_elements": ["Landing-site rehabilitation"]},
            malformed_client, assessment_id="assessment-malformed-diagnostics")
    unknown_logs = [m for m in caplog.messages if "outcome=structuring_diagnostic" in m]
    assert unknown_logs
    assert "passage_checks=received:-1,selected:-1,invalid:-1,admitted:-1" in unknown_logs[0]


def test_research_summary_distinguishes_unknown_from_known_zero_counts(caplog):
    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        app_module.log_climate_research_summary(
            "assessment-unknown", {"status": "failed"}, elapsed_ms=1
        )
        app_module.log_climate_research_summary(
            "assessment-zero",
            {
                "status": "failed",
                "passage_diagnostics": {
                    "received_count": 0,
                    "selected_count": 0,
                    "invalid_selection_count": 0,
                    "admitted_claim_count": 0,
                },
            },
            elapsed_ms=1,
        )

    unknown = next(
        message for message in caplog.messages
        if "assessment_id=assessment-unknown" in message
    )
    known_zero = next(
        message for message in caplog.messages
        if "assessment_id=assessment-zero" in message
    )
    assert "passage_checks=received:-1,selected:-1,invalid:-1,admitted:-1" in unknown
    assert "passage_checks=received:0,selected:0,invalid:0,admitted:0" in known_zero


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


def test_climate_research_accepts_single_source_evidence_without_retry():
    client = _SequencedResearchClient([
        _insufficient_but_structured_climate_response(),
        _valid_climate_response(),
    ])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Natural resources",
        {"project_elements": ["Landing sites"]},
        client,
    )

    assert result["status"] == "complete"
    assert result["attempts"] == 1
    assert len(client.calls) == 1


def test_climate_research_does_not_retry_truncated_structured_evidence():
    truncated = _insufficient_but_structured_climate_response()
    truncated.stop_reason = "max_tokens"
    client = _SequencedResearchClient([truncated, _valid_climate_response()])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Natural resources",
        {"project_elements": ["Landing sites"]},
        client,
    )

    assert result["status"] == "complete"
    assert len(result["claims"]) == 1
    assert climate_research_evidence_gate(result)["ok"]
    assert result["attempts"] == 1
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


@pytest.mark.parametrize("host,expected", [
    ("notworldbank.org", None), ("notipcc.ch", None),
    ("documents1.worldbank.org", "world-bank"), ("www.ipcc.ch", "scientific")])
def test_lookalike_hosts_are_other_caution_and_official_hosts_keep_type(host, expected, monkeypatch):
    from sector_lenses import research
    packet = build_climate_evidence_packet([{"type": "text", "citations": [{
        "url": f"https://{host}/report", "title": "Burundi climate report",
        "cited_text": "Flooding affects access in Burundi."}]}],
        {"project_elements": ["Component 2"], "beneficiary_countries": ["Burundi"]})
    if expected is None:
        # Look-alike hosts are admitted but labelled for caution, never as official.
        assert packet["sources"][0]["trust_tier"] == "caution"
        assert len(packet["passages"]) == 1
    captured = {}
    normalize = research.normalize_climate_research_bundle

    def capture_classification(payload):
        captured.update(payload)
        return normalize(payload)

    monkeypatch.setattr(research, "normalize_climate_research_bundle", capture_classification)
    result = research.resolve_climate_passage_selections({"selections": [{
        "passage_id": packet["passages"][0]["id"], "geographies": ["Burundi"],
        "project_elements": ["Component 2"], "confidence": "medium",
        "evidence_status": "observed", "time_horizons": ["current-near-term"],
        "evidence_gap": "Current status unverified."}]}, packet)
    assert captured["sources"][0]["source_type"] == (expected or "other")
    assert result["sources"][0]["source_type"] == (expected or "other")
    assert result["sources"][0]["trust_tier"] == ("caution" if expected is None else "standard")


def test_research_passage_diagnostics_explain_rejection_without_source_content():
    base = {'url': 'https://www.worldbank.org/report', 'title': 'PRIVATE_TITLE',
            'cited_text': 'PRIVATE_QUOTE'}
    packet = build_climate_evidence_packet([{'type': 'text', 'citations': [
        base, base, {**base, 'url': 'http://localhost/report'},
        {**base, 'url': 'https://www.facebook.com/post'},
        {**base, 'cited_text': ''}, {**base, 'cited_text': 'x' * 1501},
        {**base, 'url': 'https://www.worldbank.org/other', 'title': ''},
    ]}], {})
    counts = packet['passage_diagnostics']
    assert counts == {'candidates': 7, 'invalid_source': 1, 'denied': 1,
                      'missing_title': 1, 'metadata_only': 1, 'overlong_quote': 1,
                      'duplicate': 1, 'admitted': 1, 'retained': 1, 'own_project': 0}
    assert 'PRIVATE' not in json.dumps(counts)
    assert packet['passages'][0]['excerpt'] == 'PRIVATE_QUOTE'


def test_long_native_quotes_keep_qualifications_through_research_gate():
    from sector_lenses.research import resolve_climate_passage_selections, verify_climate_research_claims
    quote = ('Flooding affects access in Burundi. ' * 6) + 'This is a projection, not an observed loss.'
    citations = [SimpleNamespace(url=url, title='Burundi climate report', cited_text=quote)
                 for url in ['https://worldbank.org/report', 'https://undp.org/report']]
    content = [SimpleNamespace(type='text', text='Notes', citations=citations)]
    packet = build_climate_evidence_packet(content, {
        'beneficiary_countries': ['Burundi'], 'project_elements': ['Component 1']})
    assert len(packet['passages']) == 2
    assert all(p['excerpt'] == quote for p in packet['passages'])
    selections = [{'passage_id': p['id'], 'geographies': ['Burundi'],
                   'project_elements': ['Component 1'], 'evidence_status': 'projected',
                   'confidence': 'medium', 'time_horizons': ['project-lifetime']}
                  for p in packet['passages']]
    bundle = resolve_climate_passage_selections({'selections': selections}, packet)
    assert climate_research_evidence_gate(bundle)['ok']
    assert all(c['source_excerpt'] == quote == c['claim'] for c in bundle['claims'])
    assert verify_climate_research_claims(bundle, content)['claims'] == bundle['claims']
    forged = {**bundle, 'claims': [{**bundle['claims'][0], 'source_excerpt': 'Invented quotation'}]}
    assert verify_climate_research_claims(forged, content)['claims'] == []


def test_packet_admits_non_allowlisted_cited_passage():
    packet = build_climate_evidence_packet([{"type": "text", "citations": [
        {"url": "https://www.crisisgroup.org/x", "title": "Crisis report",
         "cited_text": "Flooding displaced thousands in Burundi."}]}], {})
    assert len(packet["passages"]) == 1
    assert packet["sources"][0]["trust_tier"] == "standard"
    assert packet["sources"][0]["source_type"] == "research"


def test_packet_admits_ellipsis_passage():
    quote = "Flooding displaced thousands (in Burundi... and neighbouring areas."
    packet = build_climate_evidence_packet([{"type": "text", "citations": [
        {"url": "https://example.org/x", "title": "Report", "cited_text": quote}]}], {})
    assert [p["excerpt"] for p in packet["passages"]] == [quote]
    assert packet["sources"][0]["trust_tier"] == "caution"


def test_raw_search_result_is_metadata_only():
    packet = build_climate_evidence_packet([{"type": "web_search_tool_result", "content": [
        {"url": "https://www.worldbank.org/r", "title": "Report", "page_age": "2026-09-01",
         "snippet": "Some metadata"}]}], {})
    counts = packet["passage_diagnostics"]
    assert counts["metadata_only"] == 1 and "missing_quote" not in counts
    assert packet["passages"] == []


def test_packet_reads_page_age():
    packet = build_climate_evidence_packet([
        {"type": "web_search_tool_result", "content": [
            {"url": "https://www.worldbank.org/r", "title": "Report", "page_age": "2026-09-01"}]},
        {"type": "text", "citations": [
            {"url": "https://www.worldbank.org/r", "title": "Report", "cited_text": "Flooding in Burundi."}]},
    ], {})
    assert packet["sources"][0]["publication_date"] == "2026-09-01"
    assert packet["passages"][0]["publication_date"] == "2026-09-01"


def test_packet_round_robin_hosts():
    citations = [{"url": f"https://www.worldbank.org/r{i}", "title": f"WB {i}",
                  "cited_text": f"Flooding passage {i}."} for i in range(6)]
    citations += [{"url": "https://www.un.org/a", "title": "UN", "cited_text": "UN passage."},
                  {"url": "https://www.fao.org/b", "title": "FAO", "cited_text": "FAO passage."}]
    packet = build_climate_evidence_packet([{"type": "text", "citations": citations}], {})
    hosts = [p["url"].split("/")[2] for p in packet["passages"]]
    assert hosts[:3] == ["www.worldbank.org", "www.un.org", "www.fao.org"]
    assert hosts[3] == "www.worldbank.org"
    assert len(packet["sources"]) == 8 and len(packet["passages"]) == 8


def test_denied_source_counted():
    packet = build_climate_evidence_packet([{"type": "text", "citations": [
        {"url": "https://www.facebook.com/post", "title": "Post", "cited_text": "Flood."}]}], {})
    assert packet["passage_diagnostics"]["denied"] == 1
    assert packet["sources"] == [] and packet["passages"] == []


def test_packet_carries_project_country():
    packet = build_climate_evidence_packet([], {"country": "Burundi"})
    assert packet["project_profile"]["country"] == "Burundi"


def _admission_packet(url, text, title="Climate report", profile=None):
    return build_climate_evidence_packet(
        [{"type": "text", "citations": [{"url": url, "title": title, "cited_text": text}]}],
        profile if profile is not None else {"country": "Kenya", "beneficiary_countries": ["Kenya"]},
    )


def _resolve(packet, **selection):
    from sector_lenses.research import resolve_climate_passage_selections
    base = {"passage_id": "CP-001"}
    base.update(selection)
    return resolve_climate_passage_selections({"selections": [base]}, packet)


def test_single_news_source_passes_gate():
    packet = _admission_packet("https://www.reuters.com/x", "Floods hit Kenya's Tana River basin.")
    bundle = _resolve(packet, geographies=["Kenya"])
    gate = climate_research_evidence_gate(bundle)
    assert gate["ok"] and len(gate["bundle"]["claims"]) == 1
    assert gate["bundle"]["sources"][0]["trust_tier"] == "standard"
    assert gate["bundle"]["sources"][0]["source_type"] == "news"


def test_caution_claim_carries_note():
    from live_source_policy import CAUTION_NOTE
    from sector_lenses.research import CLIMATE_SOURCE_CONTEXT_CAVEAT
    packet = _admission_packet("https://somesite.example/p", "Drought is worsening in Kenya.")
    bundle = _resolve(packet, geographies=["Kenya"])
    gap = bundle["claims"][0]["evidence_gap"]
    assert CAUTION_NOTE in gap and CLIMATE_SOURCE_CONTEXT_CAVEAT in gap
    assert bundle["sources"][0]["trust_tier"] == "caution"


def test_context_only_claim_note():
    packet = _admission_packet("https://www.reuters.com/x", "Drought grips East Africa this season.")
    bundle = _resolve(packet, geographies=["Kenya"])
    assert len(bundle["claims"]) == 1
    assert ("Source does not name Kenya explicitly; regional or background context only."
            in bundle["claims"][0]["evidence_gap"])


def test_wrong_country_passage_rejected():
    packet = _admission_packet("https://www.reuters.com/x", "Floods displaced thousands in Niger.",
                               profile={"country": "Nigeria", "beneficiary_countries": ["Nigeria"]})
    bundle = _resolve(packet, geographies=["Nigeria"])
    assert bundle["claims"] == []
    assert bundle["passage_diagnostics"]["invalid_selection_count"] == 1


def test_invented_passage_id_rejected():
    packet = _admission_packet("https://www.reuters.com/x", "Floods hit Kenya.")
    bundle = _resolve(packet, passage_id="CP-999", geographies=["Kenya"])
    assert bundle["claims"] == []
    assert bundle["passage_diagnostics"]["invalid_selection_count"] == 1


def test_missing_labels_get_defaults():
    packet = _admission_packet("https://www.reuters.com/x", "Floods hit Kenya.")
    claim = _resolve(packet, geographies=["Kenya"])["claims"][0]
    assert claim["confidence"] == "medium"
    assert claim["evidence_status"] == "inferred"
    assert claim["time_horizons"] == ["current-near-term"]
    assert claim["project_elements"] == []


def test_uncovered_country_does_not_block():
    packet = _admission_packet(
        "https://www.reuters.com/x", "Floods hit Kenya.",
        profile={"country": "Kenya", "beneficiary_countries": ["Kenya", "Uganda"]})
    bundle = _resolve(packet, geographies=["Kenya"])
    assert bundle["uncovered_countries"] == ["Uganda"]
    assert bundle["status"] == "partial"
    assert climate_research_evidence_gate(bundle)["ok"]


def test_normalizer_keeps_news_source_type():
    bundle = normalize_climate_research_bundle({
        "status": "partial",
        "sources": [{"id": "s1", "source_type": "news", "title": "AP", "url": "https://apnews.com/x"}],
        "claims": [{"id": "c1", "claim": "Floods.", "source_ids": ["s1"]}]})
    assert len(bundle["sources"]) == 1
    assert bundle["sources"][0]["source_type"] == "news"
    assert bundle["sources"][0]["trust_tier"] == "standard"


def test_normalizer_recomputes_unknown_type_and_tier():
    bundle = normalize_climate_research_bundle({
        "status": "partial",
        "sources": [{"id": "s1", "source_type": "weird", "trust_tier": "bogus",
                     "title": "AP", "url": "https://apnews.com/x"}],
        "claims": [{"id": "c1", "claim": "Floods.", "source_ids": ["s1"]}]})
    assert bundle["sources"][0]["source_type"] == "news"
    assert bundle["sources"][0]["trust_tier"] == "standard"


def test_legacy_verifier_accepts_ellipsis_quote():
    from sector_lenses.research import verify_climate_research_claims
    quote = "Floods displaced 40 families in Kenya... and more elsewhere."
    content = [SimpleNamespace(type="text", text="n", citations=[SimpleNamespace(
        url="https://www.reuters.com/x", title="T", cited_text=quote)])]
    source = {"id": "climate-source-1", "source_type": "news", "title": "T",
              "url": "https://www.reuters.com/x", "publication_date": ""}
    claim = {"id": "climate-claim-1", "claim": quote, "source_excerpt": quote,
             "source_ids": ["climate-source-1"], "geographies": [], "evidence_gap": ""}
    bundle = {"status": "partial", "sources": [source], "claims": [claim]}
    kept = verify_climate_research_claims(bundle, content)
    assert len(kept["claims"]) == 1
    bad = {**bundle, "claims": [{**claim, "claim": quote + " 99 more"}]}
    assert verify_climate_research_claims(bad, content)["claims"] == []


def test_climate_search_request_has_no_allow_list():
    client = _SequencedResearchClient([_valid_climate_response()])
    app_module.run_climate_web_research("South Sudan", "Water", {}, client)
    tool = client.calls[0]["tools"][0]
    assert "allowed_domains" not in tool
    assert tool == {"type": "web_search_20250305", "name": "web_search", "max_uses": 3}


def test_climate_search_prompt_is_open():
    prompt = research_module.build_climate_search_prompt("South Sudan", "Water", {})
    assert "up to 3 web searches" in prompt
    assert "different publishers" in prompt
    for dropped in ("exactly two", "140 characters", "untrusted sources", "ellipses"):
        assert dropped not in prompt
    assert "900 words" in prompt


def test_summary_log_counts_trust(caplog):
    bundle = _valid_bundle()
    second = dict(_second_authoritative_source())
    second["trust_tier"] = "caution"
    second["source_type"] = "news"
    bundle["sources"][0]["trust_tier"] = "standard"
    bundle["sources"] = [bundle["sources"][0], second]
    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        app_module.log_climate_research_summary("a-1", bundle, elapsed_ms=5)
    assert "trust=standard:1,caution:1" in caplog.text
    assert "news" in caplog.text


def test_climate_research_retries_once_when_first_attempt_admits_no_claims():
    empty = SimpleNamespace(content=[SimpleNamespace(
        type="text", text="No structured evidence.", citations=[])],
        stop_reason="end_turn")
    client = _SequencedResearchClient([empty, _insufficient_but_structured_climate_response()])
    result = app_module.run_climate_web_research(
        "South Sudan", "Natural resources", {"project_elements": ["Landing sites"]}, client
    )
    assert result["status"] in {"complete", "partial"}
    assert climate_research_evidence_gate(result)["ok"]
    assert result["attempts"] == 2
    assert len(client.calls) == 2


def _pid_profile(*beneficiaries):
    # Mirrors app.py: the project country is "; ".join(extract_beneficiary_countries(...)).
    return {"country": "; ".join(beneficiaries), "beneficiary_countries": list(beneficiaries)}


def test_drc_pid_name_accepts_drc_passage_without_context_note():
    packet = _admission_packet(
        "https://www.reuters.com/x", "Floods hit the Democratic Republic of the Congo.",
        profile=_pid_profile("Congo, Democratic Republic of"))
    bundle = _resolve(packet, geographies=["Democratic Republic of the Congo"])
    assert len(bundle["claims"]) == 1
    assert "regional or background context only" not in bundle["claims"][0]["evidence_gap"]
    assert bundle["uncovered_countries"] == []


def test_drc_pid_name_rejects_republic_of_congo_passage():
    packet = _admission_packet(
        "https://www.reuters.com/x", "Floods hit Brazzaville in the Republic of the Congo.",
        profile=_pid_profile("Congo, Democratic Republic of"))
    bundle = _resolve(packet, geographies=["Republic of the Congo"])
    assert bundle["claims"] == []
    assert bundle["passage_diagnostics"]["invalid_selection_count"] == 1


def test_yemen_pid_name_accepts_yemen_passage_without_note_or_gap():
    packet = _admission_packet(
        "https://www.reuters.com/x", "Floods displaced families in Yemen.",
        profile=_pid_profile("Yemen, Republic of"))
    bundle = _resolve(packet, geographies=["Yemen"])
    assert len(bundle["claims"]) == 1
    assert "regional or background context only" not in bundle["claims"][0]["evidence_gap"]
    assert bundle["coverage_countries"] == ["Yemen, Republic of"]
    assert bundle["uncovered_countries"] == []
    assert bundle["failure_reason"] == ""


def test_multi_country_candidates_are_split_on_semicolons():
    packet = _admission_packet(
        "https://www.reuters.com/x", "Floods displaced families in Mali.",
        profile=_pid_profile("Niger", "Mali"))
    bundle = _resolve(packet, geographies=["Mali"])
    assert len(bundle["claims"]) == 1
    assert "regional or background context only" not in bundle["claims"][0]["evidence_gap"]


def test_multi_country_wrong_country_passage_is_rejected():
    packet = _admission_packet(
        "https://www.reuters.com/x", "Floods in Nigeria displaced thousands.",
        title="Floods in Nigeria", profile=_pid_profile("Niger", "Mali"))
    bundle = _resolve(packet, geographies=["Nigeria"])
    assert bundle["claims"] == []
    assert bundle["passage_diagnostics"]["invalid_selection_count"] == 1


def test_context_only_passage_gets_no_project_country_geography():
    packet = _admission_packet("https://www.reuters.com/x", "Drought grips East Africa this season.")
    bundle = _resolve(packet, geographies=["Kenya"])
    assert len(bundle["claims"]) == 1
    assert bundle["claims"][0]["geographies"] == []
    kept = _resolve(packet, geographies=["East Africa"])
    assert kept["claims"][0]["geographies"] == ["East Africa"]


def test_accepted_passage_falls_back_to_matched_country_geography():
    packet = _admission_packet("https://www.reuters.com/x", "Floods hit Kenya.")
    bundle = _resolve(packet, geographies=["Invented Place"])
    assert bundle["claims"][0]["geographies"] == ["Kenya"]


def test_uncovered_beneficiaries_are_named_in_failure_reason():
    packet = _admission_packet(
        "https://www.reuters.com/x", "Floods hit Kenya.",
        profile={"country": "Kenya", "beneficiary_countries": ["Kenya", "Uganda", "Rwanda"]})
    bundle = _resolve(packet, geographies=["Kenya"])
    assert bundle["uncovered_countries"] == ["Uganda", "Rwanda"]
    assert bundle["failure_reason"] == "No live web evidence was found for: Uganda, Rwanda."
    normalized = normalize_climate_research_bundle(bundle)
    assert normalized["failure_reason"] == "No live web evidence was found for: Uganda, Rwanda."
    gate = climate_research_evidence_gate(bundle)
    assert gate["ok"]
    assert gate["bundle"]["failure_reason"] == bundle["failure_reason"]


def test_combined_country_string_is_never_one_candidate():
    # As one string, "Congo, Democratic Republic of; Burundi" would canonicalise to
    # plain "Congo" and wrongly accept Republic of the Congo material.
    packet = _admission_packet(
        "https://www.reuters.com/x", "Flooding hit Congo-Brazzaville this season.",
        profile=_pid_profile("Congo, Democratic Republic of", "Burundi"))
    bundle = _resolve(packet, geographies=["Congo-Brazzaville"])
    assert bundle["claims"] == []


def _zero_claim_attempt(stop_reason="end_turn"):
    return SimpleNamespace(content=[SimpleNamespace(
        type="text", text="No structured evidence.", citations=[])],
        stop_reason=stop_reason)


def test_climate_research_does_not_retry_zero_claims_after_max_tokens():
    client = _SequencedResearchClient([
        _zero_claim_attempt("max_tokens"),
        _insufficient_but_structured_climate_response(),
    ])
    result = app_module.run_climate_web_research(
        "South Sudan", "Natural resources", {"project_elements": ["Landing sites"]}, client
    )
    assert result["status"] == "failed"
    assert result["attempts"] == 1
    assert len(client.calls) == 1


def test_climate_research_never_makes_a_third_attempt():
    client = _SequencedResearchClient([
        _zero_claim_attempt(), _zero_claim_attempt(),
        _insufficient_but_structured_climate_response(),
    ])
    result = app_module.run_climate_web_research(
        "South Sudan", "Natural resources", {"project_elements": ["Landing sites"]}, client
    )
    assert result["status"] == "failed"
    assert result["attempts"] == 2
    assert len(client.calls) == 2


def test_climate_evidence_packet_drops_own_project_sources():
    content = [{
        "type": "text",
        "text": "Water evidence.",
        "citations": [
            {
                "type": "web_search_result_location",
                "title": "The World Bank Guinea Water and Sanitation Project (P179017)",
                "url": "https://documents1.worldbank.org/curated/en/pad.pdf",
                "cited_text": "The project finances water supply in Guinea.",
            },
            {
                "type": "web_search_result_location",
                "title": "Guinea water report",
                "url": "https://www.un.org/guinea-water",
                "cited_text": "Guinea faces water stress.",
            },
        ],
    }]
    packet = build_climate_evidence_packet(
        content, {"documents": ["PAD.docx"], "project_ids": ["P179017"]}
    )

    assert [s["url"] for s in packet["sources"]] == ["https://www.un.org/guinea-water"]
    assert [p["url"] for p in packet["passages"]] == ["https://www.un.org/guinea-water"]
    assert packet["passage_diagnostics"]["own_project"] == 1
