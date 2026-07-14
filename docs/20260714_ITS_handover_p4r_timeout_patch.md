# ITS Handover Brief - PforR/DPO Stage 2/3 Timeout Patch (and recent main merge)

Date: 2026-07-14

Audience: ITS colleagues maintaining the internal World Bank (FastAPI / Gemini) version of the FCV Project Screener.

Purpose: hand over one important bug fix - the PforR (P4R) Stage 2/Stage 3 timeout - plus a brief pointer to the other changes that just landed on `origin/main`. The timeout patch is the priority; the rest should already be reflected in the internal version from earlier OPCS-consistency work.

---

## 1. Executive Summary

The public/Render app was timing out on Stage 2 and Stage 3 for PforR/P4R operations (reproduced with `PforR_Morocco_GreenGeneration_P170419_PAD`). The same symptom was observed on the internal ITS build.

Root cause on the Render build: an instrument-vocabulary "repair" step (added in the v9.14 OPCS policy-consistency work) ran a **blocking, non-streaming** model call **after** the SSE stream had already finished, and it ran **only for PforR and DPF/DPO**. During that call no keepalives reached the client, so the connection sat idle for 1.5-3 minutes on top of an already-long stream, exceeding the frontend abort budget and tearing the stream as a timeout (`BodyStreamBuffer was aborted`).

Fix: replace the blocking model rewrite with an instant, deterministic in-process regex scrub, and expand the scrub map to cover every banned term. No model call, no idle gap, no truncation.

