# Repository Agent Instructions

Read `claude.md`, `HANDOFF.md`, and the applicable design/plan under
`docs/superpowers/` before changing prompts, Stage 3 JSON, routes, readers, or
exports. Also read the private parity contract named in the user-level instructions
before changing a shared Render/ITS contract surface.

## Branch and scope

- Use an isolated worktree for substantive changes and never commit directly to
  `main`.
- Keep diffs narrow and preserve ITS-specific retrieval differences.
- When a user selects "keep the branch," preserve both the branch and its worktree.

## Local verification prerequisites

The Climate-FCV country bank is a pinned submodule. Before treating bank tests as
failures, run:

```powershell
git submodule sync --recursive
git submodule update --init --recursive
```

An uninitialized submodule correctly makes the runtime report `bank_missing`; that
is a checkout/setup problem, not an application regression. On managed Windows
machines, pytest and Playwright may need normal process permissions for the user
Temp directory and named pipes. Sandbox `WinError 5` setup failures are not product
failures. Run the full suite in a normal shell after focused tests pass.

## Render live-acceptance protocol

Use `test_documents/live_acceptance/somalia-stairp-p513127-concept-pid-20260207.pdf`
as the standard recent FCV-country IPF check unless a task requires another case.
Use the current dated handoff for service names and URLs; verify the configured
branch and deployed SHA because test services can be repointed.

1. Verify the Render service, configured branch, and deployed commit before upload.
2. Wake the service before starting. The preview services used in August 2026 were
   observed returning toward dormancy after roughly eight idle minutes. Keep a
   separate page or browser context on the service and refresh it periodically during
   long preparation or review gaps.
3. After a cold start, wait for the landing page and upload controls to be stable
   before interacting. Retry a page load race before diagnosing the app.
4. Run Smoke first, then one quality run against the same complete document.
5. Preserve the `assessment_id`. Filter Render logs by that ID and confirm every
   `/api/run-stage` request completes, noting timestamps, status codes, explicit
   stage timeouts, worker restarts, OOM signals, or gateway 5xx responses.
6. Capture a Summary screenshot and save the Detailed browser HTML. Also download
   the detailed standalone HTML and DOCX to prove the export boundary.
7. Review model-generated current-context assertions against the uploaded document
   and cited public sources. A structurally valid Summary is not proof that every
   dated external claim is current.

## Timeout and streaming guardrails

- Keep frontend abort budgets strictly above backend stage wall-clock caps; keep
  both below the gunicorn/hosting request limit.
- Do not add blocking, non-streaming model calls after or between SSE stages. Any
  lengthy preprocessing must emit progress or keepalives.
- Preserve compact conversation-history labels; do not store full injected prompts
  and carry them into later stages.
- Keep Stage 3 structured JSON before the detailed narrative. Long trailing JSON
  blocks were observably omitted by otherwise successful model generations.
- Distinguish an app `TimeoutError` from browser abort, gateway 502/503, worker OOM,
  cold start, and upload 413 before changing timeout values.
- Initialize submodules through `render_build.py`; do not replace that build entry
  point with a plain dependency-install command.

## Acceptance artifacts and reporting

Do not commit generated screenshots, raw model responses, downloaded reports, or
Render logs. Record their paths and checks in the current handoff. The only binary
retained in this repository for this workflow is the small public standard check
PDF documented in `test_documents/live_acceptance/README.md`.

## Implementation lessons from the normal-FCV Summary

- Core prompt additions must be scoped by route. `_embed_core_concise_stage3_schema()`
  runs only when `active_lenses` is empty; a global schema edit can silently leak
  core fields into specialist-lens contracts.
- Some Stage 3 templates pass through Python `.format(...)`. Escape literal JSON
  braces only inside text that still awaits that formatting pass. Schema constants
  injected afterwards by `_embed_core_concise_stage3_schema()` must retain normal
  single braces. Inspect final rendered design and implementation prompts in tests;
  template source alone cannot prove brace safety.
- Do not validate only `concise_readout`. Summary requires the readout and a complete
  concise object on every ranked priority. Partial bundles create misleading hybrid
  views and must be discarded atomically.
- Persistence must save and restore `stageConciseReadout`, `stageThreePriorities`,
  `fcvRating`, and `fcvResponsivenessRating` before evaluating the Summary gate.
  Restoring only the readout always falls back to Detailed because priorities are
  unavailable.
- `downloadReport()` and `downloadHTML()` are deliberate detailed-only boundaries.
  Contract tests should confirm they do not call Summary renderers or contain
  advisory/accordion state.
- A successful Summary header is not enough for live acceptance. Inspect all
  priorities in the raw Stage 3 payload, verify every concise object, exercise a
  non-first accordion card, switch tabs, and inspect both browser HTML and the
  standalone export.
- Use the smallest efficient verification ladder: focused parser/frontend contracts,
  syntax and diff checks, then the full suite once. Expand only when a check fails.
- Keep raw model responses outside Git. They are useful for separating prompt
  omission, malformed JSON, parser rejection, and frontend rendering defects.
- Structural acceptance and analytical quality are separate gates. Smoke proves the
  pipeline; quality review checks grounding, current-context assertions, project
  specificity, lifecycle calibration, and whether priority wording overstates
  evidence.
