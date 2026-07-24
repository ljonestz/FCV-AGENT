# Climate-Native Phase 1 — Graceful Priorities Gate — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop the Climate-lens `climate_links` validation from deleting the entire Stage 3 priorities array, so the recommendations panel always renders; surface an honest soft notice for any priority whose climate provenance could not be validated.

**Architecture:** In `extract_priorities()` the climate-links check currently returns an all-or-nothing error result (empties `priorities`) if any one priority's `climate_links` fail to normalize. Change it to per-priority graceful degradation: keep every priority, attach + tag `climate` where links are valid, null the link and count it where not. Thread an `climate_unlinked` / `climate_total` count through both Stage 3 SSE payloads and render a soft notice on the frontend. No change to non-climate mode.

**Tech Stack:** Python 3.13 (Flask, `app.py`), vanilla JS (`index.html`), pytest, node for frontend contract tests.

**Scope note:** This is Phase 1 of the approved Approach C climate-native flow (`docs/superpowers/specs/2026-07-24-climate-native-flow-design.md` §3.5). It is independently shippable and unblocks the panel. The native single-call diagnostic (§3.3) and the climate-led note (§3.4) are later plans.

**Run tests from the worktree** (flags avoid a OneDrive pytest-cache crash; frontend tests need `node` on PATH):
```
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT/.worktrees/sector-lens-platform"
C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```

---

### Task 1: Backend — graceful per-priority `climate_links` gate

**Files:**
- Modify: `app.py` — `extract_priorities()`: loop init (before `for pr in priorities_raw:` at ~5186), the enforce block (~5270–5287), the `lens_relevance` block (~5293–5298), and the success return (~5376–5392).
- Test: `tests/test_extract_priorities.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_extract_priorities.py`:

```python
import json
import app as app_module


def _stage3_block(priorities):
    payload = {
        "fcv_rating": "Moderate", "fcv_responsiveness_rating": "Moderate",
        "sensitivity_summary": "s", "responsiveness_summary": "r",
        "risk_exposure": {"risks_to": "x", "risks_from": "y"},
        "priorities": priorities,
    }
    return "%%%JSON_START%%%" + json.dumps(payload) + "%%%JSON_END%%%"


def _climate_diag():
    # Minimal usable+complete climate diagnostic with one recognized pathway id.
    return {"lenses": [{
        "lens_id": "climate", "applicability": "material",
        "materiality_level": "high", "materiality_summary": "m",
        "integration_level": "partly_integrated", "integration_summary": "ok",
        "reflections": [{"question_key": "cq1_interaction", "title": "t",
                         "status_cue": "ok", "text": "grounded"}],
        "interaction_readout": [{
            "direction_id": "climate-fcv-on-project", "summary": "s",
            "pathways": [{"pathway_id": "climate-fcv-on-project-1",
                          "pressure": "p", "mechanism": "m",
                          "project_implication": "i", "design_response": "d"}],
        }],
        "readout_sections": [], "additional_pathways": [],
        "sensitivity_evidence": [], "responsiveness_evidence": [], "less_central": "",
    }], "findings": []}


def _priority(title, climate_links):
    return {
        "title": title, "fcv_dimension": "Contextual awareness", "tag": "[S]",
        "refresh_shift": "Shift A: Anticipate", "risk_level": "High",
        "the_gap": "g in Bentiu", "why_it_matters": "w", "actions": [
            {"document_element": "PAD", "guidance": "do X in Bentiu", "suggested_language": ""}],
        "who_acts": "TTL", "when": "before appraisal",
        "action_timing": "required-before-appraisal", "resources": "r",
        "pad_sections": "SORT", "implementation_note": "n", "cpf_alignment": None,
        "climate_links": climate_links,
    }


def test_climate_links_failure_keeps_priorities_and_counts_unlinked():
    good = {"status": "linked",
            "interaction_pathway_ids": ["climate-fcv-on-project-1"],
            "contribution": "c", "strengthening_effect": "s"}
    priorities = [_priority("Good one", good), _priority("Bad one", {"status": "bogus"})]
    result = app_module.extract_priorities(
        _stage3_block(priorities), ["Doc.pdf"], ["climate"], _climate_diag())
    assert result["error"] is False
    assert len(result["priorities"]) == 2                    # panel is NOT blanked
    assert result["climate_unlinked"] == 1
    assert result["climate_total"] == 2
    assert "climate" in result["priorities"][0]["lens_ids"]  # good one tagged
    assert "climate" not in result["priorities"][1]["lens_ids"]
    assert result["priorities"][1]["climate_links"] is None   # bad one degraded, not fatal
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_extract_priorities.py::test_climate_links_failure_keeps_priorities_and_counts_unlinked -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL — currently returns `error: True` / empty priorities (the all-or-nothing gate), so `result["error"] is False` and `len == 2` assertions fail; `climate_unlinked` KeyError.

- [ ] **Step 3: Add the counter initialisation before the priority loop**

Immediately before `for pr in priorities_raw:` (~line 5186 in `extract_priorities`), add:

```python
    climate_unlinked = 0
    climate_total = 0
