# Climate Verified Reader — Lay Readout Restructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the climate verified reader into a lay-legible report — Overview (readout + rating scale) at the top, a clean diagnose-vs-act split, three actionability tiers (Priorities / Quick fixes / Watch), a materiality-driven priority count, and removal of model-internal metadata and raw evidence codes from the reader view — while preserving the evidence-gated discipline that won the blind eval.

**Architecture:** All reader output flows from one model (`build_reader_model` in `sector_lenses/climate_verified_render.py`) rendered to three parity surfaces: server HTML (`render_reader_html`), DOCX (`write_reader_docx`), and the frontend (`renderClimateVerifiedAssessment` in `index.html`). Most 3-tier content already exists (`minor_climate_points`, `review_readiness_flags`, per-question `watch`); this plan reorganises and re-surfaces it, raises two `[:3]` caps, drops render-only metadata, and adds prompt-level guardrails + two new driver questions. No new pipeline stage.

**Tech Stack:** Python 3.13, Flask, python-docx, vanilla JS. Tests: pytest. Run tests with `"C:/WBG/Python313/python.exe" -m pytest -q`.

**Design spec:** `docs/superpowers/specs/2026-08-06-climate-reader-lay-readout-restructure-design.md`

---

## Working conventions (read first)

- **Worktree:** `.worktrees/climate-country-bank-deploy` on branch `feat/climate-reader-lay-comprehensibility`. All paths below are relative to that worktree root.
- **Edit reliability (OneDrive):** the Edit tool intermittently silent-no-ops on the large files here (`index.html` especially). After every edit to `index.html`, `app.py`, or `climate_verified_render.py`, **verify by re-reading the changed region or grepping for the new string** before moving on. If Edit no-ops, fall back to an atomic Python read-modify-write (`C:/WBG/Python313/python.exe`: read bytes → `.replace(old, new)` → write bytes, preserving CRLF) and re-verify.
- **Commits:** `git add` + `git commit` in one chained call. **No `Co-Authored-By` trailer.** `claude.md` is tracked lowercase (not relevant here).
- **Baseline:** full suite is **853 passing** (854 after the v9.31 em-dash test on this branch — run once at the start to confirm the real baseline number and use that as the green bar).
- **Parity rule:** every reader-visible change must land in all three surfaces (`render_reader_html`, `write_reader_docx`, `renderClimateVerifiedAssessment`). Each task lists all three.
- **Do NOT** read the OPCS/ESF corpus. Do NOT touch `main` or the ITS/stable service.

**Task 0 — confirm baseline (no code):**
- [ ] Run `"C:/WBG/Python313/python.exe" -m pytest -q tests/` and record the passing count. Expected: ~853–854 passing. This is the green bar for every later task.

---

## Task 1: Raise the priority count cap (3 → 5, materiality-driven)

**Files:**
- Modify: `sector_lenses/climate_verified_render.py` (the `build_reader_model` priorities slice, ~line 312)
- Modify: `sector_lenses/climate_recommendations.py` (the `admit_and_rank` return slice, ~line 884, `[:3]`)
- Modify: `sector_lenses/climate_verified_schemas.py` (candidate-count description, ~line 396)
- Test: `tests/test_climate_verified_render.py`, `tests/test_climate_recommendations.py`

- [ ] **Step 1: Write failing test for the render-model cap.** Add to `tests/test_climate_verified_render.py`:

```python
def test_build_reader_model_keeps_up_to_five_priorities():
    from sector_lenses.climate_verified_render import build_reader_model
    assessment = {
        "executive_readout": "One. Two. Three.",
        "judgments": {},
        "priorities": [
            {"rank": i, "title": f"Priority {i}", "recommendation_id": f"REC-00{i}"}
            for i in range(1, 7)  # six candidates
        ],
    }
    model = build_reader_model(assessment)
    # Cap is five, not three; a sixth is dropped.
    assert len(model["priorities"]) == 5
    assert [p["title"] for p in model["priorities"]] == [f"Priority {i}" for i in range(1, 6)]
```

- [ ] **Step 2: Run it, verify it fails.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_verified_render.py::test_build_reader_model_keeps_up_to_five_priorities`
Expected: FAIL (`assert 3 == 5`).

- [ ] **Step 3: Raise the render-model cap.** In `sector_lenses/climate_verified_render.py`, find:

```python
    priorities = sorted(
        _records(assessment.get("priorities")),
        key=lambda item: (_rank(item.get("rank")), _text(item.get("title"))),
    )[:3]
