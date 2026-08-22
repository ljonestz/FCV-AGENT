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


def _js_escape_helper() -> str:
    return """
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
"""


def test_stage3_detailed_reading_shell_uses_compact_sticky_rating_rail():
    html = INDEX.read_text(encoding="utf-8")

    assert ".main{max-width:1180px" in html
    normalized = re.sub(r"\s+", "", html)
    assert re.search(
        r"\.stage3-reading-shell\{[^}]*display:grid;[^}]*grid-template-columns:minmax\(180px,220px\)",
        normalized,
    )
    assert re.search(
        r"\.stage3-rating-rail\{[^}]*position:sticky;[^}]*top:",
        normalized,
    )
    assert '.stage3-reading-shell[data-stage3-view="summary"]{grid-template-columns:1fr}' in normalized
    assert re.search(
        r"@media\(max-width:860px\)\{.*?\.stage3-reading-shell\{grid-template-columns:1fr;gap:12px\}.*?\.stage3-rating-rail\{display:none\}.*?\.stage3-mobile-ratings\{display:block\}",
        normalized,
    )
    assert "min-height:44px" in normalized
    assert ".stage3-mobile-ratingssummary:focus-visible" in normalized
    assert ".stage3-mobile-ratings summary:focus-visible" in html
    assert ".stage3-mobile-ratings" in html
    assert "stage3-rating-rail" in html
    assert ".sw-grid{display:grid;grid-template-columns:1fr;" in html
    assert '<aside class="fcv-sidebar"' not in html
    assert "stage3OverviewHtml()" in html


def test_stage3_reading_shell_switches_rail_visibility_with_the_active_view():
    source = INDEX.read_text(encoding="utf-8")

    setter = _extract_js_function(source, "setStage3View")
    assert "stage3-reading-shell" in setter
    assert "data-stage3-view" in setter
    assert "is-summary" in setter
    assert "is-detailed" in setter
    assert "stage3View=view" in setter


def test_stage3_view_keyboard_navigation_refocuses_the_rerendered_tab():
    source = INDEX.read_text(encoding="utf-8")
    handler = _extract_js_function(source, "handleStage3ViewKeydown")
    script = f"""
let generation = 0;
let activeId = 'stage3-summary-tab';
let focusedOld = false;
let focusedNew = false;
const oldTabs = [
  {{id:'stage3-summary-tab', focus:()=>{{focusedOld=true;}}}},
  {{id:'stage3-detailed-tab', focus:()=>{{focusedOld=true;}}}}
];
const newTabs = [
  {{id:'stage3-summary-tab', focus:()=>{{focusedNew=true;}}}},
  {{id:'stage3-detailed-tab', focus:()=>{{focusedNew=true;}}}}
];
const document = {{
  get activeElement() {{ return activeId === 'stage3-summary-tab' ? (generation ? newTabs[0] : oldTabs[0]) : (generation ? newTabs[1] : oldTabs[1]); }},
  querySelectorAll: () => generation ? newTabs : oldTabs,
  getElementById: id => (generation ? newTabs : oldTabs).find(tab => tab.id === id) || null
}};
const setStage3View = (view,preservePriority,focusTabId) => {{
  generation = 1;
  activeId = view === 'summary' ? 'stage3-summary-tab' : 'stage3-detailed-tab';
  if (focusTabId) document.getElementById(focusTabId).focus();
}};
{handler}
handleStage3ViewKeydown({{key:'ArrowRight', preventDefault:()=>{{}}}});
if (focusedOld) throw new Error('keyboard navigation focused detached tab');
if (!focusedNew) throw new Error('keyboard navigation did not focus rerendered tab');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_stage3_direct_tab_activation_refocuses_only_when_requested():
    source = INDEX.read_text(encoding="utf-8")
    toggle = _extract_js_function(source, "stage3ViewToggleHtml")
    setter = _extract_js_function(source, "setStage3View")
    script = f"""
let stage3View = 'detailed';
let stage3DetailedHtml = '<p>Detailed</p>';
let openSummaryPriority = 0;
let currentPriority = 0;
let generation = 0;
let focusedOld = false;
let focusedNew = false;
const makeTab = (id, fresh) => ({{
  id,
  classList: {{remove(){{}}, toggle(){{}}}},
  setAttribute(){{}},
  focus(){{ if (fresh) focusedNew = true; else focusedOld = true; }}
}});
const oldTabs = {{summary:makeTab('stage3-summary-tab',false), detailed:makeTab('stage3-detailed-tab',false)}};
const newTabs = {{summary:makeTab('stage3-summary-tab',true), detailed:makeTab('stage3-detailed-tab',true)}};
const shell = {{dataset:{{}}, setAttribute(){{}}, classList:{{toggle(){{}}}}}};
const stageDisplay = {{dataset:{{}}, setAttribute(){{}}, classList:{{toggle(){{}}}}}};
const out = {{dataset:{{}}, setAttribute(){{}}, set innerHTML(value){{ this.html = value; generation = 1; }}}};
const document = {{
  getElementById(id) {{
    if (id === 'stage3-summary-tab') return generation ? newTabs.summary : oldTabs.summary;
    if (id === 'stage3-detailed-tab') return generation ? newTabs.detailed : oldTabs.detailed;
    if (id === 'stage-disp') return stageDisplay;
    if (id === 'out-txt') return out;
    return null;
  }},
  querySelector(selector) {{ return selector === '.stage3-reading-shell' ? shell : null; }}
}};
const supportsAnyStage3Summary = () => true;
const renderStage3Summary = () => '<p>Summary</p>';
const renderSummaryPriorityAccordion = () => '';
const renderPrioritiesIntro = () => {{}};
const renderPriorityStepper = () => {{}};
const showPriority = () => {{}};
{toggle}
{setter}
const toggleHtml = stage3ViewToggleHtml();
if (!toggleHtml.includes("setStage3View('summary',true,'stage3-summary-tab')")) throw new Error('direct Summary activation does not request focus');
setStage3View('summary');
if (focusedOld || focusedNew) throw new Error('programmatic view change stole focus');
generation = 0;
focusedOld = false;
focusedNew = false;
setStage3View('summary', true, 'stage3-summary-tab');
if (focusedOld) throw new Error('direct activation focused detached tab');
if (!focusedNew) throw new Error('direct activation did not focus rerendered tab');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_climate_opening_uses_relevance_language_and_quiet_provenance():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "climateMaterialityLevel",
            "climateReadoutComplete",
            "renderClimateModuleNotice",
            "renderClimateGroundingSources",
        )
    )
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{helpers}
const lens = {{
  materiality_level:'high',
  executive_summary:'This natural resources operation works in a setting shaped by conflict, displacement, and repeated climate shocks.',
  materiality_summary:'Flood access affects Component 1 delivery.',
  reflections:[{{text:'A grounded reflection.'}}],
  integration_summary:'A complete readout.'
}};
const notice = renderClimateModuleNotice(lens,false,{{state:'thematic-only'}});
for (const expected of [
  'Climate relevance to this project',
  'High climate relevance','Why it matters:',
  'This natural resources operation works in a setting shaped by conflict, displacement, and repeated climate shocks.',
  'Flood access affects Component 1 delivery.'
]) {{
  if (!notice.includes(expected)) throw new Error('missing '+expected+' | '+notice);
}}
for (const forbidden of [
  'Climate-FCV module','climate-module-notice','materiality','reviewed country-bank release',
  'advisory FCV screening readout','You selected'
]) {{
  if (notice.toLowerCase().includes(forbidden.toLowerCase())) throw new Error('forbidden '+forbidden+' | '+notice);
}}
const expectedEvidence = {{
  'bank+research':'Reviewed country evidence and current country research',
  'bank-only':'Reviewed country evidence',
  'research-only':'Current country research',
  'thematic-only':'Project documents and thematic Climate-FCV sources'
}};
for (const [state,copy] of Object.entries(expectedEvidence)) {{
  const rendered=renderClimateGroundingSources({{state,sources:[]}});
  if (!rendered.includes('Evidence basis') || !rendered.includes(copy)) throw new Error(state+' | '+rendered);
  for (const forbidden of ['bank_missing','country-bank release','warning_code']) {{
    if (rendered.includes(forbidden)) throw new Error(state+' leaks '+forbidden+' | '+rendered);
  }}
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_climate_summary_caps_dynamic_strengths_and_uses_longer_overview():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "climateSummaryStrengths",
            "climateSummaryPriorityItems",
            "renderStage3AdvisoryTransition",
            "getConcisePriority",
            "renderSummaryPriorityAccordion",
            "renderClimateVerifiedSummary",
        )
    )
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
const reviewMode='design';
let openSummaryPriority=0;
{helpers}
const reader = {{
  operation_context: {{
    document_type:'Program Paper', instrument_type:'PforR',
    preparation_regime:'new_model', es_regime:'INSTRUMENT_SPECIFIC', is_mpa:false
  }},
  executive_readout: 'First overview paragraph with the project context and the main climate-FCV interaction.\\n\\nSecond overview paragraph with the design choices and remaining implementation implications.',
  existing_responses: [
    {{description:'Climate resilience is embedded in infrastructure standards.'}},
    {{description:'Resource governance is sequenced before investment.'}},
    {{description:'Inclusion safeguards are concrete and operational.'}},
    {{description:'A fourth positive design feature should not appear in the compact summary.'}}
  ],
  priorities: [{{rank:1, title:'Priority 1', narrative:'A concrete operational action.', minimum_action:'Add the action to the design.'}}],
  climate_sensitivity_rating: {{label:'Strong'}}
}};
const strengths = climateSummaryStrengths(reader);
if (strengths.length !== 3) throw new Error('expected three strengths, got '+strengths.length);
const html = renderClimateVerifiedSummary(reader);
if (html.includes('Climate-FCV design readout')) throw new Error('summary contains redundant climate title');
if (!html.includes('Second overview paragraph')) throw new Error('summary omitted the longer overview');
if (html.includes('A fourth positive design feature')) throw new Error('summary exceeded the three-tile cap');
if (!html.includes('class="concise-strength-text"')) throw new Error('strength explanation lacks readable body element');
if (!html.includes('id="summary-priority-accordion"')) throw new Error('summary omitted the priority accordion');
if (!html.includes('How this operation was routed') || !html.includes('Program Paper') || !html.includes('PforR')) throw new Error('summary omitted operation routing');
if (!html.includes('E&amp;S route') || !html.includes('INSTRUMENT SPECIFIC')) throw new Error('summary omitted E&S routing');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_incomplete_recommendations_are_fail_loud_in_both_climate_views():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "climateSummaryStrengths",
            "climateSummaryPriorityItems",
            "renderStage3AdvisoryTransition",
            "getConcisePriority",
            "renderSummaryPriorityAccordion",
            "renderClimateVerifiedSummary",
            "isPublicWorldBankHttpsUrl",
            "renderClimateVerifiedAssessment",
        )
    )
    reader = {
        "recommendation_status": "incomplete",
        "recommendation_message": (
            "The recommendation stage could not be completed. "
            "Do not treat this Recommendations Note as complete."
        ),
        "executive_readout": "A bounded executive readout.",
        "priorities": [],
        "core_questions": [],
        "existing_responses": [],
        "review_readiness_flags": [],
        "minor_climate_points": [],
    }
    script = f"""
{_js_escape_helper()}
const renderClimateRelevantGuidance = () => '';
const reviewMode='design';
let openSummaryPriority=0;
{helpers}
const reader = {json.dumps(reader)};
for (const [name,html] of [
  ['summary',renderClimateVerifiedSummary(reader)],
  ['detailed',renderClimateVerifiedAssessment(reader)]
]) {{
  if (!html.toLowerCase().includes('could not be completed')) {{
    throw new Error(name+' view hides incomplete recommendation state | '+html);
  }}
  if (html.includes('No operational priorities were identified')) {{
    throw new Error(name+' view uses neutral zero-priority copy | '+html);
  }}
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )

    assert result.returncode == 0, result.stderr
    render_out = _extract_js_function(source, "renderOut")
    assert "recommendation_status==='incomplete'" in render_out
    assert "Recommendations stage incomplete" in render_out


def test_climate_summary_strength_cards_split_full_heading_from_explanation():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "climateSummaryStrengths")
    script = f"""
{helper}
const fullHeading = 'Climate-resilient infrastructure standards protect fisheries investments and local livelihoods from severe seasonal flooding.';
const explanation = 'Sub-component 1.2 requires all-weather facilities, helping services continue when seasonal water levels rise.';
const cards = climateSummaryStrengths({{existing_responses:[
  {{description:fullHeading+' '+explanation}},
  {{description:'Co-management agreements are sequenced before infrastructure becomes operational.'}}
]}});
if (cards[0].title !== fullHeading) throw new Error('heading was truncated: '+cards[0].title);
if (cards[0].text !== explanation) throw new Error('explanation was not separated: '+cards[0].text);
if (cards[1].title !== cards[1].text) throw new Error('one-sentence fallback was not preserved');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_climate_summary_initial_render_hydrates_priority_navigation():
    source = INDEX.read_text(encoding="utf-8")

    assert "if(host)host.innerHTML=renderSummaryPriorityAccordion();" in source
    assert "el.style.display=showSummary?'none':''" in source
    assert "if(supportsClimateVerifiedStage3View())stageThreePriorities=climateSummaryPriorityItems(climateVerifiedReader);" in source
    assert "if(supportsClimateVerifiedStage3View()&&stageThreePriorities&&stageThreePriorities.length)initStage3UI();" in source


