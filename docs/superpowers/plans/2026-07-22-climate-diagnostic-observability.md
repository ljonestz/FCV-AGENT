# Climate Diagnostic Recovery Observability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add privacy-safe structural telemetry that reveals why a returned Climate-FCV recovery response fails validation.

**Architecture:** A pure helper in `app.py` will classify only allowlisted structural properties of the raw recovery response and normalized diagnostic. `repair_lens_diagnostic()` will emit that summary at warning level only when a returned response fails validation; exception and success behavior remain unchanged.

**Tech Stack:** Python 3, Flask logging, `json`, `re`, pytest, pytest `caplog`

---

### Task 1: Add the safe structural-summary helper

**Files:**
- Modify: `tests/test_sector_lens_app_contract.py:523-850`
- Modify: `app.py:986-1044`

- [ ] **Step 1: Write failing helper tests**

Add `import pytest` after the existing standard-library imports:

```python
import pytest
```

Then add these tests after `test_lens_diagnostic_failure_names_parser_errors_and_missing_entries`:

```python
@pytest.mark.parametrize(
    ("response_text", "expected_status"),
    [
        ("no diagnostic delimiters", "missing_delimiters"),
        (
            app_module.LENS_DIAGNOSTIC_START
            + "{not valid json}"
            + app_module.LENS_DIAGNOSTIC_END,
            "invalid_json",
        ),
    ],
)
def test_lens_recovery_structure_classifies_unparseable_responses(
    response_text, expected_status
):
    summary = app_module.lens_recovery_structure(
        response_text,
        {"error": True, "message": "Recovery invalid."},
        ["climate"],
    )

    assert summary["json_status"] == expected_status
    assert summary["climate_entry_present"] is False
    assert summary["materiality_present"] is False
    assert summary["recognized_interactions"] == []


def test_lens_recovery_structure_reports_only_allowlisted_shape():
    sentinel = "SECRET PROJECT EVIDENCE MUST NOT LEAK"
    raw_payload = {
        "lenses": [{
            "lens_id": "climate",
            "materiality_summary": sentinel,
            "interaction_readout": [{
                "direction_id": "climate-fcv-on-project",
                "summary": sentinel,
                "untrusted_key": sentinel,
            }],
            "untrusted_key": sentinel,
        }],
        "findings": [{"evidence": [sentinel]}],
        "untrusted_key": sentinel,
    }
    response_text = (
        app_module.LENS_DIAGNOSTIC_START
        + json.dumps(raw_payload)
        + app_module.LENS_DIAGNOSTIC_END
    )
    normalized = {
        "lenses": [{
            "lens_id": "climate",
            "materiality_level": "",
            "materiality_summary": sentinel,
            "interaction_readout": [{
                "direction_id": "climate-fcv-on-project",
                "summary": sentinel,
            }],
        }],
        "findings": [],
    }

    summary = app_module.lens_recovery_structure(
        response_text, normalized, ["climate"]
    )
    serialized = json.dumps(summary, sort_keys=True)

    assert summary["json_status"] == "valid_object"
    assert summary["lenses_list"] is True
    assert summary["lens_count"] == 1
    assert summary["findings_list"] is True
    assert summary["finding_count"] == 1
    assert summary["climate_entry_present"] is True
    assert summary["materiality_present"] is False
    assert summary["materiality_valid"] is False
    assert summary["recognized_interactions"] == [
        "climate-fcv-on-project"
    ]
    assert summary["missing_required_interactions"] == []
    assert sentinel not in serialized
    assert "untrusted_key" not in serialized
```

- [ ] **Step 2: Run the helper tests and verify RED**

Run:

```powershell
python -m pytest -q -p no:cacheprovider tests/test_sector_lens_app_contract.py -k "lens_recovery_structure"
```

Expected: both test functions fail with `AttributeError: module 'app' has no attribute 'lens_recovery_structure'`.

- [ ] **Step 3: Implement the minimal pure helper**

Add this function immediately after `lens_diagnostic_failure_message()`:

