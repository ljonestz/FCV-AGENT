"""Evidence binding and admission for prose compiled after decision review."""
from __future__ import annotations

from copy import deepcopy
import re

from sector_lenses.climate_verified_schemas import (
    _SUMMARY_MONTHS, validate_summary_fragment, validate_summary_overview,
)


_READER_NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?%?\b")


def _reader_record_text(record: dict) -> str:
    return record.get('text') or ' '.join(record.get('paragraphs', []))


def reader_correction_allowed_numeric_date_tokens(record: dict) -> dict[str, list[str]]:
    """Expose the numeric and date tokens the correction validator permits."""
    text = _reader_record_text(record)
    dates: set[str] = set()
    for month in _SUMMARY_MONTHS:
        dates.update(re.findall(
            rf"\b{month}\s+\d{{4}}\b|\b\d{{1,2}}\s+{month}\b",
            text.casefold(),
        ))
    return {
        'numeric_tokens': sorted(set(_READER_NUMBER_RE.findall(text))),
        'date_phrases': sorted(dates),
    }


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
            if key == "recommendation_id":
                # An accepted action is not independent evidence for its narrative premises.
                action_fields = (
                    "recommendation_id", "title", "decision", "minimum_action",
                    "enhanced_action", "enhanced_activation", "project_anchor_ids",
                    "pathway_ids", "residual_gap_ids", "existing_response_ids",
                )
                records[identifier] = {
                    field: deepcopy(record[field]) for field in action_fields if field in record
                }
                records[identifier]["support_role"] = "accepted_proposed_action"
            else:
                records[identifier] = record
    return {key: record for key, record in records.items() if key not in duplicates}


