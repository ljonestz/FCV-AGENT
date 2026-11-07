"""Evidence binding and admission for prose compiled after decision review."""
from __future__ import annotations

from copy import deepcopy
import re

from sector_lenses.climate_verified_schemas import (
    _SUMMARY_MONTHS, SEMANTIC_REVIEW_REASON_CODES, _summary_strings, validate_summary_fragment,
    validate_summary_overview,
)


_READER_NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?%?\b")


def reader_records(payload: object) -> list[dict]:
    """Summary and finding records that are objects; malformed containers yield none."""
    if not isinstance(payload, dict):
        return []
    return [record for key in ('summary_paragraphs', 'assessment_narratives')
            for record in (payload.get(key) if isinstance(payload.get(key), list) else [])
            if isinstance(record, dict)]


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
                diagnostics = assessment.get("recommendation_diagnostics")
                marked = diagnostics.get("verification_issues", {}) if isinstance(diagnostics, dict) else {}
                if isinstance(marked, dict) and identifier in marked:
                    continue
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
        record['paragraphs'] = texts if len(texts) <= 3 else [texts[0], texts[1], ' '.join(texts[2:])]
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
    for record in reader_records(repaired):
        refs = record.get('evidence_ids')
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


def _fact_prose_numbers(fact: dict) -> set[str]:
    """Numbers stated in a fact's prose; identifier fields are not evidence."""
    values = [value for key, value in fact.items()
              if not key.endswith(('_id', '_ids'))]
    return set(_READER_NUMBER_RE.findall(' '.join(_summary_strings(values))))


def bind_same_summary_number_references(payload: dict, assessment: dict) -> tuple[dict, int]:
    """Bind the one admitted fact that states a number a record uses, without editing prose.

    A compiler can state a figure in two records but cite its fact in only one
    (Honduras: "46-km corridor" cited by SUM-001, not SUM-002). When a record's
    own evidence does not support a number, the number is bound only when one
    admitted fact states it: a fact already cited by a sibling record in this
    reader is preferred, otherwise the single admitted fact. More than one
    candidate is ambiguous and nothing is bound. Meaning still requires review.
    """
    repaired = deepcopy(payload)
    support = reader_support_records(assessment)
    facts = {
        fact['claim_id']: _fact_prose_numbers(fact) for fact in assessment.get('facts', [])
        if isinstance(fact, dict) and fact.get('claim_id') in support
    }
    records = reader_records(repaired)
    judgments = assessment.get('judgments', {})
    added = 0
    for record in records:
        refs = record.get('evidence_ids')
        if not isinstance(refs, list) or not refs or any(ref not in support for ref in refs):
            continue
        texts = [record['text']] if 'text' in record else record.get('paragraphs', [])
        if not isinstance(texts, list):
            continue
        sibling_refs = {ref for other in records if other is not record
                        for ref in (other.get('evidence_ids') or []) if isinstance(ref, str)}
        for text in texts:
            for _ in range(len(facts)):
                diagnostics: dict = {}
                validate_summary_fragment(text, canonical_text=[support[ref] for ref in refs] + [judgments],
                                          allow_paraphrase=True, semantic_review_required=True,
                                          diagnostics=diagnostics)
                if diagnostics.get('reason') != 'SUMMARY_NUMBER_UNSUPPORTED':
                    break
                number = diagnostics.get('detail', '')
                candidates = [identifier for identifier, numbers in facts.items()
                              if identifier not in refs and number in numbers]
                preferred = [identifier for identifier in candidates if identifier in sibling_refs]
                chosen = preferred or candidates
                if len(chosen) != 1:
                    break
                refs.append(chosen[0])
                added += 1
    return repaired, added


def validate_final_reader(payload: object, assessment: dict[str, object],
                          *, issues: list[dict] | None = None) -> tuple[list[str], list[dict]]:
    """All-or-nothing precheck: every record must pass, or nothing is returned.

    Kept for callers that certify a whole reader; admission uses the per-record
    result from validate_final_reader_records.
    """
    result = validate_final_reader_records(payload, assessment, issues=issues)
    if (not result['structure_valid'] or not result['summary']
            or not all(result['record_status'].values())):
        return [], []
    return result['summary'], payload['assessment_narratives']


