# Detailed analysis restoration

User-approved baseline: `f8e8142`, before the September 20 management brief work.
Keep the current Summary, browser/HTML/Word templates, and WBG editorial style.
Restore technical depth and document-focused recommendations; retain subsequent
source-coverage, factual-status, SORT and lifecycle safeguards.

## Implementation and verification

- [x] Add regression checks for the original detailed action paragraph, action
  guidance/drafting depth, paired-strength discussion and Summary-only brevity.
- [x] Restore these instructions in the standard Stage 3 composer. Keep grounded
  priority selection and instrument applicability rather than manufacturing findings.
- [x] Run focused prompt, parser, frontend and export checks; confirm presentation
  files are unchanged.
- [ ] Run one fresh complete Honduras PAD assessment on the test preview, inspect
  detailed content, Summary and exports, and record limitations.
- [ ] Update developer references and the private parity register; commit/push
  a reviewable feature branch.


User clarification: preserve WBG editorial style (including bold leads and no em
dashes). Summary and Detailed must share actions, strengths and gaps. Preserve
original detailed subheadings, two-way risk exposure, sensitivity and
responsiveness. Expand Summary links to mention full details and suggested text.

Root cause found in saved-output inspection: original raw Stage 3 JSON contains
risk_exposure and both assessment summaries, but the saved/reopened session loses
them. Fix session persistence/restoration as part of the technical restoration.


## Verification checkpoint

Candidate `b44da5e` is deployed to the existing quality preview. The last combined
prompt/parser/export/frontend regression pass contains 171 passing cases; prior
focused routing, extraction and Word checks also passed. Inline JavaScript syntax,
Python compilation and diff checks pass. The actual previous Honduras saved file
recovers all three missing technical sections exactly. Its four Summary action
sets also pass the strengthened admission without changes.

Fresh PAD test was stopped before upload by automatic approval review, which
requires explicit approval for the source document and external preview destination.
No fresh model run has started at this checkpoint.
