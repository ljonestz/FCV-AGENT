# Render output and public research update

This change addresses report copying, output consistency, research provenance and recoverable Playbook loading in the FCV Project Screener. It is a Render feature-branch update. No ITS code, deployment or configuration is included.

## Output behavior

Full-report copying uses the canonical assessment and all priority actions, including suggested drafting and watch items. Summary copying is identified separately. Full HTML retains the research briefing and Stage 2 analytical annex; Word retains the substantive recommendations without those supplements. Optional on-demand Playbook exploration is separate from the core report.

The Watch List has a single section title. Rating interpretation retains the existing six categories and makes clear that responsiveness depends on the operation's scope. RRA guidance distinguishes a primary document's reference to a diagnostic from the use of an uploaded diagnostic as context. It must not assert the latter without extracted evidence.

## Public research behavior

The existing core search call now receives a bounded project profile and instructions consistent with its existing search budget. It preserves actual provider citation metadata, source passages and available dates. Credible reporting is not limited to a publisher catalogue or a fixed set of FCV keywords. Definite namesake-country material is excluded; uncertain geography and missing dates are disclosed. Model interpretation is distinct from provider-cited passages and is not independently verified current evidence.

The self-contained research briefing carries source links through the existing brief fields and session persistence. Stage prompts must preserve source attribution and distinguish current reporting from evidence available at historical preparation. Unsupported external assertions cannot independently justify a rating change or firm project requirement. A limited briefing does not block document analysis.

Cache entries are separated by country, sector, lens budget and project profile. They expire after six hours; failed or source-free results are not cached. The existing aggregate research time budget and provider call count are unchanged. No additional retrieval provider, server-side article fetcher or package dependency is introduced.

## Integration points

- `fcv_core_research.py`: pure prompt and provider-response helpers.
- `app.py`: existing research call, cache boundaries, standard evidence guidance and Word heading handling.
- `fcv_presentation.py`: leading Watch List heading normalization.
- `index.html`: explicit copying, output scope, rating explanation, research persistence and Playbook recovery.
- Formal rating values, priority JSON, provider endpoint and existing research brief transport fields remain compatible.

Adapt these changes to the receiving application's framework and UI. Do not copy internal infrastructure assumptions or replace existing retrieval integration. This note describes the Render implementation only; it is not an ITS validation record.

## Acceptance and limits

Targeted checks passed across the relevant suites: 101 backend/export/integration tests, 17 core-research normalization tests, and 27 frontend tests. Frontend checks cover copy construction, persistence, scope labels, new-run research resets, and Playbook empty/error/timeout/retry handling. Synthetic Edge browser checks passed for full/summary copy, HTML and Word content, one Watch List heading, research session save/reload, and mobile overflow. Desktop and mobile screenshots were visually inspected. JavaScript syntax and git whitespace checks passed. Initial local validation used provider-free fixtures; live Render acceptance is recorded below. Provider-free fixtures establish preservation, failure handling and attribution boundaries, not the truth of live reporting. A citation is not independent factual verification, and country attribution remains qualified when the available passage/title is insufficient. This update does not resolve all previously recorded project-fact or commitment-status errors.

The pre-merge CodeQL gate identified potentially slow regex backtracking in heading cleanup. Both Python and JavaScript heading cleanup now use linear line parsing, with long near-match regression cases. The first live run led to the additional evidence boundary described below.


## Live acceptance follow-up

The first Somalia run on `02590927ca58` retained five distinct provider source URLs. The EUAA publication date and quoted finding were independently checked. Stage 2 initially ended without a completion event; a single resume streamed normally. Its analysis nevertheless promoted uncited model synthesis into a historical political-context finding. The follow-up excludes uncited synthesis and country-ambiguous passages from analysis input while preserving the qualified full briefing for the reader. It also makes source/event dates and site-specific evidence boundaries explicit. The two new regressions failed before the correction; 29 research/backend checks pass after it. The corrected live run is recorded below.

Country matching normalizes typographic possessives before ASCII folding, so a national-news title such as "Somalia’s ..." is not falsely downgraded to ambiguous regional context. The regression includes the exact title returned during live research and retains the namesake-country cases. The initial regression failed and all 20 normalization checks passed after the correction.


### Corrected live run

On the designated Render test service, assessment `render-review-81d479beef59` completed all three standard-FCV stages on build `2638d276d658`, using the full public Somalia STAIRP P513127 concept PID with no specialist lens. Stage durations were 197, 287 and 414 seconds; the final response parsed successfully with five priorities and a concise readout. Research retained institutional, specialist and national sources, qualified missing provider dates, and did not reproduce the earlier unsupported South West political claim. EUAA source passages were spot-checked at the publisher; this was not exhaustive factual verification.

Browser session loading and Summary/Detailed switching passed. Summary copying retained all five concise priorities (8,539 characters). Full copying retained all five canonical titles and all 24 action/drafting fields checked across the priority cards (43,000 characters). The Summary screenshot was visually inspected. The in-app browser did not expose the HTML download event and does not support content export; live downloaded-HTML capture remains unverified, while the earlier synthetic Edge HTML content check passed.

The subsequent one-line typographic-apostrophe correction was verified against the exact national-news title returned in this run and the full 20-test normalization suite. No additional paid end-to-end rerun was made solely for that deterministic normalization correction.

Residual analytical limitations remain: the model over-prescribed SORT rating floors for a concept-stage PID, treated some missing detail as established absence, and inferred site-level insecurity from broader contextual reporting. These outputs require expert review; this update is not a factual-quality certification and does not claim to solve the previously documented preparation-stage calibration and project-fact issues. The initial run's incomplete Stage 2 stream and the interrupted baseline Stage 3 during redeployment are retained in local QA artifacts; the corrected run completed without either interruption.

Live Word export was then verified on final code build `3bdf64d27c08`: the 52,707-byte DOCX retained all five canonical priority titles and all 24 action/drafting fields. The final source contained no Watch section and the export did not add one. Luna at maximum reasoning independently checked priority/action completeness and session parity; the coordinator verified browser copy fields and the live export command.