```

Change the final slice to `[:5]`.

- [ ] **Step 4: Raise the admission cap.** In `sector_lenses/climate_recommendations.py` near line 884, find the `admit_and_rank` return that ends `)[:3]` and change it to `)[:5]`. Read the surrounding 15 lines first to confirm it is the ranked-candidate return (it sorts then slices) and not an unrelated slice.

- [ ] **Step 5: Update the schema description.** In `sector_lenses/climate_verified_schemas.py` ~line 396 change `"No more than three admitted candidates."` to `"No more than five admitted candidates; use more than three only where materiality clearly warrants."` Then grep the prompt for any residual low count: `grep -nE "three (priorit|recommend|admitted)|no more than three" sector_lenses/climate_verified_prompts.py` — if `_recommendation_prompt` states a hard "three", change it to "up to five, and only beyond three where materiality clearly warrants; do not pad".

- [ ] **Step 6: Write failing test for the admission cap.** Add to `tests/test_climate_recommendations.py` a test that feeds six admissible candidates through `admit_and_rank` and asserts `len(result) == 5`. (Read an existing `admit_and_rank` test in that file first and mirror its candidate-construction helper exactly so the fixtures are valid.)

- [ ] **Step 7: Frontend cap.** In `index.html` ~line 4674 change `.slice(0,3)` on the priorities array to `.slice(0,5)`. Verify by grep: `grep -n "sort((x,y)=>(Number(x.rank)" index.html` then confirm the trailing slice reads `.slice(0,5)`.

- [ ] **Step 8: Run the two new tests + the render/recommendations suites.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_verified_render.py tests/test_climate_recommendations.py`
Expected: PASS. Fix any existing test that hard-asserted exactly three priorities (update its expectation to reflect the input, not a hard 3).

- [ ] **Step 9: Commit.**

```bash
git add sector_lenses/climate_verified_render.py sector_lenses/climate_recommendations.py sector_lenses/climate_verified_schemas.py index.html tests/test_climate_verified_render.py tests/test_climate_recommendations.py
git commit -m "feat: raise climate reader priority cap 3->5 (materiality-driven, no silent truncation)"
```

---

## Task 2: Overview at the top (lift the sensitivity rating scale above the fold)

**Files:**
- Modify: `sector_lenses/climate_verified_render.py` (`render_reader_html` ~lines 725–751; `write_reader_docx` ~lines 977–1008)
- Modify: `index.html` (`renderClimateVerifiedAssessment` — the `csr` rating block and final assembly ~lines 4635, 4754)
- Test: `tests/test_climate_verified_render.py`

Currently the executive readout renders under `HEADINGS[0]`, then `HEADINGS[1]` ("Core climate-FCV questions"), and the rating scale renders **inside** the Core Questions section (`render_reader_html` line ~748–750). Move the rating so it renders **immediately after the executive readout and before `HEADINGS[1]`**, i.e. as part of the Overview.

- [ ] **Step 1: Write the failing test (server HTML ordering).** Add to `tests/test_climate_verified_render.py`:

```python
def test_rating_scale_renders_in_overview_before_core_questions():
    from sector_lenses.climate_verified_render import build_reader_model, render_reader_html
    assessment = {
        "executive_readout": "Alpha sentence. " * 60,  # satisfies length gate loosely
        "judgments": {"sensitivity": {"value": "moderate", "rationale": "Because.", "evidence_ids": []}},
        "priorities": [],
    }
    html = render_reader_html(build_reader_model(assessment))
    rating_pos = html.find("climate-sens-rating")
    core_pos = html.find("Core climate-FCV questions")
    assert rating_pos != -1 and core_pos != -1
    assert rating_pos < core_pos  # rating is in the overview, above core questions
```

- [ ] **Step 2: Run it, verify it fails.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_verified_render.py::test_rating_scale_renders_in_overview_before_core_questions`
Expected: FAIL (rating currently renders after the core-questions heading).

- [ ] **Step 3: Move the rating in `render_reader_html`.** Remove this block from just after the `HEADINGS[1]` heading + `CORE_QUESTIONS_INTRO` paragraph (lines ~746–750):

```python
    rating = _mapping(model.get("climate_sensitivity_rating"))
    if rating:
        parts.append(_sensitivity_rating_html(rating))
