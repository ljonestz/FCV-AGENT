"""Frontend contracts for optional Climate selection and diagnostic readouts."""

import json
import re
import subprocess
from pathlib import Path


INDEX = Path(__file__).resolve().parents[1] / "index.html"
SOUTH_SUDAN_FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "climate"
    / "south_sudan_dual_use.json"
)


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
                return source[start:index + 1]
    raise AssertionError(f"Unterminated body for {name}()")


def test_selector_explains_explicit_optional_selection():
    html = INDEX.read_text(encoding="utf-8")
    assert "Select up to two specialist lenses before analysis" in html
    assert "Some lenses may be suggested" in html
    assert "Climate is not selected automatically" in html


def test_climate_readout_has_two_conditional_sections():
    html = INDEX.read_text(encoding="utf-8")
    assert "renderLensReadoutSections" in html
    assert "materiality_summary" in html
    assert "other_pathways" in html
    assert "What the project may invest in" in html
    assert "How the project may deliver" in html
    assert "lensDisplayName(id)" in html


def test_readout_renderer_is_safe_conditional_and_compact():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "renderLensReadoutSections")
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{helper}
const lens = {{
  applicability: 'material',
  materiality_summary: 'Drought <script>alert(1)</script> affects delivery.',
  analysis_emphasis: ['adaptation', 'resource access'],
  readout_sections: [
    {{section_id:'invest-in',items:[{{item_id:'institutions',status:'supported',mechanism:'Transparent allocation.',evidence:['Water committees.'],evidence_gap:'Seasonal users missing.',trade_off:'May exclude customary users.'}}]}},
    {{section_id:'deliver-through',items:[{{item_id:'adaptive',status:'potential',mechanism:'Flexible delivery.',evidence:[],evidence_gap:'Trigger absent.',trade_off:''}}]}}
  ],
  other_pathways: [{{pathway:'mitigation-transition',status:'not_material',reason:'No clear pathway.'}}]
}};
const catalogue = {{name:'Climate',readout_sections:[
  {{id:'invest-in',title:'What the project may invest in',item_ids:['institutions']}},
  {{id:'deliver-through',title:'How the project may deliver',item_ids:['adaptive']}},
  {{id:'unused',title:'Unused section',item_ids:['unused']}}
]}};
const html = renderLensReadoutSections(lens,catalogue);
for (const expected of ['Climate materiality','What the project may invest in','How the project may deliver','Evidence gap','Other pathways considered','No clear pathway.']) {{
  if (!html.includes(expected)) throw new Error('missing: '+expected+' | '+html);
}}
if (html.includes('Unused section')) throw new Error('empty section rendered');
if (html.includes('<script>')) throw new Error('model HTML was not escaped');
const notApplicable = renderLensReadoutSections({{applicability:'not_applicable',materiality_summary:'Not material.',readout_sections:lens.readout_sections,other_pathways:lens.other_pathways}},catalogue);
if (!notApplicable.includes('Not material.') || notApplicable.includes('What the project may invest in') || notApplicable.includes('Other pathways considered')) throw new Error('not-applicable rendering expanded beyond materiality');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_option_a_renderers_scale_materiality_suppress_weak_items_and_escape():
    source = INDEX.read_text(encoding="utf-8")
    names = [
        "climateMaterialityLevel", "renderClimateModuleNotice",
        "renderHorizonBadge", "renderClimatePathwayStrip",
        "renderClimateInteractions", "renderClimateDividendSynthesis",
        "climateContributionZone", "renderPriorityClimateContribution",
        "renderSRNarrative",
    ]
    helpers = "\n".join(_extract_js_function(source, name) for name in names)
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{helpers}
const high = {{
  materiality_level:'high',
  materiality_summary:'Central <script>bad()</script>',
  interaction_readout:[
    {{direction_id:'climate-fcv-on-project',summary:'Flood and insecurity disrupt access.',pathways:[{{
      pathway_id:'climate-fcv-on-project-1',pressure:'Erratic floods',
      mechanism:'Access roads close during insecure periods.',
      project_implication:'Landing-site rehabilitation may be delayed.',
      design_response:'Use seasonal work windows.',project_elements:['Landing-site rehabilitation'],
      geographies:['Upper Nile'],affected_groups:['Fishing households'],
      time_horizons:['project-lifetime'],confidence:'medium',evidence_gap:'Site thresholds missing.'
    }}]}},
    {{direction_id:'project-on-climate-fcv',summary:'Benefit rules can build trust or exclusion.',pathways:[{{
      pathway_id:'project-on-climate-fcv-1',pressure:'New access rules',
      mechanism:'Rules redistribute seasonal access.',
      project_implication:'Seasonal users may lose adaptive options.',
      design_response:'Represent seasonal users.',project_elements:['BFMU governance'],
      geographies:['Sudd'],affected_groups:['Seasonal users'],
      time_horizons:['current-near-term','asset-system-lifetime'],confidence:'medium',evidence_gap:''
    }}]}}
  ],
  readout_sections:[{{section_id:'invest-in',items:[
    {{item_id:'livelihoods-opportunity',status:'supported',
      project_contribution:'Resilient livelihoods.',
      strengthening_action:'Clarify benefit sharing.',evidence:['PCN component.']}},
    {{item_id:'social-cohesion-inclusion',status:'not_material',
      project_contribution:'Do not show.',strengthening_action:'Do not show.'}}
  ]}}],
  additional_pathways:[]
}};
const priorities=[{{title:'Core priority',climate_links:{{status:'no-material-pathway',reason:'Core FCV need.'}}}},
  {{title:'Inclusive access',climate_links:{{status:'linked',interaction_pathway_ids:[],
    dividend_pathway_ids:['livelihoods-opportunity'],finding_ids:[],
    contribution:'Protects access.',strengthening_effect:'Adds monitoring.'}}}}];
