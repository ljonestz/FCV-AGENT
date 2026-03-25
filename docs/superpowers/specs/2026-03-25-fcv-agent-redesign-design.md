# FCV Agent App Redesign — Design Specification

**Date:** 2026-03-25
**Status:** Draft — pending user review
**Scope:** Full pipeline redesign (prompts, frontend, backend, knowledge base)

---

## 1. Problem Statement

The FCV Project Screener currently uses only a fraction of the WBG's FCV operational guidance. Feedback from an FCV specialist who trialled the app identified these gaps:

- **Incomplete OST Manual coverage:** Only 6 of 12 recommendations used; 25 key questions and 3 key elements untouched
- **Outdated strategy framing:** Responsiveness analysis references old FCV Strategy pillars (preventing conflict, remaining engaged, transition, spillovers) instead of the 4 shifts from the January 2026 FCV Refresh
- **Duplication between stages:** Screening (Stage 2) and Gaps (Stage 3) overlap — gaps are identified twice
- **Missing operational depth:** No integration with the FCV Operational Playbook, which covers diagnostics, preparation, implementation, and closing guidance
- **Terminology ambiguity:** "Strong/Partial/Weak" status labels, undefined "Priority", Do No Harm vs. FCV Sensitivity confusion, narrow "Who Acts" options, vague timing
- **No stage-awareness:** Recommendations are generic regardless of whether the project is at PCN, PAD, or implementation stage

## 2. Design Goals

1. **Full OST Manual integration** — all 12 recommendations, 25 key questions, and 3 key elements drive the analysis internally
2. **FCV Refresh adoption** — the 4 strategic shifts replace old pillars throughout
3. **FCV Playbook integration** — stage-aware recommendations drawing on lifecycle-appropriate guidance
4. **Streamlined pipeline** — 3 stages instead of 4, eliminating duplication
5. **TTL-first output** — clean, actionable findings; framework detail available "under the hood" for FCV CCs
6. **Terminology clarity** — all labels defined, consistent, unambiguous

## 3. Target Audience

**Primary:** Non-specialist Task Team Leaders (TTLs) who need the tool to do the analytical heavy-lifting and deliver actionable, near-final recommendations with minimal FCV expertise.

**Secondary:** FCV Country Coordinators (CCs) who know the framework and want to review the analytical depth behind the recommendations. Served via "Under the Hood" expandable panels.

## 4. Revised Stage Pipeline

### 4.1 Overview

```
Current:  Stage 1 (Extraction) → Stage 2 (Screening) → Stage 3 (Gaps) → Stage 4 (Recommendations)
Proposed: Stage 1 (Context)    → Stage 2 (Assessment)                  → Stage 3 (Recommendations)
```

### 4.2 Stage 1 — Context & Extraction

**Purpose:** Extract FCV-relevant content from uploaded documents, enrich with web research and Playbook diagnostics guidance.

**Input:** Project document (any stage) + optional contextual docs (RRA, country risk assessments).

**Automated pre-processing (unchanged):**
- `extract_country_name()` — LLM call to identify country
- `extract_sector_name()` — LLM call to identify sector
- `run_fcv_web_research(country, sector)` — Anthropic web_search tool, 9 searches, cached by "country::sector"

**Output:**
- Part A: Direct extraction from project document (no outside knowledge)
- Part B: Contextual enrichment (uploaded docs → web research → training knowledge, tiered citations)
- Research brief collapsible dropdown at top (as now)
- **New:** Project stage badge (e.g., "PCN stage detected") — confirms classification for stage-aware recommendations later
- **New:** FCS country indicator if applicable (e.g., "FCS country — PRA/RECA/TAA context noted")
- Document type classification embedded in output: `%%%DOC_TYPE: [type]%%%`

**What's new in Stage 1:**
- Extraction guided by Playbook Diagnostics questions (RRA utilisation, compound risks, forced displacement, CPSD)
- FCV classification context from FCV Refresh (is this an FCS country?)
- Part B enriched with Playbook-aware framing

**Prompt includes:** `FCV_GUIDE`, `PLAYBOOK_DIAGNOSTICS`, `FCV_REFRESH_FRAMEWORK`

**Refine loop available before proceeding.**

### 4.3 Stage 2 — FCV Assessment (merged Screening + Gaps)

**Purpose:** Assess project FCV sensitivity and responsiveness using the full OST framework. Identify gaps and Do No Harm status. Produce both a TTL-facing summary and detailed analytical record.

**Input:** Stage 1 output.

**Internal analytical engine:** All 12 OST recommendations + 25 key questions + 3 key elements. The TTL does NOT see the framework structure — they see themed findings.

**Output structure:**

**TTL-facing (main output area):**
- **Assessment Summary** (400–500 words, thematic narrative):
  - FCV Sensitivity findings: what the project addresses well, where it falls short
  - Do No Harm traffic-light summary (inline): e.g., "Do No Harm: 6 of 8 principles addressed | 1 partial | 1 gap"
  - FCV Responsiveness findings: framed around the 4 FCV Refresh shifts
  - Key gaps: prioritised, 3–5 most critical, with evidence
