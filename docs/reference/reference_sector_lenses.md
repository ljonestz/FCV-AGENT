# Sector-Lens Platform Reference

The sector-lens platform overlays optional specialist analysis on the common FCV assessment. It does not add a score, change the rating denominator, or create a second recommendation list. The production catalogue is intentionally empty until a content module is separately approved.

## Module package

Each direct child of `sector_lenses/modules/` is a versioned module with:

- `manifest.yaml`: identity, status, aliases, detection signals, stage budgets, and stage instructions.
- `questions.yaml`: conditional Stage 2 questions, source IDs, priority, and explicit core mappings.
- `guidance.md`: distilled synthesis guidance.
- `sources.yaml`: stable source IDs, titles, citations, and optional URLs.
- optional `source_notes/`: SME distillation notes; these are never read into runtime prompts.

The loader uses `yaml.safe_load`. Invalid packages are quarantined in registry diagnostics and cannot break core screening. Valid mappings are `ost:1` through `ost:12`, `dnh:1` through `dnh:9`, and `shift:A` through `shift:D`. Module budgets cannot exceed 600 / 2,000 / 900 estimated tokens for Stages 1 / 2 / 3.

## Selection and detection

`GET /api/sector-lenses` returns enabled selector metadata. `/api/detect-document-type` also returns ranked `lens_suggestions`; suggestions at or above a module's materiality threshold are preselected, while uncertain matches remain unselected. Detection or extraction failure returns an empty list and never blocks manual selection.

Clients send ordered `active_lenses` (maximum two) and optional `lens_versions`. Array order is primary then secondary. The server drops unknown or disabled IDs with `lens_warnings`, enforces the limit, and always resolves the authoritative installed version. Saved sessions use version 3; older sessions load as core-only. An incomplete version-3 run whose module version changed must restart at Stage 1.

## Stage contract

`build_lens_stage_context()` is used by both Express and Step-by-Step paths.

- Stage 1 injects only evidence requests and research intents. The model emits hidden JSON between `%%%LENS_EVIDENCE_START%%%` and `%%%LENS_EVIDENCE_END%%%`.
- Stage 2 injects distilled guidance and applicable questions. The model emits JSON between `%%%LENS_DIAGNOSTIC_START%%%` and `%%%LENS_DIAGNOSTIC_END%%%`, with `lenses[]` and `findings[]`. Findings include `lens_ids`, `evidence`, `status`, `source_ids`, `core_mappings`, `mechanism`, `geography`, and `action_target`.
- Before Stage 3, findings are merged when mappings, mechanism, geography, and action target match. Contributing lens and source IDs are retained.
- Stage 3 integrates findings into the existing priority set. Affected priorities may carry `lens_ids` and `lens_relevance`; no separate score or recommendation set is permitted.

One lens may use its module allowance up to the platform ceiling. With two lenses, the platform budget is split two-thirds to the primary lens and one-third to the secondary lens. Questions are included in priority order, as whole blocks, and reported as truncated when they cannot fit.

Hidden blocks are removed from displayed prose. Stage 2 renders the parsed diagnostic. Stage 3 renders provenance badges. DOCX downloads append source and evidence details.

## Compatibility contract

The Flask and private FastAPI builds must keep these fields and delimiters aligned:

- request/session: `active_lenses`, `lens_versions`, saved-session version 3;
- metadata: `lens_suggestions`;
- SSE: `active_lenses`, `lens_warnings`, `lens_diagnostic`;
- Stage 3 priority: `lens_ids: string[]`, `lens_relevance: string`;
- hidden delimiter names and diagnostic status/core-mapping enums.

Raw literature must not be injected at runtime. The existing Climate-FCV prompt check remains unchanged until the Climate lens specification is approved.
