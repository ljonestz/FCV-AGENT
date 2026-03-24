# FCV Project Screening App — Claude Development Guide

> **Claude Code Maintenance Instruction:** After every substantial change to this app (new features, prompt changes, new delimiters, UI additions, architectural decisions), update this `claude.md` file to reflect the change before committing. Keep section 1.3 (Stage pipeline), section 3 (Prompt Architecture), section 4 (Frontend), and section 5.3 (Priority Parsing) accurate at all times.

---

## Overview

This is a **World Bank FCV (Fragility, Conflict, and Violence) Project Screener** — a Flask-based web application that guides Task Team Leaders (TTLs) through a 4-stage workflow to assess how well a World Bank project integrates FCV considerations, and to generate targeted, actionable recommendations for improving its design and delivery.

The tool explicitly distinguishes two concepts:
- **FCV Sensitivity** — whether the project avoids doing harm: do-no-harm, contextual awareness, conflict-informed design, and operational readiness for FCV conditions.
- **FCV Responsiveness** — whether the project actively addresses the root drivers of fragility or builds resilience, anchored to the four pillars of the WBG FCV Strategy 2020–2025 (Preventing conflict / Crisis engagement / Transition out of fragility / Spillover mitigation).

Every prompt output now tags recommendations, mitigations, and priorities as [S], [R], or [S+R].

**Key goal:** Move from broad, vague recommendations ("service delivery needs to be targeted so it doesn't contribute to grievance") to specific, location-aware, operationally grounded suggestions ("historically, Nzerekore, Kindia, and Kankan have been excluded from service delivery; focus on these regions to rebuild state-society relationships").

---

## 1. Project Architecture

### 1.1 Tech Stack
- **Backend:** Python Flask 3.0.3 + Anthropic Claude API (Claude Sonnet 4 - latest version)
- **Frontend:** HTML + vanilla JavaScript + Markdown rendering
- **Hosting:** Render.com
- **Document processing:** PDF text extraction (pypdf) + LLM-assisted large document summarization
- **Session management:** Browser localStorage + JSON-serialized conversation history
- **Document generation:** python-docx for potential export functionality

### 1.2 Core Files
```
app.py                 # Flask backend, all 4 prompts, stage routes, explorer endpoint, document processing
index.html             # Frontend UI, Stage 1-4 display, explorer panel, prompt modal
background_docs.py     # FCV_GUIDE and FCV_OPERATIONAL_MANUAL constants (WBG FCV framework)
prompts.json           # Session-specific prompt overrides (persisted per session)
requirements.txt       # Python dependencies (Flask, Anthropic SDK, pypdf, python-docx)
Procfile              # Render deployment config
.gitignore            # Git ignore rules
static/               # Static assets (if any)
```

### 1.3 Four-Stage Pipeline

