# South Sudan Climate-FCV Evidence Bank Redesign

**Date:** 2026-08-01
**Status:** Approved design
**Scope:** South Sudan pilot bank, FCV-AGENT bank selection, Climate-FCV live research, and validation
**Branch:** `feat/climate-country-bank`

## 1. Decision

Adopt a coverage-led country evidence bank with compact project-specific selection.
The approved structural bank remains the reliable foundation. A deterministic
project profile and coverage-aware selector tailor that foundation to each uploaded
project. Live web research remains a non-fatal, assessment-time enrichment layer
directed at the most material gaps left by the bank.

The redesign must improve evidence depth and project specificity without increasing
the current context limits, adding a required curator-model call, or weakening the
live-research evidence gate.

## 2. Why the current pilot needs revision

The approved South Sudan pilot proves the repository, review, release, deployment,
selection, and bank-only fallback architecture. It is not yet a sufficiently
systematic country foundation for the range of projects the Climate-FCV lens may
assess.

The present package has 12 registered sources, 19 approved evidence records, and
seven approved pathways. Its main strengths are traceability, explicit uncertainty,
human approval, causal caution, and concrete material on flooding, displacement,
pastoral mobility, resource competition, and humanitarian access.

The substantive audit identified the following limitations:

- 15 of 19 records are observed, three inferred, and one projected.
- Seventeen records address current conditions; only one carries a long-term
  horizon.
- Flood-related tags appear on 12 records, and six records rely on the same SIPRI
  fact sheet.
- The only explicit future impact finding is a directional statement that hotter
  conditions could reduce sorghum yields by 2050; it includes no magnitude,
  scenario range, or subnational differentiation.
- Vulnerability evidence consists of useful examples rather than a systematic
  treatment of exposure, sensitivity, coping capacity, adaptive capacity, and
  institutional capacity.
- Institutional evidence describes plans and broad constraints but does not map
  mandates, delivery arrangements, financing, subnational capacity, or demonstrated
  performance.
- Positive resilience evidence mainly records activities, not evaluated outcomes.
- Geographic coverage is concentrated in selected flood-affected locations and is
  not organized by state, county, livelihood zone, or ecological system.
- Agriculture, health, and humanitarian access dominate. Fisheries, forests, the
  Sudd, water systems, transport, urban systems, and other sectors lack depth.
- The dossier repeats canonical records as evidence, pathways, uncertainties,
  screening implications, and trace rows instead of providing a concise analytical
  synthesis.

The runtime compounds these content limitations. The compact packet strips
geography, groups, sectors, institutions, time horizon, scenario, confidence,
uncertainty, and locators from selected evidence. Selection uses exact token overlap
against a bounded document excerpt rather than a structured project profile. Adding
more records without addressing these runtime constraints would improve the dossier
more than the assessment.

## 3. Goals

1. Make the South Sudan bank systematic across climate pressure, exposure,
   vulnerability, capacity, institutions, pathways, and response performance.
2. Preserve atomic, source-traceable, human-approved evidence and explicit causal
   limits.
3. Distinguish slow-changing structural evidence from refreshable current evidence
   and assessment-time project research.
4. Select a balanced, project-relevant packet using deterministic local logic.
5. Preserve the metadata necessary for the model to reason about geography,
   affected systems, uncertainty, and relevance.
6. Direct live web research at named project locations, sectors, systems,
   institutions, and uncovered evidence needs.
7. Improve research failure diagnostics while retaining safe bank-only fallback.
8. Validate substantive quality across contrasting South Sudan project archetypes.
9. Preserve the established context, timeout, privacy, copyright, and human-review
   boundaries.

## 4. Non-goals

- Do not build additional countries in this change.
- Do not support multi-country bank allocation or cross-border pathway selection.
- Do not make live research mandatory for a valid Climate-FCV assessment.
- Do not add an assessment-time curator LLM call.
- Do not increase the 6,000-character bank limit, six-claim live limit, or
  12,000-character combined grounding limit in the first implementation.
- Do not loosen source, attribution, claim-linkage, or truncation requirements.
- Do not redistribute source PDFs or store unpermitted source text.
- Do not treat national indices, plans, or model-generated synthesis as causal
  evidence.
- Do not change the generic FCV workflow or recreate its generic question engine in
  Climate mode.

## 5. Evidence architecture

The evidence system has three layers.

### 5.1 Structural country bank

The reviewed South Sudan bank contains slow-changing evidence on:

- climate pressures and projections;
- exposure and sensitivity;
- household and community coping capacity;
- longer-term adaptive capacity;
- formal and informal institutions;
- implementation and response performance;
- mediated Climate-FCV pathways; and
- resilience and peace-supporting capacities.

