# Climate Judgment Timeout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the full-model judgment review complete within a realistic bounded budget while preserving content-free failure telemetry and the original transient error cause.

**Architecture:** Change only the verified JSON call contract and adapter. The call budget remains pipeline-owned and cumulative across attempts; the adapter emits sanitized attempt metadata through an injected logger and chains the original provider exception when no retry time remains.

**Tech Stack:** Python 3, pytest, Anthropic Python SDK, Flask/Render.

---

### Task 1: Lock the timeout and diagnostic contract

**Files:**
- Modify: `tests/test_climate_verified_contracts.py`
- Modify: `tests/test_climate_verified_client.py`

- [ ] **Step 1: Write failing tests**

Add assertions that `CALL_BUDGETS["judgment_review"].timeout_seconds == 120`, a transient failure records only stage/attempt/timing/type/status/size metadata, and an exhausted budget raises a timeout chained from the original exception.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `python -m pytest tests/test_climate_verified_contracts.py tests/test_climate_verified_client.py -q`

Expected: failures for the 60-second budget and missing diagnostic/cause behavior.

### Task 2: Implement the bounded adapter change

**Files:**
- Modify: `sector_lenses/climate_verified_contracts.py`
- Modify: `sector_lenses/climate_verified_client.py`
- Modify: `app.py`

- [ ] **Step 1: Increase only the judgment budget**

Change `CallBudget(12_000, 4_000, 60)` to `CallBudget(12_000, 4_000, 120)`.

- [ ] **Step 2: Add sanitized attempt diagnostics**

Inject an optional diagnostic callback into `AnthropicVerifiedJsonClient`. On provider failure, emit a dictionary containing only `stage`, `attempt`, `elapsed_ms`, `exception_type`, `status_code`, `prompt_chars`, `timeout_seconds`, and `remaining_seconds`.

- [ ] **Step 3: Preserve the original failure cause**

When the cumulative retry budget has no time left, raise the bounded timeout using `raise ... from last_error` and include the last exception class/status without its potentially sensitive message.

- [ ] **Step 4: Wire diagnostics to the existing application logger**

Pass a callback from `_build_verified_pipeline_clients` that logs the allowlisted metadata as one structured line. Do not log prompts, responses, document text, or secrets.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run: `python -m pytest tests/test_climate_verified_contracts.py tests/test_climate_verified_client.py tests/test_stream_stage_timeout.py -q`

Expected: all tests pass.

### Task 2A: Bound recommendation output

**Files:**
- Modify: `sector_lenses/climate_verified_prompts.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`
- Modify: `tests/test_climate_verified_client.py`
- Modify: `tests/test_climate_verified_pipeline.py`

- [ ] **Step 1: Add failing prompt-contract and manifest-version tests**

Require an explicit maximum of three candidates, a 45-word free-text bound, and prompt version `climate-recommendations-v2.2`.

- [ ] **Step 2: Implement the bounded prompt contract**

Add only the explicit cardinality and field-length constraints; retain the 5,000-token ceiling and all existing gates.

- [ ] **Step 3: Run focused tests and verify GREEN**

Run the prompt-contract and manifest tests and expect both to pass.

### Task 2B: Bound conditional semantic review output

**Files:**
- Modify: `sector_lenses/climate_verified_prompts.py`
- Modify: `sector_lenses/climate_verified_pipeline.py`
- Modify: `tests/test_climate_verified_client.py`
- Modify: `tests/test_climate_verified_pipeline.py`

- [ ] **Step 1: Add failing review-contract and manifest-version tests**

Require one object, at most 12 reason codes and object IDs, a 500-word response limit, and prompt version `climate-review-v2.1`.

- [ ] **Step 2: Implement the bounded review contract**

Add only the explicit output-shape and cardinality constraints; retain the semantic review, 2,500-token ceiling, and fail-safe behavior.

- [ ] **Step 3: Run focused tests and verify GREEN**

Run the prompt-contract and manifest tests and expect both to pass.

### Task 2C: Diagnose executive-readout length integrity

**Files:**
- Modify: `sector_lenses/climate_verified_runtime.py`
- Modify: `tests/test_climate_verified_runtime.py`

- [ ] **Step 1: Add a failing integrity-telemetry test**

Require reader-integrity errors caused by executive length to include only the calculated word count.

- [ ] **Step 2: Add the bounded diagnostic**

Append `executive_words=<count>` only when `EXECUTIVE_LENGTH_INVALID` is present; do not expose prose.

- [ ] **Step 3: Run focused and full tests**

Verify the telemetry regression and the complete Climate-FCV suite before a cheap diagnostic smoke run.

### Task 3: Verify, deploy, and capture the replacement result

**Files:**
- Create after success: `docs/20260803_south-sudan-climate-quality-output.md`

- [ ] **Step 1: Run the Climate-FCV regression suite**

Run the verified runtime, client, contracts, pipeline, prompt, workflow, rendering, and app-contract tests plus `compileall`.

- [ ] **Step 2: Commit and push the bounded fix**

Commit message: `fix: allow bounded climate judgment completion`.

- [ ] **Step 3: Verify the deployed commit in smoke mode**

Confirm `/health`, run one South Sudan smoke workflow, and verify all stages, SSD bank selection, reader validation, and exports.

- [ ] **Step 4: Run the authorized replacement quality assessment**

Switch only `fcv-agent-1` to quality, confirm `/health`, run the PCN once, and save the full SSE, assessment, and reader payloads.

- [ ] **Step 5: Create and validate the Markdown note**

Render every reader section and technical-annex field to `docs/20260803_south-sudan-climate-quality-output.md`. Confirm the preview label, complete recommendations or semantic-withholding explanation, reason codes, no truncation, and exact run/build identifiers.

- [ ] **Step 6: Restore smoke mode**

Set only `fcv-agent-1` back to smoke and confirm `/health` before reporting results.
