"""Contracts for the versioned Climate-FCV assessment payload."""

import copy

from sector_lenses import (
    CLIMATE_NATIVE_SCHEMA_VERSION,
    climate_missing_fields,
    climate_readout_is_complete,
    merge_climate_repair,
    normalize_lens_diagnostic,
)


def _interaction(direction_id):
    return {
        "direction_id": direction_id,
        "summary": "Flood and insecurity interact with delivery.",
        "pathways": [{
            "pathway_id": f"{direction_id}-1",
            "pressure": "Seasonal flood pulse",
            "mechanism": "Access and allocation conditions change.",
            "project_implication": (
                "Sub-component 1.2 faces a distributional delivery risk."
            ),
            "design_response": "Apply a named seasonal access safeguard.",
            "project_elements": ["Sub-component 1.2 landing sites"],
            "geographies": ["Jonglei"],
            "affected_groups": ["Displaced households"],
            "systems_or_assets": [],
            "time_horizons": ["project-lifetime"],
            "research_claim_ids": [],
            "confidence": "medium",
            "evidence_gap": "Site-level evidence remains incomplete.",
        }],
    }


def canonical_payload():
    return {
        "schema_version": CLIMATE_NATIVE_SCHEMA_VERSION,
        "fcv_baseline": {
            "sensitivity_rating": "Adequate",
            "responsiveness_rating": "Emerging",
            "sensitivity_reasoning": (
                "Conflict-sensitive delivery is explicit."
            ),
            "responsiveness_reasoning": (
                "Some root-cause pathways are present."
            ),
            "evidence_trail": [{
                "claim": "Landing-site access is seasonally constrained.",
                "source_ids": ["climate-source-1"],
                "project_anchor": "Sub-component 1.2 landing sites",
            }],
        },
        "lenses": [{
            "lens_id": "climate",
            "applicability": "material",
            "materiality_level": "high",
            "materiality_summary": "Flooding and insecurity interact.",
            "executive_summary": (
                "Flood access and benefit allocation are the material "
                "intersection."
            ),
            "integration_level": "partly_integrated",
            "integration_rating": "Adequate",
            "integration_summary": (
                "Hazards are recognized but allocation is incomplete."
            ),
            "operating_context": {
                "fcv_setting": (
                    "Jonglei access is institutionally constrained."
                ),
                "climate_setting": (
                    "Flood timing affects landing-site access."
                ),
                "intersection": (
                    "Sub-component 1.2 depends on contested seasonal access."
                ),
            },
            "interaction_readout": [
                _interaction("climate-fcv-on-project"),
                _interaction("project-on-climate-fcv"),
            ],
            "reflections": [{
                "question_key": "cq2_maladaptation",
                "title": "Could the design lock in maladaptation?",
                "status_cue": "partial gap",
                "source": "FCV-Sensitive Climate Action Framework",
                "text": "The siting decision may entrench unequal access.",
            }],
            "supplementary_questions": [{
                "question_id": "cq5-hdp-nexus",
                "title": (
                    "Does delivery connect to humanitarian coordination?"
                ),
                "status_cue": "unconfirmed",
                "source": "Defueling Conflict",
                "text": (
                    "The project names displaced groups but not the "
                    "coordination forum."
                ),
            }],
            "strengths_weaknesses": [{
                "side": "strength",
                "title": "Community co-management",
                "text": "Sub-component 2.1 uses named local institutions.",
            }, {
                "side": "gap",
                "title": "Seasonal access",
                "text": (
                    "The operations manual lacks a flood-access decision rule."
                ),
            }],
            "readout_sections": [],
            "additional_pathways": [],
            "other_pathways": [],
        }],
        "findings": [],
    }


def test_current_schema_survives_and_stale_schema_is_rejected():
    normalized = normalize_lens_diagnostic(
        canonical_payload(), ["climate"]
    )

    assert normalized["error"] is False
    assert normalized["schema_version"] == CLIMATE_NATIVE_SCHEMA_VERSION

    stale = canonical_payload()
    stale["schema_version"] = "climate-native-v0"
    rejected = normalize_lens_diagnostic(stale, ["climate"])

    assert rejected["error"] is True


