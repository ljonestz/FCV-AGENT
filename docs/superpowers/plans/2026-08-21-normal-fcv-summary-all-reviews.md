# Normal FCV Summary Across All Reviews Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every normal FCV Stage 3 review open with a validated five-minute Summary while preserving the comprehensive Detailed analysis and adding the approved advisory transition to both normal and Climate + FCV summaries.

**Architecture:** Add optional `concise_readout` and `priority.concise` fields to the existing core Stage 3 JSON, validate them independently, and transport them through both SSE workflows. A shared frontend shell renders either the normal concise bundle or the verified climate reader; invalid concise data falls back to Detailed without another model call.

**Tech Stack:** Python 3.10+, Flask, vanilla JavaScript, HTML/CSS, pytest, Node.js frontend checks.

---

## Context and File Map

- Work in `C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT/.worktrees/climate-summary-direct` on `codex/climate-summary-quality-fixes`.
- Follow `docs/superpowers/specs/2026-08-21-normal-fcv-summary-all-reviews-design.md`.
- Use `codex/concise-stage3-readout` only as a reference; do not merge or cherry-pick it wholesale.
- Modify `app.py`: prompt contract, lifecycle context, normalization, parsing, and SSE payloads.
- Modify `index.html`: state, shared summary shell, ratings, advisory text, accordions, restoration, and export boundaries.
- Create `tests/test_concise_stage3_contract.py`.
- Modify `tests/test_extract_priorities.py` and `tests/test_climate_lens_frontend.py`.
- Update local-only `C:/Users/wb559324/.claude/FCV_BUILD_PARITY.md`; never stage it.

## Task 1: Validate the Concise Bundle Independently

**Files:** `app.py:5957-6165`, `tests/test_concise_stage3_contract.py`, `tests/test_extract_priorities.py`

- [ ] **Step 1: Write failing parser tests**

Create a Stage 3 JSON fixture with valid detailed fields, two priorities, this top-level object, and a `concise` object on each priority:

```python
CONCISE_READOUT = {
    "headline": "FCV risks are recognized, but key delivery choices remain unresolved.",
    "overview": " ".join(["The operation faces material access, exclusion, and legitimacy risks."] * 18),
    "strengths": [
        {"title": "Context awareness", "text": "The document identifies the main FCV pressures."},
        {"title": "Community feedback", "text": "The design includes beneficiary feedback channels."},
        {"title": "Adaptive delivery", "text": "Implementation arrangements allow bounded adjustment."},
    ],
}

CONCISE_PRIORITY = {
    "title": "Define access triggers",
    "why": "The unresolved choice affects access, inclusion, and delivery.",
    "how": ["Define the trigger and owner.", "Record the response in the current instrument."],
    "suggested_wording": {"document_element": "Implementation arrangements", "text": "Review access conditions quarterly."},
    "project_cycle": {
        "primary_label": "Address during implementation",
        "primary_text": "Agree the trigger, response, and owner now.",
        "secondary_label": "Track through the ISR",
        "secondary_text": "Report activation through routine implementation reporting.",
    },
}
```

Assert a complete bundle is returned. Then remove one priority's `concise` field and assert detailed parsing still succeeds, `concise_readout is None`, and all partial `concise` fields are removed. Add cases for an overview below 100 words, fewer than three strengths, fewer than two `how` actions, and missing primary lifecycle text.

- [ ] **Step 2: Verify failure**

Run `python -m pytest tests/test_concise_stage3_contract.py tests/test_extract_priorities.py -q`.

Expected: FAIL because `extract_priorities()` does not return or normalize concise fields.

- [ ] **Step 3: Implement minimal normalizers**

Add before `extract_priorities()`:

```python
def _clean_concise_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _normalize_concise_readout(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict) or not isinstance(value.get("strengths"), list):
        return None
    headline = _clean_concise_string(value.get("headline"))
    overview = _clean_concise_string(value.get("overview"))
    strengths = [{"title": _clean_concise_string(i.get("title")), "text": _clean_concise_string(i.get("text"))}
                 for i in value["strengths"] if isinstance(i, dict)]
    if not headline or not 100 <= len(overview.split()) <= 250 or len(strengths) != 3:
        return None
    if any(not i["title"] or not i["text"] for i in strengths):
        return None
    return {"headline": headline, "overview": overview, "strengths": strengths}
```

Implement `_normalize_concise_priority(value)` requiring non-empty `title`, `why`, two-to-four `how` strings, and `project_cycle.primary_label` plus `primary_text`. Normalize optional suggested wording and secondary lifecycle fields to empty strings.

