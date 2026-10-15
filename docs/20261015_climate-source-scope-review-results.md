# Source-scope targeted validation: acceptance failed

## Outcome

Two authorized reviewer-only calls tested candidate 039a112 with the same full-context
inputs, model and experimental reasoning configuration as the preceding comparison.
Only reviewer instructions changed. Both calls completed normally without retries.
No full assessment, correction-generation call, deployment or merge occurred.

The safeguard-specificity error is now identified correctly, alongside the study,
financing and planned-versus-delivered errors. However, the reviewer still treats
regional continuity as proof of access for the affected population, rejecting the
valid REC-003 question and repeating that mistaken objection in NARR-inclusion.
Reader diagnostics also fail the application's correction-admission contract.
**Production and ITS acceptance remain held. Both calls are consumed; no further
paid calls were made or authorized by this check.**

| Stage | Input tokens | Output tokens including reasoning | Provider time | Attempts |
|---|---:|---:|---:|---:|
| Core/readiness | 67,451 | 5,339 | 41.080 s | 1 |
| Reader | 44,168 | 2,232 | 27.846 s | 1 |
| Total | 111,619 | 7,571 | 68.926 s | 2 |

Actual model claude-sonnet-5-5; adaptive thinking with display omitted, high effort,
8,192 total output-token cap, 180-second timeout and zero retries. Both stop reasons
were end_turn. Thinking/text block types were recorded; thinking content/signatures
were not retained. These settings remain isolated experimental settings, not the
production client's configuration. One sample per reviewer is not a reliability
estimate. The four synthetic contrast cases were not sent after this failure.

## Source meaning and application admission

- REC-001 correctly identifies Kasindi's unsupported inclusion in existing studies.
- REC-005 correctly identifies a shared prioritization pool assumed across separate
  Burundi and DRC financing envelopes.
- REC-002/004 remain accepted; all four readiness decisions match expectations.
- REC-003 is falsely rejected: redeploying Goma resources to Kasindi for North Kivu
  communities does not establish access for traders connected to cancelled sites.
  More explicit credit for regional provision may improve precision, but cannot
  justify discarding the qualified distributional question.
- NARR-dividends correctly targets only the assertion of an immediate flood-ready
  facility benefit where source evidence describes planned design/construction.
- NARR-inclusion correctly identifies that generic ESF instruments and recognition
  of exclusion risk do not establish an exclusion-specific safeguard. The reason
  code is EXISTING_MITIGATION_MISREPRESENTED rather than the frozen expectation
  PROJECT_FACT_UNSUPPORTED; the explanation is nevertheless substantively correct.
- A second NARR-inclusion issue repeats the false regional-benefit/access equivalence.
  This is a new unsupported objection, not successful coverage of a valid defect.

Both responses pass their frozen native JSON schemas. All three reader quotes match
current text exactly and uniquely. Core premise reconciliation is internally valid.
However, direct application of _valid_reader_revision(response, final_reader)
returns False: two issue entries target NARR-inclusion, while the contract requires
unique issue IDs. This output would withhold reader prose without entering bounded
correction. Schema validity does not establish application admission.

Object-ID agreement is 13/14, but that count hides the added false objection, reason-
code mismatch and rejected correction diagnostic. It must not be reported as a
clean semantic pass. Independent source and code review confirmed these conclusions.
No expected labels were changed after the run.

## Execution and artifacts

The old task browser connection stalled before submission. Its dedicated Edge
session/daemon was recovered with the same saved profile, and the authenticated
terminal was verified before submission. No provider request was sent during browser
recovery. The isolated job was submitted once and its artifacts were retrieved
without resubmission. No deployed application files/settings were changed.

Local ignored artifacts:
- output/20261015-source-scope-review-preflight/{requests,manifest}.json
- output/20261015-source-scope-review-responses.json
- output/20261015-source-scope-review-evaluation.json (ID agreement only)
- output/20261015-source-scope-review-adjudication.json (semantic/admission findings)
- output/20261015-source-scope-review-bundle.json and matching ZIP
- output/playwright/20261015-source-scope-*.txt (connection/submission/retrieval)

Case SHA256: 6c78b568a3a3cb6b5ba08b13ac3662f05323e577629cd611d8a293ce55068b7b
Bundle SHA256: 8d95516706021d1a083c13e9bea9b22a56d2657ca969ed138e06b652466271c0
Response SHA256: 3888e972be577125546f9bec1244c5fd245ddd6df5dafffddcf2d20f65c9aea2
Retrieved response bytes match the remote checksum. Remote directory:
/tmp/fcv-source-scope-review-20261015-8d9551670602
Both remote prompt/schema fingerprints match the pre-frozen offline manifest.

## Next work

Do not spend a full assessment on this candidate. Isolate the disputed access claim
and its source relationship for adjudication, distinguishing a wording refinement
from grounds to discard valid analysis. Resolve multiple legitimate defects in one
paragraph within the existing bounded-correction contract without silently merging
away unsupported objections or widening edit permissions. Test the source contrast
pairs and diagnostic handling before considering further model usage. A successful
model review would still need correction/re-review and export acceptance.
