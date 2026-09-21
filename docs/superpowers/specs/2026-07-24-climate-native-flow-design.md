# Climate-Native Assessment Flow — Design (Approach C)

**Date:** 2026-07-24
**Branch:** `codex/climate-fcv-output-redesign`
**Status:** Design approved (brainstorming); pending spec review → implementation plan.
**Supersedes (for the Climate lens):** the v9.19 "dedicated module output" execution and the v9.20 completeness patch remain as fallbacks, but the primary generation path is redesigned here.

---

## 1. Problem

Selecting the Climate lens today runs the **entire generic FCV engine** (400–500 word generic memo + 12-OST table + 9-principle DNH + 25-question map + ratings) **and** a climate layer on top of it, in one overloaded Stage 2 call that must also emit a large hidden climate diagnostic block. Consequences observed in live South Sudan PCN runs (2026-07-24):

1. **Diagnostic omitted on the primary call** (not truncation — no `max_tokens`; trailing-requirement fatigue after a huge visible output). The bounded **Haiku recovery** then carries the whole module, producing thin, generic, checklist-style content by construction (its prompt demands "short evidence-grounded sentences, at most three short strings per array").
2. **Priority recommendations panel never renders.** `extract_priorities()` enforces `climate_links` on every priority in an all-or-nothing loop (`app.py` ~5264–5280): one priority whose `climate_links` fail to cite recognized diagnostic IDs returns an error result → `priorities: []` → `initStage3UI()` returns early → no panel. The Haiku-recovered diagnostic's IDs don't match what Stage 3 cites, so this fails on essentially every run.
3. **Output is "generic FCV memo + climate appendix."** Opening Assessment / Operating Context / Strengths / Gaps come from the generic core-FCV Stage 3 prompt and are almost entirely FCV, not climate-FCV.
4. **Reflections read mechanically** (chip-checklist of the six core questions), **interactions/dividends are thin and generic**, not lay-readable, not linked to the specific project, and the ordering/hierarchy reads as a bolt-on.
5. Heaviest, slowest path in the app; closest to the token-window and wall-clock limits.

User-confirmed scope: problems are **priorities broken**, **assessment content quality**, and **rendering/layout**. The dedicated-module *framing* is fine. No ground-up architecture change; the fix is to stop double-running the generic engine in climate mode.

## 2. Goal

When the Climate lens is active, produce **one coherent, climate-led, lay-readable, project-specific climate-FCV note** — generated natively and reliably — instead of a generic engine plus a fragile climate appendix. Non-climate mode is unchanged.

## 3. Approach (C): climate-native flow

The token/timing win is structural: **remove the verbose generic visible engine from climate mode**, which frees the same LLM budget to produce a rich, complete climate diagnostic natively (no trailing-block fatigue, no load-bearing Haiku recovery).

### 3.1 Clean branch
When `climate` is in the active lenses, the pipeline takes a climate-native branch. When it is not, the existing generic pipeline (12-OST/DNH/25-Q engine + all instrument modules IPF/DPF/PforR/MPA/multi-country/mid-cycle/intersection) runs **byte-for-byte unchanged**. This is a hard requirement for safety and testing.

### 3.2 Stage 1 (Context & Extraction)
Unchanged: context extraction, country classification, and the existing concurrent climate research pass.

### 3.3 Stage 2 (Climate-FCV Assessment) — one Sonnet call, lighter than today
The single call emits:
- **Visible:** the climate-FCV assessment — integration readout + a short thematic climate-FCV synthesis. Replaces the generic narrative memo.
- **Ratings block** (`%%%STAGE2_RATINGS%%%`, existing parser): S/R ratings + reasoning, derived from an **internal** OST/DNH/Strategy assessment the model reasons through but does **not** dump as full tables.
- **Compact evidence trail:** a handful of grounded bullets (the "lean internal input" transparency layer), in place of the 25-question/12-OST/DNH verbosity. Surfaced in a compact Under-the-Hood view.
- **Climate diagnostic block** (existing `%%%LENS_DIAGNOSTIC%%%` contract): `integration_level`/`integration_summary`, both interaction directions with stable pathway IDs and specific pathways, dividends (`readout_sections`), 3–5 reflections, `less_central`, and separate `sensitivity_evidence`/`responsiveness_evidence`.

Because the biggest token consumer (the verbose generic visible engine) is gone, this call is smaller and the diagnostic emits reliably on the happy path. The v9.20 completeness check + Haiku recovery remain **only as a genuine fallback**.

