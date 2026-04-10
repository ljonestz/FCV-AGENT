# FCV App Robustness & TTL Output Quality — Design Spec

**Date:** 2026-03-23
**Branch:** docs/trim-claude-md
**Scope:** Approach 2 — JSON migration + prompt redesign + UX improvements
**Goal:** Outputs reliable enough for expert review AND polished enough for direct non-specialist TTL use

---

## 1. Context & Motivation

The FCV Project Screener is used by FCV specialists (primary) and will increasingly be used by non-specialist TTLs from health, agriculture, finance, and governance verticals. Two categories of issues were identified:

### 1.1 Structural Fragility
- Stage 4 delimiter parsing (`%%%PRIORITY_START%%% ... %%%PRIORITY_END%%%`) silently loses field content when the LLM wraps text across multiple lines or varies whitespace. Priority cards with empty `THE_GAP` or `SUGGESTED_DIRECTIONS` fields appear without any warning.
- No runtime validation that required fields are present and non-empty.

### 1.2 Output Quality Gaps
- Recommendations often present 3–4 option variants ("Option A / B / C") within a single priority, which is confusing for non-specialists who need a clear directive.
- Geographic specificity is requested in prompts but not enforced — vague recommendations ("improve stakeholder engagement") pass through without flagging.
- Citation hallucination is unguarded: a `[From: Kenya RRA 2023]` reference with no uploaded RRA goes to the TTL unchecked.
- S/R tag distinction (Sensitivity vs. Responsiveness) is not self-explanatory in the UI — non-specialist TTLs don't know what [R] means operationally.

---

## 2. Approach: JSON Migration + Prompt Redesign + UX Layer

Three sequenced layers:
1. **Foundation**: Migrate Stage 4 structured output to JSON (eliminates parsing fragility)
2. **Prompts**: Redesign Stage 4 prompt for single recommendations + geographic specificity + citation guard; tighten Stages 2–3
3. **UX**: Add tooltips, warning badges, upload feedback, Explorer improvements, stage consistency warnings

---

## 3. Stage 4 JSON Migration

### 3.1 Current System
The LLM produces a narrative memo followed by delimiter-wrapped priority blocks. A regex parser extracts fields line-by-line. Any multi-line field value causes silent data loss.

### 3.2 New System
The Stage 4 prompt instructs the LLM to append a single JSON block at the end of its response, wrapped in `%%%JSON_START%%%` / `%%%JSON_END%%%` markers. The narrative memo (preamble, exec summary, strengths, gaps) is preserved as display text before the JSON block. The backend parses ONLY the JSON block.

### 3.3 JSON Schema

```json
{
  "fcv_rating": "Adequate",
  "fcv_responsiveness_rating": "Low",
  "sensitivity_summary": "80–100 word assessment of sensitivity level",
  "responsiveness_summary": "80–100 word assessment of responsiveness level",
  "risk_to_project": "Paragraph on risks FROM the FCV context TO the project",
  "risk_from_project": "Paragraph on risks the project poses TO the FCV context",
  "priorities": [
    {
      "number": 1,
      "title": "Priority 1 · Short descriptive phrase",
      "dimension": "Inclusion",
      "tag": "[S+R]",
      "risk_level": "High",
      "the_gap": "Specific gap with named location/group/institution",
      "why_it_matters": "Why this gap matters for this project, including S/R pillar justification",
      "recommendation": "One cohesive recommended action with multiple components if needed",
      "who_acts": "TTL / FCV Specialist / Government counterpart / etc.",
      "when": "Project preparation / Implementation / Restructuring",
      "resources": "Minimal / Moderate / Significant"
    }
  ]
}
```

**Key field changes from current system:**
- `SUGGESTED_DIRECTIONS` → `recommendation` (singular, no options menu)
- All fields are validated as present and non-empty after parsing

### 3.4 Backend Changes (`app.py`)

**`extract_priorities()` rewrite:**
1. Find `%%%JSON_START%%%` ... `%%%JSON_END%%%` block in LLM output
2. `json.loads()` the content
3. Validate: all required fields present, `priorities` list has 4–5 items, each priority has all 10 fields non-empty
4. For each priority, run two post-processing checks:
   - **Specificity check**: scan `the_gap` and `recommendation` for capitalised words that appear mid-sentence (i.e., not the first word of a sentence). This is a lightweight heuristic — a word capitalised mid-sentence is more likely to be a proper noun (place name, group, institution) than generic language. Known false positives are acceptable; the badge is advisory only and dismissible. The check errs toward false negatives (not flagging vague text) rather than false positives. If no mid-sentence capitalised word is found, set `specificity_warning: true` on that priority.
   - **Citation check**: scan all text fields for `[From: ...]` patterns. Uploaded document names must be passed into `extract_priorities()` as a parameter (see architectural note below). Cross-check each citation against (a) uploaded document names and (b) a hardcoded whitelist: `["World Bank", "ACLED", "UNODC", "ICG", "UNHCR", "WFP", "OCHA", "ND-GAIN", "OECD", "training knowledge", "web research"]`. Any unmatched citation appended to `unverified_citations: []`.
