# Verified Climate-FCV Assessment Pipeline Design

**Date:** 2026-08-01  
**Branch:** `feat/climate-country-bank`  
**Status:** Approved design  
**Scope:** Dedicated Climate-FCV design-review route

## 1. Objective

Rebuild the Climate-FCV module around a controlled chain from project-document facts to analytical pathways and operational recommendations. The module must remain fully automatic while producing advice that is more accurate, relevant, proportionate, and useful to a World Bank task team than a capable one-shot LLM review.

The governing principle is:

> The system may only be precise where its evidence is precise. Where project facts, routing, timing, or scope are not verified, it must become more conditional rather than more confident.

The redesign preserves the current module's strongest features: two-directional Climate-FCV analysis, project-specific pathways, country evidence, ranked operational advice, responsibility and timing, optional drafting language, and FCV sensitivity/responsiveness framing. It replaces the current monolithic Stage 2 diagnostic and unverified Stage 3 specificity with linked, typed products and automated validation.

## 2. Success criteria

The redesigned module succeeds when:

- every consequential project claim resolves to an exact primary-document excerpt;
- study and instrument existence, scope, timing, status, and routing capability are verified separately;
- existing project responses are represented before residual gaps are identified;
- country evidence sharpens contextual pathways without becoming project fact;
- zero to three headline priorities pass explicit admission and ranking rules;
- drafting language appears only where operational routing is verified;
- unsupported dates, statistics, thresholds, and authority claims are rejected or softened;
- the executive readout is concise, balanced, and internally consistent;
- web, HTML, and DOCX outputs reproduce complete structured fields without UI leakage or truncation;
- the full workflow completes automatically without a human-review dependency; and
- regression tests prevent recurrence of the verified South Sudan errors.

## 3. Non-goals

- Do not add a human review, approval, assignment, or audit workflow.
- Do not turn the Climate-FCV module into a general project-quality or OPCS-compliance reviewer.
- Do not treat analytical frameworks or country evidence as formal policy authority.
- Do not require exactly three recommendations.
- Do not create separate climate and FCV recommendation lists.
- Do not duplicate or redesign the country evidence bank while its parallel workstream is active.
- Do not increase confidence merely to populate a required output field.
- Do not preserve the current freely generated overall integration rating.

## 4. Architecture overview

The visible three-stage user journey remains Context, Assessment, and Recommendations. Internally, the Climate route uses bounded products:

1. Structured source blocks and atomic project facts.
2. Existing project responses.
3. Climate-FCV pathways.
4. Residual gaps.
5. Multidimensional judgment.
6. Recommendation candidates, admission results, and compiled priorities.
7. Review-readiness flags.
8. Automated validation and targeted semantic review.

The authoritative source is the verified project-fact registry, not Stage 2 prose. Downstream stages may reject an upstream assertion that is unsupported by the registry. They may not silently rewrite primary facts.

## 5. Phase 1: Verified extraction

### 5.1 Structured source blocks

Document extraction must preserve enough structure for stable provenance. Each extracted block contains:

```json
{
  "block_id": "DOC1-B0085",
  "document_id": "DOC1",
  "order": 85,
  "heading_path": ["Project Description", "Sub-component 1.4"],
  "block_type": "paragraph",
  "table_location": null,
  "text": "A feasibility study will be completed in Year 1 of implementation."
}
```

DOCX locators use document ID, heading path where available, body-order index, and table coordinates. PDF blocks retain page numbers where extraction supports them. The existing document character limits remain unchanged in the first implementation.

### 5.2 Atomic project facts

The extractor returns bounded, decision-relevant claims rather than a general summary. The default target is no more than 60 claims and the hard maximum is 100. Claims cover components, activities, locations, groups, institutions, studies, operational instruments, scope, timing, commitments, existing mitigation, results indicators, decision gates, responsibilities, material figures, placeholders, and contradictions.

```json
{
  "claim_id": "PF-017",
  "claim_type": "study_timing",
  "subject": "Sub-component 1.4 school-feeding feasibility study",
  "predicate": "scheduled_for",
  "object": "Year 1 of implementation",
  "epistemic_status": "explicit",
  "source_block_ids": ["DOC1-B0085"],
  "supporting_excerpt": "A feasibility study will be completed in Year 1 of implementation.",
  "confidence": "high"
}
```

Existence does not prove scope. Scope does not prove timing. Timing does not prove that a vehicle can establish a proposed requirement. These are separate claims.

Allowed epistemic states are:

- `explicit`
- `confirmed_absence`
- `not_found`
- `not_yet_specified`
- `contradictory`
- `not_applicable`

