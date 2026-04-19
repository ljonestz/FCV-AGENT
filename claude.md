# FCV Project Screening App — Claude Development Guide

> **Maintenance instruction:** After every substantial change (new features, prompt changes, new delimiters, UI additions, architectural decisions), update this file AND the relevant reference doc before committing. Keep section 1.3 (Stage pipeline), section 3 (Prompt Architecture), and section 5.3 (Priority Parsing) accurate at all times.
>
> **Reference files** (detailed specs moved here to keep this file under 40k):
> - `docs/reference/reference_prompt_architecture.md` — per-stage prompt specs, delimiter schemas, parsing details
> - `docs/reference/reference_frontend_functions.md` — JS function list, Express mode architecture, removed items
> - `docs/reference/reference_backend_routes.md` — all routes, SSE event shapes, parsing function signatures

---

## Overview

This is a **World Bank FCV (Fragility, Conflict, and Violence) Project Screener** — a Flask-based web app that guides Task Team Leaders (TTLs) through a **3-stage workflow** to assess how well a World Bank project integrates FCV considerations and generate targeted, actionable recommendations.

The tool explicitly distinguishes two concepts:
- **FCV Sensitivity [S]** — Is the project *aware of and designed for* the FCV context? Contextual awareness, conflict-informed design, Do No Harm, FCV-adapted operations.
- **FCV Responsiveness [R]** — Does the project *actively work to change* the FCV situation? Root-cause engagement, resilience building, transformative use of FCV tools, peace & stability dividends.

The 4 FCV Strategy Shifts (Anticipate / Differentiate / Jobs & Private Sector / Enhanced Toolkit) are **cross-cutting** — they apply to both S and R findings and are tagged inline.

Every prompt output tags findings as [S], [R], or [S+R], assigned dynamically per-finding. [S+R] strictly only for: (1) inclusion/targeting of conflict-affected populations; (2) FCV logic in ToC/PDO; (3) adaptive M&E for harm + resilience; (4) GRM for state-citizen accountability. If in doubt → [S] or [R].

**Key goal:** Move from broad, vague recommendations to specific, location-aware, operationally grounded, stage-aware suggestions (e.g., "historically, Nzerekore, Kindia, and Kankan have been excluded from service delivery — focus on these regions before PAD appraisal").

**Analytical backbone:** WBG FCV Strategy Refresh, FCV Operational Manual (OST, enriched with Peace & Inclusion Lens dimensions and Strategic DRR Framing from Good Practice Notes), FCV Operational Playbook, and Good Practice Notes on Peace & Inclusion Lenses and FCV-Sensitive Programming. When a Country Partnership Framework (CPF) is uploaded as a contextual document, Stage 3 recommendations include a `cpf_alignment` field linking priorities to CPF outcomes.

**Version history:**
- **v7.0** — Redesigned from 4 stages to 3; full 12 OST recs + 25 key questions; FCV Playbook integration; Under the Hood panels; refresh_shift field
- **v7.2** — Stage 2 dynamic thematic narrative; actions[] array replaces recommendation string; Go Deeper 2-tab panel; Stage 3 clean memo (no inline citations)
- **v7.4** — Express Analysis mode (single SSE endpoint for all 3 stages)
- **v7.5** — UX polish: styled uploads, smart timer, condensed output, refined landing page; S/R definition box removed from Stage 3; rating rubric with reasoning block
- **v7.6** — Document format fixes: DOCX properly parsed via python-docx (base64, reading-order-aware, merged-cell dedup); PPTX support added via python-pptx; silent extraction failures surfaced as chip warnings and SSE banners
- **v7.7** — Concurrency hardening: per-tab assessment IDs in the frontend, assessment-aware request payloads, express workflow execution moved onto the background assessment executor, and multi-worker gunicorn defaults for better parallel use
- **v8.0** — Major knowledge base and prompt quality overhaul (branch `feat/v8-knowledge-base`, merged 2026-04):
  - **Knowledge base:** 6 instrument entries (IPF/PforR/DPO/TA/MPA/IPF-DDO) + 5 process guides (MTR/ISR/AF/Restructuring/ICR) + 29 glossary terms + FCS country list (2015–present)
  - **Prompt quality:** WB LLM quality review integrated — SEA/SH as 9th DNH principle, gender-FCV trigger block (7 conditions), lifecycle guardrails (SORT/ESF/SEP/ESCP minimum set for PAD), instrument routing guardrail per doc type, mandatory priority cards for gender and SEA/SH flags
  - **Temporal anchoring fix:** `_build_temporal_guardrail(temporal_ctx, doc_type)` now takes `doc_type`; PAD/PCN/PID/AF/Restructuring documents always receive preparation-phase framing regardless of whether approval date is in the past — prevents implementation-review hallucination cascade in Stages 2–3
  - **Stage 1 UX:** Prompt now requires 2–3 sentence narrative lead paragraph at top of each Part. Frontend `renderStage1()` parses Part A/B split and renders with styled section badges ("From your document only" / "Wider context & research"); narrative lead paragraph visually distinguished
  - **Finalized PAD notice:** `isFinalizedPAD()` detects uploaded PADs with past approval dates; amber retrospective notice injected in Stage 3 output and downloaded report
  - **FCS cross-checking:** `FCS_LIST` constant added to `background_docs.py` (39 current members, year of entry, 9 graduated countries); injected into Stage 1 and Stage 2 prompts so LLM verifies classification against authoritative list
  - **Implementation review locked off:** `fcv_review_mode` localStorage restore IIFE removed; app always defaults to design review mode on load; implementation review preserved in backend for future activation
  - **Rating recalibration:** Percentage-based thresholds, partial credit for Weakly addressed, softened responsiveness cap
  - **Optional context box:** User can supply framing before analysis (peer review notes, changed conflict conditions)
  - **Step-by-step:** Load-first mode (full output on completion, not progressive streaming)