The structural bank is reviewed annually or when material new evidence becomes
available. It is the dependable fallback when research is unavailable or rejected.

### 5.2 Current refresh layer

Time-sensitive evidence covers recent hazards, displacement, food security,
conflict/access conditions, service disruption, and operational constraints. Each
record carries an explicit `review_due` date appropriate to its volatility. Stale
current evidence remains visible for review but is not silently promoted into a new
runtime release.

The intended refresh cadence is quarterly or semi-annual, depending on the source
and topic. This layer remains part of the reviewed release process rather than an
unreviewed cache.

### 5.3 Assessment-time project research

Live research addresses the uploaded project's named locations, sectors,
components, groups, institutions, assets, and unresolved evidence gaps. It is
validated separately from bank content and retains distinct provenance. Failure or
rejection produces an honest warning and bank-only assessment.

## 6. Canonical evidence model

### 6.1 Evidence classes

Every canonical evidence record has one primary `evidence_class`:

| Evidence class | Question answered |
|---|---|
| `climate-pressure` | What climate condition is changing, where, when, and with what uncertainty? |
| `exposure` | Which people, assets, ecosystems, or services are located in affected areas? |
| `sensitivity` | Why is the exposed livelihood, system, or group susceptible? |
| `coping-capacity` | What enables or prevents management of immediate shocks? |
| `adaptive-capacity` | What enables or prevents longer-term adjustment? |
| `institutional-capacity` | Which institution has the mandate, resources, access, and delivery capability? |
| `response-performance` | What intervention was attempted, and what is known about delivery or results? |
| `direct-climate-fcv` | What evidence directly supports a Climate-FCV link or mediator? |
| `resilience-peace-capacity` | What system, relationship, or institution reduces risk or supports cooperation? |

The existing `analytical_role` remains during migration for compatibility and is
mapped to the new class. It no longer serves as the primary coverage dimension.

### 6.2 Required canonical fields

Each record contains:

- stable evidence ID and country code;
- one atomic evidence statement;
- one compact screening statement;
- primary evidence class and compatibility analytical role;
- observed, projected, or inferred evidence status;
- hazard and impact tags where applicable;
- geography plus administrative or ecological level;
- affected groups;
- sectors and livelihood systems;
- institutions;
- systems, assets, and resources;
- mediator tags where applicable;
- interaction direction;
- time horizons and scenario where applicable;
- source references with precise locators;
- confidence and uncertainty;
- structural or current refresh tier;
- review status, review date, and review-due date.

Records must remain atomic. A source passage that supports different analytical
claims becomes separate linked records rather than a compound paragraph.

### 6.3 Pathway structure

Every pathway continues to distinguish:

- climate pressure;
- documented impact;
- FCV mediator;
- possible consequence;
- affected groups, institutions, and systems;
- geography;
- supporting evidence by link;
- evidence strength;
- alternative explanations;
- resilience factors;
- interaction direction; and
- uncertainty.

Pathways do not convert co-occurrence into attribution. Inferred consequences remain
conditional in both the runtime packet and the user-facing output.

### 6.4 Schema migration

The expanded release uses runtime schema `1.1.0`. The application loader accepts
both `1.0.0` and `1.1.0` during migration. A `1.0.0` release is projected into the
new internal shape with null or empty values for fields that did not exist. The
current approved South Sudan release remains deployable until the new release is
approved and promoted.

The companion schemas reject unknown evidence classes, invalid review tiers,
unresolved source links, cross-country references, and projected records without a
time horizon or scenario description.

## 7. South Sudan coverage plan

The revision fills gaps according to coverage, not an arbitrary record target.

### 7.1 Priority domains

1. CMIP6 temperature, precipitation, variability, and extreme-event projections.
2. Flood persistence, hydrology, and geographic exposure.
3. Drought, dry spells, rainfall variability, and dry-season water stress.
4. Agriculture, livestock, fisheries, forests, and the Sudd wetland system.
5. Roads, markets, water systems, health, education, and humanitarian access.
6. Displacement, return, land access, high-ground use, and host-community pressure.
7. Differentiated gender, age, disability, displacement, and livelihood
   vulnerability.
8. Household, community, and customary coping systems.
9. Formal and informal institutional mandates, delivery capacity, and coordination.
10. Early warning, climate services, disaster response, and anticipatory action.
11. Evaluated response effectiveness, delivery failure, and unintended effects.
12. Climate-to-FCV, bidirectional, and FCV-to-climate pathways.

