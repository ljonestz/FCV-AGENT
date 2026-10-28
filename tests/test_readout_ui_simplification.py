"""Behavior contracts for the compact Stage 3 readout controls and cards."""

import subprocess
from pathlib import Path


INDEX = Path(__file__).resolve().parents[1] / "index.html"


def _extract_js_function(source: str, name: str) -> str:
    marker = f"function {name}("
    start = source.find(marker)
    assert start >= 0, f"Missing JavaScript function {name}()"
    brace = source.find("{", start + len(marker))
    assert brace >= 0
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise AssertionError(f"Unterminated JavaScript function {name}()")


def _run_node(script: str) -> None:
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_climate_summary_uses_full_short_actions_and_links_each_gap_to_detailed():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "climateSummaryPriorityItems",
            "getConcisePriority",
            "renderSummaryPriorityAccordion",
            "renderNormalSummaryPriorities",
            "climateSummaryWatchItems",
            "renderClimateWatchDisclosure",
            "renderClimateSummaryGaps",
            "renderClimateVerifiedSummary",
        )
    )
    script = f"""
const esc=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
const normalizeVisibleText=value=>String(value??'').replace(/\\s+/g,' ').trim();
const boldVisibleFirstSentence=value=>esc(value||'');
const boldEscapedFirstSentence=value=>esc(value||'');
const climateDraftingRouteGate=()=>({{canRender:false,confirmed:false}});
const climateSummaryStrengths=()=>[];
const renderStage3AdvisoryTransition=()=>'<p>Advisory</p>';
const renderClimateRelevantGuidance=()=>'';
const supportsClimateVerifiedStage3View=()=>true;
let openSummaryPriority=0;
{helpers}
const completeAction='Adopt a locally managed flood maintenance plan with ring-fenced resources, community-defined access rules, and trigger-based inspection responsibilities before procurement, then embed those duties in municipal contracts and monitor them jointly with district authorities, water user groups, and project engineers across each rainy season.';
const priorities=[
  {{rank:1,title:'Priority 1 - Protect access',minimum_action:'Keep priority one access routes open.'}},
  {{rank:2,title:'Priority 2 - Maintain flood assets',minimum_action:completeAction}}
];
const gap='Maintenance responsibilities for flood assets are not yet assigned.';
const html=renderClimateVerifiedSummary({{
  analysis_status:'partial',analysis_message:'Some evidence could not be checked.',
  operation_context:{{preparation_regime:'unresolved_policy_source'}},
  summary_overview:['The project invests in resilient assets.'],
  priorities,summary_gaps:[{{text:gap}}],
  assessment_themes:[{{findings:[{{text:gap,priority_ranks:[2]}}]}}],
  climate_sensitivity_rating:{{label:'Strong'}},
  core_questions:[{{watch:'Monitor wet-season access.'}}]
}});
const emptySummary=renderClimateVerifiedSummary({{summary_overview:['No priorities are available.'],priorities:[]}});
if(emptySummary.includes('<p>Advisory</p>'))throw new Error('Climate priority advisory appeared without any priorities');
if(completeAction.split(/\\s+/).length<39||completeAction.split(/\\s+/).length>45)throw new Error('fixture action must stay within the saved 39–45 word range');
if(!html.includes(completeAction))throw new Error('the complete minimum action was clipped');
if(!html.includes('Suggested action'))throw new Error('short action label is missing');
if(!html.includes('href=\"#climate-priority-2\"')||!html.includes('openClimateDetailedPriority(2)'))throw new Error('gap does not target its exact Detailed card: '+html);
if(!html.includes('class=\"normal-summary-priority\"')||html.includes('summary-priority-accordion'))throw new Error('Climate priorities are not compact cards');
for(const removed of ['Draft - human review required','Preparation route:','Climate-FCV sensitivity:','Where this fits in the project cycle','Specialist reasoning, evidence and operational references','What to keep an eye on']){{
  if(html.includes(removed))throw new Error('removed Summary content remains: '+removed);
}}
for(const retained of ['Assessment evidence is incomplete.','Suggested document wording is not shown because the document type or financing route could not be confirmed reliably.']){{
  if(!html.includes(retained))throw new Error('required notice disappeared: '+retained);
}}
"""
    _run_node(script)


