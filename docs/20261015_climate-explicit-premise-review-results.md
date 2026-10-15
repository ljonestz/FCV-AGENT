# Explicit-premise reviewer validation: acceptance failed

## Scope and execution

The user said proceed after targeted model validation was proposed. This check used
exactly two reviewer-only calls on candidate 8b1039c425659c07f083350b81531e6d3d3f5cef:
one conditional/core review and one reader review. No full assessment, correction
model call, retry, deployment or merge occurred. Both calls are consumed.

The saved case bytes match the previous full-context check exactly. Expected labels
were not sent to the model. The candidate client, prompts, schemas and runtime config
ran in an exclusive temporary directory on the existing Render service. The live
application stayed on main1168a8f; branch main and its shell commit were verified.
An initial oversized shell command did not create the job log. Compact transfer
subsequently started one locked job. Dashboard retrieval timed out after submission;
completion was verified from the saved log, without repeating provider calls.

| Stage | Input tokens | Output tokens | Provider elapsed | Attempts |
|---|---:|---:|---:|---:|
| Core/readiness | 66,962 | 1,330 | 11.725 s | 1 |
| Reader | 43,679 | 694 | 7.018 s | 1 |
| Total | 110,641 | 2,024 | 18.743 s | 2 |

Actual model: claude-sonnet-5-5. Calls ran 2026-10-15 10:37:57–10:38:16 UTC.
Each retained a 120-second timeout, 2,500 output-token limit and zero retries.
Token counts are not a verified monetary invoice.

## Structural checks

Both responses validate against the candidate native schemas. Every core has a
known-source premise record. All three reader objections quote a unique exact span
in the current reader. Deterministic core reconciliation admits all five because
the model labels all five qualified. The application cannot infer a false semantic
label from structurally valid IDs. The new contract was followed, but the model's
judgments remain inadequate. The prior 1,661 offline tests do not establish otherwise.

## Source-based findings

- **REC-001 remains a real missed defect.** Its minimum action puts Kasindi checks
  within the border-market feasibility studies, and its narrative says this uses
  existing sequencing. Source blocks ending c25c5b513e49 and 04ce6f66f831 scope those
  studies to Kasumbalesa/Kipushi; e0b766485dcf separately covers Kasindi construction.
  A valid climate-screening proposal does not establish that existing study scope.
- **REC-005 remains a real missed defect.** Its decision prioritizes limited funds
  among Burundi, Haut-Katanga and Angola-axis sites; its narrative calls these
  competing claims on limited funds. Blocks 48367f0bc6b4 and cc72fb7787af distinguish
  Burundi's additional grant from the DRC restructuring envelope. The reviewer
  acknowledges that distinction, but incorrectly says the core is not a tradeoff.
  It objects only to the optional draft. A sound correction would keep prioritization
  within each relevant envelope, not remove the analytical concern.
- **REC-003 exposes an overly restrictive historical expectation.** The actual core
  asks a conditional access/distribution question, explicitly warns against equating
  cancelled-site traders with displaced people or Haut-Katanga beneficiaries, and
  makes enhanced action conditional on remapping findings. Its acceptance is
  defensible. The old reject label must not be used to train away useful analysis.
  The malformed phrase “Component and Component 3” is an editorial issue, not proof
  of an invented beneficiary relationship.
- **Readiness regressed.** Only DIF-003 passed. That flag compares rounded 59/1
  million allocations with precise 59.025/0.975 million allocations, which are
  consistent. The material DIF-002 component-allocation discrepancy was not passed.
- **SUM-002 is falsely rejected.** “Most displacement” conservatively paraphrases
  the source's 92 percent. Adding the source's mid-2025 qualifier improves precision;
  the sentence does not assert an all-time universal claim.
- **NARR-design needs precision, not rejection of its underlying meaning.** “Works
  shift” is less exact than “resources and activities shift.” The source documents
  reallocation to studies, equipment, market construction and related activities.
- **NARR-inclusion has a narrow real issue.** The source identifies exclusion risk
  and generic E&S instruments, not an exclusion-specific safeguard. Narrow that
  clause. The paragraph's conditional cancelled-site access concern remains valid.
- **NARR-dividends still contains an unflagged status defect.** “The immediate
  benefit is … flood-ready border posts” treats planned redesign/construction as
  delivered status. “The intended benefit … planned flood-resilient border posts”
  would retain the analysis without the implementation-status overstatement.

All block suffixes above refer to DOC-ce08d41a57d2a4c6-B- in the saved inputs.
Root inspected the actual wording and sources after two independent read-only
semantic reviews. The frozen comparison is retained (5/14 decisions match); the
separate adjudication records corrected expectations and borderline wording.
This single-document comparison is not a statistical reliability estimate.
Even accepting REC-003 and treating the two reader precision issues generously,
the missed study scope, funding scope, implementation status and rounding error
independently establish failure. No saved failure is relabelled a successful run.

## Decision

Do not spend a full assessment on this candidate. The bounded correction machinery
is software-tested, but these calls did not exercise model-generated correction
and re-review. The reviewer still sends the wrong defects into that machinery and
misses material ones. Exact quotes and per-core source IDs did not fix that.

Before another paid test, use the adjudicated cases to assess a materially different
review approach: explicitly separate source assertions about site scope, financing
scope and implementation status from proposals, uncertainty and optional precision
edits. Compare reviewer performance on the fixed full-context inputs before another
full assessment. Do not keep broadening prompt prohibitions or reject valid analysis
merely to improve a historical score. No additional paid calls are authorized by
this completed two-call check; production and successful ITS handover remain held.

## Local evidence (not committed)

- output/20261015-explicit-premise-review-manifest.json and -bundle.zip
- output/20261015-explicit-premise-review-preflight/cases.json and runner.py
- output/playwright/20261015-explicit-premise-review-responses.json
- output/playwright/20261015-explicit-premise-review-evaluation.json
- output/playwright/20261015-explicit-premise-review-adjudication.json

Response: 6,105 bytes; SHA-256
1344555aa19cf961185b53c8e5309b6a09093326352c06fdcee6049cdf04f210.
Bundle SHA-256: 137963ab194de5a0fa7b107452887b3dda911be49c779adb300bf3b14a8c9ed6.
Case SHA-256: 6c78b568a3a3cb6b5ba08b13ac3662f05323e577629cd611d8a293ce55068b7b.
Remote directory: /tmp/fcv-explicit-premise-review-20261015-137963ab194d.
