"""Behavioral contracts for the Render review frontend fixes."""

import json
import re
import subprocess
from pathlib import Path


INDEX = Path(__file__).resolve().parents[1] / "index.html"


def _source() -> str:
    return INDEX.read_text(encoding="utf-8")


def _extract_js_function(source: str, name: str) -> str:
    match = re.search(rf"function\s+{name}\s*\(", source)
    assert match, f"Missing JS helper {name}()"
    start = match.start()
    if source[max(0,start-6):start] == "async ":
        start -= 6
    brace = source.find("{", match.end())
    assert brace != -1
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise AssertionError(f"Unterminated body for {name}()")


def _run_node(script: str) -> None:
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_stage3_controls_offer_distinct_summary_and_full_copy_actions():
    source = _source()
    assert "Copy summary" in source
    assert "Copy full report" in source
    assert "onclick=\"copySummary()\"" in source
    assert "onclick=\"copyFullReport()\"" in source


def test_full_copy_uses_canonical_priority_actions_watch_risk_and_ratings():
    source = _source()
    helper = _extract_js_function(source, "buildFullReportText")
    payload = {
        "stage3": "Narrative lead",
        "priorities": [
            {
                "title": "Protect access",
                "risk_level": "High",
                "the_gap": "Access trigger is missing.",
                "why_it_matters": "Delivery may exclude remote communities.",
                "actions": [
                    {
                        "document_element": "Implementation arrangements",
                        "guidance": "Name the trigger and owner.",
                        "suggested_language": "The team will review access quarterly.",
                    }
                ],
            }
        ],
        "risk": {"risks_to": "Conflict may interrupt delivery.", "risks_from": "Unequal access may deepen grievance."},
        "watch": "Monitor access conditions during supervision.",
        "sensitivity": "Adequate",
        "responsiveness": "Low",
    }
    script = f"""
const state = {json.dumps(payload)};
const stageThreePriorities = state.priorities;
const stageOutputs = {{3: state.stage3}};
const stageRiskExposure = state.risk;
const horizonConsiderations = state.watch;
const fcvRating = state.sensitivity;
const fcvResponsivenessRating = state.responsiveness;
let midCycleWatch = [], dpfWatch = [], p4rWatch = [], regionalWatch = [];
const stageSensitivitySummary='',stageResponsivenessSummary='',focusQuestionsResult=null;
const supportsClimateVerifiedStage3View=()=>false,md=x=>x,esc=x=>x,stripWatchHeading=x=>x,reportPlainText=x=>x;
const renderRiskExposure=x=>JSON.stringify(x),renderSRCards=()=>'',_buildExportPriorityCard=x=>JSON.stringify(x);
{helper}
const out = buildFullReportText();
for (const expected of Object.values(state)) {{
  const values = typeof expected === 'object' ? Object.values(expected).flatMap(value => typeof value === 'object' ? Object.values(value) : [value]) : [expected];
  for (const value of values) if (typeof value === 'string' && value && !out.includes(value)) throw new Error('missing ' + value + '\\n' + out);
}}
"""
    _run_node(script)


def test_research_fields_are_saved_and_restored():
    source = _source()
    save_start = source.index("function saveSession()")
    save_end = source.index("function showLegacyBanner", save_start)
    load_start = source.index("function loadSession(input)")
    load_end = source.index("function updateSessionBar", load_start)
    checkpoint = _extract_js_function(source, "epSafeStore")
    for section in (source[save_start:save_end], source[load_start:load_end], checkpoint):
        assert "researchBrief" in section
        assert "researchCountry" in section


def test_playbook_request_is_bounded_and_recovers_with_retry_without_stale_writes():
    source = _source()
    load = _extract_js_function(source, "loadDeeperTab")
    assert "90 * 1000" in load or "90*1000" in load
    assert "retryDeeper" in source
    assert "No additional FCV Playbook guidance" in source
    assert "requestId" in load or "requestToken" in load


def test_context_rating_meanings_are_six_tier_and_responsiveness_is_not_a_quality_proxy():
    source = _source()
    assert "LEVELS.length" in source
    assert "limited direct FCV action" in source.lower() or "not a proxy for overall project quality" in source.lower()
    assert "View research briefing" in source
    assert "View sources" not in source


def test_export_labels_word_annex_difference_and_html_keeps_full_sections():
    source = _source()
    assert "Word export" in source and "Annex" in source
    assert "researchBrief" in source[source.index("function downloadHTML()") :]
    assert "stageThreePriorities.forEach" in source[source.index("function downloadHTML()") :]
    assert "md(stripWatchHeading(horizonConsiderations))" in source[source.index("function downloadHTML()") :]



def test_playbook_empty_failure_retry_and_timeout_cleanup():
    source = _source()
    helpers = "\n".join(_extract_js_function(source, name) for name in (
        "loadDeeperTab", "retryDeeperButton", "retryDeeper"))
    script = r"""
let deeperAbortController=null,deeperRequestId=0;
const stageThreePriorities=[{title:'Synthetic priority'}],hist=[],docType='PAD';
const result={innerHTML:'',isConnected:true},loading={style:{}},timer={textContent:''};
const document={getElementById:id=>id.startsWith('deeper-result')?result:id.startsWith('deeper-loading')?loading:timer};
const esc=x=>x,md=x=>x,renderDeeperContent=(tab,x)=>x;
let timerCallback,clears=0,mode='empty',cached=[];
const setTimeout=(fn,ms)=>{if(ms!==90000)throw Error('wrong budget');timerCallback=fn;return 1;};
const clearTimeout=()=>{clears++;},setInterval=()=>2,clearInterval=()=>{};
const localStorage={setItem:(k,v)=>cached.push(v)};
const fetch=async(url,options)=>{
  if(mode==='failure')return {ok:false,status:503};
  if(mode==='timeout')return new Promise((resolve,reject)=>{
    options.signal.addEventListener('abort',()=>reject(Object.assign(new Error('abort'),{name:'AbortError'})));
    queueMicrotask(()=>timerCallback());
  });
  let sent=false;
  return {ok:true,body:{getReader:()=>({read:async()=>{
    if(mode==='success'&&!sent){sent=true;return {done:false,value:new TextEncoder().encode('data: {"chunk":"Synthetic guidance"}\n\n')};}
    return {done:true};
  }})}};
};
""" + helpers + r"""
(async()=>{
 await loadDeeperTab(0,'playbook');
 if(!result.innerHTML.includes('No additional')||!result.innerHTML.includes('Retry')||cached.length)throw Error('empty state');
 mode='failure';await retryDeeper(0,'playbook');
 if(!result.innerHTML.includes('503')||!result.innerHTML.includes('Retry'))throw Error('failure state');
 mode='timeout';await retryDeeper(0,'playbook');
 if(!result.innerHTML.includes('timed out')||loading.style.display!=='none')throw Error('timeout state');
 mode='success';await retryDeeper(0,'playbook');
 if(result.innerHTML!=='Synthetic guidance'||cached.length!==1||clears!==4)throw Error('retry cleanup');
})().catch(e=>{console.error(e);process.exit(1);});
"""
    _run_node(script)



def test_new_research_runs_clear_recovered_brief_but_stage_refinement_keeps_it():
    source = _source()
    for name in ("restartExpressFromStage1", "discardExpressRecovery", "runExpress"):
        helper = _extract_js_function(source, name)
        assert "researchBrief='';researchCountry='';" in helper
    run_stage = _extract_js_function(source, "runStage")
    assert "if(stage===1&&!followOn){researchBrief='';researchCountry='';}" in run_stage