- **Ratings sidebar:** Sensitivity gauge + Responsiveness gauge (moved from current Stage 4 to Stage 2)
- **S/R classification** with updated terminology:
  - "Strongly addressed / Partially addressed / Weakly addressed / Not addressed" (replaces "Strong/Partial/Weak")

**"Under the Hood" panels (collapsed by default, expandable `<details>`):**
- Panel 1: Full 12-recommendation assessment (table: recommendation | status | evidence | gaps)
- Panel 2: Detailed Do No Harm checklist (8 principles, traffic-light table with evidence)
- Panel 3: 25 key questions mapping (which were answerable, which had gaps, evidence for each)
- Panel 4: Evidence trail (sources used, citation tier for each finding)

**Responsiveness framing in Stage 2:**
The responsiveness assessment replaces the old pillar-by-pillar probe with a shift-by-shift analysis:
- For each of the 4 FCV Refresh shifts, assess whether the project aligns with, has potential for, or does not engage with that shift
- The TTL-facing summary presents this as a narrative ("The project has strong alignment with Shift B (differentiated engagement) given its crisis-context design, but does not address Shift C (jobs/private sector)...")
- The "Under the Hood" Panel 1 (12-rec table) includes a column mapping each recommendation to its most relevant shift(s)

**Do No Harm — canonical 8 principles:**
1. Conflict-sensitive targeting and beneficiary selection
2. Avoiding reinforcement of existing power asymmetries
3. Preventing exacerbation of inter-group tensions
4. Ensuring equitable geographic distribution of benefits
5. Safeguarding against elite capture of project resources
6. Protecting project staff and beneficiaries from security risks
7. Monitoring for unintended negative consequences
8. Establishing accessible and trusted grievance mechanisms

**Delimiter structure for LLM output:**
```
[TTL-facing summary — rendered in main output area]

%%%STAGE2_RATINGS_START%%%
{"sensitivity_rating": "Adequate", "responsiveness_rating": "Low"}
%%%STAGE2_RATINGS_END%%%

%%%UNDER_HOOD_START%%%
%%%RECS_TABLE_START%%%
[Full 12-recommendation assessment table in Markdown]
%%%RECS_TABLE_END%%%
%%%DNH_CHECKLIST_START%%%
[Detailed Do No Harm checklist — 8 principles, traffic-light table]
%%%DNH_CHECKLIST_END%%%
%%%QUESTIONS_MAP_START%%%
[25 key questions with findings]
%%%QUESTIONS_MAP_END%%%
%%%EVIDENCE_TRAIL_START%%%
[Evidence trail — sources, tiers, confidence]
%%%EVIDENCE_TRAIL_END%%%
%%%UNDER_HOOD_END%%%
```

Frontend parses and routes content:
- TTL summary → main output area
- Ratings JSON → sidebar gauges (parsed via `extract_stage2_ratings()`)
- Under the Hood blocks → expandable `<details>` panels
- Under the Hood raw text also stored in `localStorage` key `stage2_under_hood` for use by "Go Deeper" analytical trail tab (no round-trip to backend needed)