Inference cannot enter the project-fact registry. `not_found` never becomes confirmed absence. A missing claim does not prove that the document lacks the information.

### 5.3 Truth-layer verification

Code verifies that excerpts resolve exactly to cited source blocks, IDs and enums are valid, and project facts use eligible project sources. A bounded semantic check verifies that the quoted text supports the asserted relationship and has not broadened scope or omitted a material qualifier.

If downstream analysis needs a fact absent from the registry, it issues a targeted request against preserved source blocks. A newly found fact enters through the same excerpt-resolution and semantic checks before it can support analysis or routing.

## 6. Phase 2: Bounded analysis

### 6.1 Existing-response register

Every material pathway is matched to what the project already does. Each response references project claims and records `substantial`, `partial`, `not_yet_specified`, `contradictory`, or `not_found` coverage. The analysis must represent all relevant documented measures before identifying a gap.

### 6.2 Climate-FCV pathway register

Each pathway contains:

- stable pathway ID;
- direction: `climate_fcv_on_project` or `project_on_climate_fcv`;
- pressure and mediated mechanism;
- verified project anchors;
- affected groups, geography, systems, assets, and time horizon;
- positive and adverse potential effects where relevant;
- project and contextual evidence IDs;
- confidence and uncertainty.

A pathway must reference at least one verified project fact and describe an actual Climate-FCV mechanism. Generic co-occurrence is suppressed. The hard maximum is three pathways per direction.

### 6.3 Residual-gap register

A residual gap exists only after comparing a pathway with documented existing responses. Gap types are:

- `confirmed_omission`
- `partial_response`
- `not_yet_specified`
- `contradictory`
- `evidence_gap`

Each gap records project basis, existing responses considered, materiality, decision window, evidence sufficiency, and remaining uncertainty. The hard maximum is eight residual gaps. Concept-stage silence should normally be described as `not_yet_specified`, not absence.

### 6.4 Evidence entitlements

Sources have typed permissions:

- **Primary project evidence** may establish project facts, commitments, timing, existing mitigation, indicators, responsibilities, and operational routing.
- **Applicable project-package evidence** may establish project claims only when operation, version, geography, stage, and financed scope are verified as applicable.
- **Country and sector evidence** may establish contextual plausibility, exposure, vulnerability, institutional or distributional mechanisms, and reasons for deeper testing. It may not establish a project-site fact by itself.
- **Guidance and comparative evidence** may support analytical framing and good-practice options. It may not independently prove a project gap.
- **Analytical inference** may support a conditional pathway, verification question, or condition-triggered enhanced action. It may not establish project fact, formal authority, or a high-confidence site-specific conclusion.

The application validates these permissions. Country-bank records enter the pathway register only and retain geography, evidence status, time horizon, source, confidence, and uncertainty.

### 6.5 Multidimensional judgment

The module reports four separate judgments:

- **Climate-FCV relevance:** `high | medium | low | unclear`
- **FCV sensitivity:** `strong | moderate | limited | unclear`
- **FCV responsiveness:** `strong | emerging | limited | not_material | unclear`
- **Operationalization:** `embedded | partial | early | not_evidenced | unclear`

Operationalization is delivery maturity across sensitivity and responsiveness, not a third substantive FCV category. The interface uses a deterministic summary such as `High relevance · Moderate sensitivity · Emerging responsiveness · Partial operationalization`. No free overall rating is generated.

## 7. Phase 3: Recommendation admission and compilation

### 7.1 Hard admission gates

A candidate becomes a headline priority only when it passes:

1. verified project connection;
2. residuality after existing responses;
3. material consequence;
4. realistic task-team decision lever;
5. action before the relevant decision; and
6. distinctiveness from other candidates.

Strong or moderate evidence may support a direct design recommendation. Limited evidence supports only verification, screening, or options analysis.

### 7.2 Internal ranking

The model assigns bounded rubric values with evidence IDs; code computes the score:

- material consequence: 1-3;
- residual-gap strength: 0-2;
- decision leverage and urgency: 0-2;
- evidence sufficiency: 0-2;
- feasibility and proportionality: 0-1.

Admission requires medium-or-higher material consequence and at least 6/10. Ties are resolved by earlier or more irreversible decisions, greater harm/delivery prevention, then stronger evidence. The score is internal. The output shows rank only and removes the current `High priority` badge.

The compiler returns zero to three priorities and never manufactures a replacement for a rejected item.

### 7.3 Recommendation contract

Each admitted recommendation contains:

- stable ID and rank;
- linked pathway, response, gap, and project-claim IDs;
- decision needed;
- project evidence, existing response, and residual gap;
- why it matters;
- minimum action, scope, and timing;
- optional enhanced action with a required activation condition;
- function-first routing and routing status;
- responsibility by function, with assignment status;
- completion evidence;
- confidence, limitations, and implementation caution;
- optional drafting language.

Core fields needed for admission are mandatory. Operational home, detailed responsibility, and drafting language may be unresolved with an explicit reason.

### 7.4 Function-first routing

The compiler first defines the required function, such as climate-informed siting, service continuity, conflict-sensitive access governance, adaptive monitoring, transparent benefit sharing, or inclusive representation. It then tests candidate operational homes.

Routing statuses are:

- `verified_existing`
- `verified_with_scope_change`
- `new_vehicle_may_be_needed`
- `team_to_confirm`
- `not_applicable`

Drafting language is allowed only for `verified_existing` and `verified_with_scope_change`. Where routing is unresolved, the recommendation describes the function and asks the team to determine the correct vehicle.

Authority basis is limited to `project_commitment | policy | directive | procedure | guidance | reviewer_judgment`. Mandatory language requires verified formal authority or an explicit project commitment. Analytical frameworks remain advisory evidence.

### 7.5 Minimum and enhanced actions

The minimum action is the smallest credible, proportionate response supported across the stated scope. An enhanced action is optional and must specify the condition that activates it, the bounded additional action, and the affected locations, groups, or risk characteristics.

An enhanced action without an activation condition is invalid. The compiler must not impose full political-economy analysis, quantitative modelling, detailed continuity protocols, or other high-burden measures universally.

### 7.6 Recommendation safety

Every candidate is tested for risks including formalized exclusion, implementation paralysis, security exposure, grievance suppression, excessive monitoring burden, enforcement of mediation problems, and unsupported authority. A concise implementation caution is retained in the admitted recommendation.

## 8. Review-readiness flags

The module may return zero to four non-scoring flags under `Review readiness flags for task-team verification`.

A flag must be directly visible in project documentation, materially affect verification or operationalization of the Climate-FCV assessment, and be expressed as a verification issue rather than a compliance determination.

Allowed categories are incomplete or referenced-but-missing climate screening; material financing inconsistency; undefined or overlapping result indicator; contradictory risk, timing, geography, or institutional statement; material unresolved placeholder; unverified operational or processing route; and a recommended function with no identifiable operational home.

Each flag contains only the flag, why it matters, document basis, and suggested verification. General proofreading and unverified processing requirements are excluded. Flags do not affect the four judgments unless the underlying issue independently appears in residual analysis.

## 9. Phase 4: Automated validation

### 9.1 Deterministic checks

Code validates:

- source, block, claim, pathway, response, gap, and recommendation references;
- exact excerpts and evidence entitlements;
- allowed values and bounds;
- recommendation admission and ranking;
- routing support and authority language;
- zero to three priorities and zero to four readiness flags;
- unique ranks and IDs;
- enhanced-action activation conditions;
- suppression of drafting language for unresolved routing;
- traceability of numbers, dates, and thresholds;
- absence of placeholders; and
- full structured-field parity across web, HTML, and DOCX outputs.

Exports are generated directly from structured data, not browser DOM text. Round-trip checks detect missing or clipped fields, duplicate sections, navigation leakage, inaccessible evidence codes, malformed links, and truncation.

### 9.2 Semantic checks

A bounded automated reviewer receives relevant source blocks and typed products. It checks claim relationships, existing mitigation, residual logic, evidence overreach, judgment coherence, recommendation proportionality, unintended consequences, and semantic duplication.

The reviewer returns `pass | revise | block` with affected IDs and reasons. It may revise derived analysis but cannot silently alter primary facts.

One bounded repair attempt is allowed. Invalid facts are re-extracted or made unusable; invalid pathways, gaps, and recommendations are revised or suppressed; unresolved routing becomes `team_to_confirm`; render failures block artifact release. The system prefers fewer verified recommendations over unsafe completeness.

An additional final semantic check is triggered when a recommendation names a study or instrument, relies on a number/date/threshold, invokes formal authority, depends materially on country evidence, references contradictory facts, has only moderate evidence for high materiality, produces a deterministic warning, or includes drafting language.

### 9.3 Fully automatic workflow

No human review is required or managed by the application. The standard flow completes automatically through extraction, analysis, compilation, checking, bounded repair, and rendering. The output retains a concise AI-assisted advisory disclaimer and transparent confidence limitations. Optional consultation with specialists remains outside the product workflow.

## 10. Phase 5: Presentation

### 10.1 Executive readout

