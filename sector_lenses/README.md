# Sector lens packages

The production `modules/` directory is intentionally empty. Add a module only after its literature, detection rules, questions, mappings, and recommendations have been approved.

Use this structure:

```text
modules/<lens-id>/
├── manifest.yaml
├── questions.yaml
├── guidance.md
├── sources.yaml
└── source_notes/        # optional; never loaded into prompts
```

Minimal `manifest.yaml`:

```yaml
id: example
name: Example Lens
version: 1.0.0
description: What this lens adds to the common FCV assessment.
status: disabled
aliases: [example sector]
detection:
  keywords: [example activity]
  sector_codes: [EX]
  threshold: 2
compatibility:
  compatible_with: ['*']
  incompatible_with: []
budgets:
  stage1: 100
  stage2: 600
  stage3: 150
stage_instructions:
  stage1: Identify material evidence needs.
  stage2: Apply approved conditional questions.
  stage3: Integrate mapped findings into existing priorities.
```

`questions.yaml` entries require stable IDs, question text, declared source IDs, and one or more explicit core mappings (`ost:1..12`, `dnh:1..9`, or `shift:A..D`). Optional `priority` values determine which questions fit first when two lenses share the Stage 2 budget.

See `tests/fixtures/sector_lenses/test-agriculture/` for a test-only example and `docs/reference/reference_sector_lenses.md` for the full runtime contract.