**SSE done-event payload for Stage 2:**
```json
{
    "done": true,
    "output": "full raw LLM text",
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

**Error handling for Stage 2 parsing:**
If `extract_under_hood()` fails (missing delimiters, malformed blocks):
- Return `parse_error: true` with message in SSE done event
- Frontend renders raw Stage 2 text as-is (no panel routing)
- Yellow warning banner at top: "Assessment detail could not be parsed into panels. Full output shown below."
- "Under the Hood" section shows raw text in a single expandable `<details>` as fallback
- Stage 3 can still proceed — it uses conversation history, not parsed panels

**Prompt includes:** `FCV_OPERATIONAL_MANUAL` (full 12 recs + 25 questions), `FCV_REFRESH_FRAMEWORK`, `FCV_GUIDE`

**Refine loop available before proceeding.**

### 4.4 Stage 3 — Recommendations Note (enhanced, stage-aware)

**Purpose:** Generate a formal, memo-ready Recommendations Note with actionable priority cards, tailored to the project's lifecycle stage.

**Input:** Stages 1–2 output + detected project stage (from Stage 1 `%%%DOC_TYPE%%%`).

**Stage-awareness logic:**
| Detected doc type | Playbook source | Timing emphasis | Example recommendation framing |
|---|---|---|---|
| PCN / PID | `PLAYBOOK_PREPARATION` | Identification / Preparation | "Build into the ToC now", "Flag at QER" |
| PAD | `PLAYBOOK_PREPARATION` | Preparation / Appraisal | "Revise Section X", "Add to ESCP Commitment Y" |
| AF / Restructuring | `PLAYBOOK_IMPLEMENTATION` | Implementation / Restructuring | "Add as restructuring condition", "Revise results framework" |
| ISR | `PLAYBOOK_IMPLEMENTATION` | Implementation | "Flag in next ISR", "Adjust during next restructuring" |
| Unknown | `PLAYBOOK_PREPARATION` | Preparation (safe default) | Generic framing |

**Output — narrative memo (same structure as current Stage 4, enhanced):**
- Preamble (50–75 words)
- Opening Assessment (1 bold sentence)
- Operational Context (150–200 words)
- FCV Risk Exposure (risks TO project + risks FROM project)
- Strengths (80–120 words)
- Gaps (100–130 words)
- FCV Sensitivity Summary (80–100 words) — extracted to summary card
- FCV Responsiveness Summary (80–100 words) — extracted to summary card
- FCV Sensitivity Rating (Extremely Low → Very Well Embedded scale)
- FCV Responsiveness Rating (same scale)
- **New:** Project stage badge (e.g., "Recommendations tailored for PCN stage")

**Priority cards — "Priority actions for the Task Team" (4–5 priorities):**

Each priority includes:

| Field | Description | Change from current |
|---|---|---|
| `title` | Priority N · [Actionable verb phrase] | No change |
| `fcv_dimension` | One of 6 dimensions | No change |
| `tag` | [S] / [R] / [S+R] | No change |
| `refresh_shift` | Which of the 4 FCV Refresh shifts this aligns with | **New** |
| `risk_level` | High / Medium / Low | No change |
| `the_gap` | 2–3 sentences naming document section | No change |
| `why_it_matters` | 2–3 sentences + shift justification for [R]/[S+R] | Updated framing |
| `recommendation` | Single cohesive action, 4–6 sentences | No change |
| `who_acts` | TTL / PIU / Government / FCV CC / FM Team / ESF Team / Technical Team / M&E Team | **Expanded** |
| `when` | Identification / Preparation / Appraisal / Implementation / Restructuring | **Expanded** |
| `resources` | Minimal (existing budget) / Moderate (dedicated allocation) / Significant (requires restructuring) | **Definitions added** |
| `pad_sections` | Semicolon-separated PAD section names | No change |
| `suggested_language` | 2–4 sentences of draft WBG-register text | No change |
| `implementation_note` | 1–2 sentences on timing/cost/dependency | No change |

**JSON block** appended after narrative (same `%%%JSON_START/END%%%` pattern), with all fields above plus `fcv_rating`, `fcv_responsiveness_rating`, `sensitivity_summary`, `responsiveness_summary`, `risk_exposure` (nested: `{"risks_to": "...", "risks_from": "..."}`).

**Field naming resolution (breaking from current code for consistency):**
- `fcv_dimension` — canonical name going forward (current code uses `dimension`; rename during migration)
- `risk_exposure` — always a nested object `{risks_to, risks_from}` (current code has flat `risk_to_project`/`risk_from_project` in some places; standardise to nested)
- `who_acts` — **multi-value field**, semicolon-separated (e.g., `"TTL; ESF Team"`). This is a change from the current single-value behaviour.

**"Go Deeper" per priority** (replaces current Explorer, lazy-loaded `<details>`):
- **Tab 1 — Alternative approaches:** 2–3 optional alternatives (same as current Explorer content)
- **Tab 2 — Analytical trail:** Which OST recs/questions drove this priority, with evidence. Sourced from Stage 2 "Under the Hood" data — **no API call needed**, filtered from cached Stage 2 output
- **Tab 3 — Playbook references:** Relevant operational flexibilities, policy citations, implementation guidance. Lightweight LLM call matching priority against Playbook content

**Follow-on card** (unchanged): peer review chip, expand recommendation, review revised text, summarise for brief.

**Download:** Always complete from JSON, includes all enhanced fields. No click-through needed. Optionally appends "Go Deeper" content if already loaded.

**Prompt includes:** `STAGE_GUIDANCE_MAP` (matched to doc type), relevant `PLAYBOOK_PREPARATION` or `PLAYBOOK_IMPLEMENTATION`, `FCV_REFRESH_FRAMEWORK`

**Citation policy (unchanged):** Only cite documents that appeared as `[From: doc name]` in Stage 1. Non-uploaded sources → `[From: training knowledge]` or `[From: web research]`.

## 5. Backend Changes

### 5.1 Routes

| Route | Method | Change |
|---|---|---|
| `/api/run-stage` | POST | Stage numbering updated (1–3). Stage 2 = merged assessment. Stage 3 = recommendations. |
| `/api/run-deeper` | POST | **Renamed** from `/api/run-explorer`. Accepts `tab` parameter for 3 content types. |
| `/api/run-followon` | POST | No change |
| `/api/admin/prompts` | GET/POST | Prompt keys updated: `"1"`, `"2"`, `"3"`, `"deeper"`, `"followon"` |
| `/api/default-prompts` | GET | Updated keys |
| `/api/admin/prompts/reset` | POST | Updated keys |

### 5.2 `/api/run-deeper` Route

```
POST /api/run-deeper
{
    "priority_index": 0,
    "tab": "alternatives" | "analytical_trail" | "playbook_refs",
    "priority_title": "...",
    "priority_body": "...",
    "history": [...],
    "stage2_under_hood": "..."  // only needed for analytical_trail tab
}
```

- `tab: "alternatives"` — SSE-streamed LLM call using `DEFAULT_PROMPTS["deeper"]`, same as current Explorer (2–3 alternative approaches)
- `tab: "analytical_trail"` — **no LLM call**; filters Stage 2 "Under the Hood" data by priority's `fcv_dimension`. Filtering logic: match `fcv_dimension` against rec table rows (each row's dimension column) and key questions (each question's thematic area). Return all matching rows/questions. If a priority spans multiple dimensions (rare), match on primary dimension only.
- `tab: "playbook_refs"` — SSE-streamed LLM call using `DEFAULT_PROMPTS["deeper_playbook"]`. Prompt receives the priority JSON + the stage-appropriate Playbook constant (`PLAYBOOK_PREPARATION` or `PLAYBOOK_IMPLEMENTATION` based on `doc_type`) and returns relevant operational flexibilities, policy citations, and implementation guidance specific to this priority.

**Note:** `analytical_trail` data is sent from the frontend (stored in `localStorage` key `stage2_under_hood` after Stage 2 completes). The backend does not re-parse Stage 2 output — it receives pre-parsed text sections from the frontend and filters them.

### 5.3 Stage-Awareness Injection

```python
# In /api/run-stage handler, when stage == "3":
doc_type = request_data.get("doc_type", "Unknown")

