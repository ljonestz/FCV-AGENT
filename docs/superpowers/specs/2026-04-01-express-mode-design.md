# Express Mode — Dual-Workflow Design Spec

**Date:** 2026-04-01
**Status:** Approved
**Scope:** Add Express and Step-by-Step workflow modes to the FCV Project Screener landing page

---

## 1. Problem Statement

User feedback indicates that while the 3-stage step-by-step workflow is valued by engaged users, many potential users disengage before reaching Stage 3 (Recommendations Note) because each stage requires waiting and interaction. The total time across all stages is 3–5 minutes, but the need to actively review and proceed at each stage causes drop-off.

**Goal:** Allow users to choose between two workflow modes:
- **Express Analysis** (default): Upload docs, run all 3 stages automatically, present final recommendations. User waits ~4–5 minutes with a progress screen but no interaction required.
- **Step-by-Step** (recommended): Current interactive workflow, preserved exactly as-is.

Both modes produce identical output quality. Express mode runs the same code path — it is purely a frontend orchestration change.

---

## 2. Architectural Approach

**Frontend-orchestrated chain (no backend changes).**

Express mode reuses the existing `runStage()` function. A new `runExpress()` function calls `runStage(1)`, and on each stage's completion callback, automatically triggers the next stage. Each stage populates `stageOutputs[n]` and `stageHists[n]` exactly as today. The backend `/api/run-stage` route is unchanged — it does not know or care about modes.

**Why this approach:**
- Zero backend changes required
- Output quality guaranteed identical — same prompts, same context passing, same parsing
- If a stage fails, the chain halts and completed stages are preserved
- Existing session save/load works with minimal extension

---

## 3. Landing Page: Mode Selection

### 3.1 Placement

The mode selector is placed **within the existing upload card**, between the notices (pre-loaded, confidentiality) and the "Begin FCV Analysis" button. It is separated from the upload zones by a subtle `border-top` divider. The existing landing page layout (hero, upload intro, project doc / contextual doc zones, notices) is completely unchanged.

### 3.2 UI: Two Side-by-Side Cards

Section label: **"Choose your workflow"** with a settings gear icon.

Two cards in a horizontal flex layout:

**Left card — Express Analysis (pre-selected, default):**
- Grey "Default" badge (top-left)
- Title: "Express Analysis"
- Description: "Runs all stages automatically. Get your full Recommendations Note in one go. Review intermediate findings after."
- Time estimate: "~4–5 min · No interaction needed"
- Radio indicator (top-right): filled blue when selected

**Right card — Step-by-Step (recommended):**
- Navy "Recommended" badge (top-left)
- Title: "Step-by-Step"
- Description: "Guide the analysis stage by stage. Review findings, add local knowledge, and refine before proceeding."
- Time estimate: "~8–12 min · Full control"
- Radio indicator (top-right): filled blue when selected

### 3.3 Styling

Cards use the existing WBG design system:
- Background: `var(--wbg-gray-50)` unselected, `white` selected
- Border: `1.5px solid var(--wbg-gray-100)` unselected, `var(--wbg-cyan)` selected
- Border-radius: 6px
- Compact sizing — cards feel like a setting within the upload panel, not a separate page
- Radio indicators: 16px circles, filled with `var(--wbg-cyan)` + white inset when selected
- Badges: 9px uppercase, navy background for "Recommended", grey for "Default"

### 3.4 State

New JS variable: `let analysisMode = 'express'`

Clicking a card toggles `analysisMode` between `'express'` and `'stepbystep'`. The "Begin FCV Analysis" button routes to the appropriate flow based on `analysisMode`.

`analysisMode` is persisted to localStorage on change, included in session save/load, and restored on page reload.

---

## 4. Express Mode: Execution Flow

### 4.1 Chain Logic

New function `runExpress()`:

```
runExpress():
  1. Hide landing page, show progress screen
  2. Start elapsed timer
  3. Call runStage(1) with express callback
  4. On Stage 1 complete:
     - Extract 1-line summary from output (country, doc type, risk factor count)
     - Update progress screen: Stage 1 → done, Stage 2 → active
     - Automatically call runStage(2)
  5. On Stage 2 complete:
     - Extract summary (sensitivity rating, responsiveness rating, gap count)
     - Update progress screen: Stage 2 → done, Stage 3 → active
     - Automatically call runStage(3)
  6. On Stage 3 complete:
     - Hide progress screen
     - Render full Stage 3 output (recommendations, priorities, etc.)
     - Enable stage navigation
```