```

- [ ] **Step 4: Replace the all-or-nothing enforce block with graceful degradation**

Replace the current block (~5270–5287):

```python
        if enforce_climate_links:
            climate_links = normalize_priority_climate_links(
                pr.get("climate_links"), lens_diagnostic
            )
            if not climate_links:
                failed = dict(_error_result)
                failed["message"] = (
                    "Climate priority linkage was missing or invalid; "
                    "please re-run Stage 3."
                )
                return failed
            pr["climate_links"] = climate_links
            pr["lens_ids"] = [
                lens_id for lens_id in pr["lens_ids"]
                if lens_id != "climate"
            ]
            if climate_links["status"] == "linked":
                pr["lens_ids"].append("climate")
```

with:

```python
        if enforce_climate_links:
            climate_total += 1
            climate_links = normalize_priority_climate_links(
                pr.get("climate_links"), lens_diagnostic
            )
            pr["lens_ids"] = [
                lens_id for lens_id in pr["lens_ids"]
                if lens_id != "climate"
            ]
            if climate_links:
                pr["climate_links"] = climate_links
                if climate_links["status"] == "linked":
                    pr["lens_ids"].append("climate")
            else:
                # Graceful degradation: keep the priority so the panel never
                # blanks; null the unvalidated link and do not tag climate.
                pr["climate_links"] = None
                climate_unlinked += 1
```

- [ ] **Step 5: Guard the `lens_relevance` derivation against a null link**

Replace the block (~5293–5298):

```python
        if (
            enforce_climate_links
            and pr["climate_links"]["status"] == "linked"
            and not pr["lens_relevance"]
        ):
            pr["lens_relevance"] = pr["climate_links"]["contribution"][:500]
```

with:

```python
        if (
            enforce_climate_links
            and isinstance(pr.get("climate_links"), dict)
            and pr["climate_links"].get("status") == "linked"
            and not pr["lens_relevance"]
        ):
            pr["lens_relevance"] = pr["climate_links"]["contribution"][:500]
```

- [ ] **Step 6: Add the counts to the success return**

In the success `return {` block (~5376–5392), add two keys before the closing brace:

```python
        'wider_fcv_context': wider_fcv_context,
        'climate_unlinked': climate_unlinked,
        'climate_total': climate_total,
    }
