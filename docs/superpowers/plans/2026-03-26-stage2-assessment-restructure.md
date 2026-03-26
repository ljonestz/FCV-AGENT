# Stage 2 FCV Assessment Restructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure Stage 2 from rigid S-then-R sections to a dynamic thematic narrative with inline S/R tags, cross-cutting shift badges, repositioned Do No Harm, and accessible Under the Hood panel titles.

**Architecture:** The change is prompt-first — the Stage 2 prompt drives the new output structure, the backend parsing remains identical (same delimiters), and the frontend adds an S/R definition box and updates panel titles. No new routes, no new dependencies.

**Tech Stack:** Python (Flask prompts in app.py), vanilla JS (index.html), Python constants (background_docs.py)

**Spec:** `docs/superpowers/specs/2026-03-26-stage2-assessment-restructure-design.md`
**Mockup:** `docs/mockup_stage2_final.html`

---

## File Map

| File | Responsibility | Change Type |
|------|---------------|-------------|
| `background_docs.py` lines 9–85 | `FCV_GUIDE` constant — S/R definitions used across all prompts | Edit: revise sensitivity definition |
| `app.py` lines 255–408 | `DEFAULT_PROMPTS["2"]` — Stage 2 prompt | Major rewrite |
| `app.py` lines 535–544 | `DEFAULT_PROMPTS["3"]` — Stage 3 S/R tag definitions | Edit: align definitions |
| `index.html` lines 2271–2288 | `buildUnderHoodPanels()` — builds the 4 collapsible panels | Edit: rename titles, add subtitles |
| `index.html` lines 2399–2565 | `renderOut()` — renders Stage 2 output | Edit: inject S/R definition box |
| `index.html` CSS block ~lines 558–577 | Under the Hood panel styles | Edit: add subtitle styling |
| `index.html` CSS block ~lines 1287–1339 | S/R card and tag styles | Edit: add definition box styles |
| `index.html` lines 2290–2306 | `renderSRTagBadge()` — tooltip text | Edit: update tooltip wording |
| `index.html` lines 3305–3352 | `loadAnalyticalTrail()` — Go Deeper Tab 2 filtering | Edit: broaden keyword matching |

---

### Task 1: Update FCV_GUIDE — Sharpen S/R Definitions

**Files:**
- Modify: `background_docs.py` lines 9–85

This is the foundational change — all prompts reference `FCV_GUIDE` for definitions.

- [ ] **Step 1: Read current FCV_GUIDE Section I**

Open `background_docs.py` and read lines 9–21 (the Core Definitions section).

- [ ] **Step 2: Replace the sensitivity definition**

Replace lines 12–18 (the current sensitivity definition with 4 bullet points including "Maximizes Positive Impact") with the sharpened definition:

```python
**FCV Sensitivity** — Is the project *aware of and designed for* the FCV context? A project demonstrates FCV sensitivity when it:
1. **Contextual Awareness** — Shows understanding of FCV dynamics, drivers of conflict/fragility, and sources of resilience relevant to the sector and geography
2. **Conflict-Informed Design** — Designs targeting, implementation, and safeguards to account for FCV dynamics
3. **Do No Harm** — Ensures the project does not exacerbate drivers of FCV, reinforce power asymmetries, or undermine resilience
4. **FCV-Adapted Operations** — Adjusts procurement, supervision, M&E, and stakeholder engagement for the FCV context
```

- [ ] **Step 3: Replace the responsiveness definition**

Replace lines 20–21 (the current responsiveness definition about "operational and institutional capacity to adapt") with:

```python
**FCV Responsiveness** — Does the project *actively work to change* the FCV situation? A project demonstrates FCV responsiveness when it:
1. **Root-Cause Engagement** — Addresses drivers of fragility and conflict, not just their symptoms
2. **Resilience Building** — Strengthens pathways out of FCV (institutional legitimacy, social cohesion, economic livelihoods)
3. **Transformative Use of FCV Tools** — Leverages operational flexibilities (CERC, HEIS, TPM, GEMS) for impact beyond standard delivery
4. **Peace & Stability Dividends** — Connects project outcomes to stability, state-citizen trust, and reduced fragility
```