def validate_final_reader_records(payload: object, assessment: dict[str, object],
                                  *, issues: list[dict] | None = None) -> dict[str, object]:
    """Allow paraphrase, with each paragraph bound to specific admitted evidence.

    This checks numbers, dates, identifiers and format, not meaning. Independent
    reader_review is mandatory before these paragraphs may be published.

    Returns ``structure_valid`` (reader shape), ``record_status`` (pass/fail by
    object_id), ``summary`` (normalized Summary paragraphs, only when every
    Summary record passes) and ``narratives`` (the passing narrative records).
    """
    record_status: dict[str, bool] = {}

    def result(summary: list[str] | None = None, passing: list[dict] | None = None,
               structure_valid: bool = True) -> dict[str, object]:
        return {'structure_valid': structure_valid, 'record_status': record_status,
                'summary': summary or [], 'narratives': passing or []}

    def rejected(identifier: object, explanation: str, code: str = 'READER_FORMAT_INVALID') -> bool:
        if issues is not None and isinstance(identifier, str):
            issues.append({'object_id': identifier, 'reason_codes': [code], 'explanation': explanation})
        return False

    if not isinstance(payload, dict):
        rejected('reader', 'Reader must be an object.', 'READER_STRUCTURE_INVALID')
        return result(structure_valid=False)
    support = reader_support_records(assessment)
    paragraphs = payload.get("summary_paragraphs", [])
    narratives = payload.get("assessment_narratives", [])
    if not isinstance(paragraphs, list):
        rejected('reader', 'Reader requires a list of Summary records.', 'READER_STRUCTURE_INVALID')
        return result(structure_valid=False)
    # A malformed findings list withholds every finding but cannot sink a
    # Summary whose records are well formed; those are still checked and reviewed.
    if (not isinstance(narratives, list) or len(narratives) != 3
            or not all(isinstance(record, dict) for record in narratives)):
        rejected('reader', 'Reader requires exactly three finding objects; findings are withheld.', 'READER_STRUCTURE_INVALID')
        record_status['reader-narratives'] = False
        narratives = []
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

    for index, record in enumerate(paragraphs):
        if not isinstance(record, dict) or record.get('object_id') != f'SUM-{index + 1:03d}':
            rejected('reader', 'Summary IDs must be sequential and unique.', 'READER_STRUCTURE_INVALID')
            return result(structure_valid=False)
    for record in paragraphs:
        record_status[record['object_id']] = grounded(record, [record.get('text')])
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
            explanation = (f'Summary has {count} words; hard ceiling is 500 across all Summary paragraphs (editorial target 160-230).'
                           if summary_diagnostics.get('reason') == 'SUMMARY_WORD_COUNT'
                           else str(summary_diagnostics))
            rejected(record['object_id'], explanation, summary_diagnostics.get('reason', 'READER_FORMAT_INVALID'))
            record_status[record['object_id']] = False
    themes: set[str] = set()
    passing: list[dict] = []
    for position, record in enumerate(narratives):
        theme, texts = record.get("theme"), record.get("paragraphs")
        identifier = record.get('object_id')
        status_key = identifier if isinstance(identifier, str) and identifier not in record_status else f'reader-narrative-{position}'
        if (not isinstance(theme, str) or theme not in {"design", "dividends", "inclusion"} or theme in themes
                or identifier != f"NARR-{theme}"
                or not isinstance(texts, list) or not 1 <= len(texts) <= 3
                or any(not isinstance(text, str) for text in texts)):
            rejected(identifier, 'Use the required ID/theme and one to three text paragraphs.', 'READER_STRUCTURE_INVALID')
            valid = False
        else:
            # Presentation defects must not mask unsupported evidence references.
            valid = grounded(record, texts)
            count = sum(len(text.split()) for text in texts)
            if not 1 <= count <= 400:
                rejected(identifier, f'Finding has {count} words; nonempty prose is required and the hard ceiling is 400 (editorial target 180-240).', 'READER_WORD_COUNT')
                valid = False
        record_status[status_key] = valid
        if valid:
            passing.append(record)
        if isinstance(theme, str):
            themes.add(theme)
    summary_passes = bool(summary) and all(record_status[record['object_id']] for record in paragraphs)
    return result(summary if summary_passes else [], passing)


