"""Deterministic project-relevant selection from a validated climate bank."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import re
from typing import Any, Iterable

from .climate_bank import (
    ClimateBankLoad, expired_current_evidence_ids, materialize_bank_manifest,
)


CLIMATE_BANK_TARGET_ITEMS = 8
CLIMATE_BANK_MAX_ITEMS = 12
CLIMATE_BANK_MAX_CHARS = 6_000

MATCH_WEIGHTS = {
    "geography": 10,
    "sector": 8,
    "project_element": 8,
    "affected_group": 6,
    "institution": 6,
    "system_asset_resource": 6,
    "mediator": 4,
    "hazard": 4,
    "direct_climate_fcv_role": 3,
    "vulnerability_capacity_role": 3,
    "direct_pathway": 3,
    "triangulated_pathway": 2,
    "recent_source": 1,
}

_TOKEN = re.compile(r"[a-z0-9]+")
_RECENT_YEARS = 5
_SOURCE_DIVERSITY_CAP = 3


@dataclass(frozen=True)
class _Candidate:
    record_id: str
    kind: str
    score: int
    primary_source_id: str
    physical_baseline: bool = False


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


def _field_tokens(record: dict[str, Any], *keys: str) -> set[str]:
    values: list[Any] = []
    for key in keys:
        value = record.get(key)
        if isinstance(value, list):
            values.extend(value)
        elif value is not None:
            values.append(value)
    return _tokens(values)


def _match_score(
    signal_tokens: set[str],
    fields: Iterable[tuple[str, set[str]]],
) -> int:
    return sum(
        MATCH_WEIGHTS[name]
        for name, field in fields
        if signal_tokens.intersection(field)
    )


def _publication_year(source: dict[str, Any] | None) -> int | None:
    value = source.get("publication_date") if source else None
    match = re.match(r"^(\d{4})", str(value or ""))
    return int(match.group(1)) if match else None


def _release_year(release: dict[str, Any]) -> int:
    value = str(release.get("generated_at", ""))
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).year
    except ValueError:
        match = re.match(r"^(\d{4})", value)
        return int(match.group(1)) if match else datetime.now().year


def _is_recent(
    source_ids: Iterable[str],
    source_index: dict[str, dict[str, Any]],
    release_year: int,
) -> bool:
    cutoff = release_year - _RECENT_YEARS
    return any(
        (year := _publication_year(source_index.get(source_id))) is not None
        and year >= cutoff
        for source_id in source_ids
    )


def _evidence_sources(record: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for ref in record.get("source_refs", []):
        if isinstance(ref, dict) and isinstance(ref.get("source_id"), str):
            result.append(ref["source_id"])
    return result


def _score_evidence(
    record: dict[str, Any],
    *,
    signal_tokens: set[str],
    source_index: dict[str, dict[str, Any]],
    release_year: int,
) -> _Candidate:
    score = _match_score(
        signal_tokens,
        (
            ("geography", _field_tokens(record, "geographies")),
            ("sector", _field_tokens(record, "sectors")),
            (
                "project_element",
                _field_tokens(
                    record,
                    "impact_tags",
                    "statement",
                    "compact_statement",
                ),
            ),
            ("affected_group", _field_tokens(record, "affected_groups")),
            ("institution", _field_tokens(record, "institutions")),
            (
                "system_asset_resource",
                _field_tokens(record, "systems_assets_resources"),
            ),
            ("mediator", _field_tokens(record, "mediator_tags")),
            ("hazard", _field_tokens(record, "hazard_tags")),
        ),
    )
    role = record.get("analytical_role")
    if role == "direct-climate-fcv":
        score += MATCH_WEIGHTS["direct_climate_fcv_role"]
    elif role == "vulnerability-capacity":
        score += MATCH_WEIGHTS["vulnerability_capacity_role"]
    source_ids = _evidence_sources(record)
    if _is_recent(source_ids, source_index, release_year):
        score += MATCH_WEIGHTS["recent_source"]
    return _Candidate(
        record_id=str(record.get("evidence_id", "")),
        kind="evidence",
        score=score,
        primary_source_id=source_ids[0] if source_ids else "",
        physical_baseline=role == "physical-baseline",
    )


def _pathway_sources(
    record: dict[str, Any],
    evidence_index: dict[str, dict[str, Any]],
) -> list[str]:
    result: list[str] = []
    for evidence_id in record.get("supporting_evidence_ids", []):
        evidence = evidence_index.get(evidence_id)
        if evidence:
            result.extend(_evidence_sources(evidence))
    return list(dict.fromkeys(result))


def _score_pathway(
    record: dict[str, Any],
    *,
    signal_tokens: set[str],
    evidence_index: dict[str, dict[str, Any]],
    source_index: dict[str, dict[str, Any]],
    release_year: int,
) -> _Candidate:
    score = _match_score(
        signal_tokens,
        (
            ("geography", _field_tokens(record, "geographies")),
            ("sector", _field_tokens(record, "sectors")),
            (
                "project_element",
                _field_tokens(
                    record,
                    "documented_impact",
                    "possible_consequence",
                    "compact_statement",
                ),
            ),
            ("affected_group", _field_tokens(record, "affected_groups")),
            ("institution", _field_tokens(record, "institutions")),
            (
                "system_asset_resource",
                _field_tokens(record, "systems_assets_resources"),
            ),
            ("mediator", _field_tokens(record, "fcv_mediator")),
            ("hazard", _field_tokens(record, "climate_pressure")),
        ),
    )
    supporting = [
        evidence_index[evidence_id]
        for evidence_id in record.get("supporting_evidence_ids", [])
        if evidence_id in evidence_index
    ]
    roles = {item.get("analytical_role") for item in supporting}
    if "direct-climate-fcv" in roles:
        score += MATCH_WEIGHTS["direct_climate_fcv_role"]
    if "vulnerability-capacity" in roles:
        score += MATCH_WEIGHTS["vulnerability_capacity_role"]
    strength = record.get("evidence_strength")
    if strength == "direct":
        score += MATCH_WEIGHTS["direct_pathway"]
    elif strength == "triangulated":
        score += MATCH_WEIGHTS["triangulated_pathway"]
    source_ids = _pathway_sources(record, evidence_index)
    if _is_recent(source_ids, source_index, release_year):
        score += MATCH_WEIGHTS["recent_source"]
    return _Candidate(
        record_id=str(record.get("pathway_id", "")),
        kind="pathway",
        score=score,
        primary_source_id=source_ids[0] if source_ids else "",
    )


def _rank(candidates: Iterable[_Candidate]) -> list[_Candidate]:
    return sorted(candidates, key=lambda item: (-item.score, item.record_id))


def _unavailable(code: str) -> dict[str, str]:
    return {"bank_status": "unavailable", "warning_code": code}


def _manifest(
    bank: ClimateBankLoad,
    country: dict[str, Any],
    selected: list[_Candidate],
) -> dict[str, Any]:
    manifest = {
        "bank_status": "ok",
        "warning_code": "",
        "schema_version": bank.release["schema_version"],
        "content_version": bank.release["content_version"],
        "country_iso3": country["iso3"],
        "evidence_ids": [
            item.record_id for item in selected if item.kind == "evidence"
        ],
        "pathway_ids": [
            item.record_id for item in selected if item.kind == "pathway"
        ],
    }
    if bank.candidate_preview:
        manifest["candidate_preview"] = True
    return manifest


def _compact_country_profile(value: Any) -> dict[str, Any]:
    """Keep whole, text-bearing profile rows before record ID lists."""

    if not isinstance(value, dict):
        return {}
    profile_max_chars = 1_700
    field_max_chars = 780
    profile: dict[str, Any] = {}
    truncated_fields: set[str] = set()
    id_fields = {
        "record_ids": "record_count",
        "evidence_ids": "evidence_count",
        "pathway_ids": "pathway_count",
        "source_ids": "source_count",
    }
    for field in ("known_gaps", "coverage"):
        rows = value.get(field)
        if not isinstance(rows, list):
            continue
        profile[field] = []
        for row in rows:
            if isinstance(row, dict):
                compact_row = {
                    key: item for key, item in row.items() if key not in id_fields
                }
                for key, count_key in id_fields.items():
                    if isinstance(row.get(key), list):
                        compact_row[count_key] = len(row[key])
            else:
                compact_row = row
            candidate_rows = [*profile[field], compact_row]
            candidate = {"country_profile": {field: candidate_rows}}
            serialized = json.dumps(
                candidate,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            if len(serialized) <= field_max_chars:
                profile[field].append(compact_row)
            else:
                truncated_fields.add(field)
    if truncated_fields:
        profile["truncated_fields"] = sorted(truncated_fields)

    def profile_length() -> int:
        return len(json.dumps(
            {"country_profile": profile},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ))

    while profile_length() > profile_max_chars:
        removable_field = next(
            (
                field
                for field in ("coverage", "known_gaps")
                if len(profile.get(field, [])) > 1
            ),
            None,
        )
        if removable_field is None:
            break
        profile[removable_field].pop()
        truncated_fields.add(removable_field)
        profile["truncated_fields"] = sorted(truncated_fields)

    if profile_length() > profile_max_chars:
        for field in ("known_gaps", "coverage"):
            if len(profile.get(field, [])) == 1:
                profile[field] = []
                truncated_fields.add(field)
                profile["truncated_fields"] = sorted(truncated_fields)
                if profile_length() <= profile_max_chars:
                    break
    return profile


def compact_bank_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Project canonical records into the bounded Stage-2 grounding shape."""

    if not isinstance(packet, dict) or packet.get("bank_status") != "ok":
        return {}
    sources = []
    for source in packet.get("sources", []):
        if not isinstance(source, dict):
            continue
        compact_source = {
            key: source[key]
            for key in (
                "source_id", "title", "organization", "publication_date",
                "publication_date_basis", "url",
            )
            if key in source and source[key] not in (None, "")
        }
        if compact_source.get("source_id"):
            sources.append(compact_source)

    evidence_records = []
    evidence_fields = (
        "evidence_id", "compact_statement", "evidence_status",
        "evidence_class", "analytical_role", "hazard_tags", "impact_tags",
        "sectors", "interaction_direction", "scenario", "time_horizons",
        "confidence", "uncertainty", "geographies", "affected_groups",
        "administrative_level", "ecological_level",
    )
    for record in packet.get("evidence_records", []):
        if not isinstance(record, dict):
            continue
        source_refs = [
            {
                key: ref[key]
                for key in ("source_id", "locator")
                if key in ref and ref[key] not in (None, "")
            }
            for ref in record.get("source_refs", [])
            if isinstance(ref, dict)
        ]
        compact_record = {
            key: record[key] for key in evidence_fields if key in record
        }
        compact_record["source_refs"] = source_refs
        compact_record["source_ids"] = list(dict.fromkeys(
            ref["source_id"] for ref in source_refs if ref.get("source_id")
        ))
        evidence_records.append(compact_record)

    pathway_fields = (
        "pathway_id", "compact_statement", "evidence_strength",
        "supporting_evidence_ids", "interaction_direction", "geographies",
        "affected_groups", "alternative_explanations", "uncertainty",
    )
    pathways = [
        {key: record[key] for key in pathway_fields if key in record}
        for record in packet.get("pathways", [])
        if isinstance(record, dict)
    ]
    profile = packet.get("country_profile")
    if not isinstance(profile, dict):
        profile = {
            key: packet[key]
            for key in ("coverage", "known_gaps")
            if key in packet
        }
    compact_profile = _compact_country_profile(profile)
    compact = {
        "content_version": packet.get("content_version"),
        "country_iso3": packet.get("country_iso3"),
        "sources": sources,
        "evidence_records": evidence_records,
        "pathways": pathways,
        "coverage_metadata_available": bool(compact_profile),
        "coverage_note": (
            "Country coverage metadata unavailable; selected records do not "
            "establish complete national or population coverage."
            if not compact_profile
            else
            "Profile coverage and known gaps do not establish complete "
            "national or population coverage."
        ),
        "pathway_coverage_note": (
            "An empty selected pathway list does not establish that no such "
            "pathways exist."
        ),
    }
    if compact_profile:
        compact["country_profile"] = compact_profile
    if packet.get("candidate_preview") is True:
        compact["candidate_preview"] = True
    if packet.get("limitations"):
        compact["limitations"] = list(packet["limitations"])
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


