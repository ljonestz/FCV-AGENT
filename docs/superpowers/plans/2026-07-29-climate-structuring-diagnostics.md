# Climate Structuring Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add privacy-safe production telemetry that identifies how the Haiku climate structuring response fails without changing runtime behavior.

**Architecture:** A pure helper in `sector_lenses/research.py` will reduce untrusted response text and provider metadata to allowlisted structural facts. `run_climate_web_research()` will emit one correlated log entry only after a structuring call, while retaining the existing prompt, model, limits, parser, evidence gate, and user-facing failure behavior.

**Tech Stack:** Python, Flask logging, Anthropic SDK response objects, pytest

---

### Task 1: Specify the privacy-safe diagnostic contract

**Files:**
- Modify: `tests/test_climate_research.py`
- Modify: `sector_lenses/research.py`

- [ ] **Step 1: Import the planned helper in the focused test module**

Add `summarize_climate_structuring_response` to the existing import from
`sector_lenses.research`.

- [ ] **Step 2: Write failing structural and privacy tests**

Add tests equivalent to:

```python
def test_climate_structuring_diagnostic_reports_truncation_without_text():
    secret = "SECRET PROJECT EVIDENCE Upper Nile https://example.invalid"
    text = CLIMATE_RESEARCH_START + '{"status":"partial","sources":[' + secret
    usage = SimpleNamespace(input_tokens=1200, output_tokens=2500)

    summary = summarize_climate_structuring_response(
        text,
        usage=usage,
        stop_reason="max_tokens",
        gate_code="climate_research_failed",
    )

    assert summary == {
        "stop_reason": "max_tokens",
        "input_tokens": 1200,
        "output_tokens": 2500,
        "response_chars": len(text),
        "start_present": True,
        "end_present": False,
        "json_status": "incomplete",
        "top_level_object": False,
        "fields_present": ("status", "sources"),
        "sources_count": -1,
        "claims_count": -1,
        "gate_code": "climate_research_failed",
    }
    assert secret not in repr(summary)


def test_climate_structuring_diagnostic_reports_complete_object_shape():
    payload = {
        "status": "complete",
        "attempts": 1,
        "sources": [{}, {}],
        "claims": [{}, {}, {}, {}],
        "failure_reason": "",
        "SECRET ARBITRARY KEY": "SECRET VALUE",
    }
    text = (
        CLIMATE_RESEARCH_START
        + json.dumps(payload)
        + CLIMATE_RESEARCH_END
    )

    summary = summarize_climate_structuring_response(
        text,
        usage={"input_tokens": 900, "output_tokens": 700},
        stop_reason="end_turn",
        gate_code="",
    )

    assert summary["json_status"] == "valid"
    assert summary["top_level_object"] is True
    assert summary["fields_present"] == (
        "status", "attempts", "sources", "claims", "failure_reason"
    )
    assert summary["sources_count"] == 2
    assert summary["claims_count"] == 4
    assert "SECRET" not in repr(summary)
```

- [ ] **Step 3: Run the two tests and confirm the helper is missing**

Run:

```powershell
python -m pytest -q -p no:cacheprovider `
  tests/test_climate_research.py::test_climate_structuring_diagnostic_reports_truncation_without_text `
  tests/test_climate_research.py::test_climate_structuring_diagnostic_reports_complete_object_shape
```

Expected: collection/import failure because
`summarize_climate_structuring_response` is not defined.

- [ ] **Step 4: Implement the minimal pure helper**

In `sector_lenses/research.py`, add a helper with this interface:

```python
def summarize_climate_structuring_response(
    text: str,
    *,
    usage: Any = None,
    stop_reason: Any = "",
    gate_code: Any = "",
) -> dict[str, Any]:
    """Return bounded, content-free structural telemetry."""
```

Implementation requirements:

- cap token and character counts at `9_999_999`;
- accept usage as either an object or dictionary;
- allowlist stop reasons to `end_turn`, `max_tokens`, `stop_sequence`,
  `pause_turn`, `refusal`, and `unknown`;
- allowlist gate codes to `ok`, `climate_research_failed`, and
  `climate_research_insufficient`;
- detect the two delimiters independently;
- parse JSON only when both delimiters exist;
- report `json_status` as `valid`, `invalid`, `incomplete`, or `absent`;
- inspect only the allowlisted top-level fields `status`, `attempts`,
  `sources`, `claims`, and `failure_reason`;
- use `-1` when a source or claim count is unavailable;
- never return response text, payload values, arbitrary keys, or exceptions.

- [ ] **Step 5: Run the two tests and confirm they pass**

Run the command from Step 3.

Expected: `2 passed`.

- [ ] **Step 6: Commit the pure diagnostic contract**

```powershell
git add -- sector_lenses/research.py tests/test_climate_research.py
git commit -m "test: define climate structuring diagnostics"
```

### Task 2: Integrate one correlated production log

**Files:**
- Modify: `sector_lenses/__init__.py`
- Modify: `app.py`
- Modify: `tests/test_climate_research.py`

- [ ] **Step 1: Write a failing integration-log test**

