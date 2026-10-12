"""Scope-aware Climate rating questions and a short, grounded Summary gap readout."""

import json
import subprocess
from io import BytesIO

from docx import Document

from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_render import (
    build_reader_model,
    render_reader_html,
    write_reader_docx,
)
from tests.test_climate_lens_frontend import INDEX, _extract_js_function, _js_escape_helper
from tests.test_shared_rating_sidebar import render_cards


SENSITIVITY_QUESTION = "How well does the project recognize and address interacting climate and FCV risks?"
RESPONSIVENESS_QUESTION = (
    "How well does the project use relevant opportunities to generate wider peace "
    "and social dividends through its climate-related design and delivery?"
)


def test_rating_questions_match_in_sidebar_and_exports():
    reader = build_reader_model({"judgments": {
        "sensitivity": {"value": "moderate"},
        "responsiveness": {"value": "moderate"},
    }})
    stream = BytesIO()
    write_reader_docx(reader, stream)
    stream.seek(0)
    doc_text = "\n".join(p.text for p in Document(stream).paragraphs)
    for content in [render_cards(), render_reader_html(reader), doc_text]:
        assert SENSITIVITY_QUESTION in content
        assert RESPONSIVENESS_QUESTION in content
    assert "Peace and social dividends" in render_cards()


def test_judgment_prompt_requires_risk_response_and_evidenced_dividends():
    prompt = build_verified_stage_prompt("judgment_review", {})
    assert SENSITIVITY_QUESTION in prompt
    assert RESPONSIVENESS_QUESTION in prompt
    for rule in [
        "Recognition alone cannot justify strong or very_strong sensitivity",
        "a concrete climate-FCV mechanism",
        "social cohesion and inclusion",
        "institutional capacity and legitimacy",
        "jobs and livelihoods",
        "Do not score the project's theoretical maximum",
        "not_expected",
        "unclear",
    ]:
        assert rule in prompt


def test_compiler_keeps_gap_language_short_and_qualified():
    prompt = build_verified_stage_prompt("recommendation_compiler", {})
    assert "For limitation, write one complete sentence of at most 35 words" in prompt
    assert "missing evidence from a confirmed omission" in prompt
    assert "optional dividends opportunity is not a required correction" in prompt


def _render_gaps(priorities):
    source = INDEX.read_text(encoding="utf-8")
    script = (
        _js_escape_helper()
        + _extract_js_function(source, "boldEscapedFirstSentence")
        + _extract_js_function(source, "renderClimateSummaryGaps")
        + "\nconsole.log(renderClimateSummaryGaps({}," + json.dumps(priorities) + "));"
    )
    result = subprocess.run(["node", "-"], input=script, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_legacy_summary_gaps_reuses_up_to_five_distinct_complete_limitations():
    first = "Flood performance is addressed, but upkeep arrangements are not documented."
    second = "A wider livelihoods dividend remains an optional opportunity within the project's scope."
    html = _render_gaps([
        {"limitation": first, "narrative": "Do not copy the action narrative."},
        {"limitation": "  " + first.upper() + "  "},
        {"limitation": second},
        {"limitation": "A distinct operational limitation remains unresolved."},
    ])
    assert "Potential gaps" in html
    assert first in html
    assert "optional opportunity" in html
    assert "Do not copy" not in html and "distinct operational limitation" in html
    assert html.count("<li") == 3 and "<ul" in html


def test_summary_gaps_preserves_qualifications_and_never_slices_long_fields():
    qualified = "The upload does not show <maintenance> arrangements; this is missing evidence, not proof of an omission."
    html = _render_gaps([
        {"limitation": "Long " * 81 + "qualification."},
        {"limitation": qualified},
    ])
    assert "Long" not in html
    assert "missing evidence, not proof of an omission." in html
    assert "&lt;maintenance&gt;" in html and "<maintenance>" not in html
    assert _render_gaps([]) == ""
    assert _render_gaps([{"narrative": "An unsupported gap must not be inferred."}]) == ""


def test_summary_gap_section_uses_reader_findings_without_candidate_diagnostics():
    source = INDEX.read_text(encoding="utf-8")
    summary = _extract_js_function(source, "renderClimateVerifiedSummary")
    assert "renderClimateSummaryGaps(r,priorities)" in summary
    assert "diagnostic_trace" not in summary and "recommendation_candidates" not in summary
    assert summary.index("${strengthsHtml}") < summary.index("${gapsHtml||bridge}")
    assert summary.index("${gapsHtml||bridge}") < summary.index("Priority actions for the task team")


def test_shared_caveat_respects_project_scope():
    source = INDEX.read_text(encoding="utf-8")
    caveat = _extract_js_function(source, "screenerCaveatHtml")
    assert "ideal project" not in caveat and "maximum time" not in caveat
    assert "scope and delivery constraints" in caveat
    assert "Responsiveness is not expected for every project" in caveat


def test_detailed_question_preserves_server_text_and_migrates_known_legacy_wording():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(_extract_js_function(source, name) for name in (
        "climateAccessibleRouteValue", "climateDraftingRouteGate",
        "renderPriorityProjectCycle", "climateSummaryWatchItems",
        "renderClimateVerifiedAssessment",
    ))
    script = _js_escape_helper() + helpers + """
const renderClimateRelevantGuidance=()=>'';
const questions=[
  'How sensitive is this project to climate and FCV considerations?',
  'An authoritative server question?',
  ''
];
for(const question of questions){
  const html=renderClimateVerifiedAssessment({climate_sensitivity_rating:{question,label:'Strong',level:4,scale:['Very limited','Limited','Moderate','Strong','Very strong']}});
  const expected=question==='An authoritative server question?'?question:
    'How well does the project recognize and address interacting climate and FCV risks?';
  if(!html.includes(expected))throw new Error('question field or legacy migration lost');
  if(!html.includes('>Strong<'))throw new Error('saved score changed');
}
"""
    result = subprocess.run(["node", "-"], input=script, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
