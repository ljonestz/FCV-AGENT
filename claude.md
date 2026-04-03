# FCV Project Screening App — Claude Development Guide

> **Claude Code Maintenance Instruction:** After every substantial change to this app (new features, prompt changes, new delimiters, UI additions, architectural decisions), update this `claude.md` file to reflect the change before committing. Keep section 1.3 (Stage pipeline), section 3 (Prompt Architecture), section 4 (Frontend), and section 5.3 (Priority Parsing) accurate at all times.
>
> **Version note:** This file was updated for v7.5 (UX polish). If sections reference "Stage 4" or "Explorer" without qualification, that is legacy content from v6.0 — check whether it has been superseded.

---

## Overview

This is a **World Bank FCV (Fragility, Conflict, and Violence) Project Screener** — a Flask-based web application that guides Task Team Leaders (TTLs) through a **3-stage workflow** to assess how well a World Bank project integrates FCV considerations, and to generate targeted, actionable recommendations for improving its design and delivery.

**v7.0 redesign:** The app was redesigned from 4 stages to 3 stages, driven by feedback from FCV practitioners and integration of the full OST Manual, the FCV Playbook, and the January 2026 FCV Refresh Strategy. Old Stage 2 (Screening) and Stage 3 (Gaps) are merged into a single FCV Assessment stage. The Recommendations Note (formerly Stage 4) becomes Stage 3.

The tool explicitly distinguishes two concepts:
- **FCV Sensitivity [S]** — Is the project *aware of and designed for* the FCV context? Contextual awareness, conflict-informed design, Do No Harm, FCV-adapted operations. Shorthand: does this help the project avoid making things worse?
- **FCV Responsiveness [R]** — Does the project *actively work to change* the FCV situation? Root-cause engagement, resilience building, transformative use of FCV tools, peace & stability dividends. Shorthand: does this actively help make fragility dynamics better?

The 4 FCV Strategy Shifts (Anticipate / Differentiate / Jobs & Private Sector / Enhanced Toolkit) are **cross-cutting** — they apply to both sensitivity and responsiveness findings and are tagged inline as "FCV Strategy Shift: X".

Every prompt output tags recommendations, mitigations, and priorities as [S], [R], or [S+R]. These are assigned dynamically per-finding based on how the project implements each measure — not pre-assigned per recommendation. S/R definitions are shown to the user in a "Key Definitions" box at the top of Stage 2 output and on the landing page. Stage 3 shows the tag legend only (no full definition box).

**Key goal:** Move from broad, vague recommendations ("service delivery needs to be targeted so it doesn't contribute to grievance") to specific, location-aware, operationally grounded, stage-aware suggestions ("historically, Nzerekore, Kindia, and Kankan have been excluded from service delivery; focus on these regions to rebuild state-society relationships — action required before PAD appraisal").

**New in v7.0:**
- Full 12 OST recommendations + 25 key questions drive Stage 2 internally (up from 6 recs)
- FCV Playbook integration for stage-aware recommendations (PCN vs. PAD vs. implementation)
- "Under the Hood" expandable panels in Stage 2 for FCV Country Coordinators (plain-language titles referencing OST Manual)
- Do No Harm shown as traffic-light after thematic analysis (8 canonical principles), before synthesis
- `refresh_shift` field added to each priority card (maps to 1 of 4 FCV Strategy Shifts)
- Expanded `who_acts`, `when`, and `resources` fields with defined value sets

**New in v7.2 (Stage 2 restructure):**
- Stage 2 output restructured from fixed Sensitivity→DNH→Responsiveness→Gaps to **dynamic thematic narrative** (3–5 themes derived from project)
- S/R tags dynamically assigned per-finding (not pre-assigned per-rec); shifts cross-cutting (not boxed under responsiveness)
- DNH repositioned after themes, before synthesis
- Under the Hood panels renamed to plain-language questions with OST Manual subtitles; Panel 1 gains S/R Tag column
- S/R definition box shown at top of Stage 2 (with tag legend); removed from Stage 3 in v7.5
- S/R definitions added to landing page hero section
- Stage 3 `recommendation` replaced by structured `actions` array — each action has `document_element`, `guidance` (2–4 sentences), and `suggested_language` (2–3 sentences of ready-to-paste PAD text). Rendered as individual action cards with "Suggested text:" label. "Where in the PAD" chips removed (action titles already identify document elements).
- Stage 3 no longer includes inline `[From: ...]` citation tags — clean peer-review memo
- "Go Deeper" reduced to 2 tabs: "Evidence trail" (instant, default) + "Link to FCV Playbook" (LLM call). "Other options" (alternatives) tab removed
- Deeper Playbook prompt rewritten to focus on Playbook quotes, operational tools, WBG teams/resources, and policy hooks

**New in v7.5 (UX polish):**
- File upload zones restyled with custom "Browse files" buttons (no raw browser file input)
- Mode card badges: Express shows "DEFAULT" only; Step-by-Step has no badge (was "RECOMMENDED")
- Hero text condensed from 3 sentences to 2
- Session bar hides "No active session" text on initial load; shows session info only when meaningful
- Express progress: smart time estimate (updates message after 5 min / 7 min overruns)
- Express progress: 12 rotating messages (was 7) — mix of casual and informative
- Express progress: bottom note shortened to "Do not close or refresh this tab."
- Stage 3 instruction callout condensed to single title line (removed verbose "What you are reading" body)
- S/R definition box removed from Stage 3 output (kept at Stage 2 only)
- "view prompt" link removed from stage headings (accessible via "View / Edit Prompts" in session bar)
- Priority stepper text bumped from 9px to 10px with 3-line clamp and ellipsis
- Workflow section label spacing adjusted (padding-left: 6px)

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
app.py                 # Flask backend, all 3 stage prompts + deeper/followon prompts, routes, document processing
index.html             # Frontend UI, Stage 1-3 display, Go Deeper panel, prompt modal;
                       #   also contains express mode UI: mode-selection cards, progress screen,
                       #   runExpress(), retryExpressStage(), resumeExpressRun(), post-express
                       #   stepper navigation, and session v2 persistence (analysisMode field)
background_docs.py     # 8 constants: FCV_GUIDE, FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK,
                       #   PLAYBOOK_DIAGNOSTICS, PLAYBOOK_PREPARATION, PLAYBOOK_IMPLEMENTATION,
                       #   PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP
prompts.json           # Session-specific prompt overrides (persisted per session)
requirements.txt       # Python dependencies (Flask, Anthropic SDK, pypdf, python-docx)
Procfile              # Render deployment config (gunicorn + gevent; see Section 8.2)
.gitignore            # Git ignore rules
static/               # Static assets (if any)
```

### 1.3 Three-Stage Pipeline

**Two workflow modes (v7.4):** The pipeline stages are identical in both modes — the difference is in how they are orchestrated.
- **Express Analysis** (default) — user uploads docs and clicks Begin; a single `/api/run-express` SSE endpoint runs all 3 stages in one connection with no user interaction needed mid-run. A progress screen shows a stepper, stage cards, elapsed timer, and rotating messages.
- **Step-by-Step** — existing interactive workflow, unchanged; each stage calls `/api/run-stage` individually and the user can refine before proceeding.

```
STAGE 1 — Context & Extraction
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
├─ Extraction guided by Playbook Diagnostics questions (RRA utilisation, compound risks, forced
│  displacement, CPSD context)
├─ FCV classification context from FCV Refresh (is this an FCS country? what trajectory?)
├─ Prompt includes: FCV_GUIDE, PLAYBOOK_DIAGNOSTICS, FCV_REFRESH_FRAMEWORK
└─ UI: Stage header + research brief dropdown (top) + main output card + refine input box
   Loading note: Stage 1 shows "may take 60–90 seconds" due to web research phase
   DOC_TYPE line is stripped from display text before rendering

