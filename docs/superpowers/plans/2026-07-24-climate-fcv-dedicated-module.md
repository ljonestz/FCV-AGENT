# Climate-FCV Dedicated Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Climate-FCV lens into a dedicated module output — the six core questions become the Stage 2 spine and drive a structured Reflections block; the two interaction sections render as prose callout boxes (no causal-strip diagram); a single "How well does the project integrate climate and FCV?" gauge replaces the two S/R gauges; a Wider FCV context note is added; and the blocks are reordered dynamics → reflections → dividends → wider-FCV, across live HTML, shared HTML and DOCX.

**Architecture:** The climate lens is a file-based module under `sector_lenses/modules/climate/` orchestrated by `app.py`. Stage 2 emits a hidden diagnostic block (`%%%LENS_DIAGNOSTIC_START/END%%%`) parsed by `sector_lenses/pipeline.py:extract_lens_diagnostic`; Stage 3 emits a priorities JSON block parsed by `app.py:extract_priorities`. The per-stage prompt is built by `app.py:build_lens_stage_context`. Frontend rendering, gauge, and both exports live in `index.html`; DOCX export is `app.py:download_report`. This plan extends the diagnostic contract with `reflections`, `integration_level`, `integration_summary`, adds a top-level `wider_fcv_context` to Stage 3 JSON, and updates all three render surfaces.

**Tech Stack:** Python 3.13, Flask, Anthropic SDK, python-docx, vanilla JS in a single `index.html`, pytest (+ Node for frontend render tests).

**Design spec:** `docs/superpowers/specs/2026-07-24-climate-fcv-dedicated-module-design.md`

**Working dir for all commands (OneDrive worktree — avoids pytest cache-dir failures):**
```
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT/.worktrees/sector-lens-platform"
```
**Standard test invocation:**
```
python -m pytest <files> -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```
Frontend tests require `node` on PATH (they fail, not skip, if absent).

**Commit rule:** no `Co-Authored-By` / AI-attribution trailer on any commit (repo owner standing instruction).

---

## Contract additions (single source of truth — referenced by every phase)

**A. Stage 2 climate diagnostic** (per-lens entry, `lens_id == "climate"`) gains:
- `reflections`: array of 3–5 objects `{ "question_key", "title", "status_cue", "text" }`
  - `question_key` ∈ `{cq1_interaction, cq2_maladaptation, cq3_dividends, cq4_inclusion, cq5_institutions, cq6_adaptive}`
  - `title`: short label (≤80 chars). `status_cue`: short soft phrase (≤40 chars, e.g. "well recognised", "partial gap", "strong", "unclaimed opportunity"). `text`: 1–3 sentences (≤700 chars).
- `less_central`: optional string (≤300 chars) naming non-material core questions.
- `integration_level`: one of `strong | moderate | limited`.
- `integration_summary`: string (≤400 chars) for the gauge caption.

**B. Stage 3 priorities JSON** gains one top-level field:
- `wider_fcv_context`: string or null — a material non-climate FCV issue, surfaced not developed.

**C. Six core questions → existing `questions.yaml` grounding** (spine mapping, for prompt wording):
- cq1_interaction ← `project-climate-influence`, `compound-risk`, `delivery-feasibility`
- cq2_maladaptation ← `maladaptation`, `power-distribution`, `resource-access`, `disaster-services`
- cq3_dividends ← `dividends-invest`, `livelihoods-food`, `governance-trust`
- cq4_inclusion ← `differentiated-effects`, `mobility-displacement`, `participation-grm`
- cq5_institutions ← `institutional-feasibility`, `delivery-feasibility`, `governance-trust`
- cq6_adaptive ← `monitor-adapt`, `dividends-deliver`

**D. Render order (all three surfaces), climate-valid:**
1 materiality notice → 2 exec summary (core prose) → 3 Box A interaction → 4 Box B interaction → 5 Reflections → 6 Dividends synthesis → 7 Wider FCV context → then priority panels. The integration gauge replaces the two S/R gauges in the sidebar.

---

## PHASE 1 — Backend: diagnostic contract, parser, prompt spine, SSE

### Task 1.1: Parse `reflections`, `integration_level`, `integration_summary`, `less_central` in the climate diagnostic

**Files:**
- Modify: `sector_lenses/pipeline.py` (inside `extract_lens_diagnostic`, climate branch, after the `normalized_interactions` block ends near line 430; and where the per-lens dict is assembled — find the `lenses.append({...})` for the climate entry, downstream of line 490)
- Test: `tests/test_sector_lens_pipeline.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_sector_lens_pipeline.py`:
```python
def test_climate_diagnostic_parses_reflections_and_integration():
    block = (
        "%%%LENS_DIAGNOSTIC_START%%%"
        '{"lenses":[{"lens_id":"climate","applicability":"material",'
        '"materiality_level":"high","materiality_summary":"Water and conflict.",'
        '"integration_level":"moderate","integration_summary":"Aware but allocation untreated.",'
        '"reflections":[{"question_key":"cq2_maladaptation","title":"Maladaptation and lock-in",'
        '"status_cue":"partial gap","text":"Siting is treated as engineering, not allocation."},'
        '{"question_key":"cq4_inclusion","title":"Vulnerable groups","status_cue":"strong",'
        '"text":"IDP households are explicitly targeted."}],'
        '"less_central":"HDP coordination is light here.",'
        '"source_ids":[],"readout_sections":[],"interaction_readout":[],'
        '"additional_pathways":[],"other_pathways":[]}],"findings":[]}'
        "%%%LENS_DIAGNOSTIC_END%%%"
    )
    result = extract_lens_diagnostic(block, ["climate"])
    lens = result["lenses"][0]
    assert lens["integration_level"] == "moderate"
    assert lens["integration_summary"].startswith("Aware")
    assert [r["question_key"] for r in lens["reflections"]] == [
        "cq2_maladaptation", "cq4_inclusion",
    ]
    assert lens["reflections"][0]["status_cue"] == "partial gap"
    assert lens["less_central"] == "HDP coordination is light here."


def test_climate_reflections_drop_unknown_keys_and_cap_at_five():
    reflections = ",".join(
        '{"question_key":"cq1_interaction","title":"t","status_cue":"ok","text":"x"}'
        for _ in range(7)
    )
    bad = '{"question_key":"not_a_cq","title":"t","status_cue":"ok","text":"x"}'
    block = (
        "%%%LENS_DIAGNOSTIC_START%%%"
        '{"lenses":[{"lens_id":"climate","applicability":"material",'
        '"materiality_level":"high","reflections":[' + bad + "," + reflections + "],"
        '"source_ids":[],"readout_sections":[],"interaction_readout":[],'
        '"additional_pathways":[],"other_pathways":[]}],"findings":[]}'
        "%%%LENS_DIAGNOSTIC_END%%%"
    )
    lens = extract_lens_diagnostic(block, ["climate"])["lenses"][0]
    assert all(r["question_key"] != "not_a_cq" for r in lens["reflections"])
    assert len(lens["reflections"]) <= 5
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_sector_lens_pipeline.py::test_climate_diagnostic_parses_reflections_and_integration -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (KeyError on `integration_level` / `reflections` missing).

- [ ] **Step 3: Add a module-level constant and normalizer near the top of `pipeline.py`** (beside `_INTERACTION_DIRECTIONS`, ~line 22):
```python
_CLIMATE_REFLECTION_KEYS = {
    "cq1_interaction", "cq2_maladaptation", "cq3_dividends",
    "cq4_inclusion", "cq5_institutions", "cq6_adaptive",
}
_CLIMATE_INTEGRATION_LEVELS = {"strong", "moderate", "limited"}


