# Proposed offline design: bounded claim adjudication batches

Status: design for review. No implementation or provider calls authorized by this
document. Continues the existing branch and worktree; no deployment or merge.

## Objective and evidence

Judge every frozen claim against the supplied evidence, finding both known factual
defects while preserving valid qualified analysis. Retain the enumerate-then-
adjudicate mechanism and the committed harness. Do not return to asking the model
to volunteer defects.

V1 produced only one of thirty judgments. V2-V4 produced no judgments: the provider
rejected union count, an unsupported array keyword, then overall grammar size.
These later failures test request compatibility, not detection quality. Batching
is a hypothesis for reducing grammar complexity; five keys are not guaranteed to
compile until tested on the endpoint.

## Options

| Approach | Advantage | Cost or limitation |
|---|---|---|
| Five claims per call (recommended) | Six small schemas; retains required keyed coverage | Repeats context six times; endpoint acceptance unproven |
| One claim per call | Smallest schema and clearest failure attribution | Thirty calls and substantial repeated input |
| One unconstrained/list response for all claims | One call and smallest request schema | Reintroduces the observed incomplete-output failure; offline rejection cannot force generation |

Use five claims in original inventory order. Do not select or reorder using expected
defects, and do not optimize batch membership after seeing model results.

## Frozen partition

Read the existing inventory; take consecutive slices of five. Inspection confirms
30 unique claims across five records, yielding these six batches:

| Batch | First claim | Last claim | Count |
|---|---|---|---|
| 01 | SUM-001#p0#s0 | SUM-001#p0#s4 | 5 |
| 02 | SUM-002#p0#s0 | NARR-design#p0#s0 | 5 |
| 03 | NARR-design#p0#s1 | NARR-design#p1#s2 | 5 |
| 04 | NARR-dividends#p0#s0 | NARR-dividends#p1#s1 | 5 |
| 05 | NARR-dividends#p1#s2 | NARR-inclusion#p0#s2 | 5 |
| 06 | NARR-inclusion#p0#s3 | NARR-inclusion#p1#s3 | 5 |

Record order is SUM-001 (5), SUM-002 (4), NARR-design (6), NARR-dividends (7),
NARR-inclusion (8). Batch boundaries may cross records; full context is retained.

Freeze input byte hashes before preparing requests:

- inventory.json: `c755359f2501a9d309eeb73e2010c82899c74e73a9240b8a630fdd659acadaa1`
- sources.json: `3eeeb64b1625a598e4f37e1554928100d74044a433cd4406c077d94471b1b988`
- expected.json: `1c364b221ef7281e5a9d04f1f9211fb88cc63c7526ab8ae65397efd256641379`

These are the existing files in `output/20261015-claim-adjudication-realcase/`.

## Request and validation contracts

Each request receives the same full 30-claim context and all 34 source passages
as v4, plus the five selected IDs. Replace the instruction to judge every context
claim with an explicit instruction to judge only the selected IDs; other claims
are context, not requested output. Never include expected labels or previous
model judgments. Keep the substantive adjudication rules unchanged.

The request schema requires exactly those five keys and forbids additional keys.
Reuse v4's provider-subset judgment shape: role, verdict, is_defect, defect array,
and support_source_checks. No unions, maxItems or minLength in the provider schema.
Keep strong local validation: nonempty quotes and source IDs; zero defect objects
when is_defect is false, exactly one when true. Preserve exact-quote checks.

Bind every request/response to experiment ID, batch ID, selected IDs, prompt hash,
request-schema hash and frozen input hashes. Never mix artifacts from different
candidates, inputs or runs. The request builder must fail on input hash drift.

For each response: verify its checksum and prompt hash, require end_turn, validate
the local schema and exact batch coverage, then convert the keyed object to the
existing list contract. Validate against a copy of the full inventory retaining
the original reader/digest but selecting only that batch's claims. This allows the
unchanged adjudicate_claims harness to check evidence and semantic invariants early.

After all six batches validate, combine raw converted judgments in original claim
order, reject duplicates or missing/extra IDs, and call adjudicate_claims again
against the original full inventory. Only then call score_against_expected with
the untouched expected.json. One experiment-level reviewer label is sufficient;
it does not imply six independent reviewers.

## Failure handling and proposed spending boundary

Prepare all six payloads offline, but initially seek authorization for batch 01
only. It is a compatibility/completeness check and cannot establish whole-case
detection. Do not choose the first batch by known defect location.

Retain the comparison configuration: claude-sonnet-5-5, adaptive/high, max_tokens
16,384, timeout 300 seconds, max_retries 0. Each batch has its own exclusive start
lock, created before its request. No auto-retry, timeout resubmission, fallback
model, automatic batch-size change or repair request. Do not import old locks or
authorization. A failed attempt consumes that batch's authorization.

If batch 01 succeeds structurally, report actual usage and seek fresh authorization
for the remaining identified calls before continuing. Execute sequentially and
stop on any provider error, timeout, incomplete response or validation failure.
Preserve successes and errors; a partial set is INCOMPLETE, never a passed run.
No additional request may be launched merely to fill missing coverage.

The proposed full experiment is six calls maximum, 98,304 aggregate output-token
cap (including thinking), and up to 30 minutes of configured request time plus
overhead. Full evidence repeats in every input, so input cost is higher than one
call. No dollar estimate or price assumption is asserted here; use actual first-
batch usage and current pricing when requesting the remaining spending authority.

Run only in the existing Render shell using its environment credentials. No SSH
registration, credential extraction, app setting changes, deployment or full run.

## Offline implementation and acceptance checks

If approved, build one experiment-specific preparer/decoder under output/, reusing
the existing harness and v4 transport. Keep raw sources, prompts and responses
uncommitted; commit only synthetic tests and concise documentation if needed.

Required checks before requesting any call:

1. Partition is deterministic, six groups of five, disjoint, union equals all 30
   original IDs; input hashes and expected labels remain unchanged.
2. Every payload preserves all context claims and all source passages, excludes
   expected labels, and requires only the selected five output keys.
3. Provider keyword allowlist passes; local constraints remain intact. Verify the
   final embedded command payload, not only the schema-builder source.
4. Synthetic complete responses round-trip through conversion and aggregation,
   finding two labelled synthetic defects with no false positives.
5. Missing/extra/duplicate IDs, wrong batch or prompt hash, mixed-run artifacts,
   empty/fabricated quotes and inconsistent defect arrays are rejected.
6. A partial batch set cannot produce a whole-case pass; an all-supported fixture
   fails frozen scoring when true defects exist. Existing 13 harness tests pass.
7. Runner stops after the first failure; start locks prevent duplicate calls.
   Exercise this offline with a fake provider, never a live connectivity probe.

Live acceptance remains: 30 valid judgments, both frozen defects detected, zero
false positives, and passed=True from the unchanged scorer. Exact quotes establish
traceability, not entailment: inspect the two defect judgments and protected
analysis against their sources as a separate qualitative check. Do not relax the
frozen scoring labels to accommodate new outputs; report disputes separately.

Even a pass validates one reader case only. Enumeration completeness, automatic
editing, core recommendations, cost/latency and UI/exports remain unaccepted.
publication_approved stays false. No supervised-pilot product change is included.