5. Graceful fallback: if JSON block is malformed or missing, return an error state with message "Stage 4 output could not be parsed — please re-run this stage." Do NOT silently render incomplete data.

**Architectural note — passing document names to citation check:**
`extract_priorities()` currently receives only the raw LLM output string. To support citation cross-checking, the Stage 4 API request payload must include the list of uploaded document filenames. Flow:
- Frontend stores uploaded document names in localStorage (already available as part of session state)
- When the user runs Stage 4, the `/api/run-stage` request body includes `uploaded_doc_names: ["filename1.pdf", "filename2.docx"]`
- The Stage 4 branch of the `/api/run-stage` route passes this list to `extract_priorities(full_text, uploaded_doc_names=[])`
- Default is empty list (citation check skips the doc-name cross-check if not provided, only checks the org whitelist)

**`clean_stage4_output()` update:**
- Strip `%%%JSON_START%%% ... %%%JSON_END%%%` block from display text (same pattern as existing delimiter stripping)
- Remove old `%%%PRIORITY_START/END%%%`, `%%%RISK_EXPOSURE_START/END%%%` etc. stripping (no longer needed)

**Orphaned extraction functions — explicit fate:**
The following standalone extraction functions currently called at the Stage 4 `done` block must be updated:
- `extract_fcv_rating()` → **delete**; `fcv_rating` now read from JSON
- `extract_fcv_responsiveness_rating()` → **delete**; `fcv_responsiveness_rating` now read from JSON
- `extract_sensitivity_summary()` → **delete**; `sensitivity_summary` now read from JSON
- `extract_responsiveness_summary()` → **delete**; `responsiveness_summary` now read from JSON
- `extract_risk_exposure()` → **delete**; `risk_to_project` and `risk_from_project` now read from JSON
- `extract_gap_table()` → **retain** (gap table is out of scope for this spec; existing behaviour unchanged)

The SSE `done` payload currently sends `fcv_rating`, `sensitivity_summary`, `responsiveness_summary`, `risk_exposure` as separate keys. Under the new system, these are embedded in the JSON block. The `done` payload should send the full parsed JSON object (or the raw priorities array + top-level fields) so the frontend can access them. Update the `done` event construction in the Stage 4 streaming block accordingly.

### 3.5 Frontend Changes (`index.html`)

**`showPriority()` update:**
- Read from parsed JSON object instead of delimiter-extracted object
- Field names: `the_gap`, `why_it_matters`, `recommendation`, `who_acts`, `when`, `resources` (same display layout, updated field names)
- Render `specificity_warning` badge if present (see Section 5b)
- Render `unverified_citations` warning if non-empty (see Section 5c)

**`downloadReport()` update:**
- The report download function currently reads `pr.suggested_directions`. Update to `pr.recommendation` to match the renamed field. This function must be updated in the same pass as `showPriority()` to avoid a broken `.doc` export.

**`priority_body` construction for Explorer:**
- `loadExplorerForPriority()` currently builds `priority_body` by concatenating several priority fields and sends it as `priority_body` in the `/api/run-explorer` request. Update this concatenation to use the new field names: `the_gap`, `why_it_matters`, `recommendation` (replacing `suggested_directions`). Omit any fields that no longer exist in the schema. This ensures the Explorer prompt receives complete, accurate priority content.

---

## 4. Prompt Redesign

### 4.1 Stage 4 — Single Recommendation per Priority

**Change to `RECOMMENDATION` field instruction:**

> "Write ONE cohesive recommended action for this priority. It may contain multiple components (e.g., 'Revise the beneficiary targeting criteria to explicitly include IDP households in Bentiu and Malakal, update the consultation plan to ensure female-headed households are reached, and add a disaggregated monitoring indicator tracking service uptake by displacement status') but it must read as a single direction — not a menu of choices. No bullet points within this field. No 'Option A / Option B' structure. If multiple actions are truly needed, pick the highest-leverage one and note what it depends on."

**Validation instruction added to prompt:**

> "Before finalising each priority, check: does `the_gap` field name at least one specific location, group, or institution drawn from the uploaded documents or web research? If not, revise it. If no specific geography is available in your sources, name the administrative level at which the project operates (e.g., county, district, commune) and note that sub-national detail is missing."

