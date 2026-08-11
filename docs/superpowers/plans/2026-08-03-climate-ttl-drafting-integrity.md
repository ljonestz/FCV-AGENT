# Climate-FCV TTL Drafting and Integrity Implementation Plan

> **For the implementer:** Follow this plan with test-driven development. Do
> not lower recommendation admission thresholds, alter the South Sudan bank
> generation process, access restricted raw OPCS/ESF sources, or touch the
> stable `fcv-agent.onrender.com` service.

**Goal:** Make every admitted Climate-FCV recommendation contain useful,
evidence-safe current-document drafting, add a second instrument draft only
when distinct and supported, and fix the South Sudan coherence, readiness, and
live-research provenance defects.

**Architecture:** Extend the verified-v2 native schema and immutable
recommendation model with a structured drafting object. Inject a small
versioned operational-guidance registry selected by document/instrument type.
Keep generation model-authored but make admission, precision, routing,
deduplication, provenance, and rendering deterministic. Continue using the
single canonical reader dictionary for browser, HTML, and DOCX output.

**Stack:** Python 3, dataclasses, Flask, Anthropic native structured output,
vanilla JavaScript, python-docx, pytest.

**Design:**
`docs/superpowers/specs/2026-08-03-climate-ttl-drafting-integrity-design.md`

---

## Task 1: Establish the new drafting contract with failing tests

**Files:**

- Modify: `tests/test_climate_recommendations.py`
- Modify: `tests/test_climate_verified_schemas.py`
- Modify: `tests/test_climate_verified_pipeline.py`

**Steps:**

1. Add fixture helpers for a `DraftingBlock` containing target document,
   target section, status, text, project IDs, residual-gap IDs, and guidance
   IDs.
2. Replace fixture `drafting_language` values with required
   `current_document_drafting` plus nullable
   `operational_instrument_drafting`.
3. Add failing tests proving:
   - missing current-document drafting blocks admission;
   - a null second block is valid;
   - a distinct, evidenced second block is valid;
   - a duplicate second block is dropped with a bounded repair code;
   - unknown drafting fact/gap/guidance references block admission; and
   - the provider schema keeps the second object required-but-nullable so all
     native objects remain closed.
4. Run:
   `python -m pytest -q tests/test_climate_recommendations.py tests/test_climate_verified_schemas.py tests/test_climate_verified_pipeline.py`
5. Confirm the new tests fail because the structured fields do not yet exist.

## Task 2: Add the bounded operational-guidance registry

**Files:**

- Create: `sector_lenses/climate_operational_guidance.py`
- Create: `tests/test_climate_operational_guidance.py`
- Modify: `sector_lenses/climate_verified_runtime.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`
- Modify: `app.py`
- Modify: `tests/test_climate_verified_runtime.py`
- Modify: `tests/test_sector_lens_app_contract.py`

**Steps:**

1. Write failing registry tests for stable IDs, allowed stages/document types,
   permitted target sections, authority class, maximum packet size, unique
   IDs, and absence of mandatory or fabricated paragraph citations.
2. Implement immutable `GuidanceEntry` records and a selector accepting
   `doc_type` and `instrument_type`. Initial entries cover PCN/PAD design,
   results measurement, concept-stage risk/SORT treatment, adaptive
   management, evidenced E&S-instrument routing, and FCV operational
   continuity. Use only summaries already represented in repository guidance.
3. Thread `doc_type` and `instrument_type` from the Express route through
   `_iter_verified_climate_assessment()`, `run_verified_from_doc_parts()`, and
   `run_verified_climate_pipeline()`.
4. Add the selected bounded registry packet to the recommendation-compiler
   input only. Do not add it to fact extraction or use it as proof of a project
   gap/commitment.
5. Run:
   `python -m pytest -q tests/test_climate_operational_guidance.py tests/test_climate_verified_runtime.py tests/test_sector_lens_app_contract.py`
6. Commit checkpoint: `feat: add bounded climate drafting guidance`.

## Task 3: Implement structured drafting and safe routing

**Files:**

- Modify: `sector_lenses/climate_recommendations.py`
- Modify: `sector_lenses/climate_verified_schemas.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`
- Modify: `sector_lenses/climate_verified_prompts.py`
- Modify: `tests/test_climate_recommendations.py`
- Modify: `tests/test_climate_verified_client.py`
- Modify: `tests/test_climate_verified_pipeline.py`