```

and re-insert it immediately after the executive-readout loop and the `evidence_status` block, i.e. right before `parts.append(_heading(2, HEADINGS[1]))` (line ~746). The rating now sits between the readout and the Core Questions heading.

- [ ] **Step 4: Mirror in `write_reader_docx`.** Move the rating block (lines ~994–1007, `rating = _mapping(...)` through the caveat paragraph) so it renders after the executive-readout loop / `evidence_status` field and **before** `document.add_heading(HEADINGS[1], level=1)` (line ~992).

- [ ] **Step 5: Mirror in the frontend.** In `index.html` `renderClimateVerifiedAssessment`, locate where the `csr` rating HTML is currently concatenated (inside the core-questions section variable) and move it into the Overview: append the rating HTML right after `execHtml`/`statusHtml` and before `coreQuestionsSection` in the final `return` (line ~4754). Verify by grep that `climate-sens-rating` (or the csr variable) now precedes `coreQuestionsSection` in the returned template string.

- [ ] **Step 6: Run the render test + full render suite.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_verified_render.py`
Expected: PASS. Update any existing test that asserted the rating appears after the core-questions heading.

- [ ] **Step 7: Commit.**

```bash
git add sector_lenses/climate_verified_render.py index.html tests/test_climate_verified_render.py
git commit -m "feat: lift climate sensitivity rating into a top overview block (all three surfaces)"
```

---

## Task 3: Drop routing/authority metadata and hide evidence codes from visible tiers

**Files:**
- Modify: `sector_lenses/climate_verified_render.py` (`PRIORITY_FIELDS` ~lines 114–133; core-question evidence render ~769–775; rating evidence in `_sensitivity_rating_html` ~694–698; minor-point evidence ~854–860; flag document-basis ~832–833; and the DOCX equivalents ~1004, 1022, 1064, 1084)
- Modify: `index.html` (`detailFields` ~line 4665; core-question evidence; rating evidence; minor-point evidence)
- Test: `tests/test_climate_verified_render.py`

Decision (from spec): the model-internal routing fields never appear in the reader view; raw evidence codes (`PF-`/`RG-`/`PW-`/`ER-`) are removed from the visible tiers but retained in the "How this analysis was produced" fold (the evidence key), which reads from the raw assessment and is unaffected.

- [ ] **Step 1: Write the failing test.** Add to `tests/test_climate_verified_render.py`:

```python
def test_visible_tiers_hide_routing_metadata_and_evidence_codes():
    from sector_lenses.climate_verified_render import build_reader_model, render_reader_html, attach_provenance
    assessment = {
        "executive_readout": "Alpha sentence. " * 60,
        "judgments": {"sensitivity": {"value": "moderate", "rationale": "Because.", "evidence_ids": ["PF-001"]}},
        "priorities": [{
            "rank": 1, "title": "Do the thing", "recommendation_id": "REC-001",
            "decision": "Do it.", "minimum_action": "Add a clause.", "confidence": "high",
            "routing_status": "standard_document_advisory", "authority_basis": "none_verified",
            "recommendation_basis": "project_evidence", "pathway_ids": ["PW-001"],
            "project_anchor_ids": ["PF-001"],
            "current_document_drafting": {"target_document": "PCN", "target_section": "X",
                "drafting_status": "advisory_proposal", "text": "Add text.",
                "project_basis_ids": [], "gap_basis_ids": [], "guidance_ids": []},
        }],
    }
    model = build_reader_model(assessment)
    html = render_reader_html(model)
    # Priority card must not show the internal routing metadata rows.
    assert "Routing status" not in html
    assert "Authority basis" not in html
    assert "Recommendation basis" not in html
    assert "Pathway references" not in html
    # The priority body must not leak raw evidence codes.
    priorities_section = html.split("Ranked operational priorities", 1)[1].split("Points to check", 1)[0]
    assert "PW-001" not in priorities_section
    assert "PF-001" not in priorities_section
    # But the evidence key in the provenance fold still resolves codes.
    model = attach_provenance(model, assessment)
    html2 = render_reader_html(model)
    assert "Evidence key" in html2
```

