# Stage 2 FCV Assessment — Restructured Analytical Framework

**Date:** 2026-03-26
**Branch:** feat/3-stage-redesign
**Scope:** Stage 2 prompt architecture, output structure, Under the Hood panels, downstream Stage 3 alignment
**Mockup:** `docs/mockup_stage2_final.html`

---

## Problem Statement

Stage 2's current output structure has four conceptual problems:

1. **Misframed Refresh Shifts.** The 4 FCV Refresh strategic shifts (Anticipate, Differentiate, Jobs & PS, Enhanced Toolkit) are presented only under "FCV Responsiveness Assessment," implying they are responsiveness-only. They are cross-cutting strategic directions that apply to both sensitivity and responsiveness.

2. **Unclear S/R boundary.** The current `FCV_GUIDE` definition of sensitivity includes "Maximizes Positive Impact — Actively seeks to address FCV sources and strengthen resilience," which overlaps with responsiveness. The definitions need sharpening.

3. **Fixed S/R tagging per recommendation.** The practitioner feedback questioned why each of the 12 OST recommendations has a pre-assigned [S] or [R] tag. Many recs can be either depending on how the project implements them.

4. **Rigid output structure.** The current Sensitivity → DNH → Responsiveness → Gaps flow forces findings into S/R buckets that may not reflect the project's actual FCV landscape.

---

## Design Decisions (Agreed)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Keep S/R distinction? | Yes — as rating outputs and finding-level tags | TTLs and FCV CCs need the S/R lens; it feeds Stage 3 priority cards |
| S/R definitions | Sharpened (see below) | Remove overlap; make operationally distinct |
| Output organisation | Thematic narrative (Option 1) | More natural reading; avoids forcing findings into S/R buckets |
| Themes fixed or dynamic? | Dynamic — derived by LLM from 12 recs + 25 questions | Each project surfaces different salient themes |
| S/R tagging per rec | Dynamic — LLM assigns [S], [R], or [S+R] per project | Same rec can be S in one project, R in another |
| Refresh shifts placement | Inline badges on findings (cross-cutting) | Not boxed under responsiveness; shifts are metadata |
| Do No Harm placement | Before synthesis, after all themes | Capstone check after thematic analysis; feeds into synthesis |
| Under the Hood panel titles | Plain-language questions | Most users won't know "OST Manual" or "12 recommendations" |
| Panel 1 (12-rec table) | Add S/R Tag column | Full traceability for FCV CCs |

---

## Revised S/R Definitions

These definitions replace the current `FCV_GUIDE` definitions and will appear as a compact box at the top of every Stage 2 output.

**FCV Sensitivity** — Is the project *aware of and designed for* the FCV context?
- Contextual awareness of FCV drivers and dynamics
- Conflict-informed design and targeting
- Do No Harm — ensuring the project does not exacerbate fragility
- FCV-adapted operations and safeguards

**FCV Responsiveness** — Does the project *actively work to change* the FCV situation?
- Addressing root causes of fragility and conflict
- Strengthening resilience and building pathways out of FCV
- Leveraging FCV tools and flexibilities for transformative impact
- Connecting project outcomes to stability and peace dividends

**[S+R]** — Genuinely dual: the same measure serves both awareness/protection AND active FCV engagement. Only applied when justified — not a default. The four canonical overlap zones remain:
1. Inclusion/targeting of conflict-affected populations (S: avoids exclusion harm; R: actively rebuilds inclusion)
2. FCV logic embedded in ToC/PDO (S: acknowledges dynamics; R: designs for change)
3. Adaptive M&E that monitors harm AND adapts for resilience
4. GRM designed to strengthen state-citizen accountability (S: receives complaints; R: builds trust)

---

## Stage 2 Output Structure

### TTL-Facing Output

