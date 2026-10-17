# Source-scope review repair: offline candidate

## Problem and design

The reasoning-enabled comparison caught the earlier study, financing and delivery
status errors but still substituted broad provision for narrow evidence twice:
it treated regional continuity as proof of affected-trader access, and generic
safeguard instruments as evidence of an exclusion-specific protection.

The repair adds one shared 218-word source-to-claim comparison to conditional_review
and reader_review. It requires matching population, site, activity, status/time and
relationships. Broad provisions must receive credit without establishing a narrower
claim. Conversely, an explicit matching mechanism defeats a blanket omission claim.
Risk recognition, generic instruments, risk-specific measures and effectiveness are
separate propositions. Unseen content does not mean failed protection. Correct only
the unsupported clause; preserve supported facts, proposals and qualified analysis.

This is a narrow prompt candidate, not a new factual classifier or a claim that
semantic acceptance is solved. Exact-quote admission, bounded correction and fresh
review already exist and are retained. Adding a new ledger/parser or relaxing the
acceptance gate would not independently establish the disputed relationship.

Prompt versions: conditional review2.19 and reader review1.9. No native schema,
model configuration, reasoning setting, token/retry budget, correction mechanism,
retrieval path, renderer or export contract changes. No paid calls, full assessment,
deployment or merge in this repair. The experimental reasoning settings remain
outside the production client; this prompt change does not silently adopt them.

## Contrasting evidence

New source_scope_calibration.json reuses the existing four-case offline harness.
All passages are explicitly synthetic examples, not claims about an actual project.
Each pair keeps claim wording constant and changes the supplied provision:

| Source | Claim | Expected review |
|---|---|---|
| Regional redeployment only | Credits continuity but asks how cancelled-market traders access replacement services | Preserve qualified question |
| Adds vouchers/stalls for registered cancelled-market traders | Same statement that access arrangements are not described | Correct that blanket omission; retain unregistered-trader/effectiveness questions |
| Exclusion risk and generic instruments | Says safeguards against exclusion are documented | Narrow factual clause; preserve conditional livelihood analysis |
| Adds explicit accessible registration/outreach against exclusion | Same safeguards statement | Accept documented provision without claiming proven effectiveness |

Independent review found and removed an unrelated premise ambiguity: both reader
variants now contain identical replacement-market/trader/livelihood context. This
keeps the pair focused on the existence of an explicit protective measure.
The historical full-context inputs and expected labels are unchanged. Expected
outcomes, synthetic provenance and adjudication notes are kept outside model inputs.

## Verification

- Three new prompt tests failed before insertion and passed after it.
- 171 focused reviewer, calibration, pipeline and experiment-harness tests passed.
- Rendered prompt comparison against ef589d3: only the intended two review stages
  changed; the other seven rendered stage prompts are byte-identical.
- Both contrast pairs pass existing offline fixture validation, with labels omitted
  from rendered inputs. These tests do not simulate or prove semantic success.
- Independent review found no blocking code/design issue.
- Full repository suite: 1,677 passed in 1,274.80 seconds (21m14s). All 158
  checked source/fixture hashes remained unchanged during verification.

The unchanged original case SHA256 is
6c78b568a3a3cb6b5ba08b13ac3662f05323e577629cd611d8a293ce55068b7b.
Offline preparation of the revised full-context request bytes is saved under
output/20261015-source-scope-review-preflight/ (requests.json and manifest.json).
It makes no provider request. Old expected manifests will reject the new prompts,
preventing accidental comparison against stale request fingerprints.

## Acceptance remains open

Offline tests prove instruction scope and application behavior, not whether the
model follows the revised distinctions. The earlier 12/14 result belongs to the
previous prompts. It must not be reused as validation of this candidate. A fresh
bounded semantic check should cover the paired cases and saved full-context failures
before any full assessment. No paid call allowance is created by this repair.
Successful semantic review would still leave correction/re-review and end-to-end
operational/export acceptance to verify before production or ITS handover.
