"""Native review contracts preserve analysis while exposing factual decisions."""
from sector_lenses.climate_verified_schemas import stage_output_schema
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt


def test_core_review_requires_explicit_premise_decisions():
    schema = stage_output_schema('conditional_review')
    assert 'core_reviews' in schema['required']
    record = schema['properties']['core_reviews']['items']
    assert set(record['required']) == {
        'recommendation_id', 'premise_verdict', 'source_block_ids',
        'reason_codes', 'explanation',
    }
    assert set(record['properties']['premise_verdict']['enum']) == {
        'supported', 'qualified', 'unsupported',
    }


def test_reader_objection_is_anchored_without_inheriting_core_checks():
    reader = stage_output_schema('reader_review')
    core = stage_output_schema('conditional_review')
    assert 'core_reviews' not in reader['properties']
    assert 'quoted_text' in reader['properties']['issues']['items']['required']
    for schema in (reader, core):
        assert {'quoted_text', 'disposition', 'verification_note'} <= set(schema['properties']['issues']['items']['required'])


def test_explicit_review_retains_qualified_analysis_and_proposals():
    core = build_verified_stage_prompt('conditional_review', {})
    reader = build_verified_stage_prompt('reader_review', {})
    assert 'core_reviews' in core
    assert 'Core recommendations contain no proposed wording' not in core
    assert 'qualified' in core
    assert 'Proposed actions need not already exist' in core
    assert 'quoted_text' in reader
    assert 'do not require impacts to be proven' in reader.lower()


def test_explicit_scope_change_proposal_is_not_treated_as_existing_scope():
    prompt = ' '.join(build_verified_stage_prompt('conditional_review', {}).split())
    assert "An explicit proposal to extend a study's scope" in prompt
    assert 'feasibility and authority' in prompt
