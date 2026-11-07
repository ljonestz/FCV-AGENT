# IDA country-bank expansion handoff

Status: 60 new draft banks prepared for review; no activation or deployment.

## Branches and review package

- Bank commit: `97dec8a6c5f94f3cc2c8df6e73f9aac51bbfa643`, branch `feat/ida-country-candidates-20261026`, [draft PR 4](https://github.com/ljonestz/climate-fcv-country-bank/pull/4). Stacked on the previous approved-bank branch.
- App branch: `feat/ida-country-expansion-20261026`, based on `7aee6406dcb92ba4573267bccbc5f3f43ff89786`. That integration includes the recent Word design commit `3ab33b5`. This expansion changes documentation only.
- [Approval table](https://github.com/ljonestz/climate-fcv-country-bank/blob/97dec8a6c5f94f3cc2c8df6e73f9aac51bbfa643/reviews/20261026_ida-approval-table.md), [Codex web review instructions](https://github.com/ljonestz/climate-fcv-country-bank/blob/97dec8a6c5f94f3cc2c8df6e73f9aac51bbfa643/research/20261026_ida_expansion/START_HERE.md), [bound manifest](https://github.com/ljonestz/climate-fcv-country-bank/blob/97dec8a6c5f94f3cc2c8df6e73f9aac51bbfa643/reviews/20261026_ida-approval-manifest.json).

## Coverage and status

The [official IDA list](https://ida.worldbank.org/en/about/borrowing-countries), updated 6 July 2026, has 78 FY27 eligible countries. Eighteen already have banks; the 60 new banks complete that roster, including blend and inactive borrowers. Six existing non-IDA banks remain unchanged. Eligibility is not an FCV classification.

New material: 153 source records from 151 distinct URLs, 392 passage-linked evidence records and 14 conditional pathways. Each country has schema 1.1 ledgers, a profile and a deterministic dossier under `countries/ISO/candidates/2026.10.26/`. All approval fields remain draft/null. The manifest binds 372 files; it does not grant approval.

The existing 24-country approved runtime and app submodule pin remain at `cccf251d86a8f3f3a73c930ff8b284c256304c1a`. Do not pin the app to the new draft commit expecting the extra countries to become available: no new runtime release has been built.

## Verification

- Focused expansion checks: 65 passed, covering all 60 countries, exact extraction coverage, source/locator traceability, source budgets, dossiers, draft-promotion rejection, manifest and baseline hashes.
- Full bank suite: 381 passed in 65.96 seconds. A subsequent newline-only contract cleanup updated the manifest hash; the manifest regression passed again.
- Read-only integrity audit and coordinator checks: all 505 baseline files unchanged; 373 additions, no existing bank/runtime/schema/code files modified; staged diff check clean.
- App ancestry and unchanged submodule pin checked. No app code, prompt, route, reader, export, dependency, Word-layout or ITS contract change. The app suite and live UI were not rerun for documentation-only changes.

The default root-discovery validator already fails on 23 old versioned country roots at the baseline. Explicit versioned directories pass validation; the utility remains unchanged. Source PDF access and size limits are recorded per country. Text-level source checks do not imply a complete visual review of every PDF.

## Review and activation boundary

Review the country table and approve named rows against the bound hashes. These are initial banks with uneven depth. Some contain detailed local examples; others rely on national summaries or dated assessments. No completed pathway is asserted for 46 countries. Proposed adaptation measures and reported outputs are distinguished from evaluated effectiveness; conditional pathways are not causal effect estimates.

After approval, use the existing workflow to create approved snapshots and build a validated runtime release. Recheck current claims and expired deadlines, then test all newly available country selections/materializations before updating the app pin. Any changed source, claim or dossier requires a new bound review snapshot. The older 10 November 2026 deadlines are not extended by this work.

No merge, deployment, hosted configuration change or paid application-model call was made. Preserve both feature branches and worktrees.
