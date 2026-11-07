"""Scope-aware Climate rating questions and a short, grounded Summary gap readout."""

import json
from pathlib import Path
from io import BytesIO

from docx import Document

from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_render import (
    build_reader_model,
    render_reader_html,
    write_reader_docx,
)
from tests.test_climate_lens_frontend import INDEX, _extract_js_function, _readout_harness, _run_node
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
    document = Document(stream)
    doc_text = "\n".join([p.text for p in document.paragraphs] + [cell.text for table in document.tables for row in table.rows for cell in row.cells])
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


def _render_gaps(gaps):
    """Render the verified readout and return only its 'Key gaps at this stage' block."""
    script = _readout_harness() + "\nconsole.log(renderClimateVerifiedAssessment({summary_gaps:" + json.dumps(gaps) + "}));"
    result = _run_node(script)
    assert result.returncode == 0, result.stderr
    html = result.stdout
    start = html.find("Key gaps at this stage")
    if start < 0:
        return ""
    return html[start:html.index("</section>", start)]


def test_readout_gaps_show_up_to_five_complete_findings():
    first = "Flood performance is addressed, but upkeep arrangements are not documented."
    second = "A wider livelihoods dividend remains an optional opportunity within the project's scope."
    html = _render_gaps([
        {"text": first},
        {"text": second},
        {"text": "A distinct operational limitation remains unresolved."},
        {"text": "Fourth finding."},
        {"text": "Fifth finding."},
        {"text": "Sixth finding must not appear."},
    ])
    assert "Key gaps at this stage" in html
    assert "upkeep arrangements are not documented." in html
    assert "optional opportunity" in html
    assert "distinct operational limitation" in html
    assert "Sixth finding" not in html
    assert html.count('<p class="fr-p">') == 5


def test_readout_gaps_preserve_qualifications_and_never_slice_long_fields():
    qualified = "The upload does not show <maintenance> arrangements; this is missing evidence, not proof of an omission."
    html = _render_gaps([
        {"text": "Long " * 81 + "qualification."},
        {"text": qualified},
    ])
    assert html.count("Long") == 81
    assert "qualification." in html
    assert "missing evidence, not proof of an omission." in html
    assert "&lt;maintenance&gt;" in html and "<maintenance>" not in html
    assert _render_gaps([]) == ""
    assert _render_gaps([{"narrative": "An unsupported gap must not be inferred."}]) == ""


def test_readout_gap_section_uses_reader_findings_without_candidate_diagnostics():
    module = (Path(INDEX).parent / "static" / "fcv_readout.js").read_text(encoding="utf-8")
    start = module.index("function renderClimate(")
    body = module[start:]
    assert "r.summary_gaps" in body
    assert "diagnostic_trace" not in body and "recommendation_candidates" not in body
    assert body.index("What is already working") < body.index("Key gaps at this stage")
    assert body.index("Key gaps at this stage") < body.index("Priority Actions for the Task Team")


def test_shared_caveat_respects_project_scope():
    source = INDEX.read_text(encoding="utf-8")
    caveat = _extract_js_function(source, "screenerCaveatHtml")
    assert "ideal project" not in caveat and "maximum time" not in caveat
    assert "scope and delivery constraints" in caveat
    assert "Responsiveness is not expected for every project" in caveat


def test_readout_uses_the_canonical_rating_question_and_preserves_the_saved_score():
    script = _readout_harness() + """
for (const question of ['How sensitive is this project to climate and FCV considerations?', 'An authoritative server question?', '']) {
  const html = renderClimateVerifiedAssessment({climate_sensitivity_rating:{question, value:'strong', label:'Strong', level:4}});
  if (!html.includes('How well does the design recognize and manage interacting climate and FCV risks, and avoid doing harm?')) throw new Error('canonical rating question missing');
  if (html.includes('How sensitive is this project to climate and FCV considerations?')) throw new Error('legacy wording leaked');
  if (!html.includes('>Strong<')) throw new Error('saved score changed');
}
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr
