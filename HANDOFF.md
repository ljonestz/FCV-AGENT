# Current handoff

### 2026-10-15 full-context paid reviewer check: failed

Two explicitly approved reviewer-only calls are now used; no retries, full run,
deployment or merge occurred. Candidate 94a0f2c used claude-sonnet-5-5 and recorded
108,819 input / 1,068 output tokens. Both native responses validated, but analytical
acceptance failed: all five core recommendations passed, including known scope
errors REC-001/003/005; all four readiness decisions matched; reader review again
rejected valid coordinated wording and missed the flood-ready status overstatement.
A new inclusion objection is recorded with its source nuance. REC-005's financing
scope error was recognized only on its optional draft, leaving the faulty core
approved. More context alone did not solve admission. No further paid authority
remains from this approval; production/ITS acceptance stays held. See
[full results](docs/20261015_climate-full-context-review-results.md).

### 2026-10-15 full-context offline repair (not production accepted)

The user approved an offline repair following quality13. Cited original source
blocks now accompany facts through generation and reader stages so site/activity
and recipient/funding boundaries remain visible. Corrections use unique anchored
sentence/clause edits, preserving surrounding text and evidence; numeric/date
checks and fresh independent meaning review remain mandatory. Research telemetry
recognizes selections and preserves numeric rejection counts, distinguishing
unknown diagnostics from known zero counts without logging source text.

The full-context replay reconstructs 104 source blocks, 60 facts, five core
recommendations, four flags and five reader records; its recorded outcome correctly
fails seven acceptance checks. It separates reconstructed baseline inputs from the
current candidate reader input and never injects expected labels into model input.
The offline validation record is docs/20261015_climate-full-context-repair-validation.md.
Added source context increases input size (43,322 serialized characters per full
context call on quality13); no new model calls or retries were added. No provider
calls, paid assessments or deployments occurred in this repair. Production/ITS
acceptance remains outstanding; saved failures remain unchanged. Draft PR83 and
its worktree are preserved. Do not treat software tests as semantic certification.

### 2026-10-15 quality13: production acceptance failed

The one newly authorized full paid run is used; all six targeted reviewer calls are
also used. Candidate f463684 passed 1,591 offline tests, exact-commit CodeQL and the
four targeted calibration cases, but quality13 failed source-based acceptance.
Assessment 09c194d6-a4f0-40a7-bc9b-3eccfc952f6a completed HTTP200 at 07:10:45UTC.
Four priorities survived; REC-001 misroutes Kasindi through Haut-Katanga feasibility
studies and REC-005 combines separate Burundi/DRC financing pools. The reviewer
admitted false rounding/status contradictions and again rejected valid qualified
reader wording. One real reader status defect was found; its correction introduced
new numeric tokens and was correctly rejected. Summary 198 words was not the issue.
Research returned zero admitted claims; stale structural telemetry cannot establish
why selections failed. See docs/20261015_climate-quality13-acceptance-diagnosis.md.

Production restored to original main 1168a8f by dep-db87rsm89jmc73ciiij0, live
2026-10-15 07:17:29UTC; branch main, On Commit and HTTP200 build health verified.
Preview 23958ae/auto-deploy off; branch/worktree and draft PR83 retained. Actual
browser/HTML/DOCX artifacts are local and agree, including the review-needed fallback.
No further paid call, main merge, ITS deployment or successful ITS handover is
approved by this failed result. Historical allowance statements below are superseded.
The isolated calibration did not generalize; production readiness is not established.

### 2026-10-15 reviewer calibration complete; full acceptance pending

The latest user authority permits six targeted reviewer-only calls and one further
full paid assessment after repairs. All six targeted calls are now used; the new
full run is not yet used. This supersedes historical exhausted-allowance statements
below. No additional reviewer-only calls are authorized.

The repair separates accepted proposed actions from factual evidence, retains
material siting criteria, checks every core premise against source passages, and
calibrates reader review for faithful weaker paraphrases and conditional inference.
Four final calibration cases passed the configured reviewer with native schemas,
exact targets, appropriate per-object reasons and manual source review. Two negative
cases were purified and repeated within the six-call cap; positive payloads and
runtime prompts were unchanged. See docs/20261015_climate-reviewer-calibration.md.

Frozen verification: 1,591 tests passed in339.79 seconds; all157 checked Python/fixture
source hashes unchanged. Independent acceptance review found no remaining blocker.

Versions: facts2.7, analysis2.11, judgments2.15, recommendations2.16,
conditional-review2.16, drafting1.6, compiler1.7, correction1.4,
reader-review1.6, normalization2.8. Renderer2.19 and all schemas/call budgets
are unchanged. No cached-result re-review is implied. Fresh end-to-end analytical,
browser and export acceptance remains mandatory before a successful ITS handover.
Production remains original main1168a8f/On Commit; preview23958ae/auto-deploy off.

