"""Deployment contract for the public Climate-FCV country-bank runtime."""

from datetime import date
from pathlib import Path

import pytest
import render_build
import sector_lenses.climate_bank as bank_module

from sector_lenses.climate_bank import load_climate_bank, materialize_bank_manifest
from sector_lenses.climate_bank_selector import select_bank_manifest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def approved_bank(monkeypatch):
    class ApprovalDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 10, 27)

    # Version-bound acceptance; separate expiry tests exercise real date boundaries.
    monkeypatch.setattr(bank_module, "date", ApprovalDate)
    monkeypatch.delenv("CLIMATE_COUNTRY_BANK_PATH", raising=False)
    monkeypatch.delenv("CLIMATE_COUNTRY_BANK_PREVIEW", raising=False)
    return load_climate_bank()


def test_public_submodule_and_override_are_documented() -> None:
    modules = (ROOT / ".gitmodules").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "data/climate-fcv-country-bank" in modules
    assert (
        "https://github.com/ljonestz/climate-fcv-country-bank.git"
        in modules
    )
    assert "CLIMATE_COUNTRY_BANK_PATH" in readme
    assert "python render_build.py" in readme


def test_no_restricted_opcs_dependency_in_bank_modules() -> None:
    source = "\n".join(
        (ROOT / "sector_lenses" / name).read_text(encoding="utf-8")
        for name in (
            "climate_bank.py",
            "climate_bank_selector.py",
            "climate_grounding.py",
        )
    )

    assert "ppf_indexer" not in source
    assert "from background_docs import" not in source


def test_render_build_initializes_pinned_submodules_before_dependencies() -> None:
    commands = render_build.build_commands("python")

    assert commands == [
        ["git", "submodule", "sync", "--recursive"],
        ["git", "submodule", "update", "--init", "--recursive"],
        ["python", "-m", "pip", "install", "-r", "requirements.txt"],
    ]


def test_pinned_bank_contains_approved_country_runtime(approved_bank) -> None:
    bank = approved_bank

    assert bank.status == "ok"
    assert bank.warning_code == ""
    assert bank.release["content_version"] == "2026.10.27.approved-global-country-bank"
    assert bank.release["schema_version"] == "1.1.0"
    assert bank.release["candidate"] is False
    country_codes = set(bank.release["countries"])
    assert len(country_codes) == 146
    original_approved_countries = set(
        "AFG BFA CAF CMR COD ETH HTI IRN IRQ LBN LBY MLI MMR MOZ NER NGA "
        "PNG PSE SDN SOM SSD SYR UKR YEM".split()
    )
    assert original_approved_countries <= country_codes
    assert bank.release["countries"]["SSD"]["status"] == "approved"
    assert bank.release["countries"]["SSD"]["reviewer"] == "Lindsey Jones"
    assert len(bank.release["evidence_records"]) == 2_643
    assert len(bank.release["pathways"]) == 241
    assert len(bank.release["sources"]) == 1_045


@pytest.mark.parametrize("iso3", "AFG BFA CAF CMR COD ETH HTI IRN IRQ LBN LBY MLI MMR MOZ NER NGA PNG PSE SDN SOM SSD SYR UKR YEM".split())
def test_approved_country_selects_without_preview_token(iso3, approved_bank) -> None:
    bank = approved_bank
    manifest = select_bank_manifest(
        bank, country=iso3, country_scope="single", resolved_country_count=1,
        sector="Agriculture", project_signals="water drought flood livelihoods displacement",
    )
    assert manifest["bank_status"] == "ok", manifest
    assert manifest["country_iso3"] == iso3
    assert manifest["evidence_ids"], manifest
    packet = materialize_bank_manifest(bank, manifest)
    assert packet["bank_status"] == "ok", packet
