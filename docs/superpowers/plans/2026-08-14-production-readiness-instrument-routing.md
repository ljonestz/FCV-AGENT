# Production-ready Climate Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure every supported Climate Preview instrument/document route can produce safely targeted recommendations and make any all-suppressed recommendation run visibly incomplete rather than falsely successful.

**Architecture:** Complete the bounded operational-guidance registry for the supported IPF, DPF, PforR, and MPA route matrix while retaining strict current-document target validation. Add one pipeline invariant that distinguishes “no candidates generated” from “candidates generated but all rejected,” project that state into the reader contract, and render it consistently in server HTML, DOCX, detailed web, and summary web surfaces.

**Tech Stack:** Python 3, Flask, pytest, dataclasses, vanilla JavaScript, python-docx, Render/gunicorn.

---

### Task 1: Lock the supported guidance matrix with failing tests

**Files:**
- Modify: `tests/test_climate_operational_guidance.py`
- Modify: `sector_lenses/climate_operational_guidance.py`

- [ ] **Step 1: Write the failing route-matrix test**

Add a parameterized test covering these exact supported routes:

```python
SUPPORTED_ROUTES = (
    ("IPF", "PCN"), ("IPF", "PID"), ("IPF", "PAD"),
    ("IPF", "Project Paper"), ("IPF", "AF"),
    ("IPF", "Restructuring"),
    ("DPF", "PCN"), ("DPF", "PID"), ("DPF", "PAD"),
    ("DPF", "Program Document"),
    ("PforR", "PCN"), ("PforR", "PID"), ("PforR", "PAD"),
    ("PforR", "Program Paper"),
)

@pytest.mark.parametrize(("instrument", "document"), SUPPORTED_ROUTES)
def test_every_supported_route_has_current_document_guidance(
    instrument: str, document: str
) -> None:
    packet = select_operational_guidance(
        doc_type=document, instrument_type=instrument
    )
    assert packet
    assert any(
        target_document.casefold() == document.casefold()
        for entry in packet
        for target_document, _ in entry.permitted_targets
    )
```

Add explicit tests that `Unknown`, `TA`, and `ISR` remain empty/fail-closed and
that MPA selection contains both base guidance and `GUIDE-MPA-PROGRAM-LAYER`.

- [ ] **Step 2: Run the matrix tests and verify RED**

Run:

```powershell
python -m pytest tests/test_climate_operational_guidance.py -q
```

Expected: failures for the currently missing IPF PID/AF/Restructuring, DPF
PCN/PID/PAD, and PforR PCN/PID routes.

- [ ] **Step 3: Add the smallest complete registry coverage**

Extend the existing registry entries with instrument-true targets. Use current
document names exactly and include only sections that are legitimate for that
document family. Required target families:

```python
# Examples of bounded targets; final strings follow headings evidenced in the
# representative repository test documents.
("pid", "concept description")
("pid", "poverty and social impacts and environmental aspects")
("af", "description of additional financing")
("restructuring", "proposed changes")
("program document", "program description and policy matrix")
("pad", "program scope and design")
```

Do not add `Unknown`, TA, or ISR to a preparation guidance entry. Keep the
six-entry packet cap and existing non-authoritative wording.

- [ ] **Step 4: Run the matrix tests and verify GREEN**

Run the same command. Expected: all tests in the file pass.

- [ ] **Step 5: Commit the guidance matrix**

```powershell
git add -- sector_lenses/climate_operational_guidance.py tests/test_climate_operational_guidance.py
git commit -m "fix: cover supported climate document routes"
```

### Task 2: Reproduce and prevent the Somalia DPF PID suppression

**Files:**
- Modify: `tests/test_climate_verified_pipeline.py`
- Modify only if the regression remains red: `sector_lenses/climate_recommendations.py`

- [ ] **Step 1: Write a Somalia-shaped DPF PID pipeline regression**

Build from the existing `_responses()` fixture, set `doc_type="PID"` and
`instrument_type="DPF"`, and provide four grounded candidates targeting the
actual concept PID headings:

```python
DPF_PID_TARGETS = (
    "Concept Description",
    "Poverty and Social Impacts and Environmental Aspects",
    "Proposed Development Objective(s)",
)
```

Each candidate must cite only guidance returned for DPF PID. Assert:

```python
assert diagnostics["raw_candidate_count"] == 4
assert diagnostics["valid_candidate_count"] == 4
assert diagnostics["final_priority_count"] >= 1
assert "DRAFTING_CURRENT_TARGET_INVALID" not in diagnostics["reason_codes"]
```

- [ ] **Step 2: Run the regression and verify its result**

Run:

```powershell
python -m pytest tests/test_climate_verified_pipeline.py::test_dpf_pid_candidates_use_current_concept_document_targets -q
```

Expected after Task 1: PASS. If it fails only on harmless heading variants,
capture the exact failure before changing normalization.

