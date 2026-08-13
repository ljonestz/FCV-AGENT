# Climate Country-Bank Preview Rollout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all 24 reviewed candidate country packages usable on the existing Render smoke service and a new isolated Render preview service without changing production approval status.

**Architecture:** Both non-production services explicitly load the schema-1.1 candidate runtime with the reviewed-candidate token and default to the smoke model profile. Local contract checks establish that the exact pinned runtime resolves all 24 countries; live checks establish that Render deploys the intended application commit, uses smoke mode, selects the candidate bank, completes the workflow, and preserves preview labelling. One South Sudan quality run, plus a second only if an authentic candidate-country project document is already available, provides bounded final acceptance before the dedicated service is returned to smoke mode.

**Tech Stack:** Python 3.13, pytest, Flask `/health`, Render web services, Git submodules, PowerShell, browser-based deployment checks.

---

## File Map

- Read: `sector_lenses/climate_bank.py` - application loader and candidate-preview gate.
- Read: `data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json` - immutable 24-country candidate runtime.
- Read: `render_build.py` - Render submodule initialization and dependency installation.
- Read: `Procfile` - Render start command.
- Read: `docs/20260803_south-sudan-climate-testing-handover.md` - service split and authentic South Sudan test input.
- Create: `docs/20260813_climate_country_bank_preview_rollout_handover.md` - deployment evidence and final operating state.
- No application code, approved release, or production configuration is changed by this plan.

### Task 1: Verify the exact branch and 24-country runtime locally

**Files:**
- Test: `tests/test_climate_bank.py`
- Test: `tests/test_climate_bank_selector.py`
- Test: `tests/test_climate_bank_deployment_contract.py`
- Test: `tests/test_climate_lens_frontend.py`
- Test: `data/climate-fcv-country-bank/tests/test_release.py`

- [ ] **Step 1: Confirm branch, application commit, and pinned bank commit**

Run:

```powershell
git status --short --branch
git rev-parse HEAD
git ls-tree HEAD data/climate-fcv-country-bank
```

Expected: branch `codex/climate-summary-quality-fixes`, no unrelated working-tree changes, and gitlink `12a804fe92bacfdaf0bec7926725d8a7a9376fe4`.

- [ ] **Step 2: Run the targeted application contract tests outside the OneDrive pytest temp path**

Run:

```powershell
$previewPytestTemp = 'C:\Users\wb559324\AppData\Local\Temp\fcv-agent-country-bank-preview-app'
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_climate_bank.py tests/test_climate_bank_selector.py tests/test_climate_bank_deployment_contract.py tests/test_climate_lens_frontend.py::test_verified_reader_visual_refresh_preserves_depth_and_orders_sections -q -p no:cacheprovider --basetemp $previewPytestTemp
```

Expected: all selected tests pass with no assertion failure. A sandbox permission failure requires rerunning the same command with approved access; it is not an application-test failure.

- [ ] **Step 3: Run the companion-bank release tests outside the OneDrive pytest temp path**

Run:

```powershell
Push-Location data/climate-fcv-country-bank
$previewBankTemp = 'C:\Users\wb559324\AppData\Local\Temp\fcv-agent-country-bank-preview-bank'
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_release.py -q -p no:cacheprovider --basetemp $previewBankTemp
Pop-Location
```

Expected: `tests/test_release.py` passes. Do not rebuild or promote the runtime.

- [ ] **Step 4: Validate the committed candidate runtime and exact record counts**

Run from the application worktree:

```powershell
Push-Location data/climate-fcv-country-bank
& 'C:\WBG\Python313\python.exe' -c "import json; from pathlib import Path; from climate_bank.validation import validate_runtime_release; p=Path('releases/candidates/2026.08/runtime.json'); r=json.loads(p.read_text(encoding='utf-8')); e=validate_runtime_release(r); assert not e, e; assert r['schema_version']=='1.1.0'; assert r['content_version']=='2026.08.multi-country-preview'; assert r.get('candidate') is True; assert (len(r['countries']),len(r['sources']),len(r['evidence_records']),len(r['pathways']))==(24,291,565,178); print('PASS candidate runtime: 24 countries, 291 sources, 565 evidence, 178 pathways')"
Pop-Location
```

Expected: `PASS candidate runtime: 24 countries, 291 sources, 565 evidence, 178 pathways`.

- [ ] **Step 5: Exercise the actual application loader against every country and alias set**

Run:

```powershell
$env:CLIMATE_COUNTRY_BANK_PATH = 'data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json'
$env:CLIMATE_COUNTRY_BANK_PREVIEW = 'reviewed-candidate'
& 'C:\WBG\Python313\python.exe' -c "from sector_lenses.climate_bank import load_climate_bank; b=load_climate_bank(); assert b.status=='ok', b.warning_code; assert b.candidate_preview is True; assert len(b.release['countries'])==24; missing=[c.get('name',k) for k,c in b.release['countries'].items() if b.resolve_country(c.get('name','')) is None or b.resolve_country(c.get('iso3','')) is None]; assert not missing, missing; print('PASS app loader: 24 candidate countries resolve by name and ISO3')"
Remove-Item Env:CLIMATE_COUNTRY_BANK_PATH
Remove-Item Env:CLIMATE_COUNTRY_BANK_PREVIEW
```

