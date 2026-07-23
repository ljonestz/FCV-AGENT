"""Contract tests for lens detection, hidden diagnostics, and cross-lens merging."""

import json
from itertools import permutations
from pathlib import Path

from sector_lenses import (
    detect_lens_suggestions,
    extract_lens_diagnostic,
    extract_lens_evidence,
    lens_catalogue,
    load_registry,
    merge_lens_findings,
    normalize_lens_diagnostic,
    strip_lens_blocks,
)


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "sector_lenses"


def test_catalogue_and_detection_are_ranked_and_non_blocking():
    registry = load_registry(FIXTURE_ROOT)

    catalogue = lens_catalogue(registry)
    suggestions = detect_lens_suggestions(
        "The irrigation activity addresses food security and irrigation access.",
        registry,
    )
    uncertain = detect_lens_suggestions("An irrigation activity is mentioned.", registry)

    assert catalogue == [{
        "id": "test-agriculture",
        "name": "Test Agriculture Lens",
        "version": "1.2.0",
        "description": "Test-only lens for registry and prompt-slice coverage.",
        "activation": "suggested",
        "readout_sections": [{
            "id": "production-opportunities",
            "title": "Where agricultural design can help",
            "item_ids": ["equitable-access", "resilient-markets"],
        }],
        "aliases": ["agriculture", "irrigation"],
        "compatibility": {"compatible_with": ["*"], "incompatible_with": []},
    }]
    assert suggestions[0]["lens_id"] == "test-agriculture"
    assert suggestions[0]["confidence"] == "high"
    assert suggestions[0]["selected_by_default"] is True
    assert uncertain[0]["confidence"] == "uncertain"
    assert uncertain[0]["selected_by_default"] is False
    assert detect_lens_suggestions("No relevant sector text.", registry) == []


def test_hidden_lens_diagnostic_is_validated_and_removed_from_display_text():
    payload = {
        "lenses": [{"lens_id": "test-agriculture", "applicability": "material"}],
        "findings": [{
            "lens_ids": ["test-agriculture"],
            "evidence": ["Targeting uses water-user groups."],
            "status": "partially_addressed",
            "source_ids": ["agri-guidance"],
            "core_mappings": ["dnh:3"],
            "mechanism": "water access grievance",
            "geography": "project area",
            "action_target": "beneficiary targeting",
        }],
    }
    text = "Visible assessment\n%%%LENS_DIAGNOSTIC_START%%%\n" + json.dumps(payload) + (
        "\n%%%LENS_DIAGNOSTIC_END%%%\nVisible close"
    )

    diagnostic = extract_lens_diagnostic(text, active_lens_ids=["test-agriculture"])

    assert diagnostic["error"] is False
    assert diagnostic["findings"][0]["core_mappings"] == ["dnh:3"]
    assert "LENS_DIAGNOSTIC" not in strip_lens_blocks(text)
    assert strip_lens_blocks(text) == "Visible assessment\n\nVisible close"


def test_diagnostic_normalizes_declared_readout_items():
    payload = {"lenses": [{
        "lens_id": "test-agriculture",
        "applicability": "material",
        "materiality_summary": "Water access is material.",
        "analysis_emphasis": ["resource access"],
        "readout_sections": [{
            "section_id": "production-opportunities",
            "items": [{
                "item_id": "equitable-access",
                "status": "supported",
                "mechanism": "Transparent water allocation reduces grievance risk.",
                "evidence": ["Water-user groups allocate access."],
                "evidence_gap": "Seasonal-user representation is not documented.",
                "trade_off": "Formal rules may exclude customary users.",
                "source_ids": ["agri-guidance"],
            }],
        }],
        "other_pathways": [{
            "pathway": "resilient-markets",
            "status": "not_material",
            "reason": "The project has no market component.",
        }],
    }], "findings": []}
    schema = {"test-agriculture": {
        "production-opportunities": {
            "equitable-access", "resilient-markets"
        }
    }}

    result = normalize_lens_diagnostic(
        payload,
        ["test-agriculture"],
        {"test-agriculture": {"agri-guidance"}},
        schema,
    )

    lens = result["lenses"][0]
    assert lens["materiality_summary"] == "Water access is material."
    assert lens["readout_sections"][0]["items"][0]["status"] == "supported"
    assert lens["other_pathways"][0]["status"] == "not_material"


