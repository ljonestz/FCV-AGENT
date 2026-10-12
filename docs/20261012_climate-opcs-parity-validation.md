# Climate OPCS parity validation - 12 October 2026

Base: main `1168a8f`. Candidate branch: `fix/climate-opcs-parity`.

## Scope and method

Verified Climate context, guidance, prompts, recommendation validation and shared
reader. No standard-route changes. The maintainer authorized local OPCS source
access for this session. Policy sources were read locally; no source PDFs or raw
internal text are included in the repository.

## Policy basis

- IPF and PforR One-step / Two-step Preparation procedures (April 2026), Section I:
  OIS boundaries, risk rules, AF, MPA, FMRF and hybrid component distinctions.
- DPF Procedure (May 2026), Section I and processing tables: April 18 boundary,
  Program Document and instrument-specific processing.
- Environmental and Social Directive/Procedure for IPF (January 2026), scope and
  Annex III: ESF trigger, exceptions and PforR IPF-component E&S instruments.
- Multiphase Programmatic Approach Guidance (November 2021 revision), page 4:
  DPF cannot finance an MPA.
- Preparation of IPF Guidance (June 2026), page 15: climate co-benefits and the
  climate-indicator check when the evidenced share is at least 20%.
- Preparing the IPF Project Paper (July 2026), page 11, and PforR Program Paper
  (June 2026), page 13: Paris Alignment and climate appraisal evidence.

The curated October index warns that it lags the live PPF library. These changes
are grounded in inspected local documents, not certification of all latest policy
revisions. OIS-as-Concept-Decision wording and the exact April 17 boundary retain
the existing Help Desk caveats. TA applicability and guarantee routing remain
outside resolved coverage; no automatic TA-to-IPF conversion was added.

## Verification history

- Original audit: 264 existing tests passed; additional probes exposed gaps.
- New regressions initially reproduced 16 failures (2 cases already passed).
- Focused candidate tests: 229 passed after final MPA/FMRF and E&S hardening.
- Full suite on 7d1296a: 1,355 passed, 8 failed (906 seconds). Three stale
  wording assertions were aligned with the applicable-review label and scoped
  PforR hybrid exception; all 113 tests in those three files then passed.
  The remaining five frontend fixture failures reproduce on the untouched
  checkout: two missing SR_TERM_S_TIP fixtures, two obsolete horizon-render
  fixtures, and a null checkpoint fixture. The full suite is not green.
- Live smoke completed on the original candidate; quality is held. Only `fcv-agent-climate-smoke`, service
  `srv-d6gsivcr85hc73a2833g`, URL `https://fcv-agent-1.onrender.com`, is authorized
  for these checks. The service now tracks `fix/climate-opcs-parity`, candidate
  `7d1296ab0597`, with smoke mode confirmed by /health.
- Production and ITS have not been deployed or modified.

## Shared-build implications

Mirror verified Climate resolver, registry, prompt, hybrid validator and reader
changes together only after acceptance. Preserve ITS retrieval differences.
Do not port just the component prompt exception without its deterministic guard.
No external payload field, delimiter, rating or provider-call change is intended.

## Great Lakes live result and remaining acceptance limits

The user replaced the Somalia test with the original checkout's
`test_documents/P174814-great-lakes-pid-20261007.pdf`. This 15-page appraisal PID
is internally dated 10 July 2026 and concerns P174814 Additional Financing Request
1. It names Burundi and DRC and identifies IPF. No explicit OIS creation date or
processing-model marker was found; the filename date is not an OIS date.

Smoke assessment `6a02d352-3456-4ef6-af4f-4bd379c0ccbf` started at 13:23:41 UTC
on 12 October and completed all three stages. Extraction returned 48,288 characters
with no warnings. The initial country was Unknown, the bank was unavailable, and
web research passed its gate on the second attempt (research-only grounding).
The saved reader correctly identifies AF/IPF but incorrectly labels country scope
single while its narrative names Burundi and DRC. Preparation regime remains
unresolved and processing model unknown. This run therefore does not establish
new-appraisal routing or quality acceptance. Do not run quality until the scope
defect is resolved; no quality call was made. The five-point scale added afterward
has deterministic verification only, not a fresh live model run.

