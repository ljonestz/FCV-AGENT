"""Deterministic project-relevant selection from a validated climate bank."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
import re
from typing import Any, Iterable, Mapping

from .climate_bank import ClimateBankLoad, materialize_bank_manifest
from .climate_project_profile import ProjectClimateProfile


CLIMATE_BANK_TARGET_ITEMS = 8
CLIMATE_BANK_MAX_ITEMS = 12
CLIMATE_BANK_MAX_CHARS = 6_000
CLIMATE_BANK_MAX_CANDIDATES = 256

MATCH_WEIGHTS = {
    "geographies": 12,
    "project_elements": 10,
    "sectors": 8,
    "affected_groups": 7,
    "institutions": 7,
    "systems_assets": 7,
    "documented_hazards": 4,
    "time_horizons": 3,
}

_TOKEN = re.compile(r"[a-z0-9]+")
_SOURCE_DIVERSITY_CAP = 3
_NEAR_DUPLICATE_THRESHOLD = 0.80
_MATCHED_FIELDS = tuple(MATCH_WEIGHTS)
_MATERIAL_FIELDS = frozenset(_MATCHED_FIELDS) - {"time_horizons"}
_BALANCE_SLOTS = (
    "climate-pressure",
    "vulnerability-capacity",
    "vulnerability-capacity",
    "institution-response",
    "climate-to-fcv-pathway",
    "reverse-or-bidirectional-pathway",
)
_MISSING_CLASSES = tuple(dict.fromkeys(_BALANCE_SLOTS))
_VULNERABILITY_ROLES = {
    "sensitivity",
    "coping-capacity",
    "adaptive-capacity",
}
_INSTITUTION_ROLES = {
    "institutional-capacity",
    "response-performance",
}
_V1_ROLE_MAP = {
    "physical-baseline": "climate-pressure",
    "vulnerability-capacity": "sensitivity",
    "direct-climate-fcv": "direct-climate-fcv",
}
_PATHWAY_ROLE_MAP = {
    "climate-to-fcv": "climate-to-fcv-pathway",
    "fcv-to-climate": "fcv-to-climate-pathway",
    "bidirectional": "bidirectional-pathway",
}
_SUPPRESSION_ORDER = {
    "stale_current": 0,
    "stale_support": 1,
    "near_duplicate": 2,
    "source_diversity": 3,
    "low_relevance": 4,
    "packet_bound": 5,
    "target_reached": 6,
}


@dataclass(frozen=True)
class _Candidate:
    record_id: str
    kind: str
    score: int
    matched_fields: tuple[str, ...]
    balance_role: str
    source_ids: tuple[str, ...]
    claim_tokens: frozenset[str]
    staleness: str = ""


def _tokens(value: Any) -> set[str]:
    """Normalize text using the selector's stable, deliberately small rules."""

    if isinstance(value, (list, tuple, set)):
        text = " ".join(str(item) for item in value)
    else:
        text = str(value or "")
    result: set[str] = set()
    for token in _TOKEN.findall(text.casefold()):
        if len(token) > 4 and token.endswith("s"):
            token = token[:-1]
        result.add(token)
    return result


def _field_values(record: Mapping[str, Any], *keys: str) -> tuple[str, ...]:
    values: list[Any] = []
    for key in keys:
        value = record.get(key)
        if isinstance(value, list):
            values.extend(value)
        elif value is not None:
            values.append(value)
    return tuple(str(value) for value in values if isinstance(value, str))


def _canonical_value(value: str) -> str:
    return " ".join(re.sub(r"[-_/]+", " ", value.casefold()).split())


def _canonical_values(values: Iterable[str]) -> set[str]:
    return {
        normalized
        for value in values
        if (normalized := _canonical_value(value))
    }


def _profile_fields(
    profile: ProjectClimateProfile,
) -> dict[str, set[str]]:
    return {
        field: _canonical_values(getattr(profile, field))
        for field in _MATCHED_FIELDS
    }


def _evidence_sources(record: Mapping[str, Any]) -> tuple[str, ...]:
    result: list[str] = []
    for ref in record.get("source_refs", []):
        if isinstance(ref, dict) and isinstance(ref.get("source_id"), str):
            result.append(ref["source_id"])
    return tuple(sorted(set(result)))