def test_missing_schema_is_rejected_only_for_nonempty_climate_payloads():
    missing = canonical_payload()
    missing.pop("schema_version")

    assert normalize_lens_diagnostic(missing, ["climate"])["error"] is True
    assert normalize_lens_diagnostic({}, ["climate"])["error"] is False

    non_climate = {
        "lenses": [{
            "lens_id": "agriculture",
            "applicability": "material",
        }],
        "findings": [],
    }
    result = normalize_lens_diagnostic(non_climate, ["agriculture"])
    assert result["error"] is False


def test_empty_climate_envelopes_remain_version_tolerant():
    for payload in (
        None,
        {},
        {"lenses": [], "findings": []},
        {
            "schema_version": "",
            "fcv_baseline": {},
            "lenses": [],
            "findings": [],
        },
        {
            "schema_version": "climate-native-v0",
            "fcv_baseline": {},
            "lenses": [],
            "findings": [],
        },
    ):
        normalized = normalize_lens_diagnostic(payload, ["climate"])
        assert normalized["error"] is False


def test_substantive_climate_content_requires_current_version():
    payloads = (
        {"lenses": [{"lens_id": "climate"}], "findings": []},
        {
            "lenses": [],
            "findings": [{"lens_ids": ["climate"]}],
        },
        {
            "fcv_baseline": {"sensitivity_rating": "Adequate"},
            "lenses": [],
            "findings": [],
        },
    )

    for payload in payloads:
        assert normalize_lens_diagnostic(
            payload, ["climate"]
        )["error"] is True


def test_existing_error_payload_is_not_rejected_as_stale():
    payload = {
        "error": True,
        "message": "Upstream diagnostic failed.",
        "lenses": [],
        "findings": [],
    }

    normalized = normalize_lens_diagnostic(payload, ["climate"])

    assert normalized["error"] is True
    assert normalized["message"] == "Upstream diagnostic failed."


def test_canonical_payload_normalizes_new_fields_and_bounds_them():
    payload = canonical_payload()
    payload["fcv_baseline"].update({
        "sensitivity_rating": "S" * 100,
        "responsiveness_rating": "R" * 100,
        "sensitivity_reasoning": "A" * 1000,
        "responsiveness_reasoning": "B" * 1000,
        "evidence_trail": [
            {
                "claim": f"claim-{index}-" + ("x" * 600),
                "source_ids": [f"source-{item}-" + ("y" * 120)
                               for item in range(6)],
                "project_anchor": "anchor-" + ("z" * 300),
            }
            for index in range(8)
        ] + [{"claim": "drop", "project_anchor": ""}, "drop"],
    })
    climate = payload["lenses"][0]
    climate["executive_summary"] = "E" * 2000
    climate["operating_context"] = {
        "fcv_setting": "F" * 1600,
        "climate_setting": "C" * 1600,
        "intersection": "I" * 1600,
    }
    climate["supplementary_questions"] = [
        {
            "question_id": question_id,
            "title": "T" * 300,
            "status_cue": "material_gap",
            "source": "S" * 200,
            "text": "Q" * 2200,
            "invented": "drop",
        }
        for question_id in (
            "cq1-hazard-delivery",
            "cq2-infra-horizon",
            "cq3-peace-dividend",
            "cq4-vulnerable-reach",
            "cq5-hdp-nexus",
            "not-in-bank",
        )
    ]

    normalized = normalize_lens_diagnostic(payload, ["climate"])
    baseline = normalized["fcv_baseline"]
    climate = normalized["lenses"][0]

    assert len(baseline["sensitivity_rating"]) == 80
    assert len(baseline["responsiveness_rating"]) == 80
    assert len(baseline["sensitivity_reasoning"]) == 900
    assert len(baseline["responsiveness_reasoning"]) == 900
    assert len(baseline["evidence_trail"]) == 6
    assert len(baseline["evidence_trail"][0]["claim"]) == 500
    assert len(baseline["evidence_trail"][0]["project_anchor"]) == 240
    assert len(baseline["evidence_trail"][0]["source_ids"]) == 4
    assert all(
        len(source_id) <= 100
        for source_id in baseline["evidence_trail"][0]["source_ids"]
    )
    assert len(climate["executive_summary"]) <= 1800
    assert all(
        len(climate["operating_context"][key]) == 1400
        for key in ("fcv_setting", "climate_setting", "intersection")
    )
    assert [
        item["question_id"]
        for item in climate["supplementary_questions"]
    ] == [
        "cq1-hazard-delivery",
        "cq2-infra-horizon",
        "cq3-peace-dividend",
        "cq4-vulnerable-reach",
    ]
    assert set(climate["supplementary_questions"][0]) == {
        "question_id", "title", "status_cue", "source", "text",
    }


