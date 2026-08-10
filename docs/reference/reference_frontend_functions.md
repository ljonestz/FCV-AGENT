# Frontend Functions — Detailed Reference

> Extracted from CLAUDE.md to keep the main file under the 40k context limit.
> Keep this file updated when JS functions are added, renamed, or removed.

---

## Key JavaScript Functions

### Sector lenses
- `renderLensReadoutSections(lens, catalogueLens)` safely renders materiality, catalogue-declared invest/deliver sections, evidence gaps, trade-offs, and collapsed other pathways; empty and not-applicable sections are suppressed.
- `lensDisplayName(id)` resolves provenance badges to trusted catalogue names.
- Climate selection is manual-only; suggestion rendering remains available for modules whose catalogue activation allows it.
- Session version 3 and Express checkpoints persist `lensContextSources` with active versions and diagnostics. Requests and DOCX downloads send it as `lens_context_sources`; resets, lens changes, stale versions, and older-session loads clear it.
- `loadLensCatalogue()` — fetches `/api/sector-lenses`; an empty catalogue keeps the selector hidden.
- `renderLensSelector()` / `toggleLens(id)` — render ordered selection chips, enforce two lenses, show materially relevant suggestions, and lock changes once analysis starts.
- `lensVersions()` — sends client-observed versions for mismatch detection; the backend remains authoritative.
- `showLensWarnings()` — displays non-fatal unknown/disabled/version warnings while core analysis continues.
- `renderLensDiagnostic()` — renders the parsed Stage 2 diagnostic with evidence, core mappings, and source IDs.
- Session JSON is version 3 and persists `activeLenses`, `lensVersions`, and `lensDiagnostic`; older sessions load core-only.
- Stage 3 priority cards render `lens_ids` badges with `lens_relevance` tooltips. DOCX payloads include active lenses and diagnostics for the appendix.

### Stage management
- `runStage(stage, followOn=null)` — async; sends stage request to `/api/run-stage`; `followOn` used by Express mode
- `updateSessionBar()` — refresh progress indicator

### Stage 1
- `addDocument()` — trigger file upload
- `removeDocument(idx)` — remove doc from list
- `renderStage1(text, hasPackage)` — display Part A and Part B with styled section badges

### Stage 3 priorities + Go Deeper
- `initStage3UI()` — parse priorities from JSON, build stepper, show Priority 1
- `showPriority(idx)` — render full priority card with zone-act layout from JSON (refresh_shift badge, actions[] loop with per-action guidance + suggested text, implementation note); re-enable Next when navigating back from the last priority; no auto-load of Go Deeper
- `handleDeeperToggle(detailsEl, idx)` — ontoggle handler for `<details class="go-deeper">`; initialises 2 tab buttons on first open
- `loadDeeperTab(idx, tab)` — dispatches to correct loader based on `tab`:
  - `tab: "trail"` → calls `loadAnalyticalTrail(idx)` (no API call — filters localStorage)
  - `tab: "playbook_refs"` → SSE call to `/api/run-deeper?tab=playbook_refs`; caches in `deeper_{idx}_playbook`
- `loadAnalyticalTrail(idx)` — no API call; reads in-memory `stage2UnderHood` first, falls back to `localStorage.stage2_under_hood`; filters by `priority.fcv_dimension`; renders matching OST recs/questions instantly
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
- `saveSession()` / `loadSession()` - localStorage serialization
- `fcvSaveStage2UnderHood(underHood)` - best-effort persistence for the large Stage 2 Under the Hood payload; prunes stale FCV cache keys on quota errors and returns `false` instead of throwing
- `fcvSafeLocalStorageSet(key, value)` - safe wrapper for optional localStorage writes that should not fail a running analysis
- Browser session storage is now automatically namespaced by per-tab `assessment_id` via a storage/fetch shim appended at the end of `index.html`
- Landing and upload copy explicitly frames supported inputs as WBG appraisal/design-stage documents across PCN, PID, PAD, AF, Restructuring, DPF/DPO, PforR, MPA, and regional operations; MTR/ISR implementation review remains marked as coming soon.
- Upload caps are enforced in drag/drop, polling, and FormData fallback paths: Zone 1 primary document = 1 file, Zone 2 project package = up to 10 files, Zone 3 contextual documents = up to 3 files. Secondary documents are read for key signals through backend distillation, not fully assessed as standalone documents.

---

## Priority Points (v9.13)