def test_climate_summary_caps_ranked_priorities_at_three():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "climateSummaryPriorityItems")
    script = f"""
{helper}
const priorities = climateSummaryPriorityItems({{
  priorities: [
    {{rank:4, title:'Fourth'}},
    {{rank:2, title:'Second'}},
    {{rank:1, title:'First'}},
    {{rank:3, title:'Third'}}
  ]
}});
if (priorities.length !== 3) throw new Error('expected three priorities, got '+priorities.length);
if (priorities.map(item => item.title).join('|') !== 'First|Second|Third') {{
  throw new Error('priorities are not ranked correctly: '+priorities.map(item => item.title).join('|'));
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_climate_summary_truncates_overview_at_a_complete_sentence():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "climateSummaryStrengths",
            "climateSummaryPriorityItems",
            "renderStage3AdvisoryTransition",
            "getConcisePriority",
            "renderSummaryPriorityAccordion",
            "renderClimateVerifiedSummary",
        )
    )
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
const reviewMode='design';
let openSummaryPriority=0;
{helpers}
const first = 'Context '.repeat(119) + 'first sentence ends here.';
const second = 'Design '.repeat(109) + 'second sentence ends here.';
const third = 'Unfinished-tail-marker '.repeat(40) + 'third sentence ends here.';
const html = renderClimateVerifiedSummary({{executive_readout:first+' '+second+' '+third}});
if (!html.includes('second sentence ends here.…')) throw new Error('overview did not end at the last complete sentence');
if (html.includes('Unfinished-tail-marker')) throw new Error('overview included words beyond the sentence boundary');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_climate_detailed_reader_keeps_rating_above_core_questions_and_plain_method_fold():
    source = INDEX.read_text(encoding="utf-8")
    renderer = _extract_js_function(source, "renderClimateVerifiedAssessment")

    assert renderer.index("${ratingHtml}") < renderer.index("climateReportSection('Core climate-FCV questions'")
    assert "Method, limitations, and sources" in renderer
    assert "technical_annex" not in renderer


def test_climate_stage3_overview_explains_why_strengthening_is_needed():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in ("climateIntegrationShortLabel", "stage3OverviewHtml")
    )
    script = f"""
const isClimateLensActive = () => true;
{helpers}
if (climateIntegrationShortLabel('Adequate') !== 'Opportunities to further strengthen climate and FCV elements') {{
  throw new Error('rating helper does not explain the improvement opportunity');
}}
const html=stage3OverviewHtml();
for (const expected of ['stage3-rating-rail','Climate-FCV integration','fcv-int-summary','stage3-mobile-ratings','stage3-rating-meaning']) {{
  if (!html.includes(expected)) throw new Error('missing '+expected+' | '+html);
}}
if ((html.match(/class="stage3-rating-card"/g)||[]).length !== 2) throw new Error('climate lens should have one desktop and one mobile card | '+html);
if (html.includes('<svg')) throw new Error('climate rating still renders a gauge SVG | '+html);
if (!html.includes('Opportunities to further strengthen climate and FCV elements')) throw new Error('climate meaning text is missing | '+html);
for (const forbidden of ['Indicative Climate-FCV Integration Readout','This AI-assisted readout supports expert review','Priority overview','pov-sb']) {{
  if (html.includes(forbidden)) throw new Error('verbose gauge copy remains | '+html);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_climate_executive_readout_is_stacked_and_constructive():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "renderClimateStrengthsWeaknesses")
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{helper}
const html=renderClimateStrengthsWeaknesses({{strengths_weaknesses:[
  {{side:'strength',title:'Flood-resilient sites',text:'Component 1 uses raised designs.'}},
  {{side:'gap',title:'Seasonal operating rules',text:'The PCN does not yet evidence a trigger.'}}
]}});
for (const expected of ['Executive readout','Where the design is stronger','Where the design could be strengthened']) {{
  if (!html.includes(expected)) throw new Error('missing '+expected+' | '+html);
}}
if (html.includes('Where the design is weak')) throw new Error('old deficit language remains');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


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
        "climateMaterialityLevel", "climateReadoutComplete",
        "renderClimateModuleNotice",
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
if(!notice.includes('High climate relevance')) throw new Error(notice);
if(!interactions.includes('climate-interaction-box')) throw new Error(interactions);
if(interactions.includes('causal-strip')) throw new Error('causal-strip should be gone: '+interactions);
if(!interactions.includes('over the project')) throw new Error('prose horizon missing: '+interactions);
if(!interactions.includes('Landing-site rehabilitation')) throw new Error(interactions);
if(!dividends.includes('The current design already contributes')) throw new Error(dividends);
if(!dividends.includes('Priority 2')) throw new Error(dividends);
if(dividends.includes('climate-dividend-card')) throw new Error(dividends);
if(dividends.includes('Do not show')) throw new Error(dividends);
if(!linkedPanel.includes('Climate, peace and social dividend contribution')) throw new Error(linkedPanel);
if(!unlinkedPanel.includes('No material dividend pathway identified')) throw new Error(unlinkedPanel);
if(!sr.includes('FCV Sensitivity') || !sr.includes('FCV Responsiveness')) throw new Error(sr);
if((notice+interactions+dividends+linkedPanel+unlinkedPanel+sr).includes('<script>')) throw new Error('unsafe HTML');
const low={{materiality_level:'low',materiality_summary:'Limited.',readout_sections:[],additional_pathways:[]}};
if(!renderClimateModuleNotice(low,false).includes('Limited climate relevance')) throw new Error('low disclosure missing');
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

    # Climate-valid path (redesign): notice/gauge -> strengths & weaknesses -> core questions.
    # renderSRNarrative is NOT in the climate path (replaced by integration gauge + core questions)
    climate_order = [
        "renderClimateModuleNotice",
        "renderClimateStrengthsWeaknesses",
        "renderClimateCoreQuestions",
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
    # Climate-valid path mirrors renderOut (redesign): notice -> strengths&weaknesses -> core questions.
    required = [
        "renderClimateModuleNotice",
        "wrapSRTerms(md(summarybody))",
        "renderClimateStrengthsWeaknesses",
        "renderClimateCoreQuestions",
    ]
    positions = [helper.index(value) for value in required]
    assert positions == sorted(positions)
    # Dividends + wider-FCV are no longer called in the climate export block
    _seg = helper[helper.index("renderClimateStrengthsWeaknesses"):helper.index("renderClimateCoreQuestions") + 400]
    assert "renderClimateDividendSynthesis" not in _seg
    assert "renderWiderFcvContext" not in _seg
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


def test_priority_controls_have_no_secondary_next_previous_navigator():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "showPriority")

    assert "pc-nav" not in source
    assert "nextPriority" not in source
    assert "prevPriority" not in source
    assert "if(nextBtn)" not in helper
    assert '<button type="button" class="ps-step' in source
    assert 'aria-pressed="${i===currentPriority?' in source


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


def test_frontend_persists_display_safe_climate_grounding_across_outputs():
    source = INDEX.read_text(encoding="utf-8")

    assert "climateGrounding={}" in source
    assert "if(p.climate_grounding)climateGrounding=p.climate_grounding" in source
    assert "climate_grounding:climateGrounding" in source
    assert "climate_grounding: climateGrounding || {}" in source
    assert (
        "lensDiagnostic={};lensContextSources=[];climateResearch={};"
        "climateGrounding={}"
    ) in source


def test_climate_grounding_notice_is_separate_from_opening_card():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in [
            "climateMaterialityLevel",
            "climateReadoutComplete",
            "renderClimateModuleNotice",
            "renderClimateGroundingSources",
        ]
    )
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{helpers}
const lens = {{materiality_level:'medium', materiality_summary:'Material.', reflections:[{{text:'Grounded.'}}], integration_summary:'Integrated.'}};
const states = {{
  'bank+research':'Reviewed country evidence and current country research',
  'bank-only':'Reviewed country evidence',
  'research-only':'Current country research',
  'thematic-only':'Project documents and thematic Climate-FCV sources'
}};
for (const [state, expected] of Object.entries(states)) {{
  const grounding={{state, content_version:'v1<script>alert(1)</script>', sources:[]}};
  const notice = renderClimateModuleNotice(lens, false, grounding);
  const evidence = renderClimateGroundingSources(grounding);
  if (!evidence.includes(expected)) throw new Error(state+' evidence basis missing');
  if (notice.includes(expected) || notice.includes('climate-grounding-warning')) throw new Error(state+' provenance leaked into opening card');
  if ((notice+evidence).includes('<script>')) throw new Error('metadata was not escaped');
}}
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_shared_html_lists_only_reviewed_bank_source_metadata():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "renderClimateGroundingSources")
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{helper}
const html = renderClimateGroundingSources({{
  state:'bank-only',
  content_version:'ssd-v1',
  sources:[
    {{title:'Reviewed <source>',url:'https://example.org/reviewed',provenance:['bank']}},
    {{title:'Live source',url:'https://example.org/live',provenance:['research']}}
  ]
}});
if (!html.includes('Evidence basis')) throw new Error('heading missing');
if (!html.includes('Content version: ssd-v1')) throw new Error('version missing');
if (!html.includes('Reviewed &lt;source&gt;')) throw new Error('bank title missing or unsafe');
if (!html.includes('https://example.org/reviewed')) throw new Error('bank URL missing');
if (html.includes('Live source')) throw new Error('live source leaked into bank subsection');
const researchOnly=renderClimateGroundingSources({{state:'research-only',sources:[]}});
if (!researchOnly.includes('Current country research')) throw new Error('research-only evidence basis missing');
if (researchOnly.includes('Reviewed country sources used')) throw new Error('research-only must not render bank source details');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_climate_notice_uses_relevance_title_and_source_list():
    html = INDEX.read_text(encoding="utf-8")
    assert "Climate relevance to this project" in html
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


