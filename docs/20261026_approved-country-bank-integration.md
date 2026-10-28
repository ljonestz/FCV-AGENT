# Approved country-bank integration: 26 October 2026

The approved country bank is integrated on `feat/country-bank-integration-20261026`,
based on `feat/word-readout-redesign` at
`3ab33b598492f8f9ee8882d094b00ee2dfa453a3`. The Word design files are unchanged.
This is a branch integration, not a production deployment.

## Release and approval

The app pins bank commit `cccf251d86a8f3f3a73c930ff8b284c256304c1a`:
`2026.10.26.approved-country-bank`, schema 1.1.0, `candidate: false`.
It contains 24 countries, 272 referenced sources, 531 evidence records and
168 pathways. Countries: AFG, BFA, CAF, CMR, COD, ETH, HTI, IRN, IRQ, LBN, LBY,
MLI, MMR, MOZ, NER, NGA, PNG, PSE, SDN, SOM, SSD, SYR, UKR and YEM.

Lindsey Jones explicitly approved integration of the corrected review package.
The bank preserves the original drafts and review decisions, adds separate
approved copies, and records approval provenance and normalized-text hashes in
`reviews/20261026_production-approval-manifest.json`. The prior current runtime
is preserved in `releases/archive/2026.07.south-sudan-pilot/runtime.json`.
Bank [PR #3](https://github.com/ljonestz/climate-fcv-country-bank/pull/3)
is stacked on the reviewed-drafts branch in PR #2; neither is merged here.

The Word base lacked the approved-schema support already prepared in `3ee149e`.
This integration carries over its four runtime-module changes and synthetic
production tests unchanged. Approval status remains separate from schema support;
reviewed candidates still require explicit preview opt-in. Expired current
evidence and dependent pathways are withheld, with omission limitations retained
through compact grounding and the context adapter. No prompt, rating, route,
reader presentation, export or Word design code changed.

## Verification

- Companion bank: 316 passed, including exact approval metadata, original hashes,
  deterministic dossier generation and release rebuilding.
- Focused app integration: 100 passed, including selection and materialization
  for all 24 countries without a preview token, synthetic approval/expiry cases,
  grounding and Word rendering.
- Word rendering/style/structure checks: 31 passed.
- Broader offline app suite: 1,941 passed, two skipped, four deselected in 299.93s.
- Separate actual-date check: all 24 countries loaded, selected and materialized.
- Independent read-only review: no remaining blockers after carrying over the
  approved-schema support. Approval snapshot tests use 26 October 2026; synthetic
  expiry tests retain their date-boundary checks.
- Diff checks passed. Word base ancestry and unchanged Word assets were verified.

The broader command was `python -m pytest -q -p no:cacheprovider` with these four
previously documented hanging Chromium-driver tests explicitly deselected from
`tests/test_climate_lens_frontend.py`:

- `test_chromium_print_opens_exported_disclosures_and_restores_screen_state`
- `test_result_stage_tabs_do_not_overflow_phone_viewport`
- `test_result_download_header_wraps_inside_phone_card`
- `test_result_session_bar_wraps_inside_phone_viewport`

The first full bank run found one remaining pilot-only current-release assertion.
That test now validates the preserved pilot archive with its original assertions;
the subsequent full run passed. No preservation checks were removed.

## Operational limits and next release

All evidence review deadlines remain unchanged. Only the six expired country-level
deadlines changed, each to its earliest included evidence deadline. BFA, HTI, PNG,
UKR and YEM require renewal after 10 November 2026; SSD after 31 January 2027.
Other country-level deadlines remain unchanged. Evidence-level checks can withhold
current records earlier than their country's overall deadline.

Source coverage remains uneven, especially below national level. Accepted
geographic, causal, source-access and evaluation limitations remain in the dossiers.
Bank approval is not fresh source verification, acceptance of generated assessments,
or permission to publish a report. Existing saved assessments remain version-bound;
they are not rewritten by this integration.

Before any separately authorized hosted release, verify the deployed branch/SHA,
initialize the pinned submodule through `python render_build.py`, and inspect
`CLIMATE_COUNTRY_BANK_PATH`. An old candidate override would still select the old
preview rather than this approved default release. Perform the repository's live
acceptance protocol only with the required deployment and paid-call authorization.

ITS must mirror the approved-schema, freshness and limitation semantics documented
in the private parity contract before adopting this release. ITS code, retrieval,
configuration and acceptance were not changed or certified.

No merge, deployment, hosted configuration change, paid model call, new source
research or additional-country review was performed. Keep both integration
branches and their isolated worktrees for review.