**Steps:**

1. Add immutable `DraftingBlock` with statuses
   `existing_commitment|advisory_proposal`.
2. Replace `CandidateRecommendation.drafting_language` with required
   `current_document_drafting` and nullable
   `operational_instrument_drafting`.
3. Replace successful unresolved routing with
   `standard_document_advisory`. Remove `team_to_confirm` and
   `new_vehicle_may_be_needed` from the native compiler enum; missing
   operational homes belong in readiness flags, not admitted recommendations.
4. Validate the required block against candidate project/gap references and
   the selected registry. Validate a named standalone second target against a
   linked `named_instrument` project fact. Permit standard downstream sections
   only when the registry allows them.
5. Implement deterministic second-block value-add handling: normalize target
   document/section and substantive tokens; drop the optional block when it
   repeats the first target or has very high text overlap. Record
   `DRAFTING_SECOND_BLOCK_REDUNDANT` as a repair, without suppressing the
   otherwise valid recommendation.
6. Update the compiler prompt to require 90-160 words for the first draft,
   request a second only when distinct/useful, forbid team-confirm routing,
   credit existing mitigation, and prohibit invented vehicles.
7. Raise only the drafting-text bounds; retain 45-word limits for other
   compiler fields and the existing three-candidate/token ceiling.
8. Run the Task 1 tests and confirm green.
9. Commit checkpoint: `feat: add evidence-safe climate drafting blocks`.

## Task 4: Add operational precision, authority, and timing safeguards

**Files:**

- Modify: `sector_lenses/climate_recommendations.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`
- Modify: `sector_lenses/climate_verified_prompts.py`
- Modify: `sector_lenses/climate_semantic_review.py`
- Modify: `tests/test_climate_recommendations.py`
- Modify: `tests/test_climate_semantic_review.py`
- Modify: `tests/test_climate_verified_pipeline.py`

**Steps:**

1. Add failing South Sudan-shaped regressions for:
   - invented "PSC Security Risk Management Plan focal point";
   - unsupported "before effectiveness";
   - invented Project Operations Manual;
   - unsupported hydrometeorological system; and
   - mandatory language with reviewer-judgment authority.
2. Extend recommendation validation with a linked-fact context. Named plans,
   manuals, frameworks, protocols, systems, committees, units, and focal
   points must either match linked project facts or use an allowed generic
   standard-section target from the registry.
3. Add timing-pattern checks for effectiveness/appraisal/Board conditions,
   fixed dates, and bounded-day requirements. Require a linked timing or
   authority fact; normal stage-aware placement language remains advisory.
4. Run numeric and named-precision checks over both drafting texts as well as
   decision/action/completion fields. Report field paths and safe reason codes;
   never log prose.
5. Make any drafting block trigger semantic review. Update the reviewer prompt
   to check both blocks, existing mitigation, target existence/scope, actor,
   timing, authority, and unsupported technical precision.
6. Run:
   `python -m pytest -q tests/test_climate_recommendations.py tests/test_climate_semantic_review.py tests/test_climate_verified_pipeline.py`
7. Commit checkpoint: `fix: constrain climate operational drafting claims`.

## Task 5: Enforce judgment evidence and reconcile the executive readout

**Files:**

- Modify: `sector_lenses/climate_judgments.py`
- Modify: `sector_lenses/climate_verified_prompts.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`
- Modify: `sector_lenses/climate_verified_render.py`
- Modify: `tests/test_climate_judgments.py`
- Modify: `tests/test_climate_verified_pipeline.py`
- Modify: `tests/test_climate_verified_render.py`

**Steps:**

1. Add failing tests requiring each non-suppressed judgment to carry at least
   one resolvable evidence ID, including `not_expected` and `not_evidenced`
   outcomes. An `unclear` fallback remains visibly attention-marked and cannot
   be reported as fully verified.
2. Replace dimension-specific missing codes with the bounded shared diagnostic
   `JUDGMENT_EVIDENCE_MISSING` plus the dimension as object ID, while retaining
   invalid-reference and embedded-delivery checks.