- **v8.1** — WBG LLM review batch + web research fix (branch `fix/wbllm-review-batch`, merged 2026-04-13):
  - **Instrument calibration:** New `FCV_INSTRUMENT_CALIBRATION` constant in `background_docs.py` — DPF failure modes (policy reversal, adjustment sequencing, programmatic series risk, Cat DDO scrutiny), FCV Envelope nuances (EDP, annual review requirement, eligibility logic), RRA as consultative process, trust funds and ASA as alternatives
  - **DPF guardrail (Stage 3):** ESCP, ESF standards, SORT-as-monitoring, and DLIs are now explicitly excluded for DPF/DPO instruments; recommendations framed around prior action conflict-sensitivity and reform sequencing instead
  - **Adjustment sequencing DNH (Stage 2):** New budget-support-specific DNH check on reform cost/safety net sequencing gap — flagged as the primary DNH pathway for DPF operations in FCV settings
  - **Citation discipline (Stage 1):** Part B now required to label training knowledge as `[From: general knowledge — ...]` not `[From: training knowledge - ...]`
  - **FCV Envelope eligibility guardrail:** Stage 1 prompt and `FCS_LIST` constant updated to prohibit explicit eligibility determinations for IDA FCV Envelope windows (PRA/RECA/TAA) — eligibility is multi-criteria and determinations risk being incorrect
  - **Web research timeout:** Research client timeout increased 45s → 120s; error now logged as `[WebResearch ERROR]` in Render logs
  - **Upload UI:** Project zone now lists PCN/PID/PAD only; contextual zone updated with PPSD/technical studies examples; "implementation coming soon" notice upgraded to amber banner
  - **Download:** Reports default to `.docx`