def test_complete_readout_requires_baseline_context_and_both_interactions():
    normalized = normalize_lens_diagnostic(
        canonical_payload(), ["climate"]
    )
    baseline = normalized["fcv_baseline"]
    complete = normalized["lenses"][0]

    assert climate_readout_is_complete(
        complete, baseline=baseline
    ) is True

    for direction in (
        "climate-fcv-on-project",
        "project-on-climate-fcv",
    ):
        missing = copy.deepcopy(complete)
        missing["interaction_readout"] = [
            item for item in missing["interaction_readout"]
            if item["direction_id"] != direction
        ]
        assert climate_readout_is_complete(
            missing, baseline=baseline
        ) is False

    no_pathways = copy.deepcopy(complete)
    no_pathways["interaction_readout"][0]["pathways"] = []
    assert climate_readout_is_complete(
        no_pathways, baseline=baseline
    ) is False
    assert climate_readout_is_complete(complete) is False


def test_climate_missing_fields_returns_deterministic_dotted_paths():
    payload = {
        "fcv_baseline": {
            "sensitivity_rating": "Adequate",
        },
        "lenses": [{
            "lens_id": "climate",
            "materiality_level": "high",
            "operating_context": {"fcv_setting": "Constrained."},
            "interaction_readout": [{
                "direction_id": "climate-fcv-on-project",
            }],
        }],
    }

    assert climate_missing_fields(payload) == [
        "schema_version",
        "fcv_baseline.responsiveness_rating",
        "fcv_baseline.sensitivity_reasoning",
        "fcv_baseline.responsiveness_reasoning",
        "fcv_baseline.evidence_trail",
        "lenses.climate.executive_summary",
        "lenses.climate.integration_rating",
        "lenses.climate.integration_summary",
        "lenses.climate.materiality_summary",
        "lenses.climate.reflections",
        "lenses.climate.strengths_weaknesses",
        "lenses.climate.operating_context.climate_setting",
        "lenses.climate.operating_context.intersection",
        "lenses.climate.interaction_readout.project-on-climate-fcv",
    ]
    assert climate_missing_fields(None) == [
        "schema_version",
        "fcv_baseline",
        "lenses.climate",
    ]


def test_merge_climate_repair_changes_only_requested_leaves():
    primary = canonical_payload()
    primary["untouched"] = {"value": "keep"}
    primary["lenses"].append({
        "lens_id": "agriculture",
        "summary": "keep",
    })
    repair = canonical_payload()
    repair["schema_version"] = "replacement-version"
    repair["fcv_baseline"]["sensitivity_rating"] = "Replacement"
    repair["fcv_baseline"]["sensitivity_reasoning"] = (
        "Unrequested replacement reasoning"
    )
    repair["fcv_baseline"]["responsiveness_reasoning"] = (
        "Requested replacement reasoning"
    )
    repair_climate = repair["lenses"][0]
    repair_climate["operating_context"] = {
        "fcv_setting": "Replacement FCV.",
        "climate_setting": "Replacement climate.",
        "intersection": "Replacement intersection.",
    }
    repair_climate["executive_summary"] = "Do not copy."
    repair_climate["supplementary_questions"] = [{
        "question_id": "cq6-adaptive-triggers",
        "title": "Replacement question",
        "status_cue": "gap",
        "source": "CCDR guidance note",
        "text": "Replacement text.",
    }]

    merged = merge_climate_repair(
        primary,
        repair,
        [
            "schema_version",
            "fcv_baseline.sensitivity_rating",
            "fcv_baseline.responsiveness_reasoning",
            "lenses.climate.operating_context.intersection",
            "lenses.climate.supplementary_questions",
        ],
    )
    climate = next(
        item for item in merged["lenses"]
        if item.get("lens_id") == "climate"
    )

    assert merged["schema_version"] == "replacement-version"
    assert merged["fcv_baseline"]["sensitivity_rating"] == "Replacement"
    assert (
        merged["fcv_baseline"]["sensitivity_reasoning"]
        == primary["fcv_baseline"]["sensitivity_reasoning"]
    )
    assert (
        merged["fcv_baseline"]["responsiveness_reasoning"]
        == "Requested replacement reasoning"
    )
    assert climate["operating_context"] == {
        "fcv_setting": (
            primary["lenses"][0]["operating_context"]["fcv_setting"]
        ),
        "climate_setting": (
            primary["lenses"][0]["operating_context"]["climate_setting"]
        ),
        "intersection": "Replacement intersection.",
    }
    assert (
        climate["supplementary_questions"]
        == repair_climate["supplementary_questions"]
    )
    assert (
        climate["executive_summary"]
        == primary["lenses"][0]["executive_summary"]
    )
    assert merged["lenses"][1] == primary["lenses"][1]
    assert merged["untouched"] == primary["untouched"]
    assert merged["findings"] == primary["findings"]
    assert primary["schema_version"] == CLIMATE_NATIVE_SCHEMA_VERSION
    repair_climate["supplementary_questions"][0]["text"] = "Mutated."
    assert (
        climate["supplementary_questions"][0]["text"]
        == "Replacement text."
    )