- [ ] **Step 2: Run it, verify it fails.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_verified_render.py::test_visible_tiers_hide_routing_metadata_and_evidence_codes`
Expected: FAIL ("Routing status" present).

- [ ] **Step 3: Trim `PRIORITY_FIELDS`.** In `climate_verified_render.py` replace the `PRIORITY_FIELDS` tuple (lines ~114–133) with only the reader-relevant rows, dropping every reference/metadata row:

```python
PRIORITY_FIELDS = (
    ("Decision", "decision"),
    ("Minimum action", "minimum_action"),
    ("Enhanced action", "enhanced_action"),
    ("Activation condition", "enhanced_activation"),
    ("Who", "responsible_function"),
    ("Completion evidence", "completion_evidence"),
    ("Completion evidence status", "completion_evidence_status"),
    ("Confidence", "confidence"),
    ("Limitation", "limitation"),
    ("Caution", "caution"),
)
```

(This drops Routing status, Authority basis, Recommendation basis, Project evidence references, Pathway references, Existing-response references, Residual-gap references, Instrument references from **both** the HTML loop at ~802 and the DOCX loop at ~1044, which both iterate `PRIORITY_FIELDS`.)

- [ ] **Step 4: Remove the inline evidence line from core questions (HTML + DOCX).** In `render_reader_html` delete the core-question evidence block (lines ~769–775, `evidence_refs = _field_text(question.get("evidence_ids"))` and its `parts.append`). In `write_reader_docx` delete the matching `_docx_field(document, "Evidence", question.get("evidence_ids"))` (~line 1022).

- [ ] **Step 5: Remove the evidence line from the rating (HTML + DOCX).** In `_sensitivity_rating_html` delete the `evidence`/`evidence_html` lines (~694–698) and the `+ evidence_html` in the return. In `write_reader_docx` delete `_docx_field(document, "Evidence", rating.get("evidence_ids"))` (~line 1004).

- [ ] **Step 6: Remove the evidence line from minor points and the document-basis from flags (HTML + DOCX).** In `render_reader_html`: delete the minor-point `refs`/Evidence block (~854–860) and the `"Document basis:"` fragment inside the flag render (~832–833) — keep "Why it matters" and "Suggested verification". In `write_reader_docx`: delete `_docx_field(document, "Evidence", point.get("residual_gap_ids"))` (~1084) and `_docx_field(document, "Document basis", flag.get("document_basis_ids"))` (~1064).

- [ ] **Step 7: Mirror in the frontend.** In `index.html` `renderClimateVerifiedAssessment`: (a) delete the `detailFields` array (~line 4665) and the loop that renders it into each priority card; (b) remove the core-question "Evidence:" line if present; (c) remove the rating "Evidence" line if present; (d) remove the minor-point "Evidence:" line (~4694 `ptcItem` `ev` argument — pass `''`). Verify by grep: `grep -n "Routing status\|detailFields\|Pathway references" index.html` returns nothing in the verified renderer.

- [ ] **Step 8: Run render tests.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_verified_render.py tests/test_climate_evidence_trail.py`
Expected: PASS. Fix any existing test asserting a dropped field is present.

- [ ] **Step 9: Commit.**

```bash
git add sector_lenses/climate_verified_render.py index.html tests/test_climate_verified_render.py
git commit -m "feat: drop routing metadata + inline evidence codes from climate reader visible tiers (fold keeps the audit trail)"
```

---

## Task 4: Surface the Quick fixes tier (un-collapse + reframe how-to-address)

**Files:**
- Modify: `sector_lenses/climate_verified_render.py` (`render_reader_html` points-to-check `<details>` ~820–861; `write_reader_docx` ~1056–1084; `HEADINGS` ~100–106 and `POINTS_TO_CHECK_INTRO` ~109–113 if relabelled)
- Modify: `index.html` (`renderClimateVerifiedAssessment` — the `flagsHtml`/`ptcItem`/final `<details>` ~4690–4754)
- Test: `tests/test_climate_verified_render.py`

The `review_readiness_flags` ("Document points to confirm") and `minor_climate_points` currently render **inside a collapsed `<details>`**. Make this a **visible `<section>`** placed after Priorities, and reframe the minor-point label from "How to check" to "How to address".

- [ ] **Step 1: Write the failing test.** Add to `tests/test_climate_verified_render.py`:

```python
def test_quick_fixes_are_visible_not_collapsed():
    from sector_lenses.climate_verified_render import build_reader_model, render_reader_html
    assessment = {
        "executive_readout": "Alpha sentence. " * 60,
        "judgments": {"sensitivity": {"value": "moderate", "rationale": "Because.", "evidence_ids": []}},
        "priorities": [],
        "minor_climate_points": [
            {"point": "Reconcile the figure", "why": "Two values differ.",
             "how_to_check": "Confirm the cost across cover and tables.", "residual_gap_ids": []}
        ],
        "review_readiness_flags": [
            {"flag": "Empty screening field", "why_it_matters": "Template field blank.",
             "document_basis_ids": [], "suggested_verification": "Confirm before the meeting."}
        ],
    }
    html = render_reader_html(build_reader_model(assessment))
    quick = html.split("Ranked operational priorities", 1)[1]
    # The quick-fix content appears outside any <details> (before the technical annex fold).
    head, _, annex = quick.partition("Technical annex")
    assert "Reconcile the figure" in head
    assert "Empty screening field" in head
    assert "How to address" in head
    # The quick-fix block itself is a <section>, not wrapped in <details><summary>Points to check…
    assert "<summary>Points to check" not in head
```

