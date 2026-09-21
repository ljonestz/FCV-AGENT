# Climate-FCV Dedicated Module Output Redesign

**Date:** 24 July 2026
**Status:** Design approved in brainstorming; ready for implementation planning
**Branch (worktree):** `codex/climate-fcv-output-redesign`
**Supersedes:** the integrated dual-use output design (`docs/superpowers/specs/2026-07-23-climate-fcv-dual-use-output-redesign-design.md`) for the Climate lens specifically. Core (non-module) behaviour is unchanged.

## 1. Purpose and headline decision

Selecting the Climate lens should produce a **dedicated climate-FCV assessment**, not the general FCV assessment with climate findings added on. When a user clicks the Climate module, Stages 1 to 3 reorient around climate-FCV: the research, the internal Stage 2 spine, the ratings, the narrative, and the priorities are all predominantly about the intersection of climate and FCV.

This is a **deliberate reversal** of the 23 July fixed decision, which kept the Climate lens as an integrated dual-use overlay and placed a Climate-primary mode explicitly out of scope. The reversal is intentional: a dedicated output is more coherent and more useful than a general FCV report carrying a climate section.

The general FCV engine is retained as an **internal input source** (Do No Harm logic feeds CQ2; conflict-driver analysis feeds CQ1 and CQ3; vulnerable-group analysis feeds CQ4), but it no longer defines the visible output.

## 2. Fixed decisions

- Climate remains manually selected and is never auto-suggested.
- Core-only (non-module) runs are untouched: research depth, four to five substantive priorities, and the lightweight conditional climate check all remain as they are.
- An active Climate lens supersedes the lightweight conditional check.
- The output is **intersection-led**: every finding must have a genuine climate *and* FCV element. Pure climate-engineering points with no FCV dimension, and pure FCV points with no climate dimension, are not the focus.
- Adaptation and resilience are primary. Deep mitigation or transition analysis requires a clear, material project pathway.
- No more than five substantive priorities. Composition is evidence-led, not quota-driven.
- Trusted-source grounding: World Bank CCDR first where relevant, then other authoritative country-specific climate-conflict sources via the research pass. A generic claim is worse than an explicit evidence gap and must be suppressed.
- No separate numeric climate score, and no separate climate priority list.

## 3. The six core questions (Stage 2 internal spine)

These become the internal analytical spine of Stage 2 when the Climate lens is active. They are a **pool**, not a checklist to print in full: the visible reflections surface the three to five most material, with a brief "less central here" note for the rest. Selection is calibrated by the country's existing FCV category.

- **CQ1 Climate-FCV interaction and delivery.** How do climate hazards and FCV dynamics interact in this specific context, and how could that affect delivery and results? Which hazards are material to the project's actual locations and horizons; how do they intersect with local drivers (resource competition, mobility, grievance, state presence); what does that mean for access, sequencing, supervision, disbursement.
- **CQ2 Maladaptation, Do No Harm and lock-in.** Could the project's climate action inadvertently worsen fragility, conflict or exclusion, now or as conditions shift? Winners and losers in how climate benefits are allocated; entrenching grievances, inequalities or power imbalances, or reading as externally imposed; risk transfer onto another place or group; and, where relevant, whether design choices lock in siting, settlement or resource-use patterns that longer-term climate shifts could later turn maladaptive or conflict-aggravating.
- **CQ3 Peace and social dividends and root causes.** Does the project actively reduce FCV drivers and build cohesion, or is that opportunity left unclaimed? Does it tackle an underlying driver; are there credible, project-attached cohesion opportunities; are these supported by design or only potential.
- **CQ4 Vulnerable regions, groups and inclusion.** Does the project reach and reflect the most climate-exposed and FCV-affected people and places? Historically excluded regions and groups explicitly targeted; differentiated needs (gender, displaced, pastoralist, youth) built into design; participation genuine and locally owned, not tokenistic.
- **CQ5 Institutions, governance and HDP coordination.** Does the project work with and strengthen the institutions and coordination needed to deliver in this FCV setting? Building rather than bypassing local and national capacity and legitimacy; coordination across development, DRM, humanitarian and peace actors where footprints overlap; delivery arrangements realistic given access and state presence.
- **CQ6 Adaptive design, monitoring and uncertainty.** Is the project designed to sense and respond to evolving climate and FCV conditions? Monitoring the broader FCV context, not only outputs, with feedback and accountability; flexibility and scenario thinking for worsening conditions; early detection of drift in its own assumptions (hydrology, security, allocation).

### 3.1 Cross-cutting analytical rules

