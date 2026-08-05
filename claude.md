# FCV Project Screening App — Claude Development Guide

> **Maintenance instruction:** After every substantial change (new features, prompt changes, new delimiters, UI additions, architectural decisions), update this file AND the relevant reference doc before committing. Keep section 1.3 (Stage pipeline), section 3 (Prompt Architecture), and section 5.3 (Priority Parsing) accurate at all times.
>
> **Reference files** (detailed specs moved here to keep this file under 40k):
> - `docs/reference/reference_prompt_architecture.md` — per-stage prompt specs, delimiter schemas, parsing details
> - `docs/reference/reference_frontend_functions.md` — JS function list, Express mode architecture, removed items
> - `docs/reference/reference_sector_lenses.md` — module packages, budgets, selection, delimiters, and parity contract
> - `docs/reference/reference_backend_routes.md` — all routes, SSE event shapes, parsing function signatures

---

## Overview

This is a **World Bank FCV (Fragility, Conflict, and Violence) Project Screener** — a Flask-based web app that guides Task Team Leaders (TTLs) through a **3-stage workflow** to assess how well a World Bank project integrates FCV considerations and generate targeted, actionable recommendations.

The tool explicitly distinguishes two concepts:
- **FCV Sensitivity [S]** — Is the project *aware of and designed for* the FCV context? Contextual awareness, conflict-informed design, Do No Harm, FCV-adapted operations.
- **FCV Responsiveness [R]** — Does the project *actively work to change* the FCV situation? Root-cause engagement, resilience building, transformative use of FCV tools, peace & stability dividends.

The 4 FCV Strategy Shifts (Anticipate / Differentiate / Jobs & Private Sector / Enhanced Toolkit) are **cross-cutting** — they apply to both S and R findings and are tagged inline.

Every prompt output tags findings as [S], [R], or [S+R], assigned dynamically per-finding. [S+R] strictly only for: (1) inclusion/targeting of conflict-affected populations; (2) FCV logic in ToC/PDO; (3) adaptive M&E for harm + resilience; (4) GRM for state-citizen accountability. If in doubt → [S] or [R].

**Key goal:** Move from broad, vague recommendations to specific, location-aware, operationally grounded, stage-aware suggestions (e.g., "historically, Nzerekore, Kindia, and Kankan have been excluded from service delivery — focus on these regions before PAD appraisal").

**Analytical backbone:** WBG FCV Strategy 2026-2030, FCV Operational Manual (OST, enriched with Peace & Inclusion Lens dimensions and Strategic DRR Framing from Good Practice Notes), FCV Operational Playbook, and Good Practice Notes on Peace & Inclusion Lenses and FCV-Sensitive Programming. When a Country Partnership Framework (CPF) is uploaded as a contextual document, Stage 3 recommendations include a `cpf_alignment` field linking priorities to CPF outcomes. When an RRA or equivalent conflict analysis is uploaded, Stage 3 also includes `rra_driver_alignment` linking priorities to identified conflict drivers where relevant.

## OPCS Source Policy Documents (local reference corpus - NOT in this repo)

The authoritative OPCS policies, directives, and guidance notes this app's prompts and knowledge base (`background_docs.py`) are meant to stay consistent with are **not stored in this repository**. They live locally on the maintainer's machine, outside any git-tracked folder:

- **Full OPCS Policy and Procedure Framework (PPF) document corpus:** `C:\Users\wb559324\WBG\Policy and Procedure Framework - PPFDocuments` - 178 PDF policy/directive files as of 2026-07, including the IDA FCV Envelope policy and directive, the Program-for-Results policy/directive, the DPF policy/directive, and the MPA policy/directive referenced throughout `background_docs.py`.
- **Document name index:** `C:\Users\wb559324\Downloads\OPCS docs.xlsx` - a spreadsheet listing every file name in the PPF corpus above, for quick lookup without opening each PDF.
- **Relevance triage:** `C:\Users\wb559324\Downloads\LLM input on relevant project docs.docx` - an internal WBG LLM's assessment of which documents in the PPF corpus are most relevant to this app's FCV screening use case, used to prioritise which policies to actually read in depth rather than working through all 178 files.
- **ESF Manual:** The full World Bank Environmental and Social Framework manual PDF, uploaded directly as session context when doing OPCS-consistency work (not saved to a fixed path - treat it as a session attachment each time it is needed).
- **Test cases:** `C:\Users\wb559324\OneDrive - WBG\FCV_Screener_test_cases` - sample project documents used to QA-test the app's outputs against these policies.

**Cross-reference these three sources together** (PPF folder + `OPCS docs.xlsx` + `LLM input on relevant project docs.docx`) when doing any OPCS-policy-consistency work - the spreadsheet and LLM-relevance docx let you avoid reading all 178 PPF files, by narrowing to the ones flagged as relevant to a given FCV instrument or topic before opening the actual PDFs.

**ACCESS RESTRICTION - read this before opening any of the above:**
**Only GitHub Copilot (this CLI / Copilot Chat / Copilot coding agent) is permitted to read the source files in the PPF folder, the `OPCS docs.xlsx` index, the `LLM input on relevant project docs.docx` triage doc, and the ESF Manual PDF.** Claude Code, OpenAI Codex, or any other coding agent working in this repository **must not** open, read, or ingest these source documents directly - even if asked to do OPCS-policy-consistency work. Other agents should work from **already-written, GitHub-Copilot-authored summaries** (e.g. design specs and plans under `docs/superpowers/`, or corrections already landed in `background_docs.py`/`app.py`) rather than the raw policy corpus itself. If a non-Copilot agent's task appears to require reading these source files directly, it should stop and ask the maintainer rather than accessing the folder.

**Version history:**
- **v7.0** — Redesigned from 4 stages to 3; full 12 OST recs + 25 key questions; FCV Playbook integration; Under the Hood panels; refresh_shift field
- **v7.2** — Stage 2 dynamic thematic narrative; actions[] array replaces recommendation string; Go Deeper 2-tab panel; Stage 3 clean memo (no inline citations)
- **v7.4** — Express Analysis mode (single SSE endpoint for all 3 stages)
- **v7.5** — UX polish: styled uploads, smart timer, condensed output, refined landing page; S/R definition box removed from Stage 3; rating rubric with reasoning block
- **v7.6** — Document format fixes: DOCX properly parsed via python-docx (base64, reading-order-aware, merged-cell dedup); PPTX support added via python-pptx; silent extraction failures surfaced as chip warnings and SSE banners
- **v7.7** — Concurrency hardening: per-tab assessment IDs in the frontend, assessment-aware request payloads, express workflow execution moved onto the background assessment executor, and multi-worker gunicorn defaults for better parallel use
- **v8.0** — Major knowledge base and prompt quality overhaul (branch `feat/v8-knowledge-base`, merged 2026-04):
  - **Knowledge base:** 6 instrument entries (IPF/PforR/DPO/TA/MPA/IPF-DDO) + 5 process guides (MTR/ISR/AF/Restructuring/ICR) + 29 glossary terms + FCS country list (2015–present)
  - **Prompt quality:** WB LLM quality review integrated — SEA/SH as 9th DNH principle, gender-FCV trigger block (7 conditions), lifecycle guardrails (SORT/ESF/SEP/ESCP minimum set for PAD), instrument routing guardrail per doc type, mandatory priority cards for gender and SEA/SH flags
  - **Temporal anchoring fix:** `_build_temporal_guardrail(temporal_ctx, doc_type)` now takes `doc_type`; PAD/PCN/PID/AF/Restructuring documents always receive preparation-phase framing regardless of whether approval date is in the past — prevents implementation-review hallucination cascade in Stages 2–3
  - **Stage 1 UX:** Prompt now requires 2–3 sentence narrative lead paragraph at top of each Part. Frontend `renderStage1()` parses Part A/B split and renders with styled section badges ("From your document only" / "Wider context & research"); narrative lead paragraph visually distinguished
  - **Finalized PAD notice:** `isFinalizedPAD()` detects uploaded PADs with past approval dates; amber retrospective notice injected in Stage 3 output and downloaded report
  - **FCS cross-checking:** `FCS_LIST` and FY26 category constants added to `background_docs.py` (35 FY26 FCS economies, with Conflict and Fragility metadata); injected into Stage 1 and Stage 2 prompts so LLM verifies classification against authoritative list
  - **Implementation review locked off:** `fcv_review_mode` localStorage restore IIFE removed; app always defaults to design review mode on load; implementation review preserved in backend for future activation
  - **Rating recalibration:** Percentage-based thresholds, partial credit for Weakly addressed, softened responsiveness cap
  - **Optional context box:** User can supply framing before analysis (peer review notes, changed conflict conditions)
  - **Step-by-step:** Load-first mode (full output on completion, not progressive streaming)
- **v8.1** — WBG LLM review batch + web research fix (branch `fix/wbllm-review-batch`, merged 2026-04-13):
  - **Instrument calibration:** New `FCV_INSTRUMENT_CALIBRATION` constant in `background_docs.py` — DPF failure modes (policy reversal, adjustment sequencing, programmatic series risk, Cat DDO scrutiny), FCV Envelope nuances (EDP, annual review requirement, eligibility logic), RRA as consultative process, trust funds and ASA as alternatives
  - **DPF guardrail (Stage 3):** ESCP, ESF standards, SORT-as-monitoring, and DLIs are now explicitly excluded for DPF/DPO instruments; recommendations framed around prior action conflict-sensitivity and reform sequencing instead
  - **Adjustment sequencing DNH (Stage 2):** New budget-support-specific DNH check on reform cost/safety net sequencing gap — flagged as the primary DNH pathway for DPF operations in FCV settings
  - **Citation discipline (Stage 1):** Part B now required to label training knowledge as `[From: general knowledge — ...]` not `[From: training knowledge - ...]`
  - **FCV Envelope eligibility guardrail:** Stage 1 prompt and `FCS_LIST` constant updated to prohibit explicit eligibility determinations for IDA FCV Envelope windows (PRA/RECA/TAA) — eligibility is multi-criteria and determinations risk being incorrect
  - **Web research timeout:** Research client timeout increased 45s → 120s; error now logged as `[WebResearch ERROR]` in Render logs
  - **Upload UI:** Project and contextual zone copy refreshed with PPSD/technical studies examples; "implementation coming soon" notice upgraded to amber banner
  - **Download:** Reports default to `.docx`