Local artifacts: `output/playwright/.playwright-cli/fcv-session-2026-10-12.json`,
the Summary screenshot `page-2026-10-12T13-30-41-595Z.png`, and subsequent compact
layout screenshots `20261012-compact-climate-summary.png` and
`20261012-compact-climate-mobile.png`. Raw artifacts are not committed.
Standalone export acceptance is still pending.

## Approved sidebar follow-up

Both normal FCV and verified Climate now retain sidebars in Summary and Detailed.
Climate cards have short glosses and collapsed full rationale; mobile retains a
collapsed ratings section. Responsiveness is an additional contribution whose
expectation depends on scope, often a sign of going above and beyond.

At the user's request, the Climate responsiveness contract changed to five points:
very_limited, limited, moderate, strong, very_strong; not_expected and unclear remain
unscored. Prompt/schema version is climate-judgments-v2.5. This supersedes the
no-rating-change statement above. Historical Emerging results remain legacy and
unscored in the UI, requiring reassessment. Normal FCV's existing scale is unchanged.

Follow-up verification: 99 focused pipeline/schema/runtime/sidebar tests passed;
8 final sidebar tests passed. Two missing frontend fixture constants were repaired;
the three other pre-existing full-suite failures remain outside this change.
The full suite has not been rerun after this follow-up. Local saved-session replay
confirmed desktop Summary/Details and the mobile disclosure. The local static
preview has expected API 404s and is not a backend acceptance run.

## Production-readiness follow-up (superseded by acceptance result below)

The user authorized remaining fixes and one paid acceptance run. The run has not
yet been used. Offline checks of the actual PDF through the application's own
extractor now resolve Burundi and DRC, multi-country scope, AF/IPF and ESF.
The parser excludes the adjacent DRC-Angola geographic corridor from beneficiaries.
Preparation remains unresolved because the PID does not establish the OIS date;
the browser and exports now state that limitation. No date was inferred.

Metadata helpers now disable adaptive thinking and safely collect text blocks;
the previous first-block assumption could silently return Unknown. E&S markers
are checked throughout retained primary evidence. No new API call was added.

Offline verification: seven metadata tests pass; 67 related routing/bank tests
passed before the final combined-column regression; 99 reader/export tests pass;
16 final metadata/sidebar/export checks pass. Saved Emerging results remain
readable as legacy while new judgment validation requires the five-point scale.
All three remaining baseline fixture defects were reproduced and corrected.
Full suite and live quality/export acceptance are in progress.


## Final acceptance result: HOLD production promotion

One user-authorized paid quality run was used on candidate `cbd31ddd1084` at
14:33:09 UTC on 12 October 2026; it ended at 14:36:56 UTC. The browser retained
assessment ID `6a02d352-3456-4ef6-af4f-4bd379c0ccbf` from the earlier smoke run;
distinguish the runs by timestamp, build and runtime_mode. No second quality run
was started. Production and ITS remain unchanged; PR #83 stays draft.

The Great Lakes PDF resolves AF/IPF, multi-country and ESF correctly. The country
bank is withheld for the multi-country operation; research-only grounding passed
its gate. OIS/preparation route remains explicitly unresolved. Live ratings are
Moderate sensitivity and Limited responsiveness contribution, each on five points.
The desktop sidebar appears in Summary and Detailed; at 390px viewport the page
has no horizontal overflow. Short glosses and collapsed explanations are retained.

Quality acceptance FAILED: five recommendations were generated, one failed the
actor check and all four admitted candidates were rejected by semantic review.
Reasons include unsupported target, authority and scope. The note correctly says
Recommendations stage incomplete; no rejected recommendation was promoted.
The generated dedicated overview also failed its contract and used the supported
fallback. The run does not demonstrate acceptable recommendation quality.