`runStage()` gains an optional `onComplete` callback parameter. When provided (by `runExpress()`), it is called after the stage's SSE `done` event is processed and `stageOutputs[n]` / `stageHists[n]` are written. When not provided (step-by-step mode), behaviour is unchanged — the stage completes and waits for user interaction. This is the only modification to `runStage()`. Each stage writes to `stageOutputs[n]` and `stageHists[n]` as normal.

### 4.2 Stage Summary Extraction

After each stage completes during express mode, a brief summary is extracted for the progress screen:

- **Stage 1:** Country name (from `extract_country_name` result or parsed from output), doc type (from `%%%DOC_TYPE:...%%%`), FCV risk factor count (count of key themes in Part B)
- **Stage 2:** Sensitivity rating, responsiveness rating (from `extract_stage2_ratings`), key gap count (from Under the Hood data)

These are displayed as 1-line summaries in the completed stage cards on the progress screen. Stage 3 has no summary — it transitions directly to the full output.

---

## 5. Express Mode: Progress Screen

### 5.1 Layout

Full-screen progress view (replaces the landing page while running):

1. **WBG accent bar** — 4px gradient bar across the top (`#002244` → `#009FDA` → `#002244`)
2. **Title:** "Preparing Your FCV Recommendations Note" (22px, navy, 700 weight)
3. **Subtitle:** "Your documents are being analysed against 12 operational standards, 25 key questions, and the full FCV Playbook."
4. **Stepper** — 3-node horizontal stepper:
   - Done stages: navy circle with checkmark
   - Active stage: white circle with blue border + blue glow ring
   - Pending stages: white circle with grey border
   - Connectors: navy (done), gradient (active), grey (pending)
5. **Thin progress bar** — 3px height, navy→blue gradient fill, advances proportionally (33% / 66% / 100%)
6. **Stage cards** (stacked vertically):
   - Done: white card, grey border, navy title, 1-line summary, checkmark icon
   - Active: white card, blue border, blue title, three-dot pulse animation + description
   - Pending: grey background, muted text, "Pending"
7. **Elapsed timer:** "Elapsed: 1:42 · Estimated total: 4–5 minutes"
8. **Rotating message card** — white card with icon + italic message, rotates every 15 seconds
9. **Bottom note:** "Keep this tab open. You'll be able to review each stage's findings once the analysis is complete."

### 5.2 Rotating Messages

Array of messages, cycled every 15 seconds with a fade transition:

```
[
  {icon: "☕", text: "Go grab a coffee — this will take a few minutes."},
  {icon: "📚", text: "Your project is being assessed against 12 operational standards and 25 key questions."},
  {icon: "⏳", text: "Don't worry, the wait will be worth it."},
  {icon: "🌍", text: "In FCV settings, nothing good happens quickly."},
  {icon: "📈", text: "We're cross-referencing your document against the full FCV Playbook."},
  {icon: "💡", text: "Tip: You can review each stage's findings once the analysis is complete."}
]
```

### 5.3 Design Language

