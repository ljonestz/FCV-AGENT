"""Deployment contract for the public Climate-FCV country-bank runtime."""

from pathlib import Path

import render_build

from sector_lenses.climate_bank import load_climate_bank


ROOT = Path(__file__).resolve().parents[1]


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


def test_pinned_bank_contains_approved_south_sudan_runtime() -> None:
    bank = load_climate_bank()

    assert bank.status == "ok"
    assert bank.warning_code == ""
    assert bank.release["content_version"] == "2026.07.south-sudan-pilot"
    assert bank.release["countries"]["SSD"]["status"] == "approved"
    assert bank.release["countries"]["SSD"]["reviewer"] == "Lindsey Jones"
    assert len(bank.release["sources"]) == 12
    assert len(bank.release["evidence_records"]) == 19
    assert len(bank.release["pathways"]) == 7