def _normalize_climate_reflections(value):
    reflections = []
    for raw in _list_values(value):
        if not isinstance(raw, dict):
            continue
        key = str(raw.get("question_key", ""))
        text = str(raw.get("text", "")).strip()[:700]
        if key not in _CLIMATE_REFLECTION_KEYS or not text:
            continue
        reflections.append({
            "question_key": key,
            "title": str(raw.get("title", "")).strip()[:80],
            "status_cue": str(raw.get("status_cue", "")).strip()[:40],
            "text": text,
        })
        if len(reflections) >= 5:
            break
    return reflections
```

- [ ] **Step 4: In the climate branch of `extract_lens_diagnostic`, compute the new fields** (add just before the climate lens dict is appended to `lenses`). Insert:
```python
        reflections = (
            _normalize_climate_reflections(item.get("reflections"))
            if lens_id == "climate" else []
        )
        integration_level = ""
        integration_summary = ""
        less_central = ""
        if lens_id == "climate":
            raw_integration = str(item.get("integration_level", "")).lower()
            integration_level = (
                raw_integration if raw_integration in _CLIMATE_INTEGRATION_LEVELS
                else "" if strict_required_fields
                else "moderate" if applicability == "material" else "limited"
            )
            integration_summary = str(item.get("integration_summary", "")).strip()[:400]
            less_central = str(item.get("less_central", "")).strip()[:300]
```
Then add these keys to the appended climate lens dict (the `lenses.append({...})` / dict literal that already carries `materiality_level`, `interaction_readout`, etc.):
```python
            "reflections": reflections,
            "integration_level": integration_level,
            "integration_summary": integration_summary,
            "less_central": less_central,
```

- [ ] **Step 5: Run both new tests to verify pass**

Run: `python -m pytest tests/test_sector_lens_pipeline.py -k "reflections or integration" -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**
```bash
git add sector_lenses/pipeline.py tests/test_sector_lens_pipeline.py
git commit -m "feat: parse climate reflections and integration level in diagnostic"
```

---

### Task 1.2: Parse `wider_fcv_context` in Stage 3 priorities

**Files:**
- Modify: `app.py` `extract_priorities()` (starts app.py:5010) — where the top-level result dict is assembled (alongside `sensitivity_summary`, `risk_exposure`)
- Test: `tests/test_extract_priorities.py`

- [ ] **Step 1: Write the failing test** — add to `tests/test_extract_priorities.py`:
```python
def test_extract_priorities_captures_wider_fcv_context():
    text = (
        "%%%JSON_START%%%"
        '{"fcv_rating":"Moderate","fcv_responsiveness_rating":"Moderate",'
        '"sensitivity_summary":"s","responsiveness_summary":"r",'
        '"risk_exposure":{"risks_to":[],"risks_from":[]},'
        '"wider_fcv_context":"Reliance on contested state structures is a non-climate FCV risk.",'
        '"priorities":[]}'
        "%%%JSON_END%%%"
    )
    result = extract_priorities(text)
    assert result["wider_fcv_context"].startswith("Reliance on contested")


def test_extract_priorities_wider_fcv_defaults_none():
    text = (
        "%%%JSON_START%%%"
        '{"fcv_rating":"Moderate","priorities":[]}'
        "%%%JSON_END%%%"
    )
    assert extract_priorities(text).get("wider_fcv_context") is None
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_extract_priorities.py -k wider_fcv -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (KeyError / None mismatch).

- [ ] **Step 3: Implement** — in `extract_priorities()`, where the return dict is built, add:
```python
    wider_fcv_context = data.get("wider_fcv_context")
    if isinstance(wider_fcv_context, str):
        wider_fcv_context = wider_fcv_context.strip()[:1200] or None
    else:
        wider_fcv_context = None
