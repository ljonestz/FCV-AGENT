# Country bank production preparation plan

Approved scope: the staged approach in `20261026_country-bank-approval-readiness.md`. Execute inline in the existing isolated worktree. No country approval, paid model call or deployment is implied.

## Loader and freshness

Execution status: loader/freshness implementation, regression checks and the first-wave review packet are complete. The checklist below preserves the original plan; detailed results and qualifications are in `20261026_country-bank-production-handoff.md`. Substantive evidence approval, candidate corrections, release promotion and live acceptance remain pending.

- [ ] Add failing synthetic contract tests in `tests/test_climate_bank_production.py` for approved 1.1 loading/materialization, approval enforcement, candidate opt-in, unknown schemas, required metadata, current-record expiry, dependent pathways, structural fallback and grounding limitations.
- [ ] Run `python -m pytest tests/test_climate_bank_production.py -q -p no:cacheprovider`; confirm failures are the missing behaviors.
- [ ] In `sector_lenses/climate_bank.py`, accept approved 1.1 only with `candidate: false`, keep 1.0 compatibility and candidate-preview opt-in. Pass schema separately from `allow_reviewed` into evidence validation. Reject selected expired current records including pathway support. Compute omissions from canonical server data.
- [ ] In `sector_lenses/climate_bank_selector.py`, exclude expired current evidence and dependent pathways before ranking. Preserve valid structural records. Return `bank_content_expired` if expiry leaves no selectable records. Include the canonical omission limitation in compact packets.
- [ ] In `sector_lenses/climate_grounding.py`, retain that limitation in bounded model grounding. Keep the existing 6,000/12,000-character budgets and model-call behavior.
- [ ] Preserve the same limitation through `sector_lenses/climate_context_adapter.py` in the existing `ContextEvidenceRef.evidence_gap` field for the verified pipeline. The compact prompt is used by the older route; checking it alone is insufficient.
- [ ] Run new tests and existing bank, selector and grounding tests. Then run the full offline suite, reporting environment failures separately.

## First wave review

- [ ] Prepare a version-bound, source-linked review packet for SSD, BFA, HTI, PNG, UKR and YEM from the pinned candidate files. Include exact record IDs, statements, uncertainty, locators, profile/pathway references and unresolved review decisions. Do not renew dates or set approved status.
- [ ] Check public source passages for selected consequential claims and record precisely which records were checked. Leave unchecked records explicitly pending; tests are not evidence approval.
- [ ] Record the included-file hashes so later corrections invalidate this review scope. Preserve previous releases.

## Handoff

- [ ] Inspect the actual diff, record checks and remaining limitations, commit only intended files, push the branch and open a review PR. Record shared runtime semantics in the local parity log without publishing private material.
- [ ] Request designated human evidence sign-off against the frozen packet before promotion. Identify any additional source corrections before asking for approval. Verify production service/configuration and obtain a specific paid-run allocation before live acceptance; deployment requires an exact tested-release decision.

The change reuses existing loaders, selectors, fixtures and release tooling. It adds no dependencies, provider calls or data-status automation. The prior July South Sudan release remains supported for rollback.
