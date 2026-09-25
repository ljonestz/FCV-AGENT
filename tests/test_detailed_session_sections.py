"""Frontend contracts for restoring the detailed Stage 3 sections."""

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


def _run_node(script: str) -> None:
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_stage3_structured_sections_restore_from_legacy_saved_history_json():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "restoreSavedStage3Sections")
    payload = {
        "risk_exposure": {
            "risks_to": "Flooding can interrupt access to clinics.",
            "risks_from": "Unequal targeting could deepen local grievance.",
        },
        "sensitivity_summary": "The design recognises access constraints.",
        "responsiveness_summary": "The design has limited entry points for resilience.",
    }
    state = {
        "version": 3,
        "history": [
            {"role": "assistant", "content": "Stage 2 output"},
            {
                "role": "assistant",
                "content": "Narrative\n%%%JSON_START%%%\n"
                + json.dumps(payload)
                + "\n%%%JSON_END%%%\n",
            },
        ],
    }
    script = f"""
let stageRiskExposure = null;
let stageSensitivitySummary = '';
let stageResponsivenessSummary = '';
{helper}
restoreSavedStage3Sections({json.dumps(state)});
if(stageRiskExposure.risks_to !== 'Flooding can interrupt access to clinics.') throw new Error('risk-to was not restored');
if(stageRiskExposure.risks_from !== 'Unequal targeting could deepen local grievance.') throw new Error('risk-from was not restored');
if(stageSensitivitySummary !== 'The design recognises access constraints.') throw new Error('sensitivity summary was not restored');
if(stageResponsivenessSummary !== 'The design has limited entry points for resilience.') throw new Error('responsiveness summary was not restored');
"""
    _run_node(script)


def test_stage3_structured_sections_are_saved_loaded_and_checkpointed():
    source = INDEX.read_text(encoding="utf-8")
    save_start = source.index("function saveSession()")
    save_end = source.index("function showLegacyBanner", save_start)
    load_start = source.index("function loadSession(input)")
    load_end = source.index("function updateSessionBar", load_start)
    checkpoint = _extract_js_function(source, "epSafeStore")
    for section, field in (
        (source[save_start:save_end], "stageRiskExposure"),
        (source[save_start:save_end], "stageSensitivitySummary"),
        (source[save_start:save_end], "stageResponsivenessSummary"),
        (source[load_start:load_end], "restoreSavedStage3Sections"),
        (checkpoint, "stageRiskExposure"),
        (checkpoint, "stageSensitivitySummary"),
        (checkpoint, "stageResponsivenessSummary"),
    ):
        assert field in section

    script = f"""
const values = new Map();
const localStorage = {{
  setItem(key, value) {{ values.set(key, String(value)); }},
  getItem(key) {{ return values.get(key) || null; }}
}};
let researchBrief = null, researchCountry = '';
let activeLenses = [], lensDiagnostic = {{}}, lensContextSources = [];
let climateResearch = {{}}, climateGrounding = {{}};
let climateVerifiedAssessment = null, climateVerifiedReader = null;
let stageConciseReadout = null, stageThreePriorities = [];
let fcvRating = 'Adequate', fcvResponsivenessRating = 'Emerging';
let stageRiskExposure = {{risks_to:'risk to', risks_from:'risk from'}};
let stageSensitivitySummary = 'sensitivity';
let stageResponsivenessSummary = 'responsiveness';
let midCycleWatch = [], dpfWatch = [], p4rWatch = [], regionalWatch = [];
let horizonConsiderations = '';
let docType = 'PAD', instrumentType = 'IPF', countryScope = 'single';
let temporalContext = {{approval_date:'2024-12'}};
const lensVersions = () => ({{}});
{checkpoint}
epSafeStore({{}}, {{}}, 3);
const saved = JSON.parse(localStorage.getItem('fcv_express_lensState'));
if(saved.stageRiskExposure.risks_to !== 'risk to') throw new Error('checkpoint lost risk exposure');
if(saved.stageSensitivitySummary !== 'sensitivity') throw new Error('checkpoint lost sensitivity');
if(saved.stageResponsivenessSummary !== 'responsiveness') throw new Error('checkpoint lost responsiveness');
if(saved.temporalContext.approval_date !== '2024-12') throw new Error('checkpoint lost project date');
"""
    _run_node(script)


def test_reset_clears_detailed_sections_and_summary_link_explains_detail_target():
    source = INDEX.read_text(encoding="utf-8")
    reset_start = source.index("function reset()")
    reset_end = source.index("// Markdown renderer", reset_start)
    reset = source[reset_start:reset_end]
    for field, value in (
        ("stageRiskExposure", "null"),
        ("stageSensitivitySummary", "''"),
        ("stageResponsivenessSummary", "''"),
    ):
        assert f"{field}={value}" in reset
    assert (
        "See full Priority ${idx+1} details and suggested text for the project package in Detailed Analysis"
        in source
    )


def test_temporal_context_survives_session_and_express_restore():
    source = INDEX.read_text(encoding="utf-8")
    save = source[source.index("function saveSession()"):source.index("function showLegacyBanner")]
    load = source[source.index("function loadSession(input)"):source.index("function updateSessionBar")]
    express_restore = source[source.index("const savedLensState=JSON.parse("):source.index("function restartExpressFromStage1()")]
    checkpoint = _extract_js_function(source, "epSafeStore")
    reset = _extract_js_function(source, "reset")

    assert "temporalContext={}" in reset
    assert "temporalContext: temporalContext" in save
    assert "temporalContext=state.temporalContext||{}" in load
    assert "temporalContext:temporalContext" in checkpoint
    assert "temporalContext=savedLensState.temporalContext||{}" in express_restore
