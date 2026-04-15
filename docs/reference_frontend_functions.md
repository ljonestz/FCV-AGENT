# Frontend Functions — Detailed Reference

> Extracted from CLAUDE.md to keep the main file under the 40k context limit.
> Keep this file updated when JS functions are added, renamed, or removed.

---

## Key JavaScript Functions

### Stage management
- `goToStage(n)` — advance to stage n
- `onStageComplete()` — callback when LLM finishes streaming output
- `updateSessionBar()` — refresh progress indicator

### Stage 1
- `addDocument()` — trigger file upload
- `removeDocument(idx)` — remove doc from list
- `submitStageInput()` — send docs + user refinement to `/api/run-stage`
- `renderStage1Output()` — display Part A and Part B

### Stage 3 priorities + Go Deeper
- `initStage3UI()` — parse priorities from JSON, build stepper, show Priority 1
- `showPriority(idx)` — render full priority card with zone-act layout from JSON (refresh_shift badge, actions[] loop with per-action guidance + suggested text, implementation note); no auto-load of Go Deeper
- `handleGoDeeper(el, idx)` — ontoggle handler for `<details class="go-deeper">`; initialises 2 tab buttons on first open
- `switchGoDeeperTab(idx, tabName)` — swaps active tab; loads content if not cached
  - `tabName: "trail"` → calls `loadDeeperTrail(idx)` (no API call — filters localStorage)
  - `tabName: "playbook"` → calls `loadDeeperPlaybook(idx)`
- `loadDeeperTrail(idx)` — no API call; reads `localStorage.stage2_under_hood`; filters by `priority.fcv_dimension`; renders matching OST recs/questions instantly
- `loadDeeperPlaybook(idx)` — SSE call to `/api/run-deeper?tab=playbook_refs`; caches in `deeper_{idx}_playbook`
- `cancelGoDeeper()` — aborts in-flight SSE request via `goDeeperAbortController`
- `renderGoFurtherHtml(parsed)` — renders `parsed.goFurtherItems` as `.beyond-item` cards (legacy alternatives tab)
- `renderPriorityStepper()` — build horizontal step indicator; compact S/R badge + refresh_shift below risk badge on each tab
- `renderPrioritiesIntro()` — renders intro list; compact S/R badge + refresh_shift after risk label in each `pi-item`

### S/R tag badges
- `renderSRTagBadge(tag, compact)` — renders inline pill badge
  - Full mode (default): "Sensitivity" / "Responsiveness" / "Sensitivity + Responsiveness"
  - Compact mode (`compact=true`): "S" / "R" / "S+R"
  - CSS classes: `.sr-tag`, `.sr-tag.sensitivity`, `.sr-tag.responsiveness`, `.sr-tag.both`
- `renderSRCards(sensitivityText, responsivenessText)` — renders two side-by-side summary cards
  - Inserted between the Gaps paragraph and the `<div id="priorities-intro">` div
  - CSS: `.sensitivity-responsiveness-grid`, `.sr-card`, `.sr-card.sensitivity` (border `#0050A0`), `.sr-card.responsiveness` (border `#16A34A`), `.sr-card-label`

### Sidebar (`updateSidebar()`)
- Animates both gauges: sensitivity arc + responsiveness arc
- Priority overview (`pov-row`) includes compact S/R badge after risk label
- Gauge element IDs: `fcv-resp-arc-fill`, `fcv-resp-leaf-path`, `fcv-resp-rating-label`, `fcv-resp-need-label`

### Utilities
- `md(text)` — markdown-to-HTML renderer
- `escHtml()` / `escAttr()` — HTML escaping
- `formatDate()` — human-readable timestamps
- `saveSession()` / `loadSession()` — localStorage serialization
- Browser session storage is now automatically namespaced by per-tab `assessment_id` via a storage/fetch shim appended at the end of `index.html`

---

## Removed Items (v7.0 — for historical reference)

- **`/api/run-explorer` route** — replaced by `/api/run-deeper`
- **`DEFAULT_PROMPTS["4"]` and `DEFAULT_PROMPTS["explorer"]`** — replaced by `"3"`, `"deeper"`, `"deeper_playbook"`
- **`loadExplorerForPriority()`, `handleBeyondToggle()`, `cancelExplorer()`** — replaced by `loadDeeperPlaybook()`, `handleGoDeeper()`, `cancelGoDeeper()`
- **`explorerAbortController`, `explorerCache`** — replaced by `goDeeperAbortController` + per-tab cache keys
- **`renderAboveAndBeyondHtml()`** — renamed/replaced by `renderGoFurtherHtml()`
- **`clean_stage4_output()`** — renamed `clean_stage3_output()`
- **`initStage4UI()`** — renamed `initStage3UI()`
- **`DEFAULT_PROMPTS["3"]`** (was `"4"`)
- **`pc-followup` inline "Ask →" input** — previously removed; remains dead code

---

## Download Behaviour

