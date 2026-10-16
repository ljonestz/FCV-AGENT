### 2026-10-16 Advisory native reader length

Native Climate reader word targets are editorial guidance: Summary 160-230 and
findings 70-180 words. Hard runaway-output ceilings are 500 total Summary words
and 400 per finding; nonempty prose, evidence, numeric/date, exact-edit and meaning
checks remain required. Strict Summary callers retain their prior length contract.
Never truncate prose or treat mechanical admission as a clean semantic review.
Reader/correction/review versions v1.10/v1.7/v1.10; normalization v2.13.
See docs/20261016_reader-correction-live-check.md for the paid check and offline replay.

### 2026-10-16 Native correction schema and PID display

Do not put numeric bounds such as minimum in native Anthropic output schemas.
reader_correction uses integer paragraph_index; apply_reader_corrections enforces
nonnegative/in-range integer values locally before applying exact edits. Tests
cover every stage schema, including rarely reached corrections. Independent
meaning review remains required. The paid acceptance reached meaning review but
its correction request failed; no post-fix paid validation is claimed.

The shared reader projection displays PID in recommendation prose and drafting
destination labels. Preserve lowercase internal routing values and the immutable
assessment; do not rewrite saved evidence or identifiers for presentation casing.

### 2026-10-16 Research admission and reader tolerance repair

Climate search now supplies the same allowed_domains that downstream provenance
validation accepts. Previously unrestricted searches spent their two-search budget
on results later rejected by the fixed domain list. Provider-owned quotations up
to 700 characters (the existing claim-text bound) are preserved whole across packet,
normalization and matching; the 12,000-character packet cap, exact proof checks,
country/project linkage and existing search/call/time limits remain. Never clip a
long quote or manufacture a shorter one to force admission. This follows normal
FCV's whole-passage approach with Climate's smaller context budget.

Final-reader normalization drops only empty or punctuation-only paragraph entries
and folds excess paragraph breaks without deleting substantive text. Raw output
stays in diagnostics. All word-count, evidence-ID, factual and meaning checks run
after normalization; a reviewer block still withholds the reader. Normalization
version v2.12. Recommendation prompt v2.19 removes the compulsory reviewer-at-next-
gate clause and requests the current document/allowed section, concrete edit or
decision, completion evidence, and distinct later preparation work when relevant.
These specificity instructions are not new admission gates. No policy authority,
new formal milestone, approval or implementation commitment is inferred.

Normal FCV also retains single-source coverage as limited; Climate still requires
two distinct cited sources and beneficiary coverage for live-grounding admission.
Do not equate that coverage threshold with falsity of a retained individual quote.
Changing partial-evidence use would require preserving its limited status through
grounding and exports; this repair does not silently relabel it complete.

### 2026-10-16 General final-reader evidence safeguards

Reader compilation uses a request-scoped JSON-schema enum of the supplied support
registry. Empty registries fail before provider calls. This constrains identifiers,
not truth or semantic relevance; application validation and independent meaning
review remain mandatory. Invalid references are checked even when text is overlong.
Findings target 70-180 words; up to 200 are allowed to preserve qualifications, with
no exception to evidence, numeric/date or semantic checks. Withheld reader diagnostics
carry the actual precheck codes. Reader/correction versions v1.9/v1.6; normalization
v2.11. Research logs now report bounded numeric passage rejection counts without
quotes or source titles; admission rules are unchanged. No case-specific ID mapping,
quote truncation, new model calls, or publication approval is introduced.

### 2026-10-16 Late MPA descriptions and internal metadata

Climate routing retains the short header check and also recognizes explicit
current-operation MPA self-descriptions across prepared primary-document blocks.
This fixes the standard Somalia PID whose MPA Phase 1 statement follows long
country context. Other-project, future, negated and supporting-document examples
must not activate the new body matcher. IPF remains the base instrument.

Fact extraction, recommendation compilation and conditional review now distinguish
operation_context routing metadata from uploaded evidence. An internal mismatch
is not a source-document inconsistency. Corresponding prompt versions are facts
v2.9, recommendations v2.18 and conditional review v2.20. No schema change.
See current HANDOFF for verification. Historical model output remains unchanged; no new paid acceptance.

### 2026-10-16 Opt-in preview spend reservations

All four Anthropic clients accept the same opt-in HTTP request hook when
FCV_PILOT_BUDGET_MICROUSD and FCV_PILOT_BUDGET_DB are both set. Default is off.
The hook reserves before each send, including retries, using text bytes plus4096
framing headroom and full output cap at pinned known rates with a2x margin.
SQLite updates are atomic across clients/workers and reservations are never
refunded. Unknown request fields, server tools/MCP/compaction, nontext blocks,
caching and unpriced routing are rejected before send. This is a controlled
single-instance preview-campaign guard, not an account billing system.

The ledger survives worker restarts but NOT Render ephemeral-filesystem replacement.
Use fixed phase-specific allowances whose sum never exceeds the authorized total;
after any mid-phase replacement subtract all previous reservations before starting
another ledger. Blocked optional research must be disclosed; it is not equivalent
to a full web-grounded acceptance run. Production remains default-off.

# FCV Project Screening App — Claude Development Guide

### 2026-10-16 External human review packet

User selected approval in an existing authenticated organisational workflow.
Climate Summary, Detailed, HTML and Word now say Draft - human review required;
client approval flags cannot remove that status. The review-packet download reuses
the snapshot mismatch gate and creates a ZIP containing Detailed HTML, Word,
canonical snapshot JSON, a checksum manifest, blank named-review template and
instructions. The actual report files and snapshot have SHA-256 hashes; both
reports display the snapshot ID. Reviewer identity, decision and workflow reference
must be recorded externally. No approval is imported or asserted by the app.
Changes require a new packet and review against actual file checksums held in the
authenticated record. Source uploads are not bundled; the reviewer must resolve
source access/provenance and all consequential claims, including unflagged claims.

Render read-only check: service srv-d6de99jh46gs73d0jjrg remains on main with
commit-triggered auto-deploy. This PR branch was not deployed. No in-app identity
or durable approval storage was found in repository review. Workspace database
inventory was unavailable without selecting a workspace; no inventory absence is
claimed. No new infrastructure, paid calls, merge or live acceptance.
Synthetic packet: output/20261016-external-review-packet/synthetic-review-packet.zip.
Validation: 1,732 full-suite tests passed in 1,605.74 seconds (26:45);
187 connected packet/renderer/route tests passed. Read-only review found no
blockers. Synthetic HTML inspected in headless Edge at desktop and phone widths,
with readable notice/hash and no phone overflow. Word content/checksums were
verified programmatically; no visual Word-layout acceptance is claimed.


### 2026-10-16 Climate export consistency boundary

Climate HTML and Word exports now share a no-model assessment/reader consistency
check. Supplied stale or edited readers receive READER_SNAPSHOT_MISMATCH (409),
not a silently rebuilt report. Canonical assessment corrections remain exportable.
The HTML path checks before downloading and rejects an in-flight report change.
Runtime readers use JSON-compatible evidence values and deterministic evidence
ordering so saved/restored reports can pass the same boundary. A SHA-256 snapshot
identity includes the complete supplied assessment and projected reader; it is not
an authenticated approval or independent source verification. Publication approval
remains false. Older mismatching saved readers require regeneration from their
assessment; missing-reader legacy Word requests still export the canonical draft.
No provider calls, prompt changes, merge or deployment. Validation: 1,721 full-suite tests passed in 1,064.31 seconds using Python
UTF-8 mode and normal process permissions; final snapshot tests 17 passed.
Read-only code review found no remaining blockers. The first default-encoding
run was stopped after reproducing a Windows cp1252 subprocess error; the UTF-8
full rerun passed. No live-service acceptance is claimed.


> **Maintenance instruction:** After every substantial change (new features, prompt changes, new delimiters, UI additions, architectural decisions), update this file AND the relevant reference doc before committing. Keep section 1.3 (Stage pipeline), section 3 (Prompt Architecture), and section 5.3 (Priority Parsing) accurate at all times.
>
> **Reference files** (detailed specs moved here to keep this file under 40k):
> - `docs/reference/reference_prompt_architecture.md` — per-stage prompt specs, delimiter schemas, parsing details
> - `docs/reference/reference_frontend_functions.md` — JS function list, Express mode architecture, removed items
> - `docs/reference/reference_sector_lenses.md` — module packages, budgets, selection, delimiters, and parity contract
> - `docs/reference/reference_backend_routes.md` — all routes, SSE event shapes, parsing function signatures

---

## Overview

### 2026-10-15 claim-level paid check: overall failed

Both authorized calls completed normally, without retries. Discovery returned no
findings and missed both known factual defects. Independent review of the manually
corrected reader accepted the two narrow edits and correctly rejected the false
access objection; schemas, source quotes and the finalizer pass. This is successful
targeted adjudication, not an automated detection/correction chain or release pass.
Usage: 32,758 input / 5,275 output tokens; 50.491 seconds provider time. No full run,
deployment or merge. No additional paid authority. Production/ITS acceptance remains
held because missed factual premises remain unresolved. See [results](docs/20261015_climate-claim-model-results.md).

### 2026-10-15 claim-level repair: offline prototype verified

A standalone adapter now records exact factual findings, permits multiple narrow
edits in one paragraph, retains disputed analysis for explicit adjudication and
requires complete final review. Optional precision alone cannot block acceptance.
Production prompts, runtime and deployments are unchanged.

170 focused/connected tests passed. Curated replay of the saved five-record reader
made two factual edits and preserved the disputed access paragraph and all evidence.
This validates mechanics, not fresh model judgment. No paid calls were made;
production/ITS acceptance remains held. The next gate is bounded claim-level model
validation before runtime integration or another full paid assessment.
See [validation](docs/20261015_climate-claim-repair-validation.md).

### 2026-10-15 source-scope paid validation: failed

Two targeted calls on 039a112 are consumed, no retries/full assessment/deployment.
The reviewer catches safeguard specificity but still falsely equates regional
continuity with affected-population access in REC-003 and NARR-inclusion. Reader
issues duplicate NARR-inclusion, so the actual correction-admission gate returns
False despite valid native JSON and exact quotes. Raw 13/14 ID agreement is not
semantic/application acceptance. Usage: 111,619 input / 7,571 output; provider time 68.926 s.
No more paid authority from this check. Production/ITS acceptance remains held.
See [results](docs/20261015_climate-source-scope-review-results.md).

### 2026-10-15 source-scope reviewer repair: offline verified

The two review prompts now compare exact population/access and risk/instrument
relationships, credit broad provisions without treating them as narrower proof,
and retain qualified analysis. Explicit matching provisions defeat blanket omission
claims; unseen safeguard content does not mean failed protection. Review versions
are core2.19 and reader1.9. Schemas, correction paths, model settings and budgets
are unchanged. Four synthetic contrast cases reuse the existing offline harness.

171 focused tests and all 1,677 full-suite tests passed (1,274.80s); all 158 checked
source/fixture hashes remained unchanged. Seven other rendered stage prompts are
byte-identical to the preceding commit. Independent review found no blocking issue.
No paid calls, full assessment, deployment or merge. This candidate's model judgment
is unvalidated: the prior 12/14 result applies to older prompts. Production/ITS
acceptance remains held. See [repair](docs/20261015_climate-source-scope-review-repair.md).

### 2026-10-15 reasoning-enabled comparison: improved, still failed

Two authorized isolated reviewer calls are consumed, no retries or full assessment.
Adaptive/high reasoning caught study scope, separate funding envelopes and planned
versus delivered facilities; readiness decisions were correct. Decision agreement
was 12/14 against pre-frozen adjudicated labels. Remaining failures: false rejection
of qualified cancelled-site access analysis and missed exclusion-specific safeguard
overstatement. Both actual schemas, fingerprints and exact quote checks passed;
33 focused tests passed. Usage: 110,643 input / 7,831 output tokens; provider time 56.608 s.
No app settings, deployment or merge changed. Production/ITS acceptance remains
held. No further paid authority from this experiment. See
[results](docs/20261015_climate-reasoning-review-results.md).

### 2026-10-15 explicit-premise paid check: failed

Two newly authorized reviewer calls on candidate8b1039c are consumed; no retries,
correction-generation calls, full assessment or deployment. Both native schemas and
reader quote checks pass, but the model still admits Kasindi study-scope and separate
funding-envelope errors, misses planned-versus-delivered flood-ready status, and
accepts rounding as an inconsistency. The historical REC-003 reject label was too
strict: its explicitly qualified access question is valid analysis. Inclusion needs
a narrow safeguard wording correction; other reader objections overstate precision
issues. Keep frozen expectations and the separate source adjudication visible.
Actual Sonnet5.5 usage:110641 input/2024 output tokens. Production/ITS readiness stays
held; no further paid authority from this check. See [results](docs/20261015_climate-explicit-premise-review-results.md).

### 2026-10-15 explicit premise review and bounded correction

The offline candidate now requires a source-linked premise decision for every core
recommendation and an exact current-text quote for every reader objection. Supported
facts, qualified analysis and proposed actions remain admissible. An unsupported
parent premise cannot pass merely because only its optional draft was flagged.
Precise findings use the existing bounded correction and fresh review; malformed
findings cannot authorize speculative edits. Valid unrelated cores and untouched
reader text are preserved. Reader publication still needs a clean meaning review;
the verified Detailed fallback remains available if it fails.

Core review2.18, reader review1.8 and normalization2.10 record the contract change;
renderer2.19 and maximum call/retry budgets are unchanged. No provider calls or
deployment occurred in this repair. Offline tests establish admission behavior,
not model judgment: fresh semantic acceptance and production/ITS readiness remain
unproven. Stored assessments are not automatically re-reviewed. See
[repair and verification](docs/20261015_climate-explicit-premise-repair-validation.md).

### 2026-10-15 full-context paid reviewer check: failed

Two explicitly approved reviewer-only calls are now used; no retries, full run,
deployment or merge occurred. Candidate 94a0f2c used claude-sonnet-5-5 and recorded
108,819 input / 1,068 output tokens. Both native responses validated, but analytical
acceptance failed: all five core recommendations passed, including known scope
errors REC-001/003/005; all four readiness decisions matched; reader review again
rejected valid coordinated wording and missed the flood-ready status overstatement.
A new inclusion objection is recorded with its source nuance. REC-005's financing
scope error was recognized only on its optional draft, leaving the faulty core
approved. More context alone did not solve admission. No further paid authority
remains from this approval; production/ITS acceptance stays held. See
[full results](docs/20261015_climate-full-context-review-results.md).

### 2026-10-15 full-context offline repair (not production accepted)

The user approved an offline repair following quality13. Cited original source
blocks now accompany facts through generation and reader stages so site/activity
and recipient/funding boundaries remain visible. Corrections use unique anchored
sentence/clause edits, preserving surrounding text and evidence; numeric/date
checks and fresh independent meaning review remain mandatory. Research telemetry
recognizes selections and preserves numeric rejection counts, distinguishing
unknown diagnostics from known zero counts without logging source text.

The full-context replay reconstructs 104 source blocks, 60 facts, five core
recommendations, four flags and five reader records; its recorded outcome correctly
fails seven acceptance checks. It separates reconstructed baseline inputs from the
current candidate reader input and never injects expected labels into model input.
The offline validation record is docs/20261015_climate-full-context-repair-validation.md.
Added source context increases input size (43,322 serialized characters per full
context call on quality13); no new model calls or retries were added. No provider
calls, paid assessments or deployments occurred in this repair. Production/ITS
acceptance remains outstanding; saved failures remain unchanged. Draft PR83 and
its worktree are preserved. Do not treat software tests as semantic certification.

### 2026-10-15 quality13: production acceptance failed

The one newly authorized full paid run is used; all six targeted reviewer calls are
also used. Candidate f463684 passed 1,591 offline tests, exact-commit CodeQL and the
four targeted calibration cases, but quality13 failed source-based acceptance.
Assessment 09c194d6-a4f0-40a7-bc9b-3eccfc952f6a completed HTTP200 at 07:10:45UTC.
Four priorities survived; REC-001 misroutes Kasindi through Haut-Katanga feasibility
studies and REC-005 combines separate Burundi/DRC financing pools. The reviewer
admitted false rounding/status contradictions and again rejected valid qualified
reader wording. One real reader status defect was found; its correction introduced
new numeric tokens and was correctly rejected. Summary 198 words was not the issue.
Research returned zero admitted claims; stale structural telemetry cannot establish
why selections failed. See docs/20261015_climate-quality13-acceptance-diagnosis.md.

Production restored to original main 1168a8f by dep-db87rsm89jmc73ciiij0, live
2026-10-15 07:17:29UTC; branch main, On Commit and HTTP200 build health verified.
Preview 23958ae/auto-deploy off; branch/worktree and draft PR83 retained. Actual
browser/HTML/DOCX artifacts are local and agree, including the review-needed fallback.
No further paid call, main merge, ITS deployment or successful ITS handover is
approved by this failed result. Historical allowance statements below are superseded.
The isolated calibration did not generalize; production readiness is not established.

### 2026-10-15 reviewer calibration complete; full acceptance pending

The latest user authority permits six targeted reviewer-only calls and one further
full paid assessment after repairs. All six targeted calls are now used; the new
full run is not yet used. This supersedes historical exhausted-allowance statements
below. No additional reviewer-only calls are authorized.

The repair separates accepted proposed actions from factual evidence, retains
material siting criteria, checks every core premise against source passages, and
calibrates reader review for faithful weaker paraphrases and conditional inference.
Four final calibration cases passed the configured reviewer with native schemas,
exact targets, appropriate per-object reasons and manual source review. Two negative
cases were purified and repeated within the six-call cap; positive payloads and
runtime prompts were unchanged. See docs/20261015_climate-reviewer-calibration.md.

Frozen verification: 1,591 tests passed in339.79 seconds; all157 checked Python/fixture
source hashes unchanged. Independent acceptance review found no remaining blocker.

Versions: facts2.7, analysis2.11, judgments2.15, recommendations2.16,
conditional-review2.16, drafting1.6, compiler1.7, correction1.4,
reader-review1.6, normalization2.8. Renderer2.19 and all schemas/call budgets
are unchanged. No cached-result re-review is implied. Fresh end-to-end analytical,
browser and export acceptance remains mandatory before a successful ITS handover.
Production remains original main1168a8f/On Commit; preview23958ae/auto-deploy off.

### 2026-10-15 quality12 outcome: rollout held

Final combined offline verification: 1,573 tests passed; 163 source/test hashes unchanged.
See the quality12 diagnosis for live failures, offline changes and remaining limits.

Offline follow-up (not deployed): conditional-review2.15 now receives readiness
flags in its existing call and returns passed_readiness_ids. Only explicit, valid,
uncontested acceptances reach output; no-priority runs withhold unreviewed flags
without another call. Flag disputes cannot remove explicitly accepted core actions.
Correction calls clear the flag list. Original flag wording remains reserved against
minor-point duplication, conservatively preventing rejected claims from resurfacing.
Reader-correction1.3 exposes per-target numeric/date tokens while retaining deterministic
rejection. Normalization2.7; renderer2.19 unchanged. These changes are offline verified
only; relational-scope errors and reviewer false positives still require fresh analytical
acceptance. No further paid call is authorized under the exhausted two-run allowance.

Both authorized paid runs are consumed. Quality12 on 23958ae completed HTTP 200,
retained three priorities and two-country research, but failed analytical/native-reader
acceptance. Summary length was valid at 204 words. One initial meaning review ran;
the correction added a date outside the original record and was rejected before any
fresh review. Source checks found unsupported displaced-trader/site linkage, overstated
missing siting criteria, and unverified integrity flags, alongside reviewer false positives.
See docs/20261015_climate-quality12-acceptance-diagnosis.md. Do not admit saved results,
run another paid assessment/provider review, merge, or deploy to ITS.
Production rollback dep-db80ii8u01pc738ev6tg restored original main1168a8f at
2026-10-14 23:00:04 UTC; On Commit and HTTP200 original-build health verified.
The branch preview remains23958ae with auto-deploy off. No successful ITS Word
handover has been authored. Historical statements below about one remaining run
are superseded. Offline safety improvements do not establish fresh analytical acceptance.

### 2026-10-15 bounded quality11 repair (acceptance pending)

October15 quality11 follow-up: the first of two newly authorized paid trials
completed on paid production but failed analytical acceptance (false same-scope
contradiction, incomplete country research, Summary321/288 words without meaning
review). Production was restored to original main1168a8f, On Commit, healthy.
One paid trial remains. Native reader repair now combines initial meaning issues
with repairable text prechecks in one correction, followed by fresh review; length
patches receive220 total words of application-owned paragraph budgets, while the
admission ceiling remains260. Malformed/block reviews skip correction. Research
retains received proof ahead of snippets and reserves coverage within existing
caps. Fact/review prompts verify comparability and residual-gap premises. Versions:
facts2.6, review2.14, compiler1.6, correction1.2, reader-review1.5, normalization2.6.
Renderer2.19 unchanged. See docs/20261015_climate-quality11-repair-validation.md.
Earlier paid-authority restrictions below are historical. Rollout remains held.


### 2026-10-14 quality10 follow-up: meaning takes priority over modest length

The user authorized further paid acceptance, including a full run if needed, and
clarified that roughly twenty extra words must not be the main acceptance blocker.
Quality10 on 4231ab9 retained five independently accepted priorities but withheld
native prose: Summary 250 words, then 239 after the single correction. Meaning
review was never reached. Complete initial/precheck/patch diagnostics were retained.

Native Summary targets remain 160-230 words, with an admission allowance up to 260.
Legacy Summary retains its 230-word limit. Native meaning review remains mandatory;
unreviewed historical results are never promoted. Compiler1.5/correction1.1/reviewer1.4
explicitly preserve country/component/activity scope, beneficiary-population scope,
and planned versus delivered benefits. Normalization2.5; renderer2.19 unchanged.
No extra correction, retry or provider budget was added. See
docs/20261014_climate-quality10-validation.md. Production/main/ITS remain held
pending fresh analytical acceptance; earlier no-paid statements below are historical.

### 2026-10-14 approved native reader contract repair (rollout held)

Quality9 consumed the single follow-on paid allowance. It retained four independently
accepted actions and five Summary gaps, but native prose was withheld before meaning
review: the returned Summary had 274 words and the old capitalization heuristic
rejected Protections. The original precheck/reader response was overwritten during
whole-reader correction, preventing an exact diagnosis of its scope failure.

Compiler 1.4/correction 1.0/reviewer 1.3 and normalization 2.4 replace whole-reader copying
with exact-ID text patches. The application preserves all evidence, themes and
untargeted records. Native mechanical checks retain reference, number/date, format
and length boundaries; independent meaning review owns actors, actions, units,
negation, source scope and planned/completed status. Normal FCV Summary stays strict.
Corrections receive original claim scope and restricted cited support, followed by
complete revalidation and fresh review. Missing/malformed/non-clean review fails
closed. Initial response, prechecks, returned patch and review outcomes remain bounded
private diagnostics, excluded from display, grounding and exports. One correction
uses the existing deadline/shared 9,000-token allowance with zero repair retries.
Reader 2.19 and legacy contracts are unchanged. No further paid call is authorized;
offline archive replay supplies no retrospective semantic pass. Production/main/ITS
remain held. See docs/20261014_climate-reader-contract-validation.md.