Post-run fixes (offline verified, live analytical effect not established):
- The semantic verifier now receives the same scoped operational-guidance packet
  and registry version as the compiler. Previously it lacked the permitted-target
  evidence it was asked to judge. Review prompt v2.6 distinguishes an advisory
  destination from an existing commitment without weakening actor/authority checks.
- Upload handlers resolve current file arrays after removal/reset, and reset clears
  package files, metadata and native inputs. Two regressions reproduced the defect.
- Incomplete Word/HTML exports now carry the warning before the assessment body.
- The streaming test retains its elapsed-time invariant with Windows scheduling
  headroom; its original 200ms deadline flaked under the full test workload.

The saved result does not retain suppressed drafting or raw semantic-review input.
Consequently the rejection causes cannot be fully reconstructed, and the guidance
fix cannot be represented as having recovered the paid result. A further explicitly
authorized live quality check is required before production promotion.

Artifacts (local, excluded from commits):
`output/playwright/20261012-quality-session.json`, matching `quality-report.html`,
`quality-report.docx`, Word-rendered `quality-report.pdf`, and Summary/mobile PNGs.
HTML and Word downloads were exercised against the test service without model
calls. Both preserve the scope wording, incomplete status and OIS caveat. Word
rendered to eight nonempty PDF pages; the first page was visually inspected.
The newer front-page warning is covered by the offline export regression.


Final offline verification: full suite 1,381 passed in 612.66 seconds after upload
and timing-test fixes (`output/20261012_acceptance-suite.txt`). Subsequent reviewer
context and export-warning edits passed 51 focused pipeline/sidebar/upload checks
and three shared frontend-renderer checks. `git diff --check` passed. These are
code/regression checks, not a successful replacement for live analytical acceptance.


### 2026-10-12 offline hardening before another paid run

The shared Markdown renderer now keeps headings, lists, tables and rules as blocks,
so blank-line-separated bullets do not accumulate stray breaks or invalid paragraph
wrappers. Visible complete or two-percent-drifted machine markers are removed;
backend Stage 3 cleanup canonicalizes that drift before removing duplicated blocks.
Percentages and prose are preserved. The screenshot-shaped fixture was reproduced
and checked in local Edge (`output/playwright/20261012-context-spacing-fixed.png`).

Actor normalization now covers title, narrative and responsible_function as well
as action/drafting fields. Verified actors are preserved; invented instruments,
destinations and systems remain subject to the existing guards. The compiler says
to address the task team when no responsible actor is verified. An offline AF
advisory-target fixture passes while invented targets/instruments fail.

Saved verified assessments now retain `diagnostic_trace`: bounded JSON snapshots
of the raw overview, raw candidate set (first five), review input, separately
retained normalized reviewed recommendations, and semantic review response. Each
snapshot is at most 60,000 characters and explicitly marks truncation. These are
untrusted diagnostic data in Save session only, excluded from reader/report output
and app logs; they do not recover the previously discarded paid-run proposals.
The reviewer schema adds per-recommendation `issues` with codes and a short
explanation. Admission and suppression still use the existing verdict/ID controls.

Summary validation now records its specific rejection reason and paragraph index
without relaxing shape, length, grounding or copy checks. Prompt v2.6 explicitly
names all four required dimensions and targets about 190 words. Compiler prompt
v2.5 and reviewer prompt v2.7 accompany these changes. Five-point rating semantics
are unchanged. Shared prompt/schema/diagnostic changes must travel together if
later mirrored to ITS. No additional provider call or paid run was added.


This pass completes the identified offline follow-ups. The old run's raw summary
and rejected proposals were already discarded, so their exact rejection causes
remain unrecoverable. New diagnostics prevent the same loss in a subsequent run.
The prior failed run is still incomplete; no recommendation was reinstated and
production promotion remains held pending a separately authorized live check.


