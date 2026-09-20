"""Frontend contracts for the standard FCV management brief UI."""

import json
import re
import subprocess
from pathlib import Path


INDEX = Path(__file__).resolve().parents[1] / "index.html"


def _extract_js_function(source: str, name: str) -> str:
    match = re.search(rf"function\s+{name}\s*\(", source)
    assert match, f"Missing JS helper {name}()"
    start = match.start()
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


def _esc_js() -> str:
    return """
const esc=value=>String(value??'')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
"""


def _priority(index: int) -> dict:
    return {
        "title": f"Priority {index}: Protect access in Bentiu",
        "the_gap": f"The document leaves the access trigger for Bentiu unclear {index}.",
        "why_it_matters": "Unclear access decisions can interrupt delivery for conflict affected communities.",
        "actions": [
            {"document_element": "PCN", "guidance": "Name the access trigger in the PCN."},
            {"document_element": "Implementation arrangements", "guidance": "Assign the response owner."},
        ],
        "cpf_alignment": "CPF Outcome 1",
        "rra_driver_alignment": "RRA Driver 2",
        "country_category_relevance": "The conflict affected context makes this especially relevant.",
        "refresh_shift": "Shift B: Differentiate",
        "action_timing": "required-before-appraisal",
        "concise": {
            "title": f"Protect access in Bentiu {index}",
            "why": "Clear access decisions help keep delivery inclusive in Bentiu.",
            "how": [
                "Set an access trigger for Bentiu.",
                "Record the response owner in the implementation arrangements.",
            ],
        },
    }


def _readout(*, strengths=None) -> dict:
    readout = {
        "headline": "The design is aware of FCV risks but needs clearer delivery choices.",
        "overview": "The project recognises exclusion risks and has a workable platform, but access and accountability arrangements need sharper decisions before preparation advances.",
        "strengths": strengths if strengths is not None else [{"title": "Local reach", "text": "The design uses existing local delivery channels."}],
    }
    # These fields remain part of canonical admission even when not displayed.
    readout.update(
        {
            "strengths_transition": "These strengths provide a useful foundation.",
            "priorities_transition": "The priorities focus on decisions that affect delivery.",
            "closing": "The full assessment contains the supporting detail.",
        }
    )
    return readout


