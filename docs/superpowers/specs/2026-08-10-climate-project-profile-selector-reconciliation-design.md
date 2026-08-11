# Climate Project Profile and Selector Reconciliation

**Date:** 2026-08-10
**Status:** Approved
**Branch:** `feat/climate-country-bank`
**Baseline:** deployment line through `0025511`, merged as `43b7789`

## 1. Decision

Complete the deterministic Project Climate Profile and coverage-aware bank
selection increment on top of the current verified Climate-FCV pipeline. The
public companion repository remains the sole country-bank content authority.
The reviewed South Sudan schema 1.1 candidate is the fixed content baseline for
this increment.

This design reconciles the approved 2026-08-01 South Sudan bank redesign with
the later verified-v2.1 pipeline and reader work. It does not recreate the old
flat country-profile bank or the original live generator.

## 2. Current baseline

The application already provides:

- a pinned, approved-only companion bank plus reviewed-candidate preview;
- runtime schema 1.0 and 1.1 compatibility;
- canonical-ID manifests and server-side rematerialization;
- bounded bank/live grounding with four provenance states;
- non-fatal live research and bank-only fallback;
- a verified Climate-FCV pipeline with evidence, recommendation, reader, and
  provenance gates; and
- browser, HTML, and DOCX reader parity through commit `0025511`.

The remaining weakness is project selection. It still scores unstructured
excerpt tokens and discards important geography, group, system, uncertainty,
and relevance metadata from the prompt packet.

## 3. Scope

### Included

1. A deterministic local `ProjectClimateProfile`.
2. Controlled bank-provided aliases for geography, sector, livelihood,
   institution, group, hazard, and system/asset matching.
3. Coverage-aware selection with balance, diversity, staleness, and duplicate
   controls.
4. Content-safe selection diagnostics.
5. Rich compact evidence and pathway capsules.
6. One profile and selection path shared by step-by-step and Express workflows.
7. Compatibility with the verified context-evidence adapter and reader
   provenance chain.
8. Synthetic golden fixtures for five South Sudan project archetypes.

### Deferred

- additional literature ingestion or country-bank content edits;
- candidate review or release promotion;
- additional countries or multi-country allocation;
- gap-directed live-research questions and new evidence-gate telemetry;
- any prompt, rating, recommendation, or reader redesign;
- paid model runs, Render deployment, or stable-service changes; and
- live acceptance runs unless separately authorized.

## 4. Ownership and cleanup

Country-bank content belongs only in `data/climate-fcv-country-bank`. The
temporary root-level `climate_country_bank.json`,
`climate_country_bank_data.py`, and their test are removed in a separate,
reversible commit. No reviewed companion content changes in this increment.

## 5. Project Climate Profile

Local preprocessing builds one immutable bounded profile from extracted project
text and document metadata:

- country;
- instrument and document stage;
- geographies;
- sectors and livelihoods;
- project elements;
- affected groups;
- institutions;
- systems and assets;
- document-explicit hazards;
- time horizons;
- safe signal metadata; and
- unresolved controlled signals.

Only explicit document or metadata matches become project facts. Bank-derived
candidates remain separately labelled and cannot be promoted into document
facts. Extraction makes no provider call and logs no uploaded text.

## 6. Selection

The selector matches structured profile fields rather than a raw excerpt.
Geography and named project elements receive the highest weights. It also:

- uses controlled aliases;
- balances climate pressure, vulnerability/capacity, institutional/response,
  and both pathway directions where supported;
- penalizes stale current records;
- suppresses near-duplicate claims;
- evaluates diversity across all supporting sources; and
- leaves unsupported balance classes empty rather than filling them with weak
  matches.

The selection result retains canonical evidence/pathway IDs plus bounded
diagnostics: score, matched field names, balance role, suppression reason,
staleness decision, and missing coverage classes. Diagnostics never retain
matched source text or confidential document content.

## 7. Materialization and verified-pipeline integration

Canonical records remain server-side. Prompt materialization emits whole,
compact capsules containing the minimum reasoning metadata needed by the model:
geography, groups/systems, evidence class or pathway direction, relevance,
status/strength, uncertainty, and canonical source/evidence IDs.

A selected pathway does not automatically inflate the packet with every
supporting evidence statement. Whole low-priority capsules are dropped when
needed; individual claims and uncertainty statements are never cut into
ambiguous fragments.

The existing verified adapter continues to receive full rematerialized records,
so `ContextEvidenceRef`, provenance, candidate-preview status, and reader
evidence trails remain intact.

## 8. Hard invariants

- target 8 and maximum 12 selected bank items;
- bank prompt context at most 6,000 characters;
- combined external grounding at most 12,000 characters;
- maximum 6 accepted live claims;
- no required runtime curator call;
- no weakening of source, claim-linkage, approval, or truncation gates;
- live research remains non-fatal;
- candidate preview remains visibly non-approved;
- generic FCV behavior is unchanged; and
- no confidential project text in logs, persisted diagnostics, or fixtures.

## 9. Validation

Strict TDD covers:

- profile extraction and false-positive prevention;
- schema 1.0 and 1.1 compatibility;
- alias and geography matching;
- balance, staleness, diversity, and duplicate suppression;
- deterministic results and content-safe diagnostics;
- whole-capsule character-bound behavior;
- accurate materialized item counts;
- both application workflows;
- verified-context adaptation and provenance; and
- five contrasting synthetic South Sudan project archetypes.

The phase ends with focused climate-bank/verified tests and the full local
tracked suite. No paid or live acceptance run is part of this phase.

## 10. Dual-build parity

The profile shape, diagnostic enums, schema 1.1 fields, capsule fields, and
selection semantics are shared-contract candidates. The private parity log is
updated once the contracts settle. The Render implementation remains
framework-specific; no ITS code is changed here.

## 11. Completion

This increment is complete when contrasting synthetic projects receive
materially different, explainable, balanced bank packets within existing
limits, both application workflows use the same deterministic profile, the
verified evidence chain remains intact, and all local tests pass.
