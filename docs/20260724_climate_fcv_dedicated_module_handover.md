# Climate-FCV Dedicated Module: Session Handover

**Date:** 24 July 2026
**Status:** Implemented, reviewed, tested (351 passed), committed, and pushed. Render deployment of this branch + real-PAD live validation remain.
**Repository:** `ljonestz/FCV-AGENT`
**Worktree:** `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\sector-lens-platform`
**Branch:** `codex/climate-fcv-output-redesign`
**HEAD at handover:** `42f32ad` (`fix: wire wider_fcv_context to sse, colour integration gauge, docx/html parity, render S/R evidence`)
**Remote:** pushed — `origin/codex/climate-fcv-output-redesign` is at `42f32ad`.
**Render app:** `https://fcv-agent.onrender.com/`

---

## 0. Read first (repo rules and access restriction)

- Read the worktree `CLAUDE.md` (now at **v9.19**), the shared `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\AGENTS.md`, and the private parity contract `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md` before changing prompts, delimiters, priority JSON, routes, or shared schemas.
- **OPCS access restriction (critical):** Claude Code / Codex / non-Copilot agents must NOT open or read the OPCS policy corpus (`C:\Users\wb559324\WBG\Policy and Procedure Framework - PPFDocuments`, `OPCS docs.xlsx`, the LLM-triage docx, the ESF Manual, or the folder `C:\Users\wb559324\OneDrive - WBG\OPCS policies and proceedures`). Work only from GitHub-Copilot / WBG-LLM-authored summaries. The OPCS-compliance work in this session came from a WBG-LLM review the maintainer pasted in — see §5 and spec §12.
- Machine quirks: the Edit tool can silently no-op on the OneDrive path (re-read after editing); git staging is lost between tool calls (chain `git add` + `git commit`); the tracked dev guide is lowercase `claude.md` (use `git ls-files` before `git add`); no `Co-Authored-By` trailer on commits.

---

## 1. What this session delivered

Turned the manually-selected Climate lens into a **dedicated climate-FCV module output** (a deliberate reversal of the 23 July "integrated dual-use, never climate-primary" decision). When the Climate lens is active, Stages 1–3 reorient around climate-FCV; the general FCV engine is retained only as an internal input source.

Authoritative design + plan (both committed under `docs/superpowers/`, which is force-added on this branch):
- Spec: `docs/superpowers/specs/2026-07-24-climate-fcv-dedicated-module-design.md` (see esp. §4 output architecture, §12 OPCS guardrails)
- Plan: `docs/superpowers/plans/2026-07-24-climate-fcv-dedicated-module.md` (Phases 1–5, with the OPCS additions appended as Phase 5)
- Supersedes (for the Climate lens): `docs/superpowers/specs/2026-07-23-climate-fcv-dual-use-output-redesign-design.md` and `docs/20260723_climate_fcv_output_redesign_handoff.md`.

---

## 2. Contract additions (the backbone — keep these consistent across layers)

**Stage 2 climate diagnostic** (per-lens entry, `lens_id=="climate"`), parsed in `sector_lenses/pipeline.py:extract_lens_diagnostic`:
- `reflections`: 3–5 × `{question_key, title, status_cue, text}`; `question_key` ∈ `{cq1_interaction, cq2_maladaptation, cq3_dividends, cq4_inclusion, cq5_institutions, cq6_adaptive}`.
- `less_central`: string.
- `integration_level`: `well_integrated | partly_integrated | weakly_integrated | insufficient_evidence`. **Safe default `insufficient_evidence`** (never a middling value) — see `_CLIMATE_INTEGRATION_LEVELS`.
- `integration_summary`: string.
- `sensitivity_evidence`, `responsiveness_evidence`: bounded string lists (kept separate internally per OPCS §12.3).

**Stage 3 priorities JSON**, parsed in `app.py:extract_priorities`:
- top-level `wider_fcv_context`: string|null.
- per-priority `policy_status`: `mandatory_reference | document_commitment | advisory | not_determined` (default `not_determined`).
- per-priority `specialist_referral`: `null` or `{required:bool, route, reason}`; `route` ∈ `{Task Team E&S specialist, RSA, ESF Help Desk, OESRC, Legal, UN engagement team}`.