STAGE_MAP = {
    "PCN": {"playbook": PLAYBOOK_PREPARATION, "timing": "Identification / Preparation"},
    "PID": {"playbook": PLAYBOOK_PREPARATION, "timing": "Identification / Preparation"},
    "PAD": {"playbook": PLAYBOOK_PREPARATION, "timing": "Preparation / Appraisal"},
    "AF":  {"playbook": PLAYBOOK_IMPLEMENTATION, "timing": "Implementation / Restructuring"},
    "Restructuring": {"playbook": PLAYBOOK_IMPLEMENTATION, "timing": "Implementation / Restructuring"},
    "ISR": {"playbook": PLAYBOOK_IMPLEMENTATION, "timing": "Implementation"},
}
config = STAGE_MAP.get(doc_type, {"playbook": PLAYBOOK_PREPARATION, "timing": "Preparation"})

# Inject into Stage 3 prompt via string formatting
```

### 5.4 `extract_priorities()` Updates

- Parse new `refresh_shift` field from JSON
- Updated `who_acts` validation: `TTL | PIU | Government | FCV CC | FM Team | ESF Team | Technical Team | M&E Team`
- Updated `when` validation: `Identification | Preparation | Appraisal | Implementation | Restructuring`
- `resources` string includes parenthetical definition — strip for badge display, keep for download
- All existing validation (specificity check, citation check) unchanged

### 5.5 Stage 2 Output Parsing

New function `extract_under_hood(stage2_output)`:
- Finds `%%%UNDER_HOOD_START%%%` ... `%%%UNDER_HOOD_END%%%` block
- Extracts sub-blocks: recs table, DNH checklist, questions map, evidence trail
- Returns structured dict for frontend rendering and "Go Deeper" analytical trail tab
- Strips "Under the Hood" block from main display text (same pattern as `clean_stage4_output()`)

### 5.6 `DEFAULT_PROMPTS` Keys

```python
DEFAULT_PROMPTS = {
    "1": "...",              # Stage 1: Context & Extraction
    "2": "...",              # Stage 2: FCV Assessment
    "3": "...",              # Stage 3: Recommendations Note
    "deeper": "...",         # Go Deeper: Alternative approaches (Tab 1)
    "deeper_playbook": "...",# Go Deeper: Playbook references (Tab 3)
    "followon": "...",       # Follow-on: Post-analysis tasks
}
```

**Note:** `analytical_trail` (Tab 2) has no prompt — it is a frontend-only data filter, no LLM call.

## 6. Knowledge Base Expansion (`background_docs.py`)

### 6.1 New and Updated Constants

| Constant | Source | Est. tokens | Purpose |
|---|---|---|---|
| `FCV_GUIDE` | Existing, updated | ~3,000 | Core S/R framework — updated with FCV Refresh framing, old pillars removed |
| `FCV_OPERATIONAL_MANUAL` | Existing, expanded | ~5,000 | Full 12 recs + 25 key questions + 3 key elements (currently only 6 recs) |
| `FCV_REFRESH_FRAMEWORK` | **New** — from Jan 2026 Strategy briefing | ~1,500 | 4 shifts, new classification scheme, FCV-sensitive vs FCV-responsive definitions |
| `PLAYBOOK_DIAGNOSTICS` | **New** — from Playbook Diagnostics doc | ~2,000 | RRA guidance, data sources, compound risks, analytical questions |
| `PLAYBOOK_PREPARATION` | **New** — from Playbook Preparation doc | ~3,000 | Operational flexibilities, policy refs, design guidance, M&E, FM/procurement |
| `PLAYBOOK_IMPLEMENTATION` | **New** — from Playbook Implementation doc | ~2,500 | TPM, GEMS, stakeholder engagement, security sector, adaptation |
| `PLAYBOOK_CLOSING` | **New** — from Playbook Closing doc | ~1,500 | ICR guidance, impact evaluation, results assessment in FCV. **Used only for ISR doc types** — injected into Stage 3 when `doc_type == "ISR"`. Also available to "Go Deeper" playbook_refs tab. Reserved for future use if app adds a closing/ICR assessment stage. |
| `STAGE_GUIDANCE_MAP` | **New** — synthesised | ~800 | Maps doc_type → relevant constants + timing emphasis |

**Total new background content:** ~20k tokens.

### 6.2 Token Budget per Stage (revised — includes prompt text + conversation history)

Each stage loads only what it needs. Estimates include background constants + prompt instructions + typical conversation history:

| Stage | Constants | Prompt text | Conv. history | Total input est. | Output est. |
|---|---|---|---|---|---|
| Stage 1 | ~6,500 | ~2,000 | ~500 (user docs separate) | ~9,000 | ~2,000–3,000 |
| Stage 2 | ~9,500 | ~3,000 | ~3,000–5,000 (Stage 1 output) | ~15,500–17,500 | ~3,000–4,000 |
| Stage 3 | ~5,500 | ~3,000 | ~6,000–8,000 (Stages 1+2) | ~14,500–16,500 | ~3,000–4,000 |

**Stage 2 is the heaviest call.** At ~17k input + ~4k output, this is within Claude Sonnet's capabilities but warrants monitoring. If output quality degrades (rushed "Under the Hood" panels), the fallback is to split into two sequential calls: (1) full detailed assessment, (2) TTL summary from the detail. This adds latency (~15-20s extra) but improves quality.

### 6.3 `background_docs.py` File Structure

All constants remain in a single `background_docs.py` file (consistent with current architecture). If the file exceeds ~2,000 lines, consider splitting into `background_docs_playbook.py` — but this is a future optimisation, not a launch requirement.

### 6.3 Content Distillation Principle

Playbook content is **distilled for prompt use**, not raw document text. Each constant is a structured, token-efficient reference that preserves:
- Key questions and decision criteria
- Specific operational mechanisms (named: CERC, HEIS, TPM, GEMS, etc.)
- Policy references (OP 7.30, OP 8.00, Para 12 IPF, etc.)
- Named actors, tools, and resources

But removes:
- Narrative padding, introductions, transitions
- Repeated cross-references
- Contact details and URLs (not useful in prompts)
- "Text forthcoming" placeholders

## 7. Frontend Changes

### 7.1 Stage Stepper
- **3 steps** instead of 4: Context → Assessment → Recommendations
- Same visual pattern (progress bar, coloured stage indicators)
- Stage colours: s1 (blue), s2 (amber), s3 (green) — or keep existing palette

### 7.2 Stage 1 UI (minimal changes)
- Web research dropdown at top (unchanged)
- Part A / Part B output (unchanged)
- Refine input box (unchanged)
- **New:** Project stage badge below output (e.g., "PCN stage detected")
- **New:** FCS country indicator if applicable

### 7.3 Stage 2 UI (new layout)
- **Main output:** Assessment Summary (thematic narrative, ~400–500 words)
  - Includes inline DNH traffic-light: "Do No Harm: 6 of 8 principles addressed | 1 partial | 1 gap"
- **Ratings sidebar:** Sensitivity gauge (blue, shield) + Responsiveness gauge (green, leaf) — moved from current Stage 4
- **"Under the Hood" panels:** 4 expandable `<details>` sections (same interaction pattern as current Explorer)
  - Full 12-rec assessment
  - Detailed DNH checklist
  - 25 key questions mapping
  - Evidence trail
- **Refine input box**

### 7.4 Stage 3 UI (enhanced current Stage 4)
- Main output: narrative memo (largely unchanged layout)
- **New:** Project stage badge (e.g., "Recommendations tailored for PCN stage")
- **Priority cards** — "Priority actions for the Task Team":
  - Same zone-act layout (recommendation, PAD sections, suggested language, implementation note)
  - Enhanced fields: `refresh_shift` badge, expanded `who_acts`, expanded `when`, `resources` with tooltip definitions
  - S/R tag badges with hover tooltips (unchanged)
  - Specificity + citation warning badges (unchanged)
- **"Go Deeper"** per priority (replaces Explorer):
  - Outer container: `<details class="go-deeper">` (same expand pattern as current Explorer)
  - Inside the `<details>`: **3 tab buttons** (styled as pill tabs, not nested `<details>`)
    - Tab 1: "Alternative approaches" (default active on open)
    - Tab 2: "Analytical trail"
    - Tab 3: "Playbook references"
  - Tab content area below buttons, swapped on tab click
  - `analytical_trail` tab renders instantly from `localStorage.stage2_under_hood` (no API call)
  - `alternatives` and `playbook_refs` tabs lazy-loaded via SSE on first open, with loading spinner + cancel button
  - All 3 tabs cached in localStorage per priority index per tab type (keys: `deeper_{idx}_alternatives`, `deeper_{idx}_trail`, `deeper_{idx}_playbook`)
- **Follow-on card** (unchanged)
- **Download** (unchanged — always complete from JSON)

### 7.5 Terminology Updates (throughout UI)
| Current | Proposed |
|---|---|
| "Strong / Partial / Weak" | "Strongly addressed / Partially addressed / Weakly addressed / Not addressed" |
| "Priority" (unlabelled) | "Priority actions for the Task Team" |
| "Do No Harm Checklist" (standalone) | DNH traffic-light inline in Stage 2 + detailed checklist in "Under the Hood" |
| Old 4 pillars in responsiveness | FCV Refresh 4 shifts |
| "Who Acts": TTL / PIU / Government / FCV specialist / Procurement | TTL / PIU / Government / FCV CC / FM Team / ESF Team / Technical Team / M&E Team |
| "When": At design stage / Before appraisal / During implementation | Identification / Preparation / Appraisal / Implementation / Restructuring |
| "Resources": Minimal / Moderate / Significant | Minimal (existing budget) / Moderate (dedicated allocation) / Significant (requires restructuring) |
| "Explorer" / "Above and beyond" | "Go Deeper" |

### 7.6 Removed from UI
- Stage 2 (Screening) and Stage 3 (Gaps) as separate stages
- Stage 4 numbering (becomes Stage 3)
- Old 4-pillar responsiveness references
- Standalone Do No Harm Checklist section (folded into Stage 2)

### 7.7 Preserved (no change)
- Onboarding modal (disclaimer + AI limitations)
- Session management (save/load/resume in localStorage)
- Prompt admin modal (updated to show 3 stage prompts + deeper + followon)
- SSE streaming for all LLM calls
- Conversation history passed between stages
- Styling, typography, WBG colour palette
- Priority card zone-act layout (recommendation, PAD sections chips, suggested language, implementation note)

## 8. FCV Refresh Integration

### 8.1 The 4 Strategic Shifts (replacing old pillars)

| Shift | Focus | How it maps to project-level assessment |
|---|---|---|
| **Shift A: Anticipate** | New FCV classification, AI-enabled Fragility Index, early warning | Does the project design reflect current fragility classification? Does it anticipate deterioration scenarios? |
| **Shift B: Differentiate** | Crisis / transition / prevention contexts; lasting impact potential | Is the project calibrated to the country's FCV trajectory? Does it differentiate its approach based on context type? |
| **Shift C: Jobs & private sector** | Foundations, business enabling, private sector financing | Does the project address economic livelihoods and job creation as a stability pathway? Are private sector entry points identified? |
| **Shift D: Enhanced toolkit** | OP7.30, TPIs, FCV sensitivity tag, partnerships, talent | Does the project leverage available operational flexibilities? Are implementation arrangements FCV-appropriate? |

### 8.2 Where Shifts Appear in the App
- **Stage 2:** Responsiveness assessment framed around the 4 shifts (replaces old pillar-by-pillar analysis)
- **Stage 3:** Each priority card includes a `refresh_shift` badge showing alignment
- **Stage 3 "Go Deeper":** Playbook references tab maps to shift-relevant operational guidance
- **Sensitivity/Responsiveness summary cards:** Updated framing language

### 8.3 S/R Classification (updated)
- [S] = FCV Sensitivity — project avoids doing harm, is contextually aware, conflict-informed
- [R] = FCV Responsiveness — project actively addresses fragility drivers or builds resilience, aligned to one or more of the 4 shifts
- [S+R] = Genuine overlap (strict definition unchanged): (1) inclusion/targeting of conflict-affected populations, (2) FCV logic in ToC/PDO, (3) adaptive M&E for harm + resilience, (4) GRM for state-citizen accountability

## 9. Migration & Compatibility

### 9.1 Breaking Changes
- Stage numbering changes (2→merged, 3→removed, 4→3) — existing saved sessions will not map cleanly
- Prompt keys change (`"4"` → `"3"`, `"explorer"` → `"deeper"`)
- JSON schema adds `refresh_shift`, changes `who_acts`/`when`/`resources` value sets
- "Under the Hood" delimiter blocks are new — old sessions won't have them

### 9.2 Migration Strategy
- **Existing saved sessions:** On load, detect old format (presence of stage `"4"` key in history or absence of `stage2_under_hood` in localStorage). Show a one-time banner: "This session was created with an earlier version of the screener. To use the new assessment framework, please start a new session. Your old session data is preserved." No dual rendering paths — old sessions display raw text only, without panel routing or gauge extraction.
- **`prompts.json` session overrides:** Clear on upgrade (overrides are session-scoped anyway)
- **No database migration needed** (localStorage only)
- **Error messages:** Update all references from "Stage 4" to "Stage 3" in `extract_priorities()` error messages and frontend parse-error banners

## 10. Prompt Skeleton Outlines

These are structural outlines for the prompt rewrites — not final prompt text, but enough to guide implementation.

### 10.1 Stage 1 Prompt Skeleton

```
# Role
You are an expert FCV analyst for the World Bank Group.