```

- [ ] **Step 7: Run the new test + the existing priorities suite**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_extract_priorities.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS, including the new test. Note: the previous test that asserted an error on invalid climate_links must be updated — see Task 2.

- [ ] **Step 8: Commit**

```bash
git add app.py tests/test_extract_priorities.py
git commit -m "fix: graceful per-priority climate_links gate so priorities panel never blanks"
```

---

### Task 2: Update the now-obsolete hard-fail test

**Files:**
- Test: `tests/test_extract_priorities.py` (and `tests/test_sector_lens_app_contract.py` if it asserts the old hard-fail)

- [ ] **Step 1: Find any test asserting the old all-or-nothing behaviour**

Run: `grep -rn "Climate priority linkage was missing" tests/`
Also: `grep -rn "climate_links" tests/test_extract_priorities.py tests/test_sector_lens_app_contract.py`

- [ ] **Step 2: Convert each hard-fail assertion to the graceful contract**

For any test that currently asserts `result["error"] is True` / empty `priorities` when a `climate_links` is invalid, change it to assert `result["error"] is False`, priorities preserved, and `result["climate_unlinked"] >= 1`. (Keep tests that assert error for genuinely malformed JSON / missing `%%%JSON_START%%%` block — those paths are unchanged.)

- [ ] **Step 3: Run the affected files**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_extract_priorities.py tests/test_sector_lens_app_contract.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: update climate_links tests to graceful-degradation contract"
```

---

### Task 3: Thread `climate_unlinked`/`climate_total` into both Stage 3 SSE payloads

**Files:**
- Modify: `app.py` — express Stage 3 `stage_done: 3` payload (~8447) and step-by-step Stage 3 `stage_done` payload (~8356/where `parsed` is emitted).
- Test: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write the failing test**

```python
def test_stage3_payload_exposes_climate_link_counts():
    # extract_priorities now always returns the counts on success.
    import json, app as app_module
    payload = {
        "fcv_rating": "Moderate", "fcv_responsiveness_rating": "Moderate",
        "sensitivity_summary": "s", "responsiveness_summary": "r",
        "risk_exposure": {"risks_to": "x", "risks_from": "y"},
        "priorities": [{
            "title": "P", "fcv_dimension": "Contextual awareness", "tag": "[S]",
            "refresh_shift": "Shift A: Anticipate", "risk_level": "High",
            "the_gap": "g in Bentiu", "why_it_matters": "w",
            "actions": [{"document_element": "PAD", "guidance": "do X in Bentiu",
                         "suggested_language": ""}],
            "who_acts": "TTL", "when": "before appraisal",
            "action_timing": "required-before-appraisal", "resources": "r",
            "pad_sections": "SORT", "implementation_note": "n", "cpf_alignment": None,
            "climate_links": {"status": "no-material-pathway", "reason": "none"},
        }],
    }
    block = "%%%JSON_START%%%" + json.dumps(payload) + "%%%JSON_END%%%"
    result = app_module.extract_priorities(block, ["Doc.pdf"], ["climate"], {
        "lenses": [{"lens_id": "climate", "materiality_level": "high",
                    "integration_summary": "x",
                    "reflections": [{"question_key": "cq1_interaction", "title": "t",
                                     "status_cue": "ok", "text": "g"}],
                    "interaction_readout": [{"direction_id": "climate-fcv-on-project",
                        "summary": "s", "pathways": [{"pathway_id": "climate-fcv-on-project-1",
                        "pressure": "p", "mechanism": "m", "project_implication": "i",
                        "design_response": "d"}]}]}], "findings": []})
    assert "climate_unlinked" in result and "climate_total" in result
    assert result["climate_total"] == 1
```

- [ ] **Step 2: Run to verify it passes already at the extract layer, then wire the SSE**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_sector_lens_app_contract.py::test_stage3_payload_exposes_climate_link_counts -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (Task 1 added the keys). This test locks the extract-layer contract the SSE relies on.

- [ ] **Step 3: Add the counts to the express Stage 3 SSE payload**

In `/api/run-express` Stage 3 `yield f"data: {json.dumps({'stage_done': 3, ...})}"` (~8447), add inside the dict:

```python
                        'climate_unlinked': parsed.get('climate_unlinked', 0),
                        'climate_total': parsed.get('climate_total', 0),
```

- [ ] **Step 4: Add the same to the step-by-step Stage 3 SSE payload**

In `/api/run-stage` Stage 3 done payload (the `json.dumps({'stage_done': 3 or 'stage_done'...})` that carries `priorities`), add the same two keys:

```python
                    'climate_unlinked': parsed.get('climate_unlinked', 0),
                    'climate_total': parsed.get('climate_total', 0),
```

