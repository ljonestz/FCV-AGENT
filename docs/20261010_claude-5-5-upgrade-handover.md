# Handover — Claude 5.5 model upgrade (FCV Project Screener)

**Date:** 2026-10-10
**Status:** ✅ COMPLETE — both standard and climate paths live-verified on Claude 5.5 (all via PRs #74–#78, merged to `main`; production build `e74f364`).
**Production service:** `FCV-AGENT` (Render `srv-d6de99jh46gs73d0jjrg`) → deploys from `main`, autoDeploy on commit → https://fcv-agent.onrender.com
**Render workspace:** `FCV LLM Services` (`tea-d6de2tsr85hc73bqdi0g`)

---

## 1. Objective
Upgrade the whole app from the previous-generation Claude 4.x models to the **Claude 5.5 generation** (released late Sept 2026), using Opus for the reasoning-heavy stages and cheaper models elsewhere.

> **Lesson logged:** the bundled `claude-api` skill's model catalog is cached (June 2026) and lagged the 5.5 release — it wrongly suggested "Sonnet 5.5 doesn't exist." Always verify the current lineup live (WebFetch `https://platform.claude.com/docs/en/about-claude/models/overview.md`). Memory: `feedback_verify_model_lineup_live`.

## 2. Model tiering (the end state)
| Where | Model | Constant |
|---|---|---|
| Core Stage 2 (assessment) + Stage 3 (recommendations) | `claude-opus-5-5` | `app.MODEL_REASONING` (via `_stage_model()` in `_stream_stage`) |
| Stage 1 extraction, web research, Go Deeper, follow-on, priority points, climate lens recovery | `claude-sonnet-5-5` | `app.MODEL_STANDARD` |
| Helpers (country/sector/condense), secondary-doc distillation | `claude-haiku-5-5` | `app.MODEL_LIGHT`; `fcv_distillation.HAIKU_MODEL` |
| Climate verified pipeline (quality mode) | `claude-sonnet-5-5` | `sector_lenses/climate_runtime_config.QUALITY_MODEL` |
| Climate verified pipeline (smoke mode) | `claude-haiku-5-5` | `sector_lenses/climate_runtime_config.SMOKE_MODEL` |

**Opus 5.5 has always-on adaptive thinking** → Stage 2/3 output caps raised (`STAGE_MAX_TOKENS` = {1:8000, 2:32000, 3:32000}; native-climate Stage 3 `NATIVE_CLIMATE_STAGE3_MAX_TOKENS` = 20000, was 9000) so thinking can't truncate the trailing `%%%`/JSON blocks.

Doc-input limits were **not** changed — `main` already had `STANDARD_FCV_PRIMARY_DOC_CHARS = 300_000` for the core route (specialist routes keep 60k).

## 3. PRs merged to `main` (all deployed, all green on tests)
- **#74** — Claude 5.5 upgrade (model tiers, Opus thinking headroom). Merge `35ba2fa`.
- **#75** — remove deprecated `temperature=0` from `climate_verified_client` (5.5 models reject `temperature`/`top_p`/`top_k`). Merge `487ae3e`.
- **#76** — disable adaptive thinking on climate research structuring (Haiku) + verified client, to restore the 4.6-era no-thinking budget calibration. Merge `b837c14`.
- **#77** — make the verified client's thinking-off param **model-aware** (`_thinking_off()`): Sonnet 5.5 requires `{"type":"between_tools"}` (rejects `disabled`); Haiku 5.5 uses `{"type":"disabled"}`. Merge `35b41fc`.
- **(pending) #78** — climate reader rank-order normalization (see §5).

## 4. Verification status — BOTH PATHS VERIFIED ✅
- **Standard FCV path: ✅ live-verified end-to-end** (paid run #1, Somalia STAIRP PID): Stage 1 Sonnet 5.5 (57s, 255k chars extracted), Stage 2 Opus 5.5 (109s), Stage 3 Opus 5.5 (220s). 0 errors, delimiters intact. **Production-ready.**
- **Climate path: ✅ live-verified end-to-end** (paid run #5, same PID, `active_lenses:["climate"]`, build `e74f364`): research `status=partial` (4 sources/claims), Stage 2 verified pipeline `stage_done:2` at 203s with **no `READER_INTEGRITY` error**, `stage_done:3` + `express_done:true`, **0 errors**. Only a benign `Climate bank unavailable: bank_country_unavailable` warning (Somalia not in the curated country bank — graceful fallback). **Production-ready.** All four 5.5-compat fixes (§5) confirmed working together.

### How to run a live verification (the browser upload tool is broken)
The Claude-in-Chrome `file_upload` tool rejects host paths, so verify by **replicating the frontend `/api/run-express` POST** directly. Pattern (a throwaway script, deleted after use):
```python
payload = {
  "assessment_id": str(uuid.uuid4()),
  "documents": [{"name": PDF.name, "type": "pdf",
                 "content": base64.standard_b64encode(PDF.read_bytes()).decode(),
                 "isContext": False, "docRole": "primary"}],
  "review_mode": "design", "user_context": "", "priority_questions": [],
  "active_lenses": [],                 # ["climate"] + "lens_versions":{"climate":"1.1.0"} for a climate run
  "lens_versions": {},
}
# POST to https://fcv-agent.onrender.com/api/run-express, stream the SSE, parse `data: {...}` lines.
```
Test doc: `test_documents/live_acceptance/somalia-stairp-p513127-concept-pid-20260207.pdf`.
Monitor server-side via the Render MCP: `list_logs(resource=["srv-d6de99jh46gs73d0jjrg"], ...)`. The climate research structuring diagnostic logs `stop_reason`/`json_status`/`block_types`; the verified client logs `Climate verified call failure` on 400s only; the `/health` endpoint reports the live build commit.

## 5. The climate pipeline is fragile — the sequence of 5.5-compat issues found
Each paid run surfaced one issue the unit tests couldn't (the verified pipeline is tightly coupled to the old model's behaviour):
1. **`temperature` 400** — 5.5 rejects it. Fixed (#75).
2. **adaptive thinking ate the output budget** — Haiku research structuring truncated its JSON (`block_types=thinking,text`, `stop_reason=max_tokens`). Fixed by disabling thinking + bumping the structuring cap 2500→4000 (#76). Verified working (run #3: `gate_code=ok`, 4 sources/claims).
3. **Sonnet 5.5 rejects `thinking:{"type":"disabled"}`**, requires `between_tools`. Fixed model-aware (#77).
4. **`PRIORITY_RANK_ORDER_INVALID`** — `validate_reader_model` (`climate_verified_render.py:971`) requires priority `rank`s to be exactly `[1..N]`; Sonnet 5.5 emits non-sequential/unordered ranks. **Fixed (PR #78, merge `e74f364`, ✅ live-verified run #5):** `build_reader_model` now renumbers ranks to the sorted position (`climate_verified_render.py` ~696, `enumerate(priorities, start=1)`), preserving the model's intended order; `priority_summary` is derived so stays consistent. Unit test: `test_build_reader_model_normalizes_nonsequential_priority_ranks`.

**Watch for more:** `validate_reader_model` has ~a dozen integrity checks (executive length 300–900 words, judgment dimensions/values/rationale, duplicate titles, drafting completeness, placeholders, truncation, summary match). Run #4 tripped **only** rank-order, so Sonnet 5.5's output otherwise complies — but a different document could trip another. If the next live climate run fails a new `READER_INTEGRITY: *` code, apply the same pattern: normalize format-level invariants in `build_reader_model`; treat genuine quality checks (placeholders, truncation) as real failures to investigate.

## 6. Paid-run budget
User authorised 2 runs, then "one more," then 2 more for the climate tuning. **Used: runs #1–#5** (run #1 standard pass; runs #2–#4 climate issue discovery; run #5 climate end-to-end confirmation ✅). **1 run remains unused.** No further runs needed — both paths verified.

## 7. Status: COMPLETE
Both the standard and climate paths are live-verified on Claude 5.5 and production-ready. Nothing outstanding for the upgrade itself.

**Optional follow-ups (not blocking):**
1. The climate verified pipeline has other strict `READER_INTEGRITY` validators (handover §5) — a very different document *could* trip one. If a future climate screening fails a new `READER_INTEGRITY: *` code, normalize that format-level invariant in `build_reader_model` the same way.
2. Clean up stale remote branches (`feat/model-5-5-and-doc-limits` and the per-fix branches `fix/climate-5-5-*`).
3. The pre-existing 7 test failures on `main` (climate-bank/frontend node-eval) are unrelated to this upgrade and predate it.

## 8. Key files
- `app.py` — `MODEL_*` constants, `_stage_model`, `_stage_output_budget`, `STAGE_MAX_TOKENS`, `NATIVE_CLIMATE_STAGE3_MAX_TOKENS`, `_stream_stage`, climate research structuring call (~8161).
- `sector_lenses/climate_runtime_config.py` — `QUALITY_MODEL`/`SMOKE_MODEL`.
- `sector_lenses/climate_verified_client.py` — `_thinking_off()` (model-aware), the `complete_json` call.
- `sector_lenses/climate_verified_render.py` — `build_reader_model` (rank renumber), `validate_reader_model` (integrity checks).
- `fcv_distillation.py` — `HAIKU_MODEL`.
- Tests: `test_climate_verified_client.py`, `test_climate_research.py`, `test_climate_verified_render.py`, `test_climate_workflow_contract.py`, `test_zone2_constants.py`.