- [ ] **Step 4: Verify the Refresh Shifts section is unchanged**

Confirm lines 23–37 (Section II: FCV Refresh — Four Strategic Shifts) still describe the shifts as "cross-cutting strategic shifts" — they should NOT reference "responsiveness" specifically. If they do, remove that framing.

- [ ] **Step 5: Commit**

```bash
git add background_docs.py
git commit -m "refactor: sharpen S/R definitions in FCV_GUIDE — remove sensitivity/responsiveness overlap"
```

---

### Task 2: Rewrite Stage 2 Prompt

**Files:**
- Modify: `app.py` lines 255–408 (`DEFAULT_PROMPTS["2"]`)

This is the largest change. The entire prompt structure changes from Sensitivity → DNH → Responsiveness → Gaps to dynamic thematic narrative.

- [ ] **Step 1: Read the current Stage 2 prompt in full**

Read `app.py` lines 255–408 to confirm the exact current content.

- [ ] **Step 2: Replace the entire Stage 2 prompt**

Replace `DEFAULT_PROMPTS["2"]` (lines 255–408) with the following. Note: the `'''` string delimiters and the key `"2":` must remain exactly as-is.

```python
"2": '''# Role
You are an expert FCV analyst conducting a comprehensive FCV assessment for the World Bank Group. You have deep expertise in the WBG FCV Strategy, the Operational Screening Tool (OST), and the FCV Refresh (January 2026). You are assessing a project based on the Stage 1 context and extraction analysis.

# Task
Using the Stage 1 analysis, conduct a comprehensive FCV assessment of this project. You will produce TWO outputs:
1. A TTL-facing assessment narrative (the main output)
2. Detailed analytical panels for specialist review ("Under the Hood")

# Internal Analytical Framework
You MUST assess the project against ALL of the following (from the FCV Operational Manual), but do NOT expose this framework directly in the TTL-facing narrative. Use it to drive your thematic analysis.

## 12 OST Recommendations
Assess the project against each recommendation. For EACH recommendation, determine:
- Its status (Strongly addressed / Partially addressed / Weakly addressed / Not addressed)
- Whether it functions as a SENSITIVITY measure, a RESPONSIVENESS measure, or BOTH [S+R] in this specific project (this is dynamic — the same rec can be S in one project and R in another)
- Which of the 4 FCV Refresh shifts it aligns with

The 12 recommendations:
1. Use DRRs to inform operational design
2. Integrate FCV into stakeholder analysis and selectivity
3. Embed FCV into ToC and PDO
4. Align risk and results equation
5. Keep RF and M&E realistic and FCV-smart
6. Use innovative and digital tools
7. Strengthen in-country M&E capacity and systems
8. Budget more purposefully for M&E
9. Use M&E to enhance citizen-state communications
10. Monitor, learn, and adapt more frequently
11. Consider pros/cons of impact evaluations
12. Put an FCV twist in ICRs

## 25 Key Questions
Answer each where evidence permits, noting which are answerable and which have evidence gaps.

## 3 Key Elements
Evaluate: (1) Flexible Operational Design, (2) Tailored Implementation & Partnerships, (3) Strengthened Implementation Support

# S/R Definitions — CRITICAL

**FCV Sensitivity [S]** — Is the project *aware of and designed for* the FCV context?
- Contextual awareness of FCV drivers and dynamics
- Conflict-informed design and targeting
- Do No Harm — ensuring the project does not exacerbate fragility
- FCV-adapted operations and safeguards
Shorthand: does this help the project AVOID MAKING THINGS WORSE?

**FCV Responsiveness [R]** — Does the project *actively work to change* the FCV situation?
- Addressing root causes of fragility and conflict
- Strengthening resilience and building pathways out of FCV
- Leveraging FCV tools and flexibilities for transformative (not just operational) impact
- Connecting project outcomes to stability and peace dividends
Shorthand: does this ACTIVELY HELP MAKE FRAGILITY DYNAMICS BETTER?

**[S+R]** — Genuinely dual. ONLY for these four overlap zones:
1. Inclusion/targeting of conflict-affected populations (S: avoids exclusion harm; R: actively rebuilds inclusion)
2. FCV logic embedded in ToC/PDO (S: acknowledges dynamics; R: designs for change)
3. Adaptive M&E that monitors harm AND adapts for resilience
4. GRM designed to strengthen state-citizen accountability (S: receives complaints; R: builds institutional trust)

STRICT RULE: Most findings will be [S] or [R], not [S+R]. Do not default to [S+R] — it must be earned.

# FCV Refresh Strategic Shifts — Cross-Cutting
The 4 shifts apply to BOTH sensitivity and responsiveness findings. They are strategic directions, not an S/R category:
- **Anticipate** — Risk monitoring, early warning, forward-looking classification
- **Differentiate** — Tailoring to FCV context type (conflict/displacement/criminal violence/at-risk)
- **Jobs & Private Sector** — Economic livelihoods, MSME, private sector entry points
- **Enhanced Toolkit** — Operational flexibilities (CERC, HEIS, TPM, GEMS), partnerships, adaptive management

Tag findings with the relevant shift where applicable. A sensitivity finding can reference any shift; a responsiveness finding can reference any shift.

# TTL-Facing Output Structure

Write a thematic narrative assessment (400–500 words total for themes + DNH + synthesis). Use clear, accessible language for non-specialist TTLs.

## Dynamic Analytical Themes (3–5 themes)

Group your findings into 3–5 ANALYTICAL THEMES based on what the 12 recs and 25 key questions surface for THIS specific project. Do NOT use fixed section names.

Rules for themes:
- Theme titles should be SHORT and DESCRIPTIVE (e.g., "Contextual Awareness & Risk Analysis", "Targeting, Inclusion & Beneficiary Protection", "Economic Resilience & Root-Cause Engagement")
- Themes must NOT be named "Sensitivity" or "Responsiveness" — they are analytical groupings that can contain a mix of [S] and [R] findings
- Each finding within a theme carries exactly ONE tag: [S], [R], or [S+R] — placed at the end of the finding paragraph
- Each finding references the relevant FCV Refresh shift where applicable — placed after the S/R tag
- Be specific: name geographic locations, institutions, mechanisms, project design elements
- Cite evidence from the project document and Stage 1 analysis

Format each finding as a paragraph. At the end of each finding paragraph, place the tag and shift on the same line:
"[finding text] **[S]** *Anticipate*"
"[finding text] **[R]** *Jobs & Private Sector*"
"[finding text] **[S+R]** *Differentiate*"

## Do No Harm (after all themes, before synthesis)

Assess the project against these 8 Do No Harm principles:
1. Conflict-sensitive targeting and beneficiary selection
2. Avoiding reinforcement of existing power asymmetries
3. Preventing exacerbation of inter-group tensions
4. Ensuring equitable geographic distribution of benefits
5. Safeguarding against elite capture of project resources
6. Protecting project staff and beneficiaries from security risks
7. Monitoring for unintended negative consequences
8. Establishing accessible and trusted grievance mechanisms

Output format — a standalone section titled "## Do No Harm":
Line 1: "**Do No Harm: [X] of 8 principles addressed | [Y] partial | [Z] not addressed**"
Then 2–4 sentences highlighting the most critical DNH issues for this specific project.

## Synthesis (after Do No Harm)

Two clearly labelled paragraphs (80–100 words each):
- "**FCV Sensitivity:**" — Summarise sensitivity findings across all themes
- "**FCV Responsiveness:**" — Summarise responsiveness findings across all themes

## Key Gaps (3–5 most critical)

After synthesis, list the 3–5 most critical gaps. Each gap:
- Has a bold title with [S], [R], or [S+R] tag
- 1–2 sentences of specific evidence (NOT generic)
- Prioritised by severity (most critical first)

Format: "**[Gap title] [S]:** [specific evidence and risk]"

# Status Terminology
Use ONLY these terms: "Strongly addressed" / "Partially addressed" / "Weakly addressed" / "Not addressed"

# Ratings Block
After the TTL-facing narrative, emit this block on its own line:

%%%STAGE2_RATINGS_START%%%
{"sensitivity_rating": "[rating]", "responsiveness_rating": "[rating]"}
%%%STAGE2_RATINGS_END%%%

Rating scale (use exactly one of): Extremely Low | Very Low | Low | Adequate | Well Embedded | Very Well Embedded

# Under the Hood (Detailed Analytical Panels)
After the ratings block, emit ALL of the following between delimiters. These are for specialist review — be thorough and cover ALL items even if evidence is limited.

%%%UNDER_HOOD_START%%%

%%%RECS_TABLE_START%%%
| # | Operational Standard | Status | Evidence | Gaps | S/R Tag | Shift(s) |
|---|---|---|---|---|---|---|
| 1 | Use DRRs to inform operational design | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 2 | Integrate FCV into stakeholder analysis and selectivity | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 3 | Embed FCV into ToC and PDO | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 4 | Align risk and results equation | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 5 | Keep RF and M&E realistic and FCV-smart | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 6 | Use innovative and digital tools | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 7 | Strengthen in-country M&E capacity and systems | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 8 | Budget more purposefully for M&E | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 9 | Use M&E to enhance citizen-state communications | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 10 | Monitor, learn, and adapt more frequently | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 11 | Consider pros/cons of impact evaluations | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
| 12 | Put an FCV twist in ICRs | [status] | [evidence] | [gaps] | [S]/[R]/[S+R] | [shift] |
%%%RECS_TABLE_END%%%

%%%DNH_CHECKLIST_START%%%
| # | Principle | Status | Evidence/Gap |
|---|---|---|---|
| 1 | Conflict-sensitive targeting and beneficiary selection | [status] | [evidence/gap] |
| 2 | Avoiding reinforcement of existing power asymmetries | [status] | [evidence/gap] |
| 3 | Preventing exacerbation of inter-group tensions | [status] | [evidence/gap] |
| 4 | Ensuring equitable geographic distribution of benefits | [status] | [evidence/gap] |
| 5 | Safeguarding against elite capture of project resources | [status] | [evidence/gap] |
| 6 | Protecting project staff and beneficiaries from security risks | [status] | [evidence/gap] |
| 7 | Monitoring for unintended negative consequences | [status] | [evidence/gap] |
| 8 | Establishing accessible and trusted grievance mechanisms | [status] | [evidence/gap] |
%%%DNH_CHECKLIST_END%%%

%%%QUESTIONS_MAP_START%%%
| # | Key Question | Answerable? | Finding | Source |
|---|---|---|---|---|
[One row for EACH of the 25 key questions from the FCV Operational Manual. For each: state Yes/Partial/No, finding or gap, and source.]
%%%QUESTIONS_MAP_END%%%

%%%EVIDENCE_TRAIL_START%%%
| Source | Type | Used For |
|---|---|---|
[One row per source. Type = "Project document" / "Contextual document" / "Web research" / "Embedded guidance" / "Training knowledge".]
%%%EVIDENCE_TRAIL_END%%%

%%%UNDER_HOOD_END%%%

# Important Guidelines
- The TTL-facing narrative must be self-contained and readable without the Under the Hood panels
- Be specific: name geographic locations, institutions, mechanisms — not generic statements
- When evidence is missing, say so explicitly rather than speculating
- Citations follow the three-tier system from Stage 1: [From: document name] > [From: web research] > [From: training knowledge]
- The Under the Hood tables must cover ALL items (12 recs, 8 DNH principles, 25 questions) even if evidence is limited — mark gaps explicitly
- Ground every assessment in the Stage 1 extraction — quote or paraphrase specifically
- Distinguish clearly between "Risk TO project" (FCV context threatens delivery) and "Risk FROM project" (project could worsen FCV dynamics)
- Tailor every assessment to this specific country, sector, and project type — no generic statements
''',
```