def _corrected_paragraphs(original: dict, edits: object, canonical: list[object],
                          reject) -> list[str] | None:
    """Apply one record's exact edits, or report why the patch is unusable."""
    identifier = original['object_id']
    paragraphs = [original['text']] if 'text' in original else list(original['paragraphs'])
    if not isinstance(edits, list):
        return reject('READER_CORRECTION_EDIT_FIELDS_INVALID', identifier)
    spans: dict[int, list[tuple[int, int, str]]] = {}
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'paragraph_index', 'old_text', 'new_text'}:
            return reject('READER_CORRECTION_EDIT_FIELDS_INVALID', identifier)
        index, old, new = edit['paragraph_index'], edit['old_text'], edit['new_text']
        if type(index) is not int or not 0 <= index < len(paragraphs):
            return reject('READER_CORRECTION_PARAGRAPH_INVALID', identifier)
        if not isinstance(old, str) or not old.strip() or not isinstance(new, str):
            return reject('READER_CORRECTION_TEXT_INVALID', identifier)
        # Conservative sentence boundary: decimals do not match. If an
        # abbreviation matches, request a smaller clause anchor instead.
        if any(re.search(r"[.!?][\"'’”)]*\s+\S", text) for text in (old, new)):
            return reject('READER_CORRECTION_SENTENCE_SCOPE_INVALID', identifier)
        text = paragraphs[index]
        start = text.find(old)
        if start < 0 or text.find(old, start + 1) >= 0:
            return reject('READER_CORRECTION_ANCHOR_INVALID', identifier)
        end = start + len(old)
        existing = spans.setdefault(index, [])
        if any(start < prior_end and prior_start < end for prior_start, prior_end, _ in existing):
            return reject('READER_CORRECTION_OVERLAP_INVALID', identifier)
        existing.append((start, end, new))
    # Resolve every anchor against the unchanged original, then merge from
    # right to left so one edit cannot change another edit's location.
    for index, paragraph_spans in spans.items():
        for start, end, new in sorted(paragraph_spans, reverse=True):
            paragraphs[index] = paragraphs[index][:start] + new + paragraphs[index][end:]
    if any(not text.strip() for text in paragraphs):
        return reject('READER_CORRECTION_TEXT_INVALID', identifier)
    diagnostic: dict = {}
    if not validate_summary_fragment(' '.join(paragraphs), canonical_text=canonical,
                                     allow_paraphrase=True, semantic_review_required=True,
                                     diagnostics=diagnostic):
        return reject('READER_CORRECTION_' + diagnostic.get('reason', 'TEXT_INVALID'), identifier)
    return paragraphs


