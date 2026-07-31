"""Runtime helpers for lens discovery, hidden diagnostics, and finding composition."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any, Iterable

import climate_question_bank

from .climate_native import (
    CLIMATE_NATIVE_SCHEMA_VERSION,
    CLIMATE_REQUIRED_DIRECTIONS,
)
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
_INTERACTION_DIRECTIONS = CLIMATE_REQUIRED_DIRECTIONS
_CLIMATE_TIME_HORIZONS = {
    "current-near-term",
    "project-lifetime",
    "asset-system-lifetime",
}
_CLIMATE_CONFIDENCE_LEVELS = {"high", "medium", "low"}
_CLIMATE_CLAIM_ID = re.compile(r"^climate-claim-[1-9][0-9]?$")
_CLIMATE_BANK_IDS = {
    item["id"] for item in climate_question_bank.CLIMATE_QUESTION_BANK
}

# Finding IDs look like "<slug>-finding-<n>". Validate with two non-overlapping
# fullmatch checks split on the literal marker rather than one pattern whose
# "[a-z0-9-]*" overlaps the following "-finding-" literal — the overlap makes the
# single-regex form backtrack in polynomial time on hostile input
# (CodeQL py/polynomial-redos). Each check below is linear.
_FINDING_SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")
_FINDING_NUM = re.compile(r"[1-9][0-9]?")


def _is_valid_finding_id(value: str) -> bool:
    marker = "-finding-"
    idx = value.rfind(marker)
    if idx <= 0:
        return False
    return bool(_FINDING_SLUG.fullmatch(value[:idx])) and bool(
        _FINDING_NUM.fullmatch(value[idx + len(marker):])
    )
_CLIMATE_REFLECTION_KEYS = {
    "cq1_interaction", "cq2_maladaptation", "cq3_dividends",
    "cq4_inclusion", "cq5_institutions", "cq6_adaptive",
}
_CLIMATE_INTEGRATION_LEVELS = {"well_integrated", "partly_integrated", "weakly_integrated", "insufficient_evidence"}

# 6-tier display scale (matches the default app gauge labels in index.html).
_CLIMATE_INTEGRATION_RATINGS = (
    "Extremely Low", "Very Low", "Low",
    "Adequate", "Well Embedded", "Very Well Embedded",
)


def climate_integration_rating(value: Any) -> str:
    """Return a valid 6-tier rating label, or '' if absent/invalid."""
    raw = str(value or "").strip()
    return raw if raw in _CLIMATE_INTEGRATION_RATINGS else ""


def _normalize_climate_sw(value: Any) -> list[dict[str, Any]]:
    """Validate the structured strengths/weaknesses list for the full-detail block.

    Each entry: {side: strength|gap, title (<=160), text (<=600)}. Up to 4 per side.
    """
    strengths: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for raw in _list_values(value):
        if not isinstance(raw, dict):
            continue
        side = str(raw.get("side", "")).strip().lower()
        title = str(raw.get("title", "")).strip()[:160]
        text = str(raw.get("text", "")).strip()[:600]
        if side not in {"strength", "gap"} or not title:
            continue
        entry = {"side": side, "title": title, "text": text}
        bucket = strengths if side == "strength" else gaps
        if len(bucket) < 4:
            bucket.append(entry)
    return strengths + gaps


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


def _normalize_climate_baseline(value: Any) -> dict[str, Any]:
    """Return the bounded FCV baseline embedded in a Climate diagnostic."""

    raw = value if isinstance(value, dict) else {}
    trail: list[dict[str, Any]] = []
    for item in _list_values(raw.get("evidence_trail")):
        if not isinstance(item, dict):
            continue
        claim = str(item.get("claim", "")).strip()[:500]
        project_anchor = str(
            item.get("project_anchor", "")
        ).strip()[:240]
        if claim and project_anchor:
            trail.append({
                "claim": claim,
                "source_ids": _bounded_strings(
                    item.get("source_ids"), 4, 100
                ),
                "project_anchor": project_anchor,
            })
        if len(trail) >= 6:
            break
    return {
        "sensitivity_rating": str(
            raw.get("sensitivity_rating", "")
        ).strip()[:80],
        "responsiveness_rating": str(
            raw.get("responsiveness_rating", "")
        ).strip()[:80],
        "sensitivity_reasoning": str(
            raw.get("sensitivity_reasoning", "")
        ).strip()[:900],
        "responsiveness_reasoning": str(
            raw.get("responsiveness_reasoning", "")
        ).strip()[:900],
        "evidence_trail": trail,
    }


def _normalize_operating_context(value: Any) -> dict[str, str]:
    """Return bounded Climate and FCV operating-context narratives."""

    raw = value if isinstance(value, dict) else {}
    return {
        key: str(raw.get(key, "")).strip()[:1400]
        for key in ("fcv_setting", "climate_setting", "intersection")
    }


def _normalize_supplementary_questions(
    value: Any,
) -> list[dict[str, str]]:
    """Keep up to four bounded questions declared by the current bank."""

    result: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for raw in _list_values(value):
        if not isinstance(raw, dict):
            continue
        question_id = str(raw.get("question_id", "")).strip()
        text = str(raw.get("text", "")).strip()[:1800]
        if (
            question_id not in _CLIMATE_BANK_IDS
            or question_id in seen_ids
            or not text
        ):
            continue
        result.append({
            "question_id": question_id,
            "title": str(raw.get("title", "")).strip()[:200],
            "status_cue": _concise_status_cue(raw.get("status_cue", "")),
            "source": str(raw.get("source", "")).strip()[:160],
            "text": text,
        })
        seen_ids.add(question_id)
        if len(result) >= 4:
            break
    return result


def _normalize_climate_pathways(
    value: Any,
    direction_id: str,
) -> list[dict[str, Any]]:
    """Keep only bounded, project-specific Climate causal pathways."""

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    pathway_id_pattern = re.compile(
        rf"^{re.escape(direction_id)}-[1-4]$"
    )
    for raw in _list_values(value):
        if not isinstance(raw, dict):
            continue
        pathway_id = str(raw.get("pathway_id", "")).strip()
        if (
            not pathway_id_pattern.fullmatch(pathway_id)
            or pathway_id in seen_ids
        ):
            continue
        pressure = str(raw.get("pressure", "")).strip()[:300]
        mechanism = str(raw.get("mechanism", "")).strip()[:500]
        project_implication = str(
            raw.get("project_implication", "")
        ).strip()[:600]
        design_response = str(raw.get("design_response", "")).strip()[:600]
        project_elements = _bounded_strings(
            raw.get("project_elements"), 4, 180
        )
        geographies = _bounded_strings(raw.get("geographies"), 4, 160)
        affected_groups = _bounded_strings(
            raw.get("affected_groups"), 4, 160
        )
        systems_or_assets = _bounded_strings(
            raw.get("systems_or_assets"), 4, 180
        )
        horizons = [
            item
            for item in _bounded_strings(raw.get("time_horizons"), 3, 40)
            if item in _CLIMATE_TIME_HORIZONS
        ]
        claim_ids = [
            item
            for item in _bounded_strings(
                raw.get("research_claim_ids"), 4, 80
            )
            if _CLIMATE_CLAIM_ID.fullmatch(item)
        ]
        confidence = str(raw.get("confidence", "")).strip().lower()
        evidence_gap = str(raw.get("evidence_gap", "")).strip()[:500]
        if (
            not pressure
            or not mechanism
            or not project_implication
            or not design_response
            or not project_elements
            or not (geographies or affected_groups or systems_or_assets)
            or not horizons
            or not (claim_ids or evidence_gap)
            or confidence not in _CLIMATE_CONFIDENCE_LEVELS
        ):
            continue
        normalized.append({
            "pathway_id": pathway_id,
            "pressure": pressure,
            "mechanism": mechanism,
            "project_implication": project_implication,
            "design_response": design_response,
            "project_elements": project_elements,
            "geographies": geographies,
            "affected_groups": affected_groups,
            "systems_or_assets": systems_or_assets,
            "time_horizons": horizons,
            "research_claim_ids": claim_ids,
            "confidence": confidence,
            "evidence_gap": evidence_gap,
        })
        seen_ids.add(pathway_id)
        if len(normalized) == 4:
            break
    return normalized


# Models frequently emit machine-token status cues (e.g. "material_gap",
# "unaddressed") despite the prompt asking for soft plain-language phrasing.
# Soften deterministically at the parse layer so live HTML, shared HTML, and
# DOCX all render human-readable chips — never a raw snake_case enum token.
_STATUS_CUE_SOFT_MAP = {
    "material_gap": "material gap",
    "gap": "gap",
    "partial": "partial gap",
    "partial_gap": "partial gap",
    "unaddressed": "not yet addressed",
    "not_addressed": "not yet addressed",
    "unspecified": "not yet specified",
    "not_specified": "not yet specified",
    "addressed": "recognised",
    "well_addressed": "well recognised",
    "recognised": "recognised",
    "recognized": "recognised",
    "well_integrated": "well recognised",
    "partly_integrated": "partially recognised",
    "weakly_integrated": "weak",
    "weak": "weak",
    "strong": "strong",
    "strength": "strong",
    "unclaimed": "unclaimed opportunity",
    "unclaimed_opportunity": "unclaimed opportunity",
    "opportunity": "unclaimed opportunity",
    "insufficient_evidence": "insufficient evidence",
    "ok": "recognised",
}


def _soften_status_cue(value: Any) -> str:
    """Map a machine-token status cue to soft plain-language phrasing.

    Already-soft cues (e.g. "partial gap", "strong") pass through unchanged;
    snake_case tokens are mapped or, as a fallback, de-underscored.
    """

    raw = str(value or "").strip()
    if not raw:
        return ""
    key = raw.lower().replace(" ", "_").replace("-", "_")
    if key in _STATUS_CUE_SOFT_MAP:
        return _STATUS_CUE_SOFT_MAP[key]
    # Unknown token: strip snake_case so no raw enum ever reaches the UI.
    return raw.replace("_", " ")


def _clip_text(value: Any, limit: int) -> str:
    """Clip display text without leaving a visibly broken final word."""

    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    if limit <= 1:
        return "…"[:limit]
    candidate = text[: limit - 1].rstrip()
    boundary = max(candidate.rfind(" "), candidate.rfind("\n"))
    if boundary >= max(1, (limit - 1) // 2):
        candidate = candidate[:boundary]
    return candidate.rstrip(" ,;:-—") + "…"


def _plain_climate_relevance_text(value: Any) -> str:
    """Replace internal assessment jargon in reader-facing climate summaries."""

    text = str(value or "").strip()
    text = re.sub(
        r"\bhigh[- ]materiality\b",
        "high-priority",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\bmedium[- ]materiality\b",
        "moderate climate relevance",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\blow[- ]materiality\b",
        "limited climate relevance",
        text,
        flags=re.IGNORECASE,
    )
    return re.sub(
        r"\bmateriality\b",
        "climate relevance",
        text,
        flags=re.IGNORECASE,
    )


def _clip_complete_summary(value: Any, limit: int) -> str:
    """Prefer complete sentences when bounding the opening climate narrative."""

    text = _plain_climate_relevance_text(value)
    if len(text) <= limit:
        return text
    candidate = text[:limit].rstrip()
    sentence_ends = [
        match.end()
        for match in re.finditer(r"[.!?](?=\s|$)", candidate)
    ]
    if sentence_ends and sentence_ends[-1] >= limit // 2:
        return candidate[:sentence_ends[-1]].rstrip()
    return _clip_text(text, limit)


def _concise_status_cue(value: Any) -> str:
    """Reduce model-authored status explanations to a short reader chip."""

    softened = _soften_status_cue(value)
    key = softened.lower().strip()
    for prefix, label in (
        ("material gap", "material gap"),
        ("risk present", "risk present"),
        ("partially addressed", "partially addressed"),
        ("partial gap", "partial gap"),
        ("not yet addressed", "not yet addressed"),
        ("not yet specified", "not yet specified"),
        ("well recognised", "well recognised"),
        ("well recognized", "well recognised"),
        ("unclaimed opportunity", "unclaimed opportunity"),
        ("insufficient evidence", "insufficient evidence"),
        ("potential", "potential"),
        ("strong", "strong"),
        ("addressed", "addressed"),
    ):
        if key.startswith(prefix):
            return label
    return _clip_text(softened, 36)


def _normalize_climate_reflections(value: Any) -> list[dict[str, Any]]:
    """Validate and bound climate diagnostic reflection (theme answer) entries.

    Each entry is a stable-theme answer: question_key + reader title + softened
    status cue + a two-paragraph answer (text, up to ~1800 chars, paragraph
    breaks preserved) + a short source attribution.
    """

    reflections: list[dict[str, Any]] = []
    for raw in _list_values(value):
        if not isinstance(raw, dict):
            continue
        key = str(raw.get("question_key", ""))
        text = str(raw.get("text", "")).strip()[:1800]
        if key not in _CLIMATE_REFLECTION_KEYS or not text:
            continue
        reflections.append({
            "question_key": key,
            "title": str(raw.get("title", "")).strip()[:160],
            "status_cue": _concise_status_cue(raw.get("status_cue", "")),
            "source": str(raw.get("source", "")).strip()[:120],
            "text": text,
        })
        if len(reflections) >= 6:
            break
    return reflections


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
    strict_required_fields: bool = False,
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
                else "" if strict_required_fields
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
                normalized_item = {
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
                }
                if lens_id == "climate":
                    normalized_item["pathway_id"] = item_id
                normalized_items.append(normalized_item)
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
                    "narrative": str(
                        raw_interaction.get("narrative", "")
                    ).strip()[:1600],
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
                    "pathways": _normalize_climate_pathways(
                        raw_interaction.get("pathways"),
                        direction_id,
                    ),
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
                    "pathway_id": (
                        f"additional-{section_id}-"
                        f"{additional_by_section.get(section_id, 0) + 1}"
                    ),
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
        reflections: list[dict[str, Any]] = []
        strengths_weaknesses: list[dict[str, Any]] = []
        integration_level = ""
        integration_rating = ""
        integration_summary = ""
        less_central = ""
        sensitivity_evidence: list[str] = []
        responsiveness_evidence: list[str] = []
        if lens_id == "climate":
            reflections = _normalize_climate_reflections(item.get("reflections"))
            strengths_weaknesses = _normalize_climate_sw(item.get("strengths_weaknesses"))
            integration_rating = climate_integration_rating(item.get("integration_rating"))
            raw_integration = str(item.get("integration_level", "")).lower()
            integration_level = (
                raw_integration if raw_integration in _CLIMATE_INTEGRATION_LEVELS
                else "insufficient_evidence"
            )
            integration_summary = str(item.get("integration_summary", "")).strip()[:400]
            less_central = str(item.get("less_central", "")).strip()[:300]
            sensitivity_evidence = _bounded_strings(item.get("sensitivity_evidence"), 5, 500)
            responsiveness_evidence = _bounded_strings(item.get("responsiveness_evidence"), 5, 500)
        normalized_lens = {
            "lens_id": lens_id,
            "applicability": applicability,
            "materiality_summary": _clip_complete_summary(
                item.get("materiality_summary", ""), 600
            ),
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
                "executive_summary": str(
                    item.get("executive_summary", "")
                ).strip()[:1800],
                "operating_context": _normalize_operating_context(
                    item.get("operating_context")
                ),
                "supplementary_questions": (
                    _normalize_supplementary_questions(
                        item.get("supplementary_questions")
                    )
                ),
                "interaction_readout": normalized_interactions,
                "additional_pathways": normalized_additional,
                "reflections": reflections,
                "strengths_weaknesses": strengths_weaknesses,
                "integration_level": integration_level,
                "integration_rating": integration_rating,
                "integration_summary": integration_summary,
                "less_central": less_central,
                "sensitivity_evidence": sensitivity_evidence,
                "responsiveness_evidence": responsiveness_evidence,
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
        proposed_finding_id = str(raw.get("finding_id", "")).strip()[:64]
        default_finding_id = (
            f"{sorted(set(lens_ids))[0]}-finding-{len(findings) + 1}"
        )
        finding_id = (
            proposed_finding_id
            if _is_valid_finding_id(proposed_finding_id)
            else default_finding_id
        )
        findings.append(
            {
                "finding_id": finding_id,
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
    result = {
        "error": False,
        "message": "",
        "lenses": lenses,
        "findings": findings,
        "truncated": truncated,
    }
    if "climate" in active:
        result["schema_version"] = str(
            data.get("schema_version", "")
        ).strip()[:80]
        result["fcv_baseline"] = _normalize_climate_baseline(
            data.get("fcv_baseline")
        )
    return result


def _has_substantive_climate_content(payload: dict[str, Any]) -> bool:
    """Return whether a stored envelope contains actual Climate content."""

    baseline = payload.get("fcv_baseline")
    if isinstance(baseline, dict) and any(
        bool(value) for value in baseline.values()
    ):
        return True
    lenses = payload.get("lenses")
    if isinstance(lenses, list) and any(
        isinstance(item, dict) and item.get("lens_id") == "climate"
        for item in lenses
    ):
        return True
    findings = payload.get("findings")
    return isinstance(findings, list) and any(
        isinstance(item, dict)
        and "climate" in _list_values(item.get("lens_ids"))
        for item in findings
    )


def normalize_lens_diagnostic(
    payload: dict[str, Any] | None,
    active_lens_ids: Iterable[str],
    source_ids_by_lens: dict[str, set[str]] | None = None,
    readout_schema_by_lens: dict[str, dict[str, set[str]]] | None = None,
) -> dict[str, Any]:
    """Apply the model-output validator to a diagnostic received from a client/session."""

    raw = payload if isinstance(payload, dict) else {}
    active = set(active_lens_ids)
    climate_active = "climate" in active
    if climate_active and raw.get("error"):
        return _error_diagnostic(str(raw.get("message", "")))
    # Stored/client Climate payloads with substantive assessment content are
    # strict here. Empty/control envelopes and raw model extraction remain
    # version-tolerant during the staged dedicated-prompt migration.
    if (
        climate_active
        and _has_substantive_climate_content(raw)
        and raw.get("schema_version") != CLIMATE_NATIVE_SCHEMA_VERSION
    ):
        return _error_diagnostic(
            "Climate diagnostic schema version was missing or unsupported."
        )
    serialized = json.dumps(raw, ensure_ascii=False)
    wrapped = LENS_DIAGNOSTIC_START + serialized + LENS_DIAGNOSTIC_END
    return extract_lens_diagnostic(
        wrapped,
        active_lens_ids,
        source_ids_by_lens,
        readout_schema_by_lens,
    )


def normalize_priority_climate_links(
    raw: Any,
    diagnostic: dict[str, Any] | None,
) -> dict[str, Any]:
    """Validate priority-to-diagnostic Climate provenance links."""

    if not isinstance(raw, dict):
        return {}
    diagnostic = diagnostic if isinstance(diagnostic, dict) else {}
    interaction_ids: set[str] = set()
    dividend_ids: set[str] = set()
    for lens in diagnostic.get("lenses", []):
        if not isinstance(lens, dict) or lens.get("lens_id") != "climate":
            continue
        for interaction in _list_values(lens.get("interaction_readout")):
            if not isinstance(interaction, dict):
                continue
            for pathway in _list_values(interaction.get("pathways")):
                if isinstance(pathway, dict) and pathway.get("pathway_id"):
                    interaction_ids.add(str(pathway["pathway_id"]))
        for section in _list_values(lens.get("readout_sections")):
            if not isinstance(section, dict):
                continue
            for item in _list_values(section.get("items")):
                if isinstance(item, dict) and item.get("pathway_id"):
                    dividend_ids.add(str(item["pathway_id"]))
        for pathway in _list_values(lens.get("additional_pathways")):
            if isinstance(pathway, dict) and pathway.get("pathway_id"):
                dividend_ids.add(str(pathway["pathway_id"]))
    finding_ids = {
        str(finding.get("finding_id"))
        for finding in _list_values(diagnostic.get("findings"))
        if isinstance(finding, dict)
        and "climate" in _list_values(finding.get("lens_ids"))
        and finding.get("finding_id")
    }

    def recognized(name: str, allowed: set[str]) -> list[str]:
        return list(dict.fromkeys(
            value
            for value in _bounded_strings(raw.get(name), 8, 100)
            if value in allowed
        ))

    interaction_links = recognized(
        "interaction_pathway_ids", interaction_ids
    )
    dividend_links = recognized("dividend_pathway_ids", dividend_ids)
    finding_links = recognized("finding_ids", finding_ids)
    status = str(raw.get("status", "")).strip()
    contribution = str(raw.get("contribution", "")).strip()[:700]
    strengthening_effect = str(
        raw.get("strengthening_effect", "")
    ).strip()[:700]
    reason = str(raw.get("reason", "")).strip()[:700]
    if status == "linked":
        if (
            not (interaction_links or dividend_links or finding_links)
            or not contribution
            or not strengthening_effect
        ):
            return {}
    elif status == "no-material-pathway":
        raw_ids_present = any(
            bool(raw.get(name))
            for name in (
                "interaction_pathway_ids",
                "dividend_pathway_ids",
                "finding_ids",
            )
        )
        if (
            raw_ids_present
            or interaction_links
            or dividend_links
            or finding_links
            or not reason
        ):
            return {}
        contribution = ""
        strengthening_effect = ""
    else:
        return {}
    return {
        "status": status,
        "interaction_pathway_ids": interaction_links,
        "dividend_pathway_ids": dividend_links,
        "finding_ids": finding_links,
        "contribution": contribution,
        "strengthening_effect": strengthening_effect,
        "reason": reason if status == "no-material-pathway" else "",
    }


def climate_lens_readout(diagnostic: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return the normalized Climate lens entry from a diagnostic, or None."""

    if not isinstance(diagnostic, dict):
        return None
    for lens in diagnostic.get("lenses", []):
        if isinstance(lens, dict) and lens.get("lens_id") == "climate":
            return lens
    return None


