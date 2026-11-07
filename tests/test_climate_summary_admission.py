"""Per-record admission of the climate final reader.

Replays trimmed traces from two paid runs that lost a clean Summary because a
narrative (Afghanistan) or a missing sibling citation (Honduras) failed the
deterministic precheck, plus one run that already succeeded (2026-10-27).
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from sector_lenses.climate_final_reader import (
    apply_reader_corrections,
    bind_same_passage_project_references,
    bind_same_summary_number_references,
    normalize_reader_paragraphs,
    reviewed_final_reader,
    valid_reader_revision,
    validate_final_reader,
    validate_final_reader_records,
)
from sector_lenses.climate_verified_pipeline import PipelineClients, run_verified_climate_pipeline
from tests.test_climate_verified_pipeline import (
    FakeClient,
    _arguments,
    _final_reader,
    _native_pass_review,
    _responses,
)

FIXTURES = Path(__file__).parent / 'fixtures' / 'climate' / 'final_reader_admission'


def _load(name: str) -> dict:
    return json.loads((FIXTURES / f'{name}.json').read_text(encoding='utf-8'))


def _prepared_reader(fixture: dict) -> dict:
    """Apply the deterministic pre-review steps the pipeline applies."""
    assessment = fixture['reader_assessment']
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    reader, _ = bind_same_passage_project_references(reader, assessment)
    reader, _ = bind_same_summary_number_references(reader, assessment)
    return reader


def _ids(records: list[dict]) -> list[str]:
    return [record['object_id'] for record in records]


# Afghanistan, 2026-11-07: NARR-inclusion fails on '1,000'; Summary is clean.

def test_afghanistan_precheck_reports_each_record_separately():
    fixture = _load('afghanistan_20261107')
    reader, assessment = fixture['initial_final_reader'], fixture['reader_assessment']
    issues: list[dict] = []
    result = validate_final_reader_records(reader, assessment, issues=issues)
    assert result['structure_valid']
    assert result['record_status'] == {
        'SUM-001': True, 'SUM-002': True,
        'NARR-design': True, 'NARR-dividends': True, 'NARR-inclusion': False,
    }
    assert result['summary'][0].startswith('The project already builds climate thinking')
    assert _ids(result['narratives']) == ['NARR-design', 'NARR-dividends']
    assert issues == fixture['prechecks'][0]['issues']
    # The legacy all-or-nothing contract stays available to existing callers.
    assert validate_final_reader(reader, assessment) == ([], [])


def test_afghanistan_first_review_admits_summary_and_drops_failing_narrative():
    fixture = _load('afghanistan_20261107')
    reader = _prepared_reader(fixture)
    summary, narratives = reviewed_final_reader(
        reader, fixture['meaning_reviews'][0], fixture['reader_assessment'])
    assert len(summary) == 2
    assert summary[0].startswith('The project already builds climate thinking')
    assert _ids(narratives) == ['NARR-design', 'NARR-dividends']


def test_afghanistan_correction_merges_with_numbers_from_cited_evidence():
    fixture = _load('afghanistan_20261107')
    reader = _prepared_reader(fixture)
    issues: list[dict] = []
    merged = apply_reader_corrections(
        reader, fixture['correction']['response'],
        set(fixture['correction']['target_ids']), issues=issues,
        assessment=fixture['reader_assessment'])
    assert merged is not None
    assert issues == []
    narratives = {record['object_id']: record for record in merged['assessment_narratives']}
    assert 'Subcomponent 1.3' in narratives['NARR-dividends']['paragraphs'][0]
    assert '1,000' not in ' '.join(narratives['NARR-inclusion']['paragraphs'])
    assert merged['summary_paragraphs'] == reader['summary_paragraphs']
    status = validate_final_reader_records(merged, fixture['reader_assessment'])['record_status']
    assert all(status.values())


def test_afghanistan_one_bad_patch_does_not_discard_the_others():
    fixture = _load('afghanistan_20261107')
    reader = _prepared_reader(fixture)
    response = deepcopy(fixture['correction']['response'])
    # Reintroduce a number found in no cited evidence for NARR-dividends only.
    edit = response['corrections'][1]['edits'][0]
    edit['new_text'] = edit['new_text'].replace('Subcomponent 1.3', 'Subcomponent 9.7')
    issues: list[dict] = []
    merged = apply_reader_corrections(
        reader, response, set(fixture['correction']['target_ids']), issues=issues,
        assessment=fixture['reader_assessment'])
    assert merged is not None
    assert [(issue['object_id'], issue['reason_codes']) for issue in issues] == [
        ('NARR-dividends', ['READER_CORRECTION_SUMMARY_NUMBER_UNSUPPORTED'])]
    narratives = {record['object_id']: record for record in merged['assessment_narratives']}
    original = {record['object_id']: record for record in reader['assessment_narratives']}
    assert narratives['NARR-dividends'] == original['NARR-dividends']
    assert narratives['NARR-design'] != original['NARR-design']
    assert '1,000' not in ' '.join(narratives['NARR-inclusion']['paragraphs'])


# Honduras, 2026-10-18: SUM-002 cites no fact containing '46'; review had two
# issues on NARR-inclusion.

def test_honduras_number_binding_prefers_the_sibling_cited_fact():
    fixture = _load('honduras_20261018')
    assessment = fixture['reader_assessment']
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    bound, added = bind_same_summary_number_references(reader, assessment)
    assert added == 1
    # PF-003 (cited by SUM-001) and PF-042 (uncited) both contain 46.
    assert bound['summary_paragraphs'][1]['evidence_ids'][-1] == 'PF-003'
    assert 'PF-042' not in bound['summary_paragraphs'][1]['evidence_ids']
    assert bound['summary_paragraphs'][1]['text'] == reader['summary_paragraphs'][1]['text']
    assert all(validate_final_reader_records(bound, assessment)['record_status'].values())
    assert reader['summary_paragraphs'][1]['evidence_ids'][-1] != 'PF-003'


def test_honduras_number_binding_refuses_ambiguous_candidates():
    fixture = _load('honduras_20261018')
    assessment = fixture['reader_assessment']
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    # Without a sibling citation, PF-003 and PF-042 are equally plausible.
    for record in reader['summary_paragraphs'] + reader['assessment_narratives']:
        record['evidence_ids'] = [ref for ref in record['evidence_ids'] if ref != 'PF-003']
    bound, added = bind_same_summary_number_references(reader, assessment)
    assert added == 0
    assert bound == reader


def test_honduras_review_with_two_issues_on_one_record_is_a_valid_revision():
    fixture = _load('honduras_20261018')
    reader = _prepared_reader(fixture)
    review = fixture['meaning_reviews'][0]
    assert [issue['object_id'] for issue in review['issues']].count('NARR-inclusion') == 2
    assert valid_reader_revision(review, reader)
    summary, narratives = reviewed_final_reader(reader, review, fixture['reader_assessment'])
    assert len(summary) == 2
    assert summary[0].startswith('The project already recognizes that flooding is its most significant risk')
    assert _ids(narratives) == ['NARR-design', 'NARR-dividends', 'NARR-inclusion']
    inclusion = ' '.join(narratives[2]['paragraphs'])
    assert inclusion.count('[Verify before sharing:') == 2


def test_revision_still_requires_unique_object_ids_and_full_coverage():
    fixture = _load('honduras_20261018')
    reader = _prepared_reader(fixture)
    review = deepcopy(fixture['meaning_reviews'][0])
    review['object_ids'] = ['NARR-design', 'NARR-inclusion', 'NARR-inclusion']
    assert not valid_reader_revision(review, reader)
    review['object_ids'] = ['NARR-design']
    assert not valid_reader_revision(review, reader)


# 2026-10-27 success case must keep passing.

def test_success_case_still_admits_everything():
    fixture = _load('success_20261027')
    assessment = fixture['reader_assessment']
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    assert bind_same_summary_number_references(reader, assessment) == (reader, 0)
    summary, narratives = validate_final_reader(reader, assessment)
    assert summary and len(narratives) == 3
    summary, narratives = reviewed_final_reader(reader, fixture['meaning_reviews'][0], assessment)
    assert len(summary) == len(reader['summary_paragraphs'])
    assert _ids(narratives) == ['NARR-design', 'NARR-dividends', 'NARR-inclusion']


# Precedence rules on synthetic records.

def test_precheck_failure_is_never_admitted_even_with_a_clean_review():
    fixture = _load('afghanistan_20261107')
    reader = _prepared_reader(fixture)
    clean = {'verdict': 'pass', 'object_ids': [], 'reason_codes': [], 'issues': []}
    summary, narratives = reviewed_final_reader(reader, clean, fixture['reader_assessment'])
    assert summary
    assert 'NARR-inclusion' not in _ids(narratives)


def test_withheld_summary_record_empties_the_summary_only():
    fixture = _load('success_20261027')
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    review = deepcopy(fixture['meaning_reviews'][0])
    review['issues'][0]['severity'] = 'consequential'
    review['issues'][0]['quoted_text'] = 'not present anywhere in the summary'
    review['issues'][0].pop('disposition')
    review['issues'][0].pop('verification_note')
    assert not valid_reader_revision(review, reader)
    review = deepcopy(fixture['meaning_reviews'][0])
    review['issues'][0].update(severity='consequential', disposition='withhold')
    summary, narratives = reviewed_final_reader(reader, review, fixture['reader_assessment'])
    assert summary == []
    assert _ids(narratives) == ['NARR-design', 'NARR-dividends', 'NARR-inclusion']


def test_failing_summary_record_withholds_summary_but_keeps_reviewed_narratives():
    fixture = _load('success_20261027')
    assessment = fixture['reader_assessment']
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    reader['summary_paragraphs'][1]['text'] += ' About 987654 people are affected.'
    clean = {'verdict': 'pass', 'object_ids': [], 'reason_codes': [], 'issues': []}
    summary, narratives = reviewed_final_reader(reader, clean, assessment)
    assert summary == []
    assert len(narratives) == 3


# Pipeline loop on the synthetic harness.

def _reader_with_unsupported_inclusion_number() -> dict:
    final = _final_reader()
    final['assessment_narratives'][2]['paragraphs'][0] += ' About 987654 traders benefit.'
    return final


def _inclusion_patch() -> dict:
    return {'object_id': 'NARR-inclusion', 'edits': [{
        'paragraph_index': 0, 'old_text': ' About 987654 traders benefit.', 'new_text': ''}]}


def test_pipeline_keeps_summary_when_correction_provider_fails():
    responses = _responses()
    responses[2]['reader_contract'] = 'final-reader-v1'

    def unavailable(**kwargs):
        raise ConnectionError('Provider unavailable')

    assessment = FakeClient(responses + [_reader_with_unsupported_inclusion_number(), unavailable], [])
    reviewer = FakeClient([_native_pass_review] * 3, [])
    result = run_verified_climate_pipeline(**_arguments(), clients=PipelineClients(assessment, reviewer))
    assert result['summary_overview_status'] == 'generated'
    assert result['summary_overview']['paragraphs']
    assert _ids(result['assessment_narratives']) == ['NARR-design', 'NARR-dividends']
    assert [call['stage'] for call in reviewer.calls].count('reader_review') == 1
    assert 'FINAL_READER_CORRECTION_UNAVAILABLE' in result['validation']['reason_codes']
    assert len(result['priorities']) == 1


def test_pipeline_merges_valid_patches_and_rereviews_once():
    responses = _responses()
    responses[2]['reader_contract'] = 'final-reader-v1'
    bad_dividends = {'object_id': 'NARR-dividends', 'edits': [{
        'paragraph_index': 0, 'old_text': 'The project', 'new_text': 'The project with 987655 sites'}]}
    review = {'verdict': 'revise', 'object_ids': ['NARR-dividends'],
              'reason_codes': ['PROJECT_FACT_UNSUPPORTED'], 'issues': [{
                  'object_id': 'NARR-dividends', 'reason_codes': ['PROJECT_FACT_UNSUPPORTED'],
                  'quoted_text': 'Verdict and foundation: The project recognizes',
                  'explanation': 'Keep the benefit conditional.'}]}
    assessment = FakeClient(responses + [
        _reader_with_unsupported_inclusion_number(),
        {'corrections': [bad_dividends, _inclusion_patch()]}], [])
    reviewer = FakeClient([_native_pass_review, review, _native_pass_review], [])
    result = run_verified_climate_pipeline(**_arguments(), clients=PipelineClients(assessment, reviewer))
    assert result['summary_overview_status'] == 'generated'
    assert '987654' not in json.dumps(result['final_reader'])
    assert '987655' not in json.dumps(result['final_reader'])
    trace = result['diagnostic_trace']['final_reader']
    assert [(i['object_id'], i['reason_codes']) for i in trace['correction']['issues']] == [
        ('NARR-dividends', ['READER_CORRECTION_SUMMARY_NUMBER_UNSUPPORTED'])]
    assert [call['stage'] for call in reviewer.calls].count('reader_review') == 2
    assert [call['stage'] for call in assessment.calls].count('reader_correction') == 1
    assert len(result['assessment_narratives']) == 3


@pytest.mark.parametrize('second_review_fails', [False, True])
def test_pipeline_reviews_partially_failing_reader_after_correction(second_review_fails):
    responses = _responses()
    responses[2]['reader_contract'] = 'final-reader-v1'
    # The patch targets NARR-inclusion but leaves the unsupported number.
    noop = {'object_id': 'NARR-inclusion', 'edits': [{
        'paragraph_index': 0, 'old_text': 'About 987654 traders', 'new_text': 'Around 987654 traders'}]}
    assessment = FakeClient(responses + [_reader_with_unsupported_inclusion_number(),
                                         {'corrections': [noop]}], [])

    def failing(**kwargs):
        raise ConnectionError('Provider unavailable')

    reviewer = FakeClient([_native_pass_review, _native_pass_review,
                           failing if second_review_fails else _native_pass_review], [])
    result = run_verified_climate_pipeline(**_arguments(), clients=PipelineClients(assessment, reviewer))
    assert result['summary_overview_status'] == 'generated'
    assert _ids(result['assessment_narratives']) == ['NARR-design', 'NARR-dividends']
    assert [call['stage'] for call in assessment.calls].count('reader_correction') == 1


# Saved sessions: the reader status follows admission recomputed on load.

def test_saved_fallback_status_follows_recomputed_admission():
    from sector_lenses.climate_verified_render import build_reader_model
    responses = _responses()
    responses[2]['reader_contract'] = 'final-reader-v1'
    result = run_verified_climate_pipeline(**_arguments(), clients=PipelineClients(
        FakeClient(responses + [_final_reader()], []), FakeClient([_native_pass_review] * 2, [])))
    assert result['summary_overview_status'] == 'generated'
    # A session saved when older rules withheld this Summary recorded 'fallback'.
    saved = {**result, 'summary_overview_status': 'fallback'}
    assert build_reader_model(saved)['summary_overview_status'] == 'generated'
    # A review that does not admit the Summary still yields the fallback.
    blocked = {**saved, 'reader_review': {'verdict': 'block'}}
    assert build_reader_model(blocked)['summary_overview_status'] == 'fallback'


# Malformed findings withhold the findings only; a malformed Summary fails all.

_CLEAN = {'verdict': 'pass', 'object_ids': [], 'reason_codes': [], 'issues': []}


def _malformed_findings(narratives: list, case: str) -> object:
    if case == 'two':
        return narratives[:2]
    if case == 'four':
        return narratives + [deepcopy(narratives[0])]
    if case == 'non_dict':
        return [narratives[0], 'not a record', narratives[2]]
    return {'NARR-design': narratives[0]}


@pytest.mark.parametrize('case', ['two', 'four', 'non_dict', 'not_list'])
def test_malformed_findings_still_admit_a_clean_reviewed_summary(case):
    fixture = _load('success_20261027')
    assessment = fixture['reader_assessment']
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    reader['assessment_narratives'] = _malformed_findings(reader['assessment_narratives'], case)
    issues: list[dict] = []
    checked = validate_final_reader_records(reader, assessment, issues=issues)
    assert checked['structure_valid']
    assert checked['summary'] and checked['narratives'] == []
    assert checked['record_status']['reader-narratives'] is False
    assert ('reader', ['READER_STRUCTURE_INVALID']) in [
        (issue['object_id'], issue['reason_codes']) for issue in issues]
    # The all-or-nothing wrapper still refuses the whole reader.
    assert validate_final_reader(reader, assessment) == ([], [])
    summary, narratives = reviewed_final_reader(reader, _CLEAN, assessment)
    assert len(summary) == len(reader['summary_paragraphs'])
    assert narratives == []


@pytest.mark.parametrize('case', ['non_dict', 'wrong_id', 'not_list'])
def test_malformed_summary_still_fails_the_whole_reader(case):
    fixture = _load('success_20261027')
    assessment = fixture['reader_assessment']
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    if case == 'non_dict':
        reader['summary_paragraphs'][1] = 'not a record'
    elif case == 'wrong_id':
        reader['summary_paragraphs'][1]['object_id'] = 'SUM-007'
    else:
        reader['summary_paragraphs'] = {'SUM-001': reader['summary_paragraphs'][0]}
    checked = validate_final_reader_records(reader, assessment)
    assert not checked['structure_valid']
    assert reviewed_final_reader(reader, _CLEAN, assessment) == ([], [])


def test_pipeline_reviews_summary_when_compiler_returns_two_findings():
    responses = _responses()
    responses[2]['reader_contract'] = 'final-reader-v1'
    final = _final_reader()
    final['assessment_narratives'] = final['assessment_narratives'][:2]
    assessment = FakeClient(responses + [final], [])
    reviewer = FakeClient([_native_pass_review] * 2, [])
    result = run_verified_climate_pipeline(**_arguments(), clients=PipelineClients(assessment, reviewer))
    assert result['summary_overview_status'] == 'generated'
    assert result['summary_overview']['paragraphs']
    assert result['assessment_narratives'] == []
    assert [call['stage'] for call in reviewer.calls].count('reader_review') == 1
    assert 'reader_correction' not in [call['stage'] for call in assessment.calls]
    assert len(result['priorities']) == 1


# A block that names only findings withholds those findings.

def _block(*identifiers: str, issues: list | None = None) -> dict:
    return {'verdict': 'block', 'object_ids': list(identifiers),
            'reason_codes': ['PROJECT_FACT_UNSUPPORTED'],
            'issues': issues if issues is not None else [
                {'object_id': identifier, 'reason_codes': ['PROJECT_FACT_UNSUPPORTED'],
                 'explanation': 'Unsupported.'} for identifier in identifiers]}


def test_narrative_only_block_keeps_clean_summary_and_other_findings():
    fixture = _load('success_20261027')
    assessment = fixture['reader_assessment']
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    summary, narratives = reviewed_final_reader(reader, _block('NARR-dividends'), assessment)
    assert len(summary) == len(reader['summary_paragraphs'])
    assert _ids(narratives) == ['NARR-design', 'NARR-inclusion']
    summary, narratives = reviewed_final_reader(
        reader, _block('NARR-design', 'NARR-dividends', 'NARR-inclusion'), assessment)
    assert summary and narratives == []


@pytest.mark.parametrize('review', [
    _block('SUM-001'),
    _block('NARR-dividends', 'SUM-002'),
    _block('NARR-dividends', issues=[{'object_id': 'SUM-001', 'reason_codes': ['PROJECT_FACT_UNSUPPORTED'],
                                      'explanation': 'Unsupported.'}]),
    _block(),
    {'verdict': 'block'},
    {'verdict': 'block', 'object_ids': ['NARR-dividends'], 'issues': [{'explanation': 'No target.'}]},
    {'verdict': 'block', 'object_ids': ['NARR-dividends'], 'issues': ['not an object']},
    {'verdict': 'block', 'object_ids': ['NARR-other']},
    {'verdict': 'block', 'object_ids': 'NARR-dividends'},
])
def test_any_other_block_still_withholds_everything(review):
    fixture = _load('success_20261027')
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    assert reviewed_final_reader(reader, review, fixture['reader_assessment']) == ([], [])


def test_narrative_only_block_never_admits_a_summary_that_fails_precheck():
    fixture = _load('success_20261027')
    reader = normalize_reader_paragraphs(fixture['initial_final_reader'])
    reader['summary_paragraphs'][0]['text'] += ' About 987654 people are affected.'
    summary, narratives = reviewed_final_reader(reader, _block('NARR-dividends'), fixture['reader_assessment'])
    assert summary == []
    assert _ids(narratives) == ['NARR-design', 'NARR-inclusion']


def test_pipeline_narrative_only_block_admits_summary_with_notice():
    from sector_lenses.climate_verified_render import build_reader_model
    responses = _responses()
    responses[2]['reader_contract'] = 'final-reader-v1'
    assessment = FakeClient(responses + [_final_reader()], [])
    reviewer = FakeClient([_native_pass_review, _block('NARR-inclusion')], [])
    result = run_verified_climate_pipeline(**_arguments(), clients=PipelineClients(assessment, reviewer))
    assert result['summary_overview_status'] == 'generated'
    assert _ids(result['assessment_narratives']) == ['NARR-design', 'NARR-dividends']
    assert 'FINAL_READER_REVIEW_REQUIRED' in result['validation']['reason_codes']
    assert 'FINAL_READER_WITHHELD' not in result['validation']['reason_codes']
    assert 'reader_correction' not in [call['stage'] for call in assessment.calls]
    notice = build_reader_model(result)['reader_review_notice']
    assert 'fair benefits' in notice and 'withheld' in notice
