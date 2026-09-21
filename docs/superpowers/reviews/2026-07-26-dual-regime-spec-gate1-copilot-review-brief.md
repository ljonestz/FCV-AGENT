# Gate-1 Peer-Review Brief — Dual-Regime Process Model spec (for a fresh GitHub Copilot session)

**Date:** 2026-07-26
**Reviewer:** GitHub Copilot (the ONLY agent authorised to read the OPCS PPF corpus, `OPCS docs.xlsx`, the relevance-triage docx, and the ESF Manual — see the ACCESS RESTRICTION in `CLAUDE.md`).
**Artifact under review:** `docs/superpowers/specs/2026-07-26-dual-regime-process-model-design.md` (attach it to the session).
**Why this brief exists:** the spec was authored by Claude working *only* from your earlier review outputs (`ChatCowork.docx`, `OPCS Regime Routing and Review Rules.docx`, `results.docx`, `results 2.docx`, `results 3.docx`, `results4.docx`), never from the corpus itself. This is the Gate-1 check: confirm every load-bearing OPCS citation against the source PDFs before an implementation plan is built on top of it.

---

## How to run this review

1. Open the spec and read it end to end once.
2. For each numbered claim below, open the cited PPF document (use `OPCS docs.xlsx` to locate the file; use the relevance-triage docx to confirm it is the right instrument), and return one of: **CONFIRMED** / **CORRECT-AS-FOLLOWS** (give the fix + exact citation) / **CANNOT-VERIFY** (say why — file missing, ambiguous, needs a template not in the corpus).
3. Do **not** re-derive the whole spec. Only touch the claims listed. If you spot a *material* error the checklist misses, add it under "Reviewer-found issues" at the end.
4. Keep the "Public" (Access-to-Information designation) vs "Published" (publication status) distinction: only assert "Published" from the PPF registry, never from a cover page.

**Output format:** a numbered list matching the item numbers below, each with the verdict + citation (title, catalogue number, effective date, section/paragraph). Save as `results5.docx` in `Downloads/` so Claude can fold it into the spec and memory without corpus access.

---

## A. Preparation-regime axis

**A1. Boundary date.** Spec §4.1: the preparation-regime split uses the operation's **own OIS creation date**, threshold **18 April 2026**, sourced from the one/two-step procedures **OPS5.03-PROC.281 / OPS5.03-PROC.282 (eff 18 Apr 2026)** — NOT the E&S Directive. The procedures phrase it "on or after April 17, 2026", which the spec reads as *after the 17th* = 18 Apr. Confirm the phrasing and that 18 Apr is the correct encoded boundary.

**A2. Governing field.** Confirm the *preparation* axis is governed by the OIS creation date and NOT by the Concept Decision date (which governs the separate E&S axis). Confirm these are two independent classifiers with different governing fields.

**A3. One-step conditions [OPS5.03-PROC.281].** Spec §4.2: ONE-STEP if (SORT-overall **and** E&S both Low/Moderate) **OR** AF **OR** urgent-need/capacity-constraints (para 12) **OR** small-TF IPF (RETF ≤ US$5M). Confirm each disjunct, the RETF threshold value, and the "para 12" reference.

**A4. Two-step conditions [OPS5.03-PROC.282].** Spec §4.2: TWO-STEP if (SORT-overall **or** E&S in {Substantial, High}) **OR** first MPA phase **OR** FMRF (except AF-to-existing-FMRF). Confirm, including that a risk change can flip the route.

**A5. PforR routing.** Spec §4.2: same risk rule; first MPA phase always two-step; AF one-step; FMRF two-step except AF; hybrid PforR+IPF one-step only if PforR ratings Low/Mod **and** the IPF-component ESRC is Low/Mod. Confirm and give the PforR procedure citation.

**A6. DPF routing [OPS5.02-PROC.113, eff 22 May 2026].** Spec §4.2: standalone or first-in-series → two-step (TD+IR); subsequent-in-series → one-step (OR); Supplemental/Scalable → One Review (no TD); management may flip a subsequent op to two-step on significant change. Confirm.