def apply_reader_corrections(payload: dict, response: object, targets: set[str],
                             *, issues: list[dict],
                             assessment: dict[str, object] | None = None) -> dict | None:
    """Merge exact text patches per record; the model cannot alter evidence or other records.

    Each patch stands alone: an unusable patch is reported and dropped, and its
    record keeps its current text, while valid patches for other records merge.
    New numbers and dates must already appear in the record's text or, when the
    assessment is supplied, in the admitted evidence the record cites. Returns
    None when the response is malformed or no patch could be applied.
    """
    def reject(code: str, identifier: str = 'reader') -> None:
        issues.append({'object_id': identifier, 'reason_codes': [code], 'explanation': code})

    if not isinstance(response, dict) or set(response) != {'corrections'} or not isinstance(response['corrections'], list):
        reject('READER_CORRECTION_FORMAT_INVALID')
        return None
    records = {record['object_id']: record for record in reader_records(payload)
               if isinstance(record.get('object_id'), str)}
    support = reader_support_records(assessment) if isinstance(assessment, dict) else {}
    patches: dict[str, list[str]] = {}
    seen: set[str] = set()
    duplicated: set[str] = set()
    for patch in response['corrections']:
        if not isinstance(patch, dict) or set(patch) != {'object_id', 'edits'}:
            identifier = patch.get('object_id') if isinstance(patch, dict) else None
            reject('READER_CORRECTION_FIELDS_INVALID', identifier if isinstance(identifier, str) else 'reader')
            if isinstance(identifier, str):
                if identifier in seen:
                    duplicated.add(identifier)
                seen.add(identifier)
            continue
        identifier = patch['object_id']
        if not isinstance(identifier, str) or identifier not in targets or identifier not in records:
            reject('READER_CORRECTION_TARGET_INVALID', identifier if isinstance(identifier, str) else 'reader')
            continue
        if identifier in seen:
            # Two patches for one record are ambiguous; neither is applied.
            reject('READER_CORRECTION_TARGET_INVALID', identifier)
            duplicated.add(identifier)
            continue
        seen.add(identifier)
        original = records[identifier]
        canonical: list[object] = [_reader_record_text(original)]
        refs = original.get('evidence_ids')
        if isinstance(refs, list):
            canonical.extend(support[ref] for ref in refs if isinstance(ref, str) and ref in support)
        paragraphs = _corrected_paragraphs(original, patch['edits'], canonical, reject)
        if paragraphs is not None:
            patches[identifier] = paragraphs
    for identifier in duplicated:
        patches.pop(identifier, None)
    if not targets <= seen:
        reject('READER_CORRECTION_TARGETS_MISSING')
    if not patches:
        return None
    corrected = deepcopy(payload)
    for key in ('summary_paragraphs', 'assessment_narratives'):
        for record in corrected[key] if isinstance(corrected.get(key), list) else []:
            if isinstance(record, dict) and record.get('object_id') in patches:
                if key == 'summary_paragraphs':
                    record['text'] = patches[record['object_id']][0]
                else:
                    record['paragraphs'] = patches[record['object_id']]
    return corrected


def review_display_text(texts: list[str], issue: dict) -> list[str] | None:
    """Apply an explicit review disposition; originals remain in the audit record."""
    disposition = issue.get('disposition')
    quote, note = issue.get('quoted_text'), issue.get('verification_note')
    if (not isinstance(disposition, str) or disposition not in {'verify', 'omit_sentence'} or not isinstance(note, str)
            or not note.strip() or len(note) > 600 or not isinstance(quote, str)
            or not quote.strip() or sum(text.count(quote) for text in texts) != 1):
        return None
    result = list(texts)
    index = next(i for i, text in enumerate(texts) if quote in text)
    text = texts[index]
    if disposition == 'omit_sentence':
        # Only an exact whole sentence is removable; ambiguous boundaries stay closed.
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        if quote not in sentences or not any(part != quote and part.strip() for part in sentences):
            return None
        text = ' '.join(part for part in sentences if part != quote)
        marker = 'Sentence withheld. Verify before sharing: '
    else:
        marker = 'Verify before sharing: '
    result[index] = text + ' [' + marker + note.strip() + ']'
    return result


