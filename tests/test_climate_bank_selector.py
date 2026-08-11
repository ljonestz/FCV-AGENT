"""Tests for deterministic, structured Climate-FCV bank selection."""

from __future__ import annotations

import copy
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
    CLIMATE_BANK_MAX_ITEMS,
    select_bank_manifest,
)
from sector_lenses.climate_grounding import merge_climate_grounding
from sector_lenses.climate_project_profile import ProjectClimateProfile


FIXTURE = Path(__file__).parent / "fixtures" / "climate_bank" / "runtime_v1.json"
V1_1_FIXTURE = FIXTURE.with_name("runtime_v1_1_candidate.json")


def _profile(**overrides: object) -> ProjectClimateProfile:
    values: dict[str, object] = {
        "country": "South Sudan",
        "instrument": "IPF",
        "document_stage": "PCN",
        "geographies": ("Jonglei",),
        "sectors": ("fisheries",),
        "project_elements": ("landing sites",),
        "affected_groups": ("fishers", "seasonal users"),
        "institutions": ("BFMU",),
        "systems_assets": ("landing sites", "Sudd wetlands"),
        "documented_hazards": ("flood",),
        "time_horizons": ("current",),
        "signal_metadata": (),
        "unresolved": (),
    }
    values.update(overrides)
    return ProjectClimateProfile(**values)


def _select(profile: ProjectClimateProfile) -> dict[str, object]:
    return select_bank_manifest(
        load_climate_bank(FIXTURE),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=profile,
    )


def _selected_row(manifest: dict[str, object], record_id: str) -> dict:
    return next(
        row for row in manifest["diagnostics"]["selected"] if row["id"] == record_id
    )


def _candidate_bank() -> ClimateBankLoad:
    release = json.loads(V1_1_FIXTURE.read_text(encoding="utf-8"))
    return ClimateBankLoad("ok", "", release, candidate_preview=True)


def test_jonglei_fisheries_outranks_unrelated_record() -> None:
    bank = load_climate_bank(FIXTURE)
    release = copy.deepcopy(bank.release)
    release["evidence_records"][1]["geographies"] = ["South Sudan"]
    manifest = select_bank_manifest(
        ClimateBankLoad("ok", "", release),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(),
    )
    assert _selected_row(manifest, "SSD-E-001")["score"] > _selected_row(
        manifest, "SSD-E-002"
    )["score"]


def test_named_element_and_geography_outweigh_hazard_only_overlap() -> None:
    manifest = _select(
        _profile(
            affected_groups=(),
            institutions=(),
            systems_assets=(),
            time_horizons=(),
        )
    )
    local = _selected_row(manifest, "SSD-E-001")
    hazard_only = _selected_row(manifest, "SSD-E-002")
    assert local["score"] > hazard_only["score"]
    assert {"geographies", "project_elements"} <= set(local["matched_fields"])
    assert hazard_only["matched_fields"] == ["documented_hazards"]


def test_reviewed_alias_canonical_values_drive_structured_matching() -> None:
    bank = _candidate_bank()
    release = copy.deepcopy(bank.release)
    release["evidence_records"][0]["systems_assets_resources"] = ["fish landing sites"]
    manifest = select_bank_manifest(
        ClimateBankLoad("ok", "", release, candidate_preview=True),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(
            project_elements=(),
            systems_assets=("fish landing sites",),
        ),
    )
    assert "systems_assets" in _selected_row(manifest, "SSD-E-001")["matched_fields"]


def test_schema_v1_roles_map_conservatively() -> None:
    manifest = _select(_profile())
    assert _selected_row(manifest, "SSD-E-001")["balance_role"] == "sensitivity"
    assert _selected_row(manifest, "SSD-E-002")["balance_role"] == "direct-climate-fcv"
    assert (
        _selected_row(manifest, "SSD-P-001")["balance_role"]
        == "climate-to-fcv-pathway"
    )


def test_schema_v1_physical_baseline_maps_to_climate_pressure() -> None:
    bank = load_climate_bank(FIXTURE)
    release = copy.deepcopy(bank.release)
    release["evidence_records"][0]["analytical_role"] = "physical-baseline"
    manifest = select_bank_manifest(
        ClimateBankLoad("ok", "", release),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(),
    )
    assert _selected_row(manifest, "SSD-E-001")["balance_role"] == "climate-pressure"


def test_schema_v1_1_uses_evidence_class() -> None:
    bank = _candidate_bank()
    manifest = select_bank_manifest(
        bank,
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(),
    )
    expected = bank.release["evidence_records"][0]["evidence_class"]
    assert _selected_row(manifest, "SSD-E-001")["balance_role"] == expected


