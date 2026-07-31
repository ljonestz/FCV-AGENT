"""Merge reviewed bank evidence and live Climate-FCV research safely."""

from __future__ import annotations

from copy import deepcopy
import json
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .climate_bank_selector import (
    CLIMATE_BANK_MAX_CHARS,
    compact_bank_packet,
)


CLIMATE_LIVE_TARGET_CLAIMS = 4
CLIMATE_LIVE_MAX_CLAIMS = 6
CLIMATE_COMBINED_MAX_CHARS = 12_000

_CONFLICT_FIELDS = {
    "conflicts",
    "conflicting_evidence",
    "conflicts_with",
    "has_conflicting_evidence",
}


def _dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [deepcopy(item) for item in value if isinstance(item, dict)]


def _compact_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _normalized_url(value: Any) -> str:
    """Return a stable URL key without changing the reported source URL."""

    if not isinstance(value, str) or not value.strip():
        return ""
    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        return value.strip().casefold().rstrip("/")
    hostname = (parsed.hostname or "").casefold()
    if not parsed.scheme or not hostname:
        return value.strip().casefold().rstrip("/")
    try:
        port = parsed.port
    except ValueError:
        return value.strip().casefold().rstrip("/")
    if port and not (
        (parsed.scheme.casefold() == "https" and port == 443)
        or (parsed.scheme.casefold() == "http" and port == 80)
    ):
        hostname = f"{hostname}:{port}"
    path = re.sub(r"/+", "/", parsed.path or "").rstrip("/")
    return urlunsplit(
        (
            parsed.scheme.casefold(),
            hostname,
            path,
            parsed.query,
            "",
        )
    )


def _source_id(source: dict[str, Any]) -> str:
    value = source.get("source_id", source.get("id", ""))
    return str(value).strip()


