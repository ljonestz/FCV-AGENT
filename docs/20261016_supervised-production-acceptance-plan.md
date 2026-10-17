# Supervised production acceptance plan

Status: evaluation design and audited development inventory, not release approval.
The user selected supervised production on 2026-10-16: a named reviewer checks
consequential claims before reports are shared. Minor LLM errors and inconsistent
labels are acceptable when they do not alter substantive decisions. The priority
is a usable, dependable end-to-end service, not perfect automated adjudication.

## Release outcome and boundary

A supported assessment produces a useful draft, exposes evidence and limitations,
lets a named reviewer resolve consequential issues, and preserves their sign-off
against the exact report version shared. A disclaimer alone is not sign-off. Review
must include consequential claims the model did not flag: the latest complete
replay accepted both known real-case defects.

Compare three release approaches:
- Recommended and selected: supervised production, evaluated as a human-plus-system
  workflow. Model misses are measured and matter to workload; unresolved consequential
  errors in the signed-off report block release.
- Fully automated sharing: deferred. Present evidence does not support relying on
  the model as an independent major-error gate.
- Continuing example-specific prompt tuning: development only. It cannot certify
  generalization and is not the release plan.

Assess the changed Climate workflow across its advertised supported instruments,
document stages and MPA overlays, with regression checks for normal FCV behavior.
Do not silently narrow the product's advertised scope to the cases that pass. A
route without adequate evidence stays unqualified; any initial route restriction
must be explicit to the user and approved by the release owner. This plan does not
change routing or authorize an app-wide redesign. Render and ITS deployment
acceptance remain distinct: neither inherits the other's validation automatically.

## What we know and what is missing

The latest complete isolated replay returned 56 real propositions, ten synthetic
propositions and 36 parent decisions. It missed both original consequential claims,
correctly held the three harmful synthetic parent cases, and supplied one invalid
placeholder citation. The two narrow candidate edits demonstrate repair mechanics,
not discovery reliability. Historical suite passes are not current release checks.

Audited five local development assets: Great Lakes PID, Somalia STAIRP concept PID,
the explicitly synthetic South Sudan pattern, proposition contrasts and materiality
contrasts. File existence and SHA256 fingerprints are recorded in the accompanying
JSON manifest. Great Lakes resides in the main checkout; other listed assets were
verified in the active worktree. No raw PDFs or model outputs are added to Git.

All five are development assets because they have been used in QA or calibration.
None is a fresh holdout. The external corpus was recovered at
C:/Users/wb559324/OneDrive - WBG/fcv-project-screener/FCV_Screener_test_cases;
the old configuration omitted its parent folder. Metadata inventory found 27 files
and five candidate project families: Afghanistan HCJ, Afghanistan Private, Guinea
Governance, Guinea Water and Honduras. Instrument classifications are not verified
from filenames. Guinea has related prior-test outputs; other exposure histories
remain unknown. Related PCN/PAD/BOSIB files are one family, not extra holdouts.
Explicitly synthetic Chad material, generated recommendations/assessments and issue
logs are not independent real source cases. Country-context documents supplement
projects rather than increase project counts. The local file-level inventory is
output/20261016-production-acceptance-inventory/local_corpus_inventory.json.

There are currently zero confirmed fresh holdouts and zero independently reviewed
gold documents in this acceptance inventory. This is an exposure/annotation gap,
not a missing-corpus blocker. The manifest's 12 holdout entries remain selection
slots, not completed cases or test results.

## Representative evaluation set

Start with 12 document families, selected before changing the candidate further:

| Slots | Required coverage |
| --- | --- |
| H01-H04 | IPF concept, appraisal, additional financing and restructuring |
| H05-H06 | DPF/DPO concept PID and Program Document |
| H07-H08 | PforR concept PID and appraisal/program paper |
| H09-H10 | MPA with resolved IPF and PforR base instruments; phase/program distinction |
| H11 | Lower-conflict comparator to test overdiagnosis and generic FCV assumptions |
| H12 | Ambiguous or unsupported route; visible restriction/defer behavior |

