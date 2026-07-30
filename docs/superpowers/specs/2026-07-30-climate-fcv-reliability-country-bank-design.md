# Climate-FCV Module — Reliability Re-architecture via a Country Bank

**Date:** 2026-07-30
**Branch:** `feat/climate-country-bank` (cut from `feat/climate-readout-redesign` @ `13ce1a7`, v9.22; `main` is a clean ancestor)
**Status:** Design approved in brainstorming; awaiting spec review before planning
**Supersedes:** the mandatory-live-research parts of the 2026-07-28 reliability redesign and the `codex/*` "bounded climate evidence handoff" band-aid line. Retains that spec's reliability safeguards (single deadline owner, primary-diagnostic-required, observable bounded recovery, typed failures).

---

## 1. Problem

Selecting the Climate-FCV lens produces an unreliable assessment. Two independent root causes, only one of which prior sessions attacked:

1. **Prompt architecture (never fixed).** Climate mode runs the *entire generic FCV Stage 2 engine* (~45k chars: 12-OST table, DNH-9, 25-question map, generic narrative, evidence trail, ratings) **plus** a ~13k-char climate suffix that requests the structured diagnostic, in one call. Sonnet reliably completes the generic output and **omits the trailing climate diagnostic block on nearly every run** (confirmed by two live South Sudan PCN runs; not `max_tokens` truncation — trailing-requirement fatigue). This makes a non-streaming ~120s Haiku/Sonnet **recovery call load-bearing on every run**, and that recovery is what times out.

2. **Research as a hard gate (over-attacked, wrong fix).** Climate mode treats live web research as a mandatory precondition. On free-tier Render that research frequently returns **0 accepted sources**, exceeds nested deadlines, or hits Anthropic **HTTP 529** overloads. Prior sessions produced ~30 commits tuning the search (retries, truncation handling, bounded evidence handoff) without removing the dependency, so a research failure still collapses the whole climate assessment.

**Net effect:** a feature that fails or degrades on most live runs.

## 2. Goal

A Climate-FCV assessment that **always completes with substantive, specific grounding**, is genuinely climate-led (not a generic FCV memo with climate bolted on), and does not depend on flaky free-tier live research to succeed — while still using live research, when it works, for the current and sub-national specificity a static knowledge base cannot hold.

Non-goals: changing the standard (non-climate) FCV route in any way; ITS/FastAPI parity (deferred); merging to `main` (stays a clean ITS-compatible baseline — maintainer decision).

## 3. Approved architecture — two-part fix

### Fix A — grounding no longer depends on live search (three layers)

Grounding is assembled from three layers, in descending reliability:

1. **Country climate-FCV bank (bundled, offline-generated) — the reliable floor.** A committed data file of rich per-country profiles for the FCV-relevant universe. Always available at runtime with zero live calls. Guarantees the assessment is never source-less.
2. **Thematic climate-FCV KB (bundled) — the analytical spine.** Already largely present as `sector_lenses/modules/climate/source_notes/*.md` distilled from the 8 curated `docs/climate_module/` PDFs, plus `climate_question_bank.py`. Provides the mechanisms, pathways, and question grounding.
3. **Live web research — the primary source of current + sub-national specificity.** **Always attempted** on every climate run, targeted at the project's country, sub-national hotspots, and up-to-date challenges. **A failure is non-fatal:** the run falls back to layers 1–2. This is the single change that dissolves the failure mode — search stops being a *gate* and becomes *enrichment on a guaranteed floor*.

### Fix B — dedicated climate Stage 2 prompt

When the Climate lens is active, Stage 2 uses a **climate-native base prompt** in which the structured climate diagnostic is the **primary** output, not a trailing suffix:

- The generic FCV engine (12-OST table, DNH-9, 25-question map, generic narrative) is **not run visibly and not requested as a large hidden checklist** in climate mode.
- A **compact internal FCV baseline** (S/R ratings + brief evidence trail) is retained as internal input only.
- Because the diagnostic is the main thing the model produces, it is no longer dropped after a large generic output. **Recovery reverts to a rare exception** (repairing specific missing/invalid fields), bounded and observable — not the de-facto generator.
- The standard FCV route is untouched (separate code path, unchanged prompts/tests).

