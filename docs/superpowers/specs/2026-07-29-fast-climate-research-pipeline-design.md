# Fast Climate Research Pipeline Design

## Problem

Production build `c97aa85` proved that three relevant web-search result blocks were available after 98.5 seconds, but the Sonnet structuring continuation then exhausted the remaining 36.5 seconds. The existing first call is overloaded: it searches iteratively while also being instructed to synthesize project-specific claims and serialize a strict JSON schema.

## Architecture

Separate discovery from structuring by design, rather than treating structuring as failure recovery.

1. Sonnet receives a short search-only prompt. It performs at most two targeted searches, prioritizes a CCDR or other authoritative climate source plus one complementary authoritative source, and returns concise evidence notes. It is not shown the JSON contract. Output is capped at 1,800 tokens.
2. When at least two web-search result blocks are present, Haiku receives the returned assistant content plus the full project profile and evidence-bundle schema. It has no tools and cannot search. Output is capped at 2,500 tokens.
3. The existing parser and mandatory two-source evidence gate validate the bundle. An active Climate run never falls back to generic FCV.

Both calls share the existing 135-second attempt cap and parent deadline. Existing overload handling and `pause_turn` continuation remain bounded. A directly valid bundle from the first call may still be accepted defensively, but the normal path is always search then structure.

## Verification

Tests require the first call to use Sonnet, `max_tokens=1800`, and `max_uses=2`; the second call to use Haiku with no tools; and the final evidence gate to accept only a validated two-source bundle. Focused climate tests, syntax compilation, and diff checks are sufficient.
