# Climate Verified Operational Routing Implementation Plan

1. Add failing tests for authoritative document-context resolution, DPF/PforR/IPF/MPA differentiation, multi-country detection, and instrument-specific preparation dates.
2. Implement a typed server-side verified-operation context resolver and run it before research planning and country-bank selection.
3. Pass the resolved context through the verified runtime and pipeline prompts/output.
4. Replace unknown-instrument IPF inheritance with fail-closed guidance selection; add PforR, DPF, new-model IPF, and MPA program-layer guidance.
5. Add an operational-routing block to full and summary readers, with explicit unresolved-context copy.
6. Update repository architecture/reference documentation and the local dual-build parity log where shared contracts are affected.
7. Run focused tests, the climate bank suite, and the smallest practical broader suite; inspect the final diff before commit and push.
