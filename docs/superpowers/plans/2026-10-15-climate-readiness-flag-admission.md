# Climate readiness flag admission implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement these steps.

**Goal:** Prevent structurally valid but semantically unreviewed document-integrity and readiness claims from reaching reader/export output.

**Architecture:** Include the existing merged readiness flags in the existing conditional-review request. Return a separate list of explicitly accepted flag IDs and admit only valid, uncontested IDs. Keep core/drafting review outcomes separate, with no new provider call, repair loop, token allowance, or deployment. If no core priorities exist, unreviewed flags are withheld rather than triggering an additional call. Review is not infallible; historical quality12 remains withheld and live acceptance remains outstanding.

**Tech Stack:** Existing Python pipeline, native JSON schema, pytest fake clients.

## Task 1: Demonstrate the bypass and specify admission
- [x] Add focused tests to tests/test_climate_document_integrity.py using existing pipeline fixtures where appropriate. Verify flags are passed with source blocks; absent, malformed, duplicate, unknown or contested acceptance IDs cannot admit flags. Accept one of two flags without losing independently accepted core recommendations. With no priorities, no new reviewer call and no admitted flags.
- [x] Observe failing tests before changing production logic.

## Task 2: Minimal repair
- [x] sector_lenses/climate_verified_schemas.py: separate passed_readiness_ids in conditional_review only; exclude from reader_review schema.
- [x] sector_lenses/climate_verified_prompts.py: review flags against source passages, require comparable contradiction claims and credit existing provisions before asserting absence. Uncertainty is not a proven contradiction. Keep readiness decisions separate from the core verdict/repair targets.
- [x] sector_lenses/climate_verified_pipeline.py: send flags in initial review; explicitly admit subset after response; withhold unreviewed/malformed flags with a diagnostic and correct suppression counts. Do not broaden core/draft correction scope. Clear readiness inputs on correction review calls. Correct the structural helper docstring's overstated guarantee.
- [x] Tests must show native reader schemas do not inherit the new field and correction calls do not resubmit flags. Update version metadata for this contract.

## Task 3: Verify and record limits
- [x] Run focused integrity, pipeline and client/schema tests, then full suite once for final combined offline candidate.
- [x] Inspect diff for unrelated changes, exact saved-quality12 rejection, no provider calls, and immutable archives.
- [x] Update current handoff/reference/private parity, commit and push feature branch only. No deployment, production-ready claim, or successful ITS Word handover without fresh acceptance. Two paid trials are already exhausted.

Verification: 1,573 passed, source hashes unchanged. Independent review closure confirmed.
Implementation retains pre-review reservation of all flag wording deliberately, preventing
rejected claims from resurfacing as unreviewed minor points; this may omit a legitimate
identical-text minor point. See the quality12 diagnosis for this accepted conservative limit.
