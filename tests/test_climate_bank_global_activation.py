"""Default-startup acceptance for the approved global Climate-FCV bank."""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path

import sector_lenses.climate_bank as climate_bank_module
import sector_lenses.climate_bank_selector as climate_bank_selector_module
from sector_lenses.climate_bank import load_climate_bank, materialize_bank_manifest
from sector_lenses.climate_bank_selector import select_bank_manifest
from sector_lenses.climate_grounding import merge_climate_grounding


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE = (
    ROOT / "data" / "climate-fcv-country-bank" / "releases" / "current" / "runtime.json"
)
ARCHIVED_24_RELEASE = (
    ROOT
    / "data"
    / "climate-fcv-country-bank"
    / "releases"
    / "archive"
    / "2026.10.26.approved-country-bank"
    / "runtime.json"
)
APPROVED_VERSION = "2026.10.27.approved-global-country-bank"
ARCHIVED_24_LF_SHA256 = (
    "12f0a7b5c8267ec3a8ed8033f3e4716af69024a9290e023e5264a94ed35ebda8"
)
APPROVED_PROFILE_DISCLOSURE = (
    "Automated machine-screening is not independent source verification. "
    "Routine/default app-use approval does not certify claims or sources."
)
APPROVED_REVIEW_LIMIT = (
    "Routine/default app-use approval granted by Lindsey Jones on 2026-10-27; "
    "independent source verification remains incomplete."
)
NORMAL_STARTUP_ENV = (
    "CLIMATE_COUNTRY_BANK_PATH",
    "CLIMATE_COUNTRY_BANK_PREVIEW",
    "FCV_APP_ENV",
    "CLIMATE_RESEARCH_MODE",
)
RELEASE_DATE = date(2026, 10, 27)


class _FrozenDate(date):
    @classmethod
    def today(cls):
        return cls(RELEASE_DATE.year, RELEASE_DATE.month, RELEASE_DATE.day)


class _FrozenDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(RELEASE_DATE.year, RELEASE_DATE.month, RELEASE_DATE.day, tzinfo=tz)


def _default_startup_bank(monkeypatch):
    """Load the default release with preview flags cleared and dates frozen."""

    for name in NORMAL_STARTUP_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(climate_bank_module, "date", _FrozenDate)
    monkeypatch.setattr(climate_bank_selector_module, "datetime", _FrozenDateTime)
    return load_climate_bank()


def _final_prompt_bank(bank, *, country: str, sector: str, signals: str) -> dict:
    manifest = select_bank_manifest(
        bank,
        country=country,
        country_scope="single",
        resolved_country_count=1,
        sector=sector,
        project_signals=signals,
    )
    assert manifest.get("bank_status") == "ok"
    assert manifest["content_version"] == APPROVED_VERSION
    assert "candidate_preview" not in manifest

    packet = materialize_bank_manifest(bank, manifest)
    assert packet.get("bank_status") == "ok"
    assert "candidate_preview" not in packet

    merged = merge_climate_grounding(packet, {})
    assert merged["state"] == "bank-only"
    assert merged["candidate_preview"] is False
    assert len(merged["prompt_context"]) <= 6_000
    prompt_bank = json.loads(merged["prompt_context"])["bank"]
    assert prompt_bank["candidate_preview"] is False
    return prompt_bank


def test_normal_startup_uses_approved_global146_release(monkeypatch):
    bank = _default_startup_bank(monkeypatch)

    assert bank.status == "ok"
    assert bank.warning_code == ""
    assert bank.candidate_preview is False
    assert bank.draft_preview is False
    release = bank.release
    assert release["content_version"] == APPROVED_VERSION
    assert release["schema_version"] == "1.1.0"
    assert release.get("candidate") is False
    assert "artifact_kind" not in release
    assert "test_expires_on" not in release
    assert len(release["countries"]) == 146
    assert len(release["evidence_records"]) == 2_643
    assert len(release["pathways"]) == 241

    for country in release["countries"].values():
        assert country["status"] == "approved"
        assert country["reviewer"]
        assert country["reviewed_on"]
        assert country["review_due"]
    for record in release["evidence_records"] + release["pathways"]:
        assert record["review_status"] == "approved"
        assert record["review_date"]

    assert DEFAULT_RELEASE.is_file()


