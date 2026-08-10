"""Bundled per-country climate-FCV grounding bank.

The bank is runtime read-only. Its planned generator is
``scripts/build_climate_country_bank.py``.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from background_docs import FCS_COUNTRY_ALIASES


REQUIRED_PROFILE_KEYS = frozenset({
    "country",
    "iso3",
    "fcs_category",
    "climate_vulnerability",
    "climate_vulnerability_basis",
    "primary_hazards",
    "climate_fragility_pathways",
    "hotspot_regions",
    "displacement_and_resource_dynamics",
    "adaptation_entry_points",
    "key_uncertainties",
    "sources",
    "generated_with",
    "bank_version",
})

_LIST_PROFILE_KEYS = frozenset({
    "primary_hazards",
    "climate_fragility_pathways",
    "hotspot_regions",
    "adaptation_entry_points",
    "key_uncertainties",
    "sources",
})
_FCS_CATEGORIES = {
    "Conflict",
    "Institutional and Social Fragility",
    "High-Intensity Conflict",
    "not-FCS",
}
_BANK_PATH = Path(__file__).parent / "climate_country_bank.json"
_SOURCE_NOTES_PATH = (
    Path(__file__).parent
    / "sector_lenses"
    / "modules"
    / "climate"
    / "source_notes"
)


def _available_sources() -> set[str]:
    """Return source-note stems accepted by the profile schema."""

    return {path.stem for path in _SOURCE_NOTES_PATH.glob("*.md")} | {
        "general-knowledge"
    }


def validate_profile(profile: dict[str, Any]) -> None:
    """Raise ``ValueError`` when a country profile violates the schema."""

    if not isinstance(profile, dict):
        raise ValueError("profile must be an object")

    missing = REQUIRED_PROFILE_KEYS - set(profile)
    if missing:
        raise ValueError(f"profile missing required key(s): {', '.join(sorted(missing))}")
    extra = set(profile) - REQUIRED_PROFILE_KEYS
    if extra:
        raise ValueError(f"profile has unsupported key(s): {', '.join(sorted(extra))}")

    for key in _LIST_PROFILE_KEYS:
        if not isinstance(profile[key], list):
            raise ValueError(f"{key} must be a list")
        if any(
            not isinstance(item, str) or not item.strip()
            for item in profile[key]
        ):
            raise ValueError(f"{key} entries must be non-empty strings")

    for key in REQUIRED_PROFILE_KEYS - _LIST_PROFILE_KEYS:
        value = profile[key]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")

    if len(profile["iso3"]) != 3 or any(
        character < "A" or character > "Z"
        for character in profile["iso3"]
    ):
        raise ValueError("iso3 must be three uppercase ASCII letters")
    if profile["fcs_category"] not in _FCS_CATEGORIES:
        raise ValueError(
            "fcs_category must be one of: " + ", ".join(sorted(_FCS_CATEGORIES))
        )

    available_sources = _available_sources()
    for source in profile["sources"]:
        if not isinstance(source, str) or source not in available_sources:
            raise ValueError(f"invalid profile source: {source!r}")


def validate_country_profile(
    profile: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Return schema validity and human-readable errors for generator callers."""

    try:
        validate_profile(profile)
    except ValueError as exc:
        return False, [str(exc)]
    return True, []


@lru_cache(maxsize=1)
def load_country_bank() -> dict[str, Any]:
    """Load and validate the bundled country bank once per process."""

    with _BANK_PATH.open(encoding="utf-8") as handle:
        bank = json.load(handle)

    if not isinstance(bank, dict):
        raise ValueError("country bank must be an object")
    for key in ("bank_version", "generated"):
        if not isinstance(bank.get(key), str) or not bank[key].strip():
            raise ValueError(f"country bank {key} must be a non-empty string")
    profiles = bank.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError("country bank profiles must be an object")

    for iso3, profile in profiles.items():
        validate_profile(profile)
        if not isinstance(iso3, str) or iso3.casefold() != profile["iso3"].casefold():
            raise ValueError(f"profile key {iso3!r} does not match profile iso3")
        if profile["bank_version"] != bank["bank_version"]:
            raise ValueError(f"profile {iso3} bank_version does not match bank")

    return bank


def _normalize_country(value: str) -> str:
    return value.strip().casefold()


def get_country_profile(country_name: str) -> dict[str, Any] | None:
    """Return a profile by case-insensitive country name, ISO3, or known alias."""

    if not isinstance(country_name, str) or not country_name.strip():
        return None

    profiles = load_country_bank()["profiles"]
    lookup = _normalize_country(country_name)
    for iso3, profile in profiles.items():
        if lookup in {
            _normalize_country(iso3),
            _normalize_country(profile["iso3"]),
            _normalize_country(profile["country"]),
        }:
            return profile

    canonical_target = next(
        (
            target
            for alias, target in FCS_COUNTRY_ALIASES.items()
            if lookup in {_normalize_country(alias), _normalize_country(target)}
        ),
        None,
    )
    if canonical_target is None:
        return None

    normalized_target = _normalize_country(canonical_target)
    return next(
        (
            profile
            for profile in profiles.values()
            if _normalize_country(profile["country"]) == normalized_target
        ),
        None,
    )
