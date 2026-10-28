# IDA country-bank expansion plan

Goal: extend the existing draft-review-approval workflow to every remaining
FY27 IDA-eligible country. Existing approved banks and Word design remain intact.
The official list has 78 members; 18 are already covered, leaving 60 new banks.
Include blend and inactive borrowers, without treating IDA eligibility as FCV status.

- [x] Bind the official eligibility roster and preserve all baseline bank hashes.
- [x] Collect primary-source metadata and passage-level claims in five disjoint
  regional batches. Luna at max handles routine collection/extraction only.
- [x] Coordinator reviews the extracted claims, verifies substantive source
  support, preserves national/subnational scope and builds draft bank ledgers
  using the existing schema 1.1 and dossier generator. Do not invent pathways;
  record missing climate-FCV links as gaps.
- [x] Validate all new directories, references, dossiers, draft approval gates,
  target completeness and baseline preservation. Run focused and full bank tests.
- [x] Prepare a country approval table and version-bound manifest. Publish feature
  branches and draft PRs; retain worktrees. No production release, app pin update,
  merge, deployment or paid application-model call without separate approval.

Files: bank research/20261026_ida_expansion/{TARGET_COUNTRIES.json,
EXTRACTION_CONTRACT.md,extractions/*.json}; countries/ISO/candidates/2026.10.26/
for the 60 new countries; reviews/20261026_ida-*; tests/test_ida_expansion.py.
Validate explicit versioned directories. The default root-discovery CLI already
fails on the baseline's older versioned banks; changing that CLI is out of scope.
App files are documentation only on a branch from 7aee640 (Word-based integration).
No new application code, schema fields, prompts, export changes or dependencies.

Research quality controls reuse research/20261026_browser-review/START_HERE.md.
Current records need short review windows; structural records can use annual
review. Draft dates/null approval fields remain explicit. Existing source dates
and all prior release/current bytes remain unchanged.
