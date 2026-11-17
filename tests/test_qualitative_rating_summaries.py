"""Summary boxes show a one-sentence judgment instead of rating gauges (2026-11-16).

The Stage 3 rating fields stay in the JSON for ITS parity; the browser readout,
Share export and Word exports no longer display them on either route.
"""

from io import BytesIO

from docx import Document

from fcv_docx_style import first_sentence
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_render import build_reader_model, write_reader_docx
from tests.test_climate_lens_frontend import _readout_harness, _run_node

SENS = ("The project keeps delivery steady in a volatile setting, e.g. through third-party "
        "monitoring. It still lacks a grievance channel that women can use safely.")
RESP = "The project mainly operates in an FCV setting rather than aiming to address drivers. Its cash transfers add some resilience."


def _doc_text(document):
    return "\n".join([p.text for p in document.paragraphs]
                     + [c.text for t in document.tables for r in t.rows for c in r.cells])


def test_first_sentence_skips_abbreviations_and_decimals():
    assert first_sentence(SENS).endswith("third-party monitoring.")
    assert first_sentence("Coverage is 2.5 times the U.S. baseline. Next point.") == "Coverage is 2.5 times the U.S. baseline."
    assert first_sentence("**Bold lead.** Rest.\n\nSecond paragraph.") == "Bold lead."
    assert first_sentence("") == ""


def test_normal_readout_shows_sentences_not_gauges():
    script = _readout_harness() + f"""
const html = frApi().renderNormal({{stage3Markdown:'', fcvRating:'Adequate', fcvResponsivenessRating:'Low',
  sensitivitySummary:{SENS!r}, responsivenessSummary:{RESP!r}, priorities:[], riskExposure:{{}}}});
const top = html.slice(0, html.indexOf('</section>'));
if (!top.includes('fr-sc-summary')) throw new Error('summary card missing');
if (!top.includes('third-party monitoring.')) throw new Error('first sentence missing');
if (top.includes('grievance channel')) throw new Error('card should show one sentence only');
if (html.includes('fr-meter') || html.includes('fr-sc-value')) throw new Error('gauge still rendered');
if (html.includes('>Adequate<') || html.includes('>Low<')) throw new Error('rating label still displayed');
if (!html.includes('grievance channel')) throw new Error('full judgment missing from main section');
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


def test_climate_readout_shows_sentences_not_gauges():
    script = _readout_harness() + f"""
const html = renderClimateVerifiedAssessment({{judgments:[
  {{dimension:'sensitivity', value:'moderate', rationale:{SENS!r}}},
  {{dimension:'responsiveness', value:'limited', rationale:{RESP!r}}}]}});
if (!html.includes('fr-sc-summary')) throw new Error('summary card missing');
if (html.includes('fr-meter')) throw new Error('gauge still rendered');
if (html.includes('>Moderate<') || html.includes('>Limited<')) throw new Error('rating label still displayed');
if (!html.includes('Its cash transfers add some resilience.')) throw new Error('rationale missing');
"""
    result = _run_node(script)
    assert result.returncode == 0, result.stderr


def test_climate_word_export_shows_sentences_not_scale():
    reader = build_reader_model({"judgments": {
        "sensitivity": {"value": "moderate", "rationale": SENS},
        "responsiveness": {"value": "limited", "rationale": RESP},
    }})
    stream = BytesIO()
    write_reader_docx(reader, stream)
    stream.seek(0)
    text = _doc_text(Document(stream))
    assert first_sentence(SENS) in text
    assert "Very limited / Limited / Moderate" not in text
    assert "Limited contribution" not in text
    assert "Responsiveness is not required of every project" in text


def test_stage3_prompts_ask_for_standalone_opening_sentence_and_no_criticism():
    from app import DEFAULT_PROMPTS

    for key in ("3", "impl_3"):
        prompt = DEFAULT_PROMPTS[key]
        assert prompt.count("shown alone in the summary box") == 2, key
        assert "Do not name a rating label" in prompt, key
    stage3 = DEFAULT_PROMPTS["3"]
    assert "many projects will have low responsiveness scores" not in stage3
    assert "Responsiveness is not expected of every project" in stage3
    assert "obvious responsiveness potential that it ignores" in stage3


def test_me_calibration_in_stage2_and_stage3_prompts():
    from app import DEFAULT_PROMPTS

    stage2, stage3 = DEFAULT_PROMPTS["2"], DEFAULT_PROMPTS["3"]
    assert "## M&E calibration" in stage2
    for prompt in (stage2, stage3):
        assert "peace, stability, social cohesion or conflict reduction" in prompt
        assert "disaggregat" in prompt
        assert "PDO" in prompt
    assert "a very large indicator set is itself a monitoring risk" in stage2


def test_climate_judgment_prompt_requires_standalone_opening_sentence():
    prompt = build_verified_stage_prompt("judgment_review", {})
    assert "shown alone in the summary box" in prompt
    assert "Do not name the rating category" in prompt
    assert "do not criticize a limited or not_expected" in prompt
