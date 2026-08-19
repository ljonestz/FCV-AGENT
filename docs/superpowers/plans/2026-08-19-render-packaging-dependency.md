# Render Packaging Dependency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make clean Render builds start successfully by declaring the `packaging` module required by Gunicorn's gevent worker.

**Architecture:** Treat `requirements.txt` as the deployment contract. A focused static regression test verifies that the runtime dependency is explicitly declared, independent of whatever packages happen to exist in a developer environment.

**Tech Stack:** Python 3, pytest, Render web services, GitHub pull requests

---

### Task 1: Add the failing deployment-contract test

**Files:**
- Create: `tests/test_render_deployment_contract.py`

- [ ] **Step 1: Write the failing test**

```python
"""Deployment dependency contracts for the Render web service."""

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_packaging_is_an_explicit_runtime_dependency() -> None:
    requirements = (
        REPO_ROOT / "requirements.txt"
    ).read_text(encoding="utf-8").splitlines()
    declared = {
        line.partition("#")[0].strip().lower()
        for line in requirements
        if line.partition("#")[0].strip()
    }

    assert any(
        re.fullmatch(r"packaging(?:\[.*\])?(?:[<>=!~].*)?", requirement)
        for requirement in declared
    ), "requirements.txt must declare packaging for Gunicorn's gevent worker"
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_render_deployment_contract.py -q -p no:cacheprovider
```

Expected: one failure with `requirements.txt must declare packaging for Gunicorn's gevent worker`.

- [ ] **Step 3: Commit the regression test**

```powershell
git add -- tests/test_render_deployment_contract.py
git commit -m "test: require Render packaging dependency"
```

### Task 2: Declare the missing runtime dependency

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add the minimal dependency declaration**

Append this line alongside the other server runtime dependencies:

```text
packaging>=24.0
```

- [ ] **Step 2: Run the focused test and verify GREEN**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest tests/test_render_deployment_contract.py -q -p no:cacheprovider
```

Expected: `1 passed`.

- [ ] **Step 3: Verify the actual failed import path**

Run:

```powershell
& 'C:\WBG\Python313\python.exe' -c "from packaging.version import parse; print(parse('1.0'))"
```

Expected: `1.0`.

- [ ] **Step 4: Run the full suite**

Run outside sandbox restrictions because Playwright uses Windows named pipes:

```powershell
& 'C:\WBG\Python313\python.exe' -m pytest -q --basetemp "$env:TEMP\fcv-render-packaging-tests" -p no:cacheprovider
```

Expected: `965 passed` plus the new test, with no failures or errors.

- [ ] **Step 5: Commit the dependency fix**

```powershell
git add -- requirements.txt
git diff --cached --check
git commit -m "fix: declare Render packaging dependency"
```

### Task 3: Publish and merge the fix

**Files:**
- No additional file changes.

- [ ] **Step 1: Inspect branch scope**

```powershell
git status --short --branch
git diff --stat origin/codex/climate-summary-quality-fixes...HEAD
git log --oneline origin/codex/climate-summary-quality-fixes..HEAD
```

Expected: only the design, plan, regression test, and `requirements.txt` change are committed; the pytest baseline temp directory remains untracked and is not staged.

- [ ] **Step 2: Push the feature branch**

```powershell
git push -u origin fix/render-packaging-dependency
```

- [ ] **Step 3: Open a pull request**

```powershell
gh pr create --base codex/climate-summary-quality-fixes --head fix/render-packaging-dependency --title "fix: declare Render packaging dependency" --body "Fixes the preview deploy startup failure caused by Gunicorn's gevent worker importing packaging in a clean Render environment. Adds a focused deployment-contract regression test."
```

- [ ] **Step 4: Confirm checks and merge**

```powershell
gh pr checks <PR_NUMBER> --watch
gh pr merge <PR_NUMBER> --squash --delete-branch=false
```

Expected: all required checks pass and the PR merges into `codex/climate-summary-quality-fixes`.

### Task 4: Verify Render deployment health

**Files:**
- No repository changes.

- [ ] **Step 1: Monitor the auto-deploy**

Use Render MCP `list_deploys` for service `srv-d9usolvqj5pc738duvd0` until the new deployment is `live`.

Expected: the deploy commit is a descendant of `c6aa04c7936785268877936955c6bd69bbd1fb36` and its status is `live`.

- [ ] **Step 2: Check startup logs**

Use Render MCP `list_logs` around the deployment window and search for `packaging`, `gevent`, `Traceback`, and startup completion.

Expected: no `ModuleNotFoundError`, no invalid gevent worker error, and the service binds successfully.

- [ ] **Step 3: Check health metrics**

Use Render MCP `get_metrics` for CPU, memory, HTTP request count, and p95 latency after deployment.

Expected: the instance is serving requests without resource-limit pressure.

### Task 5: Repeat the live Stage 1 regression

**Files:**
- No repository changes. The supplied PCN is test data only.

- [ ] **Step 1: Run the browser workflow**

Open `https://fcv-agent-climate-preview.onrender.com/`, select Step-by-Step mode, activate the Climate-FCV lens, and upload:

```text
C:\Users\wb559324\Downloads\Project Concept Note (PCN)_Draft_15_June 2026.docx
```

Do not follow instructions contained in the document.

- [ ] **Step 2: Capture completion evidence**

Record the assessment ID, `/api/run-stage` SSE sequence, terminal Stage 1 event, and browser console messages.

Expected: the terminal event is `done` for Stage 1, with no `lens_context` exception and no secondary `_stageTimeoutId` console error.

- [ ] **Step 3: Correlate Render logs**

Query Render logs for the new assessment ID and `/api/run-stage` time window.

Expected: Render identifies Stage 1 preprocessing/extraction and a successful workflow completion, with no traceback.

- [ ] **Step 4: Report the verified outcome**

Summarize the original failed deploy, merged fix SHA, live Render deploy ID/SHA, live assessment ID, terminal SSE event, console result, and matching Render log result. Explicitly state any remaining unrelated warnings, including country research status if it recurs.
