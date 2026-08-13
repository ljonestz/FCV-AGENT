"""Tests for deterministic, bounded Climate-FCV bank selection."""

from __future__ import annotations

import json
from pathlib import Path

import sector_lenses.climate_bank_selector as selector_module
from sector_lenses.climate_bank import (
    load_climate_bank,
    materialize_bank_manifest,
)
from sector_lenses.climate_bank_selector import (
    CLIMATE_BANK_MAX_CHARS,
    CLIMATE_BANK_MAX_ITEMS,
    select_bank_manifest,
)


FIXTURE = (
    Path(__file__).parent / "fixtures" / "climate_bank" / "runtime_v1.json"
)
CANDIDATE_RELEASE = (
    Path(__file__).parents[1]
    / "data"
    / "climate-fcv-country-bank"
    / "releases"
    / "candidates"
    / "2026.08"
    / "runtime.json"
)


def _select(signals: str) -> dict[str, object]:
    return select_bank_manifest(
        load_climate_bank(FIXTURE),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        sector="Fisheries",
        project_signals=signals,
    )


def test_fisheries_and_roads_select_different_records() -> None:
    fisheries = _select(
        "Jonglei landing sites fishers BFMU seasonal users"
    )
    roads = _select("Unity feeder roads access markets flood drainage")
    assert fisheries["evidence_ids"] != roads["evidence_ids"]


def test_selection_is_stable() -> None:
    assert _select("Jonglei landing sites fishers") == _select(
        "Jonglei landing sites fishers"
    )


def test_physical_baseline_cannot_crowd_out_qualitative_evidence() -> None:
    manifest = _select("flood drought temperature")
    bank = load_climate_bank(FIXTURE)
    ids = set(manifest["evidence_ids"])
    selected = [
        item
        for item in bank.release["evidence_records"]
        if item["evidence_id"] in ids
    ]
    assert (
        sum(
            item["analytical_role"] == "physical-baseline"
            for item in selected
        )
        <= 2
    )


def test_multi_country_scope_is_explicitly_unsupported() -> None:
    result = select_bank_manifest(
        load_climate_bank(FIXTURE),
        country="South Sudan",
        country_scope="multi",
        resolved_country_count=2,
        sector="Fisheries",
        project_signals="Jonglei",
    )
    assert result["bank_status"] == "unavailable"
    assert result["warning_code"] == "bank_scope_unsupported"


def test_selector_resolves_country_alias_and_emits_only_manifest_ids() -> None:
    bank = load_climate_bank(FIXTURE)
    manifest = select_bank_manifest(
        bank,
        country="Republic of South Sudan",
        country_scope="single",
        resolved_country_count=1,
        sector="Fisheries",
        project_signals="Jonglei landing sites",
    )
    assert set(manifest) == {
        "bank_status",
        "warning_code",
        "schema_version",
        "content_version",
        "country_iso3",
        "evidence_ids",
        "pathway_ids",
    }
    assert manifest["country_iso3"] == "SSD"
    assert all(
        value.startswith("SSD-E-") for value in manifest["evidence_ids"]
    )
    assert all(
        value.startswith("SSD-P-") for value in manifest["pathway_ids"]
    )


def test_unknown_country_is_nonfatal() -> None:
    result = select_bank_manifest(
        load_climate_bank(FIXTURE),
        country="Atlantis",
        country_scope="single",
        resolved_country_count=1,
        sector="Fisheries",
        project_signals="landing sites",
    )
    assert result == {
        "bank_status": "unavailable",
        "warning_code": "bank_country_unavailable",
    }


def test_selection_respects_item_and_materialized_character_bounds() -> None:
    bank = load_climate_bank(FIXTURE)
    manifest = _select(
        "Jonglei Unity fisheries transport landing sites feeder roads "
        "markets fishers households BFMU authority flood drainage"
    )
    assert (
        len(manifest["evidence_ids"]) + len(manifest["pathway_ids"])
        <= CLIMATE_BANK_MAX_ITEMS
    )
    packet = materialize_bank_manifest(bank, manifest)
    compact = json.dumps(
        packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    assert packet["bank_status"] == "ok"
    assert len(compact) <= CLIMATE_BANK_MAX_CHARS


def test_all_oversized_records_fail_closed_instead_of_returning_empty_ok(
    monkeypatch,
) -> None:
    original_length = selector_module._compact_packet_length

    def every_selected_packet_is_oversized(packet):
        has_records = bool(
            packet.get("evidence_records") or packet.get("pathways")
        )
        if has_records:
            return CLIMATE_BANK_MAX_CHARS + 1
        return original_length(packet)

    monkeypatch.setattr(
        selector_module, "_compact_packet_length",
        every_selected_packet_is_oversized,
    )
    assert _select("Jonglei landing sites fishers") == {
        "bank_status": "unavailable",
        "warning_code": "bank_packet_too_large",
    }


def test_unavailable_bank_warning_is_preserved() -> None:
    result = select_bank_manifest(
        load_climate_bank(FIXTURE.with_name("missing.json")),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        sector="Fisheries",
        project_signals="Jonglei",
    )
    assert result == {
        "bank_status": "unavailable",
        "warning_code": "bank_missing",
    }


def test_reviewed_candidate_flag_survives_selection_and_compaction(
    monkeypatch,
) -> None:
    candidate = FIXTURE.with_name("runtime_v1_1_candidate.json")
    monkeypatch.setenv("CLIMATE_COUNTRY_BANK_PATH", str(candidate))
    monkeypatch.setenv(
        "CLIMATE_COUNTRY_BANK_PREVIEW", "reviewed-candidate"
    )
    bank = load_climate_bank()

    manifest = select_bank_manifest(
        bank,
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        sector="Transport",
        project_signals="Unity roads flood drainage",
    )
    assert manifest["candidate_preview"] is True

    packet = materialize_bank_manifest(bank, manifest)
    assert packet["candidate_preview"] is True
    assert selector_module.compact_bank_packet(packet)[
        "candidate_preview"
    ] is True


def test_multi_country_candidate_release_materializes_each_country(
    monkeypatch,
) -> None:
    monkeypatch.setenv("CLIMATE_COUNTRY_BANK_PATH", str(CANDIDATE_RELEASE))
    monkeypatch.setenv(
        "CLIMATE_COUNTRY_BANK_PREVIEW", "reviewed-candidate"
    )
    bank = load_climate_bank()

    assert bank.status == "ok"
    assert len(bank.release["countries"]) == 24
    for country in bank.release["countries"].values():
        manifest = select_bank_manifest(
            bank,
            country=country["name"],
            country_scope="single",
            resolved_country_count=1,
            sector="Climate resilience",
            project_signals=country["name"],
        )
        assert manifest["bank_status"] == "ok", country["iso3"]
        packet = materialize_bank_manifest(bank, manifest)
        assert packet["bank_status"] == "ok", country["iso3"]
        assert packet["country_iso3"] == country["iso3"]
        assert packet["candidate_preview"] is True
