# South Sudan Climate-FCV Readout Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a wider, single-column Climate-FCV Stage 3 readout with compact rating language, clearer evidence provenance, stronger project anchoring, and unambiguous CERC eligibility rules.

**Architecture:** Preserve the canonical Climate payload and change only its presentation and prompt calibration. `index.html` will keep the current renderer helpers but replace the sidebar composition with a full-width overview, while `sector_lenses/climate_native.py` will strengthen output instructions without changing schemas.

**Tech Stack:** Flask, vanilla HTML/CSS/JavaScript, Python prompt builders, pytest, Node-based renderer contract tests.

---

### Task 1: Lock the frontend refinement contract

**Files:**
- Modify: `tests/test_climate_lens_frontend.py`
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Add failing renderer and static-contract tests**

Add tests that execute `renderClimateModuleNotice`, the grounding evidence renderer, the executive readout renderer, the new compact rating helper, and the Stage 3 overview helper. Assert:

```python
assert "Climate relevance to this project" in rendered_notice
assert "High climate relevance" in rendered_notice
assert "Why it matters:" in rendered_notice
assert "materiality" not in rendered_notice.lower()
assert "reviewed country-bank release" not in rendered_notice.lower()
assert "advisory fcv screening readout" not in rendered_notice.lower()
assert compact_summary == "Partly integrated"
assert "Executive readout" in rendered_executive
assert "Where the design is stronger" in rendered_executive
assert "Where the design could be strengthened" in rendered_executive
assert "stage3-overview" in rendered_overview
assert "<aside" not in stage3_template
```

Cover all four grounding states and require human-readable “Evidence basis” wording without `bank_missing`, “release,” or other backend vocabulary.

- [ ] **Step 2: Run the new tests and confirm RED**

Run:

```powershell
python -m pytest tests/test_climate_lens_frontend.py -q -p no:cacheprovider
```

Expected: failures on the old sidebar, materiality wording, narrative rating summary, and old provenance copy.

- [ ] **Step 3: Commit the red tests with the implementation only after GREEN**

Do not commit a deliberately failing tree. Keep the verified RED output as the TDD record, then continue to Task 2.

### Task 2: Implement the full-width Stage 3 readout

**Files:**
- Modify: `index.html`
- Modify: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Add compact presentation helpers**

Add a deterministic rating-to-short-label helper:

```javascript
function climateIntegrationShortLabel(rating) {
  return ({
    'Extremely Low': 'Minimal integration',
    'Very Low': 'Limited integration',
    'Low': 'Early integration',
    'Adequate': 'Partly integrated',
    'Well Embedded': 'Well integrated',
    'Very Well Embedded': 'Deeply integrated'
  })[String(rating || '')] || 'Evidence limited';
}
```

Create a full-width `stage3OverviewHtml()` using the existing dial IDs and `pov-sb` so `updateSidebar()` and `renderPriorityOverview()` continue to update real UI state.

- [ ] **Step 2: Replace the sidebar composition**

In `renderOut`, render `stage3OverviewHtml()` before the Stage 3 output card and remove the `<aside class="fcv-sidebar">` composition. Keep the overview available for Climate and core FCV runs, using two compact FCV rating cards for non-Climate mode.

- [ ] **Step 3: Update CSS**

Set the desktop `.main` width to 1180px, add full-width overview styles, give priority rows readable spacing, and make `.sw-grid` a one-column stack. Explicitly set identical font family, size, weight, and line-height rules for `.sw-strength` and `.sw-gap` children. Preserve the mobile breakpoint.

- [ ] **Step 4: Simplify opening wording and move provenance**

Update `renderClimateModuleNotice()` to use visible climate-relevance terminology, start with `materiality_summary`, and remove generic module, backend release, and advisory prose. Update the grounding renderer to emit the four human-readable “Evidence basis” states after the main Climate analysis in live and shared HTML paths.

- [ ] **Step 5: Update headings**

