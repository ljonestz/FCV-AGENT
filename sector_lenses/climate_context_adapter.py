"""Adapt the final bank/live grounding object to contextual evidence refs."""

from __future__ import annotations

from typing import Any

from sector_lenses.climate_analysis import ContextEvidenceRef


PREVIEW_STATUS = "preview; not approved"


def _dict_list(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _text(value: object) -> str:
    return str(value or "").strip()


def _scope(record: dict[str, Any]) -> str:
    level = _text(record.get("administrative_level"))
    geographies = [
        _text(item)
        for item in record.get("geographies", [])
        if _text(item)
    ]
    geography = ", ".join(geographies)
    if level and level != "not-applicable" and geography:
        return f"{level}: {geography}"
    return geography or level or "unresolved"


def _bank_prefix(preview: bool) -> str:
    return "bank-preview" if preview else "bank"


def adapt_grounding_evidence(
    grounding: object,
) -> tuple[ContextEvidenceRef, ...]:
    """Return sourced context only; never promote grounding to project facts."""

    if not isinstance(grounding, dict):
        return ()
    content_version = _text(grounding.get("content_version"))
    preview = grounding.get("candidate_preview") is True
    preview_status = PREVIEW_STATUS if preview else None
    prefix = _bank_prefix(preview)
    bank_sources = _dict_list(grounding.get("bank_sources"))
    bank_source_ids = {
        _text(item.get("source_id"))
        for item in bank_sources
        if _text(item.get("source_id"))
    }
    bank_records = _dict_list(grounding.get("bank_evidence_records"))
    bank_record_ids = {
        _text(item.get("evidence_id"))
        for item in bank_records
        if _text(item.get("evidence_id"))
    }
    result: list[ContextEvidenceRef] = []

    for record in bank_records:
        identifier = _text(record.get("evidence_id"))
        statement = _text(
            record.get("compact_statement") or record.get("statement")
        )
        source_ids = {
            _text(ref.get("source_id"))
            for ref in _dict_list(record.get("source_refs"))
            if _text(ref.get("source_id"))
        }
        if (
            not identifier
            or not statement
            or not content_version
            or not source_ids
            or not source_ids.issubset(bank_source_ids)
        ):
            continue
        result.append(
            ContextEvidenceRef(
                evidence_id=f"CE-BANK-{identifier}",
                evidence_class="country",
                scope=_scope(record),
                statement=statement,
                source_ref=f"{prefix}:{content_version}:{identifier}",
                confidence=_text(record.get("confidence")) or "medium",
                source_kind="country_bank",
                context_class=(
                    _text(record.get("evidence_class")) or None
                ),
                preview_status=preview_status,
            )
        )

    for pathway in _dict_list(grounding.get("bank_pathways")):
        identifier = _text(pathway.get("pathway_id"))
        statement = _text(
            pathway.get("compact_statement")
            or pathway.get("possible_consequence")
        )
        support = {
            _text(item)
            for item in pathway.get("supporting_evidence_ids", [])
            if _text(item)
        }
        if (
            not identifier
            or not statement
            or not content_version
            or not support
            or not support.issubset(bank_record_ids)
        ):
            continue
        direction = _text(pathway.get("interaction_direction"))
        result.append(
            ContextEvidenceRef(
                evidence_id=f"CE-BANK-{identifier}",
                evidence_class="country",
                scope=_scope(pathway),
                statement=statement,
                source_ref=f"{prefix}:{content_version}:{identifier}",
                confidence=(
                    _text(pathway.get("evidence_strength")) or "medium"
                ),
                source_kind="country_bank",
                context_class=(
                    f"{direction}-pathway" if direction else "pathway"
                ),
                preview_status=preview_status,
            )
        )

    live_sources = _dict_list(grounding.get("live_sources"))
    live_source_urls = {
        _text(item.get("id")): _text(item.get("url"))
        for item in live_sources
        if _text(item.get("id")) and _text(item.get("url"))
    }
    for claim in _dict_list(grounding.get("live_claims")):
        identifier = _text(claim.get("id"))
        statement = _text(claim.get("claim"))
        declared_source_ids = [
            _text(item)
            for item in claim.get("source_ids", [])
            if _text(item)
        ]
        if (
            not identifier
            or not statement
            or not declared_source_ids
            or any(item not in live_source_urls for item in declared_source_ids)
        ):
            continue
        primary_url = live_source_urls[declared_source_ids[0]]
        result.append(
            ContextEvidenceRef(
                evidence_id=f"CE-LIVE-{identifier}",
                evidence_class="country",
                scope=_scope(claim),
                statement=statement,
                source_ref=f"live:{primary_url}:{identifier}",
                confidence=_text(claim.get("confidence")) or "medium",
                source_kind="live_research",
                context_class="live_claim",
                preview_status=None,
            )
        )
    return tuple(result)
