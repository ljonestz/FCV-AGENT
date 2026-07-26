# Climate Diagnostic Recovery Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure a missing or incomplete Climate-FCV Stage 2 diagnostic is recovered through a dedicated, bounded client instead of the 25-second fast client.

**Architecture:** Preserve the existing inline diagnostic as the fast path. Add one dedicated Anthropic client for conditional diagnostic recovery, with a 120-second default/read timeout and no SDK retries, then pass every recovered response through the existing normalization and validation contract before either route can use it.

**Tech Stack:** Python 3, Flask, Anthropic Python SDK, httpx, pytest

---

## File structure

- Modify `app.py`: add the recovery-client factory, route recovery through it, and add bounded timing/status logs.
- Modify `tests/test_sector_lens_app_contract.py`: add factory, default-client, success, invalid-response, and provider-timeout regression tests.
- Modify `CLAUDE.md`: record the dedicated recovery-client architecture and operational diagnostics.
- Modify `docs/reference/reference_backend_routes.md`: document identical Express and step-by-step recovery behaviour.

### Task 1: Lock down the dedicated client contract

**Files:**
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `app.py:5683-5710`

- [ ] **Step 1: Write the failing client-factory test**

Add this test near the other sector-lens recovery tests:

```python
def test_lens_recovery_client_has_bounded_timeout_and_no_sdk_retries(monkeypatch):
    captured = {}
    sentinel = object()

    def fake_anthropic(**kwargs):
        captured.update(kwargs)
        return sentinel

    monkeypatch.setattr(app_module.anthropic, "Anthropic", fake_anthropic)
    monkeypatch.setattr(app_module, "_lens_recovery_client", None, raising=False)

    client = app_module.get_lens_recovery_client()

    assert client is sentinel
    assert captured["max_retries"] == 0
    assert captured["timeout"].connect == 10.0
    assert captured["timeout"].read == 120.0
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
python -m pytest tests/test_sector_lens_app_contract.py::test_lens_recovery_client_has_bounded_timeout_and_no_sdk_retries -q
```

Expected: FAIL because `get_lens_recovery_client` does not exist.

- [ ] **Step 3: Implement the minimal dedicated client factory**

Add beside `get_fast_client()` in `app.py`:

```python
_lens_recovery_client = None


def get_lens_recovery_client():
    """Client for one bounded structured sector-lens recovery request."""
    global _lens_recovery_client
    if _lens_recovery_client is None:
        _lens_recovery_client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            timeout=httpx.Timeout(timeout=120.0, connect=10.0),
            max_retries=0,
        )
    return _lens_recovery_client
```

- [ ] **Step 4: Run the focused test and verify GREEN**

Run the Step 2 command again.

Expected: `1 passed`.

- [ ] **Step 5: Commit the client contract**

```powershell
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "fix: add bounded climate diagnostic recovery client"
```

### Task 2: Route recovery through the dedicated client

**Files:**
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `app.py:1045-1170`

- [ ] **Step 1: Write the failing default-client regression test**

Add a small helper that returns a valid delimited diagnostic response and this test:

```python
def test_lens_diagnostic_repair_uses_recovery_client_not_fast_client(monkeypatch):
    repaired_payload = {
        "lenses": [{
            "lens_id": "climate",
            "applicability": "material",
            "materiality_level": "medium",
            "materiality_summary": "Flood and conflict pressures affect delivery.",
            "interaction_readout": [
                {"direction_id": "climate-fcv-on-project", "summary": "Delivery risk."},
                {"direction_id": "project-on-climate-fcv", "summary": "Distribution risk."},
            ],
            "readout_sections": [],
            "additional_pathways": [],
        }],
        "findings": [],
    }

    class FakeMessages:
        def create(self, **kwargs):
            text = (
                app_module.LENS_DIAGNOSTIC_START
                + json.dumps(repaired_payload)
                + app_module.LENS_DIAGNOSTIC_END
            )
            return type("Response", (), {
                "content": [type("Text", (), {"text": text})()]
            })()

    recovery_client = type("Client", (), {"messages": FakeMessages()})()
    monkeypatch.setattr(
        app_module, "get_lens_recovery_client", lambda: recovery_client
    )
    monkeypatch.setattr(
        app_module,
        "get_fast_client",
        lambda: (_ for _ in ()).throw(AssertionError("fast client used")),
    )

    repaired, recovered = app_module.repair_lens_diagnostic(
        "Visible Stage 2 assessment",
        ["climate"],
        {"climate": set()},
        {"climate": {"invest-in": set(), "deliver-through": set()}},
    )

    assert recovered is True
    assert repaired["lenses"][0]["materiality_level"] == "medium"
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
python -m pytest tests/test_sector_lens_app_contract.py::test_lens_diagnostic_repair_uses_recovery_client_not_fast_client -q
```

Expected: FAIL with `AssertionError: fast client used`.

- [ ] **Step 3: Make the minimal production change**

Change the default client expression in `repair_lens_diagnostic()` from:

```python
(client or get_fast_client()).messages.create(...)
```

to:

```python
(client or get_lens_recovery_client()).messages.create(...)
```

- [ ] **Step 4: Run the test and verify GREEN**

Run the Step 2 command again.

Expected: `1 passed`.

- [ ] **Step 5: Run both recovery success tests**

Run:

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -k "lens_diagnostic_repair" -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit the routing fix**

