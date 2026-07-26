# Climate-FCV Output Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the selected Climate-FCV module explicit, materiality-scaled, analytically substantive, and identical across the live Recommendations Note, downloaded HTML, and DOCX.

**Architecture:** Extend the existing normalized lens diagnostic with a validated materiality level, two fixed interaction directions, richer dividend pathways, and bounded additional pathways. Keep Stage 3's common five-priority list, then render Option A conditionally from the same normalized diagnostic while leaving the core-only note unchanged. Treat Option B as a future renderer switch, not a second model contract.

**Tech Stack:** Python 3, Flask, dataclasses, PyYAML, vanilla JavaScript and CSS in `index.html`, python-docx, pytest, Node.js contract tests.

---

## File map

- `sector_lenses/pipeline.py`: validate and normalize the extended diagnostic.
- `sector_lenses/modules/climate/manifest.yaml`: bump the module version and update readout titles and stage instructions.
- `sector_lenses/modules/climate/guidance.md`: define materiality scaling, development-project co-benefit screening, layer separation, and suppression rules.
- `sector_lenses/modules/climate/questions.yaml`: collect evidence for both interaction directions and the current-contribution/strengthening anatomy.
- `app.py`: update Stage 2 and Stage 3 prompt contracts, bounded Stage 3 context, omission warnings, and DOCX rendering.
- `index.html`: add reusable Option A renderers, styles, live wiring, HTML export parity, and safe fallback.
- `tests/test_sector_lens_pipeline.py`: normalization and invalid-input coverage.
- `tests/test_climate_lens_package.py`: production package and version contract.
- `tests/test_sector_lens_app_contract.py`: prompt, budget, provenance warning, and DOCX parity coverage.
- `tests/test_climate_lens_frontend.py`: JavaScript renderer, order, escaping, materiality, and export parity coverage.
- `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`: local-only shared-contract log; never stage or commit.

## Task 1: Normalize the extended Climate-FCV diagnostic

**Files:**
- Modify: `tests/test_sector_lens_pipeline.py`
- Modify: `sector_lenses/pipeline.py`

- [ ] **Step 1: Write failing normalization tests**

Add a reusable Climate payload and assertions covering valid materiality, both interaction directions, richer baseline items, bounded additional pathways, invalid identifiers, source filtering, and legacy applicability mapping:

```python
def test_climate_diagnostic_normalizes_materiality_interactions_and_pathways():
    payload = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "materiality_level": "high",
        "materiality_summary": "Flood and fragility pressures are central.",
        "source_ids": ["peace-social-dividends", "invented"],
        "interaction_readout": [{
            "direction_id": "climate-fcv-on-project",
            "summary": "Flood, displacement, and weak access could disrupt delivery.",
            "mechanisms": ["Flood damage combines with insecurity."],
            "project_implications": ["Remote sites may become inaccessible."],
            "positive_effects": [],
            "adverse_effects": ["Infrastructure completion may be delayed."],
            "evidence": ["The PCN identifies flood-prone sites."],
            "evidence_gap": "Site-level access data are incomplete.",
            "source_ids": ["peace-social-dividends", "invented"],
        }, {
            "direction_id": "project-on-climate-fcv",
            "summary": "Benefit rules could strengthen resilience or deepen exclusion.",
            "mechanisms": ["Co-management changes access to natural resources."],
            "project_implications": ["Customary users need representation."],
            "positive_effects": ["More legitimate resource rules."],
            "adverse_effects": ["Seasonal users could be excluded."],
            "evidence": ["Community institutions allocate access."],
            "evidence_gap": "Seasonal users are not mapped.",
            "source_ids": ["peace-social-dividends"],
        }],
        "readout_sections": [{
            "section_id": "invest-in",
            "items": [{
                "item_id": "livelihoods-opportunity",
                "status": "supported",
                "mechanism": "Diversified livelihoods reduce climate exposure.",
                "project_contribution": "The project finances resilient livelihoods.",
                "strengthening_action": "Clarify access and benefit-sharing rules.",
                "evidence": ["A livelihoods component is financed."],
                "source_ids": ["peace-social-dividends"],
            }],
        }],
        "additional_pathways": [{
            "section_id": "invest-in",
            "title": "Shared ecosystem restoration",
            "status": "potential",
            "mechanism": "Joint restoration can create collective benefits.",
            "project_contribution": "The project restores shared watersheds.",
            "strengthening_action": "Define joint oversight and dispute resolution.",
            "evidence": ["Watershed restoration is included."],
            "source_ids": ["peace-social-dividends"],
        }],
    }], "findings": []}
    schema = {"climate": {
        "invest-in": {"livelihoods-opportunity"},
        "deliver-through": {"flexible-adaptive-delivery"},
    }}

    result = normalize_lens_diagnostic(
        payload,
        ["climate"],
        {"climate": {"peace-social-dividends"}},
        schema,
    )

    climate = result["lenses"][0]
    assert climate["materiality_level"] == "high"
    assert [item["direction_id"] for item in climate["interaction_readout"]] == [
        "climate-fcv-on-project", "project-on-climate-fcv",
    ]
    assert climate["interaction_readout"][0]["source_ids"] == [
        "peace-social-dividends"
    ]
    pathway = climate["readout_sections"][0]["items"][0]
    assert pathway["project_contribution"].startswith("The project finances")
    assert pathway["strengthening_action"].startswith("Clarify access")
    assert climate["additional_pathways"][0]["title"] == (
        "Shared ecosystem restoration"
    )


def test_climate_diagnostic_rejects_invalid_extensions_and_maps_legacy_low():
    payload = {"lenses": [{
        "lens_id": "climate",
        "applicability": "not_applicable",
        "materiality_level": "extreme",
        "interaction_readout": [{
            "direction_id": "invented-direction",
            "summary": "Drop this.",
        }],
        "additional_pathways": [{
            "section_id": "invented-section",
            "title": "Drop this",
            "status": "supported",
            "project_contribution": "Unsupported.",
            "strengthening_action": "Unsupported.",
            "evidence": ["Unsupported."],
        }],
    }], "findings": []}

    result = normalize_lens_diagnostic(
        payload,
        ["climate"],
        {"climate": {"peace-social-dividends"}},
        {"climate": {"invest-in": {"livelihoods-opportunity"}}},
    )

    climate = result["lenses"][0]
    assert climate["materiality_level"] == "low"
    assert climate["interaction_readout"] == []
    assert climate["additional_pathways"] == []
```

- [ ] **Step 2: Run the new tests and confirm they fail**

Run:

```powershell
python -m pytest tests/test_sector_lens_pipeline.py -k "climate_diagnostic" -v
```

Expected: FAIL because `materiality_level`, `interaction_readout`, `project_contribution`, `strengthening_action`, and `additional_pathways` are not normalized yet.

- [ ] **Step 3: Implement bounded normalization**

Add constants and normalization inside `extract_lens_diagnostic()`:

```python
_MATERIALITY_LEVELS = {"high", "medium", "low"}
_INTERACTION_DIRECTIONS = {
    "climate-fcv-on-project",
    "project-on-climate-fcv",
}


def _bounded_strings(value: Any, limit: int, length: int) -> list[str]:
    return [
        str(item).strip()[:length]
        for item in _list_values(value)
        if str(item).strip()
    ][:limit]
```

For the active `climate` lens, map missing or invalid legacy materiality deterministically, normalize at most two fixed interactions, preserve the richer baseline fields, and accept at most two evidence-backed additional pathways per declared section:

