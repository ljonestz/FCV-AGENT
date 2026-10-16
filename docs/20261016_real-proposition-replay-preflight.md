# Real proposition replay: prepared offline, UNSENT

Continues the user's approved materiality calibration and request to prepare the
real-case replay. No provider call, runtime change, deployment or publication.

## Scope and acceptance

Preserves the frozen original reader, all 30 parent sentences, complete source
registry and original expected labels. Manually chosen clause boundaries produce
56 real-case propositions; all nonpunctuation text is covered by exact, nonoverlapping
spans. Parent sentences and the full reader remain available to resolve inherited
subjects, conditions, modality and references. This is agent-curated decomposition,
not a validated automated enumerator or independent human sign-off.

Adds the six frozen materiality cases (ten propositions) in a separately scored
synthetic section. Each of the 36 parent sentences also requires a retain/hold
decision. The shallow provider envelope therefore has 102 required string keys:
66 proposition judgments and 36 parent decisions. Inner judgments use role, verdict,
severity, exact source evidence and reason. Parent decisions use handling and reason.

The original two defect targets map uniquely to their new spans:
- NARR-dividends#p0#s0~1: immediate climate resilience / flood-ready border posts.
- NARR-inclusion#p0#s2~3: safeguards against vulnerable-group exclusion.

The three original protected claims remain mapped to their exact fragments: most
climate-related displacement, qualified cancelled-site access concerns, and the
absence of stated climate criteria in new-site selection. Synthetic cases require
three major findings and preserve seven nondefects. Expected labels, target IDs,
protected IDs and parent decisions are excluded from the model prompt.

The practical gate requires all five preidentified major defects, no major flags
on protected propositions, correct expected parent handling, and no parent approved
while a major premise is flagged. Additional major findings outside the prelabelled
set require source review and prevent automatic acceptance; they are not automatically
called false positives. Exact role/verdict disagreement is diagnostic, not itself a
failure. This preserves the user's tolerance for minor inconsistencies.

Machine results always require evidence reasoning review. In particular, severity
must be justified by a concrete decision consequence, and valid qualifications must
be preserved. A label or exact source substring alone cannot prove that the evidence
supports the proposition. The historical strict scores and old harness are unchanged.

## Offline verification

13 tests pass in 0.080 seconds: a clearly synthetic one-case oracle, missing/extra
coverage, invented and cross-case quotes, empty explanation, missed major defect,
role escape, bad parent approval, tolerated minor label disagreement, binding
mismatch, duplicate JSON and truncated response. These tests establish adapter
behavior, not model performance.

Validated original hashes; exact spans and lexical coverage; unique target mapping;
unchanged original gold; exclusion of expected answers; exact decoded-command/request
equality; runner compilation. A fake SDK execution made one mock call and a second
execution failed on the exclusive lock before reaching the fake provider. No real
SDK/client was contacted. A sandbox temporary-directory WinError 5 was resolved by
running the offline mock check with normal process permissions; this was not a
product failure. Temporary artifacts remain local.

Direct AST inspection confirms the existing experiment helpers are intact; an
earlier displayed file read omitted sections. They remain unchanged. The new
adapter is self-contained because its severity and parent-decision contract differs
from the old strict-label diagnostic. Historical outputs and scorers are preserved.

## Artifacts and fingerprints

Local scaffolding, not committed:
- output/20261016_real_replay_plan.md
- output/20261016_real_proposition_replay.py
- output/20261016_test_real_replay.py
- output/20261016-real-proposition-replay-v1/: reviewer_inputs.json, expected.json,
  request.json, manifest.json, run_command.sh, offline_validation.json, offline_mock/.

Experiment: `real-proposition-v1-9a688ce18fe51886`.
Request SHA256: `9b4ceb36f65c186b5be64f8bf5501adb2a24268fdd60cce58632066a272482da`.
Prompt SHA256: `e92c6c93f61aed3893f809415814daaa47141560b1e44e2b84839b138a132e95`.
Schema SHA256: `be6e2004d241c30d938f6bc8bbacaa2a7124fe5c554719226d49cfe87fdcc65e`.
Command: 34,113 bytes; prompt: 62,695 UTF-8 bytes; shallow schema: 6,791 bytes.
The initial offline_validation.json records the first eight tests; the expanded
13-test run above followed it without altering the prepared request.

## Concrete live-call boundary

One proposed Render-shell call on the existing FCV-AGENT service, using credentials
only there: claude-sonnet-5-5, adaptive/high, max_tokens 16,384, timeout 300 seconds,
max_retries 0. Verify service/session and lock absence before submission. The command
verifies payload/prompt/schema checksums and exclusively creates
`/tmp/real-proposition-v1-9a688ce18fe51886/started.lock` before the request.

This larger 102-key envelope has not been live-tested. Schema acceptance and output
budget sufficiency remain unproven; any provider error or truncation consumes the
attempt and must be reported, not retried automatically. A successful response
must be captured once with its ADJSHA and ADJBEGIN...ADJEND envelope, then scored:

```powershell
& 'C:\WBG\Python313\python.exe' -X utf8 output/20261016_real_proposition_replay.py score output/20261016-real-proposition-replay-v1/response_blob.txt
```

The previous one-call approval is consumed. This preparation does not submit the
new request. After explicit approval for this concrete call, execute once, score,
review reasoning and stop. No correction generation, full assessment, deployment,
merge or publication is included. publication_approved remains false.
