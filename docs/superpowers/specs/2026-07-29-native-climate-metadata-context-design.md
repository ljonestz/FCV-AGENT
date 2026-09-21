# Native Climate Metadata Context Design

**Date:** 29 July 2026
**Branch:** `feat/climate-readout-redesign`
**Status:** Approved for implementation

## Problem

Dedicated Climate-FCV Stage 2 replaces the legacy sector-lens prompt with its
canonical native prompt. Before that replacement, both application routes still
compose the unused legacy prompt. Validated research plus triggered questions
can push that unused prompt beyond the 3,300-token lens ceiling and abort the
stage before any Stage 2 model call.

## Decision

Add an optional metadata-only mode to `build_lens_stage_context()`. It will
retain authoritative lens selection, warnings, normalized context sources,
version checks, and Stage 3 diagnostic normalization while returning an empty
prompt. Dedicated Climate-FCV Stage 2 and Stage 3 will use this mode in both
Express and step-by-step routes because they build their own canonical prompts.
Generic and implementation-review routes retain existing composition.

## Verification

Regression tests will cover the previously failing combination of validated
research and all triggered question-bank signals, and assert that both routes
still invoke the native climate prompt. Existing focused climate and lens
contract tests must remain green.
