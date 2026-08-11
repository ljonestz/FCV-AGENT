"""Tests for bounded bank and live Climate-FCV grounding."""
import json

from sector_lenses.climate_bank_selector import compact_bank_packet

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
        "selected_evidence_ids": ["SSD-E-001"],
        "selected_pathway_ids": [],
        "project_relevance": {
            "SSD-E-001": {
                "score": 29,
                "matched_fields": ["geographies", "systems_assets"],
            }
        },
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
        "selected_evidence_ids": [
            f"SSD-E-{index:03d}" for index in range(1, 13)
        ],
        "evidence_records": [
            {
                "evidence_id": f"SSD-E-{index:03d}",
                "compact_statement": "x" * 900,
                "uncertainty": "u" * 300,
            }
            for index in range(1, 13)
        ],
    }
    merged = merge_climate_grounding(bank, {})

    assert len(merged["prompt_context"]) <= 12_000
    assert merged["bank_character_count"] <= 6_000


def test_evidence_and_pathway_capsules_preserve_required_metadata() -> None:
    bank = _bank_packet()
    evidence = bank["evidence_records"][0]
    evidence.update({
        "analytical_role": "vulnerability-capacity",
        "geographies": ["Jonglei"],
        "affected_groups": ["fishers"],
        "systems_assets_resources": ["landing sites"],
        "uncertainty": "Screening evidence only.",
    })
    bank["pathways"] = [{
        "pathway_id": "SSD-P-001",
        "interaction_direction": "climate-to-fcv",
        "climate_pressure": "Seasonal flooding",
        "fcv_mediator": "Limited access arrangements",
        "possible_consequence": "Possible livelihood tensions",
        "geographies": ["Jonglei"],
        "systems_assets_resources": ["landing sites"],
        "evidence_strength": "direct",
        "uncertainty": "Not a causal claim.",
        "supporting_evidence_ids": ["SSD-E-001"],
    }]
    bank["selected_pathway_ids"] = ["SSD-P-001"]

    compact = compact_bank_packet(bank)

    assert compact["evidence_capsules"] == [{
        "id": "SSD-E-001",
        "evidence_class": "sensitivity",
        "claim": "Reviewed evidence.",
        "geographies": ["Jonglei"],
        "affected_groups": ["fishers"],
        "systems_assets_resources": ["landing sites"],
        "project_relevance": {
            "score": 29,
            "matched_fields": ["geographies", "systems_assets"],
        },
        "evidence_status": "observed",
        "uncertainty": "Screening evidence only.",
        "source_ids": ["SSD-SRC-001"],
    }]
    assert compact["pathway_capsules"] == [{
        "id": "SSD-P-001",
        "direction": "climate-to-fcv",
        "climate_pressure": "Seasonal flooding",
        "fcv_mediator": "Limited access arrangements",
        "possible_consequence": "Possible livelihood tensions",
        "geographies": ["Jonglei"],
        "systems_assets_resources": ["landing sites"],
        "evidence_strength": "direct",
        "uncertainty": "Not a causal claim.",
        "supporting_evidence_ids": ["SSD-E-001"],
    }]
    assert "sources" not in compact


def test_bank_bound_drops_low_priority_capsules_whole_without_slicing() -> None:
    claims = [f"claim-{index}:" + (str(index) * 2_100) for index in range(1, 4)]
    uncertainties = [
        f"uncertainty-{index}:" + (str(index) * 350)
        for index in range(1, 4)
    ]
    bank = {
        "bank_status": "ok",
        "content_version": "test-1",
        "country_iso3": "SSD",
        "sources": [],
        "pathways": [],
        "selected_evidence_ids": ["SSD-E-001", "SSD-E-002", "SSD-E-003"],
        "selected_pathway_ids": [],
        "evidence_records": [
            {
                "evidence_id": f"SSD-E-{index:03d}",
                "compact_statement": claims[index - 1],
                "analytical_role": "direct-climate-fcv",
                "geographies": ["Unity"],
                "affected_groups": [],
                "systems_assets_resources": ["roads"],
                "evidence_status": "observed",
                "uncertainty": uncertainties[index - 1],
                "source_refs": [],
            }
            for index in range(1, 4)
        ],
    }

    merged = merge_climate_grounding(bank, {})
    capsules = json.loads(merged["prompt_context"])["bank"]["evidence_capsules"]

    assert merged["bank_character_count"] <= 6_000
    assert merged["combined_character_count"] <= 12_000
    assert [item["id"] for item in capsules] == ["SSD-E-001", "SSD-E-002"]
    assert [item["claim"] for item in capsules] == claims[:2]
    assert [item["uncertainty"] for item in capsules] == uncertainties[:2]
    assert claims[2] not in merged["prompt_context"]
    assert uncertainties[2] not in merged["prompt_context"]
    assert merged["selected_item_count"] == 2


