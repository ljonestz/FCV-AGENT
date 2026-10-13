"""Simplified report keeps its evidence internally and shows action-led prose."""
from docx import Document

from sector_lenses.climate_verified_prompts import _judgment_prompt, _recommendation_prompt
from sector_lenses.climate_verified_render import _priority_sections, build_reader_model, render_reader_html, write_reader_docx
from tests.test_climate_verified_render import _assessment


def test_simplified_exports_keep_evidence_internal(tmp_path):
    model = build_reader_model(_assessment())
    model['core_questions'] = [{'question': 'Internal evidence question', 'summary': 'Detailed internal finding.'}]
    html = render_reader_html(model)
    path = write_reader_docx(model, tmp_path / 'report.docx')
    word = '\n'.join(p.text for p in Document(path).paragraphs)
    for output in (html, word):
        assert 'Supporting question analysis' not in output
        assert 'Project details behind this assessment' not in output
        assert 'Why this matters' in output
        assert 'What the team could do' in output
    assert 'Recommendation details' in html
    assert model['core_questions'][0]['summary'] == 'Detailed internal finding.'


def test_generation_requests_fluent_context_and_priority_paragraphs():
    judgment = _judgment_prompt({})
    assert 'summarize the four judgments' not in judgment
    assert 'Name relevance, sensitivity, responsiveness and operationalization' not in judgment
    assert 'Avoid semicolons' in judgment
    recommendation = _recommendation_prompt({})
    assert 'first paragraph' in recommendation
    assert 'remaining paragraphs' in recommendation
    assert 'Do not use' in recommendation and 'Done looks like' in recommendation


def test_priority_sections_preserve_all_paragraphs_and_legacy_actions():
    sections = _priority_sections({'narrative': 'The gap matters.\n\nThe team can act.\n\nThe result can be checked.'})
    assert sections == [('Why this matters', ['The gap matters.']),
                        ('What the team could do', ['The team can act.', 'The result can be checked.'])]
    sections = _priority_sections({'limitation': 'The scope is unclear.', 'minimum_action': 'Clarify the scope.'})
    assert sections[0][1] == ['The scope is unclear.']
    assert sections[1][1] == ['Clarify the scope.']
