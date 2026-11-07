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
    assert ">01<" in html and ">07<" in html and ">08<" not in html
    assert html.index('fr-h1-txt">Watch List for Supervision<') < html.index('fr-h1-txt">Relevant WBG Guidance<') < html.index('fr-h1-txt">Limitations<')
    assert html.index("id='tail'") < html.index('fr-h1-txt">Limitations<')
    assert "fr-ptable" not in html and "Strategic Priorities" not in html
    assert "2 priority actions are identified by the FCV Screener." in html
    assert html.count('class="fr-ms fr-c') == 4 + 3
    assert "Address before Decision Review (DM/ROC)" in html and "Required" not in html
    assert "Sensitivity + Responsiveness" in html[html.index('id="fr-priority-1"'):]
    assert 'id="fr-priority-1" data-fr-src-index="0" open>' in html and 'id="fr-priority-2" data-fr-src-index="1">' in html
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
             'fr-h1-txt">Assessment Findings<', 'fr-h1-txt">Climate-FCV Sensitivity and Responsiveness<',
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
    closing = '<p class="fr-note fr-closing">This automated screening supports task-team judgment. It is not a compliance, eligibility or clearance decision.</p>'
    assert normal({}).endswith(closing + "</article>")
    assert climate(CLIMATE_READER).endswith(closing + "</article>")
    already = climate(dict(CLIMATE_READER, advisory_notice="This note does not constitute a clearance."))
    assert "fr-closing" not in already


def test_climate_fallback_overview_moves_to_limitations():
    reader = dict(CLIMATE_READER, reader_contract="final-reader-v1", summary_overview_status="fallback",
                  summary_overview=["A short summary is not shown for this run.", "Use the priorities."])
    html = climate(reader)
    overview = html[html.index('fr-h1-txt">Overview<'):html.index('fr-h1-txt">Assessment Findings<')]
    assert "A short summary" not in overview and "Assessment snapshot" not in overview
    assert "What is already working" in overview and "Key gaps at this stage" not in overview
    limits = html[html.index('class="fr-limits"'):]
    assert limits.index("A short summary is not shown for this run.</strong> Use the priorities.") < limits.index("Concept stage only.")
    # Single-sentence Limitations paragraphs are not bold.
    assert '<p dir="auto" class="fr-p">Concept stage only.</p>' in limits
    assert html.count("A short summary is not shown") == 1


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
    assert '<span class="fr-pc-meta"><span class="fr-meta-seg"><span class="fr-pill fr-pill-high">High priority</span></span><span class="fr-meta-seg"> &middot; Sensitivity' in summary
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


STAGE2_MD = """## Do No Harm

Text.

## Supplementary FCV Dimensions
- **SORT adequacy:** Ratings look low. [S]
- **Gender and GBV**: Reporting channels are missing. [S+R]
- Not a bold bullet.
- **Empty label:**

### Nested note
- **Nested:** still inside.

## Synthesis

- **FCV Sensitivity:** Not a supplementary point.
"""


def test_supplementary_points_parse_labels_and_strip_tags():
    out = json.loads(run_js(f"process.stdout.write(JSON.stringify(FR.parseSupplementaryPoints({json.dumps(STAGE2_MD)})));"))
    assert out == [{"title": "SORT adequacy", "why": "Ratings look low."},
                   {"title": "Gender and GBV", "why": "Reporting channels are missing."},
                   {"title": "Empty label", "why": ""},
                   {"title": "Nested", "why": "still inside."}]
    assert json.loads(run_js("process.stdout.write(JSON.stringify(FR.parseSupplementaryPoints('## Synthesis\\n- **A:** b')));")) == []


def test_normal_smaller_points_section_order_and_skip():
    html = normal({"smallerPoints": [{"title": "SORT adequacy", "why": "Ratings look low."}]})
    order = ['fr-h1-txt">Priority Actions for the Task Team<', 'fr-h1-txt">Smaller Points to Check During Preparation<',
             "Smaller checks for the project team to confirm", "None is a reason to stop the project.", 'class="fr-check-title">SORT adequacy<',
             'fr-h1-txt">Watch List for Supervision<', 'fr-h1-txt">Limitations<']
    positions = [html.index(marker) for marker in order]
    assert positions == sorted(positions)
    assert ">05</span><h2 class=\"fr-h1-txt\">Smaller Points" in html
    assert 'href="#fr-s05">Smaller Points to Check During Preparation<' in html
    assert "How to address" not in html
    assert "Smaller Points" not in normal({"smallerPoints": []})


