# Claim batching: implemented and verified offline, UNSENT

Implements the approved [batching design](20261016_climate-claim-batching-design.md)
as local experiment scaffolding. No provider calls, runtime changes, deployment,
merge or publication approval. The existing branch and worktree are preserved.

## Prepared artifacts

Under output/ in the climate-opcs-parity worktree:

- `20261016_claim_batches.py`: offline preparation, decode, validation, command
  generation and aggregate scoring. It generates self-contained Render commands;
  the local CLI has no provider-call action.
- `20261016_test_claim_batches.py`: synthetic offline tests with a fake SDK.
- `20261016-claim-batches-v1/requests.json`: all six frozen request envelopes,
  each with full 30-claim context, all 34 sources and five required output keys.
- `20261016-claim-batches-v1/manifest.json`: input/request hashes and configuration.
- `20261016-claim-batches-v1/run_batch_01.sh`: the only generated call command.
- `20261016-claim-batches-v1/offline_validation.json`: verified preflight summary.

Experiment ID: `claim-batches-v1-09f6b11c8cc9d515`.

Batch 01 fingerprints:

- Prompt: `fe57238017119e53ddf2e07e33e77f272a596d2cc7e9833a0882cc990cf23d97`
- Request schema: `6ba66a6f52b78fdf638d09043cf92f444026422de3cc68375bfb7d7616e7d262`
- Command length: 31,308 characters.

Raw data, requests and experiment scripts remain uncommitted by the established
output/ convention. Only this result document is committed.

## Verification evidence

32 tests passed in 16.90 seconds: 19 experiment tests plus the existing 13 harness
tests. The first run encountered the known sandbox WinError 5 in pytest Temp setup;
the final run used normal process permissions. No live SDK request was made.

Checks cover complete synthetic scoring, partial/duplicate/missing/extra coverage,
duplicate JSON members, wrong experiment/batch/prompt/schema/input bindings,
fabricated/empty source quotes, inconsistent defect arrays, incomplete stop reason,
and an all-supported response that correctly fails frozen scoring.

The actual generated command was decoded and executed against a fake SDK: prompt
and schema matched, one call occurred, response markers were emitted, and a second
execution was blocked by the exclusive lock. A simulated provider rejection was
saved and its lock consumed. Command generation for batch 02 fails without a valid
batch 01 response, including when the prior response exists but is incomplete.

The saved real payloads were separately inspected: frozen input byte hashes match;
all 30 IDs appear exactly once across six batches; every request retains all context
claims and all sources; no expected labels enter the prompt; the final embedded
batch 01 payload exactly matches the saved request and its checksum. Only one call
command exists and no response files exist. Provider keyword allowlist checks pass.

The full application suite was not run: no production code changed. Provider
grammar compilation and model judgment remain untested. Five-key schemas are a
smaller candidate, not a guarantee of endpoint acceptance.

## Next bounded action requires fresh authorization

Proposed first call: batch 01 only (SUM-001#p0#s0 through SUM-001#p0#s4), using
claude-sonnet-5-5, adaptive/high, max_tokens 16,384, timeout 300 seconds, zero retries.
This tests compatibility and complete per-claim output, not whole-case detection.
Do not execute it from the local machine. Use the existing Render FCV-AGENT shell
and its environment credentials; leave deployed application code unchanged.

After authorization, disable bracketed paste in the shell and submit the frozen
run_batch_01.sh once. The exclusive lock is located under
`/tmp/claim-batches-v1-09f6b11c8cc9d515/01/started.lock`. Capture exactly one ADJSHA
and ADJBEGIN...ADJEND response into a new local blob file, then run:

```powershell
& 'C:\WBG\Python313\python.exe' -X utf8 output/20261016_claim_batches.py decode --batch 1 --blob output/20261016-claim-batches-v1/blob_01.txt
```

The decoder verifies checksums and bindings, saves the response (including provider
errors), then validates the strong local schema and unchanged harness. Any failure
stops progress. Successful decoding does not authorize another call.

After a valid prior response, a later command can be prepared offline with
`command --batch 2` (and similarly for subsequent batches). Every preceding response
is revalidated first. Each execution still needs fresh spending authorization.
No automatic retry, resizing, fallback or multi-call loop exists.

Only after all six responses validate, run `score` to aggregate in original order
and apply the unchanged frozen score. Missing files or invalid responses prevent
scoring. Never label a partial experiment passed. Publication remains false even
if the complete bounded experiment eventually passes.