CodeQL follow-up: research source classification now uses exact World Bank/IPCC
domains or their dot-delimited subdomains, matching the existing trusted HTTPS
admission rule. Lookalike hosts cannot receive official-source labels even before
normalization rejects them. No source entitlement or schema change.

### 2026-10-14 richer benefits prose preflight (rollout held)

The user requested richer dividends/fair-benefit findings and authorized one new
quality8 paid run after offline fixes. Analysis 2.10 records conditional benefit
mechanisms and enabling conditions in existing responses/pathways, including who
could benefit or bear costs. Final reader/reviewer 1.2 use project-feature-led,
connected prose, distinguish missing instrument visibility from failed protection,
and never treat absent dividend language or an explicit mechanism as a defect.
Dividends/inclusion target 150-180 words in two paragraphs when supported; native
admission now allows 70-180 words, matching the existing theme renderer and keeping
short saved outputs readable. Reader version 2.18. An exact sentence-initial Clear access arrangements
exception retains one-word actor, multiword-name and acronym guards. No extra calls or budget changes.
Focused177passed; full1510passed/one obsolete wording assertion; aligned client
module18passed. Runtime unchanged after full suite. Fresh quality8 acceptance
remains outstanding.
See docs/superpowers/plans/2026-10-14-climate-benefits-prose.md.

### 2026-10-14 quality7 reader-boundary follow-up (rollout held)

The one paid quality7 run passed research (2 sources/4 passages) but failed at the
runtime reader gate CURRENT_DRAFTING_INCOMPLETE. Its completed assessment was not
returned or cached, so accepted priority count and native prose are unobservable.
No paid retry; allowance consumed. See docs/20261014_climate-quality7-validation.md.
Reader 2.17 explicitly carries final-reader-v1 so missing optional wording passes,
while supplied malformed wording and legacy readers retain their checks. Native
prose requires all three theme answers. Typed reader failures return a separate
caller-only diagnostic event, manually saved/loaded as climateVerifiedFailure,
never used for display, exports, follow-on inputs or automatic storage. Reset/new
run clears it and stale session labels. Context evidence retains source metadata,
dates, limitations and relevance horizons; unknown dates leave current status
unverified. All prompts include that temporal calibration; no extra calls added.

### 2026-10-14 Climate backend candidate (rollout held)

Approved redesign implements separate operational-decision and optional-drafting
validation. Native reviewers explicitly list passed_core_ids; missing/unresolved
acceptance fails closed. Draft artifacts have separate IDs. Decision corrections
use recommendation_compiler, wording corrections use drafting_compiler, with one
independent re-review and a shared9,000-output-token allowance (no repair retries).
Optional drafting reserves core review time. Cancellation propagates; optional
provider/editorial failures retain previously accepted decisions.

Research classification selects received citation passage IDs and source-owned
project labels; the application owns quotes, URLs and metadata. Search continuation
keeps encrypted blocks; the pure classification call sends only the bounded packet.
Incomplete exact proof is retained for inspection but excluded from admitted prompt
grounding. Beneficiary coverage, whole source-label spans and bank unavailable
reasons remain explicit. Country evidence never establishes a project/site fact.

The native judgment stage defers prose with final-reader-v1. reader_compiler runs
after final action review; reader_review checks supported meaning, status and scope.
Summary and three findings cite admitted evidence/action IDs. Reader2.16 exports
reviewed narratives, ignores separate unreviewed top-level prose, rechecks support
and uses a clear limited fallback. Legacy saved assessments remain unchanged.
All priorities remain open; their details and04-06 disclosures remain closed.
Per-attempt metrics record configured/resolved model, usage, scope and failures.
See docs/20261014_climate-decision-acceptance-benchmark.md. Full offline verification
and branch-test checks are recorded in the matching backend-validation handover.
No additional paid generation; fresh live quality acceptance remains outstanding.

### 2026-10-13 pipeline reassessment and priority visibility

Reader2.15 opens every ranked Climate operational priority initially in browser
Detailed and standalone HTML. Recommendation details and sections04–06 remain
closed; user toggling and print restoration are retained. Generation is unchanged.
The six-run/backend assessment identifies a native correction schema defect:
compiler corrections cannot contain drafting, but confirmed-route validation
requires it. Existing passing fixtures supplied legacy fields forbidden live.
The Summary lexical gate also rejects ordinary prose and can accept inverted
meaning. These are diagnosed/proposed backend changes, not implemented repairs.
See `docs/20261013_climate-pipeline-readiness-assessment.md` for evidence, options,
cost/coverage limits and the recommended redesign checkpoints. Rollout remains held.

### 2026-10-13 quality6 follow-up (rollout held)

The new paid quality assessment generated four candidates and retained two after
independent review; correction recovered none. Research provenance failed and
native Summary fell back. This is a failed quality gate; PR83 remains draft.
Reader2.14 repairs rejection of the full DRC country name against an admitted DRC
fact and ordinary sentence-initial Today in analytical prose. Summary no longer
requires four literal dimension labels; its other grounding checks remain strict.
Correction trace retains bounded response and pre-review rejection reasons.
No new model calls, recommendation restoration or generation-prompt changes.
The Word route also calls the existing provenance helper after canonical reader
validation, restoring matched guidance and method/source notes from the assessment
and curated references. It never copies provenance from the incoming saved reader.
See `docs/20261013_climate-quality6-validation.md` for evidence and remaining blockers.

### 2026-10-12 candidate: shared rating sidebar

Normal FCV and verified Climate now keep the rating sidebar in Summary and Detailed;
mobile uses the existing collapsed disclosure. Climate shows separate sensitivity
and responsiveness cards with short glosses and collapsed rationale. Responsiveness
uses five contribution levels (very_limited through very_strong), with not_expected
and unclear unscored. The judgment prompt is climate-judgments-v2.8; saved
Emerging results remain visibly legacy and unscored. The approved scope message is:
"Contributing to responsiveness is often a sign of going above and beyond. The
expected contribution depends on the project's scope." Normal FCV's existing
rating scale is unchanged. This candidate has not been merged to production.

Production-readiness follow-up: explicit PID beneficiary-country fields are read
before source normalization, including bounded handling of concatenated geography
columns. Verified Climate uses that metadata for regional scope. Metadata model
helpers disable adaptive thinking and collect text blocks safely. E&S markers are
checked across retained primary evidence, not only the opening 8,000 characters.
Missing OIS/processing evidence is now explicit in Summary, Detailed and exports.
HTML/Word exports include the contribution interpretation; saved Emerging readers
remain valid while new generation rejects that legacy value. Mobile utility CSS
now follows the desktop rule so wrapped controls retain their background/height.

This is a **World Bank FCV (Fragility, Conflict, and Violence) Project Screener** — a Flask-based web app that guides Task Team Leaders (TTLs) through a **3-stage workflow** to assess how well a World Bank project integrates FCV considerations and generate targeted, actionable recommendations.

The tool explicitly distinguishes two concepts:
- **FCV Sensitivity [S]** — Is the project *aware of and designed for* the FCV context? Contextual awareness, conflict-informed design, Do No Harm, FCV-adapted operations.
- **FCV Responsiveness [R]** — Does the project *actively work to change* the FCV situation? Root-cause engagement, resilience building, transformative use of FCV tools, peace & stability dividends.

The 4 FCV Strategy Shifts (Anticipate / Differentiate / Jobs & Private Sector / Enhanced Toolkit) are **cross-cutting** — they apply to both S and R findings and are tagged inline.

Every prompt output tags findings as [S], [R], or [S+R], assigned dynamically per-finding. [S+R] strictly only for: (1) inclusion/targeting of conflict-affected populations; (2) FCV logic in ToC/PDO; (3) adaptive M&E for harm + resilience; (4) GRM for state-citizen accountability. If in doubt → [S] or [R].

**Key goal:** Move from broad, vague recommendations to specific, location-aware, operationally grounded, stage-aware suggestions (e.g., "historically, Nzerekore, Kindia, and Kankan have been excluded from service delivery — focus on these regions before PAD appraisal").

**Analytical backbone:** WBG FCV Strategy 2026-2030, FCV Operational Manual (OST, enriched with Peace & Inclusion Lens dimensions and Strategic DRR Framing from Good Practice Notes), FCV Operational Playbook, and Good Practice Notes on Peace & Inclusion Lenses and FCV-Sensitive Programming. When a Country Partnership Framework (CPF) is uploaded as a contextual document, Stage 3 recommendations include a `cpf_alignment` field linking priorities to CPF outcomes. When an RRA or equivalent conflict analysis is uploaded, Stage 3 also includes `rra_driver_alignment` linking priorities to identified conflict drivers where relevant.

## OPCS Source Policy Documents (local reference corpus - NOT in this repo)

The authoritative OPCS policies, directives, and guidance notes this app's prompts and knowledge base (`background_docs.py`) are meant to stay consistent with are **not stored in this repository**. They live locally on the maintainer's machine, outside any git-tracked folder:

- **Full OPCS Policy and Procedure Framework (PPF) document corpus:** `C:\Users\wb559324\WBG\Policy and Procedure Framework - PPFDocuments` - 178 PDF policy/directive files as of 2026-07, including the IDA FCV Envelope policy and directive, the Program-for-Results policy/directive, the DPF policy/directive, and the MPA policy/directive referenced throughout `background_docs.py`.
- **Document name index:** `C:\Users\wb559324\Downloads\OPCS docs.xlsx` - a spreadsheet listing every file name in the PPF corpus above, for quick lookup without opening each PDF.
- **Relevance triage:** `C:\Users\wb559324\Downloads\LLM input on relevant project docs.docx` - an internal WBG LLM's assessment of which documents in the PPF corpus are most relevant to this app's FCV screening use case, used to prioritise which policies to actually read in depth rather than working through all 178 files.
- **ESF Manual:** The full World Bank Environmental and Social Framework manual PDF, uploaded directly as session context when doing OPCS-consistency work (not saved to a fixed path - treat it as a session attachment each time it is needed).
- **Test cases:** `C:\Users\wb559324\OneDrive - WBG\FCV_Screener_test_cases` - sample project documents used to QA-test the app's outputs against these policies.

**Cross-reference these three sources together** (PPF folder + `OPCS docs.xlsx` + `LLM input on relevant project docs.docx`) when doing any OPCS-policy-consistency work - the spreadsheet and LLM-relevance docx let you avoid reading all 178 PPF files, by narrowing to the ones flagged as relevant to a given FCV instrument or topic before opening the actual PDFs.

**ACCESS RESTRICTION - read this before opening any of the above:**
**Only GitHub Copilot (this CLI / Copilot Chat / Copilot coding agent) is permitted to read the source files in the PPF folder, the `OPCS docs.xlsx` index, the `LLM input on relevant project docs.docx` triage doc, and the ESF Manual PDF.** Claude Code, OpenAI Codex, or any other coding agent working in this repository **must not** open, read, or ingest these source documents directly - even if asked to do OPCS-policy-consistency work. Other agents should work from **already-written, GitHub-Copilot-authored summaries** (e.g. design specs and plans under `docs/superpowers/`, or corrections already landed in `background_docs.py`/`app.py`) rather than the raw policy corpus itself. If a non-Copilot agent's task appears to require reading these source files directly, it should stop and ask the maintainer rather than accessing the folder.

