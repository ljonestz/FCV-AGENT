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


def test_standard_readout_gate_accepts_short_readout_with_zero_strengths_and_valid_priority_bundle():
    source = INDEX.read_text(encoding="utf-8")
    supports = _extract_js_function(source, "supportsConciseStage3View")
    priorities = [_priority(index) for index in range(1, 6)]
    script = f"""
{_esc_js()}
let activeLenses=[];
let stageThreePriorities={json.dumps(priorities)};
let stageConciseReadout={json.dumps(_readout(strengths=[]))};
{supports}
if(!supportsConciseStage3View())throw new Error('short valid readout was rejected');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_standard_detailed_timing_is_advisory_and_differentiated_context_is_removed():
    source = INDEX.read_text(encoding="utf-8")
    timing = _extract_js_function(source, "renderPriorityTiming")
    context = _extract_js_function(source, "renderStandardPriorityContext")
    script = f"""
{_esc_js()}
let activeLenses=[];
const isClimateLensActive=()=>false;
{timing}
const standard=renderPriorityTiming('required-before-appraisal');
if(!standard.includes('Consider before appraisal'))throw new Error('standard timing is mandatory');
if(standard.includes('Required before'))throw new Error('standard timing retained mandatory label');
{context}
const disclosure=renderStandardPriorityContext({{cpf_alignment:'CPF & <Outcome>',rra_driver_alignment:'RRA driver',refresh_shift:'Strategy contribution'}});
for(const expected of ['<details','CPF &amp; &lt;Outcome&gt;','RRA driver','Strategy contribution']){{if(!disclosure.includes(expected))throw new Error('missing alignment '+expected);}}
if(disclosure.includes(' open'))throw new Error('alignment should be closed by default');

"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    for forbidden in ("renderSpecialistPriorityContext", "Differentiated approach note", "country_category_relevance"):
        assert forbidden not in source


def test_reader_cleanup_removes_visible_metadata_panels_and_attribution_but_keeps_route_warnings():
    source = INDEX.read_text(encoding="utf-8")
    for forbidden in (
        "temporal-context-panel",
        "injectTemporalContextPanel",
        "applied-snippets-attr",
        "renderAppliedSnippetsAttribution",
        "Differentiated approach note",
        "country_category_relevance",
    ):
        assert forbidden not in source, f"removed reader/export content remains: {forbidden}"
    assert "temporalContext" in source
    assert "climate-route-warning" in source


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
        for name in ("normalizeVisibleText", "md", "stripWatchHeading", "normalFcvWatchGroups", "renderNormalFcvWatchBody")
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
const html=renderNormalFcvWatchBody();
if(!html.includes('<div class="normal-fcv-watch-narrative">'))throw new Error('horizon narrative was not rendered as prose');
if((html.match(/<li>/g)||[]).length)throw new Error('horizon narrative was flattened into a list item');
if(html.includes('Watch List for Supervision'))throw new Error('duplicate watch heading was not stripped');
if(!html.includes('Track access conditions.')||!html.includes('Review delivery signals.'))throw new Error('watch prose was lost');
if(!html.includes('&lt;script&gt;alert(1)&lt;/script&gt;'))throw new Error('watch narrative was not escaped');
if(html.includes('<script>'))throw new Error('raw script reached watch markup');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_brief_download_controls_are_gated_only_on_a_valid_concise_readout():
    source = INDEX.read_text(encoding="utf-8")
    controls = _extract_js_function(source, "renderManagementBriefControls")
    assert "stage3View" not in controls
    script = f"""
let valid=true;
const supportsConciseStage3View=()=>valid;
{controls}
const shown=renderManagementBriefControls();
if(!shown.includes('Brief Word')||!shown.includes('Brief HTML'))throw new Error('brief downloads not shown for a valid readout');
valid=false;
if(renderManagementBriefControls()!=='')throw new Error('unusable brief controls remain');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    render_out = _extract_js_function(source, "renderOut")
    assert 'id="management-brief-controls">${renderManagementBriefControls()}' in render_out


def test_manual_session_load_restores_completed_stage3_without_rerun_and_keeps_partial_resume():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in ("isRestorableExpressStage3Output", "restoreSavedStage3Sections", "captureClimateFailureDiagnostic", "loadSession")
    )
    script = f"""
