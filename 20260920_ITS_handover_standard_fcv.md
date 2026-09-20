# Standard FCV management brief and prioritization handover

Date: 20 September 2026

**Status: revised management readability package under final verification. Earlier live trials passed the workflow but identified analytical issues. A fresh full PAD run will validate the latest prompts, gaps section and exports before this handover is finalized.**

## Baseline and scope

ITS reported that QA includes application commit `f8e8142` on `codex/climate-summary-quality-fixes`. This change branch, `codex/nairobi-project-screener`, starts from that exact commit. It is intended as a bounded port onto the QA baseline, not a replacement of the ITS infrastructure or retrieval implementation. The GitHub `main` branch remains an older baseline and is not the target for this patch.

Analytical scope is the standard FCV project screener. Diagnostic-bank expansion, new sector resources, and analytical changes to the Climate module are deferred. The user explicitly included the Climate route in the routing-disclosure removal and subsequently requested shared Word readability improvements. This presentation change applies to Summary, Detailed and matching HTML/Word exports; analytical and internal routing behavior remains unchanged.

## Product changes

1. A compact management brief uses the existing Stage 3 result. It shows plain-language findings, evidenced strengths, potential gaps, and the leading suggested action for each of one to five priorities. The complete assessment retains formal ratings, all actions, drafting, and evidence.
2. Core prompts consider PDO relevance, activity and beneficiary scale, severity of potential harm, and delivery dependencies. Spending is an input to judgement, not a mechanical score. Critical low-budget implementation arrangements and serious harms remain eligible for highest priority.
3. Core generation no longer fills a four-to-five-priority quota. Advice should use applicable project, operational, and commitment instruments without prescribing unnecessary revisions to supporting assessments.
4. Responsiveness is interpreted in relation to the operation's purpose. A limited direct contribution to FCV drivers is not automatically evidence of poor design.
5. Unsupported policy authority, portfolio-wide comparisons, and invented numerical decision thresholds must not be presented as established requirements.
6. Separate Word and print-ready HTML brief downloads supplement the existing comprehensive exports. Browser Print / Save as PDF works with the HTML; no server-side PDF dependency is added.
7. Technical routing disclosures are removed from reader views. Internal routing, document/instrument detection, and actionable unresolved-route warnings remain.
8. Watch narratives retain their paragraphs and Markdown structure instead of appearing as one escaped bullet.

## ITS issue reproduced before changes

On the completed standard-route QA result, the Summary's `What to keep an eye on` section contained one `<li>` holding the entire multiline horizon narrative. Literal `###` and `**` markers appeared in the user-facing text. There were four numbered watch headings inside that single bullet. This was verified from the rendered DOM, not inferred from a model error.

The Render baseline has the equivalent defect: `normalFcvWatchGroups()` collapses whitespace in `horizonConsiderations`, and `renderNormalFcvWatchDisclosure()` treats the result as a plain escaped list item. ITS should render horizon Markdown through its safe Markdown renderer in a prose block and retain true array entries as ordinary bullets. Preserve line breaks before Markdown parsing; do not pass unsanitized model HTML to the DOM.

The QA Summary also displayed a `How this operation was routed` box containing an internal preparation-status label. Remove the routing disclosure in both Summary and Detailed for standard and Climate views and matching exports, without disabling routing logic or suppressing a substantive warning about incomplete analysis.

Private run observations and screenshots are kept outside Git. Their analytical claims have not been independently fact-checked against the uploaded project package. Portfolio comparisons and precise monitoring thresholds were identified as content-review flags, not proven factual errors.

## Shared contract and porting instructions