**Version history:**
- **v9.42** — FY26 OPCS routing refresh + advisory caveat + reinstated S/R hovers (branch `fix/opcs-fy26-policy-refresh` + caveat/hover/dedupe commits, integrated via `release/fy26-app-updates`, merged to `main` in **PR #80** `a6958ea`, **deployed to production 2026-10-12**; live-smoked on `fcv-agent-1` with the DRC-Angola Great Lakes PID P174814). Routing verified against the local OPCS PPF folder + an internal policy review (mAI), which **reversed two earlier reviewer claims**: DPF `OPS5.02-POL.120` (eff 1 Feb 2024) is correct, and PforR already cites the OPS5.04 series — the asserted "14 Jul 2026" policy reissue is **not** in the current OPCS index (a snapshot-lag; the index's own "Update assessment" sheet says to judge currency by Published status + effective date, not filename — so the app cites by **stable document title**, not churny OPS numbers). Fixes: (a) `classify_processing_model` gates the urgent-need / small-TF one-step triggers to the IPF family (PforR one-step = risk rule + AF only); (b) `appraisal_document_label` renders a legacy **DPF** as a *Program Document*, not a PAD; (c) `MPA_MODULE_GUIDE` drops the non-existent `OPS5.01-POL/DIR` (MPA sits in the Multiphase Programmatic Approach Guidance + the IPF/PforR Policies); (d) Rapid Response re-cited to the *Rapid Response to Crises and Emergencies* Policy + the RRO Procedure (not `OPS5.04-POL.125 ¶12`); (e) **new-model E&S** — `classify_es_regime` gains `preparation_regime` + `ois_creation_date`, so a new-model IPF-family op (no Concept Review; OIS well after 1 Oct 2018) resolves to **ESF** via the OIS decision instead of `UNRESOLVED`; legacy/unresolved unchanged; (f) ESS reference-set gate widened from exact `ipf` to `{ipf, ipf-ddo}` (TA still excluded pending Help Desk); (g) `RESTRUCTURING_GUIDE` — add the safeguard-category-to-Category-A Level 1 (Board) case; PDO change = Level 2 / **RVP** (dropped "CD-DD"); significant PDO change = management Board referral. **UX:** a blunt advisory **caveat banner** (`screenerCaveatHtml`) now sits above the Summary *and* Detailed readouts (advisory-only; verify policy refs with OPCS; ideal-project framing / "2 of 5 is a win"); the **FCV sensitivity/responsiveness hover definitions** are reinstated on the rating gauges (`.stage3-rating-dimension.sr-term`) with `wrapSRTerms` now case-insensitive; the legacy in-body `DO_NO_HARM_HEADER` is **stripped from the on-screen display only** (downloads/exports untouched) so the banner is the single on-screen disclaimer. Tests across `test_regime_router`, `test_regime_terminology`, knowledge-base, and frontend suites; full suite green. ITS handover: `20261012_ITS_handover_fy26_app_updates.docx`; open items: `docs/20261012_opcs-open-issues-log.md` (local). **ITS/FastAPI parity:** mirror fixes (a)(b)(e)(f)(g) + citation corrections (c)(d); see `FCV_BUILD_PARITY.md`.
- **v9.41** — Configurable upload cap + wired-in pre-submit size warning (branch `feat/configurable-upload-limit`, 2026-10-12; **merged to `main` via PR #80 and deployed to production 2026-10-12**). The public Render service is now on a **paid** tier, so the former hard 50 MB `MAX_CONTENT_LENGTH` (sized for the free tier's RAM) was the main user-facing wall left after the 5.5 / 1M-context / 300k-primary updates — a full project package (primary PAD + up to 10 package + 3 context PDFs) easily exceeds 50 MB after browser base64. Fix: new env-configurable `MAX_UPLOAD_MB` (default raised 50→**100**; IT tunes to the instance) drives `MAX_CONTENT_LENGTH`; the effective value is published on `/api/sector-lenses` as `max_upload_mb` and read by the frontend so the pre-submit size warning cannot drift from the backend cap. Also **wired `uploadPayloadLimitMessage()` into `begin()`** — it was defined and unit-tested but never called, so users previously only hit a post-upload 413; they now get a friendly warning (at ~90% of the cap) before a doomed upload. Deliberately **no change** to document counts (1/10/3), distillation budget (32k), or websearch (`max_uses`/150s) — those are gated by latency / Stage 3 payload / focus, not by context or tier, and the recent updates don't relax them. Tests: `test_upload_payload_limits.py` (+2: env-configurable cap, endpoint publishes cap), `test_frontend_timeout_handling.py` (+1: preflight tracks published cap). Affected suites green (10 + 87 passed). Shipped to production in the v9.42 PR #80 batch.
- **v9.40** — Claude 5.5 climate-pipeline compatibility fixes + live verification (2026-10-10). Four live screenings on production surfaced issues the unit tests could not. **Standard FCV path live-verified end-to-end** on 5.5 (Stage 1 Sonnet 5.5, Stage 2/3 Opus 5.5; 0 errors; delimiters intact) — production-ready. The climate verified pipeline (tuned to the 4.6 models) needed four 5.5-compat fixes: (1) removed deprecated `temperature=0` from `climate_verified_client` (PR #75 — 5.5 rejects `temperature`/`top_p`/`top_k`); (2) disabled adaptive thinking on the Haiku research-structuring call (PR #76 — thinking consumed the output budget and truncated the research JSON; also bumped that cap 2500→4000); (3) made the verified client's thinking-off param **model-aware** `_thinking_off()` (PR #77 — Sonnet 5.5 rejects `{"type":"disabled"}` and requires `{"type":"between_tools"}`; Haiku uses `disabled`); (4) `build_reader_model` now **renumbers priority ranks** to a clean `1..N` sequence in sorted order (PR #78 — Sonnet 5.5 emits non-sequential ranks that tripped the `PRIORITY_RANK_ORDER_INVALID` reader-integrity check). The climate verified pipeline has ~a dozen strict `READER_INTEGRITY` validators calibrated to the old model; a different document could trip another — normalize format-level invariants in `build_reader_model`, treat quality checks (placeholders/truncation) as real failures. Full handover: `docs/20261010_claude-5-5-upgrade-handover.md`. Live verification uses a direct `/api/run-express` POST replication (the Claude-in-Chrome upload tool rejects host paths) — see the handover.
- **v9.39** — Claude 5.5 model upgrade (branch `feat/model-5-5-upgrade`, 2026-10-09): Moved the whole app off the previous-generation 4.x models onto the Claude 5.5 family. Three tier constants in `app.py`: `MODEL_REASONING = "claude-opus-5-5"` (core Stage 2 FCV assessment + Stage 3 recommendations — the reasoning-heavy stages, selected via `_stage_model(stage_num)` inside the shared `_stream_stage()`), `MODEL_STANDARD = "claude-sonnet-5-5"` (Stage 1 extraction, lens recovery, web research, Go Deeper, follow-on, priority points), `MODEL_LIGHT = "claude-haiku-5-5"` (country/sector extraction, condensation, distillation). The climate/sector-lens module bumps its own `sector_lenses/climate_runtime_config.py` constants to the same generation (`QUALITY_MODEL = claude-sonnet-5-5`, `SMOKE_MODEL = claude-haiku-5-5`) and `fcv_distillation.HAIKU_MODEL = claude-haiku-5-5`. **Opus 5.5 has always-on adaptive thinking** that consumes the response budget, so Stage 2/3 output caps were raised to prevent truncation of the trailing `%%%`/JSON blocks: `STAGE_MAX_TOKENS` = {1: 8000, 2: 32000, 3: 32000} via `_stage_output_budget()`, and native-climate Stage 3 `NATIVE_CLIMATE_STAGE3_MAX_TOKENS = 20000` (was 9000). Doc-input limits are unchanged — the core route's 300k primary budget (`STANDARD_FCV_PRIMARY_DOC_CHARS`) already landed in the Nairobi update. The climate pipeline keeps a like-for-like Sonnet bump (not Opus) on its own module calls to avoid destabilising it, but the shared core Stage 2/3 stream it uses now runs on Opus 5.5 — **so a dedicated live climate run is required in verification** (always-on thinking can change the diagnostic-omission / Haiku-recovery behaviour; easy revert is pinning `_stage_model` Stage 2/3 back to Sonnet). Tests: climate-workflow budget assertions updated (16k→32k, 9k→20k) and model-ID assertions bumped to 5.5; full suite 1324 passed (the 7 remaining failures are pre-existing on `main`, unrelated to this change). Live-verify on Render: Opus 5.5 end-to-end timing on the largest PforR PAD against the wall-clock caps (S1 8m / S2 9m / S3 9m) and that the delimiter blocks still parse.
- **Nairobi standard-FCV update (2026-09-20)** - Live PAD testing exposed a pre-existing 60,000-character primary-input cutoff; standard FCV now reads up to 300,000 primary characters with a visible warning for remaining truncation, while specialist limits remain unchanged. Evidence instructions preserve conditional scope and planned-versus-completed measures.  Standard-route generation targets an 80-110-word management overview, zero to three evidenced strengths and one to five material priorities. Summary presents every leading action and links to canonical Detailed priorities; formal ratings stay in Detailed. A separate HTML/Word management-brief download revalidates the concise bundle without a model call. Watch prose retains safe Markdown structure; routing disclosures are removed from both views while relevant warnings remain. Existing detailed exports, enums and Climate analytical contracts are preserved. See `20260920_ITS_handover_standard_fcv.md` for the baseline, porting contract and validation status.
- **v9.38** - Production Climate Summary and DOCX metadata extraction: one shared recursive OOXML walker (`docx_structure.py`) now preserves visible paragraph/table/SDT order, nested tables, checked controls, and structured header/value fields while `extract_docx_text()` retains its public two-value API and internal routes carry a separate structured-field sidecar. Climate-only verified runs use source manifest `source-blocks-v3`, structured financing metadata takes precedence over prose with typed conflict/unresolved warnings, and the judgment call emits the validated `summary_overview.paragraphs` contract (`climate-judgments-v2.4`) without another model call. Climate Summary renders that overview, closed watch/guidance disclosures, and the same gated drafting content as Detailed; normal FCV keeps its established narrative/schema/prompt contract and adds only an applicable closed watch-items disclosure.
- **v7.0** — Redesigned from 4 stages to 3; full 12 OST recs + 25 key questions; FCV Playbook integration; Under the Hood panels; refresh_shift field
- **v7.2** — Stage 2 dynamic thematic narrative; actions[] array replaces recommendation string; Go Deeper 2-tab panel; Stage 3 clean memo (no inline citations)
- **v7.4** — Express Analysis mode (single SSE endpoint for all 3 stages)
- **v7.5** — UX polish: styled uploads, smart timer, condensed output, refined landing page; S/R definition box removed from Stage 3; rating rubric with reasoning block
- **v7.6** — Document format fixes: DOCX properly parsed via python-docx (base64, reading-order-aware, merged-cell dedup); PPTX support added via python-pptx; silent extraction failures surfaced as chip warnings and SSE banners
- **v7.7** — Concurrency hardening: per-tab assessment IDs in the frontend, assessment-aware request payloads, express workflow execution moved onto the background assessment executor, and multi-worker gunicorn defaults for better parallel use
- **v8.0** — Major knowledge base and prompt quality overhaul (branch `feat/v8-knowledge-base`, merged 2026-04):
  - **Knowledge base:** 6 instrument entries (IPF/PforR/DPO/TA/MPA/IPF-DDO) + 5 process guides (MTR/ISR/AF/Restructuring/ICR) + 29 glossary terms + FCS country list (2015–present)
  - **Prompt quality:** WB LLM quality review integrated — SEA/SH as 9th DNH principle, gender-FCV trigger block (7 conditions), lifecycle guardrails (SORT/ESF/SEP/ESCP minimum set for PAD), instrument routing guardrail per doc type, mandatory priority cards for gender and SEA/SH flags
  - **Temporal anchoring fix:** `_build_temporal_guardrail(temporal_ctx, doc_type)` now takes `doc_type`; PAD/PCN/PID/AF/Restructuring documents always receive preparation-phase framing regardless of whether approval date is in the past — prevents implementation-review hallucination cascade in Stages 2–3
  - **Stage 1 UX:** Prompt now requires 2–3 sentence narrative lead paragraph at top of each Part. Frontend `renderStage1()` parses Part A/B split and renders with styled section badges ("From your document only" / "Wider context & research"); narrative lead paragraph visually distinguished
  - **Finalized PAD notice:** `isFinalizedPAD()` detects uploaded PADs with past approval dates; amber retrospective notice injected in Stage 3 output and downloaded report
  - **FCS cross-checking:** `FCS_LIST` and FY26 category constants added to `background_docs.py` (35 FY26 FCS economies, with Conflict and Fragility metadata); injected into Stage 1 and Stage 2 prompts so LLM verifies classification against authoritative list
  - **Implementation review locked off:** `fcv_review_mode` localStorage restore IIFE removed; app always defaults to design review mode on load; implementation review preserved in backend for future activation
  - **Rating recalibration:** Percentage-based thresholds, partial credit for Weakly addressed, softened responsiveness cap
  - **Optional context box:** User can supply framing before analysis (peer review notes, changed conflict conditions)
  - **Step-by-step:** Load-first mode (full output on completion, not progressive streaming)
- **v8.1** — WBG LLM review batch + web research fix (branch `fix/wbllm-review-batch`, merged 2026-04-13):
  - **Instrument calibration:** New `FCV_INSTRUMENT_CALIBRATION` constant in `background_docs.py` — DPF failure modes (policy reversal, adjustment sequencing, programmatic series risk, Cat DDO scrutiny), FCV Envelope nuances (EDP, annual review requirement, eligibility logic), RRA as consultative process, trust funds and ASA as alternatives
  - **DPF guardrail (Stage 3):** ESCP, ESF standards, SORT-as-monitoring, and DLIs are now explicitly excluded for DPF/DPO instruments; recommendations framed around prior action conflict-sensitivity and reform sequencing instead
  - **Adjustment sequencing DNH (Stage 2):** New budget-support-specific DNH check on reform cost/safety net sequencing gap — flagged as the primary DNH pathway for DPF operations in FCV settings
  - **Citation discipline (Stage 1):** Part B now required to label training knowledge as `[From: general knowledge — ...]` not `[From: training knowledge - ...]`
  - **FCV Envelope eligibility guardrail:** Stage 1 prompt and `FCS_LIST` constant updated to prohibit explicit eligibility determinations for IDA FCV Envelope windows (PRA/RECA/TAA) — eligibility is multi-criteria and determinations risk being incorrect
  - **Web research timeout:** Research client timeout increased 45s → 120s; error now logged as `[WebResearch ERROR]` in Render logs
  - **Upload UI:** Project and contextual zone copy refreshed with PPSD/technical studies examples; "implementation coming soon" notice upgraded to amber banner
  - **Download:** Reports default to `.docx`
- **v8.2** — GPN integration + CPF upload support (branch `feat/v8.2-gpn-cpf-integration`, merged 2026-04-14):
  - **GPN enrichment:** `FCV_OPERATIONAL_MANUAL` enriched with two Good Practice Note subsections — "Peace & Inclusion Lens Dimensions" (5 dimensions: geographic targeting against RRA divides, social cohesion/reconciliation, project-cycle-specific application, conflict actor engagement, unintended consequences screening) and "Strategic DRR Framing" (DRR mapping, 4 P's framework, strategic vs operational distinction)
  - **CPF upload:** Country Partnership Framework accepted as named contextual upload; Stage 1 extracts automatically; Stage 3 adds `cpf_alignment` field (null if no CPF; string linking to CPF outcome if present)
  - **CPF_INTEGRATION_GUIDE:** New constant in `background_docs.py` injected into Stage 3 prompt (both step-by-step and express paths)
  - **Source attribution:** Good Practice Notes listed alongside OST Manual, Playbook, and Strategy in all 4 UI locations (onboarding modal, limitations note, pre-loaded sources banner, express progress screen)
  - **Architecture map:** `docs/fcv-agent-knowledge-architecture.html` — shareable HTML showing knowledge sources → pipeline stages → outputs
  - **Stage 3 timeout fix (2026-04-15):** Three-part fix for "BodyStreamBuffer was aborted" on Stage 3 in Express mode — (1) Express frontend now resets the abort timer to a fresh 8-minute budget when `stage_start:3` fires, rather than using whatever remains of the global 10-minute budget; (2) both Express and Step-by-Step backends now store a compact label for each stage's user prompt in `conversation_history` instead of the full 80k-char prompt, halving the Stage 3 API input size; (3) model updated from deprecated `claude-sonnet-4-20250514` to `claude-sonnet-4-6` across all call sites. Step-by-step Stage 3 timeout also raised from 6 → 8 minutes to match Express.
- **v9.0** — Differentiated knowledge architecture (branch `feat/v9-differentiated-approaches`, 2026-04-17):
  - **Country classification:** Stage 1 prompt outputs `%%%COUNTRY_CLASSIFICATION_START/END%%%` block (category, confidence, reasoning); `extract_country_classification()` parses it; `classify_country()` cross-references FCS list with bidirectional name matching
  - **Classification widget:** Rendered at top of Stage 1 output using `researchCountry` and classification reasoning; narrative format ("This analysis places [country] within the [category] category…"); always ends with caveat: "This is a subjective judgement on the part of this AI tool and does not constitute an official WBG classification."; dropdown override auto-saves on change; no confirmation step required
  - **Secondary knowledge snippets:** `select_secondary_knowledge()` picks category-specific knowledge snippets from `background_docs.py`; injected into Stages 2 and 3 prompts for differentiated framing
  - **`country_category_relevance` field:** Added to Stage 3 priority JSON — explains why each priority is particularly relevant for this country's specific FCV category
  - **DIFFERENTIATED_APPROACHES constant:** New knowledge constant in `background_docs.py` injected into Stages 2 and 3
- **v9.3** — MAI feedback improvements: knowledge base calibration, prompt quality, action_timing expansion (branch `feat/v9.3-mai-feedback-improvements`, 2026-04-21):
  - **Knowledge base — CERC calibration:** `FCV_INSTRUMENT_CALIBRATION` extended with CERC FCV notes: frame as "worth actively exploring" not required; emergency-to-emergency redirect risk; slow activation in FCV (practitioner experience, not formally evaluated); OP 7.30 trigger unavailability and OPCS clearance requirement
  - **Knowledge base — PforR calibration:** IVA access breakdown risk; DLI misalignment in low-governance; disbursement cliff (no CERC equivalent); ESSA limitations; OP 7.30 incompatibility ("effectively unusable"); phase transition risk in MPAs
  - **Knowledge base — MPA calibration:** Phase financing NOT guaranteed; electoral cycle exposure; institutional continuity assumption; OP 7.30 phase governance; combined MPA+PforR failure modes
  - **`action_timing` enum expanded to 5 values:** `flag-for-preparation` | `required-before-appraisal` | `required-before-board` | `next-series` | `supervision`; backward-compat remap: `pre-appraisal` → `required-before-appraisal`; UI pills and DOCX timing_map updated to match
  - **Stage 1 prompt — RRA cross-reference:** 3-case RRA fallback instruction before IDA FCV Envelope advisory: Case 1 (RRA uploaded — scenario cross-check with sub-items a/b/c), Case 2 (RRA known but not uploaded — invite upload), Case 3 (no RRA — note absence, summarise risk drivers)
  - **Stage 2 prompt — new supplementary dimensions:** SORT Adequacy Check (conditional on SORT table; reference ranges for 3 FCV categories; inherent vs residual E&S check); Forced Displacement (conditional on material displacement in doc); DNH: Economic Inclusion and Private Sector Harm Risk (conditional on private sector/skills + suppression context)
  - **Stage 2 prompt — enhanced dimensions:** Climate-FCV Nexus: stricter 3-condition trigger requiring documented country-specific climate-fragility pathway; HDP Nexus Coordination: narrowed to geographic+sectoral overlap, not country-level co-presence; added WBG comparative advantage framing
  - **Stage 3 prompt — PCN/PID calibration:** Stage Awareness expanded with differentiated rules (PCN = strategic risks only; PID = strategic + design/M&E; no PPSD/ESCP/SEA-SH AP requirements at PID); front-loaded work rule; action_timing guidance for PCN/PID stages
  - **Stage 3 prompt — CERC framing rule:** Inserted after instrument feasibility guardrail; frames CERC as "explore with OPCS focal points"; names redirect risk; explicit OP 7.30 trigger caveat
  - **Stage 3 prompt — Conditionality leverage guardrail:** ECA-type access mechanisms and reform DLIs with weak political economy compliance; theory-of-leverage framing; carve-out for routine fiduciary prior actions
  - **Stage 3 prompt — terminology rule:** 4 required replacements for non-WBG due diligence terminology (IDD, IDD protocol, private sector screening, implementing partner vetting)
  - **Stage 3 prompt — paired risk + systemic risk framing:** Strengths section requires embedded risk/limiting factor for top 3-4 strengths; systemic risk rule distinguishes externally-driven risks (monitoring) from design-addressable risks (recommendations)
- **v9.4** - Stream timeout hardening (branch `fix/stage3-stream-timeout`, 2026-05-06):
  - **Backend stream timeout:** `_stream_stage()` now enforces server-side stage wall-clock limits (Stage 1: 8 min, Stage 2: 6 min, Stage 3: 8 min) in addition to frontend abort timers. This prevents Stage 3 provider stalls from sending keepalives indefinitely and leaving Express or Step-by-Step runs stuck on the loading screen.
  - **Shared stream helper:** Step-by-Step now uses the same queue-based `_stream_stage()` helper as Express, so keepalive and timeout behavior is consistent across both modes.
- **v9.5** - Storage quota resilience and document-scope copy (branch `fix/stage2-storage-quota`, 2026-06-18):
  - **Stage 2 storage quota hardening:** Stage 2 Under the Hood persistence is best-effort via `static/fcv_storage.js`; quota failures no longer fail Stage 2 or block Stage 3.
  - **Document scope UX:** Landing/upload copy now frames supported inputs as WBG appraisal/design-stage documents across PCN/PID/PAD/AF/Restructuring plus DPF/DPO, PforR, MPA, and regional operations. MTR/ISR remains marked as implementation review coming soon.
- **v9.6** - Phase 1 mid-cycle overlay: Additional Financing & Restructuring (branch `feat/phase1-mid-cycle`, base Phase 0 `8389f39` / PR #24, 2026-06-17):
  - **Change-type block:** Stage 1 emits `%%%CHANGE_TYPE_START%%%...%%%CHANGE_TYPE_END%%%` (change_types; restructuring_level; rationale) for AF/Restructuring; stripped from display by `clean_stage1_output()`. Parsed by `extract_change_types()`; level derived by `derive_restructuring_level()`
  - **Audit-resolved restructuring level:** PDO change = Level 2 / RVP or CD-DD advisory signal (NOT Level 1). Level 1 is narrow: Alternative Procurement Arrangements and Bank Guarantee expiration-date extension only. Routing is advisory - verify with OPCS, no determinations. `RESTRUCTURING_GUIDE` + `AF_GUIDE` constants added; stale `WB_PROCESS_GUIDE[Restructuring]` Level-1 text corrected
  - **Mid-cycle temporal guardrail:** `_build_temporal_guardrail(temporal_ctx, doc_type)` returns MID-CYCLE LIVE-PROJECT FRAMING (Tier-1 anchored) for AF/Restructuring vs preparation framing for PCN/PID/PAD
  - **Registry/state:** `MODULE_REGISTRY` specialization for AF/Restructuring IPF single with `mid_cycle_overlay` guardrail + change_type output; `AnalysisState` carries change_types/restructuring_level
  - **Stage 2 overlay:** two linked checks per change - context-change since approval + conflict-sensitivity; AF waiver advisory; PDO ToC reassessment; reappraisal-trigger advisory
  - **Stage 3 priorities:** new change_type, restructuring_level, priority_scope fields + top-level mid_cycle_watch; Board-memo vs team-advisory register (7 top-level / 19 per-priority JSON fields)
  - **Export parity:** `/api/download-report` (DOCX) and `downloadHTML()` both render change/level/scope chips and a Mid-Cycle FCV Watch section
  - **Tests:** `tests/test_mid_cycle_phase1.py` (7 tests); full suite 87 passed; no IPF single-country regression
- **v9.7** - Phase 2 DPF/DPO instrument module (branch `feat/phase2-dpf`, base Phase 1 `feat/phase1-mid-cycle` / PR #25, 2026-06-17):
  - **Prior-action spine:** Stage 1 emits `%%%PRIOR_ACTIONS_START%%%...%%%PRIOR_ACTIONS_END%%%` (financing_source IBRD/IDA; series_position; cat_ddo; prior_actions; indicative_triggers) when INSTRUMENT_TYPE is DPO; parsed by `extract_prior_actions()`; stripped from display by `clean_stage1_output()`
  - **DPF rubric:** `DPF_RUBRIC` (prior-action conflict-sensitivity / reform-sequencing / PSIA / conflict-exception / macro-fiscal / political-economy) via the Phase 0 `score_sr()` interface - replaces the 12-OST '% addressed' rubric for DPF
  - **Registry/state:** `MODULE_REGISTRY` entries for `(PCN|PID|PAD|Unknown, DPO, single)` with `dpf_prior_action_spine` / `dpf_no_esf_escp_dli` / `dpf_macro_imf_headline` guardrails; `AnalysisState` carries financing_source / series_position / cat_ddo / prior_actions and auto-adds `dpf_module`
  - **Stage 2 overlay:** prior-action unit (no ESF/ESCP/DLI); headline 1 = macro framework / IMF coordination (para 8); headline 2 = conflict-exception adequacy (Paragraph 38-39); PSIA hybrid harm screen; series 24-month lapse / reversal; IBRD vs IDA; Cat DDO sub-branch
  - **Stage 3:** DPF-aware output (Program Document sections / policy matrix / LDP; DPF reference set; `next-series` timing); top-level `dpf_watch` array + DPF FCV Watch section in DOCX and HTML exports
  - **Knowledge:** `DPF_MODULE_GUIDE` + `DPF_POLICY_AREA_CHECKLIST` in `background_docs.py`, grounded in OPS5.02-POL.120 + OP 2.30; injected via `get_dpf_slice()`
  - **Tests:** `tests/test_dpf_phase2.py` (9 tests); full suite 96 passed; no IPF/mid-cycle regression
- **v9.8** - Phase 3 P4R/PforR instrument module (branch `feat/phase3-p4r`, base Phase 2 `feat/phase2-dpf` / PR #26, 2026-06-17):
  - **DLI + verification spine:** Stage 1 emits `%%%DLIS_START%%%...%%%DLIS_END%%%` (ipf_component; program_boundary; fcs_status; dlis; verification) when INSTRUMENT_TYPE is PforR; parsed by `extract_dlis()`; stripped from display by `clean_stage1_output()`
  - **P4R rubric:** `P4R_RUBRIC` (DLI conflict-sensitivity / IVA-verifiability / geographic inclusion / ESSA-ESMS / GRM / disbursement-cliff) via the Phase 0 `score_sr()` interface
  - **Registry/state:** `MODULE_REGISTRY` entries for `(PCN|PID|PAD|Unknown, PFORR, single)` with `p4r_dli_verification_spine` / `p4r_no_esf_escp` / `p4r_disbursement_under_conflict_headline` / `p4r_instrument_feasibility_advisory` guardrails; `AnalysisState` carries dlis / has_ipf_component, auto-adds `p4r_module`
  - **Stage 2 overlay:** DLI unit (no ESF/ESCP); headline = disbursement under conflict (IVA verification access + disbursement cliff, no CERC valve); DLI-realism; program-boundary/exclusions; ESSA/ESMS + GRM harm screen; OP 7.30 / government-systems feasibility advisory; IPF-component dual-spine
  - **Stage 3:** P4R-aware output (PforR PAD sections; DLI / verification-protocol / PAP language; P4R reference set); top-level `p4r_watch` array + P4R FCV Watch section in DOCX and HTML exports
  - **Knowledge:** `P4R_MODULE_GUIDE` in `background_docs.py`, grounded in OPS5.09 + OP 7.30; injected via `get_p4r_slice()`
  - **Tests:** `tests/test_p4r_phase3.py` (9 tests); full suite 105 passed; no IPF/mid-cycle/DPF regression
- **v9.9** - Phases 4+5 MPA wrapper + Multi-country / regional layer (branch `feat/phase45-mpa-multicountry`, base Phase 3 `feat/phase3-p4r` / PR #27, 2026-06-17):
  - **Multi-country / regional (orthogonal country_scope layer):** Stage 1 emits `%%%COUNTRY_SET_START%%%...%%%COUNTRY_SET_END%%%` (countries; regional_pdo; implementing_entity); `extract_country_set()` parses it (>=2 financed countries -> multi). `classify_country_set()` classifies each country (4-category + FY26 FCS) and flags non-FCS spillover/host-pressure candidates. `weighted_rollup()` does a fragility/exposure-weighted S/R roll-up (conflict x3, fragility x2) so a fragile minority is not masked. `REGIONAL_CROSSBORDER_LENS` + `get_regional_slice()`; cross-border lens, regional implementing-entity check (IGAD/ECOWAS/TDB), advisory financing-window pointers (Regional Window/CRW/WHR)
  - **MPA wrapper:** Stage 1 emits `%%%MPA_CONTEXT_START%%%...%%%MPA_CONTEXT_END%%%` (is_mpa; phase; base_instrument; regional_mpa; phase_transition_triggers); `extract_mpa_context()` derives approval authority (Board for Phase 1 / RVP for subsequent - advisory); `mpa_carve_outs()` suppresses subsequent-phase false positives (CERC/ESF/program-ToC/etc.); `MPA_MODULE_GUIDE` + `get_mpa_slice()`; adaptive-sequencing + institutional-continuity lens, cross-phase FCV-drift; routes each phase to its base instrument
  - **State:** `AnalysisState` sets country_scope=multi for >=2 countries and adds `multi_country_layer`; adds `mpa_wrapper` when is_mpa; carries is_mpa / implementing_entity / approval_authority
  - **Stage 2/3 overlays + output:** per-country + regional synthesis; `priority_scope` country-specific vs regional; top-level `regional_watch` + Regional FCV Watch section (DOCX + HTML); slices injected at Stage 2/3 (step-by-step via echoed country_scope/is_mpa; express via Stage-1 extraction locals)
  - **Tests:** `tests/test_mpa_multicountry_phase45.py` (13 tests); full suite 118 passed; no prior-phase regression
- **v9.10** - Phase 6 intersection matrix / multi-dimension composition (branch `feat/phase6-intersection`, base Phase 4+5 `feat/phase45-mpa-multicountry` / PR #28, 2026-06-17):
  - **Composition router:** `build_composition_plan(state)` selects the base instrument spine (IPF/DPF/P4R) and the active overlays (mid_cycle, multi_country) + MPA wrapper from `AnalysisState.active_modules`, and resolves **precedence**: mid-cycle live-project framing governs temporal; fragility-weighted roll-up governs rating when multi-country; restructuring level sets the output register; the instrument unit of analysis always governs. Backward-compatible (plain IPF -> no overlays)
  - **Single synthesis:** `dedupe_and_scope_priorities()` merges/dedupes priorities by normalised title and ensures a `priority_scope` on each
  - **Bounded injection (no silent truncation):** `bounded_injection_plan()` caps overlays by priority (instrument spine never dropped: instrument > mid-cycle > MPA > multi-country detail) and returns a disclosure string when anything is bounded
  - **Knowledge + prompt:** `INTERSECTION_SYNTHESIS_GUIDE` (layering, single coherent memo, precedence, bloat guardrail); Stage 3 prompt gains a Composition & Synthesis section; Stage 3 (both routes) injects the guide when `build_composition_plan(...).is_intersection` (>=2 active layers)
  - **Tests:** `tests/test_intersection_phase6.py` (8 tests); full suite 126 passed; no prior-phase regression. Completes the Phase 0-6 expansion (mid-cycle, DPF, P4R, MPA, multi-country, intersection) on the registry foundation
- **v9.11** - Secondary-document distillation and upload expansion (branch `feat/secondary-doc-distillation`, 2026-06-18):
  - **Upload tiers:** Zone 1 is a single required primary project document; Zone 2 accepts up to 10 supporting project-package documents; Zone 3 accepts up to 3 contextual documents.
  - **Secondary distillation:** `fcv_distillation.py` classifies and distills package/context documents into compact source-labelled cards before Stage 1 assembly. The primary document remains on the existing 60k-character Stage 1 path.
  - **Budget guard:** Secondary cards are capped per tier and by a global 32k-character budget with a context reserve. Overflow and distillation failures produce named stubs rather than silent drops.
  - **Stage 3 matching:** Priority JSON now includes `rra_driver_alignment` alongside `cpf_alignment`, so recommendations can link to RRA conflict drivers where uploaded and relevant.
- **v9.14** — Priority Points (branch `feat/priority-points`): single "Analysis guidance" box; client-side detection derives priority points from the text; a confirm strip (checkbox default ON) decides whether the answer panel is produced. Points injected as bounded soft emphasis into Stages 1–3 in both run routes (Stage 2 rating guardrail so ratings/DNH/rec-set are unaffected). New `/api/run-priority-questions` route fired AFTER the run completes (never inline, preserving the timeout design) + `extract_focus_questions` parser (`%%%FOCUS_QUESTIONS_START/END%%%`, truncation salvage; top-level `overview`). Single tinted "Responses to your priority points" panel: LLM-generated intro/overview + numbered responses, each a fuller 1–2 paragraph answer (route `max_tokens` 10k; blank-line paragraphs rendered in live/DOCX/HTML) + "Linked recommendations" + a "Note:" gap line. Status is internal-only (no pill); no evidence-basis line, no example chips, no per-answer re-run (further edits use the end-of-page follow-on box). DOCX + HTML export section; peer-review follow-on feed (`priority_responses`). Backend field names `priority_questions`/`focus_questions`; user-facing label "priority points".
- **v9.15** — PforR/DPO vocabulary-repair timeout fix (branch `feat/lending-diff-plus-priority-questions`, merged to `main` via PR #47, 2026-07-14):
  - **Root cause:** The Workstream-2 vocabulary repair (`repair_vocabulary_violations()`) ran a **blocking, non-streaming** Anthropic rewrite *after* the SSE stream had ended, and only for PforR/DPO (IPF returns no rule key and skips the path entirely). Because a substantive PforR output almost always leaks at least one banned ESS/SEP term, the repair fired on nearly every PforR run. With **no keepalives** reaching the client during that 1.5–3 min call — and PforR's outputs already being the longest in the app (near the Stage 2 6 min / Stage 3 8 min wall-clock caps) — the total request exceeded the frontend abort budget (`EXPRESS_STAGE_TIMEOUTS` S2 8m / S3 9m), tearing the stream as a Stage 2/3 timeout (`BodyStreamBuffer was aborted`). A secondary bug: the repair used `max_tokens=8000` against 16k/20k-token outputs, truncating long Stage 3 output and dropping the trailing `%%%JSON_START/END%%%` priorities block.
  - **Fix (deterministic scrub only):** `repair_vocabulary_violations()` now performs an **instant in-process regex scrub** with no LLM call — eliminating the blocking gap and the truncation. `_VOCABULARY_SCRUB_MAP` expanded to cover **every** banned term for PforR and DPO (previously only `ESS2`/`ESS4` were mapped, so `ESS1`/`ESS3`/`ESS5`–`ESS10` would pass through the scrub un-repaired). `\b` word-boundary matching means `ESS1` never matches inside `ESS10`, so ordering is irrelevant. The `violations` argument is retained for call-site compatibility but is no longer used (the scrub map is keyed on instrument). Behaviour is unchanged for IPF and for the four call sites (step-by-step S2/S3, express S2/S3). Tradeoff: scrub phrasing is blunter than an LLM rewrite (e.g. `ESS6` → "the ESSA", `SEP` → "the borrower's GRM"), accepted for determinism and zero timeout risk. `tests/test_vocabulary_validator.py` (2 new tests: no-LLM-call + all-banned-terms-scrubbed). Full suite: 203 passed.
  - **Note:** This PR also merged the previously-unmerged `feat/priority-points` (v9.14) and lending-diff / PforR SEA-SH reframing work onto `main` in one go — they had not been on `main` before PR #47.
- **v9.16** — PforR Stage 2/3 wall-clock caps raised (branch `fix/pforr-stage-timeout-caps`, 2026-07-14):
  - **Symptom:** After v9.15, PforR runs still timed out at ~6:55 elapsed. Evidence: the backend `STAGE_STREAM_TIMEOUTS[2]` cap was **6 min**; a large PforR PAD's Stage 2 stream (the app's largest output — 12-rec table, DNH, 25 questions, Under the Hood, ratings, category lens) legitimately ran up to that cap, and `_stream_stage()` raised `TimeoutError` at 360s into Stage 2 (Stage 1 ~55s + 360s ≈ 6:55 on the total-elapsed timer). The caps were set in v9.4 **before** PforR was added in v9.8, so they never accounted for PforR-scale output.
  - **Fix:** Raised backend caps `STAGE_STREAM_TIMEOUTS` to **S1 8m / S2 9m / S3 9m** (`app.py`). Raised the matching frontend abort budgets so each stays strictly above its backend cap (no frontend==backend race): Express `EXPRESS_STAGE_TIMEOUTS` → **S1 9m / S2 10m / S3 10m**; step-by-step `_stageTimeoutMs` → **S1 9m / S2 10m / S3 10m** (`index.html`). Step-by-step S1 (was 8m == cap) and S2 (was 6m == cap) had latent races that are now removed. All budgets sit well under the gunicorn `--timeout 1200` (20 min). `tests/test_stream_stage_timeout.py` unaffected (passes `max_seconds` explicitly). Full suite: 203 passed.
  - **Free-tier caveat:** The public Render service runs on the **free tier**, which spins down on inactivity (50s+ cold start) and is CPU/RAM-constrained. Raising the caps addresses the wall-clock cause, but reliable multi-minute SSE runs (PforR especially) ultimately want a paid Render instance. If a PforR run still times out after this, capture the Render log line at failure to distinguish an app-level stage `TimeoutError` (needs more time / smaller output) from a worker OOM/kill (needs a bigger instance).
- **v9.17** - Stage 1 timeout observability and distillation keepalive hardening (branch `fix/pforr-stage-timeout-caps`, 2026-07-14):
  - **Root cause correction:** The frontend abort timer calls `AbortController.abort(new Error(...))`; browsers may reject `fetch()` with that custom `Error` rather than an `AbortError`. The old catch block mislabelled such timeouts as `Could not reach the server`, so a 9-minute Stage 1 failure could be a frontend timeout, not necessarily a dropped connection or worker death. `requestErrorMessage()` now preserves custom timeout messages while still using the network fallback for true fetch failures.
  - **Stage 1 diagnostics:** Both `/api/run-stage` and `/api/run-express` now log low-cardinality Stage 1 preprocessing summaries (`docs`, role counts, aggregate uploaded content chars) and extraction completion timing (`elapsed_ms`, `doc_parts`, extracted chars, warning count). These logs avoid filenames/content but make Render failures easier to separate into frontend budget, preprocessing delay, extraction bottleneck, or worker OOM.
  - **Distillation keepalives:** `fcv_distillation.py` now yields each completed/timeout result as it arrives and emits `keepalive`/`distilling_wait` SSE events while slower secondary docs are still pending. This removes the previous collect-all silent window before Stage 1 model streaming.
  - **Upload-size guard:** Correct Render logs showed `/api/run-express` returning `500 106`, consistent with Flask's 50MB `MAX_CONTENT_LENGTH` being exceeded by a large base64 JSON upload rather than worker OOM. Oversized uploads now return an explicit `413` JSON response, and the frontend preflights file sizes before reading/submitting files, warning when raw files would exceed the deployment limit after browser base64 encoding. Tests added: frontend timeout classification, payload-size preflight, backend 413, per-doc distillation progress, Stage 1 payload diagnostics. Full suite: 208 passed.
  - **Main/Render state for IPS handover:** PR #51 merged these PforR timeout/payload changes to `main` as merge commit `2877bf9` on 2026-07-14. Live Render checks confirmed the Morocco Green Generation PforR PAD can complete end-to-end via `/api/run-express` (all three stages streamed; about 13:42 total in one run) and Stage 1 alone completed in about 4:14. A later India STARS PforR PAD live Express test hung before HTTP response headers and timed out client-side after 30 minutes, while local PDF extraction finished in about 18 seconds; treat that as a Render worker/gateway/pre-response stall pending Render-log review. The active IPS/ITS handover is `docs/20260714_ITS_handover_p4r_timeout_patch.md`.
- **v9.20** — Climate dedicated-module completeness hardening (branch `codex/climate-fcv-output-redesign`, 2026-07-24):
  - **Bug:** A live South Sudan PCN run rendered a silent "hybrid" — the two climate interaction boxes appeared, but the Reflections block, integration gauge, dividends synthesis, and wider-FCV note were missing (Render log: `Stage 2 lens diagnostic invalid ... The Climate-FCV diagnostic was omitted from the Stage 2 structured output`). Root cause: nothing enforced the v9.19 dedicated-module fields (`reflections`, `integration_level`, `integration_summary`, S/R evidence). Three layers each let them slip: the validity gate (`lens_diagnostic_failure_message`) accepts a diagnostic on materiality + one interaction alone; the Haiku recovery prompt (`repair_lens_diagnostic`) was written for the pre-v9.19 dual-use contract and never requested reflections/integration, so any recovery produced a valid-but-degraded readout; and a max_tokens-truncated primary (South Sudan is the app's largest output) dropped the diagnostic tail with no detection.
  - **Fix (full robustness):** (1) New pure helper `climate_readout_is_complete()` in `sector_lenses/pipeline.py` (complete = ≥1 grounded reflection AND non-empty `integration_summary`), plus `climate_lens_readout()`; both exported. (2) `extract_or_repair_lens_diagnostic` now triggers recovery not only on a hard failure but also when a *usable* climate diagnostic is incomplete, and **never downgrades a usable primary** — a recovered diagnostic is adopted only if the primary was unusable or the recovery is complete. (3) `repair_lens_diagnostic` prompt + compact-shape now request `integration_level`, `integration_summary`, 3–5 `reflections` (with `question_key` ∈ the six cq keys), `less_central`, and separate `sensitivity_evidence`/`responsiveness_evidence`; recovery `max_tokens` 6000→8000 and char budget 12,000→16,000. (4) Honest partial notice: when a usable readout is still incomplete after recovery, the module notice (frontend `renderClimateModuleNotice` via new `climateReadoutComplete()`; DOCX `add_climate_notice`; shared HTML via the same renderer) shows an amber "reflections and integration readout could not be generated for this run … were not substituted" line instead of silently omitting the sections. (5) Truncation observability: `_stream_stage` captures the provider `stop_reason`; both Stage 2 call sites log a warning when a climate-active Stage 2 hits `max_tokens`.
  - **Contract note:** "Usable" (interactions + materiality) is unchanged; "complete" (adds reflections + integration_summary) is the new bar that drives recovery and the honest notice. `climate_error`/`climate_valid` are unchanged; completeness is a separate, non-blocking signal (graceful degradation preserved — an incomplete-but-usable diagnostic is never dropped to core-only). ITS/FastAPI parity: add the completeness helper + recovery-prompt fields to `FCV_BUILD_PARITY.md`.
  - **Tests:** new `tests/test_climate_diagnostic_completeness.py` (helper, recovery-prompt fields, incomplete-triggers-recovery, no-downgrade, complete-skips-recovery) + frontend partial-notice test; existing bypass/recovery tests updated for the new complete-diagnostic contract and 8000/16,000 bounds. Full suite: 363 passed.
- **v9.23** - Climate-FCV country-bank runtime grounding (branch `feat/climate-country-bank`, 2026-07-31):
  - A public submodule at `data/climate-fcv-country-bank` supplies schema `1.0.0` approved-only runtime releases; `CLIMATE_COUNTRY_BANK_PATH` is the explicit local/deployment override.
  - Deterministic selection targets 8 and caps 12 bank items, 6,000 bank characters, and 12,000 combined bank/live characters.
  - Grounding states are `bank+research`, `bank-only`, `research-only`, and `thematic-only`. Live research failure is non-fatal. Express and step-by-step rematerialize canonical IDs server-side; the browser retains display-safe metadata only.
  - Dedicated Climate Stage 2 remains native. Reviewed structural evidence and accepted current/project-specific research enter one bounded untrusted-data block with evidence-status, causal, and uncertainty guardrails. Standard non-Climate routing is unchanged.
  - Live HTML, shared HTML, and DOCX show matching provenance. DOCX rematerializes the manifest and cannot accept browser-supplied reviewed-source metadata.
  - South Sudan is the initial single-country pilot and is approved in production content version `2026.07.south-sudan-pilot`; runtime materialization returns 12 selected items from 19 approved evidence records and seven approved pathways.
  - The companion bank stores structured summaries/citations, not raw PDFs; generated summaries cannot self-cite.
  - **Final reader polish:** the opening is a normal narrative section rather than a colored module notice, combining two-to-three scene-setting sentences with a project-specific "Why it matters" transition. Both mandatory interaction directions permit two short component-anchored paragraphs. Core-question status chips are hidden, framework labels read "For further insights on why this matters, see", and the gauge pairs its rating with a concise improvement message. Reader-facing climate summaries replace the noun "materiality" and clip on sentence boundaries where possible. The priority Next button is re-enabled when returning from the last card.
  - **Live-research recovery:** a structured `partial|complete` bundle that contains sources and claims but narrowly fails `climate_research_insufficient` may retry once within the existing two-attempt/deadline cap. Missing structured output, truncation, timeout, and terminal provider errors are never duplicated by this path.
- **v9.24** - Verified Climate-FCV evidence-to-decision runtime (branch `feat/climate-country-bank`, 2026-08-01):
  - Climate-only Express design reviews dispatch to `climate-verified-v2` after the existing country-bank/live-research resolver; mixed-lens, implementation-review, step-by-step, and stored legacy flows remain unchanged.
  - One unambiguous file explicitly placed in the Project Document slot becomes the bounded project-fact source, labelled `user_designated` rather than independently verified/latest; stage, geography, and financed-scope applicability remain unresolved. Unresolved package uploads remain inventoried but their fact authority is withheld; multiple candidate primaries force unresolved precedence. Runtime chunks are deterministic projections of extracted text, not original DOCX/PDF structural locators.
  - Four independent judgments replace the old single Climate integration label. The reader shows zero to three admitted/ranked priorities, condition-triggered enhanced actions, bounded readiness flags, and no generic High-priority labels.
  - Automatic deterministic checks suppress unsupported dependent objects; one conditional semantic reviewer runs only for high-risk judgments. No routine human review step is required.
  - `climate_assessment` and the canonical `climate_reader` are additive SSE fields. Live HTML and shared HTML render the server reader directly; DOCX deterministically rebuilds the same reader from the assessment. Reader state is preserved in session files and completed Express checkpoints; zero-priority HTML/DOCX outputs retain the explicit no-recommendation admission message; candidate-bank outputs retain `preview; not approved`.
  - The browser budget is 15 minutes; backend verified execution is capped at 14 minutes, bounds retry time across attempts, emits keepalives, and cancels later model calls after timeout or disconnect.
  - Privacy-safe recommendation diagnostics record raw, parsed, structurally valid, gate-admitted, and final counts; deterministic admission reason codes; up to 12 unsupported numeric tokens; and whether the conditional semantic reviewer ran and its bounded verdict. Numeric component/subcomponent labels are auto-supported only from candidate-linked verified project facts, while suffixes of structured IDs and numbered-list markers are excluded from numeric-claim checks; unsourced dates, thresholds, and quantities remain blocking. The same fields appear in the technical annex and one bounded Render log line, without candidate prose.
- **v9.32** — Verified reader lay-readout restructure (same branch, 2026-08-07; spec `docs/superpowers/specs/2026-08-06-climate-reader-lay-readout-restructure-design.md`, plan `docs/superpowers/plans/2026-08-07-climate-reader-lay-readout-restructure.md`). Acts on the cross-context recommendations from the four-way blind eval without regressing the evidence-gated discipline. Eight changes, all kept in parity across the three reader surfaces (`render_reader_html`, `write_reader_docx`, frontend `renderClimateVerifiedAssessment`): (1) **Overview at the top** — the headline sensitivity rating scale (`_sensitivity_rating_html`) is lifted out of the Core Questions section to sit directly under the executive readout. (2) **Diagnose-vs-act split + promotion rule** (`_judgment_prompt`) — core-question answers stay diagnostic (finding + one-line watch, no fix); a material issue must instead surface once as a ranked priority; one finding lives in exactly one tier. (3) **Three actionability tiers** — deep Priorities; a **visible Quick fixes** tier (the old collapsed "Points to check" `<details>` is now an open `<section>`, minor-point label reframed "How to check" → "How to address"); and a **standalone Watch section** ("What to keep an eye on", `HEADINGS[5]`) consolidating the per-question watch notes (inline "What to watch" removed). (4) **Priority cap 3 → 5** — both `[:3]` slices raised (`build_reader_model` and `admit_and_rank`), prompt says "at most five … only where materiality clearly warrants", schema description updated; no silent truncation. **Follow-up fix (`c9a167a`):** a live quality run then hit `max_tokens` on `recommendation_compiler` (five full candidates > its 5k output budget), so `CALL_BUDGETS["recommendation_compiler"].output_tokens` was raised 5k→9k (matching `judgment_review`); raising the cap without the budget bump truncates Stage 2 at `stop_reason=max_tokens`. (5) **Routing metadata dropped from the reader view** — `PRIORITY_FIELDS` trimmed of `routing_status`/`authority_basis`/`recommendation_basis`/all `*_ids` rows; frontend `detailFields` removed. (6) **Raw evidence codes hidden** from Overview/Core-questions/Priorities/Quick-fixes (rating, core-question, minor-point evidence lines removed); the `PF-`/`RG-`/`PW-` key remains only in the "How this analysis was produced" fold. (7) **Calibration guardrails** added to the shared `_common` prompt wrapper — use the source's own acronym expansion (never invent), preserve a number's verb on paraphrase ("affected" ≠ "displaced"), and mark unverifiable figures/institutions/events as unverified context to confirm. (8) **Two new climate-tied driver questions** (`CLIMATE_DRIVER_QUESTIONS`) — `dq-geo-overlap` (do climate activities land where conflict/fragility is worst?) and `dq-participation-quality` (is the quality of participation monitored, not just a quota met?). Tests: 8 added/updated across `test_climate_verified_render.py`, `test_climate_recommendations.py`, `test_climate_verified_client.py`, `test_climate_core_questions.py`, `test_climate_driver_depth.py`; full suite **862 passed** (baseline 854). Not yet deployed to quality; ITS/FastAPI parity for these reader changes is deferred (handover item B1, `FCV_BUILD_PARITY.md` §26).
- **v9.33** — Verified reader top-of-report overview summary (same branch, 2026-08-08). Completes the v9.32 "Overview at the top" change, which had only *relocated* the sensitivity rating card (below the full 6-paragraph Executive readout, carrying just the generic level-keyed gloss) - so the report still opened like the previous version. A live smoke review confirmed the intended combined, concise, project-specific overview never existed. Fix: a new purpose-written `overview_summary` model field (3-4 plain-language sentences: what the project is, how well it handles the climate-FCV intersection overall, the most important residual gap; no overall numeric rating). Added to the `judgment_review` schema (`climate_verified_schemas.py`, required) and prompt (`climate_verified_prompts.py`, instruction + Return JSON key); carried through the pipeline into the assessment (`climate_verified_pipeline.py`, alongside `executive_readout`); surfaced by `build_reader_model` both top-level and embedded in the factored overview unit (`climate_sensitivity_rating.overview_summary`). All three reader surfaces now render the **overview block at the very top** - the summary embedded in the rating card, positioned *after* the "How sensitive" graphic (question, rating label, scale, one-line gloss), which comes first; the whole card sits above the fuller Executive readout (kept below as detail): `_sensitivity_rating_html` + reordered `render_reader_html`; reordered `write_reader_docx`; frontend `renderClimateVerifiedAssessment` (`ratingHtml` gains the summary; return order = smoke -> rating/overview -> status -> Executive readout -> core questions). Graceful degradation: empty `overview_summary` (older/blank/smoke runs) renders the card with only its level gloss, unchanged. `normalize_climate_assessment` shallow-copies v2.1 payloads so the DOCX rebuild path preserves the field. A live smoke re-run confirmed the model-authored summary renders in the top card end-to-end. Two follow-up refinements from that review: (a) the "How sensitive" graphic (question/label/scale/gloss) is ordered *first* in the card, with the overview text below it (all three surfaces); (b) a judgment-prompt de-duplication rule stops the Executive readout re-opening with the same one-sentence project identification and financing figure the overview_summary already states (takes effect on the next model run). Tests: 6 new/updated in `test_climate_verified_render.py` (build-model carry, HTML top-placement, graphic-before-summary ordering, DOCX ordering, absent-field degradation) + 2 prompt assertions in `test_climate_verified_client.py`; the in-memory-stream DOCX test updated for the new order. Full suite **867 passed**. ITS/FastAPI parity deferred with the rest of v9.26-v9.32 (handover B1).
- **v9.34** - Verified Climate-FCV HTML reader refresh (same branch, 2026-08-09). Live and standalone HTML now share `renderClimateVerifiedAssessment()` and the same scoped stylesheet, with a prose-led numbered report hierarchy. Full priority narratives, suggested drafting, checks, watch items, methodology, evidence key, source list, and displayed diagnostics remain intact; smaller Climate-FCV considerations now precede document checks. Project-relevant WBG guidance is derived deterministically only when a current core question's normalized source title exactly matches a reader source with a valid public World Bank HTTPS URL; unmatched guidance is omitted. This is an HTML presentation-only change: no prompt, schema, backend, model, rating, substantive content, recommendation/evidence logic, or DOCX change.
- **v9.35** - Verified Climate-FCV reader hierarchy and project-specific guidance refinement (same branch, 2026-08-10). The reader now uses a balanced, prose-led hierarchy across live HTML, standalone HTML, and DOCX: one restrained Overview panel for the sensitivity rating, normal-flow executive and core-question prose, a narrative transition into the ranked priorities, numbered smaller Climate-FCV points/document checks/watch items (with smaller Climate-FCV points first), and a neutral zero-priority state: "No operational priorities were identified in this assessment. Review the core questions and points to check below." Live and exported HTML open Priority 1 and collapse later priorities without removing any narrative, drafting, or structured detail; DOCX keeps every priority fully expanded. Printing temporarily opens all reader disclosures and restores their prior screen state afterwards. The reader-facing evidence-status label, technical annex, evidence key, recommendation/run diagnostics, and similar internal verdicts are removed; the smoke-mode warning and the method, pathways, limitations, and source list remain. Project-specific WBG guidance is now carried canonically as `guidance_items`: only matched, public World Bank HTTPS sources are eligible, normally yielding two to four when available, with no fixed-source padding; each item explains both its practical value and how it relates to current project findings. The frontend prefers canonical items and safely derives a bounded fallback for older saved readers. The landing page continues to accept one primary document plus up to ten project-package documents, with the cap enforced by a shared helper and covered by an executable contract test. This refinement changes presentation and deterministic reader assembly only; it does not change the Climate-FCV prompt, schema, model calls, rating, or recommendation/evidence admission logic.
  - Guidance follow-up: the numbered guidance section now contains one collapsed native disclosure for all sources. Each source is limited to one controlled practical-value sentence and one verified project follow-up sentence; full core-question summaries are not copied. Print opens this disclosure and restores its prior state, while DOCX remains expanded.
- **v9.36** - Climate-FCV country-bank candidate expansion (branch `codex/climate-summary-quality-fixes`, 2026-08-13): the pinned bank submodule now references companion-bank commit `12a804f`, which adds schema-1.1 reviewed candidate packages for Afghanistan, Burkina Faso, Cameroon, Central African Republic, Democratic Republic of the Congo, Ethiopia, Haiti, Iran, Iraq, Lebanon, Libya, Mali, Mozambique, Myanmar, Niger, Nigeria, Papua New Guinea, Somalia, South Sudan, Sudan, Syria, Ukraine, West Bank and Gaza, and Yemen. The explicit candidate runtime contains 24 countries, 291 sources, 565 evidence records, and 178 pathways. The production `releases/current/runtime.json` remains unchanged and approved-only; candidate use requires both `CLIMATE_COUNTRY_BANK_PATH` and `CLIMATE_COUNTRY_BANK_PREVIEW=reviewed-candidate`, and remains visibly labelled `preview; not approved`. A packet importer and contract tests were added in the companion repository; country-level substantive review and promotion remain required.
  - Preview-smoke follow-up: multi-country releases may reuse the same public source URL under different country-scoped source IDs. Runtime materialization therefore validates normalized URL uniqueness only within the selected country package, while continuing to reject duplicates within that package. A regression materializes all 24 candidate countries.
  - Rollout safeguard follow-up: candidate-backed readers now show `Candidate country evidence: preview; not approved.` in live HTML, shared HTML, and DOCX. This restores the candidate-approval warning removed by the v9.35 reader simplification without restoring evidence-status panels, technical annexes, evidence keys, or run diagnostics.
  - Drafting-target repair follow-up: verified Climate-FCV recommendations now canonicalize a non-standard current-document section label only when the cited operational-guidance entry supplies a unique permitted target with a meaningful token match. Unknown guidance, unrelated sections, and ambiguous targets remain blocking; the repair is recorded as `DRAFTING_CURRENT_SECTION_CANONICALIZED` before the unchanged validator and admission gates run.
  - Summary strength-card follow-up: verified-analysis `existing_responses.description` now uses two or three plain-language sentences within the existing 45-word bound. The first is a short self-contained statement; the remainder names a project anchor and explains why the response matters. `climateSummaryStrengths()` uses that complete first sentence as the card heading and the remaining sentence(s) as the explanation, without eleven-word truncation. One-sentence legacy responses retain a readable fallback. No schema, delimiter, rating, recommendation, or detailed-reader contract changed.
  - Operational-routing follow-up: the verified Climate-only Express path now resolves a typed operation context from the primary document before research planning and country-bank selection. It distinguishes IPF, PforR, and DPF; recognizes Project Paper, Program Paper, Program Document, PCN, PID, and PAD; retains an MPA wrapper only with a separately resolved base instrument; identifies explicit regional/multi-country scope; and records preparation, processing, and E&S routing only where supported. Unknown instrument or document routes fail closed and receive no IPF drafting packet. Guidance registry v3 adds instrument-correct targets for new-model IPF, PforR (ESSA/PAP/DLIs), DPF (prior actions/policy and impact analysis), and the MPA program layer. The resolved context is passed to every verified model stage and shown in detailed, summary, standalone HTML, and DOCX readers. Regional operations continue to withhold the single-country bank. Preparation boundaries are now instrument-specific: IPF/PforR on or after 17 April 2026; DPF on or after 18 April 2026.
  - Operational-routing review fixes: an explicit OIS date overrides document-name regime markers; PforR and DPF recommendation/drafting prose is deterministically blocked when it uses incompatible IPF/PforR instrument terminology; the MPA program layer is prioritized inside the bounded guidance packet; and the five-minute reader now shows the E&S route as well as instrument, document, preparation model, and MPA status.
  Frontend timeout budgets remain Express 15/15/10 minutes and step-by-step 15/10/10 minutes.
- **v9.39** - Normal-FCV five-minute Summary across all reviews (branch `codex/climate-summary-quality-fixes`, 2026-08-22; design `docs/superpowers/specs/2026-08-21-normal-fcv-summary-all-reviews-design.md`). Core Stage 3 emits optional `concise_readout` plus `concise` on every ranked priority, with JSON-first ordering to reduce trailing structured-block omission. The parser admits the concise bundle atomically and otherwise preserves Detailed with no repair call. Valid normal reviews open Summary by default with a detailed overall assessment, both FCV ratings, exactly three strengths, and all priorities in a single-open accordion. Normal and verified Climate summaries share the controlled non-mandatory advisory. Completed Express recovery persists the complete Summary state; HTML/DOCX remain detailed-only. Live smoke and quality acceptance used Somalia STAIRP Phase 1 (P513127); final repository verification was `1012 passed`. See `docs/20260822_ITS_handover_normal_fcv_summary.md` and `test_documents/live_acceptance/README.md`.
- **v9.38** - Verified Climate recommendation routing completeness and fail-loud handling (branch `codex/climate-summary-quality-fixes`, 2026-08-14). A Somalia DPF PID exposed a routing hole: the recommendation compiler produced four candidates, but all four were suppressed as invalid current-document targets because the guidance registry covered DPF Program Documents but not DPF PIDs. `climate-guidance-v3` now covers every supported active route: IPF PCN/PID/PAD/Project Paper/AF/Restructuring; PforR PCN/PID/PAD/Program Paper; DPF PCN/PID/PAD/Program Document; and the MPA overlay for each supported base instrument. Unknown document, TA, ISR, and unresolved-instrument routes continue to fail closed. A route-matrix contract test and a Somalia-shaped DPF PID pipeline regression protect against recurrence. If a model emits one or more parsed candidates but every candidate is suppressed, diagnostics now add `RECOMMENDATIONS_ALL_SUPPRESSED`, set `review_status=attention`, and every reader surface displays an explicit incomplete-recommendations warning instead of a neutral or successful zero-priority result. A genuine zero-candidate model response retains the normal zero-priority state.
- **v9.31** — Em-dash provenance polish (same branch, 2026-08-07): the verified reader's `attach_provenance()` runs AFTER `build_reader_model()`'s `_scrub_placeholders` pass, so model-generated evidence-trail text and the static source descriptions bypassed the dash/placeholder scrub - a live scrape found ~5 residual em/en-dashes there (the earlier mojibake `�` defect was already fixed in v9.28). `attach_provenance()` now runs `_scrub_placeholders` over both `evidence_trail` and `sources` (`sector_lenses/climate_verified_render.py`), normalising em/en dashes to ASCII hyphens on every reader surface (live HTML, shared HTML, DOCX) at once. Additive and non-gating (runs after `validate_reader_model`). `tests/test_climate_evidence_trail.py` (1 new regression test); whole suite 854 passed.
- **v9.30** — Remaining-updates batch (same branch, 2026-08-06): (A3) recommendation narrative vs suggested-drafting repetition tightened in `climate_verified_prompts.py` - narrative (reasoning), structured fields (breakdown), and drafting (ready-to-use text) are kept as three distinct registers. (C) the `CCDR guidance note` literature entry now links to the canonical FCV-in-CCDRs Approach Note (documents.worldbank.org/.../099021025050037410); the `Conflict-Sensitive Climate Action Compendium` stays `url=None` (no confirmed public title - never fabricate). (A4) **document-integrity scan ported to the general (non-climate) screener** (`app.py`/`index.html`): Stage 1 emits a light `%%%DOC_CHECKS_START/END%%%` block (`{finding, why_it_matters, where}`, max 5, empty if none, document-text-only, the same four defect classes as the climate reader), stripped by `clean_stage1_output()`, parsed by `extract_doc_checks()`, attached on both run routes; the frontend stores `docChecks` and renders a light 'Points to check in the document' collapsible at Stage 3 (general + climate-module paths; the verified reader keeps its own points-to-check). `tests/test_doc_checks.py`; whole suite 853 passed.
- **v9.29** — Climate-FCV driver-depth lens (same branch, 2026-08-06; spec `docs/superpowers/specs/2026-08-06-climate-driver-depth-lens-design.md`). Closes the blind-eval "thin analytical driver depth" critique without regressing calibration. New `CLIMATE_DRIVER_QUESTIONS` (5) + `select_triggered_drivers()` in `climate_question_bank.py`: deeper political-economy driver questions - resource rents / elite capture, value-chain / market-actor capture, intercommunal representation, tenure & displacement, security-economy / armed-actor incentives - each **explicitly tied to the climate/environmental dimension** and worded as a design question, never a prediction. They fire on trigger signals and feed the VERIFIED reader's existing `core_questions` path (the core `CLIMATE_QUESTION_BANK` and the dedicated module are untouched): `_core_questions_to_answer` merges core-bank + driver candidates (deduped); `_CORE_QUESTION_CAP` 5->7; the judgment prompt gains a driver note + a no-prediction / no-named-actor guardrail; the schema/core-question count reads "three to seven". No schema-structure or render change - drivers render as additional core-question cards, mixed in. Evidence-gating unchanged (each answer must cite a resolving ID or flag a gap). `tests/test_climate_driver_depth.py`; full suite 568 passed.
- **v9.28** — Verified reader quality-review refinements (same branch, 2026-08-06, after the first successful quality run): (1) **em/en-dash normalisation** — `_scrub_placeholder_text` (which runs on every reader string in `build_reader_model`) now maps `—`/`–` and any stray replacement char to ASCII hyphens, fixing the mojibaked `�` seen in exported prose and matching house style. (2) **5-point sensitivity scale** — the `sensitivity` judgment enum is expanded from 3 substantive levels to 5 (`very_strong|strong|moderate|limited|very_limited` + `unclear`) across the schema, `climate_judgments.ALLOWED`, and the judgment prompt; `_SENSITIVITY_RATING` / `_SENSITIVITY_SCALE_LABELS` render the headline rating on a Very Limited → Limited → Moderate → Strong → Very Strong scale (`level` 0-5). Tests updated in `test_climate_verified_placeholder_scrub.py` + `test_climate_core_questions.py`; full suite 563 passed.
- **v9.27** — Verified reader smoke-review refinements (same branch, 2026-08-05, after a live smoke render review): (1) the generic "overall reads" strip is replaced by a headline **climate & FCV sensitivity rating** — `build_reader_model` derives `climate_sensitivity_rating` from the retained internal `sensitivity` judgment on a Limited→Moderate→Strong scale (`_SENSITIVITY_RATING`, `level` 0-3, tone colours, evidence IDs, AI-judgement caveat) rendered as a segmented scale in frontend + server HTML and as text in DOCX (`_sensitivity_rating_html`); `judgment_reads` removed. (2) Core-question summaries lengthened to ~120-220 words in two short paragraphs (schema + prompt) and rendered with paragraph breaks on all surfaces. (3) `_METHODOLOGY_NOTE` rewritten in plain, lay language. (4) `build_evidence_trail` now drops pathways with empty `chain_prose` and evidence-key entries that resolve to empty text (removes the smoke-model naked "Climate -> FCV:" bullets and bare PW- codes). (5) **judgment_review budget raise (quality-run fix):** the richer judgment output (exec readout + 4 judgments + core_questions ~2 paragraphs x5 + minor_climate_points) overran the 4,000-token `CALL_BUDGETS["judgment_review"].output_tokens` on the quality model, truncating Stage 2 (`stop_reason=max_tokens` -> "Structured climate output incomplete"); raised to output_tokens 9,000 / timeout 240s (`climate_verified_contracts.py`); contract + pipeline-timeout tests updated. Smoke passed only because the cheap model wrote terser answers under 4k. Tests updated + added in `test_climate_core_questions.py`; full suite 562 passed.
- **v9.26** — Verified Climate-FCV reader lay-comprehensibility redesign (branch `feat/climate-reader-lay-comprehensibility`, base `codex/climate-country-bank-deploy` `6a59a6f`, 2026-08-05). Makes the verified reader (`climate-verified-v2.1`) legible to a lay, first-time reader seen blind, and removes executive-summary repetition — while preserving the evidence-gated, cannot-promise discipline that won the blind eval. Four workstreams:
  - **WS1 — sources + provenance clarity:** `CLIMATE_LITERATURE_REFERENCES` entries gain a plain-language `description`; "Sources & further reading" renders title + description with linked WB publication pages, and name-only sources (`url=None`) are explicitly marked "reference only; no public link shown until confirmed" (never fabricated). The provenance annex gains lay intros for "Pathways" and the "Evidence key"; the "Points to check" intro is rewritten in plain language; server `HEADINGS[3]` + DOCX label unified to the frontend "Points to check before the decision meeting" (fixes a prior parity mismatch).
  - **WS2 — Core climate-FCV questions (replaces the four judgment boxes):** `climate_question_bank` wired into the verified pipeline for the first time — `project_signals` derived from verified facts (`_core_questions_to_answer`), up to six triggered questions posed at the judgment stage, only evidence-grounded answers kept (`_admit_core_questions`: question posed + ≥1 cited evidence ID resolves), capped at five. New `core_questions` field + `CORE_QUESTION_SCHEMA` on the judgment stage, with a no-overlap-with-executive-readout rule, source attribution, and a cannot-promise "what to watch" line. The four judgment VALUES are retained internally (calibration + semantic-reviewer risk); the reader shows a compact "overall reads" strip (sensitivity / responsiveness / from-intent-to-delivery; relevance dropped from view as it echoed the exec readout) + literature-grounded question cards. `HEADINGS[1]` → "Core climate-FCV questions".
  - **WS3 — Smaller climate & fragility points to check:** new `minor_climate_points` + `MINOR_CLIMATE_POINT_SCHEMA` on the **judgment** stage (hosted there rather than the recommendation stage to keep the latter under its 4100-char transport-complexity budget) — up to three smaller climate/FCV points tied to a residual gap that may not warrant a full recommendation. `_admit_minor_climate_points` gates them (gap exists AND not covered by an admitted priority; deduped against priority titles + readiness-flag text; cap 3). "Points to check" renders two labelled groups — "Document points to confirm" (existing integrity flags) + "Smaller climate & fragility points to consider".
  - **WS4 — recommendation-details intro:** the frontend "Recommendation details" collapsible gains a plain-language intro for first-time readers.
  - **Parity + guards:** every reader change lands in the frontend `renderClimateVerifiedAssessment`, server `render_reader_html`, and DOCX `write_reader_docx`. Readers without `core_questions` / `minor_climate_points` (older/blank) still render (reads strip only; single points-to-check group). All additive fields are non-gating (`build_reader_model` / `validate_reader_model` unaffected).
  - **Smoke caveat:** core-question cards and minor points are model-generated, so a cheap smoke run may return few/none (schemas allow empty arrays); the reads strip, intros, and section structure render regardless — real content appears on a quality run.
  - **Tests:** `tests/test_climate_core_questions.py`, `tests/test_climate_minor_points.py` + updates to literature / render / evidence-trail / app-contract tests. Full climate/sector suite: 560 passed (baseline 550). Not yet deployed (smoke auto-deploys on push to `codex/climate-country-bank-deploy`). ITS/FastAPI parity logged in `FCV_BUILD_PARITY.md` §26.
- **v9.25** - Verified Climate-FCV TTL drafting integrity (`climate-verified-v2.1`, branch `feat/climate-country-bank`, 2026-08-03):
  - Each admitted priority requires a structured 90-160 word current-document drafting block. A second operational-instrument block is optional and survives only when distinct and linked to an evidenced named instrument. `team_to_confirm` and `new_vehicle_may_be_needed` are not successful recommendation routes; safe stage-document advice uses `standard_document_advisory`.
  - A versioned, bounded operational-guidance registry selects permitted PCN/PAD destinations by document and instrument type. It is advisory context, not project evidence or a policy corpus, and contains no fabricated policy paragraph citations.
  - Deterministic validation blocks unsupported instruments, actors, effectiveness/appraisal timing, technical systems, mandatory wording, and drafting references. Telemetry records only reason codes and field paths. Readiness flags carry residual-gap IDs and are suppressed when they duplicate admitted priorities.
  - Every judgment value, including `unclear`, `not_expected`, and `not_evidenced`, requires a resolvable evidence ID. The final-priority summary is derived only after deterministic admission and semantic review.
  - Accepted live research is counted from distinct `CE-LIVE-*` evidence IDs; mixed valid/invalid source declarations are rejected. Browser, HTML, and DOCX render the same drafting labels, destinations, status, guidance basis, text, priority summary, provenance count, and `preview; not approved` evidence label.
  - Raw OPCS/ESF material remains outside the runtime and repository workflow. Any later WBG Cowork review is a separate, targeted conformance check of selected registry propositions and wording boundaries.

- **v9.22** — Climate-FCV readout redesign: core-question bank + reader layout (branch `feat/climate-readout-redesign`, base `main` post-#55, 2026-07-27):
  - **Core-question bank:** new pure `climate_question_bank.py` — a WBG-source question bank (six stable themes cq1-cq6, each question carries a `source` + lowercase `triggers`) + `select_triggered_questions(project_signals)` that fires per-theme questions from Stage-1-derived signals (cq1 always guaranteed). Sourced from the unrestricted climate-FCV frameworks under `docs/climate_module/` (Maximizing the Peace and Social Dividends of Climate Action; FCV-Sensitive Climate Action Framework; Defueling Conflict; Conflict-Sensitive Climate Action Compendium; CCDR guidance note). `tests/test_climate_question_bank.py`.
  - **Diagnostic contract additions** (`sector_lenses/pipeline.py`): climate `reflections[]` gain a `source` field and a larger two-paragraph `text` bound (700→1800; title 80→160; cap 5→6); new 6-tier `integration_rating` (`Extremely Low`..`Very Well Embedded`, via `climate_integration_rating()`, `''` when absent, keeps `integration_level` for back-compat); new `strengths_weaknesses[]` (`_normalize_climate_sw`, `{side: strength|gap, title, text}`, ≤4 per side).
  - **Stage 2 climate-native prompt** (`build_lens_stage_context`, `project_signals` kwarg wired at both routes): injects the triggered bank, requests per-theme two-paragraph answers with `source`, the 6-tier `integration_rating`, and structured `strengths_weaknesses`. Recovery prompt (`repair_lens_diagnostic`) mirrors source/rating/two-paragraph + the OPCS §12 boundary one-liner.
  - **Phase 4B — OPCS §12/§12.9 calibration:** Stage 2 climate suffix gains the recommendation-calibration guardrails (instrument-route; PA/CDRS flag-not-determine; no universal numeric horizon → "asset-appropriate design horizon"; IPF-only ESS map; conditional compound-risk wording; analytical-source labelling). Stage 3 climate prefix drops `wider_fcv_context` (parsed for back-compat, no longer requested) and gains §12.5/§12.9 CERC + CDRS + AF/Restructuring/MPA guardrails + the `authority_basis` tag (shared with the dual-regime field; not re-added). Climate module `manifest.yaml` stage3 line no longer requests `wider_fcv_context`.
  - **Budgets:** `PLATFORM_STAGE_BUDGETS` Stage 2 2000→3300, Stage 3 1200→1600; `_bounded_stage3_lenses` token target 1100→1500 (fit the bank + calibration + S&W).
  - **Native-route context boundary:** Dedicated Climate-FCV Stages 2-3 call `build_lens_stage_context(..., compose_prompt=False)` in both Express and step-by-step paths. This preserves authoritative lens metadata, sources, version checks, and diagnostic normalization without composing the discarded legacy sector-lens prompt.
  - **Frontend + exports:** 6-tier gauge (`climateIntegrationRatingFraction`, legacy 4-tier fallback); new `renderClimateCoreQuestions` (lay intro naming the source literature → both interaction directions in prose → per-theme answers with soft status + source line) and `renderClimateStrengthsWeaknesses` (two-column full detail). New climate readout order = notice/gauge → strengths & weaknesses → core questions; standalone dividends + wider-FCV sections dropped in module mode. Live HTML, shared HTML (`downloadHTML`), and DOCX (`add_climate_core_questions` / `add_climate_strengths_weaknesses`) kept in parity.
  - **Tests:** `tests/test_climate_question_bank.py` + extensions across pipeline, app-contract, and frontend suites; South Sudan fixture extended with `source`/`integration_rating`/`strengths_weaknesses`. Full suite: 454 passed.
- **v9.21** — Dual-regime process model: legacy PAD ↔ new-model Project Paper (branch `feat/dual-regime-process-model`, PR #55, 2026-07-27). *(Version-history entry recovered here: the original dual-regime docs commit staged nothing for this file because the guide is tracked as lowercase `claude.md` and `git add CLAUDE.md` silently no-ops — see the reference docs for the full spec.)* Two independent axes: `preparation_regime` (`new_model`|`legacy_transitional`|`unresolved_policy_source`, corrected in v9.37 to the instrument-specific OIS boundaries of 17 Apr 2026 for IPF/PforR and 18 Apr 2026 for DPF) and `es_regime` (ESF/legacy-safeguards/PS/instrument-specific/unresolved, governed by Concept Decision date vs 1 Oct 2018). Pure `regime_router.py`; Stage 1 `%%%REGIME_CONTEXT%%%` detection (`extract_regime_context`); terminology (`appraisal_document_label`, `pad_sections`↔`appraisal_document_sections`); regime-aware `action_timing`; regime-gated minimum reference set (`appraisal_reference_set`); `build_regime_header`/`build_minimum_reference_block` injected into Stage 2/3 (both routes); `authority_basis` recommendation field. Legacy + unresolved render byte-for-byte unchanged. Full suite: 436 passed.
- **v9.19** — Climate-FCV dedicated module output + OPCS compliance guardrails (branch `codex/climate-fcv-output-redesign`, 2026-07-24):
  - **Dedicated module output:** selecting the Climate lens now produces a dedicated climate-FCV assessment. The six core questions (cq1_interaction, cq2_maladaptation incl. lock-in, cq3_dividends, cq4_inclusion, cq5_institutions, cq6_adaptive) are the Stage 2 internal spine; the general FCV engine is retained only as an internal input.
  - **Diagnostic contract additions** (`sector_lenses/pipeline.py`): per-climate-lens `reflections[]` ({question_key,title,status_cue,text}), `less_central`, `integration_level` (well_integrated|partly_integrated|weakly_integrated|insufficient_evidence; safe `insufficient_evidence` default — no material→moderate), `integration_summary`, and separate `sensitivity_evidence`/`responsiveness_evidence`. Stage 3 priorities JSON adds top-level `wider_fcv_context` and per-priority `policy_status` + `specialist_referral` (`extract_priorities`).
  - **Output redesign:** causal-strip diagram replaced by two prose interaction boxes; new "Reflections on core climate and FCV considerations" block with soft status chips; single "How well does the project integrate climate and FCV?" gauge (reframed "Indicative Climate-FCV Integration Readout") replaces the two S/R gauges in module mode; "Wider FCV context" callout; reorder to interactions → reflections → dividends → wider-FCV. Live HTML, shared HTML, and DOCX kept in parity.
  - **OPCS compliance guardrails** (from WBG LLM review): explicit POLICY BOUNDARY (advisory only; not an ESF/ESS/ESRC determination) in prompts, UI notice, and DOCX; instrument/framework-awareness guardrail; CQ2/CQ4/CQ5 refinements (managed-risk vs new-gap; open-list vulnerability; contextual institutions); dividends never framed as requirements; cross-document consistency; two source layers (current policy vs analytical). Hybrid structured layer: `policy_status` + `specialist_referral` surfaced in exports, understated in UI.
  - **Budgets:** Stage 3 sector-lens ceiling raised 900→1200 (`PLATFORM_STAGE_BUDGETS`) to fit the richer dedicated Stage 3 prompt; `_bounded_stage3_lenses` target 890→1100, findings cap 700→900.
  - **Tests:** extended across pipeline, priorities, app-contract, package, and frontend suites + the South Sudan regression fixture. Full suite: 348 passed.
- **v9.18** - Sector-lens diagnostic recovery reliability (2026-07-22):
  - Missing or incomplete active-lens Stage 2 diagnostics trigger one dedicated Haiku recovery request. Its client has a 120-second default/read timeout, a 10-second connection timeout, and zero SDK retries.
  - Recovered output is strictly parsed, normalized, and validated against the active-lens contract before use. Express and step-by-step routes call the same recovery function and follow the same behavior.
  - Recovery failure is non-fatal to the core FCV assessment: the original diagnostic failure remains explicit in the parse-error payload, while invalid, failed, recovered, and unsuccessful recovery outcomes are logged.
- **v9.12** - Express per-stage abort budgets (branch `fix/express-stage2-timeout`, 2026-06-19):
  - **Stage 2 "BodyStreamBuffer was aborted" fix:** Express mode armed a single 10-minute frontend abort timer covering Stages 1 and 2, reset only at `stage_start:3`. A slow Stage 1 (web research on a fragile-context AF) could consume the shared budget, firing the timer mid-Stage-2 and tearing the fetch stream. `armExpressTimeout(stage)` now re-arms the abort timer at every `stage_start` with per-stage budgets (`EXPRESS_STAGE_TIMEOUTS` = S1 9m / S2 8m / S3 9m), each sitting above the backend wall-clock limits (S1 8m / S2 6m / S3 8m) so the backend stage error surfaces before the frontend tears the stream. Also removes a latent Stage 3 race where the frontend 8m budget equalled the backend 8m limit.
- **v9.13** - CERC conflict-trigger guardrail (branch `fix/cerc-violence-guardrail`, 2026-06-19):
  - **Stage 2/3 CERC guardrail:** Prompts now prohibit recommending CERC, or flagging absence of CERC readiness as a gap, for violence/conflict escalation, insecurity, armed-group activity, civil unrest, or access constraints alone.
  - **Eligible CERC framing:** CERC can be recommended only where there is a credible natural-hazard, climate, health, or economic emergency exposure and a plausible borrower emergency declaration/request pathway. The specific hazard pathway must be named.
  - **Alternative levers:** Conflict/violence-driven implementation risk should be routed to adaptive management, POM stop/go provisions, security-triggered restructuring, SORT updating, conflict-sensitive indicators, Security Management Plan, TPM/GEMS, or IPF urgent-need/condensed procedures.
  - **Knowledge-base alignment:** `FCV_INSTRUMENT_CALIBRATION`, CERC guidance, differentiated country guidance, IPF applicability checks, rapid-response guidance, and procurement-in-FCV guidance were updated to remove the previous "CERC for conflict escalation" framing and non-standard trigger workaround examples.
- **v9.14** - OPCS policy consistency: instrument-conditional vocabulary, programmatic validator, KB corrections, classification tightening, lifecycle detection, MPA governance_level (branch `feat/opcs-policy-consistency`, 2026-07-02):
  - **Workstream 1 — instrument-conditional SEA/SH & DNH vocabulary (QA Issues 1, 2, 4):** The hard-coded, unconditional "DNH Principle 9" (SEA/SH) block in `DEFAULT_PROMPTS["2"]` and the "Gender-FCV / SEA-SH Card Rule" block in `DEFAULT_PROMPTS["3"]` are now placeholders (`{dnh_seash_guidance}` / `{seash_gender_card_guidance}`) gated on `INSTRUMENT_TYPE`. Six new `background_docs.py` constants (`DNH_SEASH_IPF/PFORR/DPF`, `SEASH_GENDER_CARD_IPF/PFORR/DPF`) + selectors `get_dnh_seash_guidance()` / `get_seash_gender_card_guidance()` in `app.py`. IPF keeps ESF/ESCP/ESS2/ESS4/RF language; PforR uses ESSA Core Principle #6 + PAP + ESMS; DPF/DPO uses PSIA + Program Document + Adjustment Sequencing. The PforR/DPF variants are deliberately free of the ESF acronyms themselves (they describe the excluded instruments in plain language) so they neither seed banned vocabulary nor trip the Workstream 2 validator. Injection wired at all four design-review call sites (step-by-step S2 `.replace`, S3 `.format` kwarg; express S2 `.replace` after MPA slice, S3 `.format` kwarg — express S3 uses the kwarg, NOT a post-format `.replace`, to avoid a `KeyError` that would blank every placeholder). Impl-review prompts (`impl_2`/`impl_3`) are untouched (no placeholder → their `.format()`/`.replace()` sites are unaffected). `tests/test_vocabulary_gating.py`.
  - **Workstream 2 — programmatic vocabulary validator + silent repair:** `validate_instrument_vocabulary(output_text, instrument_type)` scans Stage 2/3 output for banned ESF/ESCP/ESS/SEP terms (PforR/DPO only) using whole-word `\b` matching (so "SEP" does not match "separate"/"September" and "ESS1" does not match "ESS10"). On a hit, `repair_vocabulary_violations()` runs one bounded non-streaming Anthropic rewrite, then a deterministic `\b`-anchored regex scrub as last resort, logging any residual server-side only (`app.logger.warning`) — never a user-facing error, per product decision. Wired into the step-by-step route (`if not is_impl and stage in (2,3)`) and both express Stage 2/3 hooks. `tests/test_vocabulary_validator.py`, `tests/test_vocabulary_repair_wiring.py`.
  - **Workstream 3 — knowledge base corrections (OPCS source audit):** `MPA_MODULE_GUIDE` no longer lists DPF as a valid MPA phase instrument (only IPF or P4R under OPS5.01-POL/DIR) and no longer states RVP-approves-all-subsequent-phases as absolute (Board referral possible for material scope/cost/PrDO changes); `AF_GUIDE` no longer names RVP as the approval level for all waivers; `P4R_MODULE_GUIDE` reframes OP 7.30 as a feasibility constraint (not a formal cross-reference), removes the "Category-A-equivalent" mislabel, and adds the Rapid Response Option (RRO, OPS5.04-POL.125 para 12); `FCV_INSTRUMENT_CALIBRATION` replaces the unverified "EDP" acronym with a verification-flagged description; `app.py` no longer presents WHR as an FCV Envelope (FCVE) allocation in the Stage 1 prompt or the `RenderSourceProvider` summary. `tests/test_knowledge_base_corrections.py`.
  - **Workstream 4 — FCV classification tightening (QA Issue 3):** Stage 1 prompt gains a geographic-footprint anchoring rule (sub-national risk factors must be checked against the project's actual implementing regions before being cited) and a mandatory one-line `trigger` field in the `%%%COUNTRY_CLASSIFICATION%%%` block; `extract_country_classification()` parses `trigger`. `tests/test_classification_tightening.py`.
  - **Workstream 5 — lifecycle detection (QA Issue 5):** Document-text-only. New `lifecycle_status` field in the `%%%TEMPORAL_CONTEXT%%%` block (`active` | `closed - <reason>` | `Unknown`); `extract_temporal_context()` parses it (defaults to `active` for legacy blocks, `Unknown` when the block is missing). Frontend `isClosedOrCompletedProject()` / `closedProjectStatusReason()` render an amber advisory banner in `renderOut()` (never a hard block), mirroring `isFinalizedPAD()`. Designed so a future WBG project-status/P-code lookup can populate the same field without a contract change. `tests/test_lifecycle_detection.py`.
  - **Workstream 6 — MPA `governance_level` field (QA Issue 6):** New Stage 3 priority field `governance_level` (`"Regional Platform"` | `"Country Phase"` | null for non-MPA) added through the full pipeline: prompt schema (21 fields), `_REQUIRED_PRIORITY_FIELDS`, `extract_priorities()` enum validation, frontend chip in `showPriority()`, and DOCX export metadata line. `tests/test_governance_level_field.py`.
  - **Deviations from the source plan (documented):** (1) Two selector-test/constant inconsistencies in the plan were reconciled by making the constants match the tests' clear intent (PforR/DPF variants stripped of raw ESF acronyms; IPF DNH test asserts `ESS2`, the acronym actually present, not `ESS4`); (2) the validator/scrub use `\b` word boundaries (plan omitted them) to prevent false-positive repairs on common words; (3) express Stage 3 wiring uses a `.format()` kwarg rather than the plan's post-MPA-slice `.replace()`, which would have raised `KeyError` and blanked all placeholders; (4) `tests/test_phase0_foundation.py` updated to reference the relocated SEA/SH risk-classification string now living in `DNH_SEASH_IPF`; (5) commits omit the `Co-Authored-By: Copilot` trailer specified in the handover, per the repo owner's standing global instruction that no AI-attribution trailer appear in any commit. Full suite: 180 passed (baseline was 140).
- **v9.2** - Classification caveat and background_docs policy corrections (branch `feat/v9-differentiated-approaches`, 2026-04-19):
  - **Classification widget caveat:** Narrative now always ends with "This is a subjective judgement on the part of this AI tool and does not constitute an official WBG classification." — consistent with Stage 1 AI disclaimer framing
  - **background_docs.py — ICR timing:** `STAGE_GUIDANCE_MAP["ICR"]["timing_options"]` corrected from `"During implementation"` to `"At project closing"`
  - **background_docs.py — Para 12 naming:** Removed all incorrect "Para 11" / "Para 11/12" references; standardised to "Paragraph 12 of Section III of the IPF Policy" with correct two-situation description (urgent need; capacity constraints); clarified Para 12 is NOT required for Framework Approach, Phased Implementation, or Unallocated Funds
- **v9.1** — UX, prompt quality, and bug fixes (branch `feat/v9-differentiated-approaches`, 2026-04-18):
  - **DOCX download fix:** `downloadReport()` now POSTs to new `/api/download-report` route; backend generates a true python-docx binary (not HTML masquerading as .docx). New helpers: `_md_to_docx_para()` (markdown→docx paragraphs), `_safe_run()` (safe runs[0] access)
  - **Stage 1 prompt — prose narrative:** Body content now required to be prose paragraphs (2–4 sentences per subsection); bullets restricted to genuinely enumerable items only
  - **Stage 1 prompt — country-specific fact flagging:** Part B must tag unverifiable country-specific claims (named institutions, legislation, political events, officials) with `[Verify: ...]` inline
  - **Stage 1 prompt — IDA FCV Envelope advisory:** For Conflict-Affected and Situations of Fragility countries, adds a brief end-of-Part-B advisory prompting TTL to discuss PRA/RECA/TAA eligibility with regional FCV coordinator (not an eligibility determination)
  - **Stage 2 prompt — Refresh shifts as qualitative lenses:** FCV Strategy 2026-2030 shifts explicitly framed as analytical lenses for strategic alignment, not a scoring checklist
  - **Stage 3 prompt — Watch List for Supervision:** "Horizon Considerations" section renamed and reframed as "Watch List for Supervision"; each item must name a specific WBG tracking vehicle (ISR risk flag, MTR agenda item, RRA update, restructuring trigger); panel heading in frontend updated to match
  - **Stage 3 priorities — `action_timing` field:** New enum field (`pre-appraisal` / `next-series` / `supervision`) with coloured pill in UI and included in DOCX download
  - **SORT guardrail:** Stage 3 prompt now prohibits prescribing specific SORT ratings; frames risk exposure as "consider whether the current rating adequately reflects X"
  - **Source credibility flagging:** Stage 1 Part B labels source type inline (`[Data: high-quality]`, `[Data: secondary]`, `[Source: news/media]`); data gap flagging for missing FCV dimensions
  - **Classification confirm button removed:** Dropdown auto-applies on change via `onchange` listener; `confirmClassification()` function deleted; act-area no longer hidden
  - **Step-by-step loading timers:** Elapsed timer and rotating stage-specific messages added; hints updated to reflect real durations (Stage 2: 3–5 min, Stage 3: 4–6 min)
  - **Paragraph spacing fix:** `.out-body p` CSS set to `margin-top: 0; margin-bottom: 0.5em` to eliminate double gaps in Stage 1 output
  - **CPF upload encouragement:** Contextual zone hint updated with bold/underlined CPF prompt; SCD removed; RRA mentioned as secondary option

---

## Repository Structure

### What's in the public GitHub repo
The repo contains only what's needed to understand, deploy, and maintain the app:
- Core app files: `app.py`, `background_docs.py`, `index.html`
- `docs/reference/` — detailed specs for prompts, routes, and frontend functions
- `docs/fcv-agent-knowledge-architecture.html` — shareable knowledge architecture diagram
- `tests/` — unit tests for priority extraction
- Deployment files: `requirements.txt`, `Procfile`, `.gitignore`, `README.md`

### What's kept locally only (not in the repo)
These folders exist on the development machine but are gitignored — do not commit them:
- `app_feedback/` — internal review documents, colleague feedback, test PDFs
- `docs/superpowers/` — implementation plans and design specs from development sessions
- `.claude/` — local Claude Code configuration
- `.superpowers/` — brainstorming session artifacts
- `AGENTS.md` — internal agent instructions
- Session handoff notes (e.g. `docs/*SESSION_HANDOFF*`) and dev mockups (`docs/mockup_*`)

---

## 1. Project Architecture

### 1.1 Tech Stack
- **Backend:** Python Flask 3.0.3 + Anthropic Claude API (Claude 5.5 generation — `claude-opus-5-5` for core Stage 2/3 reasoning, `claude-sonnet-5-5` for Stage 1 + secondary calls + the climate lens, `claude-haiku-5-5` for helpers/distillation)
- **Frontend:** HTML + vanilla JavaScript + Markdown rendering
- **Hosting:** Render.com (gunicorn + gevent)
- **Concurrency model:** Per-tab assessment IDs in the browser; Express runs emitted from a background assessment executor; multi-worker gunicorn in production
- **Document processing:** PDF (pypdf), DOCX (python-docx), PPTX (python-pptx) text extraction; all binary formats sent as base64 from browser
- **Session management:** Browser storage namespaced by per-tab assessment ID + JSON-serialized conversation history

### 1.2 Core Files
```
app.py              # Flask backend, all prompts (DEFAULT_PROMPTS), routes, document processing
index.html          # Single-page frontend UI (Stage 1–3, Go Deeper, Express mode, prompt modal)
docx_structure.py   # Shared recursive OOXML walker + structured-field extraction
background_docs.py  # 10 constants: FCV_GUIDE, FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK,
                    #   PLAYBOOK_DIAGNOSTICS, PLAYBOOK_PREPARATION, PLAYBOOK_IMPLEMENTATION,
                    #   PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP, FCS_LIST, CPF_INTEGRATION_GUIDE
                    #   + WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE, FCV_INSTRUMENT_CALIBRATION (helpers)
prompts.json        # Session-specific prompt overrides (empty by default)
requirements.txt    # Flask, anthropic, pypdf, python-docx, python-pptx, gunicorn, gevent
Procfile            # Render deployment config
```

### 1.3 Three-Stage Pipeline

**Current upload tiering:** Zone 1 accepts exactly one primary project document; Zone 2 accepts up to 10 package documents that are distilled into key-signal cards; Zone 3 accepts up to 3 contextual documents distilled into RRA driver / CPF pillar cards or generic context cards.

**Two workflow modes:** Express Analysis (default — all 3 stages run automatically via `/api/run-express`) and Step-by-Step (interactive, one stage at a time via `/api/run-stage`). Same prompts, same output quality.

**Optional sector lenses:** users may select up to two ordered lenses. Both workflows resolve authoritative module versions and inject the same bounded stage slices. Lens findings must map to existing OST/DNH/Strategy criteria; they do not add a score or separate recommendation list. The production Climate-FCV Lens is manual-only and never auto-suggested. After selection it screens climate-intent and wider development operations automatically, prioritizes adaptation, and activates deep mitigation only for a clear pathway. Core-only uses 1-5 evidence-led material priorities and retains the lightweight Climate-FCV check; active Climate supersedes that check and uses no more than five substantive priorities with a flexible evidence-led mix. `lens_context_sources` persists optional validated Climate research and World Bank CCDR sources without making CCDR material a routine recommendation.

**Climate-active dual-use contract (implemented on `codex/climate-fcv-output-redesign`):** Stage 1 runs reduced core research and one dedicated bounded trusted-source Climate pass concurrently, with one narrower retry. Stage 2 requires both directional interaction pathways with stable IDs, project/place/group/system anchors, causal steps, confidence, evidence gaps or research claim IDs, and current/project/asset-system horizons. Stage 3 retains both causal directions inside the 900-token lens ceiling and validates `climate_links` on every priority as either `linked` to recognized interaction/dividend/finding IDs or `no-material-pathway` with a concrete reason. Live HTML, shared HTML, and DOCX use the same narrative interactions, causal strips, qualitative dividend synthesis, and priority contribution panels. See `docs/20260723_climate_fcv_output_redesign_handoff.md`.

**Bounded Climate evidence handoff:** Sonnet performs two targeted web searches. If structuring is needed, Haiku continues the original native search messages, including encrypted result blocks, with further tool use disabled. No extra call is added. Fresh claims require a short source_excerpt matching a provider cited passage at the declared trusted source URL; downstream claim text is that passage, preserving measured quantities and qualifiers. Citation-split JSON text is joined without injected newlines. Missing matching passages fail the evidence gate; source metadata alone is insufficient. See the sector-lens reference for bounds and remaining acceptance limits.

```
STAGE 1 — Context & Extraction
├─ Input: appraisal/design-stage project doc (PCN/PID/PAD/AF/Restructuring; instrument type IPF/PforR/DPO/TA/MPA/IPF-DDO; regional ops supported) + optional contextual docs
├─ Automated web research: extract_country_name() + extract_sector_name() → bounded core brief
│  (cached by "country::sector::ccdr=<0|1>"; Climate-active runs add concurrent validated ClimateResearchBundle research)
├─ Three-tier citation: Tier 1 uploaded docs → Tier 2 web research → Tier 3 training knowledge
├─ Output: 2–3 sentence narrative lead (required) then PROSE PARAGRAPHS (not bullets) — for EACH of:
│    Part A (doc extract only) and Part B (contextualized, tiered citations)
│    Bullets restricted to genuinely enumerable items only (named locations, dates, prior actions)
├─ Country-specific fact flagging: Part B tags unverifiable claims (named institutions, legislation,
│    political events, officials) inline with [Verify: ...]; claims from uploaded docs are exempt
├─ IDA FCV Envelope advisory: for Conflict-Affected and Situations of Fragility countries, end-of-
│    Part-B advisory prompts TTL to discuss PRA/RECA/TAA eligibility with regional FCV coordinator
│    (not a determination — coexists with existing eligibility guardrail)
├─ Frontend: renderStage1() parses Part A/B split; renders with styled section badges
│  (blue "From your document only" / green "Wider context & research"); narrative lead
│  styled as tinted callout above bullets
├─ Classifier lines (stripped from display by clean_stage1_output(); kept in history):
│  %%%DOC_TYPE: [PCN/PID/PAD/AF/Restructuring/ISR/Unknown]%%%
│  %%%INSTRUMENT_TYPE: [IPF/PforR/DPO/TA/MPA/IPF-DDO/Unknown]%%%
│  %%%TEMPORAL_CONTEXT_START%%%...%%%TEMPORAL_CONTEXT_END%%% → approval_date, closing_date,
│    safeguards_framework, other_temporal_markers
│  (parsed by frontend; passed to Stage 2/3 requests as instrument_type, temporal_context)
├─ Large docs: >150k chars → LLM condensation; >500k chars → truncation
└─ Prompt constants: FCV_GUIDE, PLAYBOOK_DIAGNOSTICS, FCV_REFRESH_FRAMEWORK, FCS_LIST

STAGE 2 — FCV Assessment
├─ Input: Stage 1 output (conversation history)
├─ Internal engine: 12 OST recs + 25 key questions + 3 key elements (TTL sees themes, not framework)
├─ TTL-facing output (400–500 words): 3–5 dynamic themes → DNH traffic-light → S/R synthesis
│  → Sensitivity + Responsiveness ratings → 3–5 key gaps
├─ Delimiter blocks (stripped from display, parsed to frontend):
│  %%%STAGE2_RATINGS_START/END%%% → {sensitivity_rating, responsiveness_rating}
│  %%%RATING_REASONING_START/END%%% → reasoning block (auditing only)
│  %%%UNDER_HOOD_START/END%%% → 4 sub-blocks:
│    %%%RECS_TABLE_START/END%%%    — 12-rec table with S/R Tag column
│    %%%DNH_CHECKLIST_START/END%%% — 9-principle DNH checklist (principle 9 = SEA/SH)
│    %%%QUESTIONS_MAP_START/END%%% — 25 key questions with findings
│    %%%EVIDENCE_TRAIL_START/END%%% — sources and citation tiers
├─ Under Hood text kept in memory and best-effort localStorage "stage2_under_hood" → used by Go Deeper Tab 1
├─ Rating rubric: Sensitivity = OST recs % addressed → 6-tier (percentage-based, partial credit
│  for Weakly addressed, quality gates apply); Responsiveness = FCV Strategy 2026-2030 pillars count → 6-tier
│  Stage 3 inherits Stage 2 ratings verbatim — no independent re-rating
├─ SEA/SH flag: seash_standalone_flag: TRUE → mandatory SEA/SH priority card in Stage 3
├─ Gender flag: gender_fcv_flag: TRUE (any of 7 trigger conditions) → mandatory gender card
└─ Prompt constants: FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK, FCV_GUIDE, FCS_LIST

STAGE 3 — Recommendations Note (stage-aware)
├─ Input: Stages 1–2 history + doc_type + uploaded_doc_names
├─ Stage-awareness: PCN/PID → PLAYBOOK_PREPARATION; PAD → PLAYBOOK_PREPARATION;
│  AF/Restructuring → PLAYBOOK_IMPLEMENTATION; ISR → PLAYBOOK_IMPLEMENTATION+CLOSING
├─ Temporal guardrail: _build_temporal_guardrail(temporal_ctx, doc_type) — for design-stage
│  docs (PAD/PCN/PID/AF/Restructuring), always returns preparation-phase framing regardless
│  of whether approval date is in the past. Prevents implementation-review hallucination.
├─ Finalized PAD notice: isFinalizedPAD() detects PAD with past approval date → amber
│  retrospective banner injected in output and downloaded report
├─ Instrument routing guardrail: per-doc-type constraints injected into prompt
├─ PAD minimum instrument reference set: SORT, ESS1, SEA/SH AP, SEP/ESS10, ESCP, OM, PPSD, RF
├─ Output: narrative memo + %%%JSON_START%%%...%%%JSON_END%%% block
│  JSON top-level: fcv_rating, fcv_responsiveness_rating, sensitivity_summary,
│    responsiveness_summary, risk_exposure {risks_to, risks_from}, priorities[]
│  Each priority: title, fcv_dimension, tag, refresh_shift, action_timing, risk_level, the_gap,
│    why_it_matters, actions[] (document_element + guidance + suggested_language),
│    who_acts, when, resources, pad_sections, implementation_note,
│    cpf_alignment (null if no CPF uploaded; string linking to CPF outcome if CPF present)
│    action_timing: flag-for-preparation | required-before-appraisal | required-before-board | next-series | supervision — rendered as coloured pill
├─ Watch List for Supervision: final section (replaces "Horizon Considerations"); each item names
│    a specific WBG tracking vehicle (ISR risk flag, MTR agenda item, RRA update, restructuring
│    trigger); items without a named vehicle excluded; framed as risks to monitor, not act on now
├─ SORT guardrail: prompt prohibits prescribing specific SORT ratings; frames risk exposure as
│    "consider whether current rating adequately reflects X"
├─ clean_stage3_output(): strips JSON block, risk narrative, and everything from
│  %%%PRIORITIES_START%%% onwards — all shown as cards from JSON
├─ Citation policy: ONLY cite docs from Stage 1 [From: name]. Never fabricate titles.
└─ Prompt constants: stage-appropriate PLAYBOOK + FCV_REFRESH_FRAMEWORK + CPF_INTEGRATION_GUIDE

FOLLOW-ON (Stage 3 bottom card)
├─ POST /api/run-followon — full history + user message → SSE response appended below card
└─ 4 pre-fill chips: "Draft peer review note" / "Expand top recommendation" /
   "Review my revised text" / "Summarise for brief"

GO DEEPER (per-priority, Stage 3 only — 2 tabs)
├─ Tab 1 (Evidence trail): DEFAULT. No API call — filters in-memory Stage 2 Under Hood data,
│  falling back to localStorage.stage2_under_hood when available; renders instantly
└─ Tab 2 (FCV Playbook): SSE call to /api/run-deeper?tab=playbook_refs
   Cache keys: deeper_{idx}_trail, deeper_{idx}_playbook
```

> **Full prompt schemas, delimiter formats, and parsing function signatures:**
> → `docs/reference/reference_prompt_architecture.md`

---

## 2. Design Decisions & Philosophy

### 2.1 Why 3 Stages?
- Sequential refinement: users pause, review, and correct at each step
- Old Stages 2 (Screening) and 3 (Gaps) were duplicative — merged into a single Assessment stage
- Fewer stages = cleaner TTL workflow without losing quality

### 2.2 Why Part A / Part B Split in Stage 1?
- Transparency: users see what came from their doc vs. external context
- Accuracy accountability: Part A errors = extraction issue; Part B errors = contextual interpretation issue

### 2.3 Why "Go Deeper" (2-tab panel)?
- Tab 1 (Evidence trail): No API call — uses Stage 2 Under the Hood data already in localStorage. Instant.
- Tab 2 (FCV Playbook): Lightweight LLM call for operational tools, WBG teams, policy hooks.
- "Other options" (alternatives) tab removed in v7.2 — rarely used, added cognitive load.
- Core recommendation is self-contained in JSON. Go Deeper is optional depth. Download never needs it.

### 2.4 Specificity Mandate
Recommendations must name geography, mechanism, and entry points — not broad policy suggestions.
- **Bad:** "Service delivery needs to be targeted so it doesn't contribute to grievance"
- **Good:** "In Nzerekore, Kindia, and Kankan — historically excluded — focus service delivery via community health extension workers and cash-for-work entry points"

Enforced via: full 12-rec OST engine in Stage 2; geographic/mechanism requirements in Stage 3 prompt; `_check_specificity()` in `extract_priorities()`.

### 2.5 Session Persistence
All inputs and outputs stored in browser localStorage as JSON. Passed to each stage for full context.
Limitation: browser-specific, not suitable for team collaboration or long-term archival.

---

## 3. Prompt Architecture

### 3.1 Where Prompts Live

Verified Climate uses sector_lenses/climate_verified_prompts.py. All six stages
share sensitivity/dividend calibration, commitment-status preservation and the
current review date. Historical estimated approval dates do not establish current
status. Source-proof and prompt versions are recorded in the sector-lens reference.

```python
# app.py — top-level DEFAULT_PROMPTS dictionary
DEFAULT_PROMPTS = {
    "1": "...",               # Stage 1: Context & Extraction
    "2": "...",               # Stage 2: FCV Assessment
    "3": "...",               # Stage 3: Recommendations Note
    "deeper": "...",          # Legacy alternatives tab (retained for backwards compat)
    "deeper_playbook": "...", # Go Deeper Tab 2: FCV Playbook
    "followon": "..."         # Follow-on post-analysis tasks
}
# Go Deeper Tab 1 (Evidence trail) has NO prompt — frontend-only filter from localStorage
```

**Session overrides:** stored in `prompts.json`, loaded via `load_prompts()`, merged with defaults.
**To override:** Admin modal → stage selector → edit → Save & Close (session-scoped only).
**To persist globally:** edit `DEFAULT_PROMPTS` in `app.py`.
**Note:** `deeper_playbook` is not exposed in the Admin modal — edit directly in `app.py`.

### 3.2 Per-Stage Prompt Summary

Standard core-only runs append project-fact/materiality context in Stages 1 and 2. Stage 3 removes fixed priority and document-reference quotas while retaining conditional instrument/safeguarding checks, then embeds the shorter management readout schema. Specialist prompts bypass these changes. The concise layer is generated in the existing call and does not change rating semantics.

| Stage | Input | Key outputs | Prompt constants |
|---|---|---|---|
| 1 | Project doc + optional context | Part A (extract) + Part B (contextualised) + DOC_TYPE line | FCV_GUIDE, PLAYBOOK_DIAGNOSTICS, FCV_REFRESH_FRAMEWORK |
| 2 | Stage 1 history | Thematic narrative + ratings + Under the Hood delimiter blocks | FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK, FCV_GUIDE |
| 3 | Stages 1–2 history + doc_type | Narrative memo + JSON priorities block | Stage-appropriate PLAYBOOK + FCV_REFRESH_FRAMEWORK |

> **Full per-stage specs, JSON schemas, and delimiter formats:**
> → `docs/reference/reference_prompt_architecture.md`

### 3.3 Key Modification Workflows

**Change a prompt:** Admin modal (session-scoped) or edit `DEFAULT_PROMPTS` in `app.py` (global).

**Change the 6 FCV dimensions:**
1. Edit Stage 2 prompt in `DEFAULT_PROMPTS`
2. Update Stage 3 prompt to reference same dimensions (fcv_dimension must match for Go Deeper trail filtering)

**Change Stage 3 priority fields:**
1. Update JSON schema in `DEFAULT_PROMPTS["3"]`
2. Update `extract_priorities()` in `app.py`
3. Update `showPriority()` in `index.html`
4. Update `downloadReport()` if field should appear in export

**Change the 4 FCV Strategy 2026-2030 pillars:**
1. Edit `FCV_REFRESH_FRAMEWORK` in `background_docs.py`
2. Update Stage 2 and Stage 3 prompts
3. Update `extract_priorities()` shift validation list
4. Update `refresh_shift` badge rendering in `showPriority()`

---

## 4. Frontend Architecture

### 4.1 UI Panels
1. **Onboarding modal** — AI disclaimer + checkbox to suppress on future visits
2. **Session bar** — stage progress + save session button (hides "No active session" on initial load)
3. **Stage progress stepper** — 3-step: Context → Assessment → Recommendations
4. **Input panel (Stages 1–2)** — file upload zone, document list, refine input
5. **Output panel (Stages 1–3)** — LLM output + collapsible sections
6. **Under the Hood panels (Stage 2)** — 4 expandable `<details>`:
   - Panel 1: "How well does the project integrate FCV considerations?" (12 OST recs, S/R Tag column)
   - Panel 2: "Could this project unintentionally cause harm?" (9 DNH principles)
   - Panel 3: "What did we look for — and what was missing?" (25 diagnostic questions)
   - Panel 4: "Where did this analysis come from?" (sources, tiers, contributions)
7. **Ratings sidebar (Stage 2+)** — Sensitivity gauge (blue, shield) + Responsiveness gauge (green, leaf)
8. **Go Deeper panel (Stage 3)** — Per-priority `<details class="go-deeper">` with 2 tab buttons
9. **Prompt modal** — Admin-only: view/edit prompts per session

### 4.2 Styling
- **Colours:** WB palette — wb-blue (#009FDA), wb-navy (#002244), wb-gray-900 (#111827), wb-gray-50 (#F7F8FA), wb-gray-100 (#EEF0F3). RAG: red (#D73027), amber (#FFFFBF), green (#1A9850). Full reference: `memory/reference_wb_design_system.md`
- **Typography:** Open Sans, 14px/400 body, 15px/700 section headings, 10px/600 labels
- **Spacing:** 4px base unit; xs=4, sm=8, md=16, lg=24, xl=32
- **Cards:** border-radius 8px, box-shadow 0 1px 3px rgba(0,0,0,0.08)
- **Font consistency:** `.pc-zone-body` and `.out-body` both 14px — do not let these diverge

### 4.3 Do No Harm Rendering
- **Stage 2 inline:** traffic-light summary, e.g., "Do No Harm: 6 of 9 addressed | 1 partial | 1 gap"
- **Stage 2 Under the Hood Panel 2:** full 9-principle table with evidence (from `%%%DNH_CHECKLIST_START/END%%%`)
- DNH is NOT shown as a standalone checklist in Stage 3

> **Full JS function list, Express mode functions, and removed items:**
> → `docs/reference/reference_frontend_functions.md`

---

## 5. Backend Routes & API

### 5.1 Route Summary

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/run-stage` | Core analysis (Stages 1–3, step-by-step) |
| POST | `/api/run-express` | Express mode (all 3 stages, single SSE) |
| POST | `/api/run-deeper` | Go Deeper tab content |
| POST | `/api/run-followon` | Follow-on post-analysis queries |
| POST | `/api/download-report` | Generate true DOCX binary via python-docx |
| GET | `/api/sector-lenses` | Return enabled sector-lens selector catalogue |
| GET | `/api/default-prompts` | Return current DEFAULT_PROMPTS dict |
| GET | `/` | Main app |
| GET | `/health` | Health check |

### 5.2 Key Constants & Limits

```python
MAX_DOC_CHARS = 500_000        # Hard cap on chars extracted from any single document
STAGE1_MAX_DOC_CHARS = 60_000  # Primary doc truncated to this before Stage 1
CARD_CHARS_2A = 2_800          # Structured secondary package card cap in fcv_distillation.py
CARD_CHARS_2B = 1_200          # Generic secondary package card cap in fcv_distillation.py
CARD_CHARS_CONTEXT = 1_800     # Context card cap in fcv_distillation.py
MAX_UPLOAD_MB = 100            # Max request body (base64 upload JSON); env MAX_UPLOAD_MB; drives MAX_CONTENT_LENGTH; published to the frontend via /api/sector-lenses
PROMPTS_FILE = 'prompts.json'
```

### 5.3 Priority Parsing (`extract_priorities()`)

Standard concise admission accepts 40-200-word overviews, zero to three strengths and one to four concise actions for backward compatibility; new generation targets 80-110 words and one to two actions. Admission remains atomic across the readout and all priorities, with grounding and lifecycle checks retained. Standard results require 1-5 priorities and reject excess priorities rather than silently truncating them. `/api/download-management-brief` reuses canonical admission before calling `fcv_management_brief.py`; active lenses are not supported by this endpoint.

Optional sector provenance is normalized as `lens_ids: string[]` and `lens_relevance: string`. These fields decorate affected priorities only and never define an additional score or recommendation list.

Finds `%%%JSON_START%%%...%%%JSON_END%%%`, parses via `json.loads()`, validates field values, runs `_check_specificity()` and `_check_citations()`, returns unified dict. On malformed JSON: `{error: True, message: ...}` — NOT silent failure.

### 5.4 Stage 2 Parsing

- `extract_stage2_ratings()` → `{sensitivity_rating, responsiveness_rating, rating_reasoning}`
- `extract_under_hood()` → `{recs_table, dnh_checklist, questions_map, evidence_trail}`
- `clean_stage2_output()` — strips all delimiter blocks from display text
- On `extract_under_hood()` failure: `parse_error: true` in SSE event; yellow banner shown; Stage 3 still proceeds

> **Full route specs, SSE event shapes, parsing function signatures:**
> → `docs/reference/reference_backend_routes.md`

---

## 6. Key Implementation Details

### 6.1 SSE Streaming
All stage and Go Deeper requests use Server-Sent Events. Frontend renders text progressively. Session history preserved even if a stream fails mid-way.

Core stage streams use `_stream_stage()`, which runs the Anthropic stream in a background thread, sends keepalive events every 20 seconds during quiet periods, and enforces backend wall-clock limits: Stage 1 = 8 minutes, Stage 2 = 9 minutes, Stage 3 = 9 minutes. If the provider stream stays open without completing, the backend returns a stage error rather than keeping the Render request alive indefinitely. Stage 1 secondary-document distillation also emits preprocessing progress/keepalive events while slower package/context documents are pending, before the model stream opens.

### 6.2 Conversation History
History passed to each stage so the LLM maintains context. Stored in localStorage. Allows session recovery on page reload.

**Compact-label pattern (critical for performance):** Each stage stores a compact user label in `conversation_history` instead of the full prompt with injected background constants. The full prompt is used for the API call but is replaced with a label like `"[Stage 2 — analysis prompt with operational guidance injected]"` before being saved to history. This prevents 80k+ chars of background docs from accumulating in the Stage 3 (and follow-on) API call inputs, which would otherwise cause slow time-to-first-token and risk hitting Render's 10-minute proxy timeout. Stage 1 has always done this; Stages 2 and 3 were updated in v8.2. Each stage re-injects its own fresh background docs — the assistant outputs are what matters for continuity.

### 6.3 Under the Hood → Go Deeper Flow
Stage 2 emits `%%%UNDER_HOOD_START/END%%%` delimiter block. After Stage 2 completes, the frontend keeps this data in memory and attempts to persist it in `localStorage.stage2_under_hood`. Persistence is best-effort: `static/fcv_storage.js` prunes stale large FCV cache entries and returns `false` instead of throwing if the browser quota is still exceeded. Go Deeper Tab 1 (Evidence trail) reads the in-memory value first and falls back to localStorage, so a storage quota failure must not fail Stage 2 or block the current run.

### 6.4 Priority JSON Parsing
`extract_priorities()` uses `json.loads()` on the `%%%JSON_START/END%%%` block. No regex field extraction. Validates all field value sets. Runs specificity check (proper-noun proxy) and citation check (against uploaded doc names + org whitelist).

### 6.5 UX Safeguards
- **S/R tag tooltips:** `renderSRTagBadge()` adds `title` attribute explaining [S]/[R]/[S+R]
- **Specificity warning:** amber badge if `priority.specificity_warning === true`
- **Citation warning:** amber badge if `priority.citation_warnings.length > 0`
- **Under the Hood parse error banner:** yellow banner if `extract_under_hood()` fails; raw text shown as fallback
- **Stage consistency banner:** yellow banner at Stage 3 if Stage 2 was re-run after Stage 3

---

## 7. Common Workflows

### Changing a Prompt
- **Session only:** Admin modal → stage → edit → Save & Close
- **Globally:** Edit `DEFAULT_PROMPTS` in `app.py`

### Adding a Field to Stage 3 Priorities
1. Update JSON schema in `DEFAULT_PROMPTS["3"]`
2. Update `extract_priorities()` in `app.py`
3. Update `showPriority()` in `index.html`
4. Update `downloadReport()` if needed in `index.html`

### Adding a 4th Stage
1. Add key to `DEFAULT_PROMPTS`
2. Add case in `/api/run-stage` stage switch
3. Add stage card + input panel to `index.html`
4. Update stepper to show 1-of-4

### Questions to Ask Before Any Change
1. What problem does this solve? Is it a real user pain point?
2. How does this affect other stages? (Stage 2 changes → Stage 3 prompt? Go Deeper trail filtering?)
3. Does this add complexity without clear benefit?
4. How do I test it? What does a "good" outcome look like?
5. Who is the user — TTL, FCV CC, or both?

---

## 8. Deployment

### Local
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="..."
python3 app.py   # http://localhost:5000
```

### Render.com
- Connect GitHub repo → Render reads `Procfile` + `requirements.txt`
- **Production server:** gunicorn + gevent via the `wsgi:app` entry point (runs `gevent.monkey.patch_all()` before importing the app, so the worker does not block on SSL and trip WORKER TIMEOUT); `--worker-class gevent --workers 1 --timeout 1200` — required for long-running SSE
- **Env vars:** `ANTHROPIC_API_KEY` (required); `MAX_UPLOAD_MB` (optional, default 100) — max accepted upload request body in MB; tune to the Render instance RAM
- Auto-deploys on push/merge to connected branch

### Render service separation (mandatory)

- **ITS/stable service:** `https://fcv-agent.onrender.com` must remain connected to `main`. ITS colleagues use this service. Never repoint it to a feature branch or use it for branch testing.
- **Branch-testing service:** `https://fcv-agent-1.onrender.com` is the only Render service to use for feature-branch and Climate-FCV testing. Point this service at the branch under test.
- Before any live test, verify the linked branch in the Render service header and verify the deployed build through `/health` where supported. Do not infer the deployed branch from page content alone.
- Keep service-specific build commands separate. Stable `main` uses `pip install -r requirements.txt`; the Climate-FCV testing branch may use `python render_build.py` because that branch carries the companion-bank build helper. Do not copy the testing service's build command onto the stable service.

### Cost-controlled live testing (mandatory)

Use the same verified Climate-FCV architecture in two passes:

1. **Smoke pass first:** set `CLIMATE_VERIFIED_RUN_MODE=smoke` on the branch-testing service. This uses the cheap model profile and tests upload, extraction, country-bank loading, stage completion, schema parsing, validation, rendering, and export. Smoke output is for workflow verification only and must not be treated as an analytical quality benchmark.
2. **Quality pass only after smoke passes:** set `CLIMATE_VERIFIED_RUN_MODE=quality` and run the minimum representative case needed to assess analytical accuracy, relevance, coherence, and TTL utility. Avoid repeated quality reruns while deterministic or integration defects remain.

Never run either pass against the ITS/stable service. If a quality run exposes a deterministic failure, reproduce and fix it through tests or the smoke profile before paying for another quality run.

### GitHub Security & Branch Workflow
- `main` is protected: changes go through pull requests. No approving review is currently required (`required_approving_review_count: 0`), so PRs can be merged programmatically (e.g. `gh pr merge`); open review conversations must still be resolved first, and protection applies to admins.
- Branch protection dismisses stale approvals, requires conversation resolution, applies to admins, and blocks force pushes and branch deletion.
- GitHub Advanced Security features enabled for this public repo: Dependabot vulnerability alerts, Dependabot security updates, secret scanning, and push protection.
- `.github/dependabot.yml` schedules weekly dependency update checks for Python (`requirements.txt`) and GitHub Actions.
- `.github/workflows/codeql.yml` runs CodeQL Python analysis on PRs to `main`, pushes to `main`, and weekly on Monday.
- After the first CodeQL run is stable on `main`, consider adding the CodeQL check as a required status check in branch protection.

---

### Current branch live-acceptance workflow

Use the standard public fixture at
`test_documents/live_acceptance/somalia-stairp-p513127-concept-pid-20260207.pdf`.
Use the dated current handoff for Smoke and Preview service URLs because branch-test
services can be repointed. Run Smoke first, then Preview quality, and never use the
ITS/stable service for feature acceptance. Verify branch and deployed SHA each time.

Before upload, verify the service is connected to the intended branch and that the
live deploy SHA matches the local/remote branch head. Wake the service and wait for
stable upload controls after cold start. During long manual gaps, keep a separate
service page or browser context active and refresh it periodically; the August 2026
preview services were observed heading toward dormancy after roughly eight idle
minutes even though the assessment itself may take fifteen minutes or more.

Use one complete document for both runs. Capture the `assessment_id`, Summary
screenshot, Detailed browser HTML, standalone detailed HTML, DOCX, and raw stage
responses. Filter Render logs by assessment ID and verify each stage's HTTP result
and timestamps. A cold-start navigation race, frontend abort, backend `TimeoutError`,
413 upload rejection, gateway 502/503, and worker OOM/restart are different failure
classes and must not be treated as one generic timeout.

### Timeout and build invariants

- Frontend abort budgets must remain strictly greater than backend stage caps; both
  must remain below the gunicorn/hosting request limit.
- Do not introduce blocking non-streaming work after a stream goes quiet. Long
  preprocessing and inter-stage work must emit progress or keepalives.
- Preserve compact conversation-history labels so Stage 3 does not carry prior full
  injected prompts.
- Core Stage 3 structured JSON is emitted before the narrative. Long trailing JSON
  was omitted stochastically even when visible prose completed.
- Render builds on this branch must run `python render_build.py` so the pinned
  Climate-FCV bank submodule is initialized before dependencies are installed.
- Before local full-suite verification, run `git submodule sync --recursive` and
  `git submodule update --init --recursive`. Missing bank files produce legitimate
  `bank_missing` results and should be diagnosed as checkout setup first.

### Summary implementation invariants

- Apply the core concise schema only when no specialist lens is active.
- Escape literal JSON braces only in templates that still await Python `.format(...)`.
  Keep normal single braces in schema constants injected afterwards by
  `_embed_core_concise_stage3_schema()`. Test the final rendered prompt, not only
  the template source.
- Admit Summary atomically: readout plus every ranked priority's concise object.
- Restore readout, priorities, sensitivity rating, and responsiveness rating before
  applying the Summary capability gate.
- Management brief downloads are separate and use the normalized concise projection.
- Keep `downloadReport()` and `downloadHTML()` independent of Summary renderers,
  advisory copy, and accordion state.
- Inspect every priority in raw Stage 3 output during live acceptance. A valid top
  readout with partial concise priorities is a failed Summary bundle.
- Treat pipeline completeness and analytical grounding as separate quality gates.
  Dated live-research assertions not supported by the uploaded document must be
  verified before sharing.

## 9. Safety & Output Handling

Stage 3 outputs are prepended with an AI disclaimer header (`DO_NO_HARM_HEADER` constant in `app.py`) making clear this is LLM-assisted output for review only, not a substitute for professional FCV analysis.

Citation hallucination guard: Stage 3 prompt explicitly prohibits fabricating document citations. If Stage 3 prompt is modified, ensure this guard is preserved.

---

## 10. Known Limitations

- **localStorage scope:** Browser-specific; no team sharing or long-term archival
- **Rate limiting:** LLM calls are not rate-limited; high-volume use could hit API throttles
- **Large documents:** >500k chars truncated; very large projects may lose nuance. Scanned/image-only PDFs extract to near-zero text — a warning is shown but analysis still runs.
- **DOCX/PPTX:** Modern formats only (.docx, .pptx). Legacy binary formats (.doc, .ppt) are not supported.
- **Research cache:** In-process memory; lost on server restart
- **Mobile:** Desktop-optimized; mobile experience limited

---

## 11. Why These Decisions?

| Decision | Reason |
|---|---|
| Opus 5.5 (core Stage 2/3) + Sonnet 5.5 (Stage 1 / secondary / climate lens) | Opus for the reasoning-heavy assessment and recommendations; Sonnet for fast, low-cost long-context extraction, secondary calls, and the fragile climate pipeline; both 1M-token context |
| Flask (not React) | Lightweight; direct LLM integration; vanilla JS sufficient; easy Render deploy |
| SSE streaming | Real-time feedback; no polling overhead; better UX |
| localStorage sessions | Quick to implement; no database needed; works offline |
| Delimiter + JSON parsing | Reliable extraction; allows LLM to generate prose around structured data; easy to extend |
| 3 stages (not 4 or 1) | Sequential refinement; old Stages 2+3 were duplicative; merged for cleaner workflow |

---

## 12. Testing Checklist

**Per run, check:**
- [ ] Stage 1 Part A extracts from doc only; Part B uses correct citation tiers
- [ ] Stage 2 Assessment is thematic and uses FCV Strategy 2026-2030 framing (not old pillars)
- [ ] Stage 2 Under the Hood panels parse correctly (12-rec table, DNH, questions, evidence)
- [ ] Stage 2 gauges animate; ratings are plausible
- [ ] Stage 3 priorities include geographic callouts and `refresh_shift` badges
- [ ] Stage 3 lifecycle framing matches doc type (PCN vs PAD framing)
- [ ] Go Deeper Trail tab renders instantly from Stage 2 data
- [ ] Go Deeper Playbook tab loads relevant guidance
- [ ] Follow-on card works with at least 2 pre-fill chips

**Prompt quality checks:**
- Are recommendations specific (geography, mechanism, entry points)?
- Are they evidence-based (grounded in uploaded docs)?
- Does the Stage 2 Assessment correctly apply 4 FCV Strategy 2026-2030 pillars (not old pillars)?

---

## 13. Debugging

| Symptom | Check |
|---|---|
| Stage 1 hangs on large PDF | LLM summarizing (expected, 30–60s). Check `MAX_DOC_CHARS`. |
| DOCX/PPTX shows "could not extract" | Check python-docx/python-pptx are installed (`pip install -r requirements.txt`). Only .docx/.pptx supported — not .doc/.ppt. |
| Scanned PDF shows blank Stage 1 | Expected — extraction warning banner shown. User should upload a text-based version. |
| Stage 2 ratings seem off | Review via Admin modal; refine Stage 2 prompt and re-run |
| Under the Hood panels missing | Look for `%%%UNDER_HOOD_START%%%` in Stage 2 output; check for yellow parse error banner |
| Go Deeper Trail shows nothing | Check `localStorage.stage2_under_hood` has content; verify `priority.fcv_dimension` matches dimension in recs table |
| Stage 1 fails around 9 minutes with timeout/server message | Check frontend timeout handling first: custom abort reasons should show the stage timeout, not `Could not reach the server`. In Render logs, inspect `Stage 1 preprocessing start` and `Stage 1 extraction complete` timing, then search for `SIGKILL` / out-of-memory if the stream dies before logs complete. |
| Stage 3 loading runs indefinitely | Check for backend timeout errors from `_stream_stage()` and confirm `STAGE_STREAM_TIMEOUTS[3]` is active. If it repeats, inspect Stage 3 prompt size and Stage 1/2 history payloads. |
| Stage 3 missing `refresh_shift` | Check `DEFAULT_PROMPTS["3"]` includes `refresh_shift` in JSON schema |

**Debug steps:**
1. Browser console (F12) for JS errors
2. Flask server logs (Render dashboard) for backend errors
3. Admin modal to inspect exact prompt used for a stage

---

## 15. File Structure

```
FCV-AGENT/
├── app.py                        # Flask backend + DEFAULT_PROMPTS + all routes
├── index.html                    # Single-page frontend (~4000+ lines)
├── background_docs.py            # Knowledge base constants (10 background doc strings)
├── prompts.json                  # Session-specific prompt overrides (empty by default)
├── requirements.txt
├── Procfile
├── .github/
│   ├── dependabot.yml            # Weekly dependency update configuration
│   └── workflows/
│       └── codeql.yml            # CodeQL Python security scanning
├── README.md                     # Deployment guide for IT
├── CLAUDE.md                     # This file — developer reference
├── docs/
│   ├── reference/
│   │   ├── reference_prompt_architecture.md   # Detailed prompt specs + delimiter schemas
│   │   ├── reference_frontend_functions.md    # JS function list + Express mode
│   │   └── reference_backend_routes.md        # Routes + SSE shapes + parsing signatures
│   └── fcv-agent-knowledge-architecture.html  # Shareable knowledge pipeline diagram
└── tests/
    ├── __init__.py
    └── test_extract_priorities.py
```

Local-only (gitignored — see `.gitignore` and the Repository Structure section above):
```
app_feedback/      # Internal feedback documents
docs/superpowers/  # Dev plans and specs
.claude/           # Local Claude Code config
.superpowers/      # Brainstorming session artifacts
```

---

**Last updated:** 2026-10-12
**Current version:** FCV Project Screener v9.42
**Claude models:** `claude-opus-5-5` (core Stage 2/3), `claude-sonnet-5-5` (Stage 1 + secondary + climate lens), `claude-haiku-5-5` (helpers)
**Stack:** Flask 3.0.3 + vanilla JS + Anthropic SDK + gunicorn/gevent on Render

### Word presentation and evidence retention follow-up (2026-09-20)

`fcv_presentation.py` supplies pure first-sentence and punctuation helpers. `fcv_word_style.py` provides dependency-free shared presentation for brief, comprehensive standard and verified Climate Word exports: Arial, navy running headers and headings, readable action accents, repeating table headings and native page numbers. It preserves content and existing page geometry. Standard Stage 1 explicitly retains component budgets, beneficiaries, instrument status and conditional safeguards in a compact sourced facts table, including conflicting source statements. Standard Stage 3 concise lifecycle metadata must be copied exactly from its canonical priority; admission rules are unchanged.

Standard Stage 2 replaces the legacy SORT benchmark subsection with evidence-based project-specific calibration before adding the standard context contract. The unsupported FCS percentage/category floors are removed from the composed standard prompt; specialist prompts remain unchanged. Specific SEA/SH risk ratings cannot be inferred from overall E&S/SORT ratings, and later evidence must not be attributed to historical preparation.

### Management readability follow-up

The current standard Summary and management exports follow overall assessment,
green strengths, light-orange potential gaps, then action-focused priorities.
Optional grounded `concise.gap` supports the gap paragraph; legacy cards can use
admitted `why`. New generation targets a fuller 1.5-2-page management brief.
Shared Word presentation follows the user's global report rules: Arial, bold
opening sentences and no em dashes. Reader-only routing metadata, differentiated-
approach notes and applied-Playbook attribution are removed, including mobile.
Internal routing/retrieval and genuine unresolved-analysis warnings remain.
The handover records the required fresh live PAD rerun and output artifacts.

### Final Nairobi readability verification (20 September 2026)

A fresh complete Honduras PAD assessment completed all three stages. After small display/admission fixes, its exact recorded output passed the full live UI/export repeat. The actual management brief is two A4 pages and the comprehensive note is twelve. Saved-session recovery is fixed. Regression coverage is 1,279 cases across partitions and targeted reruns, with four legacy Windows Chromium cases still unverified. Remaining factual/status issues are documented separately; the diagnostic output is not analytically approved. See `20260920_ITS_handover_standard_fcv.md` for contracts, provenance and acceptance limits.


## 2026-09-21 Detailed technical content restoration

Standard Stage 3 retains the pre-September 20 document-focused action instructions:
2-4 substantive actions where supported, 2-4-sentence guidance and 2-3-sentence
suggested drafting. Detailed strengths retain the paired-risk discussion. Summary
word/action targets apply only to concise fields. Summary actions, strengths and
gaps must derive from the same canonical detailed findings; its leading action
condenses the first canonical action. Keep the original two-way FCV risk exposure,
sensitivity/responsiveness discussion and detailed section structure. WBG editorial
style and current browser/Word/HTML templates remain. Evidence-status, full-source
coverage, SORT corrections, grounded prioritization and lifecycle safeguards remain.

Saved sessions must retain and restore risk_exposure, sensitivity_summary and
responsiveness_summary as well as ratings and priorities, so these detailed sections
remain available after reloading and in comprehensive downloads. No new model call,
delimiter, rating enum or priority schema is introduced.

Standard concise admission now checks each how action against canonical action
anchors, with the first how tied to the first detailed action. Matching title or
rationale alone is insufficient. Mismatches use the existing deterministic Detailed
fallback. This lexical check is a guard, not semantic or factual verification;
strength alignment remains a generation instruction and a content-review check.

Fresh restoration verification: one complete standard PAD run produced four priorities and ten full actions. Recorded-output local replay passed all links, four exports, technical-section save/reload and mobile checks. The initial live assertion was corrected for CSS-capitalized headings. Remaining factual/status issues are recorded separately; this is structural/content-alignment acceptance, not analytical sign-off. See `20260921_detailed-analysis-restoration.md`.

## September 21 production release

The user authorized promotion to main and https://fcv-agent.onrender.com.
This supersedes earlier preview-only status statements. The tested development
snapshot supersedes main's July rollback; no later independent main work exists.
Production remains on main with automatic deployment and uses `python render_build.py`
to install dependencies and initialize the pinned public bank. ITS deployment is
not included. Fresh restoration verification and factual limitations remain as
recorded in `20260921_detailed-analysis-restoration.md`.

## Strengths and gaps readability (2026-09-21)

Summary Potential gaps now uses one bullet per existing priority gap. Summary
strength cards are unchanged. Detailed Strengths and Gaps headings render each
existing prose paragraph as a bullet, retaining the complete explanation and
inline emphasis. Existing lists and other narrative sections remain unchanged.
The change is presentation-only: saved sessions receive the same formatting,
without rewriting stored text or changing prompts, ratings, schemas or model calls.

`bulletFindingSections()` in `index.html` and `bullet_finding_sections()` in
`fcv_presentation.py` apply the same paragraph boundaries to the browser,
detailed HTML and detailed Word export. Brief HTML gaps also use list items;
brief Word gaps already use Word's List Bullet style.

## Render review follow-up (2026-09-22)

Core research uses `fcv_core_research.py` to preserve provider citations and distinguish uncertain geography and model interpretation. The existing search budget is unchanged; profile-aware cache entries expire after six hours and source-free failures are not cached. Standard prompts distinguish primary-document RRA references from actual use of extracted contextual evidence. Report controls distinguish summary and full copying, retain the research briefing through session saves, normalize the Watch List heading, and recover from Playbook loading failures. See `20260922_render-output-research-handover.md` for scope and validation.

Watch List heading normalization uses linear line parsing in Python and JavaScript so adversarial whitespace cannot cause regex backtracking.


Live acceptance exposed uncited synthesis leaking into analysis. `core_research_analysis_context` now supplies only country-attributable provider passages to both Stage 1 workflows; the full qualified briefing stays visible and exportable. Timing guidance requires later developments to remain watch items, not historical gaps, and forbids inferring site-specific events from broad country excerpts.

Country matching normalizes typographic possessives before ASCII folding, so a national-news title such as "Somalia’s ..." is not falsely downgraded to ambiguous regional context. The regression includes the exact title returned during live research and retains the namesake-country cases.


## Climate OPCS parity candidate (2026-10-12)

Branch `fix/climate-opcs-parity` updates verified Climate routing and the bounded
registry to `climate-guidance-v4`. DPF PAD hints normalize to Program Document;
IPF-DDO uses IPF; unsupported TA stays unresolved. PID, Project Paper and Program
Document alone do not establish a preparation regime. Explicit OIS dates use the
shared instrument boundaries. AF/restructuring purpose precedes generic paper
labels. Labelled risk inputs use the shared processing classifier with MPA,
FMRF and hybrid-component safeguards; conflicting processing markers fail closed.
New-model IPF can resolve ESF through the shared OIS rule, while AF/restructuring
needs explicit E&S evidence and mixed framework mentions stay unresolved.

DPF-MPA drafting is withheld. PforR mid-cycle guidance is registered. Hybrid PforR
recommendations can use IPF E&S terminology only in explicitly component-scoped
sentences supported by linked component facts; standalone PforR/DPF guards remain.
`DraftingValidationContext.has_ipf_component` is an internal optional boolean;
no output schema, delimiter, rating or extra model call changes.

Appraisal guidance adds evidence checks and specialist referrals for Paris
Alignment, climate/disaster risk screening, climate co-benefits and indicators.
It never certifies compliance or treats a missing upload as an absent assessment.
Reader timing uses conditional new-model review destinations, and PID is not
assumed concept-stage. Source currency remains subject to live PPF verification.
Live acceptance and release status: see `docs/20261012_climate-opcs-parity-validation.md`.

### 2026-10-12 quality acceptance hold (PR #83)

The single Great Lakes quality run on cbd31ddd1084 correctly resolved AF/IPF/multi/ESF and the five-point ratings, but all recommendations were suppressed. Do not promote this candidate as analytically accepted. The semantic verifier now receives the compiler's scoped operational guidance (review prompt v2.6); live effect remains unverified. Upload handlers now resolve current arrays after removal/reset; reset clears package files and metadata. Incomplete exports put their warning before the assessment. See docs/20261012_climate-opcs-parity-validation.md for acceptance evidence.


### 2026-10-12 offline hardening before another paid run

Shared Markdown spacing/marker-drift cleanup and actor normalization now cover all
visible fields. Saved assessments retain bounded diagnostic_trace snapshots,
excluded from readers/logs/exports; reviewer schema adds per-REC issues. Summary
validation records specific failures without relaxing grounding. Prompt versions:
judgments v2.6, compiler v2.5, review v2.7. No added provider calls. See
`docs/20261012_climate-opcs-parity-validation.md` for checks and acceptance limits.
Production remains held pending a separately authorized live quality check.


### 2026-10-12 second quality trial and post-run fixes

The authorized trial on 152656b retained one of three priorities; two correctly
failed scope/authority review. Production remains held. Post-run fixes accept
ordinary grounded summary prose, reject project-document titles on country-homepage
URLs and avoid treating page_age as publication date. Climate scope/CERC and
conditional proposal guards are strengthened (analysis v2.3, compiler v2.6,
drafting v1.1, review v2.8; judgments v2.6). Reader status partial adds a short
needs-review notice across app, copied Summary and exports. See the current
validation document for trace, evidence and live-acceptance limits.


### Native research-context continuation correction

The existing research structuring call now preserves native search/encrypted
context, with further searches disabled and no added call. All 55 research,
grounding and context checks pass. The current validation record documents the
protocol and remaining live-acceptance hold; ITS remains unchanged.


### 2026-10-12 approved dividends framing and Summary gaps

Climate judgment/compiler prompts are v2.7; reader manifest v2.4. Sensitivity now
asks how well the project recognizes and addresses interacting climate/FCV risks;
recognition alone cannot earn a strong rating. Responsiveness asks how well relevant
climate-related design and delivery choices support wider peace and social dividends
within scope, using an evidenced mechanism rather than theoretical maximum benefit.
Five-point values and unscored/legacy exceptions are retained. The shared caveat now
respects project objectives, scope and delivery constraints.

The later Summary-completeness update supersedes the two-item gaps paragraph.
The reader projects up to five complete project-linked residual-gap statements,
independently of recommendation count. Summary uses the normal FCV bullet style,
first-sentence emphasis and every supported priority up to five. Statements over
75 words are omitted, never sliced. Older readers without summary_gaps reuse their
existing priority limitations. Sidebar glosses, saved grades and withholding
notices are preserved. Summary copying inherits these findings and actions.

### 2026-10-12 expanded gaps and candidate coverage

Reader v2.6 adds optional summary_gaps: up to five complete qualified residual-gap
statements, independent of action count. Kept-priority links come first, then
design findings before contextual evidence gaps. The projection checks typed
project/pathway/response/evidence references and explicit-negative support for
confirmed omissions, deduplicates IDs/text, and keeps whole qualifications.
Evidence-trail assembly includes those gap IDs, preserving their supporting prose
in detailed HTML/Word. Legacy readers use existing limitation fields; only fresh
or rebuilt readers gain summary_gaps. Archives are not regraded or regenerated.

Analysis v2.5 explains each gap in two/three sentences, 35-65 words: what remains,
its project-specific consequence and evidence/scope qualifier. Compiler v2.9
considers every admitted gap and may return up to five material distinct actions,
grouping only gaps resolved by the same action. No quota or lowered review gate.
The Climate Summary now displays all five supported priorities, matching normal
FCV's cap. Unknown gap evidence IDs are rejected before compilation. Exact source
words within hyphenated expressions no longer falsely fail entity grounding;
unsupported entities still fail. No dependency, extra provider call, repair loop
or native generation-schema field. Other prompt versions are unchanged.


Final pre-paid refinements: Stage 1 now passes its existing explicit PID beneficiary
countries and country scope into both search and bounded structuring. Neighboring
countries in geographic identifiers are excluded. Regional searches prioritize an
uncovered beneficiary within the existing two-search limit; incomplete coverage
must remain partial. Profile/page text is evidence, never instructions, and document
excerpts must not become public search queries. No new provider or metadata call.
The Summary no longer credits high risk relevance as a project strength; genuine
very_strong responsiveness retains its positive interpretation. Literal source
words/acronyms in compounds, including Flood-resilient and C-ESMP, pass the shared
whole-word grounding check; unsupported entities remain rejected. Methodology
wording describes source-linked checks and expert corroboration without promising
that generation cannot invent a claim. Other gates and five-point values remain.


### 2026-10-13 post-quality4 handoff repair

Analysis v2.6 clarifies exact fact/context IDs and project-only mechanisms when
context evidence is empty. Reader v2.7 adds a plain analysis_status/message for
withheld evidence, shown in both views and HTML/Word. Source packets enrich
metadata with later native citations and prioritize quoted passages within the
same four-source cap, using cumulative pause-turn content. Sonnet search uses
between_tools/3000 tokens and bounded cited quotes; the existing Haiku structurer,
two-search/150s limit and independent evidence/review gates remain. No extra call
or fetch. See docs/20261012_climate-opcs-parity-validation.md for the unaccepted
quality4 result, original private artifacts, tests and remaining paid allowance.


Source-notice wording follow-up: _climate_source_warning_messages preserves
bundle codes while omitting routine primary-selection bookkeeping from the
banner. Regional coverage and unresolved document precedence have plain messages.
Full source/pipeline regression and the subsequent focused wording checks are
recorded in docs/20261012_climate-opcs-parity-validation.md.


2026-10-13 final readout safeguards: reader v2.8 withholds a whole narrative that
introduces responsiveness absent from the reviewed action fields; complete field
presentation retains every action/qualification and grades are unchanged.
Compiler/reviewer v2.10 align titles with minimum actions and distinguish ordinary
measurement from wider dividends. Source proof retains only cited sources and
explicit provider publication dates; unknown dates stay unknown. Climate gaps
carry a concise optional-dividend scope note. No new model/fetch call; original
paid archives remain unchanged. Final trial/check evidence is recorded in
`docs/20261012_climate-opcs-parity-validation.md`.


Detailed export completeness: HTML/Word render the optional reader summary_gaps
as Supporting gap findings before priorities, preserving all five full qualified
statements and the optional-dividend scope note. They still use detailed renderer
boundaries. Legacy readers without summary_gaps do not gain an empty section.


Final export parity: browser Detailed/Share HTML also includes Supporting gap
findings under the core questions, matching the complete data in Python HTML/Word.
Final full verification: 1,444 passed after the hostname-boundary follow-up; paid and replay limits are recorded in the
validation handover. Production/main and ITS remain unchanged.


### 2026-10-13 action-led Climate candidate (rollout held)

The verified reader derives `assessment_themes` from admitted gap statements and
question/evidence links, with `priority_ranks` or explicit evidence follow-up. Detailed
retains full questions in supporting analysis; Word uses an appendix. Summary retains
five complete gaps. Paired five-point ratings replace the old export panel. Climate
Detailed no longer renders the normal route's duplicate priority stepper/cards.
Judgment prompt v2.9 targets 180–260 words of operational context; recommendation
prompt v2.11 targets three to five substantive decisions where evidence warrants them.
An explicit explained revise verdict permits one bounded compiler correction plus
independent re-review through the same validation and original deadline. Original
review and correction diagnostics remain separate; accepted actions survive repair
failure. Reader version v2.9. No new paid generation has validated this candidate.
See `docs/20261013_climate-action-led-validation.md` for acceptance and saved replay.


### 2026-10-13 narrative findings follow-up

The existing judgment call now returns assessment_narratives (design/dividends/inclusion),
one or two connected paragraphs per theme, targeting 70-130 words and citing verified
register IDs. Shared reader admission requires unique themes, known citations including
a project fact, complete plain prose and number/entity/action checks. This narrative
path permits natural paraphrase; the existing strict Summary vocabulary gate is unchanged.
Original canonical gaps and recommendation links remain available as supporting detail.
Browser and HTML use question headings, prose and native disclosures; Word preserves
prose with original detail in its supporting appendix. Sections 04-07 use distinct cards
in HTML. Common prompt calibration assesses conditional potential and enabling conditions,
without penalizing missing peace/dividends terminology. Executive provider schema is
aligned to the existing 180-260 word instruction. No extra generation call or dependency.

Prompt versions: facts2.4, analysis2.7, judgments2.10, recommendations2.12, review2.11,
drafting1.3; reader2.10. Fresh provider output remains unvalidated; PR83 stays draft.


### 2026-10-13 reader simplification (supersedes visible supporting detail above)

User-approved follow-up removes per-theme project-detail disclosures and the
supporting question/watch appendix from Detailed, HTML and Word. Internal evidence
and canonical questions remain available for validation and audit. The three
question-led narrative answers remain. Method shows coverage, limitations and
sources without repeating pathways. Priority cards now use Why this matters and
What the team could do, with implementation/drafting in Recommendation details.
Word mirrors those headings with a detail block. Legacy narrative/field fallback
preserves complete text. Mobile card padding is reduced. Summary watches unchanged.
Judgment and recommendation instructions require natural prose without framework
recaps, label-and-colon verdicts, semicolons or literal Done looks like cues.
Versions: judgments2.11, recommendations2.13, reader2.11. No added model calls.
See docs/20261013_climate-reader-simplification-validation.md for evidence and limits.


### 2026-10-13 standalone brief review

Context/findings/priority prose instructions now develop a connected brief instead
of repeating project history and gap inventories. A reproduced capitalization
false positive rejected sentence-initial Links and silently restored old dividends
wording. Analytical paraphrase now permits bounded generic sentence openings and
inflections of existing permitted prose terms. Multiword names/acronyms, figures,
dates, markup and action checks remain. Strict Summary mode is unchanged.
Versions judgments2.12, recommendations2.14, reader2.12. No added provider calls
or schema fields. New editorial preview asserts admission of all three narratives.
See docs/20261013_climate-cohesive-brief-validation.md. Fresh paid generation remains
unvalidated and PR83 remains draft.

### 2026-10-14 quality8 outcome and reader repair

Quality8 on d6282ef produced four independently accepted priorities and five
Summary gaps. Both-country research recovered on its existing bounded second
attempt. Native Summary/findings were withheld before meaning review; the actual
dividends fallback was 43 words. The single paid allowance is consumed. Preserve
the original session; do not invent or substitute a native reader_review pass.

Post-paid fixes bind only a unique explicit sibling fact from an already-cited
passage, recognize exact grammatical prose openings and distinguish qualified
causal consequences from new project instructions. One targeted final-reader
correction shares the existing output allowance/deadline and requires fresh
meaning review. Untargeted records/themes/actions stay unchanged; correction
cannot add evidence IDs or new names, quantities or action anchors. Compiler1.3,
normalization2.3; reader2.19 links direct accepted recommendation references to
priority cards. Semantic reviewer1.2 remains unchanged.

The original compiler response passes the fixed structural gate but remains
withheld without meaning review. A separate source-checked editorial preview is
not native acceptance. See docs/20261014_climate-quality8-validation.md. PR83,
production/main and ITS remain held pending fresh hosted prose acceptance.
