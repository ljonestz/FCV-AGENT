# Native Climate Metadata Context Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent dedicated Climate-FCV stages from failing while composing an unused legacy sector-lens prompt.

**Architecture:** Extend `build_lens_stage_context()` with a default-on prompt-composition flag. Native climate routes request metadata only; every other caller keeps current behavior.

**Tech Stack:** Python, Flask, pytest

---

### Task 1: Add metadata-only context and wire both routes

**Files:**
- Modify: `app.py`
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `tests/test_climate_workflow_contract.py`

- [ ] Add a failing unit regression using validated research plus signals that trigger the full question bank. Assert `compose_prompt=False` returns the active Climate lens, an empty prompt, zero estimated tokens, and no ceiling exception.
- [ ] Add route-contract assertions proving native Climate Stage 2 passes `compose_prompt=False` in both step-by-step and Express execution.
- [ ] Run only the new tests and confirm they fail because the argument is unsupported or absent.
- [ ] Add `compose_prompt: bool = True` to `build_lens_stage_context()`. After lens resolution, source normalization, and diagnostic normalization, return the normal metadata contract with an empty prompt when false.
- [ ] Compute native-climate flags before calling the builder and pass `compose_prompt=not native_climate` in both routes.
- [ ] Run the new tests and confirm they pass.
- [ ] Run focused climate, workflow, and sector-lens contract tests plus Python compilation and `git diff --check`.
- [ ] Verify the diff does not change prompts, models, token limits, research, parsing, schemas, or generic/implementation-review behavior.
- [ ] Commit and push `feat/climate-readout-redesign`.