- **v8.2** — GPN integration + CPF upload support (branch `feat/v8.2-gpn-cpf-integration`, merged 2026-04-14):
  - **GPN enrichment:** `FCV_OPERATIONAL_MANUAL` enriched with two Good Practice Note subsections — "Peace & Inclusion Lens Dimensions" (5 dimensions: geographic targeting against RRA divides, social cohesion/reconciliation, project-cycle-specific application, conflict actor engagement, unintended consequences screening) and "Strategic DRR Framing" (DRR mapping, 4 P's framework, strategic vs operational distinction)
  - **CPF upload:** Country Partnership Framework accepted as named contextual upload; Stage 1 extracts automatically; Stage 3 adds `cpf_alignment` field (null if no CPF; string linking to CPF outcome if present)
  - **CPF_INTEGRATION_GUIDE:** New constant in `background_docs.py` injected into Stage 3 prompt (both step-by-step and express paths)
  - **Source attribution:** Good Practice Notes listed alongside OST Manual, Playbook, and Strategy in all 4 UI locations (onboarding modal, limitations note, pre-loaded sources banner, express progress screen)
  - **Architecture map:** `docs/fcv-agent-knowledge-architecture.html` — shareable HTML showing knowledge sources → pipeline stages → outputs
  - **Stage 3 timeout fix (2026-04-15):** Three-part fix for "BodyStreamBuffer was aborted" on Stage 3 in Express mode — (1) Express frontend now resets the abort timer to a fresh 8-minute budget when `stage_start:3` fires, rather than using whatever remains of the global 10-minute budget; (2) both Express and Step-by-Step backends now store a compact label for each stage's user prompt in `conversation_history` instead of the full 80k-char prompt, halving the Stage 3 API input size; (3) model updated from deprecated `claude-sonnet-4-20250514` to `claude-sonnet-4-6` across all call sites. Step-by-step Stage 3 timeout also raised from 6 → 8 minutes to match Express.
- **v9.0** — Differentiated knowledge architecture (branch `feat/v9-differentiated-approaches`, 2026-04-17):
  - **Country classification:** Stage 1 prompt outputs `%%%COUNTRY_CLASSIFICATION_START/END%%%` block (category, confidence, reasoning); `extract_country_classification()` parses it; `classify_country()` cross-references FCS list with bidirectional name matching
  - **Classification widget:** Rendered at top of Stage 1 output using `researchCountry` and classification reasoning; narrative format ("This analysis places [country] within the [category] category…"); always ends with caveat: "This is a subjective judgement on the part of this AI tool and does not constitute an official WBG classification."; dropdown override auto-saves on change; no confirmation step required
  - **Secondary knowledge snippets:** `select_secondary_knowledge()` picks category-specific knowledge snippets from `background_docs.py`; injected into Stages 2 and 3 prompts for differentiated framing
  - **`country_category_relevance` field:** Added to Stage 3 priority JSON — explains why each priority is particularly relevant for this country's specific FCV category
  - **DIFFERENTIATED_APPROACHES constant:** New knowledge constant in `background_docs.py` injected into Stages 2 and 3
- **v9.3** — MAI feedback improvements: knowledge base calibration, prompt quality, action_timing expansion (branch `feat/v9.3-mai-feedback-improvements`, 2026-04-21):
  - **Knowledge base — CERC calibration:** `FCV_INSTRUMENT_CALIBRATION` extended with CERC FCV notes: frame as "worth actively exploring" not required; emergency-to-emergency redirect risk; slow activation in FCV (practitioner experience, not formally evaluated); OP 7.30 trigger unavailability and OPCS clearance requirement
  - **Knowledge base — PforR calibration:** IVA access breakdown risk; DLI misalignment in low-governance; disbursement cliff (no CERC equivalent); ESSA limitations; OP 7.30 incompatibility ("effectively unusable"); phase transition risk in MPAs
  - **Knowledge base — MPA calibration:** Phase financing NOT guaranteed; electoral cycle exposure; institutional continuity assumption; OP 7.30 phase governance; combined MPA+PforR failure modes
  - **`action_timing` enum expanded to 5 values:** `flag-for-preparation` | `required-before-appraisal` | `required-before-board` | `next-series` | `supervision`; backward-compat remap: `pre-appraisal` → `required-before-appraisal`; UI pills and DOCX timing_map updated to match
  - **Stage 1 prompt — RRA cross-reference:** 3-case RRA fallback instruction before IDA FCV Envelope advisory: Case 1 (RRA uploaded — scenario cross-check with sub-items a/b/c), Case 2 (RRA known but not uploaded — invite upload), Case 3 (no RRA — note absence, summarise risk drivers)
  - **Stage 2 prompt — new supplementary dimensions:** SORT Adequacy Check (conditional on SORT table; reference ranges for 3 FCV categories; inherent vs residual E&S check); Forced Displacement (conditional on material displacement in doc); DNH: Economic Inclusion and Private Sector Harm Risk (conditional on private sector/skills + suppression context)
  - **Stage 2 prompt — enhanced dimensions:** Climate-FCV Nexus: stricter 3-condition trigger requiring documented country-specific climate-fragility pathway; HDP Nexus Coordination: narrowed to geographic+sectoral overlap, not country-level co-presence; added WBG comparative advantage framing
  - **Stage 3 prompt — PCN/PID calibration:** Stage Awareness expanded with differentiated rules (PCN = strategic risks only; PID = strategic + design/M&E; no PPSD/ESCP/SEA-SH AP requirements at PID); front-loaded work rule; action_timing guidance for PCN/PID stages
  - **Stage 3 prompt — CERC framing rule:** Inserted after instrument feasibility guardrail; frames CERC as "explore with OPCS focal points"; names redirect risk; explicit OP 7.30 trigger caveat
  - **Stage 3 prompt — Conditionality leverage guardrail:** ECA-type access mechanisms and reform DLIs with weak political economy compliance; theory-of-leverage framing; carve-out for routine fiduciary prior actions
  - **Stage 3 prompt — terminology rule:** 4 required replacements for non-WBG due diligence terminology (IDD, IDD protocol, private sector screening, implementing partner vetting)
  - **Stage 3 prompt — paired risk + systemic risk framing:** Strengths section requires embedded risk/limiting factor for top 3-4 strengths; systemic risk rule distinguishes externally-driven risks (monitoring) from design-addressable risks (recommendations)
- **v9.4** - Stream timeout hardening (branch `fix/stage3-stream-timeout`, 2026-05-06):
  - **Backend stream timeout:** `_stream_stage()` now enforces server-side stage wall-clock limits (Stage 1: 8 min, Stage 2: 6 min, Stage 3: 8 min) in addition to frontend abort timers. This prevents Stage 3 provider stalls from sending keepalives indefinitely and leaving Express or Step-by-Step runs stuck on the loading screen.
  - **Shared stream helper:** Step-by-Step now uses the same queue-based `_stream_stage()` helper as Express, so keepalive and timeout behavior is consistent across both modes.
- **v9.5** - Storage quota resilience and document-scope copy (branch `fix/stage2-storage-quota`, 2026-06-18):
  - **Stage 2 storage quota hardening:** Stage 2 Under the Hood persistence is best-effort via `static/fcv_storage.js`; quota failures no longer fail Stage 2 or block Stage 3.
  - **Document scope UX:** Landing/upload copy now frames supported inputs as WBG appraisal/design-stage documents across PCN/PID/PAD/AF/Restructuring plus DPF/DPO, PforR, MPA, and regional operations. MTR/ISR remains marked as implementation review coming soon.
- **v9.6** - Phase 1 mid-cycle overlay: Additional Financing & Restructuring (branch `feat/phase1-mid-cycle`, base Phase 0 `8389f39` / PR #24, 2026-06-17):
  - **Change-type block:** Stage 1 emits `%%%CHANGE_TYPE_START%%%...%%%CHANGE_TYPE_END%%%` (change_types; restructuring_level; rationale) for AF/Restructuring; stripped from display by `clean_stage1_output()`. Parsed by `extract_change_types()`; level derived by `derive_restructuring_level()`
  - **Audit-resolved restructuring level:** PDO change = Level 2 / RVP or CD-DD advisory signal (NOT Level 1). Level 1 is narrow: Alternative Procurement Arrangements and Bank Guarantee expiration-date extension only. Routing is advisory - verify with OPCS, no determinations. `RESTRUCTURING_GUIDE` + `AF_GUIDE` constants added; stale `WB_PROCESS_GUIDE[Restructuring]` Level-1 text corrected
  - **Mid-cycle temporal guardrail:** `_build_temporal_guardrail(temporal_ctx, doc_type)` returns MID-CYCLE LIVE-PROJECT FRAMING (Tier-1 anchored) for AF/Restructuring vs preparation framing for PCN/PID/PAD
  - **Registry/state:** `MODULE_REGISTRY` specialization for AF/Restructuring IPF single with `mid_cycle_overlay` guardrail + change_type output; `AnalysisState` carries change_types/restructuring_level
  - **Stage 2 overlay:** two linked checks per change - context-change since approval + conflict-sensitivity; AF waiver advisory; PDO ToC reassessment; reappraisal-trigger advisory
  - **Stage 3 priorities:** new change_type, restructuring_level, priority_scope fields + top-level mid_cycle_watch; Board-memo vs team-advisory register (7 top-level / 19 per-priority JSON fields)
  - **Export parity:** `/api/download-report` (DOCX) and `downloadHTML()` both render change/level/scope chips and a Mid-Cycle FCV Watch section
  - **Tests:** `tests/test_mid_cycle_phase1.py` (7 tests); full suite 87 passed; no IPF single-country regression
- **v9.7** - Phase 2 DPF/DPO instrument module (branch `feat/phase2-dpf`, base Phase 1 `feat/phase1-mid-cycle` / PR #25, 2026-06-17):
  - **Prior-action spine:** Stage 1 emits `%%%PRIOR_ACTIONS_START%%%...%%%PRIOR_ACTIONS_END%%%` (financing_source IBRD/IDA; series_position; cat_ddo; prior_actions; indicative_triggers) when INSTRUMENT_TYPE is DPO; parsed by `extract_prior_actions()`; stripped from display by `clean_stage1_output()`
  - **DPF rubric:** `DPF_RUBRIC` (prior-action conflict-sensitivity / reform-sequencing / PSIA / conflict-exception / macro-fiscal / political-economy) via the Phase 0 `score_sr()` interface - replaces the 12-OST '% addressed' rubric for DPF
  - **Registry/state:** `MODULE_REGISTRY` entries for `(PCN|PID|PAD|Unknown, DPO, single)` with `dpf_prior_action_spine` / `dpf_no_esf_escp_dli` / `dpf_macro_imf_headline` guardrails; `AnalysisState` carries financing_source / series_position / cat_ddo / prior_actions and auto-adds `dpf_module`
  - **Stage 2 overlay:** prior-action unit (no ESF/ESCP/DLI); headline 1 = macro framework / IMF coordination (para 8); headline 2 = conflict-exception adequacy (Paragraph 38-39); PSIA hybrid harm screen; series 24-month lapse / reversal; IBRD vs IDA; Cat DDO sub-branch
  - **Stage 3:** DPF-aware output (Program Document sections / policy matrix / LDP; DPF reference set; `next-series` timing); top-level `dpf_watch` array + DPF FCV Watch section in DOCX and HTML exports
  - **Knowledge:** `DPF_MODULE_GUIDE` + `DPF_POLICY_AREA_CHECKLIST` in `background_docs.py`, grounded in OPS5.02-POL.120 + OP 2.30; injected via `get_dpf_slice()`
  - **Tests:** `tests/test_dpf_phase2.py` (9 tests); full suite 96 passed; no IPF/mid-cycle regression
- **v9.8** - Phase 3 P4R/PforR instrument module (branch `feat/phase3-p4r`, base Phase 2 `feat/phase2-dpf` / PR #26, 2026-06-17):
  - **DLI + verification spine:** Stage 1 emits `%%%DLIS_START%%%...%%%DLIS_END%%%` (ipf_component; program_boundary; fcs_status; dlis; verification) when INSTRUMENT_TYPE is PforR; parsed by `extract_dlis()`; stripped from display by `clean_stage1_output()`
  - **P4R rubric:** `P4R_RUBRIC` (DLI conflict-sensitivity / IVA-verifiability / geographic inclusion / ESSA-ESMS / GRM / disbursement-cliff) via the Phase 0 `score_sr()` interface
  - **Registry/state:** `MODULE_REGISTRY` entries for `(PCN|PID|PAD|Unknown, PFORR, single)` with `p4r_dli_verification_spine` / `p4r_no_esf_escp` / `p4r_disbursement_under_conflict_headline` / `p4r_instrument_feasibility_advisory` guardrails; `AnalysisState` carries dlis / has_ipf_component, auto-adds `p4r_module`
  - **Stage 2 overlay:** DLI unit (no ESF/ESCP); headline = disbursement under conflict (IVA verification access + disbursement cliff, no CERC valve); DLI-realism; program-boundary/exclusions; ESSA/ESMS + GRM harm screen; OP 7.30 / government-systems feasibility advisory; IPF-component dual-spine
  - **Stage 3:** P4R-aware output (PforR PAD sections; DLI / verification-protocol / PAP language; P4R reference set); top-level `p4r_watch` array + P4R FCV Watch section in DOCX and HTML exports
  - **Knowledge:** `P4R_MODULE_GUIDE` in `background_docs.py`, grounded in OPS5.09 + OP 7.30; injected via `get_p4r_slice()`
  - **Tests:** `tests/test_p4r_phase3.py` (9 tests); full suite 105 passed; no IPF/mid-cycle/DPF regression
- **v9.9** - Phases 4+5 MPA wrapper + Multi-country / regional layer (branch `feat/phase45-mpa-multicountry`, base Phase 3 `feat/phase3-p4r` / PR #27, 2026-06-17):
  - **Multi-country / regional (orthogonal country_scope layer):** Stage 1 emits `%%%COUNTRY_SET_START%%%...%%%COUNTRY_SET_END%%%` (countries; regional_pdo; implementing_entity); `extract_country_set()` parses it (>=2 financed countries -> multi). `classify_country_set()` classifies each country (4-category + FY26 FCS) and flags non-FCS spillover/host-pressure candidates. `weighted_rollup()` does a fragility/exposure-weighted S/R roll-up (conflict x3, fragility x2) so a fragile minority is not masked. `REGIONAL_CROSSBORDER_LENS` + `get_regional_slice()`; cross-border lens, regional implementing-entity check (IGAD/ECOWAS/TDB), advisory financing-window pointers (Regional Window/CRW/WHR)
  - **MPA wrapper:** Stage 1 emits `%%%MPA_CONTEXT_START%%%...%%%MPA_CONTEXT_END%%%` (is_mpa; phase; base_instrument; regional_mpa; phase_transition_triggers); `extract_mpa_context()` derives approval authority (Board for Phase 1 / RVP for subsequent - advisory); `mpa_carve_outs()` suppresses subsequent-phase false positives (CERC/ESF/program-ToC/etc.); `MPA_MODULE_GUIDE` + `get_mpa_slice()`; adaptive-sequencing + institutional-continuity lens, cross-phase FCV-drift; routes each phase to its base instrument
  - **State:** `AnalysisState` sets country_scope=multi for >=2 countries and adds `multi_country_layer`; adds `mpa_wrapper` when is_mpa; carries is_mpa / implementing_entity / approval_authority
  - **Stage 2/3 overlays + output:** per-country + regional synthesis; `priority_scope` country-specific vs regional; top-level `regional_watch` + Regional FCV Watch section (DOCX + HTML); slices injected at Stage 2/3 (step-by-step via echoed country_scope/is_mpa; express via Stage-1 extraction locals)
  - **Tests:** `tests/test_mpa_multicountry_phase45.py` (13 tests); full suite 118 passed; no prior-phase regression
- **v9.10** - Phase 6 intersection matrix / multi-dimension composition (branch `feat/phase6-intersection`, base Phase 4+5 `feat/phase45-mpa-multicountry` / PR #28, 2026-06-17):
  - **Composition router:** `build_composition_plan(state)` selects the base instrument spine (IPF/DPF/P4R) and the active overlays (mid_cycle, multi_country) + MPA wrapper from `AnalysisState.active_modules`, and resolves **precedence**: mid-cycle live-project framing governs temporal; fragility-weighted roll-up governs rating when multi-country; restructuring level sets the output register; the instrument unit of analysis always governs. Backward-compatible (plain IPF -> no overlays)
  - **Single synthesis:** `dedupe_and_scope_priorities()` merges/dedupes priorities by normalised title and ensures a `priority_scope` on each
  - **Bounded injection (no silent truncation):** `bounded_injection_plan()` caps overlays by priority (instrument spine never dropped: instrument > mid-cycle > MPA > multi-country detail) and returns a disclosure string when anything is bounded
  - **Knowledge + prompt:** `INTERSECTION_SYNTHESIS_GUIDE` (layering, single coherent memo, precedence, bloat guardrail); Stage 3 prompt gains a Composition & Synthesis section; Stage 3 (both routes) injects the guide when `build_composition_plan(...).is_intersection` (>=2 active layers)
  - **Tests:** `tests/test_intersection_phase6.py` (8 tests); full suite 126 passed; no prior-phase regression. Completes the Phase 0-6 expansion (mid-cycle, DPF, P4R, MPA, multi-country, intersection) on the registry foundation
- **v9.11** - Secondary-document distillation and upload expansion (branch `feat/secondary-doc-distillation`, 2026-06-18):
  - **Upload tiers:** Zone 1 is a single required primary project document; Zone 2 accepts up to 10 supporting project-package documents; Zone 3 accepts up to 3 contextual documents.
  - **Secondary distillation:** `fcv_distillation.py` classifies and distills package/context documents into compact source-labelled cards before Stage 1 assembly. The primary document remains on the existing 60k-character Stage 1 path.
  - **Budget guard:** Secondary cards are capped per tier and by a global 32k-character budget with a context reserve. Overflow and distillation failures produce named stubs rather than silent drops.
  - **Stage 3 matching:** Priority JSON now includes `rra_driver_alignment` alongside `cpf_alignment`, so recommendations can link to RRA conflict drivers where uploaded and relevant.
- **v9.14** — Priority Points (branch `feat/priority-points`): single "Analysis guidance" box; client-side detection derives priority points from the text; a confirm strip (checkbox default ON) decides whether the answer panel is produced. Points injected as bounded soft emphasis into Stages 1–3 in both run routes (Stage 2 rating guardrail so ratings/DNH/rec-set are unaffected). New `/api/run-priority-questions` route fired AFTER the run completes (never inline, preserving the timeout design) + `extract_focus_questions` parser (`%%%FOCUS_QUESTIONS_START/END%%%`, truncation salvage; top-level `overview`). Single tinted "Responses to your priority points" panel: LLM-generated intro/overview + numbered responses, each a fuller 1–2 paragraph answer (route `max_tokens` 10k; blank-line paragraphs rendered in live/DOCX/HTML) + "Linked recommendations" + a "Note:" gap line. Status is internal-only (no pill); no evidence-basis line, no example chips, no per-answer re-run (further edits use the end-of-page follow-on box). DOCX + HTML export section; peer-review follow-on feed (`priority_responses`). Backend field names `priority_questions`/`focus_questions`; user-facing label "priority points".
- **v9.15** — PforR/DPO vocabulary-repair timeout fix (branch `feat/lending-diff-plus-priority-questions`, merged to `main` via PR #47, 2026-07-14):
  - **Root cause:** The Workstream-2 vocabulary repair (`repair_vocabulary_violations()`) ran a **blocking, non-streaming** Anthropic rewrite *after* the SSE stream had ended, and only for PforR/DPO (IPF returns no rule key and skips the path entirely). Because a substantive PforR output almost always leaks at least one banned ESS/SEP term, the repair fired on nearly every PforR run. With **no keepalives** reaching the client during that 1.5–3 min call — and PforR's outputs already being the longest in the app (near the Stage 2 6 min / Stage 3 8 min wall-clock caps) — the total request exceeded the frontend abort budget (`EXPRESS_STAGE_TIMEOUTS` S2 8m / S3 9m), tearing the stream as a Stage 2/3 timeout (`BodyStreamBuffer was aborted`). A secondary bug: the repair used `max_tokens=8000` against 16k/20k-token outputs, truncating long Stage 3 output and dropping the trailing `%%%JSON_START/END%%%` priorities block.
  - **Fix (deterministic scrub only):** `repair_vocabulary_violations()` now performs an **instant in-process regex scrub** with no LLM call — eliminating the blocking gap and the truncation. `_VOCABULARY_SCRUB_MAP` expanded to cover **every** banned term for PforR and DPO (previously only `ESS2`/`ESS4` were mapped, so `ESS1`/`ESS3`/`ESS5`–`ESS10` would pass through the scrub un-repaired). `\b` word-boundary matching means `ESS1` never matches inside `ESS10`, so ordering is irrelevant. The `violations` argument is retained for call-site compatibility but is no longer used (the scrub map is keyed on instrument). Behaviour is unchanged for IPF and for the four call sites (step-by-step S2/S3, express S2/S3). Tradeoff: scrub phrasing is blunter than an LLM rewrite (e.g. `ESS6` → "the ESSA", `SEP` → "the borrower's GRM"), accepted for determinism and zero timeout risk. `tests/test_vocabulary_validator.py` (2 new tests: no-LLM-call + all-banned-terms-scrubbed). Full suite: 203 passed.
  - **Note:** This PR also merged the previously-unmerged `feat/priority-points` (v9.14) and lending-diff / PforR SEA-SH reframing work onto `main` in one go — they had not been on `main` before PR #47.
- **v9.16** — PforR Stage 2/3 wall-clock caps raised (branch `fix/pforr-stage-timeout-caps`, 2026-07-14):
  - **Symptom:** After v9.15, PforR runs still timed out at ~6:55 elapsed. Evidence: the backend `STAGE_STREAM_TIMEOUTS[2]` cap was **6 min**; a large PforR PAD's Stage 2 stream (the app's largest output — 12-rec table, DNH, 25 questions, Under the Hood, ratings, category lens) legitimately ran up to that cap, and `_stream_stage()` raised `TimeoutError` at 360s into Stage 2 (Stage 1 ~55s + 360s ≈ 6:55 on the total-elapsed timer). The caps were set in v9.4 **before** PforR was added in v9.8, so they never accounted for PforR-scale output.
  - **Fix:** Raised backend caps `STAGE_STREAM_TIMEOUTS` to **S1 8m / S2 9m / S3 9m** (`app.py`). Raised the matching frontend abort budgets so each stays strictly above its backend cap (no frontend==backend race): Express `EXPRESS_STAGE_TIMEOUTS` → **S1 9m / S2 10m / S3 10m**; step-by-step `_stageTimeoutMs` → **S1 9m / S2 10m / S3 10m** (`index.html`). Step-by-step S1 (was 8m == cap) and S2 (was 6m == cap) had latent races that are now removed. All budgets sit well under the gunicorn `--timeout 1200` (20 min). `tests/test_stream_stage_timeout.py` unaffected (passes `max_seconds` explicitly). Full suite: 203 passed.
  - **Free-tier caveat:** The public Render service runs on the **free tier**, which spins down on inactivity (50s+ cold start) and is CPU/RAM-constrained. Raising the caps addresses the wall-clock cause, but reliable multi-minute SSE runs (PforR especially) ultimately want a paid Render instance. If a PforR run still times out after this, capture the Render log line at failure to distinguish an app-level stage `TimeoutError` (needs more time / smaller output) from a worker OOM/kill (needs a bigger instance).
- **v9.17** - Stage 1 timeout observability and distillation keepalive hardening (branch `fix/pforr-stage-timeout-caps`, 2026-07-14):
  - **Root cause correction:** The frontend abort timer calls `AbortController.abort(new Error(...))`; browsers may reject `fetch()` with that custom `Error` rather than an `AbortError`. The old catch block mislabelled such timeouts as `Could not reach the server`, so a 9-minute Stage 1 failure could be a frontend timeout, not necessarily a dropped connection or worker death. `requestErrorMessage()` now preserves custom timeout messages while still using the network fallback for true fetch failures.
  - **Stage 1 diagnostics:** Both `/api/run-stage` and `/api/run-express` now log low-cardinality Stage 1 preprocessing summaries (`docs`, role counts, aggregate uploaded content chars) and extraction completion timing (`elapsed_ms`, `doc_parts`, extracted chars, warning count). These logs avoid filenames/content but make Render failures easier to separate into frontend budget, preprocessing delay, extraction bottleneck, or worker OOM.
  - **Distillation keepalives:** `fcv_distillation.py` now yields each completed/timeout result as it arrives and emits `keepalive`/`distilling_wait` SSE events while slower secondary docs are still pending. This removes the previous collect-all silent window before Stage 1 model streaming.
  - **Upload-size guard:** Correct Render logs showed `/api/run-express` returning `500 106`, consistent with Flask's 50MB `MAX_CONTENT_LENGTH` being exceeded by a large base64 JSON upload rather than worker OOM. Oversized uploads now return an explicit `413` JSON response, and the frontend preflights file sizes before reading/submitting files, warning when raw files would exceed the deployment limit after browser base64 encoding. Tests added: frontend timeout classification, payload-size preflight, backend 413, per-doc distillation progress, Stage 1 payload diagnostics. Full suite: 208 passed.
  - **Main/Render state for IPS handover:** PR #51 merged these PforR timeout/payload changes to `main` as merge commit `2877bf9` on 2026-07-14. Live Render checks confirmed the Morocco Green Generation PforR PAD can complete end-to-end via `/api/run-express` (all three stages streamed; about 13:42 total in one run) and Stage 1 alone completed in about 4:14. A later India STARS PforR PAD live Express test hung before HTTP response headers and timed out client-side after 30 minutes, while local PDF extraction finished in about 18 seconds; treat that as a Render worker/gateway/pre-response stall pending Render-log review. The active IPS/ITS handover is `docs/20260714_ITS_handover_p4r_timeout_patch.md`.
- **v9.20** — Climate dedicated-module completeness hardening (branch `codex/climate-fcv-output-redesign`, 2026-07-24):
  - **Bug:** A live South Sudan PCN run rendered a silent "hybrid" — the two climate interaction boxes appeared, but the Reflections block, integration gauge, dividends synthesis, and wider-FCV note were missing (Render log: `Stage 2 lens diagnostic invalid ... The Climate-FCV diagnostic was omitted from the Stage 2 structured output`). Root cause: nothing enforced the v9.19 dedicated-module fields (`reflections`, `integration_level`, `integration_summary`, S/R evidence). Three layers each let them slip: the validity gate (`lens_diagnostic_failure_message`) accepts a diagnostic on materiality + one interaction alone; the Haiku recovery prompt (`repair_lens_diagnostic`) was written for the pre-v9.19 dual-use contract and never requested reflections/integration, so any recovery produced a valid-but-degraded readout; and a max_tokens-truncated primary (South Sudan is the app's largest output) dropped the diagnostic tail with no detection.
  - **Fix (full robustness):** (1) New pure helper `climate_readout_is_complete()` in `sector_lenses/pipeline.py` (complete = ≥1 grounded reflection AND non-empty `integration_summary`), plus `climate_lens_readout()`; both exported. (2) `extract_or_repair_lens_diagnostic` now triggers recovery not only on a hard failure but also when a *usable* climate diagnostic is incomplete, and **never downgrades a usable primary** — a recovered diagnostic is adopted only if the primary was unusable or the recovery is complete. (3) `repair_lens_diagnostic` prompt + compact-shape now request `integration_level`, `integration_summary`, 3–5 `reflections` (with `question_key` ∈ the six cq keys), `less_central`, and separate `sensitivity_evidence`/`responsiveness_evidence`; recovery `max_tokens` 6000→8000 and char budget 12,000→16,000. (4) Honest partial notice: when a usable readout is still incomplete after recovery, the module notice (frontend `renderClimateModuleNotice` via new `climateReadoutComplete()`; DOCX `add_climate_notice`; shared HTML via the same renderer) shows an amber "reflections and integration readout could not be generated for this run … were not substituted" line instead of silently omitting the sections. (5) Truncation observability: `_stream_stage` captures the provider `stop_reason`; both Stage 2 call sites log a warning when a climate-active Stage 2 hits `max_tokens`.
  - **Contract note:** "Usable" (interactions + materiality) is unchanged; "complete" (adds reflections + integration_summary) is the new bar that drives recovery and the honest notice. `climate_error`/`climate_valid` are unchanged; completeness is a separate, non-blocking signal (graceful degradation preserved — an incomplete-but-usable diagnostic is never dropped to core-only). ITS/FastAPI parity: add the completeness helper + recovery-prompt fields to `FCV_BUILD_PARITY.md`.
  - **Tests:** new `tests/test_climate_diagnostic_completeness.py` (helper, recovery-prompt fields, incomplete-triggers-recovery, no-downgrade, complete-skips-recovery) + frontend partial-notice test; existing bypass/recovery tests updated for the new complete-diagnostic contract and 8000/16,000 bounds. Full suite: 363 passed.
- **v9.23** - Climate-FCV country-bank runtime grounding (branch `feat/climate-country-bank`, 2026-07-31):
  - A public submodule at `data/climate-fcv-country-bank` supplies schema `1.0.0` approved-only runtime releases; `CLIMATE_COUNTRY_BANK_PATH` is the explicit local/deployment override.
  - Deterministic selection targets 8 and caps 12 bank items, 6,000 bank characters, and 12,000 combined bank/live characters.
  - Grounding states are `bank+research`, `bank-only`, `research-only`, and `thematic-only`. Live research failure is non-fatal. Express and step-by-step rematerialize canonical IDs server-side; the browser retains display-safe metadata only.
  - Dedicated Climate Stage 2 remains native. Reviewed structural evidence and accepted current/project-specific research enter one bounded untrusted-data block with evidence-status, causal, and uncertainty guardrails. Standard non-Climate routing is unchanged.
  - Live HTML, shared HTML, and DOCX show matching provenance. DOCX rematerializes the manifest and cannot accept browser-supplied reviewed-source metadata.
  - South Sudan is the initial single-country pilot and is approved in production content version `2026.07.south-sudan-pilot`; runtime materialization returns 12 selected items from 19 approved evidence records and seven approved pathways.
  - The companion bank stores structured summaries/citations, not raw PDFs; generated summaries cannot self-cite.
  - **Final reader polish:** the opening is a normal narrative section rather than a colored module notice, combining two-to-three scene-setting sentences with a project-specific "Why it matters" transition. Both mandatory interaction directions permit two short component-anchored paragraphs. Core-question status chips are hidden, framework labels read "For further insights on why this matters, see", and the gauge pairs its rating with a concise improvement message. Reader-facing climate summaries replace the noun "materiality" and clip on sentence boundaries where possible. The priority Next button is re-enabled when returning from the last card.
  - **Live-research recovery:** a structured `partial|complete` bundle that contains sources and claims but narrowly fails `climate_research_insufficient` may retry once within the existing two-attempt/deadline cap. Missing structured output, truncation, timeout, and terminal provider errors are never duplicated by this path.
- **v9.24** - Verified Climate-FCV evidence-to-decision runtime (branch `feat/climate-country-bank`, 2026-08-01):
  - Climate-only Express design reviews dispatch to `climate-verified-v2` after the existing country-bank/live-research resolver; mixed-lens, implementation-review, step-by-step, and stored legacy flows remain unchanged.
  - One unambiguous file explicitly placed in the Project Document slot becomes the bounded project-fact source, labelled `user_designated` rather than independently verified/latest; stage, geography, and financed-scope applicability remain unresolved. Unresolved package uploads remain inventoried but their fact authority is withheld; multiple candidate primaries force unresolved precedence. Runtime chunks are deterministic projections of extracted text, not original DOCX/PDF structural locators.
  - Four independent judgments replace the old single Climate integration label. The reader shows zero to three admitted/ranked priorities, condition-triggered enhanced actions, bounded readiness flags, and no generic High-priority labels.
  - Automatic deterministic checks suppress unsupported dependent objects; one conditional semantic reviewer runs only for high-risk judgments. No routine human review step is required.
  - `climate_assessment` and the canonical `climate_reader` are additive SSE fields. Live HTML and shared HTML render the server reader directly; DOCX deterministically rebuilds the same reader from the assessment. Reader state is preserved in session files and completed Express checkpoints; zero-priority HTML/DOCX outputs retain the explicit no-recommendation admission message; candidate-bank outputs retain `preview; not approved`.
  - The browser budget is 15 minutes; backend verified execution is capped at 14 minutes, bounds retry time across attempts, emits keepalives, and cancels later model calls after timeout or disconnect.
  - Privacy-safe recommendation diagnostics record raw, parsed, structurally valid, gate-admitted, and final counts; deterministic admission reason codes; up to 12 unsupported numeric tokens; and whether the conditional semantic reviewer ran and its bounded verdict. Numeric component/subcomponent labels are auto-supported only from candidate-linked verified project facts, while suffixes of structured IDs and numbered-list markers are excluded from numeric-claim checks; unsourced dates, thresholds, and quantities remain blocking. The same fields appear in the technical annex and one bounded Render log line, without candidate prose.
- **v9.27** — Verified reader smoke-review refinements (same branch, 2026-08-05, after a live smoke render review): (1) the generic "overall reads" strip is replaced by a headline **climate & FCV sensitivity rating** — `build_reader_model` derives `climate_sensitivity_rating` from the retained internal `sensitivity` judgment on a Limited→Moderate→Strong scale (`_SENSITIVITY_RATING`, `level` 0-3, tone colours, evidence IDs, AI-judgement caveat) rendered as a segmented scale in frontend + server HTML and as text in DOCX (`_sensitivity_rating_html`); `judgment_reads` removed. (2) Core-question summaries lengthened to ~120-220 words in two short paragraphs (schema + prompt) and rendered with paragraph breaks on all surfaces. (3) `_METHODOLOGY_NOTE` rewritten in plain, lay language. (4) `build_evidence_trail` now drops pathways with empty `chain_prose` and evidence-key entries that resolve to empty text (removes the smoke-model naked "Climate -> FCV:" bullets and bare PW- codes). Tests updated + added in `test_climate_core_questions.py`; full suite 562 passed.
- **v9.26** — Verified Climate-FCV reader lay-comprehensibility redesign (branch `feat/climate-reader-lay-comprehensibility`, base `codex/climate-country-bank-deploy` `6a59a6f`, 2026-08-05). Makes the verified reader (`climate-verified-v2.1`) legible to a lay, first-time reader seen blind, and removes executive-summary repetition — while preserving the evidence-gated, cannot-promise discipline that won the blind eval. Four workstreams:
  - **WS1 — sources + provenance clarity:** `CLIMATE_LITERATURE_REFERENCES` entries gain a plain-language `description`; "Sources & further reading" renders title + description with linked WB publication pages, and name-only sources (`url=None`) are explicitly marked "reference only; no public link shown until confirmed" (never fabricated). The provenance annex gains lay intros for "Pathways" and the "Evidence key"; the "Points to check" intro is rewritten in plain language; server `HEADINGS[3]` + DOCX label unified to the frontend "Points to check before the decision meeting" (fixes a prior parity mismatch).
  - **WS2 — Core climate-FCV questions (replaces the four judgment boxes):** `climate_question_bank` wired into the verified pipeline for the first time — `project_signals` derived from verified facts (`_core_questions_to_answer`), up to six triggered questions posed at the judgment stage, only evidence-grounded answers kept (`_admit_core_questions`: question posed + ≥1 cited evidence ID resolves), capped at five. New `core_questions` field + `CORE_QUESTION_SCHEMA` on the judgment stage, with a no-overlap-with-executive-readout rule, source attribution, and a cannot-promise "what to watch" line. The four judgment VALUES are retained internally (calibration + semantic-reviewer risk); the reader shows a compact "overall reads" strip (sensitivity / responsiveness / from-intent-to-delivery; relevance dropped from view as it echoed the exec readout) + literature-grounded question cards. `HEADINGS[1]` → "Core climate-FCV questions".
  - **WS3 — Smaller climate & fragility points to check:** new `minor_climate_points` + `MINOR_CLIMATE_POINT_SCHEMA` on the **judgment** stage (hosted there rather than the recommendation stage to keep the latter under its 4100-char transport-complexity budget) — up to three smaller climate/FCV points tied to a residual gap that may not warrant a full recommendation. `_admit_minor_climate_points` gates them (gap exists AND not covered by an admitted priority; deduped against priority titles + readiness-flag text; cap 3). "Points to check" renders two labelled groups — "Document points to confirm" (existing integrity flags) + "Smaller climate & fragility points to consider".
  - **WS4 — recommendation-details intro:** the frontend "Recommendation details" collapsible gains a plain-language intro for first-time readers.
  - **Parity + guards:** every reader change lands in the frontend `renderClimateVerifiedAssessment`, server `render_reader_html`, and DOCX `write_reader_docx`. Readers without `core_questions` / `minor_climate_points` (older/blank) still render (reads strip only; single points-to-check group). All additive fields are non-gating (`build_reader_model` / `validate_reader_model` unaffected).
  - **Smoke caveat:** core-question cards and minor points are model-generated, so a cheap smoke run may return few/none (schemas allow empty arrays); the reads strip, intros, and section structure render regardless — real content appears on a quality run.
  - **Tests:** `tests/test_climate_core_questions.py`, `tests/test_climate_minor_points.py` + updates to literature / render / evidence-trail / app-contract tests. Full climate/sector suite: 560 passed (baseline 550). Not yet deployed (smoke auto-deploys on push to `codex/climate-country-bank-deploy`). ITS/FastAPI parity logged in `FCV_BUILD_PARITY.md` §26.
- **v9.25** - Verified Climate-FCV TTL drafting integrity (`climate-verified-v2.1`, branch `feat/climate-country-bank`, 2026-08-03):
  - Each admitted priority requires a structured 90-160 word current-document drafting block. A second operational-instrument block is optional and survives only when distinct and linked to an evidenced named instrument. `team_to_confirm` and `new_vehicle_may_be_needed` are not successful recommendation routes; safe stage-document advice uses `standard_document_advisory`.
  - A versioned, bounded operational-guidance registry selects permitted PCN/PAD destinations by document and instrument type. It is advisory context, not project evidence or a policy corpus, and contains no fabricated policy paragraph citations.
  - Deterministic validation blocks unsupported instruments, actors, effectiveness/appraisal timing, technical systems, mandatory wording, and drafting references. Telemetry records only reason codes and field paths. Readiness flags carry residual-gap IDs and are suppressed when they duplicate admitted priorities.
  - Every judgment value, including `unclear`, `not_expected`, and `not_evidenced`, requires a resolvable evidence ID. The final-priority summary is derived only after deterministic admission and semantic review.
  - Accepted live research is counted from distinct `CE-LIVE-*` evidence IDs; mixed valid/invalid source declarations are rejected. Browser, HTML, and DOCX render the same drafting labels, destinations, status, guidance basis, text, priority summary, provenance count, and `preview; not approved` evidence label.
  - Raw OPCS/ESF material remains outside the runtime and repository workflow. Any later WBG Cowork review is a separate, targeted conformance check of selected registry propositions and wording boundaries.

- **v9.22** — Climate-FCV readout redesign: core-question bank + reader layout (branch `feat/climate-readout-redesign`, base `main` post-#55, 2026-07-27):
  - **Core-question bank:** new pure `climate_question_bank.py` — a WBG-source question bank (six stable themes cq1-cq6, each question carries a `source` + lowercase `triggers`) + `select_triggered_questions(project_signals)` that fires per-theme questions from Stage-1-derived signals (cq1 always guaranteed). Sourced from the unrestricted climate-FCV frameworks under `docs/climate_module/` (Maximizing the Peace and Social Dividends of Climate Action; FCV-Sensitive Climate Action Framework; Defueling Conflict; Conflict-Sensitive Climate Action Compendium; CCDR guidance note). `tests/test_climate_question_bank.py`.
  - **Diagnostic contract additions** (`sector_lenses/pipeline.py`): climate `reflections[]` gain a `source` field and a larger two-paragraph `text` bound (700→1800; title 80→160; cap 5→6); new 6-tier `integration_rating` (`Extremely Low`..`Very Well Embedded`, via `climate_integration_rating()`, `''` when absent, keeps `integration_level` for back-compat); new `strengths_weaknesses[]` (`_normalize_climate_sw`, `{side: strength|gap, title, text}`, ≤4 per side).
  - **Stage 2 climate-native prompt** (`build_lens_stage_context`, `project_signals` kwarg wired at both routes): injects the triggered bank, requests per-theme two-paragraph answers with `source`, the 6-tier `integration_rating`, and structured `strengths_weaknesses`. Recovery prompt (`repair_lens_diagnostic`) mirrors source/rating/two-paragraph + the OPCS §12 boundary one-liner.
  - **Phase 4B — OPCS §12/§12.9 calibration:** Stage 2 climate suffix gains the recommendation-calibration guardrails (instrument-route; PA/CDRS flag-not-determine; no universal numeric horizon → "asset-appropriate design horizon"; IPF-only ESS map; conditional compound-risk wording; analytical-source labelling). Stage 3 climate prefix drops `wider_fcv_context` (parsed for back-compat, no longer requested) and gains §12.5/§12.9 CERC + CDRS + AF/Restructuring/MPA guardrails + the `authority_basis` tag (shared with the dual-regime field; not re-added). Climate module `manifest.yaml` stage3 line no longer requests `wider_fcv_context`.
  - **Budgets:** `PLATFORM_STAGE_BUDGETS` Stage 2 2000→3300, Stage 3 1200→1600; `_bounded_stage3_lenses` token target 1100→1500 (fit the bank + calibration + S&W).
  - **Native-route context boundary:** Dedicated Climate-FCV Stages 2-3 call `build_lens_stage_context(..., compose_prompt=False)` in both Express and step-by-step paths. This preserves authoritative lens metadata, sources, version checks, and diagnostic normalization without composing the discarded legacy sector-lens prompt.
  - **Frontend + exports:** 6-tier gauge (`climateIntegrationRatingFraction`, legacy 4-tier fallback); new `renderClimateCoreQuestions` (lay intro naming the source literature → both interaction directions in prose → per-theme answers with soft status + source line) and `renderClimateStrengthsWeaknesses` (two-column full detail). New climate readout order = notice/gauge → strengths & weaknesses → core questions; standalone dividends + wider-FCV sections dropped in module mode. Live HTML, shared HTML (`downloadHTML`), and DOCX (`add_climate_core_questions` / `add_climate_strengths_weaknesses`) kept in parity.
  - **Tests:** `tests/test_climate_question_bank.py` + extensions across pipeline, app-contract, and frontend suites; South Sudan fixture extended with `source`/`integration_rating`/`strengths_weaknesses`. Full suite: 454 passed.
- **v9.21** — Dual-regime process model: legacy PAD ↔ new-model Project Paper (branch `feat/dual-regime-process-model`, PR #55, 2026-07-27). *(Version-history entry recovered here: the original dual-regime docs commit staged nothing for this file because the guide is tracked as lowercase `claude.md` and `git add CLAUDE.md` silently no-ops — see the reference docs for the full spec.)* Two independent axes: `preparation_regime` (`new_model`|`legacy_transitional`|`unresolved_policy_source`, governed by OIS date vs 18 Apr 2026) and `es_regime` (ESF/legacy-safeguards/PS/instrument-specific/unresolved, governed by Concept Decision date vs 1 Oct 2018). Pure `regime_router.py`; Stage 1 `%%%REGIME_CONTEXT%%%` detection (`extract_regime_context`); terminology (`appraisal_document_label`, `pad_sections`↔`appraisal_document_sections`); regime-aware `action_timing`; regime-gated minimum reference set (`appraisal_reference_set`); `build_regime_header`/`build_minimum_reference_block` injected into Stage 2/3 (both routes); `authority_basis` recommendation field. Legacy + unresolved render byte-for-byte unchanged. Full suite: 436 passed.
- **v9.19** — Climate-FCV dedicated module output + OPCS compliance guardrails (branch `codex/climate-fcv-output-redesign`, 2026-07-24):
  - **Dedicated module output:** selecting the Climate lens now produces a dedicated climate-FCV assessment. The six core questions (cq1_interaction, cq2_maladaptation incl. lock-in, cq3_dividends, cq4_inclusion, cq5_institutions, cq6_adaptive) are the Stage 2 internal spine; the general FCV engine is retained only as an internal input.
  - **Diagnostic contract additions** (`sector_lenses/pipeline.py`): per-climate-lens `reflections[]` ({question_key,title,status_cue,text}), `less_central`, `integration_level` (well_integrated|partly_integrated|weakly_integrated|insufficient_evidence; safe `insufficient_evidence` default — no material→moderate), `integration_summary`, and separate `sensitivity_evidence`/`responsiveness_evidence`. Stage 3 priorities JSON adds top-level `wider_fcv_context` and per-priority `policy_status` + `specialist_referral` (`extract_priorities`).
  - **Output redesign:** causal-strip diagram replaced by two prose interaction boxes; new "Reflections on core climate and FCV considerations" block with soft status chips; single "How well does the project integrate climate and FCV?" gauge (reframed "Indicative Climate-FCV Integration Readout") replaces the two S/R gauges in module mode; "Wider FCV context" callout; reorder to interactions → reflections → dividends → wider-FCV. Live HTML, shared HTML, and DOCX kept in parity.
  - **OPCS compliance guardrails** (from WBG LLM review): explicit POLICY BOUNDARY (advisory only; not an ESF/ESS/ESRC determination) in prompts, UI notice, and DOCX; instrument/framework-awareness guardrail; CQ2/CQ4/CQ5 refinements (managed-risk vs new-gap; open-list vulnerability; contextual institutions); dividends never framed as requirements; cross-document consistency; two source layers (current policy vs analytical). Hybrid structured layer: `policy_status` + `specialist_referral` surfaced in exports, understated in UI.
  - **Budgets:** Stage 3 sector-lens ceiling raised 900→1200 (`PLATFORM_STAGE_BUDGETS`) to fit the richer dedicated Stage 3 prompt; `_bounded_stage3_lenses` target 890→1100, findings cap 700→900.
  - **Tests:** extended across pipeline, priorities, app-contract, package, and frontend suites + the South Sudan regression fixture. Full suite: 348 passed.
- **v9.18** - Sector-lens diagnostic recovery reliability (2026-07-22):
  - Missing or incomplete active-lens Stage 2 diagnostics trigger one dedicated Haiku recovery request. Its client has a 120-second default/read timeout, a 10-second connection timeout, and zero SDK retries.
  - Recovered output is strictly parsed, normalized, and validated against the active-lens contract before use. Express and step-by-step routes call the same recovery function and follow the same behavior.
  - Recovery failure is non-fatal to the core FCV assessment: the original diagnostic failure remains explicit in the parse-error payload, while invalid, failed, recovered, and unsuccessful recovery outcomes are logged.
- **v9.12** - Express per-stage abort budgets (branch `fix/express-stage2-timeout`, 2026-06-19):
  - **Stage 2 "BodyStreamBuffer was aborted" fix:** Express mode armed a single 10-minute frontend abort timer covering Stages 1 and 2, reset only at `stage_start:3`. A slow Stage 1 (web research on a fragile-context AF) could consume the shared budget, firing the timer mid-Stage-2 and tearing the fetch stream. `armExpressTimeout(stage)` now re-arms the abort timer at every `stage_start` with per-stage budgets (`EXPRESS_STAGE_TIMEOUTS` = S1 9m / S2 8m / S3 9m), each sitting above the backend wall-clock limits (S1 8m / S2 6m / S3 8m) so the backend stage error surfaces before the frontend tears the stream. Also removes a latent Stage 3 race where the frontend 8m budget equalled the backend 8m limit.
- **v9.13** - CERC conflict-trigger guardrail (branch `fix/cerc-violence-guardrail`, 2026-06-19):
  - **Stage 2/3 CERC guardrail:** Prompts now prohibit recommending CERC, or flagging absence of CERC readiness as a gap, for violence/conflict escalation, insecurity, armed-group activity, civil unrest, or access constraints alone.
  - **Eligible CERC framing:** CERC can be recommended only where there is a credible natural-hazard, climate, health, or economic emergency exposure and a plausible borrower emergency declaration/request pathway. The specific hazard pathway must be named.
  - **Alternative levers:** Conflict/violence-driven implementation risk should be routed to adaptive management, POM stop/go provisions, security-triggered restructuring, SORT updating, conflict-sensitive indicators, Security Management Plan, TPM/GEMS, or IPF urgent-need/condensed procedures.
  - **Knowledge-base alignment:** `FCV_INSTRUMENT_CALIBRATION`, CERC guidance, differentiated country guidance, IPF applicability checks, rapid-response guidance, and procurement-in-FCV guidance were updated to remove the previous "CERC for conflict escalation" framing and non-standard trigger workaround examples.
- **v9.14** - OPCS policy consistency: instrument-conditional vocabulary, programmatic validator, KB corrections, classification tightening, lifecycle detection, MPA governance_level (branch `feat/opcs-policy-consistency`, 2026-07-02):
  - **Workstream 1 — instrument-conditional SEA/SH & DNH vocabulary (QA Issues 1, 2, 4):** The hard-coded, unconditional "DNH Principle 9" (SEA/SH) block in `DEFAULT_PROMPTS["2"]` and the "Gender-FCV / SEA-SH Card Rule" block in `DEFAULT_PROMPTS["3"]` are now placeholders (`{dnh_seash_guidance}` / `{seash_gender_card_guidance}`) gated on `INSTRUMENT_TYPE`. Six new `background_docs.py` constants (`DNH_SEASH_IPF/PFORR/DPF`, `SEASH_GENDER_CARD_IPF/PFORR/DPF`) + selectors `get_dnh_seash_guidance()` / `get_seash_gender_card_guidance()` in `app.py`. IPF keeps ESF/ESCP/ESS2/ESS4/RF language; PforR uses ESSA Core Principle #6 + PAP + ESMS; DPF/DPO uses PSIA + Program Document + Adjustment Sequencing. The PforR/DPF variants are deliberately free of the ESF acronyms themselves (they describe the excluded instruments in plain language) so they neither seed banned vocabulary nor trip the Workstream 2 validator. Injection wired at all four design-review call sites (step-by-step S2 `.replace`, S3 `.format` kwarg; express S2 `.replace` after MPA slice, S3 `.format` kwarg — express S3 uses the kwarg, NOT a post-format `.replace`, to avoid a `KeyError` that would blank every placeholder). Impl-review prompts (`impl_2`/`impl_3`) are untouched (no placeholder → their `.format()`/`.replace()` sites are unaffected). `tests/test_vocabulary_gating.py`.
  - **Workstream 2 — programmatic vocabulary validator + silent repair:** `validate_instrument_vocabulary(output_text, instrument_type)` scans Stage 2/3 output for banned ESF/ESCP/ESS/SEP terms (PforR/DPO only) using whole-word `\b` matching (so "SEP" does not match "separate"/"September" and "ESS1" does not match "ESS10"). On a hit, `repair_vocabulary_violations()` runs one bounded non-streaming Anthropic rewrite, then a deterministic `\b`-anchored regex scrub as last resort, logging any residual server-side only (`app.logger.warning`) — never a user-facing error, per product decision. Wired into the step-by-step route (`if not is_impl and stage in (2,3)`) and both express Stage 2/3 hooks. `tests/test_vocabulary_validator.py`, `tests/test_vocabulary_repair_wiring.py`.
  - **Workstream 3 — knowledge base corrections (OPCS source audit):** `MPA_MODULE_GUIDE` no longer lists DPF as a valid MPA phase instrument (only IPF or P4R under OPS5.01-POL/DIR) and no longer states RVP-approves-all-subsequent-phases as absolute (Board referral possible for material scope/cost/PrDO changes); `AF_GUIDE` no longer names RVP as the approval level for all waivers; `P4R_MODULE_GUIDE` reframes OP 7.30 as a feasibility constraint (not a formal cross-reference), removes the "Category-A-equivalent" mislabel, and adds the Rapid Response Option (RRO, OPS5.04-POL.125 para 12); `FCV_INSTRUMENT_CALIBRATION` replaces the unverified "EDP" acronym with a verification-flagged description; `app.py` no longer presents WHR as an FCV Envelope (FCVE) allocation in the Stage 1 prompt or the `RenderSourceProvider` summary. `tests/test_knowledge_base_corrections.py`.
  - **Workstream 4 — FCV classification tightening (QA Issue 3):** Stage 1 prompt gains a geographic-footprint anchoring rule (sub-national risk factors must be checked against the project's actual implementing regions before being cited) and a mandatory one-line `trigger` field in the `%%%COUNTRY_CLASSIFICATION%%%` block; `extract_country_classification()` parses `trigger`. `tests/test_classification_tightening.py`.
  - **Workstream 5 — lifecycle detection (QA Issue 5):** Document-text-only. New `lifecycle_status` field in the `%%%TEMPORAL_CONTEXT%%%` block (`active` | `closed - <reason>` | `Unknown`); `extract_temporal_context()` parses it (defaults to `active` for legacy blocks, `Unknown` when the block is missing). Frontend `isClosedOrCompletedProject()` / `closedProjectStatusReason()` render an amber advisory banner in `renderOut()` (never a hard block), mirroring `isFinalizedPAD()`. Designed so a future WBG project-status/P-code lookup can populate the same field without a contract change. `tests/test_lifecycle_detection.py`.
  - **Workstream 6 — MPA `governance_level` field (QA Issue 6):** New Stage 3 priority field `governance_level` (`"Regional Platform"` | `"Country Phase"` | null for non-MPA) added through the full pipeline: prompt schema (21 fields), `_REQUIRED_PRIORITY_FIELDS`, `extract_priorities()` enum validation, frontend chip in `showPriority()`, and DOCX export metadata line. `tests/test_governance_level_field.py`.
  - **Deviations from the source plan (documented):** (1) Two selector-test/constant inconsistencies in the plan were reconciled by making the constants match the tests' clear intent (PforR/DPF variants stripped of raw ESF acronyms; IPF DNH test asserts `ESS2`, the acronym actually present, not `ESS4`); (2) the validator/scrub use `\b` word boundaries (plan omitted them) to prevent false-positive repairs on common words; (3) express Stage 3 wiring uses a `.format()` kwarg rather than the plan's post-MPA-slice `.replace()`, which would have raised `KeyError` and blanked all placeholders; (4) `tests/test_phase0_foundation.py` updated to reference the relocated SEA/SH risk-classification string now living in `DNH_SEASH_IPF`; (5) commits omit the `Co-Authored-By: Copilot` trailer specified in the handover, per the repo owner's standing global instruction that no AI-attribution trailer appear in any commit. Full suite: 180 passed (baseline was 140).
- **v9.2** - Classification caveat and background_docs policy corrections (branch `feat/v9-differentiated-approaches`, 2026-04-19):
  - **Classification widget caveat:** Narrative now always ends with "This is a subjective judgement on the part of this AI tool and does not constitute an official WBG classification." — consistent with Stage 1 AI disclaimer framing
  - **background_docs.py — ICR timing:** `STAGE_GUIDANCE_MAP["ICR"]["timing_options"]` corrected from `"During implementation"` to `"At project closing"`
  - **background_docs.py — Para 12 naming:** Removed all incorrect "Para 11" / "Para 11/12" references; standardised to "Paragraph 12 of Section III of the IPF Policy" with correct two-situation description (urgent need; capacity constraints); clarified Para 12 is NOT required for Framework Approach, Phased Implementation, or Unallocated Funds
- **v9.1** — UX, prompt quality, and bug fixes (branch `feat/v9-differentiated-approaches`, 2026-04-18):
  - **DOCX download fix:** `downloadReport()` now POSTs to new `/api/download-report` route; backend generates a true python-docx binary (not HTML masquerading as .docx). New helpers: `_md_to_docx_para()` (markdown→docx paragraphs), `_safe_run()` (safe runs[0] access)
  - **Stage 1 prompt — prose narrative:** Body content now required to be prose paragraphs (2–4 sentences per subsection); bullets restricted to genuinely enumerable items only
  - **Stage 1 prompt — country-specific fact flagging:** Part B must tag unverifiable country-specific claims (named institutions, legislation, political events, officials) with `[Verify: ...]` inline
  - **Stage 1 prompt — IDA FCV Envelope advisory:** For Conflict-Affected and Situations of Fragility countries, adds a brief end-of-Part-B advisory prompting TTL to discuss PRA/RECA/TAA eligibility with regional FCV coordinator (not an eligibility determination)
  - **Stage 2 prompt — Refresh shifts as qualitative lenses:** FCV Strategy 2026-2030 shifts explicitly framed as analytical lenses for strategic alignment, not a scoring checklist
  - **Stage 3 prompt — Watch List for Supervision:** "Horizon Considerations" section renamed and reframed as "Watch List for Supervision"; each item must name a specific WBG tracking vehicle (ISR risk flag, MTR agenda item, RRA update, restructuring trigger); panel heading in frontend updated to match
  - **Stage 3 priorities — `action_timing` field:** New enum field (`pre-appraisal` / `next-series` / `supervision`) with coloured pill in UI and included in DOCX download
  - **SORT guardrail:** Stage 3 prompt now prohibits prescribing specific SORT ratings; frames risk exposure as "consider whether the current rating adequately reflects X"
  - **Source credibility flagging:** Stage 1 Part B labels source type inline (`[Data: high-quality]`, `[Data: secondary]`, `[Source: news/media]`); data gap flagging for missing FCV dimensions
  - **Classification confirm button removed:** Dropdown auto-applies on change via `onchange` listener; `confirmClassification()` function deleted; act-area no longer hidden
  - **Step-by-step loading timers:** Elapsed timer and rotating stage-specific messages added; hints updated to reflect real durations (Stage 2: 3–5 min, Stage 3: 4–6 min)
  - **Paragraph spacing fix:** `.out-body p` CSS set to `margin-top: 0; margin-bottom: 0.5em` to eliminate double gaps in Stage 1 output
  - **CPF upload encouragement:** Contextual zone hint updated with bold/underlined CPF prompt; SCD removed; RRA mentioned as secondary option

---

## Repository Structure

### What's in the public GitHub repo
The repo contains only what's needed to understand, deploy, and maintain the app:
- Core app files: `app.py`, `background_docs.py`, `index.html`
- `docs/reference/` — detailed specs for prompts, routes, and frontend functions
- `docs/fcv-agent-knowledge-architecture.html` — shareable knowledge architecture diagram
- `tests/` — unit tests for priority extraction
- Deployment files: `requirements.txt`, `Procfile`, `.gitignore`, `README.md`

### What's kept locally only (not in the repo)
These folders exist on the development machine but are gitignored — do not commit them:
- `app_feedback/` — internal review documents, colleague feedback, test PDFs
- `docs/superpowers/` — implementation plans and design specs from development sessions
- `.claude/` — local Claude Code configuration
- `.superpowers/` — brainstorming session artifacts
- `AGENTS.md` — internal agent instructions
- Session handoff notes (e.g. `docs/*SESSION_HANDOFF*`) and dev mockups (`docs/mockup_*`)

---

## 1. Project Architecture

### 1.1 Tech Stack
- **Backend:** Python Flask 3.0.3 + Anthropic Claude API (`claude-sonnet-4-6`)
- **Frontend:** HTML + vanilla JavaScript + Markdown rendering
- **Hosting:** Render.com (gunicorn + gevent)
- **Concurrency model:** Per-tab assessment IDs in the browser; Express runs emitted from a background assessment executor; multi-worker gunicorn in production
- **Document processing:** PDF (pypdf), DOCX (python-docx), PPTX (python-pptx) text extraction; all binary formats sent as base64 from browser
- **Session management:** Browser storage namespaced by per-tab assessment ID + JSON-serialized conversation history

### 1.2 Core Files
```
app.py              # Flask backend, all prompts (DEFAULT_PROMPTS), routes, document processing
index.html          # Single-page frontend UI (Stage 1–3, Go Deeper, Express mode, prompt modal)
background_docs.py  # 10 constants: FCV_GUIDE, FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK,
                    #   PLAYBOOK_DIAGNOSTICS, PLAYBOOK_PREPARATION, PLAYBOOK_IMPLEMENTATION,
                    #   PLAYBOOK_CLOSING, STAGE_GUIDANCE_MAP, FCS_LIST, CPF_INTEGRATION_GUIDE
                    #   + WB_INSTRUMENT_GUIDE, FCV_GLOSSARY, WB_PROCESS_GUIDE, FCV_INSTRUMENT_CALIBRATION (helpers)
prompts.json        # Session-specific prompt overrides (empty by default)
requirements.txt    # Flask, anthropic, pypdf, python-docx, python-pptx, gunicorn, gevent
Procfile            # Render deployment config
```

### 1.3 Three-Stage Pipeline

**Current upload tiering:** Zone 1 accepts exactly one primary project document; Zone 2 accepts up to 10 package documents that are distilled into key-signal cards; Zone 3 accepts up to 3 contextual documents distilled into RRA driver / CPF pillar cards or generic context cards.

**Two workflow modes:** Express Analysis (default — all 3 stages run automatically via `/api/run-express`) and Step-by-Step (interactive, one stage at a time via `/api/run-stage`). Same prompts, same output quality.

**Optional sector lenses:** users may select up to two ordered lenses. Both workflows resolve authoritative module versions and inject the same bounded stage slices. Lens findings must map to existing OST/DNH/Strategy criteria; they do not add a score or separate recommendation list. The production Climate-FCV Lens is manual-only and never auto-suggested. After selection it screens climate-intent and wider development operations automatically, prioritizes adaptation, and activates deep mitigation only for a clear pathway. Core-only retains 4-5 substantive priorities and the lightweight Climate-FCV check; active Climate supersedes that check and uses no more than five substantive priorities with a flexible evidence-led mix. `lens_context_sources` persists optional validated Climate research and World Bank CCDR sources without making CCDR material a routine recommendation.

**Climate-active dual-use contract (implemented on `codex/climate-fcv-output-redesign`):** Stage 1 runs reduced core research and one dedicated bounded trusted-source Climate pass concurrently, with one narrower retry. Stage 2 requires both directional interaction pathways with stable IDs, project/place/group/system anchors, causal steps, confidence, evidence gaps or research claim IDs, and current/project/asset-system horizons. Stage 3 retains both causal directions inside the 900-token lens ceiling and validates `climate_links` on every priority as either `linked` to recognized interaction/dividend/finding IDs or `no-material-pathway` with a concrete reason. Live HTML, shared HTML, and DOCX use the same narrative interactions, causal strips, qualitative dividend synthesis, and priority contribution panels. See `docs/20260723_climate_fcv_output_redesign_handoff.md`.

**Bounded Climate evidence handoff:** Sonnet still performs exactly two targeted web searches. If it returns search results without the validated JSON bundle, a pure adapter retains only bounded note text, trusted cited source metadata, and a bounded project profile. Haiku receives that packet in a fresh single-turn request; the original prompt, tool-use blocks, encrypted result payloads, and full assistant conversation are not replayed. The ClimateResearchBundle schema and mandatory evidence gate are unchanged. Truncated structuring output is reported separately from missing sources.

```
STAGE 1 — Context & Extraction
├─ Input: appraisal/design-stage project doc (PCN/PID/PAD/AF/Restructuring; instrument type IPF/PforR/DPO/TA/MPA/IPF-DDO; regional ops supported) + optional contextual docs
├─ Automated web research: extract_country_name() + extract_sector_name() → bounded core brief
│  (cached by "country::sector::ccdr=<0|1>"; Climate-active runs add concurrent validated ClimateResearchBundle research)
├─ Three-tier citation: Tier 1 uploaded docs → Tier 2 web research → Tier 3 training knowledge
├─ Output: 2–3 sentence narrative lead (required) then PROSE PARAGRAPHS (not bullets) — for EACH of:
│    Part A (doc extract only) and Part B (contextualized, tiered citations)
│    Bullets restricted to genuinely enumerable items only (named locations, dates, prior actions)
├─ Country-specific fact flagging: Part B tags unverifiable claims (named institutions, legislation,
│    political events, officials) inline with [Verify: ...]; claims from uploaded docs are exempt
├─ IDA FCV Envelope advisory: for Conflict-Affected and Situations of Fragility countries, end-of-
│    Part-B advisory prompts TTL to discuss PRA/RECA/TAA eligibility with regional FCV coordinator
│    (not a determination — coexists with existing eligibility guardrail)
├─ Frontend: renderStage1() parses Part A/B split; renders with styled section badges
│  (blue "From your document only" / green "Wider context & research"); narrative lead
│  styled as tinted callout above bullets
├─ Classifier lines (stripped from display by clean_stage1_output(); kept in history):
│  %%%DOC_TYPE: [PCN/PID/PAD/AF/Restructuring/ISR/Unknown]%%%
│  %%%INSTRUMENT_TYPE: [IPF/PforR/DPO/TA/MPA/IPF-DDO/Unknown]%%%
│  %%%TEMPORAL_CONTEXT_START%%%...%%%TEMPORAL_CONTEXT_END%%% → approval_date, closing_date,
│    safeguards_framework, other_temporal_markers
│  (parsed by frontend; passed to Stage 2/3 requests as instrument_type, temporal_context)
├─ Large docs: >150k chars → LLM condensation; >500k chars → truncation
└─ Prompt constants: FCV_GUIDE, PLAYBOOK_DIAGNOSTICS, FCV_REFRESH_FRAMEWORK, FCS_LIST

STAGE 2 — FCV Assessment
├─ Input: Stage 1 output (conversation history)
├─ Internal engine: 12 OST recs + 25 key questions + 3 key elements (TTL sees themes, not framework)
├─ TTL-facing output (400–500 words): 3–5 dynamic themes → DNH traffic-light → S/R synthesis
│  → Sensitivity + Responsiveness ratings → 3–5 key gaps
├─ Delimiter blocks (stripped from display, parsed to frontend):
│  %%%STAGE2_RATINGS_START/END%%% → {sensitivity_rating, responsiveness_rating}
│  %%%RATING_REASONING_START/END%%% → reasoning block (auditing only)
│  %%%UNDER_HOOD_START/END%%% → 4 sub-blocks:
│    %%%RECS_TABLE_START/END%%%    — 12-rec table with S/R Tag column
│    %%%DNH_CHECKLIST_START/END%%% — 9-principle DNH checklist (principle 9 = SEA/SH)
│    %%%QUESTIONS_MAP_START/END%%% — 25 key questions with findings
│    %%%EVIDENCE_TRAIL_START/END%%% — sources and citation tiers
├─ Under Hood text kept in memory and best-effort localStorage "stage2_under_hood" → used by Go Deeper Tab 1
├─ Rating rubric: Sensitivity = OST recs % addressed → 6-tier (percentage-based, partial credit
│  for Weakly addressed, quality gates apply); Responsiveness = FCV Strategy 2026-2030 pillars count → 6-tier
│  Stage 3 inherits Stage 2 ratings verbatim — no independent re-rating
├─ SEA/SH flag: seash_standalone_flag: TRUE → mandatory SEA/SH priority card in Stage 3
├─ Gender flag: gender_fcv_flag: TRUE (any of 7 trigger conditions) → mandatory gender card
└─ Prompt constants: FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK, FCV_GUIDE, FCS_LIST

STAGE 3 — Recommendations Note (stage-aware)
├─ Input: Stages 1–2 history + doc_type + uploaded_doc_names
├─ Stage-awareness: PCN/PID → PLAYBOOK_PREPARATION; PAD → PLAYBOOK_PREPARATION;
│  AF/Restructuring → PLAYBOOK_IMPLEMENTATION; ISR → PLAYBOOK_IMPLEMENTATION+CLOSING
├─ Temporal guardrail: _build_temporal_guardrail(temporal_ctx, doc_type) — for design-stage
│  docs (PAD/PCN/PID/AF/Restructuring), always returns preparation-phase framing regardless
│  of whether approval date is in the past. Prevents implementation-review hallucination.
├─ Finalized PAD notice: isFinalizedPAD() detects PAD with past approval date → amber
│  retrospective banner injected in output and downloaded report
├─ Instrument routing guardrail: per-doc-type constraints injected into prompt
├─ PAD minimum instrument reference set: SORT, ESS1, SEA/SH AP, SEP/ESS10, ESCP, OM, PPSD, RF
├─ Output: narrative memo + %%%JSON_START%%%...%%%JSON_END%%% block
│  JSON top-level: fcv_rating, fcv_responsiveness_rating, sensitivity_summary,
│    responsiveness_summary, risk_exposure {risks_to, risks_from}, priorities[]
│  Each priority: title, fcv_dimension, tag, refresh_shift, action_timing, risk_level, the_gap,
│    why_it_matters, actions[] (document_element + guidance + suggested_language),
│    who_acts, when, resources, pad_sections, implementation_note,
│    cpf_alignment (null if no CPF uploaded; string linking to CPF outcome if CPF present)
│    action_timing: flag-for-preparation | required-before-appraisal | required-before-board | next-series | supervision — rendered as coloured pill
├─ Watch List for Supervision: final section (replaces "Horizon Considerations"); each item names
│    a specific WBG tracking vehicle (ISR risk flag, MTR agenda item, RRA update, restructuring
│    trigger); items without a named vehicle excluded; framed as risks to monitor, not act on now
├─ SORT guardrail: prompt prohibits prescribing specific SORT ratings; frames risk exposure as
│    "consider whether current rating adequately reflects X"
├─ clean_stage3_output(): strips JSON block, risk narrative, and everything from
│  %%%PRIORITIES_START%%% onwards — all shown as cards from JSON
├─ Citation policy: ONLY cite docs from Stage 1 [From: name]. Never fabricate titles.
└─ Prompt constants: stage-appropriate PLAYBOOK + FCV_REFRESH_FRAMEWORK + CPF_INTEGRATION_GUIDE

FOLLOW-ON (Stage 3 bottom card)
├─ POST /api/run-followon — full history + user message → SSE response appended below card
└─ 4 pre-fill chips: "Draft peer review note" / "Expand top recommendation" /
   "Review my revised text" / "Summarise for brief"

GO DEEPER (per-priority, Stage 3 only — 2 tabs)
├─ Tab 1 (Evidence trail): DEFAULT. No API call — filters in-memory Stage 2 Under Hood data,
│  falling back to localStorage.stage2_under_hood when available; renders instantly
└─ Tab 2 (FCV Playbook): SSE call to /api/run-deeper?tab=playbook_refs
   Cache keys: deeper_{idx}_trail, deeper_{idx}_playbook
```

> **Full prompt schemas, delimiter formats, and parsing function signatures:**
> → `docs/reference/reference_prompt_architecture.md`

---

## 2. Design Decisions & Philosophy

### 2.1 Why 3 Stages?
- Sequential refinement: users pause, review, and correct at each step
- Old Stages 2 (Screening) and 3 (Gaps) were duplicative — merged into a single Assessment stage
- Fewer stages = cleaner TTL workflow without losing quality

### 2.2 Why Part A / Part B Split in Stage 1?
- Transparency: users see what came from their doc vs. external context
- Accuracy accountability: Part A errors = extraction issue; Part B errors = contextual interpretation issue

### 2.3 Why "Go Deeper" (2-tab panel)?
- Tab 1 (Evidence trail): No API call — uses Stage 2 Under the Hood data already in localStorage. Instant.
- Tab 2 (FCV Playbook): Lightweight LLM call for operational tools, WBG teams, policy hooks.
- "Other options" (alternatives) tab removed in v7.2 — rarely used, added cognitive load.
- Core recommendation is self-contained in JSON. Go Deeper is optional depth. Download never needs it.

### 2.4 Specificity Mandate
Recommendations must name geography, mechanism, and entry points — not broad policy suggestions.
- **Bad:** "Service delivery needs to be targeted so it doesn't contribute to grievance"
- **Good:** "In Nzerekore, Kindia, and Kankan — historically excluded — focus service delivery via community health extension workers and cash-for-work entry points"

Enforced via: full 12-rec OST engine in Stage 2; geographic/mechanism requirements in Stage 3 prompt; `_check_specificity()` in `extract_priorities()`.

### 2.5 Session Persistence
All inputs and outputs stored in browser localStorage as JSON. Passed to each stage for full context.
Limitation: browser-specific, not suitable for team collaboration or long-term archival.

---

## 3. Prompt Architecture

### 3.1 Where Prompts Live

```python
# app.py — top-level DEFAULT_PROMPTS dictionary
DEFAULT_PROMPTS = {
    "1": "...",               # Stage 1: Context & Extraction
    "2": "...",               # Stage 2: FCV Assessment
    "3": "...",               # Stage 3: Recommendations Note
    "deeper": "...",          # Legacy alternatives tab (retained for backwards compat)
    "deeper_playbook": "...", # Go Deeper Tab 2: FCV Playbook
    "followon": "..."         # Follow-on post-analysis tasks
}
# Go Deeper Tab 1 (Evidence trail) has NO prompt — frontend-only filter from localStorage
```

**Session overrides:** stored in `prompts.json`, loaded via `load_prompts()`, merged with defaults.
**To override:** Admin modal → stage selector → edit → Save & Close (session-scoped only).
**To persist globally:** edit `DEFAULT_PROMPTS` in `app.py`.
**Note:** `deeper_playbook` is not exposed in the Admin modal — edit directly in `app.py`.

### 3.2 Per-Stage Prompt Summary

| Stage | Input | Key outputs | Prompt constants |
|---|---|---|---|
| 1 | Project doc + optional context | Part A (extract) + Part B (contextualised) + DOC_TYPE line | FCV_GUIDE, PLAYBOOK_DIAGNOSTICS, FCV_REFRESH_FRAMEWORK |
| 2 | Stage 1 history | Thematic narrative + ratings + Under the Hood delimiter blocks | FCV_OPERATIONAL_MANUAL, FCV_REFRESH_FRAMEWORK, FCV_GUIDE |
| 3 | Stages 1–2 history + doc_type | Narrative memo + JSON priorities block | Stage-appropriate PLAYBOOK + FCV_REFRESH_FRAMEWORK |

> **Full per-stage specs, JSON schemas, and delimiter formats:**
> → `docs/reference/reference_prompt_architecture.md`

### 3.3 Key Modification Workflows

**Change a prompt:** Admin modal (session-scoped) or edit `DEFAULT_PROMPTS` in `app.py` (global).

**Change the 6 FCV dimensions:**
1. Edit Stage 2 prompt in `DEFAULT_PROMPTS`
2. Update Stage 3 prompt to reference same dimensions (fcv_dimension must match for Go Deeper trail filtering)

**Change Stage 3 priority fields:**
1. Update JSON schema in `DEFAULT_PROMPTS["3"]`
2. Update `extract_priorities()` in `app.py`
3. Update `showPriority()` in `index.html`
4. Update `downloadReport()` if field should appear in export

**Change the 4 FCV Strategy 2026-2030 pillars:**
1. Edit `FCV_REFRESH_FRAMEWORK` in `background_docs.py`
2. Update Stage 2 and Stage 3 prompts
3. Update `extract_priorities()` shift validation list
4. Update `refresh_shift` badge rendering in `showPriority()`

---

## 4. Frontend Architecture

### 4.1 UI Panels
1. **Onboarding modal** — AI disclaimer + checkbox to suppress on future visits
2. **Session bar** — stage progress + save session button (hides "No active session" on initial load)
3. **Stage progress stepper** — 3-step: Context → Assessment → Recommendations
4. **Input panel (Stages 1–2)** — file upload zone, document list, refine input
5. **Output panel (Stages 1–3)** — LLM output + collapsible sections
6. **Under the Hood panels (Stage 2)** — 4 expandable `<details>`:
   - Panel 1: "How well does the project integrate FCV considerations?" (12 OST recs, S/R Tag column)
   - Panel 2: "Could this project unintentionally cause harm?" (9 DNH principles)
   - Panel 3: "What did we look for — and what was missing?" (25 diagnostic questions)
   - Panel 4: "Where did this analysis come from?" (sources, tiers, contributions)
7. **Ratings sidebar (Stage 2+)** — Sensitivity gauge (blue, shield) + Responsiveness gauge (green, leaf)
8. **Go Deeper panel (Stage 3)** — Per-priority `<details class="go-deeper">` with 2 tab buttons
9. **Prompt modal** — Admin-only: view/edit prompts per session

### 4.2 Styling
- **Colours:** WB palette — wb-blue (#009FDA), wb-navy (#002244), wb-gray-900 (#111827), wb-gray-50 (#F7F8FA), wb-gray-100 (#EEF0F3). RAG: red (#D73027), amber (#FFFFBF), green (#1A9850). Full reference: `memory/reference_wb_design_system.md`
- **Typography:** Open Sans, 14px/400 body, 15px/700 section headings, 10px/600 labels
- **Spacing:** 4px base unit; xs=4, sm=8, md=16, lg=24, xl=32
- **Cards:** border-radius 8px, box-shadow 0 1px 3px rgba(0,0,0,0.08)
- **Font consistency:** `.pc-zone-body` and `.out-body` both 14px — do not let these diverge

### 4.3 Do No Harm Rendering
- **Stage 2 inline:** traffic-light summary, e.g., "Do No Harm: 6 of 9 addressed | 1 partial | 1 gap"
- **Stage 2 Under the Hood Panel 2:** full 9-principle table with evidence (from `%%%DNH_CHECKLIST_START/END%%%`)
- DNH is NOT shown as a standalone checklist in Stage 3

> **Full JS function list, Express mode functions, and removed items:**
> → `docs/reference/reference_frontend_functions.md`

---

## 5. Backend Routes & API

### 5.1 Route Summary

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/run-stage` | Core analysis (Stages 1–3, step-by-step) |
| POST | `/api/run-express` | Express mode (all 3 stages, single SSE) |
| POST | `/api/run-deeper` | Go Deeper tab content |
| POST | `/api/run-followon` | Follow-on post-analysis queries |
| POST | `/api/download-report` | Generate true DOCX binary via python-docx |
| GET | `/api/sector-lenses` | Return enabled sector-lens selector catalogue |
| GET | `/api/default-prompts` | Return current DEFAULT_PROMPTS dict |
| GET | `/` | Main app |
| GET | `/health` | Health check |

### 5.2 Key Constants & Limits

```python
MAX_DOC_CHARS = 500_000        # Hard cap on chars extracted from any single document
STAGE1_MAX_DOC_CHARS = 60_000  # Primary doc truncated to this before Stage 1
CARD_CHARS_2A = 2_800          # Structured secondary package card cap in fcv_distillation.py
CARD_CHARS_2B = 1_200          # Generic secondary package card cap in fcv_distillation.py
CARD_CHARS_CONTEXT = 1_800     # Context card cap in fcv_distillation.py
PROMPTS_FILE = 'prompts.json'
```

### 5.3 Priority Parsing (`extract_priorities()`)

Optional sector provenance is normalized as `lens_ids: string[]` and `lens_relevance: string`. These fields decorate affected priorities only and never define an additional score or recommendation list.

Finds `%%%JSON_START%%%...%%%JSON_END%%%`, parses via `json.loads()`, validates field values, runs `_check_specificity()` and `_check_citations()`, returns unified dict. On malformed JSON: `{error: True, message: ...}` — NOT silent failure.

### 5.4 Stage 2 Parsing

- `extract_stage2_ratings()` → `{sensitivity_rating, responsiveness_rating, rating_reasoning}`
- `extract_under_hood()` → `{recs_table, dnh_checklist, questions_map, evidence_trail}`
- `clean_stage2_output()` — strips all delimiter blocks from display text
- On `extract_under_hood()` failure: `parse_error: true` in SSE event; yellow banner shown; Stage 3 still proceeds

> **Full route specs, SSE event shapes, parsing function signatures:**
> → `docs/reference/reference_backend_routes.md`

---

## 6. Key Implementation Details

### 6.1 SSE Streaming
All stage and Go Deeper requests use Server-Sent Events. Frontend renders text progressively. Session history preserved even if a stream fails mid-way.

Core stage streams use `_stream_stage()`, which runs the Anthropic stream in a background thread, sends keepalive events every 20 seconds during quiet periods, and enforces backend wall-clock limits: Stage 1 = 8 minutes, Stage 2 = 9 minutes, Stage 3 = 9 minutes. If the provider stream stays open without completing, the backend returns a stage error rather than keeping the Render request alive indefinitely. Stage 1 secondary-document distillation also emits preprocessing progress/keepalive events while slower package/context documents are pending, before the model stream opens.

### 6.2 Conversation History
History passed to each stage so the LLM maintains context. Stored in localStorage. Allows session recovery on page reload.

**Compact-label pattern (critical for performance):** Each stage stores a compact user label in `conversation_history` instead of the full prompt with injected background constants. The full prompt is used for the API call but is replaced with a label like `"[Stage 2 — analysis prompt with operational guidance injected]"` before being saved to history. This prevents 80k+ chars of background docs from accumulating in the Stage 3 (and follow-on) API call inputs, which would otherwise cause slow time-to-first-token and risk hitting Render's 10-minute proxy timeout. Stage 1 has always done this; Stages 2 and 3 were updated in v8.2. Each stage re-injects its own fresh background docs — the assistant outputs are what matters for continuity.

### 6.3 Under the Hood → Go Deeper Flow
Stage 2 emits `%%%UNDER_HOOD_START/END%%%` delimiter block. After Stage 2 completes, the frontend keeps this data in memory and attempts to persist it in `localStorage.stage2_under_hood`. Persistence is best-effort: `static/fcv_storage.js` prunes stale large FCV cache entries and returns `false` instead of throwing if the browser quota is still exceeded. Go Deeper Tab 1 (Evidence trail) reads the in-memory value first and falls back to localStorage, so a storage quota failure must not fail Stage 2 or block the current run.

### 6.4 Priority JSON Parsing
`extract_priorities()` uses `json.loads()` on the `%%%JSON_START/END%%%` block. No regex field extraction. Validates all field value sets. Runs specificity check (proper-noun proxy) and citation check (against uploaded doc names + org whitelist).

### 6.5 UX Safeguards
- **S/R tag tooltips:** `renderSRTagBadge()` adds `title` attribute explaining [S]/[R]/[S+R]
- **Specificity warning:** amber badge if `priority.specificity_warning === true`
- **Citation warning:** amber badge if `priority.citation_warnings.length > 0`
- **Under the Hood parse error banner:** yellow banner if `extract_under_hood()` fails; raw text shown as fallback
- **Stage consistency banner:** yellow banner at Stage 3 if Stage 2 was re-run after Stage 3

---

## 7. Common Workflows

### Changing a Prompt
- **Session only:** Admin modal → stage → edit → Save & Close
- **Globally:** Edit `DEFAULT_PROMPTS` in `app.py`

### Adding a Field to Stage 3 Priorities
1. Update JSON schema in `DEFAULT_PROMPTS["3"]`
2. Update `extract_priorities()` in `app.py`
3. Update `showPriority()` in `index.html`
4. Update `downloadReport()` if needed in `index.html`

### Adding a 4th Stage
1. Add key to `DEFAULT_PROMPTS`
2. Add case in `/api/run-stage` stage switch
3. Add stage card + input panel to `index.html`
4. Update stepper to show 1-of-4

### Questions to Ask Before Any Change
1. What problem does this solve? Is it a real user pain point?
2. How does this affect other stages? (Stage 2 changes → Stage 3 prompt? Go Deeper trail filtering?)
3. Does this add complexity without clear benefit?
4. How do I test it? What does a "good" outcome look like?
5. Who is the user — TTL, FCV CC, or both?

---

## 8. Deployment

### Local
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="..."
python3 app.py   # http://localhost:5000
```

### Render.com
- Connect GitHub repo → Render reads `Procfile` + `requirements.txt`
- **Production server:** gunicorn + gevent via the `wsgi:app` entry point (runs `gevent.monkey.patch_all()` before importing the app, so the worker does not block on SSL and trip WORKER TIMEOUT); `--worker-class gevent --workers 1 --timeout 1200` — required for long-running SSE
- **Env vars:** `ANTHROPIC_API_KEY` (required)
- Auto-deploys on push/merge to connected branch

### Render service separation (mandatory)

- **ITS/stable service:** `https://fcv-agent.onrender.com` must remain connected to `main`. ITS colleagues use this service. Never repoint it to a feature branch or use it for branch testing.
- **Branch-testing service:** `https://fcv-agent-1.onrender.com` is the only Render service to use for feature-branch and Climate-FCV testing. Point this service at the branch under test.
- Before any live test, verify the linked branch in the Render service header and verify the deployed build through `/health` where supported. Do not infer the deployed branch from page content alone.
- Keep service-specific build commands separate. Stable `main` uses `pip install -r requirements.txt`; the Climate-FCV testing branch may use `python render_build.py` because that branch carries the companion-bank build helper. Do not copy the testing service's build command onto the stable service.

### Cost-controlled live testing (mandatory)

Use the same verified Climate-FCV architecture in two passes:

1. **Smoke pass first:** set `CLIMATE_VERIFIED_RUN_MODE=smoke` on the branch-testing service. This uses the cheap model profile and tests upload, extraction, country-bank loading, stage completion, schema parsing, validation, rendering, and export. Smoke output is for workflow verification only and must not be treated as an analytical quality benchmark.
2. **Quality pass only after smoke passes:** set `CLIMATE_VERIFIED_RUN_MODE=quality` and run the minimum representative case needed to assess analytical accuracy, relevance, coherence, and TTL utility. Avoid repeated quality reruns while deterministic or integration defects remain.

Never run either pass against the ITS/stable service. If a quality run exposes a deterministic failure, reproduce and fix it through tests or the smoke profile before paying for another quality run.

### GitHub Security & Branch Workflow
- `main` is protected: changes go through pull requests. No approving review is currently required (`required_approving_review_count: 0`), so PRs can be merged programmatically (e.g. `gh pr merge`); open review conversations must still be resolved first, and protection applies to admins.
- Branch protection dismisses stale approvals, requires conversation resolution, applies to admins, and blocks force pushes and branch deletion.
- GitHub Advanced Security features enabled for this public repo: Dependabot vulnerability alerts, Dependabot security updates, secret scanning, and push protection.
- `.github/dependabot.yml` schedules weekly dependency update checks for Python (`requirements.txt`) and GitHub Actions.
- `.github/workflows/codeql.yml` runs CodeQL Python analysis on PRs to `main`, pushes to `main`, and weekly on Monday.
- After the first CodeQL run is stable on `main`, consider adding the CodeQL check as a required status check in branch protection.

---

## 9. Safety & Output Handling

Stage 3 outputs are prepended with an AI disclaimer header (`DO_NO_HARM_HEADER` constant in `app.py`) making clear this is LLM-assisted output for review only, not a substitute for professional FCV analysis.

Citation hallucination guard: Stage 3 prompt explicitly prohibits fabricating document citations. If Stage 3 prompt is modified, ensure this guard is preserved.

---

## 10. Known Limitations

- **localStorage scope:** Browser-specific; no team sharing or long-term archival
- **Rate limiting:** LLM calls are not rate-limited; high-volume use could hit API throttles
- **Large documents:** >500k chars truncated; very large projects may lose nuance. Scanned/image-only PDFs extract to near-zero text — a warning is shown but analysis still runs.
- **DOCX/PPTX:** Modern formats only (.docx, .pptx). Legacy binary formats (.doc, .ppt) are not supported.
- **Research cache:** In-process memory; lost on server restart
- **Mobile:** Desktop-optimized; mobile experience limited

---

## 11. Why These Decisions?

| Decision | Reason |
|---|---|
| Claude Sonnet 4 | Strong FCV reasoning; fast enough for iterative refinement; efficient cost |
| Flask (not React) | Lightweight; direct LLM integration; vanilla JS sufficient; easy Render deploy |
| SSE streaming | Real-time feedback; no polling overhead; better UX |
| localStorage sessions | Quick to implement; no database needed; works offline |
| Delimiter + JSON parsing | Reliable extraction; allows LLM to generate prose around structured data; easy to extend |
| 3 stages (not 4 or 1) | Sequential refinement; old Stages 2+3 were duplicative; merged for cleaner workflow |

---

## 12. Testing Checklist

**Per run, check:**
- [ ] Stage 1 Part A extracts from doc only; Part B uses correct citation tiers
- [ ] Stage 2 Assessment is thematic and uses FCV Strategy 2026-2030 framing (not old pillars)
- [ ] Stage 2 Under the Hood panels parse correctly (12-rec table, DNH, questions, evidence)
- [ ] Stage 2 gauges animate; ratings are plausible
- [ ] Stage 3 priorities include geographic callouts and `refresh_shift` badges
- [ ] Stage 3 lifecycle framing matches doc type (PCN vs PAD framing)
- [ ] Go Deeper Trail tab renders instantly from Stage 2 data
- [ ] Go Deeper Playbook tab loads relevant guidance
- [ ] Follow-on card works with at least 2 pre-fill chips

**Prompt quality checks:**
- Are recommendations specific (geography, mechanism, entry points)?
- Are they evidence-based (grounded in uploaded docs)?
- Does the Stage 2 Assessment correctly apply 4 FCV Strategy 2026-2030 pillars (not old pillars)?

---

## 13. Debugging

| Symptom | Check |
|---|---|
| Stage 1 hangs on large PDF | LLM summarizing (expected, 30–60s). Check `MAX_DOC_CHARS`. |
| DOCX/PPTX shows "could not extract" | Check python-docx/python-pptx are installed (`pip install -r requirements.txt`). Only .docx/.pptx supported — not .doc/.ppt. |
| Scanned PDF shows blank Stage 1 | Expected — extraction warning banner shown. User should upload a text-based version. |
| Stage 2 ratings seem off | Review via Admin modal; refine Stage 2 prompt and re-run |
| Under the Hood panels missing | Look for `%%%UNDER_HOOD_START%%%` in Stage 2 output; check for yellow parse error banner |
| Go Deeper Trail shows nothing | Check `localStorage.stage2_under_hood` has content; verify `priority.fcv_dimension` matches dimension in recs table |
| Stage 1 fails around 9 minutes with timeout/server message | Check frontend timeout handling first: custom abort reasons should show the stage timeout, not `Could not reach the server`. In Render logs, inspect `Stage 1 preprocessing start` and `Stage 1 extraction complete` timing, then search for `SIGKILL` / out-of-memory if the stream dies before logs complete. |
| Stage 3 loading runs indefinitely | Check for backend timeout errors from `_stream_stage()` and confirm `STAGE_STREAM_TIMEOUTS[3]` is active. If it repeats, inspect Stage 3 prompt size and Stage 1/2 history payloads. |
| Stage 3 missing `refresh_shift` | Check `DEFAULT_PROMPTS["3"]` includes `refresh_shift` in JSON schema |

**Debug steps:**
1. Browser console (F12) for JS errors
2. Flask server logs (Render dashboard) for backend errors
3. Admin modal to inspect exact prompt used for a stage

---

## 15. File Structure

```
FCV-AGENT/
├── app.py                        # Flask backend + DEFAULT_PROMPTS + all routes
├── index.html                    # Single-page frontend (~4000+ lines)
├── background_docs.py            # Knowledge base constants (10 background doc strings)
├── prompts.json                  # Session-specific prompt overrides (empty by default)
├── requirements.txt
├── Procfile
├── .github/
│   ├── dependabot.yml            # Weekly dependency update configuration
│   └── workflows/
│       └── codeql.yml            # CodeQL Python security scanning
├── README.md                     # Deployment guide for IT
├── CLAUDE.md                     # This file — developer reference
├── docs/
│   ├── reference/
│   │   ├── reference_prompt_architecture.md   # Detailed prompt specs + delimiter schemas
│   │   ├── reference_frontend_functions.md    # JS function list + Express mode
│   │   └── reference_backend_routes.md        # Routes + SSE shapes + parsing signatures
│   └── fcv-agent-knowledge-architecture.html  # Shareable knowledge pipeline diagram
└── tests/
    ├── __init__.py
    └── test_extract_priorities.py
```

Local-only (gitignored — see `.gitignore` and the Repository Structure section above):
```
app_feedback/      # Internal feedback documents
docs/superpowers/  # Dev plans and specs
.claude/           # Local Claude Code config
.superpowers/      # Brainstorming session artifacts
```

---

**Last updated:** 2026-08-05
**Current version:** FCV Project Screener v9.27
**Claude model:** `claude-sonnet-4-6`
**Stack:** Flask 3.0.3 + vanilla JS + Anthropic SDK + gunicorn/gevent on Render