- **Intersection-only**, as in section 2.
- **Time horizons are an available lens, not a mandatory component.** Surface them where they genuinely matter: current and near-term extremes; project-lifetime shifting patterns (gradual warming, changing precipitation); and asset or system-lifetime slow-onset change and lock-ins. Emphasise only where relevant; do not force a horizon read into every finding.
- **Grounded sourcing**, as in section 2.

### 3.2 Source pool

The core questions and the impact analysis draw on: *Maximizing the Peace and Social Dividends of Climate Action*; the *FCV-Sensitive Climate Action Framework*; the CCDR FCV-sensitivity approach note; the *Defueling Conflict* natural-resource-management series; the adelphi climate-security guidance; and the conflict-sensitive adaptation literature. On-screen text attributes these generically ("established climate and FCV frameworks and evidence") rather than by formal name, except in the source signpost (section 4.1).

## 4. Output architecture

Ordering, live HTML, shared HTML and DOCX are identical. The narrative block runs first, then the standard priority panels.

Visual treatment stays within the existing WB design system (8px radius, subtle shadow, tinted background, coloured left-accent border). RAG red, amber and green stay reserved for their existing meanings; the two directional interaction boxes use non-RAG accents so they are not read as good or bad.

1. **Orientation card: "How relevant is climate to this project?"** (renames "materiality"). High, Medium or Low, with a concise project-specific rationale, the principal locations, systems, groups or assets that make the pathway material, and a brief evidence limitation where relevant. Blue-family card.
   - **Source signpost** in this card: *Maximizing the Peace and Social Dividends of Climate Action*, the *FCV-Sensitive Climate Action Framework*, and the *Defueling Conflict* series.
2. **Orientation card: "How well does the project integrate climate and FCV?"** A single qualitative gauge replacing the two sensitivity and responsiveness gauges. It reflects how well the project recognises and responds to the material climate-FCV interactions (blending awareness and active response). Derived from the core-question reflections. Carries the standard caveat: this is a subjective judgement by the AI tool and is not an official WBG assessment. Blue-family card.
3. **Executive summary.** Integrated, climate-FCV-led narrative: opening assessment, key strength, key gap. Plain prose, no box, so the boxes below stand out.
4. **Box A: "How climate and FCV dynamics could affect this project."** Project- and location-specific causal prose; named components, activities, institutions, assets, sites or groups; time horizons woven in only where they matter; a soft "current design response / remaining gap" close. Tinted callout, muted slate-blue accent. No causal-strip diagram.
5. **Box B: "How this project could affect climate and FCV dynamics."** Positive and adverse pathways as bold prose lead-ins ("Positive pathway" / "Risk or maladaptation pathway"), kept separate from Box A. Tinted callout, muted teal accent.
6. **Reflections on core climate and FCV considerations.** Opens with an adaptable sentence that signposts the source pool and the project type, then gives the three to five most material core-question reflections. Each carries a soft, desaturated status chip (for example "well recognised", "partial gap", "strong") and the block ends with a "less central here" line for the non-material questions. Clean list, not sub-headed cards.
7. **Climate, peace and social dividends.** Approachable prose, not sub-headed. Read against *Maximizing the Peace and Social Dividends of Climate Action*: distinguish dividends from *what the project funds* versus *how it is delivered*, and touch the report's pathways (for example cohesion, trust and collaboration mechanisms, jobs and livelihoods, institutional capacity) as soft encouragement rather than a required checklist. Names supported versus potential contributions, the main trade-off or maladaptation watch, and which numbered priorities carry the opportunities forward. Soft-green "opportunity" callout.
8. **Wider FCV context.** A short prose subsection, not a priority. Flags any material FCV issue that has no real climate angle so a TTL using the Climate module is not blindsided. It is surfaced, not developed into priorities. This closes the narrative block, before the priority panels. Muted grey callout.

Then, as their own standalone panels exactly as in the default FCV screening:

9. **Priorities.** Up to five climate-FCV priorities, rendered in the standard pop-up priority panels (same design as core runs). Each carries the climate-contribution panel: where a material pathway exists, name it and explain the project-specific mechanism and how the priority strengthens it; where none exists, state that no material dividend pathway was identified and why the priority was retained on core FCV grounds.

## 5. Pipeline changes

- **Stage 1.** Climate-FCV-led shared research plan plus the dedicated bounded climate research pass, reusing `ClimateResearchBundle` with one narrower retry. Extract locations, components, long-lived assets, livelihood and natural-resource systems, and affected or excluded groups. CCDR is a targeted first check, not a quota.
- **Stage 2.** The internal engine is reorganised around the six core questions (using the FCV analytical tools as inputs). It emits both directional interaction pathways with stable IDs, horizons where relevant, evidence and confidence, and produces the integration-gauge judgement and the reflections. Both directions retain project, place, group, system anchors and causal steps; generic pathways are discarded.
- **Stage 3.** Up to five climate-FCV priorities, each with validated `climate_links`, within the existing 900-token lens ceiling. Plus the wider-FCV-context note.

