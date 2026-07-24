# Sector-Lens Platform Reference

The sector-lens platform overlays optional specialist analysis on the common FCV assessment. It does not add a score, change the rating denominator, or create a second recommendation list. The production catalogue includes the approved manual-only Climate-FCV Lens.

## Module package

Each direct child of `sector_lenses/modules/` is a versioned module with:

- `manifest.yaml`: identity, status, `activation`, aliases, detection signals, declared `readout_sections`, stage budgets, and stage instructions.
- `questions.yaml`: conditional Stage 2 questions, source IDs, priority, and explicit core mappings.
- `guidance.md`: distilled synthesis guidance.
- `sources.yaml`: stable source IDs, titles, citations, and optional URLs.
- optional `source_notes/`: SME distillation notes; these are never read into runtime prompts.

The loader uses `yaml.safe_load`. Invalid packages are quarantined in registry diagnostics and cannot break core screening. Valid mappings are `ost:1` through `ost:12`, `dnh:1` through `dnh:9`, and `shift:A` through `shift:D`. Module budgets cannot exceed 600 / 2,000 / 900 estimated tokens for Stages 1 / 2 / 3.

## Selection and detection

`GET /api/sector-lenses` returns enabled selector metadata, including activation and readout declarations. `/api/detect-document-type` also returns ranked `lens_suggestions` for `suggested` modules. Modules with `activation: manual`, including Climate, are never auto-suggested or preselected. Detection or extraction failure returns an empty list and never blocks manual selection.

Clients send ordered `active_lenses` (maximum two) and optional `lens_versions`. Array order is primary then secondary. The server drops unknown or disabled IDs with `lens_warnings`, enforces the limit, and always resolves the authoritative installed version. Saved sessions use version 3; older sessions load as core-only. An incomplete version-3 run whose module version changed must restart at Stage 1.

## Stage contract

`build_lens_stage_context()` is used by both Express and Step-by-Step paths.

- Stage 1 injects evidence requests and research intents. The model emits hidden JSON between `%%%LENS_EVIDENCE_START%%%` and `%%%LENS_EVIDENCE_END%%%`. Climate-active runs also execute a dedicated bounded trusted-source research pass and one narrower retry; normalized `ClimateResearchBundle` claims join Stage 1 and Stage 2 context without changing core-only research.
- Stage 2 injects distilled guidance, applicable questions, and bounded normalized Climate claims. The model emits JSON between `%%%LENS_DIAGNOSTIC_START%%%` and `%%%LENS_DIAGNOSTIC_END%%%`, with `lenses[]` and `findings[]`. Climate interaction entries contain stable project-specific `pathways` for both fixed directions. Each pathway includes pressure, mechanism, project implication, design response, project/location/group/system anchors, time horizons, research claim IDs or an evidence gap, and confidence. Lens entries also include `materiality_summary`, `analysis_emphasis`, `readout_sections`, and `other_pathways`; undeclared or generic entries are dropped. Findings include deterministic `finding_id` values plus `lens_ids`, evidence, status, source IDs, core mappings, mechanism, geography, and action target.
- Before Stage 3, findings are merged when mappings, mechanism, geography, and action target match. Contributing lens and source IDs are retained.
- Stage 3 integrates findings into the opening assessment, operational context, two-way risk narrative, strengths, gaps, and existing priority set. Climate compaction prioritizes both directional pathways and recognized dividend IDs within the 900-token platform ceiling. Every priority in a valid Climate-active run carries validated `climate_links`; affected priorities derive `lens_ids` and `lens_relevance` from recognized diagnostic IDs. No separate score or recommendation set is permitted.

One lens may use its module allowance up to the platform ceiling. With two lenses, the platform budget is split two-thirds to the primary lens and one-third to the secondary lens. Questions are included in priority order, as whole blocks, and reported as truncated when they cannot fit.

