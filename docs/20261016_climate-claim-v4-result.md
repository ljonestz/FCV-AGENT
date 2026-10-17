# Claim adjudication v4: rejected before generation

Supersedes the UNSENT v4 status in
[the earlier handoff](20261016_climate-claim-adjudication-handoff.md).

The user authorized one v4 call. It was submitted once through the existing
Render FCV-AGENT shell, with prompt/bundle checksum verification, an exclusive
v4 run lock, and zero retries. Anthropic returned HTTP 400:

> The compiled grammar is too large, which would cause performance issues.

Request ID: `req_011Cg5bdRnpsJisAvwdi2TFf`.

No model response, judgments, usage report or score was produced. Detection
remains unproven; `publication_approved` is false. No runtime changes, deployment,
merge or additional request occurred. The single-call authorization is consumed.

The request used the documented provider schema subset, zero union fields and
30 required claim keys. Removing unsupported keywords did not resolve the
provider's overall grammar-complexity limit. The precise complexity threshold
was not supplied. Offline JSON Schema validity does not prove provider compilation.

## Decision needed

Stop iterating on this single-call schema after the three provider rejections.
The recommended next design is smaller claim batches, retaining required keyed
coverage within each batch and validating full coverage/uniqueness across the
combined response with the unchanged harness. Batch size, total request budget,
failure handling and fresh run authority need agreement before implementation
or calls. No v5 candidate has been prepared or submitted.

## Local artifacts

Under `output/20261016-claim-adjudication-v4/` in the existing worktree:

- `authorization.txt`: the user's fresh one-call authorization.
- `submission_cli.txt`: submission record.
- `terminal_error.txt`: captured shell output including the request ID.
- `result.json`: verified rejection status; score null; publication false.
- Existing prompt, schemas, checksums and command remain for reproducibility.

Raw artifacts remain uncommitted. The browser session remains open.
