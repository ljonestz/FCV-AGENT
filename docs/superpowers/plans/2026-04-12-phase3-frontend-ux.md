# Phase 3: Frontend UX — Implementation Plan

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Phase 2 backend improvements visible in the UI: temporal context panel, expanded badges, Horizon Considerations panel, glossary tooltips, clickable stepper, enhanced upload instructions.

**Architecture:** All changes in `index.html` (single-page app with inline CSS + JS). Consumes new SSE fields: `instrument_type`, `temporal_context`, `horizon_considerations` from the backend.

**File:** `index.html` (~4824 lines)

---

### Task 1: Consume instrument_type and temporal_context from Stage 1 done event
- Store in JS variables and localStorage
- Display temporal context info panel after Stage 1

### Task 2: Render Horizon Considerations collapsible panel in Stage 3
- Parse `horizon_considerations` from Stage 3 done event
- Render as collapsible `<details>` below priority cards

### Task 3: Expand FCV Refresh shift badge labels
- Full labels: "FCV Refresh Shift A: Anticipate" etc.
- "FCV Risk: High/Medium/Low"
- Tooltips with one-line explanations

### Task 4: Enable clickable stepper in Step-by-Step mode
- Extend enableClickableStepper() to activate after each stage completes

### Task 5: Add FCV glossary tooltips
- Fetch /api/glossary on load
- Scan rendered output for glossary terms
- Add dotted-underline + hover tooltip

### Task 6: Enhanced upload instructions
- Context-aware helper text
- Document condensation note