def test_interactions_prefer_narrative_prose_and_fall_back_to_strip():
    html = INDEX.read_text(encoding="utf-8")
    fn = _extract_js_function(html, "renderClimateInteractions")
    dep = _extract_js_function(html, "renderClimatePathwayStrip")
    esc = _extract_js_function(html, "esc")
    lens = {
        "interaction_readout": [
            {
                "direction_id": "climate-fcv-on-project",
                "summary": "Flood and insecurity disrupt delivery.",
                "narrative": "Flooding does more than damage roads.\n\nIt pushes fishing communities into contested areas.",
                "pathways": [{"pressure": "Drought", "mechanism": "road closure",
                              "project_implication": "delayed works",
                              "design_response": "seasonal windows"}],
            },
            {
                "direction_id": "project-on-climate-fcv",
                "summary": "Siting reallocates water.",
                "pathways": [{"pressure": "Siting", "mechanism": "reallocation",
                              "project_implication": "grievance",
                              "design_response": "committee allocation"}],
            },
        ]
    }
    script = f"{esc}\n{dep}\n{fn}\nprocess.stdout.write(renderClimateInteractions({json.dumps(lens)}));"
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    # Direction 1 has a narrative → prose paragraphs, split on blank lines.
    assert out.stdout.count("climate-interaction-prose") == 2
    assert "Flooding does more than damage roads." in out.stdout
    # The narrative is used instead of the stitched strip for that direction.
    assert "seasonal windows" not in out.stdout
    # Direction 2 has no narrative → falls back to the pathway strip.
    assert "climate-pathway-prose" in out.stdout
    assert "committee allocation" in out.stdout


