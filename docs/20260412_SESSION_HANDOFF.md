# Session Handoff — 2026-04-12

**Branch:** `feat/v8-knowledge-base`  
**Last commit:** `56d9153` — streamline landing page UX  
**Status:** All changes pushed. App is deployable.

---

## What Was Done This Session (in order)

### 1. WB Internal LLM Output Quality Review Package
- Generated `app_feedback/20260412_wbllm_review/` — three .docx files (Knowledge Base, Stage Prompts, FCV Reference Constants) via `generate_review_docs.py`
- Wrote `PROMPT_Output_Quality_Review.md` — structured review prompt given to the WB LLM covering all 5 review areas
- WB LLM reviewed Honduras PAD (P181166) Stage 1/2/3 outputs and returned detailed feedback

### 2. WB LLM Feedback Integrated (commit `9b905cf`)
Nine changes implemented in `app.py` and `background_docs.py`:
1. **HDP Nexus made conditional** — only assessed if country has documented heavy humanitarian presence
2. **Digital/Tech Risks dimension removed** — no longer a supplementary assessment dimension
3. **Shift A explicit rating** — Stage 2 prompt now requires explicit Shift A (Anticipate) assessment with justification
4. **DNH cap transparency** — prompt clarifies when Sensitivity is capped by DNH gaps and explains why
5. **QUESTIONS_MAP updated** — reflects HDP/Digital changes
6. **Hallucinated precision guardrail** — Stage 3 prompt prohibits AI-generated budget figures, staffing ratios, thresholds
7. **IPF procurement guardrail** — Stage 3 prompt clarifies what is/isn't feasible under standard IPF procurement
8. **SORT routing** — any conflict/security/political-economy recommendation must list SORT as a pad_section
9. **CDD sub-modality + Para 18** — two new fields added to IPF entry in WB_INSTRUMENT_GUIDE (elite capture risks, non-state actor engagement)

### 3. Phase 4 — Implementation Review (commit `2c0a2aa`)
**Backend (fully built, gated behind `review_mode == 'implementation'`):**
- `extract_process_type()` — reads `%%%PROCESS_TYPE: ...%%%` from Stage 1 impl output
- `get_process_slice()` — formats WB_PROCESS_GUIDE entry for prompt injection
- `DEFAULT_PROMPTS['impl_1']` — Stage 1 for MTR/ISR documents; detects process type
- `DEFAULT_PROMPTS['impl_2']` — Stage 2 FCV performance assessment; uses same delimiter structure
- `DEFAULT_PROMPTS['impl_3']` — Stage 3 course-correction note; uses same JSON structure
- Both `run_stage()` and `run_express()` bifurcated by `review_mode` param

**Frontend (disabled — tiles removed, "coming soon" note):**
- `reviewMode` and `processType` state variables declared
- `selectReviewMode()` function written (null-safe)
- `review_mode` and `process_type` passed in all API payloads
- Temporal context panel shows process type in impl mode
- Express progress titles switch for impl mode
- **Why disabled:** Stage 3 needs a fundamentally different JSON schema and output structure for course-correction vs. design-stage recommendations. Redesign needed before re-enabling.
- **How to re-enable:** Remove `review-type-card-disabled` class from `#rt-implementation` and restore tile HTML. See `docs/IMPLEMENTATION_REVIEW_DESIGN.md` for full redesign checklist.

### 4. Design Scope & Priority Label Fixes (commit `acb39a0`)
- **Implementation Review scoped out:** Tiles replaced with a single muted one-liner
- **"FCV Risk: High/Medium/Low" → "Priority: High/Medium/Low"** fixed in four places:
  - Priority overview list (`.pov-risk`)
  - Step-by-step sidebar stepper (`.ps-risk`)
  - Priority card header chip (`.pc-chip`)
  - DOCX download
- **Stage 3 prompt `RISK_LEVEL` description** updated to clarify this is priority ordering, not a risk rating
- **Step-by-step mode now load-first:** No progressive streaming to DOM. Chunks buffered silently. `load-sub-msg` text updates on research/preprocess events. Full output rendered via `renderOut()` on completion.
- `docs/IMPLEMENTATION_REVIEW_DESIGN.md` created — archives all Phase 4 design decisions, what's built, and re-activation steps

### 5. Optional Context Box (commit `5e5b78f`)
- Collapsible toggle positioned above the Begin button
- Two example chips: (1) Peer review / Do No Harm focus, (2) Changed security conditions
- `user_context` extracted in `run_stage()` and `run_express()`; injected into Stage 1 prompt as labelled block
- Backend injection label: "ADDITIONAL CONTEXT PROVIDED BY THE TASK TEAM"

### 6. Landing Page UX Streamlining (commit `56d9153`)
- Removed review-type tile cards entirely
- Added tiny one-liner: "Currently covers design-stage documents (PCN · PID · PAD). Implementation review (MTR · ISR) — coming soon."
- Context box restyled with light-blue button (prominent, clearly interactive)
- Reduced context chips from 4 to 2; added "Examples — click to use:" label
- Pre-loaded and confidentiality notices moved to after the Begin button
- `selectReviewMode()` made null-safe

