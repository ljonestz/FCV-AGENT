# Climate-FCV Evidence Bank and Reliable Grounding Design

**Date:** 2026-07-30
**Branch:** `feat/climate-country-bank`
**Status:** Approved in collaborative design; awaiting review of this written specification
**Supersedes:** `2026-07-30-climate-fcv-reliability-country-bank-design.md` and the bank-related assumptions in `2026-07-30-climate-fcv-country-bank-reliability.md`

## 1. Decision Summary

The Climate-FCV module will use a public, versioned country evidence bank as a reliable grounding floor. The bank will contain detailed source catalogues, structured evidence records, mediated Climate-FCV pathways, and human-readable country dossiers. At runtime, the application will select a small project-relevant subset of approved records and merge it with live web research.

The design has six governing decisions:

1. Rich country research and compact runtime context are separate products.
2. Vulnerability, adaptive capacity, institutions, and mediated Climate-FCV pathways receive more analytical weight than detailed physical-climate projections.
3. Language models may extract, classify, and summarize evidence, but model general knowledge is never an evidence source.
4. Runtime selection is dynamic but deterministic in version 1. It adds no provider call.
5. Live research is always attempted for current, subnational, and project-specific enrichment, but failure is non-fatal.
6. The existing dedicated climate-native Stage 2 prompt is retained. It is already implemented and tested; it must not be recreated as proposed in the superseded plan.

South Sudan is the first full pilot, using the existing PCN as the runtime validation case.

## 2. Problem and Current State

The Climate-FCV module currently has two reliability characteristics:

- Climate mode already uses a dedicated climate-native Stage 2 prompt and does not run the generic 12-OST, DNH-9, or 25-question engine. Both Express and step-by-step routes select the dedicated builder, and existing tests protect that boundary.
- Live Climate research is still treated as a mandatory evidence gate. Search, continuation, structuring, and validation can consume the Stage 1 research budget or fail stochastically. A failed live pass can therefore prevent the otherwise valid climate-native assessment from running.

The country bank addresses the second characteristic. It also improves analytical quality by supplying reviewed, stable evidence on country vulnerability, capacity, institutions, sectors, and Climate-FCV mechanisms that a short live search cannot reconstruct reliably on every run.

## 3. Goals and Non-Goals

### 3.1 Goals

- Produce a substantive Climate-FCV assessment when live research fails.
- Keep live research as the preferred source of current and highly localized enrichment.
- Ground country-specific claims in traceable sources and locators.
- Distinguish physical climate pressures from vulnerability, capacity, and mediated FCV pathways.
- Select different evidence for different projects in the same country.
- Keep runtime bank context within a strict prompt budget.
- Preserve source and evidence provenance through assessment and export.
- Support incremental country review and release rather than one unreviewed bulk generation.
- Keep the standard non-Climate FCV route unchanged.

### 3.2 Non-Goals

- Replacing the existing thematic Climate-FCV knowledge module.
- Rebuilding the dedicated climate-native Stage 2 prompt.
- Running a new runtime LLM-based evidence-curator call in version 1.
- Treating indexes, co-occurring hazards and conflict, or model output as proof of causality.
- Reproducing full copyrighted source documents in the bank.
- Completing all FCS countries before the South Sudan design is validated.
- Applying country-bank evidence to multi-country or regional operations during the
  single-country pilot.
- Porting the feature to the ITS/FastAPI build during this effort.

## 4. System Boundaries

### 4.1 Public Companion Repository

A new public repository named `climate-fcv-country-bank` is the source of truth for:

- source metadata;
- structured evidence ledgers;
- structured interaction pathways;
- country dossiers;
- review records;
- schemas and validators;
- offline ingestion and release scripts; and
- versioned compact runtime releases.

Source PDFs are included only where redistribution rights clearly permit it. Otherwise, the repository stores citations, URLs, access dates, page or section locators, and derived summaries.

### 4.2 FCV-AGENT Repository

The application repository contains:

- the runtime release loader;
- schema compatibility checks;
- country and ISO matching;
- the deterministic evidence selector;
- the bounded grounding merger;
- synthetic test fixtures;
- UI and export provenance notices; and
- typed observability.

