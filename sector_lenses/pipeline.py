"""Runtime helpers for lens discovery, hidden diagnostics, and finding composition."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any, Iterable

from .models import LensActivationMode, LensRegistry


LENS_EVIDENCE_START = "%%%LENS_EVIDENCE_START%%%"
LENS_EVIDENCE_END = "%%%LENS_EVIDENCE_END%%%"
LENS_DIAGNOSTIC_START = "%%%LENS_DIAGNOSTIC_START%%%"
LENS_DIAGNOSTIC_END = "%%%LENS_DIAGNOSTIC_END%%%"
_VALID_MAPPING = re.compile(r"^(?:ost:(?:[1-9]|1[0-2])|dnh:[1-9]|shift:[A-D])$")
_VALID_STATUSES = {
    "addressed", "partially_addressed", "not_yet_addressed", "gap", "not_applicable",
}
_MATERIALITY_LEVELS = {"high", "medium", "low"}
_INTERACTION_DIRECTIONS = {
    "climate-fcv-on-project",
    "project-on-climate-fcv",
}


def _list_values(value: Any) -> list[Any]:
    """Return model-provided collection values without iterating scalars."""

    return list(value) if isinstance(value, (list, tuple)) else []


def _bounded_strings(value: Any, limit: int, length: int) -> list[str]:
    """Return bounded, non-empty strings from a model-provided collection."""

    return [
        str(item).strip()[:length]
        for item in _list_values(value)
        if str(item).strip()
    ][:limit]


def lens_catalogue(registry: LensRegistry) -> list[dict[str, Any]]:
    """Return selector-safe metadata for enabled modules only."""

    return [
        {
            "id": lens.id,
            "name": lens.metadata.name,
            "version": lens.version,
            "description": lens.metadata.description,
            "activation": lens.metadata.activation.value,
            "readout_sections": [
                {
                    "id": section.id,
                    "title": section.title,
                    "item_ids": list(section.item_ids),
                }
                for section in lens.readout_sections
            ],
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
        if lens.metadata.activation is not LensActivationMode.SUGGESTED:
            continue
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
            "evidence_requests": [
                str(value) for value in _list_values(
                    item.get("evidence_requests")
                ) if str(value).strip()
            ],
            "research_intents": [
                str(value) for value in _list_values(
                    item.get("research_intents")
                ) if str(value).strip()
            ],
        })
    return {"error": False, "message": "", "lenses": lenses}


def extract_lens_diagnostic(
    text: str,
    active_lens_ids: Iterable[str],
    source_ids_by_lens: dict[str, set[str]] | None = None,
    readout_schema_by_lens: dict[str, dict[str, set[str]]] | None = None,
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
        raw_materiality = str(item.get("materiality_level", "")).lower()
        materiality_level = ""
        if lens_id == "climate":
            materiality_level = (
                raw_materiality
                if raw_materiality in _MATERIALITY_LEVELS
                else "medium" if applicability == "material" else "low"
            )
        lens_sources = list(dict.fromkeys(
            str(value) for value in _list_values(item.get("source_ids"))
        ))[:10]
        if source_ids_by_lens is not None:
            lens_sources = [
                value for value in lens_sources
                if value in source_ids_by_lens.get(lens_id, set())
            ]
        declared_sections = (
            readout_schema_by_lens.get(lens_id, {})
            if readout_schema_by_lens is not None else {}
        )
        normalized_sections: list[dict[str, Any]] = []
        raw_sections = item.get("readout_sections", [])
        for raw_section in raw_sections if isinstance(raw_sections, list) else []:
            if not isinstance(raw_section, dict):
                continue
            section_id = str(raw_section.get("section_id", ""))
            allowed_items = declared_sections.get(section_id)
            if allowed_items is None:
                continue
            normalized_items: list[dict[str, Any]] = []
            raw_items = raw_section.get("items", [])
            for raw_item in raw_items if isinstance(raw_items, list) else []:
                if not isinstance(raw_item, dict):
                    continue
                item_id = str(raw_item.get("item_id", ""))
                status = str(raw_item.get("status", "potential"))
                if item_id not in allowed_items or status not in {
                    "supported", "potential", "not_material",
                }:
                    continue
                item_sources = list(dict.fromkeys(
                    str(value) for value in _list_values(
                        raw_item.get("source_ids")
                    )
                ))[:10]
                if source_ids_by_lens is not None:
                    item_sources = [
                        value for value in item_sources
                        if value in source_ids_by_lens.get(lens_id, set())
                    ]
                normalized_items.append({
                    "item_id": item_id,
                    "status": status,
                    "mechanism": str(raw_item.get("mechanism", "")).strip()[:500],
                    "project_contribution": str(
                        raw_item.get("project_contribution", "")
                    ).strip()[:700],
                    "strengthening_action": str(
                        raw_item.get("strengthening_action", "")
                    ).strip()[:700],
                    "evidence": [
                        str(value).strip()[:500]
                        for value in _list_values(raw_item.get("evidence"))
                        if str(value).strip()
                    ][:5],
                    "evidence_gap": str(raw_item.get("evidence_gap", "")).strip()[:500],
                    "trade_off": str(raw_item.get("trade_off", "")).strip()[:500],
                    "source_ids": item_sources,
                })
                if len(normalized_items) >= 3:
                    break
            if normalized_items:
                normalized_sections.append({
                    "section_id": section_id,
                    "items": normalized_items,
                })
        normalized_interactions: list[dict[str, Any]] = []
        if lens_id == "climate":
            seen_directions: set[str] = set()
            for raw_interaction in _list_values(item.get("interaction_readout")):
                if not isinstance(raw_interaction, dict):
                    continue
                direction_id = str(raw_interaction.get("direction_id", ""))
                if (
                    direction_id not in _INTERACTION_DIRECTIONS
                    or direction_id in seen_directions
                ):
                    continue
                seen_directions.add(direction_id)
                interaction_sources = list(dict.fromkeys(_bounded_strings(
                    raw_interaction.get("source_ids"), 10, 200
                )))
                if source_ids_by_lens is not None:
                    interaction_sources = [
                        source_id for source_id in interaction_sources
                        if source_id in source_ids_by_lens.get(lens_id, set())
                    ]
                normalized_interactions.append({
                    "direction_id": direction_id,
                    "summary": str(
                        raw_interaction.get("summary", "")
                    ).strip()[:700],
                    "mechanisms": _bounded_strings(
                        raw_interaction.get("mechanisms"), 3, 350
                    ),
                    "project_implications": _bounded_strings(
                        raw_interaction.get("project_implications"), 3, 350
                    ),
                    "positive_effects": _bounded_strings(
                        raw_interaction.get("positive_effects"), 3, 350
                    ),
                    "adverse_effects": _bounded_strings(
                        raw_interaction.get("adverse_effects"), 3, 350
                    ),
                    "evidence": _bounded_strings(
                        raw_interaction.get("evidence"), 5, 500
                    ),
                    "evidence_gap": str(
                        raw_interaction.get("evidence_gap", "")
                    ).strip()[:500],
                    "source_ids": interaction_sources,
                })

        normalized_additional: list[dict[str, Any]] = []
        additional_by_section: dict[str, int] = {}
        if lens_id == "climate":
            for raw_pathway in _list_values(item.get("additional_pathways")):
                if not isinstance(raw_pathway, dict):
                    continue
                section_id = str(raw_pathway.get("section_id", ""))
                title = str(raw_pathway.get("title", "")).strip()[:200]
                status = str(raw_pathway.get("status", ""))
                contribution = str(
                    raw_pathway.get("project_contribution", "")
                ).strip()[:700]
                strengthening = str(
                    raw_pathway.get("strengthening_action", "")
                ).strip()[:700]
                evidence = _bounded_strings(raw_pathway.get("evidence"), 5, 500)
                if (
                    section_id not in declared_sections
                    or additional_by_section.get(section_id, 0) >= 2
                    or not title
                    or status not in {"supported", "potential"}
                    or not contribution
                    or not strengthening
                    or not evidence
                ):
                    continue
                pathway_sources = list(dict.fromkeys(_bounded_strings(
                    raw_pathway.get("source_ids"), 10, 200
                )))
                if source_ids_by_lens is not None:
                    pathway_sources = [
                        source_id for source_id in pathway_sources
                        if source_id in source_ids_by_lens.get(lens_id, set())
                    ]
                normalized_additional.append({
                    "section_id": section_id,
                    "title": title,
                    "status": status,
                    "mechanism": str(
                        raw_pathway.get("mechanism", "")
                    ).strip()[:500],
                    "project_contribution": contribution,
                    "strengthening_action": strengthening,
                    "evidence": evidence,
                    "evidence_gap": str(
                        raw_pathway.get("evidence_gap", "")
                    ).strip()[:500],
                    "trade_off": str(
                        raw_pathway.get("trade_off", "")
                    ).strip()[:500],
                    "source_ids": pathway_sources,
                })
                additional_by_section[section_id] = (
                    additional_by_section.get(section_id, 0) + 1
                )
        normalized_other: list[dict[str, str]] = []
        raw_other = item.get("other_pathways", [])
        for pathway in raw_other if isinstance(raw_other, list) else []:
            if not isinstance(pathway, dict):
                continue
            status = str(pathway.get("status", ""))
            name = str(pathway.get("pathway", "")).strip()[:200]
            if not name or status not in {"potential", "not_material"}:
                continue
            normalized_other.append({
                "pathway": name,
                "status": status,
                "reason": str(pathway.get("reason", "")).strip()[:500],
            })
            if len(normalized_other) >= 10:
                break
        normalized_lens = {
            "lens_id": lens_id,
            "applicability": applicability,
            "materiality_summary": str(
                item.get("materiality_summary", "")
            ).strip()[:600],
            "analysis_emphasis": [
                str(value).strip()[:100]
                for value in _list_values(item.get("analysis_emphasis"))
                if str(value).strip()
            ][:5],
            "evidence": [
                str(value).strip()[:500]
                for value in _list_values(item.get("evidence"))
                if str(value).strip()
            ][:5],
            "source_ids": lens_sources,
            "readout_sections": normalized_sections,
            "other_pathways": normalized_other,
        }
        if lens_id == "climate":
            normalized_lens.update({
                "materiality_level": materiality_level,
                "interaction_readout": normalized_interactions,
                "additional_pathways": normalized_additional,
            })
        lenses.append(normalized_lens)

    findings: list[dict[str, Any]] = []
    truncated = len(raw_findings) > 20
    for raw in raw_findings[:20]:
        if not isinstance(raw, dict):
            continue
        lens_ids = [
            value for value in _list_values(raw.get("lens_ids"))
            if value in active
        ]
        mappings = [
            value for value in _list_values(raw.get("core_mappings"))
            if _VALID_MAPPING.match(str(value))
        ]
        if not lens_ids or not mappings:
            continue
        status = str(raw.get("status", "not_yet_addressed"))
        if status not in _VALID_STATUSES:
            status = "not_yet_addressed"
        evidence = [
            str(value).strip()[:500]
            for value in _list_values(raw.get("evidence"))
            if str(value).strip()
        ][:5]
        source_ids = list(dict.fromkeys(
            str(value) for value in _list_values(raw.get("source_ids"))
        ))[:10]
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
    readout_schema_by_lens: dict[str, dict[str, set[str]]] | None = None,
) -> dict[str, Any]:
    """Apply the model-output validator to a diagnostic received from a client/session."""

    serialized = json.dumps(payload or {}, ensure_ascii=False)
    wrapped = LENS_DIAGNOSTIC_START + serialized + LENS_DIAGNOSTIC_END
    return extract_lens_diagnostic(
        wrapped,
        active_lens_ids,
        source_ids_by_lens,
        readout_schema_by_lens,
    )


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
