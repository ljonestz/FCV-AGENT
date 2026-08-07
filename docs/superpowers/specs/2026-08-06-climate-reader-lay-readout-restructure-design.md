# Climate Verified Reader — Lay Readout Restructure

**Date:** 2026-08-06
**Branch:** `feat/climate-reader-lay-comprehensibility`
**Status:** Design approved; ready for implementation planning

## Motivation

A blind test compared four FCV screening outputs of the same South Sudan concept-stage
PCN. Three independent evaluators (an internal WB LLM, Copilot, and an external Claude
Code review) scored them. The full-app output ("Example D") placed first or second in
every evaluation, but the evaluations converged on a consistent set of **cross-context**
weaknesses in how the app's output is *structured and surfaced* — not in its analysis.

This spec captures only the recommendations that generalise to **any** project and
context (South-Sudan-specific findings are explicitly out of scope). It targets the
**climate verified reader** output surface (`sector_lenses/climate_verified_*`), which is
what produced Example D.

Key realisation from code exploration: **most of the desired structure already exists in
the pipeline but is buried or mislabelled.** This is therefore primarily a
reorganisation + prompt-tuning round, not net-new generation — low risk.

## Scope

**In scope**
- The climate verified reader reader-model + HTML/DOCX render (`climate_verified_render.py`).
- The prompts/schemas that feed it (`climate_verified_prompts.py`, `climate_verified_schemas.py`).
- The priority admission/ranking count cap (`climate_recommendations.py` / `climate_verified_pipeline.py`).
- Two new cross-context diagnostic checks (prompt-level).

**Out of scope (this round)**
- The general (non-climate) FCV Stage 3 output. We *factor* the new overview block so the
  general run can adopt the same top-of-report pattern later, but change no general-run code.
- Any South-Sudan-specific content or knowledge-bank changes.
- The ITS/FastAPI parity mirror (tracked separately as B1 in the handover).

## Design decisions (resolved during brainstorming)

1. **Judgment/priority relationship — clean split (diagnose vs act).** Core-question
   panels are a pure diagnostic layer: a finding plus a single `Watch:` line *or* a bare
   `→ see Priority N` pointer. They never contain the fix. All "how" lives once, in the
   priorities. Repetition is eliminated by construction.
2. **Promotion rule.** Any judgment call material enough to need action MUST surface as a
   ranked item downstream (priority or quick-fix). The reader is never left with a flagged
   issue and no direction — but the direction is written once, where it belongs.
3. **Three actionability tiers**, each finding in exactly one tier by a materiality gate:
   - **Priorities** — deep, ~3–5, full drafting/mechanism/who-when.
   - **Quick fixes** — brief prose *how to address*, no full drafting apparatus.
   - **Watch** — monitor-only, no action now.
4. **Count is materiality-driven**, soft target ~3, hard cap 5. Remove the `[:3]` code
   truncation that currently overrides the prompt's stated max of five.
5. **Routing metadata dropped from reader view** (`routing_status`, `authority_basis`,
   `recommendation_basis`, `pathway_ids`). Internal scoring/routing fields with no lay meaning.
6. **Evidence codes hidden from visible tiers.** `PF-`/`RG-`/`ER-`/`PW-` codes are removed
   from Overview/Priorities/Quick-fixes/Watch and kept only in the "How this analysis was
   produced" fold (which already carries a code→source legend).
7. **Two new analytical checks included** (see below).

## New reader order

1. **Overview** *(new placement)* — a 2–3 sentence plain-language readout **plus the
   sensitivity rating scale lifted to the very top.** Today the readout is prose-only at
   the top and the rating scale sits lower, inside Core Questions. The rating scale render
   (`_sensitivity_rating_html`) is factored into a standalone "overview block" unit so the
   general FCV run can reuse it later.
2. **Core questions** *(diagnosis only)* — finding + `Watch:` line or `→ see Priority N`
   pointer. Solution/how-to language removed via prompt change.