```
┌─────────────────────────────────────────────────────┐
│ S/R Definition Box (compact, always present)        │
│ ┌──────────────────┐  ┌──────────────────┐          │
│ │ S: Sensitivity   │  │ R: Responsiveness│          │
│ │ Aware & designed │  │ Actively changes │          │
│ └──────────────────┘  └──────────────────┘          │
├─────────────────────────────────────────────────────┤
│                                                     │
│ FCV Assessment: [Project Name]                      │
│                                                     │
│ ── Theme 1: [Dynamic title] ──────────────────────  │
│   Finding [S] (Shift badge)                         │
│   Finding [R] (Shift badge)                         │
│                                                     │
│ ── Theme 2: [Dynamic title] ──────────────────────  │
│   Finding [S+R] (Shift badge)                       │
│   Finding [S] (Shift badge)                         │
│                                                     │
│ ── Theme 3: [Dynamic title] ──────────────────────  │
│   ...                                               │
│                                                     │
│ ── Theme N (3–5 themes total) ────────────────────  │
│   ...                                               │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Do No Harm: X addressed | Y partial | Z gap    │ │
│ │ [Brief narrative on most critical DNH issues]   │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ Synthesis                                           │
│ ┌─ FCV Sensitivity: [80–100 word paragraph] ──────┐ │
│ └─────────────────────────────────────────────────┘ │
│ ┌─ FCV Responsiveness: [80–100 word paragraph] ───┐ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ┌── Sensitivity ──┐  ┌── Responsiveness ──┐         │
│ │    Adequate     │  │      Low           │         │
│ └─────────────────┘  └────────────────────┘         │
│                                                     │
│ Key Gaps (3–5, tagged [S]/[R]/[S+R])                │
│ ▌ Gap 1 [S]                                         │
│ ▌ Gap 2 [R]                                         │
│ ▌ Gap 3 [S+R]                                       │
│ ...                                                 │
├─────────────────────────────────────────────────────┤
│ Under the Hood — Detailed Assessment                │
│ ▸ How well does the project integrate FCV?          │
│ ▸ Could this project unintentionally cause harm?    │
│ ▸ What did we look for — and what was missing?      │
│ ▸ Where did this analysis come from?                │
└─────────────────────────────────────────────────────┘
```

### Theme Generation Rules (for prompt)

The LLM must:
- Generate 3–5 analytical themes based on what the 12 OST recs and 25 key questions surface for this project
- Each theme gets a short descriptive title (e.g., "Contextual Awareness & Risk Analysis," "Economic Resilience & Root-Cause Engagement")
- Themes should not be named "Sensitivity" or "Responsiveness" — they are analytical groupings, not S/R buckets
- Each finding within a theme carries exactly one tag: [S], [R], or [S+R]
- Each finding carries zero or one shift badge (Anticipate / Differentiate / Jobs & PS / Enhanced Toolkit)
- A theme can contain a mix of [S] and [R] findings — this is expected and correct

### Do No Harm Section

Position: After all themes, before Synthesis.

Content:
- Traffic-light bar: "X of 8 addressed | Y partial | Z gap" (same 8 canonical principles)
- Brief narrative (2–4 sentences) highlighting the most critical DNH issues
- DNH is NOT a theme — it's a standalone capstone section

### Synthesis Section

Two paragraphs:
- **FCV Sensitivity paragraph** (80–100 words): Summarises sensitivity findings across all themes
- **FCV Responsiveness paragraph** (80–100 words): Summarises responsiveness findings across all themes

### Ratings

Same scale as current: Extremely Low | Very Low | Low | Adequate | Well Embedded | Very Well Embedded

Ratings must be grounded in the synthesis — the reader should be able to trace the rating back to the evidence.

### Key Gaps

3–5 most critical gaps, prioritised by severity:
- Each tagged [S], [R], or [S+R]
- Red border = high severity; amber border = medium severity
- Brief description with specific evidence (not generic)

---

## Under the Hood Panels

### Panel Renaming

| Current Title | New Title | Subtitle |
|---------------|-----------|----------|
| Full 12-Recommendation Assessment | How well does the project integrate FCV considerations? | 12 operational standards assessed with status and evidence |
| Do No Harm Checklist (8 Principles) | Could this project unintentionally cause harm? | 8 conflict-sensitivity principles checked against the design |
| 25 Key Questions Assessment | What did we look for — and what was missing? | Diagnostic questions used to probe the project |
| Evidence Trail | Where did this analysis come from? | Sources, types, and what each contributed |

### Panel 1 Schema Change

Add S/R Tag column to the 12-rec table. New columns:

| Column | Description |
|--------|-------------|
| Operational Standard | Rec description (renamed from "Recommendation" for accessibility) |
| Status | Strongly addressed / Partially addressed / Weakly addressed / Not addressed |
| Evidence | What the project does |
| Gaps | What's missing |
| S/R Tag | [S], [R], or [S+R] — dynamically assigned |
| Shift(s) | Anticipate / Differentiate / Jobs & PS / Enhanced Toolkit |

### Panels 2–4

No structural changes beyond the title rename. Content format stays the same.

---

## Delimiter Structure

The Stage 2 LLM output must include these delimiter blocks (parsed by backend, stripped from display):