## 6. Reuse versus new

**Reused from the current branch:** `ClimateResearchBundle` and the bounded retry; both directional pathways with stable IDs; the three time horizons; structured research-claim distillation; `climate_links` per priority with deterministic provenance from recognised IDs; the materiality panel; safe fallback; safe telemetry (structural counts only); live, shared HTML and DOCX parity.

**New or changed:** dedicated-mode routing when the Climate lens is active; the six core questions as the Stage 2 spine; the reflections block; the single integration gauge replacing the two S and R gauges; conversion of the causal strips to prose boxes with the WB panel styling; the retitled orientation cards; the source signpost; the CQ2 lock-in and time-scale element; the intersection-only rule; the wider-FCV-context subsection; the dividends framing against the *Maximizing* report.

## 7. Safe fallback and telemetry

Retained from the current design. If the climate diagnostic is invalid after bounded recovery: preserve normal core FCV behaviour, generate no unvalidated climate-specific readout or dividend or priority or materiality claim, explain the evidence or diagnostic limitation, and keep the active lens from re-triggering the lightweight check. Telemetry records structural counts only and never logs project prose, evidence text, prompts, credentials or untrusted keys.

## 8. Parity contract

The dedicated-mode routing, the single integration gauge, the reflections block, the retitled cards and any priority-JSON additions are shared contract surfaces. Record the contract change in the private build-parity log so the ITS FastAPI build can mirror it.

## 9. Out of scope

- Auto-suggesting or auto-activating the Climate lens.
- Any change to core-only runs.
- A separate numeric climate score or a separate climate priority list.
- Decorative graphics beyond the tinted prose boxes, orientation cards, soft status chips and horizon references.
- Deep mitigation analysis without a material project pathway.

## 10. Success criteria

A Climate-active output:

- reads as a dedicated climate-FCV assessment, not a general FCV report with a climate section;
- keeps every finding at the climate-FCV intersection;
- uses country, subnational and project-specific evidence, grounded in trusted sources;
- answers the material core questions in the reflections block, flexibly and without a mechanical checklist;
- gives two nuanced causal directions in prose boxes rather than diagrams or generic lists;
- surfaces time horizons only where they genuinely matter;
- frames dividends against the *Maximizing* report in approachable prose;
- flags material non-climate FCV issues in the wider-FCV-context note without developing them;
- renders priorities in the standard panels with a climate-contribution panel each;
- completes reliably within bounded production time and context limits, and degrades safely when research or diagnostics fail.

## 12. OPCS compliance guardrails (WBG LLM review, 2026-07-24)

An internal WBG LLM with access to the OPCS policy corpus reviewed this design and plan for consistency with current OPCS/ESF policy. Claude Code must NOT read the OPCS corpus; these guardrails are the authoritative summary to implement. Scope decision: adopt the clearly-right items in full, plus a lightweight ("hybrid") structured layer (`policy_status` + `specialist_referral`); do not build the full four-way `finding_type` taxonomy.

### 12.1 Policy boundary (adopt)
A `POLICY BOUNDARY` block is injected into the Stage 2 and Stage 3 climate prompts, shown as a short UI notice, and included in exports. The module is an advisory FCV screening and design-support tool. It does NOT: determine ESF/ESS compliance; assign, confirm or revise an Environmental and Social Risk Classification; determine which ESSs apply; replace the E&S assessment, ESRS, ESCP, SEP or other required instruments; give authoritative OPCS-policy interpretation; or substitute for the Task Team's accredited E&S specialist, ES Practice Manager, RSA, CESSO, OESRC, Legal, or UN engagement team. Where a finding overlaps ESF requirements, it is framed as an issue to verify against the project's E&S documentation and responsible specialist.

### 12.2 Integration readout reframe (adopt — revises §4.2)
The gauge is titled/captioned "Indicative Climate-FCV Integration Readout" with the caveat: "This AI-assisted readout supports expert review. It is not an official WBG rating, policy determination, ESF assessment, Paris Alignment assessment, or substitute for Task Team and specialist judgment." The internal `integration_level` enum becomes `well_integrated | partly_integrated | weakly_integrated | insufficient_evidence`. Absence of a valid value defaults to `insufficient_evidence` — NOT to a middling value (the prior "material→moderate" default was analytically unsafe).

### 12.3 Keep sensitivity and responsiveness separate internally (adopt)
Even though one combined gauge is shown, the diagnostic retains separate `sensitivity_evidence` and `responsiveness_evidence` arrays. An operation may be FCV-sensitive without being responsive; the combined readout must not penalise a project for not pursuing dividends when it manages FCV risk well, nor reward dividend talk over basic Do No Harm.

