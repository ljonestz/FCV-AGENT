# v8.0 Knowledge Base Branch — Handoff Document

**Branch:** `feat/v8-knowledge-base`
**Date:** 2026-04-12
**Status:** Phase 1-3 complete, Phase 4 pending. Ready for testing and refinement.

---

## What this branch does

This branch addresses detailed practitioner feedback from an FCV colleague who tested the app with a real PAD and found systemic issues. The full feedback is in `app_feedback/Colleague Feedback.docx`.

### Core problems solved:
1. **The LLM lacked instrument knowledge** — judged IPFs for things only possible under DPOs or PforRs
2. **Time dimension errors** — applied current-day standards to historical projects (e.g., ESF to pre-ESF projects)
3. **PDO/scope creep** — recommended beyond the project's stated scope, then penalised for not doing those things
4. **Narrow keyword matching** — only looked for "GEMS" not broader "geospatial analysis"
5. **Rewarded complexity** — penalised lean, fit-for-purpose designs appropriate for FCV settings
6. **Contradictory statements** — didn't reconcile analytical tensions
7. **UX friction** — opaque badge labels, no navigation between stages, no glossary

---

## What was built (27 commits)

### Phase 1: Knowledge Base (`background_docs.py`)
- **WB_INSTRUMENT_GUIDE** — 6 instruments (IPF, PforR, DPO, TA, MPA, IPF-DDO) with per-instrument:
  - Description, FCV levers, not-applicable guardrails, typical structure
  - OST recommendation applicability (fully/partially/N/A per instrument)
  - DNH principle applicability per instrument
  - Policy transitions (ESF date, safeguards framework)
  - Recent procedural changes (Jan 2026 IPF Procedure, etc.)
- **WB_PROCESS_GUIDE** — 5 processes (MTR, ISR, AF, Restructuring, ICR) with purpose, scope, key policies, typical documents, FCV considerations, common pitfalls, backward/forward look
- **FCV_GLOSSARY** — 29 FCV terms with definitions, measurement approaches, and sources
- **Broadened existing constants** — GEMS → geospatial family, M&E capacity → crisis management, IE abbreviation recognition
- **Helper functions** in `app.py`: `get_instrument_slice()`, `get_glossary_for_prompt()`, `/api/glossary` endpoint

### Phase 2: Prompt Changes (`app.py` — DEFAULT_PROMPTS)
- **Stage 1:** Instrument type extraction (`%%%INSTRUMENT_TYPE%%%`), temporal context extraction (`%%%TEMPORAL_CONTEXT_START/END%%%`), PDO/ToC/RF extraction, abbreviation handling, concept recognition instructions
- **Stage 2:** Instrument-aware rubric (N/A marking, adjusted denominator), temporal anchoring guardrail, PDO/scope bounding ("Beyond scope"), simplicity recognition (3-point test), logical consistency check, concept equivalence table, 6 supplementary dimensions (Gender/GBV, Climate-FCV, PEA quality, HDP nexus, IDA FCV Envelope, digital/tech risks)
- **Stage 3:** Instrument-feasible recommendations, temporal guardrail, scope-bounded priorities, Horizon Considerations section (`%%%HORIZON_START/END%%%`), canonical PAD section labels, RF indicator full specification
- **Backend injection:** Instrument slices and temporal guardrails injected into Stages 2-3 via request payload; glossary injected into Stage 2; Stage 3 max_tokens increased to 20k

### Phase 3: Frontend UX (`index.html`)
- **Temporal context panel** — blue info bar showing instrument, dates, safeguards framework
- **Horizon Considerations panel** — collapsible `<details>` below Stage 3 priorities
- **Expanded badge labels** — "FCV Refresh Shift B: Differentiate" (was "B: Differentiate"), "FCV Risk: High" (was "High"), with hover tooltips
- **Clickable stepper** — works in Step-by-Step mode, not just Express
- **Glossary tooltips** — 29 terms with dotted underline + hover definition
- **Enhanced upload instructions** — suggests supplementary docs, notes condensation

### Rating Recalibration
- **Sensitivity:** "Weakly addressed" now scores 0.5 points (was 0). Percentage-based thresholds replace count-based.
- **Responsiveness:** Adaptive M&E cap softened from "Low" to "Adequate"
- **Effect:** Honduras transport PAD moved from Very Low/Low → Adequate/Adequate

---

## What was tested