- Preserve delimiter names, formal rating semantics and timing enum values.
- Retain `concise_readout` and per-priority `concise`; new output is shorter, while valid older concise bundles remain readable.
- Core brief generation targets an 80-110-word overview, zero to three evidenced strengths, 35-50-word gaps and 40-60-word leading actions. Aim for a 1.5-2-page A4 brief, with a maximum of two pages for new output. Do not generate positive findings solely to fill three cards.
- Keep canonical Detailed priorities as the source for concise alignment, lifecycle admission and deterministic fallback. The brief must not introduce a new fact, action or milestone.
- Browser and exports show each admitted concise priority's gap (or legacy why fallback) before a separate list of titles and first actions; they explicitly refer readers to Detailed for the complete actions and evidence.
- `POST /api/download-management-brief` accepts `concise_readout`, canonical `priorities`, `fcv_rating`, `fcv_responsiveness_rating`, resolved `doc_type`, `active_lenses` and `format` (`html` or `docx`). Revalidate on the server, reject specialist routes and unavailable concise bundles, and return the generated attachment. The existing comprehensive download route retains its behavior.
- Reuse the standalone Python exporter in `fcv_management_brief.py` from FastAPI after validation. It has no Flask dependency and no model calls.
- Keep internal OPCS retrieval and ITS infrastructure unchanged. No raw policy corpus, credentials or assessment output belongs in the patch.

## Files and integration points

| Area | Files / symbols to mirror |
|---|---|
| Core prompts and admission | `app.py`: standard Stage 1/2 context, `append_core_concise_stage3_contract()`, `_prepare_standard_stage3_prompt()`, concise normalizers and `extract_priorities()` |
| Brief endpoint | `app.py`: `download_management_brief()`; adapt the Flask response handling to FastAPI while preserving canonical validation |
| Portable exporters | `fcv_management_brief.py`, `fcv_word_style.py`, `fcv_presentation.py`: shared HTML/Word projection, Arial style and safe first-sentence emphasis |
| Browser | `index.html`: concise capability gate, compact priority list, exact-priority links, watch Markdown, brief controls, advisory timing/context, routing disclosure removal |
| Climate export consistency | `sector_lenses/climate_verified_render.py`: HTML/Word presentation only; retain internal route state and drafting gates |
| Regression coverage | `tests/test_nairobi_backend.py`, `tests/test_nairobi_frontend.py`, `tests/test_management_brief.py`, and updated concise/Climate renderer tests |

The public patch is based on the reported QA commit. Adapt shared behavior to the ITS layout rather than replacing its infrastructure wholesale. Restart from a fresh assessment when validating prompt changes; a saved result can validate presentation and downloads but cannot demonstrate the revised model output quality.

## Acceptance cases

- One, two and five substantive priorities retain their order and correspondence across the brief, Detailed and brief exports.
- A project dominated by one component receives proportionate attention, while a critical cross-cutting implementation or harm issue can outrank budget share.
- A valid older saved summary remains readable. An incomplete concise bundle falls back to Detailed with an explicit notice.
- Summary contains no formal rating widgets or technical routing box; Detailed retains formal ratings.
- Every brief priority links to the matching Detailed priority, including non-first priorities and after tab switches.
- A four-section horizon narrative displays headings and paragraphs without literal Markdown markers; ordinary watch arrays remain bullets, and embedded HTML is escaped.
- Brief Word and HTML contain the same leading actions. Comprehensive exports still contain all actions and suggested wording.
- Unsupported comparison claims and numerical trigger values are not invented or presented as policy obligations.
- Existing Climate analytical contracts remain unchanged; only the requested routing-disclosure removal and Word presentation affect its display.

## Earlier validation checkpoints (superseded by the final run below)

- **1,260 tests passed across partitioned runs:** 1,167 broad-suite cases, 11 bank-selector cases, and 82 Climate frontend contracts. This includes standard prompt/parser, concise compatibility, brief endpoint/export, and Climate rendering coverage.
- Python compilation, complete inline JavaScript syntax, and diff whitespace checks passed.
- Four Chromium browser cases remain unverified: print and phone-layout runs stalled in the Windows Playwright runner, and the two following browser cases were not completed. These are not counted as passes.

The bank-selector suite exposed a calendar-dependent archived-snapshot test. It now evaluates the August release at its publication date; all 32 bank/selector tests passed, including expiry rejection. Runtime bank code, expiry safeguards and the pinned country-bank commit are unchanged. Six entries in that candidate bank currently return `bank_content_expired` and require content review before a future Climate bank update.

