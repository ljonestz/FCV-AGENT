"""Realistic-volume tests for compact Climate-FCV bank selection."""

from __future__ import annotations

from collections import Counter
import copy
from datetime import date
import hashlib
import json
from pathlib import Path

import sector_lenses.climate_bank_selector as selector_module
from sector_lenses.climate_bank import (
    ClimateBankLoad,
    load_climate_bank,
    materialize_bank_manifest,
)
from sector_lenses.climate_bank_selector import (
    CLIMATE_BANK_MAX_CHARS,
    CLIMATE_BANK_TARGET_ITEMS,
    _compact_packet_length,
    compact_bank_packet,
    select_bank_manifest,
)
from sector_lenses.climate_project_profile import ProjectClimateProfile


FIXTURE = Path(__file__).parent / "fixtures" / "climate_bank" / "runtime_v1.json"


def _resign(release: dict) -> None:
    sources = [
        {key: value for key, value in source.items() if key != "checksum"}
        for source in release["sources"]
    ]
    payload = json.dumps(
        sources,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    release["source_manifest_checksum"] = hashlib.sha256(payload).hexdigest()


def _expanded_bank(tmp_path: Path):
    release = json.loads(FIXTURE.read_text(encoding="utf-8"))
    source_three = copy.deepcopy(release["sources"][0])
    source_three.update(
        {
            "source_id": "SSD-SRC-003",
            "title": "Synthetic institutional capacity note",
            "url": "https://example.org/synthetic-capacity-note",
        }
    )
    release["sources"].append(source_three)
    source_ids = ["SSD-SRC-001", "SSD-SRC-002", "SSD-SRC-003"]

    fish_base = copy.deepcopy(release["evidence_records"][0])
    road_base = copy.deepcopy(release["evidence_records"][1])
    evidence = []
    for index in range(1, 13):
        is_fisheries = index <= 6
        record = copy.deepcopy(fish_base if is_fisheries else road_base)
        record["evidence_id"] = f"SSD-E-{index:03d}"
        record["statement"] = (
            f"VERBOSE_SENTINEL_{index} "
            + ("Detailed canonical source context. " * 45)
        )
        record["compact_statement"] = (
            f"Synthetic {'Jonglei fisheries' if is_fisheries else 'Unity road'} "
            f"evidence {index}."
        )
        record["analytical_role"] = (
            "direct-climate-fcv" if index % 2 else "vulnerability-capacity"
        )
        record["source_refs"] = [
            {
                "source_id": source_ids[(index - 1) % len(source_ids)],
                "locator": f"Synthetic section {index}",
            }
        ]
        if is_fisheries:
            record.update(
                {
                    "geographies": ["Jonglei"],
                    "affected_groups": ["fishers", "seasonal users"],
                    "sectors": ["fisheries"],
                    "systems_assets_resources": ["landing sites", "Sudd wetlands"],
                    "institutions": ["BFMU"],
                    "impact_tags": ["landing-site-access"],
                    "mediator_tags": ["seasonal-access"],
                }
            )
        else:
            record.update(
                {
                    "geographies": ["Unity"],
                    "affected_groups": ["rural households"],
                    "sectors": ["transport"],
                    "systems_assets_resources": ["feeder roads", "markets"],
                    "institutions": ["county road authority"],
                    "impact_tags": ["market-access-disruption"],
                    "mediator_tags": ["limited-drainage-capacity"],
                }
            )
        evidence.append(record)

    pathway_base = release["pathways"][0]
    pathway_specs = [
        (1, [1, 7, 8, 9, 10], True),
        (2, [2, 9, 10, 11, 12], True),
        (3, [7, 1, 2, 3, 4], False),
        (4, [8, 3, 4, 5, 6], False),
    ]
    pathways = []
    for pathway_number, evidence_numbers, is_fisheries in pathway_specs:
        pathway = copy.deepcopy(pathway_base)
        pathway_id = f"SSD-P-{pathway_number:03d}"
        evidence_ids = [
            f"SSD-E-{evidence_number:03d}"
            for evidence_number in evidence_numbers
        ]
        pathway["pathway_id"] = pathway_id
        pathway["supporting_evidence_ids"] = evidence_ids
        pathway["link_evidence"] = {
            key: [evidence_ids[0]]
            for key in ("pressure", "impact", "mediator", "consequence")
        }
        pathway["evidence_strength"] = "direct"
        if is_fisheries:
            pathway.update(
                {
                    "climate_pressure": "Seasonal flooding in Jonglei",
                    "documented_impact": "Landing-site access disruption",
                    "fcv_mediator": "Seasonal access constraints",
                    "possible_consequence": "Possible fisheries livelihood tension",
                    "geographies": ["Jonglei"],
                    "affected_groups": ["fishers", "seasonal users"],
                    "sectors": ["fisheries"],
                    "systems_assets_resources": ["landing sites", "Sudd wetlands"],
                    "institutions": ["BFMU"],
                    "compact_statement": (
                        f"Synthetic Jonglei fisheries pathway {pathway_number}."
                    ),
                }
            )
        else:
            pathway.update(
                {
                    "climate_pressure": "Seasonal flooding in Unity",
                    "documented_impact": "Feeder-road market disruption",
                    "fcv_mediator": "Limited drainage capacity",
                    "possible_consequence": "Possible rural access tension",
                    "geographies": ["Unity"],
                    "affected_groups": ["rural households"],
                    "sectors": ["transport"],
                    "systems_assets_resources": ["feeder roads", "markets"],
                    "institutions": ["county road authority"],
                    "compact_statement": (
                        f"Synthetic Unity road pathway {pathway_number}."
                    ),
                }
            )
        pathways.append(pathway)

    release["evidence_records"] = evidence
    release["pathways"] = pathways
    country = release["countries"]["SSD"]
    country["evidence_ids"] = [item["evidence_id"] for item in evidence]
    country["pathway_ids"] = [item["pathway_id"] for item in pathways]
    _resign(release)
    path = tmp_path / "runtime.json"
    path.write_text(json.dumps(release), encoding="utf-8")
    return load_climate_bank(path)


def _profile(*, roads: bool = False) -> ProjectClimateProfile:
    return ProjectClimateProfile(
        country="South Sudan",
        instrument="IPF",
        document_stage="PCN",
        geographies=("Unity",) if roads else ("Jonglei",),
        sectors=("transport",) if roads else ("fisheries",),
        project_elements=("feeder roads",) if roads else ("landing sites",),
        affected_groups=(
            ("rural households",)
            if roads
            else ("fishers", "seasonal users")
        ),
        institutions=("county road authority",) if roads else ("BFMU",),
        systems_assets=(
            ("feeder roads", "markets")
            if roads
            else ("landing sites", "Sudd wetlands")
        ),
        documented_hazards=("flood",),
        time_horizons=("current",),
        signal_metadata=(),
        unresolved=(),
    )


def _select(bank, *, profile: ProjectClimateProfile) -> dict:
    return select_bank_manifest(
        bank,
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=profile,
    )


def test_realistic_selection_retains_target_pathways_and_relevant_sets(
    tmp_path: Path,
) -> None:
    bank = _expanded_bank(tmp_path)
    fisheries = _select(bank, profile=_profile())
    roads = _select(bank, profile=_profile(roads=True))

    assert set(fisheries["evidence_ids"]) != set(roads["evidence_ids"])
    for manifest in (fisheries, roads):
        assert (
            len(manifest["evidence_ids"]) + len(manifest["pathway_ids"])
            <= CLIMATE_BANK_TARGET_ITEMS
        )
        assert len(manifest["evidence_ids"]) + len(manifest["pathway_ids"]) >= 6
        assert len(manifest["pathway_ids"]) >= 1

        packet = materialize_bank_manifest(bank, manifest)
        assert len(packet["evidence_records"]) > len(
            manifest["evidence_ids"]
        )
        full = json.dumps(
            packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        assert len(full) > CLIMATE_BANK_MAX_CHARS
        assert _compact_packet_length(packet) <= CLIMATE_BANK_MAX_CHARS
        compact = json.dumps(
            compact_bank_packet(packet),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        assert "VERBOSE_SENTINEL" not in compact


def _balanced_bank() -> ClimateBankLoad:
    release = json.loads(
        FIXTURE.with_name("runtime_v1_1_candidate.json").read_text(
            encoding="utf-8"
        )
    )
    source_base = release["sources"][0]
    sources = []
    for number in range(1, 6):
        source = copy.deepcopy(source_base)
        source.update(
            {
                "source_id": f"SSD-SRC-{number:03d}",
                "title": f"Synthetic source {number}",
                "url": f"https://example.org/balanced-source-{number}",
            }
        )
        sources.append(source)
    release["sources"] = sources

    evidence_base = release["evidence_records"][0]

    def evidence(
        number: int,
        evidence_class: str,
        source_number: int,
        claim: str,
        *,
        relevant: bool = True,
        refresh_tier: str = "structural",
        review_due: str = "2099-12-31",
    ) -> dict:
        record = copy.deepcopy(evidence_base)
        record.update(
            {
                "evidence_id": f"SSD-E-{number:03d}",
                "statement": claim,
                "compact_statement": claim,
                "evidence_class": evidence_class,
                "analytical_role": (
                    "direct-climate-fcv"
                    if evidence_class == "direct-climate-fcv"
                    else (
                        "physical-baseline"
                        if evidence_class == "climate-pressure"
                        else "vulnerability-capacity"
                    )
                ),
                "geographies": ["Jonglei"] if relevant else ["South Sudan"],
                "sectors": ["fisheries"] if relevant else ["agriculture"],
                "affected_groups": ["fishers"] if relevant else ["farmers"],
                "institutions": ["BFMU"] if relevant else ["crop ministry"],
                "systems_assets_resources": (
                    ["landing sites"] if relevant else ["irrigation canals"]
                ),
                "impact_tags": ["landing sites"] if relevant else ["crop yields"],
                "hazard_tags": ["flood"] if relevant else ["drought"],
                "time_horizons": ["current"],
                "source_refs": [
                    {
                        "source_id": f"SSD-SRC-{source_number:03d}",
                        "locator": f"Synthetic section {number}",
                    }
                ],
                "refresh_tier": refresh_tier,
                "review_due": review_due,
            }
        )
        return record

    records = [
        evidence(
            1,
            "climate-pressure",
            1,
            "Flood pressure affects Jonglei landing sites.",
        ),
        evidence(
            2,
            "sensitivity",
            2,
            "Jonglei fishers face seasonal access constraints during floods.",
        ),
        evidence(
            3,
            "coping-capacity",
            3,
            "BFMU access planning supports fishers at landing sites.",
        ),
        evidence(
            4,
            "institutional-capacity",
            4,
            "BFMU flood planning covers Jonglei landing sites.",
        ),
        evidence(
            5,
            "adaptive-capacity",
            5,
            "Fishers adapt seasonal use of Jonglei landing sites.",
        ),
        evidence(
            6,
            "direct-climate-fcv",
            1,
            "Landing site disruption can raise livelihood tensions.",
        ),
        evidence(
            7,
            "climate-pressure",
            5,
            "A stale flood estimate covers Jonglei landing sites.",
            refresh_tier="current",
            review_due="2026-07-31",
        ),
        evidence(
            8,
            "sensitivity",
            4,
            "Jonglei fishers face seasonal access constraints during floods today.",
        ),
        evidence(
            9,
            "response-performance",
            5,
            "National crop response performance is documented.",
            relevant=False,
        ),
    ]
    release["evidence_records"] = records

    pathway_base = release["pathways"][0]

    def pathway(
        number: int,
        direction: str,
        supporting: list[int],
        *,
        relevant: bool = True,
    ) -> dict:
        item = copy.deepcopy(pathway_base)
        ids = [f"SSD-E-{value:03d}" for value in supporting]
        item.update(
            {
                "pathway_id": f"SSD-P-{number:03d}",
                "interaction_direction": direction,
                "supporting_evidence_ids": ids,
                "link_evidence": {
                    key: [ids[index % len(ids)]]
                    for index, key in enumerate(
                        ("pressure", "impact", "mediator", "consequence")
                    )
                },
                "geographies": ["Jonglei"] if relevant else ["South Sudan"],
                "sectors": ["fisheries"] if relevant else ["agriculture"],
                "affected_groups": ["fishers"] if relevant else ["farmers"],
                "institutions": ["BFMU"] if relevant else ["crop ministry"],
                "systems_assets_resources": (
                    ["landing sites"] if relevant else ["irrigation canals"]
                ),
                "climate_pressure": "Flood" if relevant else "Drought",
                "documented_impact": (
                    "Landing sites" if relevant else "Crop yields"
                ),
                "compact_statement": (
                    f"Synthetic {'fisheries' if relevant else 'crop'} pathway "
                    f"{number}."
                ),
            }
        )
        return item

    release["pathways"] = [
        pathway(1, "climate-to-fcv", [1, 2]),
        pathway(2, "fcv-to-climate", [3, 4]),
        pathway(3, "bidirectional", [5, 6]),
        pathway(4, "climate-to-fcv", [9], relevant=False),
    ]
    country = release["countries"]["SSD"]
    country["evidence_ids"] = [item["evidence_id"] for item in records]
    country["pathway_ids"] = [
        item["pathway_id"] for item in release["pathways"]
    ]
    release["generated_at"] = "2026-08-01T00:00:00Z"
    return ClimateBankLoad("ok", "", release, candidate_preview=True)


def _supporting_source_counts(bank: ClimateBankLoad, manifest: dict) -> Counter:
    evidence = {
        item["evidence_id"]: item for item in bank.release["evidence_records"]
    }
    pathways = {
        item["pathway_id"]: item for item in bank.release["pathways"]
    }
    counts = Counter()
    for evidence_id in manifest["evidence_ids"]:
        for ref in evidence[evidence_id]["source_refs"]:
            counts[ref["source_id"]] += 1
    for pathway_id in manifest["pathway_ids"]:
        source_ids = {
            ref["source_id"]
            for evidence_id in pathways[pathway_id]["supporting_evidence_ids"]
            for ref in evidence[evidence_id]["source_refs"]
        }
        counts.update(source_ids)
    return counts


def test_balanced_packet_uses_supported_roles_and_both_directions() -> None:
    bank = _balanced_bank()
    manifest = _select(bank, profile=_profile())
    roles = {
        row["balance_role"]
        for row in manifest["diagnostics"]["selected"]
    }
    vulnerability_roles = roles & {
        "sensitivity", "coping-capacity", "adaptive-capacity"
    }
    assert "climate-pressure" in roles
    assert len(vulnerability_roles) >= 2
    assert "institutional-capacity" in roles
    assert "climate-to-fcv-pathway" in roles
    assert "fcv-to-climate-pathway" in roles
    assert (
        len(manifest["evidence_ids"]) + len(manifest["pathway_ids"])
        == CLIMATE_BANK_TARGET_ITEMS
    )


def test_vulnerability_slots_prefer_distinct_supported_roles() -> None:
    bank = _balanced_bank()
    release = copy.deepcopy(bank.release)
    release["evidence_records"][7]["compact_statement"] = (
        "Separate sensitivity evidence concerns fisheries households."
    )
    release["evidence_records"][7]["statement"] = (
        "Separate sensitivity evidence concerns fisheries households."
    )
    for index in (2, 4):
        release["evidence_records"][index].update(
            {
                "geographies": ["South Sudan"],
                "affected_groups": ["farmers"],
                "institutions": ["crop ministry"],
                "systems_assets_resources": ["irrigation canals"],
                "impact_tags": ["crop yields"],
                "hazard_tags": ["drought"],
                "time_horizons": ["historical"],
            }
        )
    extra = copy.deepcopy(release["evidence_records"][5])
    extra.update(
        {
            "evidence_id": "SSD-E-010",
            "statement": "Distinct direct evidence supports fisheries access.",
            "compact_statement": (
                "Distinct direct evidence supports fisheries access."
            ),
            "source_refs": [
                {
                    "source_id": "SSD-SRC-005",
                    "locator": "Synthetic section 10",
                }
            ],
        }
    )
    release["evidence_records"].append(extra)
    release["countries"]["SSD"]["evidence_ids"].append("SSD-E-010")
    bank = ClimateBankLoad("ok", "", release, candidate_preview=True)

    manifest = _select(bank, profile=_profile())
    vulnerability_roles = {
        row["balance_role"]
        for row in manifest["diagnostics"]["selected"]
        if row["balance_role"]
        in {"sensitivity", "coping-capacity", "adaptive-capacity"}
    }

    assert len(vulnerability_roles) >= 2
    assert vulnerability_roles & {"coping-capacity", "adaptive-capacity"}
    assert "vulnerability-capacity" not in manifest["diagnostics"][
        "missing_classes"
    ]


def test_stale_current_and_near_duplicate_records_are_suppressed() -> None:
    manifest = _select(_balanced_bank(), profile=_profile())
    suppressed = {
        row["id"]: row["reason"]
        for row in manifest["diagnostics"]["suppressed"]
    }
    assert "SSD-E-007" not in manifest["evidence_ids"]
    assert suppressed["SSD-E-007"] == "stale_current"
    assert "SSD-E-008" not in manifest["evidence_ids"]
    assert suppressed["SSD-E-008"] == "near_duplicate"


def test_near_duplicate_is_suppressed_across_capacity_roles() -> None:
    bank = _balanced_bank()
    release = copy.deepcopy(bank.release)
    release["evidence_records"][7]["evidence_class"] = "coping-capacity"
    bank = ClimateBankLoad("ok", "", release, candidate_preview=True)

    manifest = _select(bank, profile=_profile())
    suppressed = {
        row["id"]: row["reason"]
        for row in manifest["diagnostics"]["suppressed"]
    }

    assert "SSD-E-002" in manifest["evidence_ids"]
    assert "SSD-E-008" not in manifest["evidence_ids"]
    assert suppressed["SSD-E-008"] == "near_duplicate"


def test_v1_structural_defaults_are_not_marked_stale() -> None:
    manifest = _select(
        load_climate_bank(FIXTURE),
        profile=_profile(),
    )
    assert all(
        row["reason"] != "stale_current"
        for row in manifest["diagnostics"]["suppressed"]
    )


def test_current_record_staleness_uses_selection_date_not_release_date() -> None:
    bank = _balanced_bank()
    release = copy.deepcopy(bank.release)
    release["evidence_records"][6]["review_due"] = "2026-08-05"
    bank = ClimateBankLoad("ok", "", release, candidate_preview=True)

    manifest = select_bank_manifest(
        bank,
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(),
        as_of=date(2026, 8, 10),
    )

    assert "SSD-E-007" not in manifest["evidence_ids"]
    assert {
        row["id"]: row["reason"]
        for row in manifest["diagnostics"]["suppressed"]
    }["SSD-E-007"] == "stale_current"


def test_pathway_with_any_stale_current_support_is_suppressed() -> None:
    for supporting_numbers in ([7], [1, 7]):
        bank = _balanced_bank()
        release = copy.deepcopy(bank.release)
        pathway = release["pathways"][0]
        supporting_ids = [
            f"SSD-E-{number:03d}" for number in supporting_numbers
        ]
        pathway["supporting_evidence_ids"] = supporting_ids
        pathway["link_evidence"] = {
            key: [supporting_ids[index % len(supporting_ids)]]
            for index, key in enumerate(
                ("pressure", "impact", "mediator", "consequence")
            )
        }
        bank = ClimateBankLoad("ok", "", release, candidate_preview=True)

        manifest = select_bank_manifest(
            bank,
            country="South Sudan",
            country_scope="single",
            resolved_country_count=1,
            project_profile=_profile(),
            as_of=date(2026, 8, 10),
        )

        assert "SSD-P-001" not in manifest["pathway_ids"]
        assert {
            row["id"]: row["reason"]
            for row in manifest["diagnostics"]["suppressed"]
        }["SSD-P-001"] == "stale_support"


def test_low_relevance_record_is_not_used_to_fill_missing_class() -> None:
    bank = _balanced_bank()
    release = copy.deepcopy(bank.release)
    relevant_institution = release["evidence_records"][3]
    relevant_institution.update(
        {
            "geographies": ["South Sudan"],
            "sectors": ["agriculture"],
            "affected_groups": ["farmers"],
            "institutions": ["crop ministry"],
            "systems_assets_resources": ["irrigation canals"],
            "impact_tags": ["crop yields"],
            "hazard_tags": ["drought"],
            "time_horizons": ["historical"],
        }
    )
    release["evidence_records"][8]["time_horizons"] = ["historical"]
    bank = ClimateBankLoad("ok", "", release, candidate_preview=True)
    manifest = _select(bank, profile=_profile())
    assert "SSD-E-004" not in manifest["evidence_ids"]
    assert "SSD-E-009" not in manifest["evidence_ids"]
    assert "institution-response" in manifest["diagnostics"]["missing_classes"]


def test_time_only_and_zero_matches_are_low_relevance_in_both_paths() -> None:
    bank = _balanced_bank()
    release = copy.deepcopy(bank.release)
    for index in (3, 8):
        release["evidence_records"][index].update(
            {
                "geographies": ["South Sudan"],
                "sectors": ["agriculture"],
                "affected_groups": ["farmers"],
                "institutions": ["crop ministry"],
                "systems_assets_resources": ["irrigation canals"],
                "impact_tags": ["crop yields"],
                "hazard_tags": ["drought"],
                "time_horizons": ["current"],
            }
        )
    bank = ClimateBankLoad("ok", "", release, candidate_preview=True)

    structured = _select(bank, profile=_profile())
    legacy = select_bank_manifest(
        bank,
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        sector="",
        project_signals="Jonglei landing sites current",
    )

    for manifest in (structured, legacy):
        assert "SSD-E-004" not in manifest["evidence_ids"]
        assert "SSD-E-009" not in manifest["evidence_ids"]
        suppressed = {
            row["id"]: row["reason"]
            for row in manifest["diagnostics"]["suppressed"]
        }
        assert suppressed["SSD-E-004"] == "low_relevance"
        assert suppressed["SSD-E-009"] == "low_relevance"
        assert "institution-response" in manifest["diagnostics"][
            "missing_classes"
        ]


def test_pathway_diversity_counts_every_supporting_source() -> None:
    bank = _balanced_bank()
    manifest = _select(bank, profile=_profile())
    counts = _supporting_source_counts(bank, manifest)
    assert "SSD-P-001" in manifest["pathway_ids"]
    assert counts["SSD-SRC-001"] >= 1
    assert counts["SSD-SRC-002"] >= 1
    assert max(counts.values()) <= 3


def test_usable_lower_duplicate_survives_unusable_higher_duplicate() -> None:
    bank = _balanced_bank()
    release = copy.deepcopy(bank.release)
    release["evidence_records"][3]["source_refs"] = [
        {
            "source_id": "SSD-SRC-001",
            "locator": "Synthetic section 4",
        }
    ]
    lower = copy.deepcopy(release["evidence_records"][5])
    lower.update(
        {
            "evidence_id": "SSD-E-010",
            "source_refs": [
                {
                    "source_id": "SSD-SRC-005",
                    "locator": "Synthetic section 10",
                }
            ],
        }
    )
    release["evidence_records"].append(lower)
    release["countries"]["SSD"]["evidence_ids"].append("SSD-E-010")
    bank = ClimateBankLoad("ok", "", release, candidate_preview=True)

    manifest = _select(bank, profile=_profile())
    suppressed = {
        row["id"]: row["reason"]
        for row in manifest["diagnostics"]["suppressed"]
    }

    assert "SSD-E-006" not in manifest["evidence_ids"]
    assert suppressed["SSD-E-006"] == "source_diversity"
    assert "SSD-E-010" in manifest["evidence_ids"]


def test_packet_feasibility_refills_and_recomputes_suppressions(
    monkeypatch,
) -> None:
    bank = _balanced_bank()
    release = copy.deepcopy(bank.release)
    release["evidence_records"][4].update(
        {
            "geographies": ["South Sudan"],
            "sectors": ["agriculture"],
            "affected_groups": ["farmers"],
            "institutions": ["crop ministry"],
            "systems_assets_resources": ["irrigation canals"],
            "impact_tags": ["crop yields"],
            "hazard_tags": ["drought"],
            "time_horizons": ["historical"],
        }
    )
    for number, source_number, claim in (
        (10, 5, "Alternative institution evidence supports fisher access."),
        (11, 1, "Final source-one evidence supports community access."),
    ):
        record = copy.deepcopy(release["evidence_records"][5])
        record.update(
            {
                "evidence_id": f"SSD-E-{number:03d}",
                "statement": claim,
                "compact_statement": claim,
                "source_refs": [
                    {
                        "source_id": f"SSD-SRC-{source_number:03d}",
                        "locator": f"Synthetic section {number}",
                    }
                ],
            }
        )
        release["evidence_records"].append(record)
        release["countries"]["SSD"]["evidence_ids"].append(
            f"SSD-E-{number:03d}"
        )
    bank = ClimateBankLoad("ok", "", release, candidate_preview=True)
    original_length = selector_module._compact_packet_length

    def reject_evidence_six(packet: dict) -> int:
        selected_ids = {
            record["evidence_id"]
            for record in packet.get("evidence_records", [])
        }
        if "SSD-E-006" in selected_ids:
            return CLIMATE_BANK_MAX_CHARS + 1
        return original_length(packet)

    monkeypatch.setattr(
        selector_module,
        "_compact_packet_length",
        reject_evidence_six,
    )
    manifest = _select(bank, profile=_profile())
    suppressed = {
        row["id"]: row["reason"]
        for row in manifest["diagnostics"]["suppressed"]
    }

    assert "SSD-E-006" not in manifest["evidence_ids"]
    assert suppressed["SSD-E-006"] == "packet_bound"
    assert {"SSD-E-010", "SSD-E-011"} <= set(manifest["evidence_ids"])

    source_counts = _supporting_source_counts(bank, manifest)
    evidence = {
        item["evidence_id"]: item
        for item in bank.release["evidence_records"]
    }
    pathways = {
        item["pathway_id"]: item for item in bank.release["pathways"]
    }
    for record_id, reason in suppressed.items():
        if reason != "source_diversity":
            continue
        if record_id in evidence:
            source_ids = {
                ref["source_id"]
                for ref in evidence[record_id]["source_refs"]
            }
        else:
            source_ids = {
                ref["source_id"]
                for evidence_id in pathways[record_id][
                    "supporting_evidence_ids"
                ]
                for ref in evidence[evidence_id]["source_refs"]
            }
        assert any(source_counts[source_id] >= 3 for source_id in source_ids)
