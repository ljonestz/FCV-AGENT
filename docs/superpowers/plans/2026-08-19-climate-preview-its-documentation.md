# Climate Preview ITS Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update canonical repository documentation and provide a concise ITS handover for the repaired Climate preview.

**Architecture:** Make documentation-only edits on the isolated branch based on deployed commit `08b3cb99`. Keep historical records unchanged and update only the current overview, developer guide, relevant reference contracts, and one new handover.

**Tech Stack:** Markdown, Git, pytest contract suite

---

### Task 1: Refresh canonical overview and developer guidance

**Files:**
- Modify: `README.md`
- Modify: `claude.md`

- [ ] **Step 1:** Mark the Climate module as experimental/pilot and explain the 24-country preview-bank boundary and reduced prior knowledge outside bank coverage.
- [ ] **Step 2:** Record the Render dependency requirement and the repaired Stage 1 lens-context initialization.
- [ ] **Step 3:** Link the new ITS handover from the documentation index.

### Task 2: Refresh technical reference contracts

**Files:**
- Modify: `docs/reference/reference_sector_lenses.md`
- Modify: `docs/reference/reference_backend_routes.md`

- [ ] **Step 1:** Align the sector-lens reference with the pilot status and country coverage/fallback behavior.
- [ ] **Step 2:** Document Stage 1 lens-context initialization and the non-fatal grounding fallback states.

### Task 3: Write the concise ITS handover

**Files:**
- Create: `20260819_its-climate-preview-handover.md`

- [ ] **Step 1:** Summarize the original ITS-reported error, root cause, two fixes, and deployed state.
- [ ] **Step 2:** Summarize the automated and full live Step-by-Step verification evidence.
- [ ] **Step 3:** State the pilot and knowledge-bank limitations, recommended landing-page signpost, ITS actions, and informal Teams message.

### Task 4: Verify and commit

**Files:**
- Verify all modified Markdown files

- [ ] **Step 1:** Run `git diff --check` and scan Markdown links and consistency fields.
- [ ] **Step 2:** Confirm only documentation files changed and historical records remain untouched.
- [ ] **Step 3:** Run the relevant documentation/contract tests, review the final diff, and commit the documentation refresh.