### 12.4 Hybrid structured compliance fields (adopt — lightweight)
Each Stage 3 priority (and, where useful, each reflection) carries:
- `policy_status`: `mandatory_reference | document_commitment | advisory | not_determined` (default `not_determined`). Distinguishes a mandatory ESF/OPCS reference, an existing project-document commitment (e.g. an ESCP/SEP action), FCV/climate good practice, and undetermined.
- `specialist_referral`: `null`, or `{ "required": bool, "route": "Task Team E&S specialist | RSA | ESF Help Desk | OESRC | Legal | UN engagement team", "reason": string }`. Phrased as "consider referral" unless policy clearly makes escalation mandatory. Triggers include: uncertainty on applicable ESS; possible conflict with an ESCP/other commitment; security-personnel issues; SEA/SH; disproportionate effects on disadvantaged/vulnerable people; significant land or natural-resource access restrictions; ESRC uncertainty; unfamiliar UN-agency implementation arrangements; apparent need for policy interpretation.
These are surfaced in the export and understated in the UI (not prominent technical labels). The full `finding_type`/`verification_route` taxonomy is deliberately out of scope for now.

### 12.5 Instrument and framework awareness (adapt — partly exists)
The underlying app already classifies `INSTRUMENT_TYPE` (IPF/PforR/DPO/MPA/AF/Restructuring) and scrubs ESF vocabulary for PforR/DPO. The climate prompts add an explicit guardrail: do not apply IPF/ESF terminology (project components, ESCP, ESS, PAD sections) to PforR or DPF as if universally applicable; if the instrument or applicable framework (ESF vs borrower systems vs predecessor Safeguards) cannot be established, state the limitation and avoid compliance-style conclusions.

### 12.6 CQ2 / CQ4 / CQ5 refinements (adopt — prompt wording)
- CQ2: distinguish project-caused risks, contextual delivery risks, exclusion/conflict effects, longer-term climate risks, and risks ALREADY managed in the ESCP/SEP/ESMF/ESMP; do not repackage an already-managed E&S risk as a new unaddressed FCV deficit.
- CQ4: identify vulnerability from project + context, NOT a fixed demographic checklist; examine disproportionate impacts, benefit-access barriers, information/consultation/grievance barriers, natural-resource dependence, displacement/mobility, intersecting disadvantage, and whether differentiated measures are documented.
- CQ5: assess the institutional trade-off contextually (state capacity vs legitimacy vs capture/exclusion vs access/security vs third-party/UN delivery vs sustainability vs accountability); "working through" vs "bypassing" government is not inherently good or bad.

### 12.7 Dividends never implied as requirements (adopt — strengthen §4 dividends)
Never describe an unclaimed peace/social dividend as policy non-compliance unless there is an explicit applicable commitment. Distinguish documented contribution / credible-but-unsupported opportunity / speculative / no material pathway. Do not recommend adding cohesion, jobs, trust or institutional objectives unless a credible project-attached mechanism exists and the proposal stays consistent with the PDO, ToC, instrument, mandate and capacity.

### 12.8 Cross-document consistency (adopt — prompt guardrail)
Compare findings against available authoritative project documents (PAD/PCN, ESRS, ESCP, SEP, ESMF/ESMP, SORT, results framework, Paris Alignment where present, CCDR). Purpose is to avoid contradiction, not to redo those assessments. If the PAD states an issue is mitigated via the SEP/ESCP, do not call it wholly unaddressed; state what the package documents, assess whether the response is specific enough for the climate-FCV pathway, and flag remaining uncertainty.

### 12.9 Two source layers (adopt — framing rule)
Layer 1 = current authoritative operational sources (current PPF policy/directive/procedure, ESF and applicable ESSs, current OPCS guidance, project-specific disclosed instruments). Layer 2 = analytical/good-practice sources (Maximizing the Peace and Social Dividends of Climate Action; FCV-Sensitive Climate Action Framework; Defueling Conflict; CCDR FCV-sensitivity materials). The source signpost names Layer 2; output must never present a Layer-2 recommendation as an OPCS requirement. Do not hard-code archived/retired OPCS PDFs as current authority.

## 11. Testing outline

Extends the current suite. Cover: unchanged core-only behaviour; dedicated-mode routing on lens selection; the six core questions driving Stage 2; reflections selection and the "less central here" path; the single integration gauge; both prose interaction boxes with intersection-only content; the CQ2 lock-in and time-scale path (present when relevant, absent when not); grounded-source versus evidence-gap handling; the wider-FCV-context note; priority panels with climate-contribution panels; CCDR-present and CCDR-absent cases; climate research timeout, retry and safe failure; and parity across live page, shared HTML and DOCX. Retain the synthetic end-to-end regression.
