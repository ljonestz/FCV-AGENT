"""Model-facing country-bank qualifier, provenance, and coverage contracts."""

from __future__ import annotations

import json

from sector_lenses.climate_grounding import (
    CLIMATE_BANK_MAX_CHARS,
    merge_climate_grounding,
)


def _prompt_bank(packet: dict) -> tuple[dict, str]:
    merged = merge_climate_grounding(packet, {})
    return json.loads(merged["prompt_context"])["bank"], merged["prompt_context"]


def _qualified_packet() -> dict:
    return {
        "bank_status": "ok",
        "content_version": "test-qualifiers",
        "country_iso3": "PNG",
        "country_profile": {
            "coverage": [
                {
                    "dimension": "geographic",
                    "covered": ["island communities"],
                    "limits": ["coverage is uneven across provinces"],
                }
            ],
            "known_gaps": ["no ward-level population denominator"],
        },
        "sources": [
            {
                "source_id": "PNG-SRC-103",
                "title": "Annual results report",
                "organization": "UNDP",
                "publication_date": "2025-05",
                "publication_date_basis": "publication",
                "url": "https://example.org/annual-results",
            }
        ],
        "evidence_records": [
            {
                "evidence_id": "PNG-E-103",
                "compact_statement": (
                    "The programme expected to benefit over 16,000 people; "
                    "this is planned reach, not achieved reach. The report "
                    "asserts a climate-security mechanism but provides no "
                    "measured local causal estimate."
                ),
                "evidence_status": "projected",
                "evidence_class": "direct-climate-fcv",
                "analytical_role": "direct-climate-fcv",
                "scenario": "SSP2-4.5",
                "time_horizons": ["medium-term"],
                "confidence": "low",
                "uncertainty": "Preliminary, source-reported claim.",
                "interaction_direction": "fcv-to-climate",
                "geographies": ["island communities"],
                "affected_groups": ["coastal households"],
                "administrative_level": "site",
                "source_refs": [
                    {
                        "source_id": "PNG-SRC-103",
                        "locator": "physical PDF p. 17; printed pp. 29-30",
                    }
                ],
            }
        ],
        "pathways": [
            {
                "pathway_id": "PNG-P-103",
                "compact_statement": (
                    "Preliminary reverse-FCV pathway: insecurity may reduce "
                    "the durability of climate adaptation access."
                ),
                "evidence_strength": "hypothesis",
                "supporting_evidence_ids": ["PNG-E-103"],
                "interaction_direction": "fcv-to-climate",
                "geographies": ["island communities"],
                "affected_groups": ["coastal households"],
                "alternative_explanations": ["service access constraints"],
                "uncertainty": "No causal estimate is reported.",
            }
        ],
    }


def test_final_prompt_preserves_qualifiers_sources_and_profile_coverage() -> None:
    bank, prompt = _prompt_bank(_qualified_packet())
    evidence = bank["evidence_records"][0]
    pathway = bank["pathways"][0]

    assert len(prompt) <= CLIMATE_BANK_MAX_CHARS
    assert evidence["scenario"] == "SSP2-4.5"
    assert evidence["time_horizons"] == ["medium-term"]
    assert evidence["confidence"] == "low"
    assert evidence["evidence_status"] == "projected"
    assert evidence["interaction_direction"] == "fcv-to-climate"
    assert evidence["geographies"] == ["island communities"]
    assert evidence["affected_groups"] == ["coastal households"]
    assert evidence["administrative_level"] == "site"
    assert evidence["source_refs"][0]["locator"] == (
        "physical PDF p. 17; printed pp. 29-30"
    )
    assert "expected to benefit" in evidence["compact_statement"]
    assert "not achieved reach" in evidence["compact_statement"]
    assert "no measured local causal estimate" in evidence["compact_statement"]
    assert "Preliminary" in evidence["uncertainty"]
    assert pathway["interaction_direction"] == "fcv-to-climate"
    assert pathway["alternative_explanations"] == ["service access constraints"]
    assert bank["sources"][0]["publication_date"] == "2025-05"
    assert bank["sources"][0]["url"] == "https://example.org/annual-results"
    assert bank["country_profile"]["coverage"][0]["limits"] == [
        "coverage is uneven across provinces"
    ]
    assert bank["country_profile"]["known_gaps"] == [
        "no ward-level population denominator"
    ]


def test_budget_trimming_keeps_qualifiers_atomic_and_pathway_support_closed() -> None:
    packet = _qualified_packet()
    omitted = {
        **packet["evidence_records"][0],
        "evidence_id": "PNG-E-104",
        "uncertainty": "preliminary " + ("x" * 6500),
    }
    packet["evidence_records"].append(omitted)
    packet["pathways"][0]["supporting_evidence_ids"].append("PNG-E-104")

    bank, prompt = _prompt_bank(packet)

    assert len(prompt) <= CLIMATE_BANK_MAX_CHARS
    assert [item["evidence_id"] for item in bank["evidence_records"]] == [
        "PNG-E-103"
    ]
    assert "Preliminary, source-reported claim." == (
        bank["evidence_records"][0]["uncertainty"]
    )
    assert bank["pathways"] == []
    assert "PNG-E-104" not in prompt


