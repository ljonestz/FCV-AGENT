"""Recommendation details keep readable qualifications and hide machine metadata."""
from copy import deepcopy
from html import escape
from io import BytesIO
import json
import re
import subprocess

from docx import Document

from sector_lenses.climate_verified_render import build_reader_model, render_reader_html, write_reader_docx
from sector_lenses.climate_verified_prompts import _recommendation_prompt
from tests.test_climate_verified_render import _assessment
from tests.test_climate_lens_frontend import INDEX, _extract_js_function, _js_escape_helper


def _model():
    assessment = _assessment()
    assessment['operation_context'] = {'document_type': 'PCN', 'instrument_type': 'IPF'}
    assessment['priorities'] = assessment['priorities'][:1]
    priority = assessment['priorities'][0]
    priority.update(
        narrative='Flood-season access needs attention.\n\nRevise the PCN implementation arrangements to identify continuity responsibilities.',
        limitation='Detailed arrangements may follow later in preparation. Keep unresolved responsibilities explicit.',
        caution='Confirm funding coverage with the task team. Do not assume that any asset is excluded.',
        enhanced_action='Prepare a site-level continuity map.',
        enhanced_activation='If the site list and access information become available.',
    )
    return assessment, build_reader_model(assessment)


def test_html_and_word_details_keep_qualifications_without_the_field_dump():
    assessment, model = _model()
    before = deepcopy(model)
    page = render_reader_html(model)
    detail = re.search(r'<details class="climate-priority-detail">(.*?)</details>', page, re.S).group(1)
    output = BytesIO()
    write_reader_docx(model, output)
    paragraphs = [p.text for p in Document(output).paragraphs]
    start = paragraphs.index('Recommendation details')
    end = paragraphs.index('Points to check before the applicable review')
    word = '\n'.join(paragraphs[start:end])
    priority = model['priorities'][0]
    for text in (detail, word):
        for value in (priority['limitation'], priority['caution'], priority['enhanced_action'], priority['enhanced_activation']):
            assert value in text
        for label in ('Minimum action:', 'Decision:', 'Completion evidence:', 'Completion evidence status:',
                      'Limitation:', 'Caution:', 'Guidance basis:', 'Drafting status:',
                      'Where this fits in the project cycle', 'updated_section', 'GUIDE-PCN-DESIGN'):
            assert label not in text
        assert 'Suggested targeted text for the current project document.' in text
        assert 'PCN' in text and 'Project Description' in text
        assert 'Confidence' in text and 'medium' in text
    assert '<p class="climate-priority-detail-prose">' + escape(priority['limitation']) + '</p>' in detail
    assert model == before
    assert assessment['priorities'][0]['completion_evidence_status'] == 'updated_section'


def test_details_do_not_repeat_qualifications_already_visible_or_conditional_work():
    _, model = _model()
    priority = model['priorities'][0]
    priority['narrative'] += '\n\n' + priority['limitation'] + '\n\n' + priority['enhanced_action'] + ' ' + priority['enhanced_activation']
    detail = re.search(r'<details class="climate-priority-detail">(.*?)</details>', render_reader_html(model), re.S).group(1)
    assert priority['limitation'] not in detail
    assert priority['enhanced_action'] not in detail
    assert priority['caution'] in detail


def test_browser_details_match_the_export_content_and_escape_prose():
    _, model = _model()
    model['priorities'][0]['caution'] += ' Preserve <community> access & qualifications.'
    source = INDEX.read_text(encoding='utf-8')
    helpers = '\n'.join(_extract_js_function(source, name) for name in (
        'renderPriorityProjectCycle', 'climateAccessibleRouteValue', 'climateDraftingRouteGate',
        'climateSummaryWatchItems', 'renderClimateVerifiedAssessment'))
    script = _js_escape_helper() + '\nconst renderClimateRelevantGuidance=()=>"";\n' + helpers + '\n' + rf'''
const reader={json.dumps(model)};
const html=renderClimateVerifiedAssessment(reader);
const detail=html.match(/<details class="climate-priority-detail">([\s\S]*?)<\/details>/)[1];
for(const expected of ['climate-priority-detail-prose','Detailed arrangements may follow','Do not assume that any asset is excluded.',
  'Prepare a site-level continuity map.','If the site list and access information become available.',
  '&lt;community&gt; access &amp; qualifications.','Suggested targeted text for the current project document.']){{
 if(!detail.includes(expected))throw new Error('Missing '+expected);
}}
for(const omitted of ['Minimum action:','Recommendation:','Limitation:','Caution:','How to confirm completion:',
  'Where this fits in the project cycle','updated_section','GUIDE-PCN-DESIGN','<community>']){{
 if(detail.includes(omitted))throw new Error('Unwanted field dump '+omitted);
}}
'''
    result = subprocess.run(['node', '-'], input=script, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr


def test_generation_uses_existing_fields_for_complementary_detail_prose():
    prompt = ' '.join(_recommendation_prompt({}).split())
    assert 'Recommendation details' in prompt
    assert 'complementary paragraphs' in prompt
    assert 'Do not repeat the visible action' in prompt
