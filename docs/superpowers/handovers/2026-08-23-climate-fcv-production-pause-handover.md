# Climate and FCV Production Alignment - Pause Handover

**Paused:** 2026-08-23  
**Reason:** User requested a clean handover for a later Codex session.  
**Implementation status:** Incomplete and intentionally uncommitted. Do not describe the branch as production-ready.

## Repository state

- Repository: `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT`
- Active worktree: `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-summary-direct`
- Branch: `codex/climate-summary-quality-fixes`
- Current HEAD: `c1617e5 docs: plan climate fcv summary production alignment`
- Design commit: `a2b578b docs: design climate fcv summary production alignment`
- Remote branch remains at `5284659 fix: align climate reader unresolved routes`
- Nothing from the current implementation attempt has been committed or pushed.

The approved documents are:

- `docs/superpowers/specs/2026-08-23-climate-fcv-summary-extraction-production-design.md`
- `docs/superpowers/plans/2026-08-23-climate-fcv-summary-extraction-production.md`

## User-approved outcome

The implementation should eventually deliver all of the following:

1. A dedicated two-to-three-paragraph Climate Summary synthesis, distinct from the Detailed executive readout.
2. Bold first sentence in each Climate Summary paragraph.
3. Climate Summary disclosures for “What to keep an eye on” and “Relevant WBG guidance for this project.”
4. Distinct Detailed bands for decision preparation and further guidance.
5. Suggested drafting in Climate Summary and Detailed whenever the current document route is safely resolved.
6. Only source-supported standard guidance-purpose sentences; remove unreliable generated project-specific follow-up sentences.
7. A conditional main-FCV “What to keep an eye on” disclosure, while preserving its existing strong concise narrative and per-priority guidance pattern.
8. One shared DOCX extraction path that handles content controls, nested tables, structured metadata, and checked versus unchecked options for both Climate and main FCV.
9. Fresh South Sudan PCN smoke, full-browser screenshots, shareable offline HTML, full tests, deployment, and deployed smoke before any production-readiness claim.

## Current uncommitted files

Tracked modifications:

- `app.py`
- `sector_lenses/climate_source_blocks.py`
- `sector_lenses/climate_verified_runtime.py`
- `tests/test_climate_verified_runtime.py`

Untracked task files:

- `docx_structure.py`
- `tests/test_docx_structure.py`

Pre-existing untracked `.pytest_tmp_*` directories are still present. They were not created for this handover and must not be deleted casually.

## Work completed so far

### Shared DOCX walker

`docx_structure.py` currently provides an immutable `DocxUnit` and a recursive OOXML walker. It is wired into:

- `app.extract_docx_text()` while preserving the public `(text, part_count)` return contract;
- `sector_lenses.climate_source_blocks.build_docx_blocks()` for stable evidence blocks.

Implemented behavior includes:

- traversal through `w:sdtContent`;
- nested-table traversal;
- visible-text filtering for hidden runs, field instructions, and deleted text;
- suppression of unchecked Word checkbox controls and `[ ]` options;
- retention of checked controls and `[x]` options;
- stable locations and block IDs;
- same-row structured label/value pairing.

The following focused command passed before the later real-template regression was added:

```powershell
python -m pytest tests/test_docx_structure.py tests/test_climate_source_blocks.py -q
```

Result at that checkpoint: `11 passed`.

### Structured instrument routing

`sector_lenses/climate_verified_runtime.py` and `tests/test_climate_verified_runtime.py` currently add:

- precedence for one explicit `Financing Instrument: ...` source block over incidental narrative mentions;
- fail-closed `Unknown` behavior with `INSTRUMENT_STRUCTURED_CONFLICT` for incompatible labelled values;
- a regression proving `Environmental and Social Risk Classification: Substantial` does not itself determine the E&S framework route;
- non-sensitive `instrument_structured:<instrument>` evidence notes.

The combined focused command passed before the real-template header/value-row issue was addressed:

```powershell
python -m pytest tests/test_climate_verified_runtime.py tests/test_docx_structure.py tests/test_climate_source_blocks.py -q
```

Result: `31 passed`.

Note for review: `_structured_financing_instruments()` was inserted near the end of `climate_verified_runtime.py`, after its call site. This is valid at runtime after module import, but should be moved beside `_primary_context_text()` before final acceptance for readability.

## Real South Sudan PCN finding

Test document:

`C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.superpowers\brainstorm\Southsudan\Project Concept Note (PCN)_Draft_15_June 2026.docx`

The first real-document smoke found a table pattern not covered by the original synthetic fixture:

- row 1 contains three headers: Operation ID, Financing Instrument, Environmental and Social Risk Classification;
- row 2 contains the corresponding values: P511185, Investment Project Financing (IPF), Substantial.

The current walker incorrectly emits `Operation ID: Financing Instrument`, then emits the values separately. The operation still resolves to IPF and `is_mpa=False` through narrative heuristics, but this is not acceptable because the structured metadata is not preserved correctly.

A new regression was added:

```powershell
python -m pytest tests/test_docx_structure.py::test_header_row_followed_by_value_row_preserves_each_structured_pair -q
```

Current result: **RED**, one failure. Actual fields contain only `Operation ID: Financing Instrument`; expected all three correct pairs.

## Pending patch - deliberately not applied

The implementation patch for header-row/value-row pairing was authored but not applied because the user requested a pause:

`C:\Users\wb559324\.codex\visualizations\2026\08\22\01a0287e-d676-7653-a10d-d9e839d41965\task1a-header-values-runtime.patch`

Resume with inspection first, then:

```powershell
git apply --recount --check "C:\Users\wb559324\.codex\visualizations\2026\08\22\01a0287e-d676-7653-a10d-d9e839d41965\task1a-header-values-runtime.patch"
git apply --recount "C:\Users\wb559324\.codex\visualizations\2026\08\22\01a0287e-d676-7653-a10d-d9e839d41965\task1a-header-values-runtime.patch"
```

Then rerun the single RED test and the combined focused suite. Inspect the patch carefully for:

- exactly one emission per field;
- correct document order;
- no duplicate processing of the consumed value row;
- nested tables within either header or value cells;
- stable paragraph and table location metadata.

## Windows editing constraint

Windows Application Control blocks the normal `apply_patch` helper when it tries to update existing files inside this OneDrive reparse-point worktree. The error is:

`CreateProcessAsUserW failed: 4551 (An Application Control policy has blocked this file.)`

Creating new patch artifacts works. The safe fallback used in this session was:

1. author a unified patch artifact in the existing visualization directory;
2. inspect it;
3. run `git apply --recount --check`;
4. run `git apply --recount`.

Do not use direct PowerShell/Python source-file rewrites. GNU `patch.exe` created `.orig` and `.rej` files during one attempt; those four task-created artifacts were removed with an explicit, dry-run-confirmed `git clean`. None remain in the worktree.

## Delegation status

The following Luna xhigh agents were attempted and are now interrupted:

- `docx_extraction_impl`
- `docx_walker_impl`
- `docx_routing_impl`

They were blocked or stalled primarily by the Windows patch-helper limitation. No agent remains active. A later session should use fresh Luna xhigh agents with smaller, non-overlapping ownership after the pending table fix is integrated.

## Safe resume sequence

1. Read `CLAUDE.md`, the approved design, the approved plan, and this handover.
2. Confirm branch, worktree, `git status`, and that no unexpected user changes appeared.
3. Inspect and apply the pending header/value-row patch.
4. Run the single RED test; require it to turn GREEN.
5. Run:

   ```powershell
   python -m pytest tests/test_climate_verified_runtime.py tests/test_docx_structure.py tests/test_climate_source_blocks.py -q
   ```

6. Repeat the real South Sudan extraction smoke. Require these exact structured lines:

   - `Operation ID: P511185`
   - `Financing Instrument: Investment Project Financing (IPF)`
   - `Environmental and Social Risk Classification: Substantial`

   Also require `instrument_type='IPF'` and `is_mpa=False`. The E&S framework route may resolve from separate explicit ESF evidence, but never from the word `Substantial` alone.
7. Inspect all Task 1 diffs, run spec-compliance and code-quality reviews, fix findings, then commit Task 1 only.
8. Continue Tasks 2-4 from the implementation plan using fresh Luna xhigh agents and strict RED/GREEN checkpoints.
9. Update `CLAUDE.md`, relevant reference docs, and the private `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md` only after the final contract is known.
10. Run focused tests, full suite, fresh Climate and normal-FCV PCN runs, responsive browser QA, full-browser screenshots, shareable offline HTML verification, deployment, and deployed smoke.

## What has not started

No implementation work has started for:

- the dedicated Climate `summary_overview.paragraphs` schema/prompt/pipeline field;
- the new Climate Summary paragraph renderer;
- guidance simplification;
- the amber/teal Detailed follow-up bands;
- Climate Summary watch/guidance disclosures;
- the main-FCV watch disclosure;
- documentation/parity updates for the final contract;
- final full-suite, browser, export, deployment, or deployed smoke acceptance.

Do not skip directly to UI work: the shared extraction and real-PCN routing checkpoint must be completed and reviewed first.
