# Preview readiness campaign: 460eaef, 17 October 2026

## Outcome

The explicitly approved preview-only campaign completed one Smoke and one Quality run. The technical pipeline, session restoration, and report/packet exports worked. Quality produced four useful, substantial recommendations (356-381 words each), with concrete PID section edits and preparation decisions in visible prose. Practical considerations is readable task-team prose. Full analytical acceptance remains open: a source-based review found an unflagged airstrip-phasing error in REC-001, while automated review withheld one drafting block and the native reader. No production readiness or detection certification is claimed.

No application change was made during this campaign. Candidate and deployed application: `460eaef736343e0d33ea9ca79d499fdb72d003a4` (application unchanged since 9d0f547). Branch and worktree preserved; PR83 remains draft; production untouched.

## Executions and technical evidence

| Check | Smoke | Quality |
|---|---|---|
| Assessment | 0999c005-9be4-4558-bbf9-37e60348f5b0 | 13290d23-ae01-4bdc-8656-3dcbc3eeefef |
| Deployment | dep-db9rq04s728c73cqchgg | dep-db9rttjbc2fs73d11l60 |
| Run UTC | 18:26:16-18:28:10 | 18:34:50-18:38:36 |
| Native model | claude-haiku-5-5 | claude-sonnet-5-5 |
| Native calls returned | 8 | 10 |
| Native input/output tokens | 225263 / 17461 | 347646 / 28557 |
| Candidates / retained | 1 / 1 | 4 / 4 |
| Summary | fallback | fallback |

Usage excludes upstream research/helpers; invoice cost is unknown. The approved temporary guard opening had no guaranteed dollar ceiling. These are completed, consumed submissions; neither lock nor prior allowance authorizes another call.

Both runs used the complete standard Somalia PID. Quality logs record 21,988 extracted characters, zero extraction warnings, the assessment ID, recommendation counts and HTTP 200 completion. Browser captures record one express request per run, completed stage 1/2/3 events and express_done. No timeout, worker restart, OOM or gateway failure appears in the captured Quality run window. This route uses `/api/run-express`, not separate `/api/run-stage` requests.

Offline artifact checks passed for both: all retained fact source IDs resolve among 65 source blocks; reader contracts validate; exported priority prose is present in HTML and Word; packet manifests and hashes agree; publication_approved=false. Both live packet endpoints rejected deliberately mismatched readers with HTTP 409. Successful Word/packet exports returned 200. Both saved sessions restored the exact assessment and reader. Quality's second priority and its Practical considerations disclosure were exercised successfully. An initial automation click closed the already-open priority and timed out on its hidden child; reopening it resolved the automation issue, without an app change.

Summary/Detailed screenshots and the second disclosure were visually inspected. Quality Word was rendered read-only through a separate hidden Word instance to PDF: 12 nonempty pages, all inspected in a contact sheet, without visible clipping or overlapping text. Paragraphs span pages and the report is long; no pixel-level typography certification is claimed. Original downloaded files remain unchanged.

Smoke generated one candidate, rather than losing four to suppression. It retained a qualified priority but had partial analysis and validation codes FACT_SOURCE_UNRESOLVED, PATHWAY_LIMIT_EXCEEDED, RESPONSE_PATHWAY_REF_INVALID, GAP_PATHWAY_REF_INVALID, SEMANTIC_REVIEW_VERDICT_INVALID and FINAL_READER_WITHHELD. The usable, structurally verified result met the approved technical condition for Quality; it was not an analytical pass.

Quality retained all four candidates. Codes: DRAFTING_SCOPE_UNSUPPORTED, READINESS_FLAGS_NOT_ACCEPTED, FINAL_READER_WITHHELD. REC-003 current-document suggested drafting was withheld; the main recommendation remains. Native-reader objections caused fallback. These are visible limitations, not successful full acceptance.

## Source review and smallest remaining correction

Review method: compare consequential recommendation premises with the complete PID passages and footnotes, distinguish existing arrangements from proposals, and review unflagged text as well as automated objections. Physical PDF pages are used below. This is agent source review, not authenticated human approval. Human reviewer minutes and approval have not yet been recorded.