## 4. Components

### 4.1 `climate_country_bank.json` (new, committed data)

Per-country profiles for the FCV-relevant universe (~50–60 countries): all FY26 FCS economies (35, already in `FCS_LIST`) **plus** high-climate-vulnerability fragile states (ND-GAIN bottom quartile not already in FCS). Rich profile per country, e.g.:

- `country`, `iso3`, `fcs_category` (Conflict / Institutional-and-Social-Fragility / High-Institutional-and-Social-Fragility / not-FCS), `climate_vulnerability` (qualitative band + basis).
- `primary_hazards[]` (e.g. drought, flooding, heat, cyclone, sea-level rise, glacial melt) with brief characterisation.
- `climate_fragility_pathways[]` — the mechanisms by which climate stress interacts with conflict/fragility in *this* country (resource competition, pastoralist–farmer tension, displacement, elite capture of adaptation finance, service-delivery grievance, cross-border spillover).
- `hotspot_regions[]` — named sub-national areas where climate × conflict converge (bank-level, coarse; live search refines).
- `displacement_and_resource_dynamics` — narrative.
- `adaptation_entry_points[]` — conflict-sensitive entry points and institutions.
- `key_uncertainties[]` — what is contested or data-poor (so the model does not over-claim).
- `sources[]` — which thematic notes / general-knowledge basis; `generated_with`, `bank_version`.

Design constraints: source-tagged; explicitly labelled analytical (not OPCS policy, not an official WBG classification); coarse sub-national resolution by design (live search is where fine sub-national/current detail comes from).

### 4.2 `scripts/build_climate_country_bank.py` (new, committed, offline, re-runnable)

Batch-generates 4.1 with Claude, grounded in the thematic notes + general knowledge. Requirements:

- Runs **offline** by the maintainer with `ANTHROPIC_API_KEY`; output committed. Free-tier Render runtime constraints are irrelevant to it.
- **Resumable:** one file per country under a working dir, merged into `climate_country_bank.json` at the end, so AV-scan latency / interruptions never lose completed countries.
- **Regenerable:** re-run to add countries or refresh after literature updates; deterministic country list derived from `FCS_LIST` + an explicit ND-GAIN supplement list kept in the script.
- Emits a per-run manifest (countries generated, model, date, bank_version) for provenance.
- Does **not** read the restricted OPCS corpus; uses only `docs/climate_module/` distillations (explicitly unrestricted) + general knowledge.

### 4.3 Thematic KB (reuse + light consolidation)

Reuse existing `sector_lenses/modules/climate/source_notes/*.md`, `sources.yaml`, and `climate_question_bank.py`. Add a thin accessor if needed so both the bank generator (4.2) and the runtime prompt (Fix B) draw from one canonical thematic source. No re-distillation of the PDFs required.

### 4.4 Runtime wiring

- **Stage 1:** existing country detection → look up the bank profile (bidirectional name/ISO match, mirroring `classify_country`). Attach the profile to `AnalysisState` / lens context. Kick off the bounded live climate search concurrently (as today), owned by a single deadline.
- **Stage 2 (climate-native):** inject bank profile + thematic KB + (if returned in time) live-search evidence into the dedicated prompt. Produce the diagnostic as primary output.
- **Merge rule:** live-search findings take precedence for current/sub-national specifics and are cited as such; the bank fills every field the search did not cover. Provenance is visible (see 4.5).

### 4.5 Graceful degradation (replaces "fail-closed / generate nothing")

| Situation | Behaviour |
|---|---|
| Country in bank, search returns in time (common case) | Full climate assessment: live search drives current + sub-national specifics, layered on the bank; both cited by tier |
| Country in bank, search fails/empties/times out | Full climate assessment from **bank + thematic KB + project doc**; **visible amber note**: "Live country research was unavailable for this run; grounding drawn from the curated climate-FCV knowledge base." Never a hard fail |
| Country **not** in bank, search returns | Assessment from search + thematic KB + project doc |
| Country not in bank, search fails | Assessment from thematic KB + project doc, with a visible note that country-specific external grounding was unavailable; still completes |