**A7. Transition cases.** Spec §4.1(a–e): (a) new op → new model; (b) OIS pre-boundary still in prep → legacy, retaining PCN/track 1&2/PAD/Appraisal Stage/Decision Review, IPF doc = "Preparation of Investment Project Financing" (eff 1 Jan 2026); (c) **AF routes by the AF's own OIS date** (new one-step includes AF regardless of a legacy parent); (d) **standalone restructuring bypasses** the preparation-regime classifier unless bundled with a new AF; (e) MPA later phases route by that phase's own OIS/risk, first MPA phase always two-step. Confirm each.

**A8. Gates & the death of "appraisal".** Spec §4.3: initiation = **OIS package (OIS + Initial PID + Initial ESRS)**; one-step = OIS → One Review (OR) → negotiate → Board; two-step = OIS → Technical Design (TD) review → Implementation Readiness (IR) review → negotiate → Board. "Appraisal" and "Decision Review" are replaced for new-model Bank-led IPF/PforR and retained ONLY for legacy operations and ADB-led FMRF Trail-Lender cases. Confirm the OIS-package contents and the retained-appraisal carve-outs.

**A9. Legacy → new mapping.** Spec §4.3: PCN/Concept Review → OIS decision (+TD for two-step); PAD prep → progressive PP; Appraisal Package → IR package (or OR); Decision Review → IR Review (or One Review). Confirm this mapping is defensible.

**A10. IPF Project Paper structure [OPS5.03-GUID.180].** Spec §5.4: I Strategic Context; II Project Description; III Implementation; IV **Project Assessment Summary** (Technical/Economic/Financial; Fiduciary [FM, Procurement]; Environmental/Social/Legal); V Key Risks; **Annex 1 Results Framework as the only mandatory annex**. SORT in Datasheet+V; econ IV.A; PPSD/Procurement IV.B; ESRC/ESSs/SEA-SH/SEP/ESCP/GRM IV.C; ESRS separate. Confirm the section map and the "Annex 1 only mandatory annex" claim.

**A11. PforR Program Paper [OPS5.04-GUID.128].** Spec §5.4: adds Program Scope, DLIs, IPF-Component summary, **Program Action Plan (IV.E)**. Confirm.

**A12. DPF document name.** Spec §5.4 + memory: DPF keeps the **Program Document (PD)** (NOT renamed to Project/Program Paper); new-model DPF is two-step (TD PD → IR PD) or OR (subsequent / Supplemental / Scalable); IR PD package includes SORT, Paris-Alignment-Assessment annex, Fund-Relations annex, draft Letter of Development Policy, Updated PID, Legal Agreements, Prior Action Legal Evidence Form. Confirm.

## B. E&S-regime axis (independent of the preparation axis)

**B1. Governing field + threshold.** Spec §3/§5.1: the E&S axis is governed by the operation's **Concept Decision (or equivalent) date** against **1 October 2018** [Environmental and Social Directive/Procedure for IPF, **OPS5.03-DIR.123**, eff 15 Jan 2026, §III.A ¶1]. Confirm the directive number, effective date, section, and threshold date.

**B2. Decision order (A–F).** Spec §5.1: (A) instrument ≠ IPF → `INSTRUMENT_SPECIFIC`; (B) OP/BP 4.03 applies → `PERFORMANCE_STANDARDS_OP_BP_4_03`; (C) AF where the parent is under Safeguard Policies **and** the AF addresses **exclusively** a cost overrun / financing gap → `LEGACY_SAFEGUARDS`; (D) Concept Decision ≥ 1 Oct 2018 → `ESF_ESS1_TO_ESS10`; (E) < 1 Oct 2018 → `LEGACY_SAFEGUARDS`; (F) missing/contradictory → `UNRESOLVED`. Confirm the order and each branch, especially the AF "exclusively cost-overrun/gap" carve-out (C).