At this initial checkpoint, visual checks used synthetic data only. All one/two/five priorities remained visible, the fourth priority opened the correct Detailed card, formal ratings stayed in Detailed, and the watch disclosure rendered escaped headings/paragraphs. Mobile width was checked at 390 pixels. A five-priority management brief printed on one A4 page in both Word and Chromium HTML; longer legacy content is allowed to overflow to additional pages. The local browser completed its assertions but stalled during shutdown and was terminated after the diagnostic timeout; the captured output and screenshots establish the UI checks, not a successful browser-process exit.

The user-requested live acceptance protocol was: run the existing Honduras Sustainable Connectivity PAD (P181166) through the updated Render standard route, check all priorities against the source package, compare summary/full downloads, and confirm the ITS watch formatting and routing removal. Prompt guards reduce risk but do not prove factual accuracy without this source-based review. Render Smoke and quality preview deployed candidate `f17abebe868f2ebb5d214fc5d6bb41973c651231` on 20 September 2026. ITS QA has not received this update. Live acceptance was still in progress at this checkpoint.

## Live PAD trial source checks

The test PAD provides a useful materiality case: the main corridor is US$158m of US$187m (84.5%); feeder roads are US$14m, landscape/livelihood activities US$5m, and institutional strengthening/project management US$10m. The output should give the main investment proportionate attention while retaining serious harm and delivery dependencies. The source already includes an estimated 185 hectares of land acquisition, resettlement instruments, labor-influx/SEA-SH measures, participatory selection, and grievance arrangements. Recommendations must recognize those commitments and identify specific verification or operational gaps. Planned measures must not be described as completed. Current implementation status cannot be established from this historical PAD alone.


## Live-trial finding: primary-document coverage

The first complete Honduras diagnostic reached Stage 3 but its source review exposed a pre-existing coverage defect: the 65-page PAD extracted to 216,462 characters, while the standard Stage 1 prompt retained only the first 60,000. The explicit illicit-activity risk and conditional Indigenous Peoples planning provisions occur after that cutoff. Consequently the output incorrectly treated existing provisions as absent, and Stage 2 repeated those claims. Successful extraction did not establish complete analytical coverage.

The follow-up raises the standard primary-document allowance to 300,000 characters in both Express and step-by-step paths, preserves specialist-route limits, and surfaces the existing warning event for any remaining cutoff. No new model call is added. The standard evidence instructions also distinguish recognized risks, planned mitigation, unknown implementation status and absent measures, preserve conditional geographic scope, and avoid inferring policy violations from generic relevance flags. A fresh complete-PAD run is required to validate this correction; a saved assessment cannot establish improved analysis.

The first Smoke attempt stopped at Stage 2 without a retained error message; a second run passed that stage. Its cause is not established and it must not be represented as a diagnosed or resolved provider failure.

The diagnostic completed with four priorities and exercised Summary, all four links to Detailed, rating visibility, safe watch Markdown, and all four HTML/Word downloads. It failed the final session-save check because Save session remained hidden after Express completion. The follow-up calls the existing session-bar updater at completion. Mobile checks were not reached in that diagnostic; they subsequently passed in both complete-PAD trials. The management brief was also too verbose when the canonical fallback was used; generation now receives shorter per-field targets, while legacy admission and factual grounding remain unchanged.

Follow-up regression checks: 158 backend, route, concise and workflow tests passed; eight frontend contract tests passed. Python compilation and diff checks passed. This checkpoint preceded the complete-PAD Smoke and Quality trials recorded below.

## Word readability and source-retention follow-up

The user additionally requested Word presentation resembling the CPF screener. `fcv_word_style.py` is a portable python-docx helper shared by management briefs, standard comprehensive reports and verified Climate Word reports. Copy this helper alongside the brief exporter; call it after assembling the native document. The initial version applied Calibri, navy running headers/headings, subtle priority/action accents, repeated table headings and editable page numbers without altering analysis or page geometry. The readability follow-up below replaces Calibri with Arial and adds bold paragraph leads. Existing semantic warning colors remain.

Standard Stage 1 now explicitly emits a compact sourced project facts and commitments table, retaining component budgets, beneficiary scope, material safeguards commitments, status and conditional geography, including source inconsistencies. Standard Stage 3 explicitly copies the four canonical lifecycle fields into concise priorities; validators and schemas remain unchanged. These instructions address observed information loss and projection risk; they do not certify factual correctness.

