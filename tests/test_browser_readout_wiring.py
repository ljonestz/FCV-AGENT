"""index.html is wired to static/fcv_readout.js and drops the old Summary/rail/stepper."""

import json
import subprocess
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"
MODULE = Path(__file__).resolve().parents[1] / "static" / "fcv_readout.js"


def html():
    return INDEX.read_text(encoding="utf-8")


def test_module_and_styles_loaded():
    source = html()
    assert '<script src="/static/fcv_readout.js"></script>' in source
    assert '<style id="fcv-readout-style">' in source
    assert "function frApi(" in source
    assert ".fr-scorecard{" in source and ".fr-pc-hdr{" in source and "@media(max-width:760px)" in source


def test_normal_route_uses_readout_module():
    source = html()
    assert "function renderNormalReadoutHtml(" in source
    assert "frApi().renderNormal(" in source
    assert "function renderGoDeeperHtml(idx)" in source
    assert "priorityExtras:" in source


def test_climate_route_uses_readout_module():
    source = html()
    start = source.index("function renderClimateVerifiedAssessment(")
    body = source[start:source.index("\n  }\n", start)]
    assert "frApi().renderClimate(" in body
    assert "Draft - human review required." not in body  # generic preamble removed upstream (2026-10-28)
    assert "stage3AdvisoryText('climate')" in body


def test_summary_tab_rail_and_stepper_removed():
    source = html()
    for gone in ["function stage3ViewToggleHtml(", "function renderStage3Summary(", "function renderNormalFcvSummary(",
                 "function setStage3View(", "function renderPriorityStepper(",
                 'id="priority-stepper"', 'id="priority-card-area"', "function renderClimateVerifiedSummary(",
                 "function renderSummaryPriorityAccordion("]:
        assert gone not in source, gone
    start = source.index("function renderManagementBriefControls(")
    assert "stage3View" not in source[start:source.index("}", start)]


def test_share_html_export_reuses_readout():
    source = html()
    start = source.index("async function downloadHTML(")
    body = source[start:source.index("\n  }\n", start)]
    assert "buildNormalReadout(" in body
    assert "screenerCaveatHtml()" in body
    assert "_buildExportPriorityCard" not in body


def function_body(source, signature):
    start = source.index(signature)
    return source[start:source.index("\n  }\n", start)]


def test_screen_and_export_share_normal_readout_builder():
    source = html()
    builder = function_body(source, "function buildNormalReadout(")
    for part in ["stage3NoticesHtml(", "stage3DocChecksHtml()", "renderClimateGroundingSources(", "wrapSRTerms(", "renderNormalReadoutHtml("]:
        assert part in builder, part
    notices = function_body(source, "function stage3NoticesHtml(")
    for part in ["isClosedOrCompletedProject()", "isFinalizedPAD()", "stage-awareness-badge", "state.notice"]:
        assert part in notices, part
    assert "_outBodyContent=buildNormalReadout(result);" in function_body(source, "function renderOut(")
    export = function_body(source, "async function downloadHTML(")
    assert "buildNormalReadout(stageOutputs[3]||'',true,_briefHtml)" in export
    assert "renderNormalReadoutHtml(" not in export
    assert "priorityExtras:forExport?renderNormalExportPriorityExtras:renderNormalPriorityExtras" in source
    assert "renderGoDeeperHtml" not in function_body(source, "function renderNormalExportPriorityExtras(")


def test_print_opens_readout_disclosures():
    source = html()
    handler = function_body(source, "function installClimatePrintDisclosureHandler(")
    for sel in ["details.fr-pc", "details.fr-disc", "details.priority-context-disclosure"]:
        assert sel in handler, sel
    assert "\n  installClimatePrintDisclosureHandler(document);" in source
    assert "climatePrintDisclosureScript()" in function_body(source, "async function downloadHTML(")
    assert ".fr-pc-body,.fr-disc-body{display:block" not in source


def test_copy_text_drops_go_deeper_and_warnings():
    body = function_body(html(), "function reportPlainText(")
    assert "details.go-deeper" in body and ".warn-badge" in body


def test_copy_text_strips_navigation_and_decoration():
    body = function_body(html(), "function reportPlainText(")
    for sel in ["[data-copy-skip]", ".fr-sc-scale", ".fr-h1-num", ".fr-pc-rank", ".fr-meter", ".fr-toc"]:
        assert sel in body, sel


def test_glossary_skips_headings_labels_and_summaries():
    source = html()
    assert "const GLOSSARY_SKIP_SELECTOR='summary, h1, h2, h3, h4, .fr-sc-label, .fr-lbl, .fr-rating-dim, .fr-pc-meta, .fr-h1';" in source
    body = function_body(source, "function annotateGlossaryTerms(")
    assert "parent.closest(GLOSSARY_SKIP_SELECTOR)" in body and "span.tabIndex = 0;" in body
    assert ".glossary-term:focus-within .glossary-tooltip" in source and "max-width: min(320px, 90vw);" in source