STAGE 2 — FCV Assessment (merged Screening + Gaps)
├─ Input: Stage 1 output
├─ Internal analytical engine:
│  ├─ All 12 OST recommendations (up from 6 in v6.0)
│  ├─ 25 key questions
│  └─ 3 key elements
│  TTL does NOT see the framework structure — they see themed findings
├─ Output structure (v7.2 — dynamic thematic narrative):
│  ├─ S/R Definition Box (hardcoded frontend element, not LLM-generated)
│  ├─ Tag Legend ("Reading this assessment" — explains [S], [R], [S+R] and FCV Strategy Shift badges)
│  ├─ TTL-facing Assessment (400–500 words, dynamic thematic narrative):
│  │  ├─ 3–5 analytical themes (dynamic, derived from 12 recs + 25 questions for THIS project)
│  │  │  Each finding tagged [S]/[R]/[S+R] + "FCV Strategy Shift: X" inline
│  │  │  Themes can mix S and R findings — they are analytical groupings, not S/R buckets
│  │  ├─ Do No Harm traffic-light (after themes, before synthesis)
│  │  ├─ Synthesis: S paragraph (80–100 words) + R paragraph (80–100 words)
│  │  ├─ Ratings: Sensitivity + Responsiveness
│  │  └─ Key gaps: 3–5 most critical, tagged [S]/[R]/[S+R], prioritised
│  └─ Delimiter blocks (parsed by frontend, stripped from display):
│     ├─ %%%STAGE2_RATINGS_START/END%%% — JSON: {sensitivity_rating, responsiveness_rating}
│     └─ %%%UNDER_HOOD_START/END%%% containing:
│        ├─ %%%RECS_TABLE_START/END%%%    — 12-rec table (now with S/R Tag column, dynamically assigned)
│        ├─ %%%DNH_CHECKLIST_START/END%%% — 8-principle DNH checklist (traffic-light)
│        ├─ %%%QUESTIONS_MAP_START/END%%% — 25 key questions with findings
│        └─ %%%EVIDENCE_TRAIL_START/END%%% — Sources, types, contributions
├─ Do No Harm — canonical 8 principles (positioned after themes, before synthesis):
│  1. Conflict-sensitive targeting and beneficiary selection
│  2. Avoiding reinforcement of existing power asymmetries
│  3. Preventing exacerbation of inter-group tensions
│  4. Ensuring equitable geographic distribution of benefits
│  5. Safeguarding against elite capture of project resources
│  6. Protecting project staff and beneficiaries from security risks
│  7. Monitoring for unintended negative consequences
│  8. Establishing accessible and trusted grievance mechanisms
├─ FCV Strategy Shifts — 4 cross-cutting strategic directions (tagged inline on S and R findings):
│  ├─ FCV Strategy Shift A: Anticipate — risk monitoring, early warning, classification awareness
│  ├─ FCV Strategy Shift B: Differentiate — tailoring to FCV context type
│  ├─ FCV Strategy Shift C: Jobs & Private Sector — economic livelihoods, MSME, private sector
│  └─ FCV Strategy Shift D: Enhanced Toolkit — operational flexibilities, partnerships, adaptive management
├─ [S+R] strictly defined — only genuine overlap zones (unchanged from v6.0):
│  (1) inclusion/targeting of conflict-affected populations
│  (2) FCV logic embedded in ToC/PDO framing
│  (3) adaptive M&E that monitors harm AND adapts for resilience
│  (4) GRM designed to strengthen state-citizen accountability
├─ extract_stage2_ratings(): parses %%%STAGE2_RATINGS_START/END%%% → {sensitivity_rating, responsiveness_rating}
├─ extract_under_hood(): parses %%%UNDER_HOOD_START/END%%% → {recs_table, dnh_checklist, questions_map, evidence_trail}
│  └─ On failure: parse_error: true in SSE done event; raw text shown; banner displayed; Stage 3 can still proceed
├─ clean_stage2_output(): strips ratings + under_hood blocks from display text
├─ Under Hood text stored in localStorage key "stage2_under_hood" for use by Go Deeper Tab 2
├─ Prompt includes: FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK, FCV_GUIDE
└─ UI:
   ├─ Main output: Assessment Summary narrative
   ├─ Ratings sidebar: Sensitivity gauge (blue, shield) + Responsiveness gauge (green, leaf)
   │  — moved from old Stage 4 to Stage 2 in v7.0
   ├─ "Under the Hood" panels (4 expandable <details> with plain-language titles + OST Manual subtitles):
   │  ├─ Panel 1: "How well does the project integrate FCV considerations?" (12 operational standards from OST Manual, with S/R Tag column)
   │  ├─ Panel 2: "Could this project unintentionally cause harm?" (8 DNH principles from OST Manual)
   │  ├─ Panel 3: "What did we look for — and what was missing?" (25 diagnostic questions from OST Manual)
   │  └─ Panel 4: "Where did this analysis come from?" (sources, types, contributions)
   └─ Refine input box

STAGE 3 — Recommendations Note (stage-aware)
├─ Input: Stages 1–2 output (conversation history) + doc_type (from Stage 1) + uploaded_doc_names list
├─ Stage-awareness logic (doc_type passed in request body):
│  ├─ PCN/PID → PLAYBOOK_PREPARATION, timing: "Identification / Preparation"
│  ├─ PAD     → PLAYBOOK_PREPARATION, timing: "Preparation / Appraisal"
│  ├─ AF/Restructuring → PLAYBOOK_IMPLEMENTATION, timing: "Implementation / Restructuring"
│  ├─ ISR     → PLAYBOOK_IMPLEMENTATION + PLAYBOOK_CLOSING, timing: "Implementation"
│  └─ Unknown → PLAYBOOK_PREPARATION (safe default)
├─ Output (narrative memo + JSON block appended at end):
│  ├─ Narrative: Preamble + Opening Assessment + Operational Context + Risk Exposure +
│  │             Strengths + Gaps + Sensitivity Summary + Responsiveness Summary +
│  │             Stage badge (e.g., "Recommendations tailored for PCN stage")
│  └─ JSON block: delimited %%%JSON_START%%%...%%%JSON_END%%%
│     Top-level fields: fcv_rating, fcv_responsiveness_rating, sensitivity_summary,
│       responsiveness_summary, risk_exposure {risks_to, risks_from}, priorities[]
│     Each priority:
│       title, fcv_dimension, tag, refresh_shift (one of 4 FCV Refresh shifts),
│       risk_level, the_gap, why_it_matters,
│       actions[] (array of {document_element, guidance, suggested_language}),
│       who_acts (multi-value, semicolon-separated: TTL; PIU; Government; FCV CC;
│                 FM Team; ESF Team; Technical Team; M&E Team),
│       when (Identification | Preparation | Appraisal | Implementation | Restructuring),
│       resources (Minimal (existing budget) | Moderate (dedicated allocation) |
│                  Significant (requires restructuring)),
│       pad_sections (semicolon-separated), implementation_note
│     TAG: [S] / [R] / [S+R] — same strict definition as Stage 2
│     Most priorities will be [S] or [R]; [S+R] only for four named overlap zones
├─ extract_priorities() — same JSON-parse-based approach as v6.0, with updates:
│  ├─ Parses new refresh_shift field
│  ├─ Normalises actions[] array (new format); backwards-compat converts old recommendation string
│  ├─ Updated who_acts and when validation against new value sets
│  ├─ _check_specificity() validates across all action guidance text
│  └─ Returns unified dict with all fields + per-priority specificity_warning/citation_warnings
├─ clean_stage3_output() (renamed from clean_stage4_output()):
│  1. Strip %%%JSON_START/END%%% block
│  2. Strip %%%RISK_NARRATIVE_START/END%%% block
│  3. Strip everything from %%%PRIORITIES_START%%% onwards
│  4. Legacy delimiter stripping for cached outputs
├─ Citation policy (v7.2): Stage 3 NO LONGER includes inline [From: ...] citation tags.
│  The note reads as a clean peer-review memo. Sources may be mentioned naturally in prose
│  (e.g., "ACLED data suggests...") but not as bracketed citations. Never fabricate document titles.
├─ Prompt includes: stage-appropriate PLAYBOOK constant, FCV_REFRESH_FRAMEWORK
└─ UI:
   ├─ Main output card (preamble + opening assessment + operational context)
   │  NOTE: Risk Exposure stripped → shown as card from JSON
   │  NOTE: S/R summaries stripped → shown as side-by-side cards from JSON
   ├─ FCV Sensitivity + FCV Responsiveness summary cards (side by side, after Gaps)
   ├─ Priority cards (horizontal stepper, shows one at a time)
   ├─ Per-priority zone-act layout (from JSON — always available):
   │  ├─ refresh_shift badge (e.g., "FCV Strategy Shift B: Differentiate")
   │  ├─ Essential actions — loop over actions[] array, each rendered as:
   │  │  ├─ Document element title (bold, blue — e.g. "ESCP Commitment (new)")
   │  │  ├─ Guidance text (2–4 sentences)
   │  │  └─ "Suggested text:" + draft PAD language (italic, yellow card with gold border)
   │  ├─ "Where in the PAD" chips removed (action titles serve this purpose)
   │  └─ Implementation consideration (implementation_note)
   ├─ S/R tag badges with hover tooltips (unchanged)
   ├─ Specificity + citation warning badges (unchanged)
   ├─ "Go Deeper" collapsible <details> per priority (2 tabs, v7.2):
   │  ├─ 2 tab buttons: "Evidence trail" (default) | "Link to FCV Playbook"
   │  ├─ Tab 1 (Evidence trail): DEFAULT on open. NO LLM call — filters stage2_under_hood
   │  │  from localStorage by priority keywords (fcv_dimension + title words); renders instantly
   │  └─ Tab 2 (FCV Playbook): SSE-streamed LLM call via /api/run-deeper (tab="playbook_refs")
   │     Prompt: DEFAULT_PROMPTS["deeper_playbook"] — Playbook quotes, tools, WBG teams, policy hooks
   │  NOTE: "Other options" (alternatives) tab removed in v7.2 — was rarely useful
   ├─ Go Deeper tabs cached per priority per tab (keys: deeper_{idx}_trail, deeper_{idx}_playbook)
   └─ Parse error banner shown if JSON extraction fails