# Context injected
{FCV_GUIDE}
{PLAYBOOK_DIAGNOSTICS}
{FCV_REFRESH_FRAMEWORK}

# Task
Analyse the uploaded project document(s) in two strictly separated parts.

## Part A — Project Document Extraction
[Same structure as current: Direct FCV References, Implicit Indicators, Design Elements,
 Risk Assessments, Geographic Context, Data Gaps]
NEW: Guided by Playbook diagnostic questions — specifically flag:
- Whether project references or uses an RRA
- Compound risk indicators
- Forced displacement considerations
- Private sector diagnostic alignment

## Part B — Contextual Enrichment
[Same tiered citation structure: Tier 1 uploaded → Tier 2 web research → Tier 3 training]
NEW: Frame gaps against FCV Refresh classification context
NEW: Flag if country is on FCS list and note PRA/RECA/TAA eligibility

## Output format
[Same as current, ending with %%%DOC_TYPE: [type]%%%]
```

### 10.2 Stage 2 Prompt Skeleton

```
# Role
You are an expert FCV analyst conducting a comprehensive FCV assessment.

# Context injected
{FCV_OPERATIONAL_MANUAL}  — full 12 recommendations, 25 key questions, 3 key elements
{FCV_REFRESH_FRAMEWORK}   — 4 strategic shifts
{FCV_GUIDE}               — S/R definitions