Word layout was rendered with native Microsoft Word and inspected across a two-page brief and thirteen-page full report. Those previews reuse diagnostic content solely to test layout; they are not analytically accepted assessment outputs. Focused checks passed: 129 Word/brief/Climate evidence and rendering cases, followed by 45 Word/brief/Nairobi cases after the source-retention refinements.

### Complete-PAD Smoke trial (`58c68d9`)

Assessment `61bd97a4-b29f-4624-a972-56b4a7cccdc8` completed all three stages with four priorities. Upload, Summary, all priority links, Detailed ratings/actions, watch Markdown, four downloads, session saving and 390-pixel mobile layout passed. Canonical content comparisons passed for all four exports. The local browser cleanup timed out after successful assertions; this is recorded separately from the live workflow result.

Analytical review remains open: Stage 1 retained more late-PAD evidence but did not reliably carry all component budgets and conditional safeguard commitments forward. A displacement statistic also used the wrong period/category. The explicit facts table addresses source retention; generated external statistics still require verification. Do not treat this structural pass as analytical acceptance or advertise the diagnostic report as a validated assessment.

### Legacy prompt conflict identified by live Quality testing

The live Quality Stage 2 repeated a portfolio percentage and suggested risk-rating escalation. Inspection traced this to an explicit legacy SORT subsection in the source prompt, not solely free-form model invention. The standard-route prompt composer now replaces that subsection with project-specific evidence-based calibration; copy this replacement as well as the appended Nairobi instructions. The follow-up also guards against inferring a specific SEA/SH classification from aggregate E&S/SORT ratings, treating a planned instrument as noncompliance without the applicable sourced obligation/deadline, and claiming later evidence was available during historical preparation. Specialist prompts are unchanged. This correction requires a subsequent fresh analytical run; the preceding live output cannot validate a prompt it did not use.

## Final Quality trial and remaining acceptance limits

- Deployed application: `b5bd21c2238c72b5ec2b5ff1b3a7765e815b043a`; Quality deploy `dep-dao4ggu8bjmc73b293d0`; assessment `6588a843-0706-4f08-894d-e62904beec09`.
- Complete 65-page PAD upload, all three stages, Summary, all four priority links, Detailed ratings/actions, safe watch Markdown, all four exports, saved session and 390-pixel mobile layout passed. Canonical titles/action content and ordering matched the downloaded Word/HTML files. Local browser cleanup timed out after successful assertions; no application JavaScript errors were recorded.
- All four raw concise cards survived admission unchanged: 25-34 words per rationale and 23-35 words per leading action, with a 75-word overview. The previous long-card fallback was traced to rewritten lifecycle fields; exact copying resolved it in this run.
- Source retention improved: all component totals, planned GBV status, draft IPPF status and land-acquisition exposure were retained. Detailed output remained complete. Native Word inspection covered every page of the full report.
- Analytical acceptance remains open. The generated output still overstates safeguard compliance conclusions, confuses the RAP disbursement condition with the RPF in one strength, and describes approved HEIS support as activated. Some corridor-security statements need properly dated external support. The historical PAD assessment is deliberately anchored to preparation; a current implementation assessment requires newer project evidence.
- The final standard-prompt follow-up removes the explicit unsupported SORT benchmark seed and adds specific classification, commitment-status and historical-timing guards. It passed the composed-prompt/isolation checks within 146 focused tests. Its effect on generated analysis still requires a fresh run; do not represent the earlier output as proof of that correction.

The absence of a fact from the final top-priority list is not itself an error: the conditional IPPF provision need not become a priority unless material to the selected advice. However, no recommendation should contradict that condition. Do not port the recorded diagnostic assessment text as reference content.

## Port sequence

Mirror the behavior from the ITS-reported `f8e8142` baseline in this order: `605804f` (validated brief exporters), `f17abeb` (Nairobi UI and prioritization), `58c68d9` (primary-document coverage and Express session save), `b5bd21c` (shared Word presentation, sourced facts and concise lifecycle copy), then the final standard-prompt correction and compact Word spacing. `078f703` only stabilizes a historical bank test at its publication date. Adapt route wiring to FastAPI and preserve ITS retrieval. The shared Word helper and brief exporter have no Flask dependency. Main/production and the ITS QA deployment were not changed by this work.