**S/R pillar justification instruction:**

> "In the `why_it_matters` field, include a one-sentence S/R justification: e.g., 'Tagged [R] because this directly addresses Pillar 2 (remaining engaged during crisis) of the WBG FCV Strategy 2020–2025.' This must be present for any priority tagged [R] or [S+R]."

**Citation guard instruction (reinforced):**

> "In all text fields, ONLY cite documents that appeared as `[From: doc name]` in the Stage 1 output, or well-known organisations (World Bank, ACLED, UNODC, ICG, UNHCR, WFP, OCHA, ND-GAIN, OECD). NEVER fabricate document titles, report dates, or RRA names. If no specific source supports a claim, write it without a citation or attribute it to `[From: training knowledge]`."

**JSON schema instruction:**

After the narrative memo, the prompt instructs:

> "After completing the full narrative output above, append a machine-readable JSON block in EXACTLY this format, between %%%JSON_START%%% and %%%JSON_END%%% markers. Do not modify the field names. Do not skip any field. If a field has no content, write 'Not identified' rather than leaving it blank."

Followed by the schema template from Section 3.3.

### 4.2 Stage 2 — Evidence-Grounded Ratings

Add to each of the 6 OST recommendation assessments:

> "For each recommendation, cite the specific design element, document passage, or project feature that justifies your rating. Do not give a generic assessment. Example: 'Rated Partial because the PAD includes a stakeholder engagement plan (Section 4.2) but it does not differentiate consultation approaches by conflict-affected versus stable areas.'"

### 4.3 Stage 3 — Cross-Reference with Stage 2

Add instruction:

> "Only propose mitigations for recommendations rated Partial, Weak, or Not Addressed in Stage 2. Do not re-surface recommendations rated Strong or Well Embedded — these do not need mitigation. Reference the Stage 2 rating explicitly when introducing each mitigation: e.g., 'Stage 2 rated stakeholder engagement as Partial because...'"

**Note:** This instruction depends on Stage 2's existing rating vocabulary (`Strong / Partial / Weak / Not Addressed`) remaining unchanged. Do not alter Stage 2's rating scale as part of this spec.

---

## 5. UX Improvements

### 5a. S/R Tag Tooltips

Tag badges on priority cards become hoverable tooltips:

- **[S]** → *"FCV Sensitivity: this recommendation helps the project operate without causing harm or worsening fragility dynamics."*
- **[R]** → *"FCV Responsiveness: this recommendation actively addresses a root driver of fragility, aligned to one of the four WBG FCV Strategy pillars (preventing conflict, engaging in crisis, transitioning out of fragility, or mitigating spillovers)."*
- **[S+R]** → *"Both Sensitivity and Responsiveness: applies only in four specific overlap zones — inclusion/targeting of conflict-affected populations, embedding FCV logic in the ToC/PDO, adaptive M&E that monitors harm AND builds resilience, or GRM designed to strengthen state-citizen accountability."*

Same tooltips added to the dual gauge ratings at the top of the Stage 4 output.

Implementation: CSS `title` attribute or a lightweight custom tooltip (no JS library needed).

### 5b. Geographic Specificity Warning Badge

If `specificity_warning: true` on a priority:
- Show amber badge on priority card: *"May lack geographic specificity — review before sharing."*
- Badge is dismissible per card (dismissed state stored in localStorage by priority index + session)
- Does NOT block display of the priority card — advisory only

### 5c. Unverified Citation Warning

If `unverified_citations` array is non-empty on a priority:
- Show amber badge: *"Contains unverified citation(s) — confirm source exists before sharing."*
- Hovering the badge shows the citation strings in question
- Dismissible per card

### 5d. Document Upload Feedback

After successful upload:
- Show: filename + approximate word/page count + document type detected (PCN / PAD / etc.)
- On pypdf extraction failure (encrypted or scanned PDF): show clear message: *"Could not extract text from this file — it may be scanned or password-protected. Try uploading a DOCX version if available."* Currently this error is silently passed to the LLM as analysis content.

Implementation: `/api/upload` route returns `{filename, word_count, doc_type, extraction_status}` in its response JSON. Frontend renders this below the upload input.

### 5e. Explorer UX

Three changes:

1. **Cancel button**: Add a module-level `let explorerAbortController = null`. When `loadExplorerForPriority()` is called, instantiate a new `AbortController`, assign it to `explorerAbortController`, and pass `signal: explorerAbortController.signal` to the `fetch()` call. The cancel button calls `explorerAbortController.abort()`. On abort, the reader loop catches the `AbortError`, renders "Generation cancelled.", and re-enables the priority button. If a new Explorer request starts while one is in progress, abort the previous controller first.

