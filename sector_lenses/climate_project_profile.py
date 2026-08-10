"""Deterministic, content-safe project signals for Climate-FCV selection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Mapping, Sequence


MAX_VALUES_PER_FIELD = 12
MAX_SIGNAL_METADATA = 64
MAX_UNRESOLVED = 24
MAX_DOCUMENT_CHARS = 12_000
MAX_CATALOG_CANONICALS_PER_FIELD = 128
MAX_ALIASES_PER_CANONICAL = 8
MAX_CANDIDATES_PER_FIELD = 128

_FIELD_CATALOGS = (
    ("geographies", "geographies"),
    ("sectors", "sectors"),
    ("project_elements", "project_elements"),
    ("affected_groups", "affected_groups"),
    ("institutions", "institutions"),
    ("systems_assets", "systems_assets"),
    ("hazards", "documented_hazards"),
    ("time_horizons", "time_horizons"),
)
_FIELD_ORDER = {
    field: index
    for index, (_category, field) in enumerate(_FIELD_CATALOGS)
}
_SOURCE_ORDER = {
    "document": 0,
    "metadata": 1,
    "bank-candidate": 2,
}

_DEFAULT_TIME_HORIZON_ALIASES = {
    "current": ("current climate conditions", "current hazard conditions"),
    "long-term": ("long-term", "long term"),
    "medium-term": ("medium-term", "medium term"),
    "near-term": ("near-term", "near term"),
}


@dataclass(frozen=True)
class SignalMatch:
    """One controlled match without uploaded source text."""

    field: str
    canonical_value: str
    source: str
    confidence: str


@dataclass(frozen=True)
class ProjectClimateProfile:
    """Immutable, bounded project facts used by deterministic selection."""

    country: str
    instrument: str
    document_stage: str
    geographies: tuple[str, ...]
    sectors: tuple[str, ...]
    project_elements: tuple[str, ...]
    affected_groups: tuple[str, ...]
    institutions: tuple[str, ...]
    systems_assets: tuple[str, ...]
    documented_hazards: tuple[str, ...]
    time_horizons: tuple[str, ...]
    signal_metadata: tuple[SignalMatch, ...]
    unresolved: tuple[str, ...]

    def __post_init__(self) -> None:
        string_fields = (
            "geographies",
            "sectors",
            "project_elements",
            "affected_groups",
            "institutions",
            "systems_assets",
            "documented_hazards",
            "time_horizons",
            "unresolved",
        )
        for field in string_fields:
            value = getattr(self, field)
            if not isinstance(value, (tuple, list)):
                raise TypeError(f"{field} must be a tuple or list")
            normalized = tuple(value)
            if not all(isinstance(item, str) for item in normalized):
                raise TypeError(f"{field} must contain only strings")
            object.__setattr__(self, field, normalized)

        metadata = self.signal_metadata
        if not isinstance(metadata, (tuple, list)):
            raise TypeError("signal_metadata must be a tuple or list")
        normalized_metadata = tuple(metadata)
        if not all(
            isinstance(item, SignalMatch) for item in normalized_metadata
        ):
            raise TypeError(
                "signal_metadata must contain only SignalMatch values"
            )
        object.__setattr__(
            self,
            "signal_metadata",
            normalized_metadata,
        )

    def to_public_dict(self) -> dict[str, Any]:
        """Return a fresh JSON-safe projection with no source excerpts."""

        return {
            "country": self.country,
            "instrument": self.instrument,
            "document_stage": self.document_stage,
            "geographies": list(self.geographies),
            "sectors": list(self.sectors),
            "project_elements": list(self.project_elements),
            "affected_groups": list(self.affected_groups),
            "institutions": list(self.institutions),
            "systems_assets": list(self.systems_assets),
            "documented_hazards": list(self.documented_hazards),
            "time_horizons": list(self.time_horizons),
            "signal_metadata": [
                asdict(match) for match in self.signal_metadata
            ],
            "unresolved": list(self.unresolved),
        }


def _sort_key(value: str) -> tuple[str, str]:
    return value.casefold(), value


def _signal_sort_key(
    match: SignalMatch,
) -> tuple[int, str, str, int, str, str]:
    return (
        _FIELD_ORDER[match.field],
        *_sort_key(match.canonical_value),
        _SOURCE_ORDER[match.source],
        match.source,
        match.confidence,
    )


def _round_robin_signals(
    matches: Sequence[SignalMatch],
) -> list[SignalMatch]:
    by_field = {
        field: [] for _category, field in _FIELD_CATALOGS
    }
    for match in sorted(matches, key=_signal_sort_key):
        by_field[match.field].append(match)
    largest_field = max(
        (len(field_matches) for field_matches in by_field.values()),
        default=0,
    )
    return [
        by_field[field][index]
        for index in range(largest_field)
        for _category, field in _FIELD_CATALOGS
        if index < len(by_field[field])
    ]


def _bound_signal_metadata(
    explicit_matches: Sequence[SignalMatch],
    candidate_matches: Sequence[SignalMatch],
) -> tuple[SignalMatch, ...]:
    selected = (
        _round_robin_signals(explicit_matches)
        + _round_robin_signals(candidate_matches)
    )[:MAX_SIGNAL_METADATA]
    return tuple(sorted(selected, key=_signal_sort_key))


def _catalog(
    value: Any,
    *,
    include_canonical: bool = True,
) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, Mapping):
        return {}
    if len(value) > MAX_CATALOG_CANONICALS_PER_FIELD:
        return {}
    canonical_values = [
        canonical
        for canonical in sorted(
            value, key=lambda item: _sort_key(str(item))
        )
        if isinstance(canonical, str) and canonical.strip()
    ]
    canonical_owners: dict[str, set[str]] = {}
    for canonical in canonical_values:
        canonical_owners.setdefault(canonical.casefold(), set()).add(canonical)

    unambiguous_canonicals = [
        canonical
        for canonical in canonical_values
        if len(canonical_owners[canonical.casefold()]) == 1
    ][:MAX_CATALOG_CANONICALS_PER_FIELD]

    raw_catalog: dict[str, tuple[str, ...]] = {}
    for canonical in unambiguous_canonicals:
        raw_aliases = value[canonical]
        if (
            not isinstance(raw_aliases, Sequence)
            or isinstance(raw_aliases, (str, bytes))
            or len(raw_aliases) > (
                MAX_ALIASES_PER_CANONICAL
                + (0 if include_canonical else 1)
            )
        ):
            continue
        aliases: list[str] = [canonical] if include_canonical else []
        aliases.extend(
            alias
            for alias in raw_aliases
            if isinstance(alias, str) and alias.strip()
        )
        deduplicated = {
            alias.casefold(): alias
            for alias in sorted(aliases, key=_sort_key)
        }
        raw_catalog[canonical] = tuple(
            deduplicated[key] for key in sorted(deduplicated)
        )

    alias_owners: dict[str, set[str]] = {}
    for canonical, aliases in raw_catalog.items():
        for alias in aliases:
            alias_owners.setdefault(alias.casefold(), set()).add(canonical)
    catalog: dict[str, tuple[str, ...]] = {}
    for canonical, aliases in raw_catalog.items():
        unique_aliases = [
            alias
            for alias in aliases
            if len(alias_owners[alias.casefold()]) == 1
        ]
        canonical_key = canonical.casefold()
        unique_aliases.sort(
            key=lambda alias: (
                0 if alias.casefold() == canonical_key else 1,
                *_sort_key(alias),
            )
        )
        canonical_aliases = [
            alias
            for alias in unique_aliases
            if alias.casefold() == canonical_key
        ][:1]
        other_aliases = [
            alias
            for alias in unique_aliases
            if alias.casefold() != canonical_key
        ][:MAX_ALIASES_PER_CANONICAL]
        catalog[canonical] = tuple(canonical_aliases + other_aliases)
    return catalog


def _merge_catalogs(
    *catalogs: Mapping[str, Sequence[str]],
) -> dict[str, tuple[str, ...]]:
    merged: dict[str, set[str]] = {}
    for catalog in catalogs:
        for canonical, aliases in catalog.items():
            merged.setdefault(canonical, set()).update(aliases)
    combined = {
        canonical: tuple(sorted(aliases, key=_sort_key))
        for canonical, aliases in sorted(
            merged.items(), key=lambda item: _sort_key(item[0])
        )
    }
    return _catalog(combined, include_canonical=False)


def _pattern(alias: str) -> re.Pattern[str]:
    escaped = re.escape(alias).replace(r"\ ", r"\s+")
    return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)


def _bounded_document_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    if len(value) <= MAX_DOCUMENT_CHARS:
        return value
    bounded = value[:MAX_DOCUMENT_CHARS]
    if (
        bounded
        and not bounded[-1].isspace()
        and not value[MAX_DOCUMENT_CHARS].isspace()
    ):
        token_start = len(bounded)
        while token_start and not bounded[token_start - 1].isspace():
            token_start -= 1
        return bounded[:token_start]
    return bounded


def _explicit_matches(
    document_text: str,
    catalog: Mapping[str, Sequence[str]],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    aliases: list[tuple[int, int, str, str]] = []
    for canonical in sorted(catalog, key=_sort_key):
        for alias in catalog[canonical]:
            aliases.append(
                (
                    len(re.findall(r"\S+", alias)),
                    len(re.sub(r"\s+", "", alias)),
                    canonical,
                    alias,
                )
            )

    aliases.sort(
        key=lambda item: (
            -item[0],
            -item[1],
            *_sort_key(item[2]),
            *_sort_key(item[3]),
        )
    )
    occupied = bytearray(len(document_text))
    accepted_values: set[str] = set()
    for _tokens, _characters, canonical, alias in aliases:
        for occurrence in _pattern(alias).finditer(document_text):
            start, end = occurrence.span()
            if any(occupied[start:end]):
                continue
            occupied[start:end] = b"\x01" * (end - start)
            accepted_values.add(canonical)

    complete_values = tuple(sorted(accepted_values, key=_sort_key))
    return (
        complete_values[:MAX_VALUES_PER_FIELD],
        complete_values,
    )


def _catalogs(
    selection_aliases: Any,
    project_element_aliases: Any,
    time_horizon_aliases: Any,
) -> dict[str, dict[str, tuple[str, ...]]]:
    aliases = (
        selection_aliases
        if isinstance(selection_aliases, Mapping)
        else {}
    )
    result = {
        category: _catalog(aliases.get(category, {}))
        for category, _field in _FIELD_CATALOGS
    }
    result["project_elements"] = _merge_catalogs(
        _catalog(aliases.get("project_elements", {})),
        _catalog(project_element_aliases),
    )
    result["time_horizons"] = _merge_catalogs(
        _catalog(
            _DEFAULT_TIME_HORIZON_ALIASES,
            include_canonical=False,
        ),
        _catalog(aliases.get("time_horizons", {})),
        _catalog(time_horizon_aliases),
    )
    return result


def _candidate_matches(
    bank_candidate_signals: Any,
    catalogs: Mapping[str, Mapping[str, Sequence[str]]],
) -> tuple[SignalMatch, ...]:
    if not isinstance(bank_candidate_signals, Mapping):
        return ()

    field_by_category = dict(_FIELD_CATALOGS)
    matches: set[SignalMatch] = set()
    for category, field in _FIELD_CATALOGS:
        raw_values = bank_candidate_signals.get(category, ())
        if (
            not isinstance(raw_values, Sequence)
            or isinstance(raw_values, (str, bytes))
            or len(raw_values) > MAX_CANDIDATES_PER_FIELD
        ):
            continue
        canonical_lookup = {
            canonical.casefold(): canonical
            for canonical in catalogs[category]
        }
        for raw_value in raw_values:
            if not isinstance(raw_value, str):
                continue
            canonical = canonical_lookup.get(raw_value.casefold())
            if canonical is None:
                continue
            matches.add(
                SignalMatch(
                    field=field_by_category[category],
                    canonical_value=canonical,
                    source="bank-candidate",
                    confidence="candidate",
                )
            )
    return tuple(
        sorted(
            matches,
            key=lambda match: (
                match.field,
                *_sort_key(match.canonical_value),
            ),
        )
    )


def build_project_climate_profile(
    *,
    document_text: str,
    country: str,
    instrument: str,
    document_stage: str,
    selection_aliases: Mapping[str, Mapping[str, Sequence[str]]],
    bank_candidate_signals: (
        Mapping[str, Sequence[str]] | None
    ) = None,
    project_element_aliases: (
        Mapping[str, Sequence[str]] | None
    ) = None,
    time_horizon_aliases: (
        Mapping[str, Sequence[str]] | None
    ) = None,
) -> ProjectClimateProfile:
    """Build a deterministic profile from explicit text and metadata only."""

    text = _bounded_document_text(document_text)
    catalogs = _catalogs(
        selection_aliases,
        project_element_aliases,
        time_horizon_aliases,
    )
    values: dict[str, tuple[str, ...]] = {}
    metadata: list[SignalMatch] = []
    complete_explicit_keys: set[tuple[str, str]] = set()

    for category, field in _FIELD_CATALOGS:
        field_values, complete_field_values = _explicit_matches(
            text,
            catalogs[category],
        )
        values[field] = field_values
        complete_explicit_keys.update(
            (field, canonical) for canonical in complete_field_values
        )
        metadata.extend(
            SignalMatch(
                field=field,
                canonical_value=canonical,
                source="document",
                confidence="high",
            )
            for canonical in field_values
        )

    candidates = tuple(
        match
        for match in _candidate_matches(bank_candidate_signals, catalogs)
        if (
            match.field,
            match.canonical_value,
        ) not in complete_explicit_keys
    )
    unresolved = tuple(
        sorted(
            {
                f"{match.field}:{match.canonical_value}"
                for match in candidates
            },
            key=_sort_key,
        )[:MAX_UNRESOLVED]
    )

    return ProjectClimateProfile(
        country=country,
        instrument=instrument,
        document_stage=document_stage,
        geographies=values["geographies"],
        sectors=values["sectors"],
        project_elements=values["project_elements"],
        affected_groups=values["affected_groups"],
        institutions=values["institutions"],
        systems_assets=values["systems_assets"],
        documented_hazards=values["documented_hazards"],
        time_horizons=values["time_horizons"],
        signal_metadata=_bound_signal_metadata(metadata, candidates),
        unresolved=unresolved,
    )