### Honduras Sustainable Connectivity Project PAD (P181166)
- $187M IDA credit, November 2024, Transport sector, Northwestern Honduras
- File: `app_feedback/Project Appraisal Document (PAD) clean.pdf`
- Full Express mode run completed successfully
- **Results:** Stage 1 correctly identified IPF instrument, ESF framework, 2024-12 approval date. Stage 2 correctly marked DPO questions as N/A. Stage 3 produced 4 actionable priorities with specific geographic references and ready-to-paste PAD language.
- **Issue found:** Ratings were too harsh (Very Low sensitivity) — fixed by recalibrating rubric

### WB Internal LLM Reviews (3 rounds)
- Round 1: Full knowledge base review → 7 corrections, significant additions, full process guide content
- Round 2: MPA and IPF-DDO deep-dive → comprehensive new instrument entries
- Round 3: Prompt quality review → 6 guardrail gaps fixed, 6 missing dimensions added, Stage 3 specificity improved
- All feedback files in `app_feedback/` folder

---

## What still needs to be done

### Immediate: User's pending comments
The user mentioned "several comments" after testing the deployed version that haven't been captured yet. These should be collected and addressed first.

### Phase 4: Implementation Review Pipeline (not started)
Per the design spec (`docs/superpowers/specs/2026-04-11-colleague-feedback-response-design.md`, section 7):
- **Two-tab mode selector** on landing page (Design Review / Implementation Review)
- **Implementation Review Stage 1 prompt** — multi-document, timeline extraction, backward+forward look
- **Implementation Review Stage 2 prompt** — performance assessment, process-specific framing (MTR asks different questions than ISR)
- **Implementation Review Stage 3 prompt** — course-correction recommendations, process-specific output
- **Frontend:** Implementation Review upload zone, output structure, process-specific rendering
- The `WB_PROCESS_GUIDE` content is ready in `background_docs.py` — prompts need to be written

### Process Guide enhancements (from WB LLM Round 3)
Saved for Phase 4:
- ISR: rating trajectory analysis across multiple ISRs, IP/DO divergence diagnosis
- AF: defensive vs. constructive AF detection
- Restructuring: adequacy assessment (scope contraction without PDO change = rating manipulation)
- ICR: honesty/credibility lens, ICR-specific assessment mode

### Potential refinements
- Test with more document types (PforR, DPO, MPA phase docs, ISR)
- Verify web research works on Render deployment (failed in Honduras test)
- Consider `editable_at` field for Stage 3 actions (suggested by WB LLM)
- Verify glossary tooltip performance on long outputs

---

## Key files and what they do

| File | Purpose |
|---|---|
| `app.py` | Flask backend: prompts (DEFAULT_PROMPTS), routes, parsing functions, injection logic |
| `index.html` | Single-page frontend: all UI, JS, CSS |
| `background_docs.py` | Knowledge constants: 11 sections (FCV_GUIDE, FCV_OPERATIONAL_MANUAL, etc. + WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE) |
| `CLAUDE.md` | Project-level instructions for Claude Code |
| `docs/superpowers/specs/2026-04-11-colleague-feedback-response-design.md` | Full design spec |
| `docs/superpowers/plans/` | Implementation plans for Phases 1-3 |
| `app_feedback/Colleague Feedback.docx` | Original practitioner feedback |
| `app_feedback/WBLLMFeedback.docx` | WB LLM Round 1 response |
| `app_feedback/WBLLMMPFIPFDDO.docx` | WB LLM Round 2 (MPA + IPF-DDO) |
| `app_feedback/20260411_wbllm_review/` | WB LLM Round 3 documents and responses |

---

## Architecture decisions to be aware of

1. **Instrument slices injected via `.replace()` in Stage 2** (not `.format()`) because Stage 2 prompt has literal `{}` in rating blocks
2. **Stage 3 uses `.format()`** with `{{{{`/`}}}}` escaping for JSON examples
3. **Temporal context extracted by Stage 1 LLM** (not a separate API call) via delimiter blocks
4. **Frontend passes instrument_type and temporal_context back to backend** in Stage 2/3 request payloads
5. **Glossary loaded async on page load** from `/api/glossary` endpoint
6. **Rating rubric uses percentage-based scoring** with 0.5 points for "Weakly addressed"
7. **Express mode and Step-by-Step mode** share the same prompt logic but have separate streaming paths in `app.py` (`run_stage` vs `run_express`)

---

## How to continue

1. Read this document + the design spec + CLAUDE.md for full context
2. Check `app_feedback/Colleague Feedback.docx` for the original feedback points
3. The user has pending comments from their latest test — collect those first
4. For Phase 4 work, the WB_PROCESS_GUIDE content is ready; prompts need to be written following the pattern in DEFAULT_PROMPTS
5. Always test with the Honduras PAD (`app_feedback/Project Appraisal Document (PAD) clean.pdf`) as a baseline
