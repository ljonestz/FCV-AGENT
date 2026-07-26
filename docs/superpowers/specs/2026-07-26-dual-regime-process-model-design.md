# Dual-Regime Process Model (Legacy PAD ↔ New Project Paper) — Design

**Date:** 2026-07-26
**Status:** Design draft (pending spec review → implementation plan). App-wide foundation; the Climate-FCV module (`2026-07-25-climate-readout-questions-redesign-design.md`) consumes the regime-aware vocabulary produced here.
**Sources (Copilot/WBG-LLM reviews with OPCS corpus access; Claude did not read the corpus except a maintainer-authorised scoped read):** `ChatCowork.docx`, `OPCS Regime Routing and Review Rules.docx`, `results.docx` (all 2026-07-26). Every rule below is cited to a Published OPCS document in those reviews. Memory: `project_opcs_july2026_process_change.md`.

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
2. **E&S regime** — `esf` (ESS1–10) vs `legacy_safeguards` (OP/BP) vs `unresolved`. **Orthogonal to axis 1** — the 18-Apr-2026 boundary does NOT decide ESF vs safeguards; that is governed separately by the E&S Policy's own applicability/transition provisions. Detect from document content, never from the OIS date.

Store both as separate fields; never conflate them.

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
Emit, alongside the existing `%%%DOC_TYPE%%%` / `%%%INSTRUMENT_TYPE%%%`, a regime block: `preparation_regime` (new_model | legacy_transitional | unknown), `processing_model` (one_step | two_step | one_review | unknown), `es_regime` (esf | legacy_safeguards | unresolved), and `ois_creation_date` if stated.

**Detection precedence** (regime): (1) explicit document title + template signature validated against OIS date; (2) OIS creation date from OW/Datasheet; (3) gate vocabulary + section structure; (4) catalogue number (only for guidance/procedure uploads, not operation docs).
```
if explicit OIS_date: classify by date
elif title contains PAD/PCN: LEGACY
elif title contains "Project Paper"/"Program Paper" and text has TD/IR/One Review: NEW
else: UNKNOWN_REQUIRES_MANUAL_CONFIRMATION
```
**Markers** — New: "Project Paper"/"Program Paper", "Technical Design Review", "Implementation Readiness Review", "One Review", "Project Assessment Summary", "ANNEX 1: Results Framework", "Operation Information Summary", DLIs/"Program Action Plan" (PforR), catalogues OPS5.03-GUID.180 / OPS5.04-GUID.128. Legacy: "Project Concept Note"/PCN, "Concept Review", "Track 1/2", "Project Appraisal Document"/PAD, "Appraisal Stage/Package", "Decision Review". **"PID" alone is NOT decisive** (both regimes use it); a guidance catalogue number is NOT proof an operation is new-regime.
**E&S regime** — detect from content: ESRS/ESCP/SEP/ESRC/ESMS/ESS references → `esf`; explicit OP/BP safeguard invocation → `legacy_safeguards`; neither → `unresolved` (verify with OPCS). Current E&S Directive/Procedure for IPF = eff 15 Jan 2026 (file `22a9aff6…`). [ESF-applicability trigger: verify — see §9.]

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

## 9. Verify-with-OPCS (non-blocking; final Copilot pass pending)
- Exact ESF vs OP/BP-safeguards applicability trigger (E&S Directive/Procedure for IPF eff 15 Jan 2026 + the E&S Policy transition provisions) — until confirmed, `es_regime` is detected from content and defaults to `unresolved` with a verify flag.
- Rapid Response catalogue OPS5.08-POL.125 cover-page confirmation (registry index already supports it; app value kept).
- Full DPF Program Document section outline (`dpf_sections`).

## 10. Out of scope
Reading the OPCS corpus directly (Claude works from Copilot/WBG-LLM summaries); a project-status/P-code lookup to auto-populate the OIS date; the climate readout structure (separate spec); ITS/FastAPI parity.