### 7.2 Source strategy

Priority sources include:

- the full South Sudan CCDR rather than only its landing-page key message;
- World Bank Climate Change Knowledge Portal CMIP6 mean, variability, and extreme
  projections;
- IPCC regional findings where country evidence is unavailable;
- South Sudan's NAP, NDC, technology-needs, and capacity assessments;
- IOM, IPC, FAO, WFP, UNHCR, OCHA, and relevant national operational evidence;
- evaluated development, humanitarian, disaster-risk, and peacebuilding
  interventions;
- direct Climate-FCV analysis from SIPRI, UN mechanisms, and comparable specialist
  sources; and
- carefully bounded conflict, displacement, and hazard datasets for triangulation.

A source may support only the link it actually establishes. Plans demonstrate
intent, not implementation. Activity reports demonstrate delivery only to the
extent documented. National indices orient screening but do not establish local
causality. Local qualitative studies are not generalized nationally without
support.

### 7.3 Coverage standard

Readiness is determined by a coverage matrix rather than record count. Promotion
requires:

- representation of every evidence class or an explicit justified gap;
- explicit treatment of the major South Sudan livelihood and service systems;
- both interaction directions;
- separation of national, subnational, and localized claims;
- some evaluated capacity or response evidence;
- future projections separated from observed impacts;
- geographic and sector gaps visible in the review artifact; and
- no unsupported claim of comprehensive national coverage.

## 8. Human-readable dossier

The dossier becomes an analytical review product rather than a repeated database
dump. Its main body contains:

1. executive assessment;
2. evidence coverage and critical gaps;
3. climate pressures and exposure;
4. differentiated vulnerability;
5. coping and adaptive capacity;
6. institutions and delivery systems;
7. Climate-FCV pathways;
8. resilience and peace-supporting capacities;
9. geographic and livelihood-system differentiation;
10. implications by project type;
11. technical evidence register; and
12. bibliography and review decision.

The companion repository adds a reviewed `profile.json` for country-level
synthesis. It contains the executive assessment, coverage findings, geographic
notes, sector notes, and known gaps, each linked to evidence or pathway IDs. The
dossier generator combines this reviewed synthesis with canonical records and the
technical trace table. The generated `dossier.md` remains reproducible and is not
manually edited after generation.

## 9. Project Climate Profile

Before bank selection and live research, local preprocessing creates a bounded
`ProjectClimateProfile`:

```json
{
  "country": "South Sudan",
  "instrument": "IPF",
  "document_stage": "PCN",
  "geographies": ["Jonglei", "Upper Nile", "Ruweng"],
  "sectors": ["fisheries", "forestry", "natural resource management"],
  "project_elements": ["BFMUs", "CWCs", "community forestry associations"],
  "affected_groups": ["fishing communities", "pastoralists", "displaced people"],
  "institutions": ["WFP", "OCHA", "UNHCR"],
  "systems_assets": ["fisheries corridor", "forest landscapes"],
  "documented_hazards": ["flooding"],
  "time_horizons": ["preparation", "project-lifetime"],
  "unresolved": []
}
```

The extractor scans the available extracted project text locally and emits only a
bounded profile. It uses:

- country administrative and geographic aliases from the release;
- controlled sector, livelihood, institution, asset, and hazard aliases;
- component and subcomponent heading patterns;
- document type and instrument metadata; and
- explicit confidence and unresolved fields.

It does not infer an undocumented location, component, group, or institution. A
hazard may be marked `document-explicit` or `bank-candidate`; the distinction is
preserved. No provider call is added.

## 10. Coverage-aware deterministic selection

### 10.1 Matching and scoring

The selector matches:

- geography;
- sector and livelihood;
- project component or activity;
- affected group;
- institution;
- system, asset, or resource;
- hazard;
- time horizon; and
- evidence class.

Controlled aliases handle known equivalences such as pastoralism, cattle keeping,
and livestock mobility. Geography and named project-element matches retain the
highest weights. Stale current records are penalized. Near-duplicate claims are
suppressed. Source diversity is assessed across all supporting sources, not only a
pathway's first source.

### 10.2 Balanced selection

Where supported and relevant, a normal packet contains:

- one climate-pressure or projection record;
- two vulnerability, coping, or adaptive-capacity records;
- one institutional-capacity or response-performance record;
- one Climate-to-FCV pathway;
- one FCV-to-climate or bidirectional pathway; and
- up to two additional high-scoring records.

The target remains approximately eight items, the hard maximum remains 12, and the
hard bank boundary remains 6,000 characters. Low-scoring records are not selected
merely to fill a class. An uncovered class becomes a declared research gap.