FOLLOW-ON (post-analysis query card — Stage 3 only)
├─ Replaces the standard "Refine this output" card at Stage 3 bottom
├─ Stages 1–2 still show the standard refine card (calls doRefine() → re-runs stage)
├─ Input: Full conversationHistory + user message
├─ Output: SSE-streamed response appended below the follow-on card (does NOT replace Stage 3 output)
├─ 4 pre-fill chips for common TTL tasks:
│  - "Draft peer review note" → drafts a peer review email/comment for the PCN/PAD
│  - "Expand top recommendation" → first steps, who leads, TTL actions in first 30 days
│  - "Review my revised text" → user pastes revised PAD text; LLM reviews against FCV analysis
│  - "Summarise for brief" → plain-language summary for 5-minute brief or management presentation
├─ Clicking a chip pre-fills the textarea via prefillFollowon(text)
├─ Submit calls doFollowOn() → POST /api/run-followon
├─ Result rendered in .followon-result-card below the card; header updates on completion
├─ Key JS functions: prefillFollowon(text), doFollowOn(), buildFollowOnMessages(userMsg)
├─ CSS: .followon-card, .followon-desc, .followon-chips, .followon-chip, .followon-result-card
└─ Backend: /api/run-followon route, DEFAULT_PROMPTS["followon"], max_tokens=4000
   - Prompt includes full WBG peer review style guidelines
   - Route truncates large assistant messages to 40,000 chars before sending to avoid token limits

GO DEEPER (optional depth panel — Stage 3 only; replaces Explorer from v6.0)
├─ Input: Priority JSON (title + body) + doc_type + history + stage2_under_hood (for Tab 2)
├─ 3 tabs, lazy-loaded via <details class="go-deeper"> toggle:
│  Tab 1 — Other options (DEFAULT active on open):
│    ├─ SSE-streamed LLM call via POST /api/run-deeper {tab: "alternatives"}
│    ├─ Prompt: DEFAULT_PROMPTS["deeper"] — 2–3 optional alternative approaches
│    └─ Output format: %%%GO_FURTHER_START%%%...%%%GO_FURTHER_END%%% with %%%GF_ITEM%%% blocks
│  Tab 2 — Why this recommendation (NO API CALL):
│    ├─ Data sourced from localStorage key "stage2_under_hood" (saved after Stage 2 completes)
│    ├─ Backend filters recs_table and questions_map rows matching priority's fcv_dimension
│    └─ Renders instantly — no spinner; user sees OST evidence driving this priority
│  Tab 3 — WBG policy guidance:
│    ├─ SSE-streamed LLM call via POST /api/run-deeper {tab: "playbook_refs"}
│    ├─ Prompt: DEFAULT_PROMPTS["deeper_playbook"] + stage-appropriate Playbook constant
│    └─ Returns relevant operational flexibilities, policy citations, implementation guidance
├─ Cache keys: deeper_{idx}_alternatives, deeper_{idx}_trail, deeper_{idx}_playbook
├─ Cancel button aborts in-flight SSE calls for Tabs 1 and 3 (Tab 2 has no call to cancel)
└─ Design principle: core recommendation is self-contained in JSON; Go Deeper adds
   optional analytical depth — NOT required reading before downloading