Across those slots seek at least four country contexts and three sector families,
including fragile and conflict-affected settings, a lower-conflict comparator,
regional/multicountry operations, sparse concept evidence, and dense later-stage
material. Confirm classifications and scope from the source; filenames are not
proof. Do not claim 12 documents establish broad statistical reliability. This is
a bounded first release qualification exercise; absent strata remain limitations.

Partition by project/document family, not paragraphs: related phases, revisions,
additional financing and translations of a development project are not independent
holdouts. Record previous prompt/model exposure. Any case used to tune the candidate
moves into development; use new cases for the next clean acceptance claim.

For each selected family freeze document bytes/hash, provenance/access permission,
route/stage, source date, expected applicability boundaries, selection reason and
exposure history. Do not expose expected answers, severity labels or seeded-error
locations to the model or operating reviewer during evaluation.

Use two separate tracks:
1. Natural end-to-end assessments, including generation, correction, review and
   final exports. These measure the workflow users will actually receive.
2. Source-grounded challenge variants of saved drafts: consequential errors and
   matched valid controls covering status, funding/recipient boundaries, sites and
   populations, safeguards, quantities/dates, policy applicability, causal benefits
   and false premises in recommendations. Label as deliberately seeded. They test
   review/correction sensitivity and are never reported as natural error rates.

Preserve recommendation usefulness: no quota of priorities, no mandatory wording,
no reward for suppressing all findings or producing a generic report. The old
Great Lakes minimum-priority benchmark stays historical and case-specific; it does
not become a global production rule.

## Independent reference review

Lindsey Jones is the review owner, consistent with the agreed human-review step.
The reference map must be approved by a domain human, not the development agent:
prepare source-backed critical facts/decisions before seeing candidate output, then
review novel assertions in the actual output. If the same person prepares the map
and signs off the report, disclose that this is not an independently blinded
workflow evaluation. Seek a second domain opinion for disputed consequential
findings; unresolved disputes stay visible. The generating model cannot supply the
sole reference or stand in for human sign-off. Agent-prepared evidence packets may
reduce review work but are not independent labels until actually reviewed.

Each reference finding records exact source passage/location, claimed relationship,
materiality, plausible action consequence, acceptable qualified interpretations,
valid existing provisions to retain, and any dependent recommendation. Distinguish
missing evidence from explicit contradiction. A risk or generic instrument does not
prove a specific protection; unknown effectiveness does not erase a real provision.

The operating reviewer checks all consequential conclusions in the report, not
only model objections. Evaluate the signed-off output against the source-backed
reference map. Prefer an independent evaluator for the final acceptance audit;
where staffing means Lindsey performs both rounds, use separate rounds and record
that limitation instead of claiming a blinded acceptance test.
Document selection, severity and disputes are frozen before scoring. Newly found
issues remain visible and are adjudicated without retroactively tuning a pass.

## Acceptance gates

The following are proposed qualification rules for the selected supervised boundary:

| Gate | Evidence required | Release blocker |
| --- | --- | --- |
| Source/route integrity | Complete usable input; correct instrument/stage/recipient scope; traceable citations and explicit limitations | Wrong route presented as supported; fabricated material support; silent lost input |
| Draft quality | Measure consequential factual errors, unsupported action premises, false omission claims, major omissions and usefulness | A draft too poor for practical review; misleading clean/ready status |
| Human-plus-system outcome | Independent evaluation of signed-off report, including unflagged claims | Any unresolved major error, harmful action, or consequential false correction in the acceptance set |
| Useful valid content | Compare valid controls and natural reports; source-faithful actions and qualifications survive | Generic/empty output passed merely because it makes few claims; useful grounded advice removed |
| Review operation | Named sign-off tied to report/input/model/prompt version; corrections rechecked; review status survives reload/export | Stale approval reusable after substantive change; unreviewed report presented as approved |
| Reliability | Bounded timeout/token/retry/cancellation behavior, recoverable partial failures, persisted assessment ID | Silent truncation, duplicate charge/retry, false completion, or loss of review state |
| Presentation/export | Summary/Detailed and downloaded HTML/DOCX preserve material meaning and review status | Export reintroduces an error, loses qualification/evidence, or changes approval meaning |
| Deployment | Exact SHA and configuration, authorized access, smoke/quality evidence, rollback rehearsal | Unknown deployed version, unresolved regression or inability to restore known-good service |

