"""Tests for bounded bank and live Climate-FCV grounding."""

from sector_lenses.climate_grounding import merge_climate_grounding


def _bank_packet() -> dict:
    return {
        "bank_status": "ok",
        "content_version": "test-1",
        "country_iso3": "SSD",
        "sources": [{
            "source_id": "SSD-SRC-001",
            "url": "https://SIPRI.org/a/",
            "title": "Reviewed source",
        }],
        "evidence_records": [{
            "evidence_id": "SSD-E-001",
            "compact_statement": "Reviewed evidence.",
            "evidence_status": "observed",
            "analytical_role": "direct-climate-fcv",
            "source_refs": [{
                "source_id": "SSD-SRC-001",
                "locator": "p. 1",
            }],
        }],
        "pathways": [],
    }


def _research_bundle() -> dict:
    return {
        "status": "complete",
        "sources": [{
            "id": "climate-source-1",
            "url": "https://un.org/a",
            "title": "Current evidence",
            "source_type": "un",
        }],
        "claims": [{
            "id": "climate-claim-1",
            "claim": "Current claim.",
            "source_ids": ["climate-source-1"],
            "project_elements": ["Road"],
            "geographies": ["Unity"],
            "affected_groups": [],
            "systems_or_assets": ["Road"],
            "evidence_status": "observed",
            "confidence": "medium",
            "time_horizons": ["current-near-term"],
            "evidence_gap": "",
        }],
    }


def test_all_four_grounding_states() -> None:
    bank = _bank_packet()
    research = _research_bundle()

    assert merge_climate_grounding(bank, research)["state"] == "bank+research"
    assert merge_climate_grounding(bank, {})["state"] == "bank-only"
    assert merge_climate_grounding({}, research)["state"] == "research-only"
    assert merge_climate_grounding({}, {})["state"] == "thematic-only"


def test_combined_grounding_is_bounded() -> None:
    bank = {
        "bank_status": "ok",
        "sources": [],
        "pathways": [],
        "evidence_records": [
            {
                "evidence_id": f"SSD-E-{index:03d}",
                "compact_statement": "x" * 900,
            }
            for index in range(1, 13)
        ],
    }
    merged = merge_climate_grounding(bank, {})

    assert len(merged["prompt_context"]) <= 12_000
    assert merged["bank_character_count"] <= 6_000


def test_provenance_and_source_aliases_survive_url_deduplication() -> None:
    bank = _bank_packet()
    research = _research_bundle()
    research["sources"][0].update({
        "id": "climate-source-duplicate",
        "url": "https://sipri.org/a",
    })
    research["claims"][0]["source_ids"] = ["climate-source-duplicate"]

    merged = merge_climate_grounding(bank, research)

    assert merged["bank_sources"] == bank["sources"]
    assert merged["live_sources"] == research["sources"]
    assert len(merged["sources"]) == 1
    assert set(merged["sources"][0]["source_aliases"]) == {
        "SSD-SRC-001",
        "climate-source-duplicate",
    }
    assert merged["sources"][0]["provenance"] == ["bank", "research"]


def test_compact_statements_and_conflicting_claims_are_not_rewritten() -> None:
    bank = _bank_packet()
    bank["evidence_records"][0]["compact_statement"] = (
        "Exact approved compact statement; keep punctuation."
    )
    research = _research_bundle()
    research["claims"][0]["conflicts_with"] = ["SSD-E-001"]

    merged = merge_climate_grounding(bank, research)

    assert (
        merged["bank_evidence_records"][0]["compact_statement"]
        == "Exact approved compact statement; keep punctuation."
    )
    assert merged["live_claims"][0]["conflicts_with"] == ["SSD-E-001"]
    assert merged["has_conflicting_evidence"] is True
    assert "Exact approved compact statement; keep punctuation." in (
        merged["prompt_context"]
    )


def test_live_claims_and_log_counts_are_bounded_and_content_free() -> None:
    research = _research_bundle()
    research["claims"] = [
        {**research["claims"][0], "id": f"climate-claim-{index}"}
        for index in range(1, 10)
    ]

    merged = merge_climate_grounding({}, research)

    assert len(merged["live_claims"]) == 6
    assert merged["log_counts"]["live_claims"] == 6
    assert set(merged["log_counts"]) == {
        "bank_sources",
        "bank_evidence_records",
        "bank_pathways",
        "live_sources",
        "live_claims",
        "deduplicated_sources",
    }
    assert all(
        isinstance(value, int) for value in merged["log_counts"].values()
    )


def test_maximum_live_source_metadata_cannot_crowd_out_all_claims() -> None:
    research = _research_bundle()
    research["sources"] = [
        {
            "id": f"climate-source-{index}",
            "url": f"https://un.org/{index}/" + ("u" * 900),
            "title": "t" * 300,
            "source_type": "un",
            "publication_date": "2026",
            "location": "l" * 200,
        }
        for index in range(1, 11)
    ]
    research["claims"] = [
        {
            **_research_bundle()["claims"][0],
            "id": f"climate-claim-{index}",
            "claim": "c" * 700,
            "source_ids": [
                f"climate-source-{source_index}"
                for source_index in range(1, 5)
            ],
            "project_elements": ["p" * 180] * 4,
            "geographies": ["g" * 160] * 4,
            "affected_groups": ["a" * 160] * 4,
            "systems_or_assets": ["s" * 180] * 4,
            "evidence_gap": "e" * 500,
        }
        for index in range(1, 7)
    ]

    merged = merge_climate_grounding({}, research)

    assert merged["state"] == "research-only"
    assert merged["live_claims"]
    assert '"claims":[{' in merged["prompt_context"]
    assert len(merged["prompt_context"]) <= 12_000


def test_malformed_source_port_does_not_raise() -> None:
    research = _research_bundle()
    research["sources"][0]["url"] = "https://un.org:bad/x"

    merged = merge_climate_grounding({}, research)

    assert merged["state"] == "research-only"


def test_unavailable_bank_records_are_never_injected() -> None:
    bank = _bank_packet()
    bank["bank_status"] = "unavailable"
    bank["warning_code"] = "bank_content_expired"

    merged = merge_climate_grounding(bank, {})

    assert merged["state"] == "thematic-only"
    assert merged["prompt_context"] == ""
    assert merged["warning_code"] == "bank_content_expired"
