# Sector lens packages

The production `modules/` directory contains the approved manual-only Climate-FCV Lens. Add another module only after its literature, activation behavior, detection rules, questions, mappings, readouts, and recommendations have been approved.

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
activation: suggested  # or manual
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
readout_sections:
  - id: invest-in
    title: What the project may invest in
    item_ids: [social-cohesion-inclusion]
```

`questions.yaml` entries require stable IDs, question text, declared source IDs, and one or more explicit core mappings (`ost:1..12`, `dnh:1..9`, or `shift:A..D`). Optional `priority` values determine which questions fit first when two lenses share the Stage 2 budget.

`manual` modules never appear in automatic suggestions. Stage 2 output may use declared `readout_sections`; undeclared section and item IDs are discarded. Dynamic sources such as the Climate lens's `context-ccdr` are validated separately and never expand the fixed runtime literature.

See `tests/fixtures/sector_lenses/test-agriculture/` for a test-only example, `modules/climate/` for the approved production package, and `docs/reference/reference_sector_lenses.md` for the full runtime contract.
