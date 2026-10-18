# Bounded Climate calibration, 17 October 2026

## Result

The corrected saved reader passed meaning review with prompt v1.11. A separate
seven-record synthetic batch produced exactly the three expected objections,
with no objections to the four acceptable inferences. Schema validation, issue
target sets, reason-code union and unique exact quotations passed offline checks.
This is one development evaluation, not a measured production error rate or an
independent holdout. The previous v1.10 revise result remains preserved.

Recommendation prompt v2.20 generated five candidates. All five visible action
paragraphs name the Project Information Document, a permitted section and a
concrete edit. They cover selection criteria, engagement responsibility, warning
dissemination, maintenance arrangements and indicator disaggregation. No repeated
next-review-gate instruction appears. The shared renderer's actual action-section
projection was inspected offline; no new report was published or browser acceptance
claimed. Compared with the saved generation, destinations are now consistently
explicit in the visible action, though some concluding result sentences remain
formulaic. That is editorial rather than a new blocking criterion.

For example, the visible results-framework action asks the team to define existing
resilience/access indicators by displacement status, gender and location and say
how indirect costs near works would be tracked. It does not invent a baseline or
target. This is draft advice, not a project commitment.

## Remaining factual concern

The five recommendations are raw compiler candidates, not downstream-reviewed or
accepted recommendations. REC-004 repeats an unsupported premise from saved gap
RG-006: local airstrips are outside the airport authority revenue stream. PF-023
and PF-024 describe aviation revenue reform and broader operations/maintenance
frameworks but do not establish that exclusion. The original source passages
DOC-91939b7e32843c82-B-2e452cb7f0aa and
DOC-91939b7e32843c82-B-1a9b386e4fc7 were checked directly.

The useful question is how maintenance responsibility and financing cover these
assets; an assertion that a funding source excludes them is unnecessary. Preserve
this as a downstream-review acceptance case: the factual premise must be qualified
or removed without discarding the useful maintenance question. No manual edit was
made to the raw response. No new source-code repair or extra provider call followed.

## Calls and controls

User proceeded with the proposed bounded evaluation. Three calls ran once using
claude-sonnet-5-5, no retries, no tools or web research, and no full assessment rerun.
Each had a 120-second cap. Output caps were 2,500 / 2,500 / 8,000 tokens.

| Call | Input tokens | Output tokens | Duration | Outcome |
|---|---:|---:|---:|---|
| Saved corrected reader | 38,022 | 34 | 2.249 s | pass; application reader validation also passed |
| Seven synthetic records | 7,654 | 454 | 3.490 s | exactly NARR-B, NARR-C and NARR-G flagged |
| Recommendations | 30,336 | 5,680 | 35.115 s | five candidates, not downstream accepted |

Total runner time: 40.877 seconds. This short duration reflects isolated stages,
not the complete FCV pipeline. The existing spend guard reserved 1,154,676
microdollars against a new $2 ceiling; reservations are conservative bounds, not
the provider invoice. Offline request reservation checks reached the same total;
Windows temporary SQLite cleanup then raised a file-lock error after the check,
unrelated to the provider or application. No test was rerun to spend again.

Code: aa653e0. Parent public Somalia assessment:
2c30863d-cdc1-4a29-939d-25c368aeb2d0.
Isolated single-use job: /tmp/fcv-calibration-20261017-v1.
Bundle SHA256: 9036e7d3ad577e643d2e232e034fed2f7852d7872c1ad6d886108f851d47abf8.
Result SHA256: 48a9b172dae2e7e3a056f304340f628e0bea40c8140955ec3b249b386e22a209.
Result checksum matched the remote printed digest before interpretation.

## Artifacts and next boundary

Uncommitted in output/20261016-ipf-pilot-live-preflight/:
calibration-20261017.zip, calibration-20261017-result.json,
calibration-20261017-shell.txt, calibration-20261017-audit.json,
and preparation/submission/capture/audit scripts. Synthetic expected labels were
retained outside the model payload. Synthetic records are diagnostic propositions,
not a structurally complete report; they used the real review prompt and schema.

Preview remains on 98048797116a; its paid-run guard and production configuration
were unchanged. Publication approval remains false. The next acceptance boundary
is the ordinary downstream review of generated recommendations and the full live
pipeline with exports on the revised code. It must demonstrate treatment of the
funding-scope concern, rather than treating a compiler result or reader-only pass
as release acceptance. No additional call is queued.