def climate_readout_is_complete(
    climate_entry: dict[str, Any] | None,
    *,
    baseline: dict[str, Any] | None = None,
) -> bool:
    """True only for a complete canonical Climate-FCV readout."""

    if not isinstance(climate_entry, dict):
        return False
    baseline = baseline if isinstance(baseline, dict) else {}
    baseline_complete = all(
        baseline.get(key)
        for key in (
            "sensitivity_rating",
            "responsiveness_rating",
            "sensitivity_reasoning",
            "responsiveness_reasoning",
            "evidence_trail",
        )
    )
    context = climate_entry.get("operating_context")
    context_complete = isinstance(context, dict) and all(
        context.get(key)
        for key in ("fcv_setting", "climate_setting", "intersection")
    )
    reflections = climate_entry.get("reflections")
    has_reflections = isinstance(reflections, list) and any(
        isinstance(item, dict) and str(item.get("text", "")).strip()
        for item in reflections
    )
    interactions = climate_entry.get("interaction_readout")
    directions = {
        item.get("direction_id")
        for item in interactions
        if isinstance(item, dict) and item.get("pathways")
    } if isinstance(interactions, list) else set()
    return bool(
        baseline_complete
        and climate_entry.get("executive_summary")
        and climate_entry.get("integration_rating")
        and climate_entry.get("integration_summary")
        and context_complete
        and CLIMATE_REQUIRED_DIRECTIONS.issubset(directions)
        and climate_entry.get("strengths_weaknesses")
        and has_reflections
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
