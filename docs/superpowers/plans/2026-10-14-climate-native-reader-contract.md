# Climate native reader contract implementation plan

> For agentic workers: execute inline with superpowers:executing-plans in the existing isolated worktree. User approved the design in docs/20261014_climate-reader-contract-diagnosis.md. No paid calls.

Goal: replace whole-reader copying and vocabulary guesses with application-owned text patches, exact mechanical diagnostics and mandatory meaning review.

Architecture: add a text-only reader_correction response. Merge exact requested IDs into a deep copy, retaining all evidence and other fields. Native admission checks mechanical constraints; independently reviewed meaning remains mandatory. Strict normal FCV Summary stays unchanged.

Tech stack: existing Python functions, provider JSON schemas and pytest; no new dependencies.

- [x] Add failing pipeline tests for native ordinary vocabulary, text-only repair, original-response retention, exact word counts, immutable fields and semantic rejection. Run only these tests to prove the defects.
- [x] Update climate_final_reader.py with text-patch merge and precise diagnostics. Add the native mechanical-check option in climate_verified_schemas.py, retaining numeric/date/reference/format/length checks.
- [x] Add reader_correction schema, prompt and existing-reader budget alias. Update client metrics scope, pipeline merge/review loop and bounded private diagnostics. Irreparable unknown evidence/IDs must fail without a pointless text repair.
- [x] Align connected correction expectations to the new contract; test partial patches, missing/extra/duplicate IDs, extra metadata, budget exhaustion, zero retries, cancellation, review failures and export/reload admission.
- [x] Replay saved quality8/9 reader outputs offline, explicitly preserving fallback without a real clean meaning review. Save diagnostics locally only.
- [x] Run connected reader/pipeline/client/schema/render/export checks, syntax/diff checks; initialize the pinned submodule and run the full suite once in a normal process. Do not call providers. Full 1,544 passed in 263.76s with UTF-8 child and frozen source/tests; the first encoding-failure run was stopped and preserved.
- [ ] Update guide, reference, validation/handover and draft PR. Inspect staged files; commit/push reviewed source/tests/docs only. Verify exact test deployment and CI, with no assessment. Keep production and ITS held.

Acceptance: real archived failures have precise diagnostics; ordinary vocabulary reaches independent review; malformed/unsupported/unreviewed outputs cannot be displayed; patches preserve source and action scope; one correction shares the existing deadline and 9,000-token allowance with zero correction retries. Offline checks establish software behavior, not hosted analytical acceptance.
