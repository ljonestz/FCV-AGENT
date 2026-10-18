# Reasoning-enabled reviewer comparison: improved, acceptance failed

## Result

Two authorized reviewer-only calls completed without retries. The same model,
case bytes, current prompts and native schemas were used with adaptive thinking,
high effort, an 8,192 total output-token cap and a 180-second timeout. Production
client settings were not changed. No full assessment, correction-generation call,
deployment or merge occurred.

The reviewer caught the study-scope, funding-scope and implementation-status errors
missed by the earlier configuration. All four readiness decisions were correct.
It preserved the valid summaries and supported design analysis. It still falsely
rejected REC-003 and missed the narrow NARR-inclusion safeguard overstatement.
**Production/ITS acceptance remains held. No further paid calls are authorized by
this experiment.**

| Stage | Input tokens | Output tokens (including thinking) | Provider time | Calls |
|---|---:|---:|---:|---:|
| Core/readiness | 66,963 | 5,967 | 42.256 s | 1 |
| Reader | 43,680 | 1,864 | 14.352 s | 1 |
| Total | 110,643 | 7,831 | 56.608 s | 2 |

Actual model: claude-sonnet-5-5. Both ended normally with end_turn and returned
thinking/text block types. Thinking content and signatures were not retained.
This compares a configuration package with historical controls, not thinking alone.
One sample per stage is not a reliability estimate. Prior responses also ended
normally: their failures were not demonstrated truncation failures.

## Source adjudication

| Target | Finding |
|---|---|
| REC-001 | Correct: existing feasibility studies cover Kasumbalesa/Kipushi, not Kasindi construction. |
| REC-002/004 | Correct: qualified maintenance/targeting analysis remains admissible. |
| REC-003 | False rejection: North Kivu regional continuity via Kasindi does not establish access for traders linked to cancelled sites. Credit for that provision could improve precision, but does not invalidate the qualified access question. |
| REC-005 | Correct: Burundi AF and DRC restructuring use separate financing envelopes; no shared allocation pool is established. |
| DIF-001 through DIF-004 | Correct: only DIF-002 is a material inconsistency; rounding and different populations/status statements are not contradictions. |
| SUM-001/002, NARR-design | Correct: supported summaries and qualified resource-reorientation analysis are preserved. |
| NARR-dividends | Correct, narrow objection: planned design/construction does not establish an immediate benefit from flood-ready facilities. |
| NARR-inclusion | Missed: exclusion risk plus generic ESF instruments does not establish an exclusion-specific safeguard. Correct only that clause, preserving conditional access analysis. |

Decision agreement is 12/14 against the prospective adjudicated manifest. Historical
labels remain unchanged; REC-003 and inclusion were adjudicated before this run.
Optional drafting was not scored because the historical normalized draft is not
fully recoverable. An independent source review confirmed both remaining failures
and the three substantive catches. This is not a clean analytical acceptance.

## Verification and artifacts

- 33 focused tests passed (harness, production client, explicit review schema).
- Both actual responses validated against their frozen native schemas.
- Remote prompt/schema fingerprints match the offline manifest exactly, including
  the injected review date. The only reader quote occurs exactly once in its target.
- Harness requires the expected offline manifest before SDK creation, reserves an
  exclusive output/start lock, limits execution to two calls and disables retries.
- Harness status alone establishes transport success, not schema/semantic acceptance.
  Actual schema and meaning checks were performed separately after retrieval.
- Bundle imports only isolated prompt/schema modules with an empty package initializer;
  it does not start or modify the deployed application.

Local artifacts (ignored, not committed):
- output/20261015-reasoning-review-preflight/{requests,manifest}.json
- output/20261015-reasoning-review-responses.json
- output/20261015-reasoning-review-evaluation.json
- output/20261015-reasoning-review-bundle.json and matching .zip
- output/playwright/20261015-reasoning-*.txt (browser submission/retrieval records)

Case SHA256: 6c78b568a3a3cb6b5ba08b13ac3662f05323e577629cd611d8a293ce55068b7b
Bundle SHA256: 40de04bfb8ae76a569199027d969c3a53f88d2dee8b99f99b5b2477be70d11b4
Retrieved response SHA256: 6d1871d56aa18203ca5f2f81349365b142df6627efdfe87c7f28aef3738b054a
The retrieved bytes match the remote checksum. Remote job256:
/tmp/fcv-reasoning-review-20261015-40de04bfb8ae

## Next bounded work

Keep the production runtime unchanged. Use the two remaining cases to test a
source-first comparison that distinguishes regional provision from access for a
specific population, and general instruments from a specific documented safeguard.
Require exact source/claim relationships and narrow correction targets while
retaining proposals and qualified analysis. Prove this offline before proposing
more model usage. Successful integration would still require bounded correction,
fresh independent review, streaming/time-budget checks and export acceptance.

Provider configuration reference:
https://platform.claude.com/docs/en/build-with-claude/thinking