2. **Elapsed timer**: A `setInterval` starts when the SSE stream begins, incrementing a counter each second. Displays *"Generating… 14s"* in the Explorer loading area. Cleared on stream completion, error, or cancel.

3. **localStorage caching**: Explorer results are cached using index-based keys: `explorer_priority_0`, `explorer_priority_1`, etc. The existing in-memory `explorerCache` object should also be re-keyed to use priority index (integer) instead of title string, to keep them consistent. Cache invalidation on Stage 4 re-run: iterate `localStorage` keys matching `explorer_priority_*` and remove them, and clear `explorerCache`. On re-click of a priority, check `explorerCache[index]` first (in-memory), then `localStorage.getItem('explorer_priority_' + index)` — render immediately if found.

### 5f. Stage Consistency Warning

After any Stage 2 re-run:
- Store `stage2_timestamp` in localStorage on Stage 2 completion (unix ms via `Date.now()`)
- Store `stage3_timestamp` and `stage4_timestamp` in localStorage on their respective completions
- Consistency check runs in two places: (a) inside `renderOut()` when rendering Stage 3 or Stage 4 output, and (b) inside `goBack()` when navigating back to a completed Stage 3 or Stage 4
- If `stage2_timestamp > stage3_timestamp` (or `stage4_timestamp`), inject a dismissible yellow banner at the top of that stage's output area: *"Stage 2 was updated after this output was generated — consider re-running Stages 3 and 4 for consistency."*
- Dismissal stored in localStorage per stage (e.g., `stage3_consistency_dismissed: true`) and cleared whenever Stage 3 is re-run

---

## 6. Files Changed

| File | Changes |
|---|---|
| `app.py` | Rewrite `extract_priorities()` for JSON parsing + validation; update `clean_stage4_output()`; add citation cross-check logic; update `/api/upload` to return doc metadata |
| `index.html` | Update `showPriority()` for new field names; update `downloadReport()` for renamed field; update `priority_body` construction in `loadExplorerForPriority()`; add tooltip markup; add warning badge rendering; add upload feedback display; add Explorer cancel/timer/cache; add stage consistency banner |
| `DEFAULT_PROMPTS["4"]` in `app.py` | Add JSON schema instruction; rename `SUGGESTED_DIRECTIONS` → `recommendation`; add geographic validation instruction; add S/R pillar justification instruction; reinforce citation guard |
| `DEFAULT_PROMPTS["2"]` in `app.py` | Add evidence-grounded rating instruction |
| `DEFAULT_PROMPTS["3"]` in `app.py` | Add Stage 2 cross-reference instruction |

No new files required. No changes to `background_docs.py`, `prompts.json`, `requirements.txt`, or `Procfile`.

**`CLAUDE.md` must also be updated** as part of this spec (per the project's maintenance instruction). Sections requiring update:
- Section 1.3 "Stage Pipeline Summary" table: Stage 4 row — update "Non-obvious behaviour" to reference JSON output instead of delimiters
- Section 3.2 "Stage 4 Delimiters": replace with new JSON block description
- Section 1.2 "Core Files": no structural change needed

---

## 7. Out of Scope (Not in This Spec)

- Persistent research cache (Redis/SQLite) — infrastructure change, separate initiative
- Authentication on `/api/run-stage` — separate security initiative
- Sector-specific prompt variants — future iteration after core quality is stable
- Implementation sequencing between priorities — future iteration

---

## 8. Testing Checklist

1. Upload a test PAD with no RRA → run all 4 stages → confirm Stage 4 JSON block is present and all fields populated
2. Confirm a priority with no place names shows specificity warning badge
3. Fabricate a `[From: Kenya RRA 2023]` in a Stage 4 response (via prompt override) → confirm unverified citation badge appears
4. Confirm tooltip appears on [S], [R], [S+R] badges on hover
5. Re-run Stage 2 after Stage 3 exists → confirm consistency banner appears above Stage 3
6. Upload an encrypted PDF → confirm graceful error message (not silent LLM analysis of error text)
7. Open Explorer on a priority, then click Cancel → confirm stream stops and button re-enables
8. Open the same Explorer priority twice → confirm second open is instant (cached)
9. Test graceful fallback for malformed JSON: write a Python unit test that calls `extract_priorities()` directly with a fixture string containing `%%%JSON_START%%%{ invalid json }%%%JSON_END%%%` → confirm the function returns the error state dict (not an exception). Manual test via prompt override is unreliable for this case.
10. Confirm `downloadReport()` export includes recommendation content (not empty field) after field rename
11. Confirm Explorer `priority_body` payload contains all three fields (`the_gap`, `why_it_matters`, `recommendation`) when logged in browser network tab