1. **REC-001 requires correction.** Its visible narrative says the four remaining airstrips, cities and corridor segments all remain under discussion. Footnote 10 on physical page 6 already identifies five Phase 1 airstrips and says the others follow in subsequent phases. Footnote 11 leaves the city list under discussion. The recommendation has conflated different phasing/selection states. The reviewers did not flag this. Keep the conflict/displacement selection advice, but distinguish recording/reviewing the rationale for the five selected Phase 1 airstrips from criteria for subsequent-phase airstrips and still-unsettled cities/corridors. Apply consistently to minimum_action, narrative, suggested drafting and their rendered copies. Proposed replacement: "Record how conflict and displacement exposure and the distribution of access benefits informed the five selected Phase 1 airstrips. Apply the same considerations alongside technical criteria when finalizing cities and corridor segments and planning airstrips in subsequent phases."
2. **REC-002 is useful and qualified.** Pages 6-7 support drainage, access roads, national early warning links, displaced populations and possible indirect effects. Neighbourhood overlays and assessment tasks are proposed preparation actions, not claimed commitments. Preserve the hydrological qualification in Practical considerations.
3. **REC-003 should remain, with the carry-over explicitly conditional throughout.** Page 6 supports targeted construction training; footnote 12 records SURP II employment results and gender-inclusive hiring precedent. It does not commit Phase 1 to the same bidding requirements. The visible narrative distinguishes precedent and proposals, but minimum_action says Phase 1 "will carry over" those requirements. Prefer: "Agree whether and how to adapt SURP II hiring provisions for Phase 1, and describe the proposed training-intake approach for displaced people, women and youth." This preserves practical specificity without assuming adoption. The PID itself attributes over four million IDPs to urban areas (physical page 3); avoid implying they all live in selected project cities. The six-city MIS is explicitly documented on page 6.
4. **REC-004 improves on the historical miss.** Pages 6-7 support sector-revenue O&M frameworks, an airport authority roadmap and overflight reform. Fresh prose asks whether/how these cover local airstrips and uses municipal frameworks for drainage; it does not assert the historical exclusion or revenue sufficiency. The five names match footnote 10. Suggested drafting should separate the aviation coverage question from municipal drainage funding to avoid implying the airport authority finances drainage. Retain the maintenance recommendation.

The final-reader review objected to IDP-neighbourhood targeting, predecessor hiring protections being treated as current, and a coordination platform that "could support cooperation". The first two identify distinctions requiring attention; the third may be an acceptable qualified inference given Pillar 2's coordination remit. Do not turn that model objection alone into a substantive-error finding. Withheld native prose was not accepted; the displayed report uses fallback findings. Source review of the final package must include the executive readout and all other retained prose, not only those flagged fragments.

Research returned six claims from two sources with partial status. The January 2026 World Bank Somalia CCDR PDF was accessible; a historical UNifeed flood item could not be independently opened in this review. Truncated source excerpts and national evidence do not establish project-site conditions. No new provider call is needed to resolve the above PID-based corrections.

Historical v2.21 REC-004 miss remains a failed detection result. This new, better maintenance paragraph does not retrospectively validate detection. The new REC-001 miss also shows why human source review remains necessary.

## Restoration and next step

Preview `srv-d6gsivcr85hc73a2833g`, workspace `tea-d6de2tsr85hc73bqdi0g`, remains on fix/climate-opcs-parity, auto-deploy off. Restored with a merge-only environment update:

- CLIMATE_VERIFIED_RUN_MODE=quality
- CLIMATE_VERIFIED_ASSESSMENT_MODEL and CLIMATE_VERIFIED_REVIEW_MODEL empty
- FCV_PILOT_BUDGET_MICROUSD=1
- FCV_PILOT_BUDGET_DB=/tmp/fcv-ipf-readiness-20261017-853771e-post.sqlite

Restore deployment `dep-db9s3njncjis73afgo90` became live at 18:45:15 UTC on 460eaef. Browser health returned status=ok, build=460eaef73634, mode=quality. Restoration evidence is the successful merge acknowledgement, live deploy and health; no independent runtime guard-hook inspection or paid rejection probe was performed. No ledger was reset or replenished. Production was not mutated.

The smallest next step is an offline, source-corrected review copy of this Quality result, carrying the dispositions above through canonical records, matching reader, all exports and a new packet. Preserve this raw run and its honest fallback/reviewer statuses. Do not forge a reader pass or reuse the old snapshot. Then Lindsey Jones reviews consequential claims and records version-bound approval through the existing authenticated organisational workflow (specific workflow still to be named). Keep publication_approved=false. Full useful-report acceptance and human approval remain pending; no further paid run is authorized or queued.

## Artifact index

Untracked directory: `output/20261016-ipf-pilot-live-preflight/`.
Prefix: `ipf-readiness-20261017-460eaef-`, then smoke-/quality-.
Saved: health, state, observed-api, session, report.html, report.docx, review-packet.zip, verification.json, UI metadata, browser HTML, screenshots, Render logs. Quality additionally has PDF, 12 Word page images and contact sheet. Browser-current.html was captured on Summary; browser-detailed.html was captured on Detailed.

Quality snapshot: `aa49914dba1d395f320236db019058e8266ddc3f508d711c812d71c07cbe4251`.
Quality report HTML SHA256: `ddba9f64d1ff7d933d505b5579703b3ab21542548145121bf8f1b3fd476d4149`.
Quality DOCX SHA256: `7125e054044ebb7cd86bf35d3965bd064f299852f4bdf92230463010a9b5d189`.
Quality packet SHA256: `3c814fc4997ea90deb858b3f6563bc53eca23770cb36dd5fcb36fa4cbfe2b44d`.
Smoke snapshot: `6351f2c01b98c3ccf621ea6ba8b4bcf603434022ce460878f362238bddc3ba7f`.

No new application tests were needed for this documentation-only result. Previous 1,806 passing tests with four known Chromium hangs excluded remain historical checks, not a complete browser-suite pass. Raw artifacts and the pre-existing untracked tests/test_climate_final_reader.py remain outside Git.