### 3.4 Stage 3 (Climate-FCV Note) — one Sonnet call
Produces one coherent, climate-led note with these sections, each sitting explicitly at the climate–FCV intersection, naming the project's actual components/geography, written for a non-technical reader:

1. Materiality & integration readout (orientation).
2. **Climate-FCV operating context** — context framed through the intersection, not generic FCV.
3. Two-way interactions (climate-FCV → project; project → climate-FCV), prose.
4. **Reflections** — prioritised prose on the material core questions; absorbs "what's recognised / what's missing," so it doubles as the climate-FCV strengths/gaps and the separate generic Strengths/Gaps is dropped.
5. Peace & social dividends — qualitative, funds-vs-delivery framing.
6. **Priorities (≤5)** — each tied to a specific interaction/dividend, names components + geography, actionable.
7. Wider FCV context — short note so material non-climate FCV issues aren't lost.
8. Watch List for Supervision — climate-FCV monitoring items with named WBG vehicles.

### 3.5 Priorities gate → graceful (never blanks the panel)
Replace the all-or-nothing `enforce_climate_links` failure with per-priority degradation:
- Validate `climate_links` per priority. Valid → attach + tag `climate` (as today).
- Invalid/missing → **keep the priority**, null its `climate_links`, do **not** tag `climate`, increment an `unlinked` counter.
- Never return an error result solely due to `climate_links`. (Genuine JSON/structural parse errors still surface as today.)
- If `unlinked > 0`, surface one honest soft notice ("climate provenance could not be validated for N of M priorities"). This preserves provenance *validation* (only genuinely-linked priorities are tagged) without deleting the core deliverable — consistent with the app's existing amber-badge/soft-warning pattern.

With the native Sonnet diagnostic providing stable IDs, most priorities link cleanly; the gate stops being a panel-killer.

### 3.6 Sidebar / ratings
Sidebar shows the single climate-FCV integration gauge (visible, as v9.19). S/R ratings are the lean internal input — used for defensibility/export, not a competing visible engine.

## 4. Content-quality bar (prompt-enforced, both stages)
- Name specifics: the project's actual components, sites, geography — never generic "fishing communities."
- Tell a causal story a lay reader follows: pressure → plain mechanism → what it means for *this* project → what the design does/should do. Gloss any jargon.
- Ground in the uploaded document + the climate-FCV frameworks in `docs/climate_module/` (unrestricted). Suppress non-specific points rather than padding the schema.
- "So what" test: every interaction/reflection/dividend must land a decision-relevant point, not restate the document.

## 5. Rendering
- Reflections render as flowing prose with soft inline status language, not scoring chips.
- One clean top-to-bottom order (§3.4 1–8); each point has a single home (no threefold restatement of the same flood-conflict content).
- Integration readout appears both in the sidebar gauge (live) and as a short line in the exported note (DOCX/shared HTML), so the export is self-contained.
- Live HTML, shared HTML, and DOCX stay in parity via the single set of renderers.

## 6. Preserved invariants
OPCS policy-boundary + instrument-awareness guardrails; no-fabrication/citation discipline; specificity/provenance checks; ≤5 priorities; the v9.20 completeness + honest-degradation work (as fallback); the compact-history performance pattern. The OPCS corpus is **not** read by any non-Copilot agent.

## 7. Testing
- Stage 2 climate-native: one native call yields ratings + compact trail + a **complete** diagnostic (reflections + integration + both interactions with IDs); recovery not invoked on the happy path.
- Graceful priorities gate: panel never blanks; unlinked counter + soft notice; genuinely-linked priorities still tagged.
- Reflections-as-prose rendering; export parity (DOCX == live == shared HTML); integration readout present in export.
- Regression: non-climate output byte-for-byte unchanged.
- Live re-validation on the South Sudan PCN.

## 8. Rollout (phased, each independently testable)
- **Phase 1 — Unblock + reliable diagnostic:** graceful priorities gate + native single-call climate diagnostic (drop the verbose generic visible engine in climate mode; keep compact ratings+trail). Fixes the panel and content-depth root cause.
- **Phase 2 — Climate-led note + content bar:** Stage 3 climate-FCV note structure (§3.4) + content-quality guidance (§4).
- **Phase 3 — Reflections-as-prose + rendering/ordering** (§5).
- **Phase 4 — Lean internal ratings/trail polish + Under-the-Hood compaction.**

## 9. Out of scope
- ITS/FastAPI parity (`FCV_BUILD_PARITY.md`) — deferred until the branch is settled.
- A user-selectable climate-primary vs integrated mode.
- Any change to non-climate instrument modules.