- Typography: Open Sans throughout (WBG standard)
- Colour palette: navy (#002244) for completed/authoritative elements, blue (#009FDA) for active/interactive, grey scale for pending/muted
- Animations: three-dot pulse for active stage (not a spinner), fade for message rotation
- No streaming text visible — progress is shown through stage cards and stepper advancement
- Professional, institutional tone — should look like a WBG internal tool, not a generic AI chat

---

## 6. Post-Express: Stage Navigation

### 6.1 Completion Transition

When Stage 3 completes:
- Progress screen fades out
- Full Stage 3 output renders (recommendations note, priority cards, Go Deeper panels — exactly as today)
- Stepper shows all 3 stages as complete, with Stage 3 highlighted as current view

### 6.2 Clickable Stepper

After express completes, the stepper becomes navigable:
- All 3 stages show navy checkmarks (complete)
- The currently viewed stage is highlighted in blue (with glow ring)
- Clicking any stage shows its stored output from `stageOutputs[n]`
- Hint text below stepper: "Click any stage above to review its output"

### 6.3 Stage View (Read-Only with Re-Run Option)

When viewing a previous stage (Stage 1 or 2) after express mode:

**Default view:** Read-only rendering of the stored output, with a badge: "Read-only · From Express run"

**Re-run banner** (amber, positioned above the output):
- Icon: warning triangle
- Text: "**Want to refine this stage?** You can add context or correct findings and re-run. Note: re-running will produce slightly different results due to the nature of AI analysis, and Stage 3 will need to be regenerated."
- Button: "Refine & Re-run"

**Clicking "Refine & Re-run":**
1. Shows the refine input box (same as step-by-step mode)
2. User enters their refinement
3. Stage re-runs with the refinement input
4. On completion, subsequent stages are invalidated (marked as needing re-run)
5. User is now effectively in step-by-step mode from this point forward
6. `analysisMode` updates to `'stepbystep'` in state

### 6.4 Bottom Arrow Navigation

When viewing any stage, bottom navigation buttons:
- Left: "← Stage N-1: [Name]" (hidden on Stage 1)
- Right: "Stage N+1: [Name] →" (hidden on Stage 3, styled as primary button)

These navigate between stored stage outputs without re-running.

---

## 7. Step-by-Step Mode

### 7.1 No Changes

Step-by-step mode is identical to the current app behaviour. Selecting "Step-by-Step" on the landing page and clicking "Begin FCV Analysis" routes to the existing flow: Stage 1 runs, output displays, refine box appears, user clicks to proceed to Stage 2, etc.

### 7.2 Back Buttons Restored

Ensure `goBack()` is visible and functional at every stage:
- Stage 2 shows "← Back to Stage 1"
- Stage 3 shows "← Back to Stage 2"
- Back navigation renders stored output from `stageOutputs[n]` without re-running
- Re-run option available via the refine input box (same as today)

---

## 8. Session Persistence

### 8.1 localStorage During Express

As each stage completes during express mode, immediately write to localStorage:
- `stageOutputs` (per-stage output text)
- `stageHists` (per-stage conversation history snapshot)
- `analysisMode`
- `curS` (current stage number)

This ensures that if the tab is accidentally refreshed mid-express, partial progress is recoverable.

### 8.2 Resume on Refresh

If the page loads and localStorage contains partial express state (e.g., `stageOutputs[1]` exists but `stageOutputs[3]` does not):
- Show a "Resume or restart?" prompt
- "Resume" continues express from the last incomplete stage
- "Restart" clears state and returns to landing page

### 8.3 Session Save/Load

The `saveSession()` JSON format gains a new field:

```json
{
  "version": 2,
  "analysisMode": "express",
  ...existing fields...
}
```

`loadSession()` treats missing `analysisMode` as `'stepbystep'` for backwards compatibility with v1 sessions.

---

## 9. Error Handling

### 9.1 Stage Failure During Express

If any stage fails (API error, timeout, malformed output):
1. Progress screen shows error on the failed stage card (red border, error message)
2. Completed stages remain in `stageOutputs` — their data is preserved
3. Two options presented:
   - "Retry this stage" — re-runs the failed stage, continues express chain on success
   - "Switch to step-by-step" — drops to step-by-step mode at the failed stage, letting the user review prior stages and manually proceed

### 9.2 Stage 2 Parse Error

If Stage 2 completes but `extract_under_hood()` fails (existing `parse_error` handling):
- Express chain continues to Stage 3 regardless (same as current step-by-step behaviour)
- Parse error noted in state; shown as yellow banner when user later reviews Stage 2

### 9.3 Network Interruption

If SSE stream drops mid-stage:
- Same error handling as current app (retry button, error message)
- Express chain halts; user can retry or switch modes

---

## 10. Files to Modify

### 10.1 index.html
- **Landing page:** Add mode selection section (HTML + CSS) between notices and "Begin" button
- **New JS:** `analysisMode` state variable, `runExpress()` function, `selectMode()` handler
- **Progress screen:** New HTML section (`#express-progress`) with stepper, stage cards, timer, message rotator
- **Stage navigation:** Make stepper clickable post-completion, add bottom arrow nav, add re-run banner
- **Back buttons:** Ensure `goBack()` buttons are visible in step-by-step mode at Stages 2 and 3
- **Session persistence:** Extend `saveSession()` / `loadSession()` with `analysisMode` field; write `stageOutputs` to localStorage incrementally during express
- **CSS:** New styles for mode cards, progress screen, stage navigation, re-run banner

### 10.2 app.py
- **No changes.** Backend is mode-agnostic.

### 10.3 background_docs.py
- **No changes.**

### 10.4 CLAUDE.md
- Update to document dual-mode architecture, `runExpress()`, progress screen, and stage navigation behaviour.

---

## 11. Summary of Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Default mode | Express | Most users want speed; reduces drop-off |
| Recommended mode | Step-by-Step | Encourages deeper engagement for those willing |
| Backend changes | None | Same code path guarantees identical quality |
| Progress feedback | Stepper + stage summary cards + rotating messages | Informative without being overwhelming |
| Message rotation interval | 15 seconds | Fast enough to feel dynamic |
| Post-express stage review | Read-only by default + explicit re-run option | Prevents accidental re-runs |
| Re-run warning | "Results will be slightly different" | Transparent about stochastic nature |
| Tab closure during express | Partial state saved to localStorage; resume prompt on reload | Protects against accidental loss |
| Session format version | Bumped to v2 with `analysisMode` field | Backwards compatible |
| Stepper navigation | Clickable after all stages complete | Natural browsing UX |
