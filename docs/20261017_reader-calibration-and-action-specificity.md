# Reader calibration and recommendation specificity

## Change and scope

Recommendation prompt v2.20 puts the current document, permitted section and
specific project element in both minimum_action and the opening sentence of the
visible action paragraph. Each action identifies a document change and its intended
content. Later preparation work identifies the decision it informs, when supported.
This draws on normal FCV's document-edit approach without importing PAD-only
destinations, formal gates or implementation procedures into a concept PID.

The saved Somalia priorities already contain useful document edits, but their
narratives do not consistently lead with those destinations. The renderer uses
narrative paragraphs after the first paragraph for the visible action, falling
back to minimum_action only when those paragraphs are absent. Prompt instructions
therefore address both fields. No renderer, schema or additional rejection gate
was needed. Old saved reports are not rewritten.

Reader review v1.11 requires whole-record qualification and source-passage checks
before objections. It distinguishes nearby but separate activity/beneficiary
claims. General disclaimers and modal verbs cannot excuse an unsupported premise,
contradiction or completed-status claim. No case IDs, beneficiary exemptions or
automatic pass overrides were added. Publication approval remains false.

## Calibration cases for the next model evaluation

These synthetic cases describe expected judgments, not measured results. Supply
each as a separate review record with cited facts and source passages, using the
existing review schema. They complement the saved development case; they are not
independent analytical acceptance of the app.

| Source evidence | Reader assertion | Expected judgment |
|---|---|---|
| A market rehabilitation activity and exploration of an enterprise facility in that market are documented. | The possible facility could expand opportunities around the investment. The following paragraph says feasibility remains under exploration and benefits are not assured. | Allow the qualified inference; do not demand measured impact. |
| Same evidence, with no beneficiary targeting. | The facility reserves opportunities for displaced households. A later paragraph says benefits are uncertain. | Reject invented targeting; the disclaimer does not cure it. |
| Design specifications include warning equipment; operation is not documented. | The warning system is operational and protects residents. | Reject completed status and delivered impact. |
| Same design evidence. | If installed and maintained, the planned warning equipment could improve warning delivery. | Allow the mechanism with its conditions; no delivered impact asserted. |
| A short fact mentions an exploratory enterprise facility. Its cited passage also describes support around commercial areas receiving investment. | A possible facility could widen opportunities around those investments. | Inspect the passage before claiming the investment link is unsupported. |
| A road scheme targets remote communities; a separate exploratory fund has no stated target group. | The road scheme targets remote communities. The possible fund could support enterprises. | Do not transfer the road's target group to the fund. |
| Same evidence. | The fund targets remote communities and could support enterprises. | Reject the new targeting claim despite the modal benefit. |

For each objection, inspect the exact quotation, actual asserted relationship,
cited passage and treatment of any qualification. A pass on the saved Somalia
record alone would not establish calibration; the unsupported variants must still
be rejected. Preserve raw verdicts, tokens and failures. Do not manually relabel
the previous revise result.

## Recommendation evaluation

Inspect every visible action before opening dropdowns:

- Does it name the current document and an allowed section, then the specific
  component, criterion, indicator or responsibility to change?
- Could a task-team member tell what content to add and what decision it informs?
- Does later work add a distinct preparation task tied to available evidence,
  rather than repeat the current edit at an unnamed review gate?
- Are advice and existing commitments distinguishable, with no invented exact
  heading, mandatory instrument, target, beneficiary or institutional role?
- Is the advice appropriate to concept versus appraisal maturity, and does it
  preserve the Climate-FCV pathway and existing mitigation?

Treat weak specificity as an editorial improvement, not an automatic publication
block. Consequential unsupported claims still require correction. Compare a new
generation with the saved report using these criteria, not word matching.

## Deployment and acceptance

Local verification: 1,790 tests passed in 446.80 seconds. Four previously hanging
Chromium-driver tests in test_climate_lens_frontend.py were explicitly deselected
(print disclosures, stage tabs, download header and session bar). No complete
browser-suite pass is claimed. The focused run initially had 289 passes and one
expected old prompt-version assertion; that assertion was updated and its test
passed before the broader run. Diff whitespace checks passed.

This is a prompt-only preparation for evaluation. No new provider call or preview
deployment is part of this change. The previous paid review remains revise and
the preview remains on 98048797116a. A bounded model evaluation and subsequent
live end-to-end acceptance remain outstanding before claiming improved behavior
or readiness for the supervised pilot.
