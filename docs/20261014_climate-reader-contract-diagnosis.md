# Climate native reader failure and proposed repair

Status: design approved by the user on 14 October 2026; offline implementation
authorized. No further paid call is authorized. Production and ITS remain held.
Implementation and verification are recorded in
`docs/20261014_climate-reader-contract-validation.md`.

## Method and verified outcome

Inspect the actual quality9 session, manifest, returned reader response and current
source code. Replay deterministic admission against the saved assessment without
calling any provider. Compare the live repair contract with its existing tests.
Separate observed failures from explanations the retained evidence cannot prove.

Quality9 was submitted once at 18:28:58.648Z on 14 October 2026 and completed at
18:33:32.002Z. Assessment: `8733a7c5-416e-4c3b-a05e-97f744549adf`.
Test build: `2b5cf9ba0db573b82560936abd9c1311556967a7`; deploy:
`dep-db7rin87e5hc73csg06g`. Local, remote and draft PR #83 matched this build.
The Great Lakes AF PID matched SHA256
`70238ba18f619c36e0d678468779427134c5a3c77572c6e6cdfb3fd7457579c3`.

Four candidates were parsed, valid, admitted, explicitly passed by independent
core review and retained. No core action was suppressed. Five Summary gaps remain.
Two optional current-document drafts were withheld after review and one failed
wording correction. Research returned three claims from two sources, covering both
beneficiary countries; historical and off-site limitations remain explicit.

Native Summary and all three findings are fallback. `reader_review` is empty.
The manifest records `FINAL_READER_CORRECTION_SCOPE_INVALID` and
`FINAL_READER_WITHHELD`; one targeted reader correction was attempted. This is a
failed acceptance result, not production readiness. The single further paid
allowance is consumed; there is no authority for another assessment or paid review.

## Reproduced defects and missing evidence

1. The retained corrected Summary contains 274 words, exceeding the shared
   160-230 word contract. Its paragraphs contain 89, 99 and 86 words. The compiler
   prompt specifies the same limit; the correction did not deliver it.
2. Replaying the retained inclusion answer rejects the ordinary sentence-opening
   noun `Protections` as `SUMMARY_ENTITY_UNSUPPORTED`. Capitalization is being used
   as a proxy for a named actor. Previous grammatical exceptions did not solve this
   class of error. Native prose already requires independent meaning review.
3. `_reader_prompt` requires a correction to return the complete reader and copy
   every untargeted record exactly. The pipeline rejects changes to IDs, records,
   themes, evidence scope or permitted prose. A model is responsible for preserving
   immutable application state while editing selected text.
4. The pipeline assigns the correction directly to `final_reader` before checking
   scope. It retains neither the initial reader nor its precheck issues, and emits
   one generic scope-rejection code for several distinct checks. Quality9's exact
   failing comparison therefore cannot be reconstructed from its saved evidence.
   It would be incorrect to claim that a particular untouched record was rewritten.
5. Existing correction tests use short constructed responses and deep copies with
   deliberately exact untouched records. They prove those supplied cases, but do
   not establish reliable behavior for the actual generated exchange. Quality8's
   fixed structural replay had no native meaning-review pass. That was insufficient
   evidence to infer hosted prose acceptance for quality9.

Code boundaries: `climate_final_reader.py` admission;
`climate_verified_schemas.py` Summary/fragment checks;
`climate_verified_pipeline.py` final-reader loop at lines 1648-1735;
`climate_verified_prompts.py` reader/correction instructions;
`climate_verified_client.py` stage schema and call metrics.

The returned prose also needs source review: phrases describing planned protection
as an existing benefit must not be certified merely because structural checks pass.
The PID contains a future-dated March 2028 statistic despite its July 2026 date.
Neither an offline admission result nor this diagnosis supplies a semantic pass.

## Recommended design

Repair the native reader boundary while preserving the accepted-decision pipeline,
UI layout, evidence entitlement, review requirement, deadline and correction budget.

- Retain the initial reader, exact precheck issues, correction target IDs, returned
  edits, merge outcome and independent review outcome in bounded private diagnostics.
  Record a specific rejection reason and record ID. Never render diagnostic prose,
  use it as grounding, or include it as accepted export content.
- A correction returns text edits for the exact requested IDs only. Application
  code preserves IDs, themes, evidence IDs and untouched records. Reject unknown,
  duplicate, missing or extra targets before merging. The model no longer copies
  the full reader. This uses the existing one correction and shared allowance.
- Distinguish mechanically verifiable constraints from meaning. Keep schema, word
  counts, plain text, supported evidence IDs, numeric/date boundaries, accepted
  action references and mandatory source scope. For the native reader, ordinary
  vocabulary must not be rejected solely because a sentence begins with a capital.
  Unsupported actors, factual invention, changed units, negation, status, commitments
  and country-to-site inference remain failures of the mandatory independent meaning
  review. Preserve the existing strict normal FCV Summary route.
- Give the correction precise constraints: observed word count, permitted range,
  offending record and exact failure. Any merged result undergoes the complete
  structural checks and a fresh clean native meaning review. Failure keeps fallback
  and preserves independently accepted operational priorities.
- Replay the reader against frozen admitted upstream outputs. Failed reader testing
  must not regenerate research, extraction, analysis or accepted recommendations.
  Retain real failed inputs locally; commit only small non-sensitive regression
  fixtures. Do not modify or retroactively certify quality8/quality9 archives.

Alternative: render fixed prose templates directly from admitted registers. This
reduces generation uncertainty but cannot meet the requested richer, connected
dividends/fairness analysis as well. Extending vocabulary exceptions is rejected
as a continuation of the failed approach.

## Offline acceptance before any further hosted trial

- Both retained quality8 and quality9 reader responses produce explicit, reproducible
  diagnoses. Missing historical inputs are identified, never reconstructed as fact.
- A Summary above 230 words reports its exact count; a valid targeted reduction
  preserves other records. Overlong or incomplete corrections remain withheld.
- Ordinary sentence openings reach meaning review. Unsupported named actors,
  new quantities/dates, changed units, inverted meaning, completed planned works,
  unsupported commitments and country-to-site substitutions cannot be published.
- Corrections cannot change IDs, themes, evidence, untargeted records or accepted
  actions; duplicate, missing and unknown targets fail explicitly.
- No native prose is admitted without a clean independent meaning-review response.
  Provider failures, blocks, malformed reviews and exhausted allowance preserve
  accepted actions and keep fallback. There is one correction, no correction
  transient retry, and the existing deadline/output allowance remains authoritative.
- Reader, saved-session reload, browser, standalone HTML and Word use identical
  admission. Unreviewed top-level prose and diagnostic records cannot bypass it.
- Focused failing regressions precede runtime changes; connected checks follow.
  Run the full suite once after the agreed boundary change and initialized submodule.
  Document offline correctness separately from fresh generated prose quality.

No paid provider or assessment call is part of this repair plan. A future hosted
acceptance decision requires separate authority and concrete offline evidence.

## Preserved local evidence

Under the existing worktree's untracked `output/playwright/`: the actual
`20261014-quality9-session.json`, returned state snapshots, source extraction,
single-submission observer, actual HTML/Word, screenshots and Render logs.
Quality8 originals remain unchanged. Raw evidence must stay out of the PR.
