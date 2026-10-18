# Claim-level repair prototype: offline validation

## Outcome

The standalone adapter can repair two factual clauses in one paragraph, retain a
disputed analytical claim for explicit adjudication, and preserve application-owned
evidence and untouched text. It reuses the existing exact-text edit boundary.
Production integration and analytical acceptance remain pending.

## Verification

- 170 focused and connected tests passed in 8.35 seconds: prototype, curated replay,
  reader edits, reader simplification and verified pipeline.
- The initial implementation followed nine expected failing tests. Independent
  review caught optional precision incorrectly blocking acceptance; this was fixed
  and covered before the final checks.
- The saved full-reader replay retained five records, recorded three findings,
  applied two narrow edits and retained one disputed access finding for final
  adjudication. The access paragraph, evidence and unrelated records were unchanged.
- Missing coverage, stale text, overlapping edits, unsupported numeric expansion
  and unadjudicated material findings cannot produce acceptance in the tested paths.
- No provider call, full paid assessment, deployment, merge or runtime integration.
  The previous runtime suite result (1,677 passed) is historical, not a new full
  suite run for this prototype.

The saved replay is `output/20261015-claim-repair-saved-replay-verified.json`, produced
by `output/20261015_claim_repair_saved_replay.py` with the verified output filename.
Both remain local. Input evidence is the saved explicit-premise preflight and
source-scope response artifacts; historical failed results were not relabelled.
The committed fixture contains explicitly labelled synthetic source paraphrases.

## Limits and next gate

These are curated adjudications, not fresh model decisions. Exact quotes establish
traceability, not source meaning; record coverage does not prove every factual
premise was found. Execution labels do not authenticate reviewer independence, and
digests do not authenticate caller-owned state. A future orchestrator must enforce
one repair pass and spending limits. Every prototype result explicitly sets
`publication_approved` to false.

Next, validate claim identification and source adjudication in a bounded reviewer
experiment against frozen supported facts, genuine overclaims and valid analysis.
Only after that succeeds should the adapter enter the runtime correction/re-review
path and undergo cost, latency, export and full-assessment acceptance. Another full
paid assessment is not justified by this offline result alone.

See [design](20261015_climate-claim-repair-design.md) and
[preceding failed paid validation](20261015_climate-source-scope-review-results.md).