- [ ] **Step 2: Run it, verify it fails.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_verified_render.py::test_quick_fixes_are_visible_not_collapsed`
Expected: FAIL (currently wrapped in `<details>` and label is "How to check").

- [ ] **Step 3: Un-collapse in `render_reader_html`.** Replace the opening of the points-to-check block:

```python
    parts.append("<details><summary>")
    parts.append(html.escape(HEADINGS[3]))
    parts.append("</summary>")
    parts.append(f"<p>{html.escape(POINTS_TO_CHECK_INTRO)}</p>")
```

with a visible section heading:

```python
    parts.append(_heading(2, HEADINGS[3]))
    parts.append(f"<p>{html.escape(POINTS_TO_CHECK_INTRO)}</p>")
```

and remove the matching `parts.append("</details>")` that closes this block (~line 861). Change the minor-point label from `"<strong>How to check:</strong> "` to `"<strong>How to address:</strong> "` (~line 850).

- [ ] **Step 4: Mirror in `write_reader_docx`.** The DOCX already uses `document.add_heading(HEADINGS[3], level=1)` (visible) — no un-collapse needed. Change `_docx_field(document, "How to check", point.get("how_to_check"))` to `"How to address"` (~line 1083).

- [ ] **Step 5: Mirror in the frontend.** In `index.html`, the final assembly (~line 4754) wraps `flagsHtml` in `<details class="climate-fold"><summary>Points to check before the decision meeting</summary>...`. Replace that wrapper with a visible block: `<section class="climate-quick-fixes"><h2>Points to check before the decision meeting</h2>${flagsHtml}</section>`. Change the `ptcItem` label (~line 4694) from `How to check` to `How to address`. Verify by grep that `climate-quick-fixes` exists and the old `<summary>Points to check` wrapper is gone from the verified renderer.

- [ ] **Step 6: Run render tests.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_verified_render.py`
Expected: PASS. Update any test asserting the points-to-check block is collapsed / uses "How to check".

- [ ] **Step 7: Commit.**

```bash
git add sector_lenses/climate_verified_render.py index.html tests/test_climate_verified_render.py
git commit -m "feat: surface climate reader quick-fixes as a visible tier with how-to-address framing"
```

---

## Task 5: Relocate the per-question watch lines into a standalone Watch section

**Files:**
- Modify: `sector_lenses/climate_verified_render.py` (`render_reader_html` core-question watch ~764–768; `write_reader_docx` ~1021; add a new Watch section after Quick fixes; `HEADINGS`)
- Modify: `index.html` (`renderClimateVerifiedAssessment` — the `watch` inline at ~4650; add a Watch section)
- Test: `tests/test_climate_verified_render.py`

Realise the 3-tier model's monitor-only tier as a standalone "What to keep an eye on" section built from `core_questions[].watch`, and remove the inline "What to watch" line from each core-question card (no duplication; no new pipeline data). Place the Watch section after Quick fixes and before the Technical annex fold.

> **Handoff note for the reviewer:** this is the one realisation choice not fully pinned in the spec. The pipeline has no monitor-only list distinct from `core_questions[].watch`, so Watch consolidates those lines rather than introducing new model output. If you would rather keep the watch line inline on each core-question card *and* not have a separate section, drop this task — everything else stands.

- [ ] **Step 1: Add the Watch heading.** In `climate_verified_render.py` extend `HEADINGS` with a sixth entry, e.g. append `"What to keep an eye on"` as `HEADINGS[5]`. (Confirm no code indexes `HEADINGS` by a hard-coded `len`; the existing references are `HEADINGS[0..4]`.)

- [ ] **Step 2: Write the failing test.** Add to `tests/test_climate_verified_render.py`:

