# Full-context reviewer validation: acceptance failed

## Authority and execution

The user explicitly approved transfer of the saved full assessment, evidence,
judgments and recommendations to the existing hosted Anthropic reviewer through
Render for two reviewer-only calls. This followed an automatic approval rejection;
submission occurred only after the explicit re-approval. Both calls are used.
No full assessment, correction-generation call, retry, deployment or merge occurred.

Candidate: 94a0f2c181b329dd5e071bb9de446808df1a078f, draft PR83.
Exact-candidate CodeQL succeeded (run 38704461293, Python job 116320297892).
The prior offline suite remains 1,630 passed; no runtime code changed in this check.

The isolated job used current client, prompts, schemas and runtime configuration,
with an exclusive job directory and start lock. Each response was saved before
completion was logged. Both native response schemas validated locally. The response
file was retrieved with matching size and SHA-256 after intermittent dashboard
connection failures. Those failures occurred after model completion and caused no
additional calls.

| Stage | Input tokens | Output tokens | Provider elapsed | Attempts |
|---|---:|---:|---:|---:|
| Core/readiness review | 65,514 | 515 | 7.370 s | 1 |
| Reader review | 43,305 | 553 | 7.204 s | 1 |
| Total | 108,819 | 1,068 | 14.574 s | 2 |

Actual model: claude-sonnet-5-5. Calls ran 2026-10-15 08:38:45-08:38:59 UTC.
Each had a 120-second timeout, 2,500 output-token cap and zero transient/SDK retries.
These are recorded tokens, not a verified monetary invoice.

## Method and limitations

The core payload contains all 104 source blocks, 60 facts, five recommendations
and four readiness flags. REC-004 is replaced with its exact saved corrected
record; the other recommendations remain the original candidates. This assembled
diagnostic input tests valid and invalid decisions together. It is not a new
assessment or a byte-for-byte replay of the truncated historical request.

The reader payload contains the five original reader objects, 85 support records,
and 34 original cited source passages. Expected labels were not supplied to either
model. Optional drafting text reconstructed from the historical records is not
scored because its normalized historical bytes are not fully recoverable.
Its presence may influence the reviewer; this run cannot isolate that effect.

Decisions were compared with the pre-existing source-backed acceptance manifest,
then the new objections were read against the full text and source. This is one
sample per stage on one saved document, not a reliability estimate.

## Observed decisions

| Area | Expected | Actual | Result |
|---|---|---|---|
| Core recommendations | Accept REC-002/004; reject REC-001/003/005 | Accepted all five | Failed |
| Readiness flags | Accept DIF-002 only | Accepted DIF-002 only | Matched all four |
| Reader | Reject NARR-dividends status overstatement only | Rejected SUM-001, NARR-design, NARR-inclusion | Failed |

REC-001 still incorrectly routes Kasindi through feasibility studies scoped to
Kasumbalesa/Kipushi (source file pages 10/13). REC-003 retains an unsupported link
between cancelled-site beneficiaries and retained-site benefits (pages 7/10).
REC-005 combines the separate Burundi AF grant and DRC restructuring envelope
(page 7, paragraphs 11-13). All three core recommendations were passed.

The most diagnostic result is REC-005: the reviewer explicitly recognized the
separate recipient/funding envelopes in its objection to the optional draft,
but reported only DRAFTING_TARGET_UNVERIFIED on REC-005::current_document while
leaving REC-005 in passed_core_ids. The source distinction was visible and noticed;
the admission decision did not apply it to the recommendation premise. This is
strong evidence that simply adding context is insufficient. It does not prove
why the model failed or that a particular redesign will succeed.

SUM-001 was again misread as saying Component 3 support started early. Its actual
sentence separately lists the care center, early trader registration and Component
3 support. NARR-design separately attributes the financing gap to Burundi flooding
and relocation to DRC conflict; the reviewer reads the concluding combined summary
as claiming DRC conflict drove cost. Both objections impose stronger claims than
the paragraphs make. Conversely, the real 'flood-ready border posts' implementation
status overstatement in NARR-dividends received no objection.

NARR-inclusion is a new, more nuanced objection. PF-031 names exclusion risk;
PF-032 and its original source paragraph also document ESF instruments in use and
further measures. The reviewer omits that support when saying only a risk is listed.
However, generic safeguards do not prove that exclusion is prevented. The phrase
'safeguards against vulnerable group exclusion' deserves narrower wording in any
future revision. This discrepancy is recorded separately rather than changing the
frozen expectation after seeing the answer. The other six decision mismatches
independently establish failure, regardless of how this borderline wording is judged.

## Consequence and next repair target

Production readiness is not established. Keep the existing production deployment,
draft PR and worktree; do not issue a successful ITS handover. No paid allowance
remains from this two-call approval. Full-run repetition is not justified by this
result.

The next design question is how to make each core factual premise and its source
scope an explicit review decision, separately from optional drafting placement,
while retaining genuinely valid recommendations when only their draft is wrong.
For reader objections, require the exact challenged span and the stronger meaning
allegedly asserted, checked against the cited passage and surrounding sentence.
These are proposed offline repair targets, not implemented or validated fixes.
Do not blindly turn every draft rejection into a core rejection: REC-004 shows
why the distinction matters.

## Local evidence (not committed)

- output/20261015-full-context-review-manifest.json
- output/20261015-full-context-review-bundle.zip (inputs and exact candidate modules)
- output/playwright/20261015-full-context-review-responses.json
- output/playwright/20261015-full-context-review-evaluation.json
- output/playwright/20261015-quality13-full-context-acceptance-v3.json

Response bytes: 3,967. SHA-256:
9a95b682d537f79533fdb250dd2e4ebcfeb6722c1c7626fe645bbfb2e59bd62b.
Bundle SHA-256:
f275e7a56ee73ba64a5cb7c335c11d12c0460d61ed3d42837d6bee62d44411d7.
Remote isolated directory: /tmp/fcv-full-context-review-20261015-f275e7a56ee7.
Raw model data and browser artifacts remain outside Git.