- **`downloadReport()`** always includes all core priority content from JSON: `actions[]` (with per-action guidance + suggested_language), `refresh_shift`, `implementation_note`, `who_acts`, `when`, `resources`
- Does NOT require Go Deeper to have been opened — no click-through needed before downloading
- Optionally appends `goFurtherItems` (alternatives tab content) if Go Deeper was already opened
- `pad_sections` rendered as `<code>` chips in the Word export

---

## Express Mode Architecture (v7.4)

**Dual-mode workflow:** Users choose between two modes on the landing page.
- **Express Analysis** (default): All 3 stages run automatically; user waits ~4–5 min on progress screen; can review/re-run any stage after.
- **Step-by-Step**: Each stage calls `/api/run-stage` individually; user refines before proceeding.

Both modes use identical prompts, code paths, and output quality. Express is a frontend orchestration change only.

**State variable:** `let analysisMode = 'express'` (persisted to `localStorage.fcv_analysis_mode`). `selectMode(mode)` updates state + card UI.

**Mode selection UI:** Two side-by-side cards inside `.mode-section` div. CSS: `.mode-section`, `.mode-card`, `.mode-card.selected`, `.mode-radio`, `.mode-badge`.

**`runStage()` modification:** Optional third parameter `onComplete(stage, parsedResult)`. When provided (by `runExpress()`), called instead of `renderOut()`. Step-by-step passes `null` — unchanged.

**`runExpress()`:**
1. Shows `#ep-accent` + `#express-progress` via `showExpressProgress()`
2. POSTs to `/api/run-express`; reads SSE stream via `fetch()` + `ReadableStream`
3. Sets a global 10-minute `AbortController` timeout for Stages 1 & 2; when `stage_start:3` fires, resets to a fresh 8-minute timeout for Stage 3
4. After `express_done` event: hides progress, calls `renderOut(3, ...)`, calls `enableClickableStepper()`, cleans up express localStorage keys
5. On failure: `showExpressError(stage, msg)` shows red card with "Retry" and "Switch to step-by-step" options

**Abort timeout budget (Express):**
- Stages 1 + 2 combined: 10 minutes from request start (`let expressTimeout`)
- Stage 3: reset to 8 minutes from when `stage_start:3` fires (`clearTimeout` + new `setTimeout`)
- Error message distinguishes which stage timed out

**Abort timeout budget (Step-by-step):**
- Stage 1: 8 minutes (includes web research)
- Stage 2: 6 minutes
- Stage 3: 8 minutes (longest output — 20k max tokens)

**Progress screen elements** (inside `#express-progress`):
- `#ep-accent` — 4px gradient accent bar
- `.ep-stepper` — 3-node horizontal stepper with circle status, connectors
- `.ep-progress-bar` / `.ep-progress-fill` — 3px bar advancing 33%/66%/100%
- `.ep-stage-card` × 3 — status cards (pending/active/done) with 1-line summary after completion
- `.ep-timer` — elapsed + estimated total; auto-updates message after 5 min and 7 min overruns
- `.ep-message-card` — rotating message, cycles every 15s; 12 messages in `EP_MESSAGES[]`

**Progress screen JS functions:**
- `showExpressProgress()` / `hideExpressProgress()` — show/hide, start/stop timer + message rotation
- `updateEpTimer()` — increments elapsed display every 1s
- `showEpMessage(idx)` — sets icon + text from `EP_MESSAGES`
- `updateExpressStage(stage, status, summary)` — updates stepper, connectors, progress bar, card state; `status` is `'pending'|'active'|'done'`
- `showExpressError(stage, errorMsg)` — red border on failed card, shows retry/switch buttons

**Post-express navigation:**
- `enableClickableStepper()` / `disableClickableStepper()` — adds/removes `.stepper-clickable` class + onclick
- `navigateToStage(stage)` — renders stored `stageOutputs[stage]` via `renderOut()`, injects re-run banner + nav arrows
- `injectRerunBanner(stage)` — amber banner with "Refine & Re-run" button
- `startRerun(stage)` — switches to `'stepbystep'`, restores `stageHists[stage]`, invalidates subsequent outputs
- `injectStageNavArrows(stage)` — injects `← Stage N-1` / `Stage N+1 →` buttons

**`retryExpressStage(stage)`:** Re-runs failed stage and resumes chain if successful.

**`switchToStepByStep(stage)`:** Bails from express, renders last completed stage in step-by-step mode.

**Session persistence (v2 format):**
- `saveSession()` includes `analysisMode`, `stageOutputs`, `stageHists`
- `loadSession()` restores all three; missing `analysisMode` → `'stepbystep'` (v1 compat)
- During express run, outputs/hists written to `localStorage.fcv_express_stageOutputs` / `fcv_express_stageHists`
- Express resume IIFE on page load: if partial keys exist and Stage 3 missing, shows amber "Resume or restart?" banner
- `resumeExpressRun()` / `discardExpressResume()` handle the two choices

---

*Last updated: 2026-04-05 — split from CLAUDE.md v7.5*