def test_summary_suggested_actions_use_regular_font_weight_on_both_routes():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in ("normalizeVisibleText", "getConcisePriority", "renderNormalSummaryPriorities")
    )
    script = f"""
const esc=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const boldEscapedFirstSentence=value=>`<strong>${{esc(value)}}</strong>`;
const boldVisibleFirstSentence=value=>`<strong>${{esc(value)}}</strong>`;
{helpers}
const action='Add one complete operational action in a single sentence.';
for(const route of ['normal','climate']){{
const html=renderNormalSummaryPriorities([{{rank:1,title:'Protect access',minimum_action:action,concise:{{title:'Protect access',how:[action]}}}}],route);
const paragraph=html.match(/<p class="normal-summary-priority-action">([\\s\\S]*?)<\\/p>/)[1];
if(paragraph.includes('<strong>'))throw new Error('Climate Suggested action is bold: '+paragraph);
if(!paragraph.includes(action)||!paragraph.includes('Suggested action'))throw new Error('Action or label is missing: '+paragraph);
}}
"""
    _run_node(script)


def test_climate_summary_priority_navigation_opens_the_matching_detailed_card():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "openClimateDetailedPriority")
    script = f"""
let view='summary',focus='',scrolled='';
const target={{scrollIntoView:()=>{{scrolled='climate-priority-2';}}}};
const document={{getElementById:id=>id==='climate-priority-2'?target:null}};
const setStage3View=(next,preserve,focusTab)=>{{view=next;focus=focusTab;}};
{helper}
openClimateDetailedPriority(2);
if(view!=='detailed'||focus!=='stage3-detailed-tab'||scrolled!=='climate-priority-2')throw new Error('rank 2 did not open and scroll to its Detailed card');
"""
    _run_node(script)


def test_copy_active_summary_excludes_controls_but_detailed_uses_complete_report():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "copyActiveView")
    script = f"""
let stage3View='summary',copied='',capturedHtml='',usedButton=null;
const button={{id:'copy-active-view'}};
const clone={{
  innerHTML:'<div class="stage3-viewbar">Summary Detailed analysis</div><h2>Active Summary</h2><button>Copy</button><a href="#climate-priority-2">Priority navigation</a><details open><summary>Expanded guidance</summary><p>Visible expanded guidance text</p></details><details><summary>Closed guidance</summary><p>Closed WBG guidance text</p></details>',
  querySelectorAll(selector){{
    const removeText=text=>({{remove:()=>{{clone.innerHTML=clone.innerHTML.replace(text,'');}}}});
    if(selector==='details:not([open])')return [removeText('<details><summary>Closed guidance</summary><p>Closed WBG guidance text</p></details>')];
    if(!selector.includes('.stage3-viewbar')||!selector.includes('button')||!selector.includes('a[href^="#"]'))throw new Error('copy selector omits report controls');
    return [removeText('<div class="stage3-viewbar">Summary Detailed analysis</div>'),removeText('<button>Copy</button>'),removeText('<a href="#climate-priority-2">Priority navigation</a>')];
  }}
}};
const output={{cloneNode:()=>clone}};
const document={{getElementById:id=>id==='out-txt'?output:id==='copy-active-view'?button:null}};
const reportPlainText=html=>{{capturedHtml=html;return html.replace(/<[^>]+>/g,' ').replace(/\\s+/g,' ').trim();}};
const copyReportText=(text,target)=>{{copied=text;usedButton=target;}};
const buildFullReportText=()=>'<h2>Priority 2: Complete displayed Detailed card</h2><details><summary>Evidence coverage</summary><p>Detailed follow-up outside out-txt.</p></details>';
{helper}
copyActiveView();
if(!copied.includes('Active Summary'))throw new Error('active Summary text was omitted: '+copied);
if(!capturedHtml.includes('Visible expanded guidance text')||capturedHtml.includes('Closed WBG guidance text'))throw new Error('Summary copy did not preserve only the visible disclosure content: '+capturedHtml);
if(/Summary Detailed analysis|Priority navigation|>Copy</.test(capturedHtml))throw new Error('navigation or controls entered copied text: '+capturedHtml);
if(usedButton!==button)throw new Error('Copy acknowledgement was not associated with the visible button');
stage3View='detailed';copied='';capturedHtml='';usedButton=null;
copyActiveView();
if(!copied.includes('Complete displayed Detailed card')||!copied.includes('Detailed follow-up outside out-txt'))throw new Error('the complete Detailed report omitted sibling priority/follow-up content: '+copied);
if(capturedHtml!==''||usedButton!==button)throw new Error('Detailed copy did not use the full report builder and visible Copy button');
"""
    _run_node(script)