- [ ] **Step 3: If required, add only unambiguous canonicalization**

Modify `_guidance_backed_current_target()` only if a real heading variant has a
single guidance-permitted current-document destination. Do not implement a
generic “first target wins” fallback.

- [ ] **Step 4: Run drafting and pipeline tests**

```powershell
python -m pytest tests/test_climate_drafting_contract.py tests/test_climate_verified_pipeline.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit the regression**

```powershell
git add -- tests/test_climate_verified_pipeline.py sector_lenses/climate_recommendations.py
git commit -m "test: prevent DPF PID recommendation suppression"
```

### Task 3: Add the all-suppressed fail-loud pipeline invariant

**Files:**
- Modify: `tests/test_climate_verified_pipeline.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`

- [ ] **Step 1: Write the failing invariant test**

Use a parseable candidate with an invalid current target and assert:

```python
assert result["priorities"] == []
assert result["validation"]["status"] == "attention"
assert "RECOMMENDATIONS_ALL_SUPPRESSED" in result["validation"]["reason_codes"]
assert "RECOMMENDATIONS_ALL_SUPPRESSED" in (
    result["recommendation_diagnostics"]["reason_codes"]
)
```

Add a separate test where `raw_candidate_count == 0` and assert the new reason
code is absent.

- [ ] **Step 2: Run both tests and verify RED**

```powershell
python -m pytest tests/test_climate_verified_pipeline.py -k "all_suppressed or no_candidates" -q
```

Expected: the all-suppressed assertion fails because the bounded condition is
not yet recorded.

- [ ] **Step 3: Implement the invariant**

After semantic review has finalized `priorities`, add exactly one bounded code
when `parsed_candidate_count > 0 and not priorities`:

```python
if parsed_candidate_count > 0 and not priorities:
    reasons.append("RECOMMENDATIONS_ALL_SUPPRESSED")
    recommendation_reasons.append("RECOMMENDATIONS_ALL_SUPPRESSED")
    review_status = "attention"