The public companion repository is included by default as a pinned public Git
submodule. `CLIMATE_COUNTRY_BANK_PATH` may override the submodule path for local
development or a different deployment layout. The loader contract remains
path-based so the storage mechanism can change without changing the analysis
pipeline.

### 4.3 Offline Literature Ingestion

An offline Codex-assisted workflow:

1. registers approved sources;
2. extracts candidate atomic evidence records with locators;
3. proposes structured Climate-FCV pathways;
4. generates the country dossier from those records;
5. runs schema and cross-reference validation;
6. presents the dossier and evidence table for human review; and
7. promotes approved records into a versioned runtime release.

The model never cites itself and may not fill an unsupported field from general knowledge.

### 4.4 Runtime Evidence Curator

Version 1 uses a deterministic component, not a separate model call. It:

- filters by country or regional applicability;
- scores project relevance;
- enforces evidence-role and source diversity;
- selects a bounded record set; and
- returns canonical record IDs, not rewritten evidence.

The existing climate-native Stage 2 model performs final interpretation and synthesis from this selected packet. A separately model-driven curator may be evaluated later behind a feature flag, but it may never become a required path.

## 5. Evidence Methodology

### 5.1 Two Independent Source Dimensions

The bank does not use a single authority hierarchy. Each source has two independent assessments:

1. **Source quality:** institutional or scholarly credibility, methodological transparency, traceability, currency, geographic specificity, and limitations.
2. **Analytical role:** the type of proposition the source can support in a Climate-FCV assessment.

An authoritative physical-climate dataset can score highly on source quality while remaining supporting rather than central evidence for a mediated Climate-FCV pathway.

### 5.2 Analytical Roles and Priority

#### Role A: Direct Climate-FCV Evidence

This is the analytical centre of the bank:

- country and regional climate, peace, and security assessments;
- climate-conflict-mobility analyses;
- conflict-sensitive adaptation studies;
- field-based work on governance, exclusion, institutions, livelihoods, resource access, displacement, coping capacity, and social relations; and
- trusted operational NGO and humanitarian analysis.

Priority collections include relevant work from Weathering Risk/adelphi, SIPRI/NUPI, ODI, SEI, International Alert, CGIAR, UN climate-security mechanisms, and ICG where a report directly analyzes environmental or climate dynamics.

Examples:

- Weathering Risk Mali assessment: <https://weatheringrisk.org/en/publication/climate-peace-and-security-assessment-mali>
- SIPRI Climate, Peace and Security work: <https://www.sipri.org/research/peace-and-development/climate-change-and-risk>
- ODI Climate Security collection: <https://odi.org/en/topics/climate-security/>
- SEI environment-conflict-migration study: <https://www.sei.org/publications/exploring-the-environment-conflict-migration-nexus-in-asia/>
- International Alert climate, conflict, and fragility report: <https://www.international-alert.org/publications/climate-change-conflict-and-fragility/>

#### Role B: Vulnerability, Adaptive Capacity, Institutions, and Sectors

This role is at least as important as direct pathway evidence:

- Country Climate and Development Reports;
- NAPs, NAPAs where relevant, and NDCs;
- INFORM and ND-GAIN qualitative dimensions;
- sector diagnostics on food systems, water, pastoralism, health, infrastructure, urban services, energy, ecosystems, and social protection;
- institutional capacity and local-governance analysis;
- humanitarian access, displacement, mobility, markets, and coping strategies; and
- UN, government, multilateral, and trusted NGO country analysis.

CCDRs are a core source because they often connect climate exposure with development constraints, sectors, institutions, poverty, and implementation priorities:
<https://www.worldbank.org/en/publication/country-climate-development-reports>

NAPs and NDCs evidence government priorities, stated capacity gaps, and planned responses. They do not independently prove that implementation capacity or results exist.

INFORM and ND-GAIN orient qualitative inquiry. Their rankings do not establish a causal pathway or replace country analysis.

#### Role C: Supporting Physical-Climate Baseline

CCKP, IPCC, WMO, and related sources establish only the physical foundation necessary for the assessment:

- principal hazards;
- broad observed direction of change;
- major projected tendencies;
- material subnational variation;
- high-level sector exposure; and
- scientific uncertainty.

