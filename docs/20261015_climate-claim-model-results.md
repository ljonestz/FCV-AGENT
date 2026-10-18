# Claim-level model check: detection failed, adjudication passed

## Outcome

Two explicitly authorized reviewer calls completed with no retries. The first
returned no findings across all five original records, missing both frozen factual
defects: an immediate flood-ready benefit from planned facilities, and generic
safeguard instruments described as exclusion-specific safeguards. The adapter admits
this structurally complete empty review. This is a semantic detection failure, not
a JSON, browser, Render or correction-admission failure.

The second reviewer assessed the entire manually corrected reader and the three
prior findings. It correctly accepted both narrowed factual clauses and rejected
the mistaken affected-population access objection. Its explanation distinguishes
regional benefit intent from preserved access for communities near cancelled sites.
All exact source quotations, record/finding coverage and the current-reader digest
pass the actual prototype finalizer. The finalizer returns
`accepted_offline_prototype` with `publication_approved: false`.

**Overall acceptance failed.** The second call used pre-frozen manual corrections
and prior findings, independently of the first response. This is not a successful
automated detection/correction/re-review chain, nor proof of broad model reliability.
No automatic editor was tested. No full assessment, deployment or merge occurred.

## Verification and usage

| Call | Input tokens | Output tokens | Provider time | Result |
|---|---:|---:|---:|---|
| Claim discovery | 14,465 | 1,726 | 14.758 s | Missed both expected defects |
| Independent adjudication | 18,293 | 3,549 | 35.733 s | Correct on the three supplied findings |
| Total | 32,758 | 5,275 | 50.491 s | Overall failed |

Both calls used claude-sonnet-5-5, adaptive thinking, high effort, an 8,192 output
token cap, 180-second timeout and zero retries. Both ended normally. This was a
single sample per task, not a reliability estimate. Both response schemas and
prompt/schema fingerprints match the frozen requests. All 34 source passages and
five original reader records match the preceding saved case exactly.

The remote job ran once in an isolated temporary directory on the existing
FCV-AGENT service. Deployed SHA remained 1168a8f2ab2af0bcc6a3a174c4b2eeacd9403205;
application files and settings were not changed. An automatic approval review
initially blocked submission; the user then explicitly approved the exact payload
and destination. No calls occurred before that approval. Both authorized calls are
now consumed; this experiment provides no authority for additional paid calls.

## Implication

The clause-level repair mechanism handles the saved correction and dispute safely.
The unresolved bottleneck is discovering unsupported factual premises. An empty
findings list with complete record coverage is insufficient evidence of a complete
factual review. The second model result supports targeted adjudication only; it
cannot compensate for defects the first reviewer never identifies.

Do not proceed to another full paid assessment on this evidence. Fully automatic
production acceptance remains held. A supervised pilot would require an explicit
human factual-review gate; an automated release needs separate evidence that the
reviewer reliably finds defects and preserves valid analysis. Neither is claimed
complete here. Core recommendation review and automatic editor behavior were outside
this two-call test.

## Local artifacts (not committed)

- output/20261015-claim-model-preflight/{requests,manifest,readiness}.json and run.py
  (readiness records the pre-approval state).
- output/20261015-claim-model-bundle.json and matching ZIP
- output/20261015-claim-model-responses.json
- output/20261015-claim-model-evaluation.json
- output/playwright/20261015-claim-model-submission-approved.txt
- output/playwright/20261015-claim-model-terminal-final.txt

Remote directory: /tmp/fcv-claim-model-20261015-0642badbc445.
Retrieved response SHA256 matches the remote value:
d73738f1444714d83a15e6883454a86a6f826fa3ed993abba4d6bdaa387466b0.

See [prototype validation](20261015_climate-claim-repair-validation.md).
