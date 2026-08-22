# Current handoff

The current branch-level handoff is
[`docs/20260822_ITS_handover_normal_fcv_summary.md`](docs/20260822_ITS_handover_normal_fcv_summary.md).
It records the completed normal-FCV Summary implementation, shared climate advisory,
detailed-only export boundary, live Render acceptance runs, and ITS parity surface.

The remainder of this file is retained as a historical handoff for the earlier Climate-FCV output-redesign work.

# Climate-FCV Module Rework — Session Handoff

**Date:** 2026-07-24
**Repo:** `ljonestz/FCV-AGENT` (public)
**Worktree (work here):** `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\sector-lens-platform`
**Branch:** `codex/climate-fcv-output-redesign`
**HEAD at handoff:** `da56d23` (Phase 2a WIP)
**Render:** `https://fcv-agent.onrender.com/` — this service is set to auto-deploy **this branch** (not `main`). Every push redeploys. Free tier → ~50s cold start; wake it in a second tab before a run.

---

## 0. Read first (rules + access)
- Read the worktree `claude.md` (dev guide, currently v9.20), the shared `AGENTS.md`, and the private parity contract `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md` before changing prompts, delimiters, priority JSON, routes, or shared schemas.
- **OPCS access restriction (hard):** Do NOT open/read the OPCS policy corpus (`C:\Users\wb559324\WBG\Policy and Procedure Framework - PPFDocuments`, `OPCS docs.xlsx`, the LLM-triage docx, the ESF Manual). Work only from GitHub-Copilot/WBG-LLM-authored summaries. The climate frameworks under `docs/climate_module/` are NOT restricted and ARE the grounding for climate content.
- **Machine quirks:** run python as `C:/WBG/Python313/python.exe`; run tests with `-p no:cacheprovider --ignore-glob=pytest-cache-files-*` (OneDrive pytest-cache crash otherwise); the Edit tool can silently no-op on the OneDrive path (re-read after editing); git staging is lost between tool calls (chain `git add` + `git commit`); no `Co-Authored-By` trailer on commits; the tracked dev guide is lowercase `claude.md`; `docs/superpowers/` is gitignored but force-added on this branch (use `git add -f`).

---

## 1. Overarching goal
Make the **Climate-FCV sector lens** produce a genuinely good, coherent, *climate-led* assessment when selected — not a generic FCV memo with climate bolted on. The user (FCV specialist) confirmed the three real problems: **(a) priority recommendations panel broken/absent, (b) assessment content thin/generic/not lay-readable, (c) rendering/ordering off.** The dedicated-module *framing* is fine; do NOT rebuild from scratch.

## 2. Approved design — Approach C ("climate-native flow")
Full spec: **`docs/superpowers/specs/2026-07-24-climate-native-flow-design.md`** (committed `5679baa`). Read it — it's the source of truth. Essence:
- Today climate mode runs the **entire generic FCV engine** (400–500w memo + 12-OST table + DNH-9 + 25-question map) **AND** a climate layer, in one overloaded call that must also emit a big hidden diagnostic block. That double-run causes the token/timing pressure, the dropped trailing blocks, and the "FCV-only memo."
- Approach C: when Climate is active, branch to a **climate-native flow** — one coherent climate-led note (context/interactions/reflections/dividends/priorities all at the climate-FCV intersection), with the generic engine kept only as **lean internal input** (compact S/R ratings + evidence trail, NOT the verbose tables). Non-climate mode is untouched.
- Phased rollout (spec §8): **Phase 1** graceful priorities gate; **Phase 2** native single-call diagnostic + fluent content; **Phase 3** reflections-as-prose + rendering/ordering; **Phase 4** lean internal ratings/trail.

