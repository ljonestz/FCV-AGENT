# Climate Structuring Diagnostics Design

**Date:** 29 July 2026
**Branch:** `feat/climate-readout-redesign`
**Status:** Approved for implementation

## Problem

Production build `b1f854b` completed the two-search Climate-FCV evidence step in
about 43 seconds, then the tools-disabled Haiku structuring call stopped at its
2,500-token limit after about 22 seconds. The response did not contain a
complete delimited research block. Existing logs do not show whether the
response omitted the opening delimiter, began valid JSON but was truncated, or
returned an incompatible structure.

Further prompt or token-limit changes would therefore be speculative.

## Decision

Add one diagnostic-only checkpoint around the Haiku structuring response. It
will record bounded structural metadata sufficient to locate the failure while
preserving the existing prompts, models, limits, parsing, evidence gate, error
message, and fallback behavior.

## Telemetry Contract

For the structuring response, record:

- provider stop reason;
- bounded input- and output-token counts when available;
- bounded response character count;
- opening- and closing-delimiter presence;
- whether the delimited payload parses as JSON;
- whether the parsed top-level value is an object;
- allowlisted top-level field presence;
- bounded `sources` and `claims` counts when those fields are lists;
- normalized evidence-gate code.

The diagnostic helper will return only fixed booleans, bounded integers,
allowlisted field names, and normalized status codes.

## Privacy and Safety

Never log response text, evidence claims, source titles or URLs, project
content, prompts, geographic names, provider request payloads, arbitrary JSON
keys, or exception messages containing generated content.

Tests will include sentinel sensitive text and assert that it is absent from
both the helper result and captured logs.

## Integration

Add a pure helper in `sector_lenses/research.py` and call it after the Haiku
structuring response has been converted to text and evaluated by the existing
parser and evidence gate. Emit one assessment-correlated log entry for every
structuring response, including failures.

No shared Render/Azure contract changes are involved because this is local
operational telemetry only.

## Verification and Production Procedure

1. Cover complete, truncated, missing-delimiter, and invalid-JSON responses.
2. Verify sensitive sentinel text never appears in diagnostics or logs.
3. Run the focused climate research and workflow-contract tests.
4. Deploy the diagnostic-only commit.
5. Rerun the same assessment once and inspect the correlated structuring log.
6. Form one root-cause hypothesis from that evidence before proposing a
   functional change.
