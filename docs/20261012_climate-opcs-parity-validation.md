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

### Third authorized quality trial: analytical acceptance still withheld

One paid run used the Great Lakes AF PID in test_documents, on fc34b77af113.
Assessment ID: fb3f2859-32b1-40a6-8a51-d56ffdcd04ab. Server start/end were
2026-10-12 18:43:43.904 / 18:47:19.823 UTC, about 217 seconds. The single Express
request returned HTTP 200. Extraction retained 48,288 characters across 15 pages
with no extraction warnings. Native encrypted research-context continuation worked
live; the structuring call returned a valid bundle. The bundle covered Burundi,
not DRC, and did not establish relevant CCDR coverage.

Ratings were Moderate sensitivity and Limited responsiveness. Structural admission
accepted three candidates; semantic review withheld two, leaving one priority and
the partial-result warning. REC-001 promoted a required ESCP update to a completed
one; REC-002 invented drafting placement and arrangements not verified by its
cited target. REC-003 retained a conditional hazard-considerations proposal for
Kasumbalesa/Kipushi feasibility work, but the narrative incorrectly characterized
routine hazard screening as mainly responsiveness. This is sensitivity under the
approved dividend rubric. Suppression remains appropriate and is not relaxed.

Primary-source inspection found a research integrity failure: the model converted
section 5.2 and footnote 118 into land-loss/hotspot statistics, and converted a
200% sediment-loss projection to land-area degradation. The source is the World
Bank's 2022 Burundi colline-landscape diagnostic:
https://documents1.worldbank.org/curated/en/099930006302237433/pdf/P17682007885e00780b1cc093a09277df1a.pdf
Its executive summary discusses sediment loss, not that claimed land-area metric.
The false claim fed analytical context. Those three figures do not appear verbatim
in visible exported HTML or Word, but that does not make the assessment acceptable.
The original session, HTML and DOCX remain unchanged in local output/playwright
files with prefix 20261012-quality3. Both visible exports contain no %% markers.
The Summary screenshot shows the paired concise cards and partial-result notice.

Offline follow-up requires each fresh research claim to provide a short exact
source_excerpt matching a provider-supplied citation passage at the declared trusted
URL. Claim prose is replaced by that passage, preserving its measured quantity and
qualifiers. Mismatching numerical tokens, fabricated passages and wrong source URLs
fail admission. Prompt excerpts are <=140 characters; the gate allows <=150, matching
native cited_text's limit. Citation-split JSON text is joined without added newlines.
This uses the existing native search/structuring calls; no new URL fetch or model
call. Provider contracts: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
and https://platform.claude.com/docs/en/build-with-claude/citations.
Passage provenance does not itself validate inferred project links or all semantics.

All six verified stages now share sensitivity/dividend, planned/completed-status
and review-date calibration. Drafting no longer invents relative placement.
Summary's capitalized-stopword false rejection (After) is fixed without weakening
number/entity/term grounding. The original raw Summary still fails an independent
term check (rests); it has not been forced into the reader. Direct future verdict
wording reduces that mismatch. Saved scope now follows authoritative multi-country
reader metadata. AF timing is the applicable review, without assuming that an
estimated July approval remains upcoming in October. OIS/current approval status
remain unverified. Versions: facts 2.3, analysis 2.4, judgments/recommendations 2.8,
review 2.9, drafting 1.2, reader 2.5.

Focused offline results: 112 schema/frontend/reader checks passed; 51 source-proof,
research transport and related checks passed. Full follow-up verification is recorded
below once complete. The paid result is unaccepted; these fixes have not had another
generation run. Production and ITS remain held, and PR #83 remains draft.

Final follow-up suite: **1,414 passed in 478.55 seconds**, saved locally as
output/20261012-quality3-followup-regression-result.txt. Staged diff checking passed;
private run artifacts are excluded. The completed trial's actual Detailed view also
shows both sidebar cards, no visible %% markers and no horizontal overflow at
1440px. Its screenshot is 20261012-quality3-detailed.png. These checks do not
regrade the archived result or validate new generation behavior.