Expected: `PASS app loader: 24 candidate countries resolve by name and ISO3`.

### Task 2: Capture the Render baseline without changing production

**Files:**
- Read: `docs/20260803_south-sudan-climate-testing-handover.md`

- [ ] **Step 1: Open the Render dashboard and identify both existing services**

Use the authenticated in-app browser. Confirm:

```text
Production: https://fcv-agent.onrender.com
Existing branch-testing service: https://fcv-agent-1.onrender.com
```

Expected: the stable service remains linked to `main`; the testing service is distinct from production.

- [ ] **Step 2: Record the stable production baseline read-only**

Record its linked branch, deployed commit, build command, and the absence of candidate-preview variables. Open:

```text
https://fcv-agent.onrender.com/health
```

Expected: HTTP 200 and `status: ok`. Do not edit, redeploy, suspend, or restart this service.

- [ ] **Step 3: Record the existing testing-service baseline**

Record its linked branch, deployed commit, build command, start command, and values for these non-secret settings:

```text
CLIMATE_COUNTRY_BANK_PATH
CLIMATE_COUNTRY_BANK_PREVIEW
CLIMATE_VERIFIED_RUN_MODE
```

Open:

```text
https://fcv-agent-1.onrender.com/health
```

Expected: HTTP 200. Preserve the recorded settings as the rollback point.

### Task 3: Enable the 24-country candidate runtime on the existing smoke service

**Files:**
- Read: `render_build.py`
- Read: `Procfile`

- [ ] **Step 1: Configure the branch-testing service**

In Render, set the service branch and commands to:

```text
Branch: codex/climate-summary-quality-fixes
Build command: python render_build.py
Start command: gunicorn wsgi:app --worker-class gevent --workers ${WEB_CONCURRENCY:-1} --threads ${GUNICORN_THREADS:-1} --bind 0.0.0.0:$PORT --timeout 1200
```

Set exactly:

```text
CLIMATE_COUNTRY_BANK_PATH=data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json
CLIMATE_COUNTRY_BANK_PREVIEW=reviewed-candidate
CLIMATE_VERIFIED_RUN_MODE=smoke
```

Do not alter provider keys or model-override variables.

- [ ] **Step 2: Deploy the latest branch commit**

Trigger a normal deploy and wait until Render reports `Live`.

Expected: the build log shows successful recursive submodule initialization and dependency installation. The deployed application commit must equal the current `git rev-parse HEAD` value; the gitlink at that commit must remain `12a804fe92bacfdaf0bec7926725d8a7a9376fe4`.

- [ ] **Step 3: Verify service identity and runtime mode**

Open:

```text
https://fcv-agent-1.onrender.com/health
```

Expected JSON fields include:

```json
{
  "status": "ok",
  "climate_verified_run_mode": "smoke"
}
```

The returned `build` value is accepted only when it equals the first 12
characters of the commit Render reports as deployed.

- [ ] **Step 4: Run the authentic South Sudan PCN once in smoke mode**

Use the South Sudan Project Concept Note dated 15 June 2026 identified in `docs/20260803_south-sudan-climate-testing-handover.md`. Select the Climate-FCV lens and complete the workflow.

Expected:

- the run reaches the final reader;
- the Render grounding log reports `bank_version=2026.08.multi-country-preview` and `iso3=SSD`;
- the reader displays `preview; not approved`;
- the reader displays `Smoke test: validates workflow completion only; not a quality benchmark.`;
- HTML and DOCX exports preserve preview and smoke labelling; and
- no bank-loader error occurs.

- [ ] **Step 5: Recheck production after the smoke deployment**

Open `https://fcv-agent.onrender.com/health` and compare its Render branch/configuration with the Task 2 baseline.

Expected: production branch, deployed commit, build command, environment, and health status are unchanged.

### Task 4: Create the dedicated Render preview service

**Files:**
- Read: `render_build.py`
- Read: `Procfile`

- [ ] **Step 1: Create an isolated web service**

Create a Render web service named:

```text
fcv-agent-climate-preview
```

Use the same repository connection, region, instance class, health-check path, provider keys, and non-bank operational settings as `fcv-agent-1`, but configure:

```text
Branch: codex/climate-summary-quality-fixes
Build command: python render_build.py
Start command: gunicorn wsgi:app --worker-class gevent --workers ${WEB_CONCURRENCY:-1} --threads ${GUNICORN_THREADS:-1} --bind 0.0.0.0:$PORT --timeout 1200
CLIMATE_COUNTRY_BANK_PATH=data/climate-fcv-country-bank/releases/candidates/2026.08/runtime.json
CLIMATE_COUNTRY_BANK_PREVIEW=reviewed-candidate
CLIMATE_VERIFIED_RUN_MODE=smoke
```