Final Word spacing verification: the actual live four-priority brief fits on one A4 page after reducing paragraph/heading spacing. All paragraph text is identical to the live download and the 10.5-point body size is unchanged. The full report remains thirteen pages. Fourteen focused Word/export tests passed after this final presentation adjustment. Longer assessments may still span pages; no text is truncated.

Final deployed application: `36b119fb7586551f69d7609a6c12ac1d9244f80f`, Quality deploy `dep-dao4sjfavr4c73auk1p0`, live at 21:22 UTC on 20 September 2026. The deployed brief endpoint was checked using the completed assessment: text, document/style/header/footer XML exactly match the native-Word-verified one-page file. This endpoint check makes no model call and does not change the analytical acceptance limit above.


## Management readability follow-up

The latest user-approved update removes the differentiated approach note, the instrument/approval/closing/safeguards strip and the additional Playbook attribution from reader views and exports. Internal category knowledge, routing and substantive unresolved-route warnings remain. A short retrospective PAD warning identifies the historical review context without repeating metadata. CPF/RRA and strategy alignment remain available in Detailed.

The standard Summary and both brief downloads place a light-orange Potential gaps section between green strengths and suggested priorities. Every admitted priority remains represented in the same order. An optional standard-only `concise.gap` is admitted when it is nonempty, no longer than 100 words and has canonical context anchors. The 35-50-word/two-sentence drafting guidance is a generation target, not a strict admission requirement. Invalid or missing gaps use the admitted `why`; this does not invalidate an otherwise usable legacy card. Existing fields, delimiters, enums, lifecycle and rating semantics remain. This check establishes format and lexical grounding, not factual truth.

Standard generation now uses plain management language, bold main-point first sentences, explanations after the lead, no em dashes and sparse semicolons. JSON remains plain text. Shared presentation helpers apply Arial and first-sentence emphasis to Word body paragraphs and normalize visible em dashes without changing canonical assessment content, URLs, code spans or numeric ranges. The brief has an 80-110-word overview and longer strengths, gap and action explanations, targeting approximately 650-850 words and no more than two A4 pages. No text is silently truncated to meet pagination.

A saved-result native Word layout preview fits two pages. It uses earlier diagnostic analysis and is only layout evidence. Fresh live analytical, export and mobile verification is pending at this checkpoint.

Pre-deployment verification: 1,277 distinct regression cases passed across partitions and targeted reruns. The four previously identified Windows Chromium cases remain unverified. Updated expectations cover the approved optional gap and removed display elements. Local one/two/five-priority browser assertions, safe watch rendering, exact navigation and 390-pixel layout passed; browser cleanup timed out afterward. A realistic 774-word five-priority brief rendered as two A4 pages at Arial 11 without clipping. Python compilation, full inline JavaScript syntax and diff checks passed.

## Fresh readability trial and session recovery

Quality preview deployed candidate `2b1a76de51f55e7950e577395d4813c1dfcba69d` as `dep-dao5s7ss728c73bctu1g` at 22:29:36 UTC on 20 September 2026. Fresh complete-PAD assessment `118207c5-13e5-4589-a69b-fdfd999c75b0` uses that candidate. Final workflow, export, source review and pagination results are recorded below once complete.

A separate clean-browser test found that loading a completed session restored its data but left the stage navigator inactive. The frontend follow-up reuses existing navigation/rendering helpers to open saved Stage 3 and enable stage navigation. Partial sessions retain their Continue action, and reopening a completed result makes no new model call. This UI-only correction will be deployed after the live assessment completes.

The fresh assessment completed all three stages and four priorities. Its first browser pass reached every Detailed link but stopped on em dashes in fixed UI labels, before full downloads and session saving. The model produced four grounded 55-59-word gaps, all rejected by an overly strict 50-word admission ceiling. The presentation follow-up removes the remaining label punctuation and treats the drafting length as a target, with a 100-word admission ceiling. Exact recorded model JSON will be re-admitted through the corrected parser and every UI/export check repeated without another model call or editorial changes to the assessment. The original run and follow-up artifacts remain separate.
