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


NORMAL_PRIORITY = {
    "title": "Priority 1 \u00b7 Embed early warning indicators",
    "risk_level": "High", "fcv_dimension": "Security", "tag": "[S]",
    "action_timing": "required-before-appraisal",
    "the_gap": "No leading indicators exist. More detail.",
    "why_it_matters": "Risks go undetected. Costs rise.",
    "actions": [{"document_element": "Results Framework", "guidance": "Add a GRM indicator.",
                 "suggested_language": "Indicator: GRM resolution rate."}],
    "implementation_note": "Before mobilisation.",
}


def normal(extra: dict) -> str:
    data = {"stage3Markdown": STANDARD_MD, "fcvRating": "Adequate", "fcvResponsivenessRating": "Low",
            "sensitivitySummary": "Sensitivity is Adequate. Detail.", "responsivenessSummary": "Responsiveness is Low.",
            "riskExposure": {"risks_to": "Crime threatens delivery.", "risks_from": "Influx raises SEA risk."},
            "priorities": [NORMAL_PRIORITY, dict(NORMAL_PRIORITY, title="Priority 2 \u00b7 Second", risk_level="Medium", tag="[S+R]")],
            "watchHtml": "<p>Watch item</p>", "noticesHtml": "<div id='n'></div>", "tailHtml": "<div id='tail'></div>"}
    data.update(extra)
    return run_js(f"process.stdout.write(api.renderNormal(Object.assign({json.dumps(data)}, "
                  "{priorityExtras:(p,i)=>'<div class=\"extra-'+i+'\"></div>'})));")


def test_normal_readout_section_order_and_content():
    html = normal({})
    order = ["id='n'", "fr-scorecard", ">Executive Summary<", "Assessment snapshot", ">FCV Risk Exposure<",
             ">FCV Sensitivity &amp; Responsiveness<", ">Priority Actions for the Task Team<",
             ">Strategic Priorities<", ">Watch List for Supervision<", "id='tail'"]
    positions = [html.index(marker) for marker in order]
    assert positions == sorted(positions)
    assert ">01<" in html and ">06<" in html
    assert html.count('class="fr-ms fr-c') == 4 + 3
    assert "Required before Decision Review (DM/ROC)" in html
    assert "<td>Sensitivity + Responsiveness</td>" in html
    assert 'id="fr-priority-1" open>' in html and 'id="fr-priority-2">' in html
    assert 'class="extra-0"' in html and 'class="extra-1"' in html
    assert "Priority 1 \u00b7 Embed" not in html
    assert "1 High" in html and "1 Medium" in html


def test_normal_readout_omits_missing_sections_and_renumbers():
    html = normal({"riskExposure": None, "watchHtml": "", "priorities": []})
    assert "FCV Risk Exposure" not in html and "Watch List" not in html and "Strategic Priorities" not in html
    assert ">02</span><h2 class=\"fr-h1-txt\">FCV Sensitivity" in html
    assert 'class="fr-sc-count-num">0<' in html


def test_normal_readout_falls_back_to_full_markdown():
    html = normal({"stage3Markdown": "Plain text only, no headings."})
    assert "data-md" in html and "Plain text only" in html
    assert "Assessment snapshot" not in html


def test_normal_readout_escapes_model_text():
    html = normal({"priorities": [dict(NORMAL_PRIORITY, the_gap="<script>alert(1)</script>")]})
    assert "<script>" not in html


CLIMATE_READER = {
    "summary_overview": ["Snapshot sentence from overview.", "Second overview paragraph."],
    "summary_overview_status": "generated",
    "executive_readout": "Exec first sentence. Exec second sentence. Exec third.",
    "judgments": [
        {"dimension": "relevance", "value": "high", "rationale": "Floods intensify."},
        {"dimension": "sensitivity", "value": "moderate", "rationale": "Main hazards addressed."},
        {"dimension": "responsiveness", "value": "not_expected", "rationale": "Scope limited."},
        {"dimension": "operationalization", "value": "early", "rationale": "Criteria agreed."},
    ],
    "existing_responses": [{"description": f"Response {i}. Detail."} for i in range(6)],
    "summary_gaps": [{"text": "Gap one. Detail."}, {"text": "Gap two."}],
    "assessment_themes": [{"title": "Climate risks, design and delivery", "paragraphs": ["Theme para."], "priority_ranks": [1]}],
    "priorities": [
        {"rank": 2, "title": "Second", "confidence": "low", "narrative": "Why two.\n\nAct two.", "responsible_function": "Team"},
        {"rank": 1, "title": "First", "confidence": "medium", "narrative": "Why one.\n\nAct one.",
         "current_document_drafting": {"target_document": "PID", "target_section": "concept", "text": "Draft one."},
         "project_cycle": {"primary_label": "In the PID", "primary_text": "State the basis."}},
    ],
    "priority_summary": {"statement": "Two priorities follow."},
    "review_readiness_flags": [{"flag": "List unsettled", "why_it_matters": "Screening needs it.", "suggested_verification": "Confirm list."}],
    "minor_climate_points": [{"point": "Warnings reach", "why": "Last mile.", "how_to_check": "Review chain."}],
    "guidance_items": [{"title": "Good", "url": "https://example.org/a"}, {"title": "Bad", "url": "javascript:alert(1)"}],
    "evidence_trail": {"limitations": "Concept stage only."},
    "advisory_notice": "Supports judgment.",
}


def climate(reader: dict, opts: dict | None = None) -> str:
    return run_js(f"process.stdout.write(api.renderClimate({json.dumps(reader)}, {json.dumps(opts or {'draftingAllowed': True, 'noticesHtml': '<div id=cn></div>'})}));")


def test_climate_readout_structure():
    html = climate(CLIMATE_READER)
    order = ["id=cn", "fr-scorecard", ">Overview<", "Snapshot sentence from overview.", "What is already working",
             "Key gaps at this stage", ">Assessment Findings<", ">Climate &amp; FCV Sensitivity &amp; Responsiveness<",
             ">Ranked Operational Priorities<", ">Strategic Priorities<", ">Points to Check Before the Applicable Review<",
             ">Relevant WBG Guidance<", ">Limitations<"]
    positions = [html.index(marker) for marker in order]
    assert positions == sorted(positions)
    assert html.count('class="fr-ms fr-c') == 3
    assert "Not expected" in html
    assert html.count("Response ") == 4
    assert html.index('id="fr-priority-1"') < html.index('id="fr-priority-2"')
    assert "Draft one." in html and "In the PID:" in html
    assert "Operationalization: Early." in html and "Climate relevance: High." in html
    assert 'href="https://example.org/a"' in html and "javascript:" not in html
    assert "Concept stage only." in html and "Supports judgment." in html


def test_climate_snapshot_uses_executive_readout_when_overview_is_fallback():
    reader = dict(CLIMATE_READER, summary_overview_status="fallback",
                  summary_overview=["The automated Summary could not be independently verified."])
    html = climate(reader)
    assert "Exec first sentence. Exec second sentence." in html
    assert "could not be independently verified" not in html


def test_climate_zero_priorities_and_withheld_drafting():
    reader = dict(CLIMATE_READER, priorities=[], recommendation_message="Recommendations were withheld.")
    html = climate(reader, {"draftingAllowed": False})
    assert "Recommendations were withheld." in html
    assert 'class="fr-sc-count-num">0<' in html
    assert "Strategic Priorities" not in html
    html = climate(CLIMATE_READER, {"draftingAllowed": False})
    assert "Draft one." not in html


def test_parser_prefers_executive_summary_block_for_snapshot():
    s = parse("# FCV Support Note\n\n## FCV Support Note: Road Project\n\n**Project:** P123 | **Stage:** PID\n\n"
              "## EXECUTIVE SUMMARY\n\n**Real verdict sentence.**\n\n### Strengths\n\nS.")
    assert s["snapshot"] == "Real verdict sentence."
    assert {"heading": "FCV Support Note: Road Project", "body": "**Project:** P123 | **Stage:** PID"} in s["other"]


def test_parser_strips_horizontal_rules():
    s = parse("## Executive Summary\n\n### Opening Assessment\n\nSnap.\n\n---\n\n### Strengths\n\nS.")
    assert s["snapshot"] == "Snap."
    assert "---" not in json.dumps(s)


def test_parser_strips_disclaimer_at_end_of_input():
    s = parse("---\n**AI-Generated Output**\n---")
    assert "AI-Generated" not in json.dumps(s)


def test_parser_skips_watch_list_subheadings():
    s = parse("## Executive Summary\n\n### Strengths\n\nS.\n\n### Watch List for Supervision\n\nW.\n\n#### Sub watch\n\nLeak.\n\n### Gaps\n\nG.")
    assert "Leak" not in json.dumps(s) and "Sub watch" not in json.dumps(s)
    assert s["gaps"] == "G."


def test_climate_priority_ids_unique_and_dangling_links_dropped():
    reader = dict(CLIMATE_READER, priorities=[
        {"rank": 1, "title": "A", "confidence": "high", "narrative": "W.\n\nA."},
        {"rank": 1, "title": "B", "confidence": "high", "narrative": "W.\n\nA."}],
        assessment_themes=[{"title": "T", "paragraphs": ["p."], "priority_ranks": [7, 1]}])
    html = climate(reader)
    assert html.count('id="fr-priority-1"') == 1 and html.count('id="fr-priority-2"') == 1
    assert "Priority 7" not in html and "fr-priority-7" not in html
    assert ">Priority 1</a>" in html


def test_climate_missing_confidence_shows_no_pill():
    reader = dict(CLIMATE_READER, priorities=[{"rank": 1, "title": "A", "narrative": "W.\n\nA."}])
    html = climate(reader)
    assert "Unclear" not in html