```python
def test_watch_lines_render_in_standalone_section_not_inline():
    from sector_lenses.climate_verified_render import build_reader_model, render_reader_html
    assessment = {
        "executive_readout": "Alpha sentence. " * 60,
        "judgments": {"sensitivity": {"value": "moderate", "rationale": "Because.", "evidence_ids": []}},
        "priorities": [],
        "core_questions": [
            {"question_id": "cq1", "theme": "cq1_interaction", "question": "Does X hold?",
             "source": "Guidance", "summary": "A finding.", "evidence_ids": [],
             "watch": "Keep an eye on the flood season."}
        ],
    }
    html = render_reader_html(build_reader_model(assessment))
    # Watch content appears once, in the standalone section, not inline in the core-question card.
    assert "What to keep an eye on" in html
    assert "Keep an eye on the flood season." in html
    core_block = html.split("Core climate-FCV questions", 1)[1].split("Ranked operational priorities", 1)[0]
    assert "What to watch" not in core_block  # inline line removed
```

- [ ] **Step 3: Run it, verify it fails.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_verified_render.py::test_watch_lines_render_in_standalone_section_not_inline`
Expected: FAIL (watch is currently inline; no standalone section).

- [ ] **Step 4: Remove the inline watch (HTML + DOCX).** In `render_reader_html` delete the core-question watch block (~764–768). In `write_reader_docx` delete `_docx_field(document, "What to watch", question.get("watch"))` (~1021).

- [ ] **Step 5: Add the Watch section (HTML).** After the Quick-fixes block and before the Technical annex `<details>` (~line 863), append:

```python
    watch_items = [
        (_text(q.get("question")), _text(q.get("watch")))
        for q in _records(model.get("core_questions"))
        if _text(q.get("watch"))
    ]
    if watch_items:
        parts.append(_heading(2, HEADINGS[5]))
        parts.append(
            "<p>These are things to monitor as the project develops. They are not "
            "actions to take now - just points to keep in view.</p><ul>"
        )
        for question_text, watch_text in watch_items:
            lead = f"<strong>{html.escape(question_text)}</strong> " if question_text else ""
            parts.append(f"<li>{lead}{html.escape(watch_text)}</li>")
        parts.append("</ul>")
```

- [ ] **Step 6: Add the Watch section (DOCX).** After the minor-points loop and before `document.add_heading(HEADINGS[4], level=1)` (~line 1086), add the equivalent: if any `core_questions[].watch`, `document.add_heading(HEADINGS[5], level=1)`, an intro paragraph, then one paragraph per watch item (`f"{question_text}: {watch_text}"`).

- [ ] **Step 7: Mirror in the frontend.** In `index.html`: (a) remove the inline `watch` variable render in the core-question map (~line 4650, set it to `''` or delete the concatenation); (b) build a Watch section string from `r.core_questions` entries with a truthy `watch` and insert it into the final `return` after the quick-fixes section and before the provenance fold. Verify by grep that the verified renderer no longer emits "What to watch" inline and now emits "What to keep an eye on".

- [ ] **Step 8: Run render tests.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_verified_render.py`
Expected: PASS. Update any test asserting an inline "What to watch" line.

- [ ] **Step 9: Commit.**

```bash
git add sector_lenses/climate_verified_render.py index.html tests/test_climate_verified_render.py
git commit -m "feat: consolidate climate reader watch lines into a standalone Watch section"
```

---

## Task 6: Core-question diagnose-vs-act discipline + promotion rule (prompt)

**Files:**
- Modify: `sector_lenses/climate_verified_prompts.py` (`_judgment_prompt`, ~lines 100–164)
- Test: `tests/test_climate_analysis_prompts.py` (or the existing prompt-assertion test file — confirm which one asserts on `_judgment_prompt`/`build_verified_stage_prompt`)

The judgment prompt already forbids predicting outcomes and requires a one-line watch note. Add the diagnose-vs-act split and the materiality-driven promotion rule so core questions stay diagnostic and material issues surface as priorities (written once).

- [ ] **Step 1: Write the failing test.** Add to the prompt-assertion test file:

```python
def test_judgment_prompt_states_diagnose_vs_act_and_promotion_rule():
    from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
    prompt = build_verified_stage_prompt("judgment_review", {"facts": [], "analysis": {}})
    lowered = prompt.lower()
    assert "do not propose the fix" in lowered or "do not restate the fix" in lowered
    assert "priority" in lowered and "materiality" in lowered
    assert "each finding" in lowered  # one-finding-one-tier discipline
```

(First open the test file and copy the exact helper/signature used to build the judgment prompt in an existing test, so the call matches the real API.)

