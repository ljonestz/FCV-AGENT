# Climate Summary Strength Cards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the Climate-FCV summary strength cards complete headings and enough grounded explanation for non-specialist readers.

**Architecture:** Strengthen the existing verified-analysis `description` contract rather than adding a new payload field. Split multi-sentence descriptions at the first sentence in the existing frontend helper, preserving a safe one-sentence fallback and the current three-card layout.

**Tech Stack:** Python prompt builders and pytest; browser-side JavaScript embedded in `index.html`; Node-based renderer tests.

---

### Task 1: Lock the prompt contract

**Files:**
- Modify: `tests/test_climate_analysis_prompts.py`
- Modify: `sector_lenses/climate_verified_prompts.py`

- [ ] Add a test asserting that `build_analysis_prompt` requires two or three plain-language sentences, a short first sentence, a concrete project anchor, and an explanation of why the response matters.
- [ ] Run `python -m pytest tests/test_climate_analysis_prompts.py -q` and confirm the new assertion fails because the wording is absent.
- [ ] Add the narrow `existing_responses.description` instruction to `_analysis_prompt` while retaining the 45-word field bound.
- [ ] Re-run the prompt test and confirm it passes.

### Task 2: Improve summary-card rendering

**Files:**
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `index.html`

- [ ] Extend the summary regression test with a two-sentence response whose first sentence exceeds eleven words and a one-sentence compatibility response.
- [ ] Assert that the full first sentence is rendered without an ellipsis, the second sentence appears as the body without repeating the heading, and the legacy response remains readable.
- [ ] Run the focused frontend test and confirm it fails against the current eleven-word truncation behavior.
- [ ] Update `climateSummaryStrengths` to split the derived heading from the remaining description and remove artificial title truncation.
- [ ] Give the card body an explicit element and readable line height while retaining the existing responsive grid.
- [ ] Re-run the focused frontend test and confirm it passes.

### Task 3: Document and verify

**Files:**
- Modify: `CLAUDE.md`
- Modify: `docs/reference/reference_prompt_architecture.md`
- Modify outside the repository: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`

- [ ] Record the verified-analysis description contract and summary split in the architecture documentation.
- [ ] Record the shared prompt/UI contract change in the local parity log without copying internal policy material into the repository.
- [ ] Run the targeted prompt, frontend, and verified-render tests.
- [ ] Inspect the diff, commit, push `codex/climate-summary-quality-fixes`, and verify the deployed preview with a smoke run.