After detailed priorities validate, normalize atomically:

```python
readout = _normalize_concise_readout(data.get("concise_readout"))
items = [_normalize_concise_priority(p.get("concise")) for p in priorities]
ratings_ok = bool(str(data.get("fcv_rating", "")).strip() and str(data.get("fcv_responsiveness_rating", "")).strip())
if readout is None or not ratings_ok or any(item is None for item in items):
    readout = None
    for priority in priorities:
        priority.pop("concise", None)
else:
    for priority, item in zip(priorities, items):
        priority["concise"] = item
```

Return `concise_readout: readout`; add `concise_readout: None` to the parser error result.

- [ ] **Step 4: Verify pass and commit**

Run the Step 2 command. Expected: PASS. Then:

```powershell
git add app.py tests/test_concise_stage3_contract.py tests/test_extract_priorities.py
git commit -m "feat: parse normal FCV concise readout"
```

## Task 2: Generate Summaries for Every Core Review

**Files:** `app.py:2980-3080`, `app.py:8507-8755`, `app.py:10510-10679`, `tests/test_concise_stage3_contract.py`

- [ ] **Step 1: Write failing prompt tests**

Parameterize `build_concise_lifecycle_context(doc_type, temporal_context, review_mode)` for:

```python
CASES = [
    ("PCN", {"processing_track": "standard"}, "design", "Commit in the PCN"),
    ("PCN", {"processing_track": "consolidated_condensed"}, "design", "Resolve by Decision Review"),
    ("PAD", {}, "design", "Resolve before the review gate"),
    ("ISR", {}, "implementation", "Address during implementation"),
    ("Additional Financing", {}, "implementation", "Include in the current package"),
    ("Restructuring Paper", {}, "implementation", "Include in the current package"),
    ("Unknown", {}, "design", "When to address"),
]
```

Assert `append_core_concise_stage3_contract("BASE", ..., active_lenses=[])` adds `"concise_readout"` for design and implementation. Assert any active lens returns `"BASE"` unchanged. Assert `app.py` contains two helper call sites in addition to its definition.

- [ ] **Step 2: Verify failure**

Run `python -m pytest tests/test_concise_stage3_contract.py -q`.

Expected: FAIL because lifecycle and prompt helpers do not exist.

- [ ] **Step 3: Add the prompt contract and lifecycle helper**

Add `CONCISE_STAGE3_OUTPUT_CONTRACT` instructing the model to preserve detailed findings, both ratings, priority count/order/actions; target a 150-200 word `overview` covering the approved eight elements; output exactly three strengths; and add a complete `concise` object to every priority. Explicitly prohibit generating the advisory statement because the frontend controls it.

Implement:

```python
def append_core_concise_stage3_contract(stage_prompt, doc_type, temporal_context, review_mode, active_lenses):
    if active_lenses:
        return stage_prompt
    return (stage_prompt + "\n\n--- Concise readout lifecycle framing ---\n"
            + build_concise_lifecycle_context(doc_type, temporal_context, review_mode)
            + "\n\n" + CONCISE_STAGE3_OUTPUT_CONTRACT)
```

Call it after all core Stage 3 instrument/process/category/priority-question guidance is assembled in both Step-by-Step and Express. Pass the resolved active-lens list. Never append it to native climate prompts.

- [ ] **Step 4: Verify and commit**

Run `python -m pytest tests/test_concise_stage3_contract.py tests/test_sector_lens_app_contract.py -q`.

Expected: PASS with climate prompt budgets unchanged. Then:

```powershell
git add app.py tests/test_concise_stage3_contract.py
git commit -m "feat: generate summaries for all FCV reviews"
```

## Task 3: Transport the Validated Bundle

**Files:** `app.py:9288-9334`, `app.py:10776-10780`, `tests/test_concise_stage3_contract.py`

- [ ] **Step 1: Write failing SSE tests**

Using existing Flask test-client and `_stream_stage` monkeypatch patterns, make Stage 3 return the valid fixture. Assert both completion events contain identical `concise_readout` data and complete concise priorities. Repeat with a malformed bundle and assert detailed `result`, priorities, and ratings remain while `concise_readout is None`.

- [ ] **Step 2: Verify failure**

Run `python -m pytest tests/test_concise_stage3_contract.py -k "completion or payload" -q`.

Expected: FAIL because completion events omit `concise_readout`.

- [ ] **Step 3: Add the field to Stage 3 only**

Add `done_data["concise_readout"] = parsed.get("concise_readout")` to Step-by-Step and `"concise_readout": parsed.get("concise_readout")` to Express `_stage3_done`. Do not add it to Stage 1/2 or change climate verified payload generation.