3. Tighten the judgment prompt: every dimension must cite the supplied
   registers, and the executive may discuss material residual issues but may
   not state how many pass a later recommendation threshold.
4. Add deterministic `priority_summary` to the reader model after admission and
   semantic review. Generate its count and titles only from final priorities.
5. Render `priority_summary` in browser/HTML/DOCX immediately before ranked
   priorities. Add an integrity test ensuring its count matches final priorities.
6. Run:
   `python -m pytest -q tests/test_climate_judgments.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_render.py`
7. Commit checkpoint: `fix: reconcile climate judgments and final priorities`.

## Task 6: Make readiness flags reference-aware

**Files:**

- Modify: `sector_lenses/climate_recommendations.py`
- Modify: `sector_lenses/climate_verified_schemas.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`
- Modify: `sector_lenses/climate_verified_prompts.py`
- Modify: `tests/test_climate_recommendations.py`
- Modify: `tests/test_climate_verified_pipeline.py`

**Steps:**

1. Add required `residual_gap_ids` to `ReviewReadinessFlag` and the native
   schema.
2. Add failing tests showing RF-002/REC-003-style paraphrases are suppressed
   when they share an admitted residual-gap ID, while a distinct preparation
   uncertainty remains.
3. Change `admit_readiness_flags()` to validate fact and gap IDs and suppress
   flags overlapping final admitted priorities. Retain exact normalized-text
   deduplication as a secondary safeguard.
4. Update the compiler prompt to use readiness flags only for unresolved inputs
   that cannot support an actionable recommendation.
5. Run focused recommendation and pipeline tests.
6. Commit checkpoint: `fix: deduplicate climate readiness flags by evidence`.

## Task 7: Correct accepted live-research provenance

**Files:**

- Modify: `sector_lenses/climate_context_adapter.py`
- Modify: `sector_lenses/climate_run_manifest.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`
- Modify: `sector_lenses/climate_verified_render.py`
- Modify: `tests/test_climate_context_adapter.py`
- Modify: `tests/test_climate_run_manifest.py`
- Modify: `tests/test_climate_verified_pipeline.py`
- Modify: `tests/test_climate_verified_render.py`

**Steps:**

1. Add failing tests proving a live claim is rejected when any declared source
   ID is missing, rather than silently retaining the valid subset.
2. Preserve accepted live evidence IDs separately from retrieval timestamps in
   `RunManifest`. Compute `live_research_count` from distinct accepted
   `CE-LIVE-*` records, not from a `retrieved=` substring that the adapter does
   not emit.
3. Keep retrieval timestamps as optional metadata only; never substitute claim
   IDs into a timestamp field.
4. Add `live_research_count` to the reader technical annex from the canonical
   manifest and assert assessment/reader agreement.
5. Strengthen the analysis/recommendation prompts against composite live claims
   whose material clauses are not jointly supported. Deterministic checks cover
   source resolution; semantic review covers substantive overreach.
6. Run:
   `python -m pytest -q tests/test_climate_context_adapter.py tests/test_climate_run_manifest.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_render.py`
7. Commit checkpoint: `fix: align climate live research provenance`.

## Task 8: Render drafting consistently in browser, HTML, and DOCX

**Files:**

- Modify: `sector_lenses/climate_verified_render.py`
- Modify: `index.html`
- Modify: `tests/test_climate_verified_render.py`
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `tests/test_sector_lens_app_contract.py`

**Steps:**

1. Add failing parity tests for the required current-document label, optional
   operational-instrument label, target document/section, status, guidance
   IDs, full draft text, priority summary, and preview label.
2. Add shared Python helpers to render drafting blocks after minimum action.
   Do not flatten the objects through the generic priority-field loop.
3. Mirror the same conditional structure in `renderClimateVerifiedAssessment()`
   for the live browser and shared HTML export.
4. Add reader-integrity checks for missing/empty first blocks, malformed second
   blocks, and truncated drafting sentences.
5. Confirm one-block recommendations do not render an empty second heading and
   two-block recommendations preserve order in HTML and DOCX.
6. Run:
   `python -m pytest -q tests/test_climate_verified_render.py tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py`
7. Commit checkpoint: `feat: render targeted climate drafting consistently`.

