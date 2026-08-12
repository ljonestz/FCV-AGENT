# Concise Stage 3 Readout — Implementation Handover

**Date paused:** 2026-08-12

**Repository:** `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT`

**Implementation worktree:** `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\concise-stage3-readout`

**Implementation branch:** `codex/concise-stage3-readout`

**Required baseline branch:** `codex/climate-country-bank-deploy`

**Baseline commit used:** `3b5886e`

**Current implementation HEAD:** `eb484d17a553712d7d791ea0e6bdbbb6f92a70c9`

## Objective and agreed design

Implement a concise-first Stage 3 result for the normal/core FCV assessment without changing the underlying assessment:

- Default on-screen view: a plain-language Summary intended to take about five minutes.
- Toggle: `Summary` / `Detailed analysis`, with no new model request when switching.
- Summary overview: overall assessment, short explanation, three strengths, and transition to ranked actions.
- Each concise priority: `Why this is suggested`, `How it can be addressed`, copy-ready suggested wording, then a secondary `Where this fits in the project cycle` block.
- Lifecycle language must reflect document stage and explicitly evidenced processing track. A standard PCN can distinguish commitment now from development during preparation. A consolidated/condensed process must use its compressed review logic. Later-stage documents must not defer material design choices.
- Detailed analysis remains substantially the existing full readout.
- DOCX and self-contained HTML downloads remain comprehensive and independent of the selected on-screen view.
- Step-by-step mode keeps detailed Stage 1 and Stage 2 review; setup copy should explain that. No extra setup choice for output length.
- Scope the concise UI and prompt additions to the normal/core FCV route. Do not alter the Climate verified reader or future active sector-lens routes.

## Reported layout regression to fix

The supplied screenshot showed the normal/core FCV ratings and Priority Overview rendered full-width above the report. Root cause was the Climate readout change that replaced the shared `.stage4-layout` / `.fcv-sidebar` structure with `stage3OverviewHtml()` and allowed it to leak into the normal route.

Required behavior:

- Normal/core `Detailed analysis`: comprehensive report and priority cards on the left; FCV Sensitivity, FCV Responsiveness, and Priority Overview vertically stacked in a sticky right sidebar.
- Normal/core `Summary`: hide the specialist sidebar and use the available width.
- Climate verified reader: retain its current separate overview and layout.
- At genuinely narrow widths, allow the normal detailed sidebar to stack without horizontal overflow.

Screenshot supplied by user:

`C:\Users\wb559324\AppData\Local\Temp\codex-clipboard-a5cfad5c-563f-4c4f-8d40-41395c8f9209.png`

Existing detailed report used as reference:

`C:\Users\wb559324\Downloads\FCV-Analysis-2026-08-12.html`

## Authoritative design and plan

These files are on planning branch `codex/concise-stage3-readout-design`, commits `d367f23` and `0c76a79`:

- Design: `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\docs\superpowers\specs\2026-08-12-concise-stage3-readout-design.md`
- Implementation plan: `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\docs\superpowers\plans\2026-08-12-concise-stage3-readout.md`

The files are gitignored local development artifacts and are not present in the implementation worktree. Read them from the main repository path above. The implementation plan has nine tasks and must be executed from the deployed baseline, not the older planning branch.

## Required workflow and model routing

The user selected option 1: subagent-driven development.

Follow `superpowers:subagent-driven-development`:

1. Use a fresh implementer for each task.
2. Implement with test-first red/green evidence.
3. After the task commit, run a separate specification-compliance review.
4. Only after specification approval, run a separate code-quality review.
5. Send any findings back to the original implementer and re-review until approved.
6. Do not run overlapping implementation agents because the remaining tasks share `app.py` and/or `index.html`.
7. Independently inspect diffs and rerun relevant verification; do not rely only on agent reports.

User-set model ceiling:

- **Highest permitted:** `gpt-5.6-sol` with **medium** reasoning.
- Routine bounded implementers: `gpt-5.6-terra` medium or lower.
- Complex integration and reviewers: `gpt-5.6-sol` medium.
- Do not use high, max, xhigh, or ultra reasoning.
- Spawn agents with `fork_turns: "none"` and provide curated task requirements directly.

The user supplied an Engineering Workflow emphasizing minimal change, proportional delegation, clear ownership, and direct verification. It contains no literal “Luna Max” requirement; the model ceiling above is the user's explicit clarification.

## Environment and baseline verification

The isolated worktree was created correctly under the existing gitignored `.worktrees/` directory.

The deployed branch includes a pinned submodule. It was initialized in the implementation worktree:

```text
data/climate-fcv-country-bank @ d6b1a1831ffdf84438940a36bf2ad9ff5d72aefd
```

Fresh baseline verification, after initializing the submodule:

```powershell
python -m pytest tests -q -p no:cacheprovider
```

Result: **853 passed in 59.22s**.

On this Windows sandbox, pytest must be allowed normal temporary-directory access. The successful baseline run used an escalated execution of the command above. Earlier sandboxed attempts created inaccessible untracked directories named `pytest-cache-files-*` and `.test-tmp/pytest-cache-files-*` inside the worktree. They are not tracked and are unrelated to the feature. Avoid broad cleanup or deletion; use `git status --short --untracked-files=no` when they make status noisy.

## Completed work: Task 1

Task 1 adds explicit, evidence-gated `processing_track` metadata to the Stage 1 temporal block and parser.

Commits:

- `c50ca32b4cd0d98e67e1dae8390195db2495e072` — `feat: detect project processing track`
- `eb484d17a553712d7d791ea0e6bdbbb6f92a70c9` — `fix: require exact processing track field`

Files changed:

- `app.py`
- `tests/test_lifecycle_detection.py`

Implemented behavior:

- Valid named values are only `standard` and `consolidated_condensed`.
- Unsupported values, legacy blocks without the field, and missing delimiter blocks produce `Unknown`.
- Prompt explicitly prohibits inference from document dates, approval dates, or the current calendar date.
- Parser is anchored to the exact line key so `proposed_processing_track: standard` does not bypass fail-closed behavior.

TDD and verification evidence:

- Initial red: five expected failures for the absent field/parser behavior.
- Initial green: lifecycle tests 9/9; combined adjacent tests 35/35.
- Quality review found the unanchored near-match-key issue.
- Fix red: regression test reproduced `proposed_processing_track: standard` incorrectly returning `standard`.
- Fix green: lifecycle tests 10/10; combined relevant tests 36/36.
- `git diff --check` passed.

Review status at pause:

- Specification review of the first Task 1 commit: **APPROVED**; only the two intended files changed.
- First code-quality review: **CHANGES_REQUIRED** for the unanchored regex only.
- The fix was implemented and committed at `eb484d17`.
- The required code-quality **re-review was started but deliberately interrupted when the user asked to pause**. This is the first action required next session.

## Exact next action

Resume Task 1's code-quality reviewer (or dispatch a fresh `gpt-5.6-sol`, medium-reasoning reviewer) against:

```text
Range: 3b5886e..eb484d17
Focus: exact-key anchoring regression and overall two-file Task 1 quality
Expected output: APPROVED or CHANGES_REQUIRED
```

If approved:

1. Independently inspect the two commits and run:

   ```powershell
   python -m pytest tests/test_lifecycle_detection.py -q -p no:cacheprovider
   ```

2. Mark Task 1 complete.
3. Start Task 2 from the implementation plan with a fresh implementer.

If changes are required, send them to the original Task 1 implementer if it is still available; otherwise dispatch a bounded fix implementer. Re-review before proceeding.

## Remaining work

After Task 1 review closes, execute sequentially:

1. **Task 2:** Normalize optional `concise_readout` and per-priority `concise` JSON fields in `extract_priorities()`, retaining complete legacy fallback.
2. **Task 3:** Add deterministic lifecycle guidance and concise schema to the existing core Stage 3 call only; explicitly gate out active sector lenses and Climate native/verified prompts.
3. **Task 4:** Add optional `concise_readout` to both step-by-step and Express Stage 3 SSE completion payloads.
4. **Task 5:** Add accessible Summary/Detailed UI, concise overview/priority rendering, legacy fallback notice, route gating, and current-assessment in-memory view state.
5. **Task 6:** Update mode descriptions and contract-test that downloads still consume full Stage 3 data. Do not partially extend the saved-session schema.
6. **Task 7:** Restore the normal/core Detailed sidebar and isolate `stage3OverviewHtml()` to the Climate route. Replace the existing Climate frontend test that currently asserts the leaked full-width shared layout.
7. **Task 8:** Update `CLAUDE.md` and the three reference docs. Carefully preserve any existing unrelated edits. Update the private parity log `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md` only with required filesystem approval.
8. **Task 9:** Run focused tests, the full suite, frontend storage tests, browser verification of both normal/core and Climate paths, final diff review, and a final independent reviewer.

## Important constraints and pitfalls

- Work only in the implementation worktree and branch listed at the top.
- Do not implement against the main/planning worktree.
- The current deployed branch is newer than the original plan's early line references. Match functions and behavior, not stale line numbers.
- Keep one canonical Stage 3 analysis. The concise layer is an additive presentation derivative generated in the same model call.
- Detailed fields remain authoritative.
- Do not alter ratings, priority order, recommendations, or export contents when toggling views.
- Gate concise generation and UI using server-resolved active-lens state, not raw client input.
- Climate verified/native output must remain unchanged.
- Unknown processing track must use conservative stage-only wording and must not assert a procedural gate.
- Preserve existing Stage 3 grounding and citation guardrails.
- Preserve unrelated user changes in the original worktree, especially `claude.md`, existing PNG/mockup files, `HANDOVER.md`, and `output/`.
- Do not overwrite the pre-existing root `HANDOVER.md`.

## Git state at pause

Implementation branch history:

```text
eb484d1 fix: require exact processing track field
c50ca32 feat: detect project processing track
3b5886e feat: port light document-integrity scan to the general screener (A4)
```

Tracked worktree state was clean before adding this handover file. This handover itself should be committed separately if the next session confirms its contents.

## Ready-to-paste next-session prompt

```text
Continue the concise Stage 3 readout implementation using the handover at:
C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\concise-stage3-readout\20260812_concise-stage3-readout-handover.md

Work only in:
C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\concise-stage3-readout
Branch: codex/concise-stage3-readout

Read the handover, the worktree CLAUDE.md, the design specification, and the implementation plan paths recorded in the handover before acting. Continue with subagent-driven development: fresh implementer per task, then separate specification and code-quality reviews, with no overlapping write ownership. Use TDD and independently verify all agent work.

Model ceiling: never exceed gpt-5.6-sol with medium reasoning. Use terra medium or lower for routine bounded implementation and sol medium for complex integration/reviews. Use fork_turns="none" and give agents curated instructions.

First action: complete the interrupted Task 1 code-quality re-review for range 3b5886e..eb484d17. Do not begin Task 2 until Task 1 is approved and its focused tests are independently rerun. Then continue the nine-task implementation plan sequentially. Preserve the Climate verified reader, comprehensive downloads, unrelated user changes, and the private dual-build parity requirement.
```

## Final verification

- Focused final suite: **159 passed** (lifecycle, extract priorities, concise contract, grounding guardrails, climate frontend/render/runtime).
- Full suite: `python -m pytest tests -q -p no:cacheprovider` with normal temporary-directory access: **892 passed in 56.86s**.
- Frontend storage helpers: `node tests/test_frontend_storage_helpers.js` passed.
- Final `git diff --check` baseline was clean.
- Final independent review: **APPROVED**.

Caveat: no live-browser visual test was run because there was no local saved/API-free Stage 3 fixture or session.
