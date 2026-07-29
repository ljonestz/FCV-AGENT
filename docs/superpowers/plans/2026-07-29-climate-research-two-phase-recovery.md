# Climate Research Two-Phase Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover validated Climate-FCV evidence from completed web-search results without repeating searches.

**Architecture:** Add one bounded, tools-disabled structuring call after a search response that lacks the evidence block but contains at least two web-search result blocks. Reuse the returned assistant content, preserve the existing deadline, and feed the structuring response through the unchanged parser and evidence gate.

**Tech Stack:** Python, Anthropic SDK, pytest

---

### Task 1: Reproduce truncated-search recovery

**Files:**
- Modify: `tests/test_climate_research.py`

- [ ] Add `test_climate_research_structures_completed_search_results_without_researching` with a `max_tokens` response containing two `web_search_tool_result` blocks followed by a valid structured response.
- [ ] Assert the result is complete, exactly two API calls occur, the second call omits `tools` and `betas`, and its messages contain the original user prompt, returned assistant content, and a final formatting instruction.
- [ ] Run only the new test and confirm it fails because the second response is not requested.

### Task 2: Implement bounded structuring recovery

**Files:**
- Modify: `app.py`

- [ ] Count `web_search_tool_result` blocks after any `pause_turn` handling.
- [ ] If the evidence block is absent and at least two result blocks exist, compute the remaining attempt and parent deadline.
- [ ] Make one tools-disabled call with `max_tokens=2500`, the prior assistant content, and the formatting-only instruction.
- [ ] Parse and gate that response through the existing code.
- [ ] Run the new test and confirm it passes.

### Task 3: Enforce the recovery boundary

**Files:**
- Modify: `tests/test_climate_research.py`

- [ ] Add a test showing that a missing block with fewer than two search-result blocks fails without a structuring call.
- [ ] Run both recovery tests and confirm they pass.

### Task 4: Verify and publish

**Files:**
- Verify: `app.py`
- Verify: `tests/test_climate_research.py`
- Verify: `tests/test_climate_workflow_contract.py`

- [ ] Run `python -m pytest -q -p no:cacheprovider tests/test_climate_research.py tests/test_climate_workflow_contract.py`.
- [ ] Run `python -m py_compile app.py` and `git diff --check`.
- [ ] Inspect the diff, commit as `fix: structure completed climate search results`, and push `feat/climate-readout-redesign`.