The bank avoids extensive projections and precise figures unless they affect a project decision. Physical evidence supports the climate-pressure link of a pathway; it does not establish the FCV mediator or consequence.

### 5.3 Causal Discipline

Hazard exposure and FCV conditions occurring in the same place are not sufficient evidence of a Climate-FCV pathway. A pathway must identify:

1. a supported climate pressure or climate-sensitive impact;
2. a supported or explicitly inferred mediator;
3. an affected group, institution, livelihood, service, resource, system, or asset;
4. a plausible FCV or development consequence;
5. contrary evidence or important uncertainty; and
6. the source records supporting each link.

The pathway evidence-strength enum is:

- `direct`: one source directly documents the mediated pathway in the relevant geography;
- `triangulated`: separate credible sources support the pressure, mediator, and consequence;
- `analytical-inference`: the pathway is a bounded synthesis from supported elements but is not directly documented.

The application must present analytical inference conditionally and never as an established causal finding.

## 6. Data Model

### 6.1 Runtime Release

Each release contains:

- `schema_version`;
- `content_version`;
- `generated_at`;
- `compatible_app_versions`;
- `source_manifest_checksum`;
- `countries`;
- `sources`;
- `evidence_records`; and
- `pathways`.

Only approved country content is included in a production release.

### 6.2 Source Record

Required fields:

- stable `source_id`;
- title, authoring organization, and publication date;
- URL or repository-relative file reference;
- source type and analytical roles;
- country and geographic coverage;
- temporal coverage;
- access date;
- methodology summary;
- known limitations;
- license or redistribution status; and
- checksum where a local file is retained.

### 6.3 Atomic Evidence Record

Required fields:

- stable `evidence_id`;
- `iso3`;
- concise evidence statement;
- evidence status: `observed`, `projected`, or `inferred`;
- analytical role;
- hazard and impact tags;
- named geographies and spatial level;
- affected groups;
- sectors, systems, assets, resources, livelihoods, and institutions;
- FCV mediator tags;
- interaction direction where applicable;
- time horizons and scenario where applicable;
- source references with page, table, paragraph, or section locators;
- confidence;
- uncertainty or evidence gap;
- review status; and
- review date.

Quantitative statements additionally require unit, reference period, scenario or model generation where relevant, and geographic aggregation.

### 6.4 Interaction Pathway

Required fields:

- stable `pathway_id`;
- `iso3`;
- climate pressure;
- documented impact;
- FCV mediator;
- possible consequence;
- geographies and affected groups;
- relevant sectors, systems, resources, or institutions;
- supporting evidence IDs for each link;
- evidence strength;
- alternative explanations;
- uncertainty;
- resilience or mitigating factors; and
- review status.

Pathways remain country-context evidence. They are not pre-written project recommendations.

### 6.5 Review Record

Country content moves through:

- `draft`;
- `reviewed`;
- `approved`;
- `stale`; or
- `rejected`.

Human review occurs at the country dossier and linked-evidence-table level. Only `approved` records enter a production runtime release. A stale country may remain readable in the research repository but is excluded from a new release until re-reviewed.

## 7. Country Dossier

The dossier is an 8-12 page review artifact generated from the structured records. Its indicative balance is:

- 10-15 percent: physical climate and hazard baseline;
- 30-35 percent: vulnerability, adaptive capacity, institutions, and sector conditions;
- 35-45 percent: mediated Climate-FCV pathways; and
- 15-20 percent: resilience factors, uncertainties, entry points, and evidence gaps.

These percentages guide editorial balance and are not hard quotas.

The dossier includes:

1. scope, source coverage, and limitations;
2. concise climate and hazard baseline;
3. differentiated vulnerability and adaptive capacity;
4. relevant institutions, services, sectors, and livelihoods;
5. mediated Climate-FCV pathways;
6. reverse pathways showing how conflict and fragility affect climate vulnerability and action;
7. resilience factors and institutional or community capacity;
8. uncertainties and contested findings;
9. implications for project screening, without project-specific recommendations; and
10. linked bibliography and evidence table.

## 8. Runtime Selection and Context Bounds

### 8.1 Project Signals

The selector uses already-available project information:

- country and subnational locations;
- sector and instrument;
- components and activities;
- groups and beneficiaries;
- institutions and delivery arrangements;
- infrastructure, services, natural resources, livelihoods, systems, and assets;
- climate signals;
- lifecycle and time horizon; and
- user priority questions.

### 8.2 Selection Order

The selector:

1. filters records by exact country, then applicable cross-border or regional records;
2. ranks direct geography, component, sector, group, institution, system, and mediator matches above broad national matches;
3. ranks Role A and Role B evidence above generic Role C evidence;
4. retains enough Role C evidence to support material climate pressures;
5. favors records with stronger project-signal coverage and traceable support;
6. applies a small freshness preference only within otherwise similar evidence;
7. enforces source and pathway diversity; and
8. uses stable record IDs as the final deterministic tie-break.

Pure physical-baseline records may occupy no more than two of twelve selected slots when higher-relevance Role A or Role B evidence is available.

### 8.3 Bounds

- Bank packet: target 8 records, maximum 12 records, and a hard maximum of
  6,000 characters.
- Live-research enrichment: target 4 accepted claims, maximum 6.
- Combined external grounding: hard maximum of 12,000 characters.
- Long dossiers are never injected into runtime prompts.
- The existing climate-native Stage 2 output limit remains unchanged.

If a selected record must be shortened, the runtime packet uses a pre-approved compact evidence statement rather than generating a new summary.

## 9. Live Research and Merge Rules

Live Climate research remains part of every Climate run. Its role is to find:

- current conditions;
- recent shocks, displacement, or operational constraints;
- finer subnational evidence;
- project-sector-specific developments; and
- important gaps not covered by the structural bank.

The grounding merger:

- keeps bank and live records separately identifiable;
- removes exact duplicates;
- preserves conflicting findings as uncertainty;
- prefers live evidence for current facts when the live source is accepted;
- does not let live search silently replace structural vulnerability or capacity analysis;
- retains source and evidence IDs; and
- emits the grounding state: `bank+research`, `bank-only`, `research-only`, or `thematic-only`.

Live search failure is never a reason to suppress an otherwise valid Climate assessment.

## 10. Runtime Data Flow

```text
Project document
    |
    v
Existing Stage 1 country, sector, and project signals
    |------------------------------------|
    v                                    v
Local bank lookup and selection          Existing live Climate research
    |                                    |
    |-------------------|----------------|
                        v
               Bounded grounding merger
                        |
                        v
        Existing dedicated climate-native Stage 2
                        |
                        v
          Validated canonical Climate assessment
                        |
                        v
            Climate Stage 3 priorities and exports
```

Bank lookup and deterministic selection are local and should complete before the live pass. They do not consume the Stage 1 provider-call budget.

During the South Sudan pilot, bank selection is enabled only when
`country_scope == "single"` and the resolved analysis state contains exactly one
country. A multi-country or regional operation receives a typed
`bank_scope_unsupported` warning and continues through the existing live-research
and thematic paths. Bank-backed multi-country selection requires a later design
that can allocate the shared packet across countries and cross-border pathways
without allowing the first country to dominate.

## 11. Failure and Degradation Behavior

| Condition | Behavior |
|---|---|
| Bank available and live research succeeds | Full merged grounding |
| Bank available and live research fails | Complete assessment from bank, thematic knowledge, and project document; visible bank-only note |
| Country absent from bank and live research succeeds | Research, thematic knowledge, and project document; visible research-only provenance |
| Country absent and live research fails | Thematic knowledge and project document; visible country-evidence limitation |
| One invalid bank record | Reject the record, log the record ID and reason, continue |
| Release structurally invalid or incompatible | Reject the release, log typed failure, continue without the bank |
| Release stale but compatible | Warn; use only records still approved under the release policy |
| Selection exceeds bounds | Deterministically retain the highest-ranked diverse records |
| Primary diagnostic complete | Accept without recovery |
| Primary diagnostic incomplete | Use existing bounded field repair; never regenerate valid fields |

Typed, low-cardinality states include:

- `bank_missing`;
- `bank_incompatible`;
- `bank_record_invalid`;
- `bank_country_unavailable`;
- `bank_scope_unsupported`;
- `research_empty`;
- `research_timeout`;
- `provider_529`;
- `diagnostic_incomplete`;
- `recovery_timeout`; and
- `assessment_complete`.

