# Readout presentation simplification implementation plan

> Execute with bounded subagents and coordinator acceptance; the user approved the design and priorities-box placement on 28 October 2026.

**Goal:** Give Climate and normal FCV readouts simple controls, compact Summary priorities and consistent advisory wording.

**Architecture:** Reuse the normal-FCV short-card renderer for Climate, with its existing minimum_action as the complete short paragraph. Keep complete canonical recommendations in Detailed and exports. Use the existing fcv_presentation module for controlled Python advisory text and the equivalent browser template, checked for parity. No prompt, schema, bank, retrieval, model-call or publication-approval change.

**Tech stack:** Existing Python/Flask, inline JavaScript/CSS, python-docx, pytest/Node checks and headed Edge.

## Approved behavior

- One Copy control copies the active tab's main report text, excluding navigation, toolbar and sidebar. Summary copies the short Summary; Detailed copies its substantive displayed content, including report disclosures. Show a Copied acknowledgement and retain clipboard fallback.
- One Download report menu offers Word and HTML full Detailed reports on both routes. Remove the main review-packet and management-brief download buttons; keep their backend mechanisms and session save/load unchanged.
- Remove the generic draft/human-review status and preparation-route banner from app, HTML and Word, including offline readout builders. Keep evidence limitations, concrete verification notes, incomplete/smoke/candidate warnings and actual drafting-route gates.
- Summary cards show rank, short title, Suggested action label, complete existing short action paragraph and a link to the matching Detailed priority. No arbitrary prose clipping or new generation. Keep all five priorities in canonical order.
- Summary omits the duplicate Climate sensitivity line, project-cycle blocks, Specialist reasoning/evidence disclosure and What to keep an eye on disclosure. Detailed keeps their relevant substantive content.
- Rename the Climate Detailed disclosure to Practical considerations and Suggested Text. Existing distinct project-cycle timing stays here in readable stacked text; normal FCV keeps full canonical timing in Detailed.
- Expand the existing advisory paragraph to the user's full text. Use climate and FCV context on Climate and FCV context on the normal route; preserve implementation-stage adaptation. Place it before Summary priorities and inside the Detailed priorities introduction box on both routes, including HTML/Word. Do not put it above the entire assessment.
- Preserve Word banner, palette, styles, logos, fixtures/design ancestry and bank pin. Removing labels does not mark saved assessments or review packets approved.

## Task 1: Browser presentation and controls

**Owner/files:** UI agent owns index.html, tests/test_climate_lens_frontend.py, tests/test_concise_stage3_contract.py and a bounded new tests/test_readout_ui_simplification.py if needed. No Python product edits.

- [ ] Add behavior regressions for compact Climate cards, removed Summary disclosures, correct non-first Detailed link, active-view Copy and two-format download menu; observe the expected failures before editing product code.
- [ ] Update renderClimateVerifiedSummary, initStage3UI, gap links and navigation together so no old accordion hydration or missing anchors remain. Reuse renderNormalSummaryPriorities with route-aware detail navigation and Suggested action label.
- [ ] Replace toolbar controls, keeping full-report export functions independent of Summary. Add advisory once to normal HTML/full-report text and correct final readout copy boundaries; do not copy tab/button labels or the opposite view.
- [ ] Remove visible generic status/preparation text and duplicate sensitivity; rename Detailed disclosure. Keep substantive notices/gates and normal/core behavior aligned.
- [ ] Run focused Node/static UI tests and report any obsolete assertions updated for approved behavior.

## Task 2: Python HTML/Word presentation

**Owner/files:** Export agent owns fcv_presentation.py, sector_lenses/climate_verified_render.py, app.py (export boundary only), build_fcv_readout.py, build_climate_readout.py, and connected Python export/presentation test files. No index.html or UI-test edits.

- [ ] Add failing output tests for full advisory on both routes, no generic status/preparation banner, retained concrete notes/gates and canonical timing.
- [ ] Add priority_advisory_text(route='normal', *, implementation=False) in fcv_presentation, using the approved full paragraph. Use it in Climate HTML/DOCX and normal DOCX priorities introductions. Offline builders omit the generic draft default and use the same advisory.
- [ ] Rename Practical considerations and Suggested Text consistently. Preserve Word design and all canonical recommendation content; no blanket deletion of evidence/route failure warnings.
- [ ] Run focused export and Word design tests; report changes, checks and remaining issues. Do not commit or run a full suite while other owners edit.

## Task 3: Coordinator integration and verification

**Owner/files:** Coordinator owns this plan, current dated handoff, private parity divergence note, ignored browser/Word evidence, integration corrections after agents finish and Git/Render operations.

- [ ] Inspect actual diffs against every approved requirement. Check browser/Python advisory parity and core/climate canonical content, with no new providers or false approval state.
- [ ] Use supplied Syria and current saved Somalia sessions to exercise actual Summary/Detailed, every priority link, Copy in both views, download menu, exact report/session identity and substantive notes. Capture desktop and phone screenshots. Use existing headed Edge CLI; preserve unrelated sessions.
- [ ] Download both actual HTML and DOCX. Render Word pages and inspect all pages on both routes. Keep raw sessions/reports/screenshots ignored; do not modify originals or Word fixtures to hide regressions.
- [ ] Run focused connected tests, syntax and diff checks; sync/init the pinned submodule and run one final offline full suite using a fresh short Windows temporary path. Keep four documented headless hangs excluded and report separate actual Edge checks.
- [ ] Commit logical checkpoints, push only the feature branch, update draft PR89, and deploy the tested code only to the test service with its spending blocker retained. Verify exact deployed SHA/modes and unchanged production. Do not merge, deploy production, approve content, edit the bank or start paid assessments.
- [ ] Record exact commits, checks, evidence paths and limitations in the dated handoff and concise final response.
