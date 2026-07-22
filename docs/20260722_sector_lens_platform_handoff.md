# Sector-Lens Platform and Climate-FCV Lens Handoff

**Date:** 22 July 2026
**Repository:** `ljonestz/FCV-AGENT`
**Branch:** `codex/sector-lens-platform`
**Worktree:** `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\sector-lens-platform`
**Remote branch:** `origin/codex/sector-lens-platform`
**Completed implementation HEAD:** `3cd1bf1` (`fix: preserve mandatory priority exceptions`)
**Handoff commit:** the commit containing this file; confirm with `git log -1 --oneline`

## 1. Purpose of the branch

This branch implements a reusable optional sector-lens platform and the first production module, the Climate-FCV Lens. The lens supplements the common FCV assessment without adding a score, changing the rating denominator, or creating a parallel recommendation list.

The approved design and task-level implementation details remain authoritative:

- `docs/superpowers/specs/2026-07-21-climate-fcv-lens-design.md`
- `docs/superpowers/plans/2026-07-21-climate-fcv-lens.md`

The implementation plan's Markdown checkboxes were not edited during execution. All Tasks 1-9 were completed despite those boxes remaining unchecked.

## 2. Non-negotiable design decisions

- Climate is selected manually and is never auto-suggested or preselected.
- After selection, Climate screens both climate-intent operations and wider development projects automatically.
- Core-only behavior remains unchanged: the normal 4-5 substantive priorities and the existing lightweight conditional `Climate-FCV Nexus` check remain in place.
- Active Climate supersedes the lightweight check and must not create duplicate Climate findings.
- Adaptation, resilience, and climate-risk management are primary. Deep mitigation or transition analysis requires a clear material pathway.
- Peace and social dividends require a credible mechanism, material relevance, and a practical action. Only relevant dividend items are foregrounded.
- Active-lens output uses one integrated list with no more than five substantive priorities. The core/Climate/blended mix is flexible and evidence-led, not a quota.
- Mandatory Gender-FCV and SEA/SH standalone cards remain exceptions to the five-substantive-priority ceiling.
- CCDR material is optional, validated contextual evidence. It must not dominate the assessment or become a routine recommendation.
- All lens findings map to existing OST, Do No Harm, or FCV Strategy criteria and do not independently rescore them.

## 3. What was implemented

### Platform contracts

- Typed `activation` metadata with `suggested` and `manual` modes.
- Manual modules remain visible in the catalogue but are excluded from deterministic suggestions.
- Typed, registry-declared `readout_sections` and allowed item IDs.
- Hidden Stage 1 evidence and Stage 2 diagnostic delimiters with defensive normalization.
- Ordered selection of up to two lenses, server-authoritative versions, compatibility checks, and bounded stage budgets.
- Provenance fields on priorities: `lens_ids` and `lens_relevance`.
- Dynamic context contract: `lens_context_sources` across request, SSE, session/checkpoint, and report payloads.

### Climate-FCV module

The production module is under `sector_lenses/modules/climate/` and contains:

- a manual, enabled manifest;
- 19 mapped questions across the approved pathway families;
- bounded stage guidance;
- eight fixed, traceable source IDs;
- eight audit-only source notes that never enter runtime prompts;
- two readout sections: `invest-in` and `deliver-through`.

The eight fixed source IDs are:

1. `peace-social-dividends`
2. `ccdr-fcv-approach`
3. `fcv-climate-compendium`
4. `defueling-conflict`
5. `defueling-field-notes`
6. `adelphi-conflict-sensitivity`
7. `cgiar-climate-security`
8. `adaptation-review`

### Optional CCDR context

- The existing FCV research call is extended only when Climate is active and no uploaded CCDR is already present.
- Core research keeps four searches; Climate-enabled research permits five within the same call.
- `context-ccdr` requires a World Bank HTTPS host and bounded metadata.
- Failed retrieval is non-blocking, and core and CCDR-enriched cache entries are separate.

### User experience and reports

- Selector copy explicitly states that Climate is not selected automatically.
- Selection locks when analysis starts.
- Stage 2 renders materiality, emphasis, declared invest/deliver items, evidence gaps, trade-offs, and compact other pathways.
- Empty and `not_applicable` sections are suppressed.
- Stage 3 integrates Climate into the opening, operational context, two-way risks, strengths, gaps, and one priority list.
- Priority badges use trusted catalogue names rather than raw IDs.
- DOCX reports include a Climate-FCV readout and a source/evidence appendix with validated country context.
- Version 3 sessions and Express checkpoints preserve active versions, diagnostics, and CCDR context; stale versions force a Stage 1 restart.