### User-requested Summary completeness follow-up

The prior paid result showed one short gap sentence: the gaps section was tied to
surviving actions and capped at two items/80 words. The user requested four/five
substantive bullets comparable to normal FCV and reliable multiple recommendations.
The compiler also discouraged more than three candidates, and Summary capped
visible actions at three. These restrictions are corrected as described above.

Thirteen focused checks passed in 38.87s, including one/three/five synthetic actions
through separate drafting, semantic review, reader, JSON persistence and HTML/Word
export. Selective rejection keeps one action while five independently registered
qualified gaps remain; rejected recommendation prose is never restored. Boundary
checks reject unknown gap evidence, malformed references and unproven omissions.
Two old three-item/markup expectations in the broader connected pass were corrected
and covered by the thirteen passing checks. Broader final results follow below.

Actual local Edge QA loaded a clearly labelled synthetic fixture: five substantive
bullets, five actions and a working fifth accordion. Browser Save session retained
five gaps/five actions; actual HTML download retained every title and supporting
gap text. Desktop 1440px and phone 390px had no horizontal overflow; visible content
had no %% markers. Sidebar glosses stayed compact. Local artifacts have prefix
output/playwright/20261012-summary-completeness-. These are software/layout checks,
not a paid assessment or semantic endorsement of synthetic findings.
No further paid run occurred. Production/ITS and PR #83 remain on analytical hold.


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

The first full pass returned 1,423 passing checks and two obsolete expectations:
a Summary projection assertion loaded before its edit, and the compiler's exact
five-candidate phrasing. The projection passed its focused rerun; the compiler's
original at-most-five contract is preserved. Seventy-six provider/research/runtime
and completeness checks passed after regional/strength fixes. A final full pass
below uses frozen source/tests and a new log, rather than claiming that failed
historical runs passed. Windows Playwright stall diagnostics were logged; the first
pass's browser tests ultimately completed. No paid run yet under the new two-run
authorization; aim to use one after this final no-cost verification.


### Final free verification before the additional paid allowance

The frozen full suite passed: **1,428 passed in 1,086.35s (18m06s)**,
output/20261012-summary-completeness-final-regression.txt. Browser launch/event-loop
stall diagnostics were recorded, but the browser checks completed successfully.
Diff checking passed. The actual selected Great Lakes PID research profile has
exactly Burundi and Congo, Democratic Republic of, multi-country scope and count
2; Angola in the corridor identifier is excluded. The dedicated Edge release
session navigated successfully to the live test app and its upload controls.

The user authorized up to two additional paid assessments on October 12, preferring
one and permitting necessary judgment calls. None has been used under that new
allowance at this checkpoint. The candidate can proceed to isolated test deployment
and one quality assessment; software checks alone do not establish analytical
acceptance. Production/main and ITS remain unchanged.


### 2026-10-13 post-quality4 citation handoff

The first additional authorized run (6467ed54-2a50-4df3-8429-d91954cf7ce9), on
9f5d225, completed in about 179s but is unaccepted: no research claim passed its
source proof, the analysis registers lost their references, and no candidate
was generated. Originals remain under output/playwright/20261013-quality4-*.
Native search transport and actual Save session/HTML/Word exports completed;
Detailed showed no %% markers. No source/review gate is relaxed.

A reproduced metadata-first bug stopped the bounded packet at four hits before
later citations/notes. Packet construction now scans bounded blocks, enriches
matching metadata from later citations, and prioritizes quoted passages within
the same four-source cap. It uses accumulated pause-turn content. Native encrypted
blocks remain intact for the existing Haiku structurer; no new model/fetch call.
Search uses Sonnet between_tools and 3000 output tokens to preserve cited notes;
the prompt asks for four/six verbatim self-contained passages <=140 characters.
The original two-search/150s deadline limits and independent source-proof checks
remain. Content-free boundary telemetry records stop reason, token/text counts
and native-citation count. Failure messages retain the specific evidence limitation.