def valid_reader_revision(review: dict, final_reader: object) -> bool:
    """Reject incomplete diagnostics before spending the single text correction.

    Several issues may target one record; each must anchor its own quote.
    """
    if review.get('verdict') != 'revise':
        return False
    issues, identifiers, codes = (review.get(key) for key in ('issues', 'object_ids', 'reason_codes'))
    if not all(isinstance(value, list) and 0 < len(value) <= 12
               for value in (issues, identifiers, codes)):
        return False
    if (not all(isinstance(identifier, str) for identifier in identifiers)
            or len(set(identifiers)) != len(identifiers)
            or not all(isinstance(code, str) and code in SEMANTIC_REVIEW_REASON_CODES for code in codes)):
        return False
    # The Summary must be well formed; malformed findings are already withheld by
    # the precheck, so an issue can only anchor in a finding that is an object.
    if (not isinstance(final_reader, dict) or not isinstance(final_reader.get("summary_paragraphs"), list)
            or not all(isinstance(r, dict) for r in final_reader["summary_paragraphs"])):
        return False
    records = {}
    for record in reader_records(final_reader):
        identifier = record.get("object_id")
        if isinstance(identifier, str):
            records[identifier] = record
    issue_ids, issue_codes = [], set()
    for issue in issues:
        if (not isinstance(issue, dict) or not isinstance(issue.get('object_id'), str)
                or not isinstance(issue.get('explanation'), str) or not issue['explanation'].strip()
                or not isinstance(issue.get('quoted_text'), str) or not issue['quoted_text'].strip()
                or not isinstance(issue.get('reason_codes'), list) or not issue['reason_codes']
                or not all(isinstance(code, str) and code in SEMANTIC_REVIEW_REASON_CODES
                           for code in issue['reason_codes'])):
            return False
        if 'severity' in issue and (issue['severity'] not in ('minor', 'consequential')
                or not isinstance(issue.get('decision_impact'), str) or not issue['decision_impact'].strip()):
            return False
        if 'disposition' in issue and (not isinstance(issue['disposition'], str)
                or issue['disposition'] not in {'verify', 'omit_sentence', 'withhold'}
                or issue.get('severity') not in ('minor', 'consequential')
                or not isinstance(issue.get('verification_note'), str)
                or not issue['verification_note'].strip() or len(issue['verification_note']) > 600):
            return False
        record = records.get(issue['object_id'])
        if record is None:
            return False
        texts = ([record.get('text')] if isinstance(record.get('text'), str)
                 else record.get('paragraphs'))
        if (not isinstance(texts, list)
                or not all(isinstance(text, str) for text in texts)
                or sum(issue['quoted_text'] in text for text in texts) != 1
                or not all(text.find(issue['quoted_text']) == text.rfind(issue['quoted_text'])
                           for text in texts)):
            return False
        issue_ids.append(issue['object_id'])
        issue_codes.update(issue['reason_codes'])
    # Complete anchored findings control disposition; surplus aggregate codes remain
    # visible metadata warnings. A record may carry several anchored issues, but the
    # aggregate object_ids list names each record once.
    return set(issue_ids) == set(identifiers) and issue_codes <= set(codes)


_NARRATIVE_IDS = frozenset({'NARR-design', 'NARR-dividends', 'NARR-inclusion'})


def narrative_only_block(review: object) -> set[str] | None:
    """Finding IDs a block verdict names when it names nothing else, else None.

    A block is confined to findings only when object_ids is a non-empty list of
    finding IDs and every issue is an object naming a finding ID. A block that
    names a Summary record, an unknown target or no target stays a full block.
    """
    if not isinstance(review, dict) or review.get('verdict') != 'block':
        return None
    identifiers, issues = review.get('object_ids'), review.get('issues', [])
    if (not isinstance(identifiers, list) or not identifiers or not isinstance(issues, list)
            or not all(isinstance(identifier, str) and identifier in _NARRATIVE_IDS
                       for identifier in identifiers)
            or not all(isinstance(issue, dict) and issue.get('object_id') in _NARRATIVE_IDS
                       for issue in issues)):
        return None
    return set(identifiers) | {issue['object_id'] for issue in issues}


