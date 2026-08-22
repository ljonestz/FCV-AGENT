# Climate Summary Parity Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the verified Climate-FCV Summary into production parity with the main FCV readout without changing the Climate analysis methodology or adding a model call.

**Architecture:** Enrich the existing deterministic Climate reader projection with normalized display titles and canonical project-cycle records derived from the resolved operation context and existing recommendation fields. Both Climate Summary and Detailed renderers consume that same reader data. The frontend keeps the Summary concise by showing the top three priorities, explicitly disclosing the total, using existing reader prose as a transition, adding a deterministic closing, and collapsing technical routing details behind an accessible disclosure.

**Tech Stack:** Python 3, Flask repository utilities, vanilla JavaScript in `index.html`, pytest, Node-based executable frontend contract tests, python-docx.

---

### Task 1: Canonical Climate priority display records

**Files:**
- Modify: `sector_lenses/climate_verified_render.py`
- Test: `tests/test_climate_verified_render.py`

- [ ] **Step 1: Write failing reader-model tests**

Add parameterized tests proving that `build_reader_model()`:

```python
@pytest.mark.parametrize(
    ("document_type", "primary_label", "secondary_label"),
    [
        ("PCN", "At concept stage", "During preparation"),
        ("PAD", "In the current project document", "Before approval"),
        ("Additional Financing", "In the Additional Financing package", "Before approval"),
        ("Restructuring", "In the restructuring package", "During implementation"),
        ("Unknown", "At the current review stage", "Before the next decision point"),
    ],
)
def test_reader_priorities_receive_context_aware_canonical_project_cycle(...):
    ...
```

Also test that titles beginning with `Priority 2 -`, `Priority 2:`, `Priority 2.`, `Priority 2 ·`, `Priority 2 –`, `Priority 2 —`, or `Priority 2 •` are normalized once in the reader model while a rank-only title is preserved.

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
python -m pytest -q tests/test_climate_verified_render.py -k "canonical_project_cycle or normalizes_priority_title"
```

Expected: failures because reader priorities do not yet expose `project_cycle` and titles retain rank prefixes.

- [ ] **Step 3: Implement the smallest deterministic reader projection**

In `sector_lenses/climate_verified_render.py`:

```python
_PRIORITY_TITLE_PREFIX = re.compile(
    r"^\s*Priority\s+\d+\s*(?:[-:.\u00b7\u2013\u2014\u2022]\s*)?",
    re.IGNORECASE,
)

def _normalize_priority_title(value: object) -> str:
    original = _text(value)
    normalized = _PRIORITY_TITLE_PREFIX.sub("", original).strip()
    return normalized or original
```

Add a `_project_cycle_for_operation(operation_context, priority)` helper that selects only the labels in the test matrix and fills `primary_text` from `minimum_action` (falling back to `decision`) and `secondary_text` from `completion_evidence` (falling back to `enhanced_action` or `limitation`). Apply both helpers only while building the reader-facing priority copies; do not modify recommendation admission, scoring, or evidence.

- [ ] **Step 4: Run tests and verify GREEN**

Run:

```powershell
python -m pytest -q tests/test_climate_verified_render.py -k "canonical_project_cycle or normalizes_priority_title"
```

Expected: all selected tests pass.

- [ ] **Step 5: Add Detailed HTML and DOCX parity tests**

Extend `test_html_and_docx_share_headings_and_priority_order` to assert that both formats render `Where this fits in the project cycle` and the exact canonical labels after the recommendation actions/drafting content.

- [ ] **Step 6: Implement Detailed renderers and verify**

Add one escaped HTML helper and one DOCX helper in `climate_verified_render.py` that render the canonical reader `project_cycle` after the action/drafting fields. Run:

```powershell
python -m pytest -q tests/test_climate_verified_render.py
```

Expected: the complete Climate render test module passes.

- [ ] **Step 7: Commit**

```powershell
git add -- sector_lenses/climate_verified_render.py tests/test_climate_verified_render.py
git commit -m "feat: align climate priority lifecycle"
```

### Task 2: Concise Climate narrative and routing hierarchy

**Files:**
- Modify: `index.html`
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write failing executable frontend tests**

Add Node-executed tests that require:

```javascript
const html = renderClimateVerifiedSummary(reader);
// Compact visible context, with technical preparation/E&S routing in a closed details element.
// Existing priority_summary.statement appears before the priority accordion.
// "Showing the 3 highest-ranked of 5 priorities" appears when five exist.
// A concise closing appears after the priority accordion.
// The canonical priority.project_cycle is copied unchanged into concise.project_cycle.
```

Add a regression proving Climate Summary titles never begin with a second visible `Priority <rank>` prefix.

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
python -m pytest -q tests/test_climate_lens_frontend.py -k "summary and (routing or narrative or lifecycle or count or title)"
```

