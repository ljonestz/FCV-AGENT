# Targeted reader correction check, 16 October 2026

## Outcome

The native reader-correction schema was accepted by Anthropic after the removal
of its unsupported numeric minimum. All three requested exact text edits returned
and merged without changing evidence identifiers or untargeted prose. The check
did **not pass**: local admission rejected a corrected finding with 202 words
against the 200-word maximum. The independent meaning review was not called.
There is no new analytical acceptance or publication approval.

The corrected text restores conditional language for a country-level conflict
pathway, qualifies project-location scope, and describes unavailable operating
detail without claiming confirmed absence. These changes have not yet received
the required independent meaning review.

## Method and bounds

Replayed the saved public Somalia assessment
`2c30863d-cdc1-4a29-939d-25c368aeb2d0` using current correction/client/validator code
from code commit `4d4f4e0b97a4d6bf34e101a4550e8217e24c4d78`.
Reconstructed source passages from the same complete standard public PID and
verified every cited project source-block identifier. The correction prompt
matched the failed request's 46,212-character length. This is a targeted replay,
not a fresh end-to-end run or holdout evaluation.

After automatic approval review required explicit payload/destination consent,
the user approved sending the saved public assessment to Anthropic Sonnet 5.5
through the authenticated Render shell. The isolated checksum-guarded runner used
`/tmp/fcv-reader-repair-20261016-v1`, an exclusive job directory/start lock, and no
production application, environment, or deployment changes. The preview paid-call
block remained in place.

Limits: one correction plus at most one meaning review; 4,000/2,500 output tokens;
300 seconds aggregate; no SDK or application retries. Actual: **one** correction
call, 16,979 input tokens, 447 output tokens, 4,982 ms provider-call duration,
5.016 seconds runner duration. These are recorded token counts, not a dollar bill.
No further model call was made.

## Evidence and next decision

Uncommitted artifacts are under `output/20261016-ipf-pilot-live-preflight/`:
`reader-repair-check-result.json`, `reader-repair-shell-capture.txt`, packet,
checksum-guarded ZIP, preparation/execution/capture scripts and submission command.
The result's printed SHA256 was checked against decoded bytes before reading it.
Bundle SHA256:
`affe674d4d88f1d20e18de0f5c1fd269dfcc680987264d3be590e865d76b2f9a`.

The user approved advisory length targets with generous hard size ceilings.
Implemented 500 total Summary words and 400 per finding, retaining nonempty prose
and all evidence, number/date, exact-edit and mandatory meaning checks. Existing
strict Summary callers retain their prior range; editorial prompt targets remain.
Offline replay accepts the saved corrected reader mechanically, with findings of
114, 202 and 176 words, but still withholds it without a real meaning review.
Replay artifact: `reader-editorial-length-replay.json`. No additional provider call.

The schema transport defect is live-verified as repaired. Overall reader
acceptance remains unproven; `publication_approved` is false.

## Local verification

New regression tests first reproduced seven length-rule failures. Connected
pipeline/schema/client/render/packet/prompt checks passed after aligning one old
prompt-string expectation. The saved correction passed mechanical replay with no
issues; an absent meaning review still withheld it.

The unrestricted full suite stopped advancing while waiting on its own Playwright
driver child and was interrupted; no complete pass is claimed. A run excluding
only the four Chromium-launch tests completed with 1,789 passed and one failed in
774.33 seconds. The failure was an old research-handoff assertion expecting only
citations: the previously approved 700-character limit also admits unchanged
provider snippets in spare capacity. Updated the assertion to require the country
citations first and intact snippets; all 11 research-handoff tests then passed.
No research runtime change was made. Four browser-driver checks remain unverified.