def test_local_scope_is_retained_without_national_generalization() -> None:
    bank = load_climate_bank(FIXTURE)
    packet = materialize_bank_manifest(bank, _select(_profile()))
    selected = {item["evidence_id"]: item for item in packet["evidence_records"]}
    assert selected["SSD-E-001"]["geographies"] == ["Jonglei"]
    assert "South Sudan" not in selected["SSD-E-001"]["geographies"]


def test_selection_is_deterministic_under_input_reordering() -> None:
    bank = load_climate_bank(FIXTURE)
    release = copy.deepcopy(bank.release)
    for key in ("sources", "evidence_records", "pathways"):
        release[key].reverse()
    release["countries"]["SSD"]["evidence_ids"].reverse()
    release["countries"]["SSD"]["pathway_ids"].reverse()
    first = _select(_profile())
    second = select_bank_manifest(
        ClimateBankLoad("ok", "", release),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(
            affected_groups=("seasonal users", "fishers"),
            systems_assets=("Sudd wetlands", "landing sites"),
        ),
    )
    assert first == second


def test_manifest_diagnostics_are_bounded_and_content_safe() -> None:
    sentinel = "CONFIDENTIAL_UPLOAD_PHRASE"
    manifest = _select(_profile(unresolved=(sentinel,)))
    assert sentinel not in json.dumps(manifest, sort_keys=True)
    diagnostics = manifest["diagnostics"]
    assert len(diagnostics["selected"]) <= CLIMATE_BANK_MAX_ITEMS
    assert len(diagnostics["suppressed"]) <= CLIMATE_BANK_MAX_ITEMS
    assert len(diagnostics["missing_classes"]) <= 9
    allowed_fields = {
        "geographies", "sectors", "project_elements", "affected_groups",
        "institutions", "systems_assets", "documented_hazards", "time_horizons",
    }
    for row in diagnostics["selected"]:
        assert set(row) <= {
            "id", "score", "matched_fields", "balance_role", "staleness"
        }
        assert isinstance(row["score"], int)
        assert set(row["matched_fields"]) <= allowed_fields
    for row in diagnostics["suppressed"]:
        assert set(row) == {"id", "reason"}


def test_single_country_warning_codes_are_preserved() -> None:
    bank = load_climate_bank(FIXTURE)
    multi = select_bank_manifest(
        bank,
        country="South Sudan",
        country_scope="multi",
        resolved_country_count=2,
        project_profile=_profile(),
    )
    unknown = select_bank_manifest(
        bank,
        country="Atlantis",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(),
    )
    assert multi["warning_code"] == "bank_scope_unsupported"
    assert unknown["warning_code"] == "bank_country_unavailable"


def test_country_alias_ids_and_character_bounds_are_preserved() -> None:
    bank = load_climate_bank(FIXTURE)
    manifest = select_bank_manifest(
        bank,
        country="Republic of South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(),
    )
    assert manifest["country_iso3"] == "SSD"
    assert all(item.startswith("SSD-E-") for item in manifest["evidence_ids"])
    assert all(item.startswith("SSD-P-") for item in manifest["pathway_ids"])
    assert (
        len(manifest["evidence_ids"]) + len(manifest["pathway_ids"])
        <= CLIMATE_BANK_MAX_ITEMS
    )
    packet = materialize_bank_manifest(bank, manifest)
    assert selector_module._compact_packet_length(packet) <= CLIMATE_BANK_MAX_CHARS


def test_oversized_records_fail_closed(monkeypatch) -> None:
    original_length = selector_module._compact_packet_length

    def oversized(packet):
        if packet.get("evidence_records") or packet.get("pathways"):
            return CLIMATE_BANK_MAX_CHARS + 1
        return original_length(packet)

    monkeypatch.setattr(selector_module, "_compact_packet_length", oversized)
    assert _select(_profile()) == {
        "bank_status": "unavailable",
        "warning_code": "bank_packet_too_large",
    }