```

---

## 2. Design Decisions & Design Philosophy

### 2.1 Why 3 Stages (Not 4 or 1)?
- **Sequential refinement:** Each stage builds on prior outputs, allowing users to pause, review, and refine before proceeding.
- **Quality control:** Users see intermediate reasoning and can correct errors or add local knowledge at each step, rather than getting an opaque final output.
- **Cognitive load:** Breaking analysis into digestible pieces helps TTLs understand the reasoning without overwhelming them.
- **Fewer redundant stages:** Old Stages 2 (Screening) and 3 (Gaps) overlapped — the same weaknesses were being identified twice. Merging them into a single Assessment stage eliminates duplication and gives TTLs a cleaner, faster workflow.
- **Flexibility:** Users can re-run Stage 2 without re-analyzing documents, adjust findings before generating final recommendations, etc.

### 2.2 Why Stage 1 Splits Part A from Part B?
- **Transparency:** Users need to understand what the tool extracted *directly* from their project document vs. what it inferred from external context or AI training knowledge.
- **Document trust:** A project document is a formal WBG artifact; the tool respects its primacy while being clear about supplementation.
- **Accuracy accountability:** If something in Part A seems wrong, the issue is in extraction; if Part B is off, it's in contextual interpretation or knowledge gaps.

### 2.3 Why "Go Deeper" (2-tab panel)?
**Problem with old Explorer:** It only offered alternative approaches. FCV Country Coordinators wanted to see the analytical reasoning behind a recommendation (which OST recs drove it?) and the Playbook guidance relevant to their project stage.

**Solution (v7.2):** Replace Explorer with a **2-tab "Go Deeper" panel** that:
- **Tab 1 (Evidence trail):** DEFAULT on open. Which OST recs and key questions from Stage 2 drove this priority — sourced from `localStorage.stage2_under_hood` with **no API call** (renders instantly)
- **Tab 2 (Link to FCV Playbook):** FCV Playbook quotes, operational tools and flexibilities, WBG teams/resources the TTL can access, and applicable policy hooks — lightweight LLM call

The "Other options" (alternatives) tab was removed in v7.2 — user testing showed it was rarely used and added cognitive load without clear value.

**Key architectural innovation:** Tab 1 uses data already collected in Stage 2. No extra API call, no latency. The `stage2_under_hood` block is stored in localStorage after Stage 2 completes and read by Go Deeper on demand.

**Result:** Core recommendation is self-contained in JSON. Go Deeper adds optional analytical depth. Download never requires clicking through tabs.

### 2.3a Why Each Priority Uses Bulleted Document Guidance
**Principle (updated v7.2):** Non-specialist TTLs need clear guidance on what to revise in their project document.

Each priority card is structured around document-level changes from the Stage 3 JSON:
- `actions[]` — array of 2–4 objects, each with:
  - `document_element` — specific PAD section/component to revise (serves as the action title)
  - `guidance` — 2–4 sentences describing what to add/revise and why
  - `suggested_language` — 2–3 sentences of ready-to-paste draft PAD text (labelled "Suggested text:")
- `pad_sections` — retained in JSON as metadata (no longer displayed as standalone chips)
- `implementation_note` — timing/cost/dependency note (1–2 sentences)
- `refresh_shift` — which FCV Refresh shift this priority addresses

Go Deeper demoted to a collapsed section — lazy-loaded only if the user opens it, explicitly labelled Optional.

**Key architectural consequence:** All core content lives in Stage 3 JSON. `downloadReport()` never requires clicking through Go Deeper tabs — it always has everything it needs.

### 2.4 The Specificity & Actionability Mandate
**Core principle:** Recommendations must be **specific and actionable**, not broad and vague.

- **Bad:** "Service delivery needs to be targeted so it doesn't contribute to grievance"
- **Good:** "Historically, Nzerekore, Kindia, and Kankan have been excluded from service delivery. To rebuild the state-society relationship, focus service delivery in these regions, prioritizing (a) areas with highest grievance sensitivity, (b) community health extension worker networks, (c) cash-for-work entry points."

**How it's enforced:**
- Stage 2 prompt uses the full 12-rec OST Manual + 25 key questions — no longer limited to 6 recs
- Stage 3 prompt explicitly requires geographic naming, mechanism specification, and operational entry points (PAD instruments, existing WBG programs, partner organizations)
- Stage 3 prompt is stage-aware: PCN projects get "build into the ToC now" framing; PAD projects get "revise Section X" framing; implementation-stage get "adjust during next restructuring" framing
- Stage 3 generates `actions[]` (per-action document_element + guidance + suggested_language), `pad_sections`, `implementation_note`, and `refresh_shift` per priority — all in JSON
- Go Deeper "alternatives" tab generates 2–3 optional alternative approaches; core actions are always the primary directive

**Trade-off managed:** We avoid exact costs (which change) but include enough detail for a TTL to brief management or co-design with counterparts.

### 2.5 Session Persistence & Conversation History
- All user inputs and LLM outputs are stored in browser localStorage (serialized as JSON)
- On page reload, the app can recover the session and allow "continue" or "restart" workflows
- Sessions can be saved with a name, allowing users to return to previous analyses
- Conversation history is passed to each stage, so the LLM maintains context across all 3 stages

**Limitation:** localStorage is browser-specific and not suitable for long-term storage or team collaboration. For future versions, consider a backend database.

---

## 3. Prompt Architecture

### 3.1 Where Prompts Live

**Default prompts:**
```python
# In app.py, top-level DEFAULT_PROMPTS dictionary
DEFAULT_PROMPTS = {
    "1": "# Role\nYou are an expert FCV analyst...",          # Stage 1: Context & Extraction
    "2": "# Role\nYou are an expert FCV analyst...",          # Stage 2: FCV Assessment (dynamic thematic narrative)
    "3": "# Role\nYou are an expert FCV analyst...",          # Stage 3: Recommendations Note (no inline citations, bulleted recs)
    "deeper": "# Role\nYou are an FCV specialist...",         # (Legacy — alternatives tab removed in v7.2, prompt retained for backwards compat)
    "deeper_playbook": "# Role\nYou are an FCV...",           # Go Deeper Tab 2: Link to FCV Playbook
    "followon": "# Role\nYou are a senior FCV specialist..."  # Follow-on post-analysis tasks
}
# Note: Go Deeper Tab 1 (Evidence trail) has NO prompt — it is a frontend-only data filter from localStorage
```

**Session-specific overrides:**
- Stored in `prompts.json` (in project root)
- Loaded via `load_prompts()` function, which merges with DEFAULT_PROMPTS
- Saved via `save_prompts()` function when user edits via Admin modal
- Scoped to current session only (not persisted across sessions)

**How to override:**
- Via UI: Admin tab → per-stage prompt editor → Save & Close
- Via code: Edit DEFAULT_PROMPTS in app.py (persists globally across all sessions)

### 3.2 Stage 1: "Context & Extraction"

**Purpose:** Extract FCV-relevant content from uploaded project and contextual documents, enriched by automated web research and Playbook Diagnostics framing.

**Input:** Any project document at any preparation stage (Concept Note, PID, PCN, PAD, restructuring/AF draft). Optionally 1–2 contextual documents (RRA, country risk report, etc.).

**Automated FCV web research phase (runs before LLM generation):**
1. `extract_country_name()` — brief LLM call to identify project country (first 4000 chars)
2. `extract_sector_name()` — brief LLM call to identify primary project sector
3. `run_fcv_web_research(country, sector)` — Anthropic web_search tool, 9 targeted searches, up to 5500 tokens
   - Covers: conflict/security, governance, humanitarian, economic, FCV actors, structural drivers, vulnerable groups, regional dimensions, sector-specific FCV considerations
   - Results cached in-memory by `"country::sector"` key; lost on server restart
4. Research brief injected into Stage 1 context as supplemental material
5. Research brief shown as collapsible dropdown at TOP of Stage 1 output

**Three-tier citation priority:**
- Tier 1 — Uploaded contextual docs: `[From: document name]` (highest precedence)
- Tier 2 — Automated web research: `[From: web research]` or named source (e.g. `[From: ICG]`)
- Tier 3 — Training knowledge: `[From: training knowledge]` or named org/report

**Key behaviors:**
- Part A: Extract only from the project document. No outside knowledge.
- Part B: Use tiers 1→2→3 in strict priority order; always label the source tier at each point.
- Extraction guided by Playbook Diagnostics questions (RRA utilisation, compound risks, forced displacement, CPSD)
- FCV classification context from FCV Refresh injected (is this an FCS country? what trajectory?)

**Large document handling:**
- Documents > 150,000 characters are condensed via LLM extraction (FCV-relevant content only).
- Documents > 500,000 characters are truncated to MAX_DOC_CHARS.
- Truncation warnings shown to users when triggered.

**Document type classification (embedded in Stage 1):**
- The very last line of every Stage 1 response is: `%%%DOC_TYPE: [PCN/PID/PAD/AF/Restructuring/ISR/Unknown]%%%`
- The frontend extracts this via regex when Stage 1 completes and sets the `docType` state
- The DOC_TYPE line is stripped from the display text before rendering to the user
- `docType` is passed in the Stage 3 request body for stage-aware prompt injection

**Prompt constants injected:** `FCV_GUIDE`, `PLAYBOOK_DIAGNOSTICS`, `FCV_REFRESH_FRAMEWORK`

**Loading time note:** Stage 1 loading card shows "may take 60–90 seconds" due to web research phase.

**User refine loop:** After Stage 1 displays, users can correct misreadings, add local knowledge, or flag missing content before proceeding.

### 3.3 Stage 2: "FCV Assessment" (merged Screening + Gaps)

**Purpose:** Assess project FCV sensitivity and responsiveness using the full OST framework. Identify gaps and Do No Harm status. Produce both a TTL-facing thematic summary and detailed analytical record for FCV CCs.

**Internal analytical engine:** All 12 OST recommendations + 25 key questions + 3 key elements. The TTL sees themed findings only — the framework structure is in "Under the Hood" panels.

**TTL-facing output (400–500 words, thematic narrative):**
- FCV Sensitivity findings: what the project addresses well, where it falls short
- Do No Harm traffic-light inline (e.g., "6 of 8 principles addressed | 1 partial | 1 gap")
- FCV Responsiveness findings: framed around the 4 FCV Refresh shifts (not old pillars)
- Key gaps: 3–5 most critical, prioritised, with evidence

**Responsiveness assessment — 4 FCV Refresh shifts (replaces old pillar-by-pillar analysis):**
- Shift A: Anticipate — does the project design reflect current fragility classification?
- Shift B: Differentiate — is it calibrated to the country's FCV trajectory/context type?
- Shift C: Jobs & private sector — does it address economic livelihoods/job creation as a stability pathway?
- Shift D: Enhanced toolkit — does it leverage operational flexibilities (OP7.30, TPIs, CERC, etc.)?

**Do No Harm — canonical 8 principles:**
1. Conflict-sensitive targeting and beneficiary selection
2. Avoiding reinforcement of existing power asymmetries
3. Preventing exacerbation of inter-group tensions
4. Ensuring equitable geographic distribution of benefits
5. Safeguarding against elite capture of project resources
6. Protecting project staff and beneficiaries from security risks
7. Monitoring for unintended negative consequences
8. Establishing accessible and trusted grievance mechanisms

**Strict [S+R] definition (unchanged from v6.0):**
[S+R] only valid for: (1) inclusion/targeting of conflict-affected populations; (2) FCV logic in ToC/PDO; (3) adaptive M&E for harm + resilience; (4) GRM for state-citizen accountability.
If in doubt → [S] or [R].

**"Under the Hood" panels (collapsed, expandable `<details>`):**
- Panel 1: Full 12-rec assessment (table: rec | status | evidence | gaps | shift alignment)
- Panel 2: Detailed DNH checklist (8 principles, traffic-light table with evidence)
- Panel 3: 25 key questions mapping (answerable/gaps, evidence for each)
- Panel 4: Evidence trail (sources used, citation tier, confidence level)

**Backend parsing functions for Stage 2:**
- `extract_stage2_ratings()` — parses `%%%STAGE2_RATINGS_START/END%%%` → `{sensitivity_rating, responsiveness_rating}`
- `extract_under_hood()` — parses `%%%UNDER_HOOD_START/END%%%` → `{recs_table, dnh_checklist, questions_map, evidence_trail}`
- `clean_stage2_output()` — strips ratings + under_hood delimiter blocks from display text

**Error handling:** If `extract_under_hood()` fails, `parse_error: true` in SSE done event; raw text shown; yellow banner displayed; Stage 3 can still proceed using conversation history.

**Prompt constants injected:** `FCV_OPERATIONAL_MANUAL`, `FCV_REFRESH_FRAMEWORK`, `FCV_GUIDE`

**User refine loop:** Users can correct findings or add local knowledge before proceeding to Stage 3.

### 3.4 Stage 3: "Recommendations Note" (stage-aware)

**Purpose:** Generate a formal, memo-ready Recommendations Note with actionable priority cards, tailored to the project's lifecycle stage using Playbook guidance.

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
  - refresh_shift: Shift A: Anticipate | Shift B: Differentiate | Shift C: Jobs & private sector | Shift D: Enhanced toolkit
  - risk_level: High | Medium | Low
  - the_gap: 2–3 sentences
  - why_it_matters: 2–3 sentences (operational + FCV dimensions combined)
                    + shift justification for [R] and [S+R] priorities
  - actions: array of 2–4 objects, each with document_element, guidance (2–4 sentences),
             and suggested_language (2–3 sentences of ready-to-paste PAD text)
  - who_acts: TTL; PIU; Government; FCV CC; FM Team; ESF Team; Technical Team; M&E Team
              (multi-value, semicolon-separated; expanded from v6.0)
  - when: Identification | Preparation | Appraisal | Implementation | Restructuring
          (expanded from v6.0 — more granular lifecycle stages)
  - resources: Minimal (existing budget) | Moderate (dedicated allocation) | Significant (requires restructuring)
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
      "refresh_shift": "Shift B: Differentiate",
      "risk_level": "High",
      "the_gap": "...",
      "why_it_matters": "...",
      "actions": [
        {
          "document_element": "ESCP Commitment (new)",
          "guidance": "2–4 sentences describing what to add/revise and why",
          "suggested_language": "2–3 sentences of ready-to-paste draft PAD text"
        }
      ],
      "who_acts": "TTL; PIU",
      "when": "Preparation",
      "resources": "Moderate (dedicated allocation)",
      "pad_sections": "Annex 5: Stakeholder Engagement Plan; ESCP Commitment #4",
      "implementation_note": "1–2 sentences on timing, cost, or key dependency"
    }
  ]
}
%%%JSON_END%%%
```

**Critical: `actions` array (replaces old `recommendation` field):**
- 2–4 structured actions per priority, each naming a specific document element to revise
- Each action has `guidance` (2–4 sentences) and `suggested_language` (2–3 sentences of ready-to-paste text)
- Must NOT be an options menu ("Consider A / Or B / Or C" is NOT allowed)
- Must name specific location, mechanism, and entry point in guidance
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

