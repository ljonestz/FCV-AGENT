# Climate-FCV Readout Redesign — Core-Question Bank + Layout (Design)

**Date:** 2026-07-25
**Branch:** `codex/climate-fcv-output-redesign`
**Status:** Design approved (brainstorming) — pending spec review → implementation plan.
**Supersedes / extends:** `docs/superpowers/specs/2026-07-24-climate-native-flow-design.md` (Approach C, "climate-native flow"). That spec's structural direction stands; this spec refines the reader-facing readout, and adds the **source-derived core-question bank** as the Stage 2 engine.
**Canonical reader view (mock):** `docs/20260725_ss_climate_readout_mock_v3.html` (grounded in the South Sudan SSNRL PCN + CCDR).

---

## 1. Problem

Selecting the Climate lens is becoming a genuinely **standalone climate-FCV assessment**, not the generic FCV memo with a climate layer bolted on. Two gaps remain after the v9.19–v9.20 work:

1. **The readout structure doesn't yet match what a TTL wants to read.** The current output leans on the generic FCV engine's shape (opening assessment / operating context / strengths / gaps from the core-FCV Stage 3 prompt), a long integration-gauge paragraph, a mechanical chip-checklist "Reflections" block, and thin/generic interaction and dividend content. It reads as high-level and does not consistently ground claims in the project's actual components.
2. **The analytical spine is not sourced from the climate-FCV frameworks in a visible, triggered way.** The six core questions (cq1–cq6) exist in the diagnostic contract but are not driven by a bank of specific, source-traceable questions that fire when relevant to the project.

Confirmed with a real run (South Sudan SSNRL PCN + CCDR): the desired output is **prose-narrative, project-specific, prioritised-depth-over-coverage**, organised around the climate-FCV intersection.

## 2. Goal

When the Climate lens is active, produce **one coherent, climate-led, lay-readable, project-specific readout** whose analytical body is a **curated set of core climate-FCV questions**, each answered at real depth and grounded in named project components. Behind the six stable question **themes** sits a **question bank** drawn from the WBG climate-FCV source documents; only the questions triggered by the project are answered. Non-climate (core-FCV) mode is unchanged.

## 3. Reader-facing readout (climate lens active)

Order, top to bottom (canonical: mock v3). Each section is prose unless noted; every substantive claim should attach to a specific component / sub-component / institution / place where one exists.

1. **Executive summary** — 2–3 sentences. One **bolded lead sentence** carrying the single most important finding, then the design's key strength and the key unresolved gap. No scaffolding.
2. **Integration gauge** — the **default app 6-tier scale** (`Extremely Low · Very Low · Low · Adequate · Well Embedded · Very Well Embedded`), rendered as the existing semicircular arc, with the default short "need" phrase (e.g. *Targeted enhancements possible*) and **one short summary sentence**. Replaces the current 4-level `integration_level` gauge and the long paragraph readout. Keeps the existing "not an official WBG rating" caveat.
3. **Operational context** — three short blocks: **The FCV setting → The climate setting → Where they meet**. National (and regional where relevant) framing; "Where they meet" names the compound collisions against specific components. May run slightly longer than the other blocks.
4. **Strengths & weaknesses** — a **short at-a-glance** scan (≈3–4 short points each), climate-FCV-scoped; each point makes clear how it is *both* a climate and an FCV point. Depth lives in the questions below, so this stays a quick read.
5. **Core climate-FCV questions** — the analytical body. Curated to the **material** themes (see §4). Q1/Q2 are the two interaction directions; the other themes are peers at equal depth. Each answer: a bold "so what" lead, nuanced prose naming components, an understated **status word** (e.g. *Partial gap / Under-claimed / Strong, if protected / Gap*), and a subtle **source attribution** (e.g. *FCV-Sensitive Climate Action Framework*).
6. **Priority action areas** — ~3 (may be more only if genuinely warranted; ≤5 hard cap), curated and deeper, each with *Why it matters / What to do / The gap*, `action_timing` pill, and existing per-priority fields.
7. **Policy-boundary line** — advisory-only; not an ESF/ESS/ESRC determination; does not replace the accredited E&S specialist.

**Removed:** the standalone "Wider FCV context" callout (this is a dedicated climate-FCV module); the mechanical chip-checklist "Reflections" block (absorbed into the questions); the two separate S/R gauges in climate mode (single integration gauge, as v9.19).

## 4. The core-question themes and the question bank

### 4.1 Six stable themes (visible spine)
The reader always sees at most these six theme-level questions, curated to the material ones. They map to the existing diagnostic `reflections` keys and to the frameworks:

| Theme key | Reader question (stable) | Grounding |
|---|---|---|
| `cq1_interaction` | How could climate and FCV affect the project? *(interaction, inbound)* | interaction / delivery |
| `cq1_interaction` (2nd direction) | How could the project affect climate and FCV dynamics? *(interaction, outbound)* | project → climate-FCV |
| `cq2_maladaptation` | Could the design lock in maladaptation? | maladaptation / lock-in / DNH-over-time |
| `cq3_dividends` | Does it engage root causes and create peace & social dividends? | dividends / root causes |
| `cq4_inclusion` | Are the most vulnerable reached, and through the right institutions? *(inclusion may absorb `cq5_institutions` where thin)* | inclusion / vulnerability / institutions / HDP |
| `cq6_adaptive` | Is the design adaptive to uncertainty, across realistic time horizons? | adaptive design / monitoring / horizons |

`cq5_institutions` may surface as its own theme when institutionally material, or fold into `cq4_inclusion`. The two interaction directions are two entries under `cq1_interaction`.

