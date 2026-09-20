# Standard FCV usability and prioritization implementation plan

**Goal:** Deliver the approved management brief and materiality-based priorities on the standard FCV route, with an ITS porting contract and verification record.

**Architecture:** Retain canonical Detailed priorities, rating semantics, delimiters, and existing model-call count. Generate a shorter concise projection in the existing Stage 3 call; reuse validated data for the browser and a separate management-brief download. Changes apply only when no specialist lens is active.

**Baseline:** `f8e814231910d00de947c6adcfd99a10f43312c9`, fetched branch `origin/codex/climate-summary-quality-fixes`; `main` is the intentionally older baseline. Work on `codex/nairobi-project-screener` in its isolated worktree.

**Tech stack:** Existing Flask, Python, python-docx, vanilla JavaScript, pytest and Node-based frontend contract tests. No new runtime dependencies.

## Approved design

- Management brief: headline, 40-80-word overall assessment, zero to three genuinely evidenced strengths, and one to five ranked priorities. Each priority states the issue, why it matters, and the leading suggested action; detailed actions and drafting remain one click away. Formal ratings stay in Detailed. Explain sensitivity and responsiveness in plain language without implying all projects must address conflict drivers.
- Prioritization: account for PDO relevance, scale of activities/beneficiaries, severity of harm, and delivery dependencies. Spending is informative rather than a mechanical score. Critical implementation arrangements and serious harms may outrank large expenditure components. Do not invent a priority to fill a quota.
- Practical advice: preserve instrument/lifecycle routing. Prefer applicable project-document, operational and commitment targets; do not generate a quota of document revisions. Use advisory display language while preserving shared timing enum values. Keep confirmed policy obligations distinct from model suggestions.
- Detailed: retain evidence, formal ratings and suggested wording; group repetitive strategic alignment/context under a disclosure. Keep minor observations in the existing closed watch-items section. Preserve Markdown structure in multiline watch prose and remove the confusing routing disclosure from both views, retaining relevant warnings.
- Exports: add separate management-brief Word and print-ready HTML downloads using validated canonical data. Keep existing comprehensive downloads comprehensive. A4 one-page is a target for newly generated concise content, not permission to truncate findings or shrink text illegibly. HTML supports browser Print / Save as PDF.
- Compatibility: accept valid older concise bundles (150-200 words, three strengths); new generation is shorter. Keep the existing schema names and grounding/lifecycle admission. Incomplete or invalid data must not create a misleading brief. Do not change Climate analytical behavior or enable new sectors. The user subsequently requested removal of the shared routing disclosure from both views, including where the shared Climate helper renders it.

## Tasks and ownership

- [x] Baseline: work from the reported QA commit and initialize the pinned country-bank submodule. Focused normal-FCV parser/frontend checks are recorded in the handover.
- [x] Backend implementation: own `app.py` and `tests/test_concise_stage3_contract.py`, `tests/test_extract_priorities.py`, `tests/test_nairobi_backend.py`. Update standard-route prompts/validation and add a separate `/api/download-management-brief` route. Preserve specialist prompts and shared enums. Test one/two/five priorities, legacy readouts, invalid grounding, lifecycle, and route isolation.
- [x] Frontend implementation: own `index.html` and `tests/test_nairobi_frontend.py`. Show the compact brief without formal rating widgets, retain ratings in Detailed, link each priority directly to its canonical detail, soften standard-route timing display, group repetitive context, and wire the separate export controls. Test escaping, tab/priority identity, missing-summary fallback and specialist isolation.
- [x] Portable brief exporters and documentation: own `fcv_management_brief.py`, `tests/test_management_brief.py`, documentation and handover. Build escaped print HTML and editable A4 DOCX from the normalized readout/priorities. Test same ranking/action projection across formats and reject incomplete input.
- [ ] Integration: inspect actual diffs; run focused suites, Python/JavaScript syntax and diff checks, then the full suite. Render representative exports and inspect desktop/mobile UI locally. Do not interrupt an ongoing user browser assessment.
- [ ] Handover: record file/symbol changes, request/response contract, test results, reproduction steps and unresolved live checks. Record shared-contract changes in the private parity register without committing its contents. Commit and push the isolated branch and create a reviewable draft PR; trial the updated Render candidate with a real test PAD before final acceptance, as subsequently requested by the user. Confirm the Render workspace and inspect deployment configuration before selecting the deployment path.

## Export contract

The frontend posts `concise_readout`, canonical `priorities`, both formal ratings, resolved `doc_type`, `active_lenses`, and `format` (`html` or `docx`). Backend rejects active lenses, normalizes through the existing Stage 3 admission path, and rejects an unavailable concise bundle with HTTP 422. The export module receives only normalized `readout` and `priorities` and creates bytes. It introduces no additional model call and includes a concise advisory and a reminder that the full assessment contains evidence and implementation detail.

## Verification commands

Use `C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider` with the relevant focused files; then `tests/` once. Use `python -m py_compile` on changed Python modules and `git diff --check`. Frontend tests follow the repository's Node harness. Failures from missing submodules or sandbox process permissions must be distinguished from product regressions.

## Deferred packages

Broader expert-calibrated diagnostic bank and sector resources follow this first release. Live ITS defects require observed output and reproduction; do not assert a cause from the reported formatting symptom alone.

## Live PAD acceptance added at user request

Use the existing Honduras Sustainable Connectivity Project PAD (P181166) on the standard route. Verify upload/extraction, all three stages, compact Summary, exact-priority links, Detailed ratings and complete actions, watch formatting, absence of routing disclosures, and both brief/full downloads. Compare output against the source: the US$158m main corridor is 84.5% of the US$187m project, with smaller feeder-road, livelihood and implementation components. Recognize existing land, SEA/SH and participation commitments; distinguish pending measures from completed implementation. Keep raw documents and assessment output in ignored QA storage. Do not finalize the ITS handover until this live trial is recorded.

## Approved Word readability follow-up

The user requested the CPF screener Word visual treatment for FCV downloads. Apply a small shared python-docx styling helper to brief/full standard and verified Climate exports. Retain all content and existing document geometry; use native editable Word headings, a navy running header, subtle action accents, repeated table headings and page numbers. Verify both brief and full output through native Microsoft Word PDF rendering. The live PAD review also requires an explicit sourced project facts/commitments table and exact copying of canonical lifecycle metadata into concise priorities.

## Execution checkpoint

The feature branch is implemented and pushed; live Smoke and Quality PAD trials passed the complete user workflow, exports and mobile checks. Word layout has native Word visual verification. The handover is prepared as a review candidate, with remaining analytical issues and the untried final prompt correction explicitly separated from verified presentation/workflow behavior.