**`clean_stage3_output()` stripping order (renamed from `clean_stage4_output()`):**
1. Strip `%%%JSON_START%%%...%%%JSON_END%%%` block (all structured data)
2. Strip `%%%RISK_NARRATIVE_START%%%...%%%RISK_NARRATIVE_END%%%` block (Risk Exposure prose — shown as card from JSON instead)
3. Strip everything from `%%%PRIORITIES_START%%%` onwards (S/R summaries + priorities — all shown as cards from JSON)
4. Fallback: strip legacy delimiter blocks for cached outputs:
   - `%%%RISK_EXPOSURE_START/END%%%`, `%%%SENSITIVITY_SUMMARY_START/END%%%`
   - `%%%RESPONSIVENESS_SUMMARY_START/END%%%`, `%%%FCV_RATING/RESPONSIVENESS_RATING%%%`
   - `%%%PRIORITY_START/END%%%` blocks, `%%%GAP_TABLE_START/END%%%`

**Stage 3 narrative display after stripping:**
Preamble → Opening Assessment → Operational Context → [Risk Exposure card from JSON] → Strengths → Gaps → [S/R summary cards from JSON] → [Priority stepper/cards from JSON]

**Citation policy for Stage 3:**
- ONLY cite documents that appeared as `[From: document name]` in Stage 1. NEVER fabricate titles.
- Non-uploaded sources → `[From: training knowledge]` or `[From: web research]`
- This prevents hallucinated citations (e.g., citing `[RRA 2022]` when no RRA was uploaded)
- `uploaded_doc_names` must be included in `/api/run-stage` request body for citation check

**Go Deeper "alternatives" tab output format:**
- Only `%%%GO_FURTHER_START%%%...%%%GO_FURTHER_END%%%` markers used
- Each item uses `%%%GF_ITEM%%%` + `%%%GF_TITLE%%%` markers
- Parsed by `parseGoFurtherText()` → `goFurtherItems[]`
- Rendered by `renderGoFurtherHtml(parsed)` into `.beyond-item` cards inside the tab content area

**Key behaviors:**
- Recommendations are specific and actionable, not broad policy suggestions
- Geographic locations are named (e.g., "In Oromia, prioritize...")
- `pad_sections` retained in JSON as metadata (no longer displayed as standalone chips — action titles identify document elements)
- Per-action `suggested_language` rendered with "Suggested text:" label in italic yellow card (`.zone-act-draft-text`)
- `implementation_note` rendered in grey bordered card (`.zone-act-impl`)
- `refresh_shift` badge shown on priority card header (e.g., "Shift B: Differentiate")
- A collegial tone appropriate for peer review by a TTL

**Do No Harm:** Not shown as standalone checklist in Stage 3. DNH traffic-light is inline in Stage 2's Assessment Summary. Detailed DNH checklist is in Stage 2's "Under the Hood" Panel 2.

---

## 4. Frontend Architecture

### 4.1 UI Panels
1. **Onboarding modal** — Disclaimer + warning about AI limitations, checkbox to suppress on future visits
2. **Session bar** — Floating bar showing current stage progress + save session button
3. **Stage progress stepper** — 3-step indicator: Context → Assessment → Recommendations
4. **Input panel (Stages 1–2)** — Upload box, document list, refine input
5. **Output panel (Stages 1–3)** — Displays LLM output + collapsible sections
6. **Under the Hood panels (Stage 2)** — 4 expandable `<details>` sections (12-rec table, DNH checklist, key questions, evidence trail)
7. **Ratings sidebar (Stage 2+)** — FCV Sensitivity gauge (blue, shield) + FCV Responsiveness gauge (green, leaf); shown from Stage 2 onwards (moved from old Stage 4)
8. **Go Deeper panel (Stage 3)** — Per-priority `<details class="go-deeper">` containing 3 tab buttons + content area
9. **Prompt modal** — Admin-only, lets users view/edit prompts (Stage 1, 2, 3, deeper, followon) per session
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

**Stage 3 priorities + Go Deeper:**
- `initStage3UI()` — parse priorities from JSON, build stepper, show Priority 1
- `showPriority(idx)` — render full priority card with zone-act layout from JSON (refresh_shift badge, actions[] loop with per-action guidance + suggested text, implementation note); no auto-load of Go Deeper
- `handleGoDeeper(el, idx)` — ontoggle handler for `<details class="go-deeper">`; initialises 3 tab buttons on first open
- `switchGoDeeperTab(idx, tabName)` — swaps active tab; loads content if not cached
  - `tabName: "alternatives"` → calls `loadDeeperAlternatives(idx)`
  - `tabName: "trail"` → calls `loadDeeperTrail(idx)` (no API call — filters localStorage)
  - `tabName: "playbook"` → calls `loadDeeperPlaybook(idx)`
- `loadDeeperAlternatives(idx)` — SSE call to `/api/run-deeper?tab=alternatives`; writes to `#deeper-content-{idx}`; caches in `deeper_{idx}_alternatives`
- `loadDeeperTrail(idx)` — no API call; reads `localStorage.stage2_under_hood`; filters by `priority.fcv_dimension`; renders matching OST recs/questions
- `loadDeeperPlaybook(idx)` — SSE call to `/api/run-deeper?tab=playbook_refs`; caches in `deeper_{idx}_playbook`
- `cancelGoDeeper()` — aborts in-flight SSE request via `goDeeperAbortController`
- `renderGoFurtherHtml(parsed)` — renders `parsed.goFurtherItems` as `.beyond-item` cards (alternatives tab)
- `renderPriorityStepper()` — build horizontal step indicator; compact S/R badge + refresh_shift below risk badge on each tab
- `renderPrioritiesIntro()` — renders intro list; compact S/R badge + refresh_shift after risk label in each `pi-item`

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

### 4.3 Removed Items (v7.0)
- **Stage 2 (Screening) as a separate stage** — merged into new Stage 2 (Assessment).
- **Stage 3 (Gaps) as a separate stage** — merged into new Stage 2 (Assessment).
- **Old Stage 4 numbering** — Recommendations Note is now Stage 3.
- **Old 4-pillar responsiveness framing** — replaced by 4 FCV Refresh shifts throughout.
- **Standalone Do No Harm Checklist** — folded into Stage 2 (traffic-light inline + Under the Hood Panel 2).
- **`/api/run-explorer` route** — replaced by `/api/run-deeper` (3 tabs).
- **`DEFAULT_PROMPTS["4"]` and `DEFAULT_PROMPTS["explorer"]` keys** — replaced by `"3"`, `"deeper"`, `"deeper_playbook"`.
- **Explorer `<details class="zone-act-beyond">` pattern** — replaced by Go Deeper `<details class="go-deeper">` with 3 tab buttons.
- **`loadExplorerForPriority()`, `handleBeyondToggle()`, `cancelExplorer()`** — replaced by `loadDeeperAlternatives()`, `loadDeeperPlaybook()`, `handleGoDeeper()`, `cancelGoDeeper()`.
- **`explorerAbortController`, `explorerCache`** — replaced by `goDeeperAbortController` + per-tab cache keys.
- **`beyond-timer-{idx}` / `beyond-loading-{idx}`** — replaced by Go Deeper tab-level loading spinners.
- **`renderAboveAndBeyondHtml()`** — renamed/replaced by `renderGoFurtherHtml()`.
- **FCV Sensitivity and Responsiveness gauges at Stage 4** — moved to Stage 2 (shown from Stage 2 onwards).
- **`clean_stage4_output()`** — renamed `clean_stage3_output()`.
- **`initStage4UI()`** — renamed `initStage3UI()`.
- **`pc-followup` inline "Ask →" input** — previously removed; remains dead code.

**Still present but renamed:**
- `DEFAULT_PROMPTS["3"]` (was `"4"`)
- `clean_stage3_output()` (was `clean_stage4_output()`)
- `initStage3UI()` (was `initStage4UI()`)

**Preserved (no change from v6.0):**
- Onboarding modal, session management, prompt admin modal (key names updated)
- SSE streaming for all LLM calls
- Conversation history passed between stages
- Styling, typography, WBG colour palette
- Priority card zone-act layout (actions[] loop, per-action suggested text, implementation note)
- `extract_priorities()` (updated to parse `actions[]`, `refresh_shift`, new `who_acts`/`when` values)
- S/R tag badges with hover tooltips
- Specificity + citation warning badges

### 4.3a Download Behaviour
- **`downloadReport()`** always includes all core priority content from JSON: `actions[]` (with per-action guidance + suggested_language), `refresh_shift`, `implementation_note`, `who_acts`, `when`, `resources`
- Does NOT require Go Deeper to have been opened — no click-through needed before downloading
- Optionally appends `goFurtherItems` (alternatives tab content) if Go Deeper was already opened for that priority
- `pad_sections` rendered as `<code>` chips in the Word export