- [ ] **Step 5: Run full suite**

Run: `C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (all).

- [ ] **Step 6: Commit**

```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: expose climate link-validation counts in Stage 3 SSE payloads"
```

---

### Task 4: Frontend — capture counts and render an honest soft notice

**Files:**
- Modify: `index.html` — the two Stage 3 `stage_done` SSE handlers (express ~3620 and step ~3940) to store the counts; `renderPrioritiesIntro()` (~5789) to render the notice; a module-scope variable near `let stageThreePriorities = [];` (~5499) and the reset line (~4839).
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_climate_lens_frontend.py`:

```python
def test_priorities_intro_shows_soft_notice_when_links_unvalidated():
    source = INDEX.read_text(encoding="utf-8")
    # The intro renderer must reference the unlinked count and emit a soft notice.
    assert "climatePriorityUnlinked" in source
    assert "provenance could not be validated" in source
```

- [ ] **Step 2: Run to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_climate_lens_frontend.py::test_priorities_intro_shows_soft_notice_when_links_unvalidated -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL — strings absent.

- [ ] **Step 3: Add module-scope state and reset**

Near `let stageThreePriorities = [];` (~5499) add:

```javascript
  let climatePriorityUnlinked = 0, climatePriorityTotal = 0;
```

In the Stage 3 reset line (~4839, where `stageThreePriorities=[]...`) add:

```javascript
climatePriorityUnlinked=0;climatePriorityTotal=0;
```

- [ ] **Step 4: Capture the counts in both SSE handlers**

In the express Stage 3 handler (`else if(sn===3){` ~3620) and the step handler (~3940), next to `if(p.priorities)stageThreePriorities=p.priorities;` add:

```javascript
              if(p.climate_unlinked!==undefined)climatePriorityUnlinked=p.climate_unlinked;
              if(p.climate_total!==undefined)climatePriorityTotal=p.climate_total;
```

- [ ] **Step 5: Render the soft notice in `renderPrioritiesIntro()`**

Inside `renderPrioritiesIntro()` (~5789), after the existing intro HTML is assembled and before it is written to the element, append the notice when relevant. Locate the `el.innerHTML = ...` assignment (~5805) and change it to prepend a notice variable:

```javascript
    const _linkNotice = (isClimateLensActive() && climatePriorityUnlinked > 0)
      ? `<div class="climate-partial-notice">Climate provenance could not be validated for ${climatePriorityUnlinked} of ${climatePriorityTotal} priorities. Those recommendations are shown but not tagged to a specific climate-FCV pathway.</div>`
      : '';
    el.innerHTML = _linkNotice + `<div class="priorities-section-hdr">Priority Actions for the Task Team</div><div class="priorities-intro ani">
```

(Keep the remainder of the existing template literal unchanged.)

- [ ] **Step 6: Run the frontend test + full suite**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_climate_lens_frontend.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Then: `C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (all).

- [ ] **Step 7: Commit**

```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: soft notice for unvalidated climate priority links; panel always renders"
```

---

### Task 5: Regression + live validation

- [ ] **Step 1: Confirm non-climate output is unchanged**

Run: `C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: full suite green; no non-climate priority test regressed.

- [ ] **Step 2: Push and live-validate**

```bash
git push origin codex/climate-fcv-output-redesign
```
Then re-run the South Sudan PCN in Express mode on Render. Confirm: the **priority recommendations panel now renders**; if climate links didn't validate, the soft notice appears (rather than a blank panel). Capture the output + Render log slice.

---

## Self-review notes
- **Spec coverage:** implements §3.5 (graceful priorities gate) of the design; §3.3 native diagnostic and §3.4 climate-led note are explicitly deferred to later plans.
- **Type consistency:** `climate_unlinked`/`climate_total` (backend dict keys) ↔ `p.climate_unlinked`/`p.climate_total` (SSE) ↔ `climatePriorityUnlinked`/`climatePriorityTotal` (JS) — names aligned across tasks.
- **No placeholders:** all code blocks are literal; the one `.innerHTML` edit quotes the existing anchor.