```python
raw_level = str(item.get("materiality_level", "")).lower()
if lens_id == "climate":
    if raw_level not in _MATERIALITY_LEVELS:
        raw_level = "medium" if applicability == "material" else "low"
else:
    raw_level = raw_level if raw_level in _MATERIALITY_LEVELS else ""

normalized_interactions: list[dict[str, Any]] = []
if lens_id == "climate":
    seen_directions: set[str] = set()
    for raw_interaction in item.get("interaction_readout", []):
        if not isinstance(raw_interaction, dict):
            continue
        direction_id = str(raw_interaction.get("direction_id", ""))
        if direction_id not in _INTERACTION_DIRECTIONS or direction_id in seen_directions:
            continue
        seen_directions.add(direction_id)
        interaction_sources = list(dict.fromkeys(_bounded_strings(
            raw_interaction.get("source_ids"), 10, 200
        )))
        if source_ids_by_lens is not None:
            interaction_sources = [
                source_id for source_id in interaction_sources
                if source_id in source_ids_by_lens.get(lens_id, set())
            ]
        normalized_interactions.append({
            "direction_id": direction_id,
            "summary": str(raw_interaction.get("summary", "")).strip()[:700],
            "mechanisms": _bounded_strings(raw_interaction.get("mechanisms"), 3, 350),
            "project_implications": _bounded_strings(
                raw_interaction.get("project_implications"), 3, 350
            ),
            "positive_effects": _bounded_strings(
                raw_interaction.get("positive_effects"), 3, 350
            ),
            "adverse_effects": _bounded_strings(
                raw_interaction.get("adverse_effects"), 3, 350
            ),
            "evidence": _bounded_strings(raw_interaction.get("evidence"), 5, 500),
            "evidence_gap": str(
                raw_interaction.get("evidence_gap", "")
            ).strip()[:500],
            "source_ids": interaction_sources,
        })
```

Add `project_contribution` and `strengthening_action` to each normalized baseline item. Add `additional_pathways` to the lens object only after validating section, status, title, evidence, contribution, strengthening action, and source IDs.

- [ ] **Step 4: Run pipeline tests**

Run:

```powershell
python -m pytest tests/test_sector_lens_pipeline.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit Task 1**

```powershell
git add sector_lenses/pipeline.py tests/test_sector_lens_pipeline.py
git commit -m "feat: normalize climate FCV output contract"
```

## Task 2: Update the Climate package and stage prompt contract

**Files:**
- Modify: `tests/test_climate_lens_package.py`
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `sector_lenses/modules/climate/manifest.yaml`
- Modify: `sector_lenses/modules/climate/guidance.md`
- Modify: `sector_lenses/modules/climate/questions.yaml`
- Modify: `app.py`

- [ ] **Step 1: Write failing package and prompt tests**

Update the expected Climate module version to `1.1.0` and assert the new titles. Add prompt assertions:

```python
def test_active_climate_stage2_requests_materiality_interactions_and_pathways():
    state = app_module.AnalysisState.from_payload({"active_lenses": ["climate"]})

    prompt = app_module.build_lens_stage_context(state, 2)["prompt"]

    for field in (
        "materiality_level", "interaction_readout", "project_contribution",
        "strengthening_action", "additional_pathways",
    ):
        assert field in prompt
    assert "development project" in prompt
    assert "not its primary objective" in prompt


def test_active_climate_stage3_preserves_option_a_layers_and_gradient():
    state = app_module.AnalysisState.from_payload({"active_lenses": ["climate"]})
    diagnostic = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "materiality_level": "high",
        "materiality_summary": "Flood and FCV pressures are central.",
        "interaction_readout": [{
            "direction_id": "climate-fcv-on-project",
            "summary": "Flood and insecurity could disrupt delivery.",
        }],
        "readout_sections": [],
        "additional_pathways": [],
    }], "findings": []}

    prompt = app_module.build_lens_stage_context(
        state, 3, lens_diagnostic=diagnostic
    )["prompt"]

    assert "High, Medium, or Low" in prompt
    assert "executive summary" in prompt
    assert "two-way Climate-FCV interaction" in prompt
    assert "current contribution" in prompt
    assert "how it could be strengthened" in prompt
    assert "not a quota" in prompt
    assert "Flood and insecurity could disrupt delivery" in prompt
```

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run:

```powershell
python -m pytest tests/test_climate_lens_package.py tests/test_sector_lens_app_contract.py -k "climate" -v
```

Expected: FAIL on version, titles, new fields, and prompt language.

- [ ] **Step 3: Update the production Climate package**

In `manifest.yaml`:

```yaml
version: 1.1.0
readout_sections:
  - id: invest-in
    title: Where the project could build climate, peace, and social dividends
    item_ids:
      - social-cohesion-inclusion
      - institutional-capacity-legitimacy
      - livelihoods-opportunity
  - id: deliver-through
    title: How project design and delivery could strengthen those dividends
    item_ids:
      - context-analysis-monitoring
      - trust-collaboration
      - flexible-adaptive-delivery