- [ ] **Step 2: Run it, verify it fails.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q <that file>::test_judgment_prompt_states_diagnose_vs_act_and_promotion_rule`
Expected: FAIL.

- [ ] **Step 3: Add the rule to `_judgment_prompt`.** Insert this sentence into the core-questions instruction paragraph (after the existing "never promise or predict an outcome, and add a one-line watch note" sentence, ~line 151):

```
Keep each core-question answer diagnostic: describe what the document does and does
not do and add the one-line watch note, but do not propose the fix in the answer.
Where an issue is material enough to act on, it must instead appear once as a ranked
operational priority below (the priority carries the mechanism and drafting); do not
restate that fix in the core-question answer. Assign each finding to exactly one place -
a ranked priority, a smaller point to address, or a watch note - never more than one.
```

- [ ] **Step 4: Run the test + prompt suite.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q <that file>`
Expected: PASS.

- [ ] **Step 5: Commit.**

```bash
git add sector_lenses/climate_verified_prompts.py tests/<that file>
git commit -m "feat: climate judgment prompt enforces diagnose-vs-act split + one-tier promotion rule"
```

---

## Task 7: Calibration guardrails (acronym-from-source, verb fidelity, verified-vs-attributed)

**Files:**
- Modify: `sector_lenses/climate_verified_prompts.py` (`_common`, ~lines 16–34 — the shared instruction wrapper applied to every stage)
- Test: the prompt-assertion test file

- [ ] **Step 1: Write the failing test.**

```python
def test_common_prompt_carries_calibration_guardrails():
    from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
    prompt = build_verified_stage_prompt("fact_extractor", {}).lower()
    assert "acronym" in prompt            # do not expand an acronym the source defines
    assert "verb" in prompt or "affected" in prompt  # preserve a number's verb
    assert "cannot verify" in prompt or "unverified" in prompt  # verified vs attributed
```

(Confirm the exact stage key for the fact stage from `build_verified_stage_prompt`/`STAGE_OUTPUT_SCHEMAS`; the grep in Task 1 Step 5 showed the builder keys — use the real key, e.g. `"fact_extractor"`, mirroring an existing test.)

- [ ] **Step 2: Run it, verify it fails.**

- [ ] **Step 3: Add the guardrails to `_common`.** Append to the shared instruction string returned by `_common`:

```
Calibration rules: when you name an entity that the document abbreviates, use the
document's own expansion verbatim or keep the acronym - never invent or guess an
expansion. When you restate a number from the source, keep the source's own verb and
qualifier (for example "people affected by flooding" must not become "people
displaced"). State a claim as fact only when it is grounded in the verified registers;
if a figure, institution, event, or policy detail cannot be verified from those
registers, mark it as unverified context to confirm rather than asserting it.
```

- [ ] **Step 4: Run the test + prompt suite.** Expected: PASS.

- [ ] **Step 5: Commit.**

```bash
git add sector_lenses/climate_verified_prompts.py tests/<that file>
git commit -m "feat: add acronym/verb-fidelity/verified-vs-attributed calibration guardrails to climate prompts"
```

---

## Task 8: Two new driver questions (conflict-geography overlap; participation quality)

**Files:**
- Modify: `climate_question_bank.py` (`CLIMATE_DRIVER_QUESTIONS`, ~lines 253–274)
- Test: `tests/test_climate_driver_depth.py`

Add two generic, climate-tied driver questions that render as core-question cards via the existing v9.29 `select_triggered_drivers` mechanism. Keep them worded as design questions, never predictions, and explicitly tied to the climate/environmental dimension (consistent with the existing five). `_CORE_QUESTION_CAP` stays 7.

- [ ] **Step 1: Write the failing test.** Add to `tests/test_climate_driver_depth.py`:

```python
def test_new_driver_questions_fire_on_generic_triggers():
    from climate_question_bank import select_triggered_drivers, CLIMATE_DRIVER_QUESTIONS
    ids = {q["id"] for q in CLIMATE_DRIVER_QUESTIONS}
    assert {"dq-geo-overlap", "dq-participation-quality"} <= ids
    # Geo-overlap fires on conflict-location language.
    geo = select_triggered_drivers("Activities are concentrated in conflict-affected districts.")
    assert any(q["id"] == "dq-geo-overlap" for q in geo)
    # Participation quality fires on representation/monitoring language.
    part = select_triggered_drivers("The project mandates a women's quota on each committee.")
    assert any(q["id"] == "dq-participation-quality" for q in part)
```

