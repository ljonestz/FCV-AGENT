# Dual-Regime Process Model (Legacy PAD ↔ New Project Paper) — Design

**Date:** 2026-07-26
**Status:** Gate-1 reviewed (Microsoft enterprise Copilot, `results 5.docx`, 2026-07-26) — router logic CONFIRMED against the PPF PDFs; corrections folded into §0. Ready for implementation (`docs/superpowers/plans/2026-07-26-dual-regime-process-model.md`). App-wide foundation; the Climate-FCV module (`2026-07-25-climate-readout-questions-redesign-design.md`) consumes the regime-aware vocabulary produced here.
**Sources (Copilot/WBG-LLM reviews with OPCS corpus access; Claude did not read the corpus except a maintainer-authorised scoped read):** `ChatCowork.docx`, `OPCS Regime Routing and Review Rules.docx`, `results.docx`, `results 5.docx` (all 2026-07-26). Every rule below is cited to a Published OPCS document in those reviews. Memory: `project_opcs_july2026_process_change.md`.

---

## 0. Gate-1 review outcome (Microsoft enterprise Copilot, `results 5.docx`, 2026-07-26)

Copilot verified every claim against the PPF PDFs (read the source text, not prior summaries). **The router logic — both boundary dates, the one/two-step decision tables, and the DPF/PforR/AF/MPA/restructuring routing — is CONFIRMED.** `regime_router.py` (Phase 1) needs no change. Corrections and added citations fold in below; §§1–10 remain as written except where a correction is noted here.

**Confirmed catalogue numbers (use in citations):**
- Legacy IPF preparation procedure = **OPS5.03-PROC.283** (eff 1 Jan 2026, rev 30 Apr 2026) — the pre-boundary route.
- New-model IPF one-step = **OPS5.03-PROC.281**, two-step = **OPS5.03-PROC.282** (both eff 18 Apr 2026).
- New-model PforR one-step = **OPS5.04-PROC.126** (eff 18 Apr 2026).
- DPF = **OPS5.02-PROC.113** (eff 22 May 2026).
- IPF Project Paper guidance = **OPS5.03-GUID.180** (eff 1 Jul 2026); PforR Program Paper = **OPS5.04-GUID.128** (eff 28 Jun 2026).
- Restructuring / implementation-support controlling source = **OPS5.03-PROC.278** (eff/rev 15 Jan 2026).
- Rapid Response = **OPS5.08-POL.125** (Bank Policy, Public, issued/rev 25 Jun 2024, eff 10 Jul 2015) — fully confirmed from the PDF.

**Corrections to apply:**
1. **A1 boundary** — procedures literally say "on or after April 17, 2026" but cover pages say effective 18 Apr; legacy PROC.283 applies to OIS before 18 Apr. Encode **≥ 2026-04-18** (done in `regime_router.py`); store the literal "April 17" wording only as a source caveat, never admit 17 Apr.
2. **§4.3 / §5.2 — "appraisal" is NOT fully obsolete.** The claim that "appraisal"/"Decision Review" are retained ONLY for legacy + ADB is too broad: OPS5.03-DIR.123 still uses Concept/Appraisal terminology for E&S documents and clearances. Distinguish the new *preparation* review gates (TD/IR/OR) from the continuing use of "Appraisal" in E&S and external lead-lender contexts. **Terminology normalisation (§5.2) must be scoped to preparation-gate language only — do NOT globally replace "appraisal".**
3. **§4.3 — legacy→new mapping is a crosswalk, not a formal PPF equivalence.** Tag it `reviewer_judgment`/guidance, not a mandatory procedural rule.
4. **§5.4 A12 confirmed in full** (after upload): the DPF IR package expressly includes the IR Program Document with SORT, a Paris Alignment Assessment annex, a Fund Relations Annex, a draft Letter of Development Policy, an Updated PID, Legal Agreements, and a Prior Action Legal Evidence Form.
5. **§5.1 B2 — the E&S decision ORDER is app logic**, not PPF text. The substantive branches are sourced (OPS5.03-DIR.123 §III.A ¶1(a)/(b)), but the non-IPF `INSTRUMENT_SPECIFIC` routing and the `UNRESOLVED` fallback must be tagged `reviewer_judgment`, not attributed to §III.A.
6. **§5.1 B3 citation CORRECTED** — the replaced / not-replaced OP/BP lists live in the **World Bank Environmental and Social Policy for IPF, "Purpose", paragraph 1, footnote 1** (printed page 3 of the ESF), NOT "ESF Policy ¶7/fn12/¶63/fn1". Replaced list confirmed; **note OP 4.09 (not "OP/BP 4.09")**. Not replaced: OP/BP 4.03, 7.50, 7.60.
7. **§5.5 — `reviewer_judgment` is explicitly OUTSIDE the PPF hierarchy** (policy/directive/procedure/guidance map onto it; flag reviewer_judgment as app-level). The three user-facing tags (mandatory_requirement/good_practice/advisory) are app taxonomy, not official PPF labels (PPF distinguishes Clearance vs Advisory + Recommendation/concurrence/decision ADM roles).
8. **§5.3 C4 — the new-model timing vocabulary is application design, not authority text.** No PPF document declares it canonical or forbids "before appraisal" everywhere. Keep it as the app's controlled vocabulary; the "never emit before appraisal" rule applies to new-model *preparation-gate* timing only, not to E&S-context uses of "appraisal".

