# Bounded Climate Evidence Handoff Design

**Date:** 2026-07-29  
**Branch:** `feat/climate-readout-redesign`

## Problem

The Climate-FCV search can find the required sources but still fail before
Stage 1 because the Haiku structuring request replays the complete Sonnet
conversation. For the South Sudan PCN tested on Render, that request contained
14,891 input tokens. Haiku reached its 2,500-token output ceiling after 9,300
characters and did not emit the closing Climate research delimiter. The parser
correctly rejected the incomplete payload, but the UI then incorrectly implied
that the search had not found two sources.

The earlier successful run used 2,451 output tokens, showing that the current
path is inherently close to the ceiling and therefore sensitive to source and
project length.

## Approved Approach

Replace full-conversation replay with a fresh, bounded evidence handoff.

1. Sonnet continues to run exactly two targeted web searches.
2. A deterministic helper extracts only:
   - bounded evidence-note text from Sonnet's text blocks;
   - cited source title, exact HTTPS URL, publication date or page age where
     available, and a short cited excerpt;
   - bounded project-profile fields needed to connect evidence to the project.
3. Haiku receives a new single-turn request containing that evidence packet and
   the existing Climate research JSON contract. It does not receive the original
   user prompt, tool-use blocks, encrypted search payloads, or the full assistant
   conversation.
4. The contract continues to require four to six project-specific claims and at
   least two distinct cited sources, including an authoritative source.
5. Existing normalization, trusted-host validation, evidence-gate rules, bundle
   schema, and downstream Climate Stage 2/3 behavior remain unchanged.

## Boundaries

The evidence packet will be built by a pure helper in
`sector_lenses/research.py`. It will:

- accept Anthropic response content without importing Anthropic SDK types;
- tolerate dictionaries, SDK objects, missing citation metadata, and malformed
  blocks;
- deduplicate sources by normalized URL;
- retain only trusted HTTPS URLs already present in search results or citations;
- limit note text, source count, titles, dates, and excerpts before JSON
  serialization;
- return no raw project document beyond the already bounded project profile.

`app.py` will use this helper only for the Haiku structuring fallback after two
completed search results. Direct valid Climate JSON returned by Sonnet will
continue through the current path.

## Error Handling and Diagnostics

If Haiku reaches `max_tokens` or returns only one Climate delimiter, the
research bundle remains rejected. The failure reason will explicitly identify
an incomplete or truncated structuring response so the frontend says that
Climate evidence could not be structured, rather than saying that sources were
not found.

Telemetry remains content-free and will add only:

- bounded evidence-packet character count;
- extracted source count;
- whether note text was present.

No titles, URLs, excerpts, project text, or model output will be logged.

## Testing

Tests will be written first and will cover:

1. A large simulated Sonnet response produces a bounded evidence packet with
   deduplicated trusted sources.
2. The Haiku call receives a fresh single-user-message conversation and never
   receives the original search prompt, tool-result blocks, or encrypted
   content.
3. The structuring prompt retains the four-to-six-claim contract and exact
   delimiter/schema requirements.
4. `max_tokens` with a missing closing delimiter produces the new
   structuring-specific failure reason and user-facing message.
5. Direct valid Climate JSON bypasses the structuring fallback unchanged.
6. Existing Climate research, Express, step-by-step, and sector-lens contract
   tests remain green.

## Non-goals

- Changing the mandatory Climate evidence gate.
- Dropping web research or falling back to the generic FCV assessment.
- Expanding the output-token ceiling as the primary remedy.
- Changing Climate bundle fields, downstream diagnostic fields, or Stage 3
  priority JSON.
- Modifying `main` or the ITS/FastAPI build.

## Success Criteria

The supplied South Sudan PCN must pass Stage 1 Climate research on the deployed
branch and proceed into the native Climate Stage 2 assessment without the
former sector-lens prompt-ceiling failure. The evidence packet and Haiku input
must remain bounded independently of raw web-result size.
