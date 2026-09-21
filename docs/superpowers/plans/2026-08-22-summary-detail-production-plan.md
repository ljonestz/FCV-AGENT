# Summary-Detailed Production Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align Summary with canonical Detailed priorities, surface the same lifecycle guidance everywhere, streamline the Detailed header, and validate the result with live PCN smoke and quality runs.

**Architecture:** Add one normalized `priority.project_cycle` record and require the concise cycle to match it. Add grounded Summary transition/closing fields, validate lifecycle-specific metadata with the detected document type, and reuse the canonical cycle in browser Detailed, standalone HTML, and DOCX. Replace the full-width Stage 3 gauges and duplicated overview with a compact responsive ratings rail while retaining the existing accessible priority stepper.

**Tech Stack:** Python/Flask, pytest, vanilla JavaScript, HTML/CSS, python-docx, browser acceptance testing, Render preview services.

---

### Task 1: Canonical lifecycle and document-scope validation

**Files:**
- Modify: `tests/test_concise_stage3_contract.py`
- Modify: `tests/test_instrument_metadata_hygiene.py`
- Modify: `app.py:2990-3075, 5074-5135, 6170-6510, 9430-9450, 11020-11045`

- [ ] Write these failing tests using the existing `_payload`, `_wrapped`, and `_make_json_block` fixtures:

```python
def test_priority_exposes_one_canonical_project_cycle():
    result = extract_priorities(_wrapped(_payload()), document_type="PCN")
    assert result["priorities"][0]["project_cycle"] == CONCISE_PRIORITY["project_cycle"]


def test_concise_cycle_mismatch_uses_canonical_priority_fallback():
    payload = _payload()
    payload["priorities"][0]["concise"]["project_cycle"]["primary_text"] = "Different timing."
    result = extract_priorities(_wrapped(payload), document_type="PCN")
    assert result["concise_readout"] is None
    assert result["priorities"][0]["the_gap"]


def test_pcn_rejects_mid_cycle_scope():
    result = extract_priorities(
        _make_json_block("Results framework change", "Level 2", "mid-cycle"),
        document_type="PCN",
    )
    assert result["priorities"][0]["priority_scope"] is None


def test_af_preserves_mid_cycle_scope():
    result = extract_priorities(
        _make_json_block("Results framework change", "Level 2", "mid-cycle"),
        document_type="AF",
    )
    assert result["priorities"][0]["priority_scope"] == "mid-cycle"
```

- [ ] Run `python -m pytest tests/test_concise_stage3_contract.py tests/test_instrument_metadata_hygiene.py -q` and confirm the new assertions fail for the missing canonical cycle and invalid PCN scope.

- [ ] Add this server normalizer before `_normalize_concise_priority`:

```python
def _normalize_project_cycle(value: Any) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    primary_label = _clean_concise_string(value.get("primary_label"))
    primary_text = _clean_concise_string(value.get("primary_text"))
    if not primary_label or not primary_text:
        return None
    secondary_label = _clean_concise_string(value.get("secondary_label"))
    secondary_text = _clean_concise_string(value.get("secondary_text"))
    if bool(secondary_label) != bool(secondary_text):
        secondary_label = ""
        secondary_text = ""
    return {
        "primary_label": primary_label,
        "primary_text": primary_text,
        "secondary_label": secondary_label,
        "secondary_text": secondary_text,
    }
```

- [ ] Change `extract_priorities` to accept `document_type: str = "Unknown"`; normalize `priority.project_cycle`; clear `priority_scope == "mid-cycle"` unless the normalized document type is `AF` or `RESTRUCTURING`.

- [ ] Add `_derive_concise_priority(priority)` using the canonical title, `why_it_matters`/`the_gap`, the first two to four action `guidance` strings, the first action's suggested wording, and `priority.project_cycle`. Use it only when a priority's model-authored concise object is missing, malformed, or has a different cycle. Preserve a valid top-level readout and other valid concise priorities; keep Detailed-only fallback when the top-level readout or canonical priorities are invalid.

- [ ] Pass the detected document type at both production `extract_priorities` call sites.

- [ ] Update the main Stage 3 JSON exemplar to include canonical `project_cycle`, copy those exact values into `concise.project_cycle`, and replace the generic exemplar `"priority_scope": "mid-cycle"` with `"priority_scope": "Not identified"`.

