# Climate Reader Guidance and Hierarchy Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved balanced Climate-FCV reader treatment with project-specific WBG guidance, progressive priority disclosure, numbered secondary points, and a simpler methodology section.

**Architecture:** Keep `build_reader_model()` plus `attach_provenance()` as the canonical reader pipeline. Build deterministic `guidance_items` from validated core-question summaries and static WBG source metadata, then render that same data across Python HTML, DOCX, the live JavaScript reader and standalone export. No additional LLM call or source-of-truth assessment-schema change is required.

**Tech Stack:** Python 3.13, Flask, `python-docx`, browser-native HTML/CSS/JavaScript, pytest, Node-backed renderer contract tests.

---

## File Map

- `climate_question_bank.py`: add action-oriented, reader-facing practical value metadata to the core WBG literature catalog.
- `sector_lenses/climate_verified_render.py`: create canonical guidance items, replace the redundant priority-title summary, and align Python HTML/DOCX output with the approved reader hierarchy.
- `index.html`: implement the live/export visual treatment and backward-compatible guidance fallback for older saved reader objects.
- `tests/test_climate_verified_render.py`: test canonical guidance selection, summaries, Python HTML and DOCX behavior.
- `tests/test_climate_lens_frontend.py`: execute the real JavaScript renderer and lock the balanced hierarchy and guidance prose.
- `tests/test_sector_lens_app_contract.py`: preserve export parity, semantic markup, focus styles and ordering contracts.
- `claude.md`: record the new reader contract and version note.
- `docs/reference/reference_frontend_functions.md`: update the maintained frontend renderer reference.

### Task 1: Build Canonical Project-Specific Guidance Items

**Files:**
- Modify: `climate_question_bank.py`
- Modify: `sector_lenses/climate_verified_render.py`
- Test: `tests/test_climate_verified_render.py`

- [ ] **Step 1: Write failing canonical guidance tests**

Add tests that construct catalog sources and admitted core questions directly, then assert one-to-four selection, stable ordering, public-URL filtering and project-specific prose:

```python
def test_guidance_items_are_ranked_capped_and_project_specific():
    questions = [
        {
            "source": "Maximizing the Peace and Social Dividends of Climate Action",
            "question": "Can shared governance create a peace dividend?",
            "summary": (
                "BFMUs bring competing resource users into shared governance. "
                "The Pariang value chain links refugee and host communities."
            ),
            "watch": "Confirm that benefit-sharing rules cover climate shocks.",
        },
        {
            "source": "FCV-Sensitive Climate Action Framework",
            "question": "Will infrastructure remain workable?",
            "summary": "Flood-resilient fisheries infrastructure is planned at six sites.",
            "watch": "Check combined flood-conflict contingency arrangements.",
        },
    ]
    items = build_climate_guidance_items(questions, CLIMATE_LITERATURE_REFERENCES)
    assert [item["title"] for item in items] == [
        "Maximizing the Peace and Social Dividends of Climate Action",
        "FCV-Sensitive Climate Action Framework",
    ]
    assert "BFMUs" in items[0]["project_use"]
    assert "Pariang" in items[0]["project_use"]
    assert "benefit-sharing" in items[0]["project_use"]
    assert "Can shared governance" not in items[0]["project_use"]


def test_guidance_items_do_not_pad_with_unrelated_or_non_public_sources():
    questions = [{
        "source": "Matched source",
        "question": "A question",
        "summary": "A verified project detail.",
        "watch": "Confirm the follow-up.",
    }]
    sources = [
        {"title": "Matched source", "url": "https://www.worldbank.org/a", "practical_value": "Use this source."},
        {"title": "Unrelated source", "url": "https://www.worldbank.org/b", "practical_value": "Do not show."},
        {"title": "Private source", "url": "https://localhost/internal", "practical_value": "Do not show."},
    ]
    items = build_climate_guidance_items(questions, sources)
    assert [item["title"] for item in items] == ["Matched source"]


def test_guidance_items_cap_at_four_and_prefer_more_matches():
    sources = [
        {"title": "Source A", "url": "https://www.worldbank.org/source-a", "practical_value": "Use A."},
        {"title": "Source B", "url": "https://www.worldbank.org/source-b", "practical_value": "Use B."},
        {"title": "Source C", "url": "https://www.worldbank.org/source-c", "practical_value": "Use C."},
        {"title": "Source D", "url": "https://www.worldbank.org/source-d", "practical_value": "Use D."},
        {"title": "Source E", "url": "https://www.worldbank.org/source-e", "practical_value": "Use E."},
    ]
    questions = [
        {"source": "Source A", "summary": "A first detail.", "watch": "Check A1."},
        {"source": "Source A", "summary": "A second detail.", "watch": "Check A2."},
        {"source": "Source B", "summary": "B detail.", "watch": "Check B."},
        {"source": "Source C", "summary": "C detail.", "watch": "Check C."},
        {"source": "Source D", "summary": "D detail.", "watch": "Check D."},
        {"source": "Source E", "summary": "E detail.", "watch": "Check E."},
    ]
    items = build_climate_guidance_items(questions, sources)
    assert [item["title"] for item in items] == [
        "Source A", "Source B", "Source C", "Source D"
    ]
    assert len(items) == 4
```


- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests\test_climate_verified_render.py -q -p no:cacheprovider --basetemp='.tmp\pytest-guidance-canonical-red-20260810'
```

Expected: FAIL because `build_climate_guidance_items` does not exist and the catalog has no `practical_value` metadata.

- [ ] **Step 3: Add practical-value metadata**

Add these strings to the corresponding `CLIMATE_LITERATURE_REFERENCES` entries:

```python
"practical_value": (
    "Use this source to identify how climate action can strengthen peace and "
    "social outcomes, and where project design can maximize those dividends."
),
```

```python
"practical_value": (
    "Use this source to stress-test whether climate action is conflict-sensitive, "
    "avoids harm and remains deliverable in fragile settings."
),
```

```python
"practical_value": (
    "Use this source to assess how environmental and natural-resource governance "
    "can reduce conflict risks and create incentives for cooperation."
),
```

Add these exact values to the Compendium and CCDR guidance entries:

```python
"practical_value": (
    "Use this source for practical examples of adapting climate programming to "
    "conflict dynamics, exclusion risks and changing implementation conditions."
),
```

```python
"practical_value": (
    "Use this source to connect country-level climate and FCV diagnostics to "
    "operational priorities, sequencing and investment choices."
),
```

Do not add a Compendium URL unless an official public World Bank URL has been verified.

- [ ] **Step 4: Implement the deterministic guidance builder**

In `sector_lenses/climate_verified_render.py`, add `urlparse` and these bounded helpers:

```python
from urllib.parse import urlparse


