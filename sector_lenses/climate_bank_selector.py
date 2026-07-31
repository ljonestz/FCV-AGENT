"""Deterministic project-relevant selection from a validated climate bank."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import re
from typing import Any, Iterable

from .climate_bank import ClimateBankLoad, materialize_bank_manifest


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


def _take_diverse(
    candidates: list[_Candidate],
    *,
    limit: int,
    source_counts: dict[str, int],
    physical_count: int = 0,
) -> list[_Candidate]:
    """Prefer source-diverse items, then fill only when alternatives run out."""

    selected: list[_Candidate] = []
    deferred: list[_Candidate] = []
    for candidate in candidates:
        if len(selected) >= limit:
            break
        if candidate.physical_baseline and physical_count >= 2:
            continue
        source_id = candidate.primary_source_id
        if source_id and source_counts.get(source_id, 0) >= _SOURCE_DIVERSITY_CAP:
            deferred.append(candidate)
            continue
        selected.append(candidate)
        if candidate.physical_baseline:
            physical_count += 1
        if source_id:
            source_counts[source_id] = source_counts.get(source_id, 0) + 1

    for candidate in deferred:
        if len(selected) >= limit:
            break
        if candidate.physical_baseline and physical_count >= 2:
            continue
        selected.append(candidate)
        if candidate.physical_baseline:
            physical_count += 1
        source_id = candidate.primary_source_id
        if source_id:
            source_counts[source_id] = source_counts.get(source_id, 0) + 1
    return selected


def _unavailable(code: str) -> dict[str, str]:
    return {"bank_status": "unavailable", "warning_code": code}


def _manifest(
    bank: ClimateBankLoad,
    country: dict[str, Any],
    selected: list[_Candidate],
) -> dict[str, Any]:
    return {
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
    return {
        "content_version": packet.get("content_version"),
        "country_iso3": packet.get("country_iso3"),
        "sources": sources,
        "evidence_records": evidence_records,
        "pathways": pathways,
    }


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

    source_counts: dict[str, int] = {}
    selected_pathways = _take_diverse(
        ranked_pathways,
        limit=min(2, CLIMATE_BANK_MAX_ITEMS),
        source_counts=source_counts,
    )
    evidence_limit = min(
        CLIMATE_BANK_TARGET_ITEMS - len(selected_pathways),
        CLIMATE_BANK_MAX_ITEMS - len(selected_pathways),
    )
    selected_evidence = _take_diverse(
        ranked_evidence,
        limit=max(0, evidence_limit),
        source_counts=source_counts,
    )
    selected = _rank([*selected_pathways, *selected_evidence])
    selected = selected[:CLIMATE_BANK_MAX_ITEMS]

    while True:
        manifest = _manifest(bank, resolved, selected)
        packet = materialize_bank_manifest(bank, manifest)
        if packet.get("bank_status") != "ok":
            return _unavailable(
                str(packet.get("warning_code") or "bank_manifest_invalid")
            )
        if _compact_packet_length(packet) <= CLIMATE_BANK_MAX_CHARS:
            return manifest
        if not selected:
            return _unavailable("bank_packet_too_large")
        selected.pop()
