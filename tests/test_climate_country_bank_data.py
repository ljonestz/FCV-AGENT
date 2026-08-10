"""Tests for the bundled per-country climate-FCV grounding bank."""

from copy import deepcopy

import pytest

import climate_country_bank_data as country_bank


LIST_PROFILE_KEYS = {
    "primary_hazards",
    "climate_fragility_pathways",
    "hotspot_regions",
    "adaptation_entry_points",
    "key_uncertainties",
    "sources",
}


def _valid_profile() -> dict:
    return {
        "country": "Example Country",
        "iso3": "EXP",
        "fcs_category": "Conflict",
        "climate_vulnerability": "High and unevenly distributed.",
        "climate_vulnerability_basis": "Qualitative source-note synthesis.",
        "primary_hazards": ["Drought"],
        "climate_fragility_pathways": ["Drought can intensify resource-access pressure."],
        "hotspot_regions": ["Dryland livelihood zones"],
        "displacement_and_resource_dynamics": "Mobile and displaced users may have overlapping claims.",
        "adaptation_entry_points": ["Map resource users before siting investments."],
        "key_uncertainties": ["Subnational access conditions change quickly."],
        "sources": ["defueling_conflict"],
        "generated_with": "Curated qualitative synthesis",
        "bank_version": "1",
    }


def test_bank_loads_with_version_and_two_profiles():
    bank = country_bank.load_country_bank()

    assert bank["bank_version"] == "1"
    assert bank["generated"] == "2026-07-30"
    assert isinstance(bank["profiles"], dict)
    assert set(bank["profiles"]) == {"SSD", "TCD"}


def test_south_sudan_exact_name_lookup_returns_substantive_profile():
    profile = country_bank.get_country_profile("South Sudan")

    assert profile is not None
    assert profile["iso3"] == "SSD"
    assert profile["fcs_category"] == "Conflict"
    assert profile["climate_fragility_pathways"]


@pytest.mark.parametrize(
    ("lookup", "expected_iso3"),
    [
        ("south sudan", "SSD"),
        ("CHAD", "TCD"),
        ("ssd", "SSD"),
        ("tCd", "TCD"),
    ],
)
def test_lookup_is_case_insensitive_for_seed_names_and_iso3(lookup, expected_iso3):
    assert country_bank.get_country_profile(lookup)["iso3"] == expected_iso3


def test_lookup_folds_known_aliases(monkeypatch):
    monkeypatch.setattr(
        country_bank,
        "FCS_COUNTRY_ALIASES",
        {"Republic of South Sudan": "South Sudan"},
    )

    assert country_bank.get_country_profile("republic of south sudan")["iso3"] == "SSD"


def test_unknown_country_returns_none():
    assert country_bank.get_country_profile("Atlantis") is None


def test_missing_required_list_key_is_rejected():
    profile = _valid_profile()
    del profile["primary_hazards"]

    with pytest.raises(ValueError, match="primary_hazards"):
        country_bank.validate_profile(profile)


@pytest.mark.parametrize("missing_key", ["generated_with", "bank_version"])
def test_missing_required_metadata_is_rejected(missing_key):
    profile = _valid_profile()
    del profile[missing_key]

    with pytest.raises(ValueError, match=missing_key):
        country_bank.validate_profile(profile)


def test_invalid_source_note_stem_is_rejected():
    profile = _valid_profile()
    profile["sources"] = ["invented_source_note"]

    with pytest.raises(ValueError, match="invented_source_note"):
        country_bank.validate_profile(profile)


@pytest.mark.parametrize("bad_item", ["", None])
def test_list_items_must_be_non_empty_strings(bad_item):
    profile = _valid_profile()
    profile["primary_hazards"] = [bad_item]

    with pytest.raises(ValueError, match="primary_hazards"):
        country_bank.validate_profile(profile)


def test_empty_profile_lists_remain_allowed_by_schema():
    profile = _valid_profile()
    for key in LIST_PROFILE_KEYS:
        profile[key] = []

    country_bank.validate_profile(profile)


@pytest.mark.parametrize("iso3", ["abc", chr(197) + "BC"])
def test_iso3_must_be_uppercase_ascii(iso3):
    profile = _valid_profile()
    profile["iso3"] = iso3

    with pytest.raises(ValueError, match="iso3"):
        country_bank.validate_profile(profile)


def test_public_validator_returns_status_and_errors():
    ok, errors = country_bank.validate_country_profile(_valid_profile())
    assert ok is True
    assert errors == []

    bad = _valid_profile()
    del bad["primary_hazards"]
    ok, errors = country_bank.validate_country_profile(bad)
    assert ok is False
    assert any("primary_hazards" in error for error in errors)


def test_seed_profiles_disclose_general_knowledge_provenance():
    bank = country_bank.load_country_bank()

    for iso3 in ("SSD", "TCD"):
        profile = bank["profiles"][iso3]
        assert "general-knowledge" in profile["sources"]
        assert "general knowledge" in profile["generated_with"].casefold()


def test_every_seed_profile_has_complete_valid_schema():
    bank = country_bank.load_country_bank()

    for profile in bank["profiles"].values():
        assert set(profile) == country_bank.REQUIRED_PROFILE_KEYS
        country_bank.validate_profile(deepcopy(profile))
        for key in LIST_PROFILE_KEYS:
            assert isinstance(profile[key], list)
        for key in country_bank.REQUIRED_PROFILE_KEYS - LIST_PROFILE_KEYS:
            assert isinstance(profile[key], str)
            assert profile[key].strip()


def test_required_profile_keys_cannot_be_mutated():
    assert isinstance(country_bank.REQUIRED_PROFILE_KEYS, frozenset)