def _evidence_fields(record: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    systems = _field_values(record, "systems_assets_resources")
    return {
        "geographies": _field_values(record, "geographies"),
        "sectors": _field_values(record, "sectors"),
        "project_elements": _field_values(
            record, "project_elements", "impact_tags"
        )
        + systems,
        "affected_groups": _field_values(record, "affected_groups"),
        "institutions": _field_values(record, "institutions"),
        "systems_assets": systems,
        "documented_hazards": _field_values(record, "hazard_tags"),
        "time_horizons": _field_values(record, "time_horizons"),
    }


def _pathway_fields(record: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    systems = _field_values(record, "systems_assets_resources")
    return {
        "geographies": _field_values(record, "geographies"),
        "sectors": _field_values(record, "sectors"),
        "project_elements": _field_values(
            record, "project_elements", "documented_impact"
        )
        + systems,
        "affected_groups": _field_values(record, "affected_groups"),
        "institutions": _field_values(record, "institutions"),
        "systems_assets": systems,
        "documented_hazards": _field_values(record, "climate_pressure"),
        "time_horizons": (),
    }


def _structured_match(
    profile_fields: Mapping[str, set[str]],
    record_fields: Mapping[str, tuple[str, ...]],
) -> tuple[int, tuple[str, ...]]:
    matched = tuple(
        field
        for field in _MATCHED_FIELDS
        if profile_fields[field].intersection(
            _canonical_values(record_fields[field])
        )
    )
    return sum(MATCH_WEIGHTS[field] for field in matched), matched


def _legacy_match(
    signal_tokens: set[str],
    record_fields: Mapping[str, tuple[str, ...]],
) -> tuple[int, tuple[str, ...]]:
    matched = tuple(
        field
        for field in _MATCHED_FIELDS
        if signal_tokens.intersection(_tokens(record_fields[field]))
    )
    return sum(MATCH_WEIGHTS[field] for field in matched), matched


def _evidence_role(record: Mapping[str, Any], schema_version: str) -> str:
    if schema_version == "1.1.0":
        value = record.get("evidence_class")
        return str(value) if isinstance(value, str) else "direct-climate-fcv"
    return _V1_ROLE_MAP.get(
        str(record.get("analytical_role", "")),
        "direct-climate-fcv",
    )


def _pathway_role(record: Mapping[str, Any]) -> str:
    return _PATHWAY_ROLE_MAP.get(
        str(record.get("interaction_direction", "")),
        "climate-to-fcv-pathway",
    )


def _current_staleness(
    record: Mapping[str, Any],
    selection_date: date,
) -> str:
    if record.get("refresh_tier") != "current":
        return ""
    try:
        review_due = date.fromisoformat(str(record.get("review_due", "")))
    except ValueError:
        return ""
    return (
        "stale_current"
        if review_due < selection_date
        else "fresh_current"
    )


def _pathway_sources(
    record: Mapping[str, Any],
    evidence_index: Mapping[str, dict[str, Any]],
) -> tuple[str, ...]:
    result: list[str] = []
    for evidence_id in record.get("supporting_evidence_ids", []):
        evidence = evidence_index.get(evidence_id)
        if evidence:
            result.extend(_evidence_sources(evidence))
    return tuple(sorted(set(result)))


def _pathway_staleness(
    record: Mapping[str, Any],
    evidence_index: Mapping[str, dict[str, Any]],
    selection_date: date,
) -> str:
    supporting = (
        evidence_index.get(evidence_id)
        for evidence_id in record.get("supporting_evidence_ids", [])
    )
    return (
        "stale_support"
        if any(
            evidence is not None
            and _current_staleness(evidence, selection_date)
            == "stale_current"
            for evidence in supporting
        )
        else ""
    )


def _candidate(
    record: Mapping[str, Any],
    *,
    kind: str,
    schema_version: str,
    profile_fields: Mapping[str, set[str]] | None,
    legacy_tokens: set[str],
    evidence_index: Mapping[str, dict[str, Any]],
    selection_date: date,
) -> _Candidate:
    record_fields = (
        _evidence_fields(record)
        if kind == "evidence"
        else _pathway_fields(record)
    )
    score, matched = (
        _structured_match(profile_fields, record_fields)
        if profile_fields is not None
        else _legacy_match(legacy_tokens, record_fields)
    )
    record_id = str(
        record.get("evidence_id" if kind == "evidence" else "pathway_id", "")
    )
    source_ids = (
        _evidence_sources(record)
        if kind == "evidence"
        else _pathway_sources(record, evidence_index)
    )
    return _Candidate(
        record_id=record_id,
        kind=kind,
        score=score,
        matched_fields=matched,
        balance_role=(
            _evidence_role(record, schema_version)
            if kind == "evidence"
            else _pathway_role(record)
        ),
        source_ids=source_ids,
        claim_tokens=frozenset(
            _tokens(str(record.get("compact_statement", "")))
        ),
        staleness=(
            _current_staleness(record, selection_date)
            if kind == "evidence"
            else _pathway_staleness(
                record,
                evidence_index,
                selection_date,
            )
        ),
    )


def _rank(candidates: Iterable[_Candidate]) -> list[_Candidate]:
    return sorted(candidates, key=lambda item: (-item.score, item.record_id))


def _slot_accepts(slot: str, candidate: _Candidate) -> bool:
    if slot == "climate-pressure":
        return candidate.balance_role == "climate-pressure"
    if slot == "vulnerability-capacity":
        return candidate.balance_role in _VULNERABILITY_ROLES
    if slot == "institution-response":
        return candidate.balance_role in _INSTITUTION_ROLES
    if slot == "climate-to-fcv-pathway":
        return candidate.balance_role == "climate-to-fcv-pathway"
    return candidate.balance_role in {
        "fcv-to-climate-pathway",
        "bidirectional-pathway",
    }


def _source_fit(
    candidate: _Candidate,
    source_counts: Mapping[str, int],
) -> bool:
    return all(
        source_counts.get(source_id, 0) < _SOURCE_DIVERSITY_CAP
        for source_id in candidate.source_ids
    )


def _add_candidate(
    selected: list[_Candidate],
    candidate: _Candidate,
    source_counts: dict[str, int],
) -> None:
    selected.append(candidate)
    for source_id in candidate.source_ids:
        source_counts[source_id] = source_counts.get(source_id, 0) + 1


def _near_duplicate(
    candidate: _Candidate,
    retained: Iterable[_Candidate],
) -> bool:
    if not candidate.claim_tokens:
        return False
    for other in retained:
        if not other.claim_tokens:
            continue
        union = candidate.claim_tokens | other.claim_tokens
        if (
            union
            and len(candidate.claim_tokens & other.claim_tokens) / len(union)
            >= _NEAR_DUPLICATE_THRESHOLD
        ):
            return True
    return False


def _suppressed_rows(
    suppressed: Mapping[str, str],
) -> list[dict[str, str]]:
    return [
        {"id": record_id, "reason": reason}
        for record_id, reason in sorted(
            suppressed.items(),
            key=lambda item: (
                _SUPPRESSION_ORDER[item[1]],
                item[0],
            ),
        )[:CLIMATE_BANK_MAX_ITEMS]
    ]


def _missing_classes(selected: Iterable[_Candidate]) -> list[str]:
    selected_list = list(selected)
    vulnerability_roles = {
        item.balance_role
        for item in selected_list
        if item.balance_role in _VULNERABILITY_ROLES
    }
    missing = []
    for slot in _MISSING_CLASSES:
        if slot == "vulnerability-capacity":
            present = len(vulnerability_roles) >= 2
        else:
            present = any(
                _slot_accepts(slot, candidate)
                for candidate in selected_list
            )
        if not present:
            missing.append(slot)
    return missing


def _unavailable(code: str) -> dict[str, str]:
    return {"bank_status": "unavailable", "warning_code": code}


def _manifest(
    bank: ClimateBankLoad,
    country: dict[str, Any],
    selected: list[_Candidate],
    suppressed: Mapping[str, str],
) -> dict[str, Any]:
    ranked = _rank(selected)
    manifest = {
        "bank_status": "ok",
        "warning_code": "",
        "schema_version": bank.release["schema_version"],
        "content_version": bank.release["content_version"],
        "country_iso3": country["iso3"],
        "evidence_ids": [
            item.record_id for item in ranked if item.kind == "evidence"
        ],
        "pathway_ids": [
            item.record_id for item in ranked if item.kind == "pathway"
        ],
        "diagnostics": {
            "selected": [
                {
                    **{
                        "id": item.record_id,
                        "score": int(item.score),
                        "matched_fields": list(item.matched_fields),
                        "balance_role": item.balance_role,
                    },
                    **(
                        {"staleness": item.staleness}
                        if item.staleness
                        else {}
                    ),
                }
                for item in ranked[:CLIMATE_BANK_MAX_ITEMS]
            ],
            "suppressed": _suppressed_rows(suppressed),
            "missing_classes": _missing_classes(ranked)[:9],
        },
    }
    if bank.candidate_preview:
        manifest["candidate_preview"] = True
    return manifest


def compact_bank_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Project canonical records into the bounded Stage-2 grounding shape."""

    if not isinstance(packet, dict) or packet.get("bank_status") != "ok":
        return {}
    sources = []
    for source in packet.get("sources", []):
        if not isinstance(source, dict):
            continue
        sources.append({"source_id": source.get("source_id")})
    evidence_records = []
    for record in packet.get("evidence_records", []):
        if not isinstance(record, dict):
            continue
        evidence_records.append(
            {
                **{
                    key: record.get(key)
                    for key in (
                        "evidence_id", "compact_statement", "evidence_status",
                        "analytical_role",
                    )
                },
                "source_ids": [
                    ref.get("source_id")
                    for ref in record.get("source_refs", [])
                    if isinstance(ref, dict)
                ],
            }
        )
    pathways = []
    for record in packet.get("pathways", []):
        if not isinstance(record, dict):
            continue
        pathways.append(
            {
                key: record.get(key)
                for key in (
                    "pathway_id", "compact_statement", "evidence_strength",
                    "supporting_evidence_ids", "interaction_direction",
                )
            }
        )
    compact = {
        "content_version": packet.get("content_version"),
        "country_iso3": packet.get("country_iso3"),
        "sources": sources,
        "evidence_records": evidence_records,
        "pathways": pathways,
    }
    if packet.get("candidate_preview") is True:
        compact["candidate_preview"] = True
    return compact


def _compact_packet_length(packet: dict[str, Any]) -> int:
    return len(
        json.dumps(
            compact_bank_packet(packet),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def _addition_issue(
    bank: ClimateBankLoad,
    country: dict[str, Any],
    selected: list[_Candidate],
    candidate: _Candidate,
    source_counts: Mapping[str, int],
) -> tuple[str, str]:
    """Return a controlled selection constraint and any fatal warning."""

    if not _source_fit(candidate, source_counts):
        return "source_diversity", ""
    if _near_duplicate(candidate, selected):
        return "near_duplicate", ""
    trial = [*selected, candidate]
    packet = materialize_bank_manifest(
        bank,
        _manifest(bank, country, trial, {}),
    )
    if packet.get("bank_status") != "ok":
        return "", str(
            packet.get("warning_code") or "bank_manifest_invalid"
        )
    if _compact_packet_length(packet) > CLIMATE_BANK_MAX_CHARS:
        return "packet_bound", ""
    return "", ""


def select_bank_manifest(
    bank: ClimateBankLoad,
    *,
    country: str,
    country_scope: str,
    resolved_country_count: int,
    project_profile: ProjectClimateProfile | None = None,
    sector: str = "",
    project_signals: Any = None,
    as_of: date | None = None,
) -> dict[str, Any]:
    """Select a balanced canonical-ID manifest for one resolved country.

    The project_signals argument remains only as a transition path until
    application wiring supplies the typed profile. Raw text is never returned.
    """

    if not isinstance(bank, ClimateBankLoad) or bank.status != "ok":
        code = (
            bank.warning_code
            if isinstance(bank, ClimateBankLoad) and bank.warning_code
            else "bank_unavailable"
        )
        return _unavailable(code)

    resolved = bank.resolve_country(country)
    if resolved is None:
        return _unavailable("bank_country_unavailable")
    if country_scope != "single" or resolved_country_count != 1:
        return _unavailable("bank_scope_unsupported")
    if project_profile is not None and not isinstance(
        project_profile, ProjectClimateProfile
    ):
        return _unavailable("bank_profile_invalid")

    iso3 = resolved.get("iso3")
    if not isinstance(iso3, str):
        return _unavailable("bank_country_unavailable")
    country_evidence_ids = resolved.get("evidence_ids", [])
    country_pathway_ids = resolved.get("pathway_ids", [])
    if (
        not isinstance(country_evidence_ids, list)
        or not isinstance(country_pathway_ids, list)
        or len(country_evidence_ids) + len(country_pathway_ids)
        > CLIMATE_BANK_MAX_CANDIDATES
    ):
        return _unavailable("bank_packet_too_large")
    evidence_ids = set(country_evidence_ids)
    pathway_ids = set(country_pathway_ids)
    evidence_records = [
        item
        for item in bank.release.get("evidence_records", [])
        if isinstance(item, dict)
        and item.get("iso3") == iso3
        and item.get("evidence_id") in evidence_ids
    ]
    pathway_records = [
        item
        for item in bank.release.get("pathways", [])
        if isinstance(item, dict)
        and item.get("iso3") == iso3
        and item.get("pathway_id") in pathway_ids
    ]
    evidence_index = {
        item["evidence_id"]: item
        for item in evidence_records
        if isinstance(item.get("evidence_id"), str)
    }
    profile_fields = (
        _profile_fields(project_profile)
        if project_profile is not None
        else None
    )
    legacy_tokens = (
        set()
        if project_profile is not None
        else _tokens([project_signals, sector])
    )
    schema_version = str(bank.release.get("schema_version", ""))
    selection_date = as_of or date.today()
    candidates = _rank(
        [
            *(
                _candidate(
                    item,
                    kind="evidence",
                    schema_version=schema_version,
                    profile_fields=profile_fields,
                    legacy_tokens=legacy_tokens,
                    evidence_index=evidence_index,
                    selection_date=selection_date,
                )
                for item in evidence_records
            ),
            *(
                _candidate(
                    item,
                    kind="pathway",
                    schema_version=schema_version,
                    profile_fields=profile_fields,
                    legacy_tokens=legacy_tokens,
                    evidence_index=evidence_index,
                    selection_date=selection_date,
                )
                for item in pathway_records
            ),
        ]
    )

    permanent_suppressions: dict[str, str] = {}
    eligible: list[_Candidate] = []
    for candidate in candidates:
        if candidate.staleness in {"stale_current", "stale_support"}:
            permanent_suppressions[candidate.record_id] = candidate.staleness
            continue
        if not _MATERIAL_FIELDS.intersection(candidate.matched_fields):
            permanent_suppressions[candidate.record_id] = "low_relevance"
            continue
        eligible.append(candidate)

    selected: list[_Candidate] = []
    source_counts: dict[str, int] = {}
    selected_ids: set[str] = set()
    packet_rejected_ids: set[str] = set()

    def try_add(candidate: _Candidate) -> str:
        issue, warning = _addition_issue(
            bank,
            resolved,
            selected,
            candidate,
            source_counts,
        )
        if warning:
            return warning
        if issue:
            if issue == "packet_bound":
                packet_rejected_ids.add(candidate.record_id)
            return ""
        _add_candidate(selected, candidate, source_counts)
        selected_ids.add(candidate.record_id)
        return ""

    for slot in _BALANCE_SLOTS:
        slot_candidates = [
            item
            for item in eligible
            if item.record_id not in selected_ids
            and _slot_accepts(slot, item)
        ]
        if slot == "vulnerability-capacity":
            selected_vulnerability_roles = {
                item.balance_role
                for item in selected
                if item.balance_role in _VULNERABILITY_ROLES
            }
            distinct = [
                item
                for item in slot_candidates
                if item.balance_role not in selected_vulnerability_roles
            ]
            if distinct:
                repeated = [
                    item for item in slot_candidates if item not in distinct
                ]
                slot_candidates = [*distinct, *repeated]
        for candidate in slot_candidates:
            before = len(selected)
            warning = try_add(candidate)
            if warning:
                return _unavailable(warning)
            if len(selected) > before:
                break

    for candidate in eligible:
        if len(selected) >= CLIMATE_BANK_TARGET_ITEMS:
            break
        if candidate.record_id in selected_ids:
            continue
        warning = try_add(candidate)
        if warning:
            return _unavailable(warning)

    suppressed = dict(permanent_suppressions)
    for candidate in eligible:
        if candidate.record_id in selected_ids:
            continue
        if candidate.record_id in packet_rejected_ids:
            reason = "packet_bound"
        elif not _source_fit(candidate, source_counts):
            reason = "source_diversity"
        elif _near_duplicate(candidate, selected):
            reason = "near_duplicate"
        else:
            reason = "target_reached"
        suppressed[candidate.record_id] = reason

    selected = _rank(selected)[:CLIMATE_BANK_MAX_ITEMS]

    if not selected:
        if eligible and packet_rejected_ids:
            return _unavailable("bank_packet_too_large")
        manifest = _manifest(bank, resolved, selected, suppressed)
        packet = materialize_bank_manifest(bank, manifest)
        if packet.get("bank_status") != "ok":
            return _unavailable(
                str(packet.get("warning_code") or "bank_manifest_invalid")
            )
        return manifest

    return _manifest(bank, resolved, selected, suppressed)