def test_merge_climate_repair_replaces_requested_root_objects_by_deepcopy():
    primary = canonical_payload()
    primary["fcv_baseline"]["legacy_only"] = "remove"
    repair = canonical_payload()
    repair["fcv_baseline"] = {
        "sensitivity_rating": "Replacement",
        "evidence_trail": [{"claim": "Replacement claim"}],
    }
    repair["lenses"][0]["executive_summary"] = "Replacement summary."

    merged = merge_climate_repair(
        primary,
        repair,
        ["fcv_baseline", "lenses.climate"],
    )

    assert merged["fcv_baseline"] == repair["fcv_baseline"]
    assert "legacy_only" not in merged["fcv_baseline"]
    assert merged["lenses"][0] == repair["lenses"][0]
    repair["fcv_baseline"]["evidence_trail"][0]["claim"] = "Mutated."
    repair["lenses"][0]["executive_summary"] = "Mutated."
    assert (
        merged["fcv_baseline"]["evidence_trail"][0]["claim"]
        == "Replacement claim"
    )
    assert merged["lenses"][0]["executive_summary"] == "Replacement summary."


def test_merge_climate_repair_creates_climate_lens_only_when_requested():
    primary = {"lenses": [{"lens_id": "agriculture"}]}
    repair = {
        "lenses": [{
            "lens_id": "climate",
            "executive_summary": "Repaired summary.",
        }],
        "findings": [{"finding_id": "repair-only"}],
    }

    not_requested = merge_climate_repair(
        primary, repair, ["schema_version"]
    )
    assert not any(
        lens.get("lens_id") == "climate"
        for lens in not_requested["lenses"]
    )
    assert not_requested["findings"] == []

    requested = merge_climate_repair(
        primary, repair, ["lenses.climate"]
    )
    climate = next(
        lens for lens in requested["lenses"]
        if lens.get("lens_id") == "climate"
    )
    assert climate == {
        "lens_id": "climate",
        "executive_summary": "Repaired summary.",
    }
    assert requested["findings"] == []


def test_merge_climate_repair_preserves_values_for_missing_incoming_leaves():
    primary = canonical_payload()
    repair = {
        "fcv_baseline": {},
        "lenses": [{
            "lens_id": "climate",
            "operating_context": {},
            "integration_summary": "Replacement integration summary.",
        }],
    }

    merged = merge_climate_repair(
        primary,
        repair,
        [
            "fcv_baseline.sensitivity_rating",
            "lenses.climate.operating_context.intersection",
            "lenses.climate.integration_summary",
        ],
    )

    assert (
        merged["fcv_baseline"]["sensitivity_rating"]
        == primary["fcv_baseline"]["sensitivity_rating"]
    )
    assert (
        merged["lenses"][0]["operating_context"]
        == primary["lenses"][0]["operating_context"]
    )
    assert (
        merged["lenses"][0]["integration_summary"]
        == "Replacement integration summary."
    )