```

Rewrite the three stage instructions so Stage 1 collects evidence, Stage 2 assigns the gradient and distinct layers, and Stage 3 preserves executive-summary depth while ranking one common priority list.

Expand `guidance.md` with these enforceable rules:

```markdown
Selection is authoritative. Screen dedicated climate operations and wider development projects for component-level climate risks, resilience effects, adaptation opportunities, mitigation effects, and climate co-benefits. Climate need not be the primary objective.

Assign High, Medium, or Low materiality before choosing depth. High and Medium use the same analytical architecture at different depth. Low remains explicit and introduces a light climate emphasis rather than hiding the selected module.

Keep four output layers distinct: executive-summary FCV assessment; two-way Climate-FCV interactions; climate, peace, and social dividend pathways; and actionable priorities. For each displayed dividend pathway state the current project contribution and how it could be strengthened. Suppress weak and not-material pathways. The six baseline dimensions are prompts, not mandatory headings; add no more than two evidence-backed project-specific pathways per section.
```

Update the materiality, project influence, compound risk, and dividend question text so the model has direct evidence prompts for every new field without increasing the 19-question count.

- [ ] **Step 4: Extend Stage 2 and Stage 3 prompt serialization**

In `build_lens_stage_context()` require the new Stage 2 fields and explicitly state the development-project rule. Extend `_bounded_stage3_lenses()` to retain:

```python
"materiality_level": raw.get("materiality_level", "low"),
"interaction_readout": [],
"additional_pathways": [],
```

For each retained baseline and additional pathway include bounded `project_contribution` and `strengthening_action`. For interactions retain fixed direction, summary, up to two mechanisms or implications, evidence gap, and source IDs. Continue using the existing 900-token platform ceiling and drop detail from the end when necessary.

Update the Climate Stage 3 prefix to distinguish the four analytical layers, preserve the full executive summary, apply the High/Medium/Low gradient, suppress empty pathways, and retain the common maximum-five priority rule.

Return the validated diagnostic inside the internal context object so later workflow checks use the same normalized data:

```python
"lens_diagnostic": normalized_diagnostic if stage == 3 else {},
```

- [ ] **Step 5: Run package and app contract tests**

Run:

```powershell
python -m pytest tests/test_climate_lens_package.py tests/test_sector_lens_app_contract.py -v
```

Expected: all tests PASS, including the large-diagnostic token ceiling.

- [ ] **Step 6: Commit Task 2**

```powershell
git add app.py sector_lenses/modules/climate/manifest.yaml sector_lenses/modules/climate/guidance.md sector_lenses/modules/climate/questions.yaml tests/test_climate_lens_package.py tests/test_sector_lens_app_contract.py
git commit -m "feat: strengthen climate FCV generation contract"
```

## Task 3: Build safe, reusable Option A frontend renderers

**Files:**
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `index.html`

- [ ] **Step 1: Write failing JavaScript renderer tests**

Add tests that extract and execute these functions with Node:

- `climateMaterialityLevel()`
- `renderClimateModuleNotice()`
- `renderClimateInteractions()`
- `renderClimateDividends()`
- `renderSRNarrative()`

Use a helper bundle so dependencies are loaded in definition order. The test data must contain script tags in every free-text field and assert that no raw `<script>` survives.

```python
def test_option_a_renderers_scale_materiality_suppress_weak_items_and_escape():
    source = INDEX.read_text(encoding="utf-8")
    names = [
        "climateMaterialityLevel", "renderClimateModuleNotice",
        "renderClimateInteractions", "renderClimateDividends",
        "renderSRNarrative",
    ]
    helpers = "\n".join(_extract_js_function(source, name) for name in names)
    script = f"""
const esc = value => String(value ?? '')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
  .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
{helpers}
const high = {{
  materiality_level:'high', materiality_summary:'Central <script>bad()</script>',
  interaction_readout:[
    {{direction_id:'climate-fcv-on-project',summary:'Flood and insecurity disrupt access.'}},
    {{direction_id:'project-on-climate-fcv',summary:'Benefit rules can build trust or exclusion.'}}
  ],
  readout_sections:[{{section_id:'invest-in',items:[
    {{item_id:'livelihoods-opportunity',status:'supported',
      project_contribution:'Resilient livelihoods.',
      strengthening_action:'Clarify benefit sharing.',evidence:['PCN component.']}},
    {{item_id:'social-cohesion-inclusion',status:'not_material',
      project_contribution:'Do not show.',strengthening_action:'Do not show.'}}
  ]}}], additional_pathways:[]
}};
const notice=renderClimateModuleNotice(high,false);
const interactions=renderClimateInteractions(high);
const dividends=renderClimateDividends(high,{{readout_sections:[
  {{id:'invest-in',title:'Where the project could build climate, peace, and social dividends'}},
  {{id:'deliver-through',title:'How project design and delivery could strengthen those dividends'}}
]}});
if(!notice.includes('strong climate emphasis')) throw new Error(notice);
if(!interactions.includes('How Climate-FCV interactions could affect the project')) throw new Error(interactions);
if(!dividends.includes('How the project may contribute')) throw new Error(dividends);
if(!dividends.includes('How this could be strengthened')) throw new Error(dividends);
if(dividends.includes('Do not show')) throw new Error(dividends);
if((notice+interactions+dividends).includes('<script>')) throw new Error('unsafe HTML');
const low={{materiality_level:'low',materiality_summary:'Limited.',readout_sections:[],additional_pathways:[]}};
if(!renderClimateModuleNotice(low,false).includes('limited climate materiality')) throw new Error('low disclosure missing');
if(renderClimateDividends(low,{{readout_sections:[]}})!=='') throw new Error('empty low dividends rendered');
const errorNotice=renderClimateModuleNotice(null,true);
if(!errorNotice.includes('could not be produced')) throw new Error('safe failure missing');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
```

- [ ] **Step 2: Run the frontend tests and confirm they fail**

Run:

```powershell
python -m pytest tests/test_climate_lens_frontend.py -v
```

Expected: FAIL because the Option A helpers do not exist.

- [ ] **Step 3: Implement frontend data and rendering helpers**

Add pure helpers near the existing lens renderers. Use fixed labels and deterministic tier limits:

```javascript
function climateMaterialityLevel(lens){
  const level=String(lens&&lens.materiality_level||'').toLowerCase();
  if(['high','medium','low'].includes(level))return level;
  return lens&&lens.applicability==='material'?'medium':'low';
}

function isClimateLensActive(){
  return Array.isArray(activeLenses)&&activeLenses.includes('climate');
}

function climateLensEntry(diagnostic){
  const lenses=diagnostic&&Array.isArray(diagnostic.lenses)?diagnostic.lenses:[];
  return lenses.find(item=>item&&item.lens_id==='climate')||null;
}
```

`renderClimateModuleNotice(lens, diagnosticError)` must always disclose selection, use High/Medium/Low wording, include the approved evidence-base sentence, and show a safe-failure message when the diagnostic is missing or invalid.

`renderClimateInteractions(lens)` must accept only the two fixed direction IDs, escape all text, and render Low compactly.

`renderClimateDividends(lens, catalogueLens)` must:

- show only `supported` or evidence-backed `potential` pathways;
- require both contribution and strengthening text;
- suppress `not_material` and empty groups;
- merge baseline and validated additional pathways;
- limit High to six cards, Medium to four, and Low to one;
- use the approved project-led introduction.

`renderSRNarrative()` must render full FCV Sensitivity and FCV Responsiveness paragraphs as ordinary prose with optional rating labels, not as cards.

- [ ] **Step 4: Add Option A styles**

Add scoped CSS classes for:

```css
.climate-module-notice {}
.climate-materiality-pill {}
.climate-interaction-grid {}
.climate-interaction-card {}
.climate-dividends-section {}
.climate-dividend-groups {}
.climate-dividend-card {}
.sr-narrative-section {}
```

Use the existing blue lens palette, teal dividends palette, responsive one-column breakpoints, and print-safe borders. Do not alter core S/R card styles because core-only mode still uses them.

- [ ] **Step 5: Run frontend tests**

Run:

```powershell
python -m pytest tests/test_climate_lens_frontend.py -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit Task 3**

```powershell
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: add climate FCV option A renderers"
```

## Task 4: Wire Option A into the live Recommendations Note

**Files:**
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `index.html`

- [ ] **Step 1: Write a failing live-order contract test**

Extract the `renderOut()` body and assert that the climate path uses the required order and core mode retains the existing helpers:

```python
def test_live_stage3_orders_option_a_and_preserves_core_fallback():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "renderOut")

    climate_order = [
        "renderClimateModuleNotice",
        "renderSRNarrative",
        "renderClimateInteractions",
        "renderClimateDividends",
    ]
    positions = [helper.index(name) for name in climate_order]
    assert positions == sorted(positions)
    assert "isClimateLensActive" in helper
    assert "renderRiskExposure(stageRiskExposure)" in helper
    assert "renderSRCards(stageSensitivitySummary,stageResponsivenessSummary)" in helper
```

- [ ] **Step 2: Run the test and confirm it fails**

Run:

```powershell
python -m pytest tests/test_climate_lens_frontend.py -k "live_stage3" -v
```

Expected: FAIL because `renderOut()` still renders core risk and S/R cards for all runs.

- [ ] **Step 3: Add the conditional live assembly**

Inside the Stage 3 branch of `renderOut()` compute:

```javascript
const _climateActive=isClimateLensActive();
const _climateEntry=climateLensEntry(lensDiagnostic);
const _climateError=_climateActive&&(
  !lensDiagnostic||lensDiagnostic.error||!_climateEntry
);
const _climateNotice=_climateActive
  ?renderClimateModuleNotice(_climateEntry,_climateError):'';
const _climateValid=_climateActive&&!_climateError;
```

For valid Climate mode assemble:

```javascript
_closedProjectNotice+_padNotice+_stageBadge+_climateNotice+
_preHtml+md(_rest)+
renderSRNarrative(
  stageSensitivitySummary,stageResponsivenessSummary,
  fcvRating,fcvResponsivenessRating
)+
renderClimateInteractions(_climateEntry)+
renderClimateDividends(
  _climateEntry,lensCatalogue.find(item=>item.id==='climate')||{}
)
```

For core-only or malformed Climate mode retain the current `renderRiskExposure()` and `renderSRCards()` behavior. In malformed Climate mode prepend the safe notice but do not render unvalidated climate sections.

- [ ] **Step 4: Run frontend tests**

Run:

```powershell
python -m pytest tests/test_climate_lens_frontend.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit Task 4**

```powershell
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: integrate climate FCV option A in live note"
```

## Task 5: Make downloaded HTML match the live note

**Files:**
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `index.html`

- [ ] **Step 1: Write a failing HTML export parity test**

```python
def test_download_html_uses_same_climate_sections_and_order():
    source = INDEX.read_text(encoding="utf-8")
    helper = _extract_js_function(source, "downloadHTML")

    assert "isClimateLensActive" in helper
    required = [
        "renderClimateModuleNotice",
        "wrapSRTerms(md(summarybody))",
        "renderSRNarrative",
        "renderClimateInteractions",
        "renderClimateDividends",
    ]
    positions = [helper.index(value) for value in required]
    assert positions == sorted(positions)
    assert "renderRiskExposure(stageRiskExposure)" in helper
    assert "renderSRCards(stageSensitivitySummary, stageResponsivenessSummary)" in helper
```

- [ ] **Step 2: Run the test and confirm it fails**

Run:

```powershell
python -m pytest tests/test_climate_lens_frontend.py -k "download_html" -v
```

Expected: FAIL because the exporter omits the lens diagnostic.

- [ ] **Step 3: Reuse the Option A renderers in `downloadHTML()`**

Apply the same climate state calculation and conditional order as the live note. Do not copy card markup into the exporter. Reuse the pure helpers so the only export-specific logic remains the document shell, title, inline CSS, and annexes.

Core-only export must retain its existing risk exposure, S/R cards, ratings, priorities, and annexes.

- [ ] **Step 4: Run frontend tests**

Run:

```powershell
python -m pytest tests/test_climate_lens_frontend.py -v
```

Expected: all tests PASS and the original omission regression is covered.

- [ ] **Step 5: Commit Task 5**

```powershell
git add index.html tests/test_climate_lens_frontend.py
git commit -m "fix: preserve climate FCV readout in HTML export"
```

## Task 6: Bring DOCX into content parity

**Files:**
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `app.py`

- [ ] **Step 1: Replace the existing DOCX climate fixture with the extended contract**

Use High materiality, both interaction directions, a supported baseline pathway, a suppressed `not_material` pathway, and an additional pathway. Include S/R summaries and ratings. Assert paragraph order:

```python
assert text.index("Climate-focused FCV assessment") < text.index("Summary.")
assert text.index("FCV Sensitivity") < text.index(
    "How Climate-FCV interactions could affect the project"
)
assert text.index("FCV Responsiveness") < text.index(
    "How Climate-FCV interactions could affect the project"
)
assert "How the project may contribute" in text
assert "How this could be strengthened" in text
assert "Do not render this pathway" not in text
assert "Other pathways considered" not in text
```

Add a Low-materiality test that asserts the limited-materiality disclosure and no empty dividends headings. Add a malformed-diagnostic test that asserts the safe-failure notice plus retained `FCV Risk Exposure`.

- [ ] **Step 2: Run the DOCX tests and confirm they fail**

Run:

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -k "downloaded_report" -v
```

Expected: FAIL on notice, order, interaction headings, pathway anatomy, Low behavior, and safe fallback.

- [ ] **Step 3: Add shared Python Climate readout helpers**

Add small pure helpers before the report route:

```python
def climate_lens_entry(diagnostic: dict[str, Any]) -> dict[str, Any] | None:
    lenses = diagnostic.get("lenses", []) if isinstance(diagnostic, dict) else []
    return next((
        item for item in lenses
        if isinstance(item, dict) and item.get("lens_id") == "climate"
    ), None)


def climate_materiality_level(lens: dict[str, Any] | None) -> str:
    level = str((lens or {}).get("materiality_level", "")).lower()
    if level in {"high", "medium", "low"}:
        return level
    return "medium" if (lens or {}).get("applicability") == "material" else "low"
```

Add a filtered pathway iterator that applies the same status, completeness, evidence, and High/Medium/Low limits as the JavaScript renderer.

- [ ] **Step 4: Reorder and rewrite the DOCX primary readout**

After the report header and any lifecycle notice:

1. add the Climate-focused FCV assessment notice when selected;
2. add the full narrative summary;
3. add FCV Sensitivity and FCV Responsiveness prose;
4. for a valid Climate diagnostic, replace FCV Risk Exposure with both Climate-FCV interaction headings;
5. add the project-led dividends introduction and selected pathway anatomy;
6. continue to the common priorities and annexes.

For core-only and malformed Climate diagnostics retain FCV Risk Exposure. For malformed Climate, add the safe-failure notice and suppress interaction/dividend content.

- [ ] **Step 5: Run app contract tests**

Run:

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit Task 6**

```powershell
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: align climate FCV DOCX output"
```

## Task 7: Add priority provenance warning and final regressions

**Files:**
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `app.py`

- [ ] **Step 1: Write a failing High-materiality omission-warning test**

```python
def test_high_climate_materiality_warns_when_priorities_drop_provenance(caplog):
    diagnostic = {"lenses": [{
        "lens_id": "climate",
        "materiality_level": "high",
    }]}

    with caplog.at_level("WARNING"):
        warning = app_module.warn_on_missing_high_climate_priority(
            [{"title": "Core priority", "lens_ids": []}], diagnostic
        )

    assert warning is True
    assert "High Climate-FCV materiality" in caplog.text
    caplog.clear()
    assert app_module.warn_on_missing_high_climate_priority(
        [{"title": "Climate priority", "lens_ids": ["climate"]}], diagnostic
    ) is False
```

- [ ] **Step 2: Run the warning test and confirm it fails**

Run:

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -k "missing_high_climate" -v
```

Expected: FAIL because the helper does not exist.

- [ ] **Step 3: Implement and wire the non-blocking warning**

```python
def warn_on_missing_high_climate_priority(
    priorities: list[dict[str, Any]],
    diagnostic: dict[str, Any],
) -> bool:
    climate = climate_lens_entry(diagnostic)
    if climate_materiality_level(climate) != "high":
        return False
    if any("climate" in priority.get("lens_ids", []) for priority in priorities):
        return False
    app.logger.warning(
        "High Climate-FCV materiality produced no climate-tagged priority; "
        "review Stage 3 ranking and provenance extraction."
    )
    return True
```

Call it after Stage 3 priority extraction in both step-by-step and express workflows, using `lens_context_s3["lens_diagnostic"]` or the corresponding step-by-step context key. It is a warning only and must not create a quota or fail the run.

- [ ] **Step 4: Run focused and core regression tests**

Run:

```powershell
python -m pytest tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py tests/test_climate_lens_package.py tests/test_sector_lens_pipeline.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit Task 7**

```powershell
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "chore: warn on lost climate priority provenance"
```

## Task 8: Cross-build parity, end-to-end verification, and branch publication

**Files:**
- Modify locally only: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`
- Verify: all changed repository files

- [ ] **Step 1: Log the shared contract change locally**

Add a dated entry recording:

```markdown
### 2026-07-22: Climate-FCV output diagnostic v1.1

- Render/Azure parity surface: sector-lens Stage 2 diagnostic and Stage 3 compact context.
- New Climate fields: `materiality_level`, `interaction_readout`, baseline `project_contribution`, baseline `strengthening_action`, and bounded `additional_pathways`.
- Fixed interaction IDs: `climate-fcv-on-project`, `project-on-climate-fcv`.
- Priority JSON fields and enums are unchanged; `lens_ids` and `lens_relevance` retain their existing contract.
- Azure build must mirror normalization, prompts, materiality behavior, and safe failure before accepting the v1.1 Climate package.
```

Confirm with `git status` that this local parity file is not part of the repository and is not staged.

- [ ] **Step 2: Run the complete automated test suite**

Run:

```powershell
python -m pytest -q
```

Expected: zero failed tests.

- [ ] **Step 3: Run repository diff and syntax checks**

Run:

```powershell
git diff --check
python -m py_compile app.py sector_lenses/pipeline.py
node --check index.html
```

If `node --check index.html` rejects the HTML wrapper rather than JavaScript syntax, run the repository's existing frontend contract tests as the authoritative JavaScript check and record that result instead of treating the wrapper error as a code failure.

Expected: `git diff --check` and Python compilation exit 0; frontend contract tests pass.

- [ ] **Step 4: Perform a manual three-tier render check**

Use the existing local application and deterministic test diagnostics to inspect:

- High: full notice, full executive summary, S/R prose, two interactions, several selective dividend pathways, priorities below.
- Medium: same layout with fewer pathways and focused wording.
- Low: explicit limited-materiality notice, compact interaction, no empty dividends, no forced climate priority.
- Core only: unchanged risk exposure and S/R cards.
- Malformed diagnostic: safe notice plus core FCV fallback.

Export the High case to HTML and DOCX and confirm the same headings and substantive text appear in the same order.

- [ ] **Step 5: Run the final staged-scope verification**

Run:

```powershell
git status --short
git diff --stat origin/codex/sector-lens-platform...HEAD
git log --oneline origin/codex/sector-lens-platform..HEAD
```

Expected: only planned code, test, package, design, and plan files are present. The visual companion and local parity file are absent.

- [ ] **Step 6: Commit any final verified repository-only adjustments**

```powershell
git add app.py index.html sector_lenses tests docs/superpowers
git diff --cached --check
git commit -m "test: verify climate FCV output parity"
```

Skip this commit if no repository changes remain after the preceding task commits.

- [ ] **Step 7: Push the new branch**

```powershell
git push -u origin codex/climate-fcv-output-redesign
```

Expected: the remote branch is created and local tracking is configured.
