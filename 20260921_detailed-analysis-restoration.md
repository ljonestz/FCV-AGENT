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
- [x] Run one fresh complete Honduras PAD assessment on the test preview, inspect
  detailed content, Summary and exports, and record limitations.
- [x] Update developer references and the private parity register; commit/push
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

After explicit upload approval, one fresh complete PAD assessment finished all
three stages on the preview. It produced four priorities with ten detailed actions,
each with guidance and suggested drafting. All four strengths are represented in
three Summary cards; actions and gaps correspond across the two presentations.
Both risk directions and sensitivity/responsiveness sections are present.

The live check exercised all priority links and brief exports, then stopped on a
case-sensitive test expectation for a CSS-capitalized heading. The corrected test
replayed the exact recorded result locally and passed all links, four exports,
section save/reload equality and mobile layout, with no browser errors or visible
em dashes. Automatic approval review disallowed external replay; no derived
assessment was uploaded again, and no second model run was made.

Analytical acceptance is limited: the fresh output repeats evidence/status issues
around instrument absence, HEIS approval versus activation, displacement context
and proposed thresholds. These are documented in private QA evidence, not treated
as a successful factual audit. The feature restores content depth and presentation;
it does not guarantee model factual accuracy. Raw documents and test artifacts
remain gitignored. Production is unchanged.

Native Word visual QA: the brief renders to two pages and the comprehensive note to fourteen pages. Browser screenshots, both brief pages and a complete detailed-page contact sheet were reviewed; existing templates and full action/drafting content are retained.
