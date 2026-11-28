"""2026-11-27 (owner): on the normal route the Opening assessment replaces the two S/R snapshot tiles at the
top (one coloured overview box, priority count on the right) and no longer repeats in the Executive Summary.
The S/R summaries still drive the full FCV Sensitivity and Responsiveness section below."""
from io import BytesIO
from pathlib import Path

from docx import Document

import app
from tests.test_fcv_priority_advisory_exports import _docx_text
from tests.test_fcv_readout import normal

VERDICT = "The project is FCV-aware but needs sharper adaptation."


def test_browser_overview_box_replaces_sr_tiles_and_appears_once():
    html = normal({})
    top = html[:html.index("fr-exec")]
    assert 'class="fr-scorecard fr-scorecard-ov"' in top and 'class="fr-sc-overview"' in top
    assert VERDICT in top and "fr-sc-tile-summary" not in top and "Snapshot:" not in top
    assert html.count(VERDICT) == 1 and "Assessment snapshot" not in html
    # The full S/R judgments still appear lower down.
    assert "Sensitivity is Adequate." in html[html.index("fr-ratings-sec"):]


def test_browser_keeps_sr_tiles_without_an_opening_assessment():
    md = "# Note\n\n## Executive Summary\n\n### Operational Context\n\nThe corridor faces organised crime.\n"
    html = normal({"stage3Markdown": md})
    assert "fr-sc-overview" not in html and html.count("fr-sc-tile-summary") == 2


def test_split_opening_assessment():
    md = "# T\n\n## Executive Summary\n\n### **Opening assessment**\n\n**Verdict.** More.\n\n### Operational context\n\nCtx."
    text, rest = app.split_opening_assessment(md)
    assert text == "Verdict. More." and "Opening assessment" not in rest and "Operational context" in rest
    assert app.split_opening_assessment("No headings.") == ("", "No headings.")


def test_word_overview_box_replaces_sr_tiles():
    md = "## Executive Summary\n\n### Opening Assessment\n\n**" + VERDICT + "**\n\n### Operational Context\n\nCrime."
    priority = {"title": "Priority 1 · Act", "risk_level": "High", "the_gap": "Gap.", "why_it_matters": "Why.",
                "actions": []}
    resp = app.app.test_client().post("/api/download-report", json={
        "summary": md, "priorities": [priority], "metadata": {},
        "sensitivity_summary": "Sensitivity judgment.", "responsiveness_summary": "Responsiveness judgment."})
    assert resp.status_code == 200
    doc = Document(BytesIO(resp.data))
    tables = ["\n".join(c.text for c in t.rows[0].cells) for t in doc.tables]
    box = next(t for t in tables if t.startswith("SNAPSHOT"))
    text = _docx_text(doc)
    assert VERDICT in box and "PRIORITY ACTIONS" in box and "Snapshot" not in text
    assert text.count(VERDICT) == 1 and "OPENING ASSESSMENT" not in text.upper()
    assert "Sensitivity judgment." in text


def test_box_is_labelled_snapshot_on_both_routes():
    from tests.test_fcv_readout import CLIMATE_READER, climate
    for html in (normal({}), climate(CLIMATE_READER)):
        box = html[html.index('class="fr-sc-overview"'):]
        assert box.startswith('class="fr-sc-overview" data-fr-rating="overview"><div class="fr-sc-label">Snapshot</div>')
        assert "This snapshot is a high-level AI reading" in html


def test_normal_box_bolds_only_the_opening_sentence_in_browser_and_word():
    md = ("## Executive Summary\n\n### Opening Assessment\n\nGuinea's water project depends on tariff decisions. "
          "Its procurement design is strong. Affordability safeguards would help.\n\n### Operational Context\n\nCrime.")
    html = normal({"stage3Markdown": md})
    assert ('>Guinea\'s water project depends on tariff decisions. <span class="fr-sc-ov-rest">Its procurement design '
            'is strong. Affordability safeguards would help.</span>') in html
    resp = app.app.test_client().post("/api/download-report", json={
        "summary": md, "priorities": [{"title": "Priority 1 · Act", "risk_level": "High", "the_gap": "G.",
                                       "why_it_matters": "W.", "actions": []}], "metadata": {}})
    doc = Document(BytesIO(resp.data))
    cell = next(t.rows[0].cells[0] for t in doc.tables if t.rows[0].cells[0].text.startswith("SNAPSHOT"))
    runs = [r for p in cell.paragraphs for r in p.runs]
    bold = "".join(r.text for r in runs if r.bold)
    assert "depends on tariff decisions." in bold and "procurement design" not in bold