const linked=priorities[1];
const unlinked=priorities[0];
const notice=renderClimateModuleNotice(high,false);
const interactions=renderClimateInteractions(high);
const dividends=renderClimateDividendSynthesis(high,priorities);
const linkedPanel=renderPriorityClimateContribution(linked);
const unlinkedPanel=renderPriorityClimateContribution(unlinked);
const sr=renderSRNarrative('Sensitive <script>bad()</script>','Responsive','Adequate','Emerging');
if(!notice.includes('strong climate emphasis')) throw new Error(notice);
if(!interactions.includes('climate-interaction-box')) throw new Error(interactions);
if(interactions.includes('causal-strip')) throw new Error('causal-strip should be gone: '+interactions);
if(!interactions.includes('over the project')) throw new Error('prose horizon missing: '+interactions);
if(!interactions.includes('Landing-site rehabilitation')) throw new Error(interactions);
if(!dividends.includes('How the current design contributes')) throw new Error(dividends);
if(!dividends.includes('Priority 2')) throw new Error(dividends);
if(dividends.includes('climate-dividend-card')) throw new Error(dividends);
if(dividends.includes('Do not show')) throw new Error(dividends);
if(!linkedPanel.includes('Climate, peace and social dividend contribution')) throw new Error(linkedPanel);
if(!unlinkedPanel.includes('No material dividend pathway identified')) throw new Error(unlinkedPanel);
if(!sr.includes('FCV Sensitivity') || !sr.includes('FCV Responsiveness')) throw new Error(sr);
if((notice+interactions+dividends+linkedPanel+unlinkedPanel+sr).includes('<script>')) throw new Error('unsafe HTML');
const low={{materiality_level:'low',materiality_summary:'Limited.',readout_sections:[],additional_pathways:[]}};
if(!renderClimateModuleNotice(low,false).includes('limited climate materiality')) throw new Error('low disclosure missing');
if(renderClimateDividendSynthesis(low,[])!=='') throw new Error('empty low synthesis rendered');
const errorNotice=renderClimateModuleNotice(null,true);
if(!errorNotice.includes('could not be produced')) throw new Error('safe failure missing');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_south_sudan_shared_html_renders_specific_dual_use_output():
    source = INDEX.read_text(encoding="utf-8")
    fixture = json.loads(SOUTH_SUDAN_FIXTURE.read_text(encoding="utf-8"))
    lens = fixture["diagnostic"]["lenses"][0]
    priorities = fixture["stage3_block"]["priorities"]
    helpers = "\n".join(_extract_js_function(source, name) for name in (
        "renderHorizonBadge",
        "renderClimatePathwayStrip",
        "renderClimateInteractions",
        "renderClimateDividendSynthesis",
        "climateContributionZone",
        "renderPriorityClimateContribution",
    ))
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{helpers}
const lens={json.dumps(lens)};
const priorities={json.dumps(priorities)};
const sharedHtml=renderClimateInteractions(lens)
  +renderClimateDividendSynthesis(lens,priorities)
  +priorities.map(renderPriorityClimateContribution).join('');