**Six core questions → grounding** (for prompt wording): cq1←interaction/delivery; cq2←maladaptation/lock-in; cq3←dividends/root-causes; cq4←vulnerable-groups/inclusion; cq5←institutions/HDP; cq6←adaptive/monitoring. Source pool: *Maximizing the Peace and Social Dividends of Climate Action*, *FCV-Sensitive Climate Action Framework*, *Defueling Conflict* series (plus CCDR approach note, adelphi, conflict-sensitive-adaptation literature). The frameworks are files under `docs/climate_module/` and are NOT restricted (unlike the OPCS corpus).

---

## 3. Output architecture (identical across live HTML, shared HTML, DOCX)

Order when climate-valid: **materiality notice → policy boundary → integration gauge/line → interaction Box A → interaction Box B → reflections → dividends synthesis → wider-FCV note → priority panels.**
- Orientation cards retitled: "How relevant is climate to this project?" (materiality) and "How well does the project integrate climate and FCV?" (single gauge, reframed "Indicative Climate-FCV Integration Readout", replaces the two S/R gauges in module mode).
- Interaction sections are **prose in tinted boxes** (the causal-strip/arrow diagram was removed).
- "Reflections on core climate and FCV considerations" block with soft, desaturated status chips + an adaptable intro + a "Less central here" line; renders `sensitivity_evidence`/`responsiveness_evidence` understated.
- Dividends: qualitative prose, funds-vs-delivery framing, references the *Maximizing* report's pathways (soft, not a checklist).
- Wider FCV context: small grey callout, surfaced not developed.
- Per-priority `policy_status`/`specialist_referral` shown understated (live card + export card + DOCX).

Key functions:
- Frontend (`index.html`): `renderClimateModuleNotice`, `renderClimateInteractions`/`renderClimatePathwayStrip` (prose), `renderClimateReflections`, `renderWiderFcvContext`, `renderPriorityCompliance`, `renderClimateDividendSynthesis`, `sidebarHtml`/`updateSidebar` (single gauge + `integrationGaugeFraction` + `intColors`), `renderOut` and `downloadHTML` (climate-valid ordering), SSE handlers set `climateIntegration` and `stageWiderFcvContext`.
- Backend (`app.py`): `build_lens_stage_context` (Stage 2/3 climate prompt branches + the diagnostic-failure branch which stays core-only), `extract_priorities`, `climate_integration_payload`, `climate_lens_entry`, and the `download_report` nested helpers (`add_climate_notice`, `add_policy_boundary`, `add_climate_integration_line`, `add_climate_interactions`, `add_causal_strip`→prose, `add_climate_reflections`, `add_climate_dividend_synthesis`, `add_wider_fcv_context`, `add_priority_compliance`).
- Contract/parse (`sector_lenses/pipeline.py`): `extract_lens_diagnostic`, `_normalize_climate_reflections`, `_CLIMATE_REFLECTION_KEYS`, `_CLIMATE_INTEGRATION_LEVELS`, `normalize_priority_climate_links`.

---

## 4. Budgets

`sector_lenses/budgets.py`: `PLATFORM_STAGE_BUDGETS` Stage 3 raised **900 → 1200** (maintainer-approved) to fit the richer dedicated Stage 3 prompt; `app.py:_bounded_stage3_lenses` default `token_limit` 890→1100 and per-finding cap 700→900. Stage 1 (600) and Stage 2 (2000) unchanged. `build_lens_stage_context` still hard-raises `ValueError` if a stage prompt exceeds its ceiling, so watch these if you add prompt text.

---

## 5. OPCS compliance guardrails (from a WBG-LLM review — spec §12)

