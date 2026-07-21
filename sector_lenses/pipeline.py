"""Runtime helpers for lens discovery, hidden diagnostics, and finding composition."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any, Iterable

from .models import LensRegistry


LENS_EVIDENCE_START = "%%%LENS_EVIDENCE_START%%%"
LENS_EVIDENCE_END = "%%%LENS_EVIDENCE_END%%%"
LENS_DIAGNOSTIC_START = "%%%LENS_DIAGNOSTIC_START%%%"
LENS_DIAGNOSTIC_END = "%%%LENS_DIAGNOSTIC_END%%%"
_VALID_MAPPING = re.compile(r"^(?:ost:(?:[1-9]|1[0-2])|dnh:[1-9]|shift:[A-D])$")
_VALID_STATUSES = {
    "addressed", "partially_addressed", "not_yet_addressed", "gap", "not_applicable",
}


def lens_catalogue(registry: LensRegistry) -> list[dict[str, Any]]:
    """Return selector-safe metadata for enabled modules only."""

    return [
        {
            "id": lens.id,
            "name": lens.metadata.name,
            "version": lens.version,
            "description": lens.metadata.description,
            "aliases": list(lens.metadata.aliases),
            "compatibility": {
                "compatible_with": list(lens.compatibility.compatible_with),
                "incompatible_with": list(lens.compatibility.incompatible_with),
            },
        }
        for lens in registry.enabled_lenses
    ]


def detect_lens_suggestions(text: str, registry: LensRegistry) -> list[dict[str, Any]]:
    """Rank deterministic materiality signals; extraction or no-match returns an empty list."""

    if not isinstance(text, str) or not text.strip():
        return []
    haystack = text.casefold()
    suggestions: list[dict[str, Any]] = []
    for lens in registry.enabled_lenses:
        matches: list[str] = []
        occurrences = 0
        seen_signals: set[str] = set()
        keyword_signals = [(value, False) for value in (*lens.detection.keywords, *lens.metadata.aliases)]
        code_signals = [(value, True) for value in lens.detection.sector_codes]
        for keyword, is_code in (*keyword_signals, *code_signals):
            normalized = keyword.strip().casefold()
            if not normalized or normalized in seen_signals:
                continue
            seen_signals.add(normalized)
            count = (
                len(re.findall(rf"\b{re.escape(normalized)}\b", haystack))
                if is_code else haystack.count(normalized)
            )
            if count:
                matches.append(keyword)
                occurrences += count
        unique_matches = list(dict.fromkeys(matches))
        if not unique_matches:
            continue
        material = len(unique_matches) >= lens.detection.threshold or occurrences >= lens.detection.threshold
        suggestions.append(
            {
                "lens_id": lens.id,
                "version": lens.version,
                "confidence": "high" if material else "uncertain",
                "selected_by_default": material,
                "matched_signals": unique_matches,
                "score": len(unique_matches) + min(occurrences, 5) / 10,
            }
        )
    suggestions.sort(key=lambda item: (-item["selected_by_default"], -item["score"], item["lens_id"]))
    return suggestions


def strip_lens_blocks(text: str) -> str:
    """Remove hidden evidence and diagnostic blocks from user-facing prose."""

    cleaned = text
    for start, end in (
        (LENS_EVIDENCE_START, LENS_EVIDENCE_END),
        (LENS_DIAGNOSTIC_START, LENS_DIAGNOSTIC_END),
    ):
        cleaned = re.sub(
            re.escape(start) + r".*?(?:" + re.escape(end) + r"|$)",
            "",
            cleaned,
            flags=re.DOTALL,
        )
    return cleaned.strip()


def _error_diagnostic(message: str) -> dict[str, Any]:
    return {"error": True, "message": message, "lenses": [], "findings": []}


def extract_lens_evidence(text: str, active_lens_ids: Iterable[str]) -> dict[str, Any]:
    """Parse the hidden Stage-1 evidence plan while ignoring non-active lens IDs."""

    match = re.search(
        re.escape(LENS_EVIDENCE_START) + r"(.*?)" + re.escape(LENS_EVIDENCE_END),
        text or "",
        re.DOTALL,
    )
    if not match:
        return {"error": True, "message": "Lens evidence block was not produced.", "lenses": []}
    try:
        data = json.loads(match.group(1).strip())
    except (json.JSONDecodeError, TypeError, ValueError):
        return {"error": True, "message": "Lens evidence block was not valid JSON.", "lenses": []}
    active = set(active_lens_ids)
    raw_lenses = data.get("lenses", []) if isinstance(data, dict) else []
    lenses = []
    for item in raw_lenses if isinstance(raw_lenses, list) else []:
        if not isinstance(item, dict) or item.get("lens_id") not in active:
            continue
        lenses.append({
            "lens_id": item["lens_id"],
            "evidence_requests": [str(value) for value in item.get("evidence_requests", []) if str(value).strip()],
            "research_intents": [str(value) for value in item.get("research_intents", []) if str(value).strip()],
        })
    return {"error": False, "message": "", "lenses": lenses}


def extract_lens_diagnostic(
    text: str,
    active_lens_ids: Iterable[str],
    source_ids_by_lens: dict[str, set[str]] | None = None,
) -> dict[str, Any]:
    """Parse and validate the hidden Stage-2 lens diagnostic without failing core analysis."""

    match = re.search(
        re.escape(LENS_DIAGNOSTIC_START) + r"(.*?)" + re.escape(LENS_DIAGNOSTIC_END),
        text or "",
        re.DOTALL,
    )
    if not match:
        return _error_diagnostic("Lens diagnostic block was not produced.")
    try:
        data = json.loads(match.group(1).strip())
    except (json.JSONDecodeError, TypeError, ValueError):
        return _error_diagnostic("Lens diagnostic block was not valid JSON.")
    if not isinstance(data, dict):
        return _error_diagnostic("Lens diagnostic must be an object.")

    active = set(active_lens_ids)
    raw_lenses = data.get("lenses", [])
    raw_findings = data.get("findings", [])
    if not isinstance(raw_lenses, list) or not isinstance(raw_findings, list):
        return _error_diagnostic("Lens diagnostic lists were malformed.")

    lenses = []
    for item in raw_lenses:
        if not isinstance(item, dict) or item.get("lens_id") not in active:
            continue
        lens_id = item["lens_id"]
        applicability = str(item.get("applicability", "possible"))
        if applicability not in {"material", "possible", "not_applicable"}:
            applicability = "possible"
        lens_sources = list(dict.fromkeys(
            str(value) for value in item.get("source_ids", [])
        ))[:10]
        if source_ids_by_lens is not None:
            lens_sources = [
                value for value in lens_sources
                if value in source_ids_by_lens.get(lens_id, set())
            ]
        lenses.append({
            "lens_id": lens_id,
            "applicability": applicability,
            "evidence": [
                str(value).strip()[:500]
                for value in item.get("evidence", []) if str(value).strip()
            ][:5],
            "source_ids": lens_sources,
        })

    findings: list[dict[str, Any]] = []
    truncated = len(raw_findings) > 20
    for raw in raw_findings[:20]:
        if not isinstance(raw, dict):
            continue
        lens_ids = [value for value in raw.get("lens_ids", []) if value in active]
        mappings = [value for value in raw.get("core_mappings", []) if _VALID_MAPPING.match(str(value))]
        if not lens_ids or not mappings:
            continue
        status = str(raw.get("status", "not_yet_addressed"))
        if status not in _VALID_STATUSES:
            status = "not_yet_addressed"
        evidence = [str(value).strip()[:500] for value in raw.get("evidence", []) if str(value).strip()][:5]
        source_ids = list(dict.fromkeys(str(value) for value in raw.get("source_ids", [])))[:10]
        if source_ids_by_lens is not None:
            allowed_sources = set().union(*(source_ids_by_lens.get(lens_id, set()) for lens_id in lens_ids))
            source_ids = [value for value in source_ids if value in allowed_sources]
        mechanism = str(raw.get("mechanism", "")).strip()[:200]
        geography = str(raw.get("geography", "")).strip()[:200]
        action_target = str(raw.get("action_target", "")).strip()[:200]
        if not mechanism or not geography or not action_target:
            continue
        findings.append(
            {
                "lens_ids": list(dict.fromkeys(lens_ids)),
                "evidence": evidence,
                "status": status,
                "source_ids": source_ids,
                "core_mappings": list(dict.fromkeys(str(value) for value in mappings))[:5],
                "mechanism": mechanism,
                "geography": geography,
                "action_target": action_target,
            }
        )
    return {"error": False, "message": "", "lenses": lenses, "findings": findings, "truncated": truncated}


def normalize_lens_diagnostic(
    payload: dict[str, Any] | None,
    active_lens_ids: Iterable[str],
    source_ids_by_lens: dict[str, set[str]] | None = None,
) -> dict[str, Any]:
    """Apply the model-output validator to a diagnostic received from a client/session."""

    serialized = json.dumps(payload or {}, ensure_ascii=False)
    wrapped = LENS_DIAGNOSTIC_START + serialized + LENS_DIAGNOSTIC_END
    return extract_lens_diagnostic(wrapped, active_lens_ids, source_ids_by_lens)


def _extend_unique(target: list[str], values: Iterable[Any]) -> None:
    for value in values:
        string = str(value)
        if string and string not in target:
            target.append(string)


def merge_lens_findings(findings: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deterministically merge overlapping actions while preserving provenance."""

    merged: list[dict[str, Any]] = []
    ordered = sorted(
        (deepcopy(finding) for finding in findings),
        key=lambda item: (
            str(item.get("mechanism", "")).strip().casefold(),
            str(item.get("geography", "")).strip().casefold(),
            str(item.get("action_target", "")).strip().casefold(),
            tuple(sorted(str(value) for value in item.get("core_mappings", []))),
            tuple(sorted(str(value) for value in item.get("lens_ids", []))),
        ),
    )
    severity = {"not_applicable": 0, "addressed": 1, "partially_addressed": 2, "not_yet_addressed": 3, "gap": 4}
    for finding in ordered:
        mappings = set(str(value) for value in finding.get("core_mappings", []))
        base_key = (
            str(finding.get("mechanism", "")).strip().casefold(),
            str(finding.get("geography", "")).strip().casefold(),
            str(finding.get("action_target", "")).strip().casefold(),
        )
        matches = [
            item for item in merged
            if item["_base_key"] == base_key
            and mappings.intersection(item.get("core_mappings", []))
        ]
        if not matches:
            current = deepcopy(finding)
            current["_base_key"] = base_key
            current["mechanism"], current["geography"], current["action_target"] = base_key
            for field in ("lens_ids", "evidence", "source_ids", "core_mappings"):
                current[field] = []
            merged.append(current)
        else:
            current = matches[0]
            for extra in matches[1:]:
                for field in ("lens_ids", "evidence", "source_ids", "core_mappings"):
                    _extend_unique(current[field], extra.get(field, []))
                if severity.get(extra.get("status"), 0) > severity.get(current.get("status"), 0):
                    current["status"] = extra.get("status")
                merged.remove(extra)
        for field in ("lens_ids", "evidence", "source_ids", "core_mappings"):
            _extend_unique(current[field], finding.get(field, []))
        if severity.get(finding.get("status"), 0) > severity.get(current.get("status"), 0):
            current["status"] = finding.get("status")
    for item in merged:
        item.pop("_base_key", None)
        for field in ("lens_ids", "evidence", "source_ids", "core_mappings"):
            item[field] = sorted(set(item.get(field, [])), key=str.casefold)
    return sorted(merged, key=lambda item: (
        item.get("mechanism", ""), item.get("geography", ""), item.get("action_target", ""),
        tuple(item.get("core_mappings", [])),
    ))