```powershell
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "fix: route climate recovery through dedicated client"
```

### Task 3: Prove invalid and timed-out recovery remains safe

**Files:**
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `app.py:1045-1170`

- [ ] **Step 1: Write the invalid-response regression test**

```python
def test_lens_diagnostic_repair_rejects_incomplete_response():
    class FakeMessages:
        def create(self, **kwargs):
            text = (
                app_module.LENS_DIAGNOSTIC_START
                + json.dumps({"lenses": [], "findings": []})
                + app_module.LENS_DIAGNOSTIC_END
            )
            return type("Response", (), {
                "content": [type("Text", (), {"text": text})()]
            })()

    client = type("Client", (), {"messages": FakeMessages()})()
    repaired, recovered = app_module.repair_lens_diagnostic(
        "Visible Stage 2 assessment",
        ["climate"],
        {"climate": set()},
        {"climate": {"invest-in": set(), "deliver-through": set()}},
        client=client,
    )

    assert recovered is False
    assert app_module.lens_diagnostic_failure_message(
        repaired, ["climate"]
    )
```

- [ ] **Step 2: Write the provider-timeout regression test**

```python
def test_lens_diagnostic_timeout_preserves_core_warning_state(caplog):
    class TimeoutMessages:
        def create(self, **kwargs):
            request = app_module.httpx.Request(
                "POST", "https://api.anthropic.com/v1/messages"
            )
            raise app_module.anthropic.APITimeoutError(request=request)

    client = type("Client", (), {"messages": TimeoutMessages()})()
    with caplog.at_level("WARNING", logger=app_module.app.logger.name):
        repaired, recovered = app_module.repair_lens_diagnostic(
            "Visible Stage 2 assessment",
            ["climate"],
            {"climate": set()},
            {"climate": {"invest-in": set(), "deliver-through": set()}},
            client=client,
            assessment_id="assessment-test",
        )

    assert recovered is False
    assert repaired["error"] is True
    assert "APITimeoutError" in caplog.text
    assert "assessment-test" in caplog.text
```

- [ ] **Step 3: Run the new tests and verify RED for assessment-aware logging**

Run:

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -k "incomplete_response or timeout_preserves" -q
```

Expected: the incomplete-response test passes against existing validation, while the timeout test fails because `repair_lens_diagnostic()` does not yet accept or log `assessment_id`.

- [ ] **Step 4: Add bounded elapsed-time and assessment logging**

Update `repair_lens_diagnostic()` to accept `assessment_id: str = ""`, capture `started_at = time.monotonic()`, and log the elapsed milliseconds on both the normal and exception paths. Pass `assessment_id` from `extract_or_repair_lens_diagnostic()`.

The normal-path log must use this shape:

```python
app.logger.info(
    "Lens diagnostic recovery completed: assessment_id=%s "
    "elapsed_ms=%d recovered=%s",
    assessment_id or "unknown",
    round((time.monotonic() - started_at) * 1000),
    recovered,
)
```

The exception log must use this shape:

```python
app.logger.warning(
    "Lens diagnostic recovery request failed: assessment_id=%s "
    "elapsed_ms=%d error=%s",
    assessment_id or "unknown",
    round((time.monotonic() - started_at) * 1000),
    type(exc).__name__,
)
```

- [ ] **Step 5: Run the new tests and verify GREEN**

Run the Step 3 command again.

Expected: both selected tests pass.

- [ ] **Step 6: Run the complete sector-lens contract file**

Run:

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit failure-safety and observability**

```powershell
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "fix: make climate recovery failures observable and safe"
```

### Task 4: Update architecture documentation and verify the repository

**Files:**
- Modify: `CLAUDE.md`
- Modify: `docs/reference/reference_backend_routes.md`

- [ ] **Step 1: Document the recovery architecture**

Add a v9.18 entry to `CLAUDE.md` stating that missing or incomplete active-lens diagnostics use one dedicated Haiku recovery request with a 120-second default/read timeout, no SDK retries, strict validation, and identical Express/step-by-step behaviour. Update the current version from v9.17 to v9.18.

Extend the Stage 2 sector-lens paragraph in `docs/reference/reference_backend_routes.md` with the same operational contract. Clarify that v9.18 adds no further SSE fields, name the already-existing additive `lens_diagnostic_recovered` flag, and state that the diagnostic schema remains compatible.

- [ ] **Step 2: Run formatting and focused regression checks**

Run:

```powershell
python -m pytest tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py -q
```

Expected: all tests pass.

- [ ] **Step 3: Run the full repository suite**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass with zero failures.

- [ ] **Step 4: Verify the staged diff**

Run:

```powershell
git diff --check
git status --short
git diff -- app.py tests/test_sector_lens_app_contract.py CLAUDE.md docs/reference/reference_backend_routes.md
```

Expected: no whitespace errors; only the planned implementation, tests, and documentation are changed.

- [ ] **Step 5: Commit the documentation and final verified state**

```powershell
git add CLAUDE.md docs/reference/reference_backend_routes.md
git commit -m "docs: document climate diagnostic recovery reliability"
```

- [ ] **Step 6: Request code review**

Review the branch diff from `9acc2b1` to `HEAD` against the approved design. Fix every critical or important finding and rerun the focused and full suites after any change.

- [ ] **Step 7: Push the completed branch**

```powershell
git push origin codex/climate-fcv-output-redesign
```

Expected: the remote branch advances to the verified implementation commit.
