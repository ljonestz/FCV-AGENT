# Normal FCV Summary Across All Reviews

**Date:** 2026-08-21
**Status:** Implemented and live-validated on the target branch
**Target branch:** `codex/climate-summary-quality-fixes`
**Baseline:** `08b3cb9`

## Purpose

Give the normal FCV route the same concise-first Stage 3 experience as the verified Climate + FCV route. Every normal FCV review should open with a five-minute Summary while retaining the existing comprehensive Recommendations Note under **Detailed analysis**.

The summary is a presentation layer over the same assessment. It must not introduce, omit, or reprioritize findings relative to the detailed output.

## Scope

### Included

- Normal FCV reviews with no active sector lens.
- Design- and implementation-stage reviews.
- Express and Step-by-Step workflows.
- Supported document and instrument contexts, including PCN, PID, PAD, Additional Financing, restructuring, DPF/DPO, PforR, MPA, and regional operations.
- A shared Stage 3 Summary/Detailed shell for normal FCV and Climate + FCV routes.
- A shared advisory transition before priority actions.
- Strict summary validation and safe fallback to Detailed analysis.
- Detailed-only downloads.

### Not included

- A second model call to repair or regenerate a missing summary.
- Changes to the substantive detailed Recommendations Note.
- Summary content in DOCX, HTML, or other downloaded reports.
- Activation of the normal-FCV concise contract for future non-climate sector lenses.
- Changes to priority ranking or substantive FCV ratings.

## Current State

On the target branch, only a validated Climate + FCV design review can open the five-minute summary. `supportsClimateVerifiedStage3View()` gates the Summary/Detailed tabs and defaults verified climate results to Summary. Normal FCV reviews render only the detailed Stage 3 output, although that detailed note contains an executive-summary section.

The separate `codex/concise-stage3-readout` branch contains a tested normal-FCV `concise_readout` contract and UI. Implementation should selectively forward-port the relevant concepts and tests into the target branch rather than merge that divergent branch wholesale.

## Chosen Approach

Generate the normal-FCV summary as optional structured fields in the existing Stage 3 response and JSON block.

This approach:

- avoids an additional model call;
- keeps summary and detailed output grounded in one analysis;
- allows independent validation of the presentation layer;
- preserves the detailed assessment if the summary is unavailable; and
- reuses mature work from the concise Stage 3 branch without importing unrelated divergence.

## Architecture and Data Flow

### 1. Prompt assembly

Append a concise presentation contract to the core Stage 3 prompt whenever no sector lens is active. Unlike the earlier concise branch, do not restrict this contract to `reviewMode === "design"`; it applies to every normal FCV review.

The contract must instruct the model to preserve:

- the detailed findings and ratings;
- the existing priority count and order;
- each priority's substantive actions; and
- the assessment's document, instrument, and review-stage calibration.

The contract adds `concise_readout` at the Stage 3 JSON top level and `concise` inside every ranked priority.

### 2. Structured output

`concise_readout` contains:

- `headline`: one plain-language sentence stating the overall FCV judgment;
- `overall_assessment`: a 150-200 word synthesis defined below;
- `strengths`: exactly three grounded strength cards, each with `title` and `text`; and
- `priority_intro`: an optional project-specific bridge into the controlled advisory transition.

Every `priority.concise` contains:

- `title`: a plain-language action title;
- `why`: a project-specific explanation of the gap, delivery consequence, and FCV mechanism;
- `how`: two to four specific actions appropriate to the current review stage;
- `suggested_wording`: a target document element and ready-to-paste text where supportable;
- `project_cycle`: review-stage labels and actions; and
- existing detailed fields remain authoritative for specialist reasoning and evidence.

### 3. Review-stage calibration

A deterministic lifecycle-context helper supplies wording appropriate to the review:

- **Standard PCN:** commit the strategic choice in the PCN; develop proportionate operating detail during preparation.
- **Consolidated or condensed preparation:** resolve decisions by the applicable review gate and complete supporting detail in parallel.
- **PID/PAD or appraisal-readiness:** resolve material design choices before the review gate; do not defer readiness issues.
- **Implementation review:** identify adjustments to delivery, targeting, monitoring, partnerships, safeguards, or adaptive-management triggers during implementation.
- **Additional Financing or restructuring:** distinguish changes required in the current package from actions that remain within existing implementation instruments.
- **Unknown context:** use conservative labels such as “When to address” and “Next step”; do not invent a procedural gate.

Instrument-specific prompt modules remain authoritative. The concise layer restates their conclusions in plain language and must not replace IPF, DPF/DPO, PforR, MPA, regional, or mid-cycle routing rules.

