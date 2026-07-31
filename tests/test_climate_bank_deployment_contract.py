"""Deployment contract for the public Climate-FCV country-bank runtime."""

from pathlib import Path


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