def test_missing_profile_and_empty_pathways_disclose_selection_limits() -> None:
    packet = _qualified_packet()
    packet.pop("country_profile")
    packet["evidence_records"][0]["evidence_class"] = "institutional-capacity"
    packet["evidence_records"][0]["analytical_role"] = "vulnerability-capacity"
    packet["pathways"] = []

    bank, prompt = _prompt_bank(packet)

    assert len(prompt) <= CLIMATE_BANK_MAX_CHARS
    assert bank["evidence_records"][0]["evidence_class"] == (
        "institutional-capacity"
    )
    assert bank["coverage_metadata_available"] is False
    assert "metadata unavailable" in bank["coverage_note"].lower()
    assert "complete national or population coverage" in bank["coverage_note"]
    assert bank["pathways"] == []
    assert "does not establish that no such pathways exist" in (
        bank["pathway_coverage_note"]
    )
    assert "hazard-only" not in prompt.lower()


def test_materialization_carries_additive_country_profile() -> None:
    from pathlib import Path

    from sector_lenses.climate_bank import (
        ClimateBankLoad,
        materialize_bank_manifest,
    )

    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "climate_bank"
        / "runtime_v1_1_candidate.json"
    )
    release = json.loads(fixture.read_text(encoding="utf-8"))
    release["country_profiles"] = {
        "SSD": {
            "coverage": [{"dimension": "geographic", "covered": ["Jonglei"]}],
            "known_gaps": ["No county population denominator."],
        }
    }
    bank = ClimateBankLoad("ok", "", release, candidate_preview=True)
    packet = materialize_bank_manifest(
        bank,
        {
            "bank_status": "ok",
            "content_version": release["content_version"],
            "country_iso3": "SSD",
            "evidence_ids": ["SSD-E-001"],
            "pathway_ids": [],
            "candidate_preview": True,
        },
    )

    assert packet["bank_status"] == "ok"
    assert packet["country_profile"] == release["country_profiles"]["SSD"]


def test_profile_projection_prioritizes_text_and_removes_record_id_lists() -> None:
    packet = _qualified_packet()
    packet["country_profile"] = {
        "known_gaps": [
            {
                "text": f"Specific unresolved limitation {index}. "
                + ("Source support remains local. " * 3),
                "evidence_ids": [f"PNG-E-{item:03d}" for item in range(12)],
                "pathway_ids": ["PNG-P-001", "PNG-P-002"],
            }
            for index in range(5)
        ],
        "coverage": [
            {
                "dimension": "evidence_class",
                "value": f"class-{index}",
                "status": "partial",
                "record_ids": [f"PNG-E-{item:03d}" for item in range(20)],
                "gap_note": "Named local evidence remains uneven.",
            }
            for index in range(12)
        ],
    }

    bank, _ = _prompt_bank(packet)
    profile = bank["country_profile"]

    assert profile["known_gaps"]
    assert profile["known_gaps"][0]["text"].startswith(
        "Specific unresolved limitation 0."
    )
    assert profile["known_gaps"][0]["evidence_count"] == 12
    assert profile["known_gaps"][0]["pathway_count"] == 2
    assert "evidence_ids" not in profile["known_gaps"][0]
    assert profile["coverage"]
    assert profile["coverage"][0]["record_count"] == 20
    assert "record_ids" not in profile["coverage"][0]
    assert "coverage" in profile.get("truncated_fields", [])
    assert "known_gaps" in profile.get("truncated_fields", [])
    assert len(json.dumps(profile, ensure_ascii=False)) <= 1_700


def test_unrelated_large_source_cannot_crowd_out_referenced_evidence() -> None:
    packet = _qualified_packet()
    packet["sources"].insert(
        0,
        {
            "source_id": "PNG-SRC-UNRELATED",
            "title": "Unrelated appendix",
            "organization": "UNDP",
            "publication_date": "2025",
            "publication_date_basis": "publication",
            "url": "https://example.org/" + ("x" * 4800),
        },
    )

    bank, prompt = _prompt_bank(packet)

    assert "PNG-E-103" in prompt
    assert [source["source_id"] for source in bank["sources"]] == [
        "PNG-SRC-103"
    ]


def test_oversized_limitation_is_disclosed_without_dropping_profile() -> None:
    packet = _qualified_packet()
    packet["limitations"] = ["Source review limitation: " + ("x" * 6500)]

    bank, prompt = _prompt_bank(packet)

    assert len(prompt) <= CLIMATE_BANK_MAX_CHARS
    assert bank["coverage_metadata_available"] is True
    assert bank["limitations_omitted"] is True
    assert "Some bank limitations were omitted" in bank["limitations_note"]


def test_real_country_profile_keeps_gap_text_and_coverage_counts() -> None:
    from pathlib import Path

    fixture = (
        Path(__file__).parents[1]
        / "data"
        / "climate-fcv-country-bank"
        / "countries"
        / "AFG"
        / "approved"
        / "2026.10.26"
        / "profile.json"
    )
    raw_profile = json.loads(fixture.read_text(encoding="utf-8"))
    packet = _qualified_packet()
    packet["country_profile"] = {
        "coverage": raw_profile["coverage"],
        "known_gaps": raw_profile["known_gaps"],
    }

    bank, _ = _prompt_bank(packet)
    profile = bank["country_profile"]

    assert profile["known_gaps"][0]["text"].startswith(
        "Climate-projection gap:"
    )
    assert profile["known_gaps"][0]["evidence_count"] > 0
    assert "evidence_ids" not in profile["known_gaps"][0]
    assert profile["coverage"]
    assert profile["coverage"][0]["record_count"] > 0
    assert "record_ids" not in profile["coverage"][0]
    assert profile["truncated_fields"]
    assert len(json.dumps(profile, ensure_ascii=False)) <= 1_700