- [ ] Rerun the focused tests and confirm they pass.

- [ ] Commit with `git commit -m "fix: align summary with canonical lifecycle"`.

### Task 2: Grounded Summary narrative flow

**Files:**
- Modify: `tests/test_concise_stage3_contract.py`
- Modify: `app.py:2990-3075, 6170-6201`
- Modify: `index.html:6431-6435`

- [ ] Extend `CONCISE_READOUT` and the prompt/schema with required strings `strengths_transition`, `priorities_transition`, and `closing`. Add:

```python
def test_concise_bundle_requires_narrative_flow_fields():
    for field in ("strengths_transition", "priorities_transition", "closing"):
        payload = _payload()
        payload["concise_readout"].pop(field)
        assert extract_priorities(_wrapped(payload))["concise_readout"] is None
```

- [ ] Run `python -m pytest tests/test_concise_stage3_contract.py::test_concise_bundle_requires_narrative_flow_fields -q` and confirm it fails because those fields are not validated.

- [ ] Normalize the three strings in `_normalize_concise_readout` and return them with the existing readout. In the prompt, require transitions to connect only canonical findings and forbid new facts, actions, milestones, dates, institutions, or causal claims.

- [ ] Extend the existing Node renderer test with this ordered assertion:

```javascript
const ordered=['Overall assessment','These strengths provide a foundation','What is already working','The priorities move from immediate concept decisions','Priority actions for the task team','Taken together, these changes'];
const positions=ordered.map(value=>html.indexOf(value));
if(positions.some(value=>value<0)||positions.some((value,index)=>index>0&&value<positions[index-1]))throw new Error('narrative order');
```

- [ ] Run the renderer test and confirm it fails before changing `renderNormalFcvSummary`.

- [ ] Render the escaped strengths transition before strengths, the priorities transition before the controlled advisory, and the escaped closing after the accordion using a quiet `.concise-closing` block.

- [ ] Run `python -m pytest tests/test_concise_stage3_contract.py -q` and confirm it passes.

- [ ] Commit with `git commit -m "feat: add coherent summary narrative"`.

### Task 3: Minimal responsive ratings rail and uncluttered navigation

**Files:**
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `index.html:885-960, 1540-1555, 5155-5200, 6252-6385, 6738-6769`

- [ ] Replace the old Priority Overview expectations with:

```python
overview = _extract_js_function(source, "stage3OverviewHtml")
intro = _extract_js_function(source, "renderPrioritiesIntro")
assert 'class="stage3-rating-rail"' in overview
assert 'class="stage3-mobile-ratings"' in overview
assert "Priority overview" not in overview
assert 'id="pov-sb"' not in overview
assert "priority-navigation-callout" not in intro
assert '<button type="button" class="ps-step' in source
assert 'aria-pressed="${i===currentPriority?' in source
```

- [ ] Run the two affected frontend tests and confirm they fail on the old overview/callout.

- [ ] Make `stage3OverviewHtml` return a desktop `aside.stage3-rating-rail` with two compact textual rating cards and a mobile `details.stage3-mobile-ratings` containing the same rating labels as text. Preserve the climate integration variant as one compact card.

- [ ] Wrap Detailed Stage 3 in `.stage3-reading-shell` and `.stage3-reading-main`. At wide widths use `grid-template-columns:minmax(180px,220px) minmax(0,1fr)` and `position:sticky` on the rail. At the mobile breakpoint hide the rail, show the disclosure, and use one column. Hide both Detailed rating containers when Summary is active.

- [ ] Remove the Priority Overview markup and `pov-sb` update logic. Remove the duplicate priority-title list and navigation callout from `renderPrioritiesIntro`, but keep the short contextual lead and semantic numbered stepper.

- [ ] Add `:focus-visible` styling for `.ps-step` and verify the existing selected-state update remains intact.

- [ ] Run `python -m pytest tests/test_concise_stage3_contract.py tests/test_climate_lens_frontend.py -q` and confirm it passes.

- [ ] Commit with `git commit -m "feat: streamline detailed assessment layout"`.

### Task 4: Canonical project cycle across live Detailed and exports

**Files:**
- Modify: `tests/test_regime_timing.py`
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `app.py:11930-12070, 12520-12570`
- Modify: `index.html:5750-6050, 6870-6930`