Offline acceptance after this follow-up: full suite 1,391 passed in 813.27 seconds
(`output/20261012_prepaid-offline-suite.txt`). The final checkbox/UTF-8 refinement
passed all eight renderer/timeout checks; the final normalized-review snapshot
passed three focused pipeline checks. `git diff --check` passed. Local Edge visual
inspection confirmed the corrected context layout. No new paid call was made.
The candidate is ready for the next explicitly authorized quality trial, with
production promotion still held. Truncated diagnostic snapshots are partial data
and must not be treated as complete JSON evidence.


## Second authorized quality trial: partial result, promotion still held

The user authorized another paid run. Exactly one quality assessment was started
on `152656be934c` at 16:46:23 UTC and ended at 16:50:03 UTC on 12 October 2026
(HTTP 200, roughly 220 seconds). Assessment ID:
`ff7b664c-2919-4538-a895-c696be3e7f60`. No additional provider repair or rerun
was made after it. Extraction again returned 48,288 characters without warnings.
AF/IPF/multi/ESF routing was correct, with OIS/processing still explicitly unknown.
Live ratings were Strong sensitivity and Moderate responsiveness contribution.

Three candidates passed structural admission. Semantic review withheld two for
unsupported PIU decision authority and unverified timing; one GBV-service proposal
survived. These selective rejections are appropriate. The surviving proposal has
a weakly evidenced climate link, so the result does not establish satisfactory
Climate-lens analytical acceptance. The analysis register also credited CERC too
broadly for conflict shocks, despite the legacy Climate prompt's eligibility guard.
No rejected proposal was manually reinstated.

The new diagnostic trace worked: raw proposals and per-REC review explanations
were retained. Review input exceeded the snapshot cap and was flagged truncated;
the separately retained reviewed proposals were complete. The dedicated summary
failed because its first paragraph lacked a literal verdict keyword. Offline replay
then exposed ordinary connecting/reporting words rejected by the vocabulary check.
The post-run validator now accepts this same three-paragraph provider output while
retaining number/date/entity/action grounding checks. No replacement summary call.

An external-source mismatch was verified against the World Bank Burundi overview
(https://www.worldbank.org/ext/en/country/burundi): the research packet labelled it
as the uploaded project PID. Normalization now excludes a PID/PAD/project-ID source
that points to a generic country homepage and removes dependent claims. Saved
research replay changes four sources/three claims to three sources/two claims.
The SDK's page_age is last-update metadata, not publication date (official reference:
https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool).
It is no longer copied into publication_date, and relative ages are left unknown.

Post-run prompts now keep new roles/triggers/timing visibly conditional proposals,
require a specific evidenced climate mechanism for ranked FCV issues, and preserve
CERC eligible-emergency/borrower activation conditions without treating a zero
initial allocation as a funding gap. Versions: analysis v2.3, judgments v2.6,
recommendations v2.6, drafting v1.1, review v2.8. Their generation effect remains
unverified by another paid run.

Partial semantic-review results now carry a short Recommendations need review
notice in the app, copied Summary and HTML/Word exports. Neutral no-priority results
and wholly suppressed incomplete results retain their distinct existing messages.
The status is derived from actual withheld-priority diagnostics, not rating values.

Artifacts, local only: output/playwright/20261012-quality2-session.json; matching
quality2-report.html/docx, Summary/Detailed/mobile PNGs; and clearly labelled
quality2-replayed-session.json/replayed-report.docx for offline rendering. The raw
session is unchanged. HTML and Word downloads completed, preserved the OIS caveat
and contribution wording, and had no visible machine markers. At 390px viewport
there was no horizontal overflow. The replay restores the validated raw overview
and shows partial status without adding any rejected recommendation.

Production and ITS are unchanged. PR #83 remains draft. Further analytical
acceptance is required before promotion; software completion alone is insufficient.


Post-run verification: 241 connected backend tests passed in 12.30 seconds;
10 reader/frontend/export boundary checks passed in 14.40 seconds; the final
reader-status/version metadata passed three focused checks. Renderer version is
climate-reader-v2.3. The previous full suite remains 1,391 passed; it has not been
rerun after these scoped post-trial changes. `git diff --check` passed.


### Native research-context continuation correction