def test_climate_diagnostic_normalizes_materiality_interactions_and_pathways():
    payload = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "materiality_level": "high",
        "materiality_summary": "Flood and fragility pressures are central.",
        "source_ids": ["peace-social-dividends", "invented"],
        "interaction_readout": [{
            "direction_id": "climate-fcv-on-project",
            "summary": "Flood, displacement, and weak access could disrupt delivery.",
            "mechanisms": ["Flood damage combines with insecurity."],
            "project_implications": ["Remote sites may become inaccessible."],
            "positive_effects": [],
            "adverse_effects": ["Infrastructure completion may be delayed."],
            "evidence": ["The PCN identifies flood-prone sites."],
            "evidence_gap": "Site-level access data are incomplete.",
            "source_ids": ["peace-social-dividends", "invented"],
        }, {
            "direction_id": "project-on-climate-fcv",
            "summary": "Benefit rules could strengthen resilience or deepen exclusion.",
            "mechanisms": ["Co-management changes access to natural resources."],
            "project_implications": ["Customary users need representation."],
            "positive_effects": ["More legitimate resource rules."],
            "adverse_effects": ["Seasonal users could be excluded."],
            "evidence": ["Community institutions allocate access."],
            "evidence_gap": "Seasonal users are not mapped.",
            "source_ids": ["peace-social-dividends"],
        }],
        "readout_sections": [{
            "section_id": "invest-in",
            "items": [{
                "item_id": "livelihoods-opportunity",
                "status": "supported",
                "mechanism": "Diversified livelihoods reduce climate exposure.",
                "project_contribution": "The project finances resilient livelihoods.",
                "strengthening_action": "Clarify access and benefit-sharing rules.",
                "evidence": ["A livelihoods component is financed."],
                "source_ids": ["peace-social-dividends"],
            }],
        }],
        "additional_pathways": [{
            "section_id": "invest-in",
            "title": "Shared ecosystem restoration",
            "status": "potential",
            "mechanism": "Joint restoration can create collective benefits.",
            "project_contribution": "The project restores shared watersheds.",
            "strengthening_action": "Define joint oversight and dispute resolution.",
            "evidence": ["Watershed restoration is included."],
            "source_ids": ["peace-social-dividends"],
        }],
    }], "findings": []}
    schema = {"climate": {
        "invest-in": {"livelihoods-opportunity"},
        "deliver-through": {"flexible-adaptive-delivery"},
    }}

    result = normalize_lens_diagnostic(
        payload,
        ["climate"],
        {"climate": {"peace-social-dividends"}},
        schema,
    )

    climate = result["lenses"][0]
    assert climate["materiality_level"] == "high"
    assert [item["direction_id"] for item in climate["interaction_readout"]] == [
        "climate-fcv-on-project", "project-on-climate-fcv",
    ]
    assert climate["interaction_readout"][0]["source_ids"] == [
        "peace-social-dividends"
    ]
    pathway = climate["readout_sections"][0]["items"][0]
    assert pathway["project_contribution"].startswith("The project finances")
    assert pathway["strengthening_action"].startswith("Clarify access")
    assert climate["additional_pathways"][0]["title"] == (
        "Shared ecosystem restoration"
    )


def test_climate_diagnostic_rejects_invalid_extensions_and_maps_legacy_low():
    payload = {"lenses": [{
        "lens_id": "climate",
        "applicability": "not_applicable",
        "materiality_level": "extreme",
        "interaction_readout": [{
            "direction_id": "invented-direction",
            "summary": "Drop this.",
        }],
        "additional_pathways": [{
            "section_id": "invented-section",
            "title": "Drop this",
            "status": "supported",
            "project_contribution": "Unsupported.",
            "strengthening_action": "Unsupported.",
            "evidence": ["Unsupported."],
        }],
    }], "findings": []}

    result = normalize_lens_diagnostic(
        payload,
        ["climate"],
        {"climate": {"peace-social-dividends"}},
        {"climate": {"invest-in": {"livelihoods-opportunity"}}},
    )

    climate = result["lenses"][0]
    assert climate["materiality_level"] == "low"
    assert climate["interaction_readout"] == []
    assert climate["additional_pathways"] == []