def test_snapshot_rules_in_both_route_prompts():
    from fcv_snapshot_rules import SNAPSHOT_RULES
    from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
    normal_prompt = app._stage3_apply_section_specs(app.DEFAULT_PROMPTS["3"]) + app._stage3_contract_text()
    climate_prompt = build_verified_stage_prompt("reader_compiler", {})
    for prompt in (normal_prompt, climate_prompt):
        assert "SNAPSHOT AND OPENING RULES" in prompt and "Write fresh wording for this project." in prompt
        assert "overall assessment verdict, never as a plain-language project brochure" in prompt
        assert "75 to 95 words" in prompt
    assert "ONE BOLD SENTENCE, 35-60" not in normal_prompt and "100-115 words each" not in climate_prompt
    assert "about 75-95 words" in normal_prompt and "about 95-120 words" in normal_prompt
    assert "175-210 words overall" in climate_prompt and "about 195 summary words" in climate_prompt
    assert "least settled" not in SNAPSHOT_RULES.lower()
    assert "least settled" not in climate_prompt.lower()
    assert "{" not in SNAPSHOT_RULES and "}" not in SNAPSHOT_RULES
    assert "\u2014" not in SNAPSHOT_RULES and "\u2013" not in SNAPSHOT_RULES


def test_word_and_browser_agree_when_no_opening_assessment_heading():
    md = "## Executive Summary\n\n**Verdict sentence.** Supporting lead detail.\n\n### Operational Context\n\nContext body."
    assert "fr-sc-overview" not in normal({"stage3Markdown": md})
    resp = app.app.test_client().post("/api/download-report", json={
        "summary": md, "priorities": [], "metadata": {},
        "sensitivity_summary": "Sens.", "responsiveness_summary": "Resp."})
    doc = Document(BytesIO(resp.data))
    assert not any(t.rows[0].cells[0].text.startswith("SNAPSHOT") for t in doc.tables)


def test_opening_assessment_heading_with_suffix_still_fills_box():
    md = "## Executive Summary\n\n### Opening Assessment (snapshot)\n\nShort verdict here.\n\n### Operational Context\n\nCtx."
    assert app.split_opening_assessment(md)[0] == "Short verdict here."
    assert "fr-sc-overview" in normal({"stage3Markdown": md})


def test_word_keeps_note_only_opening_in_body():
    md = "## Executive Summary\n\n### Opening Assessment\n\n[Verify before sharing: confirm dates.]\n\n### Operational Context\n\nCtx."
    resp = app.app.test_client().post("/api/download-report", json={
        "summary": md, "priorities": [], "metadata": {}, "sensitivity_summary": "S.", "responsiveness_summary": "R."})
    doc = Document(BytesIO(resp.data))
    assert not any(t.rows[0].cells[0].text.startswith("SNAPSHOT") for t in doc.tables)
    assert "confirm dates" in _docx_text(doc)


def test_implementation_review_prompt_has_no_conflicting_opening_spec():
    src = Path(app.__file__).read_text(encoding="utf-8")
    assert "### Opening Assessment (ONE BOLD SENTENCE, 25\u201335 words)\nSummarise the project's current FCV integration status during implementation." in src
    sample = ("### Opening Assessment (ONE BOLD SENTENCE, 25\u201335 words)\nSummarise the project's current FCV integration "
              "status during implementation.\n\n### Implementation Context (150\u2013200 words, ONE PARAGRAPH)\nSynthesise the "
              "3\u20134 key FCV dynamics that have shaped implementation to date and that the remaining period must navigate.")
    out = app._stage3_apply_section_specs(sample)
    assert "ONE BOLD SENTENCE" not in out and "SNAPSHOT AND OPENING RULES" in out and "bold segue sentence" in out


def test_verify_and_heading_helpers_are_linear_and_correct():
    import time

    from fcv_docx_style import split_verify_notes
    assert split_verify_notes("A. [Verify before sharing: x.] B.") == ("A. B.", ["[Verify before sharing: x.]"])
    hostile = "[Verify before sharing:" * 20000
    started = time.perf_counter()
    assert split_verify_notes(hostile)[1] == []
    assert time.perf_counter() - started < 1.0
    assert app._is_opening_heading("### **Opening Assessment** (snapshot)")
    assert not app._is_opening_heading("## Opening assessments")
    assert not app._is_opening_heading("# Opening Assessment")
    started = time.perf_counter()
    app.split_opening_assessment("##" + " " * 50000 + "x")
    assert time.perf_counter() - started < 1.0