def normalize_reader_paragraphs(payload: dict) -> dict:
    """Remove empty punctuation fragments and fold paragraph breaks, never claims."""
    normalized = deepcopy(payload)
    records = normalized.get('assessment_narratives', [])
    for record in records if isinstance(records, list) else []:
        texts = record.get('paragraphs') if isinstance(record, dict) else None
        if not isinstance(texts, list) or not all(isinstance(text, str) for text in texts):
            continue
        texts = [text for text in texts if not re.fullmatch(r'[\s.,;:!?…]*', text)]
        record['paragraphs'] = texts if len(texts) <= 2 else [texts[0], ' '.join(texts[1:])]
    return normalized


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

    This checks numbers, dates, identifiers and format, not meaning. Independent
    reader_review is mandatory before these paragraphs may be published.
    """
    def rejected(identifier: object, explanation: str, code: str = 'READER_FORMAT_INVALID') -> bool:
        if issues is not None and isinstance(identifier, str):
            issues.append({'object_id': identifier, 'reason_codes': [code], 'explanation': explanation})
        return False

    if not isinstance(payload, dict):
        rejected('reader', 'Reader must be an object.', 'READER_STRUCTURE_INVALID')
        return [], []
    support = reader_support_records(assessment)
    paragraphs = payload.get("summary_paragraphs", [])
    narratives = payload.get("assessment_narratives", [])
    if (not isinstance(paragraphs, list) or not isinstance(narratives, list)
            or len(narratives) != 3):
        rejected('reader', 'Reader requires Summary records and exactly three findings.', 'READER_STRUCTURE_INVALID')
        return [], []
    ids: set[str] = set()

    def grounded(record: dict, texts: list[str]) -> bool:
        identifier, refs = record.get("object_id"), record.get("evidence_ids")
        if (not isinstance(identifier, str) or not identifier or identifier in ids
                or not isinstance(refs, list) or not refs
                or any(not isinstance(ref, str) or ref not in support for ref in refs)):
            return rejected(identifier, 'Use unique paragraph IDs and only specific admitted evidence IDs.', 'READER_EVIDENCE_INVALID')
        ids.add(identifier)
        canonical = [support[ref] for ref in refs] + [assessment.get("judgments", {})]
        for text in texts:
            diagnostics: dict = {}
            if not validate_summary_fragment(text, canonical_text=canonical, allow_paraphrase=True,
                                             diagnostics=diagnostics, semantic_review_required=True):
                return rejected(identifier, str(diagnostics), diagnostics.get('reason', 'READER_FORMAT_INVALID'))
        return True

    valid = True
    for index, record in enumerate(paragraphs):
        if not isinstance(record, dict) or record.get('object_id') != f'SUM-{index + 1:03d}':
            rejected('reader', 'Summary IDs must be sequential and unique.', 'READER_STRUCTURE_INVALID')
            return [], []
        if not grounded(record, [record.get('text')]):
            valid = False
    summary_diagnostics: dict = {}
    summary = validate_summary_overview(
        {"paragraphs": [record.get("text") for record in paragraphs]},
        executive_readout=assessment.get("executive_readout", ""),
        canonical_text=list(support.values()) + [assessment.get("judgments", {})],
        allow_paraphrase=True,
        semantic_review_required=True,
        diagnostics=summary_diagnostics,
    )
    if not summary:
        for record in paragraphs:
            count = sum(len(record['text'].split()) for record in paragraphs if isinstance(record.get('text'), str))
            explanation = (f'Summary has {count} words; permitted range is 160-260 across all Summary paragraphs (target 160-230).'
                           if summary_diagnostics.get('reason') == 'SUMMARY_WORD_COUNT'
                           else str(summary_diagnostics))
            rejected(record['object_id'], explanation, summary_diagnostics.get('reason', 'READER_FORMAT_INVALID'))
        valid = False
    themes: set[str] = set()
    for record in narratives:
        if not isinstance(record, dict):
            rejected('reader', 'Each finding must be an object.', 'READER_STRUCTURE_INVALID')
            return [], []
        theme, texts = record.get("theme"), record.get("paragraphs")
        if (not isinstance(theme, str) or theme not in {"design", "dividends", "inclusion"} or theme in themes
                or record.get("object_id") != f"NARR-{theme}"
                or not isinstance(texts, list) or not 1 <= len(texts) <= 2
                or any(not isinstance(text, str) for text in texts)):
            rejected(record.get('object_id'), 'Use the required ID/theme and one or two text paragraphs.', 'READER_STRUCTURE_INVALID')
            valid = False
        else:
            # Presentation defects must not mask unsupported evidence references.
            if not grounded(record, texts):
                valid = False
            count = sum(len(text.split()) for text in texts)
            if not 70 <= count <= 200:
                rejected(record['object_id'], f'Finding has {count} words; permitted range is 70-200 (target 70-180).', 'READER_WORD_COUNT')
                valid = False
        if isinstance(theme, str):
            themes.add(theme)
    return (summary, narratives) if valid else ([], [])


def apply_reader_corrections(payload: dict, response: object, targets: set[str],
                             *, issues: list[dict]) -> dict | None:
    """Merge exact text patches; the model cannot alter evidence or other records."""
    def reject(code: str, identifier: str = 'reader') -> None:
        issues.append({'object_id': identifier, 'reason_codes': [code], 'explanation': code})

    if not isinstance(response, dict) or set(response) != {'corrections'} or not isinstance(response['corrections'], list):
        reject('READER_CORRECTION_FORMAT_INVALID')
        return None
    records = {record['object_id']: record for key in ('summary_paragraphs', 'assessment_narratives')
               for record in payload[key]}
    patches = {}
    for patch in response['corrections']:
        if not isinstance(patch, dict) or set(patch) != {'object_id', 'edits'}:
            reject('READER_CORRECTION_FIELDS_INVALID', patch.get('object_id', 'reader') if isinstance(patch, dict) else 'reader')
            return None
        identifier = patch['object_id']
        if not isinstance(identifier, str) or identifier not in targets or identifier in patches:
            reject('READER_CORRECTION_TARGET_INVALID', identifier if isinstance(identifier, str) else 'reader')
            return None
        original = records.get(identifier)
        if original is None:
            reject('READER_CORRECTION_TARGET_INVALID', identifier)
            return None
        paragraphs = [original['text']] if 'text' in original else list(original['paragraphs'])
        edits = patch['edits']
        if not isinstance(edits, list):
            reject('READER_CORRECTION_EDIT_FIELDS_INVALID', identifier)
            return None
        spans: dict[int, list[tuple[int, int, str]]] = {}
        for edit in edits:
            if not isinstance(edit, dict) or set(edit) != {'paragraph_index', 'old_text', 'new_text'}:
                reject('READER_CORRECTION_EDIT_FIELDS_INVALID', identifier)
                return None
            index, old, new = edit['paragraph_index'], edit['old_text'], edit['new_text']
            if type(index) is not int or not 0 <= index < len(paragraphs):
                reject('READER_CORRECTION_PARAGRAPH_INVALID', identifier)
                return None
            if not isinstance(old, str) or not old.strip() or not isinstance(new, str):
                reject('READER_CORRECTION_TEXT_INVALID', identifier)
                return None
            # Conservative sentence boundary: decimals do not match. If an
            # abbreviation matches, request a smaller clause anchor instead.
            if any(re.search(r"[.!?][\"'’”)]*\s+\S", text) for text in (old, new)):
                reject('READER_CORRECTION_SENTENCE_SCOPE_INVALID', identifier)
                return None
            text = paragraphs[index]
            start = text.find(old)
            if start < 0 or text.find(old, start + 1) >= 0:
                reject('READER_CORRECTION_ANCHOR_INVALID', identifier)
                return None
            end = start + len(old)
            existing = spans.setdefault(index, [])
            if any(start < prior_end and prior_start < end for prior_start, prior_end, _ in existing):
                reject('READER_CORRECTION_OVERLAP_INVALID', identifier)
                return None
            existing.append((start, end, new))
        # Resolve every anchor against the unchanged original, then merge from
        # right to left so one edit cannot change another edit's location.
        for index, paragraph_spans in spans.items():
            for start, end, new in sorted(paragraph_spans, reverse=True):
                paragraphs[index] = paragraphs[index][:start] + new + paragraphs[index][end:]
        if any(not text.strip() for text in paragraphs):
            reject('READER_CORRECTION_TEXT_INVALID', identifier)
            return None
        original_text = _reader_record_text(original)
        diagnostic = {}
        if not validate_summary_fragment(' '.join(paragraphs), canonical_text=original_text,
                                         allow_paraphrase=True, semantic_review_required=True,
                                         diagnostics=diagnostic):
            reject('READER_CORRECTION_' + diagnostic.get('reason', 'TEXT_INVALID'), identifier)
            return None
        patches[identifier] = paragraphs
    if set(patches) != targets or not targets <= records.keys():
        reject('READER_CORRECTION_TARGETS_MISSING')
        return None
    corrected = deepcopy(payload)
    for key in ('summary_paragraphs', 'assessment_narratives'):
        for record in corrected[key]:
            if record['object_id'] in patches:
                if key == 'summary_paragraphs':
                    record['text'] = patches[record['object_id']][0]
                else:
                    record['paragraphs'] = patches[record['object_id']]
    return corrected


def reviewed_final_reader(payload: object, review: object, assessment: dict[str, object]) -> tuple[list[str], list[dict]]:
    """Require an explicit clean semantic pass, including at saved-result export."""
    if (not isinstance(review, dict) or review.get("verdict") != "pass"
            or any(review.get(key) != [] for key in ('object_ids', 'reason_codes', 'issues'))):
        return [], []
    return validate_final_reader(payload, assessment)
