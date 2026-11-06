"""Unit tests for static/fcv_readout.js (Word-aligned Stage 3 readout)."""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "static" / "fcv_readout.js"

STUBS = r"""
const esc = v => String(v ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const md = t => '<div data-md>' + esc(t) + '</div>';
const boldFirst = t => { const s = String(t || '').trim(); const m = s.match(/^([\s\S]*?[.!?])(\s[\s\S]*)?$/); return m ? '<strong>' + esc(m[1]) + '</strong>' + esc(m[2] || '') : '<strong>' + esc(s) + '</strong>'; };
const timingLabel = v => v === 'required-before-appraisal' ? 'Required before Decision Review (DM/ROC)' : (v || '');
"""


def run_js(body: str) -> str:
    script = (STUBS + f"const FR = require({json.dumps(str(MODULE))});\n"
              "const api = FR.create({esc, md, boldFirst, timingLabel});\n" + body)
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    return result.stdout


def parse(markdown: str) -> dict:
    return json.loads(run_js(f"process.stdout.write(JSON.stringify(FR.parseStage3Sections({json.dumps(markdown)})));"))


STANDARD_MD = """# FCV Support Note: Test Project

## Executive Summary

### Opening Assessment

**The project is FCV-aware but needs sharper adaptation.**

### Operational Context

**The corridor faces organised crime.** Poverty is high.

### Strengths

**Labour influx safeguards are strong.** The ESCP commits to plans.

### Gaps

**There are no conflict-sensitive indicators.** The RF lacks proxies.
"""


def test_parser_reads_standard_headings():
    s = parse(STANDARD_MD)
    assert s["found"] is True
    assert s["snapshot"] == "The project is FCV-aware but needs sharper adaptation."
    assert s["context"].startswith("**The corridor faces organised crime.**")
    assert "Labour influx" in s["strengths"]
    assert "conflict-sensitive indicators" in s["gaps"]
    assert s["other"] == []


def test_parser_falls_back_to_lead_paragraph_when_opening_assessment_missing():
    md = ("---\n**AI-Generated Output**\n\nDisclaimer.\n---\n\n# FCV Support Note\n\n"
          "## EXECUTIVE SUMMARY\n\n**The AF responds credibly but DRC access is untested.**\n\n"
          "### Operational Context\n\nContext here.\n\n%%%RISK_NARRATIVE_START%%%\n\n"
          "### FCV Risk Exposure\n\n**Risks to project:** Sites may close.\n\n"
          "### Collegial FCV Review for the Task Team\n\nExtra note.\n")
    s = parse(md)
    assert s["snapshot"] == "The AF responds credibly but DRC access is untested."
    assert s["context"] == "Context here."
    assert "Sites may close" in s["risk"]
    assert s["other"] == [{"heading": "Collegial FCV Review for the Task Team", "body": "Extra note."}]
    assert "RISK_NARRATIVE" not in json.dumps(s)
    assert "Disclaimer" not in json.dumps(s)


def test_parser_accepts_gap_heading_variants_and_skips_watch_list():
    s = parse("## Executive Summary\n\n### Potential gaps\n\nGap text.\n\n### Watch List for Supervision\n\nWatch.\n")
    assert s["gaps"] == "Gap text."
    assert "Watch." not in json.dumps(s)


def test_parser_reports_not_found_for_unstructured_text():
    s = parse("Just a paragraph with no headings.")
    assert s["found"] is False


def test_scorecard_meter_and_unknown_rating():
    html = run_js("process.stdout.write(api.scorecard(["
                  "{key:'sensitivity',label:'FCV Sensitivity',value:'Adequate',steps:6,level:4,lo:'Extremely Low',hi:'Very Well Embedded',def:'Fit?'},"
                  "{key:'responsiveness',label:'FCV Responsiveness',value:'Odd value',steps:6,level:0,lo:'a',hi:'b',def:'Drivers?'}],"
                  "{label:'Priority actions',number:3,pills:[{text:'2 High',cls:'fr-pill-high'}]}));")
    assert html.count('class="fr-ms fr-c') == 4
    assert html.count('class="fr-meter"') == 1
    assert "Odd value" in html and "Drivers?" in html
    assert 'class="fr-sc-count-num">3<' in html
    assert "Advisory judgments, not official WBG ratings." in html


def test_priority_card_open_state_extras_and_escaping():
    html = run_js("process.stdout.write(api.priorityCard({id:'fr-priority-1',rank:1,open:true,supHtml:'Priority 1',"
                  "title:'<b>x</b>',zones:[{label:'The gap',html:'<p>g</p>'},{label:'Empty',html:''}],"
                  "drafts:[{label:'Suggested text',forText:'PAD',text:'Draft <i>'}],cycle:{label:'When to address',text:'Before Board'},"
                  "extraHtml:'<div id=\"deeper-details-0\"></div>'}) + '|' + api.priorityCard({id:'fr-priority-2',rank:2,open:false,supHtml:'',title:'t',zones:[],drafts:[]}));")
    first, second = html.split("|")
    assert '<details class="fr-pc" id="fr-priority-1" open>' in first
    assert "&lt;b&gt;x&lt;/b&gt;" in first and "Draft &lt;i&gt;" in first
    assert "Empty" not in first
    assert 'id="deeper-details-0"' in first
    assert "When to address:" in first
    assert '<details class="fr-pc" id="fr-priority-2">' in second
