# Climate-FCV Readout Redesign — Core-Question Bank + Layout (Design)

**Date:** 2026-07-25
**Branch:** `codex/climate-fcv-output-redesign`
**Status:** Design approved (brainstorming) — pending spec review → implementation plan.
**Supersedes / extends:** `docs/superpowers/specs/2026-07-24-climate-native-flow-design.md` (Approach C, "climate-native flow"). That spec's structural direction stands; this spec refines the reader-facing readout, and adds the **source-derived core-question bank** as the Stage 2 engine.
**Canonical reader view (mock):** `docs/20260725_ss_climate_readout_mock_v4.html` (grounded in the South Sudan SSNRL PCN + CCDR; V3 structure with V2-level depth/nuance in strengths-weaknesses and the core questions).

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
4. **Strengths & weaknesses** — **full detail** (≈4 substantial points each side, ~2–3 sentences per point), climate-FCV-scoped; each point spells out how it is *both* a climate and an FCV issue and names the specific design element it attaches to. This is a nuanced section, not an at-a-glance scan (V2-level depth, per user preference).
5. **Core climate-FCV questions** — the analytical body. Opens with a **plain-English, lay-reader intro** (2–3 sentences) that explains what the section is and that the questions are drawn from an established bank of World-Bank-and-external climate-FCV literature — naming *Maximizing the Peace and Social Dividends of Climate Action*, the *FCV-Sensitive Climate Action Framework*, and the *Defueling Conflict* (peace and social dividends) series — and that only the questions most relevant to this project are surfaced and answered against its own components. (Reader-facing surfacing of the source bank; complements the per-question source line.) Then the questions themselves, curated to the **material** themes (see §4). Q1/Q2 are the two interaction directions; the other themes are peers at equal depth. Each answer is **two solid, nuanced paragraphs** (V2-level depth): a bold "so what" lead, prose that develops the point with as much project-specific nuance as the evidence supports and names specific components/sub-components/institutions/figures throughout, an understated **status word** (e.g. *Partial gap / Under-claimed / Strong, if protected / Gap*), and a subtle **source attribution** line (e.g. *FCV-Sensitive Climate Action Framework*). Depth and targeted, component-grounded specificity are the point — do not compress these into short summaries.
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

- **Maximise project-specific grounding throughout** (a primary, repeatedly-confirmed user priority): name the project's actual components, sub-components, sites, institutions, indicators and figures in *every* section — operational context, strengths/weaknesses, each question answer, and each priority — not just the opening. Prefer a named specific (e.g. "Sub-component 1.2 cold storage", "the National–State Fisheries Working Group", "roughly 70% post-harvest loss", "the PDO 'enhanced resilience' indicator") over a generic noun wherever the source documents support one. Generic, unattributable phrasing is a defect to be suppressed.
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

## 12. OPCS calibration of climate-FCV recommendations (Copilot review, `results 3.docx`, 2026-07-26)

The module's advisory boundary is **confirmed correct** (it may flag a potential gap, point to the relevant corporate assessment/instrument, and pose questions for the specialist — it must NOT determine Paris alignment, ESF/ESS/ESRC compliance, climate resilience, or screening adequacy). Recommendation generation must apply these rules:

**12.1 Instrument-route first, always.** Every climate recommendation resolves by instrument before naming any instrument/commitment: IPF → ESF vocabulary (ESS1–10, ESCP, ESRS, SEP, Project Operations Manual); PforR → ESSA / six core principles / PAP / DLIs / borrower systems (never ESS numbers or ESCP unless a separately financed IPF component); DPF → Program Document / prior actions / PSIA / environmental-forest-NR analysis / SORT (never ESCP/ESS/ESRS/CERC). This extends the existing instrument-conditional vocabulary validator to the climate module.

**12.2 Paris Alignment & Climate-and-Disaster-Risk-Screening (CDRS) are separate corporate processes** (PA applies to all Board operations from 1 Jul 2023, instrument-specific methods; IPF PP summarises the 3-step PA method with the assessment in project records; DPF has Annex 2 Paris Alignment Assessment on prior actions). The module **flags/points, never determines**: use "may require follow-up in the formal PA assessment", not "the project is not Paris aligned". CCDR is evidence-where-available, **not** a mandatory step; do not assert "OPCS requires consulting the CCDR".

**12.3 Good practice ≠ requirement.** Do not present analytical good practice as a mandatory OPCS/ESF requirement. Specifically: **no universal numeric design horizon** (the "20–50 year flood projections" must become "an asset-appropriate design horizon using applicable national/international standards"); adaptive triggers/continuity = "consider proportionate indicators/decision rules", not a mandated trigger matrix; actor-level conflict analysis = proportionate to evidence, reusing existing RRA/ESSA/PSIA rather than auto-commissioning a new study. Use "required" only where policy/directive/procedure clearly establishes it; otherwise "consider / where relevant / proportionate to the identified risk / confirm with the responsible specialist".

