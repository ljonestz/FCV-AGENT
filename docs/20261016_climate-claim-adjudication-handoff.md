# Claim adjudication: v2/v3 rejected before generation; v4 prepared

## Current outcome

Neither request produced model judgments. Detection remains unproven and
`publication_approved` remains false. No runtime changes, deployment, merge,
full assessment, or automatic retries were made.

- v2: one authorized request rejected with HTTP 400 because the 30 nullable
  defect fields exceeded the provider limit of 16 union parameters.
  Request ID: `req_011Cg5az85Sn4JCg1fP7bWZT`.
- v3: one request authorized by the user's subsequent "proceed" was rejected
  with HTTP 400 because array `maxItems` is unsupported.
  Request ID: `req_011Cg5bKWkVCtxZpaZQcX2iD`.
- Both calls used Render FCV-AGENT (`srv-d6de99jh46gs73d0jjrg`), whose shell
  reported deployed SHA `1168a8f2ab2af0bcc6a3a174c4b2eeacd9403205`. The commands
  embedded the experimental prompt/schema, independent of deployed application code.
- Existing v1 response files were preserved; they are not v2/v3 results.

## Prepared next candidate: v4, UNSENT

The transport uses a required object keyed by all 30 claim IDs. Each `defect`
is an array: empty when `is_defect` is false, exactly one object when true.
The decoder rejects inconsistent cardinality before converting to the unchanged
committed harness's nullable-object contract.

After v3, the provider documentation was checked:
[Structured outputs: JSON Schema limitations](https://platform.claude.com/docs/en/build-with-claude/structured-outputs#json-schema-limitations).
It excludes string length constraints and array constraints beyond `minItems`
of zero or one. V4 therefore separates:

- `request_schema.json`: provider-supported keywords only, zero unions, all
  30 claim keys required; no `maxItems` or `minLength`.
- `schema.json`: strong local validation retaining these constraints.
- Existing harness: coverage, uniqueness, exact source quotes and frozen scoring.

Offline verification passed: provider keyword allowlist, required-field coverage,
synthetic two-defect oracle through transport conversion, missing-key rejection,
inconsistent-array rejection, and generated-runner compilation. The unchanged
harness suite passed: 13 tests. These checks do not establish live API acceptance.

One future v4 call would use the same model and budgets: `claude-sonnet-5-5`,
adaptive/high, 16,384 tokens, 300-second timeout, zero retries. Its fresh lock is
`/tmp/fcv-claim-adjudication-20261016-v4/started.lock`. Fresh user authorization
is required; the v3 one-call authority is consumed.

## Local artifacts (uncommitted)

All paths are relative to the `climate-opcs-parity` worktree:

- `output/20261015-claim-adjudication-preflight/20261016_v2_terminal_error.txt`
- `output/20261015-claim-adjudication-preflight/20261016_v2_result.json`
- `output/20261016-claim-adjudication-v3/terminal_error.txt`
- `output/20261016-claim-adjudication-v3/result.json`
- `output/20261016_claim_adjudication_v3.py`
- `output/20261016_claim_adjudication_v4.py`
- `output/20261016-claim-adjudication-v4/`: prompt, local/request schemas,
  manifest with checksums, and `run_command.sh`.

After an authorized v4 call, capture `ADJSHA` and `ADJBEGIN...ADJEND` into
that v4 directory's `response_blob.txt`, then run:

```powershell
& 'C:\WBG\Python313\python.exe' -X utf8 output/20261016_claim_adjudication_v4.py --score
```

The scorer verifies response and prompt checksums, stop reason, local schema,
transport consistency, the unchanged harness and frozen expected outcomes.
Do not infer success from API completion alone. Publication stays unapproved
even if this bounded detection experiment passes.