```
STAGE 1 — Identifying FCV Risks
├─ Input: Project document (any stage: Concept Note, PID, PCN, PAD, restructuring/AF draft)
│         + optional contextual docs (RRA, country risk assessments — 1–2 recommended)
├─ Output: Part A (project doc extract) + Part B (contextualized analysis)
│  └─ Final line of output: %%%DOC_TYPE: [PCN/PID/PAD/AF/Restructuring/ISR/Unknown]%%%
│     Frontend extracts this to set docType — no separate API call needed
├─ Automated FCV Web Research (runs before LLM generation):
│  ├─ extract_country_name() — LLM call to identify country from project doc (first 4000 chars)
│  ├─ extract_sector_name()  — LLM call to identify primary sector from project doc
│  ├─ run_fcv_web_research(country, sector) — Anthropic web_search tool, 9 searches, up to 5500 tokens
│  ├─ Research cached in-memory by "country::sector" key
│  ├─ Research brief injected into Stage 1 context as supplemental Part B material
│  └─ Research brief shown as collapsible dropdown at TOP of Stage 1 output (above main content)
├─ Three-tier citation priority:
│  ├─ Tier 1 — Uploaded contextual docs: [From: document name] (highest precedence)
│  ├─ Tier 2 — Automated web research: [From: web research] or named source
│  └─ Tier 3 — Training knowledge: [From: training knowledge] or named org/report
├─ Prompt behavior:
│  ├─ Part A: Extract *only* from project doc; no outside knowledge
│  ├─ Part B: Use tiers 1→2→3 in strict priority order; always label the source tier
│  └─ Large docs (>150k chars) pre-processed by LLM FCV extraction; docs >500k chars truncated
└─ UI: Stage header + research brief dropdown (top) + main output card + refine input box
   Loading note: Stage 1 shows "may take 60–90 seconds" due to web research phase
   DOC_TYPE line is stripped from display text before rendering

STAGE 2 — FCV-Sensitivity Screening
├─ Input: Stage 1 output
├─ Output: Risk ratings across 6 FCV dimensions (both risks TO and FROM the project)
│  ├─ Institutional Legitimacy
│  ├─ Inclusion
│  ├─ Social Cohesion
│  ├─ Security
│  ├─ Economic Livelihoods
│  └─ Resilience
├─ After the Summary Assessment Table — SENSITIVITY vs. RESPONSIVENESS CLASSIFICATION:
│  ├─ Each OST recommendation tagged [S], [R], or [S+R] with pre-assigned defaults:
│  │  ├─ Rec 1 (RRA/CRSS use) = [S]
│  │  ├─ Rec 2 (conflict-sensitive targeting) = [S]
│  │  ├─ Rec 3 (inclusive stakeholder engagement) = [S+R]
│  │  ├─ Rec 4 (Do No Harm / conflict-sensitive design) = [S]
│  │  ├─ Rec 5 (adaptive management) = [S]
│  │  └─ Rec 6 (M&E / GRM) = [S+R]
│  └─ RESPONSIVENESS PROBE paragraph (100–150 words): which of the four FCV Strategy pillars
│     the project has potential to address (Pillar 1: preventing conflict / Pillar 2: crisis
│     engagement / Pillar 3: transition out of fragility / Pillar 4: spillover mitigation)
├─ [S+R] strictly defined — only genuine overlap zones:
│  (1) inclusion/targeting of conflict-affected populations
│  (2) FCV logic embedded in ToC/PDO framing
│  (3) adaptive M&E that monitors harm AND adapts for resilience
│  (4) GRM designed to strengthen state-citizen accountability
├─ Prompt includes specific location callouts and evidence-based reasoning
└─ UI: Rating table + dimension explanations + S/R classification + refine input box

STAGE 3 — Identifying Project Gaps
├─ Input: Stages 1–2 output
├─ Output:
│  ├─ Part A: FCV sensitivity gaps (what's missing from design/implementation)
│  ├─ Part B: Mitigations (specific, location-named, mechanism-focused)
│  │  └─ Each mitigation measure now includes a TAG column: [S] / [R] / [S+R]
│  ├─ Part C: Do No Harm Checklist (structured table with Yes/Partial/No + evidence)
│  ├─ Part D: FCV Responsiveness Opportunities (formerly "Enhancement Opportunities")
│  │  └─ Structured around four FCV Strategy pillars:
│  │     ├─ Pillar 1: Preventing conflict
│  │     ├─ Pillar 2: Crisis engagement
│  │     ├─ Pillar 3: Transition out of fragility
│  │     └─ Pillar 4: Spillover mitigation
│  └─ Part E: Top 5 Priority Actions — each carries a [S] / [R] / [S+R] tag
├─ Prompt enforces geographic specificity and operational grounding
└─ UI: Collapsible sections + expandable Do-No-Harm checklist rendered from Part C table

STAGE 4 — Recommendations Note + Explorer
├─ Input: Stages 1–3 output (conversation history) + uploaded_doc_names list
├─ Output (narrative memo + JSON block appended at end):
│  ├─ Narrative: Preamble + Executive Summary (risk exposure, strengths, gaps,
│  │             sensitivity summary, responsiveness summary, ratings)
│  └─ JSON block: appended after narrative, delimited %%%JSON_START%%%...%%%JSON_END%%%
│     Fields: fcv_rating, fcv_responsiveness_rating, sensitivity_summary,
│             responsiveness_summary, risk_exposure {risks_to, risks_from},
│             priorities[] — each with:
│               title, fcv_dimension, tag, risk_level, the_gap, why_it_matters,
│               recommendation (SINGULAR — one cohesive action, NOT options menu),
│               who_acts, when, resources,
│               pad_sections (semicolon-separated PAD sections to modify),
│               suggested_language (2–4 sentences of draft PAD text in WBG register),
│               implementation_note (1–2 sentences: timing/cost/sequencing)
│        when values: "At design stage" | "Before appraisal" | "During implementation"
│        TAG: [S] / [R] / [S+R] — same strict definition as Stage 2/3
│        Most priorities will be [S] or [R]; [S+R] only for four named overlap zones
│        pad_sections/suggested_language/implementation_note always present in JSON →
│        download never requires clicking Explorer tabs first
├─ extract_priorities() rewrites JSON block via json.loads() + validation:
│  ├─ Returns unified dict: {error, priorities, fcv_rating, fcv_responsiveness_rating,
│  │                         sensitivity_summary, responsiveness_summary, risk_exposure}
│  ├─ _check_specificity(): heuristic for mid-sentence capitalised words (proper nouns)
│  ├─ _check_citations(): cross-references [From: ...] patterns against uploaded doc names
│  │   (extension-stripped) + org whitelist; flags unknown sources
│  └─ Malformed JSON: returns {error: True, message: ...} — NOT silent failure
├─ clean_stage4_output() strips %%%JSON_START/END%%% block as primary;
│  legacy delimiter stripping retained as fallback for cached outputs
├─ Citation policy: ONLY cite documents that appear as [From: doc name] in Stage 1.
│  NEVER fabricate document titles. Non-uploaded sources → [From: training knowledge] or
│  [From: web research]. This prevents hallucinated citations (e.g. [RRA 2022] when no RRA uploaded).
│  uploaded_doc_names must be included in /api/run-stage request body for citation check.
└─ UI:
   ├─ Main output card (preamble + exec summary + FCV Risk Exposure + Strengths + Gaps)
   ├─ FCV Sensitivity + FCV Responsiveness summary cards (side by side, after Gaps)
   ├─ FCV Sensitivity gauge (sidebar, blue, shield icon)
   ├─ FCV Responsiveness gauge (sidebar, green, leaf icon)
   ├─ Priority cards (horizontal stepper, shows one at a time)
   ├─ S/R tag badges have hover tooltips explaining each tag meaning
   ├─ Specificity warning badge (amber, dismissible) if no proper nouns detected
   ├─ Citation warning badge (amber, dismissible) if unrecognised [From: ...] strings found
   ├─ Per-priority zone-act layout (4 sections, all from JSON — always available):
   │  ├─ Essential action box (recommendation, blue left-border)
   │  ├─ Where in the PAD (.pad-chip tags split from pad_sections on ";")
   │  ├─ Suggested PAD language (suggested_language, italic yellow card)
   │  └─ Implementation consideration (implementation_note)
   ├─ "Go above and beyond" collapsible <details> per priority (LAZY — loads on first open)
   ├─ Explorer results cached per priority integer index in localStorage
   └─ Parse error banner shown if JSON extraction fails

EXPLORER (above-and-beyond alternatives only)
├─ Input: Priority title/body + Stage 1–4 history
├─ Output: 2–3 optional alternative approaches (%%%GF_ITEM%%% format only)
│  └─ Each item: title + 2–3 paragraph prose + PAD section reference
├─ Prompt produces ONLY %%%GO_FURTHER_START%%%...%%%GO_FURTHER_END%%% markers
│  (no %%%EXPLORER_NARRATIVE_START%%% — that format is legacy/deprecated)
├─ Lazy-loaded: only fires when user expands the <details> section
├─ Design principle: core recommendation is self-contained in JSON; Explorer adds
│  optional depth for teams with additional appetite — NOT required reading
└─ UI:
   ├─ <details class="zone-act-beyond"> triggers handleBeyondToggle(el, idx) on open
   ├─ Loading spinner shown inside <details> until stream completes
   ├─ renderAboveAndBeyondHtml(parsed) renders goFurtherItems as .beyond-item cards
   └─ "Ask →" follow-up box below zone-act (separate from Explorer)
```

---

## 2. Design Decisions & Design Philosophy

### 2.1 Why 4 Stages (Not a Single Prompt)?
- **Sequential refinement:** Each stage builds on prior outputs, allowing users to pause, review, and refine before proceeding.
- **Quality control:** Users see intermediate reasoning and can correct errors or add local knowledge at each step, rather than getting an opaque final output.
- **Cognitive load:** Breaking analysis into digestible pieces helps TTLs understand the reasoning without overwhelming them.
- **Flexibility:** Users can re-run Stage 2 without re-analyzing documents, adjust Stage 3 findings before generating final recommendations, etc.

### 2.2 Why Stage 1 Splits Part A from Part B?
- **Transparency:** Users need to understand what the tool extracted *directly* from their project document vs. what it inferred from external context or AI training knowledge.
- **Document trust:** A project document is a formal WBG artifact; the tool respects its primacy while being clear about supplementation.
- **Accuracy accountability:** If something in Part A seems wrong, the issue is in extraction; if Part B is off, it's in contextual interpretation or knowledge gaps.

### 2.3 Why Remove the Technical Annex & Replace with Explorer?
**Problem:** Stage 4 was generating two outputs simultaneously:
- A fixed "Recommendations Note" for the TTL's final memo
- A "Technical Annex" with extra methodological detail

This was creating length/clarity issues — the note got dense, and it wasn't clear what belonged in a final memo vs. internal working notes.

**Solution:** Move all exploratory depth to an **on-demand Explorer panel** that is:
- **Separate:** Doesn't clutter the main Recommendations Note
- **Interactive:** Users drill into *specific* priorities, not a generic annex
- **Contextual:** Each exploration is grounded in the priority's gap + why it matters
- **Cacheable:** Avoid redundant API calls for the same priority + follow-up question

**Result:** Clean, memo-ready Stage 4 output + optional depth available when users want it.

### 2.3a Why Each Priority Now Has a Single Recommendation + PAD Guidance (not A/B/C options)
**Problem (identified by TTL user testing):** The previous Explorer auto-loaded 2–3 action options per priority on page load, creating cognitive overload: 5 priorities × 3 options = 15 things to evaluate. Non-specialist TTLs needed a clear directive, not a menu.