def test_normal_limitations_lines_and_closing_after():
    html = normal({"fileNames": ["PAD v3.docx", "RRA.docx"], "researchBrief": "x\nResearch run timestamp: 2026-11-07T08:20:40+00:00 (retrieval time).",
                   "partial": True})
    lim = html[html.index('fr-h1-txt">Limitations<'):]
    assert "Documents uploaded for this run: PAD v3, RRA." in lim and "draws only on" not in lim
    assert "Background research was retrieved on 7 November 2026; events after that date are not reflected." in lim
    assert "This run is partial; some sections may be missing." in lim
    assert "Findings are based on the text of the project documents and may miss arrangements described elsewhere." in lim
    assert lim.index('class="fr-limits"') < lim.index("fr-closing")
    bare = normal({})
    lim = bare[bare.index('fr-h1-txt">Limitations<'):]
    assert "uploaded for this run" not in lim and "retrieved on" not in lim and "partial" not in lim
    assert "Ratings and priorities are advisory" in lim
    assert "\u2014" not in html


def test_normal_research_briefing_after_limitations_collapsed():
    html = normal({"researchHtml": "<p>Brief body</p>"})
    assert html.index('fr-h1-txt">Limitations<') < html.index("Background research and sources") < html.index("fr-closing")
    assert '<details class="fr-disc fr-research"><summary class="fr-disc-sum">Background research and sources</summary>' in html
    assert "Background research" not in normal({})



def test_normal_priorities_display_high_medium_low_stably():
    pri = [dict(NORMAL_PRIORITY, title="Low one", risk_level="Low"), dict(NORMAL_PRIORITY, title="Med one", risk_level="Medium"),
           dict(NORMAL_PRIORITY, title="High one", risk_level="High"), dict(NORMAL_PRIORITY, title="Med two", risk_level="medium"),
           dict(NORMAL_PRIORITY, title="High two", risk_level="High")]
    html = normal({"priorities": pri})
    titles = ["High one", "High two", "Med one", "Med two", "Low one"]
    positions = [html.index(f'class="fr-pc-title-txt">{t}<') for t in titles]
    assert positions == sorted(positions)
    card1 = html[html.index('id="fr-priority-1"'):html.index('id="fr-priority-2"')]
    assert ">High one<" in card1 and 'data-fr-src-index="2"' in card1 and '<span class="fr-pc-rank">1</span>' in card1
    card5 = html[html.index('id="fr-priority-5"'):]
    assert ">Low one<" in card5 and 'data-fr-src-index="0"' in card5
    assert 'id="fr-priority-1" data-fr-src-index="2" open>' in html
    # Extras keep the stored index (Go Deeper and warnings look up stageThreePriorities[idx]).
    assert card1.index('class="extra-2"') > 0 and 'class="extra-0"' in card5
    order = json.loads(run_js("process.stdout.write(JSON.stringify(FR.orderByLevel([{risk_level:'Low'},{risk_level:''},{risk_level:'High'}]).map(x=>x.index)));"))
    assert order == [2, 0, 1]


def test_normal_cycle_label_reads_implementation_note():
    html = normal({})
    assert "<strong>Implementation note:</strong> Before mobilisation." in html
    html = normal({"priorities": [dict(NORMAL_PRIORITY, implementation_note="", project_cycle={"primary_label": "Before Board", "primary_text": "Agree it."})]})
    assert "<strong>Before Board:</strong> Agree it." in html and "Implementation note" not in html


def test_tag_justification_sentences_are_stripped_from_card_prose():
    pri = dict(NORMAL_PRIORITY, the_gap="No indicators exist. Tagged [S] because it avoids harm. More detail.",
               why_it_matters="Risks go undetected. Tagged [S+R] since both apply.",
               actions=[{"document_element": "RF", "guidance": "Add one. Tagged [R] as it adapts.", "suggested_language": "Indicator."}])
    html = normal({"priorities": [pri]})
    assert "Tagged [" not in html
    assert "No indicators exist." in html and "More detail." in html and "Add one." in html
    reader = dict(CLIMATE_READER, priorities=[dict(CLIMATE_READER["priorities"][1], narrative="Why one. Tagged [S] for harm.\n\nAct one.")])
    assert "Tagged [" not in climate(reader)