for(const expected of [
  'Landing-site rehabilitation','Upper Nile','Seasonal users',
  'in the near term','over the project',
  'Priority 1','Climate, peace and social dividend contribution',
  'No material dividend pathway identified'
]){{
  if(!sharedHtml.includes(expected)) throw new Error('missing '+expected);
}}
if(sharedHtml.includes('climate-dividend-card')) throw new Error('old cards returned');
if(sharedHtml.includes('causal-strip')) throw new Error('causal-strip should be gone');
if((sharedHtml.match(/climate-interaction-box/g)||[]).length<2) throw new Error('missing prose interaction boxes');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_low_materiality_shared_html_keeps_compact_path_and_no_material_panel():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(_extract_js_function(source, name) for name in (
        "renderHorizonBadge",
        "renderClimatePathwayStrip",
        "renderClimateInteractions",
        "renderClimateDividendSynthesis",
        "climateContributionZone",
        "renderPriorityClimateContribution",
    ))
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{helpers}
const low={{
  materiality_level:'low',
  interaction_readout:[{{direction_id:'climate-fcv-on-project',
    summary:'A limited seasonal access interaction.',
    pathways:[{{pathway_id:'climate-fcv-on-project-1',
      pressure:'Seasonal rainfall',mechanism:'Short access interruptions',
      project_implication:'One site may face a brief delay.',
      design_response:'Monitor the seasonal work window.',
      project_elements:['One landing site'],geographies:['Project area'],
      affected_groups:[],systems_or_assets:[],
      time_horizons:['current-near-term'],research_claim_ids:[],
      confidence:'low',evidence_gap:'Site timing is unconfirmed.'}}]}}],
  readout_sections:[],additional_pathways:[]
}};
const priority={{title:'Core safeguard',climate_links:{{
  status:'no-material-pathway',reason:'No distinct Climate-FCV pathway.'
}}}};
const html=renderClimateInteractions(low)
  +renderClimateDividendSynthesis(low,[priority])
  +renderPriorityClimateContribution(priority);
