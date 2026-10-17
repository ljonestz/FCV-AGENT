# Real proposition replay: provider schema rejection, no judgments

The user authorized the prepared single call on 2026-10-16. It was submitted once
through the existing Render shell. The expected deployed commit was
1168a8f2ab2af0bcc6a3a174c4b2eeacd9403205 and the experiment lock was absent before
submission. No retry or follow-on call was made. Authorization is consumed.

Experiment: `real-proposition-v1-9a688ce18fe51886`.
The request retained the frozen 56 real-case propositions, ten synthetic propositions
and 36 parent decisions. Local request and input hashes were checked before sending;
the pasted command's decoded payload matched request.json. Windows command-length
limits required three paste chunks followed by one Enter, not multiple requests.

## Observed outcome

The provider returned HTTP 400 invalid_request_error: the compiled grammar was too
large and the schema needed simplification. The 102 required string keys were not
accepted. Elapsed runner time was 2.182 seconds. No judgments or token usage were
reported; absence of usage is not a verified billing statement.

One distinct response was extracted from repeated terminal accessibility text and
its SHA256 verified:
`54eaae2c19cad3e7e97823e28ea9ff51ed3f508e217788074bf3b4833dd0414b`.
Provider request ID: `req_011Cg5kfMUjBjtZbSoVfSf7a`.

Offline decoding verified the response checksum and request bindings and saved
response.json. The scorer then correctly rejected it with `Incomplete provider
result` (exit 1). There is no semantic score and no evidence reasoning to review.
`practical_passed` is null in the separate transport result; coverage is zero.
Neither the original defects nor the materiality cases were evaluated by this call.

The earlier synthetic six-of-six defect result remains historical evidence for that
smaller test only. This failure is a provider grammar-size limit, not evidence that
the materiality calibration or proposition reasoning succeeded or failed.

## Artifacts and next decision

Local, uncommitted under output/20261016-real-proposition-replay-v1/:
authorization.txt, paste_0.txt through paste_2.txt, submission_started.txt,
submission.txt, terminal_poll1.txt, response_blob.txt, response.json and
transport_result.json. The manifest's UNSENT state is historical; this record
supersedes it. Raw response and source files remain outside Git.

A narrow next transport change would use a small outer schema with JSON strings
for proposition judgments and parent decisions, moving full ID coverage enforcement
to the local validator. This sacrifices provider-enforced per-ID completeness;
missing, duplicate or fabricated IDs would still fail local acceptance. Retain the
frozen inputs, materiality gates, evidence checks and no-retry rule. Do not reattempt
the same 102-key schema or change gold labels to obtain a pass. This change and any
new execution have not been performed in this turn.

No runtime integration, correction generation, deployment, merge or publication.
publication_approved remains false; real-case detection remains unproven.
