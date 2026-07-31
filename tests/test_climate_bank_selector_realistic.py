"""Realistic-volume tests for compact Climate-FCV bank selection."""

from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

from sector_lenses.climate_bank import (
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


def _select(bank, *, sector: str, signals: str) -> dict:
    return select_bank_manifest(
        bank,
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        sector=sector,
        project_signals=signals,
    )


def _primary_source_counts(bank, manifest: dict) -> Counter:
    evidence = {
        item["evidence_id"]: item for item in bank.release["evidence_records"]
    }
    pathways = {
        item["pathway_id"]: item for item in bank.release["pathways"]
    }
    counts = Counter()
    for evidence_id in manifest["evidence_ids"]:
        counts[evidence[evidence_id]["source_refs"][0]["source_id"]] += 1
    for pathway_id in manifest["pathway_ids"]:
        support_id = pathways[pathway_id]["supporting_evidence_ids"][0]
        counts[evidence[support_id]["source_refs"][0]["source_id"]] += 1
    return counts


def test_realistic_selection_retains_target_pathways_and_relevant_sets(
    tmp_path: Path,
) -> None:
    bank = _expanded_bank(tmp_path)
    fisheries = _select(
        bank,
        sector="Fisheries",
        signals="Jonglei landing sites fishers BFMU seasonal users Sudd",
    )
    roads = _select(
        bank,
        sector="Transport",
        signals="Unity feeder roads markets drainage rural households",
    )

    assert set(fisheries["evidence_ids"]) != set(roads["evidence_ids"])
    for manifest in (fisheries, roads):
        assert (
            len(manifest["evidence_ids"]) + len(manifest["pathway_ids"])
            == CLIMATE_BANK_TARGET_ITEMS
        )
        assert len(manifest["pathway_ids"]) == 2
        assert max(_primary_source_counts(bank, manifest).values()) <= 3

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
