# Climate-FCV Stage 3 Tabs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` for implementation tasks and `superpowers:test-driven-development` for each behavior change.

**Goal:** Extend the concise-first Stage 3 Summary/Detailed presentation from the core FCV route to the verified Climate-FCV route, while preserving the current Climate Detailed reader and making the Summary's strengths cards evidence-driven and variable.

**Architecture:** Keep the verified Climate schema, prompts, ratings, priority ordering, exports, and Detailed reader unchanged. Extend the existing verified reader model with bounded `existing_responses` data, add a deterministic client-side Summary renderer and Climate-specific view gate, and correct the existing lifecycle grid with an explicit label/value layout. The core FCV gate and rendering path remain unchanged.

**Tech Stack:** Flask/Python, inline vanilla JavaScript/CSS in `index.html`, pytest contract tests, Node frontend storage tests, and the existing South Sudan smoke harness.

---

### Task 1: Add red tests for the reader data and lifecycle contract

**Files:** `sector_lenses/climate_verified_render.py`, `tests/test_climate_verified_render.py`, `tests/test_concise_stage3_contract.py`

1. Add a Climate reader-model test that builds a minimal valid assessment containing two bounded `bounded_analysis.existing_responses` records and asserts the returned model exposes their safe display fields, including the response identifier, description, limitation, evidence identifiers, pathway identifiers, and project fact identifiers.
2. Add a frontend contract test asserting the lifecycle markup uses an explicit value-column wrapper for both primary and secondary lifecycle entries.
3. Add a frontend contract test asserting the corresponding responsive CSS moves that wrapper to the first column on narrow screens.
4. Run the focused tests and confirm they fail because the reader model and lifecycle markup do not yet satisfy the new contract.

### Task 2: Implement the smallest data and layout changes

**Files:** `sector_lenses/climate_verified_render.py`, `index.html`

1. Map only the bounded existing-response fields needed by the UI into `build_reader_model`, using the repository's existing safe reader-model conventions and retaining the current response order.
2. Change `showConcisePriority` so `Where this fits in the project cycle` contains one label column and a `.concise-cycle-items` value column that stacks the primary and secondary entries.
3. Update the existing `.concise-cycle` mobile media rule so both columns collapse cleanly without affecting other concise cards.
4. Rerun the Task 1 tests and confirm they pass.

### Task 3: Add red tests for Climate Summary rendering and route gating

**Files:** `tests/test_concise_stage3_contract.py`, `tests/test_sector_lens_app_contract.py`, `index.html`

1. Add static contract tests for a dedicated Climate verified Stage 3 gate, a Climate Summary renderer, and Climate Summary use of the existing view-toggle controls.
2. Add tests asserting the Climate Summary does not include the horizontal segmented rating bar, while the existing verified Detailed renderer and its rating markup remain present.
3. Add tests asserting the Summary consumes `existing_responses` before positive judgment fallbacks and renders a variable number of evidence-backed “what is working” cards rather than hard-coded three cards.
4. Add tests asserting the core concise gate still requires the core route conditions and is not widened by the Climate gate.
5. Run the focused tests and confirm they fail before implementation.

### Task 4: Implement Climate Summary/Detailed tabs without changing analysis content

**Files:** `index.html`

1. Add `supportsClimateVerifiedStage3View` as a route-specific design-stage gate based on the server-resolved `climateVerifiedReader` and verified schema version.
2. Add deterministic helpers that select bounded, evidence-backed existing responses as strengths, deduplicate them, derive compact titles from their descriptions, and fall back only to clearly positive judgment values. Render a neutral state when no positive candidate is evidenced.
3. Add `renderClimateVerifiedSummary` with the approved hierarchy: concise climate context label, executive readout, dynamic strengths cards, and compact ranked priority actions. Do not render the horizontal rating bar in Summary.
4. Generalize the existing Stage 3 toggle plumbing only where required so Climate verified output opens on Summary, switches to the unchanged `renderClimateVerifiedAssessment` Detailed content, keeps keyboard behavior and aria state, and never issues another model request.
5. Preserve the existing verified Climate reader, ratings, priorities, exports, follow-on controls, and core FCV Summary behavior. Do not introduce a second climate rating system or alter the Stage 3 schema.
6. Rerun the focused tests and then the existing Climate reader/render contract tests.

### Task 5: Verify integration and finish the branch

**Files:** `claude.md` and any implementation/test files required by verification findings

1. Inspect the complete diff and add a concise entry to the project maintenance notes describing the Climate verified Summary/Detailed presentation and dynamic strengths source.
2. Run the targeted Python contract tests, frontend storage tests, and the full pytest regression suite, recording the exact pass counts and any pre-existing skipped/ignored artifact.
3. Start the local app using the repository's documented smoke configuration and run the South Sudan PCN through the Climate-FCV lens. Verify stage completion, Summary/Detailed switching, dynamic strengths, lifecycle alignment, absence of a Summary rating bar, unchanged Detailed climate rating/readout, and no UI/SSE errors.
4. Inspect the final browser output and git status, then commit and push the focused changes on `codex/concise-stage3-readout`.

## Verification commands

From `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\concise-stage3-readout`:

```powershell
pytest -q tests/test_climate_verified_render.py tests/test_concise_stage3_contract.py tests/test_sector_lens_app_contract.py
pytest -q tests/frontend_storage.test.js
pytest -q
git diff --check
git status --short --branch
```

The smoke run will use `C:\Users\wb559324\Downloads\Project Concept Note (PCN)_Draft_15_June 2026.docx` as the South Sudan input and the repository's existing quality/runtime smoke configuration; no source document will be modified.