def test_climate_interactions_keep_specific_pathways_and_horizons():
    payload = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "materiality_level": "high",
        "materiality_summary": "Flood timing is material to fisheries delivery.",
        "interaction_readout": [{
            "direction_id": "climate-fcv-on-project",
            "summary": "Flood timing and insecurity affect landing sites.",
            "pathways": [{
                "pathway_id": "climate-fcv-on-project-1",
                "pressure": "More erratic flood timing",
                "mechanism": (
                    "Road access and seasonal movement become less predictable."
                ),
                "project_implication": (
                    "Landing-site works in Upper Nile may become inaccessible."
                ),
                "design_response": (
                    "Use site flood thresholds and seasonal work windows."
                ),
                "project_elements": ["Landing-site rehabilitation"],
                "geographies": ["Upper Nile"],
                "affected_groups": ["Fishing households"],
                "systems_or_assets": ["Access roads"],
                "time_horizons": [
                    "project-lifetime",
                    "asset-system-lifetime",
                ],
                "research_claim_ids": ["climate-claim-1"],
                "confidence": "medium",
                "evidence_gap": "Site design standards are not documented.",
            }],
        }, {
            "direction_id": "project-on-climate-fcv",
            "summary": "Access rules may redistribute resilience.",
            "pathways": [{
                "pathway_id": "project-on-climate-fcv-1",
                "pressure": "Formalized access rules",
                "mechanism": "Rules change who can fish during variable seasons.",
                "project_implication": (
                    "Seasonal users may lose access and adaptive options."
                ),
                "design_response": (
                    "Represent seasonal users and monitor distributional effects."
                ),
                "project_elements": ["BFMU governance"],
                "geographies": ["Sudd"],
                "affected_groups": ["Seasonal fishing households"],
                "time_horizons": [
                    "current-near-term",
                    "project-lifetime",
                ],
                "research_claim_ids": ["climate-claim-2"],
                "confidence": "medium",
                "evidence_gap": "",
            }],
        }],
        "readout_sections": [],
        "additional_pathways": [],
    }], "findings": []}

    result = normalize_lens_diagnostic(payload, ["climate"])
    pathways = result["lenses"][0]["interaction_readout"][0]["pathways"]

    assert pathways[0]["pathway_id"] == "climate-fcv-on-project-1"
    assert pathways[0]["time_horizons"][-1] == "asset-system-lifetime"
    assert pathways[0]["systems_or_assets"] == ["Access roads"]


def test_generic_climate_pathway_is_suppressed():
    payload = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "materiality_level": "medium",
        "interaction_readout": [{
            "direction_id": "climate-fcv-on-project",
            "summary": "Generic summary.",
            "pathways": [{
                "pathway_id": "climate-fcv-on-project-1",
                "pressure": "Climate stress",
                "mechanism": "Tensions may increase.",
                "project_implication": "The project may be affected.",
                "design_response": "Monitor climate.",
                "project_elements": [],
                "geographies": [],
                "affected_groups": [],
                "time_horizons": [],
                "research_claim_ids": [],
                "confidence": "low",
            }],
        }],
    }], "findings": []}

    result = normalize_lens_diagnostic(payload, ["climate"])

    assert result["lenses"][0]["interaction_readout"][0]["pathways"] == []


def test_climate_dividend_pathway_ids_are_stable():
    payload = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "readout_sections": [{
            "section_id": "invest-in",
            "items": [{
                "item_id": "livelihoods-opportunity",
                "status": "potential",
                "project_contribution": "A livelihoods component exists.",
                "strengthening_action": "Clarify inclusive access.",
            }],
        }],
        "additional_pathways": [{
            "section_id": "invest-in",
            "title": "Shared restoration",
            "status": "potential",
            "project_contribution": "The project restores wetlands.",
            "strengthening_action": "Add joint oversight.",
            "evidence": ["Restoration is financed."],
        }],
    }], "findings": []}
    schema = {"climate": {
        "invest-in": {"livelihoods-opportunity"},
    }}

    result = normalize_lens_diagnostic(
        payload, ["climate"], readout_schema_by_lens=schema
    )
    lens = result["lenses"][0]

    assert lens["readout_sections"][0]["items"][0]["pathway_id"] == (
        "livelihoods-opportunity"
    )
    assert lens["additional_pathways"][0]["pathway_id"] == (
        "additional-invest-in-1"
    )


def test_readout_normalization_treats_scalar_collections_as_empty():
    payload = {"lenses": [{
        "lens_id": "test-agriculture",
        "applicability": "possible",
        "analysis_emphasis": None,
        "evidence": "not-a-list",
        "source_ids": None,
        "readout_sections": [{
            "section_id": "production-opportunities",
            "title": "Spoofed model title",
            "items": [{
                "item_id": "equitable-access",
                "status": "potential",
                "evidence": None,
                "source_ids": "agri-guidance",
            }],
        }],
    }], "findings": []}

    result = normalize_lens_diagnostic(
        payload,
        ["test-agriculture"],
        {"test-agriculture": {"agri-guidance"}},
        {"test-agriculture": {
            "production-opportunities": {"equitable-access"}
        }},
    )

    lens = result["lenses"][0]
    item = lens["readout_sections"][0]["items"][0]
    assert lens["analysis_emphasis"] == []
    assert lens["evidence"] == []
    assert lens["source_ids"] == []
    assert item["evidence"] == []
    assert item["source_ids"] == []
    assert "title" not in lens["readout_sections"][0]


