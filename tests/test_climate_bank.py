"""Contract tests for loading and materializing reviewed Climate-FCV bank data."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from sector_lenses.climate_bank import (
    load_climate_bank,
    materialize_bank_manifest,
)
from sector_lenses.climate_bank_selector import compact_bank_packet
from sector_lenses.climate_grounding import merge_climate_grounding


FIXTURE = Path(__file__).parent / "fixtures" / "climate_bank" / "runtime_v1.json"


def _fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _write(tmp_path: Path, release: dict) -> Path:
    path = tmp_path / "runtime.json"
    path.write_text(json.dumps(release), encoding="utf-8")
    return path


def _resign(release: dict) -> dict:
    manifest_sources = [
        {key: value for key, value in source.items() if key != "checksum"}
        for source in release["sources"]
    ]
    payload = json.dumps(
        manifest_sources,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    release["source_manifest_checksum"] = hashlib.sha256(payload).hexdigest()
    return release


def _manifest(**overrides) -> dict:
    result = {
        "country_iso3": "SSD",
        "content_version": "test-1",
        "evidence_ids": ["SSD-E-001"],
        "pathway_ids": ["SSD-P-001"],
    }
    result.update(overrides)
    return result


def test_valid_release_loads_and_resolves_aliases() -> None:
    result = load_climate_bank(FIXTURE)
    assert result.status == "ok"
    assert result.release["content_version"] == "test-1"
    assert result.resolve_country("South Sudan")["iso3"] == "SSD"
    assert result.resolve_country("ssd")["iso3"] == "SSD"
    assert result.resolve_country("Republic of South Sudan")["iso3"] == "SSD"


def test_missing_release_is_nonfatal(tmp_path: Path) -> None:
    result = load_climate_bank(tmp_path / "missing.json")
    assert result.status == "unavailable"
    assert result.warning_code == "bank_missing"
    assert result.release == {}


def test_incompatible_release_is_nonfatal(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    path.write_text('{"schema_version":"2.0.0"}', encoding="utf-8")
    result = load_climate_bank(path)
    assert result.status == "unavailable"
    assert result.warning_code == "bank_incompatible"
    assert result.release == {}


def test_source_manifest_checksum_excludes_per_source_checksum(
    tmp_path: Path,
) -> None:
    release = _fixture()
    release["sources"][0]["checksum"] = "a" * 64
    result = load_climate_bank(_write(tmp_path, release))
    assert result.status == "ok"


def test_manifest_materialization_uses_only_canonical_content() -> None:
    result = load_climate_bank(FIXTURE)
    packet = materialize_bank_manifest(
        result,
        _manifest(statement="client supplied text", sources=[{"title": "Fake"}]),
    )
    assert packet["bank_status"] == "ok"
    assert packet["evidence_records"][0]["evidence_id"] == "SSD-E-001"
    assert packet["pathways"][0]["pathway_id"] == "SSD-P-001"
    assert packet["sources"][0]["source_id"] == "SSD-SRC-001"
    assert "client supplied text" not in str(packet)
    assert "Fake" not in str(packet)


def test_materialization_rejects_version_mismatch_without_partial_content() -> None:
    packet = materialize_bank_manifest(
        load_climate_bank(FIXTURE),
        _manifest(content_version="wrong"),
    )
    assert packet == {
        "bank_status": "unavailable",
        "warning_code": "bank_version_mismatch",
    }


def test_materialization_rejects_unknown_and_duplicate_ids() -> None:
    bank = load_climate_bank(FIXTURE)
    unknown = materialize_bank_manifest(
        bank, _manifest(evidence_ids=["SSD-E-999"])
    )
    duplicate = materialize_bank_manifest(
        bank, _manifest(evidence_ids=["SSD-E-001", "SSD-E-001"])
    )
    assert unknown["warning_code"] == "bank_manifest_invalid"
    assert duplicate["warning_code"] == "bank_manifest_invalid"
    assert set(unknown) == {"bank_status", "warning_code"}
    assert set(duplicate) == {"bank_status", "warning_code"}


def test_materialization_rejects_unapproved_or_expired_country(
    tmp_path: Path,
) -> None:
    unapproved_release = _fixture()
    unapproved_release["countries"]["SSD"]["status"] = "reviewed"
    unapproved = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, unapproved_release)), _manifest()
    )
    assert unapproved["warning_code"] == "bank_country_unapproved"

    expired_release = _fixture()
    expired_release["countries"]["SSD"]["review_due"] = "2020-01-01"
    expired = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, expired_release)), _manifest()
    )
    assert expired["warning_code"] == "bank_content_expired"


def test_materialization_rejects_bad_urls_and_cross_references(
    tmp_path: Path,
) -> None:
    bad_url_release = _fixture()
    bad_url_release["sources"][0]["url"] = "javascript:alert(1)"
    bad_url = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, _resign(bad_url_release))),
        _manifest(),
    )
    assert bad_url["warning_code"] == "bank_manifest_invalid"

    bad_xref_release = copy.deepcopy(_fixture())
    bad_xref_release["pathways"][0]["supporting_evidence_ids"] = ["SSD-E-999"]
    bad_xref = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, bad_xref_release)), _manifest()
    )
    assert bad_xref["warning_code"] == "bank_manifest_invalid"


def test_materialization_rejects_link_outside_pathway_support(
    tmp_path: Path,
) -> None:
    release = _fixture()
    release["pathways"][0]["link_evidence"]["consequence"] = ["SSD-E-002"]
    packet = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, release)), _manifest()
    )
    assert packet == {
        "bank_status": "unavailable",
        "warning_code": "bank_manifest_invalid",
    }


def test_materialization_rejects_non_string_source_id_without_raising(
    tmp_path: Path,
) -> None:
    release = _fixture()
    release["evidence_records"][0]["source_refs"][0]["source_id"] = []
    packet = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, release)), _manifest()
    )
    assert packet == {
        "bank_status": "unavailable",
        "warning_code": "bank_manifest_invalid",
    }


def test_materialization_rejects_missing_required_canonical_field(
    tmp_path: Path,
) -> None:
    release = _fixture()
    del release["evidence_records"][0]["compact_statement"]
    packet = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, release)), _manifest()
    )
    assert packet == {
        "bank_status": "unavailable",
        "warning_code": "bank_manifest_invalid",
    }


def test_materialization_rejects_unsafe_repository_path(
    tmp_path: Path,
) -> None:
    release = _fixture()
    release["sources"][0]["repository_file"] = "../source_documents/raw.pdf"
    release["sources"][0]["checksum"] = "a" * 64
    packet = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, _resign(release))), _manifest()
    )
    assert packet == {
        "bank_status": "unavailable",
        "warning_code": "bank_manifest_invalid",
    }


def test_materialization_rejects_malformed_country_code(
    tmp_path: Path,
) -> None:
    release = _fixture()
    release["sources"][0]["country_codes"].append("not-iso")
    packet = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, _resign(release))), _manifest()
    )
    assert packet == {
        "bank_status": "unavailable",
        "warning_code": "bank_manifest_invalid",
    }


def test_materialization_rejects_cross_country_source_prefix(
    tmp_path: Path,
) -> None:
    release = _fixture()
    release["sources"][0]["source_id"] = "KEN-SRC-001"
    release["evidence_records"][0]["source_refs"][0][
        "source_id"
    ] = "KEN-SRC-001"
    packet = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, _resign(release))), _manifest()
    )
    assert packet == {
        "bank_status": "unavailable",
        "warning_code": "bank_manifest_invalid",
    }


def test_pathway_materialization_includes_canonical_support_records() -> None:
    packet = materialize_bank_manifest(
        load_climate_bank(FIXTURE),
        _manifest(evidence_ids=[], pathway_ids=["SSD-P-001"]),
    )
    assert packet["bank_status"] == "ok"
    assert [item["evidence_id"] for item in packet["evidence_records"]] == [
        "SSD-E-001"
    ]


def test_pathway_support_is_materialized_but_not_counted_as_selected_evidence(
) -> None:
    manifest = _manifest(evidence_ids=[], pathway_ids=["SSD-P-001"])
    manifest["diagnostics"] = {
        "selected": [{
            "id": "SSD-P-001",
            "score": 37,
            "matched_fields": ["geographies", "project_elements"],
            "balance_role": "climate-to-fcv-pathway",
        }],
        "suppressed": [],
        "missing_classes": [],
    }
    packet = materialize_bank_manifest(load_climate_bank(FIXTURE), manifest)

    assert [item["evidence_id"] for item in packet["evidence_records"]] == [
        "SSD-E-001"
    ]
    compact = compact_bank_packet(packet)
    assert compact["evidence_capsules"] == []
    assert [item["id"] for item in compact["pathway_capsules"]] == [
        "SSD-P-001"
    ]
    assert merge_climate_grounding(packet, {})["selected_item_count"] == 1


def test_materialization_adds_only_controlled_project_relevance_without_mutation(
) -> None:
    bank = load_climate_bank(FIXTURE)
    canonical_before = copy.deepcopy(bank.release)
    manifest = _manifest(evidence_ids=["SSD-E-001"], pathway_ids=[])
    manifest["diagnostics"] = {
        "selected": [{
            "id": "SSD-E-001",
            "score": 999,
            "matched_fields": [
                "geographies", "systems_assets", "not-controlled",
            ],
            "balance_role": "sensitivity",
            "uploaded_text": "must not cross the boundary",
        }],
        "suppressed": [],
        "missing_classes": [],
    }

    packet = materialize_bank_manifest(bank, manifest)

    assert packet["project_relevance"] == {
        "SSD-E-001": {
            "score": 999,
            "matched_fields": ["geographies", "systems_assets"],
        }
    }


    assert "uploaded_text" not in str(packet["project_relevance"])
    assert bank.release == canonical_before
def test_materialization_rejects_cross_country_evidence_prefix(
    tmp_path: Path,
) -> None:
    release = _fixture()
    release["evidence_records"][0]["evidence_id"] = "KEN-E-001"
    release["countries"]["SSD"]["evidence_ids"][0] = "KEN-E-001"
    release["pathways"][0]["supporting_evidence_ids"][0] = "KEN-E-001"
    for values in release["pathways"][0]["link_evidence"].values():
        values[0] = "KEN-E-001"
    packet = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, release)),
        _manifest(evidence_ids=["KEN-E-001"]),
    )
    assert packet == {
        "bank_status": "unavailable",
        "warning_code": "bank_manifest_invalid",
    }


def test_materialization_rejects_cross_country_pathway_prefix(
    tmp_path: Path,
) -> None:
    release = _fixture()
    release["pathways"][0]["pathway_id"] = "KEN-P-001"
    release["countries"]["SSD"]["pathway_ids"][0] = "KEN-P-001"
    packet = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, release)),
        _manifest(pathway_ids=["KEN-P-001"]),
    )
    assert packet == {
        "bank_status": "unavailable",
        "warning_code": "bank_manifest_invalid",
    }


def test_materialization_rejects_normalized_duplicate_source_urls(
    tmp_path: Path,
) -> None:
    release = _fixture()
    release["sources"][1]["url"] = (
        "https://EXAMPLE.ORG/synthetic-climate-note/"
    )
    packet = materialize_bank_manifest(
        load_climate_bank(_write(tmp_path, _resign(release))),
        _manifest(
            evidence_ids=["SSD-E-001", "SSD-E-002"],
            pathway_ids=[],
        ),
    )
    assert packet == {
        "bank_status": "unavailable",
        "warning_code": "bank_manifest_invalid",
    }


def test_materialized_packets_do_not_alias_loaded_release() -> None:
    bank = load_climate_bank(FIXTURE)
    first = materialize_bank_manifest(bank, _manifest())
    first["evidence_records"][0]["compact_statement"] = "mutated"
    first["sources"][0]["title"] = "mutated"

    second = materialize_bank_manifest(bank, _manifest())

    assert second["evidence_records"][0]["compact_statement"] != "mutated"
    assert second["sources"][0]["title"] != "mutated"
    assert (
        bank.release["evidence_records"][0]["compact_statement"] != "mutated"
    )

CANDIDATE_FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "climate_bank"
    / "runtime_v1_1_candidate.json"
)


def test_reviewed_candidate_preview_requires_explicit_path_and_opt_in(
    monkeypatch,
) -> None:
    monkeypatch.delenv("CLIMATE_COUNTRY_BANK_PATH", raising=False)
    monkeypatch.delenv("CLIMATE_COUNTRY_BANK_PREVIEW", raising=False)

    default_result = load_climate_bank(CANDIDATE_FIXTURE)
    assert default_result.status == "unavailable"
    assert default_result.warning_code == "bank_incompatible"

    monkeypatch.setenv("CLIMATE_COUNTRY_BANK_PATH", str(CANDIDATE_FIXTURE))
    monkeypatch.setenv(
        "CLIMATE_COUNTRY_BANK_PREVIEW", "reviewed-candidate"
    )
    preview = load_climate_bank()
    assert preview.status == "ok"
    assert preview.candidate_preview is True
    assert preview.release["candidate"] is True

    packet = materialize_bank_manifest(
        preview,
        {
            **_manifest(content_version="test-1-preview"),
            "candidate_preview": True,
        },
    )
    assert packet["bank_status"] == "ok"
    assert packet["candidate_preview"] is True
    assert packet["evidence_records"][0]["review_status"] == "reviewed"
