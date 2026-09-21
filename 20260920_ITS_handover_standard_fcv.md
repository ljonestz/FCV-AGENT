# FCV Project Screener: Nairobi update and ITS handover

Date: 20 September 2026

**Status: the Render presentation, downloads and standard workflow are verified. Analytical acceptance remains open: the fresh PAD trial still contains unsupported claims and commitment-status errors. The saved trial reports are diagnostic examples, not approved project assessments.**

## Baseline and scope

ITS reported QA commit `f8e8142` on `codex/climate-summary-quality-fixes`. The implementation branch is `codex/nairobi-project-screener`; port onto that QA baseline rather than the older GitHub main. Adapt Flask routes to the ITS FastAPI layout while preserving its retrieval and infrastructure.

Scope is the standard FCV project screener. The user also requested removal of routing metadata from Climate views and shared Word readability improvements. Climate analytical changes, CPF screening and quarterly risk briefs remain outside this package. Main/production and ITS QA have not been deployed by this work.

## Implemented behavior

1. Summary shows an overall assessment, green evidenced strengths, light-orange potential gaps and the leading action for every ranked priority. Each action links to the matching Detailed card. Formal rating widgets and all supporting actions remain in Detailed.
2. Core generation selects one to five material priorities without category or document-revision quotas. It considers PDO relevance, investment and beneficiary scale, harm severity and delivery dependencies. Budget share is contextual evidence, not a mechanical weight.
3. Responsiveness is interpreted against the operation's purpose. Limited direct contribution to FCV drivers is not automatically poor design.
4. The management brief is available as editable Word and print-ready HTML. New drafting targets approximately 650-850 words and 1.5-2 A4 pages. The actual trial brief is 833 words and two pages in Word and Chromium printing. No findings are truncated to force pagination.
5. Word uses Arial, bold first-sentence leads, navy headers/headings and restrained action accents. Gap paragraphs stay together. Visible em dashes are normalized without changing canonical assessment content, URLs or numeric ranges. New prompts request plain management language and sparse semicolons.
6. Reader outputs omit the differentiated approach note, routing disclosure, instrument/approval/closing/safeguards strip and additional Playbook attribution. Internal category knowledge, routing, CPF/RRA alignment, substantive unresolved-route warnings and a short retrospective PAD notice remain.
7. The watch section preserves paragraph breaks and safely renders Markdown headings and emphasis. True watch arrays remain lists and embedded HTML is escaped.
8. Standard primary-document input now allows 300,000 characters rather than 60,000, with warnings for remaining truncation. The trial's complete 216,462-character PAD fits. Specialist and secondary-document limits are unchanged.
9. Express completion exposes Save session. Loading a completed saved result opens Recommendations and enables stage navigation without another model call. Incomplete sessions retain their resume action.

## Shared contracts and integration points

- Preserve delimiters, canonical detailed fields, formal rating semantics, timing enums and lifecycle gates.
- `concise_readout` generation targets an 80-110-word overview and zero to three evidenced strengths. Existing 40-200-word admission remains compatible with older complete results.
- Standard `concise.gap` is optional. Admit nonempty text up to 100 words with canonical context anchors. The 35-50-word/two-sentence drafting guidance is a generation target, not a strict parser requirement. Invalid or missing gaps use the admitted `why`. This is lexical grounding, not factual verification.
- Keep concise priority `why`, `how`, title and canonical `project_cycle`. Do not independently paraphrase the four lifecycle values. The brief shows the gap separately from the leading action; full reports retain every action and suggested wording.
- `POST /api/download-management-brief` accepts the readout, canonical priorities, both formal ratings, resolved document type, active lenses and `format=html|docx`. Revalidate server-side. Reject active-lens requests or unavailable concise bundles. No additional model call is made.
- Reuse `fcv_management_brief.py`, `fcv_word_style.py` and `fcv_presentation.py` after canonical admission. They have no Flask dependency or new runtime dependency.
- Mirror the standard prompt composers in `app.py`, including replacement of the legacy SORT benchmark subsection. Copying only appended instructions leaves conflicting legacy instructions active.
- Mirror `index.html` behavior within the ITS frontend. `sector_lenses/climate_verified_render.py` changes are presentation only and preserve drafting gates.

## Verification and provenance

Fresh assessment `118207c5-13e5-4589-a69b-fdfd999c75b0` used application commit `2b1a76de51f55e7950e577395d4813c1dfcba69d` on the Render quality preview. It processed the complete 65-page Honduras Sustainable Connectivity PAD, P181166, through all three stages and generated four priorities.