```
and include `"wider_fcv_context": wider_fcv_context,` in the returned dict.

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_extract_priorities.py -k wider_fcv -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**
```bash
git add app.py tests/test_extract_priorities.py
git commit -m "feat: parse wider_fcv_context in stage 3 priorities"
```

---

### Task 1.3: Stage 2 prompt — six core questions, intersection rule, reflections + integration instruction

**Files:**
- Modify: `app.py` `build_lens_stage_context`, Stage 2 climate branch (the `suffix += (...)` block at app.py:932-950)
- Test: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write the failing test** — add to `tests/test_sector_lens_app_contract.py`:
```python
def test_stage2_climate_prompt_requires_reflections_and_intersection():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"], "lens_versions": {}, "doc_type": "PAD",
    })
    ctx = app_module.build_lens_stage_context(
        state, 2, climate_research={"status": "failed", "attempts": 0,
                                    "sources": [], "claims": [], "failure_reason": ""},
    )
    prompt = ctx["prompt"]
    assert "reflections" in prompt
    assert "integration_level" in prompt
    assert "cq2_maladaptation" in prompt
    assert "climate and an FCV" in prompt  # intersection rule wording
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_sector_lens_app_contract.py -k stage2_climate_prompt_requires_reflections -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Implement** — append to the Stage 2 climate `suffix` (after the existing "Suppress generic pathways..." sentence, before `"Validated Climate research claims:\n"`):
```python
                " Every pathway and finding must sit at the intersection of a "
                "climate and an FCV dynamic; drop pure climate-engineering points "
                "and pure FCV points with no climate dimension. Time horizons "
                "(current-near-term, project-lifetime, asset-system-lifetime) are "
                "an available lens: use them only where they change the finding, "
                "for example where design choices could lock in patterns that "
                "longer-term climate shifts would later turn maladaptive. "
                "Also return, for the Climate lens, integration_level (strong, "
                "moderate, or limited) and integration_summary describing how well "
                "the project recognises and responds to the material Climate-FCV "
                "interactions, plus reflections: three to five objects each with "
                "question_key, title, status_cue, and text, drawn from these core "
                "questions and surfacing only the material ones: "
                "cq1_interaction (Climate-FCV interactions and delivery), "
                "cq2_maladaptation (maladaptation, Do No Harm and lock-in), "
                "cq3_dividends (peace and social dividends and root causes), "
                "cq4_inclusion (vulnerable regions, groups and inclusion), "
                "cq5_institutions (institutions, governance and HDP coordination), "
                "cq6_adaptive (adaptive design, monitoring and uncertainty). "
                "Use a soft status_cue (for example well recognised, partial gap, "
                "strong, unclaimed opportunity) and add less_central naming any "
                "core question that is not material here. "
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_sector_lens_app_contract.py -k stage2_climate_prompt_requires_reflections -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: stage 2 climate prompt drives six core questions and reflections"
```

---

### Task 1.4: Stage 3 prompt — prose interaction boxes (no causal strip), reflections carry-through, wider FCV context

**Files:**
- Modify: `app.py` `build_lens_stage_context`, Stage 3 climate prefix (app.py:988-1010)
- Test: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write the failing test**:
```python
def test_stage3_climate_prompt_uses_prose_and_wider_context():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"], "lens_versions": {}, "doc_type": "PAD",
    })
    diagnostic = {"lenses": [{"lens_id": "climate", "materiality_level": "high"}],
                  "findings": []}
    ctx = app_module.build_lens_stage_context(state, 3, lens_diagnostic=diagnostic)
    prompt = ctx["prompt"]
    assert "wider_fcv_context" in prompt
    assert "causal strip" not in prompt.lower()
    assert "prose" in prompt.lower()
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_sector_lens_app_contract.py -k stage3_climate_prompt_uses_prose -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (prompt still says "causal strip", no `wider_fcv_context`).

- [ ] **Step 3: Implement** — in the Stage 3 climate prefix (app.py:988-1010) replace the sentence:
`"write two substantive interaction narratives, each with a causal strip: pressure -> mechanism -> project implication -> design response and time horizons."`
with:
```python
                "write two substantive interaction narratives in prose, one for "
                "each direction (how Climate-FCV dynamics could affect the project; "
                "how the project could affect Climate-FCV dynamics), naming "
                "components, places, groups and assets, weaving in time horizons "
                "only where they matter, and closing each with the current design "
                "response and the remaining gap. Do not use a causal strip or arrow "
                "diagram. "
```
Then append to the end of the same climate prefix block (after the `climate_links` sentences):
```python
            prefix += (
                "Add a top-level wider_fcv_context string naming any material FCV "
                "issue with no real climate dimension so it is surfaced but not "
                "developed into a priority; use null if none. "
            )
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_sector_lens_app_contract.py -k stage3_climate_prompt_uses_prose -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: stage 3 climate prompt uses prose interactions and wider fcv context"
```

---

### Task 1.5: Emit `climate_integration` in the SSE done payloads (drives the gauge)

**Files:**
- Modify: `app.py` step-by-step done payload (Stage 2 keys ~7372-7382) and express `stage_done:2` payload (~8040)
- Test: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write the failing test** (helper that pulls integration from a diagnostic):
```python
def test_climate_integration_payload_helper():
    diagnostic = {"lenses": [{"lens_id": "climate",
                              "integration_level": "moderate",
                              "integration_summary": "Aware but allocation untreated."}]}
    out = app_module.climate_integration_payload(diagnostic)
    assert out == {"level": "moderate", "summary": "Aware but allocation untreated."}
    assert app_module.climate_integration_payload({"lenses": []}) is None
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_sector_lens_app_contract.py -k climate_integration_payload -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (no such function).

- [ ] **Step 3: Implement** — add near `climate_lens_entry` (app.py:8554):
```python
def climate_integration_payload(diagnostic):
    lens = climate_lens_entry(diagnostic)
    if not lens or not lens.get("integration_level"):
        return None
    return {
        "level": lens.get("integration_level", ""),
        "summary": lens.get("integration_summary", ""),
    }
```
Then in the step-by-step Stage 2 done keys (~7381) and express `stage_done:2` dict (~8040) add:
```python
                "climate_integration": climate_integration_payload(lens_diagnostic),
```
(use the `lens_diagnostic` variable already in scope at each site — confirm the local name when editing).

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_sector_lens_app_contract.py -k climate_integration_payload -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: emit climate integration level in stage 2 sse payloads"
```

---

## PHASE 2 — Frontend rendering (`index.html`)

All functions below live in `index.html`. Frontend tests go in `tests/test_climate_lens_frontend.py`, which extracts a named JS function and runs it under Node with injected data (see existing `_extract_js_function` helper and the `node -e` pattern).

### Task 2.1: Retitle the materiality notice and add an explicit source signpost

**Files:**
- Modify: `index.html` `renderClimateModuleNotice` (2552-2565)
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write the failing test**:
```python
def test_materiality_notice_uses_relevance_title_and_source_list():
    html = INDEX.read_text(encoding="utf-8")
    assert "How relevant is climate to this project?" in html
    assert "Maximizing the Peace and Social Dividends of Climate Action" in html
    assert "FCV-Sensitive Climate Action Framework" in html
    assert "Defueling Conflict" in html
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k materiality_notice_uses_relevance -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Implement** — in `renderClimateModuleNotice`, change the `<h3>Climate-focused FCV assessment</h3>` in BOTH the error and normal return to `<h3>How relevant is climate to this project?</h3>`, and replace the `evidence` string with an explicit list:
```javascript
    const evidence='These reflections and recommendations draw on a core set of climate and FCV frameworks and evidence, including: Maximizing the Peace and Social Dividends of Climate Action; the FCV-Sensitive Climate Action Framework; and the Defueling Conflict series, alongside other World Bank and external sources.';
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k materiality_notice_uses_relevance -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: retitle climate notice and signpost source frameworks"
```

