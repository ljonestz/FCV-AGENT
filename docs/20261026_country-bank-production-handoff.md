# Country bank production preparation handoff

The application changes for approved multi-country releases are implemented on `docs/country-bank-approval-20261026`. Evidence approval and deployment remain pending. The bank is unchanged at `12a804fe92bacfdaf0bec7926725d8a7a9376fe4`.

## Implemented

- Approved schema 1.1.0 releases load with an explicit `candidate: false`. Approved schema 1.0.0 remains supported. Reviewed candidates still require the existing path and preview opt-in.
- Schema validation is separate from approval status. Selected countries, evidence and pathways still need approved status outside preview mode.
- Selection excludes expired current-tier evidence and pathways that depend on it. Direct materialization rejects stale selected evidence, including indirect pathway support. Evidence due today remains valid.
- Remaining structural evidence can be used with a canonical omission limitation. The limitation survives both compact grounding and the verified pipeline's existing evidence-gap field.
- Existing context budgets, source checks, normal FCV behavior and model-call counts are unchanged. No dependencies were added.

Changed runtime files: `sector_lenses/climate_bank.py`, `sector_lenses/climate_bank_selector.py`, `sector_lenses/climate_grounding.py`, and `sector_lenses/climate_context_adapter.py`. New contracts are in `tests/test_climate_bank_production.py`.

## Verification

| Check | Result |
|---|---|
| New approval/expiry regression suite before implementation | 14 failed for the intended missing behaviors; 4 existing safety cases passed |
| Initial focused loader, selector and grounding suite | 61 passed |
| Verified-adapter limitation assertion before its fix | Failed because the limitation was dropped |
| Broad offline app suite | 1,913 passed, 2 skipped, 4 deselected; 1,175.42 seconds |
| Final bank, selector, grounding, context-adapter, verified-runtime and verified-pipeline suite | 261 passed; 32.29 seconds |
| Review packet integrity | 36 canonical file hashes, 104 evidence IDs and 37 pathway IDs verified |
| Independent code review, including final adapter follow-up | No introduced defects identified |
| Diff whitespace check | Passed |

The broad suite started before the final adapter handoff fix. The 261-test run covers the final code, including that fix; a second full-suite run was not performed. Four previously documented hanging Chromium tests were deliberately excluded: `test_chromium_print_opens_exported_disclosures_and_restores_screen_state`, `test_result_stage_tabs_do_not_overflow_phone_viewport`, `test_result_download_header_wraps_inside_phone_card`, and `test_result_session_bar_wraps_inside_phone_viewport`. No complete browser-suite or live deployment acceptance is claimed.

Commands used the existing Python runtime and normal process permissions for Windows Temp access. The full run was `python -m pytest tests -q -p no:cacheprovider --tb=short` with those four test names excluded using `-k`. The final focused run used:

```text
python -m pytest tests/test_climate_bank_production.py tests/test_climate_bank.py tests/test_climate_bank_selector.py tests/test_climate_bank_selector_realistic.py tests/test_climate_grounding.py tests/test_climate_context_adapter.py tests/test_climate_verified_runtime.py tests/test_climate_verified_pipeline.py -q -p no:cacheprovider --tb=short
```

## Evidence review status

[First-wave review packet](20261026_first-wave-country-bank-review.md) covers South Sudan, Burkina Faso, Haiti, Papua New Guinea, Ukraine and Yemen. It links to commit-pinned dossiers and source registers, identifies 48 current-tier records, records passage-level spot checks, and binds the scope to file hashes. It is a review aid, not substantive approval of all 104 evidence records.

Required corrections or decisions include:

- PNG-E-001: retain model disagreement in rainfall uncertainty, including model projections of annual decreases.
- BFA-E-009: remove the unsupported cost modifier unless a supporting source is added.
- UKR-E-004: clarify PDF versus printed page numbering in the source locator.
- YEM-E-005: distinguish the expired June-September projection period from the report's October-December projection. Check for a newer assessment and review the separate local-fieldwork claim.
- Review all remaining unchecked source passages, profile syntheses and pathway links. Renew the six expired country review windows only after substantive review.

The candidate files and their existing approval statuses have not been edited. Proposed corrections belong in a new candidate version and require new hashes and sign-off before promotion. Test success cannot establish source accuracy, currentness or causal attribution. A future `review_due` date does not make an old seasonal claim current.

## Remaining release work

Complete the source review, make the agreed corrections in the companion bank, and obtain designated human approval of the exact included records and dossiers. Build a versioned approved release and pin its commit. Preserve the current July South Sudan release for rollback.

Before deployment, verify the intended service, branch, deployed SHA and environment, obtain a specific paid-run allowance for live acceptance, and complete the agreed smoke/quality/export checks. No service configuration, provider budget or production release was changed in this session. The ITS implementation has not been modified or certified; its retrieval differences must be preserved when adopting the shared loader semantics.

The current adapter still does not carry every canonical bank metadata field into model context. This change carries the new omission limitation through the existing evidence-gap field; it does not claim to complete the broader evidence-capsule redesign. Source uncertainties and temporal scope therefore still require review of the canonical dossier and generated assessment.

Keep the branch and isolated worktree for follow-up. New-country collection and the browser research package remain deferred until the existing-bank release work is complete.