### 10.3 Selection diagnostics

The selector returns canonical IDs plus bounded diagnostics:

- score;
- matched profile fields;
- balance role;
- duplicate suppression reason;
- staleness decision; and
- omitted required class, if any.

Logs contain IDs and structural reason codes only, never confidential document
text. Before changing selection, implementation must reconcile the current code's
eight-item target with the final handover log reporting 12 selected items.

## 11. Compact evidence capsules

The runtime packet uses richer capsules while preserving the character limit.

Evidence capsule:

```json
{
  "id": "SSD-E-042",
  "class": "adaptive-capacity",
  "claim": "Localized flood warnings ...",
  "geographies": ["Jonglei"],
  "groups_systems": ["fishing communities", "local warning systems"],
  "project_relevance": "Relevant to community fisheries activities",
  "status": "observed",
  "uncertainty": "Evidence covers selected counties only",
  "source_ids": ["SSD-SRC-021"]
}
```

Pathway capsules retain pressure, mediator, possible consequence, geography or
system, direction, evidence strength, uncertainty, and supporting evidence IDs.

Capsules favor information density over record count. The implementation drops
whole low-priority capsules when necessary and never truncates individual claims or
uncertainties into ambiguous fragments.

## 12. Gap-directed live research

### 12.1 Research agenda

After bank selection, a deterministic coverage planner produces no more than three
ranked questions from:

- unmatched project signals;
- required evidence classes absent from the packet;
- selected records with weak geography or expired current evidence; and
- long-lived assets lacking project-lifetime evidence.

For the South Sudan natural-resource pilot, a valid agenda could ask about current
or projected flood conditions in Jonglei and Upper Nile, fisheries or wetland
sensitivity, and current displacement, access, or resource-use conditions in named
project locations.

### 12.2 Research execution

The existing bounded research mechanism remains non-fatal. It:

1. receives the structured project profile, selected bank summary, and research
   agenda;
2. performs exactly two targeted searches initially;
3. prioritizes a full CCDR or authoritative physical source where relevant;
4. uses the second search for the highest remaining material gap;
5. returns four to six claims at most;
6. requires every claim to name a project element and a geography, group,
   institution, system, or asset;
7. preserves exact source linkage and evidence status; and
8. permits one narrow retry only when the response is structurally repairable.

No additional search count, provider call, or timeout increase is introduced until
targeting and evidence-gate diagnostics have been evaluated.

### 12.3 Evidence-gate diagnostics

The gate returns one primary sub-reason plus bounded counts. Required sub-reasons
include:

- `no_authoritative_source`;
- `source_url_invalid`;
- `claim_without_source`;
- `claim_not_project_linked`;
- `claim_not_geographically_linked`;
- `insufficient_distinct_sources`;
- `response_truncated`;
- `invalid_time_horizon`; and
- `unsupported_inference`.

Diagnostics contain no source content or confidential project text. Rejected
research is excluded completely. The grounding state and disclosure continue to
distinguish `bank+research`, `bank-only`, `research-only`, and `thematic-only`.

## 13. Context, latency, and reliability constraints

The first implementation preserves:

- target eight and maximum 12 selected bank items;
- 6,000 bank characters;
- maximum six accepted live claims;
- 12,000 combined external-grounding characters;
- the existing Stage 1 aggregate research budget;
- the Stage 2 16,000-output-token ceiling;
- bank-only fallback;
- current truncation guards; and
- no required runtime curator call.

The design improves the allocation of bounded context rather than expanding it.
Local profile extraction, bank selection, coverage planning, and validation must be
deterministic and fast relative to document extraction.

## 14. Dossier and runtime separation

The full dossier remains a human review artifact and is never injected into an
assessment. The runtime release materializes approved canonical records. The
selector chooses project-relevant IDs, and the merger serializes only compact
capsules plus accepted live claims.

Full source metadata remains available for provenance and report generation but is
not duplicated in the model prompt when stable IDs suffice.

## 15. Implementation increments

### Increment 1: Evidence and dossier foundation

- Add schema `1.1.0` and compatibility validation.
- Add the reviewed country profile and coverage matrix.
- Extract and review the priority missing South Sudan evidence.
- Split compound claims into atomic records.
- Strengthen geographic, temporal, institutional, and capacity metadata.
- Regenerate and review the redesigned candidate dossier.
- Leave the current approved runtime release unchanged until approval.

### Increment 2: Selector and compact packet