```

Deduplication remains centralized in the existing final construction.

- [ ] **Step 4: Run the pipeline tests and verify GREEN**

```powershell
python -m pytest tests/test_climate_verified_pipeline.py -q
```

Expected: all pipeline tests pass.

- [ ] **Step 5: Commit the invariant**

```powershell
git add -- sector_lenses/climate_verified_pipeline.py tests/test_climate_verified_pipeline.py
git commit -m "fix: fail loudly when climate priorities are suppressed"
```

### Task 4: Project incomplete recommendation state into all reader surfaces

**Files:**
- Modify: `tests/test_climate_verified_render.py`
- Modify: `sector_lenses/climate_verified_render.py`
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `index.html`

- [ ] **Step 1: Write failing reader-contract tests**

Construct an assessment with raw candidates, zero final priorities, and the new
reason code. Assert the reader contains:

```python
assert model["recommendation_status"] == "incomplete"
assert "could not be completed" in model["recommendation_message"].casefold()
```

Assert server HTML and DOCX use the incomplete message. Add a control asserting
a true zero-candidate result retains the neutral no-priority message.

- [ ] **Step 2: Run reader tests and verify RED**

```powershell
python -m pytest tests/test_climate_verified_render.py -k "recommendation_status or all_suppressed" -q
```

Expected: missing reader fields and old neutral message.

- [ ] **Step 3: Implement the bounded reader state**

In `build_reader_model()`, derive:

```python
all_suppressed = (
    diagnostics.get("parsed_candidate_count", 0) > 0
    and diagnostics.get("final_priority_count", 0) == 0
    and "RECOMMENDATIONS_ALL_SUPPRESSED"
    in diagnostics.get("reason_codes", [])
)
```

Expose `recommendation_status` as `"incomplete"` or `"complete"` and a fixed,
non-diagnostic reader message. Update `_no_priority_message()` to use that
field. Do not expose candidate text or internal validation messages.

- [ ] **Step 4: Write the failing frontend contract test**

Add a Node-backed frontend test that loads an incomplete reader and asserts the
detailed view, summary view, stage subtitle, and callout contain the incomplete
message and do not contain `Recommendations Note generated` or `ready to copy`.

- [ ] **Step 5: Run the frontend test and verify RED**

```powershell
python -m pytest tests/test_climate_lens_frontend.py -k "incomplete_recommendations" -q
```

Expected: old generated/ready wording remains.

- [ ] **Step 6: Implement consistent frontend rendering**

Use `climateVerifiedReader.recommendation_status === 'incomplete'` to select a
fixed warning banner, the incomplete priority message, an incomplete stage
subtitle, and a non-success callout. Preserve the existing completed state for
normal runs.

- [ ] **Step 7: Run reader and frontend tests and verify GREEN**

```powershell
python -m pytest tests/test_climate_verified_render.py tests/test_climate_lens_frontend.py -q
```

Expected: all tests pass.

- [ ] **Step 8: Commit the reader behavior**

```powershell
git add -- sector_lenses/climate_verified_render.py index.html tests/test_climate_verified_render.py tests/test_climate_lens_frontend.py
git commit -m "fix: surface incomplete climate recommendations"
```

### Task 5: Update architecture, parity, and ITS handover documentation

**Files:**
- Modify: `claude.md`
- Modify: `docs/reference/reference_backend_routes.md`
- Create: `20260814_its-production-readiness-handover.md`
- Modify outside repository with approval: `C:/Users/wb559324/.claude/FCV_BUILD_PARITY.md`

- [ ] **Step 1: Document the supported route matrix and new bounded reason code**

Update the climate verified-pipeline and priority-parsing sections in
`claude.md` and the diagnostics contract in
`docs/reference/reference_backend_routes.md`. Record that
`RECOMMENDATIONS_ALL_SUPPRESSED` is a privacy-safe reason code and that the
reader exposes only a fixed incomplete status/message.

- [ ] **Step 2: Record the shared-contract divergence**

With explicit filesystem approval, append the reader/diagnostics contract
change to `C:/Users/wb559324/.claude/FCV_BUILD_PARITY.md` so the ITS FastAPI
build can mirror it. Do not copy private parity content into tracked files.

- [ ] **Step 3: Write the dated ITS production-readiness handover**

Create a new file rather than overwriting `HANDOVER.md`. Include the deployed
commit, supported route matrix, exclusions, environment variables, rollback,
automated test counts, live run evidence, and unresolved limitations. Do not
claim production readiness until Task 6 has supplied fresh evidence.

- [ ] **Step 4: Verify documentation consistency**

```powershell
rg -n "RECOMMENDATIONS_ALL_SUPPRESSED|DPF PID|supported route" claude.md docs/reference/reference_backend_routes.md 20260814_its-production-readiness-handover.md
git diff --check
```

Expected: all contract locations are updated and `git diff --check` is clean.

- [ ] **Step 5: Commit documentation**

```powershell
git add -- claude.md docs/reference/reference_backend_routes.md 20260814_its-production-readiness-handover.md
git commit -m "docs: prepare climate production handover"
```

### Task 6: Verify, deploy, and perform live acceptance

**Files:**
- Inspect: all branch changes
- Update after evidence: `20260814_its-production-readiness-handover.md`

- [ ] **Step 1: Run targeted production-readiness tests**

```powershell
python -m pytest tests/test_climate_operational_guidance.py tests/test_climate_drafting_contract.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_render.py tests/test_climate_lens_frontend.py tests/test_climate_workflow_contract.py -q
```

Expected: zero failures.

- [ ] **Step 2: Run the complete suite once**

```powershell
python -m pytest -q
```

Expected: zero failures. Do not rerun a clean full suite without new evidence.

- [ ] **Step 3: Inspect final scope and secrets**

```powershell
git status --short
git diff 36ffcb8..HEAD --check
git diff 36ffcb8..HEAD --stat
git diff 36ffcb8..HEAD -- . ':!docs/superpowers/'
```

Confirm only the planned files changed and no credentials, raw documents, or
unrelated artifacts are present.

- [ ] **Step 4: Push the exact tested branch**

```powershell
git push origin codex/climate-summary-quality-fixes
```

Record the pushed commit SHA and wait for both Render services to report that
exact SHA live.

- [ ] **Step 5: Rerun the original Somalia DPF PID in smoke and quality modes**

For each service, upload the supplied Somalia PID, run Climate Preview, and
verify the reader displays ranked priorities. In Render logs verify:

```text
raw_candidate_count > 0
valid_candidate_count > 0
final_priority_count > 0
reason_codes does not contain DRAFTING_CURRENT_TARGET_INVALID
```

- [ ] **Step 6: Run bounded representative cross-instrument checks**

Use one supplied IPF document, one PforR PID/PAD, and one MPA PID/PAD. Confirm
instrument/document routing, non-zero ranked priorities, correct terminology,
and no false completed state. Stop and investigate any failure before handover.

- [ ] **Step 7: Exercise fail-loud behavior locally**

Use the deterministic all-suppressed fixture to render the detailed page,
summary, server HTML, and DOCX. Confirm all say incomplete and none say generated
or ready.

- [ ] **Step 8: Finalize and commit the evidence-backed handover**

Populate the handover with actual commands, counts, SHAs, Render deployment IDs,
assessment IDs, and residual limitations, then run its link/path checks and
commit:

```powershell
git add -- 20260814_its-production-readiness-handover.md
git commit -m "docs: record climate production acceptance"
git push origin codex/climate-summary-quality-fixes
```

- [ ] **Step 9: Confirm final deployed SHA and clean branch**

Verify both Render services are live on the final documentation commit, confirm
the last commit is documentation-only relative to the tested application SHA,
and run `git status --short --branch`. Report production readiness only with the
fresh evidence and explicitly list any route not live-tested.
