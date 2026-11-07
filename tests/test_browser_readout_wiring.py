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
    for sel in ["details.fr-pc", "details.fr-disc"]:
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
    assert "const GLOSSARY_SKIP_SELECTOR='summary, h1, h2, h3, h4, .fr-sc-label, .fr-lbl, .fr-rating-dim, .fr-pc-meta, .fr-h1, .fr-h1-txt, .fr-toc a';" in source
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


def test_export_research_briefing_uses_renderer_source_list():
    source = html()
    helper = function_body(source, "function exportResearchBriefHtml(")
    export = function_body(source, "async function downloadHTML(")
    assert "exportResearchBriefHtml(researchBrief)" in export
    assert "Research briefing</h2>" not in export
    assert "<summary class=\"fr-disc-sum\"><span>Background research and sources</span><span class=\"fr-disc-chev\" aria-hidden=\"true\">'+frApi().CHEVRON_SVG+'</span></summary>" in export
    # Raw markdown is never passed through md(); the renderer builds the intro line and link list.
    assert "frApi().researchBriefing(brief)" in helper and "md(" not in helper


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


def test_readout_width_disclosure_chevrons_and_mobile_meta():
    source = html()
    style = source[source.index('<style id="fcv-readout-style">'):]
    style = style[:style.index("</style>")]
    assert "74ch" not in style and ".fr-readout{max-width:1040px}" in style
    assert ".fr-readout .fr-h1-num{font-size:12px;font-weight:700;color:var(--fr-blue-text);flex:none;white-space:nowrap}" in style
    # Timing stays visible on phones; only the dimension segment is hidden.
    assert "@media(max-width:760px){.fr-readout .fr-pc-meta .fr-meta-dim{display:none}" in style
    assert "fr-meta-time{display:none}" not in style
    assert '<span class="beyond-arrow" aria-hidden="true">${window.FcvReadout.CHEVRON_SVG}</span>' in function_body(source, "function renderGoDeeperHtml(")
    assert "renderStandardPriorityContext" not in source and "pcd-chev" not in source
    assert 'details.fr-pc[data-fr-src-index="' in function_body(source, "function selectPrioritySb(")


def test_readout_pills_text_size_limits_and_mobile_scroll_margin():
    source = html()
    style = source[source.index('<style id="fcv-readout-style">'):]
    style = style[:style.index("</style>")]
    # One pill box on both routes; confidence pills only switch to an outline.
    assert ".fr-readout .fr-pill{display:inline-block;padding:1px 7px;font-size:11px;font-weight:700;line-height:1.4;border:1px solid transparent;border-radius:3px;" in style
    assert ".fr-readout .fr-pill-conf{background:transparent;border-color:currentColor}" in style
    assert "@media(min-width:1024px){.fr-readout,.fr-readout .fr-p,.fr-readout .fr-md,.fr-readout .fr-info,.fr-readout .fr-actions{font-size:15px;line-height:1.6}}" in style
    assert ".fr-readout .fr-toc{display:flex;flex-wrap:wrap;column-gap:20px;row-gap:6px;" in style
    assert "border-left:3px solid #009FDA;padding:12px 15px;color:var(--fr-grey);font-weight:400}" in style
    assert "@media(max-width:640px){.fr-readout .fr-h1,.fr-readout .fr-pc{scroll-margin-top:72px}}" in style
    assert "scroll-margin-top:200px" not in style


def test_session_bar_buttons_are_icon_only_with_labels_on_phones():
    source = html()
    bar = source[source.index('<div class="session-bar" id="session-bar">'):source.index("<!-- ══ LANDING HERO ══ -->")]
    for label in ["View and edit analysis prompts", "Save session", "Load session"]:
        assert f'aria-label="{label}"' in bar and f'title="{label}"' in bar
    assert bar.count('<span class="sb-lbl">') == 3
    assert ".session-bar-btns .sb-lbl{display:none}" in source
    mobile = source[source.index("/* Phones: one row of icon-only buttons"):]
    assert "position:static" in mobile[:mobile.index(".session-bar #session-status")]
    prompt_btn = function_body(source, "function updateTopbarPromptBtn(")
    assert prompt_btn.count('<span class="sb-lbl">') == 2 and prompt_btn.count("setAttribute('aria-label'") == 2



def test_term_tooltips_do_not_underline_navigation_or_headings():
    style = INDEX.read_text(encoding="utf-8")
    style = style[style.index('<style id="fcv-readout-style">'):]
    style = style[:style.index("</style>")]
    rule = style[style.index(".fr-readout .fr-toc .sr-term"):]
    rule = rule[:rule.index("}") + 1]
    for scope in (".fr-toc", ".fr-h1", "summary", ".fr-sc-label", ".fr-rating-dim"):
        assert f".fr-readout {scope} .sr-term" in rule
    assert "border-bottom:0" in rule


