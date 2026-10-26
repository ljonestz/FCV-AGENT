# Corrected six-country candidates: handoff

The accepted corrections in the [six-country approval table](20261026_six-country-bank-approval-table.md) have been applied to new companion-bank candidates, version `2026.10.26`.

[Companion-bank draft PR #2](https://github.com/ljonestz/climate-fcv-country-bank/pull/2) contains the revised files at commit `d46e506`. The [review packet](https://github.com/ljonestz/climate-fcv-country-bank/blob/d46e506/reviews/20261026_six-country-corrections.md) links all six dossiers. Its [hash manifest](https://github.com/ljonestz/climate-fcv-country-bank/blob/d46e506/reviews/20261026_six-country-candidate-manifest.json) identifies the exact files awaiting human sign-off.

The package contains 103 evidence records and 35 pathways for South Sudan, Burkina Faso, Haiti, Papua New Guinea, Ukraine and Yemen. All 21 mandatory evidence corrections and 11 pathway corrections were applied, together with source metadata, profile and dependency changes. `BFA-P-005`, `YEM-E-009` and `YEM-P-005` are excluded from the new version. Their originals remain in the earlier candidates.

All new records, profiles and country decisions are explicitly draft, with no named reviewer or approval date. Existing review deadlines were preserved. Human evidence approval remains pending; accepting the correction work did not approve the resulting artifacts for production.

Verification:

- The full companion-bank suite passed: **295 tests**, 105.77 seconds, with normal Windows process permissions.
- Direct content comparison confirmed exactly the 21 evidence corrections, 11 pathway corrections, three exclusions and specified source-date and reuse classifications.
- Checks cover schema 1.1, references, deterministic dossiers, unchanged deadlines, the hashes of 36 new and 38 preserved files, and rejection of draft promotion.
- No existing companion-bank files were modified. The app's submodule remains pinned to `12a804fe92bacfdaf0bec7926725d8a7a9376fe4`; both existing runtime files are preserved.

The interrupted preparation left Haiti and Papua New Guinea as partial copies. The final comparison detected the missing content edits; those edits and draft statuses were completed before validation and the hash manifest were generated.

The next decision is named human sign-off on the linked candidate files, including appropriate review dates and expiry windows. Source-access limitations, historical and local evidence limits, and uncertainty about causal effects remain documented in the dossiers and source reviews. Production release preparation follows that sign-off. No runtime release, paid model call, merge or deployment was performed.

Both feature branches and worktrees are preserved. New-country expansion and its browser collection package remain deferred until the existing-country approval and release work is complete.
