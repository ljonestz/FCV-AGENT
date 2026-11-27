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
    box = next(t for t in tables if t.startswith("OVERVIEW"))
    text = _docx_text(doc)
    assert VERDICT in box and "PRIORITY ACTIONS" in box and "Snapshot" not in text
    assert text.count(VERDICT) == 1 and "OPENING ASSESSMENT" not in text.upper()
    assert "Sensitivity judgment." in text