**State globals:**
- `priorityQuestions` — array of question strings derived from the guidance box; populated by `detectPriorityPoints()`
- `focusQuestionsResult` — parsed result object from `extract_focus_questions()` once `/api/run-priority-questions` completes; `null` until the call finishes
- `pqPanelEnabled` — boolean; driven by the confirm-strip checkbox (default `true`); when `false`, `maybeRunPriorityQuestions()` skips the API call
- `_pqInFlight` — boolean guard preventing concurrent calls to `/api/run-priority-questions`
- `_pqDetectTimer` — debounce timer handle for `detectPriorityPoints()`

**Detection and confirm:**
- `onGuidanceInput()` — `oninput` handler on the Analysis Guidance textarea; debounces 400ms then calls `detectPriorityPoints()`
- `detectPriorityPoints(text)` — client-side heuristic; splits text on line breaks and `?` markers; returns array of candidate question strings; stores result in `priorityQuestions`; calls `renderPqConfirm()` when candidates found
- `renderPqConfirm()` — renders the `#pq-confirm` intake confirm strip below the guidance box; shows candidate questions as chips; checkbox (default checked) sets `pqPanelEnabled`; strip is hidden if no questions detected
- `applyPriorityChip(idx)` — click handler for a detected-question chip; toggles inclusion of that question in `priorityQuestions`

**Invocation:**
- `maybeRunPriorityQuestions()` — called after the main run completes; checks `pqPanelEnabled`, `priorityQuestions.length > 0`, and `!_pqInFlight`; if all true, calls `getPriorityQuestions()`
- `getPriorityQuestions()` — assembles the POST body `{user_context, priority_questions, stage1_output, stage2_output, stage2_ratings, stage3_output, stage3_priorities}`; SSE-streams `/api/run-priority-questions`; on `done` event calls `renderPriorityQuestions(result)`; on error calls `renderPriorityQuestionsError(msg)`
- `togglePqPanel(show)` — shows/hides `#priority-questions-section`; called by `renderPriorityQuestions()` and `renderPriorityQuestionsError()`

**Rendering:**
- `renderPriorityQuestions(result)` — renders the "Responses to your priority points" panel inside `#priority-questions-section`; one card per response object with: status pill (green / amber / grey), question text, direct answer, evidence basis, linked-priority chips, confidence gap note in italic; appends overall summary at the bottom
- `renderPriorityQuestionsError(msg)` — renders an error state inside `#priority-questions-section` with retry affordance
- `pqAddContextAndRerun(newContext)` — updates `user_context` and re-fires `getPriorityQuestions()` with the revised context; used by the "Refine" affordance on the results panel

**UI container:** `#priority-questions-section` — rendered below the Stage 3 priority stepper; hidden until `renderPriorityQuestions()` or `renderPriorityQuestionsError()` is called.

**Confirm strip:** `#pq-confirm` — appears between the guidance textarea and the run button when priority points are detected; checkbox label "Include responses to my priority points in the output" (default checked).

**Export:** `downloadReport()` includes the `focusQuestionsResult` in its POST body as `focus_questions`; `downloadHTML()` renders a "Responses to Your Priority Points" section in the HTML export. Both sections are omitted when `focusQuestionsResult` is null or errored.

---

## Classification Widget (v9.0/v9.1)

- **`renderClassificationWidget()`** — renders narrative-format classification widget at top of Stage 1 output
  - Uses `researchCountry` global (populated during web research) as `countryLabel`; falls back to `'this project's country context'`
  - Narrative: "This analysis places [country] within the [category] category of the FCV Strategy's differentiated approach. [reasoning] This is a subjective judgement on the part of this AI tool and does not constitute an official WBG classification."
  - Dropdown `onchange` auto-saves: `countryClassification = {..., category: this.value, confirmed: true}` + `localStorage.setItem('country_classification', ...)`
  - No Confirm button — dropdown change applies immediately
- **`confirmClassification()`** — REMOVED in v9.1. Was: click handler for confirm button. Functionality absorbed into dropdown `onchange`.

---

## Removed Items (v7.0 — for historical reference)