**Solution:** Restructure each priority card around one clear action with operational specifics, sourced directly from the Stage 4 JSON:
- `recommendation` — single cohesive action (already existed)
- `pad_sections` — explicit PAD sections to modify (new)
- `suggested_language` — draft text to insert verbatim (new)
- `implementation_note` — timing/cost/dependency note (new)

Explorer demoted to a collapsed "Go above and beyond" section — lazy-loaded only if the user opens it, explicitly labelled Optional.

**Key architectural consequence:** All core content now lives in the Stage 4 JSON. The download (`downloadReport()`) no longer requires clicking through all priority tabs before exporting — it always has everything it needs.

### 2.4 The Specificity & Actionability Mandate
**Core principle:** Recommendations must be **specific and actionable**, not broad and vague.

- **Bad:** "Service delivery needs to be targeted so it doesn't contribute to grievance"
- **Good:** "Historically, Nzerekore, Kindia, and Kankan have been excluded from service delivery. To rebuild the state-society relationship, focus service delivery in these regions, prioritizing (a) areas with highest grievance sensitivity, (b) community health extension worker networks, (c) cash-for-work entry points."

**How it's enforced:**
- Stage 3 prompt explicitly requires geographic naming, mechanism specification, and operational entry points (PAD instruments, existing WBG programs, partner organizations)
- Stage 4 prompt generates `pad_sections`, `suggested_language`, and `implementation_note` per priority — specifics are in the JSON, not deferred to Explorer
- Explorer prompt generates 2–3 optional alternative approaches (not A/B/C options menus); core recommendation is always the single clear directive

**Trade-off managed:** We avoid exact costs (which change) but include enough detail for a TTL to brief management or co-design with counterparts.

### 2.5 Session Persistence & Conversation History
- All user inputs and LLM outputs are stored in browser localStorage (serialized as JSON)
- On page reload, the app can recover the session and allow "continue" or "restart" workflows
- Sessions can be saved with a name, allowing users to return to previous analyses
- Conversation history is passed to each stage, so the LLM maintains context across all 4 stages

**Limitation:** localStorage is browser-specific and not suitable for long-term storage or team collaboration. For future versions, consider a backend database.

---

## 3. Prompt Architecture

### 3.1 Where Prompts Live

**Default prompts:**
```python
# In app.py, top-level DEFAULT_PROMPTS dictionary
DEFAULT_PROMPTS = {
    "1": "# Role\nYou are an expert FCV analyst...",  # Stage 1
    "2": "# Role\nYou are an expert FCV analyst...",  # Stage 2
    "3": "# Role\nYou are an expert FCV analyst...",  # Stage 3
    "4": "# Role\nYou are an expert FCV analyst...",  # Stage 4 (Recommendations Note)
    "explorer": "# Role\nYou are an expert FCV analyst..."  # Explorer deep-dive
}
```

**Session-specific overrides:**
- Stored in `prompts.json` (in project root)
- Loaded via `load_prompts()` function, which merges with DEFAULT_PROMPTS
- Saved via `save_prompts()` function when user edits via Admin modal
- Scoped to current session only (not persisted across sessions)

**How to override:**
- Via UI: Admin tab → per-stage prompt editor → Save & Close
- Via code: Edit DEFAULT_PROMPTS in app.py (persists globally across all sessions)

### 3.2 Stage 1: "Identifying FCV Risks"

**Purpose:** Extract FCV-relevant content from uploaded project and contextual documents, enriched by automated web research.

**Input:** Any project document at any preparation stage (Concept Note, PID, PCN, PAD, restructuring/AF draft). Optionally 1–2 contextual documents (RRA, country risk report, etc.).

**Automated FCV web research phase (runs before LLM generation):**
1. `extract_country_name()` — brief LLM call to identify project country (first 4000 chars)
2. `extract_sector_name()` — brief LLM call to identify primary project sector
3. `run_fcv_web_research(country, sector)` — Anthropic web_search tool, 9 targeted searches, up to 5500 tokens
   - Covers: conflict/security, governance, humanitarian, economic, FCV actors, structural drivers, vulnerable groups, regional dimensions, **sector-specific FCV considerations**
   - Results cached in-memory by `"country::sector"` key; lost on server restart
4. Research brief injected into Stage 1 context as supplemental material
5. Research brief shown as collapsible dropdown at TOP of Stage 1 output (labeled "Automated FCV risk briefing — general country & sector insights")

**Three-tier citation priority:**
- Tier 1 — Uploaded contextual docs: `[From: document name]` (highest precedence)
- Tier 2 — Automated web research: `[From: web research]` or named source (e.g. `[From: ICG]`)
- Tier 3 — Training knowledge: `[From: training knowledge]` or named org/report

**Key behaviors:**
- Part A: Extract only from the project document. No outside knowledge.
- Part B: Use tiers 1→2→3 in strict priority order; always label the source tier at each point.
- Both parts are strictly separated in the output.

**Large document handling:**
- Documents > 150,000 characters are condensed via LLM extraction (FCV-relevant content only).
- Documents > 500,000 characters are truncated to MAX_DOC_CHARS.
- Truncation warnings shown to users when triggered.

**Document type classification (embedded in Stage 1):**
- The very last line of every Stage 1 response is: `%%%DOC_TYPE: [PCN/PID/PAD/AF/Restructuring/ISR/Unknown]%%%`
- The frontend extracts this via regex when Stage 1 completes and sets the `docType` state
- This replaces the former separate `/api/detect-document-type` API call (which was slow, 10–15 seconds)
- The DOC_TYPE line is stripped from the display text before rendering to the user
- Manual document type override selects have been removed from both the upload area and session bar

**Loading time note:** Stage 1 loading card shows "may take 60–90 seconds" to set expectations for the web research phase.

**User refine loop:** After Stage 1 displays, users can use a refine box to:
- Correct misreadings
- Add local knowledge not in documents
- Flag missing content before proceeding

### 3.3 Stage 2: "FCV-Sensitivity Screening"

**Purpose:** Assess project across 6 FCV dimensions, both risks TO the project and risks FROM the project. Also classifies each OST recommendation as [S], [R], or [S+R] and probes FCV Responsiveness potential.

**Key behaviors:**
- Outputs structured risk ratings (e.g., "Risk: Medium | Evidence: Project's focus on service delivery in contested areas may increase exposure...")
- Includes specific geographic callouts (e.g., "In Nzerekore and Kindia, where state legitimacy is already low...")
- Reasoning is explicit so users can see if a dimension is overweighted, underweighted, or missing key context.

**SENSITIVITY vs. RESPONSIVENESS CLASSIFICATION (appended after Summary Assessment Table):**
- Pre-assigned defaults for the 6 OST recommendations:
  - Rec 1 (RRA/CRSS utilization) = **[S]**
  - Rec 2 (conflict-sensitive targeting) = **[S]**
  - Rec 3 (inclusive stakeholder engagement) = **[S+R]**
  - Rec 4 (Do No Harm / conflict-sensitive design) = **[S]**
  - Rec 5 (adaptive management / monitoring arrangements) = **[S]**
  - Rec 6 (M&E / GRM) = **[S+R]**
- LLM adjusts tags based on project evidence; defaults may be overridden where justified

**RESPONSIVENESS PROBE paragraph (100–150 words):**
- Written after the S/R classification table
- Assesses which of the four FCV Strategy pillars the project has potential to address:
  - Pillar 1: Preventing conflict and promoting peace
  - Pillar 2: Engaging in crisis situations
  - Pillar 3: Helping countries transition out of fragility
  - Pillar 4: Mitigating regional and global spillovers