- [ ] Add failing tests requiring both `showPriority` and `_buildExportPriorityCard` to call `renderPriorityProjectCycle(pr)`, and a DOCX test requiring `Where this fits in the project cycle` plus both fixture milestones.

- [ ] Run `python -m pytest tests/test_regime_timing.py tests/test_climate_lens_frontend.py -q` and confirm the new assertions fail.

- [ ] Add this escaped shared renderer and call it in the live and exported Detailed cards:

```javascript
function renderPriorityProjectCycle(priority){
  const cycle=priority&&priority.project_cycle&&typeof priority.project_cycle==='object'?priority.project_cycle:{};
  if(!cycle.primary_label||!cycle.primary_text)return '';
  const secondary=cycle.secondary_label&&cycle.secondary_text?`<div><strong>${esc(cycle.secondary_label)}</strong><p>${esc(cycle.secondary_text)}</p></div>`:'';
  return `<section class="priority-project-cycle"><h4>Where this fits in the project cycle</h4><div><strong>${esc(cycle.primary_label)}</strong><p>${esc(cycle.primary_text)}</p></div>${secondary}</section>`;
}
```

- [ ] In DOCX generation, add the same subsection from `priority.project_cycle` only. Use bold milestone labels and normal explanation paragraphs; omit the subsection when the canonical cycle is absent.

- [ ] Run the focused timing/frontend tests and confirm they pass.

- [ ] Commit with `git commit -m "feat: align project cycle across detailed exports"`.

### Task 5: Full verification, parity register, and deployment

**Files:**
- Modify: private `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`

- [ ] Append a private parity entry covering canonical `priority.project_cycle`, equality with `priority.concise.project_cycle`, per-priority deterministic concise fallback, required narrative fields, document-aware scope validation, and unchanged detailed-only export policy. Do not commit the private file.

- [ ] Run:

```powershell
python -m pytest tests/test_concise_stage3_contract.py tests/test_instrument_metadata_hygiene.py tests/test_regime_timing.py tests/test_climate_lens_frontend.py -q
python -m py_compile app.py
python -m pytest -q
git diff --check
git status --short
```

- [ ] Inspect the complete diff, remove unrelated changes, commit any final test adjustment, and push `HEAD` to `refs/heads/codex/climate-summary-quality-fixes`.

- [ ] Confirm both branch-testing services report the pushed commit and healthy status before uploading the PCN.

### Task 6: Live South Sudan PCN smoke and quality acceptance

**Input:**
- `.superpowers/brainstorm/Southsudan/Project Concept Note (PCN)_Draft_15_June 2026.docx`

**Artifacts:**
- Create multiple `20260822_smoke-pcn-summary-*.png` files in the active visualization folder.
- Create multiple `20260822_quality-pcn-summary-*.png` files in the active visualization folder.
- Create `20260822_quality-pcn-shareable-detailed.html` in the active visualization folder.
- Create sanitized smoke and quality Stage 3 contract captures without project-source text.

- [ ] On the smoke service, run the PCN through Express normal FCV analysis. Record the assessment ID and verify all three stages finish, Summary opens by default, exactly three strengths render, every Detailed priority has one Summary card, only Priority 1 is open, Summary and Detailed milestones match, `mid-cycle` is absent, and the browser console has no error.

- [ ] Capture at least two smoke screenshots: overview/strengths and an expanded priority with lifecycle guidance.

- [ ] Confirm the quality service runtime mode, then run the same PCN and workflow. Record the assessment ID and repeat the deterministic checks. Review the prose for standalone narrative flow, factual precision, project specificity, lifecycle appropriateness, sensitivity/responsiveness distinction, and action consistency.

- [ ] Capture at least four quality screenshots: overview/strengths, ratings-to-priorities transition, an early expanded priority, and a later priority plus closing. Capture one narrow/mobile view.

- [ ] Use `Share .html` to download the comprehensive Detailed export. Copy it to the active visualization folder under the descriptive filename, open it offline, and verify canonical lifecycle blocks, no local filesystem paths, no credentials, and no required external assets.

- [ ] Open every screenshot and the offline HTML. Compare at least two priority titles, actions, and milestones across Summary, browser Detailed, and standalone HTML. Report analytical caveats separately from structural pass/fail results.
