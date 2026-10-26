# Approved country-bank integration

Approval: Lindsey Jones, 26 October 2026. Scope: the 24 corrected country
drafts at bank commit 79fbe8abde57633120f37b8b0212c6eb7c9531ea.
App base: Word design branch feat/word-readout-redesign, commit 3ab33b5.
No deployment, merge, paid model call, or further country research.

1. Add a failing release acceptance test and update the app's pinned-bank
   contract to expect the approved 24-country release.
2. Preserve the reviewed drafts and historic runtime. Create separate approved
   copies with named approval metadata. Keep every evidence deadline unchanged;
   align the six expired country deadlines to their earliest evidence deadline.
3. Reuse the existing dossier generator and promotion builder. Publish schema
   1.1.0, candidate=false, 531 evidence records and 168 pathways. Bind the input,
   approved copies, archive and output with a normalized-text SHA-256 manifest.
4. Run focused then full bank tests. Commit and push the bank release branch.
5. Carry over the already prepared approved-schema and per-record expiry support
   from 3ee149e, absent from the Word base: climate_bank.py,
   climate_bank_selector.py, climate_context_adapter.py, climate_grounding.py,
   and tests/test_climate_bank_production.py. Preserve existing preview opt-in,
   approval enforcement and ITS retrieval differences. Pin the bank commit.
   Run real-bank selection checks for all 24
   countries, the climate-bank suite, Word design tests, then the full app suite.
6. Record results and limitations in a dated handoff. Commit and push the app
   branch, preserving Word ancestry and the isolated worktrees. Open draft PRs;
   leave production and deployment settings unchanged.

Affected surfaces: bank approval metadata and generated dossiers/runtime;
historic freeze tests (archive resolution only); app submodule pin, approved-bank
loader/selection/limitation propagation and tests; release handoff. No new
schema fields, prompts, routes, reader presentation, exports or Word design code.
ITS must mirror the existing approved-schema/expiry semantics before adopting
this bank; ITS implementation and acceptance are outside this integration.