The first UI pass stopped on em dashes in fixed Detailed labels before full exports and session saving. It also showed that a strict 50-word gap check discarded all four 55-59-word explanations. Follow-up `f041ce7934c38ce9ea13453fb0f91f79295eff67` fixes those issues and includes saved-session recovery from `cab989f`.

The exact recorded model JSON was re-admitted through the corrected parser. All four gap explanations, concise actions and canonical lifecycle values were preserved. No model call or editorial rewriting was used for the repeat check. Original and re-admitted artifacts are separate.

The repeated live check passed Summary, all four Detailed links, rating visibility, gaps and watch rendering, all four Word/HTML downloads, session saving and 390-pixel mobile layout. There were no application JavaScript errors or horizontal overflow. Removed reader disclosures and visible em dashes were absent. Downloaded titles, gap text, leading actions and comprehensive actions matched canonical data.

Native Word verification covers the two-page management brief and every page of the twelve-page full note. The brief contains no em dashes or semicolons. The full note contains no em dashes; generated prose still uses some semicolons. A separate realistic 774-word, five-priority layout case also fits two A4 pages. The final brief-only pagination refinement preserves all text and keeps each gap paragraph together.

**Regression coverage: 1,279 distinct cases passed across partitions and targeted reruns.** Four legacy Windows Chromium print/phone cases remain unverified because their runner hangs. Separate live and synthetic desktop/mobile checks passed. Browser cleanup timed out after successful assertions, which is recorded separately from application results. Python compilation, inline JavaScript syntax and diff checks passed.

Private evidence is saved under `app_feedback/20260920_nairobi-qa/` and excluded from Git: original stage outputs and raw SSE, canonical/admission records, both versions of the result, four exports, saved session, screenshots, Word PDFs/page images, export checks and source reviews. Main labels are `honduras-management-gaps-final` (original run) and `honduras-management-gaps-verified` (repeat checks).

## Remaining analytical issues for ITS

The fresh run no longer repeats the explicit unsupported 48 percent SORT benchmark and retains the top-level component budgets. However, prompt guards alone have not resolved:

- Unknown instrument status becoming a definitive absence, including claims about the Security Management Plan and documents that were not supplied.
- HEIS approval being described as activation or delivered support.
- Conditional Indigenous Peoples scope broadening upstream beyond the PAD's stated current-area exclusions.
- Planned GBV preparation being framed as a missed covenant without establishing the applicable commitment or deadline.
- External statistics losing their period, category or geographic scope. For example, UNHCR's approximately 247,000 displacement figure covers generalized violence during 2004-2018, rather than the generated 2019-2024 violence/climate claim. [UNHCR Honduras](https://www.unhcr.org/where-we-work/countries/honduras)
- Unsupported numerical monitoring thresholds and response periods sounding established rather than explicitly proposed for specialist review.

Prioritize source-backed fact/status retention and uncertainty handling before calling the analysis ready for unattended use. Keep the historical preparation review distinct from current implementation assessment. See the private source review and final content review for exact output/PAD pointers. Do not port diagnostic assessment text as reference knowledge.

## Port and acceptance sequence

1. Port the brief exporters, shared presentation helpers and standard prompt/parser changes from the ITS `f8e8142` baseline. Earlier checkpoints are `605804f`, `f17abeb`, `58c68d9`, `b5bd21c` and `36b119f`; the readability/recovery follow-ups are `2b1a76d`, `cab989f` and `f041ce7`, plus the final gap-paragraph pagination refinement accompanying this handover. `078f703` only stabilizes a historical bank test.
2. Adapt the UI and export routes without changing ITS retrieval. Preserve evidence, lifecycle, formal ratings and unresolved-route warnings.
3. Run fresh standard assessments with representative PADs, including a project dominated by one component. Check analytical claims against the source documents, not only layout.
4. Verify one/two/five priorities, older saved results, invalid concise fallback, every priority link, safe watch Markdown, complete exports, mobile layout and save/reopen behavior. Verify the brief is at most two pages for acceptance cases without cutting findings.
5. Recheck the reported ITS watch-formatting issue on QA after ITS ports the change. No ITS deployment or message to the team has been performed here.

## September 21 production release

The user authorized promotion to main and https://fcv-agent.onrender.com.
This supersedes earlier preview-only status statements. The tested development
snapshot supersedes main's July rollback; no later independent main work exists.
Production remains on main with automatic deployment and uses `python render_build.py`
to install dependencies and initialize the pinned public bank. ITS deployment is
not included. Fresh restoration verification and factual limitations remain as
recorded in `20260921_detailed-analysis-restoration.md`.
