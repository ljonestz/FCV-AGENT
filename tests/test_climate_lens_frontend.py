"""Frontend contracts for optional Climate selection and diagnostic readouts."""

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