## Task 9: Update contracts, documentation, and the later Cowork handoff

**Files:**

- Modify: `sector_lenses/climate_verified_contracts.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`
- Modify: `CLAUDE.md`
- Modify: `docs/reference/reference_sector_lenses.md`
- Modify: `docs/reference/reference_prompt_architecture.md`
- Modify locally only: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`
- Create locally: `docs/superpowers/plans/2026-08-03-climate-opcs-esf-cowork-review.md`

**Steps:**

1. Advance the verified schema, prompt, reviewer, and renderer versions for the
   intentional contract change.
2. Document the required/optional drafting objects, guidance registry,
   no-team-confirm routing, readiness gap IDs, priority summary, and accepted
   live-research count.
3. Append a dated Render-to-ITS parity entry to the local parity contract. Do
   not copy the local parity document into tracked files.
4. Write a short deferred Cowork review plan limited to:
   - registry propositions that claim operational-guidance status;
   - document/instrument destination appropriateness;
   - mandatory/advisory wording boundaries; and
   - any unresolved ESCP/ESMF/Results Framework placement questions.
   The plan must explicitly exclude general code review, product redesign,
   country-bank generation, and routine output review.
5. Run doc/contract tests and inspect `git diff --check`.
6. Commit checkpoint: `docs: record climate drafting contract and parity`.

## Task 10: Full local verification

**Steps:**

1. Run the complete focused suite:

   `python -m pytest -q tests/test_climate_operational_guidance.py tests/test_climate_recommendations.py tests/test_climate_judgments.py tests/test_climate_verified_schemas.py tests/test_climate_verified_client.py tests/test_climate_context_adapter.py tests/test_climate_run_manifest.py tests/test_climate_verified_pipeline.py tests/test_climate_verified_render.py tests/test_climate_verified_runtime.py tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py`

2. Run the full repository suite:
   `python -m pytest -q`
3. Run `git diff --check`, `git status --short --branch`, and inspect every
   staged diff. Preserve unrelated work.
4. Confirm the country-bank generation files and stable-service configuration
   are unchanged.

## Task 11: Smoke deployment and South Sudan workflow

**Rules:**

- Use only `https://fcv-agent-1.onrender.com`.
- Never modify or test `https://fcv-agent.onrender.com`.
- Testing service branch must be `feat/climate-country-bank`.
- Candidate path must remain
  `data/climate-fcv-country-bank/countries/SSD/candidates/2026.08/runtime.json`.
- Candidate preview must remain `reviewed-candidate`.
- Set `CLIMATE_VERIFIED_RUN_MODE=smoke`.

**Steps:**

1. Push the clean feature history and confirm Render deploys the intended
   commit.
2. Confirm `/health` reports that commit, smoke mode, and expected runtime.
3. Upload the South Sudan PCN and run full Climate-FCV Express.
4. Verify every stage, SSD bank selection, final reader, validation, and
   HTML/DOCX availability.
5. Save the complete smoke note as a new local Markdown/text artifact. Treat
   its prose only as workflow output.
6. Check that final-priority count, priority summary, judgment evidence,
   readiness flags, provenance count, one/two drafting blocks, and preview
   labels are coherent.
7. If anything fails, diagnose its exact stage and add a regression before
   changing implementation.

## Task 12: One paid quality run, textual capture, and assessment

1. Send the user a concise update immediately before changing the testing
   service to quality and initiating the paid call.
2. Change only `fcv-agent-1` to `CLIMATE_VERIFIED_RUN_MODE=quality` and confirm
   the service is healthy.
3. Run the South Sudan case once with the full models.
4. Save the full final recommendation note as a new local Markdown or text file
   so it remains directly reviewable without browser visuals.
5. Assess factual accuracy, existing-mitigation representation, residual-gap
   logic, instrument existence/scope/timing/authority, judgment coherence,
   recommendation utility, drafting usefulness, readiness boundaries,
   unsupported precision, truncation, research provenance, and export parity
   against the handover's Example B/C standard.
6. Return `fcv-agent-1` to smoke and verify `/health`.
7. Report the saved output path, exact deployed commit, test results, quality
   findings, remaining limitations, and the separate optional Cowork guidance
   review plan.