def test_readout_css_is_scoped_and_dead_code_removed():
    source = html()
    css = source[source.index('<style id="fcv-readout-style">'):source.index("</style>", source.index('<style id="fcv-readout-style">'))]
    assert ".fr-readout h2,.fr-readout h3,.fr-readout h4{font-family:Arial,sans-serif!important" in css
    assert "overflow-wrap:anywhere" in css and "print-color-adjust:exact" in css and "::details-content" in css
    for gone in [".fr-pt-num", ".fr-notice", "#f3e8ff"]:
        assert gone not in source, gone
    for gone in ["_buildExportPriorityCard", ".exp-table", ".exp-pcard", ".exp-ratings-row", ".exp-rating-pill"]:
        assert gone not in source, gone


def test_removed_summary_state_is_gone():
    source = html()
    for gone in ["stage3View", "openSummaryPriority", "supportsAnyStage3Summary", "renderFcvRatingIndicators",
                 "_supportsClimateStage3", ".priority-stepper", ".ps-step", ".horizon-panel", ".summary-priority-",
                 "#summary-priority-accordion", ".stage3-viewbar", ".concise-readout", ".pi-lead"]:
        assert gone not in source, gone


def test_parser_splits_bold_lead_from_supporting_text():
    script = ("const FR=require(" + json.dumps(str(MODULE)) + ");"
              "process.stdout.write(JSON.stringify(FR.parseStage3Sections("
              + json.dumps("## Executive Summary\n\n**Verdict sentence.** More detail here.\n\n### Strengths\n\nS.")
              + ")));")
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    sections = json.loads(result.stdout)
    assert sections["snapshot"] == "Verdict sentence."
    assert sections["leadRest"] == "More detail here."
    assert not any("More detail here." in o["body"] for o in sections["other"])


def test_peer_review_chip_does_not_interpolate_doc_type_into_handler():
    source = html()
    assert 'onclick="prefillFollowon(followonPeerReviewText())"' in source
    assert "prefillFollowon(&quot;Draft a peer review note for this ${docType" not in source
    assert "(docType||'project')" in function_body(source, "function followonPeerReviewText(")


def test_timing_labels_are_advisory_and_match_word_export():
    source = html()
    start = source.index("const TIMING_LABELS={")
    labels = source[start:source.index("};", start)]
    assert "Required" not in labels
    assert "'required-before-appraisal':'Address before Decision Review (DM/ROC)'" in labels
    assert "'required-before-board':'Address before Board'" in labels
    assert "'flag-for-preparation':'Consider during preparation'" in labels
    app = (INDEX.parent / "app.py").read_text(encoding="utf-8")
    timing = app[app.index("timing_map = {"):app.index("}", app.index("timing_map = {"))]
    assert "Required" not in timing and "'required-before-board': 'Address before Board'" in timing
    assert "Essential Action" not in app


def test_climate_partial_notices_merge_into_one_box():
    body = function_body(html(), "function renderClimateVerifiedAssessment(")
    assert "<strong>This run is partial.</strong>" in body
    assert "Fewer items does not mean fewer risks or gaps. Check the limitations at the end of this note before sharing." in body
    assert "if(_evidencePartial&&_recsPartial)" in body and "(_recsPartial&&!_evidencePartial)" in body


def test_export_help_text_sits_in_download_menu():
    source = html()
    assert "Full report includes all priority actions" not in source
    assert '<p class="report-download-help">Word (.docx): priorities and suggested text for the PAD team.</p>' in source
    assert '<p class="report-download-help">HTML: adds the research briefing and Stage 2 annex, for FCV review.</p>' in source


def test_stage3_result_resets_previous_stage3_state():
    source = html()
    reset = function_body(source, "function resetStage3State(")
    for part in ["stageThreePriorities=[]", "stageRiskExposure=null", "stageSensitivitySummary=''", "midCycleWatch=[]", "horizonConsiderations=''"]:
        assert part in reset, part
    run = function_body(source, "async function runStage(")
    assert "if(stage===3){\n                resetStage3State();" in run
    express = function_body(source, "async function runExpress(")
    assert "else if(sn===3){\n              resetStage3State();" in express


def test_sidebar_priority_lookup_uses_rank_order_on_climate_route():
    body = function_body(html(), "function selectPrioritySb(")
    assert "supportsClimateVerifiedStage3View()" in body and "Number(a.rank)" in body