Construct a first response with two `web_search_tool_result` blocks and a second
response containing a truncated delimited payload, `stop_reason="max_tokens"`,
and usage counts. Capture the Flask logger and assert:

```python
assert "outcome=structuring_diagnostic" in caplog.text
assert "assessment_id=assessment-diagnostic" in caplog.text
assert "stop_reason=max_tokens" in caplog.text
assert "output_tokens=2500" in caplog.text
assert "start_present=yes end_present=no" in caplog.text
assert "json_status=incomplete" in caplog.text
assert "gate_code=climate_research_failed" in caplog.text
assert secret not in caplog.text
```

Also assert the returned bundle remains failed and the API call count remains
two, proving the diagnostic does not retry or alter the evidence gate.

- [ ] **Step 2: Run the integration test and confirm the log is absent**

Run:

```powershell
python -m pytest -q -p no:cacheprovider `
  tests/test_climate_research.py::test_climate_structuring_diagnostic_is_logged_without_content
```

Expected: FAIL because `outcome=structuring_diagnostic` is absent.

- [ ] **Step 3: Export and import the diagnostic helper**

Add `summarize_climate_structuring_response` to the research imports and
`__all__` in `sector_lenses/__init__.py`, then import it in `app.py`.

- [ ] **Step 4: Track whether the structuring call occurred**

In `run_climate_web_research()`, initialize `structured_response = False`
immediately before evaluating the first response. Set it to `True` only after
the tools-disabled Haiku call returns.

- [ ] **Step 5: Emit one fixed-format structural log**

After parsing the final text and computing the evidence gate, call the helper
only when `structured_response` is true. Log fixed fields:

```python
diagnostic = summarize_climate_structuring_response(
    text,
    usage=getattr(response, "usage", None),
    stop_reason=getattr(response, "stop_reason", ""),
    gate_code=gate.get("code") or "ok",
)
app.logger.info(
    "Climate research attempt assessment_id=%s attempt=%d "
    "outcome=structuring_diagnostic stop_reason=%s "
    "input_tokens=%d output_tokens=%d response_chars=%d "
    "start_present=%s end_present=%s json_status=%s "
    "top_level_object=%s fields_present=%s sources_count=%d "
    "claims_count=%d gate_code=%s",
    assessment_id or "unknown",
    attempt,
    diagnostic["stop_reason"],
    diagnostic["input_tokens"],
    diagnostic["output_tokens"],
    diagnostic["response_chars"],
    "yes" if diagnostic["start_present"] else "no",
    "yes" if diagnostic["end_present"] else "no",
    diagnostic["json_status"],
    "yes" if diagnostic["top_level_object"] else "no",
    ",".join(diagnostic["fields_present"]) or "none",
    diagnostic["sources_count"],
    diagnostic["claims_count"],
    diagnostic["gate_code"],
)
```

- [ ] **Step 6: Run the integration test and confirm it passes**

Run the command from Step 2.

Expected: `1 passed`.

- [ ] **Step 7: Run focused regression verification**

Run:

```powershell
python -m pytest -q -p no:cacheprovider tests/test_climate_research.py tests/test_climate_workflow_contract.py
python -m py_compile app.py sector_lenses/research.py sector_lenses/__init__.py
git diff --check
```

Expected: all tests pass; compilation and diff checks exit zero.

- [ ] **Step 8: Confirm the behavioral boundary**

Inspect the staged diff and verify it does not change:

- `build_climate_search_prompt`;
- `build_climate_research_prompt`;
- model names;
- `max_tokens`;
- search-tool limits;
- timeouts or deadlines;
- parsing, evidence-gate, retry, or user-facing failure logic.

- [ ] **Step 9: Commit and push the diagnostic checkpoint**

```powershell
git add -- app.py sector_lenses/__init__.py sector_lenses/research.py tests/test_climate_research.py
git add -f -- docs/superpowers/plans/2026-07-29-climate-structuring-diagnostics.md
git commit -m "chore: diagnose climate structuring responses"
git push origin HEAD:refs/heads/feat/climate-readout-redesign
```

### Task 3: Run one controlled production diagnostic

**Files:**
- Inspect only: Render deployment logs

- [ ] **Step 1: Confirm the deployed build hash**

Wait for the startup log to identify the new diagnostic commit hash before
starting an assessment.

- [ ] **Step 2: Run the same climate assessment once**

Use the same project document and Climate lens selection. Do not retry after
the first result.

- [ ] **Step 3: Capture the correlated diagnostic line**

Copy the `outcome=structuring_diagnostic` line and its assessment ID from the
Render log. The line must contain only the structural fields specified above.

- [ ] **Step 4: Select the next hypothesis from evidence**

- `start_present=yes`, `end_present=no`, `json_status=incomplete`,
  `output_tokens=2500`: output truncation is confirmed.
- `start_present=no`: instruction adherence or leading-output behavior is the
  next target.
- both delimiters present with `json_status=invalid`: serialization validity is
  the next target.
- valid JSON with missing fields or zero counts: schema adherence or evidence
  normalization is the next target.

Do not combine functional changes across these branches. Design one minimal fix
for the observed branch only.