Minor discrepancies are logged separately and do not independently fail qualification.
A missing quote or citation is an evidence defect; judge its consequence separately,
but never fabricate a citation to make validation pass. A report is not approved
while a consequential claim lacks the support needed for the review decision.

Report major errors per document and per consequential decision, pre-review and
post-review; harmful false corrections; useful content retained; reviewer minutes
and edit count; coverage/failures; total provider calls/tokens/cost; latency. Include
failed and incomplete runs in denominators, and separate synthetic from natural
results. Avoid treating correlated clauses as independent statistical samples.
Zero observed residual major errors in 12 families is a qualification observation,
not proof that future error probability is zero or below a specified percentage.

Before live evaluation the release owner and operating reviewer must approve a
review-time ceiling and per-assessment cost/latency limits from measured pilot data.
These limits are currently unassigned and block execution of a costed acceptance
campaign; they must not be chosen after seeing held-out results. No paid budget is
created by this plan. Authorize a bounded batch with maximum total calls/tokens,
not merely a number of documents: each full assessment can make multiple calls.

## Smallest implementation path

1. Select and independently annotate the corpus; complete the manifest and freeze
   acceptance protocol. Reuse the existing test documents and synthetic fixtures
   for development only. No new provider stage is justified by this planning work.
2. Audit the existing UI, persistence, correction and export boundaries against the
   supervised workflow. Determine which capabilities already exist before coding.
   Prototype scripts' publication flags do not prove a production sign-off gate.
3. Design only the missing review controls: identity, assessed-version binding,
   decisions/edits, residual issues and approval invalidation. Draft exports may be
   necessary for review but must be visibly unapproved; approved sharing must use
   the reviewed version. Software cannot prevent screenshots or manual copying;
   controlled access and the team's sharing procedure remain necessary.
4. Exercise the workflow on development cases. A reviewer must catch the known
   delivery/safeguard failures among unflagged text and preserve valid analysis.
   Collect practical review time/cost; revise controls before freezing the candidate.
5. Run the agreed held-out campaign on an isolated preview. Use the project's
   smoke-then-quality procedure, capture assessment IDs, evidence, review records,
   exports and logs, and independently evaluate the final outputs. Do not tune on
   failures and reuse them as untouched acceptance cases.
6. Only after gates pass, propose a bounded supervised launch with an assigned
   reviewer, access list, explicit scope, monitoring and rollback. Deployment is a
   separate authorized action; this plan neither merges PR83 nor repoints services.

Reuse existing pipeline, source-provenance, exact-edit, schema, routing and export
tests. Add tests only for missing sign-off behaviors and discovered defects. Before
release initialize the pinned submodule, run focused checks then the full suite once,
and test the actual deployed candidate and downloads. Read the private parity
contract before changing shared Render/ITS surfaces; this plan changes none.

## Release monitoring and rollback

During the initial supervised launch, every externally shared assessment has a
named reviewer and immutable reviewed version. Log major corrections and near-misses,
review workload, timeout/token failures and model/config changes without recording
credentials. A major error found after sign-off triggers review of the affected
report and containment of the implicated route/version; notify affected users via
the designated operator, not autonomous agent messaging. Retain a known-good rollback
and verify approval records cannot silently attach to regenerated content.

Requalify material prompt/model/retrieval/route changes using regression cases plus
fresh acceptance evidence appropriate to their scope. A passing result on the current
case does not automatically transfer to another model, backend or document family.

## Decisions and next actions

Confirmed: supervised release; consequential errors matter more than minor wording.
Recovered: current corpus location and five candidate families. Review owner:
Lindsey Jones. Pending: establish exposure histories and source routes, select fresh
holdout families to fill coverage gaps, approve reference maps, audit workflow
capabilities, and agree review-time/cost/latency limits. Arrange a second reviewer
where needed for disputed findings or independent final audit; do not invent an
assignment. These are real gaps, not completed acceptance work.

Current deliverables: this plan and 20261016_production-evaluation-manifest.json.
No application changes, paid calls, new credentials, deployment or publication.
production_accepted=false; publication_approved=false. The immediate next tasks are
source-route/exposure classification of the recovered corpus and the workflow
capability audit. No further request for the already-recovered folder is needed.