def test_prompt_uses_source_ids_without_duplicating_source_metadata() -> None:
    bank = _bank_packet()
    merged = merge_climate_grounding(bank, {})
    assert "SSD-SRC-001" in merged["prompt_context"]
    assert "Reviewed source" not in merged["prompt_context"]
    assert "https://SIPRI.org/a/" not in merged["prompt_context"]
    assert merged["bank_sources"] == bank["sources"]
    assert merged["state"] == "bank-only"

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


def test_candidate_preview_marker_survives_bounded_grounding() -> None:
    import json

    bank = _bank_packet()
    bank["candidate_preview"] = True
    merged = merge_climate_grounding(bank, {})

    assert merged["candidate_preview"] is True
    prompt = json.loads(merged["prompt_context"])
    assert prompt["bank"]["candidate_preview"] is True

def _oversized_mixed_bank() -> dict:
    return {
        "bank_status": "ok",
        "content_version": "test-1",
        "country_iso3": "SSD",
        "sources": [],
        "selected_evidence_ids": ["SSD-E-001", "SSD-E-002"],
        "selected_pathway_ids": ["SSD-P-001", "SSD-P-002"],
        "selected_capsule_ids": [
            "SSD-P-002",
            "SSD-E-001",
            "SSD-P-001",
            "SSD-E-002",
        ],
        "evidence_records": [
            {
                "evidence_id": f"SSD-E-{index:03d}",
                "compact_statement": f"bank-claim-{index}:" + ("c" * 1_350),
                "analytical_role": "direct-climate-fcv",
                "geographies": ["Unity"],
                "affected_groups": ["rural households"],
                "systems_assets_resources": ["roads"],
                "evidence_status": "observed",
                "uncertainty": (
                    f"bank-uncertainty-{index}:" + ("u" * 120)
                ),
                "source_refs": [],
            }
            for index in range(1, 3)
        ],
        "pathways": [
            {
                "pathway_id": f"SSD-P-{index:03d}",
                "interaction_direction": "climate-to-fcv",
                "climate_pressure": (
                    f"pathway-pressure-{index}:" + ("p" * 1_350)
                ),
                "fcv_mediator": "Limited access",
                "possible_consequence": "Possible tensions",
                "geographies": ["Unity"],
                "systems_assets_resources": ["roads"],
                "evidence_strength": "analytical-inference",
                "uncertainty": (
                    f"pathway-uncertainty-{index}:" + ("v" * 120)
                ),
                "supporting_evidence_ids": ["SSD-E-001"],
            }
            for index in range(1, 3)
        ],
    }


def test_mixed_capsules_prune_in_explicit_reverse_priority_order() -> None:
    bank = _oversized_mixed_bank()

    merged = merge_climate_grounding(bank, {})
    prompt_bank = json.loads(merged["prompt_context"])["bank"]
    emitted_ids = {
        item["id"]
        for field in ("evidence_capsules", "pathway_capsules")
        for item in prompt_bank[field]
    }

    assert emitted_ids == {"SSD-P-002", "SSD-E-001", "SSD-P-001"}
    assert "SSD-E-002" not in emitted_ids
    assert merged["selected_item_count"] == 3
    assert merged["bank_character_count"] <= 6_000


def test_oversized_bank_and_live_grounding_drop_whole_strings() -> None:
    bank = _oversized_mixed_bank()
    research = _research_bundle()
    research["claims"] = [
        {
            **research["claims"][0],
            "id": f"climate-claim-{index}",
            "claim": f"live-claim-{index}:" + ("l" * 1_800),
            "uncertainty": (
                f"live-uncertainty-{index}:" + ("w" * 240)
            ),
        }
        for index in range(1, 7)
    ]
    research["claims"][0]["source_ids"] = ["climate-source-1"]
    original_bank = {
        item["evidence_id"]: (
            item["compact_statement"],
            item["uncertainty"],
        )
        for item in bank["evidence_records"]
    }
    original_live = {
        item["id"]: (item["claim"], item["uncertainty"])
        for item in research["claims"]
    }

    merged = merge_climate_grounding(bank, research)
    prompt = json.loads(merged["prompt_context"])
    emitted_bank = prompt["bank"]["evidence_capsules"]
    emitted_live = prompt["research"]["claims"]

    assert len(json.dumps(compact_bank_packet(bank))) > 6_000
    assert len(json.dumps(research)) > 12_000
    assert merged["state"] == "bank+research"
    assert merged["bank_character_count"] <= 6_000
    assert merged["combined_character_count"] <= 12_000
    assert 0 < len(emitted_live) < len(research["claims"])
    for capsule in emitted_bank:
        claim, uncertainty = original_bank[capsule["id"]]
        assert capsule["claim"] == claim
        assert capsule["uncertainty"] == uncertainty
    for claim in emitted_live:
        expected_claim, expected_uncertainty = original_live[claim["id"]]
        assert claim["claim"] == expected_claim
        assert claim["uncertainty"] == expected_uncertainty