- **`/api/run-explorer` route** — replaced by `/api/run-deeper`
- **`DEFAULT_PROMPTS["4"]` and `DEFAULT_PROMPTS["explorer"]`** — replaced by `"3"`, `"deeper"`, `"deeper_playbook"`
- **`loadExplorerForPriority()`, `handleBeyondToggle()`, `cancelExplorer()`** — replaced by `loadDeeperTab()`, `handleDeeperToggle()`, `cancelGoDeeper()`
- **`explorerAbortController`, `explorerCache`** — replaced by `goDeeperAbortController` + per-tab cache keys
- **`renderAboveAndBeyondHtml()`** — renamed/replaced by `renderGoFurtherHtml()`
- **`clean_stage4_output()`** — renamed `clean_stage3_output()`
- **`initStage4UI()`** — renamed `initStage3UI()`
- **`DEFAULT_PROMPTS["3"]`** (was `"4"`)
- **`pc-followup` CSS, `explorerHistory` variable, `submitPriorityFollowup()`, `prefillFollowup()`** — removed (dead code; called `/api/run-explorer` which no longer exists)

---

## Download Behaviour (v9.1)

- **`downloadReport()`** POSTs JSON payload to `/api/download-report`; backend returns a true DOCX binary via python-docx
  - Payload: `{summary, priorities, metadata: {date_str, classification_category, classification_reasoning, finalized_pad, finalized_pad_approval_date}}`
  - Receive `blob` → create object URL → trigger `<a>` download → revoke URL
  - On failure: `alert()` with error message
  - Previous behaviour (HTML-masquerading-as-.docx blob) removed entirely
- Does NOT require Go Deeper to have been opened — no click-through needed before downloading
- DOCX includes: `action_timing` coloured pills, `refresh_shift`, `who_acts`, `when`, `resources`, `implementation_note`

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
3. Arms a per-stage `AbortController` timeout, resetting at each `stage_start`
4. After `express_done` event: hides progress, calls `renderOut(3, ...)`, calls `enableClickableStepper()`, cleans up express localStorage keys
5. On failure: `showExpressError(stage, msg)` shows red card with "Retry" and "Switch to step-by-step" options

**Abort timeout budget (Express):**
- Stage 1: 15 minutes
- Stage 2: 15 minutes
- Stage 3: 10 minutes
- `requestErrorMessage()` preserves custom `AbortController.abort(new Error(...))` timeout messages, while still using `Could not reach the server.` for true network/fetch failures.

**Abort timeout budget (Step-by-step):**
- Stage 1: 15 minutes (includes web research)
- Stage 2: 10 minutes
- Stage 3: 10 minutes (longest output - 20k max tokens)

**Upload sizing helper (not currently wired):**
- `uploadPayloadLimitMessage(primaryFiles, packageFiles, contextFiles)` can estimate raw file size after browser base64 encoding and return an over-limit message.
- No current upload path calls this legacy helper, so it does not block a request. Active count limits are enforced separately by `addFiles()`, `selectFilesWithinUploadCap()`, and the polling/FormData fallback paths.

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

**Session persistence (v3 format):**
- `saveSession()` includes `analysisMode`, `stageOutputs`, `stageHists`, ordered `activeLenses`, authoritative `lensVersions`, and `lensDiagnostic`
- `loadSession()` treats v1/v2 files as core-only and requires a Stage 1 restart when an incomplete v3 file references a missing or changed lens version
- `loadSession()` restores all three; missing `analysisMode` → `'stepbystep'` (v1 compat)
- During express run, outputs/hists are best-effort writes to `localStorage.fcv_express_stageOutputs` / `fcv_express_stageHists`
- Express recovery never claims to resume a later stage because browser `File` objects cannot survive reload. It preserves valid lens choices, asks for document re-upload, and requires a clean Stage 1 restart.
- `restartExpressFromStage1()` clears partial outputs and diagnostics while retaining valid in-memory lens choices; `discardExpressRecovery()` also clears the choices

---

*Last updated: 2026-08-10 - Verified Climate-FCV reader hierarchy and guidance refinement.*

## Verified Climate-FCV reader (v9.35)

`runExpress()` stores additive `climate_assessment` and canonical `climate_reader`
SSE payloads in `climateVerifiedAssessment` and `climateVerifiedReader`.
`renderOut()` passes the reader, rather than the raw assessment, to
`renderClimateVerifiedAssessment()` and suppresses the legacy integration gauge,
Stage 3 overview, and priority carousel. Saved sessions and completed Express
checkpoints preserve both objects; new runs, lens changes, reruns, and full reset
clear them. Follow-on requests carry the structured reader in their history.

### Reader rendering and hierarchy

