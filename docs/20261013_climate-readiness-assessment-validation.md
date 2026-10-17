# Pipeline assessment and all-open priorities: verification

User requested every ranked operational priority open by default and a full
assessment of repeated recommendation, research and native Summary failures.

## Implemented presentation change

Browser and Python HTML now set open on every priority card, regardless of rank.
Recommendation details and sections04–06 remain closed. Word already contains
all priority content. Summary remains compact. Reader version2.15; generation
prompt versions and model-call count unchanged. Existing feature worktree/PR83;
production/main and ITS remain held.

Regression sequence: the four-priority expectation failed before the change,
then passed. Broad reader/frontend checks returned172 passed and one obsolete
expectation for a closed second priority. That fixture now expects the approved
default; four affected layout/print checks pass. A browser print test closes a
card manually after verifying all are initially open, preserving restoration
coverage. Final full suite: **1,469 passed in970.58s (16m10s)**, exit0, normal
process permissions. Log: output/20261013-open-priorities-full-regression.txt.

Connected Edge saved-case check: priorities[true,true], details[false,false],
review/guidance/method[false,false,false]. Screenshot and reviewable preview:
output/playwright/20261013-quality6-all-priorities-open.png and
output/playwright/20261013-quality6-all-priorities-open-preview.html.
These use the original paid text, ratings and two accepted actions; no paid call.

## Assessment evidence

The engineering assessment is `20261013_climate-pipeline-readiness-assessment.md`.
Six saved runs show final counts0/1/1/0/2/2, not a frontend two-item cap. Every
native Summary fell back; the latest two runs structurally admitted four actions
before semantic review. Different prompt versions limit generalization.

Offline contract probe reproduces a schema-shaped correction failing with
DRAFTING_CURRENT_MISSING before a second reviewer. It also shows quality6 native
Summary failing on points while its three paragraphs pass existing paraphrase
controls, and a lexical gate accepting a constructed negation of a supported claim.
These establish contract/validator problems, not factual acceptance of all output.
Probe source/results are untracked under output/20261013_readiness_contract_probes.py
and output/20261013-readiness-contract-probes.json. No provider calls were made.

The recommended backend redesign is a proposal. Core action review, optional
drafting review, research passage IDs, meaning-based reader checks and a case
decision inventory still require implementation and acceptance. No further paid
run is authorized or used. Existing withholding/source/policy guards remain.