def test_detailed_copy_includes_visible_document_checks_and_climate_provenance_notice():
    source = INDEX.read_text(encoding="utf-8")
    assert 'id="document-checks"' in source
    assert "climate-partial-notice" in _extract_js_function(source, "renderPrioritiesIntro")
    helper = _extract_js_function(source, "buildFullReportText")
    script = f"""
const stageOutputs={{3:'# Visible analysis'}};
const supportsClimateVerifiedStage3View=()=>false;
const md=value=>value;
const stageRiskExposure='',stageSensitivitySummary='',stageResponsivenessSummary='';
const fcvRating='',fcvResponsivenessRating='';
const stageThreePriorities=[],focusQuestionsResult=null;
const midCycleWatch=[],dpfWatch=[],p4rWatch=[],regionalWatch=[];
const horizonConsiderations='';
const esc=value=>String(value||'');
const renderRiskExposure=()=>'',renderSRCards=()=>'',reportPlainText=value=>value;
const document={{
  getElementById:id=>id==='document-checks'?{{outerHTML:'<details id="document-checks"><summary>Points to check in the document</summary><p>DOC CHECK SENTINEL: confirm the placeholder.</p></details>'}}:null,
  querySelector:selector=>selector==='#priorities-intro .climate-partial-notice'?{{outerHTML:'<div class="climate-partial-notice">CLIMATE PROVENANCE SENTINEL: one recommendation is unlinked.</div>'}}:null
}};
{helper}
const text=buildFullReportText();
if(!text.includes('DOC CHECK SENTINEL: confirm the placeholder.'))throw new Error('visible document check omitted from Detailed copy: '+text);
if(!text.includes('CLIMATE PROVENANCE SENTINEL: one recommendation is unlinked.'))throw new Error('visible climate provenance notice omitted from Detailed copy: '+text);
"""
    _run_node(script)


def test_detailed_copy_matches_the_visible_result_header_boundary():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "buildFullReportText")
    script = f"""
const stageOutputs={{3:'---\\nCLASSIFICATION: internal\\nGenerated by WBG FCV Sensitivity Project Screener\\nFor Review Purposes Only\\n---\\n# Visible analysis\\nVisible Detailed content.'}};
const supportsClimateVerifiedStage3View=()=>false;
const md=value=>value;
const stageRiskExposure='',stageSensitivitySummary='',stageResponsivenessSummary='';
const fcvRating='',fcvResponsivenessRating='';
const stageThreePriorities=[],focusQuestionsResult=null;
const midCycleWatch=[],dpfWatch=[],p4rWatch=[],regionalWatch=[];
const horizonConsiderations='';
const esc=value=>String(value||'');
const renderRiskExposure=()=>'',renderSRCards=()=>'',reportPlainText=value=>value;
{helper}
const text=buildFullReportText();
if(text.includes('For Review Purposes Only')||text.includes('Generated by WBG FCV Sensitivity Project Screener'))throw new Error('Detailed copy reintroduced an invisible legacy header: '+text);
if(!text.includes('Visible analysis')||!text.includes('Visible Detailed content.'))throw new Error('visible Detailed content was omitted: '+text);
"""
    _run_node(script)

