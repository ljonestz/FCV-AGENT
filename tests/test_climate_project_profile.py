"""Golden and safety contracts for deterministic Climate project profiles."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import inspect
import json
from pathlib import Path

import pytest

import sector_lenses.climate_project_profile as climate_profile
from sector_lenses.climate_project_profile import (
    MAX_SIGNAL_METADATA,
    MAX_UNRESOLVED,
    MAX_VALUES_PER_FIELD,
    ProjectClimateProfile,
    SignalMatch,
    build_project_climate_profile,
)


FIXTURES = Path(__file__).parent / "fixtures"
PROJECT_FIXTURES = FIXTURES / "climate_projects"
BANK_FIXTURE = FIXTURES / "climate_bank" / "runtime_v1_1_candidate.json"
ARCHETYPES = (
    "agriculture_livestock",
    "fisheries_forestry_nrm",
    "roads_infrastructure",
    "health_wash",
    "social_protection_resilience",
)
TUPLE_FIELDS = (
    "geographies",
    "sectors",
    "project_elements",
    "affected_groups",
    "institutions",
    "systems_assets",
    "documented_hazards",
    "time_horizons",
    "signal_metadata",
    "unresolved",
)
SYNTHETIC_PROJECT_ELEMENT_ALIASES = {
    "all-weather road rehabilitation": [],
    "bridge upgrades": [],
    "cash transfers": [],
    "cold-chain facilities": [],
    "community forest management plans": [],
    "community resilience grants": [],
    "irrigation schemes": ["irrigation rehabilitation"],
    "livestock vaccination": ["animal vaccination campaigns"],
    "rural water points": [],
    "solar-powered health clinics": [],
}
SYNTHETIC_TIME_HORIZON_ALIASES = {
    "current": [],
    "long-term": ["long term"],
    "medium-term": ["medium term"],
    "near-term": ["near term"],
}


def _selection_aliases() -> dict:
    release = json.loads(BANK_FIXTURE.read_text(encoding="utf-8"))
    return release["countries"]["SSD"]["selection_aliases"]


def _build(
    document_text: str,
    selection_aliases: dict | None = None,
    **overrides,
) -> ProjectClimateProfile:
    arguments = {
        "document_text": document_text,
        "country": "South Sudan",
        "instrument": "IPF",
        "document_stage": "PAD",
        "selection_aliases": selection_aliases or _selection_aliases(),
    }
    arguments.update(overrides)
    return build_project_climate_profile(**arguments)


@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_synthetic_archetype_matches_golden_profile(archetype: str) -> None:
    text = (PROJECT_FIXTURES / f"{archetype}.txt").read_text(
        encoding="utf-8"
    )
    expected = json.loads(
        (PROJECT_FIXTURES / f"{archetype}.json").read_text(encoding="utf-8")
    )

    profile = build_project_climate_profile(
        document_text=text,
        country=expected["country"],
        instrument=expected["instrument"],
        document_stage=expected["document_stage"],
        selection_aliases=_selection_aliases(),
        project_element_aliases=SYNTHETIC_PROJECT_ELEMENT_ALIASES,
        time_horizon_aliases=SYNTHETIC_TIME_HORIZON_ALIASES,
    )

    assert profile.to_public_dict() == expected


def test_caller_catalogs_augment_inputs_without_synthetic_defaults() -> None:
    aliases = _selection_aliases()
    aliases["project_elements"] = {"solar kiosks": []}

    profile = build_project_climate_profile(
        document_text=(
            "Solar kiosks and modular cooling hubs are explicit elements. "
            "The current implementation arrangements remain unchanged."
        ),
        country="South Sudan",
        instrument="IPF",
        document_stage="PAD",
        selection_aliases=aliases,
        project_element_aliases={
            "cooling hubs": ["modular cooling hubs"],
        },
    )

    assert profile.project_elements == ("cooling hubs", "solar kiosks")
    assert profile.time_horizons == ()


def test_word_boundaries_prevent_substring_false_positive() -> None:
    aliases = _selection_aliases()
    aliases["hazards"] = {"heat": ["heat"]}

    profile = _build(
        "The project will restore heather gardens near a theatre.",
        aliases,
    )

    assert profile.documented_hazards == ()


def test_document_bound_does_not_create_partial_token_boundary() -> None:
    aliases = {
        category: {}
        for category in (
            "geographies",
            "sectors",
            "affected_groups",
            "institutions",
            "systems_assets",
            "hazards",
        )
    }
    aliases["hazards"] = {"heat": []}
    prefix = ("x" * (climate_profile.MAX_DOCUMENT_CHARS - 5)) + " "

    profile = _build(prefix + "heater", aliases)

    assert profile.documented_hazards == ()


def test_document_bound_does_not_split_punctuation_token() -> None:
    aliases = {
        category: {}
        for category in (
            "geographies",
            "sectors",
            "affected_groups",
            "institutions",
            "systems_assets",
            "hazards",
        )
    }
    aliases["sectors"] = {"C++": []}
    prefix = ("x" * (climate_profile.MAX_DOCUMENT_CHARS - 4)) + " "

    profile = _build(prefix + "C++17", aliases)

    assert profile.sectors == ()


def test_acronyms_are_case_insensitive_and_boundary_aware() -> None:
    aliases = _selection_aliases()

    embedded = _build("SWASHbuckling and PNRM2 are unrelated labels.", aliases)
    explicit = _build("The project explicitly covers wash and nrm.", aliases)

    assert "WASH" not in embedded.sectors
    assert "natural-resource management" not in embedded.sectors
    assert explicit.sectors == ("natural-resource management", "WASH")


def test_aliases_are_escaped_before_compilation() -> None:
    aliases = _selection_aliases()
    aliases["systems_assets"] = {"C++ hub": []}

    profile = _build("The C++ hub is an explicit project asset.", aliases)

    assert profile.systems_assets == ("C++ hub",)


def test_longest_most_specific_overlapping_alias_wins() -> None:
    aliases = _selection_aliases()
    aliases["sectors"] = {
        "rural transport": ["feeder roads"],
        "transport": ["roads"],
    }

    profile = _build("The project rehabilitates feeder roads.", aliases)

    assert profile.sectors == ("rural transport",)


def test_longer_overlapping_alias_wins_when_it_starts_later() -> None:
    aliases = _selection_aliases()
    aliases["sectors"] = {
        "generic transport": ["river road"],
        "specific corridor": ["road corridor"],
    }

    profile = _build("The river road corridor will be rehabilitated.", aliases)

    assert profile.sectors == ("specific corridor",)


def test_overlap_specificity_ignores_occurrence_whitespace_width() -> None:
    aliases = _selection_aliases()
    aliases["sectors"] = {
        "generic transport": ["river road"],
        "specific corridor": ["road corridor"],
    }

    compact = _build("The river road corridor will be rehabilitated.", aliases)
    expanded = _build(
        "The river     road corridor will be rehabilitated.",
        aliases,
    )

    assert compact.sectors == ("specific corridor",)
    assert expanded.sectors == compact.sectors


def test_matching_streams_many_occurrences_with_fixed_occupancy() -> None:
    aliases = _selection_aliases()
    aliases["sectors"] = {
        "rural transport": ["feeder roads"],
        "transport": ["roads"],
    }
    text = ("feeder roads " * 600) + "roads"

    profile = _build(text, aliases)
    matcher_source = inspect.getsource(climate_profile._explicit_matches)

    assert profile.sectors == ("rural transport", "transport")
    assert "bytearray" in matcher_source
    assert "accepted_spans" not in matcher_source
    assert "matches.append" not in matcher_source


def test_profile_does_not_infer_unstated_project_facts() -> None:
    aliases = {
        category: {}
        for category in (
            "geographies",
            "sectors",
            "affected_groups",
            "institutions",
            "systems_assets",
            "hazards",
        )
    }

    profile = _build(
        "This operation may improve general welfare over time.",
        aliases,
    )

    assert profile.geographies == ()
    assert profile.sectors == ()
    assert profile.project_elements == ()
    assert profile.affected_groups == ()
    assert profile.institutions == ()
    assert profile.systems_assets == ()
    assert profile.documented_hazards == ()
    assert profile.time_horizons == ()


def test_bank_candidates_remain_unresolved_and_do_not_become_facts() -> None:
    aliases = _selection_aliases()
    aliases["hazards"]["flood"] = ["flooding"]
    aliases["geographies"]["Candidate County"] = ["candidate area"]

    profile = _build(
        "The document contains no location or hazard.",
        aliases,
        bank_candidate_signals={
            "geographies": ["Candidate County"],
            "hazards": ["flood"],
        },
    )

    assert profile.geographies == ()
    assert profile.documented_hazards == ()
    assert profile.unresolved == (
        "documented_hazards:flood",
        "geographies:Candidate County",
    )
    assert set(profile.signal_metadata) == {
        SignalMatch(
            field="documented_hazards",
            canonical_value="flood",
            source="bank-candidate",
            confidence="candidate",
        ),
        SignalMatch(
            field="geographies",
            canonical_value="Candidate County",
            source="bank-candidate",
            confidence="candidate",
        ),
    }


def test_explicit_match_suppresses_duplicate_bank_candidate() -> None:
    aliases = _selection_aliases()
    aliases["hazards"] = {"flood": ["flooding"]}

    profile = _build(
        "Flood is explicitly documented.",
        aliases,
        bank_candidate_signals={"hazards": ["flood"]},
    )

    assert profile.documented_hazards == ("flood",)
    assert profile.unresolved == ()
    assert profile.signal_metadata == (
        SignalMatch(
            field="documented_hazards",
            canonical_value="flood",
            source="document",
            confidence="high",
        ),
    )


def test_candidate_reconciliation_uses_matches_beyond_public_cap() -> None:
    aliases = {
        category: {}
        for category in (
            "geographies",
            "sectors",
            "affected_groups",
            "institutions",
            "systems_assets",
            "hazards",
        )
    }
    aliases["hazards"] = {
        f"hazard {index:02d}": [f"hazard signal {index:02d}"]
        for index in range(MAX_VALUES_PER_FIELD + 1)
    }
    text = " ".join(
        f"hazard signal {index:02d}"
        for index in range(MAX_VALUES_PER_FIELD + 1)
    )
    omitted_canonical = f"hazard {MAX_VALUES_PER_FIELD:02d}"

    profile = _build(
        text,
        aliases,
        bank_candidate_signals={"hazards": [omitted_canonical]},
    )

    assert len(profile.documented_hazards) == MAX_VALUES_PER_FIELD
    assert omitted_canonical not in profile.documented_hazards
    assert profile.unresolved == ()
    assert all(
        not (
            match.canonical_value == omitted_canonical
            and match.source == "bank-candidate"
        )
        for match in profile.signal_metadata
    )


def test_signal_metadata_orders_canonical_values_across_sources() -> None:
    aliases = _selection_aliases()
    aliases["sectors"] = {
        "alpha": [],
        "zulu": [],
    }

    profile = _build(
        "The document explicitly identifies zulu.",
        aliases,
        bank_candidate_signals={"sectors": ["alpha"]},
    )

    assert profile.sectors == ("zulu",)
    assert profile.unresolved == ("sectors:alpha",)
    assert profile.signal_metadata == (
        SignalMatch(
            field="sectors",
            canonical_value="alpha",
            source="bank-candidate",
            confidence="candidate",
        ),
        SignalMatch(
            field="sectors",
            canonical_value="zulu",
            source="document",
            confidence="high",
        ),
    )


def test_duplicate_aliases_collapse_deterministically() -> None:
    aliases = _selection_aliases()
    aliases["sectors"] = {
        "water services": ["WATER", "water", "WATER"],
    }

    profile = _build("Water, water, WATER.", aliases)

    assert profile.sectors == ("water services",)
    assert [
        match
        for match in profile.signal_metadata
        if match.field == "sectors"
    ] == [
        SignalMatch(
            field="sectors",
            canonical_value="water services",
            source="document",
            confidence="high",
        )
    ]


def test_ambiguous_alias_and_canonical_ownership_is_suppressed() -> None:
    shared_aliases = _selection_aliases()
    shared_aliases["sectors"] = {
        "alpha sector": ["shared corridor"],
        "beta sector": ["shared corridor"],
    }
    shared = _build("Shared corridor is named.", shared_aliases)

    colliding_aliases = _selection_aliases()
    colliding_aliases["sectors"] = {
        "River Sector": ["river programme"],
        "river sector": ["river operation"],
    }
    colliding = _build(
        "River Sector and river programme are named.",
        colliding_aliases,
        bank_candidate_signals={
            "sectors": ["River Sector", "river sector"],
        },
    )

    assert (
        shared.sectors,
        colliding.sectors,
        colliding.signal_metadata,
        colliding.unresolved,
    ) == ((), (), (), ())


def test_signal_metadata_contains_only_controlled_values() -> None:
    marker = "PRIVATE-SURROUNDING-SOURCE-TEXT"
    profile = _build(
        f"{marker} Northern Arc {marker} agriculture {marker}."
    )
    serialized = json.dumps(profile.to_public_dict()["signal_metadata"])

    assert marker not in serialized
    assert {item.source for item in profile.signal_metadata} <= {
        "document",
        "metadata",
        "bank-candidate",
    }
    assert {item.confidence for item in profile.signal_metadata} <= {
        "high",
        "candidate",
    }


def test_profile_categories_and_metadata_are_bounded() -> None:
    categories = (
        "geographies",
        "sectors",
        "affected_groups",
        "institutions",
        "systems_assets",
        "hazards",
    )
    aliases = {
        category: {
            f"{category}_canonical_{index:02d}": [
                f"{category}_alias_{index:02d}"
            ]
            for index in range(MAX_VALUES_PER_FIELD + 8)
        }
        for category in categories
    }
    text = " ".join(
        alias
        for category in aliases.values()
        for values in category.values()
        for alias in values
    )
    candidates = {
        category: list(values)
        for category, values in (
            (category, alias_map.keys())
            for category, alias_map in aliases.items()
        )
    }

    profile = _build(
        text,
        aliases,
        bank_candidate_signals=candidates,
    )
    public = profile.to_public_dict()

    for field in TUPLE_FIELDS:
        assert isinstance(getattr(profile, field), tuple)
    for field in TUPLE_FIELDS:
        assert isinstance(public[field], list)
    for field in TUPLE_FIELDS[:8]:
        assert len(getattr(profile, field)) <= MAX_VALUES_PER_FIELD
    assert len(profile.signal_metadata) <= MAX_SIGNAL_METADATA
    assert len(profile.unresolved) <= MAX_UNRESOLVED


def test_metadata_cap_preserves_explicit_field_coverage_before_candidates(
) -> None:
    categories = (
        "geographies",
        "sectors",
        "affected_groups",
        "institutions",
        "systems_assets",
        "hazards",
    )
    aliases = {
        category: {
            **{
                f"{category}_document_{index:02d}": [
                    f"{category}_explicit_{index:02d}"
                ]
                for index in range(MAX_VALUES_PER_FIELD)
            },
            **{
                f"{category}_candidate_{index:02d}": []
                for index in range(MAX_VALUES_PER_FIELD)
            },
        }
        for category in categories
    }
    text = " ".join(
        f"{category}_explicit_{index:02d}"
        for category in categories
        for index in range(MAX_VALUES_PER_FIELD)
    )
    candidates = {
        category: [
            f"{category}_candidate_{index:02d}"
            for index in range(MAX_VALUES_PER_FIELD)
        ]
        for category in categories[:3]
    }

    profile = _build(
        text,
        aliases,
        bank_candidate_signals=candidates,
    )

    assert len(profile.signal_metadata) == MAX_SIGNAL_METADATA
    assert {match.source for match in profile.signal_metadata} == {"document"}
    for field in ("institutions", "systems_assets", "documented_hazards"):
        assert any(
            match.field == field and match.source == "document"
            for match in profile.signal_metadata
        )


def test_repeated_calls_are_equal_and_profiles_are_frozen() -> None:
    text = "Northern Arc agriculture drought."

    first = _build(text)
    second = _build(text)

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.country = "Changed"  # type: ignore[misc]


def test_direct_construction_detaches_mutable_tuple_inputs() -> None:
    values = {
        field: [f"{field}-initial"]
        for field in TUPLE_FIELDS[:8]
    }
    metadata = [
        SignalMatch(
            field="geographies",
            canonical_value="Initial County",
            source="document",
            confidence="high",
        )
    ]
    unresolved = ["geographies:Candidate County"]
    profile = ProjectClimateProfile(
        country="South Sudan",
        instrument="IPF",
        document_stage="PAD",
        geographies=values["geographies"],  # type: ignore[arg-type]
        sectors=values["sectors"],  # type: ignore[arg-type]
        project_elements=values["project_elements"],  # type: ignore[arg-type]
        affected_groups=values["affected_groups"],  # type: ignore[arg-type]
        institutions=values["institutions"],  # type: ignore[arg-type]
        systems_assets=values["systems_assets"],  # type: ignore[arg-type]
        documented_hazards=values["documented_hazards"],  # type: ignore[arg-type]
        time_horizons=values["time_horizons"],  # type: ignore[arg-type]
        signal_metadata=metadata,  # type: ignore[arg-type]
        unresolved=unresolved,  # type: ignore[arg-type]
    )

    for items in values.values():
        items.append("mutated")
    metadata.clear()
    unresolved.clear()

    for field in TUPLE_FIELDS:
        assert isinstance(getattr(profile, field), tuple)
    assert profile.geographies == ("geographies-initial",)
    assert len(profile.signal_metadata) == 1
    assert profile.unresolved == ("geographies:Candidate County",)


def test_matching_work_respects_public_deterministic_bounds() -> None:
    assert climate_profile.MAX_DOCUMENT_CHARS > 0
    assert climate_profile.MAX_CATALOG_CANONICALS_PER_FIELD > 0
    assert climate_profile.MAX_ALIASES_PER_CANONICAL > 1

    tail_aliases = _selection_aliases()
    tail_aliases["systems_assets"] = {"tail asset": ["tail marker"]}
    tail = _build(
        ("x" * climate_profile.MAX_DOCUMENT_CHARS) + " tail marker",
        tail_aliases,
    )
    assert tail.systems_assets == ()

    catalog_aliases = _selection_aliases()
    catalog_aliases["geographies"] = {
        f"bounded place {index:03d}": [f"place alias {index:03d}"]
        for index in range(
            climate_profile.MAX_CATALOG_CANONICALS_PER_FIELD + 1
        )
    }
    last_index = climate_profile.MAX_CATALOG_CANONICALS_PER_FIELD
    catalog = _build(f"place alias {last_index:03d}", catalog_aliases)
    assert catalog.geographies == ()

    per_canonical_aliases = _selection_aliases()
    per_canonical_aliases["systems_assets"] = {
        "bounded asset": [
            f"asset alias {index:03d}"
            for index in range(
                climate_profile.MAX_ALIASES_PER_CANONICAL + 1
            )
        ]
    }
    alias = _build(
        f"asset alias {climate_profile.MAX_ALIASES_PER_CANONICAL:03d}",
        per_canonical_aliases,
    )
    assert alias.systems_assets == ()


def test_oversized_catalog_and_candidate_inputs_are_rejected() -> None:
    aliases = {
        category: {}
        for category in (
            "geographies",
            "sectors",
            "affected_groups",
            "institutions",
            "systems_assets",
            "hazards",
        )
    }
    aliases["geographies"] = {
        f"bounded place {index:03d}": []
        for index in range(
            climate_profile.MAX_CATALOG_CANONICALS_PER_FIELD + 1
        )
    }
    aliases["systems_assets"] = {
        "bounded asset": [
            f"asset alias {index:03d}"
            for index in range(
                climate_profile.MAX_ALIASES_PER_CANONICAL + 1
            )
        ]
    }
    aliases["hazards"] = {"candidate hazard": []}

    profile = _build(
        "bounded place 000 asset alias 000",
        aliases,
        bank_candidate_signals={
            "hazards": [
                "candidate hazard"
                for _index in range(
                    climate_profile.MAX_CANDIDATES_PER_FIELD + 1
                )
            ]
        },
    )

    assert profile.geographies == ()
    assert profile.systems_assets == ()
    assert profile.unresolved == ()


def test_catalog_and_candidate_boundary_sizes_remain_valid() -> None:
    aliases = {
        category: {}
        for category in (
            "geographies",
            "sectors",
            "affected_groups",
            "institutions",
            "systems_assets",
            "hazards",
        )
    }
    aliases["geographies"] = {
        f"bounded place {index:03d}": []
        for index in range(
            climate_profile.MAX_CATALOG_CANONICALS_PER_FIELD
        )
    }
    aliases["systems_assets"] = {
        "bounded asset": [
            f"asset alias {index:03d}"
            for index in range(
                climate_profile.MAX_ALIASES_PER_CANONICAL
            )
        ]
    }
    aliases["hazards"] = {"candidate hazard": []}
    last_index = climate_profile.MAX_CATALOG_CANONICALS_PER_FIELD - 1

    profile = _build(
        f"bounded place {last_index:03d} asset alias 000",
        aliases,
        bank_candidate_signals={
            "hazards": [
                "candidate hazard"
                for _index in range(
                    climate_profile.MAX_CANDIDATES_PER_FIELD
                )
            ]
        },
    )

    assert profile.geographies == (f"bounded place {last_index:03d}",)
    assert profile.systems_assets == ("bounded asset",)
    assert profile.unresolved == (
        "documented_hazards:candidate hazard",
    )


def test_alias_limit_counts_canonical_separately() -> None:
    aliases = _selection_aliases()
    aliases["systems_assets"] = {
        "bounded asset": [
            f"asset alias {index:03d}"
            for index in range(
                climate_profile.MAX_ALIASES_PER_CANONICAL
            )
        ]
    }
    last_alias = climate_profile.MAX_ALIASES_PER_CANONICAL - 1

    profile = _build(f"asset alias {last_alias:03d}", aliases)

    assert profile.systems_assets == ("bounded asset",)
