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
const timingLabel = v => v === 'required-before-appraisal' ? 'Address before Decision Review (DM/ROC)' : (v || '');
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
                  "{label:'Priority actions',number:3,def:'3 priority actions are identified by the FCV Screener.',pills:[{text:'2 High',cls:'fr-pill-high'}]}));")
    assert html.count('class="fr-ms fr-c') == 4
    assert html.count('class="fr-meter"') == 1
    assert "Odd value" in html and "Drivers?" in html
    assert 'class="fr-sc-count-num">3<' in html
    assert "Advisory judgments, not official WBG ratings." not in html
    assert html.index('class="fr-sc-lead"') < html.index('class="fr-scorecard"')
    assert "does not reflect" not in html and "do not reflect a formal WBG or FCV Group designation" in html
    assert 'class="fr-sc-count-def">3 priority actions are identified by the FCV Screener.<' in html


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
    order = ["id='n'", "fr-scorecard", 'fr-h1-txt">Executive Summary<', "Assessment snapshot", 'fr-h1-txt">FCV Risk Exposure<',
             'fr-h1-txt">FCV Sensitivity and Responsiveness<', 'fr-h1-txt">Priority Actions for the Task Team<',
             "priority actions have been identified", 'id="fr-priority-1"', 'fr-h1-txt">Watch List for Supervision<', "id='tail'"]
    positions = [html.index(marker) for marker in order]
    assert positions == sorted(positions)
    assert ">01<" in html and ">05<" in html and ">06<" not in html
    assert "fr-ptable" not in html and "Strategic Priorities" not in html
    assert "2 priority actions are identified by the FCV Screener." in html
    assert html.count('class="fr-ms fr-c') == 4 + 3
    assert "Address before Decision Review (DM/ROC)" in html and "Required" not in html
    assert "Sensitivity + Responsiveness" in html[html.index('id="fr-priority-1"'):]
    assert 'id="fr-priority-1" open>' in html and 'id="fr-priority-2">' in html
    assert 'class="extra-0"' in html and 'class="extra-1"' in html
    assert "Priority 1 \u00b7 Embed" not in html
    assert "1 high priority" in html and "1 medium priority" in html
    assert ">High priority</span>" in html and ">Medium priority</span>" in html
    assert ">Suggested actions<" in html and "Essential actions" not in html


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
    order = ["id=cn", "fr-scorecard", 'fr-h1-txt">Overview<', "Snapshot sentence from overview.", "What is already working",
             "Key gaps at this stage", 'fr-h1-txt">Assessment Findings<', 'fr-h1-txt">Climate-FCV Sensitivity and Responsiveness<',
             'fr-h1-txt">Priority Actions for the Task Team<', 'id="fr-priority-1"', 'fr-h1-txt">Smaller Points to Check During Preparation<',
             'fr-h1-txt">Relevant WBG Guidance<', 'fr-h1-txt">Limitations<']
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
    assert "Lead: Team" in html and "Suggested lead" not in html and "fr-ptable" not in html
    assert "2 priority actions are identified by the FCV Screener." in html


def test_climate_snapshot_uses_executive_readout_when_overview_is_fallback():
    reader = dict(CLIMATE_READER, summary_overview_status="fallback",
                  summary_overview=["The automated Summary could not be independently verified."])
    reader.pop("reader_contract", None)
    html = climate(reader)
    assert "Exec first sentence. Exec second sentence." in html
    assert "could not be independently verified" not in html


def test_climate_zero_priorities_and_withheld_drafting():
    reader = dict(CLIMATE_READER, priorities=[], recommendation_message="Recommendations were withheld.")
    html = climate(reader, {"draftingAllowed": False})
    assert "Recommendations were withheld." in html
    assert 'class="fr-sc-count-num">0<' in html
    assert "fr-sc-count-def" not in html and "fr-pc" not in html
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


def test_climate_final_reader_contract_never_uses_executive_readout():
    reader = dict(CLIMATE_READER, reader_contract="final-reader-v1", summary_overview_status="fallback",
                  summary_overview=["The automated Summary could not be independently verified."])
    html = climate(reader)
    assert "could not be independently verified" in html
    assert "Exec first sentence" not in html
    assert "Assessment snapshot" not in html


def test_climate_card_practical_considerations_dedup():
    reader = dict(CLIMATE_READER, priorities=[{
        "rank": 1, "title": "A", "narrative": "Why. Reason.\n\nDo this.", "limitation": "Do this.",
        "caution": "Beware <x>.", "enhanced_action": "Extra.", "enhanced_activation": "When ready."}])
    html = climate(reader)
    assert "Practical considerations" in html and "Beware &lt;x&gt;." in html
    assert html.count("Do this.") == 1
    assert "<strong>Extra.</strong> When ready." in html


ADVISORY = "The following priorities are suggestions <to> strengthen the project's design."


def test_normal_advisory_renders_inside_priority_intro_box_and_is_escaped():
    html = normal({"advisoryText": ADVISORY})
    section = html[html.index(">Priority Actions for the Task Team<"):html.index('class="fr-cards"')]
    assert '<p class="fr-advisory">The following priorities are suggestions &lt;to&gt; strengthen' in section
    assert section.index("priority actions have been identified") < section.index("fr-advisory")
    assert "<to>" not in html


def test_normal_advisory_is_optional_and_absent_without_priorities():
    assert "fr-advisory" not in normal({})
    assert "fr-advisory" not in normal({"advisoryText": ADVISORY, "priorities": []})


def test_normal_and_climate_drafting_labels_use_suggested_text():
    html = normal({})
    assert '<div class="fr-draft-lbl">Suggested Text</div>' in html
    reader = dict(CLIMATE_READER)
    reader["priorities"] = [dict(CLIMATE_READER["priorities"][1], operational_instrument_drafting={
        "target_document": "POM", "target_section": "Annex", "text": "Operational draft."})]
    chtml = climate(reader)
    assert '<div class="fr-draft-lbl">Suggested Text</div>' in chtml
    assert '<div class="fr-draft-lbl">Suggested Text for an operational instrument</div>' in chtml
    assert "Suggested drafting" not in chtml
    assert "Practical considerations" in climate(dict(CLIMATE_READER, priorities=[dict(
        CLIMATE_READER["priorities"][1], caution="A separate practical caution.")]))


def test_climate_advisory_follows_priority_statement_and_is_optional():
    html = climate(CLIMATE_READER, {"draftingAllowed": True, "advisoryText": ADVISORY})
    section = html[html.index(">Priority Actions for the Task Team<"):html.index('class="fr-cards"')]
    assert section.index("Two priorities follow.") < section.index('<p class="fr-advisory">')
    assert "&lt;to&gt;" in section
    no_statement = climate(dict(CLIMATE_READER, priority_summary={}), {"draftingAllowed": True, "advisoryText": ADVISORY})
    assert '<p class="fr-advisory">' in no_statement
    assert "fr-advisory" not in climate(CLIMATE_READER)
    assert "fr-advisory" not in climate(dict(CLIMATE_READER, priorities=[]), {"draftingAllowed": True, "advisoryText": ADVISORY})


def test_climate_readout_omits_reader_review_notice():
    html = climate(dict(CLIMATE_READER, reader_review_notice="Verification notes identify unresolved claims."))
    assert "Verification notes identify unresolved claims." not in html


def test_limitations_section_does_not_reuse_panel_class():
    html = climate(CLIMATE_READER)
    assert '<section class="fr-section fr-limits-sec">' in html
    assert html.count('class="fr-limits"') == 1


def test_lead_rest_renders_after_snapshot_before_context():
    md_text = ("## Executive Summary\n\n**Verdict sentence.** Supporting lead detail.\n\n"
               "### Operational Context\n\nContext body.\n\n### Gaps\n\nGap body.")
    html = normal({"stage3Markdown": md_text})
    assert html.index("Assessment snapshot") < html.index("Supporting lead detail.") < html.index("Context body.")
    assert html.index("Supporting lead detail.") < html.index("Gap body.")


def test_dimension_definitions_identical_on_tile_and_row():
    html = normal({})
    for d in ["How well does the project design fit its FCV context, avoiding harm and accounting for conflict and fragility dynamics?",
              "Does the project actively contribute to addressing FCV drivers? Not expected for every project."]:
        assert html.count(d) == 2, d
    chtml = climate(CLIMATE_READER)
    for d in ["How well does the design recognize and manage interacting climate and FCV risks, and avoid doing harm?",
              "Does the project use relevant opportunities to generate wider peace and social dividends? Not expected for every project."]:
        assert chtml.count(d) == 2, d
    assert ">Climate-FCV sensitivity<" in chtml and ">Climate-FCV responsiveness<" in chtml


def test_ratings_section_has_no_advisory_note_and_ops_note_is_labelled():
    assert "Advisory judgments" not in normal({})
    chtml = climate(CLIMATE_READER)
    assert "Advisory judgments" not in chtml
    assert chtml.index("Supporting judgments (not shown on the scorecard)") < chtml.index("Climate relevance: High.")


def test_closing_line_is_last_element_on_both_routes():
    closing = '<p class="fr-note fr-closing">This automated screening supports task-team judgment. It is not a compliance, eligibility, adequacy or clearance decision.</p>'
    assert normal({}).endswith(closing + "</article>")
    assert climate(CLIMATE_READER).endswith(closing + "</article>")
    already = climate(dict(CLIMATE_READER, advisory_notice="This note does not constitute a clearance."))
    assert "fr-closing" not in already


def test_climate_fallback_overview_is_muted_intro():
    reader = dict(CLIMATE_READER, reader_contract="final-reader-v1", summary_overview_status="fallback",
                  summary_overview=["A short summary is not shown for this run."])
    html = climate(reader)
    assert '<p class="fr-intro">A short summary is not shown for this run.</p>' in html
    assert "<strong>A short summary" not in html


def test_confidence_pill_title_and_climate_target_casing():
    reader = dict(CLIMATE_READER, priorities=[dict(CLIMATE_READER["priorities"][1], responsible_function="Task team.",
        current_document_drafting={"target_document": "pad", "target_section": "project description", "text": "Draft."})])
    html = climate(reader)
    assert 'title="How well the documents support this priority"' in html
    assert "PAD - Project Description" in html and "Lead: Task team" in html and "Task team." not in html


def test_priority_card_header_two_rows_with_title_and_chevron():
    html = normal({})
    card = html[html.index('id="fr-priority-1"'):html.index('id="fr-priority-2"')]
    summary = card[card.index("<summary"):card.index("</summary>")]
    assert '<span class="fr-pc-meta"><span class="fr-pill fr-pill-high">High priority</span> &middot; Sensitivity' in summary
    assert '<span dir="auto" class="fr-pc-title-txt">Embed early warning indicators</span>' in summary
    assert "<h3" not in summary
    assert "Priority 1" not in summary and "<svg" in summary
    assert summary.index("fr-pc-meta") < summary.index("fr-pc-title-txt")


def test_draft_copy_button_has_no_model_text_in_handler():
    html = normal({"priorities": [dict(NORMAL_PRIORITY, actions=[{"document_element": "RF", "guidance": "g",
                                                                  "suggested_language": "Quote ' and \" text"}])]})
    start = html.index('<button type="button" class="fr-copy"')
    button = html[start:html.index("</button>", start)]
    assert "data-copy-skip" in button and "Quote" not in button
    assert "querySelector('.fr-draft-text').innerText" in button
    assert '<p dir="auto" class="fr-draft-text">Quote' in html


def test_expand_all_control_only_with_several_cards():
    html = normal({})
    assert html.index('class="fr-expand"') < html.index('class="fr-cards"')
    assert ">Expand all</button>" in html and "details.fr-pc" in html
    single = normal({"priorities": [NORMAL_PRIORITY]})
    assert "fr-expand" not in single


def test_jump_nav_links_every_numbered_section():
    html = normal({})
    nav = html[html.index('<nav class="fr-toc"'):html.index("</nav>")]
    assert html.index("fr-scorecard") < html.index('<nav class="fr-toc"') < html.index(">Executive Summary<")
    for i, title in enumerate(["Executive Summary", "FCV Risk Exposure", "FCV Sensitivity and Responsiveness",
                               "Priority Actions for the Task Team", "Watch List for Supervision"], start=1):
        assert f'<a href="#fr-s{i:02d}">{title}</a>' in nav
        assert f'<header class="fr-h1" id="fr-s{i:02d}">' in html
    assert "data-copy-skip" in nav


def test_prose_and_titles_carry_dir_auto_and_copy_skip_markers():
    html = climate(CLIMATE_READER)
    assert '<p dir="auto" class="fr-p">' in html and '<p class="fr-p">' not in html
    assert 'class="fr-sc-scale" data-copy-skip' in html and 'data-copy-skip>' in html
    assert 'class="fr-pill fr-pill-conf fr-pill-conf-medium"' in html
