# Climate judgment timeout design

**Date:** 2026-08-03

## Problem

The post-fix South Sudan quality run completed Stage 1 but failed in Stage 2 with `judgment_review exceeded its retry budget`. The judgment call has a 60-second total budget. Its first provider attempt exhausted that budget and raised a transient error; the retry path then replaced the original exception with a generic timeout, leaving insufficient telemetry to distinguish provider timeout, overload, or connection failure.

## Design

Increase only the `judgment_review` total timeout from 60 to 120 seconds. Preserve the existing single total budget, zero SDK retries, one pipeline-owned transient retry, analytical prompts, validation gates, recommendation admission thresholds, and country-bank behavior.

Add content-free diagnostics at the verified JSON client boundary. For each failed provider attempt, record the stage, attempt number, elapsed milliseconds, exception class, provider status code when available, prompt character count, configured timeout, and remaining retry budget. Never log prompt text, model output, API credentials, or document content. If a transient failure leaves less than one second, re-raise a timeout chained from the original exception and include its class/status in the message so the root cause is not erased.

## Verification

Regression tests will establish that the judgment budget is 120 seconds, telemetry contains only bounded metadata, exhausted retry budgets preserve the original exception class/status, and retries continue to share one total budget. Existing Climate-FCV client, pipeline, workflow, rendering, and export tests must remain green. The deployed branch will be smoke-tested before one explicitly authorized replacement quality run. The full successful assessment and reader payload will be saved as JSON, and the complete reader note will be rendered to a new Markdown file labelled `preview; not approved`.

## Smoke-discovered compiler bound

The first post-fix smoke run reached `recommendation_compiler` but the cheap model exhausted the existing 5,000-token output ceiling and omitted the closing delimiter. The compiler contract implied, but did not explicitly state, the maximum-three-candidate rule and did not bound individual free-text values.

Keep the existing output-token ceiling. Make the contract explicit: return at most three recommendation candidates, preserve fewer when fewer pass, keep every free-text value to 45 words or fewer, and do not repeat the evidence package or add prose outside requested fields. Version this prompt as `climate-recommendations-v2.2`. This constrains verbosity without weakening admission gates or analytical content.

The next smoke run confirmed the compiler bound and then exposed the same verbosity failure in `conditional_review`: the small verdict schema reached 2,500 tokens without a closing delimiter. Keep that token ceiling and semantic fail-safe unchanged. Version the prompt as `climate-review-v2.1`, require exactly one JSON object with no prose, cap both `reason_codes` and `object_ids` at 12, and limit the full response to 500 words.

Reader-integrity failures now include only the executive-readout word count when the length boundary fails. This content-free metric distinguishes underproduction from overproduction without exposing assessment prose and must be collected before changing prompt or validator behavior.

## Cross-stage structured-output correction

Three related smoke failures occurred in different stages: recommendation compilation, conditional review, and bounded analysis each reached its output-token ceiling before closing the delimiter. This establishes a shared transport defect rather than three independent analytical defects. Prose-only JSON instructions allow the smoke model to spend its budget on repeated or overlong fields, and delimiter parsing cannot make an incomplete object usable.

Use Anthropic native structured outputs for all five verified stages through `output_config.format` with one stage-specific JSON schema. Close every object with `additionalProperties: false`, require all expected fields, and preserve nullable recommendation fields explicitly. Keep the deterministic fact, reference, judgment, admission, numeric-precision, semantic-review, and reader-integrity validators unchanged. Parse the returned text as one raw JSON object; on `max_tokens`, refusal, or parse failure, report only stage, stop reason, and character count.

Because unsupported schema length/cardinality constraints are not enforced by constrained decoding, retain concise prompt bounds. Fact strings are capped at 45 words and excerpts at 60; analysis is capped at 12 existing responses, six pathways, eight gaps, four opportunities, and four limitations with 45-word fields; judgment rationales are capped at 75 words. Existing compiler and semantic-review bounds remain. This reduces truncation risk without increasing output-token ceilings or weakening analytical gates.

## Candidate-level suppression trace

The first schema-constrained smoke run completed all five verified stages and produced three parsed recommendation candidates, but all three were rejected before admission. Existing aggregate telemetry identified deterministic validation and `RECOMMENDATION_NUMBER_UNSUPPORTED`, with no semantic reviewer invocation. To identify the precise candidate field without logging prose, add a maximum-three `candidate_suppressions` trace. Each entry contains only the stable recommendation ID, suppression stage (`parsing`, `validation`, `admission`, or `semantic_review`), up to 12 stable reason codes, and the names of fields containing unsupported numeric tokens with up to 12 digit tokens. Carry the bounded trace into the canonical reader technical annex and exports.


## Semantic-review targeting correction

The second schema-constrained smoke run completed parsing, deterministic validation, and admission for all three South Sudan candidates, then withheld all three at conditional semantic review. Candidate traces showed that the reviewer returned residual-gap and unresolved-capacity descriptions rather than recommendation-specific defects. The runtime also discarded every admitted priority for any non-pass verdict, even though the review contract exposed object_ids.

Advance the conditional-review prompt to climate-review-v2.3. Require revise/block findings to identify defects in the recommendation itself and to target only affected REC- identifiers. An unresolved indicator, protocol, capacity, or adaptation measure can be the valid purpose of a recommendation and is not independently a defect. Suppress only valid targeted recommendation IDs. If a non-pass verdict provides no target that resolves to an admitted recommendation, preserve fail-safe behavior by suppressing all admitted recommendations and add SEMANTIC_REVIEW_TARGET_UNRESOLVED. Carry the bounded target IDs into the canonical reader annex. Admission thresholds and country-bank generation remain unchanged.
