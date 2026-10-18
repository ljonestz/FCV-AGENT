# Proposition diagnostic: one request prepared offline, UNSENT

Continues the approved proposition-review design and frozen synthetic contrast set.
No provider calls, app changes, deployment or merge. Publication remains false.

## Request and acceptance

One proposed call reviews all 24 propositions in 12 synthetic cases. The full
parent sentence and case-specific sources are included. Expected answers, contrast
pair mapping and expected defect IDs are excluded. Frozen input/answer hashes are
checked before preparation and scoring; the original real-case fixtures remain
unchanged.

Uses the shallow transport that completed the previous real-case call: required
proposition-ID keys with JSON-string judgment values. Provider schema is 1,087
bytes with 24 required strings. Each decoded judgment must satisfy the strong
local schema and unchanged harness, with an additional nonempty evidence_reason
for every proposition. Evidence must come from that proposition's case.

The explanation must address the proposition's subject/population, relationship,
timing and certainty where material. Evidence for neighbouring clauses cannot
establish support. Qualified inference, recommendations and faithful weaker
paraphrase remain protected; unknown effectiveness does not erase a provision.

The scorer reports coverage, frozen defect score, role agreement, verdict agreement
and each label mismatch. Automated passed=True requires complete valid output,
all six defects found, zero false positives and exact role/verdict/defect labels
on all 24 propositions. Factual defects cannot pass by being relabelled as inference.
reasoning_review_required stays true: inspect the actual explanations and evidence
before interpreting a diagnostic pass. This simple synthetic set does not establish
real-case reliability or automated proposition enumeration.

## Offline verification

22 tests passed in 2.91 seconds: nine diagnostic tests plus 13 unchanged harness
tests. Curated synthetic oracle passes. Missing/duplicate judgments, malformed
inner JSON, empty explanations, mismatched binding, truncated output and fabricated
quotes are rejected. Role-escape and all-supported responses fail scoring.

The actual prepared payload was decoded from the shell command and compared with
the saved request. Checksums, frozen input hashes, all 24 required IDs, exact input
preservation, exclusion of gold fields and runner compilation passed. The command
is 9,028 characters. No live compatibility probe was made.

## Local artifacts and fingerprints

All experiment scaffolding stays uncommitted under output/:

- 20261016_proposition_diagnostic.py: offline prepare/score CLI.
- 20261016_test_proposition_diagnostic.py: synthetic decoder/scoring tests.
- 20261016-proposition-diagnostic-v1/: request.json, manifest.json,
  offline_validation.json and run_command.sh.

Experiment ID: `proposition-diagnostic-v1-81d367bb6c2a4a58`.
Prompt SHA256: `7964c34cc8d7159a374d347ffb69c5178b10f8ce4d9890c3afabfb8a00d655a4`.
Schema SHA256: `78062658e8aae00f09bf73769764778e31f6fa40e8ee697a9ba4dfb221988855`.

## Proposed spending boundary: fresh authorization required

Exactly one Render-shell call: claude-sonnet-5-5, adaptive/high, 16,384 output-token
cap, 300-second timeout, zero retries. Use existing service credentials only.
The checked runner verifies payload hashes and creates an exclusive experiment/01
lock before the call. No automatic follow-on, fallback, correction or regeneration.

After authorization, submit the prepared command once and capture one checksum-
valid ADJSHA/ADJBEGIN...ADJEND envelope to a new response_blob.txt in the artifact
directory. Decode and score offline:

```powershell
& 'C:\WBG\Python313\python.exe' -X utf8 output/20261016_proposition_diagnostic.py score output/20261016-proposition-diagnostic-v1/response_blob.txt
```

The decoder verifies response checksum/bindings and saves the original response.
It does not repair invalid output. Stop after the result, report the score and
inspect evidence reasoning; no real-case run is authorized by a synthetic pass.
