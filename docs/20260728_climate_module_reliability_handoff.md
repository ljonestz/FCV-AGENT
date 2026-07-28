# Climate-FCV Reliability Redesign Handoff

**Date:** 2026-07-28
**Purpose:** Restart-safe context for the next Codex or Claude Code session
**Current worktree:** `.worktrees/climate-readout`
**Current branch:** `feat/climate-readout-redesign`
**Branch head before this documentation commit:** `5323769`

## 1. Current repository arrangement

The public Render/Flask repository has been separated into two purposes:

- `main` is restored to the closest available ITS-compatible baseline. The
  rollback commit is `79f0c16`; its tree matches the earlier baseline commit
  `2d9b6fd`.
- Climate and dual-regime development remain preserved on feature branches.
- The active climate worktree is
  `C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-readout`.
- The active climate branch is `feat/climate-readout-redesign`, tracking
  `origin/feat/climate-readout-redesign`.

Do not implement the climate redesign on `main`.

## 2. Live deployment state checked on 2026-07-28

The public Render service at `https://fcv-agent.onrender.com` is currently
serving the restored baseline:

- `/health` returned only `{"status":"ok"}`;
- `/api/sector-lenses` returned HTTP 404.

This confirms that the public service is no longer serving the climate feature
branch. Climate validation must use an isolated preview deployment.

## 3. Verification baseline

On `feat/climate-readout-redesign`:

```powershell
python -m pytest -q
```

Result on 2026-07-28:

- 457 passed;
- one non-functional pytest cache warning caused by restricted write access;
- worktree clean before the documentation files were added.

Passing tests do not establish production reliability. See the design
specification for the missing latency and complete-prompt tests.

## 4. Evidence reviewed

The 2026-07-28 diagnosis reconciled:

- the current climate branch and commit history;
- `CLAUDE.md`;
- the root and project `AGENTS.md` guidance;
- the attached Claude Code transcript at
  `C:\Users\wb559324\.codex\attachments\d31f6d84-63d1-4c82-bbed-89cd1a549040\pasted-text.txt`;
- the existing climate design specifications;
- the climate implementation plan;
- the dual-regime handoff;
- the current Flask pipeline, prompts, recovery, research coordinator, sector
  lens contracts, budgets, frontend, and tests; and
- the live public Render endpoints.

Do not read the restricted raw OPCS corpus. Use only existing approved summaries
and review outputs.

## 5. Key existing documents

Read in this order:

1. `docs/superpowers/specs/2026-07-28-climate-module-reliability-redesign-design.md`
2. `docs/superpowers/specs/2026-07-25-climate-readout-questions-redesign-design.md`
3. `docs/superpowers/specs/2026-07-24-climate-native-flow-design.md`
4. `docs/superpowers/plans/2026-07-26-climate-readout-questions-redesign.md`
5. `docs/20260726_opcs_dual_regime_and_climate_handoff.md`
6. `docs/superpowers/specs/2026-07-26-dual-regime-process-model-design.md`
7. `CLAUDE.md`

The 2026-07-28 specification controls where it deliberately refines the older
documents.

## 6. Production failure evidence

The supplied run history showed:

- climate research: two attempts, approximately 176 seconds, zero accepted
  sources and claims;
- Stage 2: completed but omitted the Climate-FCV diagnostic;
- validation: rejected the missing diagnostic;
- recovery: timed out at approximately 120 seconds;
- frontend: correctly reported that a validated Climate-FCV diagnostic could
  not be produced; and
- a separate provider-side Anthropic HTTP 529 overload.

The overload retry added in `5323769` is useful but does not address the
persistent climate failure.

## 7. Confirmed root cause

The approved climate-native architecture was only partially implemented.

The current code still combines:

- the full generic Stage 2 prompt, including the 12 operational standards,
  DNH-9, 25-question map, generic narrative, evidence trail, ratings, and
  recommendations; and
- a large climate suffix that requests the structured diagnostic and detailed
  climate readout.

Measured locally before injected project context:

- generic Stage 2 prompt: approximately 45,080 characters;
- climate suffix: approximately 12,981 characters;
- combined: approximately 58,061 characters.