- [ ] **Step 4: Verify and commit**

Run `python -m pytest tests/test_concise_stage3_contract.py -q`. Expected: PASS. Then:

```powershell
git add app.py tests/test_concise_stage3_contract.py
git commit -m "feat: transport normal FCV summaries"
```

## Task 4: Add the Shared Summary Shell and Normal Adapter

**Files:** `index.html:1000-1030`, `index.html:3175-3328`, `index.html:3916-3956`, `index.html:5000-5130`, `index.html:6140-6462`, `tests/test_concise_stage3_contract.py`

- [ ] **Step 1: Write failing frontend tests**

Assert the source declares `stageConciseReadout`, `supportsConciseStage3View()`, `supportsAnyStage3Summary()`, `renderNormalFcvSummary()`, `renderFcvRatingIndicators()`, and `renderStage3Summary()`. A Node renderer test must assert the HTML includes “Five-minute readout,” “Overall assessment,” “What is already working,” “FCV sensitivity,” “FCV responsiveness,” and “Priority actions for the task team.” Assert invalid normal summaries select Detailed and render `concise_readout_unavailable`.

- [ ] **Step 2: Verify failure**

Run `python -m pytest tests/test_concise_stage3_contract.py -k frontend -q`.

Expected: FAIL because normal-summary state and renderers do not exist.

- [ ] **Step 3: Add state and capability gates**

```javascript
let stageConciseReadout=null;
let openSummaryPriority=0;
function supportsConciseStage3View(){
  return activeLenses.length===0 && !!stageConciseReadout && stageThreePriorities.length>0 &&
    stageThreePriorities.every(priority=>priority&&priority.concise);
}
function supportsAnyStage3Summary(){
  return supportsConciseStage3View()||supportsClimateVerifiedStage3View();
}
```

Set `stageConciseReadout=p.concise_readout||null` on both completion paths. Default to Summary only when a capability gate passes; otherwise Detailed. Reset concise state and `openSummaryPriority` with other assessment state.

- [ ] **Step 4: Render the overall assessment**

Implement `renderNormalFcvSummary()` using the validated headline, overview, three strength cards, both existing FCV ratings, `renderStage3AdvisoryTransition('normal')`, and an empty `summary-priority-accordion` host. Implement `renderStage3Summary()` as the route adapter. Capture `stage3DetailedHtml` before substitution. For an unavailable normal bundle, show Detailed plus: “The summary was unavailable for this run; the full analysis is shown.”

- [ ] **Step 5: Verify and commit**

Run `python -m pytest tests/test_concise_stage3_contract.py tests/test_climate_lens_frontend.py -q`.

Expected: PASS with existing climate rendering unchanged. Then:

```powershell
git add index.html tests/test_concise_stage3_contract.py
git commit -m "feat: add shared FCV summary view"
```

## Task 5: Add Accessible Accordions and Shared Advisory Text