## 4. Important implementation locations

| Area | Files |
|---|---|
| Registry and typed contracts | `sector_lenses/models.py`, `sector_lenses/registry.py`, `sector_lenses/composer.py` |
| Hidden diagnostics and normalization | `sector_lenses/pipeline.py` |
| Dynamic CCDR validation | `sector_lenses/context.py` |
| Climate package | `sector_lenses/modules/climate/` |
| Workflow, prompts, Stage 3 parsing, DOCX | `app.py` |
| Selector, readout, persistence, badges | `index.html` |
| Public contract reference | `docs/reference/reference_sector_lenses.md` |
| Module authoring guidance | `sector_lenses/README.md` |

## 5. Commit sequence

The platform baseline was audited and committed separately before Climate implementation.

| Commit | Purpose |
|---|---|
| `6c5d138` | Sector-lens platform baseline |
| `d10115a` | Manual activation metadata |
| `016ad35` | Generic diagnostic readouts |
| `6f5252d` | Literature-backed Climate-FCV module |
| `768a6fa` | Defensive readout parsing review fix |
| `36a0021` | Optional CCDR context |
| `16fffbd` | Materiality and dividend stage contracts |
| `6ce4a93` | Climate diagnostic frontend readout |
| `c9e77be` | Stage 3 Climate integration and flexible priority mix |
| `668afe3` | Climate DOCX readout and appendix |
| `4795c81` | Public contract documentation |
| `f44bbdb` | Output-bound and scalar-input review fixes |
| `3cd1bf1` | Mandatory standalone-card exception preservation |

## 6. Verification and review state

Final post-review verification at `3cd1bf1`:

```powershell
pytest -q -p no:cacheprovider tests
# 263 passed

node tests/test_frontend_storage_helpers.js
# frontend storage helper tests passed
```

Focused Climate/platform verification passed 53 tests after review fixes. Local headless-browser smoke checks also passed for:

- Climate visible and initially unselected;
- no Climate suggestion badge;
- manual selection and lock-on-start behavior;
- material readout rendering;
- empty delivery-section suppression;
- `not_applicable` readout suppression;
- CCDR context checkpoint persistence;
- no browser page errors.

The final full-branch review was clean after two review-fix commits. The last correction ensures active-lens output retains no more than five substantive priorities while preserving mandatory Gender-FCV and SEA/SH standalone exceptions.

## 7. Cross-build parity and restrictions

The shared contract update was recorded in the private parity file:

`C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`

It records `activation`, `readout_sections`, `lens_context_sources`, the extended Stage 2 diagnostic, priority behavior, and validated `context-ccdr`. Do not copy private internal-build infrastructure into public repository files.

The raw restricted OPCS corpus remains out of scope and was not accessed. Continue to follow the access restriction in the private parity guidance.

## 8. Current repository state

- The branch is pushed and tracks `origin/codex/sector-lens-platform`.
- No pull request has been created.
- The branch has not been merged.
- The worktree was clean at handoff creation before this document was added.
- No raw literature, credentials, or generated cache artifacts were intentionally added.

## 9. Startup instructions for the next LLM session

Use the existing worktree and branch. Do not create another branch or worktree unless explicitly directed.

1. Read applicable `AGENTS.md`, repository `claude.md`, and `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`.
2. Read this handoff, then the approved design and implementation plan linked in Section 1.
3. Run:

   ```powershell
   git status --short --branch
   git log -5 --oneline
   pytest -q -p no:cacheprovider tests
   node tests/test_frontend_storage_helpers.js
   ```

4. Treat the implementation as complete unless a new request identifies a defect or changed requirement. Do not restart Tasks 1-9 because the plan checkboxes are still unchecked.
5. Preserve core-only prompt behavior when changing lens code.
6. Log any shared contract change in the private parity file.
7. Do not merge or open a pull request without explicit direction.

## 10. Reasonable next steps, only if requested

- Open a draft pull request for review.
- Run a real end-to-end Climate assessment with representative project documents and external model calls.
- Mirror shared contracts into the private FastAPI build.
- Address review feedback or refine the Climate evidence/readout design based on user testing.
- Add a second sector lens only through a separately approved design and literature review.