Target 500-800 words containing project/stage, a short relevance statement, the four judgments, two to four strengths, two to four residual improvement areas, zero to three decision summaries, and evidence limitations.

### 10.2 Ranked priority actions

Collapsed cards show rank, decision, minimum action, timing, and confidence. Expanded cards show evidence, existing response, residual gap, rationale, enhanced action, routing, responsibility, completion evidence, caution, and verified drafting language.

### 10.3 Review-readiness flags

The compact separate section states that flags do not affect the Climate-FCV judgments unless independently reflected in the analysis.

### 10.4 Technical annex

The annex contains readable evidence sources, pathways, key project-fact trace, confidence and limitations, lower-priority considerations, suppressed items where useful, and automated validation status. Internal IDs appear only in the technical trace.

The web interface replaces the single integration dial with four compact judgment indicators and uses progressive disclosure. HTML and DOCX are standalone products generated from the same structured source, without browser navigation or hidden interface text.

## 11. Calls and failure handling

The internal call structure is:

1. verified project-fact extraction;
2. pathways, existing responses, and residual gaps;
3. small judgment/residual-logic review;
4. recommendation admission and compilation; and
5. conditional final semantic review.

The visible three-stage workflow remains unchanged. Existing per-stage timeout and output ceilings remain the starting constraint; implementation must measure latency before changing them.

Malformed typed output receives one bounded JSON repair. If project facts cannot be verified, dependent analysis is suppressed. If the Climate assessment cannot produce a usable truth layer, the route returns an actionable retry/fallback error rather than a confident partial assessment. Country-bank or live-research failure remains non-fatal and uses the existing grounding fallback states.

## 12. Compatibility and migration

- Existing lens selection, request fields, country-bank interfaces, and core non-Climate workflows remain unchanged.
- The new internal assessment schema is versioned `climate-verified-v2`.
- Legacy `climate-native-v1` saved sessions remain readable through a compatibility adapter but are not upgraded into verified facts retrospectively.
- New Climate sessions and exports use the v2 typed products.
- The generic non-Climate Stage 3 priority schema remains unchanged; the dedicated Climate route receives its own verified recommendation contract.
- Any new shared delimiter, session, SSE, or recommendation fields require an explicit Render/ITS parity decision and update to the private parity contract before merge.
- Final bank-integrated acceptance testing occurs after the parallel country-bank work lands. The implementation must not edit or assume incomplete companion-bank changes.

## 13. Test and evaluation strategy

### 13.1 South Sudan golden regression

The June 2026 PCN is the first labelled fixture. Tests require that:

- the only explicit Year 1 feasibility study is tied to Sub-component 1.4 and Year 1 of implementation;
- it cannot carry Sub-component 1.2 or Component 2 work without an explicit scope-change recommendation;
- Risk 16 includes every documented mitigation;
- missing dates remain unknown;
- unsupported project lifetime and inaccessible precision are omitted or qualified;
- relevance and project quality remain distinct;
- priorities are genuinely ranked and not all labelled High;
- readiness issues remain separate;
- exports contain no truncation or UI artifacts; and
- the strongest grounded features of comparator outputs A, B, and C are retained.

### 13.2 Seeded and metamorphic tests

Fixtures cover wrong-scope and wrong-timing studies, omitted mitigation, national-to-site overreach, guidance presented as requirements, duplicate priorities, unsupported thresholds, truncated fields, incorrect routing, and contradictory project information.

Metamorphic tests remove or change one fact and verify downstream behavior: routing becomes unresolved, a late study becomes inadmissible, added mitigation narrows the gap, resolved indicators remove flags, and lower confidence produces verification-oriented or suppressed actions.

### 13.3 Release acceptance

Release requires zero critical grounding or routing errors, deterministic contract and export parity, repeated-run stability on the golden case, representative tests across stages and instruments, and blinded expert comparison against A/B/C on accuracy, residual-gap discipline, proportionality, actionability, evidence traceability, readability, and integrity.

## 14. Implementation sequencing

1. Upgrade extraction and implement the verified truth layer with deterministic checks.
2. Add typed pathway, response, and residual-gap products plus evidence entitlements.
3. Replace the composite rating with four judgments.
4. Add recommendation admission, ranking, routing, and safety logic.
5. Add deterministic and semantic validation with bounded repair.
6. Replace Climate presentation/export with the v2 structured renderer.
7. Add the South Sudan golden harness and broader fixtures throughout, not only at the end.
8. Integrate and calibrate against the completed country-bank work.

Each increment must preserve the non-Climate route and retain a runnable verified subset. No implementation increment should depend on a human-review workflow.