**Open items still CANNOT VERIFY (do not hard-code):**
- **D1** — no current template gives the full DPF Program Document section TOC (`dpf_sections` stays best-effort, inferred only from package requirements).
- **D4** — no governing text establishes a distinct *program-level* MPA CDRS clearance, nor that phase 1 alone carries the program-wide climate logic. (Climate spec §12.9 MPA note stays "verify".)

**Resolved open items:**
- **D2 restructuring** [OPS5.03-PROC.278]: handled during implementation support → bypasses the preparation classifier unless a separate AF is processed. **Level 1 = exactly three cases:** (a) change from a lower safeguard category to Category A; (b) extension of the Bank Guarantee Expiration Date; (c) reliance on alternative procurement arrangements (Procurement Policy §III.F). All else Level 2; RVP decision required for a Level-2 with a PDO change, a newly-triggered safeguard policy, cumulative closing-date extension ≥ 2 years, or a safeguards deferral. (Refines the app's existing `derive_restructuring_level` — adds a third Level-1 case, the safeguard-category escalation.)
- **D3 TA-via-IPF** [OPS5.03-DIR.123 §III.A/§III.C]: follows the IPF E&S regime; ESSs applied proportionately to the TA activities; no separate TA E&S regime.

**Reviewer-found (fold into Stage 1 detection):**
- **OIS name variant:** OPS5.03-PROC.281 expands OIS as "Operation **Information** Summary"; OPS5.03-PROC.282 as "Operation **Initiation** Summary"; DPF/PforR use "Information". **Do not use the expanded name as a routing signal** — key on the acronym + date.
- **OPS5.03-GUID.180 applies to BOTH regimes** (new-model TD/IR and legacy PCN/PAD) — do not treat it as a new-model-only detection marker.
- Annex 1 is the only *mandatory* annex, but Annex 2 is expressly *optional* — do not assert "no other annex allowed".
- Registry `DocumentStatus = Published` and `BankAccessToIPD = Public / Official Use Only` are separate fields — never conflate (matches the existing source-discipline rule).

---

## 1. Problem

On **18 April 2026** (processing) and **1 July 2026** (documents), OPCS replaced the lending-preparation model. For operations whose **OIS (Operation Information Summary) was created on/after 18 April 2026**, the app's entire stage/document/timing vocabulary is stale:
- The appraisal document is now the **Project Paper (PP)** for IPF and **Program Paper (PP)** for PforR (DPF keeps the **Program Document**). "Preparing the PAD for IPF" is **archived** (retired 30 June 2026).
- Preparation runs **OIS → One Review (one-step)** or **OIS → Technical Design (TD) review → Implementation Readiness (IR) review (two-step)**, split by **risk rating**. "Appraisal" and "Decision Review" are replaced for new-model Bank-led IPF/PforR.
- The app is PAD/PCN/PID-centric (~110 "PAD" references, a "PAD minimum reference set", a `pad_sections` field, "before appraisal" timing).

Operations initiated **before** 18 April 2026 still run the **legacy** model (PCN/PID/PAD, Appraisal Stage, Decision Review) and will keep being uploaded for years. The app must therefore **support both regimes and detect which one applies from the uploaded document.**

## 2. Goal

Make the app **regime-aware on two independent axes**, detect both from the uploaded document, and render/route recommendations correctly for each — without breaking legacy support. Non-goal: forcing every project onto the new model.

## 3. The two independent axes

1. **Preparation regime** — `new_model` (OIS ≥ 18 Apr 2026) vs `legacy_transitional` (OIS < 18 Apr 2026). Determines document type, gates, and timing vocabulary.
2. **E&S regime** — routed by the operation's **Concept Decision (or equivalent) date** against the **1 October 2018** threshold [Environmental and Social Directive/Procedure for IPF, **OPS5.03-DIR.123**, eff 15 Jan 2026, §III.A ¶1]. Values: `ESF_ESS1_TO_ESS10` | `LEGACY_SAFEGUARDS` | `PERFORMANCE_STANDARDS_OP_BP_4_03` | `INSTRUMENT_SPECIFIC` (DPF/PforR — they have their own E&S provisions, ESF/ESS applies to IPF only) | `UNRESOLVED`. **Separate classifiers, different governing fields** (not "entirely independent" — AF history can create valid mixed combinations): the E&S axis is NOT decided by the OIS date, and the preparation axis is NOT decided by the Concept Decision date.

Store both as separate fields; never conflate them. A valid combination is `preparation_regime = legacy_transitional` + `es_regime = ESF_ESS1_TO_ESS10` (e.g. Concept Decision 2022, OIS before 18 Apr 2026).

## 4. Routing rules (confirmed, cited)

### 4.1 Preparation-regime boundary
Use the operation's **own OIS creation date**. `OIS ≥ 2026-04-18 → new_model`; `< → legacy_transitional`. (Procedures phrase this "on or after April 17, 2026", read as *after the 17th* = 18 Apr; encode **18 Apr 2026** with a source caveat.)

**By case:** (a) new op → new model; (b) OIS pre-boundary, still in prep → legacy (`Preparation of Investment Project Financing`, eff 1 Jan 2026; retains PCN, track 1/2, PAD, Appraisal Stage, Decision Review); (c) **AF → route by the AF's own OIS date** (new one-step includes AF regardless of a legacy parent); (d) **standalone restructuring → bypass** the preparation-regime classifier (implementation-support action) unless bundled with a new AF; (e) MPA later phases route by that phase's own OIS date/risk (first MPA phase always two-step).

### 4.2 One-step vs two-step
- **IPF** [one-step OPS5.03-PROC.281 / two-step OPS5.03-PROC.282, eff 18 Apr 2026]:
  ```
  if IPF_first_MPA_phase: TWO_STEP
  elif FMRF and not AF_to_existing_FMRF: TWO_STEP
  elif AF or urgent_need_or_capacity_constraints or small_TF_IPF(RETF<=US$5M): ONE_STEP
  elif SORT_overall in {Substantial,High} or ES_risk in {Substantial,High}: TWO_STEP
  elif SORT_overall in {Low,Moderate} and ES_risk in {Low,Moderate}: ONE_STEP
  else: VERIFY_MISSING_RISK_DATA
  ```
  Risk changes can flip the route. **FCV operations are typically Substantial/High → two-step.**
- **PforR**: same risk rule; first MPA phase always two-step; AF one-step; FMRF two-step except AF; hybrid PforR+IPF one-step only if PforR ratings Low/Mod **and** IPF-component ESRC Low/Mod.
- **DPF** [OPS5.02-PROC.113, eff 22 May 2026]: standalone or first-in-series → two-step (TD+IR); subsequent-in-series → one-step (OR); Supplemental/Scalable → One Review (no TD); management may flip subsequent to two-step on significant change.

### 4.3 Gates & the death of "appraisal"
- Initiation: **OIS package** (OIS + Initial PID + Initial ESRS); OIS decision confirms SORT + route.
- One-step: `OIS → One Review (OR) → negotiate → Board`.
- Two-step: `OIS → Technical Design review → Implementation Readiness review → negotiate → Board`.
- **"Appraisal" is replaced** by assessment + TD/IR/OR for new-model Bank-led IPF/PforR. Retain "appraisal"/"Decision Review" ONLY for legacy operations and ADB-led FMRF Trail-Lender cases.
- Legacy→new mapping: PCN/Concept Review → OIS decision (+TD for two-step); PAD prep → progressive PP; Appraisal Package → IR package (or OR); Decision Review → IR Review (or One Review); Board → Board; supervision → supervision.

## 5. App changes

### 5.1 Stage 1 detection (new)
Emit, alongside the existing `%%%DOC_TYPE%%%` / `%%%INSTRUMENT_TYPE%%%`, a regime block:
`preparation_regime` (new_model | legacy_transitional | unresolved_policy_source) + `preparation_regime_source`; `processing_model` (one_step | two_step | one_review | unknown); `ois_creation_date`; `concept_decision_or_equivalent_date` + `concept_date_source`; `es_regime` (ESF_ESS1_TO_ESS10 | LEGACY_SAFEGUARDS | PERFORMANCE_STANDARDS_OP_BP_4_03 | INSTRUMENT_SPECIFIC | UNRESOLVED) + `es_regime_source`; `op_bp_4_03_applies`; `additional_financing_exception_applies`; `op_7_50_screen` / `op_7_60_screen`; `evidence_markers`; `conflicting_evidence`; `verification_flag` + `verification_reason`. **Source discipline:** cite title + catalogue + date + section for each classification; distinguish policy text from app inference and authoritative dates from keyword fallback; do NOT equate "Public" (an Access-to-Information designation) with "Published" (publication status — read from the PPF registry or leave unverified).

**Detection precedence** (regime): (1) explicit document title + template signature validated against OIS date; (2) OIS creation date from OW/Datasheet; (3) gate vocabulary + section structure; (4) catalogue number (only for guidance/procedure uploads, not operation docs).
```
if explicit OIS_date: classify by date
elif title contains PAD/PCN: LEGACY
elif title contains "Project Paper"/"Program Paper" and text has TD/IR/One Review: NEW
else: UNKNOWN_REQUIRES_MANUAL_CONFIRMATION
```
**Markers** — New: "Project Paper"/"Program Paper", "Technical Design Review", "Implementation Readiness Review", "One Review", "Project Assessment Summary", "ANNEX 1: Results Framework", "Operation Information Summary", DLIs/"Program Action Plan" (PforR), catalogues OPS5.03-GUID.180 / OPS5.04-GUID.128. Legacy: "Project Concept Note"/PCN, "Concept Review", "Track 1/2", "Project Appraisal Document"/PAD, "Appraisal Stage/Package", "Decision Review". **"PID" alone is NOT decisive** (both regimes use it); a guidance catalogue number is NOT proof an operation is new-regime.
**E&S regime router** [OPS5.03-DIR.123, §III.A ¶1; ESF replaced/not-replaced lists at World Bank E&S Policy for IPF, "Purpose" ¶1 fn1 — see §0 correction 6] — decision order (the ORDER is app logic per §0 correction 5): (A) instrument ≠ IPF → `INSTRUMENT_SPECIFIC` (route to DPF/PforR E&S provisions; never the ESS1–10 router); (B) OP/BP 4.03 applies → `PERFORMANCE_STANDARDS_OP_BP_4_03`; (C) AF where the parent is under Safeguard Policies **and** the AF addresses **exclusively** a cost overrun or financing gap → `LEGACY_SAFEGUARDS` (do NOT apply if the AF scales up/adds/changes activities or introduces new E&S risk); (D) Concept Decision date ≥ 1 Oct 2018 → `ESF_ESS1_TO_ESS10`; (E) < 1 Oct 2018 → `LEGACY_SAFEGUARDS` (verify mixed-history); (F) date/regime/parent info missing or contradictory → `UNRESOLVED` + verify flag. **Fallback markers (evidence, not decisive):** ESF = ESRC/ESRS/ESCP/SEP/ESS1–10/E&S risk terminology; legacy = Environmental Category A/B/C/FI, ISDS, "Safeguard Policies triggered", OP/BP 4.xx; OP/BP 4.03 = PS1–PS8. Never classify from a single keyword; conflicting signals → `UNRESOLVED`. **Separate operational-policy screens (not E&S regimes):** flag `op_7_50_screen` (International Waterways) and `op_7_60_screen` (Disputed Territories) — both material in FCV/cross-border contexts — as applicable *alongside* the E&S regime.

### 5.2 Terminology normalisation
Introduce an internal lifecycle class `IPF_APPRAISAL_DOCUMENT` that both PAD and Project Paper normalise to; render the displayed label per `preparation_regime`. Keep PAD/PCN/PID as legacy input types. Rename `pad_sections → appraisal_document_sections` (accept `pad_sections` for backward compatibility). Replace user-facing "PAD stage/language/sections" and "ready-to-paste PAD text" with regime-rendered equivalents. Do **not** bulk-delete "PAD" — it stays valid for legacy + policy-level concepts + ADB-led FMRF.

### 5.3 Regime-aware timing vocabulary (`action_timing`)
- **Legacy** (unchanged): flag-for-preparation / required-before-appraisal / required-before-board / next-series / supervision.
- **New-model IPF**: shortly-after-OIS / before-TD-review / at-TD-review / between-TD-and-IR / before-IR / at-IR / before-One-Review / at-One-Review / before-negotiations / before-Board / during-implementation-support. PforR adds ESSA-consultation/disclosure timings; DPF has its own list.
- Never emit "before appraisal" for new-model Bank-led operations. The climate module (and all Stage 3) must consume this central, regime-aware vocabulary rather than hard-coding strings.

### 5.4 Document sections & instrument reference checks
- **IPF Project Paper** [OPS5.03-GUID.180]: I Strategic Context; II Project Description (PDO, ToC+PDO indicators, Beneficiaries, Components, Partners, Lessons); III Implementation (Institutional/Implementation, Results M&E/Verification, Disbursement); IV **Project Assessment Summary** (Technical/Economic/Financial; Fiduciary [FM, Procurement]; Environmental/Social/Legal); V Key Risks; **Annex 1 Results Framework (only mandatory annex)**; Annex 2 optional. SORT in Datasheet+V; econ IV.A; PPSD/Procurement IV.B; ESRC/ESSs/SEA-SH/SEP/ESCP/GRM IV.C; ESRS separate; RF Annex 1. **PforR Program Paper** [OPS5.04-GUID.128] adds Program Scope, DLIs, IPF-Component summary, Program Action Plan (IV.E). **DPF** keeps the Program Document (PD): TD PD / IR PD; IR package has Paris-Alignment + Fund-Relations annexes + draft LDP (full PD TOC → verify).
- **Corrections to the "PAD minimum reference set" (new-model, regime-gated):** replace standalone ESS1 with "applicable ESSs + ES risk assessment"; SEA/SH Action Plan → **conditional**; Operations Manual → **remove** from universal minimum; PPSD → review-package instrument (not a mandatory PP annex); keep SORT / SEP-ESS10 / ESCP / Results-Framework (mandatory Annex 1); **ADD** Readiness ESRS, Economic Analysis, FM assessment, Procurement Plan (at readiness), Legal Agreements/DFIL (separate), PID. All ESF-instrument checks gate on `es_regime == esf` and `instrument == IPF`.

### 5.5 Recommendation authority tagging
Keep the three user-facing tags (`mandatory_requirement` / `good_practice` / `advisory`) and add an `authority_basis` field (`policy` | `directive` | `procedure` | `guidance` | `reviewer_judgment`) — aligning with the ADM Clearance vs Advisory Role and preventing guidance advice being presented as a mandatory requirement.

## 6. How the climate module consumes this
The Climate-FCV module's priority `action_timing` and instrument references draw from §5.3/§5.4 (regime-aware) instead of hard-coded "Required before appraisal". Its mock v4 "Required before appraisal" strings become regime-rendered (e.g. new-model two-step → "Before Technical Design review"). No change to the climate readout structure — only its timing/instrument vocabulary source.

## 7. Preserved invariants
Legacy behaviour unchanged when `preparation_regime == legacy_transitional`; instrument-conditional vocabulary validator and DNH/SEA-SH per-instrument guidance retained; OPCS policy-boundary + advisory framing; no fabrication; ≤5 priorities; compact-history performance pattern. New fields default safely (`unknown`/`unresolved`) so a missing signal never mis-asserts a regime.

## 8. Testing
Regime detection (new vs legacy vs unknown from representative markers/dates); one/two-step/DPF routing decision tables; AF-by-own-OIS, restructuring-bypass, MPA-phase rules; timing-vocabulary selection per regime; `pad_sections`↔`appraisal_document_sections` back-compat; `es_regime` detection from content; legacy output byte-for-byte unchanged; climate module consumes regime-aware timing.

## 9. Verify-with-OPCS (non-blocking)
- **ESF applicability trigger — RESOLVED** (OPS5.03-DIR.123, §III.A ¶1: Concept Decision ≥ 1 Oct 2018 → ESF; the exceptions and the ESF/legacy split are cited above). Only *mixed-history* / contradictory-marker / ambiguous-date cases still need per-operation verification (→ `UNRESOLVED`).
- **Rapid Response — CONFIRMED** from the cover page: `OPS5.08-POL.125`, Bank Policy, issued/last-revised 25 Jun 2024, effective 10 Jul 2015, Public, IBRD/IDA. (Record "Published" only from the PPF registry, not the cover page.)
- **18 Apr 2026 preparation boundary** is sourced from the one/two-step procedures (OPS5.03-PROC.281/282, eff 18 Apr 2026) — cite that source, not the E&S Directive; if a run cannot establish it, set `preparation_regime = unresolved_policy_source`.
- Still open: full DPF Program Document section outline (`dpf_sections`).

## 10. Out of scope
Reading the OPCS corpus directly (Claude works from Copilot/WBG-LLM summaries); a project-status/P-code lookup to auto-populate the OIS date; the climate readout structure (separate spec); ITS/FastAPI parity.