def test_standard_summary_is_compact_and_shows_all_ranked_priorities_without_ratings():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "supportsConciseStage3View",
            "getConcisePriority",
            "renderNormalSummaryPriorities",
            "renderNormalFcvSummary",
        )
    )
    priorities = [_priority(index) for index in range(1, 4)]
    script = f"""
{_esc_js()}
let activeLenses=[];
let stageThreePriorities={json.dumps(priorities)};
let stageConciseReadout={json.dumps(_readout())};
let stage3View='summary';
let openSummaryPriority=0;
let reviewMode='design';
const renderStage3AdvisoryTransition=()=>'<p>Suggestions for the team.</p>';
const renderNormalFcvWatchDisclosure=()=>'';
{helpers}
const html=renderNormalFcvSummary();
for(const expected of ['Overall assessment','What is already working','Priority actions for the task team','Protect access in Bentiu 1','Protect access in Bentiu 2','Protect access in Bentiu 3','Clear access decisions help keep delivery inclusive in Bentiu.','Set an access trigger for Bentiu.']){{
  if(!html.includes(expected))throw new Error('missing '+expected+' | '+html);
}}
for(const forbidden of ['FCV sensitivity','FCV responsiveness','summary-priority-toggle','Where this fits in the project cycle','Suggested wording for the current document']){{
  if(html.includes(forbidden))throw new Error('summary exposed '+forbidden+' | '+html);
}}
if((html.match(/class="normal-summary-priority"/g)||[]).length!==3)throw new Error('wrong priority count');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_standard_summary_accepts_short_readout_with_zero_strengths_and_valid_priority_bundle():
    source = INDEX.read_text(encoding="utf-8")
    supports = _extract_js_function(source, "supportsConciseStage3View")
    render = _extract_js_function(source, "renderNormalFcvSummary")
    priorities = [_priority(index) for index in range(1, 6)]
    script = f"""
{_esc_js()}
let activeLenses=[];
let stageThreePriorities={json.dumps(priorities)};
let stageConciseReadout={json.dumps(_readout(strengths=[]))};
{supports}
if(!supportsConciseStage3View())throw new Error('short valid readout was rejected');
const renderStage3AdvisoryTransition=()=>'';
const renderNormalFcvWatchDisclosure=()=>'';
const getConcisePriority=priority=>priority.concise;
const renderNormalSummaryPriorities=()=>'';
{render}
const html=renderNormalFcvSummary();
if(html.includes('Project strength'))throw new Error('empty strengths created a placeholder');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_summary_priority_link_sets_exact_detailed_identity_and_persists_tab_selection():
    source = INDEX.read_text(encoding="utf-8")
    renderer = _extract_js_function(source, "renderNormalSummaryPriorities")
    opener = _extract_js_function(source, "openDetailedPriority")
    priorities = [_priority(index) for index in range(1, 3)]
    script = f"""
{_esc_js()}
let stageThreePriorities={json.dumps(priorities)};
let currentPriority=0;
let stage3View='summary';
let called=[];
const setStage3View=(view,preserve,focus)=>{{called.push([view,preserve,focus]);stage3View=view;}};
{opener}
const links=(()=>{{
  const getConcisePriority=priority=>priority.concise;
  {renderer}
  return renderNormalSummaryPriorities();
}})();
if(!links.includes('href="#priority-card-area"'))throw new Error('missing detailed anchor');
if(!links.includes('openDetailedPriority(1)'))throw new Error('second priority link is not identity-specific');
openDetailedPriority(1);
if(currentPriority!==1)throw new Error('detailed priority identity was not preserved');
if(called.length!==1||called[0][0]!=='detailed'||called[0][1]!==true)throw new Error('tab selection was not persisted');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_standard_detailed_timing_is_advisory_and_context_is_closed():
    source = INDEX.read_text(encoding="utf-8")
    timing = _extract_js_function(source, "renderPriorityTiming")
    context = _extract_js_function(source, "renderStandardPriorityContext")
    specialist = _extract_js_function(source, "renderSpecialistPriorityContext")
    route = _extract_js_function(source, "renderPriorityContext")
    script = f"""
{_esc_js()}
let activeLenses=[];
const isClimateLensActive=()=>false;
{timing}
{context}
{specialist}
{route}
const renderPriorityClimateContribution=()=>'<div class="climate-context"></div>';
const standard=renderPriorityTiming('required-before-appraisal');
if(!standard.includes('Consider before appraisal'))throw new Error('standard timing is mandatory');
if(standard.includes('Required before'))throw new Error('standard timing retained mandatory label');
const disclosure=renderStandardPriorityContext({{
  cpf_alignment:'CPF & <Outcome>',
  rra_driver_alignment:'RRA driver',
  country_category_relevance:'Conflict context',
  refresh_shift:'Shift B: Differentiate'
}});
if(!disclosure.startsWith('<details'))throw new Error('context is not a disclosure');
if(disclosure.includes(' open'))throw new Error('context disclosure is open by default');
for(const expected of ['CPF alignment','RRA driver alignment','Differentiated approach','Strategy alignment','CPF &amp; &lt;Outcome&gt;']){{
  if(!disclosure.includes(expected))throw new Error('missing '+expected+' | '+disclosure);
}}
activeLenses=['gender'];
const specialistHtml=renderPriorityContext({{country_category_relevance:'Keep the existing specialist context note.'}});
if(!specialistHtml.includes('Differentiated approach note'))throw new Error('specialist context was removed');
if(specialistHtml.includes('priority-context-disclosure'))throw new Error('standard disclosure leaked into specialist view');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_management_brief_controls_post_validated_payload_and_surface_422():
    source = INDEX.read_text(encoding="utf-8")
    controls = _extract_js_function(source, "renderManagementBriefControls")
    download = "async " + _extract_js_function(source, "downloadManagementBrief")
    script = f"""
let stage3View='summary';
let activeLenses=[];
let docType='PAD';
let fcvRating='Adequate';
let fcvResponsivenessRating='Emerging';
let stageConciseReadout={{headline:'Headline'}};
let stageThreePriorities=[{{title:'Priority'}}];
const supportsConciseStage3View=()=>true;
{controls}
const controlsHtml=renderManagementBriefControls();
for(const expected of ["downloadManagementBrief('html'", "downloadManagementBrief('docx'", 'Brief HTML', 'Brief Word']){{
  if(!controlsHtml.includes(expected))throw new Error('missing '+expected+' | '+controlsHtml);
}}
let captured=null;
let alertText='';
const fetch=(url,options)=>{{captured={{url,options}};return Promise.resolve({{ok:false,status:422,json:()=>Promise.resolve({{detail:'Incomplete brief'}})}});}};
const alert=value=>{{alertText=String(value);}};
const button={{disabled:false,innerHTML:'Download'}};
{download}
downloadManagementBrief('html',button).then(()=>{{
  if(captured.url!=='/api/download-management-brief')throw new Error('wrong management brief route');
  const body=JSON.parse(captured.options.body);
  for(const key of ['concise_readout','priorities','fcv_rating','fcv_responsiveness_rating','doc_type','active_lenses','format']){{if(!(key in body))throw new Error('missing '+key);}}
  if(body.format!=='html'||body.doc_type!=='PAD'||body.active_lenses.length!==0)throw new Error('wrong payload values');
  if(!alertText.includes('Incomplete brief')||button.disabled)throw new Error('422 was not surfaced and reset');
}}).catch(error=>{{console.error(error);process.exitCode=1;}});
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr



def test_standard_watch_narrative_preserves_markdown_prose_and_escapes_html():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in ("md", "normalFcvWatchGroups", "renderNormalFcvWatchDisclosure")
    )
    script = f"""
{_esc_js()}
let docType='PAD';
let instrumentType='IPF';
let countryScope='single';
let midCycleWatch=[];
let dpfWatch=[];
let p4rWatch=[];
let regionalWatch=[];
let horizonConsiderations='### Watch List for Supervision\\n\\n**1. Access**\\nTrack access conditions. <script>alert(1)</script>\\n\\n**2. Delivery**\\nReview delivery signals.';
{helpers}
const html=renderNormalFcvWatchDisclosure();
if(!html.includes('<div class="normal-fcv-watch-narrative">'))throw new Error('horizon narrative was not rendered as prose');
if((html.match(/<li>/g)||[]).length)throw new Error('horizon narrative was flattened into a list item');
if(!html.includes('<h3>Watch List for Supervision</h3>'))throw new Error('markdown heading was not rendered');
if(!html.includes('&lt;script&gt;alert(1)&lt;/script&gt;'))throw new Error('watch narrative was not escaped');
if(html.includes('<script>'))throw new Error('raw script reached watch markup');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_stage3_download_note_distinguishes_brief_and_full_downloads():
    source = INDEX.read_text(encoding="utf-8")
    toggle = _extract_js_function(source, "stage3ViewToggleHtml")
    script = f"""
let stage3View='summary';
let valid=true;
const supportsConciseStage3View=()=>valid;
{toggle}
if(!stage3ViewToggleHtml().includes('Brief downloads summarize priorities'))throw new Error('valid standard Summary lost brief note');
stage3View='detailed';
if(!stage3ViewToggleHtml().includes('Downloads include the comprehensive analysis.'))throw new Error('Detailed view lost full report note');
stage3View='summary';
valid=false;
if(!stage3ViewToggleHtml().includes('Downloads include the comprehensive analysis.'))throw new Error('legacy or climate note was changed');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_brief_download_controls_follow_summary_detailed_tab_switches():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(_extract_js_function(source, name) for name in (
        "renderManagementBriefControls", "setStage3View",
    ))
    script = """
let stage3View='detailed', currentPriority=0, openSummaryPriority=0;
let horizonConsiderations='';
const host={innerHTML:''};
const document={getElementById:id=>id==='management-brief-controls'?host:null,querySelector:()=>null};
const supportsAnyStage3Summary=()=>true;
const supportsConciseStage3View=()=>true;
const supportsClimateVerifiedStage3View=()=>false;
const renderPrioritiesIntro=()=>{}, renderPriorityStepper=()=>{}, showPriority=()=>{};
""" + helpers + """
setStage3View('summary');
if(!host.innerHTML.includes('Brief Word'))throw new Error('brief downloads not shown after opening Summary');
setStage3View('detailed');
if(host.innerHTML)throw new Error('unusable brief controls remain in Detailed');
setStage3View('summary');
if(!host.innerHTML.includes('Brief HTML'))throw new Error('brief downloads not restored');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
