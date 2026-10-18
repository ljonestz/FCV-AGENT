# Shallow claim envelope: offline verified, UNSENT

## Decision

The five-claim nested schema was rejected before generation. Rather than reduce
the batch size again, remove nested judgment structures from the provider grammar.
The new candidate requires all 30 claim IDs as top-level keys, with plain string
values. Each string encodes a complete JSON judgment. The prompt supplies the
inner judgment schema once, alongside unchanged substantive rules and all frozen
claims/sources. Expected labels are never supplied to the model.

This preserves provider-enforced claim-key coverage but deliberately moves inner
structure enforcement to local validation. The provider can produce empty or
malformed strings; these are rejected, never repaired automatically or accepted.
Schema compliance alone still cannot establish correct analysis. Returning to one
30-claim call tests this new shallow transport, not the rejected nested schema.

The local decoder rejects duplicate outer/inner JSON keys and parses each string.
It then applies the previous strong local schema, defect-array consistency checks,
and unchanged adjudication/scoring harness. The fixed reviewer label is assigned
by the decoder; it does not assert model independence. No expected labels or
semantic acceptance requirements changed. publication_approved remains false.

## Offline results

23 focused tests passed in 30.22 seconds: 10 new transport tests and 13 existing
harness tests. Synthetic full-coverage scoring passes; malformed/empty/wrong-type
inner values, duplicate/missing fields, missing/extra claims, invalid roles and
fabricated quotes fail. No production code changed or full application suite ran.

All real frozen input hashes still match. The final command payload was decoded
and compared with the saved prompt/schema and binding metadata, and compiled
offline. The provider schema contains only one object and 30 required strings:
1,957 bytes, compared with 6,493 bytes for the rejected five-claim provider schema
(measured using the same JSON serialization). It has no nested arrays, objects,
enums or unions. Size reduction does not prove provider grammar acceptance.

The command omits the strong local validation schema from its embedded bundle
because Render does not use it; the local saved request retains it. The compact
command is 31,312 characters. No provider calls were made.

## Local artifacts

In the existing climate-opcs-parity worktree (uncommitted):

- output/20261016_claim_envelope.py: prepare and score, offline CLI only.
- output/20261016_test_claim_envelope.py: synthetic tests.
- output/20261016-claim-envelope-v1/request.json and manifest.json.
- output/20261016-claim-envelope-v1/run_command_compact.sh: final command to use.
- The earlier run_command.sh is a superseded, unsent larger serialization;
  do not use it. Both represent the same prompt/schema and experiment identity.

Experiment ID: `claim-envelope-v1-1fafeb556d8bb0c6`.
Prompt SHA256: `dee972a584ee2aab13ca6e8a476333d0acdbf01dce7b06441218833e3278d8dc`.
Schema SHA256: `df7482670268b66d5d067f36dec4ce617831a69a1d87df3a937aff6ffec06035`.

## Proposed next call: fresh authorization required

Exactly one call covering all 30 claims: claude-sonnet-5-5, adaptive/high,
16,384-token cap, 300-second timeout, zero retries. Existing checked runner is
reused, with checksum verification and an exclusive experiment/01 start lock.
Use only the Render FCV-AGENT shell and its credentials; no settings or deployment
changes. No automatic follow-on call or error-driven schema modification.

After an authorized call, capture a single checksum-valid ADJSHA/ADJBEGIN...ADJEND
envelope into a new blob file, then run:

```powershell
& 'C:\WBG\Python313\python.exe' -X utf8 output/20261016_claim_envelope.py score output/20261016-claim-envelope-v1/response_blob.txt
```

Only valid complete output can reach frozen scoring. A rejection, malformed
judgment or truncated output is a failure, not a detection result. Even passed=True
would cover one case only; publication and production/ITS readiness remain held.