Expected: failures for the still-expanded routing panel, synthetic lifecycle labels, missing count disclosure/closing, or duplicated titles.

- [ ] **Step 3: Implement minimal frontend projection and narrative**

Update `climateSummaryPriorityItems(reader)` to copy `priority.project_cycle` exactly and use the reader-normalized title. Update `renderClimateVerifiedSummary(reader)` to:

```javascript
const totalPriorities = Array.isArray(r.priorities) ? r.priorities.length : 0;
const shownPriorities = priorities.length;
```

Render a short visible `Review context` line, retain unresolved-route warnings visibly, and place preparation model and E&S route inside a closed `<details>` element. Use `r.priority_summary.statement` as the bridge into priorities, add the three-of-five disclosure only when needed, and add a short deterministic closing that points readers to Detailed analysis for evidence, drafting and completion signals. Preserve the incomplete-recommendation fail-loud state.

- [ ] **Step 4: Run tests and verify GREEN**

Run:

```powershell
python -m pytest -q tests/test_climate_lens_frontend.py -k "summary"
```

Expected: all Climate Summary tests pass.

- [ ] **Step 5: Run the full Climate frontend contract**

```powershell
python -m pytest -q tests/test_climate_lens_frontend.py
```

Expected: all tests pass, including the real browser contract when permitted.

- [ ] **Step 6: Commit**

```powershell
git add -- index.html tests/test_climate_lens_frontend.py
git commit -m "feat: clarify climate summary narrative"
```

### Task 3: Production acceptance and parity documentation

**Files:**
- Modify privately, never commit: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`
- Verify: all files changed since the task base

- [ ] **Step 1: Run focused Climate suites**

```powershell
python -m pytest -q tests/test_climate_verified_render.py tests/test_climate_lens_frontend.py tests/test_climate_verified_pipeline.py tests/test_climate_workflow_contract.py
```

Expected: all tests pass.

- [ ] **Step 2: Run full repository acceptance**

```powershell
python -m pytest -q --basetemp=.pytest_tmp_climate_parity
python -m py_compile app.py sector_lenses/climate_verified_render.py
git diff --check HEAD~2..HEAD
```

Expected: zero failures, compilation exit code 0, and no whitespace errors.

- [ ] **Step 3: Review the actual diff against scope**

Confirm that no analysis prompts, evidence gates, ranking/scoring logic, source bank, or model-call paths changed. Confirm Summary still shows at most three priorities while Detailed HTML/DOCX retain all admitted priorities.

- [ ] **Step 4: Record the shared contract privately**

Append a concise parity-log entry covering canonical Climate lifecycle, normalized display titles, Summary count disclosure and narrative hierarchy. Do not stage or commit the private parity file.

- [ ] **Step 5: Request Luna max review and resolve findings**

Provide the task base and final SHAs, this plan, and explicit review focus on lifecycle correctness, Summary/Detailed/HTML/DOCX alignment, accessibility and accidental analytical changes. Resolve all Critical and Important findings before completion.

- [ ] **Step 6: Push the existing feature branch**

```powershell
git push origin HEAD:refs/heads/codex/climate-summary-quality-fixes
```

Expected: remote branch advances to the verified final SHA; production `main` remains untouched.