- [ ] **Step 2: Run it, verify it fails.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_driver_depth.py::test_new_driver_questions_fire_on_generic_triggers`
Expected: FAIL (KeyError/AssertionError — questions not present).

- [ ] **Step 3: Add the two questions.** Append to the `CLIMATE_DRIVER_QUESTIONS` list (before the closing `]` at ~line 274):

```python
    {"id": "dq-geo-overlap", "theme": "driver_geo_overlap",
     "question": "Do the project's climate activities actually land in the specific places where conflict and fragility are worst, or does the geographic footprint of the climate investment miss - or avoid - the most fragile districts it is meant to help?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["conflict-affected", "district", "region", "state", "province", "county", "target area", "geographic", "location", "site selection", "hotspot", "border"]},
    {"id": "dq-participation-quality", "theme": "driver_participation_quality",
     "question": "Beyond meeting a representation quota, does the design monitor the quality of participation - whether women, displaced people, and marginalised groups actually have voice in the climate and resource decisions (closures, allocations, benefit-sharing) that affect them?",
     "source": "Conflict-Sensitive Climate Action Compendium",
     "triggers": ["quota", "representation", "participation", "consultation", "inclusion", "women", "youth", "marginalised", "marginalized", "voice", "decision-making", "membership"]},
```

- [ ] **Step 4: Run the driver test + full driver suite.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/test_climate_driver_depth.py`
Expected: PASS.

- [ ] **Step 5: Commit.**

```bash
git add climate_question_bank.py tests/test_climate_driver_depth.py
git commit -m "feat: add conflict-geography-overlap + participation-quality climate driver questions"
```

---

## Task 9: Full-suite regression + docs

**Files:**
- Modify: `claude.md` (version-history entry) — tracked lowercase
- Test: whole suite

- [ ] **Step 1: Run the whole suite.**

Run: `"C:/WBG/Python313/python.exe" -m pytest -q tests/`
Expected: PASS at the Task-0 baseline count **plus** the new tests added here (≈ +8). If any pre-existing test fails, it is almost certainly one that asserted the old 3-cap, the old rating position, an inline watch line, a dropped metadata row, or "How to check" — update it to the new contract (do not weaken a genuine assertion).

- [ ] **Step 2: Add a version-history entry to `claude.md`.** Add a `v9.32` bullet under the version history summarising: overview-at-top (rating scale lifted), diagnose-vs-act split + promotion rule, 3-tier output (Priorities / visible Quick fixes with how-to-address / standalone Watch), priority cap 3→5 (both `build_reader_model` and `admit_and_rank`), routing metadata + inline evidence codes dropped from visible tiers (fold retains the audit trail), acronym/verb/verified-vs-attributed calibration guardrails, and two new driver questions. Note "all three reader surfaces kept in parity" and the new full-suite count. Add the ITS/FastAPI parity reminder to `FCV_BUILD_PARITY.md` §26 (design-only note; the mirror itself is handover item B1).

- [ ] **Step 3: Commit (one chained call).**

```bash
git add claude.md && git commit -m "docs: record v9.32 climate reader lay-readout restructure"
```

- [ ] **Step 4: Push to the smoke branch and smoke-test.**

```bash
git push origin HEAD:codex/climate-country-bank-deploy
```

Then, on the branch-testing Render service (`fcv-agent-1.onrender.com`, `CLIMATE_VERIFIED_RUN_MODE=smoke`), confirm a climate run renders: Overview with the rating scale at the top, diagnostic core questions (no inline fix), up to five priorities with no routing/authority/code rows, a visible Quick-fixes section with "How to address", and a standalone Watch section. Smoke validates structure only — a quality pass is a separate, cost-controlled step per `claude.md`.

---

## Self-review (completed against the spec)

- **Spec coverage:** Overview+rating (Task 2); diagnose-vs-act + promotion (Task 6); 3 tiers — Priorities (Task 1 cap), Quick fixes (Task 4), Watch (Task 5); count 3→5 both caps (Task 1); routing metadata + evidence codes dropped, fold retained (Task 3); calibration guardrails (Task 7); two new checks (Task 8); parity across all three surfaces (Tasks 2–5); reusability of the overview block — the rating render stays a single factored function (`_sensitivity_rating_html`), satisfying the "factored for general-run reuse" goal without touching the general run.
- **Placeholder scan:** none — every code step shows the code or the exact anchor to change; test-file/stage-key lookups are explicit "confirm the real signature" steps because those exact names must be read from the file, not guessed.
- **Type/name consistency:** `HEADINGS[5]` added once (Task 5) and used in both HTML and DOCX; `PRIORITY_FIELDS` trimmed once (Task 3) and consumed by both loops; `_CORE_QUESTION_CAP` unchanged (Task 8 adds ≤2 candidates, within the 7 cap).
- **Open realisation choice:** the standalone Watch section (Task 5) is flagged for the reviewer; dropping Task 5 leaves a coherent result.