Expected: the new service has its own Render service ID and URL and does not replace or alias either existing service.

- [ ] **Step 2: Deploy and verify the dedicated service**

Wait for `Live`, then open its `/health` endpoint.

Expected: `status: ok`, the build matches the intended branch commit, and `climate_verified_run_mode: smoke`. Build logs must show successful submodule initialization.

- [ ] **Step 3: Run the South Sudan PCN once in smoke mode on the dedicated service**

Repeat the smoke workflow and export checks from Task 3.

Expected: candidate content version `2026.08.multi-country-preview`, `iso3=SSD`, full completion, preview label, smoke label, and matching HTML/DOCX labels.

- [ ] **Step 4: Confirm the full-suite evidence chain**

Record together:

1. the Task 1 actual-loader result resolving all 24 countries;
2. the deployed application commit;
3. the gitlink to bank commit `12a804f`;
4. the candidate content version observed in the live grounding log; and
5. the successful dedicated-service smoke run.

Expected: this chain establishes that the deployed preview service is using the exact locally validated 24-country runtime without requiring 24 fabricated or mismatched project documents.

### Task 5: Run the bounded quality acceptance sample and restore smoke mode

**Files:**
- Read: `docs/20260803_south-sudan-climate-testing-handover.md`

- [ ] **Step 1: Switch only the dedicated preview service to quality**

Change:

```text
CLIMATE_VERIFIED_RUN_MODE=quality
```

Keep the candidate path and preview token unchanged. Wait for the redeploy to become `Live` and confirm `/health` returns `climate_verified_run_mode: quality`.

- [ ] **Step 2: Run the South Sudan PCN once in quality mode**

Expected:

- the workflow completes;
- the grounding log reports `bank_version=2026.08.multi-country-preview` and `iso3=SSD`;
- country evidence remains contextual rather than becoming unsupported project facts;
- the four judgments, narrative, admitted priorities, and readiness flags are internally coherent;
- browser, HTML, and DOCX output remain labelled `preview; not approved`; and
- no smoke label appears in quality output.

- [ ] **Step 3: Decide whether a second quality run is warranted from existing authentic inputs**

Inventory already-available project documents for the other 23 candidate countries. Run one additional quality assessment only when an authentic design-stage project document is already available and its country resolves to the candidate bank. Do not create synthetic project content, download a document merely to fill a quota, or exceed two total quality runs.

Expected: either one documented South Sudan quality run, or two total documented quality runs with the second country's authentic input identified.

- [ ] **Step 4: Restore the dedicated preview service to smoke mode**

Set:

```text
CLIMATE_VERIFIED_RUN_MODE=smoke
```

Wait for `Live` and verify `/health` again.

Expected: `climate_verified_run_mode: smoke`; candidate path and preview token remain set.

- [ ] **Step 5: Verify production a final time**

Compare the production Render settings and `/health` response with the Task 2 baseline.

Expected: no production change.

### Task 6: Write, verify, commit, and push the rollout handover

**Files:**
- Create: `docs/20260813_climate_country_bank_preview_rollout_handover.md`
- Modify: `claude.md` only if implementation required a substantial repository change beyond this operational rollout.

- [ ] **Step 1: Write the handover as a new file**

Include:

- existing smoke-service URL and final smoke state;
- dedicated preview-service URL, Render service ID, and final smoke state;
- deployed application commit and bank gitlink;
- candidate runtime path and content version;
- 24/291/565/178 validation counts;
- local test commands and exact outcomes;
- smoke run IDs and grounding-log summaries;
- quality run ID(s), country or countries, and acceptance findings;
- confirmation that production was unchanged;
- confirmation that candidates remain `preview; not approved`; and
- unresolved content or deployment caveats.

- [ ] **Step 2: Inspect repository state and handover diff**

Run:

```powershell
git status --short
git diff --check
git diff -- docs/20260813_climate_country_bank_preview_rollout_handover.md
```

Expected: only the intended handover or explicitly justified documentation changes appear, with no whitespace errors.

- [ ] **Step 3: Commit the handover**

Run:

```powershell
git add -- docs/20260813_climate_country_bank_preview_rollout_handover.md
git diff --cached --check
git diff --cached --stat
git commit -m "docs: record country-bank preview rollout"
```

Expected: one documentation commit containing the verified rollout record.

- [ ] **Step 4: Push the feature branch**

Run:

```powershell
git push origin HEAD:refs/heads/codex/climate-summary-quality-fixes
```

Expected: the remote branch advances to include the design, plan, and rollout handover commits.

- [ ] **Step 5: Final acceptance check**

Run:

```powershell
git status --short --branch
git log -3 --oneline --decorate
```

Expected: clean feature worktree; remote and local branch tips agree; both non-production services end in smoke mode; production remains unchanged.