# Task
Using the Stage 1 analysis, assess this project's FCV sensitivity and responsiveness.

## Internal analytical framework (use but do NOT expose to user in main summary)
- Assess against ALL 12 OST recommendations (not just 6)
- Answer ALL 25 key questions where evidence permits
- Evaluate the 3 key elements

## TTL-facing output (main summary, 400-500 words)
Structure thematically, NOT recommendation-by-recommendation:
1. FCV Sensitivity findings (what's addressed, what's missing)
2. Do No Harm traffic-light (inline count against 8 principles)
3. FCV Responsiveness findings — assess against each of the 4 Refresh shifts:
   - Shift A (Anticipate): Does project reflect fragility classification? Deterioration scenarios?
   - Shift B (Differentiate): Calibrated to FCV trajectory?
   - Shift C (Jobs/private sector): Economic livelihoods pathway?
   - Shift D (Enhanced toolkit): Operational flexibilities leveraged?
4. Key gaps (3-5 most critical, prioritised)

## Status terminology
Use ONLY: "Strongly addressed" | "Partially addressed" | "Weakly addressed" | "Not addressed"

## Ratings
Emit: %%%STAGE2_RATINGS_START%%%{"sensitivity_rating": "...", "responsiveness_rating": "..."}%%%STAGE2_RATINGS_END%%%
Scale: Extremely Low | Very Low | Low | Adequate | Well Embedded | Very Well Embedded

