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