3. **Priorities** *(deep, ~3–5)* — unchanged card content; count cap raised (decision 4).
4. **Quick fixes** *(new visible tier)* — surfaced *out of* the collapsed Points-to-check
   fold. Sourced from the existing `minor_climate_points` (`point`/`why`/`how_to_check`)
   and the genuinely-actionable `review_readiness_flags` / `document_integrity_findings`.
   Reframed from "how to *check*" to brief "how to *address*". This is where
   document-consistency / hygiene / placeholder items land — legible prose, not metadata,
   not inflated into full priority cards (Example D's penalised failure mode).
5. **Watch** *(monitor-only)* — from the core-question watch-lines plus non-actionable flags.
6. **How this analysis was produced** *(kept, collapsed)* — methodology note, pathways,
   evidence key (the `PF-`/`RG-`/`PW-` legend), sources. The transparency/audit fold.

**Retired from reader view:** the routing/authority/recommendation-basis/pathway-ids rows
(decision 5); inline evidence codes in the visible tiers (decision 6).

## Tiering discipline (prompt + pipeline)

- A materiality gate assigns each finding to exactly one tier: deep-priority → quick-fix →
  watch. The prompt must state the one-finding-one-tier rule explicitly so the model does
  not restate a priority as a quick-fix or a watch line.
- Remove the `[:3]` slice in `admit_and_rank` (`climate_recommendations.py:884`, called at
  `climate_verified_pipeline.py:1192`); enforce a hard cap of 5 there instead. Align with
  the prompt language that already says "approximately three … hard maximum of five."
- **Confirm during planning** which priority path actually feeds the verified reader:
  `climate_verified_pipeline.admit_and_rank` vs `climate_native.build_priorities`
  (`_native_climate_stage3` in `app.py`). The count change must be applied on the live path
  and kept consistent across both if both can render.

## Calibration guardrails (cheap, cross-context, prompt-level)

Fold into the existing fact-extraction / verification prompts (`climate_verified_prompts.py`):
- **Do not expand an acronym the source already defines.** Use the source's own expansion
  verbatim or leave the acronym (evaluators caught "Beach Fisheries Management Units" where
  the source said "Boma Fisheries Management Units").
- **Preserve a number's verb on paraphrase.** "over one million *affected*" must not become
  "*displaces* over one million" — affected ≠ displaced.
- **Separate verified from attributed claims.** A fact confirmed from the uploaded document
  reads differently from a policy/threshold claim sourced from external/internal guidance
  the tool cannot verify; the latter must be visibly marked as to-confirm.

## Two new analytical checks (prompt-level, generic)

Added to the diagnostic stage; no new pipeline sections.
1. **Conflict-geography ↔ project-site overlap.** Cross-reference conflict/fragility
   locations named in the source (or context) against the project's own named implementing
   locations, and report whether the conflict analysis actually lands on where the project
   operates. Purely generic; high value.
2. **Quality-of-participation vs quota-compliance.** Where the project mandates
   representation/quotas, check whether the *quality* of participation (voice in real
   decisions) is monitored, not merely whether a quota is met on paper.

## Files likely touched

- `sector_lenses/climate_verified_render.py` — reader-model assembly (`build_reader_model`),
  section order in `render_reader_html`, factor the overview block, new Quick-fixes / Watch
  rendering, drop routing metadata + inline codes, DOCX export parity (~line 1051+).
- `sector_lenses/climate_verified_prompts.py` — core-question diagnosis-only framing,
  tiering/materiality/promotion rule, how-to-address reframe for minor points, calibration
  guardrails, two new checks.
- `sector_lenses/climate_verified_schemas.py` — any field renames/additions for the tiering
  (e.g. quick-fix how-to-address field) and the two new checks.
- `sector_lenses/climate_recommendations.py` — replace `[:3]` with hard-cap-5.
- `sector_lenses/climate_verified_pipeline.py` — count wiring; confirm live priority path.
- `sector_lenses/climate_native.py` — align count language if it is (also) live.
- `tests/` — update render/order/count/tier tests; add tests for the two new checks, the
  count cap, the tier assignment discipline, and the retired-metadata / hidden-codes
  assertions. Baseline is 853 passing; keep it green.

## Non-goals / guardrails

- Do not touch `main` or the ITS/stable service.
- Do not read the OPCS/ESF corpus (Copilot-only).
- No `Co-Authored-By` trailers on commits.
- Preserve everything the evaluations praised in Example D: the minimum-vs-enhanced action
  structure, target-document/section anchoring, the explicit "do not prescribe a SORT
  rating / do not invent thresholds" refusals, and the subjective-judgement caveat on the
  rating.

## Risks / open questions

- **Live priority path ambiguity** (verified pipeline vs native) — must be resolved before
  the count change lands, or the cap fix could be applied to a dead path.
- **DOCX/HTML parity** — the Quick-fixes tier and overview block must render in both the
  live HTML and the DOCX export; export tests must cover the new order.
- **Materiality-gate drift** — the model could over-promote to fill five slots. The prompt
  must keep the anti-padding language and the materiality bar explicit.
- **Reusability boundary** — factor the overview block cleanly but resist refactoring the
  general run this round (scope creep).

## Success criteria

- Reader opens on an Overview that states the plain-language readout and the sensitivity
  rating scale together, at the top.
- Core questions read as diagnosis + watch/pointer, with no duplicated how-to.
- Priorities can exceed three when materiality warrants (cap 5); no silent truncation.
- Smaller issues appear as a visible, legible Quick-fixes tier with brief how-to-address.
- No routing/authority metadata and no raw evidence codes in the visible tiers; audit
  trail intact in the fold.
- The two new checks fire on a generic (non-SSD) project.
- Full suite green (853 baseline + new tests).