The model commonly completes the generic output and omits the trailing
diagnostic. The non-streaming 120-second recovery is consequently load-bearing
and times out.

Climate research also has a parent/child deadline mismatch: sequential retries
can outlive the parent Stage 1 research budget and have their eventual results
discarded.

## 8. Why the existing tests did not catch it

The current suite:

- checks climate suffix content rather than the full assembled prompt;
- does not prove that the generic Stage 2 engine is absent in climate mode;
- uses immediate fake recovery responses;
- does not simulate slow research or nested deadline exhaustion;
- does not verify server-sent-event progress during recovery; and
- does not make "primary diagnostic succeeds without recovery" an acceptance
  condition.

## 9. User-approved decisions from 2026-07-28

### Architecture

- Restore the approved climate-native route.
- Do not run the full 12-OST, DNH-9, or 25-question engine in climate mode,
  visibly or as a large hidden checklist.
- Retain only a compact FCV baseline.
- Generate the structured climate diagnostic as a primary output.
- Use climate-specific Stage 3 priorities only.

### Research

- Targeted external climate and climate-FCV research remains mandatory.
- Make broad generic FCV research lighter.
- Project documents and OPCS guidance alone are too generic for a successful
  Climate-FCV assessment.
- If mandatory research fails, generate neither the compact baseline nor the
  climate assessment.
- Offer retry or the full standard FCV assessment.

### Question bank

- Retain the six core climate-FCV themes as stable anchors.
- Do not treat six as a fixed ceiling.
- Permit additional source-derived questions when materially relevant to the
  project.
- Prefer curated depth and specificity over fixed coverage.

### Output quality

- Make every section as nuanced, tailored, and project-specific as the evidence
  permits.
- Link insights and recommendations to named project components, locations,
  beneficiaries, institutions, indicators, delivery arrangements, and
  document sections.
- Tie operational recommendations to relevant, instrument-appropriate OPCS
  guidance.
- Do not fabricate specificity when the source documents are silent.

## 10. Approved output

Order:

1. Executive summary.
2. Six-tier integration gauge.
3. Three-part operating context.
4. Detailed strengths and weaknesses.
5. Core and supplementary climate-FCV questions.
6. Approximately three, with no more than five, climate-specific priorities.
7. Advisory boundary.

The compact FCV baseline supports the climate analysis but does not recreate the
generic FCV readout.

## 11. Required implementation safeguards

- Dedicated climate Stage 2 base prompt, not a generic prompt plus suffix.
- One versioned structured Stage 2 payload as the single source of truth; do not
  generate duplicate visible and hidden copies of the climate assessment.
- Mandatory research evidence gate before Stage 2.
- One owner for the total research deadline.
- Retry only when sufficient budget remains.
- Primary diagnostic required on the normal path.
- Recovery limited to missing or invalid fields.
- Recovery preserves valid fields and merges only validated repairs.
- Recovery must stream or permit heartbeats.
- Typed failure states and assessment-ID logging.
- Specificity, provenance, and instrument-vocabulary validation.
- No partial climate success after research or recovery failure.
- Standard FCV route unchanged.

## 12. Immediate next workflow

The approved brainstorming design is complete. Follow the superpowers workflow:

1. Review the new design specification for critical gaps.
2. Present the written specification to the user for review.
3. After user approval, invoke `superpowers:writing-plans`.
4. Write a new implementation plan that supersedes the incomplete parts of the
   2026-07-26 plan.
5. Do not edit application code before the implementation plan is approved.

The implementation plan should start with failing tests for:

- full prompt isolation;
- research fail-closed behavior;
- deadline ownership;
- happy-path diagnostic without recovery; and
- observable bounded recovery.

## 13. Suggested restart commands

```powershell
Set-Location "C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-readout"
git status --short --branch
git log -8 --oneline --decorate
python -m pytest -q
```

Then read the documents in Section 5. Confirm the branch has not moved before
following any line-number references from older plans.

## 14. Integration boundary

Do not merge or push climate changes into the restored `main` during
implementation. Use an isolated Render preview and obtain user acceptance
before deciding how the climate work and dual-regime foundation should be
integrated or mirrored to the ITS/FastAPI build.