- `renderClimateVerifiedAssessment(reader)` is the shared live/standalone HTML
  renderer. It owns section numbering and renders: Overview; core questions; ranked
  operational priorities; optional points to check; optional watch items; optional
  project-specific WBG guidance; and the method/limitations/sources disclosure. It
  escapes model-authored strings and uses the neutral empty-state copy: "No
  operational priorities were identified in this assessment. Review the core
  questions and points to check below."
- The Overview contains the one restrained visual panel for the sensitivity rating;
  executive and core-question prose remain in the normal reading flow. A narrative
  transition introduces the full priorities section instead of repeating its titles.
- Priority 1 is open by default in live and standalone HTML; later priorities are
  closed native `<details>` elements. All narrative, suggested drafting, and
  structured recommendation detail remains in the DOM. The server-side DOCX renderer
  keeps every priority fully expanded.
- Smaller Climate-FCV points, document checks, and watch items are numbered. Smaller
  Climate-FCV points precede document checks. The reader no longer displays the
  evidence-status label, technical annex, evidence key, recommendation/run
  diagnostics, or internal reviewer verdicts. The smoke-mode warning and the method,
  pathways, limitations, and Sources & further reading content remain.
- `installClimatePrintDisclosureHandler(root)` records the open state of reader
  priority/detail/method disclosures on `beforeprint`, opens them for print, and
  restores the exact prior state on `afterprint`. It is installed for the live page.
- `climatePrintDisclosureScript()` serializes that same lifecycle into a standalone
  HTML export. `downloadHTML()` reuses `renderClimateVerifiedAssessment()` plus the
  page's scoped styles and print lifecycle, so the shared HTML does not fork from the
  live reader. `downloadReport()` sends the canonical reader to the server, which
  deterministically rebuilds the fully expanded DOCX.

### Project-specific WBG guidance

- `isPublicWorldBankHttpsUrl(value)` accepts only well-formed HTTPS URLs on
  `worldbank.org` or valid subdomains. It rejects credentials, ports, encoded or
  malformed authorities, invalid DNS labels, IDN labels, trailing-dot hosts, and
  non-World Bank hosts.
- `normalizeClimateSourceTitle(value)` applies NFKD normalization, lowercase,
  `&`-to-`and` conversion, non-alphanumeric collapsing, and trimming. Guidance
  matching uses equality of this normalized key, not fuzzy or substring matching.
- `buildClimateGuidanceItems(reader)` is the safe compatibility path for readers
  saved before canonical `guidance_items` existed. It joins deduplicated current core
  questions to deduplicated sources by normalized title, admits only public World
  Bank HTTPS sources with usable project-specific content, ranks by matched-question
  count then catalogue order, and returns at most four items. It never pads the list
  with unmatched publications. Each fallback item uses one controlled source-value
  sentence plus the first verified watch cue, or the matched question when no watch
  cue exists; it does not copy full core-question summaries.
- `renderClimateRelevantGuidance(reader)` prefers canonical
  `reader.guidance_items`; it invokes `buildClimateGuidanceItems(reader)` when that
  property is absent or is not an array. It validates and deduplicates the final
  items, then renders one collapsed native disclosure containing every publication
  title/link, `practical_value`, and `project_use`. It does not create one
  disclosure per source. Printing temporarily opens the shared disclosure and
  restores its exact prior state; DOCX renders the same shortened content expanded.
  Empty or unsafe
  sets omit the section entirely. Canonical generation normally selects two to four
  relevant sources when enough valid matches exist, but fewer are retained rather
  than padding with a fixed reading list.

### Landing-page document capacity

- `selectFilesWithinUploadCap(files, existingFiles, limit)` applies the same
  duplicate-aware cap logic used by drag/drop and standard file selection. With
  `MAX_PACK = 10`, the project-package zone accepts up to ten supporting documents
  and rejects additional files without displacing accepted ones. Polling and
  FormData fallback paths enforce the same limit.
- `uploadPayloadLimitMessage(primaryFiles, packageFiles, contextFiles)` separately
  estimates base64-expanded request size and returns a warning string, but no current
  upload path calls it. It therefore does not enforce a payload-size limit.
- The executable frontend contract test covers the eleven-file boundary and verifies
  that a full ten-document package cannot accept another file.

This release changes deterministic reader assembly and presentation only. It does
not change Climate-FCV prompts, schemas, model calls, ratings, or
recommendation/evidence admission. The Stage 2 Express timeout remains 15 minutes.