### 2026-10-15 quality12 outcome: rollout held

Final combined offline verification: 1,573 tests passed; 163 source/test hashes unchanged.
See the quality12 diagnosis for live failures, offline changes and remaining limits.

Offline follow-up (not deployed): conditional-review2.15 now receives readiness
flags in its existing call and returns passed_readiness_ids. Only explicit, valid,
uncontested acceptances reach output; no-priority runs withhold unreviewed flags
without another call. Flag disputes cannot remove explicitly accepted core actions.
Correction calls clear the flag list. Original flag wording remains reserved against
minor-point duplication, conservatively preventing rejected claims from resurfacing.
Reader-correction1.3 exposes per-target numeric/date tokens while retaining deterministic
rejection. Normalization2.7; renderer2.19 unchanged. These changes are offline verified
only; relational-scope errors and reviewer false positives still require fresh analytical
acceptance. No further paid call is authorized under the exhausted two-run allowance.

Both authorized paid runs are consumed. Quality12 on 23958ae completed HTTP 200,
retained three priorities and two-country research, but failed analytical/native-reader
acceptance. Summary length was valid at 204 words. One initial meaning review ran;
the correction added a date outside the original record and was rejected before any
fresh review. Source checks found unsupported displaced-trader/site linkage, overstated
missing siting criteria, and unverified integrity flags, alongside reviewer false positives.
See docs/20261015_climate-quality12-acceptance-diagnosis.md. Do not admit saved results,
run another paid assessment/provider review, merge, or deploy to ITS.
Production rollback dep-db80ii8u01pc738ev6tg restored original main1168a8f at
2026-10-14 23:00:04 UTC; On Commit and HTTP200 original-build health verified.
The branch preview remains23958ae with auto-deploy off. No successful ITS Word
handover has been authored. Historical statements below about one remaining run
are superseded. Offline safety improvements do not establish fresh analytical acceptance.

October15 quality11 follow-up: the first of two newly authorized paid trials
completed on paid production but failed analytical acceptance (false same-scope
contradiction, incomplete country research, Summary321/288 words without meaning
review). Production was restored to original main1168a8f, On Commit, healthy.
One paid trial remains. Native reader repair now combines initial meaning issues
with repairable text prechecks in one correction, followed by fresh review; length
patches receive220 total words of application-owned paragraph budgets, while the
admission ceiling remains260. Malformed/block reviews skip correction. Research
retains received proof ahead of snippets and reserves coverage within existing
caps. Fact/review prompts verify comparability and residual-gap premises. Versions:
facts2.6, review2.14, compiler1.6, correction1.2, reader-review1.5, normalization2.6.
Renderer2.19 unchanged. See docs/20261015_climate-quality11-repair-validation.md.
Earlier paid-authority restrictions below are historical. Rollout remains held.


Latest October14 authority supersedes the historical restrictions below: the user
authorized further paid acceptance, including a full run if needed, and accepts
modest additional length. Quality10 completed once on4231ab9, retaining five accepted
priorities but withholding native prose solely at the mechanical length gate
(250 then239 words). Native allowance is now260, target160-230; genuine independent
meaning review is still mandatory. See
[quality10 follow-up](docs/20261014_climate-quality10-validation.md).
Production/main/ITS remain held until analytical acceptance. Saved runs are unchanged.

October 14 Climate candidate remains on `fix/climate-opcs-parity` in the preserved
`.worktrees/climate-opcs-parity` worktree; draft PR83 and production/ITS rollout
remain held. Quality9 consumed the single further paid allowance and failed native
reader acceptance before meaning review, retaining four accepted priorities and
five gaps. No further paid run or provider review is authorized. The approved
offline reader contract repair, verification and limitations are recorded in
[reader contract validation](docs/20261014_climate-reader-contract-validation.md).
Local raw evidence is under the worktree's `output/playwright/`; private continuation
notes are in `output/20261014_reader-contract-handover.md`. Do not stage those files
or the unrelated untracked `tests/test_climate_final_reader.py`.

September 21 readability follow-up: see [strengths/gaps bullet formatting](20260921_strengths-gaps-bullets.md).

The current release combines [the September 20 standard-FCV handover](20260920_ITS_handover_standard_fcv.md)
and [the September 21 detailed restoration](20260921_detailed-analysis-restoration.md).
Production at https://fcv-agent.onrender.com follows `main`; this release supersedes
the July rollback and preserves the tested Summary and Detailed templates.
The original technical sections, full actions/drafting and saved-session recovery
are restored. The user authorized main integration and production deployment on
September 21. ITS deployment is separate and has not been performed here.
Analytical limitations remain documented; release approval is not factual approval
of the diagnostic project assessment.

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
