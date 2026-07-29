# Climate Research Two-Phase Recovery Design

## Problem

Production build `3d44085` confirmed the Climate lens was active and the web-search turn completed three searches, but it again ended at `stop_reason=max_tokens` without the required evidence block. Raising the output ceiling therefore did not address the architectural problem: one server-tool turn is being asked both to search iteratively and to serialize the final validated bundle.

## Architecture

Retain the existing focused search call, three-search limit, overload handling, `pause_turn` continuation, mandatory evidence gate, and 135-second attempt cap. If the final search response lacks the structured block but contains at least two `web_search_tool_result` blocks, make exactly one structuring call using the same conversation state. Pass the search response back as assistant content, append a user instruction to return only the required Climate-FCV evidence block, and omit web-search tools so the model cannot search again.

The structuring call uses at most 2,500 output tokens and only the time remaining within the original attempt cap and parent deadline. It does not increment the research-attempt count or repeat billed searches.

## Failure Behavior

Parse and gate the structuring response normally. If it still lacks a valid two-source bundle, retain the existing climate-specific failure message and block Stage 1. Never generate the generic FCV assessment for an active Climate run.

## Telemetry and Tests

Log only structural facts: recovery invoked, elapsed time, source-result block count, final stop reason, and gate status. Add regression coverage for `max_tokens` recovery, tools-disabled structuring, reuse of returned assistant content, and no recovery when fewer than two search-result blocks exist. Run only the climate research/workflow tests plus syntax and diff checks.