def test_meter_caption_and_climate_confidence_pills():
    html = normal({})
    assert '<span class="fr-sc-of">4 of 6</span>' in html and '<span class="fr-sc-of">3 of 6</span>' in html
    chtml = climate(CLIMATE_READER)
    assert '<span class="fr-sc-of">3 of 5</span>' in chtml
    count = chtml[chtml.index('class="fr-sc-count"'):chtml.index("</section>", chtml.index('class="fr-sc-count"'))]
    assert ">1 medium confidence<" in count and ">1 low confidence<" in count and "Confidence:" not in count
    assert count.index(">1 medium confidence<") < count.index('class="fr-pill-sep" aria-hidden="true">&middot;<') < count.index(">1 low confidence<")


def test_climate_count_tile_reads_actions_and_confidence_when_uniform():
    reader = dict(CLIMATE_READER, priorities=[dict(p, confidence="medium") for p in CLIMATE_READER["priorities"]]
                  + [dict(CLIMATE_READER["priorities"][0], rank=3, confidence="medium")])
    html = climate(reader)
    count = html[html.index('class="fr-sc-count"'):html.index("</section>", html.index('class="fr-sc-count"'))]
    assert '<span class="fr-pill fr-pill-conf fr-pill-conf-medium">3 actions · medium confidence</span>' in count
    assert "fr-pill-sep" not in count
    one = climate(dict(CLIMATE_READER, priorities=[dict(CLIMATE_READER["priorities"][1], confidence="high")]))
    assert ">1 action · high confidence<" in one
    mixed = climate(dict(CLIMATE_READER, priorities=[dict(CLIMATE_READER["priorities"][0], confidence="medium"),
                                                     dict(CLIMATE_READER["priorities"][1], confidence="high"),
                                                     dict(CLIMATE_READER["priorities"][0], rank=3, confidence="medium")]))
    assert ">1 high confidence<" in mixed and ">2 medium confidence<" in mixed


def test_card_meta_segments_mark_dimension_and_timing_for_mobile():
    html = normal({})
    card = html[html.index('id="fr-priority-1"'):html.index('id="fr-priority-2"')]
    assert '<span class="fr-meta-seg fr-meta-dim"> &middot; Security</span>' in card
    assert '<span class="fr-meta-seg fr-meta-time"> &middot; Address before Decision Review (DM/ROC)</span>' in card


def test_climate_key_gaps_only_as_fallback_without_findings():
    html = climate(CLIMATE_READER)
    overview = html[html.index('fr-h1-txt">Overview<'):html.index('fr-h1-txt">Assessment Findings<')]
    assert "Key gaps at this stage" not in overview and "Gap one" not in html and "See section 02" not in html
    assert 'id="fr-s02"><span class="fr-h1-num">02</span><h2 class="fr-h1-txt">Assessment Findings<' in html
    plain = climate(dict(CLIMATE_READER, assessment_themes=[]))
    assert "Key gaps at this stage" in plain and "Assessment Findings" not in plain
    assert "Gap one. Detail." in plain.replace("<strong>", "").replace("</strong>", "") and "See section 02" not in plain


def test_climate_practical_considerations_bold_first_sentence_only():
    pri = dict(CLIMATE_READER["priorities"][1], limitation="Rules are not shown.", caution="Test with partners.")
    html = climate(dict(CLIMATE_READER, priorities=[pri]))
    zone = html[html.index(">Practical considerations<"):]
    assert "<strong>Rules are not shown.</strong> Test with partners." in zone


PINNED = ["Maximizing the Peace and Social Dividends of Climate Action", "FCV-Sensitive Climate Action Framework", "Defueling Conflict"]


def guidance_block(html: str) -> str:
    start = html.index('fr-h1-txt">Relevant WBG Guidance<')
    return html[start:html.index('fr-h1-txt">Limitations<')]


def test_pinned_climate_reports_on_climate_route_only_in_order():
    block = guidance_block(climate(CLIMATE_READER))
    positions = [block.index(f">{t}</a>") for t in PINNED]
    assert positions == sorted(positions)
    assert positions[-1] < block.index(">Good</a>")
    assert 'Selected WBG resources for the team' in block
    normal_block = guidance_block(normal({}))
    assert all(t not in normal_block for t in PINNED)
    assert normal_block.count('class="fr-guide"') == 7
    assert "Relevant to this project" not in normal_block
    assert normal_block.index("Strategy for Engaging in FCV Settings (2026-2030)") < normal_block.index(">Forced Displacement</a>")