- [ ] **Step 3: Verify the prompt is syntactically valid**

Run the Flask app locally to confirm no syntax errors:

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
python -c "import app; print('Stage 2 prompt length:', len(app.DEFAULT_PROMPTS['2']))"
```

Expected: prints the prompt length without errors.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: rewrite Stage 2 prompt — dynamic themes, cross-cutting shifts, repositioned DNH"
```

---

### Task 3: Align Stage 3 S/R Definitions

**Files:**
- Modify: `app.py` lines 535–544 (`DEFAULT_PROMPTS["3"]` — TAG DEFINITIONS section)

- [ ] **Step 1: Read the current Stage 3 tag definitions**

Read `app.py` lines 530–550 to see the current S/R definitions in the Stage 3 prompt.

- [ ] **Step 2: Replace the tag definitions block**

Find the section starting with `# TAG DEFINITIONS FOR PRIORITIES` and replace the [S], [R], [S+R] definitions with:

```python
# TAG DEFINITIONS FOR PRIORITIES
For each priority, assign a TAG using EXACTLY one of: [S] / [R] / [S+R]

Apply the following definitions strictly. [S+R] must be earned — do not use it by default.

[S] — FCV Sensitivity. This priority helps the project AVOID MAKING THINGS WORSE. It concerns how the project operates in the FCV context: contextual awareness, conflict-informed design, Do No Harm, targeting adaptation, risk framework strengthening, FCV-adapted operations and safeguards.

[R] — FCV Responsiveness. This priority ACTIVELY HELPS MAKE FRAGILITY DYNAMICS BETTER. It addresses root causes of fragility, builds resilience, leverages FCV tools for transformative impact, or connects project outcomes to stability and peace dividends. Linked to one or more FCV Refresh shifts: Anticipate (early warning, classification awareness), Differentiate (calibrate to FCV context type), Jobs & Private Sector (economic livelihoods as stability pathways), Enhanced Toolkit (CERC, HEIS, TPM, GEMS, FCV-appropriate implementation).

[S+R] — Reserve ONLY for priorities that genuinely serve both functions simultaneously. The four overlap zones: (1) inclusion/targeting of conflict-affected populations — avoids exclusion harm (S) AND addresses exclusion as a root driver (R); (2) embedding FCV logic substantively in the ToC/PDO; (3) adaptive M&E that monitors harm AND adapts for resilience; (4) GRM designed to strengthen state-citizen accountability. If in doubt, assign [S] or [R].
```