- Honest assessment: most projects will have limited responsiveness potential; probe should not overstate

**Strict [S+R] definition (must be enforced):**
[S+R] is ONLY valid for these four overlap zones:
1. Inclusion/targeting of conflict-affected populations (where design serves both harm-avoidance AND active inclusion as a resilience strategy)
2. FCV logic embedded in the ToC/PDO framing (not just a risk note — actually changes the project theory)
3. Adaptive M&E that both monitors harm AND adapts to build resilience
4. GRM designed to strengthen state-citizen accountability (not just complaint handling)
If in doubt → assign [S] or [R]. Most recommendations will not qualify for [S+R].

**User refine loop:** Users can correct dimension ratings or add missing geographic/contextual information before proceeding to Stage 3.

### 3.4 Stage 3: "Identifying Project Gaps"

**Purpose:** Identify where the project design / implementation falls short on FCV sensitivity, and propose mitigations. Also maps responsiveness opportunities onto the four FCV Strategy pillars.

**Output parts:**
- **Part A:** Gaps in FCV sensitivity (design, implementation, M&E, stakeholder engagement, etc.)
- **Part B:** Concrete, location-specific mitigations — each with a **TAG column** (`[S]` / `[R]` / `[S+R]`)
  - Tag follows same strict definition as Stage 2 (most mitigations will be [S] or [R])
- **Part C:** Do No Harm Checklist (principle | Yes/Partial/No | evidence/gap)
- **Part D: FCV Responsiveness Opportunities** (formerly "Enhancement Opportunities")
  - Structured around the four FCV Strategy pillars:
    - Pillar 1: Preventing conflict and promoting peace
    - Pillar 2: Engaging in crisis situations
    - Pillar 3: Helping countries transition out of fragility
    - Pillar 4: Mitigating regional and global spillovers
  - Each pillar lists specific project design changes that could move beyond sensitivity into responsiveness
- **Part E:** Top 5 Priority Actions — each carries a `[S]` / `[R]` / `[S+R]` tag

**Key behaviors:**
- Mitigations are not generic ("improve stakeholder engagement") but specific ("establish community feedback forums in Kankan District, staffed by local civil society orgs trusted by Dinka pastoralists, with quarterly feedback to project implementation unit")
- When multiple options exist, framed as alternatives, not a single "solution"
- Geographic specificity is required; locations are named, and reasons for targeting specific areas are stated

**User refine loop:** Users can adjust gaps, refine mitigations, or add local knowledge (e.g., "Actually, we already have this mechanism through NGOS X and Y").

### 3.5 Stage 4: "Recommendations Note" (+ Explorer)

**Main Output (Recommendations Note):**
```
[Preamble: 50–75 words on project FCV sensitivity context]

[Executive Summary:
  - Opening Assessment (1 bold sentence)
  - Operational Context (150–200 words)
  - FCV Risk Exposure (plain language, 2 paragraphs):
      RISKS_TO_PROJECT: How FCV dynamics threaten project delivery
      RISKS_FROM_PROJECT: How project design could worsen fragility
  - Strengths (80–120 words)
  - Gaps (100–130 words)
  - FCV Sensitivity Summary (80–100 words, extracted via delimiter, shown as summary card)
  - FCV Responsiveness Summary (80–100 words, extracted via delimiter, shown as summary card)
]

[FCV Sensitivity Rating — one of:
  Extremely Low | Very Low | Low | Adequate | Well Embedded | Very Well Embedded]

[FCV Responsiveness Rating — same scale, emitted immediately after sensitivity rating]

[4–5 Strategic Priority cards, each with:
  - title: Priority N · [Actionable verb phrase]
  - fcv_dimension: one of the 6 dimensions
  - tag: [S] | [R] | [S+R]
  - risk_level: High | Medium | Low
  - the_gap: 2–3 sentences
  - why_it_matters: 2–3 sentences (operational + FCV dimensions combined)
                    + S/R pillar justification for [R] and [S+R] priorities
  - recommendation: SINGLE cohesive action (NOT an options menu) — 2–3 sentences,
                    names specific location + mechanism + entry point
  - who_acts: TTL | PIU | Government counterpart | FCV specialist | Procurement team
  - when: At design stage | Before appraisal | During implementation
  - resources: Minimal | Moderate | Significant
]
```

**JSON block format (appended after narrative memo):**
```
%%%JSON_START%%%
{
  "fcv_rating": "Adequate",
  "fcv_responsiveness_rating": "Low",
  "sensitivity_summary": "...",
  "responsiveness_summary": "...",
  "risk_exposure": {
    "risks_to": "...",
    "risks_from": "..."
  },
  "priorities": [
    {
      "title": "Priority 1 · [Actionable verb phrase]",
      "fcv_dimension": "Inclusion",
      "tag": "[S]",
      "risk_level": "High",
      "the_gap": "...",
      "why_it_matters": "...",
      "recommendation": "Single cohesive action — NOT an options menu",
      "who_acts": "TTL | PIU | Government counterpart",
      "when": "Before appraisal",
      "resources": "Moderate",
      "pad_sections": "Annex 5: Stakeholder Engagement Plan; ESCP Commitment #4",
      "suggested_language": "2–4 sentences of draft PAD text in WBG document register",
      "implementation_note": "1–2 sentences on timing, cost, or key dependency"
    }
  ]
}
%%%JSON_END%%%
```

**Critical: `recommendation` field (not `SUGGESTED_DIRECTIONS`):**
- Single cohesive action, present tense, 2–3 sentences
- Must NOT be an options menu ("Consider A / Or B / Or C" is NOT allowed)
- Must name specific location, mechanism, and entry point
- S/R pillar justification sentence required in `why_it_matters` for [R] and [S+R] priorities

**`extract_priorities()` return shape:**
```python
{
  'error': bool,               # True if JSON malformed
  'message': str,              # error description (only when error=True)
  'priorities': [...],
  'fcv_rating': str,
  'fcv_responsiveness_rating': str,
  'sensitivity_summary': str,
  'responsiveness_summary': str,
  'risk_exposure': {'risks_to': str, 'risks_from': str}
}
```

**`clean_stage4_output()` stripping order:**
1. Primary: strip `%%%JSON_START%%%...%%%JSON_END%%%` block (new format)
2. Fallback: strip legacy delimiter blocks for cached outputs:
   - `%%%RISK_EXPOSURE_START/END%%%`, `%%%SENSITIVITY_SUMMARY_START/END%%%`
   - `%%%RESPONSIVENESS_SUMMARY_START/END%%%`, `%%%FCV_RATING/RESPONSIVENESS_RATING%%%`
   - `%%%PRIORITY_START/END%%%` blocks, `%%%GAP_TABLE_START/END%%%`

**Note on %%%GAP_TABLE_START/END%%%:** LLM is no longer instructed to emit this block. The `extract_gap_table()` backend function still exists but the FCV Design Assessment Table is not displayed in the current UI.

**Citation policy for Stage 4:**
- ONLY cite documents that appeared as `[From: document name]` in Stage 1. NEVER fabricate titles.
- Non-uploaded sources → `[From: training knowledge]` or `[From: web research]`
- This prevents hallucinated citations (e.g., citing `[RRA 2022]` when no RRA was uploaded)

