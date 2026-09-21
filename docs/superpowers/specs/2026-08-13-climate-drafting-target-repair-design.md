# Climate Drafting Target Repair Design

## Problem

Two live Mozambique preview runs generated four and five recommendation
candidates respectively, but deterministic validation rejected every candidate
with `DRAFTING_CURRENT_TARGET_INVALID`. The model-generated section labels were
not exact string matches for the bounded targets in the operational-guidance
registry. The recommendation content never reached admission or semantic review.

## Decision

Keep the bounded target registry and strict post-repair validation. Before
validation, deterministically canonicalize a non-standard current-document
section only when the drafting block cites guidance that supplies a permitted
target for the current document.

The repair will first prefer a unique, meaningful token match between the
generated section and the cited guidance's permitted sections. If one cited
guidance entry permits multiple sections and no unique match exists, it will use
that entry's first registered target. If guidance is missing, unknown, spans
multiple entries ambiguously, or supplies no current-document target, validation
will continue to reject the candidate.

## Alternatives considered

1. **Guidance-backed canonicalization (selected).** Preserves the safety boundary
   while repairing harmless section-label variation.
2. **Expand the registry with aliases.** Rejected because aliases would duplicate
   semantic routing information and require continual maintenance.
3. **Make target validation advisory.** Rejected because arbitrary drafting
   destinations could then reach the reader.

## Data flow

The verified pipeline will add the selected guidance-to-target mapping to
`DraftingValidationContext`. `normalize_drafting_blocks` will use that mapping to
repair only the current-document section. Existing validation then runs without
special exceptions. A repair action will record
`DRAFTING_CURRENT_SECTION_CANONICALIZED`.

## Verification

- A focused contract test will prove a non-canonical section is repaired.
- A negative contract test will prove unknown guidance remains blocking.
- A pipeline regression will reproduce several otherwise-valid candidates with
  non-canonical sections and require them to survive validation and admission.
- Existing drafting, verified-pipeline, and operational-guidance tests will run.
