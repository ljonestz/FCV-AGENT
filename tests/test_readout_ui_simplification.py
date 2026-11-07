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


def test_climate_readout_drops_generic_preambles_but_keeps_specific_notices():
    from tests.test_climate_lens_frontend import _readout_harness
    from tests.test_climate_lens_frontend import _run_node as _run_harness
    script = _readout_harness() + r"""
const html=renderClimateVerifiedAssessment({
  analysis_status:'partial',analysis_message:'Some evidence could not be checked.',
  operation_context:{preparation_regime:'unresolved_policy_source'},
  reader_review_notice:'Verification notes identify unresolved claims.',
  summary_overview:['The project invests in resilient assets.'],
  priorities:[{rank:1,title:'Protect access',narrative:'Why.\n\nAct.'}],
  runtime_mode:'smoke',evidence_status:'preview; not approved'
});
for(const removed of ['Draft - human review required','Preparation route:','Verification notes identify unresolved claims.']){
  if(html.includes(removed))throw new Error('removed preamble remains: '+removed);
}
for(const retained of ['Assessment evidence is incomplete.','Suggested document wording is not shown because the document type or financing route could not be confirmed reliably.','Smoke test: validates workflow completion only','Candidate country evidence: preview; not approved.']){
  if(!html.includes(retained))throw new Error('required notice disappeared: '+retained);
}
"""
    result = _run_harness(script)
    assert result.returncode == 0, result.stderr


def _copy_harness(extra: str) -> str:
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "copyActiveView")
    return """
let copied='',usedButton=null;
const button={id:'copy-active-view'};
const document={getElementById:id=>id==='copy-active-view'?button:null};
const reportPlainText=html=>html.replace(/<[^>]+>/g,' ').replace(/\\s+/g,' ').trim();
const copyReportText=(text,target)=>{copied=text;usedButton=target;};
const md=value=>'<p>'+value+'</p>';
const esc=value=>String(value||'');
""" + extra + "\n" + helper + "\n"


def test_copy_uses_the_normal_readout_as_plain_text():
    script = _copy_harness("""
const stageOutputs={3:'NORMAL STAGE3'};
let focusQuestionsResult={overview:'FOCUS OVERVIEW',responses:[{question:'Q1',direct_answer:'A1'}]};
const supportsClimateVerifiedStage3View=()=>false;
const stage3ClimateLensState=()=>({valid:false});
let readoutArgs=null;
const buildNormalReadout=(text,forExport)=>{readoutArgs=[text,forExport];return '<article>READOUT '+text+'</article>';};
const renderClimateVerifiedAssessment=()=>{throw new Error('climate path used');};
const stage3DetailedHtml='STALE';
""") + """
copyActiveView();
if(!readoutArgs||readoutArgs[0]!=='NORMAL STAGE3'||readoutArgs[1]!==true)throw new Error('normal copy did not use the export readout: '+JSON.stringify(readoutArgs));
if(!copied.includes('READOUT NORMAL STAGE3')||!copied.includes('FOCUS OVERVIEW')||!copied.includes('A1'))throw new Error('copy text incomplete: '+copied);
if(copied.includes('<'))throw new Error('copy text is not plain text: '+copied);
if(usedButton!==button)throw new Error('Copy acknowledgement was not associated with the visible button');
"""
    _run_node(script)


def test_copy_uses_the_verified_climate_readout_and_legacy_fallback():
    script = _copy_harness("""
const stageOutputs={3:'LEGACY STAGE3'};
let focusQuestionsResult=null;
let verified=true,legacyValid=false;
const climateVerifiedReader={id:'reader'};
const supportsClimateVerifiedStage3View=()=>verified;
const stage3ClimateLensState=()=>({valid:legacyValid});
const buildNormalReadout=()=>'<p>NORMAL</p>';
const renderClimateVerifiedAssessment=reader=>'<article>CLIMATE '+reader.id+'</article>';
const stage3DetailedHtml='<div>LEGACY CLIMATE SCREEN</div>';
""") + """
copyActiveView();
if(copied!=='CLIMATE reader')throw new Error('verified climate copy wrong: '+copied);
verified=false;legacyValid=true;
copyActiveView();
if(copied!=='LEGACY CLIMATE SCREEN')throw new Error('legacy climate copy should reuse the on-screen body: '+copied);
"""
    _run_node(script)


def test_copy_readout_includes_document_checks_and_strips_legacy_header():
    source = INDEX.read_text(encoding="utf-8")
    assert 'id="document-checks"' in _extract_js_function(source, "stage3DocChecksHtml")
    assert "climate-partial-notice" in _extract_js_function(source, "renderLegacyClimatePrioritiesHtml")
    build = _extract_js_function(source, "buildNormalReadout")
    assert "stripStage3DoNoHarmHeader(markdownText)" in build
    assert "stage3DocChecksHtml()" in build
    strip = _extract_js_function(source, "stripStage3DoNoHarmHeader")
    script = strip + r"""
const text=stripStage3DoNoHarmHeader('---\nCLASSIFICATION: internal\nGenerated by WBG FCV Sensitivity Project Screener\nFor Review Purposes Only\n---\n# Visible analysis\nVisible content.');
if(text.includes('For Review Purposes Only')||!text.includes('Visible analysis'))throw new Error('legacy header not stripped: '+text);
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


def test_advisory_text_is_full_and_routes_to_every_priority_readout():
    source = INDEX.read_text(encoding="utf-8")
    advisory = _extract_js_function(source, "stage3AdvisoryText")
    script = "let reviewMode='design';\n" + advisory + r"""
const expectedClimate="The following priorities are suggestions to strengthen the project's design in its climate and FCV context. They are not mandatory requirements, nor may they all be relevant. The task team may wish to focus on those they believe to be more pertinent based on their own sectoral expertise and knowledge of the context within which the project will be applied. For more complex or difficult issues raised, the team are encouraged to reach out and discuss them with the FCV Country Coordinator or relevant Global Practice experts as needed.";
const expectedNormal=expectedClimate.replace('design in its climate and FCV context','design in its FCV context');
if(stage3AdvisoryText('climate')!==expectedClimate)throw new Error('full climate advisory missing');
if(stage3AdvisoryText('normal')!==expectedNormal)throw new Error('full normal advisory missing');
reviewMode='implementation';
if(!stage3AdvisoryText('climate').includes("design and implementation arrangements in its climate and FCV context"))throw new Error('implementation adaptation missing');
"""
    _run_node(script)
    assert "stage3AdvisoryText('normal')" in _extract_js_function(source, "renderNormalReadoutHtml")
    assert "stage3AdvisoryText('climate')" in _extract_js_function(source, "renderClimateVerifiedAssessment")
    assert "stage3AdvisoryText('climate')" in _extract_js_function(source, "renderLegacyClimatePrioritiesHtml")


def test_climate_detail_keeps_route_gate_and_uses_requested_labels():
    source = INDEX.read_text(encoding="utf-8")
    detailed = _extract_js_function(source, "renderClimateVerifiedAssessment")
    module = (INDEX.parent / "static" / "fcv_readout.js").read_text(encoding="utf-8")
    assert "Draft - human review required" not in detailed
    assert "Preparation route:" not in detailed
    assert "Suggested document wording is not shown because the document type or financing route could not be confirmed reliably." in detailed
    assert "'Practical considerations'" in module
    assert "'Suggested Text'" in module
    assert "'Suggested Text for an operational instrument'" in module
    assert "reader_review_notice" not in module