### 4.4 Styling & Aesthetics
- **Color scheme:** WB Design System palette — wb-blue (#009FDA), wb-navy (#002244), wb-gray-900 (#111827), wb-gray-50 (#F7F8FA), wb-gray-100 (#EEF0F3), wb-gray-500 (#6B7280). RAG status: rag-red (#D73027), rag-amber (#FFFFBF), rag-green (#1A9850). See `memory/reference_wb_design_system.md` for full palette reference.
- **Stage colors:** 3 stage colors (s1 blue, s2 amber, s3 green) used in progress bars, section headers, and priority dimension badges
- **Typography:** Open Sans (WBG standard font, loaded from Google Fonts). Body 14px/400, section headings 15px/700, page titles 18px/700, labels 10px/600. No decorative typefaces.
- **Spacing:** 4px base unit; xs=4, sm=8, md=16, lg=24, xl=32, 2xl=48
- **Cards:** border-radius: 8px, box-shadow: 0 1px 3px rgba(0,0,0,0.08)
- **Icons:** Lucide SVG icons (used sparingly). Future: migrate to OCHA Humanitarian Icons per WB style guide.

### 4.5 Do No Harm Rendering (updated v7.0)
- DNH is no longer a standalone checklist in Stage 3.
- **Inline traffic-light** (Stage 2 Assessment Summary): e.g., "Do No Harm: 6 of 8 addressed | 1 partial | 1 gap"
- **Detailed checklist** (Stage 2 "Under the Hood" Panel 2): 8-principle table with traffic-light status + evidence, rendered from `%%%DNH_CHECKLIST_START/END%%%` delimiter block
- Rendered as HTML table with color-coded status badges (green/amber/red)
- Collapsible inside Under the Hood Panel 2 `<details>` section

### 4.6 Express Mode Architecture (v7.4)

**Dual-mode workflow:** Users choose between two modes on the landing page before starting analysis.

- **Express Analysis** (default): All 3 stages run automatically; user waits ~4–5 min on a progress screen; can review/re-run any stage after.
- **Step-by-Step** (recommended): Current interactive workflow — user reviews and refines at each stage before proceeding.

Both modes use identical prompts, code paths, and output quality. Express mode is a frontend orchestration change only — no backend modifications.

**State variable:** `let analysisMode = 'express'` (persisted to `localStorage.fcv_analysis_mode`). `selectMode(mode)` updates state + card UI.

**Mode selection UI:** Two side-by-side cards inside `.mode-section` div, placed between the notices and the "Begin FCV Analysis" button on the upload panel. CSS classes: `.mode-section`, `.mode-card`, `.mode-card.selected`, `.mode-radio`, `.mode-badge`.

**`runStage()` modification:** Gains an optional third parameter `onComplete(stage, parsedResult)`. When provided (by `runExpress()`), it is called instead of `renderOut()` after all data extraction is complete. Step-by-step mode passes `null` — behaviour is unchanged.

**`runExpress()`:**
1. Shows `#ep-accent` + `#express-progress` screen via `showExpressProgress()`
2. Calls `runStage(1, null, callback1)` where callback1 stores output, updates stepper, calls `runStage(2, null, callback2)`, and so on
3. After Stage 3 completes: hides progress screen, calls `renderOut(3, ...)`, calls `enableClickableStepper()`, cleans up express localStorage keys
4. On failure: `showExpressError(stage, msg)` shows red card with "Retry this stage" and "Switch to step-by-step" options

**Progress screen elements** (all inside `#express-progress`, hidden until express starts):
- `#ep-accent` — 4px gradient accent bar across top of viewport
- `.ep-stepper` — 3-node horizontal stepper with circle status, connectors
- `.ep-progress-bar` / `.ep-progress-fill` — 3px bar advancing 33%/66%/100%
- `.ep-stage-card` × 3 — status cards (pending/active/done) with 1-line summary after completion
- `.ep-timer` — "Elapsed: X:XX · Estimated total: 4–5 minutes" (auto-updates to "Taking a little longer than usual" after 5 min, "Almost done — finalising" after 7 min)
- `.ep-message-card` — rotating message card, cycles every 15s via `setInterval`; 12 messages in `EP_MESSAGES[]` (mix of casual and informative)

**Progress screen JS functions:**
- `showExpressProgress()` / `hideExpressProgress()` — show/hide screen, start/stop timer + message rotation intervals
- `updateEpTimer()` — increments elapsed seconds display every 1s
- `showEpMessage(idx)` — sets icon + text from `EP_MESSAGES`
- `updateExpressStage(stage, status, summary)` — updates stepper circle class, connector colours, progress bar fill, stage card state; `status` is `'pending'|'active'|'done'`
- `showExpressError(stage, errorMsg)` — red border on failed card, shows retry/switch buttons

**Post-express stage navigation:**
- `enableClickableStepper()` — adds `.stepper-clickable` class to stepper, adds hint text, adds `onclick` to step elements
- `disableClickableStepper()` — removes same
- `navigateToStage(stage)` — renders stored `stageOutputs[stage]` via `renderOut()`, adds re-run banner (Stages 1–2), adds arrow nav buttons
- `injectRerunBanner(stage)` — amber warning banner: "Want to refine this stage? Re-running will produce slightly different results and Stage 3 will need to be regenerated." + "Refine & Re-run" button
- `startRerun(stage)` — switches `analysisMode` to `'stepbystep'`, restores `stageHists[stage]`, invalidates subsequent `stageOutputs`, renders stage for re-run
- `injectStageNavArrows(stage)` — injects `← Stage N-1` / `Stage N+1 →` buttons below output for navigation between stored outputs

**`retryExpressStage(stage)`:** Re-runs failed stage and resumes chain if successful.

**`switchToStepByStep(stage)`:** Bails from express, renders last successfully completed stage in step-by-step mode, sets `analysisMode = 'stepbystep'`.

**Session persistence (v2 format):**
- `saveSession()` bumped to `version: 2`, now includes `analysisMode`, `stageOutputs`, `stageHists` fields
- `loadSession()` restores all three; missing `analysisMode` treated as `'stepbystep'` (backwards compat with v1)
- During express run, `stageOutputs` / `stageHists` written to `localStorage.fcv_express_stageOutputs` / `fcv_express_stageHists` after each stage completes
- Express resume IIFE runs on page load: if partial keys exist and Stage 3 is missing, shows amber "Resume or restart?" banner in upload panel with "Resume from Stage N+1" and "Discard & start fresh" buttons
- `resumeExpressRun()` / `discardExpressResume()` handle the two choices

---

## 5. Backend Routes & API

### 5.1 Main Routes

```python
# Core analysis route (all 3 stages)
POST /api/run-stage
  Input: {stage, documents[], history[], user_message, prompt_override,
          doc_type (Stage 3 only — for stage-aware prompt injection),
          uploaded_doc_names (Stage 3 only — for citation check)}
  Output: SSE stream with chunks, then:
    Stage 1: {done, output}
    Stage 2: {done, output, sensitivity_rating, responsiveness_rating,
              under_hood: {recs_table, dnh_checklist, questions_map, evidence_trail},
              parse_error, parse_error_message}
    Stage 3: {done, output, priorities[], fcv_rating, fcv_responsiveness_rating,
              sensitivity_summary, responsiveness_summary,
              risk_exposure: {risks_to, risks_from},
              parse_error, parse_error_message}

# Express mode route (single SSE endpoint for all 3 stages)
POST /api/run-express
  Input: {documents[]}
  Output: SSE stream with events:
    stage_start: {stage_start: N} — before each stage begins
    research_status: {research_status, country} — during Stage 1 web research
    preprocess: {preprocess: message} — during Stage 1 doc extraction
    chunk: {chunk: text, stage: N} — streaming LLM text for each stage
    stage_done: {stage_done: N, result, history, ...stage-specific data} — after each stage completes
    keepalive: {keepalive: true} — every 20s if no data sent
    error: {error: message, failed_stage: N} — if a stage fails
    express_done: {express_done: true} — all 3 stages completed
  Notes: Runs Stage 1→2→3 in a single SSE connection. Reuses all existing parsing
    functions. Keepalive pings cover web research gaps and inter-stage transitions.
    Frontend runExpress() connects to this endpoint and dispatches on event types.

# Go Deeper route (replaces /api/run-explorer)
POST /api/run-deeper
  Input: {priority_index, tab, priority_title, priority_body, history[],
          doc_type, stage2_under_hood (for analytical_trail tab only)}
  tab values: "alternatives" | "analytical_trail" | "playbook_refs"
  Output:
    alternatives/playbook_refs: SSE stream with chunks, then {done, output}
    analytical_trail: {done, output} — no SSE; filtered from stage2_under_hood immediately

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

# Follow-on post-analysis route (Stage 3 bottom card)
POST /api/run-followon
  Input: {messages[]} — full conversationHistory + user message
  Output: SSE stream (same chunk/done format as run-stage)
  System prompt: DEFAULT_PROMPTS["followon"] — WBG peer review style guidelines
  max_tokens: 4000 (higher than other routes to allow full peer review notes)
  Route truncates large assistant messages to 40,000 chars before sending
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

### 5.3 Priority Parsing (Stage 3 Output)

```python
def extract_priorities(stage3_output, uploaded_doc_names=None):
    # Finds %%%JSON_START%%%...%%%JSON_END%%% block, parses via json.loads()
    # Runs _check_specificity() and _check_citations() post-parse
    # Returns unified dict:
    #   {error, message?, priorities, fcv_rating, fcv_responsiveness_rating,
    #    sensitivity_summary, responsiveness_summary,
    #    risk_exposure: {risks_to, risks_from}}
    # Each priority dict has 13 core fields:
    #   title, fcv_dimension, tag, refresh_shift, risk_level,
    #   the_gap, why_it_matters, actions[] (array of {document_element, guidance, suggested_language}),
    #   who_acts, when, resources, pad_sections, implementation_note,
    #   + 2 post-parse fields: specificity_warning (bool), citation_warnings (list)
    # Updated who_acts validation: TTL | PIU | Government | FCV CC | FM Team | ESF Team | Technical Team | M&E Team
    # Updated when validation: Identification | Preparation | Appraisal | Implementation | Restructuring
    # On malformed JSON: returns {error: True, message: ...}
```

### 5.4 Stage 2 Output Parsing

```python
def extract_stage2_ratings(stage2_output):
    # Finds %%%STAGE2_RATINGS_START/END%%% block, parses JSON
    # Returns {sensitivity_rating: str, responsiveness_rating: str}

def extract_under_hood(stage2_output):
    # Finds %%%UNDER_HOOD_START/END%%% block
    # Extracts sub-blocks: recs_table, dnh_checklist, questions_map, evidence_trail
    # Returns {recs_table: str, dnh_checklist: str, questions_map: str, evidence_trail: str}
    # On failure: returns {error: True, message: ...}

def clean_stage2_output(stage2_output):
    # Strips %%%STAGE2_RATINGS_START/END%%% and %%%UNDER_HOOD_START/END%%% from display text
```

**Stage 3 SSE done event response:**
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

**Stage 2 SSE done event response:**
```json
{
  "sensitivity_rating": "Adequate",
  "responsiveness_rating": "Low",
  "under_hood": {
    "recs_table": "...",
    "dnh_checklist": "...",
    "questions_map": "...",
    "evidence_trail": "..."
  },
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
- Admin modal allows users to override any of the 5 default prompts (Stage 1, 2, 3, deeper, followon)
- Override is scoped to the current session only (not saved globally)
- Allows experimentation / customization per project

### 6.4 Under the Hood Panels (Stage 2)
- Stage 2 LLM outputs delimiter-wrapped blocks after the TTL summary
- `extract_under_hood()` parses `%%%UNDER_HOOD_START/END%%%` → 4 sub-blocks
- Each sub-block rendered in its own expandable `<details>` section
- Sub-block raw text stored in `localStorage.stage2_under_hood` after Stage 2 completes
- `stage2_under_hood` used by Go Deeper "Analytical trail" tab (Tab 2) — **no API call needed**
- If parsing fails, `parse_error: true` in SSE event; raw text shown with yellow banner; Stage 3 still proceeds

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

### 6.6 UX Safeguard Features (v7.0 updates)

**S/R tag tooltips:** `renderSRTagBadge()` adds `title` attribute to each tag badge explaining [S], [R], [S+R] in plain language. Hover-accessible. Unchanged.

**Refresh shift badge:** New in v7.0. Each priority card header shows a `refresh_shift` badge (e.g., "Shift B: Differentiate"). Renders from JSON. No tooltip required — shift name is self-explanatory.

**Specificity warning badge:** Shown on priority card if `priority.specificity_warning === true`. Amber, dismissible, stored per-priority in localStorage (`warn_spec_dismissed_{idx}`). Unchanged.

**Citation warning badge:** Shown on priority card if `priority.citation_warnings.length > 0`. Amber, dismissible, hover shows flagged citation strings. Stored in localStorage (`warn_cite_dismissed_{idx}`). Unchanged.

**Go Deeper lazy load + cancel:** SSE calls for "alternatives" and "playbook_refs" tabs use `AbortController`. Cancel button calls `cancelGoDeeper()`. Analytical trail tab (Tab 2) renders instantly — no spinner, no cancel button needed. Cache keys: `deeper_{idx}_alternatives`, `deeper_{idx}_trail`, `deeper_{idx}_playbook`. Cache cleared on Stage 3 re-run.

**Under the Hood parse error banner:** If `extract_under_hood()` fails on Stage 2 output, a yellow dismissible banner is shown at top of Stage 2 output. Raw text displayed as fallback. Stage 3 can still proceed.

**Font consistency:** `.pc-zone-body` (priority card body text) is 14px, matching `.out-body` (exec summary). Do not let these diverge — keep both at 14px.

**Stage consistency banner:** `renderOut()` injects a yellow dismissible banner at top of Stage 3 output if `stage2_timestamp > stage3_timestamp`. Timestamps written to localStorage BEFORE `renderOut()` call. Stage 2 re-run clears dismissed flags.

### 6.7 Priority Parsing and JSON Extraction
**In `extract_priorities(text, uploaded_doc_names=None)`:**
1. Search for `%%%JSON_START%%%` and `%%%JSON_END%%%` delimiters
2. Parse JSON block via `json.loads()` (no regex field extraction)
3. Validate new `refresh_shift` field (one of 4 shifts)
4. Validate updated `who_acts` multi-value field (semicolon-separated, expanded set)
5. Validate updated `when` field (Identification | Preparation | Appraisal | Implementation | Restructuring)
6. Run `_check_specificity()`: looks for mid-sentence capitalised words as proper-noun proxy
7. Run `_check_citations()`: cross-references `[From: ...]` patterns against uploaded doc names
   (extensions stripped) + known org whitelist; flags unrecognised sources
8. Return unified dict with all fields + per-priority `specificity_warning` / `citation_warnings`
9. On malformed JSON: return `{error: True, message: ...}` — NOT silent failure

**Stage 2 parsing in `extract_stage2_ratings()` and `extract_under_hood()`:**
1. `extract_stage2_ratings()`: finds `%%%STAGE2_RATINGS_START/END%%%`, parses compact JSON `{sensitivity_rating, responsiveness_rating}`
2. `extract_under_hood()`: finds `%%%UNDER_HOOD_START/END%%%`, extracts 4 named sub-blocks via inner delimiters
3. Both called from Stage 2 SSE done handler in `/api/run-stage`
4. Results returned in SSE done event payload; stored in localStorage by frontend

---

## 7. Common Workflows & How to Modify

### 7.1 I Want to Change a Prompt
1. Open the app
2. Click "Admin" → select the stage (1, 2, 3, deeper, or followon)
3. Edit the prompt text in the modal
4. Click "Save & Close"
5. Re-run that stage with the new prompt

(This is session-scoped; to persist globally, edit `DEFAULT_PROMPTS` in `app.py`)

**Note:** `deeper_playbook` prompt (Tab 3) is not exposed in the Admin modal by default — edit in `app.py` to change it.

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

**Note:** If you change the number of dimensions, also update Stage 3 prompt to reference them correctly. The `fcv_dimension` field in Stage 3 JSON must match a known dimension for Go Deeper "Analytical trail" filtering to work.

### 7.3 I Want to Change What Stage 3 Priorities Look Like
Stage 3 prompt defines the JSON schema for each priority. Current fields (see full schema in Section 3.4):
- `title`, `fcv_dimension`, `tag`, `refresh_shift`, `risk_level`, `the_gap`, `why_it_matters`, `actions[]`, `who_acts`, `when`, `resources`, `pad_sections`, `implementation_note`

To add/remove fields:
1. Update the JSON schema section of Stage 3 prompt (`DEFAULT_PROMPTS["3"]` in `app.py`)
2. Update `extract_priorities()` in `app.py` to handle the new field from the parsed JSON
3. Update `showPriority()` in `index.html` to display the new field
4. Update `downloadReport()` in `index.html` if the field should appear in the export

### 7.4 I Want to Change the FCV Refresh Shifts
The 4 FCV Refresh shifts are referenced in Stage 2 and Stage 3 prompts and in the `refresh_shift` field of each priority JSON. To update:
1. Edit `FCV_REFRESH_FRAMEWORK` in `background_docs.py`
2. Update Stage 2 and Stage 3 prompts to reference the new shifts
3. Update `extract_priorities()` shift validation list
4. Update the `refresh_shift` badge rendering in `showPriority()` if shift names change

### 7.5 I Want to Add a 4th Stage
1. Add a new key to `DEFAULT_PROMPTS` (e.g., `"4"`)
2. Add a new case in the stage switch logic in the `/api/run-stage` route
3. Add a new stage card and input panel to `index.html`
4. Update the stepper to show 1-of-4, 2-of-4, etc.

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

**Production server:** gunicorn + gevent (`--worker-class gevent --timeout 600`). This is required for long-running SSE connections (Express mode, Stage 1 web research). Flask dev server (`python3 app.py`) is still used for local development only — do not use it in production.

**Environment variables needed (set in Render dashboard):**
- `ANTHROPIC_API_KEY` — your Claude API key (required)
- `ADMIN_PASSWORD` — optional, for prompt admin modal (default: "fcv-admin-2024" if not set)

**Current dependencies:**
- Flask 3.0.3
- anthropic >= 0.40.0 (Anthropic SDK for Claude API)
- pypdf >= 4.0.0 (PDF text extraction)
- python-docx 1.1.2 (future document generation support)
- gunicorn >= 21.2.0 (production WSGI server — required for SSE long-running connections)
- gevent >= 23.9.0 (async worker class for gunicorn — required for concurrent SSE streams)

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
All Stage 3 outputs include a header disclaimer:
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
3. Run through all 3 stages, checking:
   - Stage 1 Part A extracts correctly from the project doc
   - Stage 1 Part B references contextual docs and training knowledge separately
   - Stage 2 Assessment Summary is thematic and uses FCV Refresh framing (not old pillars)
   - Stage 2 "Under the Hood" panels parse correctly and show the full 12-rec table
   - Stage 2 gauges (sensitivity + responsiveness) animate correctly
   - Stage 3 priorities are concrete with geographic callouts and `refresh_shift` badges
   - Stage 3 priorities use the correct lifecycle stage framing (PCN vs PAD etc.)
   - Go Deeper "alternatives" tab loads correctly per priority
   - Go Deeper "analytical trail" tab renders instantly from Stage 2 data
   - Go Deeper "playbook_refs" tab loads relevant Playbook guidance
4. Try the refine loop at each stage to ensure edits feed into next stage
5. Test the Follow-on card at Stage 3 bottom with at least 2 pre-fill chips

**Prompt quality checks:**
- Are recommendations specific (geography, mechanism, entry points) or vague?
- Do they reference the WBG framework (FCV dimensions, Do No Harm)?
- Are they evidence-based (grounded in uploaded docs) or speculative?
- Are multiple options offered or a single "solution" prescribed?

### 12.2 Red-Teaming the Prompts
Ask Claude (in a separate conversation) to critique Stage 3 output:
- Are the recommended priorities the most important ones?
- Are any dimensions under/overweighted?
- Do the recommendations align with the evidence presented?
- Would a TTL find these actionable?
- Is the `refresh_shift` assignment for each priority plausible?
- Does the Stage 2 Assessment Summary correctly apply the 4 FCV Refresh shifts (not old pillars)?
- Does the "Analytical trail" tab correctly attribute priorities to OST recs/questions?

---

## 13. Questions to Ask Before Making Changes

Before modifying prompts, frontend, or backend logic, ask yourself:

1. **What problem does this solve?** Is it addressing a real user pain point or a hypothetical issue?
2. **How does this affect the other stages?** If I change Stage 2 output, does Stage 3 prompt need updating? Does it affect Go Deeper "Analytical trail" parsing?
3. **Does this add complexity without clear benefit?** Could a simpler approach work?
4. **How do I test this?** What does a "good" outcome look like?
5. **Is this a one-time fix or a recurring need?** If recurring, should it be in the prompt or the frontend?
6. **Who is the user?** Is this for TTLs, FCV specialists, or both? Does the change serve their workflow?
7. **What's the trade-off?** Does this improve output quality at the cost of longer processing time? Is that acceptable?

---

## 14. Conversation Starters for Claude

When you return with a new issue or request, here are useful framing questions:

- **"How do I improve the specificity of Stage 3 recommendations?"**
  → Share an example of a vague recommendation and ask Claude to help rewrite the Stage 3 prompt to enforce specificity.

- **"The Go Deeper 'alternatives' tab is too long / too short."**
  → Adjust `DEFAULT_PROMPTS["deeper"]` length instructions or formatting requirements.

- **"The 'analytical trail' tab isn't matching the right OST recommendations."**
  → Check that `priority.fcv_dimension` is one of the 6 canonical values and that the Stage 2 recs table has a dimension column. Update the filtering logic in `loadDeeperTrail()`.

- **"I want to test the app with a different FCV framework (e.g., the ICRC framework instead of WBG)."**
  → Provide the alternative framework and ask Claude to rewrite Stage 2 prompt and `FCV_OPERATIONAL_MANUAL` to use it.

- **"Can we improve the Do-No-Harm checklist?"**
  → The canonical 8 principles are in Section 3.3 and in the Stage 2 prompt. Update the prompt and rerun Stage 2.

- **"The app should export a Word document / PDF report."**
  → Specify what should be in the report (which sections from which stages) and ask Claude to add export functionality.

- **"I want to add collaborative review mode."**
  → Describe the workflow (multiple users commenting on priorities, etc.) and ask Claude to design the backend/frontend changes.

---

## 15. File Structure & Repository Organization

```
FCV-AGENT/
├── app.py                    # Flask backend + all prompts (5 keys) + routes
├── index.html                # Main frontend UI (single-page app, ~4000+ lines)
├── background_docs.py        # 8 constants: FCV_GUIDE, FCV_OPERATIONAL_MANUAL,
│                             #   FCV_REFRESH_FRAMEWORK, PLAYBOOK_DIAGNOSTICS,
│                             #   PLAYBOOK_PREPARATION, PLAYBOOK_IMPLEMENTATION,
│                             #   PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP
├── prompts.json              # Session-specific prompt overrides (empty by default)
├── requirements.txt          # Python dependencies (Flask, anthropic, pypdf, python-docx)
├── Procfile                  # Render deployment config
├── .gitignore               # Git ignore rules
├── CLAUDE.md                 # THIS FILE - guidance for Claude
├── static/                  # Static assets (if any)
├── docs/                    # Design specs and plans
│   └── superpowers/specs/   # Architecture design documents
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

**"Under the Hood panels aren't showing in Stage 2"**
- Check that Stage 2 output contains `%%%UNDER_HOOD_START%%%` and `%%%UNDER_HOOD_END%%%` delimiters
- Look for yellow parse error banner at top of Stage 2 output
- Check browser console for `extract_under_hood` errors
- If delimiters are missing, the Stage 2 prompt may have been overridden — reset via Admin modal

**"Go Deeper 'alternatives' tab isn't loading"**
- Check that `/api/run-deeper` route exists and `DEFAULT_PROMPTS["deeper"]` is set
- Check browser console for SSE errors
- Verify `priority.fcv_dimension` and `priority.title` are being sent correctly in the request body

**"Go Deeper 'analytical trail' shows nothing"**
- Check that `localStorage.stage2_under_hood` has content (run Stage 2 first)
- Verify `priority.fcv_dimension` matches a dimension name used in the Stage 2 recs table
- Check the `loadDeeperTrail()` filtering logic against the actual recs table format

**"Stage 3 priorities are missing `refresh_shift`"**
- The Stage 3 JSON schema requires `refresh_shift` — check that `DEFAULT_PROMPTS["3"]` includes it in the schema spec
- If priorities parse but `refresh_shift` is null/missing, badge will not render but the app won't break

### How to Debug

1. **Check the browser console** (F12 → Console tab) for JavaScript errors
2. **Check the Flask server logs** for backend errors (should print to stdout in Render dashboard)
3. **Use the prompt admin modal** to see exactly what prompt was used for a stage
4. **Copy the LLM output** and share it with Claude, asking: "Why might this recommendation be vague/inaccurate?"

---

## 18. Credits & Context

This tool was developed iteratively based on feedback from World Bank FCV practitioners (particularly feedback on specificity, actionability, and framework completeness). The key insights driving the design:

1. **Specificity mandate:** Recommendations must move from broad critique ("service delivery needs to be targeted") to specific, location-aware guidance ("focus on Nzerekore, Kindia, Kankan where state legitimacy is lowest").
2. **Framework completeness:** The original app used only 6 of 12 OST recommendations. v7.0 integrates all 12 + 25 key questions + 3 key elements, driving a richer assessment.
3. **FCV Refresh adoption:** The January 2026 FCV Refresh introduced 4 strategic shifts. Old pillar framing (prevent/engage/transition/spillover) is superseded by Anticipate/Differentiate/Jobs & private sector/Enhanced toolkit.
4. **TTL vs. FCV CC distinction:** TTLs need clean, actionable findings. FCV Country Coordinators need analytical depth. The "Under the Hood" panel architecture serves both without cluttering the primary output.

The 3-stage pipeline was chosen to balance:
- **Quality:** Each stage allows refinement + user input
- **Usability:** Not overwhelming; reduced from 4 stages by merging the duplicative Screening + Gaps stages
- **Efficiency:** Earlier stages feed directly into later ones; web research + Under the Hood data reduces redundant LLM calls in later stages

"Go Deeper" (replacing Explorer) was added to address the FCV CC need for analytical provenance — not just "what should I do" but "why did the tool say that?"

---

## 19. Final Note

This `claude.md` is a living document. As you make changes, iterate on features, and learn what works, please update it. The goal is that any developer (including Claude in future conversations) should be able to:
1. Understand the app's architecture in 30 minutes
2. Identify where to make a requested change
3. Know the consequences of that change
4. Test the change effectively

If you find gaps in this documentation, or if new design decisions emerge, update this file. Future you (and future Claude) will thank you.

---

**Last updated:** 2026-04-03
**Current version:** FCV Project Screener 7.5 (UX polish: styled uploads, smart timer, condensed output, refined landing page)
**Current Claude model:** claude-sonnet-4-20250514
**Architecture:** Flask 3.0.3 backend + vanilla JS frontend + Anthropic SDK integration
**Design system:** WB Digital Look & Feel Style Guide — Open Sans, WB palette (#009FDA/#002244/#111827), RAG status colours. Reference: https://geospatial-commons.github.io/WB-Design-Guidelines/chapters/design-system.html
