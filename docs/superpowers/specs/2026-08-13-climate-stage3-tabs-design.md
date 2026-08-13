# Climate-FCV Stage 3 Summary and Detailed Views

## Objective

Extend the verified Climate-FCV Stage 3 result with the same concise-first
Summary / Detailed analysis interaction used by the core FCV route, while
preserving the existing verified reader and all download content.

## Scope

- Fix the concise priority lifecycle block so `Before Appraisal` and `At Design
  Stage` are rendered in a consistent two-column structure rather than placing
  the second lifecycle item in the label column.
- Add Summary / Detailed analysis tabs to the verified Climate-FCV v2.1 route.
- Keep the current Climate-FCV verified reader as the complete Detailed analysis
  view, including core questions, ranked priorities, document checks,
  provenance, and routing detail.
- Make the Climate Summary a client-side presentation of the already-returned
  verified reader. Switching tabs must not make another model request.
- Do not add a horizontal rating bar to the Summary. The Summary may show the
  climate integration label as compact text, while the existing detailed rating
  content remains unchanged.
- Select the Summary's “What is already working” cards from the qualities
  evidenced in the reader data. The renderer must support a variable number of
  cards and must not assume exactly three fixed categories.
- Leave native/unverified Climate lens output and other sector-lens routes on
  their existing presentation path.

## Design

### View state and gating

The existing in-memory `stage3View` state will be extended so the verified
Climate-FCV reader can use the same accessible tab component. The Climate route
will be eligible only when the verified reader is present and the run is a
design-stage Climate-FCV assessment. The core FCV route's existing gate remains
unchanged.

The Summary tab is the default for a newly completed verified Climate-FCV
assessment. Detailed analysis is the fallback when the reader or the derived
summary data is unavailable. The tab controls retain the existing ARIA tablist,
tabpanel, roving-tabindex, and keyboard behavior.

### Climate Summary content

The Summary will contain:

1. A small Climate-FCV integration label derived from the verified reader,
   without a horizontal segmented rating bar.
2. A five-minute readout using the reader's executive readout, with the first
   sentence styled as the active lead sentence in the same manner as the
   detailed Climate-FCV reader.
3. A dynamic “What is already working” section. Candidate cards will be drawn
   first from evidenced existing responses carried in the reader and then from
   positively rated reader judgments when needed. Cards will use the source
   description/rationale, preserve the evidence basis, and render however many
   valid candidates are available within a bounded presentation limit. If no
   positive candidate is evidenced, the section will show a neutral evidence-
   limited message rather than inventing a strength.
4. A compact “Priority actions for the task team” transition and the existing
   numbered priority navigation/card area. Climate priority navigation will use
   the verified reader's ranked priorities without changing their order or
   content.

The Summary is a view-layer derivative only. It must not change ratings,
priority order, evidence, recommendation fields, or export payloads.

### Detailed analysis

The Detailed analysis tab will render the existing
`renderClimateVerifiedAssessment()` output. No Climate-FCV detailed sections
will be removed or rewritten as part of the tab work. The current detailed
rating content remains in this view, where it provides analytical detail rather
than competing with the concise Summary hierarchy.

### Lifecycle alignment

The concise priority lifecycle markup will use an explicit label column and a
stacked values column. Both `At Design Stage` and `Before Appraisal` therefore
share the same value column and align consistently across priorities and narrow
screens.

## Data flow and compatibility

- The server-side verified reader will expose the bounded existing-response
  records needed for dynamic Summary strengths, without changing the model
  prompt or the canonical assessment contract.
- Browser-side rendering will escape all reader-provided text using the existing
  `esc()` helper.
- Downloads will continue to use `stageOutputs[3]`, the complete priority list,
  and the existing verified export paths. They will not use Summary HTML.
- Saved-session compatibility remains unchanged; the tab is transient view
  state.

## Verification

- Add failing contract tests for lifecycle alignment, verified Climate tab
  gating, dynamic strength-card selection, and preservation of the detailed
  Climate reader/export path.
- Run the focused Climate, concise-contract, and frontend tests.
- Run the full Python suite and frontend storage checks.
- Run a South Sudan Climate-FCV smoke assessment and confirm all three stages
  complete without SSE/UI errors, the Summary tab opens by default, Detailed
  analysis reproduces the current reader, and no smoke warning appears in
  quality mode.
- Inspect the final diff and verify the unrelated pytest artifact remains
  unmodified/untracked.