## Under the Hood (detailed panels)
Emit between %%%UNDER_HOOD_START%%% and %%%UNDER_HOOD_END%%% delimiters:
- %%%RECS_TABLE_START/END%%%: All 12 recs as Markdown table
  Columns: # | Recommendation | Status | Evidence | Gaps | Relevant Shift(s)
- %%%DNH_CHECKLIST_START/END%%%: 8 DNH principles as traffic-light table
  Columns: Principle | Status (Yes/Partial/No) | Evidence/Gap
- %%%QUESTIONS_MAP_START/END%%%: 25 questions with findings
  Columns: # | Question | Answerable? | Finding | Source
- %%%EVIDENCE_TRAIL_START/END%%%: Source inventory
  Columns: Source | Type (uploaded/web/training) | Used for
```

### 10.3 Stage 3 Prompt Skeleton

```
# Role
You are an expert FCV analyst producing a formal Recommendations Note.

# Context injected
{STAGE_GUIDANCE_MAP} — matched to detected doc_type
{PLAYBOOK_PREPARATION} or {PLAYBOOK_IMPLEMENTATION} — stage-dependent
{FCV_REFRESH_FRAMEWORK}

# Task
Generate a memo-ready Recommendations Note with stage-appropriate guidance.

## Stage awareness
This project is at {doc_type} stage. Tailor all recommendations accordingly:
- Timing options: {timing_emphasis}
- Use stage-appropriate language (e.g., "Build into ToC" for PCN, "Revise PAD Section X" for PAD)
- Reference relevant operational flexibilities from the Playbook

## Narrative sections
[Same structure as current Stage 4: Preamble, Opening Assessment, Operational Context,
 Risk Exposure, Strengths, Gaps, S/R Summaries, Ratings]

## Priority cards — "Priority actions for the Task Team"
4-5 priorities, each as JSON with fields:
- title, fcv_dimension, tag, refresh_shift, risk_level, the_gap, why_it_matters,
  recommendation, who_acts, when, resources, pad_sections, suggested_language,
  implementation_note

## Field constraints
- who_acts: semicolon-separated from [TTL, PIU, Government, FCV CC, FM Team, ESF Team, Technical Team, M&E Team]
- when: one of [Identification, Preparation, Appraisal, Implementation, Restructuring]
- resources: one of ["Minimal (existing budget)", "Moderate (dedicated allocation)", "Significant (requires restructuring)"]
- refresh_shift: one of ["Shift A: Anticipate", "Shift B: Differentiate", "Shift C: Jobs & private sector", "Shift D: Enhanced toolkit"]
- recommendation: SINGLE cohesive action, NOT an options menu
- fcv_dimension: one of [Institutional Legitimacy, Inclusion, Social Cohesion, Security, Economic Livelihoods, Resilience]

## JSON block
Emit between %%%JSON_START%%% and %%%JSON_END%%% delimiters.
[Same structure as current, with new fields added]

## Citation policy
[Same as current — only cite uploaded docs or whitelist orgs]
```

### 10.4 Go Deeper — Alternatives Prompt Skeleton

```
# Role
Same as current Explorer prompt.