let hist=[],curS=0,instrumentType='',countryScope='',docType='',analysisMode='stepbystep',stage3View='detailed';
let stageOutputs={{}},stageHists={{}},priorityQuestions=[],focusQuestionsResult=null;
let activeLenses=[],resolvedLensVersions={{}},lensDiagnostic={{}},lensContextSources=[];
let climateResearch={{}},climateGrounding={{}},climateVerifiedAssessment=null,climateVerifiedReader=null,climateVerifiedFailure=null;
let stageConciseReadout=null,stageThreePriorities=[],fcvRating='',fcvResponsivenessRating='';
let stageRiskExposure=null,stageSensitivitySummary='',stageResponsivenessSummary='';
let midCycleWatch=[],dpfWatch=[],p4rWatch=[],regionalWatch=[],horizonConsiderations='';
let lensSelectionLocked=false,sessionName='',researchBrief='',researchCountry='';
let calls=[];
const lensCatalogueReady=Promise.resolve();
const lensCatalogue=[];
const supportsClimateVerifiedStage3View=()=>false;
const supportsAnyStage3Summary=()=>false;
const selectMode=()=>{{}};
const updateDocTypeBadge=()=>{{}};
const renderLensSelector=()=>{{}};
const setStepper=()=>{{}};
const enableClickableStepper=()=>{{calls.push('enableClickableStepper')}};
const navigateToStage=stage=>{{calls.push('navigateToStage:'+stage)}};
const alert=message=>{{calls.push('alert:'+String(message))}};
const elements={{}};
const document={{getElementById(id){{
  if(!elements[id])elements[id]={{style:{{}},textContent:'',innerHTML:'',classList:{{add(){{}},remove(){{}}}}}};
  return elements[id];
}}}};
class FileReader{{readAsText(file){{this.onload({{target:{{result:file.contents}}}})}}}}
{helpers}
const completed={{version:3,savedAt:'2026-09-20T00:00:00Z',currentStage:3,history:[],stageOutputs:{{3:'completed recommendations'}},stageHists:{{}},fileNames:{{project:[],context:[]}}}};
const partial={{version:3,savedAt:'2026-09-20T00:00:00Z',currentStage:2,history:[],stageOutputs:{{2:'assessment'}},stageHists:{{}},fileNames:{{project:[],context:[]}}}};
const input={{files:[{{name:'completed.json',contents:JSON.stringify(completed)}}],value:'selected'}};
loadSession(input);
await Promise.resolve();
await Promise.resolve();
if(calls.join('|')!=='enableClickableStepper|navigateToStage:3')throw new Error('completed session did not enter saved Stage 3: '+calls);
if(input.value!=='')throw new Error('completed session did not clear the file input');
input.files=[{{name:'partial.json',contents:JSON.stringify(partial)}}];
loadSession(input);
await Promise.resolve();
await Promise.resolve();
if(calls.length!==2)throw new Error('partial session enabled completed navigation');
if(!elements['act-area'].innerHTML.includes('Continue from Stage 3'))throw new Error('partial session lost resume action');
const failed={{...partial,currentStage:1,stageOutputs:{{1:'source inventory'}},climateVerifiedFailure:{{diagnostic_only:true,assessment:{{schema_version:'climate-verified-v2.1',executive_readout:'UNPUBLISHED_SYNTHETIC_MARKER'}},reason_codes:['SYNTHETIC_FAILURE']}}}};
input.files=[{{name:'diagnostic.json',contents:JSON.stringify(failed)}}];
loadSession(input);
await Promise.resolve();await Promise.resolve();
if(!climateVerifiedFailure||climateVerifiedAssessment||climateVerifiedReader)throw new Error('failed diagnostic became a successful reader');
if(elements['stage-disp'].innerHTML.includes('UNPUBLISHED_SYNTHETIC_MARKER'))throw new Error('raw diagnostic published');
if(elements['save-session-btn'].style.display!=='')throw new Error('diagnostic cannot be saved');
if(calls.length!==2)throw new Error('failed diagnostic enabled completed navigation');
"""
    result = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
