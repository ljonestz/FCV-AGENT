"""2026-11-27 (owner): on the normal route the Opening assessment replaces the two S/R snapshot tiles at the
top (one coloured overview box, priority count on the right) and no longer repeats in the Executive Summary.
The S/R summaries still drive the full FCV Sensitivity and Responsiveness section below."""
from io import BytesIO

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
    from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
    normal_prompt = app._stage3_apply_section_specs(app.DEFAULT_PROMPTS["3"]) + app._stage3_contract_text()
    climate_prompt = build_verified_stage_prompt("reader_compiler", {})
    for prompt in (normal_prompt, climate_prompt):
        assert "SNAPSHOT AND OPENING RULES" in prompt and "Write fresh wording for this project." in prompt
    assert "ONE BOLD SENTENCE, 35-60" not in normal_prompt and "100-115 words each" not in climate_prompt