Analysis v2.6 spells out facts.claim_id vs context_evidence.evidence_id and empty
context behavior; project-only plausible mechanisms use verified project anchors
with an empty context-reference list. Reader v2.7 reports analysis_status/message
when evidence references or project assertions are withheld. Both views and HTML/
Word display a plain limitation: fewer findings/actions are not proof that risks
or gaps are absent. Saved grades and original archival sessions are unchanged.

Seven targeted handoff checks and the connected set are covered by **131 passing
checks in 32.03s**. A frozen full pass follows before the final allowed paid run.
One of the two newly authorized paid runs is used; one remains. The second is
justified by the material failure above, after these free fixes are verified.
Production and ITS remain unchanged, and PR #83 remains draft pending acceptance.

Provider contracts checked against:
https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5


Final pre-paid regression: **1,435 passed in 764.86s (12m44s)**, saved as
output/20261013-citation-handoff-full-regression.txt. Frozen source/tests were used.
The later wording-only source-notice cleanup is covered by **65 passing focused
runtime/workflow/handoff checks in 11.35s**. It omits the routine user-selected
primary-source bookkeeping from the banner and explains regional country coverage
in plain language; source warning codes remain in the underlying bundle. The
primary-document precedence warning remains visible. Diff checking passed.
The exact Great Lakes PDF's hash/disclosure markings were checked before the
approved first additional submission. No additional paid run has followed yet;
one remains for the deployed repair's live acceptance.


### 2026-10-13 final authorized trial and deterministic follow-up

Quality5 (1c07a274-6310-4629-bb8b-b1e91ac5003d) ran on 202bb3d in quality mode.
The native search boundary returned end_turn, 2401 output tokens and 14 citations;
its bounded packet retained notes. Two source-matched claims from Burundi and DRC
survived, four were withheld and research was marked partial. Ten existing
responses, six pathways and seven residual gaps were retained. All four candidates
passed structural admission; semantic review withheld REC-001/003 for unsupported
ESCP sequencing/implementation and supervision assurances, leaving two actions.
The visible Summary has five complete gap bullets and two actions, with compact
paired five-point cards, no %% markers and no desktop overflow. Original session,
HTML and screenshots are under output/playwright/20261013-quality5-*. Actual Word
returned HTTP 200 after 63.059s (cold start exceeded the 60s browser wait); its
completed automatic download was preserved and both titles/no markers checked.
Both newly authorized paid runs are used. No third run is authorized or planned.

Manual primary-source checks matched the historical Burundi temperature period/rate
in the 2022 ASA diagnostic and the DRC worst-scenario poverty projection in the
World Bank press release. These are national context, not measured project-site
outcomes. The press release is dated November 16, 2023; the model inferred November
15 from the URL. Future fresh research now keeps only sources supporting admitted
claims and uses a publication date only from explicit provider metadata, otherwise
unknown. No fetch/model call was added and archival evidence is not recertified.

The retained results action's narrative introduced a responsiveness classification
absent from its reviewed action fields. Reader v2.8 withholds that whole narrative
and uses the existing complete field presentation, preserving the decision,
minimum/optional actions, limitations, scores, ranks and grades. The original
archive remains unchanged. Compiler/reviewer v2.10 explicitly keep titles aligned
with the minimum action and require a wider dividend mechanism for responsiveness;
measurement/finance accounting alone is sensitivity/results clarity. The reviewer
package version remains v2.1; its prompt version is recorded separately as v2.10. Climate gap lists include
a short optional-dividend scope note. One labelled local presentation replay tests
these changes without claiming a new paid generation or changed grades.

Four reproduced guardrail defects were fixed; **119 connected checks passed in
23.59s**. Final frozen regression/layout/deployment evidence follows. No paid run of
the final prompt clarifications has occurred; deterministic safeguards can be
validated against the preserved actual result. Production/main and ITS remain held
until the release acceptance record is finalized.

Primary sources checked:
https://documents1.worldbank.org/curated/en/099930006302237433/pdf/P17682007885e00780b1cc093a09277df1a.pdf
https://www.worldbank.org/en/news/press-release/2023/11/15/a-climate-solutions-country-afe-1123-democratic-republic-of-congo-institutions