---

### Task 2.2: Convert the causal-strip pathway to prose, and wrap the two interactions in tinted boxes

**Files:**
- Modify: `index.html` `renderClimatePathwayStrip` (2576-2598) and `renderClimateInteractions` (2600-2616); CSS (340-377)
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write the failing test** (Node-executed; follow the existing `_extract_js_function` + `node -e` pattern already used for `renderClimateInteractions`):
```python
def test_interactions_render_as_prose_boxes_without_causal_grid():
    html = INDEX.read_text(encoding="utf-8")
    # CSS no longer defines the arrow causal grid
    assert ".causal-strip" not in html
    # new box classes present
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
    assert "›" not in out.stdout  # no arrow glyph
    assert "seasonal windows" in out.stdout  # design response now in prose
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k interactions_render_as_prose -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Replace `renderClimatePathwayStrip`** with a prose renderer:
```javascript
  function renderClimatePathwayStrip(pathway){
    if(!pathway)return '';
    const bits=[pathway.pressure,pathway.mechanism,pathway.project_implication].filter(Boolean);
    if(bits.length<2)return '';
    const anchors=[
      ...(Array.isArray(pathway.project_elements)?pathway.project_elements:[]),
      ...(Array.isArray(pathway.geographies)?pathway.geographies:[]),
      ...(Array.isArray(pathway.affected_groups)?pathway.affected_groups:[]),
      ...(Array.isArray(pathway.systems_or_assets)?pathway.systems_or_assets:[])
    ].filter(Boolean);
    const horizons=(Array.isArray(pathway.time_horizons)?pathway.time_horizons:[])
      .map(v=>({'current-near-term':'in the near term','project-lifetime':'over the project’s life','asset-system-lifetime':'over the life of the assets'}[v])).filter(Boolean);
    const lead=esc(bits.join(', leading to '))+'.';
    const response=pathway.design_response?` The current design response is ${esc(pathway.design_response)}.`:'';
    const gap=pathway.evidence_gap?` Remaining gap: ${esc(pathway.evidence_gap)}.`:'';
    const horizonNote=horizons.length?` This matters ${horizons.map(esc).join(' and ')}.`:'';
    const anchorNote=anchors.length?` <span class="climate-pathway-anchors">Anchored in ${anchors.map(esc).join(', ')}.</span>`:'';
    return `<p class="climate-pathway-prose">${lead}${horizonNote}${response}${gap}${anchorNote}</p>`;
  }
```

- [ ] **Step 4: Replace `renderClimateInteractions`** with the tinted-box version (retitled, box classes, direction-specific accent via a modifier class):
```javascript
  function renderClimateInteractions(lens){
    if(!lens)return '';
    const labels={
      'climate-fcv-on-project':'How climate and FCV dynamics could affect this project',
      'project-on-climate-fcv':'How this project could affect climate and FCV dynamics'
    };
    const modifier={'climate-fcv-on-project':'box-inbound','project-on-climate-fcv':'box-outbound'};
    const interactions=(Array.isArray(lens.interaction_readout)?lens.interaction_readout:[])
      .filter(item=>item&&labels[item.direction_id]&&item.summary)
      .slice(0,2);
    if(!interactions.length)return '';
    return interactions.map(item=>{
      const pathways=(Array.isArray(item.pathways)?item.pathways:[])
        .map(renderClimatePathwayStrip).filter(Boolean).join('');
      return `<section class="climate-interaction-box ${modifier[item.direction_id]||''}"><h4>${esc(labels[item.direction_id])}</h4><p class="climate-interaction-summary">${esc(item.summary)}</p>${pathways}</section>`;
    }).join('');
  }