**Explorer input:** Each priority's JSON (title + body) is fed to the Explorer prompt, which generates **2–3 optional alternative approaches** only. Core content (`pad_sections`, `suggested_language`, `implementation_note`) is in the Stage 4 JSON — not Explorer.

**Explorer output format:**
- Only `%%%GO_FURTHER_START%%%...%%%GO_FURTHER_END%%%` markers used
- Each item uses `%%%GF_ITEM%%%` + `%%%GF_TITLE%%%` markers (same as legacy Go Further)
- Parsed by `parseExplorerText()` → `goFurtherItems[]`
- Rendered by `renderAboveAndBeyondHtml(parsed)` into `.beyond-item` cards inside `<details>`

**Key behaviors:**
- Recommendations are specific and actionable, not broad policy suggestions
- Geographic locations are named (e.g., "In Oromia, prioritize...")
- `pad_sections` chips are rendered from semicolon-separated string (split on `;`)
- `suggested_language` rendered in italic yellow card (`.zone-act-draft`)
- `implementation_note` rendered in grey bordered card (`.zone-act-impl`)
- A collegial tone appropriate for peer review by a TTL

**Do No Harm Checklist (from Stage 3):** Extracted and displayed as a collapsible table in the Stage 4 UI, showing which Do-No-Harm principles are addressed, partially addressed, or at risk.

---

## 4. Frontend Architecture

### 4.1 UI Panels
1. **Onboarding modal** — Disclaimer + warning about AI limitations, checkbox to suppress on future visits
2. **Session bar** — Floating bar showing current stage progress + save session button
3. **Stage progress stepper** — Visual indicator of 1-of-4, 2-of-4, etc.
4. **Input panel (Stages 1–3)** — Upload box, document list, refine input
5. **Output panel (Stages 1–4)** — Displays LLM output + collapsible sections (Parts A/B for Stage 1, etc.)
6. **Explorer panel (Stage 4)** — Horizontal priority stepper + priority card + inline explorer options
7. **Prompt modal** — Admin-only, lets users view/edit the 5 prompts (Stage 1–4 + Explorer) per session
8. **FCV Sensitivity gauge (sidebar)** — SVG arc gauge, blue, shield icon; animates from `%%%FCV_RATING%%%` delimiter
9. **FCV Responsiveness gauge (sidebar)** — SVG arc gauge, green, leaf icon; animates from `%%%FCV_RESPONSIVENESS_RATING%%%` delimiter
   - IDs: `fcv-resp-arc-fill`, `fcv-resp-leaf-path`, `fcv-resp-rating-label`, `fcv-resp-need-label`

### 4.2 Key JavaScript Functions

**Stage management:**
- `goToStage(n)` — advance to stage n
- `onStageComplete()` — callback when LLM finishes streaming output
- `updateSessionBar()` — refresh progress indicator

**Stage 1:**
- `addDocument()` — trigger file upload
- `removeDocument(idx)` — remove doc from list
- `submitStageInput()` — send docs + user refinement to `/api/run-stage`
- `renderStage1Output()` — display Part A and Part B

**Stage 4 Explorer:**
- `initStage4UI()` — parse priorities, build stepper, show Priority 1
- `showPriority(idx)` — render full priority card with 4-section zone-act layout from JSON; no auto-load of Explorer
- `loadExplorerForPriority(idx)` — lazy-loaded by `handleBeyondToggle`; writes to `#above-beyond-content-{idx}`; timer ID is `beyond-timer-{idx}`
- `handleBeyondToggle(el, idx)` — ontoggle handler for `<details class="zone-act-beyond">`; triggers `loadExplorerForPriority` on first open; renders from cache if already loaded
- `renderAboveAndBeyondHtml(parsed)` — renders `parsed.goFurtherItems` as `.beyond-item` cards; used by both `handleBeyondToggle` and `loadExplorerForPriority` done callback
- `cancelExplorer()` — aborts in-flight Explorer request via `explorerAbortController`
- `renderPriorityStepper()` — build horizontal step indicator; compact S/R badge below risk badge on each tab
- `renderPrioritiesIntro()` — renders intro list; compact S/R badge after risk label in each `pi-item`

**S/R tag badges:**
- `renderSRTagBadge(tag, compact)` — renders inline pill badge
  - Full mode (default): "Sensitivity" / "Responsiveness" / "Sensitivity + Responsiveness"
  - Compact mode (`compact=true`): "S" / "R" / "S+R"
  - CSS classes: `.sr-tag`, `.sr-tag.sensitivity`, `.sr-tag.responsiveness`, `.sr-tag.both`
- `renderSRCards(sensitivityText, responsivenessText)` — renders two side-by-side summary cards
  - Inserted between the Gaps paragraph and the `<div id="priorities-intro">` div in Stage 4 output
  - CSS: `.sensitivity-responsiveness-grid`, `.sr-card`, `.sr-card.sensitivity` (border `#0050A0`), `.sr-card.responsiveness` (border `#16A34A`), `.sr-card-label`

**Sidebar (updateSidebar()):**
- Animates both gauges: sensitivity arc + responsiveness arc
- Priority overview (`pov-row`) includes compact S/R badge after risk label

**Utilities:**
- `md(text)` — markdown-to-HTML renderer
- `escHtml()` / `escAttr()` — HTML escaping
- `formatDate()` — human-readable timestamps
- `saveSession()` / `loadSession()` — localStorage serialization

### 4.3 Removed Items
- **`detectDocumentType()` function** — removed. Doc type is now embedded in Stage 1 output (see Section 3.2).
- **`/api/detect-document-type` API call** — endpoint and call both removed.
- **Manual document type override `<select>` elements** — removed from both upload area and session bar.
- **FCV Design Assessment Table** — `renderGapTable()` is no longer called from `renderOut`. Table is not displayed. Code remains for potential future use.
- **`docTypeDetecting` variable** — removed (was used to gate doc type detection).
- **Explorer auto-load on `showPriority()`** — removed. Explorer no longer fires on priority tab click. Lazy-loaded via `<details>` toggle instead.
- **`#explorer-options-{idx}` zone** — removed from zone-act. Replaced by `#above-beyond-content-{idx}` inside `<details>`.
- **`exp-timer-{idx}` / `exp-loading-{idx}`** — removed. Replaced by `beyond-timer-{idx}` / `beyond-loading-{idx}`.

### 4.3a Download Behaviour
- **`downloadReport()`** always includes all core priority content from JSON: `recommendation`, `pad_sections`, `suggested_language`, `implementation_note`, `who_acts`, `when`, `resources`
- Does NOT require Explorer to have been loaded — no click-through needed before downloading
- Optionally appends `goFurtherItems` if Explorer was already opened for that priority
- `pad_sections` rendered as `<code>` chips in the Word export

### 4.4 Styling & Aesthetics
- **Color scheme:** WBG-inspired palette (deep navy, cobalt blue, orange accents)
- **Stage colors:** Each stage has a distinct color (s1, s2, s3, s4) used in progress bars, section headers, and priority dimension badges
- **Typography:** Noto Sans (clean, readable)
- **Spacing:** 12/24/32px grid
- **Icons:** Lucide React SVG icons (used sparingly for clarity)