Final presentation/export QA: the labelled local replay displays five complete
gap bullets and two unchanged actions, including a working second accordion.
Summary and Detailed omit the unsupported narrative classification; phone 390px
has no overflow or %% markers. Browser Save/HTML retained all actions and gaps.
The earlier full pass returned 1,439 passed/one obsolete exact-annex expectation;
that expectation now includes the safe withheld-narrative integer. Affected checks
passed 129 in 34.87s, then the frozen full suite passed **1,440 in 308.55s**.

Inspection of the actual Word replay found that supporting gap prose was not
rendered in detailed exports, despite being stored in the evidence trail. Detailed
HTML/Word now add Supporting gap findings directly from summary_gaps, retaining
complete text and the optional-dividend scope qualification without invoking the
Summary renderer. Legacy readers without the field retain their export behavior.
The explicit export regression passed two checks, and the real final replay now
retains all five exact gap statements and both titles in detailed HTML/Word.
Original paid archives remain untouched; the complete local Word replay is
output/playwright/20261013-quality5-complete-report.docx. Final full/export checks
are recorded next. No additional paid assessment was used.


### Final release-candidate acceptance

**1,443 tests passed in 354.52s (5m54s)** using frozen final source/tests:
output/20261013-release-complete-export-regression.txt. Diff checking passed.
The affected connected checks passed 104 in 33.95s. An earlier connected run's
obsolete literal heading assertion was corrected to use the existing HEADINGS
constant; its historical one failure/188 passes is not represented as green.

Final local UI/replay checks: five full gaps, two unchanged reviewed actions,
working second accordion, concise paired cards, optional-dividend scope note,
no unsupported responsiveness narrative, no visible %% markers or horizontal
overflow on desktop/phone. Actual Share HTML and Word contain all five exact gap
texts and both titles. Supporting gap findings are visible in settled Detailed
view; the initial case-sensitive innerText probe missed its uppercase CSS heading.
The browser HTML renderer now mirrors the detailed export section without
invoking Summary. Original paid archives and all saved grades remain unchanged.

The software/readout candidate is ready for rollout review. The final paid test
remains an advisory partial-evidence result: two unsupported proposed actions
were withheld, the country bank was deliberately not applied to a regional
operation, and OIS/current milestone status is not supplied. These notices are
retained. Final compiler/reviewer clarifications were added after the last paid
trial and verified offline; no fresh generation claim is made for those revisions.
The independent reader/source safeguards and full export changes were validated
against the preserved real result and synthetic boundaries without extra cost.
Production/main and ITS are unchanged. PR #83 and the private parity record carry
the exact final deployment SHA/health evidence once the candidate is live.


## Final GitHub security-gate follow-up

At commit 55a927d, GitHub's Analyze Python job succeeded, but the separate CodeQL
merge gate flagged one high-severity URL-substring alert at research.py's country
homepage classifier. The existing HTTPS source trust check already used exact
hosts/dot-delimited subdomains; the homepage classifier now uses the same boundary
for worldbank.org. This retains legitimate hosts and avoids accepting lookalike
hostnames in that classification.

The free affected research/handoff/quality/readout checks passed **64 in 13.81s**.
A regression covers the apex host, legitimate uppercase subdomain, lookalike
suffix/prefix, path-only and user-info spoof URLs, plus the PID/homepage distinction.
No model call, new dependency or change to source/recommendation admission was made.
The initial PowerShell attempt to record the full run failed to create its log and
is not treated as successful verification. Python records the final full regression
in output/20261013-release-hostname-final-regression.txt; its result and the final
GitHub/deployment checks follow in the release record.

Final frozen suite after this follow-up: **1,444 passed in 736.89s (12m16s)**,
recorded in output/20261013-release-hostname-final-regression.txt. The slower
frontend section continued successfully; only one execution process was present.
The final test deployment and both CodeQL checks are recorded in PR #83 and the
private parity record after push. Both paid allowances remain exhausted; these
checks used no model calls. Production/main and ITS remain unchanged.