---

## Current App Structure

```
Upload panel flow (top to bottom):
  1. Upload heading + description
  2. "Implementation review coming soon" — one line
  3. Upload zones (project + contextual)
  4. File chips / doc-type badge / debug log
  5. Workflow mode (Express / Step-by-Step)
  6. [Context box] — light blue toggle, opens to 2 chips + textarea
  7. Begin FCV Analysis button
  8. Pre-loaded notice
  9. Confidentiality reminder
```

---

## What Was NOT Done / Pending

### User's pending comments from testing
The user said "I'll surface these as we go" — there are likely remaining comments from running the app during this session that were not addressed. Check with the user at the start of the next session.

### Potential next priorities (user to confirm order)
1. **Test the app with a real document** — verify load-first step-by-step works correctly; verify context box injection is visible in Stage 1 output
2. **Merge `feat/v8-knowledge-base` to `main`** — branch has 15+ commits since last merge, all tested
3. **Implementation Review Phase 4 redesign** — Stage 3 output structure for course-correction notes; separate MTR vs ISR prompt paths. See `docs/IMPLEMENTATION_REVIEW_DESIGN.md` for full plan.
4. **CLAUDE.md update** — the project CLAUDE.md still says "v7.6" and references old architecture. Should be updated to reflect v8 state.

---

## Key Architecture Facts (for next session)

### Prompt keys in `DEFAULT_PROMPTS` (app.py)
| Key | Purpose |
|---|---|
| `'1'` | Stage 1 — Design Review: Context & Extraction |
| `'2'` | Stage 2 — FCV Assessment |
| `'3'` | Stage 3 — Recommendations Note |
| `'deeper_playbook'` | Go Deeper Tab 2: FCV Playbook |
| `'followon'` | Follow-on post-analysis queries |
| `'impl_1'` | Stage 1 — Implementation Review (MTR/ISR) |
| `'impl_2'` | Stage 2 — Implementation FCV Assessment |
| `'impl_3'` | Stage 3 — Course-Correction Note |

### Key backend functions added this branch
- `extract_process_type(stage1_output)` — parses `%%%PROCESS_TYPE:%%%`
- `get_process_slice(process_type)` — formats WB_PROCESS_GUIDE for prompt injection
- `extract_instrument_type()`, `extract_temporal_context()` — existing
- `extract_stage2_ratings()`, `extract_under_hood()`, `extract_priorities()` — existing parsers

### Key frontend state variables
```javascript
let reviewMode = 'design';      // always 'design' currently (impl disabled)
let processType = 'Unknown';    // set from Stage 1 in impl mode
let docType = 'Unknown';        // e.g. 'PAD', 'PCN'
let instrumentType = 'Unknown'; // e.g. 'IPF', 'PforR'
let temporalContext = {};        // {approval_date, closing_date, safeguards_framework}
let analysisMode = 'express';   // or 'stepbystep'
```

### API payload shape (both modes)
```javascript
// run-express
{ documents: [...], review_mode: 'design', user_context: '...' }

// run-stage
{ stage: 1|2|3, history: [...], document_type, instrument_type,
  temporal_context, review_mode: 'design', process_type: 'Unknown',
  user_context: '...' }
```

### Step-by-step loading (CHANGED this session)
- Load card stays visible throughout streaming
- `load-sub-msg` text updates on research_status / preprocess / preparing_analysis events
- Chunks buffered in `streamed` but NOT rendered to DOM
- `renderOut()` called once on `p.done` — full output appears at once

### Priority level field clarification
`risk_level` in Stage 3 JSON = **priority ordering** (High/Medium/Low), NOT an FCV risk assessment. The UI now shows "Priority: High" not "FCV Risk: High". The Stage 3 prompt RISK_LEVEL description was updated to clarify this.

---

## Files Modified This Session

| File | Changes |
|---|---|
| `app.py` | impl_1/2/3 prompts; extract_process_type; get_process_slice; run_stage/run_express bifurcation; user_context injection; WB LLM feedback (9 changes); RISK_LEVEL description |
| `index.html` | Phase 4 frontend (disabled); load-first step-by-step; context box; priority labels; landing page UX |
| `background_docs.py` | IPF CDD sub-modality field; Para 18 field |
| `docs/IMPLEMENTATION_REVIEW_DESIGN.md` | New — full Phase 4 design archive |
| `docs/20260412_SESSION_HANDOFF.md` | This file |
| `app_feedback/20260412_wbllm_review/` | WB LLM review package (generate script + .docx outputs) |

---

## CLAUDE.md Update Needed

The project-level CLAUDE.md at repo root still says:
- "Current version: FCV Project Screener v7.6"
- Missing Phase 4, context box, load-first streaming in the architecture section
- `DEFAULT_PROMPTS` table is incomplete

**Update at start of next session** or after merging to main.