**12.4 Climate-relevant ESS mapping (IPF only).** Primary: **ESS1** (climate/hazard in the E&S assessment), **ESS3** (resource efficiency/pollution/GHG — not a general resilience standard), **ESS4** (community safety, natural & climate-exacerbated hazards, emergency preparedness — supports hazard-resilient design but does NOT set a numeric horizon). Conditional: ESS2 (worker OHS under climate conditions), ESS5 (land/displacement from adaptation/NRM), ESS6 (biodiversity/NbS), ESS7 (Indigenous/underserved), ESS10 (engagement/GRM). PforR equivalent = ESSA public-and-worker-safety principle + PAP; DPF equivalent = PSIA + environmental/NR analysis.

**12.5 CERC — recalibrate and constrain.** Recommend considering a CERC only where the operation is an instrument that can carry one, there is a named eligible emergency (natural-hazard/climate/health/economic) with a plausible declaration/activation pathway, and the response links to the PDO. IPF only; PforR only via a separate IPF component; DPF → Cat DDO / supplemental / scalable, never an IPF CERC. Never a generic "flexibility" recommendation. (Consistent with the existing CERC conflict-trigger guardrail, v9.13.)

**12.6 Compound-risk wording guardrail.** Use conditional pathways ("may intensify", "could interact with", "creates a plausible pathway", "should be monitored") — never deterministic claims ("climate change will cause conflict", "the project will reduce conflict", "guarantees peace dividends", "the operation is maladaptive").

**12.7 Source labelling.** The primary climate-FCV analytical framework is *A Framework for Delivering Climate Action in Settings Affected by FCV* (2024/25) — label it and the other bank sources as **"World Bank analytical / good-practice source, not an OPCS policy or compliance standard"**; never rank an analytical report above current PPF policy/procedure/directive/guidance.

**12.8 Per-recommendation verdicts (mock v4 priorities):** P1 flood-resilient infrastructure → recalibrate (drop the universal 20–50yr horizon; asset-appropriate + national standards; instrument-route); P2 adaptive triggers/continuity → correct-in-principle, soften prescription; P3 actor-level conflict analysis → recalibrate (proportionate; reuse existing diagnostics); climate-conflict compound risk → correct with the §12.6 wording guardrail; CERC → recalibrate per §12.5.

These rules are prompt-enforced in the climate Stage 2/3 branches and validated by the instrument-vocabulary validator; the ≤5-priority and specificity/provenance checks are unchanged.

**12.9 Climate & Disaster Risk Screening (CDRS) + AF / Restructuring / MPA (Copilot brief #4, `results4.docx`, 2026-07-26).**
- **CDRS scope:** the corporate CDRS commitment applies across IPF/PforR/DPF **including AF, MPA phases, emergency operations, CERCs, guarantees** (Technical Note on CDRS and the ESF, Jun 2021 — a *guidance* note; the underlying commitment is mandatory, required for all IDA since 1 Jul 2014 / IBRD since 1 Jul 2017). **No named CDRS tool is mandatory** (perform the screening; the app must not require a specific application). **CDRS ≠ ESF** — CDRS is ex-ante, informs resilient design, can inform the ESS assessment but does **not** replace it; the module points to CDRS/ESF implications and never treats a CDRS result as an ESS/ESRC/ESRS/ESCP determination.
- **Additional Financing:** an AF has its **own** preparation package (AF Project Paper, PID, ESRS, PA review, updated E&S) [IPF AF procedure OPS5.03-PROC.279, eff 21 Jan 2026] and needs **AF-level CDRS** addressing the operation-as-modified (AF-financed activities + current context); parent screening is evidence, not a substitute. The IPF Paris Alignment Method [OPS5.03-GUID.168, eff 6 Mar 2024] expressly covers AF **and new activities introduced through restructuring**. **Scope climate recs to what the AF finances**, not the whole parent.
- **Restructuring:** does **not** auto-trigger a full CDRS restart. E&S-Directive change-sensitive rule: no change to E&S due diligence/ESRC → AESS submits input; design changes affecting due diligence → AESS completes input; updated ESCP where applicable. **App rule:** test whether the change introduces new activities or materially changes hazard exposure / vulnerability / geographic coverage / expected life / beneficiaries / design → if so, flag a possible CDRS update + PA Method on the **new activities**; do **not** reopen unchanged activities. Controlling source = "IPF Implementation Support to Project Completion" (current, 15 Jan 2026) — Restructuring Paper, Level 1/2, ADM roles (full text still "verify with OPCS").
- **MPA:** each phase is a self-standing IPF/PforR operation; **CDRS is required at the phase level** (phase 1 presents the program-wide climate logic/long-term risks; there is *no* separate mandatory program-level CDRS clearance — treat that as "verify"). Scope climate recs to the phase's own activities/location/beneficiaries.
- **Project Paper climate locations (where the module should point):** Sectoral/institutional context (vulnerability); Theory of Change (climate assumptions/pathways); Project Components (adaptation/mitigation measures financed); Technical analysis (PA assessment summary); Records folder (CDRS + PA risk assessment); Environmental/Social/Legal (material climate E&S risks); Key Risks (High/Substantial + mitigation); Results Framework (climate indicators where applicable, incl. the ≥20%-climate-co-benefits → ≥1 climate RF indicator rule for IPF).
