# Fast Climate Research Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the slow combined search-and-serialization turn with a concise Sonnet search followed by tools-disabled Haiku structuring.

**Architecture:** Add a search-only prompt builder in `sector_lenses/research.py`. Use it for the first API call, then use the existing full research contract as the Haiku structuring instruction over returned search blocks.

**Tech Stack:** Python, Anthropic SDK, pytest

---

### Task 1: Specify the separated API contract

**Files:**
- Modify: `tests/test_climate_research.py`

- [ ] Update the focused request test to require a search-only prompt, `max_tokens=1800`, and `max_uses=2`.
- [ ] Update the structuring test to require model `claude-haiku-4-5-20251001`, no tools, and the full evidence markers in the final user instruction.
- [ ] Run both tests and confirm they fail against the current combined Sonnet pipeline.

### Task 2: Add the search-only prompt

**Files:**
- Modify: `sector_lenses/research.py`
- Modify: `sector_lenses/__init__.py`
- Modify: `app.py`

- [ ] Add `build_climate_search_prompt(country, sector, project_profile)` requiring exactly two concise targeted searches and no JSON.
- [ ] Export and import the new builder.
- [ ] Use it in the first request with Sonnet, 1,800 output tokens, and two tool uses.

### Task 3: Use Haiku for deterministic structuring

**Files:**
- Modify: `app.py`
- Modify: `sector_lenses/research.py`

- [ ] Expand the existing full research prompt with the exact source and claim fields/enums required by the validator.
- [ ] Use that prompt in the second tools-disabled call with `claude-haiku-4-5-20251001` and 2,500 output tokens.
- [ ] Run the two contract tests and confirm they pass.

### Task 4: Verify and publish

**Files:**
- Verify: `app.py`
- Verify: `sector_lenses/research.py`
- Verify: `tests/test_climate_research.py`
- Verify: `tests/test_climate_workflow_contract.py`

- [ ] Run `python -m pytest -q -p no:cacheprovider tests/test_climate_research.py tests/test_climate_workflow_contract.py`.
- [ ] Run `python -m py_compile app.py sector_lenses/research.py` and `git diff --check`.
- [ ] Commit as `fix: separate climate search and structuring` and push `feat/climate-readout-redesign`.
