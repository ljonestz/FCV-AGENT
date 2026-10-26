# Remaining-country Climate-FCV bank handoff

The remaining 18 existing country banks have corrected `2026.10.26` draft candidates and passage-level source reviews. The earlier six-country package is unchanged. The user accepted the present coverage for this phase; comprehensive district-level enrichment was not made a release condition.

## Review package

[Companion-bank draft PR #2](https://github.com/ljonestz/climate-fcv-country-bank/pull/2), data commit `79eedc8ddd0c8289cd4255c0ec351cbba7fb8e85`:

- [Country approval table](https://github.com/ljonestz/climate-fcv-country-bank/blob/79eedc8ddd0c8289cd4255c0ec351cbba7fb8e85/reviews/20261026_remaining-country-approval-table.md), with links to all 18 reviews and dossiers.
- [Delivery manifest](https://github.com/ljonestz/climate-fcv-country-bank/blob/79eedc8ddd0c8289cd4255c0ec351cbba7fb8e85/reviews/20261026_remaining-country-review-manifest.json): 108 candidate files and 18 review sheets, identified by SHA-256 of UTF-8 text with LF line endings.
- [Preservation freeze](https://github.com/ljonestz/climate-fcv-country-bank/blob/79eedc8ddd0c8289cd4255c0ec351cbba7fb8e85/reviews/20261026_remaining-country-review-freeze.json): 182 preserved files covering the original candidates, earlier six corrected candidates and both existing runtime files.

All 461 original evidence records and 141 pathways were assessed using the 250-entry source register. Evidence decisions: 262 retain, 166 revise, 33 defer. Pathway decisions: 110 retain, 23 revise, eight defer. The new drafts contain 428 evidence records and 133 pathways; combined with the earlier six countries, the 24 draft candidates contain 531 evidence records and 168 pathways.

Revisions include dates, horizons, geography, locators and calibrated causal wording; a revised record does not necessarily mean its original finding was false. Inaccessible claim-level passages were deferred or the affected subclaim was removed. National baselines and supported local examples were preserved without turning small qualitative cases into national causal findings. Programme plans, outputs and evaluated outcomes remain distinct. Source-access methods and limits are recorded in the individual reviews; not every source was inspected cover to cover.

## Verification and unchanged production boundary

The focused integrity suite passed 20 tests in 20.21 seconds. The full companion-bank suite passed 315 tests in 109.28 seconds with normal Windows process permissions:

```text
python -m pytest tests -q -p no:cacheprovider --tb=short
```

Checks cover decision-to-content alignment, strict duplicate-key parsing, schema 1.1, references and nonempty synthesis links, deterministic dossiers, draft metadata, preserved deadlines, rejection of draft promotion and both hash manifests. Analytical grounding was reviewed separately; structural test success does not establish causal claims.

The app's submodule remains pinned to `12a804fe92bacfdaf0bec7926725d8a7a9376fe4`. No app code, prompts, readers, routes, exports, runtime files or deployment configuration changed. No app/browser integration run or paid model call was made. The source-review branches and worktrees remain available for review; neither PR is merged.

## Browser research package

Local archive:

`source_documents/20261026-browser-review/20261026_remaining-country-browser-review.zip` in the companion-bank review worktree.

SHA-256: `77541256b9040e5a379512c984598d9ba6fef21d52e6c5dc6266a819b48cb4dc`.

The 123-entry ZIP contains original seeds for the 18 countries, schemas, a corrected South Sudan example, instructions and a checksum manifest. CRC, entry count and SHA-256 were checked. No source PDFs or credentials are included. The ZIP is ignored by Git; the [instructions](https://github.com/ljonestz/climate-fcv-country-bank/blob/79eedc8ddd0c8289cd4255c0ec351cbba7fb8e85/research/20261026_browser-review/START_HERE.md) and [target list](https://github.com/ljonestz/climate-fcv-country-bank/blob/79eedc8ddd0c8289cd4255c0ec351cbba7fb8e85/research/20261026_browser-review/TARGET_COUNTRIES.json) are committed.

If the receiving research session supports attachments, upload the ZIP and use its START_HERE prompt for one country at a time. Otherwise use the pinned public-repository links. These are unverified original seeds, not the newly reviewed candidates; there is no need to rerun this completed review. Use the method for later refreshes or an explicitly scoped new-country batch, retaining honest access limits and draft status. The package was not executed in the user's Work/browser account, so attachment and file-return behavior there is unverified.

Returned JSON must be reviewed locally, validated and used to regenerate the dossier. Do not run the current Markdown importer unmodified: its version/date/reference/horizon defaults would silently reintroduce errors.

## Next decision

Human sign-off is still required for the new draft artifacts, including named reviewer, decision, review dates and suitable expiry windows. Existing deadlines were not extended. Approved-runtime generation, app pinning, app verification and any deployment remain separate authorized steps. This handoff does not change the user's no-deployment instruction.