### 4.5 Do No Harm Checklist Rendering
- Extracted from Stage 3 output via regex (looking for `## Part C` section)
- Parsed as a Markdown table with rows: `| Principle | Status | Evidence/Gap |`
- Rendered as HTML table with color-coded status badges (green/yellow/red)
- Collapsible so it doesn't clutter the main Stage 4 output

---

## 5. Backend Routes & API

### 5.1 Main Routes

```python
# Core analysis route (all 4 stages)
POST /api/run-stage
  Input: {stage, documents[], history[], user_message, prompt_override}
  Output: Server-Sent Events (SSE) stream with chunks, then {done, output, priorities, fcv_rating}

# Explorer deep-dive route
POST /api/run-explorer
  Input: {priority_title, priority_body, history[], user_question}
  Output: SSE stream with chunks, then {done, output, issue, options[]}

# Admin/Prompt management
GET /api/admin/prompts         # Get current session prompts
POST /api/admin/prompts        # Save custom prompts for session
POST /api/admin/prompts/reset  # Reset prompts to defaults

# System endpoints
GET /                          # Main app page
GET /health                    # Health check endpoint
GET /how-it-works             # Workflow explanation page
GET /admin                     # Admin panel (prompts modal)
GET /api/default-prompts      # Get default prompts for reference
```

### 5.2 Document Handling

**Large document pre-processing:**
```python
if len(doc_content) > MAX_DOC_CHARS:
    # Use LLM to extract FCV-relevant content
    # Returns: extracted_text, page_count, truncation_warning
```

**PDF extraction:**
```python
# Uses pypdf library
extracted_text, page_count = extract_pdf_text(base64_content, filename)
```

### 5.3 Priority Parsing (Stage 4 Output)

```python
def extract_priorities(stage4_output, uploaded_doc_names=None):
    # Finds %%%JSON_START%%%...%%%JSON_END%%% block, parses via json.loads()
    # Runs _check_specificity() and _check_citations() post-parse
    # Returns unified dict:
    #   {error, message?, priorities, fcv_rating, fcv_responsiveness_rating,
    #    sensitivity_summary, responsiveness_summary,
    #    risk_exposure: {risks_to, risks_from}}
    # Each priority dict has 13 core fields: title, fcv_dimension, tag, risk_level,
    #   the_gap, why_it_matters, recommendation, who_acts, when, resources,
    #   pad_sections, suggested_language, implementation_note,
    #   + 2 post-parse fields: specificity_warning (bool), citation_warnings (list)
    # On malformed JSON: returns {error: True, message: ...}
```

**Note:** The 5 orphaned delimiter-extraction functions have been DELETED:
- `extract_fcv_rating`, `extract_fcv_responsiveness_rating`
- `extract_sensitivity_summary`, `extract_responsiveness_summary`
- `extract_risk_exposure`

These were replaced by the unified `extract_priorities()` return dict.

**Stage 4 SSE done event response includes:**
```json
{
  "priorities": [...],
  "fcv_rating": "...",
  "fcv_responsiveness_rating": "...",
  "sensitivity_summary": "...",
  "responsiveness_summary": "...",
  "risk_exposure": {"risks_to": "...", "risks_from": "..."},
  "parse_error": false,
  "parse_error_message": ""
}
```

---

## 6. Key Implementation Details

### 6.1 Streaming Output (SSE)
- All stage and explorer requests use Server-Sent Events (SSE) for streaming
- Frontend displays text progressively as it arrives, avoiding "long wait" UX
- Allows users to see the LLM's output in real-time

### 6.2 Conversation History
- Entire history (all user messages + LLM responses) is maintained in browser localStorage
- Passed to each subsequent stage so the LLM maintains context
- Allows recovery/resume if page reloads
- Can be serialized to JSON for export/sharing (though this is optional)

### 6.3 Prompt Override System
- Admin modal allows users to override any of the 5 default prompts (Stage 1–4 + Explorer)
- Override is scoped to the current session only (not saved globally)
- Allows experimentation / customization per project

### 6.4 Do No Harm Extraction
- Pulled from Stage 3 output via regex (finding `## Part C` + Markdown table)
- Parsed into rows with principle/status/evidence columns
- Re-rendered in Stage 4 UI as a collapsible, color-coded table

### 6.5 PDF Processing Pipeline
**Extraction steps in `extract_pdf_text()`:**
1. Decode base64 PDF content from frontend
2. Use PyPDF to read PDF pages
3. Extract text from each page sequentially
4. Return: (extracted_text, page_count)
5. Handle errors gracefully with fallback messages

**Large document condensation in `extract_fcv_content()`:**
1. Check if document length exceeds EXTRACT_THRESHOLD (150,000 chars)
2. If yes, use Claude API to summarize FCV-relevant content
3. Preserve key information while reducing size
4. Append truncation warning to user output
5. Handle PDF extraction errors with user-friendly messages

### 6.6 UX Safeguard Features (Added v6.0)

**S/R tag tooltips:** `renderSRTagBadge()` adds `title` attribute to each tag badge explaining [S], [R], [S+R] in plain language. Hover-accessible.

**Specificity warning badge:** Shown on priority card if `priority.specificity_warning === true`. Amber, dismissible, stored per-priority in localStorage (`warn_spec_dismissed_{idx}`).

**Citation warning badge:** Shown on priority card if `priority.citation_warnings.length > 0`. Amber, dismissible, hover shows flagged citation strings. Stored in localStorage (`warn_cite_dismissed_{idx}`).

**Upload feedback:** `addFiles()` calls `fetchFileMetadata()` which hits `/api/detect-document-type` (extended to return `word_count` + `extraction_status`). Chips show filename + word count + doc type. Non-PDF files limited to 10,000 chars for speed.

**Explorer lazy load + cancel + timer:** `loadExplorerForPriority()` is triggered by `handleBeyondToggle()` when the `<details>` section is first opened. Uses `AbortController` + `setInterval` elapsed timer. Cancel button calls `cancelExplorer()`. Timer updates `beyond-timer-{idx}` (not `exp-timer-{idx}`). Local `timerHandle` variable prevents stale interval clearing.

**Explorer localStorage cache:** `explorerCache` keyed by integer priority index (not title string). Backed by `localStorage` key `explorer_priority_{idx}`. Cache cleared on Stage 4 re-run. On `handleBeyondToggle`, if cache exists, renders immediately without API call.

**Font consistency:** `.pc-zone-body` (priority card body text) is 14px, matching `.out-body` (exec summary). Do not let these diverge — keep both at 14px.

**Stage consistency banner:** `renderOut()` injects a yellow dismissible banner at top of Stage 3/4 output if `stage2_timestamp > stage${N}_timestamp`. Timestamps written to localStorage BEFORE `renderOut()` call. Stage 2 re-run clears both dismissed flags.

### 6.7 Priority Parsing and JSON Extraction
**In `extract_priorities(text, uploaded_doc_names=None)`:**
1. Search for `%%%JSON_START%%%` and `%%%JSON_END%%%` delimiters
2. Parse JSON block via `json.loads()` (no regex field extraction)
3. Run `_check_specificity()`: looks for mid-sentence capitalised words as proper-noun proxy
4. Run `_check_citations()`: cross-references `[From: ...]` patterns against uploaded doc names
   (extensions stripped) + known org whitelist; flags unrecognised sources
5. Return unified dict with all fields + per-priority `specificity_warning` / `citation_warnings`
6. On malformed JSON: return `{error: True, message: ...}` — NOT silent failure

