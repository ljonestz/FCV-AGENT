"""Conflict-provenance tests through the real research normalization path."""

from sector_lenses.climate_grounding import merge_climate_grounding
from sector_lenses.research import (
    build_climate_research_prompt,
    normalize_climate_research_bundle,
)


def _bank_packet() -> dict:
    return {
        "bank_status": "ok",
        "content_version": "test-1",
        "country_iso3": "SSD",
        "sources": [{
            "source_id": "SSD-SRC-001",
            "url": "https://sipri.org/a",
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


def _raw_research() -> dict:
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
            "conflicts_with": ["SSD-E-001"],
            "conflict_note": (
                "Current source reports a different local access pattern."
            ),
        }],
    }


def test_conflicts_survive_real_research_normalization_path() -> None:
    normalized = normalize_climate_research_bundle(_raw_research())
    merged = merge_climate_grounding(_bank_packet(), normalized)

    assert merged["live_claims"][0]["conflicts_with"] == ["SSD-E-001"]
    assert merged["live_claims"][0]["conflict_note"] == (
        "Current source reports a different local access pattern."
    )
    assert merged["has_conflicting_evidence"] is True


def test_research_prompt_exposes_optional_conflict_fields() -> None:
    prompt = build_climate_research_prompt(
        "South Sudan",
        "Transport",
        {"document_excerpt": "Unity feeder roads"},
    )

    assert '"conflicts_with"' in prompt
    assert '"conflict_note"' in prompt


def test_conflict_ids_remap_after_invalid_claims_are_skipped() -> None:
    raw = _raw_research()
    invalid = {
        **raw["claims"][0],
        "id": "climate-claim-1",
        "project_elements": [],
    }
    second = {
        **raw["claims"][0],
        "id": "climate-claim-2",
        "claim": "Second valid claim.",
        "conflicts_with": ["climate-claim-3", "climate-claim-1"],
    }
    third = {
        **raw["claims"][0],
        "id": "climate-claim-3",
        "claim": "Third valid claim.",
        "conflicts_with": ["climate-claim-2"],
    }
    raw["claims"] = [invalid, second, third]

    normalized = normalize_climate_research_bundle(raw)

    assert [claim["id"] for claim in normalized["claims"]] == [
        "climate-claim-1",
        "climate-claim-2",
    ]
    assert normalized["claims"][0]["conflicts_with"] == [
        "climate-claim-2"
    ]
    assert normalized["claims"][1]["conflicts_with"] == [
        "climate-claim-1"
    ]
    assert all(
        claim["id"] not in claim["conflicts_with"]
        for claim in normalized["claims"]
    )