def test_stage3_has_no_duplicate_status_callout():
    body = function_body(html(), "function renderOut(")
    assert "${isLast?'':`<div class=\"callout ${_calloutTone} ani\">" in body


def test_export_research_briefing_is_cleaned_and_collapsed():
    source = html()
    helper = function_body(source, "function exportResearchBriefHtml(")
    export = function_body(source, "async function downloadHTML(")
    assert "exportResearchBriefHtml(researchBrief)" in export
    assert "Research briefing</h2>" not in export
    assert '<details class="fr-disc fr-research"><summary class="fr-disc-sum">Background research and sources</summary>' in export
    brief = ("I'll run a small set of searches first.\n\n\\#\\#\\# Security\n\nViolence rose \\[uncited link removed\\].\n\n"
             "> \\\n\n> Quoted excerpt.\n\n> Quoted excerpt.")
    script = "const md=t=>'<md>'+t+'</md>';\n" + helper + "\n}\nprocess.stdout.write(exportResearchBriefHtml(" + json.dumps(brief) + "));"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "I'll run" not in out and "\\" not in out
    assert "### Security" in out and "[uncited link removed]" in out
    assert out.count("Quoted excerpt.") == 1




def test_tab_title_and_icon_track_run_status():
    source = html()
    assert "<title>FCV Screener</title>" in source
    assert '<link rel="icon" id="tab-icon" type="image/svg+xml" href="data:image/svg+xml,' in source
    helper = function_body(source, "function setTabStatus(")
    for part in ["TAB_STAGE_VERBS[stage]", "[Complete] ", "[Needs attention] ", "document.hidden", "TAB_TITLE_BASE", "setTabIcon(state);"]:
        assert part in helper, part
    assert "document.addEventListener('visibilitychange'" in source
    run = function_body(source, "async function runStage(")
    assert "setTabStatus('running',stage);" in run
    assert "setTabStatus(stage===3?(p.parse_error?'error':'complete'):'done',stage);" in run
    express = function_body(source, "async function runExpress(")
    assert "setTabStatus('running',1);" in express and "setTabStatus('running',currentStage);" in express
    assert "setTabStatus('complete',3);" in express
    assert "setTabStatus('error',stage);" in function_body(source, "function showErr(")
    assert "setTabStatus('error',stage);" in function_body(source, "function showExpressError(")
    assert "setTabStatus('idle');" in function_body(source, "function reset(")
    assert "setTabStatus(stageOutputs&&stageOutputs[3]?'loaded':'idle');" in function_body(source, "function loadSession(")
    icons_start = source.index("const TAB_ICONS={")
    icons = source[icons_start:source.index("};", icons_start) + 2]
    script = ("let tabTitleDot=false;const TAB_TITLE_BASE='FCV Screener';const TAB_STAGE_VERBS={1:'Reading',2:'Assessing',3:'Drafting'};"
              "const link={href:'',setAttribute(k,v){this[k]=v;}};const document={hidden:true,title:'',getElementById:()=>link};\n"
              + icons + "\n" + function_body(source, "function setTabIcon(") + "\n}\n" + helper + "\n}\n"
              "const out=[];const icon=()=>decodeURIComponent(link.href);"
              "setTabStatus('running',2);out.push(document.title,icon());"
              "setTabStatus('complete',3);out.push(document.title,icon());"
              "document.hidden=false;setTabStatus('error',1);out.push(document.title,icon());"
              "setTabStatus('idle');out.push(document.title,icon());"
              "process.stdout.write(JSON.stringify(out));")
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    out = json.loads(result.stdout)
    assert out[0] == "[Stage 2 of 3 \u00b7 Assessing] FCV Screener" and 'stroke="#009FDA"' in out[1]
    assert out[2] == "\u25cf [Complete] FCV Screener" and 'M9 16.5l5 5 9-10' in out[3]
    assert out[4] == "[Needs attention] FCV Screener" and 'fill="#F2A900"' in out[5]
    assert out[6] == "FCV Screener" and '<rect width="32" height="32" fill="#002244"/>' in out[7] and ">F</text>" in out[7]


def test_normal_readout_wires_smaller_points_limitations_and_partial():
    source = html()
    readout = function_body(source, "function renderNormalReadoutHtml(")
    for part in ["parseSupplementaryPoints(stageOutputs[2]||'')", "fileNames:readoutFileNames()", "researchBrief",
                 "partial:normalReadoutIsPartial(climate)", "researchHtml"]:
        assert part in readout, part
    partial = function_body(source, "function normalReadoutIsPartial(")
    assert "!stageOutputs[1]||!stageOutputs[2]" in partial and "climateReadoutComplete(state.entry)" in partial
    files = function_body(source, "function readoutFileNames(")
    assert "restoredFileNames.project" in files and "restoredFileNames.context" in files