### 4. Parsing and transport

The Stage 3 parser validates concise fields separately from the detailed contract. Both Express and Step-by-Step completion events return the normalized `concise_readout` and normalized concise objects attached to priorities.

The frontend stores this data with the existing Stage 3 state so session restoration and valid Stage 3 reruns restore the correct Summary view.

### 5. Frontend adapters

Use one shared summary shell with route-specific adapters:

- **Normal FCV adapter:** consumes normalized `concise_readout`, concise priority objects, and existing FCV sensitivity/responsiveness ratings.
- **Climate + FCV adapter:** consumes the existing validated climate reader and climate priorities.

The adapters may differ in their source data, but the tab bar, section hierarchy, advisory transition, priority accordion, accessibility behavior, and download note are shared.

## Overall Assessment

The normal-FCV overall assessment is a compact synthesis, not a copy of the first detailed paragraph. It covers:

1. **Headline judgment:** how well the operation integrates FCV considerations and its main weakness.
2. **Review-stage context:** what can reasonably be expected at concept, appraisal, implementation, Additional Financing, or restructuring stage.
3. **Principal FCV exposure:** the two or three dynamics most likely to affect delivery, inclusion, legitimacy, or sustainability.
4. **Two-way risk:** risks to the project and ways the project could worsen fragility, exclusion, grievances, or conflict.
5. **Sensitivity versus responsiveness:** whether the operation only recognizes FCV conditions or translates them into targeting, implementation arrangements, monitoring, safeguards, and adaptive decisions.
6. **Strongest feature:** the most credible existing FCV-sensitive measure.
7. **Most consequential gap:** the unresolved issue with the greatest operational significance.
8. **Bottom-line implication:** what the task team should concentrate on at the current review stage.

Display the existing FCV sensitivity and FCV responsiveness ratings immediately below the assessment as two compact status indicators. The prose must avoid citations, unexplained jargon, generic FCV language, and repetition of the subsequent strength and priority cards.

## Summary Interface

### Default view

- Stage 3 opens on **Summary** for every valid normal-FCV and Climate + FCV summary.
- **Detailed analysis** remains available beside it.
- The tab bar retains the note: “Downloads include the comprehensive analysis.”
- Switching tabs preserves the selected priority where practical.

### Section order

1. **Five-minute readout** label.
2. **Overall assessment:** headline, 150-200 word synthesis, and two FCV rating indicators for the normal route.
3. **What is already working:** exactly three compact strength cards.
4. **Priority actions for the task team:** controlled advisory transition followed by every ranked priority.

### Priority accordions

- Show all ranked priorities as concise cards.
- Expand the first priority by default.
- Collapse all remaining priorities initially.
- Opening one priority collapses the previously open priority.
- Preserve rank and order from the detailed analysis.
- Each expanded card shows, in order:
  - Why this is suggested
  - How it can be addressed
  - Suggested wording, when available
  - Where this fits in the current review or project cycle
  - Optional specialist reasoning/evidence disclosure

The compact header remains visible for collapsed cards and contains rank plus the plain-language title.

## Advisory Priority Transition

Render this as a controlled frontend template immediately before the priority accordions. It is not delegated entirely to the model and is not exported in the detailed report.

### Normal FCV design review

> The following priorities are suggestions to strengthen the project's design in its FCV context; they are not mandatory requirements. The task team may wish to focus on those most relevant and discuss them with the FCV Country Coordinator or relevant Global Practice experts as needed.

### Climate + FCV design review

> The following priorities are suggestions to strengthen the project's design in its climate and FCV context; they are not mandatory requirements. The task team may wish to focus on those most relevant and discuss them with the FCV Country Coordinator or relevant Global Practice experts as needed.

### Implementation-stage adaptation

For either route, replace “project's design” with “project's design and implementation arrangements.” Retain the optional, non-compliance framing and expert-consultation language.

## Validation and Failure Behavior

A normal-FCV Summary is available only when all of the following validate:

- non-empty headline;
- 150-200 word overall assessment;
- exactly three complete strength cards;
- both FCV rating values already validate through the detailed contract;
- every ranked priority has a complete concise object;
- `how` contains two to four non-empty actions; and
- project-cycle labels and primary action text are present and appropriate to the resolved review context.

Validation failure must not invalidate or alter the detailed Stage 3 result.

If any required summary element fails:

1. treat the entire Summary as unavailable;
2. open Detailed analysis;
3. show a short informational notice that the summary was unavailable and the full analysis is shown;
4. do not mix structured and heuristic summary content; and
5. do not make a repair model call.

The verified Climate + FCV route retains its existing schema validation and failure behavior. Adding the shared advisory transition must not weaken that contract.