### 4.2 Question bank (the engine)
- A **bank of more specific questions** is built from the WBG climate-FCV source documents under `docs/climate_module/` (unrestricted; NOT the OPCS corpus): *Maximizing the Peace and Social Dividends of Climate Action*, the *FCV-Sensitive Climate Action Framework* (`climate_fcv_framework.pdf`), the *Defueling Conflict* series, the *Conflict-Sensitive Climate Action in FCV Settings Compendium*, and the CCDR guidance note.
- Each bank question carries: `theme` (one of the six), `question` text, `source` (short attribution), and a **trigger condition** (project characteristics that make it relevant — e.g. hard infrastructure present → a maladaptation lock-in question; displacement present → an inclusion-under-displacement question; government-systems delivery → an institutions question; DPF/PforR instrument → instrument-appropriate variants).
- Stage 2 **fires only triggered bank questions**, groups them under their theme, and produces one answer per material theme that is **shaped by** the fired questions and **cites** the source. Surfacing stays at the **theme level** (the reader sees the stable six; the bank shapes the answers) — decision confirmed in brainstorming.
- Curation rule: a theme with no triggered bank question and nothing project-specific to say is **dropped**, not padded. Always answer the two interaction directions.

### 4.3 Data shape (additive to the existing diagnostic contract)
Extend the per-lens climate diagnostic (`sector_lenses/pipeline.py`) so each surfaced theme answer carries:
- `theme_key` (cq1…cq6), `title` (stable reader question), `status_cue` (soft, softened as in v9.20+), `text` (the nuanced prose answer), `source` (short attribution string), `triggered_questions` (bounded list of the specific bank-question ids/text that fired). Interaction directions keep the existing `interaction_readout` shape + `narrative`.
- The integration readout moves to the **6-tier** scale: a `rating` (one of the six labels) + derived `need_phrase`, replacing/serving alongside the 4-level `integration_level` (keep `integration_level` internally for backward-compat mapping; add the 6-tier rating for display).

## 5. Pipeline changes (climate-native flow)

- **Stage 1:** extract the project characteristics the bank triggers need (instrument, sector, hazards present, displacement, delivery institutions, geography/components). Existing climate research pass unchanged.
- **Stage 2 (climate mode):** stop emitting the verbose generic engine (12-OST table / DNH-9 / 25-question map) as visible output; reason through the six themes + triggered bank internally; emit the integration readout (6-tier), the short S&W synthesis, the per-theme answers, and the interaction narratives. The generic S/R rating is retained as lean internal input for defensibility/export. Keep the v9.20 completeness check + recovery as fallback.
- **Stage 3 (climate mode):** priorities as today (≤5, curated to ~3), climate-linked; the "opening assessment / operating context / strengths / gaps" generic scaffolding is replaced by the §3 structure. `wider_fcv_context` no longer surfaced in climate mode.

## 6. Rendering & export parity

Live HTML, shared/downloaded HTML, and DOCX render the identical §3 order from one set of renderers: exec summary → 6-tier gauge → 3-block operational context → short S&W → core-question answers (with status + source) → priorities → boundary. Update the frontend (`index.html`) renderers, the DOCX `download_report` helpers, and `downloadHTML()` together; add tests asserting DOCX == live == shared HTML for the new sections.

## 7. Content-quality bar (prompt-enforced)

- Name the project's actual components, sub-components, sites, institutions — throughout, not just the opening.
- Each answer tells a causal story a lay reader follows: pressure → plain mechanism → what it means for *this* project → what the design does / should do. Gloss jargon on first use.
- Prioritised depth over coverage: pick the material points and go concrete; suppress non-specific points rather than padding the schema or the bank.
- Dividends framed as **opportunities, never requirements**; open with a plain-English explainer of what a dividend is.

## 8. Preserved invariants

OPCS policy-boundary + instrument-awareness guardrails; no-fabrication / citation discipline; specificity & provenance checks; ≤5 priorities; the v9.20 completeness + honest-degradation fallback; compact-history performance pattern; softened status cues (no raw snake_case). The OPCS corpus is not read by any non-Copilot agent; the climate frameworks under `docs/climate_module/` ARE the grounding and are unrestricted.

## 9. Out of scope (noted for later)

- **Large-context-document handling** (e.g. a single 108-page CCDR pushing Stage 1's phase-sum near the budget). Real, but a separate scaling workstream — deferred.
- ITS/FastAPI parity (`FCV_BUILD_PARITY.md`) — deferred until the climate branch settles.
- A user-selectable climate-primary vs integrated mode.
- Changes to non-climate instrument modules.

## 10. Testing

- Bank: triggers fire correctly by project characteristic; a fisheries IPF and a hypothetical hydropower DPF surface different bank questions; non-material themes are dropped, not padded; every surfaced answer cites a source.
- Contract/parse: per-theme answer fields (theme_key/title/status_cue/text/source/triggered_questions) parsed and bounded; 6-tier rating parsed; graceful degradation preserved.
- Rendering: stable-six theme headers; status + source rendered understated; export parity (DOCX == live == shared HTML); 6-tier gauge fractions correct.
- Regression: non-climate (core-FCV) output byte-for-byte unchanged.
- Live re-validation on the South Sudan SSNRL PCN (+ CCDR).

## 11. Open items to resolve during planning

- Exact size/shape of the initial question bank (how many questions per theme to seed from the source docs) and the trigger vocabulary.
- Whether `cq5_institutions` is a standalone theme by default or folds into `cq4_inclusion` unless institutionally material (default: fold unless material).