```python
def lens_recovery_structure(
    response_text: str,
    diagnostic: dict[str, Any],
    active_lens_ids: list[str],
) -> dict[str, Any]:
    """Return privacy-safe structural facts about a recovery response."""

    text = response_text or ""
    has_start = LENS_DIAGNOSTIC_START in text
    has_end = LENS_DIAGNOSTIC_END in text
    summary: dict[str, Any] = {
        "response_chars": len(text),
        "start_delimiter": has_start,
        "end_delimiter": has_end,
        "json_status": "missing_delimiters",
        "lenses_list": False,
        "lens_count": 0,
        "findings_list": False,
        "finding_count": 0,
        "climate_entry_present": False,
        "materiality_present": False,
        "materiality_valid": False,
        "recognized_interactions": [],
        "missing_required_interactions": [],
        "failure_reason": lens_diagnostic_failure_message(
            diagnostic, active_lens_ids
        ),
    }
    if not (has_start and has_end):
        return summary
    match = re.search(
        re.escape(LENS_DIAGNOSTIC_START)
        + r"(.*?)"
        + re.escape(LENS_DIAGNOSTIC_END),
        text,
        re.DOTALL,
    )
    if not match:
        return summary
    try:
        payload = json.loads(match.group(1).strip())
    except (json.JSONDecodeError, TypeError, ValueError):
        summary["json_status"] = "invalid_json"
        return summary
    if not isinstance(payload, dict):
        summary["json_status"] = "valid_non_object"
        return summary

    summary["json_status"] = "valid_object"
    raw_lenses = payload.get("lenses")
    raw_findings = payload.get("findings")
    summary["lenses_list"] = isinstance(raw_lenses, list)
    summary["lens_count"] = min(len(raw_lenses), 99) if isinstance(
        raw_lenses, list
    ) else 0
    summary["findings_list"] = isinstance(raw_findings, list)
    summary["finding_count"] = min(len(raw_findings), 99) if isinstance(
        raw_findings, list
    ) else 0

    climate = next((
        item for item in raw_lenses or []
        if isinstance(item, dict) and item.get("lens_id") == "climate"
    ), None) if isinstance(raw_lenses, list) and "climate" in active_lens_ids else None
    if not climate:
        return summary

    summary["climate_entry_present"] = True
    summary["materiality_present"] = "materiality_level" in climate
    level = str(climate.get("materiality_level", "")).lower()
    summary["materiality_valid"] = level in {"high", "medium", "low"}
    allowed_directions = {
        "climate-fcv-on-project", "project-on-climate-fcv"
    }
    recognized = sorted({
        str(item.get("direction_id"))
        for item in climate.get("interaction_readout", [])
        if isinstance(item, dict)
        and item.get("direction_id") in allowed_directions
    })
    summary["recognized_interactions"] = recognized
    if level in {"high", "medium"}:
        summary["missing_required_interactions"] = sorted(
            allowed_directions - set(recognized)
        )
    return summary
```

- [ ] **Step 4: Run the helper tests and verify GREEN**

Run:

```powershell
python -m pytest -q -p no:cacheprovider tests/test_sector_lens_app_contract.py -k "lens_recovery_structure"
```

Expected: `3 passed`.

- [ ] **Step 5: Commit the helper**

```powershell
git add -- app.py tests/test_sector_lens_app_contract.py
git commit -m "chore: add safe climate recovery telemetry"
```

### Task 2: Log unsuccessful returned recovery structure

**Files:**
- Modify: `tests/test_sector_lens_app_contract.py:659-724`
- Modify: `app.py:1111-1130`

- [ ] **Step 1: Write the failing warning-log test**

Add this test after `test_lens_diagnostic_repair_rejects_missing_climate_materiality_level`:

```python
def test_unsuccessful_lens_recovery_logs_safe_structure(caplog):
    sentinel = "SECRET PROJECT EVIDENCE MUST NOT LEAK"
    incomplete_payload = {
        "lenses": [{
            "lens_id": "climate",
            "materiality_summary": sentinel,
            "interaction_readout": [{
                "direction_id": "climate-fcv-on-project",
                "summary": sentinel,
            }],
        }],
        "findings": [],
    }

    class FakeMessages:
        def create(self, **kwargs):
            text = (
                app_module.LENS_DIAGNOSTIC_START
                + json.dumps(incomplete_payload)
                + app_module.LENS_DIAGNOSTIC_END
            )
            return type("Response", (), {
                "content": [type("Text", (), {"text": text})()]
            })()

    client = type("Client", (), {"messages": FakeMessages()})()
    with caplog.at_level("WARNING", logger=app_module.app.logger.name):
        _, recovered = app_module.repair_lens_diagnostic(
            "Visible Stage 2 assessment",
            ["climate"],
            {"climate": set()},
            {"climate": {"invest-in": set(), "deliver-through": set()}},
            client=client,
            assessment_id="assessment-structure",
        )

    assert recovered is False
    assert "Lens diagnostic recovery invalid" in caplog.text
    assert "assessment-structure" in caplog.text
    assert '"json_status":"valid_object"' in caplog.text
    assert '"materiality_present":false' in caplog.text
    assert sentinel not in caplog.text
```

- [ ] **Step 2: Run the warning test and verify RED**

Run:

```powershell
python -m pytest -q -p no:cacheprovider tests/test_sector_lens_app_contract.py::test_unsuccessful_lens_recovery_logs_safe_structure
```

Expected: failure because the `Lens diagnostic recovery invalid` warning is absent.

- [ ] **Step 3: Add the warning-level integration**

In `repair_lens_diagnostic()`, immediately after calculating `recovered`, add:

```python
        if not recovered:
            structure = lens_recovery_structure(
                response_text, repaired, active_lens_ids
            )
            app.logger.warning(
                "Lens diagnostic recovery invalid: assessment_id=%s "
                "structure=%s",
                assessment_id or "unknown",
                json.dumps(
                    structure,
                    ensure_ascii=True,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
```

- [ ] **Step 4: Run the warning test and verify GREEN**

Run:

```powershell
python -m pytest -q -p no:cacheprovider tests/test_sector_lens_app_contract.py::test_unsuccessful_lens_recovery_logs_safe_structure
```

Expected: `1 passed`.

- [ ] **Step 5: Run focused recovery contracts**

Run:

```powershell
python -m pytest -q -p no:cacheprovider tests/test_sector_lens_app_contract.py -k "lens_diagnostic or lens_recovery"
```

Expected: all selected tests pass, including unchanged timeout, successful recovery, and client configuration tests.

- [ ] **Step 6: Run the complete suite**

Run:

```powershell
python -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```

Expected: all tests pass; baseline before this plan is `284 passed`.

- [ ] **Step 7: Commit the warning integration**

```powershell
git add -- app.py tests/test_sector_lens_app_contract.py
git commit -m "chore: log invalid climate recovery structure"
```

### Task 3: Verify scope and prepare one production diagnostic rerun

**Files:**
- Inspect: `app.py`
- Inspect: `tests/test_sector_lens_app_contract.py`
- Inspect: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`

- [ ] **Step 1: Verify the diff is telemetry-only**

Run:

```powershell
git diff 386b1af..HEAD -- app.py tests/test_sector_lens_app_contract.py docs/superpowers/specs/2026-07-22-climate-diagnostic-observability-design.md docs/superpowers/plans/2026-07-22-climate-diagnostic-observability.md
```

Expected: only the safe helper, its failed-recovery warning integration, tests, design, and plan. No prompt, timeout, parser, SSE, frontend, or report changes.

- [ ] **Step 2: Confirm parity impact**

Read the shared-contract list in `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`.

Expected: no delimiter, priority JSON, prompt constant, rating, request, SSE, or diagnostic schema change; therefore no parity-log update is required.

- [ ] **Step 3: Stop before deployment**

Report the commit IDs and test results. Do not push, deploy, or rerun production without explicit user direction.
