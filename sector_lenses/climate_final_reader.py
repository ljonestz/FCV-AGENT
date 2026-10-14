"""Evidence binding and admission for prose compiled after decision review."""
from __future__ import annotations

from copy import deepcopy
import re

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


def bind_same_passage_project_references(payload: dict, assessment: dict) -> tuple[dict, int]:
    """Bind a named explicit fact from an already cited passage, without editing prose.

    A compiler can cite the redesign fact but miss the sibling location fact
    extracted from that exact passage. This only repairs that citation; meaning
    still requires independent review. Other passages and country evidence are
    never eligible, and ambiguous IDs are excluded by the support registry.
    """
    repaired = deepcopy(payload)
    support = reader_support_records(assessment)
    facts = {
        fact['claim_id']: fact for fact in assessment.get('facts', [])
        if isinstance(fact, dict) and fact.get('claim_id') in support
        and fact.get('epistemic_status') == 'explicit'
        and isinstance(fact.get('source_block_ids'), list)
    }

    def prose(record: dict) -> str:
        return ' '.join(str(record.get(key, '')) for key in
                        ('statement', 'subject', 'predicate', 'object_value'))

    added = 0
    for record in repaired.get('summary_paragraphs', []) + repaired.get('assessment_narratives', []):
        refs = record.get('evidence_ids') if isinstance(record, dict) else None
        if not isinstance(refs, list) or not refs or any(ref not in support for ref in refs):
            continue
        cited_blocks = {block for ref in refs if ref in facts
                        for block in facts[ref]['source_block_ids'] if isinstance(block, str)}
        if not cited_blocks:
            continue
        texts = [record['text']] if 'text' in record else record.get('paragraphs', [])
        for text in texts:
            for _ in range(len(facts)):
                diagnostics: dict = {}
                validate_summary_fragment(text, canonical_text=[support[ref] for ref in refs],
                                          allow_paraphrase=True, diagnostics=diagnostics)
                if diagnostics.get('reason') != 'SUMMARY_ENTITY_UNSUPPORTED':
                    break
                name = diagnostics.get('detail', '')
                pattern = r'\b' + re.escape(name) + r'\b'
                matching = [identifier for identifier, fact in facts.items()
                            if identifier not in refs
                            and cited_blocks.intersection(fact['source_block_ids'])
                            and re.search(pattern, prose(fact), flags=re.IGNORECASE)]
                if len(matching) != 1:
                    break
                refs.append(matching[0])
                added += 1
    return repaired, added


def validate_final_reader(payload: object, assessment: dict[str, object],
                          *, issues: list[dict] | None = None) -> tuple[list[str], list[dict]]:
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

    def rejected(identifier: object, explanation: str) -> bool:
        if issues is not None and isinstance(identifier, str):
            issues.append({'object_id': identifier, 'explanation': explanation})
        return False

    def grounded(record: dict, texts: list[str]) -> bool:
        identifier, refs = record.get("object_id"), record.get("evidence_ids")
        if (not isinstance(identifier, str) or not identifier or identifier in ids
                or not isinstance(refs, list) or not refs
                or any(not isinstance(ref, str) or ref not in support for ref in refs)):
            return rejected(identifier, 'Use unique paragraph IDs and only specific admitted evidence IDs.')
        ids.add(identifier)
        canonical = [support[ref] for ref in refs] + [assessment.get("judgments", {})]
        for text in texts:
            diagnostics: dict = {}
            if not validate_summary_fragment(text, canonical_text=canonical, allow_paraphrase=True,
                                             diagnostics=diagnostics):
                return rejected(identifier, str(diagnostics))
        return True

    valid = True
    for index, record in enumerate(paragraphs):
        if not isinstance(record, dict) or record.get('object_id') != f'SUM-{index + 1:03d}':
            return [], []
        if not grounded(record, [record.get('text')]):
            valid = False
    summary = validate_summary_overview(
        {"paragraphs": [record["text"] for record in paragraphs]},
        executive_readout=assessment.get("executive_readout", ""),
        canonical_text=list(support.values()) + [assessment.get("judgments", {})],
        allow_paraphrase=True,
    )
    if not summary and valid:
        for record in paragraphs:
            rejected(record['object_id'], 'Keep the Summary within its word range and use connected, original prose.')
        valid = False
    themes: set[str] = set()
    for record in narratives:
        if not isinstance(record, dict):
            return [], []
        theme, texts = record.get("theme"), record.get("paragraphs")
        if (theme not in {"design", "dividends", "inclusion"} or theme in themes
                or record.get("object_id") != f"NARR-{theme}"
                or not isinstance(texts, list) or not 1 <= len(texts) <= 2
                or any(not isinstance(text, str) for text in texts)
                or not 70 <= sum(len(text.split()) for text in texts) <= 180):
            rejected(record.get('object_id'), 'Use the required theme, one or two paragraphs and 70-180 words.')
            valid = False
        elif not grounded(record, texts):
            valid = False
        themes.add(theme)
    return (summary, narratives) if valid else ([], [])


def reviewed_final_reader(payload: object, review: object, assessment: dict[str, object]) -> tuple[list[str], list[dict]]:
    """Require an explicit clean semantic pass, including at saved-result export."""
    if (not isinstance(review, dict) or review.get("verdict") != "pass"
            or review.get("object_ids") or review.get("reason_codes") or review.get("issues")):
        return [], []
    return validate_final_reader(payload, assessment)
