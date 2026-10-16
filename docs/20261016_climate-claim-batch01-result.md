# Five-claim batch 01: provider grammar rejection

## Outcome

One authorized batch 01 request was submitted after the Render shell recovered.
It returned HTTP 400 before generation: "The compiled grammar is too large, which
would cause performance issues." No judgments, token usage or model score were
returned. No retry or later batch was executed. Publication remains unapproved.

Request ID: `req_011Cg5euZRmJkxn8g7myErF9`.
Experiment: `claim-batches-v1-09f6b11c8cc9d515`, batch `01`.
Response checksum: `6fb1df87b3074a16740dee3e8d3b2cab2da643bcc93f6deddc998372b2ea2d22`.

The earlier browser attempt timed out while focusing the terminal, before paste.
After recovery, the shell explicitly reported BATCH01_NOT_STARTED. The deployed
SHA remained `1168a8f2ab2af0bcc6a3a174c4b2eeacd9403205`. The frozen command was
checked against the saved request, submitted once, and consumed its exclusive
lock. Existing authorization is now consumed.

## Verification

Captured the terminal output and extracted its single distinct checksum-valid
response. Browser accessibility output repeats terminal text; duplicate views of
the same response were deduplicated by checksum, not treated as separate calls.
The offline decoder verified the checksum and batch bindings, saved response_01.json,
and correctly raised ValueError: Provider failed or output is incomplete.

The aggregate experiment is incomplete. Batch 01 did not pass. No batch 02 command
was generated, and no later request was submitted. The unchanged score could not
run because there are no valid model judgments.

## Interpretation and next boundary

Reducing from thirty required claim keys to five did not make this nested schema
compile. This disproves the proposed five-claim candidate's compatibility; it does
not test factual detection, evidence entailment or preservation of valid analysis.
The provider supplied no precise grammar-size threshold or offending substructure.

Stop this batch sequence. Do not reduce the batch size again or submit another
schema variant automatically. The next design decision needs to address schema
complexity itself and preserve downstream coverage/evidence checks; no further
implementation or model call is authorized by this result. Do not weaken frozen
expected labels or claim production/ITS readiness.

## Local evidence

All in output/20261016-claim-batches-v1/ (uncommitted):

- submission_01.txt and connection_attempt_01.json: earlier pre-paste failure.
- submission_01_connected.txt: successful command submission.
- terminal_01.txt: complete captured terminal text.
- blob_01.txt: one checksum-valid response envelope.
- response_01.json: persisted provider error with request/batch bindings.
- authorization_01.txt, manifest.json and requests.json: historical authorization
  and frozen preparation records. Their original UNSENT status is historical;
  this result records the consumed batch 01 attempt.

No application code, settings, deployment or merge changed. Browser remains open.