Hidden blocks are removed from displayed prose. An invalid Climate diagnostic triggers one bounded structured recovery attempt; terminal failure retains the core assessment and suppresses unvalidated Climate claims. Stage 2 renders materiality, declared readouts, and compact other pathways. Climate-active Stage 3 renders two stacked directional narratives, causal strips, time-horizon badges, qualitative dividend synthesis, and priority contribution panels. Live HTML, shared HTML, and DOCX use the same validated structures.

**Diagnostic completeness (v9.20).** A Climate diagnostic is *usable* when it has materiality plus one interaction pathway, and *complete* when it additionally carries at least one grounded reflection and a non-empty `integration_summary` (`climate_readout_is_complete()`). Recovery fires on either a hard failure or a usable-but-incomplete readout, and the bounded recovery request asks for the full dedicated-module contract (`reflections`, `integration_level`, `integration_summary`, `less_central`, `sensitivity_evidence`, `responsiveness_evidence`). A usable primary is never downgraded: a recovered diagnostic is adopted only when the primary was unusable or the recovery is complete. When a usable readout is still incomplete after recovery, the module notice (frontend, shared HTML, and DOCX) shows an honest partial notice rather than silently omitting the reflections/integration sections. `_stream_stage` records the provider `stop_reason` so a climate-active Stage 2 `max_tokens` truncation is logged.

## Climate-FCV Lens

Selection is explicit, but screening after selection is automatic across climate-intent and wider development operations. Adaptation, resilience, and climate-risk management are primary; deep mitigation or transition analysis requires a clear material pathway. Dividend items require a mechanism, material relevance, and practical action. The eight fixed source IDs are `peace-social-dividends`, `ccdr-fcv-approach`, `fcv-climate-compendium`, `defueling-conflict`, `defueling-field-notes`, `adelphi-conflict-sensitivity`, `cgiar-climate-security`, and `adaptation-review`.

Optional CCDR material may enter as `context-ccdr` only with a validated World Bank HTTPS URL. Dedicated research sources use allowlisted trusted types and HTTPS hosts. CCDR evidence remains contextual rather than project evidence, retrieval failure is non-blocking, and it must not become a routine recommendation. Core-only runs retain the existing lightweight Climate-FCV check and 4-5 substantive priorities. Active Climate supersedes that check without duplication and uses one list of no more than five substantive priorities with a flexible, non-quota core/Climate/blended mix.

Valid interaction directions are `climate-fcv-on-project` and `project-on-climate-fcv`. Valid horizons are `current-near-term`, `project-lifetime`, and `asset-system-lifetime`. Standard dividend pathway IDs equal their declared item IDs; additional pathway IDs use `additional-{section_id}-1|2`. Climate priority links use `linked` or `no-material-pathway`. Linked records require a recognized interaction, dividend, or finding ID plus `contribution` and `strengthening_effect`; no-material records require empty ID arrays and a concrete core-FCV reason.

## Compatibility contract

The Flask and private FastAPI builds must keep these fields and delimiters aligned:

- request/session/report: `active_lenses`, `lens_versions`, `lens_context_sources`, saved-session version 3;
- metadata: `lens_suggestions`;
- catalogue: `activation`, `readout_sections`;
- SSE: `active_lenses`, `lens_warnings`, `lens_diagnostic`, `lens_context_sources`;
- Stage 3 priority: `lens_ids: string[]`, `lens_relevance: string`, and additive `climate_links` with status, interaction/dividend/finding IDs, contribution, strengthening effect, and reason;
- Climate research: normalized `sources`, project-specific `claims`, confidence, evidence status, and the three horizon enums;
- Climate diagnostic: stable pathway and finding IDs plus the causal pathway fields described above;
- hidden delimiter names and diagnostic status/core-mapping enums.

Raw literature and source notes are never injected at runtime.

*Last updated: 2026-07-24 — v9.20 diagnostic completeness (reflections + integration), recovery-prompt parity, no-downgrade adoption, honest partial notice, and stop_reason truncation logging.*
