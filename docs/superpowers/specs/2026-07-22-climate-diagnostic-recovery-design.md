# Climate Diagnostic Recovery Reliability Design

## Problem

When the Climate sector lens is active, Stage 2 can complete its visible FCV assessment without emitting the required `%%%LENS_DIAGNOSTIC_START%%%` structured block. The recovery logic introduced in `f746c96` detects that omission, but it calls `get_fast_client()`, which has a 25-second request timeout and the Anthropic SDK default of two retries.

Production evidence from the repeated 22 July 2026 test showed the resulting sequence:

1. Stage 2 completed without a lens diagnostic block.
2. Recovery started correctly.
3. Three effective 25-second attempts elapsed because of SDK retry behaviour.
4. Recovery raised `APITimeoutError` after approximately 77 seconds.
5. The core FCV assessment completed, but the climate readout and boxes were absent.

The recovery mechanism is therefore correct in intent but uses a client designed for small classification calls rather than a structured Climate-FCV diagnostic.

## Goal

Recover a missing or incomplete active-lens diagnostic reliably without adding another model call when Stage 2 already produced a valid diagnostic. A selected climate module must either produce a validated structured readout or be identified clearly as unavailable while the core FCV assessment remains usable.

## Non-goals

- Changing the Climate-FCV diagnostic schema, delimiter contract, materiality semantics, or Stage 3 priority fields.
- Changing the normal Stage 2 narrative or recommendation-note layout.
- Guaranteeing success when the model provider is unavailable.
- Adding repeated recovery attempts or an unbounded retry loop.

## Considered approaches

### 1. Increase the fast-client timeout

This is the smallest code change, but it couples lightweight document classification and research preparation calls to a much slower recovery workload. It also retains hidden SDK retries and makes unrelated fast calls wait longer. Rejected.

### 2. Dedicated validated recovery path

Keep the inline Stage 2 diagnostic as the zero-additional-latency path. Only when validation identifies a missing or incomplete diagnostic, call a dedicated recovery client with a suitable timeout and explicit retry policy. Accept the result only after the existing schema normalization and validation pass. Selected.

### 3. Always generate the diagnostic separately

This removes reliance on the inline block but adds cost and latency to every active-lens assessment, including runs where Stage 2 already complied. It duplicates valid work without providing a meaningful reliability advantage over a validated conditional recovery. Rejected.

## Design

### Dedicated client

Add a lazily initialized `get_lens_recovery_client()` alongside the existing client factories. Configure it with:

- the existing `ANTHROPIC_API_KEY` environment variable;
- a 120-second default/read timeout and 10-second connection timeout;
- `max_retries=0`, so the single application-level recovery attempt avoids multiplication from SDK retries.

The fast client remains unchanged for genuinely lightweight calls. The main streaming client remains unchanged for Stages 1-3.

### Recovery flow

`extract_or_repair_lens_diagnostic()` continues to parse and validate the inline Stage 2 block first. When it is valid, no recovery request is made.

When the diagnostic is missing or incomplete:

1. Log the existing validation reason and assessment ID.
2. Build the existing bounded JSON-only recovery prompt from no more than 30,000 characters of visible Stage 2 output plus the allowed lens/source/readout contract.
3. Call the dedicated recovery client once using Haiku and the existing bounded output budget.
4. Normalize and validate the returned diagnostic with the same production parser used for inline output.
5. Return `lens_diagnostic_recovered=true` only if the complete active-lens contract passes.

No invalid or partially parsed response may be treated as recovered.

### Error handling

Provider timeouts, connection failures, malformed responses, or incomplete responses remain non-fatal to the core FCV assessment. The response carries the existing Stage 2 parse warning, and the UI states that the climate diagnostic was unavailable rather than implying that the climate module was fully applied.

The recovery path does not retry automatically. A user-initiated rerun remains the next action after a genuine provider failure.

### Observability

Record one completion log for every recovery call containing the assessment ID, elapsed milliseconds, and success or failure status. Failure logs retain the exception class without logging prompt contents, document text, or credentials.

This makes Render verification unambiguous:

- `Stage 2 lens diagnostic recovered` confirms success;
- `Lens diagnostic recovery request failed: <ExceptionClass>` identifies provider failure;
- elapsed time helps verify a single request using the configured 120-second default/read timeout rather than multiplying through SDK retries.

### Compatibility

Both `/api/run-stage` and `/api/run-express` continue to call the shared extraction-and-recovery function, so they receive identical behaviour. This v9.18 client hardening adds no further SSE fields; the already-existing additive `lens_diagnostic_recovered` flag remains. Sector-lens delimiters, diagnostic fields, Stage 3 priority fields, and dual-build parity contracts do not change.

## Testing

The implementation will follow red-green TDD and add focused regression coverage for:

1. The dedicated recovery-client factory uses a 120-second default/read timeout, 10-second connect timeout, and zero retries.
2. `repair_lens_diagnostic()` uses the dedicated client by default and never calls `get_fast_client()`.
3. A missing inline diagnostic is recovered from a valid bounded JSON response.
4. A malformed or incomplete recovery response is rejected and produces the existing warning state.
5. A simulated `APITimeoutError` does not fail the core assessment or falsely set the recovered flag.
6. Express and step-by-step response contracts continue carrying the recovered diagnostic and warning state correctly.
7. The focused sector-lens tests and complete repository test suite pass.

## Acceptance criteria

- The production-style missing-diagnostic test follows the recovery branch and passes with a valid diagnostic.
- The recovery request cannot use the 25-second fast client or inherit two hidden retries.
- A recovered Climate-FCV diagnostic reaches Stage 3 and renders the climate interaction and dividend readouts.
- A genuine provider failure remains visible and does not corrupt or discard the core FCV assessment.
- No shared route, delimiter, diagnostic-schema, or priority-schema contract changes.