def test_hidden_stage1_evidence_is_validated_against_active_lenses():
    text = "%%%LENS_EVIDENCE_START%%%" + json.dumps({"lenses": [{
        "lens_id": "test-agriculture",
        "evidence_requests": ["Confirm irrigated districts."],
        "research_intents": ["Check water-access grievances."],
    }, {"lens_id": "unknown", "evidence_requests": ["Drop"], "research_intents": []}]}) + "%%%LENS_EVIDENCE_END%%%"

    evidence = extract_lens_evidence(text, ["test-agriculture"])

    assert evidence["error"] is False
    assert [item["lens_id"] for item in evidence["lenses"]] == ["test-agriculture"]


def test_hidden_diagnostics_treat_scalar_collections_as_empty():
    evidence = extract_lens_evidence(
        "%%%LENS_EVIDENCE_START%%%" + json.dumps({"lenses": [{
            "lens_id": "climate",
            "evidence_requests": None,
            "research_intents": "not-a-list",
        }]}) + "%%%LENS_EVIDENCE_END%%%",
        ["climate"],
    )
    diagnostic = extract_lens_diagnostic(
        "%%%LENS_DIAGNOSTIC_START%%%" + json.dumps({
            "lenses": [],
            "findings": [{
                "lens_ids": None,
                "core_mappings": "dnh:1",
                "evidence": 7,
                "source_ids": None,
                "mechanism": "x",
                "geography": "y",
                "action_target": "z",
            }],
        }) + "%%%LENS_DIAGNOSTIC_END%%%",
        ["climate"],
    )

    assert evidence["lenses"][0]["evidence_requests"] == []
    assert evidence["lenses"][0]["research_intents"] == []
    assert diagnostic["error"] is False
    assert diagnostic["findings"] == []


def test_incomplete_hidden_block_never_leaks_into_display_text():
    text = "Visible assessment\n%%%LENS_DIAGNOSTIC_START%%%\npartial hidden JSON"

    assert strip_lens_blocks(text) == "Visible assessment"


def test_incomplete_dedup_keys_are_rejected_and_merge_is_permutation_stable():
    complete = [
        {"lens_ids": ["climate"], "evidence": ["A"], "source_ids": ["c1"],
         "core_mappings": ["dnh:3", "ost:2"], "mechanism": "competition",
         "geography": "north", "action_target": "targeting", "status": "partially_addressed"},
        {"lens_ids": ["energy"], "evidence": ["B"], "source_ids": ["e1"],
         "core_mappings": ["ost:2", "shift:B"], "mechanism": "Competition",
         "geography": "North", "action_target": "Targeting", "status": "gap"},
    ]
    outputs = [merge_lens_findings(order) for order in permutations(complete)]
    incomplete_text = "%%%LENS_DIAGNOSTIC_START%%%" + json.dumps({
        "lenses": [], "findings": [{**complete[0], "geography": ""}]
    }) + "%%%LENS_DIAGNOSTIC_END%%%"

    assert outputs[0] == outputs[1]
    assert outputs[0][0]["status"] == "gap"
    assert extract_lens_diagnostic(incomplete_text, ["climate"])["findings"] == []


def test_parser_failure_is_non_fatal_and_dedup_retains_contributors():
    invalid = extract_lens_diagnostic(
        "%%%LENS_DIAGNOSTIC_START%%%not-json%%%LENS_DIAGNOSTIC_END%%%",
        active_lens_ids=["one"],
    )
    merged = merge_lens_findings([
        {
            "lens_ids": ["climate"], "evidence": ["A"], "source_ids": ["c1"],
            "core_mappings": ["dnh:3", "ost:2"], "mechanism": "resource competition",
            "geography": "north", "action_target": "targeting", "status": "gap",
        },
        {
            "lens_ids": ["energy"], "evidence": ["B"], "source_ids": ["e1"],
            "core_mappings": ["dnh:3"], "mechanism": "Resource Competition",
            "geography": "North", "action_target": "Targeting", "status": "gap",
        },
    ])

    assert invalid["error"] is True
    assert len(merged) == 1
    assert merged[0]["lens_ids"] == ["climate", "energy"]
    assert merged[0]["source_ids"] == ["c1", "e1"]
    assert merged[0]["evidence"] == ["A", "B"]