```
[TTL-facing narrative — themes, DNH, synthesis, gaps]

%%%STAGE2_RATINGS_START%%%
{"sensitivity_rating": "Adequate", "responsiveness_rating": "Low"}
%%%STAGE2_RATINGS_END%%%

%%%UNDER_HOOD_START%%%

%%%RECS_TABLE_START%%%
[12-rec table in markdown — now with S/R Tag column]
%%%RECS_TABLE_END%%%

%%%DNH_CHECKLIST_START%%%
[8-principle table — unchanged format]
%%%DNH_CHECKLIST_END%%%

%%%QUESTIONS_MAP_START%%%
[25 key questions table — unchanged format]
%%%QUESTIONS_MAP_END%%%

%%%EVIDENCE_TRAIL_START%%%
[Sources table — unchanged format]
%%%EVIDENCE_TRAIL_END%%%

%%%UNDER_HOOD_END%%%
```

No changes to delimiter names or parsing logic — only the content within `RECS_TABLE` gains the S/R Tag column.

---

## Downstream Impact

### Stage 3 Prompt

- Update S/R definitions to match the revised definitions above
- No structural change to Stage 3 output — it already carries `tag` and `refresh_shift` per priority
- The `tag` on each priority is already dynamic — no change needed
- Ensure the Stage 3 prompt references the new S/R definitions so tagging is consistent

### FCV_GUIDE in background_docs.py

- Revise the sensitivity definition: remove "Maximizes Positive Impact" (point 4) — this is responsiveness
- Replace with the sharpened definitions above
- Keep the 4 Refresh shifts section as cross-cutting (already framed this way in the constant)

### Go Deeper Tab 2 ("Why this recommendation")

- Currently filters `stage2_under_hood` by `priority.fcv_dimension`
- With dynamic themes, this filtering logic needs review — themes are not fixed dimensions
- Recommended approach: filter by matching keywords from the priority's `title` and `fcv_dimension` against the recs table and questions map content
- This is a minor frontend logic change, not an architectural one

### Frontend Changes

1. **Stage 2 output rendering** — Update `renderOut()` for Stage 2 to:
   - Inject a hardcoded S/R definition box at the top of the output (NOT generated by the LLM — this is a fixed frontend element to ensure consistency across all runs)
   - Render the narrative as-is (themes are in the markdown output from the LLM)
   - Render the DNH section (already parsed from narrative)
   - Render synthesis, ratings, gaps (no change to these)

2. **Under the Hood panel titles** — Update the `<summary>` text in the 4 `<details>` elements

3. **Under the Hood Panel 1** — Update the recs table rendering to include S/R Tag column

4. **Sidebar** — No changes needed (ratings still come from `STAGE2_RATINGS` delimiter)

---

## Files to Modify

| File | Change |
|------|--------|
| `app.py` — `DEFAULT_PROMPTS["2"]` | Major rewrite: new output structure, dynamic themes, DNH repositioned, S/R definitions, tagging instructions |
| `app.py` — `DEFAULT_PROMPTS["3"]` | Update S/R definitions to match |
| `background_docs.py` — `FCV_GUIDE` | Revise sensitivity definition (remove point 4 overlap) |
| `index.html` — Stage 2 rendering | S/R definition box, Under the Hood panel titles, Panel 1 S/R column |
| `index.html` — Go Deeper Tab 2 | Update filtering logic for dynamic themes |

---

## What Does NOT Change

- Stage 1 (Context & Extraction) — no changes
- Stage 3 JSON schema — `tag`, `refresh_shift`, and all other priority fields remain
- Stage 3 output structure — narrative + JSON block, same delimiter format
- SSE streaming — same approach
- Session management / localStorage — same approach
- Go Deeper Tabs 1 and 3 — same LLM calls, same prompts
- Follow-on card — no changes
- Rating scale — same 6 levels
- 8 DNH principles — same list
- 12 OST recs + 25 key questions — same content, different presentation

---

## Success Criteria

1. Stage 2 output reads as a natural thematic narrative, not a forced S-then-R structure
2. Every finding carries a dynamic [S]/[R]/[S+R] tag that reflects how THIS project engages with the rec/question
3. Refresh shifts appear as inline badges across both S and R findings — not boxed under responsiveness
4. DNH appears before synthesis as a capstone check
5. Under the Hood panels are accessible to non-specialists via plain-language titles
6. S/R ratings are traceable from synthesis → themes → findings → Under the Hood evidence
7. Stage 3 priority cards remain consistent with Stage 2 tagging