def test_global_profiles_keep_coverage_and_independent_verification_limits(
    monkeypatch,
):
    bank = _default_startup_bank(monkeypatch)
    profiles = bank.release.get("country_profiles")

    assert isinstance(profiles, dict)
    assert set(profiles) == set(bank.release["countries"])
    assert len(profiles) == 146
    for profile in profiles.values():
        assert isinstance(profile.get("coverage"), list) and profile["coverage"]
        assert isinstance(profile.get("known_gaps"), list) and profile["known_gaps"]
        assert any(
            APPROVED_PROFILE_DISCLOSURE.lower() in str(gap.get("text", "")).lower()
            for gap in profile["known_gaps"]
            if isinstance(gap, dict)
        )
        assert any(
            APPROVED_REVIEW_LIMIT.lower() in str(gap.get("text", "")).lower()
            for gap in profile["known_gaps"]
            if isinstance(gap, dict)
        )


def test_tuvalu_urban_and_chad_water_final_prompts_keep_qualifiers_and_profiles(
    monkeypatch,
):
    bank = _default_startup_bank(monkeypatch)
    tuvalu = _final_prompt_bank(
        bank,
        country="Tuvalu",
        sector="Urban",
        signals=(
            "urban settlements Funafuti Nui Nukufetau Vaitupu coastal inundation "
            "2060 50-year flood SSP2-4.5 sea-level rise"
        ),
    )
    tuvalu_evidence = {item["evidence_id"]: item for item in tuvalu["evidence_records"]}
    projected_flood = tuvalu_evidence["TUV-E-103"]
    assert projected_flood["scenario"] == "SSP2-4.5 and SSP5-8.5"
    assert "medium-term" in projected_flood["time_horizons"]
    assert "2060" in projected_flood["compact_statement"]
    assert "not observed change" in projected_flood["uncertainty"].lower()
    water_risk = tuvalu_evidence["TUV-E-102"]
    assert "70%" in water_risk["compact_statement"]
    assert "national" in water_risk["uncertainty"].lower()
    assert tuvalu["country_profile"]["coverage"]
    assert APPROVED_PROFILE_DISCLOSURE.lower() in (
        tuvalu["country_profile"]["known_gaps"][0]["text"].lower()
    )
    # This additional approval attribution is administrative; the substantive
    # source-verification disclosure above must survive even when the compact
    # assessment profile trims a whole known-gap row.
    assert any(
        APPROVED_REVIEW_LIMIT.lower() in item["text"].lower()
        for item in tuvalu["country_profile"]["known_gaps"]
    ) or "known_gaps" in tuvalu["country_profile"].get("truncated_fields", [])

    chad = _final_prompt_bank(
        bank,
        country="Chad",
        sector="Water",
        signals="Lake Chad floods water access refugees displacement market floodplain Chad",
    )
    chad_evidence = {item["evidence_id"]: item for item in chad["evidence_records"]}
    displacement = chad_evidence["TCD-E-109"]
    assert "floodplains" in displacement["compact_statement"].lower()
    assert "report-level vulnerability mechanism" in displacement["uncertainty"].lower()
    assert "not security threats" in displacement["uncertainty"].lower()
    pathway = next(item for item in chad["pathways"] if item["pathway_id"] == "TCD-P-101")
    canonical_pathway = next(
        item
        for item in bank.release["pathways"]
        if item["pathway_id"] == "TCD-P-101"
    )
    assert pathway["uncertainty"] == canonical_pathway["uncertainty"]
    assert "no named-site causal estimate" in pathway["uncertainty"].lower()
    assert "not a threat attributed to refugees" in pathway["uncertainty"].lower()
    assert chad["country_profile"]["coverage"]
    assert APPROVED_PROFILE_DISCLOSURE.lower() in (
        chad["country_profile"]["known_gaps"][0]["text"].lower()
    )
    assert any(
        APPROVED_REVIEW_LIMIT.lower() in item["text"].lower()
        for item in chad["country_profile"]["known_gaps"]
    ) or "known_gaps" in chad["country_profile"].get("truncated_fields", [])


def test_previous_approved24_runtime_is_preserved_at_its_archived_identity():
    assert ARCHIVED_24_RELEASE.is_file()
    raw = ARCHIVED_24_RELEASE.read_bytes()
    normalized_lf = raw.replace(b"\r\n", b"\n")
    assert hashlib.sha256(normalized_lf).hexdigest() == ARCHIVED_24_LF_SHA256
    archived = json.loads(normalized_lf.decode("utf-8"))
    assert archived["content_version"] == "2026.10.26.approved-country-bank"
    assert archived["candidate"] is False
    assert len(archived["countries"]) == 24
    assert len(archived["evidence_records"]) == 531
    assert len(archived["pathways"]) == 168