The metadata-only research fallback dropped native web-search result blocks and
therefore the provider's encrypted source context. The existing structuring call
now continues the original user/assistant search messages intact, retains the
search tool definition/beta, and sets tool_choice to none to prevent another
search. Retrieved content remains untrusted evidence. No model call was added.
Tests preserve exact native-content identity, two-call count, bounded final prompt
and content-free logs; 55 research/grounding/context checks pass. This matches the
provider's documented search continuation protocol. The live effect has not been
checked by another paid run. The quality/production hold remains in place.


### Approved peace/social dividends ratings and Summary gaps

Lindsey approved keeping paired sensitivity/responsiveness cards with revised
questions on 2026-10-12. Sensitivity now assesses recognition AND response to
interacting climate/FCV risks. Responsiveness assesses relevant, evidenced peace
and social dividends through climate-related design and delivery within scope.
Recognition alone cannot earn strong sensitivity; general social benefits or
co-location do not establish a Climate responsiveness pathway. The report's
investment/delivery framing shapes the rubric without requiring all categories
or claiming demonstrated peace impact. Judgment/compiler prompts are v2.7;
reader manifest is v2.4. Five-point values and unscored/legacy exceptions remain.

Summary now places Potential gaps between strengths and actions. It reuses at
most two distinct complete limitation fields from admitted priorities (<=45 words
each, <=80 total). It never recovers withheld recommendations, cuts qualifications
or infers a missing gap. Oversized legacy prose remains in Detailed; when no short
limitation exists, the previous bridge remains. The existing compiler asks for one
qualified limitation sentence <=35 words, distinguishing missing evidence from a
confirmed omission and optional dividend opportunities from required corrections.
No new schema field or provider call. Summary copying inherits the same content.

Local Edge replay of the preserved quality2 case: the gap is 19 words; sidebar
glosses are six and ten words, with full rationale collapsed. Both cards appear
in Summary and Detailed. The 390px mobile disclosure is closed initially, opens
to two cards, and has no horizontal overflow. Revised questions appear in the
actual browser HTML download and the deterministic replay DOCX. Word rendered
the latter to 12 PDF pages; page one was visually inspected. No visible machine
markers were found. The partial-result notice, one retained priority and OIS
qualification remain. Saved grades were not regenerated or regraded. These are
presentation checks on an archived analytically unaccepted result, not live
validation of the revised rubric.

A conflicting shared disclaimer about an ideal project with maximum resources
was corrected to respect scope and delivery constraints. The frontend retains
the authoritative server sensitivity question, with a bounded migration of the
known old saved wording only; unrelated server text is preserved.

Additional no-cost provider check: the installed SDK serialized genuine native
BetaMessage search-result blocks intact (including a dummy encrypted payload),
retained tool definitions and tool_choice none, using httpx.MockTransport. No
external request or model fee; provider-side retrieval/generation remains untested.

The connected pass initially returned 332 passing checks and two old-wording
expectations, corrected and verified by ten focused checks. A full pass then
returned 1,402 passing checks and one authoritative-question contract failure;
the fix and saved-wording migration pass nine focused checks. Final full-suite
evidence is recorded below after completion.

Artifacts are local only under output/playwright: 20261012-dividends-summary-gaps-
final.png, summary-mobile-final.png, browser-report.html, replayed-report.html/docx/
pdf and word-page1.png (all use the 20261012-dividends prefix). The input quality2
session and its prior replay remain unchanged. Static local preview API/glossary
404s reflect the intentionally serverless layout harness, not a hosted app check.
Production and ITS remain held; no further paid run was made.


Final verification after the authoritative-question correction: **1,404 tests
passed in 378.81 seconds** with the full offline suite, no cache provider.
`git diff --check` passed. No further code changes followed that full pass.
Local test-result record: output/20261012-dividends-regression-result.txt.
The configured smoke service was rechecked as fix/climate-opcs-parity with commit
auto-deploy enabled; final deployment SHA/health is recorded in draft PR #83.
The service deployment is a software check, not live model/analytical acceptance.
