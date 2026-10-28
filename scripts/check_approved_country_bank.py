"""Check the pinned approved bank and all country/sector prompts without model calls.

Run from the repository root: python -m scripts.check_approved_country_bank
Preview/path overrides are rejected so this exercises normal app startup.
"""
from __future__ import annotations

from datetime import date
import json
import os

from sector_lenses.climate_bank import load_climate_bank, materialize_bank_manifest
from sector_lenses.climate_bank_selector import select_bank_manifest
from sector_lenses.climate_grounding import merge_climate_grounding
from scripts.run_country_bank_test import _final_prompt_failure
from sector_lenses.research import build_climate_bank_search_context


def main() -> int:
    for name in ("CLIMATE_COUNTRY_BANK_PATH", "CLIMATE_COUNTRY_BANK_PREVIEW"):
        if os.environ.get(name):
            raise SystemExit(f"Clear {name} to check the default approved release")
    bank = load_climate_bank()
    assert bank.status == "ok", bank.warning_code
    assert not bank.candidate_preview and not bank.draft_preview
    release = bank.release
    assert release["content_version"] == "2026.10.27.approved-global-country-bank"
    assert release["candidate"] is False
    assert "artifact_kind" not in release and "test_expires_on" not in release
    assert len(release["countries"]) == 146
    assert len(release["evidence_records"]) == 2643
    assert len(release["pathways"]) == 241
    assert set(release["country_profiles"]) == set(release["countries"])
    identifiers = set()
    for iso3, country in release["countries"].items():
        assert country["status"] == "approved"
        assert country["reviewer"] == "Lindsey Jones"
        assert country["reviewed_on"] == "2026-10-27"
        assert date.fromisoformat(country["review_due"]) >= date.today()
        for value in (iso3, country["name"], *country.get("aliases", [])):
            key = (iso3, value.strip().casefold())
            if key not in identifiers:
                assert bank.resolve_country(value)["iso3"] == iso3, key
                identifiers.add(key)
    checked = 0
    for iso3 in sorted(release["countries"]):
        for sector, signals in (
            ("Agriculture", "drought livelihoods displacement land tenure"),
            ("Water", "flood water governance access"),
            ("Urban development", "coastal heat informal settlements institutions"),
        ):
            manifest = select_bank_manifest(
                bank, country=iso3, country_scope="single",
                resolved_country_count=1, sector=sector, project_signals=signals,
            )
            assert manifest.get("bank_status") == "ok", (iso3, sector, manifest)
            packet = materialize_bank_manifest(bank, manifest)
            assert packet.get("bank_status") == "ok", (iso3, sector, packet)
            failure = _final_prompt_failure(packet)
            assert failure is None, (iso3, sector, failure)
            merged = merge_climate_grounding(packet, {})
            assert merged["state"] == "bank-only"
            assert merged["candidate_preview"] is False
            prompt_bank = json.loads(merged["prompt_context"])["bank"]
            assert prompt_bank["evidence_records"], (iso3, sector, "no retained evidence")
            assert any(
                "not independent source verification" in gap.get("text", "").lower()
                for gap in prompt_bank["country_profile"]["known_gaps"]
                if isinstance(gap, dict)
            ), (iso3, sector, "lost verification disclosure")
            context = build_climate_bank_search_context(packet)
            assert context["selected_scope"], (iso3, sector, "no dated search scope")
            assert context["country_profile"]["known_gaps"], (iso3, sector, "no search gaps")
            assert context["country_profile"]["coverage"], (iso3, sector, "no search coverage")
            assert len(json.dumps(context, ensure_ascii=False, sort_keys=True, separators=(",", ":"))) <= 2_500
            checked += 1
    print(json.dumps({
        "content_version": release["content_version"],
        "as_of": date.today().isoformat(),
        "countries": len(release["countries"]),
        "country_identifiers": len(identifiers),
        "final_prompts": checked,
        "supplementary_search_contexts": checked,
        "provider_calls": 0,
        "source_manifest_checksum": release["source_manifest_checksum"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