def test_copy_reports_failure_when_clipboard_and_fallback_both_fail():
    source = INDEX.read_text(encoding="utf-8")
    helper = "async " + _extract_js_function(source, "copyReportText")
    script = f"""
const button={{textContent:'Copy',attrs:{{'aria-label':'Copy the active Summary or Detailed report'}},classes:new Set(),setAttribute(name,value){{this.attrs[name]=value;}},getAttribute(name){{return this.attrs[name]||null;}},classList:{{toggle(name,active){{if(active)button.classes.add(name);else button.classes.delete(name);}}}}}};
const navigator={{clipboard:{{writeText:async()=>{{throw new Error('permission denied');}}}}}};
const input={{value:'',style:{{}},select(){{}},remove(){{}}}};
const document={{createElement:()=>input,body:{{appendChild(){{}}}},execCommand:()=>false}};
const setTimeout=()=>0;
{helper}
copyReportText('full report text',button).then(copied=>{{
  if(copied!==false||button.textContent!=='Copy failed'||button.attrs['aria-label']!=='Copy failed. Clipboard permission was denied.')throw new Error('copy failure was reported as success');
}}).catch(error=>{{throw error;}});
"""
    _run_node(script)

def test_stage3_toolbar_has_one_copy_and_word_html_full_report_menu():
    source = INDEX.read_text(encoding="utf-8")
    start = source.index('<div class="out-hdr-actions"')
    end = source.index('<div class="out-body" id="out-txt"', start)
    toolbar = source[start:end]

    assert toolbar.count('onclick="copyActiveView()"') == 1
    assert "Download report" in toolbar
    assert 'onclick="downloadReport(this)"' in toolbar
    assert 'onclick="downloadHTML()"' in toolbar
    for hidden_control in (
        "renderManagementBriefControls()",
        "downloadClimateReviewPacket(this)",
        'onclick="copySummary()"',
        'onclick="copyFullReport()"',
    ):
        assert hidden_control not in toolbar
    assert "function downloadManagementBrief(" in source
    assert "function downloadClimateReviewPacket(" in source
    assert "function saveSession(" in source


def test_advisory_text_is_full_and_routes_to_both_summary_and_detailed_intro():
    source = INDEX.read_text(encoding="utf-8")
    advisory = _extract_js_function(source, "renderStage3AdvisoryTransition")
    summary = _extract_js_function(source, "renderNormalFcvSummary")
    climate_summary = _extract_js_function(source, "renderClimateVerifiedSummary")
    priorities_intro = _extract_js_function(source, "renderPrioritiesIntro")
    climate_detail = _extract_js_function(source, "renderClimateVerifiedAssessment")
    script = f"""
let reviewMode='design';
{advisory}
const expectedClimate=\"The following priorities are suggestions to strengthen the project's design in its climate and FCV context. They are not mandatory requirements, nor may they all be relevant. The task team may wish to focus on those they believe to be more pertinent based on their own sectoral expertise and knowledge of the context within which the project will be applied. For more complex or difficult issues raised, the team are encouraged to reach out and discuss them with the FCV Country Coordinator or relevant Global Practice experts as needed.\";
const expectedNormal=expectedClimate.replace('design in its climate and FCV context','design in its FCV context');
if(!renderStage3AdvisoryTransition('climate').includes(expectedClimate))throw new Error('full climate advisory missing');
if(!renderStage3AdvisoryTransition('normal').includes(expectedNormal))throw new Error('full normal advisory missing');
reviewMode='implementation';
const implementation=renderStage3AdvisoryTransition('climate');
if(!implementation.includes(\"design and implementation arrangements in its climate and FCV context\"))throw new Error('implementation adaptation missing');
"""
    _run_node(script)
    assert "renderStage3AdvisoryTransition('normal')" in summary
    assert "renderStage3AdvisoryTransition('climate')" in climate_summary
    assert "renderStage3AdvisoryTransition" in priorities_intro
    assert "renderStage3AdvisoryTransition('climate')" in climate_detail


def test_climate_detail_keeps_route_gate_and_uses_requested_disclosure_labels():
    source = INDEX.read_text(encoding="utf-8")
    detailed = _extract_js_function(source, "renderClimateVerifiedAssessment")
    summary = _extract_js_function(source, "renderClimateVerifiedSummary")

    for body in (summary, detailed):
        assert "Draft - human review required" not in body
        assert "Preparation route:" not in body
        assert "Suggested document wording is not shown because the document type or financing route could not be confirmed reliably." in body
    assert '<summary>Practical considerations and Suggested Text</summary>' in detailed
    assert "Suggested Text" in detailed