Change the strengths/gaps heading and labels to the approved executive wording. Replace the core-question introduction with the approved plain-language purpose statement followed by the framework names.

- [ ] **Step 6: Run frontend tests and confirm GREEN**

Run:

```powershell
python -m pytest tests/test_climate_lens_frontend.py -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 7: Commit the frontend slice**

```powershell
git add -- index.html tests/test_climate_lens_frontend.py
git commit -m "feat: refine climate readout layout"
```

### Task 3: Strengthen analytical specificity and CERC calibration

**Files:**
- Modify: `tests/test_climate_native.py`
- Modify: `tests/test_cerc_guardrail.py`
- Modify: `sector_lenses/climate_native.py`

- [ ] **Step 1: Add failing prompt-contract tests**

Build both Climate prompts and assert they require:

```python
assert "Never combine a CERC" in stage2_prompt
assert "conflict escalation, insecurity, civil unrest" in stage2_prompt
assert "adaptive management, restructuring, SORT updating" in stage2_prompt
assert "Never combine a CERC" in stage3_prompt
assert "confirmed omission" in stage2_prompt
assert "not evidenced at concept stage" in stage2_prompt
assert "component, subcomponent, activity, location" in stage2_prompt
```

- [ ] **Step 2: Run the prompt tests and confirm RED**

Run:

```powershell
python -m pytest tests/test_climate_native.py tests/test_cerc_guardrail.py -q -p no:cacheprovider
```

Expected: the new Climate-specific wording assertions fail while existing guardrail tests remain green.

- [ ] **Step 3: Implement the minimal prompt changes**

Extend the Stage 2 analytical-depth block to require supported project anchors and calibrated omission language. Replace the concise Climate CERC sentences in both prompt builders with the explicit separation rule while retaining the existing instrument and eligible-emergency constraints.

- [ ] **Step 4: Run prompt tests and confirm GREEN**

Run:

```powershell
python -m pytest tests/test_climate_native.py tests/test_cerc_guardrail.py -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 5: Commit the prompt slice**

```powershell
git add -- sector_lenses/climate_native.py tests/test_climate_native.py tests/test_cerc_guardrail.py
git commit -m "fix: separate climate and conflict response guidance"
```

### Task 4: Record parity and verify the integrated change

**Files:**
- Modify locally only: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`
- Verify: `index.html`, `sector_lenses/climate_native.py`, focused Climate tests

- [ ] **Step 1: Record the additive prompt calibration in the private parity log**

Add a dated entry stating that Climate-native Stage 2 and Stage 3 now prohibit mixed CERC/conflict activation wording, route conflict/security deterioration to adaptive-management tools, and require clearer project anchoring. Note that schemas and rating semantics are unchanged. Never commit or reference the private file in tracked repository content.

- [ ] **Step 2: Run focused integrated tests**

Run:

```powershell
python -m pytest tests/test_climate_lens_frontend.py tests/test_climate_native.py tests/test_cerc_guardrail.py tests/test_climate_workflow_contract.py tests/test_sector_lens_app_contract.py -q -p no:cacheprovider
```

Expected: all tests pass with no failures.

- [ ] **Step 3: Run local rendered QA**

The flow under test is: local app loads -> a representative Climate Stage 3 state renders -> the full-width rating and priority overview appear above the recommendations -> priority navigation updates without console errors.

Check desktop and mobile widths for clipping, wrapping, horizontal scroll, font consistency, and priority interaction. Use the Browser plugin when available; otherwise use the repository's existing Playwright workflow and record that the Browser plugin was unavailable.

- [ ] **Step 4: Inspect the final diff and status**

Run:

```powershell
git status --short --branch
git diff --check
git log -5 --oneline --decorate
```

Expected: only intended tracked files differ or have been committed; no whitespace errors.

- [ ] **Step 5: Push the branch**

```powershell
git push origin HEAD:refs/heads/feat/climate-country-bank
```

Expected: remote branch advances successfully; leave PR #59 in draft state for Render/browser acceptance.