---

## 7. Common Workflows & How to Modify

### 7.1 I Want to Change a Prompt
1. Open the app
2. Click "Admin" → select the stage (1, 2, 3, 4, or Explorer)
3. Edit the prompt text in the modal
4. Click "Save & Close"
5. Re-run that stage with the new prompt

(This is session-scoped; to persist globally, edit `DEFAULT_PROMPTS` in `app.py`)

### 7.2 I Want to Change the 6 FCV Dimensions
Stage 2 prompt lists the 6 dimensions explicitly:
```
1. Institutional Legitimacy
2. Inclusion
3. Social Cohesion
4. Security
5. Economic Livelihoods
6. Resilience
```

To add/remove/modify:
1. Edit the Stage 2 prompt in `DEFAULT_PROMPTS` (or via Admin modal)
2. Re-run Stage 2 with the updated prompt

**Note:** If you change the number of dimensions, you may also need to update Stage 3 & 4 prompts to reference them correctly.

### 7.3 I Want to Change What Stage 4 Priorities Look Like
Stage 4 prompt defines the JSON schema for each priority. Current fields:
```json
{
  "title": "Priority N · phrase",
  "fcv_dimension": "...",
  "tag": "[S] | [R] | [S+R]",
  "risk_level": "High|Medium|Low",
  "the_gap": "...",
  "why_it_matters": "...",
  "recommendation": "Single cohesive action — NOT an options menu",
  "who_acts": "...",
  "when": "At design stage | Before appraisal | During implementation",
  "resources": "Minimal | Moderate | Significant"
}
```

To add/remove fields:
1. Update the JSON schema section of the Stage 4 prompt (`DEFAULT_PROMPTS["4"]` in `app.py`)
2. Update `extract_priorities()` in `app.py` to handle the new field from the parsed JSON
3. Update `showPriority()` in `index.html` to display the new field
4. Update `downloadReport()` in `index.html` if the field should appear in the export

### 7.4 I Want to Add a 5th Stage
1. Add a new key to `DEFAULT_PROMPTS` (e.g., `"5"`)
2. Add a new case in the stage switch logic in the `/api/run` route
3. Add a new stage card and input panel to `index.html`
4. Update the stepper to show 1-of-5, 2-of-5, etc.

---

## 8. Deployment

### 8.1 Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (required)
export ANTHROPIC_API_KEY="your-api-key-here"
export ADMIN_PASSWORD="fcv-admin-2024"  # Optional, uses default if not set

# Run the app
python3 app.py

# Open http://localhost:5000 in your browser
```

### 8.2 Deploy to Render.com
1. Connect your GitHub repo to Render
2. Create a new Web Service, select your repo + branch
3. Render reads the `Procfile` and `requirements.txt`
4. Deploy automatically on push to that branch

**Environment variables needed (set in Render dashboard):**
- `ANTHROPIC_API_KEY` — your Claude API key (required)
- `ADMIN_PASSWORD` — optional, for prompt admin modal (default: "fcv-admin-2024" if not set)

**Current dependencies:**
- Flask 3.0.3
- anthropic >= 0.40.0 (Anthropic SDK for Claude API)
- pypdf >= 4.0.0 (PDF text extraction)
- python-docx 1.1.2 (future document generation support)

### 8.3 GitHub Workflow
```bash
# Create a feature branch
git checkout -b feature/explorer-panel

# Make changes to app.py, index.html, etc.

# Test locally
python3 app.py

# Commit and push
git add app.py index.html
git commit -m "Add explorer panel with deep-dive Q&A"
git push origin feature/explorer-panel

# Open a PR, review, merge to main
# Render auto-deploys when main is updated
```

---

## 9. Safety & Output Handling

### 9.1 AI Disclaimer Header
All Stage 4 outputs include a header disclaimer:
```
---
**AI-Generated Output — For Review Purposes Only**

This Recommendations Note was produced by an LLM-assisted screening tool. It is intended as a supplementary analytical input to support expert review, not as a substitute for professional FCV analysis. The content reflects the AI interpretation of uploaded documents and embedded WBG guidance, and may contain errors, omissions, or misjudgements. Users are responsible for critically reviewing, verifying, and adapting this output before any operational use.

*Generated by WBG FCV Project Screener · {date}*