**B3. ESF replacement scope [ESF Policy ¶7, fn12, ¶63, fn1].** Spec §5.1: ESF replaces OP/BP 4.00/4.01/4.04/4.09/4.10/4.11/4.12/4.36/4.37, but does **NOT** replace OP/BP **4.03** (Performance Standards — distinct regime), **7.50** (International Waterways), or **7.60** (Disputed Territories). Confirm the replaced list and the three non-replaced policies.

**B4. Separate operational-policy screens.** Spec §5.1: OP/BP **7.50** and **7.60** are separate screens that apply *alongside* the E&S regime (flags `op_7_50_screen` / `op_7_60_screen`), not E&S regimes themselves. Confirm they are correctly modelled as parallel screens rather than `es_regime` values.

**B5. Instrument scoping.** Confirm ESS1–10 apply to **IPF only**, and that DPF and PforR have their own E&S provisions (so a non-IPF instrument must route to `INSTRUMENT_SPECIFIC`, never through the ESS1–10 router).

## C. Minimum reference set, authority tagging, misc

**C1. "PAD minimum reference set" corrections (new-model).** Spec §5.4: replace standalone ESS1 with "applicable ESSs + ES risk assessment"; SEA/SH Action Plan → conditional; Operations Manual → remove from universal minimum; PPSD → review-package instrument (not a mandatory PP annex); keep SORT / SEP-ESS10 / ESCP / Results-Framework (Annex 1); **ADD** Readiness ESRS, Economic Analysis, FM assessment, Procurement Plan (at readiness), Legal Agreements/DFIL (separate), PID. Confirm each add/keep/drop.

**C2. Authority tagging.** Spec §5.5: keep the three user-facing tags (`mandatory_requirement` / `good_practice` / `advisory`) and add an `authority_basis` field (`policy` | `directive` | `procedure` | `guidance` | `reviewer_judgment`). Confirm this maps cleanly to the ADM Clearance vs Advisory Role distinction and that the five basis values are the right granularity.

**C3. Rapid Response citation.** Spec §9: `OPS5.08-POL.125`, Bank Policy, issued/last-revised 25 Jun 2024, effective 10 Jul 2015. Confirm from the cover page (record "Published" only from the registry).

**C4. Timing vocabulary (new-model IPF).** Spec §5.3: shortly-after-OIS / before-TD-review / at-TD-review / between-TD-and-IR / before-IR / at-IR / before-One-Review / at-One-Review / before-negotiations / before-Board / during-implementation-support; "before appraisal" is never emitted for new-model Bank-led ops. Confirm the list is complete and correctly ordered, and that PforR adds ESSA consultation/disclosure timings while DPF has its own list.

## D. Residual "verify with OPCS" — please close if you can

**D1.** Full DPF Program Document section outline (`dpf_sections`) — is there a template/guidance that gives the exact section TOC? (Spec §9, memory line 42.)

**D2.** Full text of **"IPF Implementation Support to Project Completion"** (current, 15 Jan 2026) — the controlling source for standalone restructuring (Restructuring Paper, Level 1/2, ADM roles). Confirm the restructuring-bypass rule and the Level-1/Level-2 thresholds. (Memory line 24; climate spec §12.9.)

**D3.** TA-via-IPF ESS treatment — how are ESSs applied when a TA operation is delivered through the IPF instrument? (Memory line 24.)

**D4.** Program-level MPA CDRS status — is there any *program-level* CDRS clearance, or is CDRS purely phase-level with phase 1 carrying the program-wide climate logic? (Climate spec §12.9; memory line 47.)

---

## E. Reviewer-found issues (add anything material the checklist missed)

*(Copilot: list here, with citations.)*

---

**After the review:** return `results5.docx`; Claude folds CONFIRMED items into the spec's citation footnotes, applies any CORRECT-AS-FOLLOWS fixes to the spec + `project_opcs_july2026_process_change.md`, and only then proceeds to the dual-regime implementation plan.