This is on `origin/main` now (commit `3b04a97`, merged via PR #47, merge commit `234bf43`) and auto-deploys on Render.

---

## 2. Why this is PforR-specific (and why IPF was fine)

The vocabulary rules only exist for two instrument keys: `PFORR` and `DPO`. IPF (and everything else) returns no rule key and skips the whole repair path, so IPF never incurred the extra call and never timed out on this pathway.

Two compounding factors made PforR the one that broke:

1. **The repair fired on nearly every substantive PforR run.** A real PforR PAD (especially an environment/agriculture operation like Morocco Green Generation) almost always contains ESSA/environmental-social discussion, so the generated Stage 2/3 output leaks at least one banned term (`ESS2`, `ESS4`, `SEP`, etc.). Any single hit triggered the repair.
2. **PforR produces the longest outputs in the app.** The P4R overlay asks for DLI-by-DLI analysis, a disbursement-under-conflict headline, program-boundary analysis, ESSA/ESMS and GRM screening, and a `p4r_watch` section. So the stream already ran close to the wall-clock cap (Stage 2 = 6 min, Stage 3 = 8 min) before the blocking repair was added on top.

Timing math that produced the abort:

| Stage | Backend stream cap | Output cap | Frontend abort budget | + silent repair | Worst case |
|---|---|---|---|---|---|
| Stage 2 | 6 min | 16k tokens | 8 min | ~1.5-3 min | ~9 min > 8 min -> abort |
| Stage 3 | 8 min | 20k tokens | 9 min | ~1.5-3 min | ~11 min > 9 min -> abort |

Secondary bug in the same function: the repair used `max_tokens=8000` while Stage 3 output can be 20k tokens, so on long PforR outputs the rewrite truncated the text and dropped the trailing `%%%JSON_START/END%%%` priorities block, breaking priority parsing even when it did not fully time out.

---

## 3. The Fix (Render build)

Files touched: `app.py` and `tests/test_vocabulary_validator.py`. Commit `3b04a97`.

- **`repair_vocabulary_violations()`** no longer calls the model. It now runs a deterministic regex scrub only, using `_VOCABULARY_SCRUB_MAP`, keyed on the instrument. It runs in well under a millisecond, can never truncate, and never opens an idle gap after the stream. It still logs any residual banned term server-side (never surfaced to the user), and never raises.
- **`_VOCABULARY_SCRUB_MAP`** expanded to cover every banned term in `INSTRUMENT_VOCABULARY_RULES`. Previously only `ESS2` and `ESS4` had entries, so `ESS1`, `ESS3`, `ESS5`-`ESS10` would pass through the scrub un-repaired. Word-boundary matching (`\b`) means `ESS1` never matches inside `ESS10`, so entry ordering does not matter.
- The `violations` argument is retained for call-site compatibility but is no longer used (the scrub map is keyed on instrument, not on the specific hits).
- No change to the four call sites (step-by-step Stage 2/Stage 3, express Stage 2/Stage 3) or to IPF behaviour.

Replacement phrasing is intentionally blunt but deterministic, for example (PforR): `ESCP` -> "the Program Action Plan (PAP)"; `ESS4` -> "the ESSA findings on community health and safety"; other `ESSn` -> "the ESSA"; `SEP` / `Stakeholder Engagement Plan` -> "the borrower's GRM". DPF/DPO maps to PSIA / Program Document / policy matrix equivalents.

Verification: 2 new tests (one asserts the repair makes zero model calls; one asserts every banned term including `ESS1`/`ESS6`/`ESS10` is scrubbed for both PforR and DPO). Full suite: 203 passed.

---

## 4. What ITS Needs To Do

The internal build is FastAPI + Gemini, so the code does not port line-for-line. Two cases:

**Case A - the internal build ported the v9.14 vocabulary validator/repair.**
If the internal Stage 2/3 pipeline has an equivalent "detect banned ESF/ESCP/ESS/SEP vocabulary for PforR/DPO, then repair" step, it very likely has the same defect. Apply the same change:

- Make the repair deterministic (a scrub/replace map), not a second model call.
- If a model-based rewrite must be kept, it must (a) run with keepalives/streaming so the client connection does not go idle, and (b) use a token budget at least as large as the stage output cap so it cannot truncate the JSON block.
- Ensure the scrub covers the full banned set (`ESCP`, `Environmental and Social Commitment Plan`, `ESS1`-`ESS10`, `SEP`, `Stakeholder Engagement Plan`), using whole-word matching so short acronyms like `SEP` do not hit "separate"/"September" and `ESS1` does not hit inside `ESS10`.

**Case B - the internal build did NOT port that repair.**
Then the internal timeout is coming from the build-agnostic aggravator alone: PforR simply generates the longest output and runs closest to the stage wall-clock/keepalive limits. In that case, check on the internal build:

- Per-stage server wall-clock limits and client/proxy idle timeouts for Stage 2 and Stage 3, and whether they leave headroom for the longest (PforR) outputs.
- Any post-stream processing (vocabulary repair, retrieval, parsing, DOCX assembly) that runs synchronously after the model stream ends without emitting keepalives. Any such blocking gap should be removed, made async with keepalives, or bounded.
- Keepalive cadence during the model's time-to-first-token and during long generations.

General principle for both cases: **never run a blocking, non-streaming model call (or any multi-second synchronous work) after the SSE stream has ended without keepalives.** That was the exact failure here.

---

## 5. Reference pointers

- Render code: `app.py` functions `repair_vocabulary_violations`, `validate_instrument_vocabulary`, constants `_VOCABULARY_SCRUB_MAP`, `INSTRUMENT_VOCABULARY_RULES`; tests `tests/test_vocabulary_validator.py`.
- Commit `3b04a97`; PR #47; merge commit `234bf43` on `origin/main`.
- Developer guide: `CLAUDE.md` version-history entry **v9.15** documents this fix in full.

---

## 6. Brief note on the rest of PR #47 (should already be in the internal version)

PR #47 also carried three earlier, unmerged pieces of work onto `main` in the same merge. These are prompt/knowledge changes, not infra, and the internal team should already have equivalents from prior OPCS-consistency and feature work. They are listed here only so the diff is not surprising:

- **Priority Points (v9.14, `feat/priority-points`):** an optional "Analysis guidance" box where the user can flag priority points; after a run completes, a separate `/api/run-priority-questions` call produces a "Responses to your priority points" panel. Fired only after the main run, never inline, to preserve the timeout design. See the v9.14 "Priority Points" entry in `CLAUDE.md`.
- **Lending-type differentiation (OPCS):** instrument-aware framing refinements consistent with the earlier Phase 0-6 instrument expansion already covered in the 2026-06-18 ITS handover (`docs/20260618_IT_HANDOVER_RECENT_APP_CHANGES.md`).
- **PforR SEA/SH reframing (`9e6d96a` / PR #48):** SEA/SH guidance for PforR is framed as an ESSA assessment (ESSA Core Principle #6, PAP, ESMS), not as an ESF categorical classification. This matters for the vocabulary work: PforR SEA/SH findings should use ESSA/PAP/ESMS language, never ESF/ESCP/ESS/SEP. If the internal build generates PforR SEA/SH content, confirm it uses the ESSA framing so it does not re-introduce the banned vocabulary the scrub is there to catch.

For the full instrument-expansion baseline and porting sequence, the 2026-06-18 ITS handover remains the primary reference; this brief only adds the timeout patch on top of it.