def test_climate_pinned_report_from_server_is_not_duplicated_and_blurb_renders():
    item = {"title": "fcv-sensitive  climate action framework", "url": "https://example.org/f",
            "practical_value": "Server blurb for the framework.", "project_use": "Project use text."}
    other = {"title": "Other", "url": "https://example.org/o", "project_use": "Only project use."}
    block = guidance_block(climate(dict(CLIMATE_READER, guidance_items=[other, item])))
    assert block.count("limate action framework</a>") == 1 and 'href="https://example.org/f"' in block
    assert "Server blurb for the framework." in block and "Project use text." not in block
    assert "Only project use." in block
    assert block.index("Defueling Conflict") < block.index(">Other</a>")


def test_climate_guidance_matched_question_line_and_unmatched_items():
    reader = dict(CLIMATE_READER, core_questions=[
        {"question_id": "cq1", "theme": "cq1_interaction", "source": "Defueling  conflict"},
        {"question_id": "cq3-shared-benefit", "theme": "cq3_dividends", "source": "Defueling Conflict"},
        {"question_id": "cq9", "theme": "cq3_dividends", "source": "Unknown Source"}],
        assessment_themes=[{"title": "Climate risks, design and delivery", "paragraphs": ["P."], "priority_ranks": []},
                           {"title": "Access, inclusion and potential harm", "question": "Shown inclusion question?", "paragraphs": ["Q."], "priority_ranks": []}])
    block = guidance_block(climate(reader))
    item = block[block.index(">Defueling Conflict</a>"):]
    item = item[:item.index("</div>")]
    assert ('<p class="fr-guide-rel">Relevant to this project: informs the findings on <a href="#fr-s02">climate risks, design and delivery</a>'
            ' and on <a href="#fr-s02">access, inclusion and potential harm</a> (section 02).</p>') in item
    assert block.count("Relevant to this project") == 1
    framework = block[block.index(">FCV-Sensitive Climate Action Framework</a>"):]
    assert "Relevant to this project" not in framework[:framework.index("</div>")]
    no_themes = guidance_block(climate(dict(reader, assessment_themes=[])))
    assert "Relevant to this project" not in no_themes


VERIFY_A = "[Verify before sharing: Check PF-012 (block 46ab9ca6aba6) and PF-021: the displacement statement is general. Confirm the wording.]"
VERIFY_B = ("[Verify before sharing: Check PF-020 and PF-012 and source blocks 28ef88b92d85 and 46ab9ca6aba6: drainage is expected. "
            "Confirm the link.]")


def test_verify_notes_leave_prose_and_list_once_in_limitations():
    reader = dict(CLIMATE_READER, summary_overview=[f"Snapshot sentence. {VERIFY_A}", "Second overview paragraph."],
                  assessment_themes=[{"title": "Climate risks, design and delivery", "paragraphs": [f"Theme para. {VERIFY_B}", f"More. {VERIFY_A}"],
                                      "priority_ranks": [1]}])
    html = climate(reader)
    assert "Verify before sharing:" not in html and "PF-0" not in html and "46ab9ca6aba6" not in html and "28ef88b92d85" not in html
    info = html[html.index("Assessment snapshot"):html.index("</div></div>", html.index("Assessment snapshot"))]
    assert "<strong>Snapshot sentence.</strong>" in info
    limits = html[html.index('class="fr-limits"'):]
    assert ">Points to verify before sharing<" in limits
    items = limits[limits.index("<ul"):limits.index("</ul>")]
    assert items.count("<li") == 2
    assert '<li dir="auto">The displacement statement is general. Confirm the wording.</li>' in items
    assert '<li dir="auto">Drainage is expected. Confirm the link.</li>' in items
    assert "Points to verify" not in climate(CLIMATE_READER)
    # The stored reader is not modified.
    assert VERIFY_A in json.dumps(reader)


def test_verify_notes_are_scrubbed_on_the_normal_route():
    html = normal({"sensitivitySummary": f"Sensitivity is Adequate. {VERIFY_A}"})
    assert "Verify before sharing:" not in html and "PF-012" not in html
    assert "Points to verify before sharing" in html[html.index('class="fr-limits"'):]