**Files:** `index.html:1000-1030`, `index.html:6391-6470`, `index.html:6593-6665`, `tests/test_concise_stage3_contract.py`, `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write failing interaction tests**

Assert `renderSummaryPriorityAccordion()` and `toggleSummaryPriority(idx)` exist; buttons contain `aria-expanded` and `aria-controls`; four normal priorities render four headers; exactly the first begins expanded; opening index 2 collapses index 0. Assert both route renderers call `renderStage3AdvisoryTransition()` and the output contains “not mandatory requirements,” “FCV Country Coordinator,” and “Global Practice experts.”

- [ ] **Step 2: Verify failure**

Run `python -m pytest tests/test_concise_stage3_contract.py tests/test_climate_lens_frontend.py -k "accordion or advisory" -q`.

Expected: FAIL because the current climate summary uses the separate stepper/card area.

- [ ] **Step 3: Implement controlled wording**

```javascript
function renderStage3AdvisoryTransition(route){
  const subject=reviewMode==='implementation'?"project's design and implementation arrangements":"project's design";
  const context=route==='climate'?'climate and FCV':'FCV';
  return `<p class="summary-priority-advisory">The following priorities are suggestions to strengthen the ${subject} in its ${context} context; they are not mandatory requirements. The task team may wish to focus on those most relevant and discuss them with the FCV Country Coordinator or relevant Global Practice experts as needed.</p>`;
}
```

Insert it immediately before priorities in normal and climate summaries.

- [ ] **Step 4: Implement the single-open accordion**

Render every `stageThreePriorities` item through `getConcisePriority()`. Each article has a button with rank/title and a controlled panel containing Why, How, optional suggested wording, current-review lifecycle guidance, and optional specialist reasoning. Set `expanded = idx===openSummaryPriority`; use `hidden` on other panels. `toggleSummaryPriority(idx)` sets the index, rerenders only the accordion host, and restores focus to the selected button. Keep one card open. Hide the legacy stepper/card/navigation in Summary and restore them unchanged in Detailed.

Add route-consistent CSS, `:focus-visible`, `[hidden]`, and single-column mobile rules.

- [ ] **Step 5: Verify and commit**

Run `python -m pytest tests/test_concise_stage3_contract.py tests/test_climate_lens_frontend.py -q`.

Expected: PASS; all normal priorities and existing ranked climate priorities use the accordion. Then:

```powershell
git add index.html tests/test_concise_stage3_contract.py tests/test_climate_lens_frontend.py
git commit -m "feat: add shared summary priority accordions"
```

## Task 6: Preserve Restoration and Detailed-Only Exports

**Files:** `index.html:3175-3197`, `index.html:5461-5505`, `index.html:5635-5825`, `tests/test_concise_stage3_contract.py`

- [ ] **Step 1: Write failing boundary tests**

Assert `stageConciseReadout` is stored inside the existing `fcv_express_lensState` object and restored before the summary gate runs. Slice `downloadReport()` and `downloadHtml()` and assert neither references normal/climate summary renderers, advisory text, nor accordion markup.

- [ ] **Step 2: Verify failure**

Run `python -m pytest tests/test_concise_stage3_contract.py -k "persist or download" -q`.

Expected: persistence FAILS; export-boundary assertions PASS.

- [ ] **Step 3: Persist normalized state only**

Add `stageConciseReadout` to `fcv_express_lensState`; restore with `stageConciseReadout=savedLensState.stageConciseReadout||null` before setting `stage3View=supportsAnyStage3Summary()?'summary':'detailed'`. Clear it during reset/cleanup. Do not add concise content or advisory text to export payloads/builders.

- [ ] **Step 4: Verify and commit**

Run `python -m pytest tests/test_concise_stage3_contract.py tests/test_climate_lens_frontend.py -q`. Expected: PASS. Then:

```powershell
git add index.html tests/test_concise_stage3_contract.py
git commit -m "fix: preserve summary state and detailed exports"
```

## Task 7: Record ITS Parity and Verify the Branch

**Files:** local `C:/Users/wb559324/.claude/FCV_BUILD_PARITY.md`; all files above for verification.

- [ ] **Step 1: Update the local parity log**

Record: optional top-level `concise_readout`; optional `priority.concise`; atomic discard of incomplete bundles; both Stage 3 event payloads; all-review lifecycle calibration; shared non-mandatory advisory; Summary default; detailed-only downloads; and the requirement that ITS mirror these without replacing ITS-specific OPCS retrieval. Do not stage this file.

- [ ] **Step 2: Run focused verification**

```powershell
python -m pytest tests/test_concise_stage3_contract.py tests/test_extract_priorities.py tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py -q
```

Expected: PASS.

- [ ] **Step 3: Run climate and deployment regressions**

```powershell
python -m pytest tests/test_climate_workflow_contract.py tests/test_climate_verified_render.py tests/test_render_deployment_contract.py tests/test_vocabulary_repair_wiring.py -q
```

Expected: PASS.

- [ ] **Step 4: Run syntax and diff checks**

```powershell
python -m py_compile app.py
git diff --check origin/codex/climate-summary-quality-fixes...HEAD
git status --short
git diff --name-status origin/codex/climate-summary-quality-fixes...HEAD
```

Expected: compilation succeeds; diff check is silent; no uncommitted tracked files; implementation scope is `app.py`, `index.html`, the three concise/climate/parser test files, plus committed design/plan documents.

- [ ] **Step 5: Commit test-only corrections only if needed**

```powershell
git add tests/test_concise_stage3_contract.py tests/test_climate_lens_frontend.py tests/test_extract_priorities.py tests/test_sector_lens_app_contract.py
git commit -m "test: cover normal FCV summary regressions"
```

Do not create an empty commit when no correction was needed.

## Completion Criteria

- Normal FCV design and implementation reviews default to a valid Summary.
- The approved overall assessment and both FCV ratings render.
- All ranked priorities appear; only the first begins expanded.
- Both summary routes show the controlled advisory transition.
- Detailed analysis and downloads remain comprehensive.
- Invalid concise data falls back to Detailed without another model call.
- Both workflows, restoration, accessibility, climate, and deployment tests pass.
- The local ITS parity log is current.