def reviewed_final_reader(payload: object, review: object, assessment: dict[str, object]) -> tuple[list[str], list[dict]]:
    """Keep reviewed usable sections; a partial review never certifies publication.

    Admission is per record. The Summary is admitted when every Summary record
    passes the precheck and none is withheld by review, whatever happens to the
    narratives; each narrative is admitted or dropped on its own. A record that
    fails the precheck is never admitted, whatever the review says. A block
    that names only findings withholds those findings; any other block
    withholds everything.
    """
    checked = validate_final_reader_records(payload, assessment)
    summary, narratives = checked['summary'], checked['narratives']
    if not checked['structure_valid'] or (not summary and not narratives) or not isinstance(review, dict):
        return [], []
    blocked = narrative_only_block(review)
    if blocked is not None:
        return list(summary), [record for record in deepcopy(narratives) if record['object_id'] not in blocked]
    if review.get('verdict') == 'pass':
        return (list(summary), list(narratives)) if all(review.get(k) == [] for k in ('object_ids', 'reason_codes', 'issues')) else ([], [])
    if not valid_reader_revision(review, payload):
        return [], []
    summary = list(summary)
    narratives = deepcopy(narratives)
    withheld = set()
    for issue in review['issues']:
        identifier = issue['object_id']
        if identifier.startswith('SUM-'):
            if not summary:
                continue  # Already withheld by the precheck.
            index = next(i for i, record in enumerate(payload['summary_paragraphs']) if record['object_id'] == identifier)
            changed = review_display_text([summary[index]], issue)
            if changed is not None:
                summary[index] = changed[0]
            elif issue.get('severity') != 'minor' or 'disposition' in issue:
                withheld.add(identifier)
        else:
            record = next((record for record in narratives if record['object_id'] == identifier), None)
            if record is None:
                continue  # Dropped by the precheck.
            changed = review_display_text(record['paragraphs'], issue)
            if changed is not None:
                record['paragraphs'] = changed
            elif issue.get('severity') != 'minor' or 'disposition' in issue:
                withheld.add(identifier)
    # Preserve the opening's balance when an entire argument cannot stand alone.
    if any(identifier.startswith('SUM-') for identifier in withheld):
        summary = []
    return summary, [record for record in narratives if record['object_id'] not in withheld]


def reader_review_notice(payload: object, review: object, assessment: dict[str, object]) -> str:
    """One honest status notice shared by browser, exports and saved reader hashing."""
    if (isinstance(review, dict) and review.get('verdict') == 'pass'
            and all(review.get(k) == [] for k in ('object_ids', 'reason_codes', 'issues'))
            and all(validate_final_reader(payload, assessment))):
        return ''
    summary, narratives = reviewed_final_reader(payload, review, assessment)
    if not summary and not narratives:
        return 'Automated narrative review did not establish usable prose. Source-based findings are shown where available; human review is required.'
    labels = {'SUM': 'opening', 'NARR-design': 'climate risks and delivery',
              'NARR-dividends': 'peace and social dividends', 'NARR-inclusion': 'fair benefits'}
    minor, consequential, marked = [], [], []
    blocked = narrative_only_block(review) or set()
    entries = list(review.get('issues') or [])
    entries += [{'object_id': identifier} for identifier in sorted(blocked)
                if not any(issue['object_id'] == identifier for issue in entries)]
    for issue in entries:
        label = labels['SUM'] if issue['object_id'].startswith('SUM-') else labels.get(issue['object_id'], 'findings')
        retained = (bool(summary) if issue['object_id'].startswith('SUM-') else
                    any(record['object_id'] == issue['object_id'] for record in narratives))
        target = (consequential if issue['object_id'] in blocked else
                  marked if retained and issue.get('disposition') in {'verify', 'omit_sentence'} else
                  minor if issue.get('severity') == 'minor' else consequential)
        if label not in target:
            target.append(label)
    messages = []
    if marked:
        messages.append('Verification notes identify unresolved claims in ' + ', '.join(marked) + '; human source review is required before sharing.')
    if minor:
        messages.append('Minor uncertainties remain in ' + ', '.join(minor) + '; the narrative is retained for human review.')
    if consequential:
        messages.append('Potentially consequential claims need source confirmation in ' + ', '.join(consequential) + '; the affected narrative is withheld, while other reviewed sections remain available.')
    issue_codes = {code for issue in entries
                   for code in (issue.get('reason_codes') if isinstance(issue.get('reason_codes'), list) else [])}
    review_codes = review.get('reason_codes') if isinstance(review.get('reason_codes'), list) else []
    if issue_codes != set(review_codes):
        messages.append('Automated review metadata is inconsistent; confirm the findings against the sources before sharing.')
    return ' '.join(messages)