- **v8.2** — GPN integration + CPF upload support (branch `feat/v8.2-gpn-cpf-integration`, merged 2026-04-14):
  - **GPN enrichment:** `FCV_OPERATIONAL_MANUAL` enriched with two Good Practice Note subsections — "Peace & Inclusion Lens Dimensions" (5 dimensions: geographic targeting against RRA divides, social cohesion/reconciliation, project-cycle-specific application, conflict actor engagement, unintended consequences screening) and "Strategic DRR Framing" (DRR mapping, 4 P's framework, strategic vs operational distinction)
  - **CPF upload:** Country Partnership Framework accepted as named contextual upload; Stage 1 extracts automatically; Stage 3 adds `cpf_alignment` field (null if no CPF; string linking to CPF outcome if present)
  - **CPF_INTEGRATION_GUIDE:** New constant in `background_docs.py` injected into Stage 3 prompt (both step-by-step and express paths)
  - **Source attribution:** Good Practice Notes listed alongside OST Manual, Playbook, and Strategy in all 4 UI locations (onboarding modal, limitations note, pre-loaded sources banner, express progress screen)
  - **Architecture map:** `docs/fcv-agent-knowledge-architecture.html` — shareable HTML showing knowledge sources → pipeline stages → outputs
  - **Stage 3 timeout fix (2026-04-15):** Three-part fix for "BodyStreamBuffer was aborted" on Stage 3 in Express mode — (1) Express frontend now resets the abort timer to a fresh 8-minute budget when `stage_start:3` fires, rather than using whatever remains of the global 10-minute budget; (2) both Express and Step-by-Step backends now store a compact label for each stage's user prompt in `conversation_history` instead of the full 80k-char prompt, halving the Stage 3 API input size; (3) model updated from deprecated `claude-sonnet-4-20250514` to `claude-sonnet-4-6` across all call sites. Step-by-step Stage 3 timeout also raised from 6 → 8 minutes to match Express.
- **v9.0** — Differentiated knowledge architecture (branch `feat/v9-differentiated-approaches`, 2026-04-17):
  - **Country classification:** Stage 1 prompt outputs `%%%COUNTRY_CLASSIFICATION_START/END%%%` block (category, confidence, reasoning); `extract_country_classification()` parses it; `classify_country()` cross-references FCS list with bidirectional name matching
  - **Classification widget:** Rendered at top of Stage 1 output using `researchCountry` and classification reasoning; narrative format ("This analysis places [country] within the [category] category…"); always ends with caveat: "This is a subjective judgement on the part of this AI tool and does not constitute an official WBG classification."; dropdown override auto-saves on change; no confirmation step required
  - **Secondary knowledge snippets:** `select_secondary_knowledge()` picks category-specific knowledge snippets from `background_docs.py`; injected into Stages 2 and 3 prompts for differentiated framing
  - **`country_category_relevance` field:** Added to Stage 3 priority JSON — explains why each priority is particularly relevant for this country's specific FCV category
  - **DIFFERENTIATED_APPROACHES constant:** New knowledge constant in `background_docs.py` injected into Stages 2 and 3
- **v9.2** — Classification caveat and background_docs policy corrections (branch `feat/v9-differentiated-approaches`, 2026-04-19):
  - **Classification widget caveat:** Narrative now always ends with "This is a subjective judgement on the part of this AI tool and does not constitute an official WBG classification." — consistent with Stage 1 AI disclaimer framing
  - **background_docs.py — ICR timing:** `STAGE_GUIDANCE_MAP["ICR"]["timing_options"]` corrected from `"During implementation"` to `"At project closing"`
  - **background_docs.py — Para 12 naming:** Removed all incorrect "Para 11" / "Para 11/12" references; standardised to "Paragraph 12 of Section III of the IPF Policy" with correct two-situation description (urgent need; capacity constraints); clarified Para 12 is NOT required for Framework Approach, Phased Implementation, or Unallocated Funds
- **v9.1** — UX, prompt quality, and bug fixes (branch `feat/v9-differentiated-approaches`, 2026-04-18):
  - **DOCX download fix:** `downloadReport()` now POSTs to new `/api/download-report` route; backend generates a true python-docx binary (not HTML masquerading as .docx). New helpers: `_md_to_docx_para()` (markdown→docx paragraphs), `_safe_run()` (safe runs[0] access)
  - **Stage 1 prompt — prose narrative:** Body content now required to be prose paragraphs (2–4 sentences per subsection); bullets restricted to genuinely enumerable items only
  - **Stage 1 prompt — country-specific fact flagging:** Part B must tag unverifiable country-specific claims (named institutions, legislation, political events, officials) with `[Verify: ...]` inline
  - **Stage 1 prompt — IDA FCV Envelope advisory:** For Conflict-Affected and Situations of Fragility countries, adds a brief end-of-Part-B advisory prompting TTL to discuss PRA/RECA/TAA eligibility with regional FCV coordinator (not an eligibility determination)
  - **Stage 2 prompt — Refresh shifts as qualitative lenses:** FCV Strategy Refresh shifts explicitly framed as analytical lenses for strategic alignment, not a scoring checklist
  - **Stage 3 prompt — Watch List for Supervision:** "Horizon Considerations" section renamed and reframed as "Watch List for Supervision"; each item must name a specific WBG tracking vehicle (ISR risk flag, MTR agenda item, RRA update, restructuring trigger); panel heading in frontend updated to match
  - **Stage 3 priorities — `action_timing` field:** New enum field (`pre-appraisal` / `next-series` / `supervision`) with coloured pill in UI and included in DOCX download
  - **SORT guardrail:** Stage 3 prompt now prohibits prescribing specific SORT ratings; frames risk exposure as "consider whether the current rating adequately reflects X"
  - **Source credibility flagging:** Stage 1 Part B labels source type inline (`[Data: high-quality]`, `[Data: secondary]`, `[Source: news/media]`); data gap flagging for missing FCV dimensions
  - **Classification confirm button removed:** Dropdown auto-applies on change via `onchange` listener; `confirmClassification()` function deleted; act-area no longer hidden
  - **Step-by-step loading timers:** Elapsed timer and rotating stage-specific messages added; hints updated to reflect real durations (Stage 2: 3–5 min, Stage 3: 4–6 min)
  - **Paragraph spacing fix:** `.out-body p` CSS set to `margin-top: 0; margin-bottom: 0.5em` to eliminate double gaps in Stage 1 output
  - **CPF upload encouragement:** Contextual zone hint updated with bold/underlined CPF prompt; SCD removed; RRA mentioned as secondary option

---

## Repository Structure

### What's in the public GitHub repo
The repo contains only what's needed to understand, deploy, and maintain the app:
- Core app files: `app.py`, `background_docs.py`, `index.html`
- `docs/reference/` — detailed specs for prompts, routes, and frontend functions
- `docs/fcv-agent-knowledge-architecture.html` — shareable knowledge architecture diagram
- `tests/` — unit tests for priority extraction
- Deployment files: `requirements.txt`, `Procfile`, `.gitignore`, `README.md`

### What's kept locally only (not in the repo)
These folders exist on the development machine but are gitignored — do not commit them:
- `app_feedback/` — internal review documents, colleague feedback, test PDFs
- `docs/superpowers/` — implementation plans and design specs from development sessions
- `.claude/` — local Claude Code configuration
- `.superpowers/` — brainstorming session artifacts
- `AGENTS.md` — internal agent instructions
- Session handoff notes (e.g. `docs/*SESSION_HANDOFF*`) and dev mockups (`docs/mockup_*`)

---

## 1. Project Architecture

### 1.1 Tech Stack
- **Backend:** Python Flask 3.0.3 + Anthropic Claude API (`claude-sonnet-4-6`)
- **Frontend:** HTML + vanilla JavaScript + Markdown rendering
- **Hosting:** Render.com (gunicorn + gevent)
- **Concurrency model:** Per-tab assessment IDs in the browser; Express runs emitted from a background assessment executor; multi-worker gunicorn in production
- **Document processing:** PDF (pypdf), DOCX (python-docx), PPTX (python-pptx) text extraction; all binary formats sent as base64 from browser
- **Session management:** Browser storage namespaced by per-tab assessment ID + JSON-serialized conversation history

### 1.2 Core Files
```
app.py              # Flask backend, all prompts (DEFAULT_PROMPTS), routes, document processing
index.html          # Single-page frontend UI (Stage 1–3, Go Deeper, Express mode, prompt modal)
background_docs.py  # 10 constants: FCV_GUIDE, FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK,
                    #   PLAYBOOK_DIAGNOSTICS, PLAYBOOK_PREPARATION, PLAYBOOK_IMPLEMENTATION,
                    #   PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP, FCS_LIST, CPF_INTEGRATION_GUIDE
                    #   + WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE, FCV_INSTRUMENT_CALIBRATION (helpers)
prompts.json        # Session-specific prompt overrides (empty by default)
requirements.txt    # Flask, anthropic, pypdf, python-docx, python-pptx, gunicorn, gevent
Procfile            # Render deployment config
```

### 1.3 Three-Stage Pipeline

**Two workflow modes:** Express Analysis (default — all 3 stages run automatically via `/api/run-express`) and Step-by-Step (interactive, one stage at a time via `/api/run-stage`). Same prompts, same output quality.

```
STAGE 1 — Context & Extraction
├─ Input: Project doc (PCN/PID/PAD/AF/Restructuring) + optional contextual docs
├─ Automated web research: extract_country_name() + extract_sector_name() → 9-search brief
│  (cached by "country::sector"; shown as collapsible dropdown above Stage 1 output)
├─ Three-tier citation: Tier 1 uploaded docs → Tier 2 web research → Tier 3 training knowledge
├─ Output: 2–3 sentence narrative lead (required) then PROSE PARAGRAPHS (not bullets) — for EACH of:
│    Part A (doc extract only) and Part B (contextualized, tiered citations)
│    Bullets restricted to genuinely enumerable items only (named locations, dates, prior actions)
├─ Country-specific fact flagging: Part B tags unverifiable claims (named institutions, legislation,
│    political events, officials) inline with [Verify: ...]; claims from uploaded docs are exempt
├─ IDA FCV Envelope advisory: for Conflict-Affected and Situations of Fragility countries, end-of-
│    Part-B advisory prompts TTL to discuss PRA/RECA/TAA eligibility with regional FCV coordinator
│    (not a determination — coexists with existing eligibility guardrail)
├─ Frontend: renderStage1() parses Part A/B split; renders with styled section badges
│  (blue "From your document only" / green "Wider context & research"); narrative lead
│  styled as tinted callout above bullets
├─ Classifier lines (stripped from display by clean_stage1_output(); kept in history):
│  %%%DOC_TYPE: [PCN/PID/PAD/AF/Restructuring/ISR/Unknown]%%%
│  %%%INSTRUMENT_TYPE: [IPF/PforR/DPO/TA/MPA/IPF-DDO/Unknown]%%%
│  %%%TEMPORAL_CONTEXT_START%%%...%%%TEMPORAL_CONTEXT_END%%% → approval_date, closing_date,
│    safeguards_framework, other_temporal_markers
│  (parsed by frontend; passed to Stage 2/3 requests as instrument_type, temporal_context)
├─ Large docs: >150k chars → LLM condensation; >500k chars → truncation
└─ Prompt constants: FCV_GUIDE, PLAYBOOK_DIAGNOSTICS, FCV_REFRESH_FRAMEWORK, FCS_LIST

STAGE 2 — FCV Assessment
├─ Input: Stage 1 output (conversation history)
├─ Internal engine: 12 OST recs + 25 key questions + 3 key elements (TTL sees themes, not framework)
├─ TTL-facing output (400–500 words): 3–5 dynamic themes → DNH traffic-light → S/R synthesis
│  → Sensitivity + Responsiveness ratings → 3–5 key gaps
├─ Delimiter blocks (stripped from display, parsed to frontend):
│  %%%STAGE2_RATINGS_START/END%%% → {sensitivity_rating, responsiveness_rating}
│  %%%RATING_REASONING_START/END%%% → reasoning block (auditing only)
│  %%%UNDER_HOOD_START/END%%% → 4 sub-blocks:
│    %%%RECS_TABLE_START/END%%%    — 12-rec table with S/R Tag column
│    %%%DNH_CHECKLIST_START/END%%% — 9-principle DNH checklist (principle 9 = SEA/SH)
│    %%%QUESTIONS_MAP_START/END%%% — 25 key questions with findings
│    %%%EVIDENCE_TRAIL_START/END%%% — sources and citation tiers
├─ Under Hood text stored in localStorage "stage2_under_hood" → used by Go Deeper Tab 1
├─ Rating rubric: Sensitivity = OST recs % addressed → 6-tier (percentage-based, partial credit
│  for Weakly addressed, quality gates apply); Responsiveness = FCV Refresh shifts count → 6-tier
│  Stage 3 inherits Stage 2 ratings verbatim — no independent re-rating
├─ SEA/SH flag: seash_standalone_flag: TRUE → mandatory SEA/SH priority card in Stage 3
├─ Gender flag: gender_fcv_flag: TRUE (any of 7 trigger conditions) → mandatory gender card
└─ Prompt constants: FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK, FCV_GUIDE, FCS_LIST

STAGE 3 — Recommendations Note (stage-aware)
├─ Input: Stages 1–2 history + doc_type + uploaded_doc_names
├─ Stage-awareness: PCN/PID → PLAYBOOK_PREPARATION; PAD → PLAYBOOK_PREPARATION;
│  AF/Restructuring → PLAYBOOK_IMPLEMENTATION; ISR → PLAYBOOK_IMPLEMENTATION+CLOSING
├─ Temporal guardrail: _build_temporal_guardrail(temporal_ctx, doc_type) — for design-stage
│  docs (PAD/PCN/PID/AF/Restructuring), always returns preparation-phase framing regardless
│  of whether approval date is in the past. Prevents implementation-review hallucination.
├─ Finalized PAD notice: isFinalizedPAD() detects PAD with past approval date → amber
│  retrospective banner injected in output and downloaded report
├─ Instrument routing guardrail: per-doc-type constraints injected into prompt
├─ PAD minimum instrument reference set: SORT, ESS1, SEA/SH AP, SEP/ESS10, ESCP, OM, PPSD, RF
├─ Output: narrative memo + %%%JSON_START%%%...%%%JSON_END%%% block
│  JSON top-level: fcv_rating, fcv_responsiveness_rating, sensitivity_summary,
│    responsiveness_summary, risk_exposure {risks_to, risks_from}, priorities[]
│  Each priority: title, fcv_dimension, tag, refresh_shift, action_timing, risk_level, the_gap,
│    why_it_matters, actions[] (document_element + guidance + suggested_language),
│    who_acts, when, resources, pad_sections, implementation_note,
│    cpf_alignment (null if no CPF uploaded; string linking to CPF outcome if CPF present)
│    action_timing: pre-appraisal | next-series | supervision — rendered as coloured pill
├─ Watch List for Supervision: final section (replaces "Horizon Considerations"); each item names
│    a specific WBG tracking vehicle (ISR risk flag, MTR agenda item, RRA update, restructuring
│    trigger); items without a named vehicle excluded; framed as risks to monitor, not act on now
├─ SORT guardrail: prompt prohibits prescribing specific SORT ratings; frames risk exposure as
│    "consider whether current rating adequately reflects X"
├─ clean_stage3_output(): strips JSON block, risk narrative, and everything from
│  %%%PRIORITIES_START%%% onwards — all shown as cards from JSON
├─ Citation policy: ONLY cite docs from Stage 1 [From: name]. Never fabricate titles.
└─ Prompt constants: stage-appropriate PLAYBOOK + FCV_REFRESH_FRAMEWORK + CPF_INTEGRATION_GUIDE

FOLLOW-ON (Stage 3 bottom card)
├─ POST /api/run-followon — full history + user message → SSE response appended below card
└─ 4 pre-fill chips: "Draft peer review note" / "Expand top recommendation" /
   "Review my revised text" / "Summarise for brief"

GO DEEPER (per-priority, Stage 3 only — 2 tabs)
├─ Tab 1 (Evidence trail): DEFAULT. No API call — filters localStorage.stage2_under_hood
│  by priority.fcv_dimension; renders instantly
└─ Tab 2 (FCV Playbook): SSE call to /api/run-deeper?tab=playbook_refs
   Cache keys: deeper_{idx}_trail, deeper_{idx}_playbook
```

> **Full prompt schemas, delimiter formats, and parsing function signatures:**
> → `docs/reference/reference_prompt_architecture.md`

---

## 2. Design Decisions & Philosophy

### 2.1 Why 3 Stages?
- Sequential refinement: users pause, review, and correct at each step
- Old Stages 2 (Screening) and 3 (Gaps) were duplicative — merged into a single Assessment stage
- Fewer stages = cleaner TTL workflow without losing quality

### 2.2 Why Part A / Part B Split in Stage 1?
- Transparency: users see what came from their doc vs. external context
- Accuracy accountability: Part A errors = extraction issue; Part B errors = contextual interpretation issue

### 2.3 Why "Go Deeper" (2-tab panel)?
- Tab 1 (Evidence trail): No API call — uses Stage 2 Under the Hood data already in localStorage. Instant.
- Tab 2 (FCV Playbook): Lightweight LLM call for operational tools, WBG teams, policy hooks.
- "Other options" (alternatives) tab removed in v7.2 — rarely used, added cognitive load.
- Core recommendation is self-contained in JSON. Go Deeper is optional depth. Download never needs it.

### 2.4 Specificity Mandate
Recommendations must name geography, mechanism, and entry points — not broad policy suggestions.
- **Bad:** "Service delivery needs to be targeted so it doesn't contribute to grievance"
- **Good:** "In Nzerekore, Kindia, and Kankan — historically excluded — focus service delivery via community health extension workers and cash-for-work entry points"

Enforced via: full 12-rec OST engine in Stage 2; geographic/mechanism requirements in Stage 3 prompt; `_check_specificity()` in `extract_priorities()`.

### 2.5 Session Persistence
All inputs and outputs stored in browser localStorage as JSON. Passed to each stage for full context.
Limitation: browser-specific, not suitable for team collaboration or long-term archival.

---

## 3. Prompt Architecture

### 3.1 Where Prompts Live

```python
# app.py — top-level DEFAULT_PROMPTS dictionary
DEFAULT_PROMPTS = {
    "1": "...",               # Stage 1: Context & Extraction
    "2": "...",               # Stage 2: FCV Assessment
    "3": "...",               # Stage 3: Recommendations Note
    "deeper": "...",          # Legacy alternatives tab (retained for backwards compat)
    "deeper_playbook": "...", # Go Deeper Tab 2: FCV Playbook
    "followon": "..."         # Follow-on post-analysis tasks
}
# Go Deeper Tab 1 (Evidence trail) has NO prompt — frontend-only filter from localStorage
```

**Session overrides:** stored in `prompts.json`, loaded via `load_prompts()`, merged with defaults.
**To override:** Admin modal → stage selector → edit → Save & Close (session-scoped only).
**To persist globally:** edit `DEFAULT_PROMPTS` in `app.py`.
**Note:** `deeper_playbook` is not exposed in the Admin modal — edit directly in `app.py`.

### 3.2 Per-Stage Prompt Summary

| Stage | Input | Key outputs | Prompt constants |
|---|---|---|---|
| 1 | Project doc + optional context | Part A (extract) + Part B (contextualised) + DOC_TYPE line | FCV_GUIDE, PLAYBOOK_DIAGNOSTICS, FCV_REFRESH_FRAMEWORK |
| 2 | Stage 1 history | Thematic narrative + ratings + Under the Hood delimiter blocks | FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK, FCV_GUIDE |
| 3 | Stages 1–2 history + doc_type | Narrative memo + JSON priorities block | Stage-appropriate PLAYBOOK + FCV_REFRESH_FRAMEWORK |

> **Full per-stage specs, JSON schemas, and delimiter formats:**
> → `docs/reference/reference_prompt_architecture.md`

### 3.3 Key Modification Workflows

**Change a prompt:** Admin modal (session-scoped) or edit `DEFAULT_PROMPTS` in `app.py` (global).

**Change the 6 FCV dimensions:**
1. Edit Stage 2 prompt in `DEFAULT_PROMPTS`
2. Update Stage 3 prompt to reference same dimensions (fcv_dimension must match for Go Deeper trail filtering)

**Change Stage 3 priority fields:**
1. Update JSON schema in `DEFAULT_PROMPTS["3"]`
2. Update `extract_priorities()` in `app.py`
3. Update `showPriority()` in `index.html`
4. Update `downloadReport()` if field should appear in export

**Change the 4 FCV Refresh shifts:**
1. Edit `FCV_REFRESH_FRAMEWORK` in `background_docs.py`
2. Update Stage 2 and Stage 3 prompts
3. Update `extract_priorities()` shift validation list
4. Update `refresh_shift` badge rendering in `showPriority()`

---

## 4. Frontend Architecture

### 4.1 UI Panels
1. **Onboarding modal** — AI disclaimer + checkbox to suppress on future visits
2. **Session bar** — stage progress + save session button (hides "No active session" on initial load)
3. **Stage progress stepper** — 3-step: Context → Assessment → Recommendations
4. **Input panel (Stages 1–2)** — file upload zone, document list, refine input
5. **Output panel (Stages 1–3)** — LLM output + collapsible sections
6. **Under the Hood panels (Stage 2)** — 4 expandable `<details>`:
   - Panel 1: "How well does the project integrate FCV considerations?" (12 OST recs, S/R Tag column)
   - Panel 2: "Could this project unintentionally cause harm?" (8 DNH principles)
   - Panel 3: "What did we look for — and what was missing?" (25 diagnostic questions)
   - Panel 4: "Where did this analysis come from?" (sources, tiers, contributions)
7. **Ratings sidebar (Stage 2+)** — Sensitivity gauge (blue, shield) + Responsiveness gauge (green, leaf)
8. **Go Deeper panel (Stage 3)** — Per-priority `<details class="go-deeper">` with 2 tab buttons
9. **Prompt modal** — Admin-only: view/edit prompts per session

### 4.2 Styling
- **Colours:** WB palette — wb-blue (#009FDA), wb-navy (#002244), wb-gray-900 (#111827), wb-gray-50 (#F7F8FA), wb-gray-100 (#EEF0F3). RAG: red (#D73027), amber (#FFFFBF), green (#1A9850). Full reference: `memory/reference_wb_design_system.md`
- **Typography:** Open Sans, 14px/400 body, 15px/700 section headings, 10px/600 labels
- **Spacing:** 4px base unit; xs=4, sm=8, md=16, lg=24, xl=32
- **Cards:** border-radius 8px, box-shadow 0 1px 3px rgba(0,0,0,0.08)
- **Font consistency:** `.pc-zone-body` and `.out-body` both 14px — do not let these diverge

### 4.3 Do No Harm Rendering
- **Stage 2 inline:** traffic-light summary, e.g., "Do No Harm: 6 of 8 addressed | 1 partial | 1 gap"
- **Stage 2 Under the Hood Panel 2:** full 8-principle table with evidence (from `%%%DNH_CHECKLIST_START/END%%%`)
- DNH is NOT shown as a standalone checklist in Stage 3

> **Full JS function list, Express mode functions, and removed items:**
> → `docs/reference/reference_frontend_functions.md`

---

## 5. Backend Routes & API

### 5.1 Route Summary

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/run-stage` | Core analysis (Stages 1–3, step-by-step) |
| POST | `/api/run-express` | Express mode (all 3 stages, single SSE) |
| POST | `/api/run-deeper` | Go Deeper tab content |
| POST | `/api/run-followon` | Follow-on post-analysis queries |
| POST | `/api/download-report` | Generate true DOCX binary via python-docx |
| GET/POST | `/api/admin/prompts` | Prompt management |
| GET | `/` | Main app |
| GET | `/health` | Health check |

### 5.2 Key Constants & Limits

```python
MAX_DOC_CHARS = 500_000       # Docs larger than this get LLM summarization
EXTRACT_THRESHOLD = 150_000   # Docs larger than this are condensed via LLM before analysis
ADMIN_PASSWORD = "fcv-admin-2024"  # from env var ADMIN_PASSWORD
PROMPTS_FILE = 'prompts.json'
```

### 5.3 Priority Parsing (`extract_priorities()`)

Finds `%%%JSON_START%%%...%%%JSON_END%%%`, parses via `json.loads()`, validates field values, runs `_check_specificity()` and `_check_citations()`, returns unified dict. On malformed JSON: `{error: True, message: ...}` — NOT silent failure.

### 5.4 Stage 2 Parsing

- `extract_stage2_ratings()` → `{sensitivity_rating, responsiveness_rating, rating_reasoning}`
- `extract_under_hood()` → `{recs_table, dnh_checklist, questions_map, evidence_trail}`
- `clean_stage2_output()` — strips all delimiter blocks from display text
- On `extract_under_hood()` failure: `parse_error: true` in SSE event; yellow banner shown; Stage 3 still proceeds

> **Full route specs, SSE event shapes, parsing function signatures:**
> → `docs/reference/reference_backend_routes.md`

---

## 6. Key Implementation Details

### 6.1 SSE Streaming
All stage and Go Deeper requests use Server-Sent Events. Frontend renders text progressively. Session history preserved even if a stream fails mid-way.

### 6.2 Conversation History
History passed to each stage so the LLM maintains context. Stored in localStorage. Allows session recovery on page reload.

**Compact-label pattern (critical for performance):** Each stage stores a compact user label in `conversation_history` instead of the full prompt with injected background constants. The full prompt is used for the API call but is replaced with a label like `"[Stage 2 — analysis prompt with operational guidance injected]"` before being saved to history. This prevents 80k+ chars of background docs from accumulating in the Stage 3 (and follow-on) API call inputs, which would otherwise cause slow time-to-first-token and risk hitting Render's 10-minute proxy timeout. Stage 1 has always done this; Stages 2 and 3 were updated in v8.2. Each stage re-injects its own fresh background docs — the assistant outputs are what matters for continuity.

### 6.3 Under the Hood → Go Deeper Flow
Stage 2 emits `%%%UNDER_HOOD_START/END%%%` delimiter block. After Stage 2 completes, frontend stores this in `localStorage.stage2_under_hood`. Go Deeper Tab 1 (Evidence trail) reads this directly — no API call, renders instantly.

### 6.4 Priority JSON Parsing
`extract_priorities()` uses `json.loads()` on the `%%%JSON_START/END%%%` block. No regex field extraction. Validates all field value sets. Runs specificity check (proper-noun proxy) and citation check (against uploaded doc names + org whitelist).

### 6.5 UX Safeguards
- **S/R tag tooltips:** `renderSRTagBadge()` adds `title` attribute explaining [S]/[R]/[S+R]
- **Specificity warning:** amber badge if `priority.specificity_warning === true`
- **Citation warning:** amber badge if `priority.citation_warnings.length > 0`
- **Under the Hood parse error banner:** yellow banner if `extract_under_hood()` fails; raw text shown as fallback
- **Stage consistency banner:** yellow banner at Stage 3 if Stage 2 was re-run after Stage 3

---

## 7. Common Workflows

### Changing a Prompt
- **Session only:** Admin modal → stage → edit → Save & Close
- **Globally:** Edit `DEFAULT_PROMPTS` in `app.py`

### Adding a Field to Stage 3 Priorities
1. Update JSON schema in `DEFAULT_PROMPTS["3"]`
2. Update `extract_priorities()` in `app.py`
3. Update `showPriority()` in `index.html`
4. Update `downloadReport()` if needed in `index.html`

### Adding a 4th Stage
1. Add key to `DEFAULT_PROMPTS`
2. Add case in `/api/run-stage` stage switch
3. Add stage card + input panel to `index.html`
4. Update stepper to show 1-of-4

### Questions to Ask Before Any Change
1. What problem does this solve? Is it a real user pain point?
2. How does this affect other stages? (Stage 2 changes → Stage 3 prompt? Go Deeper trail filtering?)
3. Does this add complexity without clear benefit?
4. How do I test it? What does a "good" outcome look like?
5. Who is the user — TTL, FCV CC, or both?

---

## 8. Deployment

### Local
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="..."
python3 app.py   # http://localhost:5000
```

### Render.com
- Connect GitHub repo → Render reads `Procfile` + `requirements.txt`
- **Production server:** gunicorn + gevent (`--worker-class gevent --timeout 600`) — required for long-running SSE
- **Env vars:** `ANTHROPIC_API_KEY` (required), `ADMIN_PASSWORD` (optional, default: "fcv-admin-2024")
- Auto-deploys on push to connected branch

---

## 9. Safety & Output Handling

Stage 3 outputs are prepended with an AI disclaimer header (`DO_NO_HARM_HEADER` constant in `app.py`) making clear this is LLM-assisted output for review only, not a substitute for professional FCV analysis.

Citation hallucination guard: Stage 3 prompt explicitly prohibits fabricating document citations. If Stage 3 prompt is modified, ensure this guard is preserved.

---

## 10. Known Limitations

- **localStorage scope:** Browser-specific; no team sharing or long-term archival
- **Rate limiting:** LLM calls are not rate-limited; high-volume use could hit API throttles
- **Large documents:** >500k chars truncated; very large projects may lose nuance. Scanned/image-only PDFs extract to near-zero text — a warning is shown but analysis still runs.
- **DOCX/PPTX:** Modern formats only (.docx, .pptx). Legacy binary formats (.doc, .ppt) are not supported.
- **Research cache:** In-process memory; lost on server restart
- **Mobile:** Desktop-optimized; mobile experience limited

---

## 11. Why These Decisions?

| Decision | Reason |
|---|---|
| Claude Sonnet 4 | Strong FCV reasoning; fast enough for iterative refinement; efficient cost |
| Flask (not React) | Lightweight; direct LLM integration; vanilla JS sufficient; easy Render deploy |
| SSE streaming | Real-time feedback; no polling overhead; better UX |
| localStorage sessions | Quick to implement; no database needed; works offline |
| Delimiter + JSON parsing | Reliable extraction; allows LLM to generate prose around structured data; easy to extend |
| 3 stages (not 4 or 1) | Sequential refinement; old Stages 2+3 were duplicative; merged for cleaner workflow |

---

## 12. Testing Checklist

**Per run, check:**
- [ ] Stage 1 Part A extracts from doc only; Part B uses correct citation tiers
- [ ] Stage 2 Assessment is thematic and uses FCV Refresh framing (not old pillars)
- [ ] Stage 2 Under the Hood panels parse correctly (12-rec table, DNH, questions, evidence)
- [ ] Stage 2 gauges animate; ratings are plausible
- [ ] Stage 3 priorities include geographic callouts and `refresh_shift` badges
- [ ] Stage 3 lifecycle framing matches doc type (PCN vs PAD framing)
- [ ] Go Deeper Trail tab renders instantly from Stage 2 data
- [ ] Go Deeper Playbook tab loads relevant guidance
- [ ] Follow-on card works with at least 2 pre-fill chips

**Prompt quality checks:**
- Are recommendations specific (geography, mechanism, entry points)?
- Are they evidence-based (grounded in uploaded docs)?
- Does the Stage 2 Assessment correctly apply 4 FCV Refresh shifts (not old pillars)?

---

## 13. Debugging

| Symptom | Check |
|---|---|
| Stage 1 hangs on large PDF | LLM summarizing (expected, 30–60s). Check `MAX_DOC_CHARS`. |
| DOCX/PPTX shows "could not extract" | Check python-docx/python-pptx are installed (`pip install -r requirements.txt`). Only .docx/.pptx supported — not .doc/.ppt. |
| Scanned PDF shows blank Stage 1 | Expected — extraction warning banner shown. User should upload a text-based version. |
| Stage 2 ratings seem off | Review via Admin modal; refine Stage 2 prompt and re-run |
| Under the Hood panels missing | Look for `%%%UNDER_HOOD_START%%%` in Stage 2 output; check for yellow parse error banner |
| Go Deeper Trail shows nothing | Check `localStorage.stage2_under_hood` has content; verify `priority.fcv_dimension` matches dimension in recs table |
| Stage 3 missing `refresh_shift` | Check `DEFAULT_PROMPTS["3"]` includes `refresh_shift` in JSON schema |

**Debug steps:**
1. Browser console (F12) for JS errors
2. Flask server logs (Render dashboard) for backend errors
3. Admin modal to inspect exact prompt used for a stage

---

## 15. File Structure

```
FCV-AGENT/
├── app.py                        # Flask backend + DEFAULT_PROMPTS + all routes
├── index.html                    # Single-page frontend (~4000+ lines)
├── background_docs.py            # Knowledge base constants (10 background doc strings)
├── prompts.json                  # Session-specific prompt overrides (empty by default)
├── requirements.txt
├── Procfile
├── README.md                     # Deployment guide for IT
├── CLAUDE.md                     # This file — developer reference
├── docs/
│   ├── reference/
│   │   ├── reference_prompt_architecture.md   # Detailed prompt specs + delimiter schemas
│   │   ├── reference_frontend_functions.md    # JS function list + Express mode
│   │   └── reference_backend_routes.md        # Routes + SSE shapes + parsing signatures
│   └── fcv-agent-knowledge-architecture.html  # Shareable knowledge pipeline diagram
└── tests/
    ├── __init__.py
    └── test_extract_priorities.py
```

Local-only (gitignored — see `.gitignore` and the Repository Structure section above):
```
app_feedback/      # Internal feedback documents
docs/superpowers/  # Dev plans and specs
.claude/           # Local Claude Code config
.superpowers/      # Brainstorming session artifacts
```

---

**Last updated:** 2026-04-19
**Current version:** FCV Project Screener v9.2
**Claude model:** `claude-sonnet-4-6`
**Stack:** Flask 3.0.3 + vanilla JS + Anthropic SDK + gunicorn/gevent on Render
