# Climate Research Truncation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow the focused Climate-FCV server-tool turn to finish its evidence block while making lens routing visible in safe telemetry.

**Architecture:** Preserve the existing one-call research pipeline and mandatory gate. Change only the output-token ceiling and add a bounded Express intake log derived from normalized `AnalysisState.active_lenses`.

**Tech Stack:** Python, Flask, Anthropic SDK, pytest

---

### Task 1: Prevent research truncation

**Files:**
- Modify: `tests/test_climate_research.py`
- Modify: `app.py`

- [ ] Change `test_climate_research_uses_one_focused_request` to assert `call["max_tokens"] == 4096`.
- [ ] Run `python -m pytest -q -p no:cacheprovider tests/test_climate_research.py::test_climate_research_uses_one_focused_request` and confirm it fails with `2500 != 4096`.
- [ ] Change the focused research request option in `run_climate_web_research` to `"max_tokens": 4096`.
- [ ] Re-run the focused test and confirm it passes.

### Task 2: Log Express lens routing

**Files:**
- Modify: `tests/test_climate_workflow_contract.py`
- Modify: `app.py`

- [ ] Add an endpoint test posting an Express payload with `active_lenses=["climate"]` and assert the log contains `active_lenses=climate`.
- [ ] Run that test and confirm it fails because the log is absent.
- [ ] After `AnalysisState.from_payload(data)`, log the assessment ID and a comma-joined, bounded list of normalized active lens IDs, falling back to `none`.
- [ ] Re-run the endpoint test and confirm it passes.

### Task 3: Focused verification and publication

**Files:**
- Verify: `app.py`
- Verify: `tests/test_climate_research.py`
- Verify: `tests/test_climate_workflow_contract.py`

- [ ] Run `python -m pytest -q -p no:cacheprovider tests/test_climate_research.py tests/test_climate_workflow_contract.py`.
- [ ] Run `python -m py_compile app.py`.
- [ ] Run `git diff --check` and inspect the diff.
- [ ] Commit as `fix: prevent climate research truncation` and push `feat/climate-readout-redesign`.