def test_unmatched_profile_returns_safe_empty_materializable_manifest() -> None:
    bank = load_climate_bank(FIXTURE)
    manifest = _select(
        _profile(
            geographies=("Nowhere County",),
            sectors=("unmatched sector",),
            project_elements=("unmatched component",),
            affected_groups=("unmatched group",),
            institutions=("unmatched institution",),
            systems_assets=("unmatched asset",),
            documented_hazards=("unmatched hazard",),
            time_horizons=("historical",),
        )
    )

    assert manifest["bank_status"] == "ok"
    assert manifest["evidence_ids"] == []
    assert manifest["pathway_ids"] == []
    assert manifest["diagnostics"]["selected"] == []
    assert {
        row["reason"]
        for row in manifest["diagnostics"]["suppressed"]
    } == {"low_relevance"}
    assert manifest["diagnostics"]["missing_classes"] == [
        "climate-pressure",
        "vulnerability-capacity",
        "institution-response",
        "climate-to-fcv-pathway",
        "reverse-or-bidirectional-pathway",
    ]

    packet = materialize_bank_manifest(bank, manifest)
    assert packet["bank_status"] == "ok"
    assert packet["evidence_records"] == []
    assert packet["pathways"] == []
    grounding = merge_climate_grounding(packet, {})
    assert grounding["state"] == "thematic-only"
    assert grounding["prompt_context"] == ""
    assert grounding["selected_item_count"] == 0


def test_unavailable_bank_warning_is_preserved() -> None:
    result = select_bank_manifest(
        load_climate_bank(FIXTURE.with_name("missing.json")),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(),
    )
    assert result == {"bank_status": "unavailable", "warning_code": "bank_missing"}


def test_country_candidate_volume_accepts_exact_boundary() -> None:
    bank = load_climate_bank(FIXTURE)
    release = copy.deepcopy(bank.release)
    limit = selector_module.CLIMATE_BANK_MAX_CANDIDATES
    release["countries"]["SSD"]["evidence_ids"] = [
        "SSD-E-001",
        *[f"SSD-E-{number:03d}" for number in range(3, limit + 1)],
    ]
    release["countries"]["SSD"]["pathway_ids"] = ["SSD-P-001"]

    manifest = select_bank_manifest(
        ClimateBankLoad("ok", "", release),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(),
    )

    assert manifest["bank_status"] == "ok"
    assert manifest["evidence_ids"] == ["SSD-E-001"]
    assert manifest["pathway_ids"] == ["SSD-P-001"]


def test_country_candidate_volume_overflow_fails_before_scanning(
    monkeypatch,
) -> None:
    bank = load_climate_bank(FIXTURE)
    release = copy.deepcopy(bank.release)
    limit = selector_module.CLIMATE_BANK_MAX_CANDIDATES
    release["countries"]["SSD"]["evidence_ids"] = [
        f"SSD-E-{number:03d}" for number in range(1, limit + 1)
    ]
    release["countries"]["SSD"]["pathway_ids"] = ["SSD-P-001"]

    def unexpected_candidate(*args, **kwargs):
        raise AssertionError("overflow must fail before candidate scanning")

    monkeypatch.setattr(selector_module, "_candidate", unexpected_candidate)
    manifest = select_bank_manifest(
        ClimateBankLoad("ok", "", release),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(),
    )

    assert manifest == {
        "bank_status": "unavailable",
        "warning_code": "bank_packet_too_large",
    }


def test_legacy_project_signals_remain_a_narrow_transition_path() -> None:
    manifest = select_bank_manifest(
        load_climate_bank(FIXTURE),
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        sector="Fisheries",
        project_signals="Jonglei landing sites",
    )
    assert manifest["bank_status"] == "ok"
    assert manifest["evidence_ids"] == ["SSD-E-001"]
    assert manifest["pathway_ids"] == ["SSD-P-001"]
    assert [
        row["id"] for row in manifest["diagnostics"]["selected"]
    ] == ["SSD-E-001", "SSD-P-001"]
    assert manifest["diagnostics"]["suppressed"] == [
        {"id": "SSD-E-002", "reason": "low_relevance"}
    ]
    assert "Jonglei landing sites" not in json.dumps(manifest)


def test_reviewed_candidate_flag_survives_selection_and_compaction() -> None:
    bank = _candidate_bank()
    manifest = select_bank_manifest(
        bank,
        country="South Sudan",
        country_scope="single",
        resolved_country_count=1,
        project_profile=_profile(
            geographies=("Unity",),
            sectors=("transport",),
            project_elements=("feeder roads",),
            affected_groups=("rural households",),
            institutions=("county road authority",),
            systems_assets=("feeder roads", "markets"),
        ),
    )
    assert manifest["candidate_preview"] is True
    packet = materialize_bank_manifest(bank, manifest)
    assert packet["candidate_preview"] is True
    assert selector_module.compact_bank_packet(packet)["candidate_preview"] is True