def test_climate_readout_receives_provenance_inputs_like_normal_route():
    source = html()
    climate = function_body(source, "function renderClimateVerifiedAssessment(")
    assert "fileNames:readoutFileNames(),researchBrief}" in climate
    assert "fileNames:readoutFileNames(),researchBrief," in function_body(source, "function renderNormalReadoutHtml(")


def _restore_harness(scenario):
    from tests.test_climate_lens_frontend import _extract_js_function
    source = html()
    function = ('async ' + _extract_js_function(source, "refreshRestoredClimateReader")
                + "\n" + _extract_js_function(source, "supportsClimateVerifiedStage3View"))
    script = """
let reviewMode='design', busy=false, curS=3, stageOutputs={3:'ready'};
let climateVerifiedAssessment={schema_version:'climate-verified-v2.1'};
const storedReader={summary_overview_status:'fallback',priorities:[{id:'old'}]};
let climateVerifiedReader=storedReader, stageThreePriorities=storedReader.priorities;
let renders=0, posted=null;
const window={scrollY:40,scrollTo:()=>{}};
const navigateToStage=()=>{renders++;};
const scenario=SCENARIO;
const canonical={summary_overview_status:'generated',priorities:[{id:'new'}]};
const fetch=async(url,options)=>{
  posted={url,body:JSON.parse(options.body)};
  if(scenario==='offline')throw new Error('offline');
  if(scenario==='replaced')climateVerifiedReader={other:true};
  if(scenario==='reject')return {ok:false,json:async()=>({error:'x'})};
  if(scenario==='same')return {ok:true,json:async()=>({reader:JSON.parse(JSON.stringify(storedReader))})};
  if(scenario==='malformed')return {ok:true,json:async()=>({reader:[]})};
  return {ok:true,json:async()=>({reader:canonical})};
};
if(scenario==='legacy')climateVerifiedAssessment={schema_version:'climate-verified-v2.0'};
FUNCTION
(async()=>{
  const changed=await refreshRestoredClimateReader();
  console.log(JSON.stringify({changed,renders,posted,
    reader:climateVerifiedReader===storedReader?'stored':climateVerifiedReader===canonical?'canonical':'other',
    priorities:stageThreePriorities.map(p=>p.id)}));
})().catch(e=>{console.error(e);process.exit(1)});
""".replace("SCENARIO", json.dumps(scenario)).replace("FUNCTION", function)
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_restored_session_adopts_canonical_climate_reader():
    out = _restore_harness("ok")
    assert out["posted"]["url"] == "/api/climate-report-snapshot"
    # The reader is omitted so the server returns the canonical one.
    assert set(out["posted"]["body"]) == {"climate_assessment"}
    assert out["changed"] is True and out["reader"] == "canonical"
    assert out["priorities"] == ["new"] and out["renders"] == 1


def test_restored_session_keeps_stored_reader_on_any_failure():
    for scenario in ("offline", "reject", "malformed"):
        out = _restore_harness(scenario)
        assert out["changed"] is False, scenario
        assert out["reader"] == "stored" and out["renders"] == 0, scenario
        assert out["priorities"] == ["old"], scenario


def test_restored_session_skips_redraw_when_reader_is_unchanged_or_replaced():
    same = _restore_harness("same")
    assert same["changed"] is False and same["renders"] == 0 and same["reader"] == "stored"
    replaced = _restore_harness("replaced")
    assert replaced["changed"] is False and replaced["renders"] == 0 and replaced["reader"] == "other"


def test_restored_session_ignores_non_verified_assessment():
    out = _restore_harness("legacy")
    assert out["posted"] is None and out["changed"] is False


def test_reader_refresh_runs_only_on_session_restore_paths():
    source = html()
    load = source[source.index("function loadSession(input)"):]
    load = load[:load.index("setStepper(curS+1, 'active');")]
    assert "refreshRestoredClimateReader();" in load
    express = source[source.index("// Express recovery: checkpoints"):]
    express = express[:express.index("if(hasSavedStage3Output){localStorage.removeItem")]
    assert "refreshRestoredClimateReader();" in express
    # Two restore calls plus the definition; the live-run path is unchanged.
    assert source.count("refreshRestoredClimateReader(") == 3
    # No user-facing error path: failures return quietly.
    helper = source[source.index("async function refreshRestoredClimateReader"):]
    helper = helper[:helper.index("\n  }\n")]
    assert "alert(" not in helper