# Task
Generate 2-3 optional alternative approaches that go BEYOND the core recommendation.
[Same %%%GO_FURTHER_START/END%%% and %%%GF_ITEM/TITLE%%% format as current]

# Key change from current
- Reference FCV Refresh shifts where relevant
- Updated who_acts vocabulary
```

### 10.5 Go Deeper — Playbook References Prompt Skeleton

```
# Role
You are an FCV operational specialist helping a Task Team apply WBG guidance.

# Context injected
{PLAYBOOK_PREPARATION} or {PLAYBOOK_IMPLEMENTATION} — matched to doc_type

# Task
For the given priority, identify and explain:
1. Relevant operational flexibilities (name the mechanism: CERC, HEIS, TPM, GEMS, etc.)
2. Applicable policy references (OP 7.30, OP 8.00, Para 12 IPF, etc.)
3. Implementation guidance specific to this priority's FCV dimension and context
4. Named WBG resources or teams that can support (e.g., GEMS team, OPCS UN Program)

# Output format
Structured prose, 300-500 words. NOT bullet lists.
Reference specific Playbook sections where possible.
```

### 10.6 Follow-on Prompt Skeleton

```
[Same as current, with two updates:]
1. Replace old FCV Strategy pillar references with FCV Refresh 4 shifts
2. When drafting peer review notes, reference the expanded assessment
   (12 recs, not just 6) and use updated terminology
```

## 11. Implementation Phases (suggested)

### Phase 1: Knowledge Base
- Distil and write all new `background_docs.py` constants
- Update `FCV_GUIDE` with Refresh framing
- Expand `FCV_OPERATIONAL_MANUAL` to full 12 recs + 25 questions

### Phase 2: Prompts
- Rewrite Stage 1 prompt (add Playbook Diagnostics, Refresh context)
- Write new Stage 2 prompt (merged assessment, full OST framework, "Under the Hood" delimiters)
- Rewrite Stage 3 prompt (stage-awareness, expanded fields, Playbook integration)
- Write "Go Deeper" alternatives prompt (replaces Explorer)
- Update Follow-on prompt (Refresh framing)

### Phase 3: Backend
- Update `/api/run-stage` route for 3-stage pipeline
- Add `extract_under_hood()` parser
- Update `extract_priorities()` for new JSON fields
- Add `/api/run-deeper` route with 3 tab types
- Implement stage-awareness injection logic
- Update admin routes for new prompt keys

### Phase 4: Frontend
- Update stepper (3 stages)
- Build Stage 2 UI (assessment summary + "Under the Hood" panels)
- Update Stage 3 UI (enhanced priority cards, "Go Deeper" with 3 tabs, terminology)
- Update sidebar (gauges move to Stage 2)
- Terminology updates throughout
- Update download function for new fields

### Phase 5: Testing & Polish
- End-to-end test with Guinea example (colleague's test case)
- Token budget validation per stage
- Session save/load with new structure
- Legacy session handling
- Prompt quality review (specificity, actionability, stage-awareness)

## 11. Future Option: Recommendations-First (Approach B)

If token limits and quality prove manageable, a future iteration could collapse to 2 stages:
- Stage 1: Context & Extraction (unchanged)
- Stage 2: Assessment + Recommendations in one step (assessment runs internally, user sees recommendations directly)

This would be the fastest path to value for TTLs but requires careful token management and may reduce quality control opportunities. Preserved as a design option for after the current redesign is validated.

## 12. Key References

| Document | Location | Role |
|---|---|---|
| Colleague's feedback | `app_feedback/Feedback on FCV Agent.docx` | Requirements source |
| OST Manual | `Claude_Outputs/OST Manual/FCV Operational Manual for FCV CCs - June 2025.docx` | Primary analytical framework (12 recs, 25 questions, 3 key elements) |
| FCV Playbook — Diagnostics | `Claude_Outputs/FCV Playbook/OperationalPlaybook_DiagnosticsPageText.docx` | Stage 1 enrichment |
| FCV Playbook — Preparation | `Claude_Outputs/FCV Playbook/OperationalPlaybook_PreperationPageText_WorkingFile.docx` | Stage 3 enrichment (PCN/PAD projects) |
| FCV Playbook — Implementation | `Claude_Outputs/FCV Playbook/OperationalPlaybook_ImplementationPageText_WorkingFile.docx` | Stage 3 enrichment (AF/ISR projects) |
| FCV Playbook — Closing | `Claude_Outputs/FCV Playbook/OperationalPlaybook_ProjectClosing_WorkingFile_CLEAN.docx` | ICR/closing guidance |
| FCV Refresh Strategy | `AppData/Local/Temp/FCV-strategy-update and next steps-2026-01-20-internal briefing.pptx` | 4 shifts framework |
| Current app | `app.py`, `index.html`, `background_docs.py` | Baseline to modify |

---

*Generated 2026-03-25. This spec covers the full redesign of the FCV Project Screener from a 4-stage to a 3-stage pipeline, integrating the complete OST Manual, FCV Operational Playbook, and FCV Refresh strategic shifts.*