## 3. THE root-cause insight (most important thing to understand)
Confirmed by two live South Sudan PCN runs: **the primary Sonnet Stage 2 finishes normally but does NOT emit the hidden `%%%LENS_DIAGNOSTIC%%%` block** (no `max_tokens` — it's trailing-requirement fatigue after a huge visible output, not truncation). Stage 3 shows the **same** behaviour: it sometimes omits the trailing `%%%JSON_START%%%` priorities block (download 5 = no priorities; download 6 = 5 priorities — variance).

Consequences:
- The **Haiku diagnostic "recovery"** (v9.18) is therefore the *de-facto* generator on almost every climate run — and its prompt demanded "short evidence-grounded sentences, ≤3 short strings per array," which is exactly why the interaction/reflection/dividend content read **thin and fragmented**.
- The empty priorities panel is caused **upstream** (Stage 3 not emitting the block), not only by the `climate_links` gate.

Recorded in memory: `~/.claude/projects/.../memory/project_climate_primary_omits_diagnostic.md`.

## 4. What this session implemented (all on the branch)
Commit-by-commit (oldest → newest):
1. **`c5cfc43` — v9.20 completeness fix (pushed, deployed, LIVE-VERIFIED in download 4).** Enforces the dedicated-module fields so they're never silently dropped: `climate_readout_is_complete()` + `climate_lens_readout()` in `sector_lenses/pipeline.py`; `extract_or_repair_lens_diagnostic` now recovers on incomplete-but-usable diagnostics and never downgrades a usable primary; the Haiku recovery prompt was extended to request `reflections`/`integration_level`/`integration_summary`/`less_central`/S-R evidence (max_tokens 6000→8000, char budget 12k→16k); honest amber partial-notice in `renderClimateModuleNotice` (frontend + DOCX) when a readout stays incomplete; `_stream_stage` now captures provider `stop_reason` and logs a Stage 2 climate `max_tokens` warning.
2. **`5679baa` — design spec (Approach C).**
3. **`8bd57c6` — Phase 1 implementation plan** (`docs/superpowers/plans/2026-07-24-climate-native-phase1-priorities-gate.md`).
4. **`875f22e` — Phase 1 backend: graceful `climate_links` gate.** `extract_priorities()` no longer returns an error/empties the whole priorities array when a priority's `climate_links` fail — it keeps every priority, tags `climate` only where valid, nulls + counts the rest (`climate_unlinked`/`climate_total`), and threads those counts into both Stage 3 SSE payloads. (Genuine JSON/parse errors still error.)
5. **`41b23ee` — Phase 1 frontend:** captures the counts and shows an honest amber notice ("Climate provenance could not be validated for N of M priorities…"); the panel always renders when priorities exist. **LIVE result:** download 6 rendered 5 priorities (panel works when Stage 3 emits the block).
6. **`16a1835` — observability:** a visible WARNING `"Climate Stage 3 produced no priorities: … json_block=… parse_error=… climate_total=… climate_unlinked=…"` fires when the climate panel would be empty, to pinpoint the exact failure sub-mode on empty runs.
7. **`da56d23` — Phase 2a WIP (CURRENT HEAD; may still be un-pushed — check `git log origin/...`):** fluent interaction narratives.
   - New optional `narrative` field on `interaction_readout` (parser `extract_lens_diagnostic` in `sector_lenses/pipeline.py`, bounded 1600 chars).
   - Primary Stage 2 climate suffix AND the recovery prompt now instruct a **flowing, lay-readable `narrative` per interaction direction** (why-it-matters-first; climate pressure → collision with conflict/fragility in the project's *named* places/components → concrete meaning for activities → what design does → what's unconfirmed; acronyms glossed on first use; one story; no fragments).
   - **Recovery model switched Haiku → `claude-sonnet-4-6`** (since recovery is the de-facto generator, Sonnet gives fluent, project-specific depth). Bounded client timeout unchanged; recovery failure still non-fatal.
   - Render: `renderClimateInteractions` (live/shared HTML) and `add_climate_interactions` (DOCX) now render the `narrative` as flowing prose, falling back to the old stitched pathway strip when absent.

**Approved target voice for the narratives** (user signed off on this register — match it): plain, connected, one story per box, "so what" up front, acronyms explained. Example the user approved:
> *"In the Sudd wetlands, seasonal flooding does more than damage infrastructure — it pushes fishing communities off their land and into areas controlled by armed groups, so a climate shock quickly becomes a security and displacement crisis at the same time. When that happens, people can't reach the landing sites the project is investing in, and the community fishing committees the project relies on to manage access stop functioning. The design partly anticipates this (flood-resilient construction standards), but three things aren't yet pinned down: whether those standards are built against realistic 20–50 year flood projections, whether the project's emergency financing could be released for a flood displacement, and how traders would safely reach cold-storage sites when routes are insecure."*

## 5. Current codebase state
- Full test suite: **366 passed** (`C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*` from the worktree). Frontend contract tests spawn `node` (v22 available).
- `claude.md` version history goes up to **v9.20** (the completeness fix). **Not yet updated for Phase 1 / Phase 2a** — update it when Phase 2 lands.
- **Pre-existing UNSTAGED working-tree changes not made this session** (review before committing anything sweeping): `README.md`, `docs/reference/reference_backend_routes.md`, `docs/reference/reference_frontend_functions.md`, `docs/reference/reference_prompt_architecture.md`, `sector_lenses/README.md`, `docs/superpowers/plans/2026-07-23-climate-fcv-dual-use-output-redesign.md`, `docs/superpowers/specs/2026-07-23-climate-fcv-dual-use-output-redesign-design.md`, plus untracked `docs/20260722_climate_module_unresolved_failure_handoff.md` and `docs/20260723_climate_fcv_output_redesign_handoff.md`. These were on the worktree at session start — decide if they're wanted; they are unrelated to this session's commits.
- **Confirm push state:** `git rev-parse HEAD` vs `git rev-parse origin/codex/climate-fcv-output-redesign`. If `da56d23` isn't on origin, push it (auto-deploys) before live validation.

## 6. Exact next steps (in order)
1. **Push `da56d23` if not pushed, then LIVE-VALIDATE Phase 2a** on the South Sudan PCN (Express). Check: do the two interaction boxes now read as fluent, lay-readable, connected narratives (matching §4 voice) instead of stitched fragments? Confirm the Sonnet recovery actually fires and produces the `narrative` (watch the run time — Sonnet recovery adds ~30–60s vs Haiku; ensure no timeout on free tier). Capture the downloaded HTML + the Render log slice by assessment_id.
2. **Add the missing Phase 2a unit tests** (were not written before the session was cut short): parser accepts/bounds `narrative`; `renderClimateInteractions` emits `climate-interaction-prose` from `narrative` and falls back to the strip when absent; the recovery prompt string contains the narrative instruction; recovery uses `claude-sonnet-4-6` (already asserted in `test_lens_diagnostic_repair_uses_recovery_client_not_fast_client`). TDD going forward.
3. **Apply the same fluency bar to reflections + dividends** (Phase 2 §4): they still read somewhat mechanical/checklist-like. The reflections chip-checklist → prioritised prose is spec Phase 3, but the *content* fluency guidance should extend to reflection `text` and dividend descriptions now that the generator is Sonnet.
4. **Priorities reliability (the real Phase 2 linchpin, spec §3.3):** Stage 3 still omits the priorities block on some runs (variance). Decide between: (a) same trick as Phase 2a — make the effective generator reliable (e.g. a focused Stage 3 priorities emission / retry), or (b) the fuller climate-native Stage 2/3 restructuring that drops the verbose generic engine so the structured output is the reliable primary. The observability WARNING from `16a1835` will tell you the exact sub-mode on an empty run (`json_block=False` → block omitted → needs reliable emission; `json_block=True,parse_error=True` → malformed JSON → robustness/prompt fix).
5. **`climate`-tagged priorities:** `High Climate-FCV materiality produced no climate-tagged priority` still fires because the (recovered) diagnostic's pathway IDs don't match what Stage 3 cites in `climate_links`. A reliable native diagnostic with stable IDs (step 4) should largely fix this; verify priorities get `lens_ids:["climate"]` and the amber "provenance could not be validated" notice disappears.
6. **Then Phase 3 (reflections-as-prose + ordering/hierarchy) and Phase 4 (lean internal ratings/trail)** per the spec.
7. **Deferred:** ITS/FastAPI parity (`FCV_BUILD_PARITY.md`) — the user explicitly said hold this until the climate branch is settled. Then PR to `main` (auto-deploys = public release) once the user is happy.

## 7. Key files & symbols
- `sector_lenses/pipeline.py`: `extract_lens_diagnostic` (parses the diagnostic incl. new `narrative`, `reflections`, `integration_*`), `climate_readout_is_complete`, `climate_lens_readout`, `normalize_priority_climate_links`.
- `app.py`: `build_lens_stage_context` (Stage 1/2/3 lens prompt suffixes incl. the climate Stage 2 diagnostic instruction ~line 900–1015 and Stage 3 branch ~1028+), `repair_lens_diagnostic` (the Sonnet recovery generator), `extract_or_repair_lens_diagnostic` (orchestration: recover on failure OR incompleteness, no-downgrade), `extract_priorities` (graceful climate_links gate ~5264–5300), `_stream_stage` (stop_reason capture), the express `/api/run-express` and step `/api/run-stage` Stage 2/3 blocks, DOCX `download_report` nested helpers (`add_climate_notice`, `add_climate_interactions`, `add_climate_reflections`, `add_climate_dividend_synthesis`, etc.).
- `index.html`: `renderClimateInteractions` (now narrative-prose), `renderClimateModuleNotice`, `renderClimateReflections`, `renderClimateDividendSynthesis`, `climateReadoutComplete`, `renderPrioritiesIntro` (soft link notice), `initStage3UI` (`if(!stageThreePriorities.length) return;` — why the panel skips when empty), `downloadHTML` (export parity).
- Tests: `tests/test_sector_lens_pipeline.py`, `tests/test_sector_lens_app_contract.py`, `tests/test_extract_priorities.py`, `tests/test_climate_lens_frontend.py`, `tests/test_climate_diagnostic_completeness.py`.

## 8. How to run / validate
- Local tests: `cd` to the worktree, `C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`.
- Live: push the branch → Render redeploys → wake the free-tier service → run South Sudan PCN in Express → download the HTML + read the Render log (filter by the `assessment_id`). Distinguish app-stage `TimeoutError` (needs more time / smaller output) from worker OOM/kill.

## 9. Process note for the next agent
This session twice moved to a fix before fully confirming root cause in the running system (the `climate_links` gate was real but not the live blocker; Stage 3 not emitting priorities was). **Confirm the failure sub-mode from a live log line before building the next fix** — the `16a1835` observability warning exists precisely for this.
