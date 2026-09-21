# Climate Drafting Target Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve otherwise-valid Climate-FCV recommendations when generated current-document section labels are safe variants of guidance-permitted targets.

**Architecture:** Add the selected guidance-to-target mapping to the existing drafting validation context. Canonicalize only guidance-backed current-document section variants, then run the unchanged strict validator and admission pipeline.

**Tech Stack:** Python 3, dataclasses, pytest.

---

### Task 1: Specify target repair behavior

**Files:**
- Modify: `tests/test_climate_drafting_contract.py`
- Modify: `tests/test_climate_verified_pipeline.py`

- [ ] Add a contract test that supplies a non-canonical current-document section and a recognized guidance ID, then expects the registered section and a repair code.
- [ ] Add a negative contract test showing that an unknown guidance ID does not authorize repair.
- [ ] Add a pipeline regression with multiple valid recommendation candidates whose section-label variants previously caused `DRAFTING_CURRENT_TARGET_INVALID`.
- [ ] Run the focused tests and confirm they fail for the missing repair behavior.

### Task 2: Implement guidance-backed canonicalization

**Files:**
- Modify: `sector_lenses/climate_recommendations.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`

- [ ] Extend `DraftingValidationContext` with a backward-compatible guidance-target mapping.
- [ ] Add deterministic selection of a permitted current-document target using cited guidance and normalized token matching.
- [ ] Apply the repair inside `normalize_drafting_blocks` before strict validation and record `DRAFTING_CURRENT_SECTION_CANONICALIZED`.
- [ ] Populate the mapping from the already-selected operational-guidance packet.
- [ ] Run the focused tests and confirm they pass.

### Task 3: Verify and publish

**Files:**
- Inspect: `sector_lenses/climate_recommendations.py`
- Inspect: `sector_lenses/climate_verified_pipeline.py`
- Inspect: `tests/test_climate_drafting_contract.py`
- Inspect: `tests/test_climate_verified_pipeline.py`

- [ ] Run drafting-contract, verified-pipeline, operational-guidance, and verified-runtime tests.
- [ ] Inspect the final diff for unrelated changes.
- [ ] Commit the narrow fix and push `codex/climate-summary-quality-fixes`.