def test_clean_verify_note_keeps_meaningful_lead_clause():
    out = json.loads(run_js("process.stdout.write(JSON.stringify([FR.cleanVerifyNote('Check the PAD annex (source block 0123456789ab): dates differ.'),"
                            "FR.cleanVerifyNote('Check PF-1: x.')]));"))
    assert out == ["Check the PAD annex: dates differ.", "X."]


def test_legacy_climate_fallback_sentences_are_replaced():
    legacy = ["The automated Summary could not be independently verified. The operational context and assessment findings provide the available analysis.",
              "Use the ranked operational priorities and points to check as the basis for review. Confirm the stated evidence limitations before relying on the brief."]
    html = climate(dict(CLIMATE_READER, reader_contract="final-reader-v1", summary_overview_status="fallback", summary_overview=legacy))
    assert "could not be independently verified" not in html and "Use the ranked operational priorities" not in html
    assert html.count("A short summary is not shown for this run because it could not be checked against the project documents.") == 1


def test_climate_drafts_follow_what_the_team_could_do():
    pri = dict(CLIMATE_READER["priorities"][1], caution="A separate caution.", enhanced_action="Extra step.")
    html = climate(dict(CLIMATE_READER, priorities=[pri]))
    card = html[html.index('id="fr-priority-1"'):]
    assert card.index(">What the team could do<") < card.index('class="fr-draft"') < card.index(">Practical considerations<") < card.index(">Optional further work<")


def test_research_briefing_lists_sources_from_paid_session():
    session = json.loads((ROOT / "output" / "20261106_readout-paid-runs" / "20261107_normal-afghanistan-hcj-pad-session.json").read_text(encoding="utf-8"))

    def find(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "researchBrief":
                    return v
                r = find(v)
                if r:
                    return r
        return None

    brief = find(session)
    if brief is None:
        brief = ("Research run timestamp: 2026-11-07T08:20:40+00:00 (retrieval time).\n\n#### Provider-cited source-backed excerpts\n"
                 "- [Report one](https://news.un.org/a) - 0 days ago\n  > Excerpt one.\n- [Report one](https://news.un.org/a) - 0 days ago\n  > Other.\n")
    out = run_js(f"process.stdout.write(api.researchBriefing({json.dumps(brief)}));")
    assert out.startswith('<p class="fr-p fr-research-intro">Public sources retrieved on 7 November 2026 to supplement the project documents.</p><ul class="fr-research-list">')
    for bad in ["####", "](", "&gt;", "days ago", "\\", "**"]:
        assert bad not in out, bad
    hrefs = [part.split('"')[0] for part in out.split('href="')[1:]]
    assert hrefs and len(hrefs) == len(set(hrefs)) and all(h.startswith("https://") for h in hrefs)


def test_research_briefing_rejects_unsafe_urls_and_handles_unstructured_text():
    brief = ("#### Provider-cited source-backed excerpts\n- [Bad](javascript:alert(1)) - 3 days ago\n  > Evil.\n"
             "- [Good](https://example.org/x) - 1 day ago\n  >\n  > Kept **excerpt**.\n")
    out = run_js(f"process.stdout.write(api.researchBriefing({json.dumps(brief)}));")
    assert "javascript:" not in out and "Evil." not in out
    assert '<a href="https://example.org/x" target="_blank" rel="noopener noreferrer">Good</a><span class="fr-research-ex" dir="auto">Kept excerpt.</span>' in out
    assert "Public sources retrieved to supplement the project documents." in out
    plain_brief = "I'll search first.\n\n\\#\\# Security\n\nViolence rose.\n\n> Quote."
    plain = run_js(f"process.stdout.write(api.researchBriefing({json.dumps(plain_brief)}));")
    assert plain == '<p dir="auto" class="fr-p">Violence rose.</p><p dir="auto" class="fr-p">Quote.</p>'


def test_parenthetical_internal_ids_are_dropped_from_prose():
    out = json.loads(run_js("process.stdout.write(JSON.stringify(FR.extractVerifyNotes('Standards apply (PF-008, PF-010). Not found (RG-001). Keep (PAD, 2024).', [])));"))
    assert out == "Standards apply. Not found. Keep (PAD, 2024)."
    reader = dict(CLIMATE_READER, existing_responses=[{"description": "Airstrips were screened (PF-011)."}])
    html = climate(reader)
    assert "PF-011" not in html and "Airstrips were screened." in html