---
```

This disclaimer is prepended to all Stage 4 outputs via the `DO_NO_HARM_HEADER` constant in `app.py`.

### 9.2 Stream-Based Output with Error Handling
- All API responses use Server-Sent Events (SSE) for real-time streaming
- Frontend displays text progressively as chunks arrive
- If stream fails, frontend displays error message with recovery options
- Session history is preserved even if a stage fails mid-stream

---

## 10. Known Limitations & Future Improvements

### 10.1 Current Limitations
- **localStorage scope:** Sessions are browser/device-specific; no team sharing or long-term archival
- **Rate limiting:** LLM calls are not rate-limited; high-volume usage could hit API throttles
- **Large PDFs:** Documents >500k chars are truncated; very large projects may lose nuance
- **Citation hallucination risk:** Stage 4 prompt now explicitly prohibits fabricating document citations (e.g. [RRA 2022] when no RRA was uploaded). If the Stage 4 prompt is modified, ensure this guard is preserved.
- **Research cache is in-process:** Web research results are cached in memory per "country::sector" key; cache is lost on server restart. Repeat runs with same country+sector pair use cached results.
- **Accessibility:** Some frontend components could be more accessible (ARIA labels, keyboard navigation)
- **Mobile:** UI is desktop-optimized; mobile experience is limited

### 10.2 Potential Improvements
- **Backend session database:** Store conversation history in a database (PostgreSQL, Firebase) for team collaboration and audit trails
- **Document caching:** Cache extracted/summarized documents to avoid re-processing on repeat runs
- **Priority versioning:** Track changes to priorities across refinement rounds
- **Collaborative mode:** Multiple users review the same analysis in real-time
- **Export formats:** Generate Word/PDF reports for formal sharing
- **Custom FCV frameworks:** Allow users to define their own FCV dimensions or assessment model
- **Integration with World Bank systems:** Connect to project databases, risk dashboards, etc.

---

## 11. Helpful Context & Design Decisions

### 11.1 Why Claude Sonnet 4?
- Strong reasoning for FCV analysis (structured assessment, evidence weighting)
- Fast enough for iterative refinement (vs. Opus)
- Efficient cost (vs. Haiku, which would struggle with nuanced FCV reasoning)
- **Current version:** `claude-sonnet-4-20250514` (latest available model with strong analytical capabilities)

### 11.2 Why Flask (Not React/Next.js)?
- Lightweight and quick to deploy
- Direct LLM integration on backend (easier to manage API keys, prompts, context)
- Frontend is mostly vanilla JS, so framework overhead not necessary
- Easy to host on Render or similar

### 11.3 Why SSE Streaming (Not Polling)?
- Real-time feedback to user (progressive rendering)
- Simpler UX (no "thinking..." spinners)
- Efficient (no repeated polling)

### 11.4 Why localStorage for Sessions (Current Implementation)?
- Quick to implement
- No backend database needed
- Works offline
- **Trade-off:** Not suitable for long-term storage or team collaboration (see Limitations section)

### 11.5 Why Do We Parse Priorities via Delimiters?
- Reliable extraction from unstructured LLM output
- Fallback to positional parsing if delimiters fail
- Allows the LLM to generate prose around priorities (preamble, discussion) without breaking parsing
- JSON structure inside delimiters is easy to extend (add/remove priority fields)

---

## 12. Testing & Quality Assurance

### 12.1 How to Test the App

**Manual testing workflow:**
1. Upload a test project document (e.g., a PAD from GitHub or Ghana example)
2. Add a contextual document (e.g., a recent RRA or country risk assessment)
3. Run through all 4 stages, checking:
   - Stage 1 Part A extracts correctly from the project doc
   - Stage 1 Part B references contextual docs and training knowledge separately
   - Stage 2 ratings are reasonable for the project
   - Stage 3 gaps are specific and actionable (not vague)
   - Stage 4 priorities are concrete with geographic callouts
   - Explorer options are operationally grounded
4. Try the refine loop at each stage to ensure edits feed into next stage
5. Test the Explorer deep-dive for 1–2 priorities

**Prompt quality checks:**
- Are recommendations specific (geography, mechanism, entry points) or vague?
- Do they reference the WBG framework (FCV dimensions, Do No Harm)?
- Are they evidence-based (grounded in uploaded docs) or speculative?
- Are multiple options offered or a single "solution" prescribed?

### 12.2 Red-Teaming the Prompts
Ask Claude (in a separate conversation) to critique the Stage 4 output:
- Are the recommended priorities the most important ones?
- Are any dimensions under/overweighted?
- Do the recommendations align with the evidence presented?
- Would a TTL find these actionable?

---

## 13. Questions to Ask Before Making Changes

Before modifying prompts, frontend, or backend logic, ask yourself:

1. **What problem does this solve?** Is it addressing a real user pain point or a hypothetical issue?
2. **How does this affect the other stages?** If I change Stage 2 output, do Stages 3 & 4 prompts need updating?
3. **Does this add complexity without clear benefit?** Could a simpler approach work?
4. **How do I test this?** What does a "good" outcome look like?
5. **Is this a one-time fix or a recurring need?** If recurring, should it be in the prompt or the frontend?
6. **Who is the user?** Is this for TTLs, FCV specialists, or both? Does the change serve their workflow?
7. **What's the trade-off?** Does this improve output quality at the cost of longer processing time? Is that acceptable?

---

## 14. Conversation Starters for Claude

When you return with a new issue or request, here are useful framing questions:

- **"How do I improve the specificity of Stage 4 recommendations?"**
  → Share an example of a vague recommendation and ask Claude to help rewrite the Stage 4 prompt to enforce specificity.

- **"The Explorer options are too long / too short."**
  → Adjust the Explorer prompt's length instructions or add formatting requirements (bullet points, numbered steps, etc.).

- **"I want to test the app with a different FCV framework (e.g., the ICRC framework instead of WBG)."**
  → Provide the alternative framework and ask Claude to rewrite Stage 2 & 3 prompts to use it.

- **"Can we improve the Do-No-Harm checklist?"**
  → Share the current checklist and ask Claude to propose new principles or reorganization, then update Stage 3 prompt.

- **"The app should export a Word document / PDF report."**
  → Specify what should be in the report (which sections from which stages) and ask Claude to add export functionality.

- **"I want to add collaborative review mode."**
  → Describe the workflow (multiple users commenting on priorities, etc.) and ask Claude to design the backend/frontend changes.

---

## 15. File Structure & Repository Organization

```
FCV-AGENT/
├── app.py                    # Flask backend + all prompts + routes
├── index.html                # Main frontend UI (single-page app, ~4000 lines)
├── background_docs.py        # FCV_GUIDE and FCV_OPERATIONAL_MANUAL constants
├── prompts.json              # Session-specific prompt overrides (empty by default)
├── requirements.txt          # Python dependencies (Flask, anthropic, pypdf, python-docx)
├── Procfile                  # Render deployment config
├── .gitignore               # Git ignore rules
├── claude.md                 # THIS FILE - guidance for Claude
├── static/                  # Static assets (if any)
├── .git/                    # Git repository metadata
└── README.md                # (optional) Quick start guide for users
```

---

## 16. Quick Reference: Key Constants & Limits

```python
MAX_DOC_CHARS = 500_000              # Docs larger than this get LLM summarization
EXTRACT_THRESHOLD = 150_000          # Docs larger than this are condensed via LLM before analysis
ADMIN_PASSWORD = "fcv-admin-2024"    # Password for prompt admin modal (from env var ADMIN_PASSWORD)
PROMPTS_FILE = 'prompts.json'        # Location of session-specific prompt overrides
```

---

## 17. Getting Help & Debugging

### Common Issues

**"The app hangs on Stage 1 with a large PDF"**
- The LLM is likely summarizing the document (expected, can take 30–60 seconds)
- Check browser console for errors; if none, wait longer
- If it truly hangs, check that `MAX_DOC_CHARS` isn't too large

**"Stage 2 ratings seem off"**
- Ask Claude: "Here's a project in [country]. The Stage 2 prompt gave [rating]. Does this make sense?"
- Refine Stage 2 via the Admin modal and re-run that stage

**"Explorer options aren't specific enough"**
- The Explorer prompt needs to be more prescriptive about geographic naming and mechanisms
- Update the Explorer prompt and re-run a priority

**"Do No Harm checklist isn't showing up in Stage 4"**
- Check that Stage 3 generated a `## Part C` section with a Markdown table
- If the table format is slightly different, the regex in `index.html` may not match; ask Claude to help fix the parsing

### How to Debug

1. **Check the browser console** (F12 → Console tab) for JavaScript errors
2. **Check the Flask server logs** for backend errors (should print to stdout in Render dashboard)
3. **Use the prompt admin modal** to see exactly what prompt was used for a stage
4. **Copy the LLM output** and share it with Claude, asking: "Why might this recommendation be vague/inaccurate?"

---

## 18. Credits & Context

This tool was developed iteratively based on feedback from World Bank FCV practitioners (particularly Shubham's note on specificity and actionability). The key insight — that recommendations must move from broad critique ("service delivery needs to be targeted") to specific, location-aware guidance ("focus on Nzerekore, Kindia, Kankan where state legitimacy is lowest") — is central to the design.

The 4-stage pipeline was chosen to balance:
- **Quality:** Each stage allows refinement + user input
- **Usability:** Not overwhelming; lets TTLs pause and review
- **Efficiency:** Not redundant; earlier stages feed directly into later ones

The Explorer feature was added to solve the "length vs. depth" problem: keep the main Recommendations Note clean and memo-ready, but offer deep analytical options on demand.

---

## 19. Final Note

This `claude.md` is a living document. As you make changes, iterate on features, and learn what works, please update it. The goal is that any developer (including Claude in future conversations) should be able to:
1. Understand the app's architecture in 30 minutes
2. Identify where to make a requested change
3. Know the consequences of that change
4. Test the change effectively

If you find gaps in this documentation, or if new design decisions emerge, update this file. Future you (and future Claude) will thank you.

---

**Last updated:** March 11, 2026
**Current version:** FCV Project Screener 5.0 (with S/R distinction, dual gauges, embedded doc type detection)
**Current Claude model:** claude-sonnet-4-20250514
**Architecture:** Flask 3.0.3 backend + vanilla JS frontend + Anthropic SDK integration