A WBG LLM with OPCS-corpus access reviewed the design/plan; the adopted items are implemented as prompt wording (Stage 2/3 climate branches), a UI notice, DOCX text, and the `policy_status`/`specialist_referral` fields:
1. **Policy boundary** — advisory FCV screening only; NOT an ESF/ESS compliance, ESRC, Paris-Alignment, or OPCS determination; does not replace the accredited E&S specialist.
2. **Integration reframe + `insufficient_evidence`** (no material→moderate default).
3. **Separate sensitivity/responsiveness evidence** internally.
4. **Hybrid** `policy_status` + `specialist_referral` (the full four-way `finding_type` taxonomy was deliberately deferred).
5. **Instrument/framework awareness** — don't force IPF/ESF terms on PforR/DPF; state the limitation if the framework is unclear.
6. **CQ2/CQ4/CQ5 refinements** — managed-risk vs new-gap; open-list vulnerability; contextual institutions (not "build vs bypass").
7. **Dividends never framed as requirements.**
8. **Cross-document consistency** — don't call an issue unaddressed if the ESCP/SEP already covers it.
9. **Two source layers** — never present a Layer-2 framework recommendation as an OPCS requirement.

If further OPCS-consistency work is needed, request an updated WBG-LLM/Copilot summary rather than reading the corpus.

---

## 6. Tests + how to verify

Full suite green: **351 passed**. Run from the worktree (the flags avoid a OneDrive pytest cache crash; frontend tests need `node` on PATH):
```
cd "C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT/.worktrees/sector-lens-platform"
python -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```
Focused climate suite:
```
python -m pytest tests/test_sector_lens_pipeline.py tests/test_extract_priorities.py tests/test_sector_lens_app_contract.py tests/test_climate_lens_package.py tests/test_climate_lens_frontend.py tests/test_climate_research.py tests/test_climate_ccdr_context.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```
Regression fixture (extended this session): `tests/fixtures/climate/south_sudan_dual_use.json` now carries reflections/integration/S-R-evidence/wider_fcv_context and per-priority policy_status/specialist_referral.

---

## 7. Remaining work (in priority order)

1. **Deploy this branch to Render.** A push does not auto-deploy unless Render's service branch points at `codex/climate-fcv-output-redesign` (the service normally tracks `main`). On the Render dashboard, set the service branch to this branch OR trigger a manual deploy of it. Free tier: wake it (~5 min, second tab) before a full run.
2. **Live validation on a real PAD/PCN** (the maintainer runs the upload and pastes output). Confirm end-to-end: dedicated climate-FCV narrative; two prose interaction boxes; reflections with the material core questions; single integration gauge (arc coloured, not grey); wider-FCV note visible in the LIVE page and shared HTML (not only DOCX); per-priority policy_status/referral where warranted; ≤5 priorities; DOCX == live == shared HTML. Capture the Render log line by assessment ID if anything stalls (free-tier cold start / worker limits are the usual cause, per v9.16/9.17 notes).
3. **PR to `main`** once live validation holds (branch is 26 commits ahead of the last pushed point; `main` auto-deploys, so a merge is a public release).
4. **Parity log:** add the §2 contract additions to `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md` for the ITS/FastAPI build (`C:\Users\wb559324\WBG\FCV-RISK-PYTHON-API`).
5. **Optional / deferred:** the full `finding_type` taxonomy (verification_route) from the OPCS review (only the hybrid layer was built); a user-selectable Climate-primary vs integrated mode remains out of scope.

Do not weaken source/specificity/horizon/priority-link validation to make output look fuller.

---

## 8. Suggested prompt for the next session

> Continue on the existing worktree, branch `codex/climate-fcv-output-redesign` (HEAD `42f32ad`, pushed). Read the worktree `CLAUDE.md` (v9.19), `AGENTS.md`, the private `FCV_BUILD_PARITY.md`, this handover (`docs/20260724_climate_fcv_dedicated_module_handover.md`), and the spec/plan under `docs/superpowers/`. Do NOT read the restricted OPCS corpus — use WBG-LLM/Copilot summaries. The dedicated Climate-FCV module is implemented and tested (351 passed). The next task is deploying this branch to Render and validating a real PAD/PCN run end-to-end, then a PR to `main`. Correlate any Render stall with logs by assessment ID before changing code. Preserve the contract in §2 of the handover, the strict specificity/provenance validation, the OPCS guardrails (spec §12), and the ≤5-priority maximum.
