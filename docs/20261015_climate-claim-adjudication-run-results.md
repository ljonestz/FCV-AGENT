# Enumerate-then-adjudicate: first bounded run failed (coverage collapse)

## Outcome

One authorized call was made on the Render service using its own credentials, then
scored offline. **It failed.** The model returned a single claim judgment out of
thirty enumerated claims, found zero defects, and missed both frozen true defects.
The committed harness correctly rejected the output; acceptance was withheld and
`publication_approved` stays false. No further paid call was made or is authorized.

| Item | Value |
|---|---|
| Model / config | claude-sonnet-5-5, adaptive thinking, high effort, 8,192 cap, 180s, 0 retries |
| Stop reason | end_turn |
| Usage | 16,214 input / 5,735 output tokens |
| Enumerated claims | 30 |
| Claims actually judged | 1 |
| Defects found | 0 (both frozen true defects missed) |
| Contract result | rejected (empty source_id; coverage 1/30) |
| Response SHA256 | 713e0709a937752e22923162f9519c9fbf3492e3c0f3322bf4ba3b89ced4c5c5 |

The entire returned structured text was 234 characters: one `factual_assertion`
for `SUM-001#p0#s0`, verdict `supported`, with a placeholder empty `source_id` and
empty `quoted_text`. About 5,500 output tokens were spent on hidden thinking that
did not translate into a complete structured answer.

## What this does and does not show

This is a clear negative, but it is **inconclusive about model detection ability**,
because the request did not structurally force per-claim coverage. The response
schema allowed `claim_judgments` to be any length (no `minItems`, no required entry
per enumerated `claim_id`), so the model satisfied the schema trivially with one
placeholder entry and stopped. The instruction "judge every claim_id" alone did not
compel coverage. This reproduces the handover's exact warning that mandatory filled
fields are not evidence of semantic completeness: here the one field was filled with
empty placeholders.

Two things did work as intended:
- The support-quote tightening and source-check validation caught the empty
  placeholder immediately, so a no-evidence rubber-stamp could not be accepted.
- The coverage check would also have rejected the output (1 of 30). The adapter
  withheld acceptance; nothing false was recorded as success.

The near-empty structured output despite high thinking also suggests a possible
adaptive-thinking / json_schema interaction worth isolating, but the schema gap is
sufficient to explain the result and must be fixed first.

## Decision before any further paid run

Do not launch another blind paid run. The next work is offline and falsifiable:

1. **Force coverage structurally.** Either make the schema require exactly one entry
   per enumerated `claim_id` (e.g., an object keyed by claim_id, or `minItems` equal
   to the claim count with a uniqueness/coverage check echoed back), or decompose
   adjudication into small batches / one claim per call so each claim is individually
   answered. The harness already rejects partial coverage; the request must make
   full coverage the only compliant output.
2. **Re-test offline mechanics** (the 30-claim inventory round-trips, the schema
   rejects under-coverage) before spending again.
3. Only then prepare a second bounded call, scored against the same frozen target.

Detection remains undemonstrated. A near-term supervised pilot with a human
factual-review gate is still the credible path; autonomous readiness is not claimed.
Automatic editor behaviour, core recommendations, cost/latency, UI and exports are
all still unaccepted. This document records a failed experiment, not progress toward
release.

## Artifacts (local, uncommitted)

- output/20261015-claim-adjudication-preflight/{prompt.txt,schema.json,manifest.json,run_command.sh}
- output/20261015-claim-adjudication-preflight/{response_blob.txt,response.json,result.json}
- output/20261015-claim-adjudication-realcase/{inventory.json,sources.json,expected.json}

See [design decision](20261015_climate-claim-adjudication-decision.md) and
[prior results](20261015_climate-claim-model-results.md).