def test_wider_fcv_context_renders_grey_callout_or_empty():
    html = INDEX.read_text(encoding="utf-8")
    assert "renderWiderFcvContext" in html
    fn = _extract_js_function(html, "renderWiderFcvContext")
    esc = _extract_js_function(html, "esc")
    out = subprocess.run(["node", "-e", f'{esc}\n{fn}\nprocess.stdout.write(renderWiderFcvContext("Contested state delivery structures."));'], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "Wider FCV context" in out.stdout
    assert "wider-fcv-note" in out.stdout
    assert "Contested state delivery structures." in out.stdout
    empty = subprocess.run(["node", "-e", f'{esc}\n{fn}\nprocess.stdout.write(renderWiderFcvContext(""));'], capture_output=True, text=True)
    assert empty.returncode == 0, empty.stderr
    assert empty.stdout.strip() == ""


def test_single_integration_gauge_present_in_module_mode():
    html = INDEX.read_text(encoding="utf-8")
    assert "Climate-FCV integration" in html
    assert "Indicative Climate-FCV Integration Readout" not in html
    assert "climateIntegrationShortLabel" in html
    assert "climateIntegration" in html
    assert "integrationGaugeFraction" in html
    fn = _extract_js_function(html, "integrationGaugeFraction")
    out = subprocess.run(
        ["node", "-e", f"{fn}\nconsole.log([integrationGaugeFraction('well_integrated'),integrationGaugeFraction('partly_integrated'),integrationGaugeFraction('weakly_integrated'),integrationGaugeFraction('insufficient_evidence'),integrationGaugeFraction('')].join(','))"],
        capture_output=True, text=True
    )
    assert out.returncode == 0, out.stderr
    vals = out.stdout.strip().split(",")
    assert vals[0] == "1"
    assert vals[3] == "0" and vals[4] == "0"
    assert float(vals[1]) > float(vals[2]) > 0


def test_climate_gauge_uses_six_tier_rating():
    html = INDEX.read_text(encoding="utf-8")
    assert "climateIntegrationRatingFraction" in html
    fn = _extract_js_function(html, "climateIntegrationRatingFraction")
    out = subprocess.run(
        ["node", "-e",
         f"{fn}\nconsole.log([climateIntegrationRatingFraction('Extremely Low'),"
         f"climateIntegrationRatingFraction('Adequate'),"
         f"climateIntegrationRatingFraction('Very Well Embedded'),"
         f"climateIntegrationRatingFraction('')].join(','))"],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    vals = out.stdout.strip().split(",")
    # Extremely Low > 0 (tier 1 of 6), Adequate = 4/6, top = 1, invalid = 0
    assert abs(float(vals[0]) - (1 / 6)) < 0.01
    assert abs(float(vals[1]) - (4 / 6)) < 0.01
    assert vals[2] == "1"
    assert vals[3] == "0"


def test_core_questions_render_intro_interactions_and_theme_answers_with_reference():
    html = INDEX.read_text(encoding="utf-8")
    assert "renderClimateCoreQuestions" in html
    fn = _extract_js_function(html, "renderClimateCoreQuestions")
    dep1 = _extract_js_function(html, "renderClimatePathwayStrip")
    esc = _extract_js_function(html, "esc")
    lens = {
        "interaction_readout": [
            {"direction_id": "climate-fcv-on-project", "summary": "Flood risk.",
             "narrative": "Para one.\n\nPara two names Boma Fisheries Management Units.", "pathways": []},
            {"direction_id": "project-on-climate-fcv", "summary": "Cohesion.",
             "narrative": "Governance forum.", "pathways": []},
        ],
        "reflections": [
            {"question_key": "cq2_maladaptation", "title": "Could the design lock in maladaptation?",
             "status_cue": "partial gap", "source": "FCV-Sensitive Climate Action Framework",
             "text": "Answer para one.\n\nAnswer para two."},
        ],
    }
    script = f"{esc}\n{dep1}\n{fn}\nprocess.stdout.write(renderClimateCoreQuestions({json.dumps(lens)}));"
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    # Lay-reader intro names the source literature
    assert "Maximizing the Peace and Social Dividends of Climate Action" in out.stdout
    # Both interaction directions present
    assert "climate and FCV" in out.stdout
    # Theme answer with its title, source line, and paragraph split
    assert "Could the design lock in maladaptation?" in out.stdout
    assert "FCV-Sensitive Climate Action Framework" in out.stdout
    assert "For further insights on why this matters, see:" in out.stdout
    assert "reflection-chip" not in out.stdout
    assert "partial gap" not in out.stdout
    assert out.stdout.count("<p") >= 4  # multi-paragraph answers


def test_strengths_weaknesses_two_column_full_detail():
    html = INDEX.read_text(encoding="utf-8")
    assert "renderClimateStrengthsWeaknesses" in html
    fn = _extract_js_function(html, "renderClimateStrengthsWeaknesses")
    esc = _extract_js_function(html, "esc")
    lens = {"strengths_weaknesses": [
        {"side": "strength", "title": "Community delivery", "text": "Fits weak centre and adapts to floods."},
        {"side": "gap", "title": "Flood-displacement", "text": "Named but no design response."}]}
    out = subprocess.run(["node", "-e",
        f"{esc}\n{fn}\nprocess.stdout.write(renderClimateStrengthsWeaknesses({json.dumps(lens)}));"],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "Where the design is strong" in out.stdout
    assert "Community delivery" in out.stdout
    assert "Named but no design response." in out.stdout


def test_reflections_render_without_status_chips():
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
    assert "reflection-chip" not in out.stdout
    assert "partial gap" not in out.stdout
    assert "Less central here" in out.stdout
    empty = subprocess.run(["node", "-e", f"{esc}\n{fn}\nprocess.stdout.write(renderClimateReflections({{}}));"], capture_output=True, text=True)
    assert empty.returncode == 0, empty.stderr
    assert empty.stdout.strip() == ""


def test_live_climate_order_notice_sw_questions():
    html = INDEX.read_text(encoding="utf-8")
    body = html.split("function renderOut", 1)[1][:8000]
    i_notice = body.index("renderClimateModuleNotice")
    i_sw = body.index("renderClimateStrengthsWeaknesses")
    i_q = body.index("renderClimateCoreQuestions")
    assert i_notice < i_sw < i_q
    # Dividends + wider-FCV renderers are no longer called in the climate block
    seg = body[i_notice:i_q + 400]
    assert "renderClimateDividendSynthesis" not in seg
    assert "renderWiderFcvContext" not in seg


def test_policy_boundary_notice_present():
    html = INDEX.read_text(encoding="utf-8")
    assert "does not determine ESF or ESS compliance" in html


def test_priority_compliance_renderer():
    html = INDEX.read_text(encoding="utf-8")
    assert "renderPriorityCompliance" in html
    fn = _extract_js_function(html, "renderPriorityCompliance")
    esc_fn = _extract_js_function(html, "esc")
    base = esc_fn + "\n" + fn + "\n"
    # not_determined + no referral -> empty
    e = subprocess.run(
        ["node", "-e", base + "process.stdout.write(renderPriorityCompliance({policy_status:'not_determined',specialist_referral:null}))"],
        capture_output=True, text=True,
    )
    assert e.returncode == 0, e.stderr
    assert e.stdout.strip() == ""
    # mandatory_reference + referral -> shows both
    payload = "{policy_status:'mandatory_reference',specialist_referral:{required:true,route:'Task Team E&S specialist',reason:'Possible ESCP conflict.'}}"
    o = subprocess.run(
        ["node", "-e", base + f"process.stdout.write(renderPriorityCompliance({payload}))"],
        capture_output=True, text=True,
    )
    assert o.returncode == 0, o.stderr
    assert "Mandatory reference" in o.stdout
    # esc() HTML-encodes '&' → '&amp;' in the rendered output
    assert "Task Team E" in o.stdout and "S specialist" in o.stdout
    assert "Possible ESCP conflict." in o.stdout


def test_integration_rating_uses_textual_slim_bar_updates():
    """The climate integration card is updated with text, width, and accessible progress."""
    html = INDEX.read_text(encoding="utf-8")
    assert "data-rating-key=\"climate-integration\"" in html
    assert "updateRatingCards('climate-integration'" in html
    assert "fill.style.width" in html
    assert "bar.setAttribute('aria-valuenow'" in html
    assert "climateIntegrationShortLabel(rating)" in html


def test_reflections_render_sensitivity_responsiveness_evidence():
    """I3: renderClimateReflections appends S/R evidence blocks when present."""
    html = INDEX.read_text(encoding="utf-8")
    fn = _extract_js_function(html, "renderClimateReflections")
    esc = _extract_js_function(html, "esc")
    lens = {
        "reflections": [
            {"question_key": "cq1_interaction", "title": "Climate-FCV interaction",
             "status_cue": "addressed", "text": "Flooding disrupts access."},
        ],
        "less_central": None,
        "sensitivity_evidence": ["The design acknowledges seasonal flooding risk."],
        "responsiveness_evidence": ["Mixed committee model builds cohesion."],
    }
    script = (
        f"{esc}\n{fn}\n"
        f"process.stdout.write(renderClimateReflections({json.dumps(lens)}));"
    )
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "Sensitivity evidence" in out.stdout
    assert "Responsiveness evidence" in out.stdout
    assert "seasonal flooding risk" in out.stdout
    assert "reflection-evidence" in out.stdout
    # Empty evidence arrays → no evidence blocks
    lens_no_ev = {
        "reflections": [{"question_key": "cq1_interaction", "title": "T",
                          "status_cue": "ok", "text": "Some text."}],
    }
    out_no = subprocess.run(
        ["node", "-e", f"{esc}\n{fn}\nprocess.stdout.write(renderClimateReflections({json.dumps(lens_no_ev)}));"],
        capture_output=True, text=True,
    )
    assert out_no.returncode == 0, out_no.stderr
    assert "reflection-evidence" not in out_no.stdout


def test_climate_readout_is_plain_language_narrative():
    html = INDEX.read_text(encoding="utf-8")
    esc = _extract_js_function(html, "esc")
    strip = _extract_js_function(html, "renderClimatePathwayStrip")
    inter = _extract_js_function(html, "renderClimateInteractions")
    div = _extract_js_function(html, "renderClimateDividendSynthesis")
    base = "\n".join([esc, strip, inter, div]) + "\n"
    lens = {
        "interaction_readout": [{
            "direction_id": "climate-fcv-on-project",
            "summary": "Flood risk disrupts delivery.",
            "pathways": [{
                "pressure": "Flooding", "mechanism": "cuts road access",
                "project_implication": "delays works",
                "design_response": "seasonal windows",
                "project_elements": ["landing sites"],
                "time_horizons": ["project-lifetime"],
            }],
        }],
        "readout_sections": [{"section_id": "invest-in", "items": [{
            "item_id": "livelihoods-opportunity", "status": "supported",
            "project_contribution": "Creates fisheries income.",
            "strengthening_action": "Add climate-smart species.",
            "evidence": ["x"],
        }]}],
        "additional_pathways": [],
    }
    script = (base + "process.stdout.write(renderClimateInteractions("
              + json.dumps(lens) + ")+'@@'+renderClimateDividendSynthesis("
              + json.dumps(lens) + ",[]));")
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    interactions, dividends = out.stdout.split("@@")
    assert "<strong>Flood risk disrupts delivery.</strong>" in interactions
    assert "How the design responds:" in interactions
    assert "leading to" not in interactions
    assert "Key locations and components:" in interactions
    assert "The current design already contributes" in dividends
    assert "<h4>" not in dividends
    assert "Creates fisheries income." in dividends


def test_climate_module_notice_flags_incomplete_readout():
    """The module notice must surface an honest partial notice when the
    dedicated readout (reflections + integration) could not be produced,
    rather than silently rendering an interactions-only hybrid."""
    source = INDEX.read_text(encoding="utf-8")
    names = [
        "climateMaterialityLevel", "climateReadoutComplete",
        "renderClimateModuleNotice",
    ]
    helpers = "\n".join(_extract_js_function(source, name) for name in names)
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{helpers}
const incomplete = {{
  materiality_level:'medium',
  materiality_summary:'Flood-conflict interaction is material.',
  interaction_readout:[{{direction_id:'climate-fcv-on-project',summary:'Delivery risk.'}}],
  reflections:[],
  integration_summary:''
}};
const complete = {{
  materiality_level:'medium',
  materiality_summary:'Flood-conflict interaction is material.',
  reflections:[{{question_key:'cq2_maladaptation',title:'Lock-in',status_cue:'partial gap',text:'Siting is engineering, not allocation.'}}],
  integration_summary:'Aware but allocation untreated.'
}};
const NOTICE = 'reflections and integration readout could not be generated';
const partial = renderClimateModuleNotice(incomplete,false);
if (!partial.includes(NOTICE)) throw new Error('incomplete readout missing partial notice | '+partial);
if (!partial.includes('climate-partial-notice')) throw new Error('partial notice class missing');
const full = renderClimateModuleNotice(complete,false);
if (full.includes(NOTICE)) throw new Error('complete readout must not show partial notice');
const errored = renderClimateModuleNotice(null,true);
if (errored.includes(NOTICE)) throw new Error('hard error path must use its own message, not the partial notice');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_priorities_intro_shows_soft_notice_when_links_unvalidated():
    source = INDEX.read_text(encoding="utf-8")
    assert "climatePriorityUnlinked" in source
    assert "provenance could not be validated" in source


def test_priority_navigation_is_explicit_and_keyboard_operable():
    source = INDEX.read_text(encoding="utf-8")

    assert "priority-navigation-callout" not in source
    assert "Select each numbered priority" not in source
    assert "Priority overview" not in source
    assert "pov-sb" not in source
    intro = _extract_js_function(source, "renderPrioritiesIntro")
    assert "pi-lead" in intro
    assert "pi-list" not in intro
    assert "priority-navigation-callout" not in intro
    assert '<button type="button" class="ps-step' in source
    assert 'aria-pressed="${i===currentPriority?' in source
    assert "setAttribute('aria-pressed'" in source
    assert ".ps-step:focus-visible" in source


def test_reference_describes_current_compact_stage3_controls():
    reference = (INDEX.parent / "docs" / "reference" / "reference_frontend_functions.md").read_text(encoding="utf-8")
    for stale in (
        "re-enable Next",
        "pi-item",
        "pov-row",
        "fcv-resp-arc-fill",
        "fcv-resp-leaf-path",
        "fcv-resp-rating-label",
        "fcv-resp-need-label",
    ):
        assert stale not in reference
    for current in (
        "stage3-rating-rail",
        "stage3-mobile-ratings",
        "sticky",
        "numbered `.ps-step` controls",
        "aria-pressed",
    ):
        assert current in reference


def test_stage3_overview_has_textual_slim_bar_ratings_for_normal_and_climate_modes():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "stage3OverviewHtml")
    script = f"""
let climateMode = false;
const isClimateLensActive = () => climateMode;
{helper}
const normal = stage3OverviewHtml();
const assertUniqueIds = (html,label) => {{
  const ids = [...html.matchAll(/\\sid="([^"]+)"/g)].map(match => match[1]);
  if (new Set(ids).size !== ids.length) throw new Error(label+' contains duplicate IDs: '+ids.join(','));
}};
assertUniqueIds(normal,'normal rating rail');
if (!normal.includes('<aside class="stage3-rating-rail"')) throw new Error('missing desktop rail');
if (!normal.includes('<details class="stage3-mobile-ratings"')) throw new Error('missing mobile disclosure');
if ((normal.match(/data-rating-key="sensitivity"/g)||[]).length !== 2) throw new Error('sensitivity should render in both modes');
if ((normal.match(/data-rating-key="responsiveness"/g)||[]).length !== 2) throw new Error('responsiveness should render in both modes');
if ((normal.match(/class="stage3-rating-bar"/g)||[]).length !== 4) throw new Error('missing slim bars');
if ((normal.match(/aria-valuemax="100"/g)||[]).length !== 4) throw new Error('normal bars must use percentage max');
if (!normal.includes('Is the project aware of and designed for the FCV context?')) throw new Error('sensitivity meaning is not textual');
if (!normal.includes('Does the project actively work to change the FCV situation?')) throw new Error('responsiveness meaning is not textual');
if (normal.includes('<svg')) throw new Error('normal ratings still render a gauge SVG');

climateMode = true;
const climate = stage3OverviewHtml();
assertUniqueIds(climate,'climate rating rail');
if ((climate.match(/data-rating-key="climate-integration"/g)||[]).length !== 2) throw new Error('climate integration should render in both modes');
if ((climate.match(/aria-valuemax="100"/g)||[]).length !== 2) throw new Error('climate bars must use percentage max');
if (climate.includes('data-rating-key="sensitivity"') || climate.includes('data-rating-key="responsiveness"')) throw new Error('climate lens should use one integration rating');
if (climate.includes('<svg')) throw new Error('climate rating still renders a gauge SVG');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_rating_rail_updates_state_and_preserves_legacy_color_mappings():
    source = INDEX.read_text(encoding="utf-8")
    updater = _extract_js_function(source, "updateSidebar")
    script = f"""
let climateMode = false;
let fcvRating = 'Adequate';
let fcvResponsivenessRating = 'Adequate';
let climateIntegration = null;
const LEVELS = ['Extremely Low','Very Low','Low','Adequate','Well Embedded','Very Well Embedded'];
const LEVEL_COLORS = {{1:'#C0392B',2:'#E07B00',3:'#D97706',4:'#0072BB',5:'#1A7A4A',6:'#0d5c36'}};
const RESP_LEVEL_COLORS = {{1:'#C0392B',2:'#E07B00',3:'#D97706',4:'#E07B00',5:'#1A7A4A',6:'#0d5c36'}};
const NEED_LABELS = {{Adequate:'Targeted enhancements possible'}};
const CLIMATE_RATING_ORDER = ['Extremely Low','Very Low','Low','Adequate','Well Embedded','Very Well Embedded'];
const isClimateLensActive = () => climateMode;
const climateIntegrationShortLabel = () => 'Legacy climate integration meaning';
const climateIntegrationRatingFraction = () => 0;
const integrationGaugeFraction = level => level === 'partly_integrated' ? 0.66 : 0;
const makeCard = () => {{
  const value = {{dataset:{{}}, textContent:''}};
  const meaning = {{textContent:''}};
  const fill = {{style:{{}}}};
  const bar = {{attrs:{{}}, setAttribute(name,val){{ this.attrs[name] = String(val); }}}};
  return {{value,meaning,fill,bar,querySelector(selector){{
    if (selector === '[data-rating-value]') return value;
    if (selector === '[data-rating-meaning]') return meaning;
    if (selector === '[data-rating-fill]') return fill;
    if (selector === '.stage3-rating-bar') return bar;
    return null;
  }}}};
}};
const cards = {{
  sensitivity:[makeCard()], responsiveness:[makeCard()], 'climate-integration':[makeCard()]
}};
const document = {{
  querySelectorAll(selector) {{
    if (selector.includes('sensitivity')) return cards.sensitivity;
    if (selector.includes('responsiveness')) return cards.responsiveness;
    if (selector.includes('climate-integration')) return cards['climate-integration'];
    return [];
  }}
}};
{updater}
updateSidebar();
const responsiveness = cards.responsiveness[0];
if (responsiveness.value.dataset.ratingState !== 'ready') throw new Error('normal rating state not marked ready');
if (responsiveness.fill.style.backgroundColor !== '#E07B00') throw new Error('Adequate responsiveness lost orange color');
if (responsiveness.bar.attrs['aria-valuenow'] !== '67') throw new Error('normal rating progress not updated');
if (parseFloat(responsiveness.fill.style.width) < 66) throw new Error('normal rating bar width not updated');
climateMode = true;
climateIntegration = {{level:'partly_integrated'}};
updateSidebar();
const legacy = cards['climate-integration'][0];
if (legacy.value.dataset.ratingState !== 'ready') throw new Error('legacy climate state not marked ready');
if (legacy.fill.style.backgroundColor !== '#009FDA') throw new Error('partly integrated legacy color lost');
if (legacy.bar.attrs['aria-valuenow'] !== '66') throw new Error('legacy climate progress not updated');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_verified_reader_visual_refresh_preserves_depth_and_orders_sections():
    source = INDEX.read_text(encoding="utf-8")
    renderer = _extract_js_function(source, "renderClimateVerifiedAssessment")
    url_helper = _extract_js_function(source, "isPublicWorldBankHttpsUrl")
    reader = {
        "operation_context": {
            "document_type": "Program Paper", "instrument_type": "PforR",
            "country_scope": "single", "is_mpa": False,
            "preparation_regime": "new_model", "processing_model": "two_step",
            "es_regime": "INSTRUMENT_SPECIFIC", "warning_codes": [],
        },
        "evidence_status": "preview; not approved",
        "executive_readout": (
            "The project needs climate-aware delivery rules. They should be agreed before appraisal.\n\n"
            "These rules can protect access during shocks. They also support fairer decisions."
        ),
        "climate_sensitivity_rating": {
            "question": "How climate-sensitive is this project?", "label": "Moderate", "level": 2,
            "tone": "mid", "scale": ["Limited", "Moderate", "Strong"],
            "description": "Climate and FCV factors need further design work.",
            "overview_summary": "The current design identifies risks but needs clearer operating rules.",
            "caveat": "This is an advisory assessment.",
        },
        "core_questions": [{
            "question": "How could flooding and insecurity affect delivery?",
            "source": "Climate-FCV guidance",
            "summary": "Flooding can close access routes during insecure periods.\n\nDelivery plans should account for seasonal constraints.",
            "watch": "Monitor whether seasonal access conditions change.",
        }, {
            "question": "Could benefit rules affect trust?",
            "source": "Peace dividends guidance",
            "summary": "BFMUs bring competing resource users into shared governance.",
            "watch": "Monitor whether excluded groups can influence decisions.",
        }, {
            "question": "Could natural-resource pressure intensify tension?",
            "source": "Defueling Conflict",
            "summary": "Scarcity can sharpen disputes around access and authority.",
            "watch": "Monitor whether local disputes change during dry seasons.",
        }],
        "priorities": [{
            "rank": 1, "title": "Set seasonal delivery rules",
            "narrative": (
                "Seasonal flooding and insecurity can disrupt works. The project needs agreed triggers for pausing and restarting activity.\n\n"
                "These triggers should be discussed with local delivery partners. They can reduce uneven access to project benefits."
            ),
            "current_document_drafting": {
                "target_document": "Project Appraisal Document", "target_section": "Implementation arrangements",
                "text": "Include seasonal access triggers in the implementation arrangements.",
            },
            "decision": "Agree the trigger approach before appraisal.",
            "minimum_action": "Define the operational thresholds with delivery partners.",
            "responsible_function": "Task Team Leader and implementing agency.",
            "completion_evidence": "Approved seasonal delivery protocol.",
        }, {
            "rank": 2, "title": "Strengthen shared resource governance",
            "narrative": "BFMUs bring competing resource users into shared governance.",
            "decision": "Confirm representation and dispute-resolution rules.",
            "minimum_action": "Agree transparent membership and escalation rules.",
        }, {
            "rank": 3, "title": "Sequence restoration with access agreements",
            "narrative": "Restoration changes access to contested resources and therefore needs locally legitimate sequencing.",
            "decision": "Sequence works after access agreements are documented.",
            "minimum_action": "Record locally agreed access conditions.",
        }, {
            "rank": 4, "title": "Prepare for changing delivery conditions",
            "narrative": "Complete drafting paragraph for priority four.",
            "decision": "Review triggers at each implementation checkpoint.",
            "minimum_action": "Assign a named owner for trigger reviews.",
            "current_document_drafting": {
                "target_document": "Project Appraisal Document",
                "target_section": "Implementation arrangements",
                "text": "Retain the complete priority-four drafting language.",
            },
        }],
        "minor_climate_points": [{
            "point": "Check local communication channels", "why": "Seasonal users may not receive timely updates.",
            "how_to_check": "Confirm channels with community representatives.",
        }, {
            "point": "Confirm dry-season access", "why": "Access constraints may change who benefits.",
            "how_to_check": "Check access assumptions with mobile groups.",
        }],
        "review_readiness_flags": [{
            "flag": "Confirm the works calendar", "why_it_matters": "The current calendar does not show seasonal constraints.",
            "suggested_verification": "Confirm the calendar before the decision meeting.",
        }, {
            "flag": "Confirm grievance escalation", "why_it_matters": "Escalation roles are not yet explicit.",
            "suggested_verification": "Name the responsible function before appraisal.",
        }],
        "evidence_trail": {
            "methodology_note": "The analysis used project evidence and the country bank.",
            "pathways": [{"direction_label": "Climate and FCV on project", "chain_prose": "Flooding and insecurity reduce access."}],
            "limitations": "The uploaded concept note does not yet include final implementation protocols.",
            "evidence_key": [{"id": "PF-01", "type_label": "Project fact", "text": "Old technical code."}],
            "diagnostics": {"candidate_count": 4, "admitted_count": 4, "final_count": 4},
        },
        "sources": [{
            "title": "Climate-FCV guidance", "url": "https://documents.worldbank.org/climate-fcv",
            "description": "Core climate and fragility guidance.",
        }],
        "advisory_notice": "Use this assessment alongside specialist judgement.",
    }
    script = f"""
{_js_escape_helper()}
const renderClimateRelevantGuidance = () => '';
{url_helper}
{renderer}
const html = renderClimateVerifiedAssessment({json.dumps(reader)});
if (!html.includes('How this operation was routed') || !html.includes('Program Paper') || !html.includes('PforR')) {{
  throw new Error('operational routing context missing | ' + html);
}}
const orderedSections = [
  'Overview', 'Core climate-FCV questions', 'Ranked operational priorities',
  'Points to check before the decision meeting', 'What to keep an eye on'
];
let previous = -1;
for (const section of orderedSections) {{
  const current = html.indexOf(section);
  if (current === -1 || current <= previous) {{
    throw new Error('section hierarchy is missing or out of order: ' + section + ' | ' + html);
  }}
  previous = current;
}}
const minorIndex = html.indexOf('Smaller climate and fragility points to consider');
const documentIndex = html.indexOf('Document points to confirm');
if (minorIndex < 0 || documentIndex < 0 || minorIndex >= documentIndex) {{
  throw new Error('smaller climate points must appear before document points | ' + html);
}}
for (const expected of [
  'Seasonal flooding and insecurity can disrupt works. The project needs agreed triggers for pausing and restarting activity.',
  'These triggers should be discussed with local delivery partners. They can reduce uneven access to project benefits.',
  'Include seasonal access triggers in the implementation arrangements.',
  'Recommendation details', '<article class="climate-verified-assessment">',
  '<section class="climate-report-section', '<header class="climate-section-heading">',
  '<details class="climate-priority-detail">',
  'Complete drafting paragraph for priority four.',
  'Retain the complete priority-four drafting language.',
  'identifies 4 main operational priorities',
  'Method, limitations, and sources',
  'The uploaded concept note does not yet include final implementation protocols.',
  'Sources &amp; further reading',
  'Candidate country evidence: preview; not approved.'
]) {{
  if (!html.includes(expected)) throw new Error('missing preserved reader detail: ' + expected + ' | ' + html);
}}
if (!html.includes('class="climate-sens-rating climate-overview-panel"')) {{
  throw new Error('overview panel missing | ' + html);
}}
if ((html.match(/climate-overview-panel/g)||[]).length !== 1) {{
  throw new Error('overview must use one restrained panel | ' + html);
}}
if ((html.match(/<details class="climate-priority-card"/g)||[]).length !== 4) {{
  throw new Error('all priorities must be native disclosures | ' + html);
}}
if ((html.match(/<details class="climate-priority-card" open/g)||[]).length !== 1) {{
  throw new Error('only priority one should be open | ' + html);
}}
if ((html.match(/class="climate-item-number"/g)||[]).length < 7) {{
  throw new Error('checks and watch items must be visibly numbered | ' + html);
}}
for (const removed of ['Evidence status:', 'Evidence key', 'Run diagnostics', 'final operational priorities are presented:']) {{
  if (html.includes(removed)) throw new Error('reader clutter remains: ' + removed + ' | ' + html);
}}
const headingPattern = new RegExp('<header class="climate-section-heading"><span class="climate-section-number">([0-9]{{2}})</span><h2>([^<]+)</h2></header>', 'g');
const headings = Array.from(html.matchAll(headingPattern), match => [match[1], match[2]]);
const expectedHeadings = [
  ['01', 'Overview'],
  ['02', 'Core climate-FCV questions'],
  ['03', 'Ranked operational priorities'],
  ['04', 'Points to check before the decision meeting'],
  ['05', 'What to keep an eye on'],
  ['06', 'How this analysis was produced']
];
if (JSON.stringify(headings) !== JSON.stringify(expectedHeadings)) {{
  throw new Error('numbered section sequence is not gap-free: ' + JSON.stringify(headings) + ' | ' + html);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_verified_reader_fallback_numbers_methodology_last_without_unsafe_values():
    source = INDEX.read_text(encoding="utf-8")
    renderer = _extract_js_function(source, "renderClimateVerifiedAssessment")
    reader = {
        "executive_readout": "The project needs a bounded climate-FCV review.",
        "evidence_trail": {
            "methodology_note": "The analysis used project evidence and the country bank."
        },
    }
    script = f"""
{_js_escape_helper()}
const renderClimateRelevantGuidance = () => '';
{renderer}
const html = renderClimateVerifiedAssessment({json.dumps(reader)});
for (const expected of [
  'The project needs a bounded climate-FCV review.',
  'Method, limitations, and sources'
]) {{
  if (!html.includes(expected)) throw new Error('missing fallback content: ' + expected + ' | ' + html);
}}
for (const unsafe of ['undefined', '[object Object]']) {{
  if (html.includes(unsafe)) throw new Error('unsafe rendered value: ' + unsafe + ' | ' + html);
}}
if (html.includes('Points to check before the decision meeting')) {{
  throw new Error('empty points section should be suppressed | ' + html);
}}
const headingPattern = new RegExp('<header class="climate-section-heading"><span class="climate-section-number">([0-9]{{2}})</span><h2>([^<]+)</h2></header>', 'g');
const headings = Array.from(html.matchAll(headingPattern), match => [match[1], match[2]]);
const expectedHeadings = [
  ['01', 'Overview'],
  ['02', 'Core climate-FCV questions'],
  ['03', 'Ranked operational priorities'],
  ['04', 'How this analysis was produced']
];
if (JSON.stringify(headings) !== JSON.stringify(expectedHeadings)) {{
  throw new Error('fallback section sequence is not gap-free or methodology is not final: ' + JSON.stringify(headings) + ' | ' + html);
}}
if (!html.includes('<details class="climate-fold"><summary>Method, limitations, and sources</summary>')) {{
  throw new Error('methodology disclosure summary repeats or omits its contents label | ' + html);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_public_world_bank_https_url_accepts_only_world_bank_hosts():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "isPublicWorldBankHttpsUrl")
    script = f"""
{helper}
const accepted = [
  'https://www.worldbank.org/report',
  'https://documents1.worldbank.org/report'
];
const rejected = [
  'http://www.worldbank.org/report',
  'https://',
  'https://localhost/report',
  'https://127.0.0.1/report',
  'https://[::1]/report',
  'https://user:pass@www.worldbank.org/report',
  'https://worldbank.org.evil.example/report',
  'https://.worldbank.org/report',
  'https://foo..worldbank.org/report',
  'https://-bad.worldbank.org/report',
  'https://bad-.worldbank.org/report',
  'https://bad_name.worldbank.org/report',
  'https://www.worldbank.org./report',
  'https://worldbank.org:443/report',
  'https://xn--bcher-kva.worldbank.org/report'
];
for (const url of accepted) {{
  if (!isPublicWorldBankHttpsUrl(url)) throw new Error('rejected valid World Bank URL: '+url);
}}
for (const url of rejected) {{
  if (isPublicWorldBankHttpsUrl(url)) throw new Error('accepted unsafe URL: '+url);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_verified_reader_guidance_prefers_canonical_project_specific_items():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "isPublicWorldBankHttpsUrl",
            "normalizeClimateSourceTitle",
            "buildClimateGuidanceItems",
            "renderClimateRelevantGuidance",
        )
    )
    reader = {
        "guidance_items": [{
            "title": "Defueling Conflict",
            "url": "https://documents.worldbank.org/defueling-conflict",
            "practical_value": "Use this source to assess natural-resource governance risks.",
            "project_use": "For this project, use it to test BFMU representation and dispute-resolution rules.",
        }],
        "core_questions": [{
            "source": "FCV-Sensitive Climate Action Framework",
            "summary": "This fallback content must not replace canonical guidance.",
        }],
        "sources": [{
            "title": "FCV-Sensitive Climate Action Framework",
            "url": "https://documents.worldbank.org/fcv-sensitive-framework",
            "description": "A framework for climate action in FCV settings.",
        }],
    }
    script = f"""
{_js_escape_helper()}
{helpers}
const reader = {json.dumps(reader)};
const html = renderClimateRelevantGuidance(reader);
for (const expected of [
  'Relevant WBG guidance for this project',
  'Defueling Conflict',
  'Use this source to assess natural-resource governance risks.',
  'For this project, use it to test BFMU representation and dispute-resolution rules.'
]) {{
  if (!html.includes(expected)) throw new Error('missing relevant guidance content: '+expected+' | '+html);
}}
for (const omitted of ['Most useful for following up on', 'FCV-Sensitive Climate Action Framework']) {{
  if (html.includes(omitted)) throw new Error('canonical guidance was not preferred: '+omitted+' | '+html);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_verified_reader_guidance_fallback_is_bounded_and_project_specific():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "isPublicWorldBankHttpsUrl",
            "normalizeClimateSourceTitle",
            "buildClimateGuidanceItems",
            "renderClimateRelevantGuidance",
        )
    )
    reader = {
        "core_questions": [
            {"source": "Source A", "question": "Can representation remain inclusive?", "watch": "Check representation before appraisal."},
            {"source": "Source A", "question": "Can access agreements reduce disputes?"},
            {"source": "Source B", "question": "Can seasonal triggers protect continuity?"},
            {"source": "Source C", "question": "Can transparent benefit rules support trust?"},
            {"source": "Source D", "question": "Can monitoring identify changing tensions?"},
            {"source": "Source E", "question": "Must this fifth source be capped?"},
            {"source": "Unsafe source", "question": "Must this remain excluded?"},
        ],
        "sources": [
            {"title": f"Source {label}", "url": f"https://documents.worldbank.org/{label.lower()}", "practical_value": f"Practical value {label}."}
            for label in "ABCDE"
        ] + [{"title": "Unsafe source", "url": "https://worldbank.org.evil.example/report", "description": "Unsafe."}],
    }
    script = f"""
{_js_escape_helper()}
{helpers}
const reader = {json.dumps(reader)};
const items = buildClimateGuidanceItems(reader);
if (items.length !== 4) throw new Error('fallback must cap at four | '+JSON.stringify(items));
if (items[0].title !== 'Source A') throw new Error('fallback ranking is not deterministic | '+JSON.stringify(items));
if (items[0].project_use !== 'For this project, use the source to address this follow-up: Check representation before appraisal.') throw new Error('watch follow-up mismatch | '+JSON.stringify(items));
const html = renderClimateRelevantGuidance(reader);
for (const expected of ['Practical value A.', 'For this project,', 'Check representation before appraisal.']) {{
  if (!html.includes(expected)) throw new Error('fallback prose missing: '+expected+' | '+html);
}}
for (const omitted of ['Source E', 'Unsafe source', 'Most useful for following up on']) {{
  if (html.includes(omitted)) throw new Error('fallback promoted excluded source: '+omitted+' | '+html);
}}
const watchOnly = buildClimateGuidanceItems({{
  core_questions:[{{source:'Watch source',watch:'Confirm local representation'}}],
  sources:[{{title:'Watch source',url:'https://documents.worldbank.org/watch',description:'Watch guidance.'}}]
}});
if (watchOnly[0].project_use !== 'For this project, use the source to address this follow-up: Confirm local representation.') {{
  throw new Error('watch-only fallback must remain grammatical | '+JSON.stringify(watchOnly));
}}
const empty = renderClimateRelevantGuidance({{core_questions:[],sources:reader.sources}});
if (empty !== '') throw new Error('guidance must be omitted without current question matches | '+empty);
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_verified_reader_balanced_styles_cover_mobile_print_and_accessibility():
    source = INDEX.read_text(encoding="utf-8")
    for expected in (
        ".climate-overview-panel{",
        ".climate-priority-card>summary{",
        ".climate-priority-card>summary:focus-visible{",
        ".climate-numbered-item{",
        "@media(max-width:760px)",
        "@media print",
        ".climate-priority-card:not([open])>.climate-priority-body",
        ".climate-priority-detail:not([open])>:not(summary)",
    ):
        assert expected in source



def test_print_expands_every_closed_reader_disclosure_with_its_content():
    source = INDEX.read_text(encoding="utf-8")
    renderer = _extract_js_function(source, "renderClimateVerifiedAssessment")
    script = f"""
{_js_escape_helper()}
const renderClimateRelevantGuidance = () => '';
{renderer}
const html = renderClimateVerifiedAssessment({{
  executive_readout:'Reader overview.',
  priorities:[
    {{rank:1,title:'First priority',narrative:'First narrative.',decision:'First decision.'}},
    {{rank:2,title:'Second priority',narrative:'Closed priority narrative.',decision:'Closed priority decision.'}}
  ],
  evidence_trail:{{
    methodology_note:'Closed method text.',
    limitations:'Closed limitations text.'
  }}
}});
for (const expected of [
  '<details class="climate-priority-card"><summary>',
  '<details class="climate-priority-detail"><summary>Recommendation details</summary>',
  '<details class="climate-fold"><summary>Method, limitations, and sources</summary>',
  'Closed priority narrative.', 'Closed priority decision.',
  'Closed method text.', 'Closed limitations text.'
]) {{
  if (!html.includes(expected)) throw new Error('closed disclosure/content missing: '+expected+' | '+html);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr

    print_block = source[source.index("@media print{"):source.index("\n\n    /* Buttons */")]
    assert ".climate-priority-card:not([open])>.climate-priority-body" in print_block
    assert ".climate-priority-detail:not([open])>:not(summary)" in print_block
    assert ".climate-fold:not([open])>:not(summary)" in print_block


def test_priority_summary_contains_one_valid_heading_with_rank_inside():
    source = INDEX.read_text(encoding="utf-8")
    renderer = _extract_js_function(source, "renderClimateVerifiedAssessment")
    script = f"""
{_js_escape_helper()}
const renderClimateRelevantGuidance = () => '';
{renderer}
const html = renderClimateVerifiedAssessment({{
  priorities:[{{rank:1,title:'Accessible priority',narrative:'Full priority prose.'}}]
}});
if (!html.includes('<summary><h3 class="pc-title"><span class="pc-rank">1</span><span class="pc-title-text">Accessible priority</span></h3></summary>')) {{
  throw new Error('priority summary does not use one valid heading with rank inside | '+html);
}}
if (html.includes('</span><h3 class="pc-title">')) {{
  throw new Error('rank remains a sibling of the summary heading | '+html);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr



def test_fallback_question_id_dedup_matches_canonical_ranking():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "isPublicWorldBankHttpsUrl",
            "normalizeClimateSourceTitle",
            "buildClimateGuidanceItems",
        )
    )
    script = f"""
{helpers}
const items=buildClimateGuidanceItems({{
  core_questions:[
    {{question_id:' Q-01 ',source:'Source A',watch:'First rendering.'}},
    {{question_id:'q-01',source:'Source A',watch:'Changed duplicate rendering.'}},
    {{question_id:'Q-02',source:'Source B',question:'Distinct B one?'}},
    {{question_id:'Q-03',source:'Source B',question:'Distinct B two?'}}
  ],
  sources:[
    {{title:'Source A',url:'https://documents.worldbank.org/a',description:'A value.'}},
    {{title:'Source B',url:'https://documents.worldbank.org/b',description:'B value.'}}
  ]
}});
if (items.map(item=>item.title).join(',') !== 'Source B,Source A') {{
  throw new Error('question_id duplicates inflated fallback ranking | '+JSON.stringify(items));
}}
if (items[1].project_use.includes('Changed duplicate rendering.')) {{
  throw new Error('later rendering of the same question_id was not removed | '+JSON.stringify(items));
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_fallback_content_dedup_and_summary_only_ranking_match_canonical():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "isPublicWorldBankHttpsUrl",
            "normalizeClimateSourceTitle",
            "buildClimateGuidanceItems",
        )
    )
    script = f"""
{helpers}
const items=buildClimateGuidanceItems({{
  core_questions:[
    {{source:'Source A',summary:'Same summary',question:'First rendering?',watch:'Same watch.'}},
    {{source:'Source A',summary:'Same summary',question:'Second rendering?',watch:'Same watch.'}},
    {{source:'Source B',summary:'Usable row',question:'Usable question?'}},
    {{source:'Source B',summary:'Summary-only ranking row'}}
  ],
  sources:[
    {{title:'Source A',url:'https://documents.worldbank.org/a',description:'A value.'}},
    {{title:'Source B',url:'https://documents.worldbank.org/b',description:'B value.'}}
  ]
}});
if (items.map(item=>item.title).join(',') !== 'Source B,Source A') {{
  throw new Error('content fallback ranking diverges from canonical | '+JSON.stringify(items));
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_fallback_sentence_completion_handles_closing_quotes_and_brackets():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "isPublicWorldBankHttpsUrl",
            "normalizeClimateSourceTitle",
            "buildClimateGuidanceItems",
        )
    )
    cases = [
        {
            "title": "Curly quote",
            "core_question": {"watch": "The project is \u201chigh risk.\u201d"},
            "expected": "For this project, use the source to address this follow-up: The project is \u201chigh risk.\u201d",
        },
        {
            "title": "Closing bracket",
            "core_question": {"question": "Can the team verify this?]"},
            "expected": "For this project, use the source to examine this question: Can the team verify this?]",
        },
        {
            "title": "Straight double quote",
            "core_question": {"watch": 'The project is "high risk."'},
            "expected": 'For this project, use the source to address this follow-up: The project is "high risk."',
        },
        {
            "title": "Straight apostrophe",
            "core_question": {"watch": "The project is 'high risk.'"},
            "expected": "For this project, use the source to address this follow-up: The project is 'high risk.'",
        },
        {
            "title": "Closing brace",
            "core_question": {"question": "Can the team verify this?}"},
            "expected": "For this project, use the source to examine this question: Can the team verify this?}",
        },
    ]
    script = f"""
{helpers}
const cases={json.dumps(cases)};
for (const testCase of cases) {{
  const items=buildClimateGuidanceItems({{
    core_questions:[{{source:testCase.title,...testCase.core_question}}],
    sources:[{{title:testCase.title,url:'https://documents.worldbank.org/punctuation',description:'Punctuation value.'}}]
  }});
  const actual=items[0]?.project_use;
  if (actual !== testCase.expected) {{
    throw new Error(`sentence completion mismatch for ${{testCase.title}} | expected=${{testCase.expected}} | actual=${{actual}}`);
  }}
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_canonical_guidance_deduplicates_titles_and_skips_empty_cards():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "isPublicWorldBankHttpsUrl",
            "normalizeClimateSourceTitle",
            "buildClimateGuidanceItems",
            "renderClimateRelevantGuidance",
        )
    )
    reader = {
      'guidance_items':[
        {'title':'Defueling & Conflict','url':'https://documents.worldbank.org/first','practical_value':'First practical value.','project_use':'First project use.'},
        {'title':'Defueling and Conflict','url':'https://documents.worldbank.org/duplicate','practical_value':'Duplicate practical value.','project_use':'Duplicate project use.'},
        {'title':'   ','url':'https://documents.worldbank.org/blank','practical_value':'No meaningful title.','project_use':'Should not render.'},
        {'title':'Empty prose','url':'https://documents.worldbank.org/empty','practical_value':'','project_use':''},
        {'title':'One useful field','url':'https://documents.worldbank.org/one','practical_value':'Useful practical value.','project_use':''}
      ]
    }
    script = f"""
{_js_escape_helper()}
{helpers}
const html=renderClimateRelevantGuidance({json.dumps(reader)});
if ((html.match(/Defueling &amp; Conflict/g)||[]).length !== 1) throw new Error('canonical title not rendered once | '+html);
for (const omitted of ['Defueling and Conflict','Duplicate practical value.','No meaningful title.','Empty prose']) {{
  if (html.includes(omitted)) throw new Error('invalid or duplicate canonical card rendered: '+omitted+' | '+html);
}}
for (const expected of ['First practical value.','First project use.','One useful field','Useful practical value.']) {{
  if (!html.includes(expected)) throw new Error('valid canonical content omitted: '+expected+' | '+html);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr



def test_zero_priority_reader_is_neutral_and_hides_diagnostic_verdicts():
    source = INDEX.read_text(encoding="utf-8")
    renderer = _extract_js_function(source, "renderClimateVerifiedAssessment")
    script = f"""
{_js_escape_helper()}
const renderClimateRelevantGuidance = () => '';
{renderer}
const html=renderClimateVerifiedAssessment({{
  priorities:[],
  technical_annex:{{recommendation_admitted_count:3,semantic_reviewer_verdict:'block'}}
}});
if (!html.includes('No operational priorities were identified in this assessment. Review the core questions and points to check below.')) {{
  throw new Error('neutral zero-priority message missing | '+html);
}}
for (const diagnostic of ['3 recommendation','candidate','held back','block','outcome:']) {{
  if (html.includes(diagnostic)) throw new Error('zero-priority diagnostics leaked: '+diagnostic+' | '+html);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr



def test_chromium_print_opens_exported_disclosures_and_restores_screen_state():
    from playwright.sync_api import sync_playwright

    source = INDEX.read_text(encoding="utf-8")
    renderer = _extract_js_function(source, "renderClimateVerifiedAssessment")
    url_helper = _extract_js_function(source, "isPublicWorldBankHttpsUrl")
    body_script = f"""
{_js_escape_helper()}
const renderClimateRelevantGuidance = () => '';
{url_helper}
{renderer}
console.log(renderClimateVerifiedAssessment({{
  executive_readout:'Print lifecycle overview.',
  priorities:[
    {{rank:1,title:'Open priority',narrative:'Open priority prose.',decision:'Open decision.'}},
    {{rank:2,title:'Closed priority',narrative:'Closed priority prose.',decision:'Closed decision.'}}
  ],
  evidence_trail:{{
    methodology_note:'Method text for print.',
    limitations:'Limitations text for print.'
  }},
  sources:[{{title:'Source text for print',url:'https://documents.worldbank.org/print-source',description:'Source description for print.'}}]
}}));
"""
    body_result = subprocess.run(
        ["node", "-e", body_script], capture_output=True, text=True, check=False
    )
    assert body_result.returncode == 0, body_result.stderr

    try:
        handler = _extract_js_function(source, "installClimatePrintDisclosureHandler")
        script_builder = _extract_js_function(source, "climatePrintDisclosureScript")
    except AssertionError:
        handler_script = ""
    else:
        script_result = subprocess.run(
            ["node", "-e", f"{handler}\n{script_builder}\nconsole.log(climatePrintDisclosureScript());"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert script_result.returncode == 0, script_result.stderr
        handler_script = script_result.stdout

    css = "\n".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", source))
    exported_html = (
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
        + css
        + "</style></head><body>"
        + body_result.stdout
        + '<details class="climate-guidance-disclosure"><summary>Closed guidance follow-up</summary><div>Closed guidance text for print.</div></details>'
        + '<details class="climate-guidance-disclosure" open><summary>Pre-opened guidance follow-up</summary><div>Pre-opened guidance text for print.</div></details>'
        + handler_script
        + "</body></html>"
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(exported_html, wait_until="load")
        details = page.locator("details.climate-priority-card, details.climate-priority-detail, details.climate-fold, details.climate-guidance-disclosure")
        prior_states = details.evaluate_all("elements => elements.map(element => element.open)")
        assert prior_states == [True, False, False, False, False, False, True]
        assert page.get_by_text("Open priority prose.").is_visible()
        assert not page.get_by_text("Closed priority prose.").is_visible()
        assert not page.get_by_text("Method text for print.").is_visible()
        assert not page.get_by_text("Limitations text for print.").is_visible()
        assert not page.get_by_text("Source text for print").is_visible()
        assert not page.get_by_text("Closed guidance text for print.").is_visible()
        assert page.get_by_text("Pre-opened guidance text for print.").is_visible()

        page.emulate_media(media="print")
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        assert details.evaluate_all("elements => elements.every(element => element.open)")
        assert page.get_by_text("Closed priority prose.").is_visible()
        assert page.get_by_text("Closed decision.").is_visible()
        assert page.get_by_text("Method text for print.").is_visible()
        assert page.get_by_text("Limitations text for print.").is_visible()
        assert page.get_by_text("Source text for print").is_visible()
        assert page.get_by_text("Closed guidance text for print.").is_visible()
        assert page.get_by_text("Pre-opened guidance text for print.").is_visible()

        page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        page.emulate_media(media="screen")
        assert details.evaluate_all("elements => elements.map(element => element.open)") == prior_states
        assert page.get_by_text("Open priority prose.").is_visible()
        assert not page.get_by_text("Closed priority prose.").is_visible()
        assert not page.get_by_text("Method text for print.").is_visible()
        assert not page.get_by_text("Closed guidance text for print.").is_visible()
        assert page.get_by_text("Pre-opened guidance text for print.").is_visible()
        browser.close()

    download_helper = _extract_js_function(source, "downloadHTML")
    assert "climatePrintDisclosureScript()" in download_helper


def test_relevant_guidance_uses_one_closed_native_disclosure():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "isPublicWorldBankHttpsUrl",
            "normalizeClimateSourceTitle",
            "buildClimateGuidanceItems",
            "renderClimateRelevantGuidance",
        )
    )
    reader = {
        "guidance_items": [{
            "title": "Defueling Conflict",
            "url": "https://documents.worldbank.org/defueling",
            "practical_value": "Use this source to examine natural-resource governance.",
            "project_use": "For this project, use it to check BFMU access rules.",
        }],
    }
    script = f"""
{_js_escape_helper()}
{helpers}
const html=renderClimateRelevantGuidance({json.dumps(reader)});
if ((html.match(/<details class="climate-guidance-disclosure">/g)||[]).length !== 1) {{
  throw new Error('guidance must use one closed disclosure | '+html);
}}
if (html.includes('<details class="climate-guidance-disclosure" open>')) {{
  throw new Error('guidance disclosure must be closed initially | '+html);
}}
if (!html.includes('<summary>Where the team can go for more detailed follow-up</summary>')) {{
  throw new Error('guidance summary is missing | '+html);
}}
if (!html.includes('<article class="climate-guidance-item"><h3>')) {{
  throw new Error('guidance source must continue the section heading hierarchy | '+html);
}}
const body=html.split('<summary>')[1];
if ((body.match(/<details/g)||[]).length !== 0) {{
  throw new Error('individual sources must not become nested disclosures | '+html);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_guidance_fallback_uses_short_verified_follow_up_not_summary_copy():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "isPublicWorldBankHttpsUrl",
            "normalizeClimateSourceTitle",
            "buildClimateGuidanceItems",
        )
    )
    reader = {
        "core_questions": [{
            "source": "FCV-Sensitive Climate Action Framework",
            "question": "Can delivery remain workable during floods?",
            "summary": "This long assessment paragraph must not be copied into guidance.",
            "watch": "Confirm U.N. access at Pariang, e.g. during flood closures",
        }],
        "sources": [{
            "title": "FCV-Sensitive Climate Action Framework",
            "url": "https://documents.worldbank.org/framework",
            "practical_value": "Use this source to stress-test delivery.",
        }],
    }
    script = f"""
{helpers}
const items=buildClimateGuidanceItems({json.dumps(reader)});
const expected='For this project, use the source to address this follow-up: Confirm U.N. access at Pariang, e.g. during flood closures.';
if (items.length !== 1 || items[0].project_use !== expected) {{
  throw new Error('short project follow-up mismatch | '+JSON.stringify(items));
}}
if (JSON.stringify(items).includes('long assessment paragraph')) {{
  throw new Error('full assessment summary leaked into guidance | '+JSON.stringify(items));
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_print_handler_includes_guidance_disclosure_state():
    source = INDEX.read_text(encoding="utf-8")
    handler = _extract_js_function(source, "installClimatePrintDisclosureHandler")

    assert "details.climate-guidance-disclosure" in handler

def test_detailed_priority_project_cycle_uses_one_escaped_canonical_renderer():
    source = INDEX.read_text(encoding="utf-8")
    renderer = _extract_js_function(source, "renderPriorityProjectCycle")
    live_helper = _extract_js_function(source, "showPriority")
    export_helper = _extract_js_function(source, "_buildExportPriorityCard")

    assert "renderPriorityProjectCycle(pr)" in live_helper
    assert "renderPriorityProjectCycle(pr)" in export_helper
    assert "priority.concise" not in live_helper
    assert "priority.concise" not in export_helper

    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{renderer}
const html = renderPriorityProjectCycle({{
  project_cycle: {{
    primary_label: 'Before <appraisal>',
    primary_text: 'Confirm & sequence the design.',
    secondary_label: 'At "implementation"',
    secondary_text: "Track the team\'s response."
  }},
  concise: {{ project_cycle: {{ primary_label: 'Legacy', primary_text: 'Do not use.' }} }}
}});
for (const expected of [
  'Where this fits in the project cycle',
  'Before &lt;appraisal&gt;',
  'Confirm &amp; sequence the design.',
  'At &quot;implementation&quot;',
  'Track the team&#039;s response.'
]) {{
  if (!html.includes(expected)) throw new Error('missing '+expected+' | '+html);
}}
const primaryOnly = renderPriorityProjectCycle({{
  project_cycle: {{ primary_label:'Before appraisal', primary_text:'Use the current note.' }}
}});
if (primaryOnly.includes('Next step') || primaryOnly.includes('Legacy')) throw new Error('secondary fallback leaked');
if (renderPriorityProjectCycle({{ concise: {{ project_cycle: {{ primary_label:'Legacy', primary_text:'Do not use.' }} }} }}) !== '') {{
  throw new Error('legacy concise cycle was rendered');
}}
if (renderPriorityProjectCycle({{ project_cycle: {{ primary_label:'Only label', primary_text:'' }} }}) !== '') {{
  throw new Error('invalid canonical cycle was rendered');
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr

def test_detailed_project_cycle_integrated_renderers_align_order_and_scope():
    source = INDEX.read_text(encoding="utf-8")
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "md",
            "renderPriorityProjectCycle",
            "_buildExportPriorityCard",
            "showPriority",
        )
    )
    priority = {
        "title": "Strengthen delivery sequencing",
        "dimension": "Contextual",
        "fcv_dimension": "Contextual",
        "risk_level": "High",
        "actions": [{
            "document_element": "Implementation arrangements",
            "guidance": "Action body",
            "suggested_language": "Draft action text",
        }],
        "implementation_note": "Implementation body",
        "project_cycle": {
            "primary_label": "Before appraisal",
            "primary_text": "Confirm the decision sequence.",
            "secondary_label": "During implementation",
            "secondary_text": "Track the agreed sequence.",
        },
        "concise": {
            "project_cycle": {
                "primary_label": "Legacy concise milestone",
                "primary_text": "Legacy concise text must not leak.",
            }
        },
    }
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
const renderSRTagBadge = () => '';
const renderPriorityClimateContribution = () => '';
const renderPriorityCompliance = () => '<div class="pc-compliance"><span>Compliance text</span></div>';
const isClimateLensActive = () => false;
const lensDisplayName = value => value;
const shiftTooltips = {{}};
let stageThreePriorities = [{json.dumps(priority)}];
let stage3View = 'detailed';
let currentPriority = 0;
const supportsAnyStage3Summary = () => false;
const toggleSummaryPriority = () => {{}};
const updateSidebar = () => {{}};
const localStorage = {{getItem: () => null, setItem: () => {{}}}};
const cardArea = {{innerHTML:'', scrollIntoView:() => {{}}}};
const document = {{getElementById: id => id === 'priority-card-area' ? cardArea : null}};
{helpers}
function parentClasses(html, className) {{
  const stack=[];
  const parents=[];
  const tags=/<\\/?([A-Za-z0-9]+)([^>]*)>/g;
  let match;
  while ((match=tags.exec(html))) {{
    const raw=match[0], name=match[1], attrs=match[2]||'';
    if (raw.startsWith('</')) {{
      for (let i=stack.length-1;i>=0;i--) {{
        if (stack[i].name===name) {{ stack.splice(i,1); break; }}
      }}
      continue;
    }}
    if (attrs.includes('class="'+className+'"')) parents.push(stack.map(item=>item.attrs));
    if (/\\/\\s*>$/.test(raw) || ['meta','img','br','input','path','circle','line','polyline','polygon'].includes(name)) continue;
    stack.push({{name,attrs}});
  }}
  return parents;
}}
function checkOutput(name, html) {{
  if ((html.match(/class="priority-project-cycle"/g)||[]).length !== 1) throw new Error(name+' lifecycle count');
  const order=['Action body','Where this fits in the project cycle','Compliance text'];
  const positions=order.map(value=>html.indexOf(value));
  if (positions.some(value=>value<0) || positions.some((value,index)=>index>0&&value<=positions[index-1])) throw new Error(name+' lifecycle order '+positions);
  if (html.includes('Legacy concise')) throw new Error(name+' leaked legacy concise cycle');
  const parents=parentClasses(html,'priority-project-cycle');
  if (parents.length!==1 || parents[0].some(attrs=>attrs.includes('pc-zone zone-act'))) throw new Error(name+' lifecycle nested in action zone');
}}
const exported = _buildExportPriorityCard(stageThreePriorities[0],0,1);
checkOutput('export',exported);
showPriority(0);
checkOutput('live',cardArea.innerHTML);
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_express_recovery_keeps_valid_detailed_output_when_summary_is_unavailable():
    source = INDEX.read_text(encoding="utf-8")
    recovery = source[source.index("const outputs="):source.index("// Partial state:")]
    assert "function isRestorableExpressStage3Output(" in source
    assert "const hasSavedStage3Output=" in recovery
    assert "if(hasSavedStage3Output&&isRestorableExpressStage3Output(outputs[3]))" in recovery
    assert recovery.index("if(hasSavedStage3Output&&isRestorableExpressStage3Output(outputs[3]))") < recovery.index("if(hasSavedStage3Output){localStorage.removeItem")
    restorable = _extract_js_function(source, "isRestorableExpressStage3Output")
    script = f"""
{restorable}
if (!isRestorableExpressStage3Output('Completed detailed output')) throw new Error('valid output rejected');
for (const invalid of ['', '   ', null, 42, {{result:'detailed'}}]) {{
  if (isRestorableExpressStage3Output(invalid)) throw new Error('invalid output accepted');
}}
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