## Downloads and Persistence

- DOCX/HTML downloads continue to use the existing comprehensive Stage 3 analysis.
- The concise summary and advisory transition are on-screen presentation only.
- Session restoration should reopen Summary only when the stored summary passes the same capability gate; otherwise it restores Detailed with the availability notice.
- A completed Stage 3 rerun replaces both detailed and summary state atomically.

## Accessibility and Responsive Behavior

- Summary and Detailed controls use tab semantics and accurate `aria-selected` state.
- Priority cards expose button semantics plus `aria-expanded` and `aria-controls`.
- Keyboard users can move between tabs and toggle priority cards without a pointer.
- Focus remains visible and moves predictably when a card is opened.
- Narrow screens stack strength cards and card subsections into one column.
- Collapsed headers retain sufficient context and do not rely on color alone.

## Verification Strategy

### Backend contract tests

- Concise contract is appended for core FCV Stage 3 in design and implementation reviews.
- Concise contract is not appended to active-lens prompts.
- Lifecycle context is correct for PCN, consolidated preparation, PID/PAD, implementation, Additional Financing, restructuring, and unknown contexts.
- Parser accepts complete summaries and rejects partial or malformed summaries without affecting detailed fields.
- Every priority must have a valid concise object.
- Both Express and Step-by-Step completion payloads include normalized concise data.

### Frontend contract and behavior tests

- Valid normal-FCV results default to Summary.
- Invalid or absent summaries default to Detailed and show the availability notice.
- Shared tabs render for both normal FCV and verified Climate + FCV routes.
- Overall assessment renders both normal-FCV rating indicators.
- Shared advisory wording is correct for normal, climate, design, and implementation contexts.
- All priorities render; only the first starts expanded.
- Opening a priority collapses the previously open card.
- Tab and accordion ARIA states track visible content.
- Detailed content is preserved exactly when switching views.
- Downloads continue to exclude concise-only content.
- Session restoration applies the same summary capability gate.

### Regression tests

- Existing climate verified reader, priority order, incomplete-recommendation behavior, and detailed analysis remain unchanged.
- Existing Stage 3 priority parsing, ratings, watch lists, follow-on behavior, and instrument routing remain unchanged.
- Express and Step-by-Step still produce equivalent completed Stage 3 data.

## Implementation Boundaries

- Reuse the tested concepts from `codex/concise-stage3-readout`, but port them manually against the latest target branch to avoid overwriting later climate-quality and routing fixes.
- Keep the diff focused on Stage 3 prompt assembly, parsing/normalization, SSE payloads, frontend summary components/state, and relevant tests.
- Do not refactor unrelated climate pipeline or Stage 1/2 code.
- Maintain shared contract parity with the internal ITS build and record any shared Stage 3 JSON changes in the local parity log during implementation.

## Acceptance Criteria

The feature is complete when:

1. Every valid normal FCV review opens with a five-minute Summary.
2. The overall assessment covers the approved eight elements and displays both FCV ratings.
3. Every ranked priority appears as a concise accordion card, with only the first initially expanded.
4. Both normal and climate summaries show the approved advisory transition.
5. Detailed analysis and detailed-only downloads remain unchanged.
6. Missing or invalid summary data safely falls back to Detailed without another model call.
7. Express, Step-by-Step, review-stage, accessibility, persistence, export, and climate regression tests pass.

## Implementation Record

Implemented on `codex/climate-summary-quality-fixes` through commit `012eaa2`
on 2026-08-22. The delivered implementation follows this design with two
reliability refinements established during live testing:

- the core Stage 3 prompt emits the structured JSON before the detailed narrative,
  reducing omission of the concise bundle on long outputs; and
- concise data is accepted atomically only when the top-level readout and every
  ranked priority contain a complete concise object.

Both Render smoke and quality services were live-validated with the official
Somalia STAIRP Phase 1 concept-stage PID (P513127), an IPF/MPA operation prepared
in February 2026. Both runs opened Summary by default and rendered three strengths
and five priorities with only the first expanded. The quality run also verified
single-open accordion behavior, tab state preservation, the controlled advisory,
and detailed-only HTML and DOCX exports. Render logs recorded successful responses
for all three stages and no error-level entries.

Final repository verification after initializing the pinned Climate-FCV bank
submodule: `1012 passed`. The focused concise/parser set reported `98 passed` when
run with the two submodule-dependent regression cases.

One generated-content caveat was identified during the quality review: a dated
Puntland-FGS assertion derived from live research was not substantiated by the
uploaded PID and should be verified before external use. This is a content-review
finding, not a Summary contract or rendering failure.
