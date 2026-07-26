# Handoff — OPCS dual-regime + climate-module OPCS calibration (2026-07-26)

**Context:** the prior session hit ~80% of the context window; this hands the workstream to a fresh session. Read the auto-loaded memory `project_opcs_july2026_process_change.md` FIRST — it holds all confirmed OPCS rules in detail. This doc is the map + next steps.

**Repo state:** worktree `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\sector-lens-platform`, branch `codex/climate-fcv-output-redesign`. Tests: `C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*` (last green baseline 375). Chain `git add`+`commit`; `git add -f` for `docs/superpowers/**`; no `Co-Authored-By`.

## What this workstream is
Two parallel design efforts, both grounded in a series of Copilot/WBG-LLM OPCS reviews (Claude does not read the OPCS corpus except the maintainer's scoped exception; the review outputs are in `C:\Users\wb559324\Downloads\ChatCowork.docx`, `OPCS Regime Routing and Review Rules.docx`, `results 2.docx`, `results 3.docx`, `results4.docx`):

1. **Dual-regime process model** (app-wide foundation) — the July-2026 OPCS overhaul (PAD→Project Paper, OIS, one/two-step, TD/IR/One-Review gates) + the two independent classifier axes.
   - Spec: `docs/superpowers/specs/2026-07-26-dual-regime-process-model-design.md` (commits `f8513ff`, `09548bc`). **Complete; not yet peer-reviewed or planned.**
2. **Climate-FCV readout redesign** (the module the user has been iterating on) — mock v4 `docs/20260725_ss_climate_readout_mock_v4.html`; spec `docs/superpowers/specs/2026-07-25-climate-readout-questions-redesign-design.md` (now with **§12 OPCS calibration** + **§12.9 CDRS/AF/Restructuring/MPA**, commits `8bc56bf`, this session); plan `docs/superpowers/plans/2026-07-26-climate-readout-questions-redesign.md`. **Spec complete + OPCS-calibrated; plan written but predates the OPCS calibration — the plan needs a refresh to add the §12 rules.**

## Sequencing decision already made (with the user)
Dual-regime foundation **first** (its own branch — app-wide); the climate module **consumes** the regime-aware `action_timing`/instrument vocabulary. The climate readout structure is settled; its recommendation calibration is settled (§12).

## Confirmed OPCS rules (all in memory `project_opcs_july2026_process_change.md`)
- Preparation regime: OIS creation date vs **18 Apr 2026** → new (OIS→TD→IR / One Review; Project Paper/Program Paper; DPF keeps Program Document) vs legacy (PCN/PID/PAD/Decision Review). One/two-step risk-driven (FCV ⇒ usually two-step). AF routes by own OIS; restructuring bypasses; MPA phases route individually.
- E&S regime (**separate axis**): Concept Decision date vs **1 Oct 2018** (OPS5.03-DIR.123) → ESF / else legacy-safeguards; exceptions OP/BP 4.03 + exclusively-cost-overrun/gap AF; OP/BP 7.50/7.60 separate screens. 5 `es_regime` values.
- Climate-FCV calibration (§12): instrument-route-first; Paris Alignment + CDRS are separate corporate processes the module flags-not-determines; good-practice≠requirement (no universal 20–50yr horizon); IPF-only ESS map (ESS1/3/4 + conditional 2/5/6/7/10; PforR ESSA; DPF PSIA); CERC constrained; conditional compound-risk wording; primary framework labelled analytical-not-policy; CDRS covers AF/MPA/emergency/CERC/guarantee, no mandatory tool; AF has own package + AF-level CDRS; restructuring change-sensitive; MPA phase-level CDRS.
- `authority_basis` recommendation field; "Public" ≠ "Published".

## Residual "verify with OPCS" (non-blocking)
Full text of "IPF Implementation Support to Project Completion" (restructuring package/ADM); full DPF Program Document section outline (`dpf_sections`); TA-via-IPF ESS treatment; program-level MPA CDRS status.

## Next steps (in order)
1. **Gate-1 peer review of the dual-regime spec** — draft a fresh-session Copilot brief asking it to sanity-check `2026-07-26-dual-regime-process-model-design.md` against the corpus (attach the spec + the key procedures). Fold corrections in.
2. **Refresh the climate plan** to encode §12/§12.9 (instrument-routing, PA/CDRS-flag-not-determine, drop-universal-horizon, `authority_basis`) into its tasks; the climate readout structure tasks are unchanged.
3. **Write the dual-regime implementation plan** (from the spec) — Stage 1 regime+es_regime detection, terminology normalisation (`pad_sections`→`appraisal_document_sections`, `IPF_APPRAISAL_DOCUMENT`), regime-aware `action_timing`, instrument-reference checks, new fields. **Decide the code branch**: recommend a fresh branch off `main` for the app-wide dual-regime work (note `main` currently lacks the timeout fixes + climate work that live on `codex/climate-fcv-output-redesign`; discuss integration order with the user).
4. Then execute plans (subagent-driven or inline).

## Also still open from earlier (pre-OPCS work, on this branch, unbuilt)
The climate readout redesign **implementation** itself hasn't started (plan `2026-07-26-climate-readout-questions-redesign.md`, Phases 1–7). And the branch carries the deployed Stage-1 timeout fixes + climate module (v9.20) already validated. Live PAD/PCN validation of the climate readout redesign is still pending.