Logs include the assessment ID, bank content version, country ISO code, selected-record count, packet character count, research status, and final grounding state. They do not log project text or full evidence content.

## 12. Testing and Acceptance

### 12.1 Bank Repository

- Schema validation for sources, evidence, pathways, reviews, and releases.
- Cross-reference validation for source and evidence IDs.
- Locator and required-metadata checks.
- Deterministic release generation.
- Rejection of model self-citation and unsupported `general-knowledge` sources.
- Dossier generation from structured records only.
- Approved-country-only runtime release.

### 12.2 FCV-AGENT Unit and Contract Tests

- Exact country, ISO, alias, and unknown-country lookup.
- Deterministic selection and stable tie-breaking.
- Project-signal changes produce different selected packets.
- Role A and Role B evidence are not crowded out by physical-baseline records.
- Record-count, character, and combined grounding bounds.
- Source and evidence provenance survive merge and rendering.
- All four grounding states.
- Invalid record isolation.
- Missing or incompatible bank fallback.
- Complete primary diagnostic skips recovery.
- Express and step-by-step parity.
- Standard non-Climate routes remain unchanged.
- No restricted OPCS path is read.

### 12.3 South Sudan Live Acceptance

Using the existing South Sudan PCN:

- the bank packet contains project-relevant rather than generic country evidence;
- the assessment completes when live research is deliberately unavailable;
- successful live research adds current or finer-grained evidence without displacing structural analysis;
- the primary climate diagnostic completes without routine recovery;
- visible and exported provenance match the actual grounding state;
- the assessment remains conditional about causal claims;
- runtime stays within current timeout boundaries; and
- the standard FCV route remains unaffected.

Stop after one failed live verification. Record the evidence before changing code or prompts.

## 13. Rollout

### Phase 1: South Sudan Pilot

Build and review the complete evidence chain, then validate it with the existing PCN.

### Phase 2: Comparison Set

Add five countries that collectively represent:

- Sahelian conflict and resource dynamics;
- protracted displacement and institutional breakdown;
- small-island fragility;
- urban or coastal violence and climate exposure;
- cross-border or regional dynamics; and
- a country with limited direct Climate-FCV literature.

### Phase 3: FY26 FCS Coverage

Expand across the current FCS list using the reviewed workflow. FCS status, FCV Strategy analytical category, and climate evidence remain separate fields.

### Phase 4: Demand-Driven Supplement

Add non-FCS countries based on project demand or demonstrated material Climate-FCV conditions. Do not use an arbitrary ND-GAIN threshold as an automatic supplement list.

## 14. Compatibility and Parity

The bank release schema, grounding-state enum, selected-evidence packet, and any new SSE or export fields are shared contract surfaces. Record them in the local dual-build parity document once settled.

ITS/FastAPI implementation remains deferred. The Render path must continue without the bank, allowing the companion build to adopt the contract later without blocking this pilot.

`main` remains the clean ITS-aligned baseline. Implementation continues on `feat/climate-country-bank`.

## 15. Rejected Alternatives

- **One model-generated summary per country:** insufficient provenance and poor project-level selection.
- **Inject the full 8-12 page dossier:** recreates attention and prompt-size pressure.
- **Use live research as a mandatory gate:** preserves the current reliability failure.
- **Add a required curator model call:** adds latency and another provider failure point.
- **Make detailed projections the centre of the bank:** misaligns with the module's vulnerability, capacity, and mediated-pathway purpose.
- **Generate 50-60 countries before review:** hides schema and quality problems at scale.
- **Store production content only in a 1 MB secret file:** creates an unnecessary storage constraint for public-source material.

## 16. Implementation-Plan Consequence

The next implementation plan must replace, not execute, the existing 792-line plan. In particular:

- remove the redundant dedicated-prompt Tasks 5 and 6;
- replace the simple profile JSON with the source/evidence/pathway/release model;
- add the public companion-repository workflow;
- implement deterministic runtime selection;
- make live research non-fatal;
- preserve the existing climate-native prompt and recovery contracts;
- implement the South Sudan pilot before wider generation; and
- retain TDD, route parity, prompt bounds, observability, and full-suite verification.