if(html.includes('causal-strip')) throw new Error('causal-strip should be gone: '+html);
if((html.match(/climate-interaction-box/g)||[]).length!==1) throw new Error('expected 1 prose box: '+html);
if(!html.includes('in the near term')) throw new Error('prose horizon missing: '+html);
if(!html.includes('No material dividend pathway identified')) throw new Error(html);
if(html.includes('Climate, peace and social dividends</div>')) throw new Error(html);
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_climate_state_helpers_require_selection_and_valid_entry():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(_extract_js_function(source, name) for name in (
        "isClimateLensActive", "climateLensEntry",
    ))
    script = f"""
let activeLenses=['climate'];
{helpers}
if(!isClimateLensActive()) throw new Error('selected climate not active');
const diagnostic={{lenses:[{{lens_id:'climate',materiality_level:'high'}}]}};
if(climateLensEntry(diagnostic).materiality_level!=='high') throw new Error('entry missing');
activeLenses=[];
if(isClimateLensActive()) throw new Error('unselected climate active');
if(climateLensEntry({{error:true}})!==null) throw new Error('invalid entry accepted');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_live_stage3_orders_option_a_and_preserves_core_fallback():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "renderOut")

    climate_order = [
        "renderClimateModuleNotice",
        "renderSRNarrative",
        "renderClimateInteractions",
        "renderClimateDividendSynthesis",
    ]
    positions = [helper.index(name) for name in climate_order]
    assert positions == sorted(positions)
    assert "isClimateLensActive" in helper
    assert "renderRiskExposure(stageRiskExposure)" in helper
    assert (
        "renderSRCards(stageSensitivitySummary,stageResponsivenessSummary)"
        in helper
    )


def test_download_html_uses_same_climate_sections_and_order():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "downloadHTML")

    assert "isClimateLensActive" in helper
    required = [
        "renderClimateModuleNotice",
        "wrapSRTerms(md(summarybody))",
        "renderSRNarrative",
        "renderClimateInteractions",
        "renderClimateDividendSynthesis",
    ]
    positions = [helper.index(value) for value in required]
    assert positions == sorted(positions)
    assert "renderRiskExposure(stageRiskExposure)" in helper
    assert (
        "renderSRCards(stageSensitivitySummary, stageResponsivenessSummary)"
        in helper
    )


def test_live_and_shared_priority_cards_switch_climate_panel_only_when_active():
    source = INDEX.read_text(encoding="utf-8")
    export_helper = _extract_js_function(source, "_buildExportPriorityCard")
    live_helper = _extract_js_function(source, "showPriority")

    assert "renderPriorityClimateContribution(pr)" in export_helper
    assert "Differentiated approach note" in export_helper
    assert "isClimateLensActive()" in export_helper
    assert "renderPriorityClimateContribution(pr)" in live_helper
    assert "Differentiated approach note" in live_helper
    assert "isClimateLensActive()" in live_helper


def test_express_mode_surfaces_stage2_structured_diagnostic_failures():
    source = INDEX.read_text(encoding="utf-8")
    start = source.index("else if(sn===2)")
    end = source.index("else if(sn===3)", start)
    stage2_handler = source[start:end]

    assert "p.parse_error" in stage2_handler
    assert "p.parse_error_message" in stage2_handler
    assert "showLensWarnings" in stage2_handler


def test_frontend_persists_climate_research_across_stages_and_reports():
    source = INDEX.read_text(encoding="utf-8")

    assert "climateResearch={}" in source
    assert "if(p.climate_research)climateResearch=p.climate_research" in source
    assert "climate_research:climateResearch" in source
    assert "climate_research: climateResearch || {}" in source
    assert "lensDiagnostic={};lensContextSources=[];climateResearch={}" in source


def test_materiality_notice_uses_relevance_title_and_source_list():
    html = INDEX.read_text(encoding="utf-8")
    assert "How relevant is climate to this project?" in html
    assert "Maximizing the Peace and Social Dividends of Climate Action" in html
    assert "FCV-Sensitive Climate Action Framework" in html
    assert "Defueling Conflict" in html


def test_interactions_render_as_prose_boxes_without_causal_grid():
    html = INDEX.read_text(encoding="utf-8")
    assert ".causal-strip" not in html
    assert "climate-interaction-box" in html
    fn = _extract_js_function(html, "renderClimateInteractions")
    dep = _extract_js_function(html, "renderClimatePathwayStrip")
    esc = _extract_js_function(html, "esc")
    lens = {
        "interaction_readout": [
            {"direction_id": "climate-fcv-on-project", "summary": "Drought cuts access.",
             "pathways": [{"pressure": "Drought", "mechanism": "road closure",
                           "project_implication": "delayed works",
                           "design_response": "seasonal windows",
                           "project_elements": ["water points"],
                           "time_horizons": ["current-near-term"]}]},
            {"direction_id": "project-on-climate-fcv", "summary": "Siting reallocates water.",
             "pathways": []},
        ]
    }
    script = f"{esc}\n{dep}\n{fn}\nprocess.stdout.write(renderClimateInteractions({json.dumps(lens)}));"
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "How climate and FCV dynamics could affect this project" in out.stdout
    assert "How this project could affect climate and FCV dynamics" in out.stdout
    assert "climate-interaction-box" in out.stdout
    assert "›" not in out.stdout  # no › arrow glyph
    assert "seasonal windows" in out.stdout  # design response in prose


def test_reflections_render_with_status_chips_and_intro():
    html = INDEX.read_text(encoding="utf-8")
    assert "renderClimateReflections" in html
    fn = _extract_js_function(html, "renderClimateReflections")
    esc = _extract_js_function(html, "esc")
    lens = {"reflections": [
        {"question_key": "cq2_maladaptation", "title": "Maladaptation and lock-in",
         "status_cue": "partial gap", "text": "Siting is engineering, not allocation."},
        {"question_key": "cq4_inclusion", "title": "Vulnerable groups",
         "status_cue": "strong", "text": "IDP households explicitly targeted."}],
        "less_central": "HDP coordination is light here."}
    script = f"{esc}\n{fn}\nprocess.stdout.write(renderClimateReflections({json.dumps(lens)}));"
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "Reflections on core climate and FCV considerations" in out.stdout
    assert "reflection-chip" in out.stdout
    assert "partial gap" in out.stdout
    assert "Less central here" in out.stdout
    empty = subprocess.run(["node", "-e", f"{esc}\n{fn}\nprocess.stdout.write(renderClimateReflections({{}}));"], capture_output=True, text=True)
    assert empty.returncode == 0, empty.stderr
    assert empty.stdout.strip() == ""