The old "mandatory research → generate neither baseline nor climate assessment → offer retry or standard FCV" behaviour is removed for the in-bank case (the common case) and softened to a visible note for the rare bank-miss case.

## 5. Reliability safeguards (retained from the 2026-07-28 spec)

- **Single owner for the total research deadline;** sequential retries may not outlive the parent Stage 1 research budget (fixes the "results discarded after parent timeout" mismatch).
- **Retry only when sufficient budget remains.**
- **Primary diagnostic required on the normal path** (Fix B makes this achievable); recovery limited to missing/invalid fields, preserves valid fields, merges only validated repairs.
- **Recovery streams or emits heartbeats** (no silent ~120s SSE gap).
- **Typed failure states + assessment-ID logging** to distinguish research-empty / diagnostic-omitted / recovery-timeout / provider-529 in Render logs.
- **Anthropic 529 overload retry** (already added in `5323769`) retained.

## 6. Testing (TDD — write failing tests first)

- **Full-prompt isolation:** assert the assembled climate Stage 2 prompt does **not** contain the generic engine (12-OST table / DNH-9 / 25-question map markers) — proves Fix B, guards against regression to generic+suffix.
- **Bank lookup:** in-bank country yields a profile; bidirectional name/ISO matching; unknown country yields a typed "not in bank" state.
- **Degradation matrix:** each row of §4.5 produces a completed assessment with the correct provenance/note (search-success, search-fail-in-bank, bank-miss-search-success, bank-miss-search-fail).
- **Happy path without recovery:** a well-formed primary diagnostic is accepted with **no** recovery call (recovery is the exception).
- **Observable bounded recovery:** when recovery does fire, it is bounded and emits heartbeats; failure is non-fatal.
- **Bank generator:** deterministic country list; resumability (merge of per-country files); schema validation of each profile; runs without touching restricted paths.
- **No regression:** standard (non-climate) FCV route byte-for-byte unchanged; dual-regime tests unchanged; full suite green (baseline 457).

## 7. Branch & integration

- Base: `feat/climate-country-bank` off `feat/climate-readout-redesign` (v9.22 = main + dual-regime + sector-lens platform + climate readout redesign + distilled climate notes + question bank).
- `main` stays the clean ITS-compatible baseline (maintainer decision). No merge to `main` in this effort.
- Deploy to an **isolated Render preview** for maintainer live acceptance (South Sudan PCN + a CCDR, Express): confirm the diagnostic renders on the primary path without load-bearing recovery, live search enriches when available, the amber fallback note appears when search fails, and the assessment is specific and climate-led.
- ITS/FastAPI parity deferred; record the new bank + dedicated-prompt contract in `FCV_BUILD_PARITY.md` when settled.

## 8. Phasing (for the implementation plan)

1. **Thematic KB accessor + country bank generator** (`scripts/build_climate_country_bank.py`) and the committed `climate_country_bank.json` (offline batch by maintainer).
2. **Runtime bank lookup + `AnalysisState` wiring + graceful degradation** (§4.4–4.5), search-failure non-fatal.
3. **Dedicated climate Stage 2 prompt** (Fix B): retire generic+suffix in climate mode; compact internal FCV baseline only; diagnostic as primary output.
4. **Reliability safeguards + observability** (§5): single deadline owner, bounded observable recovery, typed failures/logging.
5. **Live preview acceptance test** + docs (CLAUDE.md version entry, reference docs, parity note).

## 9. Open items to resolve during planning

- Exact ND-GAIN supplement country list (beyond FY26 FCS) — enumerate in the generator; ~15–25 fragile climate-vulnerable economies.
- Bank profile token size vs the Stage 2 budget (`PLATFORM_STAGE_BUDGETS`, `_bounded_stage3_lenses`): profiles must fit the climate-native prompt without reintroducing size pressure; cap/summarise per-country injection.
- Whether the bank also feeds Stage 1 context (country brief) or Stage 2 only — default Stage 2 (+ Stage 3 grounding), to keep Stage 1 lean.
- Confirm the live-search deadline owner boundary in the current pipeline (`build_lens_stage_context`, the research coordinator) before rewiring.