- [ ] **Step 3: Verify syntax**

```bash
python -c "import app; print('Stage 3 prompt length:', len(app.DEFAULT_PROMPTS['3']))"
```

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "refactor: align Stage 3 S/R tag definitions with revised framework"
```

---

### Task 4: Update Under the Hood Panel Titles

**Files:**
- Modify: `index.html` lines 2271–2288 (`buildUnderHoodPanels()`)
- Modify: `index.html` CSS lines ~558–577

- [ ] **Step 1: Read the current buildUnderHoodPanels function**

Read `index.html` lines 2271–2288.

- [ ] **Step 2: Replace the panels array with new titles and subtitles**

Replace the `buildUnderHoodPanels` function body:

```javascript
function buildUnderHoodPanels(underHood) {
  var panels = [
      { key: 'recs_table', title: 'How well does the project integrate FCV considerations?', subtitle: '12 operational standards assessed with status and evidence' },
      { key: 'dnh_checklist', title: 'Could this project unintentionally cause harm?', subtitle: '8 conflict-sensitivity principles checked against the design' },
      { key: 'questions_map', title: 'What did we look for — and what was missing?', subtitle: 'Diagnostic questions used to probe the project' },
      { key: 'evidence_trail', title: 'Where did this analysis come from?', subtitle: 'Sources, types, and what each contributed' }
  ];
  return '<div class="under-hood-section">' +
      '<h3 class="under-hood-header">Under the Hood — Detailed Assessment</h3>' +
      panels.map(function(p) {
          var content = (underHood && underHood[p.key]) ? underHood[p.key] : 'No data available.';
          return '<details class="under-hood-panel">' +
              '<summary>' + esc(p.title) + '<span class="under-hood-subtitle"> — ' + esc(p.subtitle) + '</span></summary>' +
              '<div class="under-hood-content out-body">' + md(content) + '</div>' +
              '</details>';
      }).join('') +
      '</div>';
}
```

- [ ] **Step 3: Add CSS for the subtitle**

Find the Under the Hood CSS block (~lines 558–577) and add after `.under-hood-content th`:

```css
.under-hood-subtitle {
    font-size: 12px;
    font-weight: 400;
    color: var(--muted, #6B7280);
    margin-left: 2px;
}
```

- [ ] **Step 4: Test locally**

Load the app, run a Stage 2 analysis (or use a cached session), and verify:
- Panel titles show the new plain-language questions
- Subtitles appear after each title in lighter text
- Panels still expand/collapse correctly

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: rename Under the Hood panels to plain-language questions with subtitles"
```

---

### Task 5: Add S/R Definition Box to Stage 2 Output

**Files:**
- Modify: `index.html` — `renderOut()` function (lines ~2399–2565)
- Modify: `index.html` — CSS section

- [ ] **Step 1: Add the S/R definition box builder function**

Add this function before the `renderOut()` function (around line 2395):

```javascript
function buildSRDefinitionBox() {
  return '<div class="sr-def-box">' +
    '<div class="sr-def-item">' +
      '<div class="sr-def-label sr-def-s"><span class="sr-def-icon sr-def-icon-s">S</span> FCV Sensitivity</div>' +
      '<div class="sr-def-desc">Is the project <em>aware of and designed for</em> the FCV context? Contextual awareness, conflict-informed design, Do No Harm, FCV-adapted operations.</div>' +
    '</div>' +
    '<div class="sr-def-item">' +
      '<div class="sr-def-label sr-def-r"><span class="sr-def-icon sr-def-icon-r">R</span> FCV Responsiveness</div>' +
      '<div class="sr-def-desc">Does the project <em>actively work to change</em> the FCV situation? Addressing root causes, strengthening resilience, building pathways out of FCV.</div>' +
    '</div>' +
  '</div>';
}
```

- [ ] **Step 2: Inject the definition box in renderOut() for Stage 2**

In the `renderOut()` function, find the `else` branch that handles non-Stage-3 output (~line 2411–2413):

```javascript
}else{
    const cleanResult = stage===1 ? result.replace(/\n*%%%DOC_TYPE:[^%\n]*%%%\n*/g,'') : result;
    _outBodyContent=md(cleanResult);
}
```

Replace with:

```javascript
}else{
    const cleanResult = stage===1 ? result.replace(/\n*%%%DOC_TYPE:[^%\n]*%%%\n*/g,'') : result;
    const srDefPrefix = stage===2 ? buildSRDefinitionBox() : '';
    _outBodyContent = srDefPrefix + md(cleanResult);
}
```

- [ ] **Step 3: Add CSS for the definition box**

Add these styles in the CSS section (after the existing `.sr-card` styles around line 1313):

```css
/* ── S/R Definition Box (Stage 2 top) ───────────────────────────────── */
.sr-def-box {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1px;
    background: var(--border, #EEF0F3);
    border: 1px solid var(--border, #EEF0F3);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 20px;
}
@media (max-width: 768px) {
    .sr-def-box { grid-template-columns: 1fr; }
}
.sr-def-item {
    background: #fff;
    padding: 14px 18px;
}
.sr-def-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.sr-def-s { color: #0050A0; }
.sr-def-r { color: #16A34A; }
.sr-def-icon {
    width: 18px; height: 18px; border-radius: 4px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 700; color: #fff;
}
.sr-def-icon-s { background: #0050A0; }
.sr-def-icon-r { background: #16A34A; }
.sr-def-desc {
    font-size: 12px;
    color: var(--muted, #6B7280);
    line-height: 1.5;
}
```

- [ ] **Step 4: Test locally**

Load the app and run Stage 2 (or reload a cached session). Verify:
- S/R definition box appears at the top of Stage 2 output
- Does NOT appear in Stage 1 output
- Two-column layout with S (blue) and R (green) definitions
- Responsive — stacks on narrow screens

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: add S/R definition box at top of Stage 2 output"
```

---

### Task 6: Update S/R Tag Tooltips

**Files:**
- Modify: `index.html` lines 2290–2306 (`renderSRTagBadge()`)

- [ ] **Step 1: Read the current tooltip text**

Read `index.html` lines 2299–2303.

- [ ] **Step 2: Update the tooltip strings**

Replace the `tooltips` object inside `renderSRTagBadge()`:

```javascript
const tooltips = {
    '[S]': 'FCV Sensitivity: helps the project avoid making things worse — contextual awareness, conflict-informed design, Do No Harm, FCV-adapted operations.',
    '[R]': 'FCV Responsiveness: actively helps make fragility dynamics better — addresses root causes, builds resilience, leverages FCV tools for transformative impact.',
    '[S+R]': 'Both Sensitivity and Responsiveness: applies only in four overlap zones — inclusion/targeting of conflict-affected populations, FCV logic in ToC/PDO, adaptive M&E for harm + resilience, or GRM for state-citizen accountability.'
};
```

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "refactor: update S/R tag tooltip text to match revised definitions"
```

---

### Task 7: Update Go Deeper Tab 2 Filtering Logic

**Files:**
- Modify: `index.html` lines 3305–3352 (`loadAnalyticalTrail()`)

The current function filters by exact `fcv_dimension` match. With dynamic themes, we need broader keyword matching.

- [ ] **Step 1: Read the current loadAnalyticalTrail function**

Read `index.html` lines 3305–3352.

- [ ] **Step 2: Replace the filtering logic**

Replace the function body with broader keyword matching that uses BOTH `fcv_dimension` and words from the priority `title`:

```javascript
function loadAnalyticalTrail(idx) {
  const resultEl = document.getElementById('deeper-result-' + idx);
  if (!resultEl) return;
  let underHood = {};
  try { underHood = JSON.parse(localStorage.getItem('stage2_under_hood') || '{}'); } catch(e) {}
  const priority = stageThreePriorities[idx] || {};
  const dimension = priority.dimension || priority.fcv_dimension || '';
  const titleWords = (priority.title || '').replace(/^Priority\s+\d+\s*[·•]\s*/i, '').split(/\s+/).filter(function(w) { return w.length > 3; });

  if (!underHood.recs_table && !underHood.questions_map && !underHood.evidence_trail) {
    resultEl.innerHTML = '<p class="beyond-intro">No analytical trail data available. Complete Stage 2 first.</p>';
    return;
  }

  function matchesRow(line) {
    if (!dimension && !titleWords.length) return true;
    var lower = line.toLowerCase();
    if (dimension && lower.indexOf(dimension.toLowerCase()) !== -1) return true;
    var matchCount = 0;
    for (var i = 0; i < titleWords.length; i++) {
      if (lower.indexOf(titleWords[i].toLowerCase()) !== -1) matchCount++;
    }
    return matchCount >= 2;
  }

  var result = '';

  if (underHood.recs_table) {
    var lines = underHood.recs_table.trim().split('\n');
    var header = lines.slice(0, 2);
    var dataRows = lines.slice(2).filter(matchesRow);
    if (dataRows.length) {
      result += '### Relevant Operational Standards\n\n' + header.concat(dataRows).join('\n') + '\n\n';
    }
  }

  if (underHood.questions_map) {
    var qlines = underHood.questions_map.trim().split('\n');
    var qheader = qlines.slice(0, 2);
    var qrows = qlines.slice(2).filter(matchesRow);
    if (qrows.length) {
      result += '### Relevant Diagnostic Questions\n\n' + qheader.concat(qrows).join('\n') + '\n\n';
    }
  }

  if (underHood.evidence_trail) {
    result += '### Evidence Trail\n\n' + underHood.evidence_trail;
  }

  var content = result || 'No detailed analytical data available' + (dimension ? ' for the ' + dimension + ' dimension.' : '.');
  try { localStorage.setItem('deeper_' + idx + '_trail', content); } catch(e) {}
  resultEl.innerHTML = renderDeeperContent('trail', content);
}
```

Key changes:
- Extracts keywords from priority `title` (words > 3 chars)
- Matches rows if dimension matches OR if 2+ title keywords match — broadens the filter for dynamic themes
- Renamed section headers from "Recommendations" to "Operational Standards" and "Key Questions" to "Diagnostic Questions" for consistency

- [ ] **Step 3: Test locally**

Run a full Stage 2 → Stage 3 flow. Open Go Deeper on a priority and check the "Why this recommendation" tab:
- Should show relevant rows from the recs table and questions map
- Should not show all rows (some filtering should occur)
- If no rows match, falls back to "No detailed analytical data available"

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: broaden Go Deeper analytical trail filtering for dynamic themes"
```

---

### Task 8: End-to-End Verification

- [ ] **Step 1: Run the app locally**

```bash
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT"
python app.py
```

Open `http://localhost:5000` in Chrome.

- [ ] **Step 2: Upload a test document and run Stages 1–3**

Use the Honduras PAD (or any available test document). Verify:

**Stage 1:** Unchanged — should work as before.

**Stage 2:**
- S/R definition box appears at the top of the output
- Output is organised by dynamic analytical themes (NOT "FCV Sensitivity Assessment" then "FCV Responsiveness Assessment")
- Each finding has [S], [R], or [S+R] tags inline
- Shift badges (Anticipate, Differentiate, etc.) appear across BOTH S and R findings
- Do No Harm traffic-light appears AFTER themes, BEFORE synthesis
- Synthesis has separate S and R paragraphs
- Ratings appear correctly in the sidebar gauges
- Under the Hood panels have the new plain-language titles with subtitles
- Panel 1 (recs table) has an S/R Tag column

**Stage 3:**
- Priority cards still have correct [S]/[R]/[S+R] tags
- refresh_shift badges still appear
- Go Deeper "Why this recommendation" tab shows relevant analytical trail data

- [ ] **Step 3: Check prompt admin modal**

Click the Admin button and verify Stage 2 prompt shows the new content.

- [ ] **Step 4: Push to remote**

```bash
git push origin feat/3-stage-redesign
```

- [ ] **Step 5: Update CLAUDE.md**

Update the relevant sections of CLAUDE.md to reflect:
- Stage 2 now uses dynamic thematic narrative (not Sensitivity → DNH → Responsiveness → Gaps)
- S/R definitions sharpened (reference spec)
- Under the Hood panels renamed
- Panel 1 has S/R Tag column
- Go Deeper Tab 2 uses broader keyword matching

Commit:
```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for Stage 2 thematic narrative restructure"
```