def select_bank_manifest(
    bank: ClimateBankLoad,
    *,
    country: str,
    country_scope: str,
    resolved_country_count: int,
    sector: str,
    project_signals: Any,
) -> dict[str, Any]:
    """Select a bounded canonical-ID manifest for one resolved country."""

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

    iso3 = resolved.get("iso3")
    if not isinstance(iso3, str):
        return _unavailable("bank_country_unavailable")
    evidence_ids = set(resolved.get("evidence_ids", []))
    pathway_ids = set(resolved.get("pathway_ids", []))
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
    expired_ids = expired_current_evidence_ids(bank, iso3)
    evidence_records = [
        item for item in evidence_records
        if item.get("evidence_id") not in expired_ids
    ]
    pathway_records = [
        item for item in pathway_records
        if not expired_ids.intersection(item.get("supporting_evidence_ids", []))
    ]
    if expired_ids and not evidence_records and not pathway_records:
        return _unavailable("bank_content_expired")
    evidence_index = {
        item["evidence_id"]: item
        for item in evidence_records
        if isinstance(item.get("evidence_id"), str)
    }
    source_index = {
        item["source_id"]: item
        for item in bank.release.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("source_id"), str)
    }
    signal_tokens = _tokens([project_signals, sector])
    release_year = _release_year(bank.release)

    ranked_pathways = _rank(
        _score_pathway(
            item,
            signal_tokens=signal_tokens,
            evidence_index=evidence_index,
            source_index=source_index,
            release_year=release_year,
        )
        for item in pathway_records
    )
    ranked_evidence = _rank(
        _score_evidence(
            item,
            signal_tokens=signal_tokens,
            source_index=source_index,
            release_year=release_year,
        )
        for item in evidence_records
    )

    selected: list[_Candidate] = []
    source_counts: dict[str, int] = {}
    physical_count = 0

    def try_add(candidate: _Candidate) -> bool:
        nonlocal physical_count
        if len(selected) >= CLIMATE_BANK_TARGET_ITEMS:
            return False
        if candidate.physical_baseline and physical_count >= 2:
            return False
        prospective = _rank([*selected, candidate])
        packet = materialize_bank_manifest(
            bank, _manifest(bank, resolved, prospective)
        )
        if (
            packet.get("bank_status") != "ok"
            or _compact_packet_length(packet) > CLIMATE_BANK_MAX_CHARS
        ):
            return False
        selected[:] = prospective
        source_id = candidate.primary_source_id
        if source_id:
            source_counts[source_id] = source_counts.get(source_id, 0) + 1
        if candidate.physical_baseline:
            physical_count += 1
        return True

    def add_fitting_candidates(
        candidates: list[_Candidate], limit: int
    ) -> None:
        added = 0
        deferred: list[_Candidate] = []
        for candidate in candidates:
            if added >= limit or len(selected) >= CLIMATE_BANK_TARGET_ITEMS:
                break
            source_id = candidate.primary_source_id
            if source_id and source_counts.get(source_id, 0) >= (
                _SOURCE_DIVERSITY_CAP
            ):
                deferred.append(candidate)
                continue
            if try_add(candidate):
                added += 1

        for candidate in deferred:
            if added >= limit or len(selected) >= CLIMATE_BANK_TARGET_ITEMS:
                break
            if try_add(candidate):
                added += 1

    add_fitting_candidates(ranked_pathways, limit=2)
    add_fitting_candidates(
        ranked_evidence,
        limit=CLIMATE_BANK_TARGET_ITEMS - len(selected),
    )
    if not any(item.kind == "evidence" for item in selected):
        # Keep at least one directly selected evidence item when a pathway's
        # supporting records leave no room for additional selection.
        selected.clear()
        source_counts.clear()
        physical_count = 0
        add_fitting_candidates(ranked_evidence, limit=1)
    if not selected:
        return _unavailable("bank_packet_too_large")
    return _manifest(bank, resolved, selected)