```
(Note: the old wrapper `.climate-interactions-section` heading/intro is dropped; each box is now standalone in document order, per render order D.)

- [ ] **Step 5: Update CSS** (index.html 348-377). Remove `.climate-interaction-stack`, `.climate-interaction-narrative*`, `.climate-pathway*`, `.causal-strip*`, `.horizon-badge*`, and the `@media` causal-strip rules. Add:
```css
    .climate-interaction-box{border:1px solid var(--border);border-left:5px solid #64748b;background:#f8fafc;border-radius:8px;padding:14px 18px;margin:0 0 14px}
    .climate-interaction-box.box-inbound{border-left-color:#475569;background:#f6f8fb}
    .climate-interaction-box.box-outbound{border-left-color:#0f766e;background:#f5fbfa}
    .climate-interaction-box h4{font-size:13px;line-height:1.4;color:#0f172a;margin:0 0 6px}
    .climate-interaction-summary{font-size:13px;line-height:1.6;color:#334155;margin:0 0 8px}
    .climate-pathway-prose{font-size:13px;line-height:1.6;color:#334155;margin:0 0 8px}
    .climate-pathway-prose:last-child{margin-bottom:0}
    .climate-pathway-anchors{color:#64748b;font-size:12px}
```
Keep `renderHorizonBadge` defined (dividend code may still reference it) but it is no longer called by the interaction path.

- [ ] **Step 6: Run to verify pass**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k interactions_render_as_prose -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS. Then run the whole frontend file and fix any now-stale assertions that referenced `causal-strip` / `climate-interaction-narrative`:
Run: `python -m pytest tests/test_climate_lens_frontend.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`

- [ ] **Step 7: Commit**
```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: render climate interactions as prose boxes, drop causal strip"
```

---

### Task 2.3: New `renderClimateReflections(lens)` with soft status chips + adaptable intro

**Files:**
- Modify: `index.html` (add function after `renderClimateInteractions`, ~2617); CSS
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write the failing test**:
```python
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
    # empty reflections -> empty string
    empty = subprocess.run(["node", "-e", f"{esc}\n{fn}\nprocess.stdout.write(renderClimateReflections({{}}));"], capture_output=True, text=True)
    assert empty.stdout.strip() == ""
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k reflections_render_with_status -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Implement** — add:
```javascript
  function renderClimateReflections(lens){
    const items=(lens&&Array.isArray(lens.reflections)?lens.reflections:[])
      .filter(r=>r&&r.text);
    if(!items.length)return '';
    const rows=items.map(r=>`<div class="reflection-row"><div class="reflection-head"><strong>${esc(r.title||'')}</strong>${r.status_cue?`<span class="reflection-chip">${esc(r.status_cue)}</span>`:''}</div><p>${esc(r.text)}</p></div>`).join('');
    const less=lens.less_central?`<p class="reflection-less"><em>Less central here:</em> ${esc(lens.less_central)}</p>`:'';
    return `<div class="climate-reflections-section"><div class="climate-readout-heading">Reflections on core climate and FCV considerations</div><p class="climate-readout-intro">The reflections below draw on a core set of climate and FCV frameworks and evidence, and focus on the considerations most material to this project rather than applying every principle mechanically.</p>${rows}${less}</div>`;
  }
```

- [ ] **Step 4: Add CSS** (near the climate block, ~373):
```css
    .climate-reflections-section{margin:20px 0}
    .reflection-row{border-left:3px solid #cbd5e1;padding:2px 0 2px 12px;margin:12px 0}
    .reflection-head{display:flex;align-items:center;gap:8px;margin:0 0 4px}
    .reflection-head strong{font-size:13px;color:#1e293b}
    .reflection-chip{display:inline-flex;padding:1px 8px;border-radius:999px;background:#eef2f7;color:#475569;font-size:10px;font-weight:700;text-transform:lowercase}
    .reflection-row p{font-size:13px;line-height:1.6;color:#334155;margin:0}
    .reflection-less{font-size:12px;color:#64748b;margin:10px 0 0}
```

- [ ] **Step 5: Run to verify pass**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k reflections_render_with_status -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 6: Commit**
```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: add climate reflections render block with soft status chips"
```

---

### Task 2.4: New `renderWiderFcvContext(text)` grey callout

**Files:**
- Modify: `index.html` (add function ~after reflections); CSS
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write the failing test**:
```python
def test_wider_fcv_context_renders_grey_callout_or_empty():
    html = INDEX.read_text(encoding="utf-8")
    assert "renderWiderFcvContext" in html
    fn = _extract_js_function(html, "renderWiderFcvContext")
    esc = _extract_js_function(html, "esc")
    out = subprocess.run(["node", "-e", f'{esc}\n{fn}\nprocess.stdout.write(renderWiderFcvContext("Contested state delivery structures."));'], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "Wider FCV context" in out.stdout
    assert "wider-fcv-note" in out.stdout
    empty = subprocess.run(["node", "-e", f'{esc}\n{fn}\nprocess.stdout.write(renderWiderFcvContext(""));'], capture_output=True, text=True)
    assert empty.stdout.strip() == ""
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k wider_fcv_context_renders -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Implement**:
```javascript
  function renderWiderFcvContext(text){
    const value=(text||'').toString().trim();
    if(!value)return '';
    return `<div class="wider-fcv-note"><div class="climate-readout-heading">Wider FCV context</div><p>${esc(value)}</p></div>`;
  }
```
CSS:
```css
    .wider-fcv-note{border:1px solid var(--border);background:#f7f8fa;border-radius:8px;padding:12px 16px;margin:18px 0}
    .wider-fcv-note p{font-size:12px;line-height:1.6;color:#475569;margin:0}
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k wider_fcv_context_renders -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: add wider fcv context callout renderer"
```

---

### Task 2.5: Single "climate-FCV integration" gauge replacing the two S/R gauges in module mode

**Files:**
- Modify: `index.html` `sidebarHtml()` (5492-5532), `updateSidebar()` (5534-5580); add a global `climateIntegration` set from SSE; CSS as needed
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write the failing test** (static string checks — the gauge functions are large and DOM-bound, so assert presence + the integration mapping helper):
```python
def test_single_integration_gauge_present_in_module_mode():
    html = INDEX.read_text(encoding="utf-8")
    assert "How well does the project integrate climate and FCV?" in html
    assert "climateIntegration" in html
    assert "integrationGaugeFraction" in html
    fn = _extract_js_function(html, "integrationGaugeFraction")
    out = subprocess.run(["node", "-e", f"{fn}\nconsole.log([integrationGaugeFraction('strong'),integrationGaugeFraction('moderate'),integrationGaugeFraction('limited'),integrationGaugeFraction('')].join(','))"], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    vals = out.stdout.strip().split(",")
    assert vals[0] == "1" and vals[2] == "0.33" and float(vals[1]) > float(vals[2])
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k single_integration_gauge -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Add globals + helper** near the gauge globals (`fcvRating` declaration ~5471):
```javascript
  let climateIntegration=null; // {level, summary}
  function integrationGaugeFraction(level){
    return ({strong:1,moderate:0.66,limited:0.33})[String(level||'').toLowerCase()]||0;
  }
```

- [ ] **Step 4: Branch `sidebarHtml()`** — at the top of the function, when `isClimateLensActive()`, return a single-gauge block instead of the two-gauge markup:
```javascript
    if(isClimateLensActive()){
      return `<div class="sidebar-widget sidebar-widget-fcv"><div class="sidebar-widget-label">How well does the project integrate climate and FCV?</div>
        <svg viewBox="0 0 60 60" class="fcv-gauge"><path class="fcv-arc-bg" d="M8 52 A 30 30 0 1 1 52 52"/><path id="fcv-int-arc" class="fcv-arc-fill" d="M8 52 A 30 30 0 1 1 52 52"/></svg>
        <div id="fcv-int-label" class="fcv-rating-label"></div><div id="fcv-int-summary" class="fcv-need-label"></div>
        <div class="fcv-gauge-caveat">A subjective AI judgement, not an official WBG assessment.</div></div>`;
    }
```
(Reuse existing arc path geometry/classes from the current sensitivity gauge markup; copy the exact `d=` path and `.fcv-arc-*` classes from lines 5495-5508 so styling matches.)

- [ ] **Step 5: Branch `updateSidebar()`** — when `isClimateLensActive()`, drive the single gauge and skip the two-gauge logic:
```javascript
    if(isClimateLensActive()){
      const arc=document.getElementById('fcv-int-arc');
      const lvl=climateIntegration&&climateIntegration.level||'';
      const frac=integrationGaugeFraction(lvl);
      const ARC_LEN=141.37;
      if(arc)arc.setAttribute('stroke-dasharray',`${(frac*ARC_LEN).toFixed(2)} ${ARC_LEN}`);
      const label=document.getElementById('fcv-int-label');
      const labels={strong:'Well integrated',moderate:'Partially integrated',limited:'Limited integration'};
      if(label)label.textContent=labels[String(lvl).toLowerCase()]||'Not yet rated';
      const summary=document.getElementById('fcv-int-summary');
      if(summary)summary.textContent=climateIntegration&&climateIntegration.summary||'';
      // still render the priority overview mini-list below (reuse existing #pov-sb block)
    } else {
      // existing two-gauge logic unchanged
    }
```
Wrap the current two-gauge body (5539-5559) in the `else`. Keep the Priority Overview block (5561-5578) running in both branches.

- [ ] **Step 6: Set `climateIntegration` from SSE** — in the `p.done`/stage-2 handler (index.html ~3851-3856, beside `lensDiagnostic`) add:
```javascript
        if(p.climate_integration!==undefined)climateIntegration=p.climate_integration;
```
and reset it where lenses reset (~2512): `climateIntegration=null;`.

- [ ] **Step 7: Add caveat CSS**:
```css
    .fcv-gauge-caveat{font-size:9px;color:#94a3b8;line-height:1.4;margin-top:6px}
```

- [ ] **Step 8: Run to verify pass**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k single_integration_gauge -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 9: Commit**
```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: single climate-fcv integration gauge in module mode"
```

---

### Task 2.6: Reorder the live render (`renderOut`) and shared HTML (`downloadHTML`) to order D

**Files:**
- Modify: `index.html` `renderOut` climate branch (4400-4418) and `downloadHTML` climate branch (5091-5116)
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write the failing test** (assert order via index positions in the generated string for the live path; reuse the existing `test_live_stage3_orders_option_a...` style). Add:
```python
def test_live_and_shared_orders_boxes_then_reflections_then_dividends_then_wider():
    html = INDEX.read_text(encoding="utf-8")
    for anchor in ("renderClimateInteractions", "renderClimateReflections",
                   "renderClimateDividendSynthesis", "renderWiderFcvContext"):
        assert anchor in html
    # live render branch: interactions before reflections before dividends before wider-fcv
    live = html.split("function renderOut", 1)[1][:6000]
    assert (live.index("renderClimateInteractions")
            < live.index("renderClimateReflections")
            < live.index("renderClimateDividendSynthesis")
            < live.index("renderWiderFcvContext"))
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k live_and_shared_orders -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Implement (live)** — in the `_climateValid` branch of `renderOut` (currently notice + preHtml + `renderSRNarrative` + `renderClimateInteractions` + `renderClimateDividendSynthesis`), change the assembled order to:
```javascript
        out = notice + preHtml
            + renderClimateInteractions(_climateEntry)
            + renderClimateReflections(_climateEntry)
            + renderClimateDividendSynthesis(_climateEntry, priorities)
            + renderWiderFcvContext((window.lastPriorities&&window.lastPriorities.wider_fcv_context)||'');
```
Remove the `renderSRNarrative(...)` call from the climate-valid branch (the single integration gauge replaces S/R here). Confirm the variable holding parsed priorities at this site (the plan uses `priorities` / `window.lastPriorities`; use the actual in-scope name — search `wider_fcv_context` is set on the Stage-3 parsed object).

- [ ] **Step 4: Implement (shared HTML)** — mirror the exact same order in `downloadHTML` (5107-5115), replacing its `renderSRNarrative + renderClimateInteractions + renderClimateDividendSynthesis` with `renderClimateInteractions + renderClimateReflections + renderClimateDividendSynthesis + renderWiderFcvContext(...)`.

- [ ] **Step 5: Run to verify pass**

Run: `python -m pytest tests/test_climate_lens_frontend.py -k "live_and_shared_orders or download_html_uses_same" -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS. Fix any stale ordering assertions in the file.

- [ ] **Step 6: Commit**
```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: reorder climate output to dynamics, reflections, dividends, wider fcv"
```

---

## PHASE 3 — DOCX export parity (`app.py` `download_report`)

Climate DOCX helpers: `add_climate_notice()` (8866), `add_causal_strip(pathway)` (8918), `add_climate_interactions()` (8971), `add_climate_dividend_synthesis()` (9005), `add_priority_climate_contribution()` (9064); doc build sequence at 9114-9136; per-priority at 9215-9216. Tests: `tests/test_sector_lens_app_contract.py` DOCX tests (they build a report from the South Sudan fixture and inspect the returned `.docx` bytes via python-docx `Document(BytesIO(...))`).

### Task 3.1: Prose interactions + notice title + source signpost in DOCX

**Files:** Modify `app.py` `add_causal_strip`→prose, `add_climate_interactions` titles, `add_climate_notice` title/signpost. Test: `tests/test_sector_lens_app_contract.py`.

- [ ] **Step 1: Write the failing test** — extend the existing DOCX contract test (find the test that builds the report for the South Sudan fixture; add assertions):
```python
def test_docx_climate_uses_prose_and_relevance_title(south_sudan_report_paragraphs):
    text = "\n".join(south_sudan_report_paragraphs)  # helper joins all doc paragraph texts
    assert "How relevant is climate to this project?" in text
    assert "How climate and FCV dynamics could affect this project" in text
    assert "How this project could affect climate and FCV dynamics" in text
    assert "Defueling Conflict" in text
    # no arrow/causal glyphs
    assert "›" not in text
```
(If no `south_sudan_report_paragraphs` fixture exists, add a small helper in the test module that POSTs the fixture's `stage3_block`/diagnostic to `/api/download-report` via the Flask test client and reads `Document(BytesIO(resp.data))` paragraph texts — mirror the existing DOCX test's setup.)

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_sector_lens_app_contract.py -k docx_climate_uses_prose -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Implement**
  - In `add_climate_notice` (8866): change the heading text to `"How relevant is climate to this project?"` and set the evidence/base paragraph to the explicit source list (`Maximizing the Peace and Social Dividends of Climate Action; the FCV-Sensitive Climate Action Framework; and the Defueling Conflict series`).
  - Replace `add_causal_strip(pathway)` body (8918) so instead of four labelled cells it writes ONE prose paragraph built from `pressure`, `mechanism`, `project_implication`, then a sentence with `design_response`, an optional horizons sentence, and an optional anchors run — mirroring the JS `renderClimatePathwayStrip` prose in Task 2.2. Keep the function name so callers are unchanged.
  - In `add_climate_interactions` (8971): update the two direction headings to the new titles ("How climate and FCV dynamics could affect this project" / "How this project could affect climate and FCV dynamics").

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_sector_lens_app_contract.py -k docx_climate_uses_prose -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: docx climate interactions as prose with relevance title"
```

---

### Task 3.2: DOCX reflections section, integration line, wider-FCV section, and reorder

**Files:** Modify `app.py` `download_report` — add `add_climate_reflections()`, `add_climate_integration_line()`, `add_wider_fcv_context()`, and reorder the build sequence (9114-9136). Test: `tests/test_sector_lens_app_contract.py`.

- [ ] **Step 1: Write the failing test**:
```python
def test_docx_climate_adds_reflections_integration_and_wider_context(south_sudan_report_paragraphs):
    text = "\n".join(south_sudan_report_paragraphs)
    assert "Reflections on core climate and FCV considerations" in text
    assert "How well does the project integrate climate and FCV?" in text
    assert "Wider FCV context" in text
    # order: interactions -> reflections -> dividends -> wider fcv
    i_int = text.index("How climate and FCV dynamics could affect this project")
    i_ref = text.index("Reflections on core climate and FCV considerations")
    i_div = text.index("Climate, peace and social dividends")
    i_wid = text.index("Wider FCV context")
    assert i_int < i_ref < i_div < i_wid
```
(Ensure the South Sudan fixture's `diagnostic` climate lens carries `reflections`, `integration_level`, `integration_summary`, and `stage3_block` carries `wider_fcv_context` — see Task 4.1 which updates the fixture; sequence Task 4.1 before running this if needed, or add inline data in the test.)

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_sector_lens_app_contract.py -k docx_climate_adds_reflections -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Implement** — inside `download_report`, define three nested helpers (mirror the style of `add_climate_dividend_synthesis`):
```python
        def add_climate_integration_line():
            payload = climate_integration_payload(lens_diagnostic)
            if not payload:
                return
            labels = {"strong": "Well integrated", "moderate": "Partially integrated",
                      "limited": "Limited integration"}
            p = doc.add_paragraph()
            run = p.add_run("How well does the project integrate climate and FCV? ")
            run.bold = True
            p.add_run(labels.get(payload["level"], "Not yet rated")
                      + (f" — {payload['summary']}" if payload.get("summary") else ""))

        def add_climate_reflections():
            reflections = (climate_readout or {}).get("reflections", []) if climate_readout else []
            if not reflections:
                return
            doc.add_heading("Reflections on core climate and FCV considerations", level=2)
            doc.add_paragraph(
                "The reflections below draw on a core set of climate and FCV frameworks "
                "and evidence, focusing on the considerations most material to this project."
            )
            for r in reflections:
                p = doc.add_paragraph()
                head = p.add_run((r.get("title") or "").strip())
                head.bold = True
                if r.get("status_cue"):
                    p.add_run(f"  [{r['status_cue']}]")
                doc.add_paragraph(r.get("text", ""))
            less = (climate_readout or {}).get("less_central")
            if less:
                doc.add_paragraph(f"Less central here: {less}")

        def add_wider_fcv_context():
            value = (priorities_payload or {}).get("wider_fcv_context")
            if not value:
                return
            doc.add_heading("Wider FCV context", level=2)
            doc.add_paragraph(value)
```
(Use the report's existing variable names: `climate_readout` from `climate_lens_entry(lens_diagnostic)` (8749) already holds the climate lens dict, so `reflections`/`less_central` live on it; `priorities_payload` is whatever the handler calls the parsed Stage-3 dict — confirm and substitute the real name.)

- [ ] **Step 4: Reorder the build sequence** (9130-9136 climate-valid branch) to:
```python
                add_climate_integration_line()
                add_climate_interactions()
                add_climate_reflections()
                add_climate_dividend_synthesis()
                add_wider_fcv_context()
```
Remove `add_sr_sections()` from the climate-valid branch (the integration line replaces the S/R sections in module mode). Leave the non-climate `else` branch unchanged. `add_climate_notice()` stays at 9114.

- [ ] **Step 5: Run to verify pass**

Run: `python -m pytest tests/test_sector_lens_app_contract.py -k "docx_climate_adds_reflections or docx_climate_uses_prose" -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 6: Commit**
```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: docx climate reflections, integration line, wider fcv, reorder"
```

---

## PHASE 4 — Fixture, regression, and manifest sync

### Task 4.1: Extend the South Sudan regression fixture with the new fields

**Files:** Modify `tests/fixtures/climate/south_sudan_dual_use.json`. Test: existing fixture-driven tests.

- [ ] **Step 1:** Add to the fixture's climate lens (`diagnostic.lenses[0]`):
```json
"integration_level": "moderate",
"integration_summary": "The project is climate-aware but treats water allocation as engineering rather than a contested-resource decision.",
"reflections": [
  {"question_key": "cq2_maladaptation", "title": "Maladaptation, Do No Harm and lock-in", "status_cue": "partial gap", "text": "New water points reallocate a contested dry-season resource; siting is not yet treated as a governance decision."},
  {"question_key": "cq4_inclusion", "title": "Vulnerable regions and groups", "status_cue": "strong", "text": "Targeting reaches drought- and displacement-affected districts and names IDP households explicitly."},
  {"question_key": "cq3_dividends", "title": "Peace and social dividends", "status_cue": "unclaimed opportunity", "text": "Shared water-user governance could produce a cohesion dividend but is not an intended outcome."}
],
"less_central": "HDP coordination is relevant given the humanitarian presence but is treated only lightly."
```
and to `stage3_block`: `"wider_fcv_context": "Reliance on federal and state delivery structures in areas of contested authority is a material non-climate FCV risk."`

- [ ] **Step 2: Update the fixture's `expected` block** if the fixture-driven tests assert on counts — add `"reflections": 3` and `"integration_level": "moderate"` and `"wider_fcv_context": true` if the consuming test reads them; otherwise leave `expected` and rely on the Phase 1-3 tests.

- [ ] **Step 3: Run the fixture-driven tests**

Run: `python -m pytest tests/test_climate_research.py tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 4: Commit**
```bash
git add tests/fixtures/climate/south_sudan_dual_use.json tests/
git commit -m "test: extend south sudan fixture with reflections, integration, wider fcv"
```

---

### Task 4.2: Sync manifest stage_instructions with the dedicated-module framing

**Files:** Modify `sector_lenses/modules/climate/manifest.yaml` `stage_instructions`. Test: `tests/test_climate_lens_package.py`.

- [ ] **Step 1: Write the failing test** — add to `tests/test_climate_lens_package.py`:
```python
def test_stage_instructions_reference_reflections_and_dedicated_focus():
    climate = load_registry(MODULE_ROOT).get("climate")
    s2 = climate.stage_instructions.get("stage2", "")
    s3 = climate.stage_instructions.get("stage3", "")
    assert "reflection" in s2.lower()
    assert "intersection" in s2.lower() or "climate and fcv" in s2.lower()
    assert "prose" in s3.lower()
    # slices still within ceilings
    for stage, ceiling in ((1, 600), (2, 2000), (3, 900)):
        assert build_stage_slice([climate], stage).estimated_tokens <= ceiling
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_climate_lens_package.py -k stage_instructions_reference_reflections -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Implement** — update `manifest.yaml` `stage_instructions.stage2` and `.stage3`:
```yaml
  stage2: Assign proportionate materiality and keep every pathway and finding at the intersection of a climate and an FCV dynamic. For both interaction directions give stable pathway_id values and specific causal chains from pressure through mechanism to project implication and design response, naming project elements, locations or groups, evidence, uncertainty, and current-near-term, project-lifetime, or asset-system-lifetime horizons where they matter. Return integration_level, integration_summary, and three to five reflections against the core climate-FCV questions, surfacing only the material ones. Keep selective dividend pathways distinct and suppress generic claims.
  stage3: Produce a dedicated climate-FCV note. Write the two interaction directions as prose (not a causal strip), a reflections read on the material core questions, and one qualitative dividends synthesis distinguishing what the project funds from how it is delivered. Integrate material findings into one common priority list of at most five substantive priorities, add a wider_fcv_context note for any material non-climate FCV issue, and avoid generic climate advice.
```
(If the combined Stage 2 slice now exceeds 2000 est-tokens, trim wording — the test's ceiling assertion guards this.)

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_climate_lens_package.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add sector_lenses/modules/climate/manifest.yaml tests/test_climate_lens_package.py
git commit -m "feat: sync climate manifest stage instructions with dedicated module"
```

---

### Task 4.3: Full-suite regression + parity-log + CLAUDE.md update

**Files:** run full suite; update `C:/Users/wb559324/.claude/FCV_BUILD_PARITY.md` (local, not committed here) and `CLAUDE.md` version history.

- [ ] **Step 1: Full focused + whole-suite run**
```
python -m pytest tests/test_climate_research.py tests/test_climate_ccdr_context.py tests/test_climate_lens_package.py tests/test_sector_lens_pipeline.py tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py tests/test_extract_priorities.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
python -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```
Expected: all green (baseline was 325 full-suite; expect 325 + the new tests).

- [ ] **Step 2:** `python -m py_compile app.py` → passes. `git diff --check` → clean.

- [ ] **Step 3:** Append a `v9.19` entry to the worktree `CLAUDE.md` version history summarising: dedicated Climate module output; six core questions as Stage 2 spine; `reflections`/`integration_level`/`integration_summary`/`less_central` diagnostic fields; `wider_fcv_context` Stage 3 field; single integration gauge; prose interaction boxes; reorder; DOCX/HTML parity. Record the contract additions in `C:/Users/wb559324/.claude/FCV_BUILD_PARITY.md` for the ITS build.

- [ ] **Step 4: Commit**
```bash
git add CLAUDE.md
git commit -m "docs: record v9.19 climate dedicated module in claude.md"
```

---

## Notes for the executor

- **Confirm in-scope variable names when editing large functions.** Where this plan references a variable at an edit site (for example the parsed Stage-3 dict name in `renderOut`, or `lens_diagnostic` at the SSE done sites, or `priorities_payload`/`climate_readout` in `download_report`), read the surrounding 20 lines and substitute the real local name. The behaviour and code shown are correct; only the binding name may differ.
- **Frontend tests need Node on PATH.** If Node is unavailable they fail (not skip); install or run on a machine with Node.
- **Do not weaken** source/specificity/horizon/priority-link validation to make output look fuller (per the 23 July guidance).
- **Do not read the restricted OPCS corpus** (per `CLAUDE.md`).
