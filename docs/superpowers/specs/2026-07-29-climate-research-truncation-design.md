# Climate Research Truncation Design

## Problem

Production telemetry from assessment `1ab4b61c-9dc7-4070-8698-b14ecc562012` shows the focused Climate-FCV web-research call completed three searches but ended with `stop_reason=max_tokens`. The required structured evidence block was never emitted, so the mandatory evidence gate correctly blocked Stage 1. A separate completed assessment produced a generic FCV report because no Climate-FCV research telemetry was present, indicating that run reached the backend without the Climate lens active.

## Decision

Keep the existing single focused research request, three-search ceiling, two-source evidence gate, 135-second cap, overload retry, and `pause_turn` continuation. Increase the request output allowance from 2,500 to 4,096 tokens so the server-tool turn can finish its compact JSON block. Do not add a retry for `max_tokens`; this avoids repeating searches and keeps usage bounded.

Add one non-sensitive log at Express request intake containing only the assessment ID and normalized active lens IDs (`climate` or `none`). This distinguishes a routing/selection issue from a research failure without logging project content.

## Error Handling

If the larger request still returns `max_tokens` without a valid evidence block, retain the current mandatory failure behavior. Do not generate a generic FCV assessment as a fallback for an active Climate run.

## Verification

Update the focused research contract test to require `max_tokens=4096`. Add an Express intake test confirming the log records `active_lenses=climate` and does not expose request content. Run only the affected climate research/workflow tests, syntax compilation, and `git diff --check`.
