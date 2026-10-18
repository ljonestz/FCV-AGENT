"""Source relationships must survive extraction without inventing a scope map."""
from copy import deepcopy

from tests.test_climate_verified_pipeline import (
    FakeClient, _arguments, _responses, _final_reader, _native_pass_review,
)
from sector_lenses.climate_verified_pipeline import PipelineClients, run_verified_climate_pipeline


def test_cited_source_context_reaches_generation_and_reader_without_mutation():
    responses = _responses()
    responses[2]['reader_contract'] = 'final-reader-v1'
    arguments = _arguments()
    before = deepcopy(arguments['source_blocks'])
    assessment = FakeClient(responses + [_final_reader()], [])
    reviewer = FakeClient([_native_pass_review, _native_pass_review], [])
    result = run_verified_climate_pipeline(**arguments, clients=PipelineClients(assessment, reviewer))
    for stage in ('bounded_analysis', 'judgment_review', 'recommendation_compiler',
                  'reader_compiler', 'reader_review'):
        call = next(c for c in assessment.calls + reviewer.calls if c['stage'] == stage)
        passages = call['payload'].get('source_passages', [])
        assert [p['block_id'] for p in passages] == [b.block_id for b in before], stage
        assert [p['text'] for p in passages] == [b.text for b in before], stage
    assert arguments['source_blocks'] == before
    assert 'source_passages' not in result  # Runtime evidence is not new export content.


def test_optional_drafting_receives_the_same_original_scope():
    responses = _responses()
    candidate = responses[3]['recommendation_candidates'][0]
    candidate.pop('current_document_drafting')
    candidate.pop('operational_instrument_drafting')
    assessment = FakeClient(responses + [{'drafting_sets': []}], [])
    arguments = _arguments()
    run_verified_climate_pipeline(**arguments, clients=PipelineClients(
        assessment, FakeClient([_native_pass_review], [])))
    payload = next(c['payload'] for c in assessment.calls if c['stage'] == 'drafting_compiler')
    assert payload['source_passages'][0]['text'] == arguments['source_blocks'][0].text


def test_reader_correction_keeps_source_context_and_still_requires_fresh_review():
    responses = _responses()
    responses[2]['reader_contract'] = 'final-reader-v1'
    assessment = FakeClient(responses + [_final_reader(), {
        'corrections': [{'object_id': 'NARR-dividends', 'edits': []}]}], [])
    reviewer = FakeClient([_native_pass_review, {
        'verdict': 'revise', 'object_ids': ['NARR-dividends'],
        'reason_codes': ['PROJECT_FACT_UNSUPPORTED'], 'issues': [{
            'object_id': 'NARR-dividends', 'reason_codes': ['PROJECT_FACT_UNSUPPORTED'],
            'explanation': 'Check planned status.',
            'quoted_text': _final_reader()['assessment_narratives'][1]['paragraphs'][0]}]},
        {'verdict': 'block', 'object_ids': ['NARR-dividends'],
         'reason_codes': ['PROJECT_FACT_UNSUPPORTED'], 'issues': [{
             'object_id': 'NARR-dividends', 'reason_codes': ['PROJECT_FACT_UNSUPPORTED'],
             'explanation': 'The status remains unsupported.'}]}], [])
    arguments = _arguments()
    result = run_verified_climate_pipeline(**arguments, clients=PipelineClients(assessment, reviewer))
    payload = next(c['payload'] for c in assessment.calls if c['stage'] == 'reader_correction')
    assert payload['source_passages'][0]['text'] == arguments['source_blocks'][0].text
    assert sum(c['stage'] == 'reader_review' for c in reviewer.calls) == 2
    assert result['summary_overview_status'] == 'fallback'


def test_source_context_excludes_uncited_blocks_and_deduplicates_shared_provenance():
    from dataclasses import replace
    from sector_lenses.climate_source_blocks import cited_source_passages
    blocks = _arguments()['source_blocks']
    blocks.append(replace(blocks[0], block_id='UNRELATED', text='Unrelated financing.'))
    facts = [{'claim_id': 'PF-1', 'source_block_ids': [blocks[0].block_id]},
             {'claim_id': 'PF-2', 'source_block_ids': [blocks[0].block_id, 'unknown']}]
    passages = cited_source_passages(facts, blocks)
    assert len(passages) == 1
    assert passages[0]['text'] == blocks[0].text
    passages[0]['text'] = 'mutated'
    assert blocks[0].text != 'mutated'