def _deduplicate_sources(
    bank_sources: list[dict[str, Any]],
    live_sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    combined: list[dict[str, Any]] = []
    indexes: dict[str, int] = {}
    for provenance, sources in (
        ("bank", bank_sources),
        ("research", live_sources),
    ):
        for source in sources:
            source_id = _source_id(source)
            url_key = _normalized_url(source.get("url"))
            key = f"url:{url_key}" if url_key else f"{provenance}:{source_id}"
            if key not in indexes:
                entry = deepcopy(source)
                entry["source_aliases"] = [source_id] if source_id else []
                entry["provenance"] = [provenance]
                indexes[key] = len(combined)
                combined.append(entry)
                continue
            entry = combined[indexes[key]]
            if source_id and source_id not in entry["source_aliases"]:
                entry["source_aliases"].append(source_id)
            if provenance not in entry["provenance"]:
                entry["provenance"].append(provenance)
    return combined


def _has_conflict(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in _CONFLICT_FIELDS and bool(item):
                return True
            if _has_conflict(item):
                return True
    elif isinstance(value, list):
        return any(_has_conflict(item) for item in value)
    return False


def _bounded_bank_projection(bank: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """Use the canonical compact projection and drop whole items to fit."""

    if bank.get("bank_status") != "ok":
        return {}, ""
    compact_input = deepcopy(bank)
    projection = compact_bank_packet(compact_input)
    if not projection:
        return {}, ""

    bounded = {
        "content_version": projection.get("content_version"),
        "country_iso3": projection.get("country_iso3"),
        "sources": [],
        "evidence_records": [],
        "pathways": [],
    }
    for field in ("sources", "evidence_records", "pathways"):
        items = projection.get(field)
        for item in items if isinstance(items, list) else []:
            candidate = deepcopy(bounded)
            candidate[field].append(item)
            if len(_compact_json(candidate)) > CLIMATE_BANK_MAX_CHARS:
                continue
            bounded = candidate
    serialized = _compact_json(bounded)
    if not bounded["evidence_records"] and not bounded["pathways"]:
        return {}, ""
    return bounded, serialized


def _bounded_live_projection(
    sources: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    *,
    remaining: int,
) -> dict[str, Any]:
    """Budget claims together with only the sources that support them."""

    projection: dict[str, Any] = {"sources": [], "claims": []}
    source_index = {
        _source_id(source): source
        for source in sources
        if _source_id(source)
    }
    included_source_ids: set[str] = set()
    for claim in claims:
        referenced_ids = [
            source_id
            for source_id in claim.get("source_ids", [])
            if isinstance(source_id, str) and source_id in source_index
        ]
        candidate = deepcopy(projection)
        for source_id in referenced_ids:
            if source_id in included_source_ids:
                continue
            candidate["sources"].append(deepcopy(source_index[source_id]))
        candidate["claims"].append(deepcopy(claim))
        if len(_compact_json(candidate)) > remaining:
            continue
        projection = candidate
        included_source_ids.update(referenced_ids)
    return projection


def merge_climate_grounding(
    bank_packet: Any,
    research_bundle: Any,
) -> dict[str, Any]:
    """Merge canonical and live evidence with provenance and prompt budgets.

    Full canonical source records remain available for report provenance. Only
    the compact bank projection is placed in ``prompt_context``.
    """

    bank = bank_packet if isinstance(bank_packet, dict) else {}
    research = research_bundle if isinstance(research_bundle, dict) else {}
    bank_sources = _dict_list(bank.get("sources"))
    bank_evidence = _dict_list(bank.get("evidence_records"))
    bank_pathways = _dict_list(bank.get("pathways"))
    live_sources = _dict_list(research.get("sources"))
    live_claims = _dict_list(research.get("claims"))[
        :CLIMATE_LIVE_MAX_CLAIMS
    ]

    bank_projection, bank_context = _bounded_bank_projection(bank)
    has_bank = bool(bank_projection)
    has_research = bool(live_claims)
    if has_bank and has_research:
        state = "bank+research"
    elif has_bank:
        state = "bank-only"
    elif has_research:
        state = "research-only"
    else:
        state = "thematic-only"

    prompt_payload: dict[str, Any] = {}
    if has_bank:
        prompt_payload["bank"] = bank_projection
    if has_research:
        base_size = len(_compact_json(prompt_payload)) if prompt_payload else 0
        remaining = max(CLIMATE_COMBINED_MAX_CHARS - base_size - 20, 0)
        live_projection = _bounded_live_projection(
            live_sources,
            live_claims,
            remaining=remaining,
        )
        if live_projection["claims"]:
            prompt_payload["research"] = live_projection
        else:
            has_research = False
            state = "bank-only" if has_bank else "thematic-only"
    prompt_context = _compact_json(prompt_payload) if prompt_payload else ""
    if len(prompt_context) > CLIMATE_COMBINED_MAX_CHARS:
        prompt_context = ""
        state = "thematic-only"

    sources = _deduplicate_sources(bank_sources, live_sources)
    log_counts = {
        "bank_sources": len(bank_sources),
        "bank_evidence_records": len(bank_evidence),
        "bank_pathways": len(bank_pathways),
        "live_sources": len(live_sources),
        "live_claims": len(live_claims),
        "deduplicated_sources": len(sources),
    }
    return {
        "state": state,
        "warning_code": str(
            bank.get("warning_code")
            or research.get("warning_code")
            or research.get("code")
            or ""
        ),
        "content_version": bank.get("content_version"),
        "country_iso3": bank.get("country_iso3"),
        "research_status": research.get("status", "failed"),
        "bank_sources": bank_sources,
        "live_sources": live_sources,
        "sources": sources,
        "bank_evidence_records": bank_evidence,
        "bank_pathways": bank_pathways,
        "live_claims": live_claims,
        "prompt_context": prompt_context,
        "bank_character_count": len(bank_context),
        "combined_character_count": len(prompt_context),
        "selected_item_count": len(bank_evidence) + len(bank_pathways),
        "has_conflicting_evidence": _has_conflict(
            [bank_evidence, bank_pathways, live_claims]
        ),
        "log_counts": log_counts,
    }
