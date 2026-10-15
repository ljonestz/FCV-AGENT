# Climate full-context repair: offline validation

## Scope and limits

The user approved an offline repair after quality13 failed. No additional model
calls or paid assessments were made. No deployment, merge to main or ITS handover
is part of this change. The saved failed assessments remain failed and unchanged.

This work changes three software boundaries and makes full-report acceptance
explicit. It does not establish that the model now reliably makes the correct
analytical decisions. Model behavior and production acceptance remain unverified.

## Changes

1. **Preserve relationships in source context.** Analysis, judgments,
   recommendations, optional drafting and the final reader receive the unchanged
   source blocks cited by admitted project facts. Blocks are deduplicated, retain
   their IDs and are not truncated or converted into guessed relationships.
   Core review already received the complete source blocks. Reader correction
   receives only passages behind its original cited project facts. Passages do
   not extend fact-citation or numeric entitlements and are not added to exports.
   Instructions require explicit site/activity and recipient/funding boundaries.
2. **Constrain correction edits.** The native response now contains exact
   old_text/new_text edits indexed by original paragraph. The application rejects
   missing or ambiguous anchors, overlapping edits, invalid targets and
   multi-sentence replacement. It preserves all text outside the selected spans,
   references and metadata. Empty edits allow a supported challenged record to
   remain unchanged, but a fresh independent review still must pass. Number/date,
   formatting and length checks remain. A single sentence can still contain a bad
   factual edit; mechanical checks are not a semantic certificate. Conservative
   sentence-boundary handling may require smaller anchors around abbreviations.
3. **Make research failure observable.** Telemetry recognizes the current
   selections response. Allowlisted numeric received/selected/invalid/admitted
   counts survive failed research handoff. No source text enters these logs.
   Missing diagnostics are distinguishable from a known zero count. Retry and
   model-call budgets are unchanged. This improves diagnosis; it does not resolve
   the unobservable cause of quality13's historical research failure.
4. **Use full-report acceptance.** A local replay verifies frozen source and saved
   artifact hashes and compares recorded decisions to source-backed expectations.
   The expectation manifest includes legitimate findings as well as false
   positives and missed defects. Reconstructed inputs are explicitly identified;
   historical raw model output remains local, outside Git. Expected decisions must
   never be supplied to a reviewer as evidence.

Reviewer instructions now distinguish compatible rounded values and status
statements, separate list items, qualified causal inference and actual unsupported
status claims. These instructions are a candidate behavior change, not a claim of
successful semantic calibration.

## Cost and compatibility

No new model calls, stages, retry allowances, dependencies or hosting changes.
Carrying cited source blocks increases input size; input-token budget constants
are not enforced by the client and must not be presented as a spending cap.
Hosted token usage and latency have not been measured. Complete blocks preserve
qualifiers at the cost of additional context. Do not silently truncate them to
claim lower cost or higher acceptance.

For the frozen quality13 source, the added context contains 34 of 104 source
blocks, 33,000 text characters and 43,322 serialized characters including metadata.
It is included in five mandatory initial generation/review calls and the optional
drafting call, and may also enter the existing correction/review sequence. This is
a character measurement, not a provider token or monetary estimate.

Stored successful assessments are not automatically re-reviewed. The native
correction response contract changed; callers must use edits, not paragraphs.
Normal FCV Summary, renderer and export admission remain unchanged. ITS retrieval
differences remain preserved and porting/deployment remains held.

Versions: facts2.8, analysis2.12, judgments2.16, recommendations2.17, core review2.17,
drafting1.7, reader1.8, correction1.5, reader review1.7, normalization2.9;
renderer2.19 unchanged.

## Verification record

- New source-handoff regressions failed on missing context before the runtime fix.
  Exact-edit and research regressions likewise failed before their respective fixes.
- Connected pipeline/client/reader verification: 165 passed. Final focused
  research/context/edit group: 113 passed. These sets overlap and are not summed.
- Frozen full offline suite: **1,630 passed in 788.14 seconds**, exit 0. All 167
  checked Python/fixture hashes were unchanged. Existing Chromium viewport checks
  were slow but passed. Submodule sync/update completed with normal permissions.
- Full-context replay tests: five passed locally (three portable evaluator/hash
  checks and two tests requiring the local archives). Clean checkouts skip only
  the two archive-dependent integration tests. The CLI itself fails on missing or
  changed archives and refuses to overwrite output.
- Replay independently verified five source/archive hashes and rebuilt 104 source
  blocks, 60 facts, five core decisions, four flags and five reader records. It
  reports seven historical decision failures: REC-001/005, DIF-003/004, SUM-001,
  NARR-design and the mixed NARR-dividends objection. This is the expected failed
  baseline, not seven newly proven model repairs.
- A native exact-edit illustration changed only the overstatement in NARR-dividends,
  preserved other records and numeric/date tokens, and remained withheld without
  a clean independent review. It does not repair bad upstream priorities.
- Independent code review found no new evidence-entitlement or correction bypass.
  The added input-cost limitation was identified and documented above.

Local evidence: output/20261015-full-context-suite.txt, corresponding -hashes.json
and -result.json, and output/playwright/20261015-quality13-full-context-acceptance-v3.json.
Raw evidence stays outside Git. Historical conditional-review input was capped;
its full semantic context is reconstructed, but normalized draft text is not
byte-for-byte recoverable and is not scored. Candidate reader input is separately
prepared with the current prompt and cited passages, without expected labels.

The next acceptance gate remains a separately authorized reviewer-only check of
this complete context. No fresh semantic pass, production-ready claim or successful
ITS handover follows from these offline results.