- Build the local Project Climate Profile.
- Add controlled aliases and coverage-aware scoring.
- Add balance rules, duplicate suppression, and staleness handling.
- Generate research-gap questions.
- Serialize richer compact capsules.
- Add content-safe selection diagnostics.

### Increment 3: Live-research reliability

- Pass the structured profile and gap agenda to research.
- Add evidence-gate sub-reasons and structural telemetry.
- Test narrow retry and truncated-response handling.
- Preserve all fallback paths and provenance disclosures.

## 16. Validation

### 16.1 Golden project profiles

Use at least five contrasting South Sudan fixtures:

| Profile | Expected evidence |
|---|---|
| Agriculture and livestock | Heat, rainfall, drought, pasture, mobility, food systems |
| Fisheries, forestry, and NRM | Flooding, wetlands, resource governance, livelihood competition |
| Roads and infrastructure | Flood exposure, access, service interruption, land and security constraints |
| Health and WASH | Flooding, heat, disease, service access, displacement, gender |
| Social protection and community resilience | Shock response, targeting, displacement, coping, local institutions |

For each fixture, verify that:

- selected evidence differs materially across project types;
- every selected item has an intelligible reason code;
- required classes are covered or explicitly missing;
- local evidence is not generalized nationally;
- pathways preserve uncertainty;
- the bank packet stays within 6,000 characters; and
- combined grounding stays within 12,000 characters.

### 16.2 Output comparison

Expert review compares the current and redesigned outputs on:

1. geographic specificity;
2. component anchoring;
3. differentiated groups;
4. institutional specificity;
5. causal discipline;
6. adaptive-capacity depth;
7. distinctiveness across projects;
8. evidence traceability;
9. unsupported or overstated claims; and
10. recommendation usefulness.

Automated tests establish contracts and bounds; expert review determines substantive
quality.

### 16.3 Live acceptance

After local verification:

1. run one South Sudan bank-only assessment;
2. pass a controlled synthetic bank-plus-research fixture through the real evidence
   gate;
3. run one production South Sudan assessment with live research;
4. confirm the precise gate outcome in logs;
5. review the note and provenance disclosure; and
6. avoid repeated paid production runs unless a specific defect has been corrected.

### 16.4 Automated coverage

Tests cover schema migration, old-release compatibility, project-profile extraction,
aliases, geographic matching, evidence balance, staleness, duplicate suppression,
capsule bounds, deterministic selection, evidence-gate sub-reasons, retry and
truncation behavior, all provenance fallbacks, and HTML/DOCX disclosure.

## 17. Promotion gates

The new South Sudan release is promoted only when:

- the candidate dossier and profile are substantively approved;
- schemas, checksums, references, and review windows validate;
- golden-project selection is accepted;
- bank and combined context limits remain unchanged;
- bank-only output is at least as strong as the accepted baseline;
- rejected research remains excluded and non-fatal;
- the production research result has a specific diagnosable gate outcome;
- no confidential project material enters logs or fixtures; and
- dual-build parity decisions are recorded.

## 18. Dual-build parity

Each implementation change is classified as companion-bank-only,
Render/Flask-specific, or a shared contract. Evidence classes, runtime fields,
provenance states, research schemas, rating semantics, and output disclosures are
shared-contract candidates and require an explicit Azure/FastAPI parity decision in
the private parity log before merge.

The first content-only increment may proceed without changing the internal build as
long as the production runtime schema remains pinned to the current approved release.

## 19. Risks and mitigations

| Risk | Mitigation |
|---|---|
| A larger bank reduces selection quality | Coverage-aware scoring, aliases, balance rules, golden fixtures |
| Rich capsules exceed context limits | Optimize for eight items and drop whole low-priority capsules |
| New fields break the current release | Dual-version loader during migration |
| Plans are mistaken for capacity | Separate institutional intent from response performance |
| Local evidence is generalized nationally | Administrative level, geography, and uncertainty are required |
| Live research repeats bank content | Gap-directed agenda and deduplication |
| Research still fails the gate | Precise sub-reasons, one narrow retry, bank-only fallback |
| More searches recreate timeout failures | Preserve search count and time budgets initially |
| Current evidence becomes stale | Refresh tiers and record-level review-due dates |
| Dossier becomes another unreviewed model product | Reviewed profile data and deterministic generation |

## 20. Definition of done

The redesign is complete when the approved South Sudan bank provides systematic,
traceable coverage; contrasting projects receive materially different and balanced
evidence packets; the model receives the geography, system, uncertainty, and
relevance needed to use those packets; targeted live research either adds validated
project-specific evidence or fails transparently; and all of this operates within
the current context and timeout contracts.
