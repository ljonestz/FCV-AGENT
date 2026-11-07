# Global country-bank test build: 27 October 2026

## Ready for local testing

The expanded bank covers 146 countries: all 84 existing banks and 62 remaining FY27 IBRD borrowers. It adds 1,716 evidence records, including 1,037 named local records, and 58 pathways (18 reverse or bidirectional). Every country has added named local evidence; 54 have new mediated pathways. Coverage and source confidence vary by country.

All expanded candidates remain draft with null human-review metadata. The default app still uses the unchanged approved 24-country runtime. No merge, deployment, hosted configuration change or paid assessment was made.

## Branches and review

| Repository | Branch/base | Draft PR |
|---|---|---|
| App | `feat/global-country-bank-depth-20261026`, stacked on `feat/ida-country-expansion-20261026` (`206e0a5`) | [#89](https://github.com/ljonestz/FCV-AGENT/pull/89) |
| Bank | `feat/global-country-bank-depth-20261026`, stacked on `feat/ida-country-candidates-20261026` (`97dec8a`) | [#5](https://github.com/ljonestz/climate-fcv-country-bank/pull/5) |

Final bank pin: `584c7673f7a11a730dcd94f9ff35a8b19394af30`. The app descends from Word-layout/design commit `3ab33b598492f8f9ee8882d094b00ee2dfa453a3`. Word styles/templates are unchanged by this branch.

Both branches and isolated worktrees are retained. The app worktree is `.worktrees/global-country-depth-app-20261026` under the original FCV-AGENT checkout. The separate research/bank worktree is `.worktrees/global-country-depth-bank-20261026`.

See the pinned bank's [approval table](../data/climate-fcv-country-bank/reviews/20261027_global-depth-approval-table.md), [review manifest](../data/climate-fcv-country-bank/reviews/20261027_global-depth-review-manifest.json) and [source/build guide](../data/climate-fcv-country-bank/research/20261026_global_depth/README.md). Country dossiers link every retained claim to its source locator and record the remaining gaps. Human approval is pending for every depth candidate.

## Start tomorrow's test

Use the existing development environment. From the app worktree:

```powershell
git submodule sync --recursive
git submodule update --init --recursive
cd data/climate-fcv-country-bank
python -m scripts.build_test_bundle --country-manifest research/20261026_global_depth/TEST_INPUTS.json --generated-at 2026-10-27T05:15:31Z --test-expires-on 2026-11-02 --content-version 2026.10.27.global146-test --output releases/testing/20261027_global146-test.json
cd ../..
python -m scripts.run_country_bank_test --bundle data/climate-fcv-country-bank/releases/testing/20261027_global146-test.json --check
python -m scripts.run_country_bank_test --bundle data/climate-fcv-country-bank/releases/testing/20261027_global146-test.json --serve
```

Open http://127.0.0.1:5001/ in Edge. The page must show UNAPPROVED COUNTRY-BANK TEST BUILD. Stop it with Ctrl+C. Do not put these test-mode settings into Render or ITS.

The bundle already exists in the prepared local worktree; skip its builder command there. A fresh checkout must build it. The builder refuses overwrite, so choose a new filename when regenerating and use that same path in the launcher. This build expires after 2 November 2026. Later tests need a fresh generation date, a test window of at most seven days and a new output filename.

The check and page-load verification make no provider calls. Submitting an assessment tomorrow still needs a fresh spending/provider decision and the appropriate local credentials; no credentials were copied into this worktree or committed.

## Verification evidence

- Bank: full suite, 695 passed in 135.07 seconds. Includes all 146 candidates, raw/decision reproduction, strict JSON, references, shared-URL budgets, draft metadata and 878 unchanged baseline-file hashes.
- App: full offline suite, 1,969 passed, two skipped and four known hanging Chromium checks deselected, in 380.35 seconds. The final data pin and handoff do not change the tested application code.
- Final focused app contracts: 28 passed in 4.47 seconds after the final bank checkout..
- Expanded bundle: 146/146 countries selected and materialized in Agriculture, Water and Urban development. All 146 official display names remain single PID beneficiaries; 363 ISO/name/alias resolutions passed.
- Real local HTTP: 200 with the UNAPPROVED banner, no-store and no stale file validators. The test server was stopped. No assessment was submitted.
- Normal startup: approved 24-country bank loads; the expanded artifact requires explicit path, preview token and isolated app-environment settings, plus valid artifact type/checksum/expiry.
- Word-layout ancestor and stacked bases verified with `git merge-base --is-ancestor`. Final diff and staged-file checks exclude source PDFs, generated bundles, raw model responses, logs and credentials.

The full app run used `--ignore-glob=pytest-cache-files-*` and explicitly deselected these existing Chromium hangs:

```text
tests/test_climate_lens_frontend.py::test_chromium_print_opens_exported_disclosures_and_restores_screen_state
tests/test_climate_lens_frontend.py::test_result_stage_tabs_do_not_overflow_phone_viewport
tests/test_climate_lens_frontend.py::test_result_download_header_wraps_inside_phone_card
tests/test_climate_lens_frontend.py::test_result_session_bar_wraps_inside_phone_viewport
```

No complete browser-suite pass, new model-generated assessment, new Word visual inspection or hosted Render-build acceptance is claimed. The local artifact and real app landing page were checked; `render_build.py` remains unchanged.

## Artifact identity

The ignored test bundle is 7,091,301 bytes and contains 1,043 referenced sources, 2,639 evidence records and 240 pathways. The review manifest separately counts 1,094 source-metadata records, including records not referenced by evidence.

- Generated: `2026-10-27T05:15:31Z`; expires: `2026-11-02`.
- Byte SHA256: `916d9c74c7537f60ab831b7e500cd31b0cb5634018824b0180ee48941e5a68b2`.
- Source-manifest checksum: `d489d0043e640421db15b5c9281fcef1529c3c40aa6bfbdd679b1b771a9163cc`.

The unchanged production runtime has 24 countries, 272 sources, 531 evidence records and 168 pathways. UTF-8/LF SHA256: `12f0a7b5c8267ec3a8ed8033f3e4716af69024a9290e023e5264a94ed35ebda8`.

## Review limits and next decisions

Review source confidence, dates and local coverage before production approval. Venezuela's user-uploaded climate-report mirror still needs an official-source check. Protection risk is not an incident count; poverty, migration, refugee identity and nonviolent protest do not automatically imply FCV. Forecasts and administrative labels retain their source vintage.

Inherited evidence deadlines were preserved, including 10 November 2026 for Burkina Faso, Haiti, Papua New Guinea, Ukraine and Yemen, and 31 January 2027 for South Sudan. The short-lived test build does not renew them.

Tomorrow: test representative established FCV and new IBRD countries in the browser, review selected evidence/pathways against original passages, and inspect Detailed HTML/DOCX exports. Obtain designated source approval before assembling a normal expanded runtime release. Hosted deployment, paid runs and production promotion remain separate decisions.

The original checkout's unrelated changes are untouched. An accidental empty, untracked `0))` file remains in the separate bank worktree because its cleanup was denied; it is excluded from all commits and has no build role.
