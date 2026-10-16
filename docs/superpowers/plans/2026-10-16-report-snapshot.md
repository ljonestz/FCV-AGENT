# Report snapshot implementation plan

Goal: prevent silent differences between displayed Climate reader and exports.
Approved direction: supervised-production capability audit and user proceed.

Architecture: retain the canonical assessment as authority. Validate its projected
reader, attach canonical provenance, and require exact agreement with the supplied
reader. Expose this no-model check for HTML and reuse it for Word. Reject stale or
reader-only edits with an explicit error; canonical corrections survive. Hash the
assessment/reader pair as an identity, never as human approval. Existing callers
without a reader can still request canonical Word; supplied partial readers fail.
No prompts, ratings, provider calls, auth, approval or deployment changes.

- [x] Add failing tests for matching export, drift rejection, malformed reader,
  canonical corrections and fingerprint changes.
- [x] Implement shared validation and endpoint; route Word and HTML through it.
- [x] Verify browser behavior with executable JS checks and backend/renderer tests.
- [x] Run focused tests, initialize submodule, full suite; inspect diff.
- [ ] Update handoff/reference docs, commit and push existing branch.

## Verification record

Initial failing endpoint test: 404, before implementation. Serialization tests then
exposed tuple/array evidence differences and dictionary-order-dependent evidence
listing; runtime JSON conversion and stable judgment traversal fix those causes.
Focused export/frontend: 106 passed. Connected runtime/export: 48 passed. Final
snapshot suite including missing-reader HTML rejection: 17 passed. Executable Node
checks cover success, refusal, offline error, missing reader and mid-request edits.
Read-only code review found no remaining blockers after missing-reader fix.
Full suite initially interrupted after a reproduced Windows cp1252 subprocess
encoding failure; restarted using python -X utf8. Final full suite: 1,721 passed in 1,064.31 seconds (17:44), Python UTF-8 mode, normal process permissions.
Existing headless browser regressions passed in the full suite. No live-service browser check, provider calls, deployed acceptance or authenticated human review
is claimed. Canonical correction test changes assessment data, not an unauthenticated
reader-only approval. Hash binds supplied metadata; missing provenance is not filled
in or independently verified. Existing stale readers fail closed.