def _normalize_source_title(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", _text(value).casefold().replace("&", " and ")).strip()


def _public_world_bank_https_url(value: object) -> bool:
    try:
        parsed = urlparse(_text(value))
    except ValueError:
        return False
    hostname = (parsed.hostname or "").casefold()
    return bool(
        parsed.scheme == "https"
        and hostname
        and not parsed.username
        and not parsed.password
        and parsed.port is None
        and (hostname == "worldbank.org" or hostname.endswith(".worldbank.org"))
    )


def _first_sentence(value: object) -> str:
    paragraph = re.split(r"\n\s*\n+", _text(value).strip(), maxsplit=1)[0]
    match = re.match(r"^(.*?[.!?])(?:\s|$)", paragraph)
    return _text(match.group(1) if match else paragraph)


def build_climate_guidance_items(
    core_questions: object,
    sources: object,
) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for question in _records(core_questions):
        key = _normalize_source_title(question.get("source"))
        if key:
            grouped.setdefault(key, []).append(question)

    candidates = []
    for source_index, source in enumerate(_records(sources)):
        title = _text(source.get("title"))
        matches = grouped.get(_normalize_source_title(title), [])
        if not matches or not _public_world_bank_https_url(source.get("url")):
            continue
        details = []
        watches = []
        for question in matches[:2]:
            sentence = _first_sentence(question.get("summary"))
            if sentence and sentence not in details:
                details.append(sentence)
            watch = _text(question.get("watch"))
            if watch and watch not in watches:
                watches.append(watch)
        project_use = "For this project, " + " ".join(details)
        if watches:
            project_use += " The team can use the source to follow up on: " + watches[0]
        candidates.append({
            "title": title,
            "url": _text(source.get("url")),
            "practical_value": _text(source.get("practical_value") or source.get("description")),
            "project_use": project_use.strip(),
            "match_count": len(matches),
            "source_order": source_index,
        })
    candidates.sort(key=lambda item: (-int(item["match_count"]), int(item["source_order"])))
    return [
        {key: value for key, value in item.items() if key not in {"match_count", "source_order"}}
        for item in candidates[:4]
    ]
```

In `attach_provenance()`, set `reader["guidance_items"]` after attaching sources:

```python
reader["guidance_items"] = build_climate_guidance_items(
    reader.get("core_questions"), reader.get("sources")
)
```

- [ ] **Step 5: Run the canonical tests and verify GREEN**

Run the Step 2 command with a fresh basetemp ending `-green-20260810`. Expected: PASS.

- [ ] **Step 6: Commit Task 1**

```powershell
git add -- climate_question_bank.py sector_lenses/climate_verified_render.py tests/test_climate_verified_render.py
git commit -m "feat: tailor climate guidance to project findings"
```

### Task 2: Align Canonical HTML and DOCX Reader Content

**Files:**
- Modify: `sector_lenses/climate_verified_render.py`
- Modify: `tests/test_climate_verified_render.py`
- Modify: `tests/test_climate_evidence_trail.py`
- Modify: `tests/test_climate_minor_points.py`

- [ ] **Step 1: Write failing HTML/DOCX hierarchy tests**

Add assertions that the Python HTML and DOCX surfaces:

```python
assert 'class="climate-overview-panel"' in html
assert "Evidence key" not in html
assert "Run diagnostics" not in html
assert "Evidence status" not in html
assert "Sources &amp; further reading" in html
assert "Method, limitations, and sources" in html
assert html.index("Smaller climate") < html.index("Document points")
assert '<details class="climate-priority-disclosure" open>' in html
assert html.count('class="climate-item-number"') == expected_number_count
assert "BFMUs" in html
assert "Maximizing the Peace" in html
```

For DOCX, reopen the in-memory document and assert that all priority narratives remain present while `Evidence key`, `Run diagnostics`, `Evidence status`, and technical-annex labels are absent. Assert `Sources & further reading` and all guidance-item project-use paragraphs remain present.

- [ ] **Step 2: Run focused renderer tests and verify RED**

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests\test_climate_verified_render.py tests\test_climate_evidence_trail.py tests\test_climate_minor_points.py -q -p no:cacheprovider --basetemp='.tmp\pytest-canonical-reader-red-20260810'
```

Expected: FAIL on the old evidence key, diagnostics, evidence-status, priority presentation and point ordering.

- [ ] **Step 3: Replace the priority summary statement**

Update `_priority_summary()` so non-empty priorities return:

```python
statement = (
    f"Drawing on the overview and core climate-FCV questions, the analysis "
    f"identifies {count} main operational {noun} for strengthening climate "
    "resilience, conflict sensitivity and implementation readiness in this "
    "project. These are followed by secondary points to check before the "
    "decision meeting and issues to keep under review as preparation advances."
)
```

Use `noun = "priority" if count == 1 else "priorities"`. Preserve the existing zero-priority statement.

- [ ] **Step 4: Implement the approved Python HTML hierarchy**

Make these exact structural changes in `render_reader_html()`:

- wrap `_sensitivity_rating_html(rating)` in `<section class="climate-overview-panel">`;
- remove the non-approved evidence-status paragraph;
- render priority 1 as `<details class="climate-priority-disclosure" open>` and later priorities as the same element without `open`;
- put rank/title in `<summary>` and all existing body fields inside the disclosure;
- render smaller climate points before document flags;
- add a two-digit `<span class="climate-item-number">01</span>` for each check and watch item;
- render watch items as numbered sections rather than an unnumbered list;
- render `guidance_items` before methodology with practical-value and project-use paragraphs;
- remove the technical-annex disclosure, evidence-key block and run-diagnostics block;
- rename the methodology disclosure summary to `Method, limitations, and sources` and retain methodology, pathways, limitations text and sources/further reading.

- [ ] **Step 5: Align DOCX content**

In `write_reader_docx()`:

- remove evidence-status and technical-annex output;
- use the new narrative priority introduction;
- keep every priority fully expanded;
- put smaller climate points before document flags and prefix their headings with local two-digit numbers;
- prefix watch paragraphs with two-digit numbers;
- add `Relevant WBG guidance for this project`, then for each canonical item write title, practical value, project use and URL;
- retain methodology and sources/further reading;
- remove evidence-key and run-diagnostics headings and values.

- [ ] **Step 6: Run the renderer tests and verify GREEN**

Run the Step 2 command with a fresh basetemp ending `-green-20260810`. Expected: PASS.

- [ ] **Step 7: Commit Task 2**

```powershell
git add -- sector_lenses/climate_verified_render.py tests/test_climate_verified_render.py tests/test_climate_evidence_trail.py tests/test_climate_minor_points.py
git commit -m "feat: simplify canonical climate reader hierarchy"
```

### Task 3: Implement the Balanced Live and Exported HTML Reader

**Files:**
- Modify: `index.html`
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write a failing real-renderer contract test**

Extend the existing Node-backed fixture with at least four complete priorities, two minor points, two document flags, three watch points and five possible sources. Assert:

```javascript
assert(html.includes('class="climate-sens-rating climate-overview-panel"'));
assert(!html.includes('Evidence status:'));
assert(!html.includes('Evidence key'));
assert(!html.includes('Run diagnostics'));
assert(html.includes('Method, limitations, and sources'));
assert(!html.includes('final operational priorities are presented:'));
assert(html.includes('identifies 4 main operational priorities'));
assert((html.match(/<details class="climate-priority-card"/g) || []).length === 4);
assert((html.match(/<details class="climate-priority-card" open/g) || []).length === 1);
assert(html.includes('Complete drafting paragraph for priority four.'));
assert(html.indexOf('Smaller climate and fragility') < html.indexOf('Document points'));
assert((html.match(/class="climate-item-number"/g) || []).length >= 7);
assert(html.includes('BFMUs bring competing resource users into shared governance.'));
assert(!html.includes('Most useful for following up on:'));
```

Add a second guidance test for old saved readers that have `core_questions` plus `sources` but no `guidance_items`, proving the JavaScript fallback still creates bounded, project-specific items.

- [ ] **Step 2: Run the frontend tests and verify RED**

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests\test_climate_lens_frontend.py tests\test_sector_lens_app_contract.py -q -p no:cacheprovider --basetemp='.tmp\pytest-balanced-frontend-red-20260810'
```

Expected: FAIL on the old overview treatment, evidence status, repeated priority titles, always-open priorities, unnumbered checks/watch items and generic guidance.

- [ ] **Step 3: Update scoped reader CSS**

Within `.climate-verified-assessment`, add or update:

```css
.climate-overview-panel{background:#fff;border:1px solid #d7e1e7;border-left:5px solid var(--climate-rating-color,#147a3d);border-radius:10px;padding:20px;margin:0 0 24px}
.climate-priority-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);margin:0 0 10px;overflow:hidden}
.climate-priority-card>summary{display:flex;align-items:flex-start;gap:12px;padding:15px 18px;cursor:pointer;list-style:none}
.climate-priority-card>summary:focus-visible{outline:3px solid #f2a900;outline-offset:2px}
.climate-priority-card[open]>summary{border-bottom:1px solid #e5e7eb}
.climate-priority-body{padding:16px 18px}
.climate-numbered-item{display:grid;grid-template-columns:34px minmax(0,1fr);gap:10px;border-top:1px solid #eef0f3;padding:12px 0 8px}
.climate-item-number{font-weight:700;color:var(--wbg-blue);font-variant-numeric:tabular-nums}
```

At the 760 px breakpoint, keep a minimum 28 px number column and reduce panel/disclosure padding without changing content.

- [ ] **Step 4: Update JavaScript guidance construction**

Make `renderClimateRelevantGuidance(reader)` prefer `reader.guidance_items`. Update `buildClimateGuidanceItems(reader)` as a backward-compatible fallback that groups by normalized source, rejects unsafe URLs, uses source `practical_value || description`, takes first sentences from matched question `summary`, incorporates one `watch`, sorts by match count then catalog order, and caps at four.

Render each item as:

```javascript
`<article class="climate-guidance-item">
  <h4><a href="${esc(item.url)}" target="_blank" rel="noopener">${esc(item.title)}</a></h4>
  <p class="climate-guidance-value">${esc(item.practical_value)}</p>
  <p class="climate-guidance-use">${esc(item.project_use)}</p>
</article>`
```

Do not render the old question-title list.

- [ ] **Step 5: Update live renderer structure**

In `renderClimateVerifiedAssessment()`:

- delete `statusHtml` and keep `smokeHtml`;
- add `climate-overview-panel` to the sensitivity block;
- derive the priority transition from the priority count, ignoring legacy title-list statements for non-empty priorities;
- render every priority as native details, with only index zero carrying `open`;
- keep all existing priority body and nested Recommendation details in `.climate-priority-body`;
- pass local indexes to check/watch render helpers and display two-digit number spans;
- preserve smaller climate points before document points;
- replace the watch `<ul>` with numbered semantic sections;
- remove evidence-key and diagnostics construction;
- retain methodology/pathways, add a short limitations paragraph, retain sources/further reading, and use `Method, limitations, and sources` as the disclosure summary.

- [ ] **Step 6: Run frontend tests and verify GREEN**

Run the Step 2 command with a fresh basetemp ending `-green-20260810`. Expected: PASS.

- [ ] **Step 7: Commit Task 3**

```powershell
git add -- index.html tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py
git commit -m "feat: refine climate reader hierarchy and guidance"
```

### Task 4: Update Maintained Documentation

**Files:**
- Modify: `claude.md`
- Modify: `docs/reference/reference_frontend_functions.md`

- [ ] **Step 1: Update the release note and renderer contract**

Add a v9.35 entry to `claude.md` stating:

```markdown
- The verified Climate-FCV reader now uses a balanced hierarchy: a restrained overview panel, priority 1 open with lower priorities collapsed in HTML, numbered decision checks and monitoring points, and a narrative action transition instead of a repeated title list.
- Relevant WBG guidance is selected from one to four evidence-matched public sources (normally two to four) and explains project-specific learning value using validated core-question summaries; selection is deterministic, not random.
- Reader-facing evidence codes, run diagnostics, technical-annex diagnostics and the non-approved evidence-status banner are removed. Methodology, limitations, sources/further reading and all underlying runtime validation remain intact.
```

Update the frontend function reference for `buildClimateGuidanceItems()`, `renderClimateRelevantGuidance()` and `renderClimateVerifiedAssessment()` with the same contracts, including the old-reader fallback.

- [ ] **Step 2: Check documentation diff**

```powershell
git diff --check -- claude.md docs/reference/reference_frontend_functions.md
rg -n "v9.35|project-specific learning|priority 1" claude.md docs\reference\reference_frontend_functions.md
```

Expected: no whitespace errors and all three phrases present.

- [ ] **Step 3: Commit Task 4**

```powershell
git add -- claude.md docs/reference/reference_frontend_functions.md
git commit -m "docs: record climate reader refinement"
```

### Task 5: Full Verification and Visual QA

**Files:**
- Create: `output/20260810_climate-reader-balanced-preview.html`
- Create: `output/20260810_climate-reader-balanced-desktop.png`
- Create: `output/20260810_climate-reader-balanced-mobile.png`
- Verify only: all modified source/test/docs files

- [ ] **Step 1: Run the focused regression suite**

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests\test_climate_verified_render.py tests\test_climate_evidence_trail.py tests\test_climate_minor_points.py tests\test_climate_lens_frontend.py tests\test_sector_lens_app_contract.py tests\test_frontend_upload_caps.py -q -p no:cacheprovider --basetemp='.tmp\pytest-balanced-final-20260810'
```

Expected: all collected tests pass with exit code 0.

- [ ] **Step 2: Run the broader suite once**

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest -q -p no:cacheprovider --basetemp='.tmp\pytest-balanced-full-20260810'
```

Expected: pass. If pytest reaches completion but Windows raises the repository's documented basetemp cleanup `PermissionError`, run one `-x -vv` diagnostic to distinguish environment cleanup from a product assertion, report the exact first affected node, and do not loop.

- [ ] **Step 3: Generate a South Sudan-like standalone preview**

Use the existing preview-generation pattern in `output/20260809_generate-climate-fcv-implemented-preview.py`, but save to the three new dated filenames. The fixture must contain the approved South Sudan-like overview, four complete priorities, numbered checks/watch items and canonical project-specific guidance. Do not overwrite the existing preview or the paid quality export.

- [ ] **Step 4: Perform desktop and mobile visual QA**

At 1280 x 900 and a true 390 x 844 emulated viewport, verify:

- no horizontal overflow;
- overview is visually prominent but not nested;
- priority 1 is open and later priorities are closed;
- lower-priority titles wrap fully;
- numbers align with their prose;
- guidance paragraphs remain readable and do not become tile-heavy;
- methodology contains no evidence key or diagnostics;
- focus indicators are visible when tabbing through disclosures and links.

- [ ] **Step 5: Verify repository scope**

```powershell
git diff --check
git status --short
git log -6 --oneline
```

Expected: no tracked unstaged changes, no whitespace errors, and only the planned commits/files. Preserve the two pre-existing untracked handover documents and `output/` artifacts.

- [ ] **Step 6: Push the feature branch for review**

```powershell
git push origin HEAD:refs/heads/codex/climate-country-bank-deploy
```

Do not merge into the stable ITS branch or run another paid quality assessment without explicit user approval.

### Task 6: Collapse and Shorten Relevant WBG Guidance

**Files:**
- Modify: `sector_lenses/climate_verified_render.py`
- Modify: `index.html`
- Modify: `tests/test_climate_verified_render.py`
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `tests/test_sector_lens_app_contract.py` only if the shared print/export contract requires it
- Regenerate in place: `output/20260810_south-sudan-climate-fcv-refined-preview.html`

- [ ] **Step 1: Write failing canonical guidance tests**

Add tests that require `build_climate_guidance_items()` to retain source
selection and ranking while emitting one controlled practical-value sentence
and one project-specific follow-up sentence. Assert that full summary
paragraphs, second matched summaries and generic tail copy are absent. Include
fixtures with abbreviations, punctuation, HTML-sensitive text, an empty watch
with a non-empty question fallback, and an empty watch/question pair that is
not promoted.

- [ ] **Step 2: Write failing canonical HTML and DOCX tests**

Require canonical HTML to keep the numbered guidance section heading and wrap
the entire body in exactly one closed
`<details class="climate-guidance-disclosure">` whose summary is `Where the
team can go for more detailed follow-up`. Assert that source articles are not
nested disclosures. Require DOCX to contain the same short source prose in
expanded form, including the follow-up heading.

- [ ] **Step 3: Write failing live/standalone and print tests**

Require `renderClimateRelevantGuidance()` to emit the same single closed native
disclosure and short two-line source treatment for canonical readers and the
old-reader fallback. Extend the real print-lifecycle test so the guidance
disclosure opens on `beforeprint` and returns to its prior closed state on
`afterprint`. Preserve a pre-opened state exactly.

- [ ] **Step 4: Run the new tests and verify RED**

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests\test_climate_verified_render.py tests\test_climate_lens_frontend.py tests\test_sector_lens_app_contract.py -q -p no:cacheprovider --basetemp='.tmp\pytest-guidance-follow-up-red-20260810'
```

Expected: failures show the current expanded guidance body, copied summary
paragraphs and missing guidance selector in the print-state handler.

- [ ] **Step 5: Implement the canonical short guidance contract**

In `build_climate_guidance_items()`, replace summary-paragraph assembly with a
small helper that selects the first distinct non-empty matched `watch` value and
returns `For this project, use the source to address this follow-up: <watch>`.
When no watch is available, use the first matched non-empty `question` as
`For this project, use the source to examine this question: <question>`.
Complete terminal punctuation without splitting or truncating sentences. Omit
items that have neither a watch nor a question. Keep the practical-value field,
ranking, source cap, source deduplication and URL validation unchanged.

Wrap all canonical HTML guidance content in one closed native disclosure. Keep
the numbered section heading outside it. In DOCX, add the follow-up heading and
render all source content normally, with no collapsed Word content.

- [ ] **Step 6: Implement matching live and standalone behavior**

Mirror the canonical project-use helper in `buildClimateGuidanceItems()` for
old saved readers. Make `renderClimateRelevantGuidance()` return one closed
`details.climate-guidance-disclosure` containing the intro and every selected
source. Add the guidance disclosure to the shared print selector so live and
standalone exports open it for printing and restore its prior state afterward.
Add scoped focus and mobile styles without adding per-source cards or nested
disclosures.

- [ ] **Step 7: Run focused tests and verify GREEN**

Run the Step 4 command with basetemp
`.tmp\pytest-guidance-follow-up-green-20260810`. Expected: all selected tests
pass.

- [ ] **Step 8: Regenerate the existing South Sudan preview without an LLM call**

```powershell
$env:PYTHONPATH='.'
& 'C:\WBG\Python313\python.exe' output\20260810_generate-south-sudan-refined-preview.py
```

Assert the generated preview has one closed guidance disclosure, three source
items, no copied full assessment paragraphs in guidance, and the existing seven
core questions and four full priorities.

- [ ] **Step 9: Complete browser and repository verification**

Inspect the regenerated preview at desktop and a viewport no wider than 760 px.
Check disclosure readability, keyboard focus, no horizontal overflow, print
expansion and exact state restoration. Then run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests -q -p no:cacheprovider --basetemp='.tmp\pytest-guidance-follow-up-all-20260810'
git diff --check
git status --short
```

Expected: every tracked test passes, `git diff --check` is clean, and existing
untracked handover/output files remain preserved.

- [ ] **Step 10: Obtain independent reviews and commit**

Request one spec-compliance review and one code-quality review against the
approved follow-up. Address findings, rerun affected tests, then commit only the
tracked implementation/test/documentation changes with:

```powershell
git add -- sector_lenses/climate_verified_render.py index.html tests/test_climate_verified_render.py tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py docs/superpowers/specs/2026-08-10-climate-reader-guidance-hierarchy-refinement-design.md docs/superpowers/plans/2026-08-10-climate-reader-guidance-hierarchy-refinement.md
git commit -m "feat: streamline climate guidance follow-up"
```

Do not push until the user asks or approves the prepared branch push.
