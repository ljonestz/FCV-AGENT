"""Evidence binding and admission for prose compiled after decision review."""
from __future__ import annotations

from sector_lenses.climate_verified_schemas import (
    validate_summary_fragment, validate_summary_overview,
)


def reader_support_records(assessment: dict[str, object]) -> dict[str, dict]:
    """Collect admitted registers only; ambiguous duplicate IDs are not support."""
    records: dict[str, dict] = {}
    duplicates: set[str] = set()
    analysis = assessment.get("analysis", {})
    if not isinstance(analysis, dict):
        analysis = {}
    for values, key in (
        (assessment.get("facts", []), "claim_id"),
        (assessment.get("derived_assertions", []), "assertion_id"),
        (assessment.get("context_evidence", []), "evidence_id"),
        (analysis.get("existing_responses", []), "response_id"),
        (analysis.get("pathways", []), "pathway_id"),
        (analysis.get("residual_gaps", []), "gap_id"),
        (assessment.get("priorities", []), "recommendation_id"),
    ):
        for record in values if isinstance(values, list) else []:
            if not isinstance(record, dict) or not isinstance(record.get(key), str):
                continue
            identifier = record[key]
            if identifier in records:
                duplicates.add(identifier)
            records[identifier] = record
    return {key: record for key, record in records.items() if key not in duplicates}


def validate_final_reader(payload: object, assessment: dict[str, object]) -> tuple[list[str], list[dict]]:
    """Allow paraphrase, with each paragraph bound to specific admitted evidence.

    This checks entities, numbers and identifiers, not meaning. Independent
    reader_review is mandatory before these paragraphs may be published.
    """
    if not isinstance(payload, dict):
        return [], []
    support = reader_support_records(assessment)
    paragraphs = payload.get("summary_paragraphs", [])
    narratives = payload.get("assessment_narratives", [])
    if (not isinstance(paragraphs, list) or not isinstance(narratives, list)
            or len(narratives) != 3):
        return [], []
    ids: set[str] = set()

    def grounded(record: dict, texts: list[str]) -> bool:
        identifier, refs = record.get("object_id"), record.get("evidence_ids")
        if (not isinstance(identifier, str) or not identifier or identifier in ids
                or not isinstance(refs, list) or not refs
                or any(not isinstance(ref, str) or ref not in support for ref in refs)):
            return False
        ids.add(identifier)
        canonical = [support[ref] for ref in refs] + [assessment.get("judgments", {})]
        return all(validate_summary_fragment(text, canonical_text=canonical, allow_paraphrase=True)
                   for text in texts)

    if any(not isinstance(record, dict) or record.get("object_id") != f"SUM-{index + 1:03d}"
           or not grounded(record, [record.get("text")])
           for index, record in enumerate(paragraphs)):
        return [], []
    summary = validate_summary_overview(
        {"paragraphs": [record["text"] for record in paragraphs]},
        executive_readout=assessment.get("executive_readout", ""),
        canonical_text=list(support.values()) + [assessment.get("judgments", {})],
        allow_paraphrase=True,
    )
    if not summary:
        return [], []
    themes: set[str] = set()
    for record in narratives:
        if not isinstance(record, dict):
            return [], []
        theme, texts = record.get("theme"), record.get("paragraphs")
        if (theme not in {"design", "dividends", "inclusion"} or theme in themes
                or record.get("object_id") != f"NARR-{theme}"
                or not isinstance(texts, list) or not 1 <= len(texts) <= 2
                or any(not isinstance(text, str) for text in texts)
                or not 70 <= sum(len(text.split()) for text in texts) <= 180
                or not grounded(record, texts)):
            return [], []
        themes.add(theme)
    return summary, narratives


def reviewed_final_reader(payload: object, review: object, assessment: dict[str, object]) -> tuple[list[str], list[dict]]:
    """Require an explicit clean semantic pass, including at saved-result export."""
    if (not isinstance(review, dict) or review.get("verdict") != "pass"
            or review.get("object_ids") or review.get("reason_codes") or review.get("issues")):
        return [], []
    return validate_final_reader(payload, assessment)
