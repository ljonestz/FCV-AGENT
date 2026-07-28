# Climate-FCV Native Reliability Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the overloaded generic-FCV-plus-climate path with a mandatory-research, climate-native workflow whose versioned structured payload drives the live readout, climate-specific priorities, and every export.

**Architecture:** Climate selection becomes an explicit branch in both express and step-by-step workflows. A focused `sector_lenses/climate_native.py` module owns the versioned Stage 2 and Stage 3 prompt contracts plus deterministic repair planning; `sector_lenses/research.py` owns the external-evidence gate; `app.py` remains responsible for API calls, deadlines, SSE events, and route orchestration. The standard FCV route remains byte-for-byte unchanged except for shared helpers that are proven neutral by regression tests.

**Tech Stack:** Python 3.13, Flask, Anthropic Python SDK, httpx, server-sent events, vanilla JavaScript, python-docx, Node-based frontend contract tests, pytest.

---

## Scope and sequencing

This is one end-to-end plan because the routing, mandatory research gate,
canonical payload, recovery, priorities, and renderer changes are not safely
deployable as independent features. Each task is independently testable and
committed, but the branch must not be preview-deployed until Tasks 1-10 are
complete.

Do not implement on `main`. Work only in:

```text
C:\Users\wb559324\OneDrive - WBG\Documents\GitHub\FCV-AGENT\.worktrees\climate-readout
```

Branch:

```text
feat/climate-readout-redesign
```

Do not read the restricted raw OPCS corpus. Use the existing approved summaries,
guardrails, source notes, and Copilot/WBG review outputs already represented in
the branch.

## File map

### Create

- `sector_lenses/climate_native.py`
  - Versioned climate payload contract.
  - Dedicated Stage 2 prompt builder.
  - Dedicated Stage 3 climate-priority prompt builder.
  - Missing-field repair plan and deterministic repair merge.
- `tests/test_climate_native.py`
  - Pure contract, prompt-isolation, completeness, repair-merge, and specificity
    tests.
- `tests/test_climate_workflow_contract.py`
  - Express/step-by-step fail-closed behavior, SSE keepalive, and route-selection
    tests.

### Modify

- `sector_lenses/research.py`
  - Mandatory research evidence gate and deadline-aware attempt policy.
- `sector_lenses/pipeline.py`
  - Versioned canonical payload normalization.
  - Compact FCV baseline, executive summary, operating context, and
    supplementary-question fields.
  - Complete-readout validation.
- `sector_lenses/__init__.py`
  - Export new public helpers and constants.
- `climate_question_bank.py`
  - Return stable anchor and supplementary candidate plans.
- `app.py`
  - Research deadline ownership.
  - Typed fail-closed SSE events.
  - Dedicated climate routing in both workflows.
  - Background/observable bounded recovery.
  - Climate-only Stage 3 call.
  - DOCX parity and telemetry.
- `index.html`
  - Climate-specific progress language.
  - Blocking research/generation failure actions.
  - Canonical structured readout rendering.
  - Shared/downloaded HTML parity.
- `tests/test_climate_research.py`
  - Evidence gate and deadline tests.
- `tests/test_climate_question_bank.py`
  - Supplementary-candidate selection tests.
- `tests/test_climate_diagnostic_completeness.py`
  - Versioned completeness and repair tests.
- `tests/test_sector_lens_pipeline.py`
  - Normalization and schema-version tests.
- `tests/test_sector_lens_app_contract.py`
  - Full assembled prompt isolation, Stage 3 priority contract, DOCX parity,
    and telemetry tests.
- `tests/test_climate_lens_frontend.py`
  - Failure actions, canonical order, supplementary questions, and HTML export
    parity.
- `tests/fixtures/climate/south_sudan_dual_use.json`
  - Canonical versioned payload and accepted research sources.
- `CLAUDE.md`
  - Version history and current climate execution contract.
- `docs/20260728_climate_module_reliability_handoff.md`
  - Implementation status, commits, verification, and preview instructions.
- `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`
  - Private divergence-log entry after the Render contract is implemented and
    verified. Never copy this file into the public repository.

## Task 1: Add the mandatory climate research evidence gate

**Files:**

- Modify: `sector_lenses/research.py`
- Modify: `sector_lenses/__init__.py`
- Test: `tests/test_climate_research.py`

- [ ] **Step 1: Write failing evidence-gate tests**

Append:

```python
from sector_lenses.research import climate_research_evidence_gate


def _second_authoritative_source():
    return {
        "id": "climate-source-2",
        "source_type": "scientific",
        "title": "Peer-reviewed flood projection",
        "url": "https://ipcc.ch/example",
        "publication_date": "2024",
    }


def test_climate_research_gate_accepts_two_sources_and_project_claim():
    bundle = _valid_bundle()
    bundle["sources"].append(_second_authoritative_source())
    bundle["claims"][0]["source_ids"].append("climate-source-2")

    decision = climate_research_evidence_gate(bundle)

    assert decision["ok"] is True
    assert decision["code"] == ""
    assert len(decision["bundle"]["sources"]) == 2


def test_climate_research_gate_rejects_one_source():
    decision = climate_research_evidence_gate(_valid_bundle())

    assert decision["ok"] is False
    assert decision["code"] == "climate_research_insufficient"
    assert "two relevant sources" in decision["message"]


def test_climate_research_gate_rejects_claim_without_climate_anchor():
    bundle = _valid_bundle()
    bundle["sources"].append(_second_authoritative_source())
    bundle["claims"][0]["source_ids"].append("climate-source-2")
    bundle["claims"][0]["geographies"] = []
    bundle["claims"][0]["affected_groups"] = []
    bundle["claims"][0]["systems_or_assets"] = []

    decision = climate_research_evidence_gate(bundle)

    assert decision["ok"] is False
    assert decision["code"] == "climate_research_insufficient"
```

- [ ] **Step 2: Run the tests and verify failure**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_research.py -k "research_gate" -q -p no:cacheprovider
```

Expected: collection fails because `climate_research_evidence_gate` does not
exist.

- [ ] **Step 3: Implement the pure evidence gate**

Add to `sector_lenses/research.py` after
`normalize_climate_research_bundle`:

```python
CLIMATE_AUTHORITATIVE_SOURCE_TYPES = {
    "ccdr",
    "world-bank",
    "un",
    "government",
    "scientific",
}
CLIMATE_RESEARCH_MIN_SOURCES = 2


def climate_research_evidence_gate(payload: Any) -> dict[str, Any]:
    """Return a safe decision for the mandatory Climate-FCV research gate."""

    bundle = normalize_climate_research_bundle(payload)
    sources = bundle["sources"]
    claims = bundle["claims"]
    authoritative = any(
        source["source_type"] in CLIMATE_AUTHORITATIVE_SOURCE_TYPES
        for source in sources
    )
    project_claim = any(
        claim["project_elements"]
        and (
            claim["geographies"]
            or claim["affected_groups"]
            or claim["systems_or_assets"]
        )
        for claim in claims
    )
    ok = (
        bundle["status"] in {"complete", "partial"}
        and len(sources) >= CLIMATE_RESEARCH_MIN_SOURCES
        and authoritative
        and project_claim
    )
    if ok:
        return {"ok": True, "code": "", "message": "", "bundle": bundle}
    code = (
        "climate_research_failed"
        if bundle["status"] == "failed" and not sources and not claims
        else "climate_research_insufficient"
    )
    message = (
        "The required Climate-FCV web research did not return at least two "
        "relevant sources, including authoritative climate evidence tied to "
        "this project's locations, groups, systems, or assets."
    )
    return {"ok": False, "code": code, "message": message, "bundle": bundle}
```

Export the constants and function from `sector_lenses/__init__.py`.

- [ ] **Step 4: Run the focused research tests**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_research.py -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```powershell
git add -- sector_lenses/research.py sector_lenses/__init__.py tests/test_climate_research.py
git commit -m "feat: add mandatory climate research evidence gate"
```

## Task 2: Give the parent research coordinator sole deadline ownership

**Files:**

- Modify: `app.py` functions `run_climate_web_research` and
  `_iter_stage1_research`
- Test: `tests/test_climate_research.py`

- [ ] **Step 1: Write failing deadline tests**

Append:

```python
def test_climate_retry_requires_remaining_parent_budget():
    client = _SequencedResearchClient([
        anthropic.APITimeoutError(
            request=httpx.Request(
                "POST", "https://api.anthropic.com/v1/messages"
            )
        )
    ])
    ticks = iter([100.0, 100.0, 166.0, 166.0])

    result = app_module.run_climate_web_research(
        "South Sudan",
        "Natural resources",
        {"project_elements": ["Landing sites"]},
        client,
        deadline=170.0,
        clock=lambda: next(ticks),
        minimum_retry_seconds=35,
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 1
    assert len(client.calls) == 1


def test_climate_request_timeout_never_exceeds_parent_remaining_time():
    client = _SequencedResearchClient([_valid_climate_response()])
    ticks = iter([200.0, 200.0, 200.0])

    app_module.run_climate_web_research(
        "South Sudan",
        "Natural resources",
        {"project_elements": ["Landing sites"]},
        client,
        deadline=250.0,
        clock=lambda: next(ticks),
    )

    assert client.calls[0]["timeout"] <= 50.0


def test_parent_passes_same_deadline_to_climate_worker(monkeypatch):
    captured = {}

    def fake_climate(*args, **kwargs):
        captured["deadline"] = kwargs["deadline"]
        return normalize_climate_research_bundle({})

    monkeypatch.setattr(app_module, "run_climate_web_research", fake_climate)
    monkeypatch.setattr(
        app_module,
        "run_fcv_web_research",
        lambda *args, **kwargs: {"brief": "core"},
    )
    monkeypatch.setattr(app_module, "get_research_client", lambda: object())
    app_module._research_cache.clear()
    plan = {
        "country": "Testland",
        "sector": "Water",
        "core": {"max_tokens": 100, "max_uses": 1},
        "climate": {"enabled": True},
        "project_profile": {},
    }

    list(app_module._iter_stage1_research(
        plan, "assessment-deadline", budget_seconds=30
    ))

    assert captured["deadline"] > 0
```

- [ ] **Step 2: Run the tests and verify failure**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_research.py -k "remaining_parent or parent_passes or never_exceeds" -q -p no:cacheprovider
```

Expected: failures because the current research function has no deadline
arguments and `_iter_stage1_research` does not pass one.

- [ ] **Step 3: Make each attempt consume only remaining parent time**

Change the function signature and attempt loop:

```python
CLIMATE_RESEARCH_ATTEMPT_CAP_SECONDS = 85
CLIMATE_RESEARCH_MINIMUM_RETRY_SECONDS = 35


def run_climate_web_research(
    country: str,
    sector: str,
    project_profile: dict[str, Any],
    api_client,
    assessment_id: str = "",
    deadline: float | None = None,
    clock=time.monotonic,
    minimum_retry_seconds: int = CLIMATE_RESEARCH_MINIMUM_RETRY_SECONDS,
) -> dict[str, Any]:
    """Run deadline-aware Climate research with at most one narrow retry."""

    started = time.perf_counter()

    def finish(bundle: dict[str, Any]) -> dict[str, Any]:
        log_climate_research_summary(
            assessment_id,
            bundle,
            elapsed_ms=int((time.perf_counter() - started) * 1000),
        )
        return bundle

    attempts = 0
    for attempt, narrow in ((1, False), (2, True)):
        remaining = (
            CLIMATE_RESEARCH_ATTEMPT_CAP_SECONDS
            if deadline is None
            else max(0.0, deadline - clock())
        )
        if remaining <= 0:
            break
        if attempt == 2 and remaining < minimum_retry_seconds:
            break
        attempts = attempt
        prompt = build_climate_research_prompt(
            country, sector, project_profile, narrow=narrow
        )
        try:
            response = api_client.beta.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=3200 if narrow else 5000,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 3 if narrow else 5,
                }],
                messages=[{"role": "user", "content": prompt}],
                betas=["web-search-2025-03-05"],
                timeout=min(remaining, CLIMATE_RESEARCH_ATTEMPT_CAP_SECONDS),
            )
            text = "\n".join(
                block.text
                for block in response.content
                if getattr(block, "type", "") == "text"
            )
            _, bundle = extract_climate_research_bundle(text)
            bundle["attempts"] = attempt
            if climate_research_evidence_gate(bundle)["ok"]:
                return finish(bundle)
        except anthropic.APITimeoutError:
            continue
        except Exception:
            break
    return finish(normalize_climate_research_bundle({
        "status": "failed",
        "attempts": attempts,
        "failure_reason": "Dedicated Climate-FCV research could not be completed.",
    }))
```

In `_iter_stage1_research`, pass the existing `deadline`:

```python
futures[pool.submit(
    run_climate_web_research,
    country,
    sector,
    research_plan["project_profile"],
    get_research_client(),
    assessment_id,
    deadline=deadline,
)] = "climate"
```

When a climate future remains pending at the parent deadline, normalize the
result to a failed bundle before yielding the final result:

```python
if timed_out and climate_enabled and "climate" in futures.values():
    results["climate_research"] = normalize_climate_research_bundle({
        "status": "failed",
        "attempts": 1,
        "failure_reason": "Climate research exceeded the assessment deadline.",
    })
    results["lens_context_sources"] = []
```

- [ ] **Step 4: Run the research suite**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_research.py -q -p no:cacheprovider
```

Expected: all tests pass without sleeping past the parent test budget.

- [ ] **Step 5: Commit**

```powershell
git add -- app.py tests/test_climate_research.py
git commit -m "fix: align climate research retries with parent deadline"
```

## Task 3: Define the versioned canonical climate payload

**Files:**

- Create: `sector_lenses/climate_native.py`
- Modify: `sector_lenses/pipeline.py`
- Modify: `sector_lenses/__init__.py`
- Create: `tests/test_climate_native.py`
- Modify: `tests/test_sector_lens_pipeline.py`
- Modify: `tests/test_climate_diagnostic_completeness.py`

- [ ] **Step 1: Write failing canonical-payload tests**

Create `tests/test_climate_native.py`:

```python
import copy

from sector_lenses import (
    CLIMATE_NATIVE_SCHEMA_VERSION,
    climate_readout_is_complete,
    normalize_lens_diagnostic,
)


def canonical_payload():
    return {
        "schema_version": CLIMATE_NATIVE_SCHEMA_VERSION,
        "fcv_baseline": {
            "sensitivity_rating": "Adequate",
            "responsiveness_rating": "Emerging",
            "sensitivity_reasoning": "Conflict-sensitive delivery is explicit.",
            "responsiveness_reasoning": "Some root-cause pathways are present.",
            "evidence_trail": [
                {
                    "claim": "Landing-site access is seasonally constrained.",
                    "source_ids": ["climate-source-1"],
                    "project_anchor": "Sub-component 1.2 landing sites",
                }
            ],
        },
        "lenses": [{
            "lens_id": "climate",
            "applicability": "material",
            "materiality_level": "high",
            "materiality_summary": "Flooding and insecurity interact.",
            "executive_summary": (
                "Flood access and benefit allocation are the material intersection."
            ),
            "integration_level": "partly_integrated",
            "integration_rating": "Adequate",
            "integration_summary": "Hazards are recognized but allocation is incomplete.",
            "operating_context": {
                "fcv_setting": "Jonglei access is institutionally constrained.",
                "climate_setting": "Flood timing affects landing-site access.",
                "intersection": (
                    "Sub-component 1.2 depends on contested seasonal access."
                ),
            },
            "interaction_readout": [],
            "reflections": [{
                "question_key": "cq2_maladaptation",
                "title": "Could the design lock in maladaptation?",
                "status_cue": "partial gap",
                "source": "FCV-Sensitive Climate Action Framework",
                "text": "The siting decision may entrench unequal access.",
            }],
            "supplementary_questions": [{
                "question_id": "cq5-hdp-nexus",
                "title": "Does delivery connect to humanitarian coordination?",
                "status_cue": "unconfirmed",
                "source": "Defueling Conflict",
                "text": "The project names displaced groups but not the coordination forum.",
            }],
            "strengths_weaknesses": [{
                "side": "strength",
                "title": "Community co-management",
                "text": "Sub-component 2.1 uses named local institutions.",
            }, {
                "side": "gap",
                "title": "Seasonal access",
                "text": "The operations manual lacks a flood-access decision rule.",
            }],
            "readout_sections": [],
            "additional_pathways": [],
            "other_pathways": [],
        }],
        "findings": [],
    }


def test_canonical_payload_requires_current_schema_version():
    payload = canonical_payload()
    normalized = normalize_lens_diagnostic(payload, ["climate"])
    assert normalized["schema_version"] == CLIMATE_NATIVE_SCHEMA_VERSION

    stale = copy.deepcopy(payload)
    stale["schema_version"] = "climate-native-v0"
    rejected = normalize_lens_diagnostic(stale, ["climate"])
    assert rejected["error"] is True


def test_canonical_payload_normalizes_baseline_and_context():
    normalized = normalize_lens_diagnostic(
        canonical_payload(), ["climate"]
    )
    climate = normalized["lenses"][0]
    assert normalized["fcv_baseline"]["sensitivity_rating"] == "Adequate"
    assert climate["executive_summary"].startswith("Flood access")
    assert climate["operating_context"]["intersection"].startswith(
        "Sub-component 1.2"
    )
    assert climate["supplementary_questions"][0]["question_id"] == (
        "cq5-hdp-nexus"
    )


def test_complete_readout_requires_baseline_context_and_both_interactions():
    normalized = normalize_lens_diagnostic(
        canonical_payload(), ["climate"]
    )
    assert climate_readout_is_complete(
        normalized["lenses"][0],
        baseline=normalized["fcv_baseline"],
    ) is False
```

- [ ] **Step 2: Run and verify failure**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_native.py -q -p no:cacheprovider
```

Expected: import and assertion failures because the version and new fields are
undefined.

- [ ] **Step 3: Add the focused climate-native module**

Create `sector_lenses/climate_native.py`:

```python
"""Pure contracts and prompt builders for the dedicated Climate-FCV route."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


CLIMATE_NATIVE_SCHEMA_VERSION = "climate-native-v1"
CLIMATE_REQUIRED_DIRECTIONS = {
    "climate-fcv-on-project",
    "project-on-climate-fcv",
}
CLIMATE_REQUIRED_LENS_FIELDS = {
    "materiality_level",
    "materiality_summary",
    "executive_summary",
    "integration_rating",
    "integration_summary",
    "operating_context",
    "interaction_readout",
    "strengths_weaknesses",
    "reflections",
}


def climate_missing_fields(payload: Any) -> list[str]:
    """Return deterministic dotted paths missing from a canonical payload."""

    if not isinstance(payload, dict):
        return ["schema_version", "fcv_baseline", "lenses.climate"]
    missing: list[str] = []
    if payload.get("schema_version") != CLIMATE_NATIVE_SCHEMA_VERSION:
        missing.append("schema_version")
    baseline = payload.get("fcv_baseline")
    if not isinstance(baseline, dict):
        missing.append("fcv_baseline")
    else:
        for key in (
            "sensitivity_rating",
            "responsiveness_rating",
            "sensitivity_reasoning",
            "responsiveness_reasoning",
            "evidence_trail",
        ):
            if not baseline.get(key):
                missing.append(f"fcv_baseline.{key}")
    lenses = payload.get("lenses")
    climate = next((
        item for item in lenses
        if isinstance(item, dict) and item.get("lens_id") == "climate"
    ), None) if isinstance(lenses, list) else None
    if climate is None:
        missing.append("lenses.climate")
        return missing
    for key in sorted(CLIMATE_REQUIRED_LENS_FIELDS):
        if not climate.get(key):
            missing.append(f"lenses.climate.{key}")
    operating = climate.get("operating_context")
    if isinstance(operating, dict):
        for key in ("fcv_setting", "climate_setting", "intersection"):
            if not operating.get(key):
                missing.append(f"lenses.climate.operating_context.{key}")
    directions = {
        item.get("direction_id")
        for item in climate.get("interaction_readout", [])
        if isinstance(item, dict)
    }
    for direction in sorted(CLIMATE_REQUIRED_DIRECTIONS - directions):
        missing.append(f"lenses.climate.interaction_readout.{direction}")
    return missing


def merge_climate_repair(
    primary: dict[str, Any],
    repair: dict[str, Any],
    requested_fields: list[str],
) -> dict[str, Any]:
    """Merge only requested top-level or Climate-lens fields."""

    result = deepcopy(primary) if isinstance(primary, dict) else {}
    allowed = set(requested_fields)
    if "schema_version" in allowed:
        result["schema_version"] = repair.get("schema_version")
    if any(path == "fcv_baseline" or path.startswith("fcv_baseline.") for path in allowed):
        existing = result.get("fcv_baseline")
        incoming = repair.get("fcv_baseline")
        result["fcv_baseline"] = {
            **(existing if isinstance(existing, dict) else {}),
            **(incoming if isinstance(incoming, dict) else {}),
        }
    result_lenses = result.setdefault("lenses", [])
    result_climate = next((
        item for item in result_lenses
        if isinstance(item, dict) and item.get("lens_id") == "climate"
    ), None)
    repair_climate = next((
        item for item in repair.get("lenses", [])
        if isinstance(item, dict) and item.get("lens_id") == "climate"
    ), None) if isinstance(repair, dict) else None
    if result_climate is None and isinstance(repair_climate, dict):
        result_climate = {"lens_id": "climate"}
        result_lenses.append(result_climate)
    if isinstance(result_climate, dict) and isinstance(repair_climate, dict):
        for path in allowed:
            prefix = "lenses.climate."
            if not path.startswith(prefix):
                continue
            key = path[len(prefix):].split(".", 1)[0]
            if key in repair_climate:
                result_climate[key] = deepcopy(repair_climate[key])
    result.setdefault("findings", [])
    return result
```

Export the constant and functions from `sector_lenses/__init__.py`.

- [ ] **Step 4: Normalize the versioned fields in the pipeline**

In `sector_lenses/pipeline.py`:

1. Import `CLIMATE_NATIVE_SCHEMA_VERSION`.
2. Add bounded normalizers for the baseline, operating context, and
   supplementary questions.
3. Retain up to four supplementary questions with IDs present in
   `climate_question_bank.CLIMATE_QUESTION_BANK`.
4. Return `schema_version` and `fcv_baseline` at the top level.
5. When Climate is active, reject a non-empty payload whose schema version is
   missing or stale.

Use:

```python
def _normalize_climate_baseline(value: Any) -> dict[str, Any]:
    raw = value if isinstance(value, dict) else {}
    trail = []
    for item in _list_values(raw.get("evidence_trail")):
        if not isinstance(item, dict):
            continue
        claim = str(item.get("claim", "")).strip()[:500]
        anchor = str(item.get("project_anchor", "")).strip()[:240]
        if claim and anchor:
            trail.append({
                "claim": claim,
                "project_anchor": anchor,
                "source_ids": _bounded_strings(
                    item.get("source_ids"), 4, 100
                ),
            })
        if len(trail) >= 6:
            break
    return {
        "sensitivity_rating": str(
            raw.get("sensitivity_rating", "")
        ).strip()[:80],
        "responsiveness_rating": str(
            raw.get("responsiveness_rating", "")
        ).strip()[:80],
        "sensitivity_reasoning": str(
            raw.get("sensitivity_reasoning", "")
        ).strip()[:900],
        "responsiveness_reasoning": str(
            raw.get("responsiveness_reasoning", "")
        ).strip()[:900],
        "evidence_trail": trail,
    }


def _normalize_operating_context(value: Any) -> dict[str, str]:
    raw = value if isinstance(value, dict) else {}
    return {
        key: str(raw.get(key, "")).strip()[:1400]
        for key in ("fcv_setting", "climate_setting", "intersection")
    }
```

Update `climate_readout_is_complete` to accept a keyword-only baseline:

```python
def climate_readout_is_complete(
    climate_entry: dict[str, Any] | None,
    *,
    baseline: dict[str, Any] | None = None,
) -> bool:
    if not isinstance(climate_entry, dict):
        return False
    baseline = baseline if isinstance(baseline, dict) else {}
    baseline_complete = all(
        baseline.get(key)
        for key in (
            "sensitivity_rating",
            "responsiveness_rating",
            "sensitivity_reasoning",
            "responsiveness_reasoning",
            "evidence_trail",
        )
    )
    context = climate_entry.get("operating_context")
    context_complete = isinstance(context, dict) and all(
        context.get(key)
        for key in ("fcv_setting", "climate_setting", "intersection")
    )
    directions = {
        item.get("direction_id")
        for item in climate_entry.get("interaction_readout", [])
        if isinstance(item, dict) and item.get("pathways")
    }
    return bool(
        baseline_complete
        and climate_entry.get("executive_summary")
        and climate_entry.get("integration_rating")
        and climate_entry.get("integration_summary")
        and context_complete
        and CLIMATE_REQUIRED_DIRECTIONS.issubset(directions)
        and climate_entry.get("strengths_weaknesses")
        and climate_entry.get("reflections")
    )
```

Update existing callers and fixtures to pass the top-level baseline.

- [ ] **Step 5: Run contract suites**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_native.py tests/test_sector_lens_pipeline.py tests/test_climate_diagnostic_completeness.py -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```powershell
git add -- sector_lenses/climate_native.py sector_lenses/pipeline.py sector_lenses/__init__.py tests/test_climate_native.py tests/test_sector_lens_pipeline.py tests/test_climate_diagnostic_completeness.py
git commit -m "feat: define canonical climate assessment payload"
```

## Task 4: Allow material source-derived questions beyond the six anchors

**Files:**

- Modify: `climate_question_bank.py`
- Modify: `sector_lenses/pipeline.py`
- Modify: `tests/test_climate_question_bank.py`
- Modify: `tests/test_climate_native.py`

- [ ] **Step 1: Write failing question-plan tests**

Append to `tests/test_climate_question_bank.py`:

```python
def test_question_plan_keeps_anchors_and_supplementary_candidates():
    plan = bank.build_question_plan(
        "flood displacement humanitarian coordination cold storage"
    )

    assert "cq1_interaction" in plan["anchors"]
    assert any(
        item["id"] == "cq5-hdp-nexus"
        for item in plan["supplementary_candidates"]
    )


def test_question_plan_deduplicates_supplementary_candidates():
    plan = bank.build_question_plan(
        "displacement refugee host humanitarian hdp nexus"
    )
    ids = [item["id"] for item in plan["supplementary_candidates"]]
    assert len(ids) == len(set(ids))
```

- [ ] **Step 2: Run and verify failure**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_question_bank.py -k "question_plan" -q -p no:cacheprovider
```

Expected: failures because `build_question_plan` does not exist.

- [ ] **Step 3: Add a deterministic plan without replacing the six themes**

Add to `climate_question_bank.py`:

```python
def build_question_plan(project_signals: Any) -> dict[str, Any]:
    """Return stable anchor groups plus distinct source-derived candidates."""

    anchors = select_triggered_questions(project_signals)
    candidates = []
    seen = set()
    for questions in anchors.values():
        for question in questions:
            question_id = question["id"]
            if question_id in seen:
                continue
            seen.add(question_id)
            candidates.append({
                "id": question_id,
                "theme": question["theme"],
                "question": question["question"],
                "source": question["source"],
            })
    return {
        "anchors": anchors,
        "supplementary_candidates": candidates,
    }
```

The prompt will permit zero to four surfaced supplementary answers, but it must
state that this is a payload bound, not a coverage target. A supplementary
candidate is surfaced only when it adds a distinct project-specific issue that
is not adequately covered in the anchor answer.

- [ ] **Step 4: Add strict supplementary-ID normalization tests**

Add to `tests/test_climate_native.py`:

```python
def test_unknown_supplementary_question_id_is_dropped():
    payload = canonical_payload()
    payload["lenses"][0]["supplementary_questions"][0][
        "question_id"
    ] = "invented-question"

    normalized = normalize_lens_diagnostic(payload, ["climate"])

    assert normalized["lenses"][0]["supplementary_questions"] == []
```

Implement the normalizer against the declared bank IDs:

```python
_CLIMATE_BANK_IDS = {
    item["id"] for item in climate_question_bank.CLIMATE_QUESTION_BANK
}


def _normalize_supplementary_questions(value: Any) -> list[dict[str, str]]:
    result = []
    for raw in _list_values(value):
        if not isinstance(raw, dict):
            continue
        question_id = str(raw.get("question_id", "")).strip()
        text = str(raw.get("text", "")).strip()[:1800]
        if question_id not in _CLIMATE_BANK_IDS or not text:
            continue
        result.append({
            "question_id": question_id,
            "title": str(raw.get("title", "")).strip()[:200],
            "status_cue": _soften_status_cue(
                raw.get("status_cue", "")
            )[:40],
            "source": str(raw.get("source", "")).strip()[:160],
            "text": text,
        })
        if len(result) >= 4:
            break
    return result
```

- [ ] **Step 5: Run question and pipeline tests**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_question_bank.py tests/test_climate_native.py tests/test_sector_lens_pipeline.py -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```powershell
git add -- climate_question_bank.py sector_lenses/pipeline.py tests/test_climate_question_bank.py tests/test_climate_native.py
git commit -m "feat: support supplementary climate questions"
```

## Task 5: Build dedicated Climate Stage 2 and Stage 3 prompts

**Files:**

- Modify: `sector_lenses/climate_native.py`
- Modify: `sector_lenses/__init__.py`
- Modify: `tests/test_climate_native.py`
- Modify: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing full-prompt isolation tests**

Add to `tests/test_climate_native.py`:

```python
from sector_lenses import (
    build_climate_stage2_prompt,
    build_climate_stage3_prompt,
)


GENERIC_ENGINE_MARKERS = (
    "12 OST",
    "12 operational standards",
    "DNH-9",
    "9 Do No Harm",
    "25 key diagnostic questions",
    "%%%UNDER_HOOD_START%%%",
    "recommendation-by-recommendation table",
)


def test_climate_stage2_prompt_is_complete_and_generic_free():
    prompt = build_climate_stage2_prompt(
        instrument_type="IPF",
        document_type="Project Paper",
        temporal_guardrail="Use current preparation-stage evidence.",
        regime_header="New preparation model; ESF.",
        project_signals="flood displacement cold storage community committee",
        climate_research={
            "status": "complete",
            "attempts": 1,
            "sources": [],
            "claims": [],
        },
        priority_questions=[],
    )

    for marker in GENERIC_ENGINE_MARKERS:
        assert marker.lower() not in prompt.lower()
    assert CLIMATE_NATIVE_SCHEMA_VERSION in prompt
    assert "fcv_baseline" in prompt
    assert "operating_context" in prompt
    assert "supplementary_questions" in prompt
    assert "single source of truth" in prompt.lower()
    assert "instrument-route" in prompt.lower()


def test_climate_stage3_prompt_requests_priorities_only():
    prompt = build_climate_stage3_prompt(
        instrument_type="IPF",
        document_type="Project Paper",
        diagnostic=canonical_payload(),
        regime_header="New preparation model; ESF.",
    )

    assert "priorities" in prompt
    assert "approximately three" in prompt.lower()
    assert "opening assessment" not in prompt.lower()
    assert "strengths section" not in prompt.lower()
    assert "wider fcv context" not in prompt.lower()
    assert "authority_basis" in prompt
```

- [ ] **Step 2: Run and verify failure**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_native.py -k "stage2_prompt or stage3_prompt" -q -p no:cacheprovider
```

Expected: import failures because the prompt builders do not exist.

- [ ] **Step 3: Implement the Stage 2 builder**

Add to `sector_lenses/climate_native.py`. Import
`build_question_plan` and `format_climate_research_context`.

The function must generate one bounded prompt containing:

```python
def build_climate_stage2_prompt(
    *,
    instrument_type: str,
    document_type: str,
    temporal_guardrail: str,
    regime_header: str,
    project_signals: str,
    climate_research: dict[str, Any],
    priority_questions: list[str],
) -> str:
    """Build the complete dedicated Climate-FCV Stage 2 prompt."""

    from climate_question_bank import build_question_plan
    from .research import format_climate_research_context

    question_plan = build_question_plan(project_signals)
    question_text = "\n".join(
        f"- [{item['id']}] {item['question']} "
        f"(analytical source: {item['source']})"
        for item in question_plan["supplementary_candidates"]
    )
    research_text = format_climate_research_context(climate_research)
    user_focus = "\n".join(
        f"- {str(value).strip()}"
        for value in priority_questions
        if str(value).strip()
    )
    prompt = f"""
You are producing the dedicated Climate-FCV assessment for a World Bank
{document_type} using the {instrument_type} instrument.

This is a climate-native route. Do not run, enumerate, summarize, or recreate
the generic 12-standard FCV assessment, the nine-part Do No Harm checklist, the
25-question map, or the generic FCV recommendation table.

Return one versioned structured assessment between
%%%LENS_DIAGNOSTIC_START%%% and %%%LENS_DIAGNOSTIC_END%%%. This payload is the
single source of truth for the reader-facing assessment. Do not write duplicate
visible and hidden versions of the same sections.

Required top-level keys:
- schema_version: {CLIMATE_NATIVE_SCHEMA_VERSION}
- fcv_baseline
- lenses: exactly one Climate lens
- findings

The compact fcv_baseline contains sensitivity_rating,
responsiveness_rating, sensitivity_reasoning, responsiveness_reasoning, and
three to six evidence_trail objects. It is informed by relevant FCV principles
but must not enumerate the full generic FCV machinery.

The Climate lens contains materiality_level, materiality_summary,
executive_summary, integration_level, integration_rating,
integration_summary, operating_context with fcv_setting, climate_setting, and
intersection, both interaction directions, detailed strengths_weaknesses,
material reflections under the six anchor themes, zero to four distinct
supplementary_questions, readout_sections, additional_pathways,
other_pathways, and source_ids.

Both interaction directions are mandatory. Every major finding follows:
pressure -> mediated mechanism -> named project implication -> current design
response or gap -> proportionate operational adaptation.

Name project components, subcomponents, activities, locations, beneficiary
groups, institutions, delivery arrangements, indicators, financing
arrangements, and document sections wherever the evidence supports them.
Suppress generic content. Never fabricate absent specificity.

Supplementary questions are not a coverage target. Surface one only when a
triggered source question adds a distinct, material project issue not already
answered under its anchor theme.

CLIMATE-FCV QUESTION CANDIDATES:
{question_text}

VALIDATED EXTERNAL RESEARCH:
{research_text}

USER FOCUS:
{user_focus}

TEMPORAL CONTEXT:
{temporal_guardrail}

PROCESS CONTEXT:
{regime_header}

OPCS CALIBRATION:
Instrument-route every operational observation before naming a process:
IPF uses ESF instruments; PforR uses ESSA, PAP, DLIs, and borrower systems;
DPF uses the Program Document, prior actions, PSIA, and SORT. Flag but never
determine Paris Alignment, CDRS, ESF, ESS, ESRC, resilience, or screening
adequacy. Separate analytical good practice from policy, directive, procedure,
and guidance. Use an asset-appropriate design horizon rather than a universal
numeric horizon. Use conditional compound-risk language such as "may
intensify" and "could interact with"; never state that climate change will
cause conflict or that the project guarantees a peace dividend.

Return no prose after %%%LENS_DIAGNOSTIC_END%%%.
""".strip()
    return prompt
```

Keep the current detailed pathway, integration-scale, source, and
instrument-calibration field instructions by moving them into this builder.
Do not retain a second copy in `build_lens_stage_context`.

- [ ] **Step 4: Implement the priorities-only Stage 3 builder**

Add:

```python
def build_climate_stage3_prompt(
    *,
    instrument_type: str,
    document_type: str,
    diagnostic: dict[str, Any],
    regime_header: str,
) -> str:
    """Build the dedicated Climate Stage 3 priority request."""

    compact = json.dumps(
        diagnostic,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"""
Generate only climate-specific operational priorities for this World Bank
{document_type} using the {instrument_type} instrument.

Use the validated Climate-FCV assessment below as the sole analytical source.
Do not regenerate an opening assessment, operating context, strengths,
weaknesses, core questions, wider FCV context, or generic FCV priorities.

Return approximately three priorities; return more only when the evidence
clearly warrants it and never more than five. Every priority must cite a
recognized Climate-FCV pathway, question, finding, component, location,
beneficiary group, institution, or document section from the payload.

Instrument-route every action. Populate authority_basis using exactly policy,
directive, procedure, guidance, or reviewer_judgment. Flag but never determine
Paris Alignment, CDRS, ESF, ESS, ESRC, or resilience. Apply the existing CERC,
AF, restructuring, MPA, conditional-language, and analytical-source
guardrails.

Return one JSON object between %%%JSON_START%%% and %%%JSON_END%%% containing
fcv_rating, fcv_responsiveness_rating, sensitivity_summary,
responsiveness_summary, risk_exposure, empty non-applicable watch arrays, and
priorities. Copy the compact baseline ratings and reasoning without
reassessing them. Each priority uses the existing application priority schema,
including climate_links and authority_basis.

PROCESS CONTEXT:
{regime_header}

VALIDATED CLIMATE-FCV ASSESSMENT:
{compact}
""".strip()
```

Add `import json` to the module and export both builders.

- [ ] **Step 5: Replace obsolete suffix assertions**

In `tests/test_sector_lens_app_contract.py`, remove tests whose intended fix is
"make the climate block a mandatory sibling of UNDER_HOOD." Replace them with a
test that assembles the actual route prompt and checks all generic markers are
absent. The route-level test will be completed in Task 6.

- [ ] **Step 6: Run the pure prompt tests**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_native.py tests/test_sector_lens_app_contract.py -k "climate and prompt" -q -p no:cacheprovider
```

Expected: all selected tests pass.

- [ ] **Step 7: Commit**

```powershell
git add -- sector_lenses/climate_native.py sector_lenses/__init__.py tests/test_climate_native.py tests/test_sector_lens_app_contract.py
git commit -m "feat: add dedicated climate stage prompts"
```

## Task 6: Route both workflows through mandatory research and dedicated Stage 2

**Files:**

- Modify: `app.py`
- Create: `tests/test_climate_workflow_contract.py`
- Modify: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing route-selection tests**

Create `tests/test_climate_workflow_contract.py`:

```python
import json

import app as app_module
from test_climate_native import canonical_payload


def _decode_sse(events):
    decoded = []
    for event in events:
        if isinstance(event, bytes):
            event = event.decode("utf-8")
        for line in str(event).splitlines():
            if line.startswith("data: "):
                decoded.append(json.loads(line[6:]))
    return decoded


def test_climate_failure_event_is_typed_and_actionable():
    event = app_module.climate_blocking_failure_event(
        "climate_research_failed",
        "Research failed.",
        failed_stage=1,
    )

    assert event == {
        "error": "Research failed.",
        "error_code": "climate_research_failed",
        "failed_stage": 1,
        "retryable": True,
        "fallback": "full_fcv",
    }


def test_route_prompt_selector_uses_dedicated_climate_prompt():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"],
        "structured_intake": {"instrument": "IPF", "doc_type": "PAD"},
    })

    prompt = app_module.build_design_stage2_prompt(
        state=state,
        instrument_type="IPF",
        document_type="PAD",
        temporal_guardrail="Preparation stage.",
        regime_header="ESF.",
        project_signals="flood displacement landing sites",
        climate_research={"status": "complete", "sources": [], "claims": []},
        priority_questions=[],
    )

    assert "single source of truth" in prompt.lower()
    assert "12 Recommendations, 25 Key Questions" not in prompt
    assert "%%%UNDER_HOOD_START%%%" not in prompt
```

- [ ] **Step 2: Run and verify failure**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_workflow_contract.py -q -p no:cacheprovider
```

Expected: failures because the shared failure and route prompt helpers do not
exist.

- [ ] **Step 3: Add shared orchestration helpers**

In `app.py`, import the new research gate and prompt builders. Add:

```python
def climate_active(state: AnalysisState) -> bool:
    return "climate" in (state.active_lenses or [])


def climate_blocking_failure_event(
    code: str,
    message: str,
    *,
    failed_stage: int,
) -> dict[str, Any]:
    return {
        "error": message,
        "error_code": code,
        "failed_stage": failed_stage,
        "retryable": True,
        "fallback": "full_fcv",
    }


def build_design_stage2_prompt(
    *,
    state: AnalysisState,
    instrument_type: str,
    document_type: str,
    temporal_guardrail: str,
    regime_header: str,
    project_signals: str,
    climate_research: dict[str, Any],
    priority_questions: list[str],
) -> str:
    if climate_active(state):
        return build_climate_stage2_prompt(
            instrument_type=instrument_type,
            document_type=document_type,
            temporal_guardrail=temporal_guardrail,
            regime_header=regime_header,
            project_signals=project_signals,
            climate_research=climate_research,
            priority_questions=priority_questions,
        )
    return ""
```

The empty non-climate result is intentional: both route call sites retain their
existing generic prompt assembly unchanged when `climate_active(state)` is
false.

- [ ] **Step 4: Fail closed immediately after research in both routes**

In `run_stage` Stage 1 and `run_express` Stage 1, after
`_iter_stage1_research` returns:

```python
if climate_active(analysis_state):
    research_decision = climate_research_evidence_gate(climate_research)
    climate_research = research_decision["bundle"]
    if not research_decision["ok"]:
        event = climate_blocking_failure_event(
            research_decision["code"],
            research_decision["message"],
            failed_stage=1,
        )
        app.logger.warning(
            "Climate workflow stopped: assessment_id=%s code=%s stage=1",
            assessment_id or "unknown",
            event["error_code"],
        )
        yield f"data: {json.dumps(event)}\n\n"
        return
```

Do not catch this deliberate stop in the broad research exception and then
continue. The stop occurs after the research `try/except`.

- [ ] **Step 5: Branch before generic Stage 2 assembly**

At both Stage 2 call sites:

```python
if climate_active(analysis_state):
    stage2_prompt = build_design_stage2_prompt(
        state=analysis_state,
        instrument_type=instrument_type,
        document_type=document_type,
        temporal_guardrail=temporal_guardrail,
        regime_header=regime_header,
        project_signals=_climate_project_signals(
            analysis_state, sector_context, stage1_output[:2500]
        ),
        climate_research=climate_research,
        priority_questions=priority_questions,
    )
else:
    # Indent the current generic Stage 2 assembly under this branch; its final statement must continue to assign stage2_prompt.
```

Move the current generic background concatenation, CPF note, differentiated
approach, secondary snippets, CATEGORY_LENS block, and generic lens suffix
inside the `else` branch. Do not append `build_lens_stage_context(analysis_state, stage=2)["prompt"]` to the dedicated climate prompt.

For Climate Stage 2:

- use a 16,000-token cap initially;
- do not parse `UNDER_HOOD` or `CATEGORY_LENS`;
- derive ratings from `lens_diagnostic["fcv_baseline"]`;
- set the Stage 2 display text from the canonical payload renderer rather than
  free-form model prose.

- [ ] **Step 6: Add a route-level assembled-prompt assertion**

Use a fake `_stream_stage` in `tests/test_climate_workflow_contract.py` to
capture `messages[-1]["content"]` from `/api/run-express`, return a canonical
payload, and assert the captured prompt lacks every `GENERIC_ENGINE_MARKERS`
entry. Add the corresponding no-climate test and assert the generic markers
remain present.

- [ ] **Step 7: Run route and regression contract tests**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_workflow_contract.py tests/test_sector_lens_app_contract.py tests/test_climate_research.py -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```powershell
git add -- app.py tests/test_climate_workflow_contract.py tests/test_sector_lens_app_contract.py
git commit -m "feat: route climate runs through native stage two"
```

## Task 7: Replace load-bearing recovery with observable field-level repair

**Files:**

- Modify: `sector_lenses/climate_native.py`
- Modify: `app.py`
- Modify: `tests/test_climate_native.py`
- Modify: `tests/test_climate_diagnostic_completeness.py`
- Modify: `tests/test_climate_workflow_contract.py`
- Modify: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing deterministic merge tests**

Add to `tests/test_climate_native.py`:

```python
def test_repair_merge_changes_only_requested_fields():
    primary = canonical_payload()
    primary["lenses"][0]["integration_summary"] = ""
    repair = canonical_payload()
    repair["lenses"][0]["executive_summary"] = "UNREQUESTED CHANGE"
    repair["lenses"][0]["integration_summary"] = "Repaired summary."

    merged = merge_climate_repair(
        primary,
        repair,
        ["lenses.climate.integration_summary"],
    )

    assert merged["lenses"][0]["integration_summary"] == "Repaired summary."
    assert merged["lenses"][0]["executive_summary"] == (
        primary["lenses"][0]["executive_summary"]
    )
```

- [ ] **Step 2: Write failing observable recovery test**

Add to `tests/test_climate_workflow_contract.py`:

```python
def test_recovery_emits_keepalive_before_slow_result(monkeypatch):
    events = list(app_module._iter_climate_diagnostic_recovery(
        primary={"schema_version": "climate-native-v1", "lenses": []},
        missing_fields=["lenses.climate"],
        active_lens_ids=["climate"],
        source_ids_by_lens={"climate": set()},
        readout_schema_by_lens={"climate": {}},
        assessment_id="assessment-recovery",
        client=SlowRecoveryClient(delay_seconds=0.05),
        max_seconds=1,
        keepalive_interval=0.01,
    ))

    assert any(event.get("recovery_status") == "repairing" for event in events)
    assert any(event.get("keepalive") is True for event in events)
    assert "result" in events[-1]
```

Add `import time` and `from types import SimpleNamespace`, then define this fake
in the test file:

```python
class SlowRecoveryClient:
    def __init__(self, delay_seconds: float):
        self.delay_seconds = delay_seconds
        self.messages = self

    def create(self, **_kwargs):
        time.sleep(self.delay_seconds)
        diagnostic = canonical_payload()
        content = (
            "%%%LENS_DIAGNOSTIC_START%%%"
            + json.dumps(diagnostic)
            + "%%%LENS_DIAGNOSTIC_END%%%"
        )
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=content)]
        )
```

- [ ] **Step 3: Run and verify failure**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_native.py tests/test_climate_workflow_contract.py -k "repair" -q -p no:cacheprovider
```

Expected: failure because the recovery iterator does not exist and the current
repair regenerates the full diagnostic synchronously.

- [ ] **Step 4: Build a field-specific repair prompt**

Add to `sector_lenses/climate_native.py`:

```python
def build_climate_repair_prompt(
    *,
    primary: dict[str, Any],
    missing_fields: list[str],
    source_ids_by_lens: dict[str, set[str]],
) -> str:
    requested = "\n".join(f"- {path}" for path in missing_fields)
    payload = json.dumps(
        primary, ensure_ascii=False, separators=(",", ":")
    )[:24000]
    sources = json.dumps(
        {
            lens_id: sorted(values)
            for lens_id, values in source_ids_by_lens.items()
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"""
Repair only the listed fields in a Climate-FCV structured assessment.
Return one object between %%%LENS_DIAGNOSTIC_START%%% and
%%%LENS_DIAGNOSTIC_END%%%. Preserve the schema version and include only enough
surrounding structure to validate and merge the requested fields. Do not
regenerate or rewrite valid fields. Do not invent evidence.

REQUESTED FIELDS:
{requested}

ALLOWED SOURCE IDS:
{sources}

VALIDATED PRIMARY PAYLOAD:
{payload}
""".strip()
```

- [ ] **Step 5: Add the background recovery iterator**

Replace the direct climate call in `repair_lens_diagnostic` with:

```python
CLIMATE_RECOVERY_MAX_SECONDS = 90
CLIMATE_RECOVERY_KEEPALIVE_SECONDS = 10


def _iter_climate_diagnostic_recovery(
    *,
    primary: dict[str, Any],
    missing_fields: list[str],
    active_lens_ids: list[str],
    source_ids_by_lens: dict[str, set[str]],
    readout_schema_by_lens: dict[str, dict[str, set[str]]],
    assessment_id: str,
    client=None,
    max_seconds: float = CLIMATE_RECOVERY_MAX_SECONDS,
    keepalive_interval: float = CLIMATE_RECOVERY_KEEPALIVE_SECONDS,
):
    import queue as recovery_queue

    queue = recovery_queue.Queue()
    started = time.monotonic()
    prompt = build_climate_repair_prompt(
        primary=primary,
        missing_fields=missing_fields,
        source_ids_by_lens=source_ids_by_lens,
    )

    def run():
        try:
            response = (client or get_lens_recovery_client()).messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4500,
                messages=[{"role": "user", "content": prompt}],
                timeout=max_seconds,
            )
            text = "".join(
                str(getattr(block, "text", ""))
                for block in getattr(response, "content", [])
            )
            repaired = extract_lens_diagnostic(
                text,
                active_lens_ids,
                source_ids_by_lens,
                readout_schema_by_lens,
                strict_required_fields=True,
            )
            queue.put(("result", repaired))
        except Exception as exc:
            queue.put(("error", type(exc).__name__))

    threading.Thread(target=run, daemon=True).start()
    yield {"recovery_status": "repairing", "missing_fields": missing_fields}
    while True:
        elapsed = time.monotonic() - started
        if elapsed >= max_seconds:
            yield {
                "result": {
                    "error": True,
                    "message": "Climate diagnostic repair timed out.",
                    "lenses": [],
                    "findings": [],
                },
                "recovered": False,
                "error_code": "climate_recovery_timeout",
            }
            return
        try:
            kind, value = queue.get(
                timeout=min(keepalive_interval, max_seconds - elapsed)
            )
        except recovery_queue.Empty:
            yield {"keepalive": True, "recovery_status": "repairing"}
            continue
        if kind == "error":
            yield {
                "result": {
                    "error": True,
                    "message": "Climate diagnostic repair failed.",
                    "lenses": [],
                    "findings": [],
                },
                "recovered": False,
                "error_code": "climate_diagnostic_invalid",
            }
            return
        merged = merge_climate_repair(primary, value, missing_fields)
        normalized = normalize_lens_diagnostic(
            merged,
            active_lens_ids,
            source_ids_by_lens,
            readout_schema_by_lens,
        )
        complete = not climate_missing_fields(normalized)
        yield {
            "result": normalized,
            "recovered": complete,
            "error_code": "" if complete else "climate_diagnostic_invalid",
        }
        return
```

- [ ] **Step 6: Yield recovery progress from both Stage 2 routes**

After primary extraction:

```python
missing_fields = climate_missing_fields(lens_diagnostic)
if missing_fields:
    for recovery_event in _iter_climate_diagnostic_recovery(
        primary=lens_diagnostic,
        missing_fields=missing_fields,
        active_lens_ids=["climate"],
        source_ids_by_lens=source_ids,
        readout_schema_by_lens=readout_schema,
        assessment_id=assessment_id,
    ):
        if "result" not in recovery_event:
            yield f"data: {json.dumps(recovery_event)}\n\n"
            continue
        lens_diagnostic = recovery_event["result"]
        lens_recovered = recovery_event["recovered"]
        recovery_code = recovery_event["error_code"]
```

If recovery remains invalid, emit `climate_blocking_failure_event` and return.
Do not send a Stage 2 `done` event containing the compact baseline alone.

- [ ] **Step 7: Remove obsolete load-bearing recovery expectations**

Update tests that assert:

- an 8,000-token full diagnostic recovery;
- a 16,000-character regenerated payload;
- recovery is the â€œde-facto climate generatorâ€; or
- an incomplete primary may remain visible.

Replace them with assertions that recovery requests only missing fields,
preserves valid fields, emits keepalives, and fails the climate run if repair is
incomplete.

- [ ] **Step 8: Run recovery suites**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_native.py tests/test_climate_diagnostic_completeness.py tests/test_climate_workflow_contract.py tests/test_sector_lens_app_contract.py -k "climate or recovery or diagnostic" -q -p no:cacheprovider
```

Expected: all selected tests pass.

- [ ] **Step 9: Commit**

```powershell
git add -- sector_lenses/climate_native.py app.py tests/test_climate_native.py tests/test_climate_diagnostic_completeness.py tests/test_climate_workflow_contract.py tests/test_sector_lens_app_contract.py
git commit -m "fix: make climate recovery bounded and observable"
```

## Task 8: Make Climate Stage 3 priorities-only

**Files:**

- Modify: `app.py`
- Modify: `tests/test_climate_workflow_contract.py`
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `tests/test_extract_priorities.py`

- [ ] **Step 1: Write failing Stage 3 route tests**

Add:

```python
def test_climate_stage3_route_uses_priority_prompt_only(monkeypatch):
    captured = {}

    def capture_prompt(**kwargs):
        captured["prompt"] = kwargs["prompt"]
        return kwargs["prompt"]

    monkeypatch.setattr(
        app_module,
        "build_climate_stage3_prompt",
        capture_prompt,
    )
    prompt = app_module.build_design_stage3_prompt(
        state=app_module.AnalysisState.from_payload({
            "active_lenses": ["climate"]
        }),
        instrument_type="IPF",
        document_type="Project Paper",
        diagnostic={"schema_version": "climate-native-v1", "fcv_baseline": {"sensitivity_rating": "Adequate", "responsiveness_rating": "Emerging"}, "lenses": [{"lens_id": "climate", "integration_summary": "Flood access rules are incomplete.", "interaction_readout": [{"direction_id": "climate-fcv-on-project", "pathways": ["Flooding disrupts landing-site access."]}]}]},
        regime_header="ESF.",
    )

    assert prompt == captured["prompt"]
    assert "priorities" in prompt
```

Add a no-climate test proving the existing generic Stage 3 prompt path remains
selected.

- [ ] **Step 2: Run and verify failure**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_workflow_contract.py -k "stage3_route" -q -p no:cacheprovider
```

Expected: failure because `build_design_stage3_prompt` does not exist.

- [ ] **Step 3: Add shared Stage 3 selection**

In `app.py`:

```python
def build_design_stage3_prompt(
    *,
    state: AnalysisState,
    instrument_type: str,
    document_type: str,
    diagnostic: dict[str, Any],
    regime_header: str,
) -> str:
    if climate_active(state):
        return build_climate_stage3_prompt(
            instrument_type=instrument_type,
            document_type=document_type,
            diagnostic=diagnostic,
            regime_header=regime_header,
        )
    return ""
```

At both Stage 3 route call sites, branch before assembling the generic Stage 3
prompt:

```python
if climate_active(analysis_state):
    stage3_prompt = build_design_stage3_prompt(
        state=analysis_state,
        instrument_type=instrument_type,
        document_type=document_type,
        diagnostic=lens_diagnostic,
        regime_header=stage3_regime_header,
    )
    stage3_messages = [{
        "role": "user",
        "content": stage3_prompt,
    }]
    stage3_max_tokens = 9000
else:
    # Indent the current generic Stage 3 prompt assembly here; it must continue to assign stage3_prompt.
    # Keep the current generic message construction unchanged here.
    # Keep the current generic token cap unchanged here.
```

Do not append the old climate Stage 3 lens prefix to the dedicated prompt.

- [ ] **Step 4: Enforce climate-only priority provenance**

After `extract_priorities`, when Climate is active:

```python
valid_priorities = []
for priority in parsed.get("priorities", []):
    links = normalize_priority_climate_links(
        priority.get("climate_links"),
        lens_diagnostic,
    )
    if links.get("status") != "linked":
        continue
    priority["climate_links"] = links
    priority["lens_ids"] = ["climate"]
    valid_priorities.append(priority)
parsed["priorities"] = valid_priorities[:5]
if not parsed["priorities"]:
    parsed["error"] = True
    parsed["message"] = (
        "No validated climate-specific operational priority was produced."
    )
```

The normal target remains approximately three. One valid priority is the
minimum completion gate; five is the hard cap.

- [ ] **Step 5: Derive final climate narrative from structured data**

For a successful Climate Stage 3:

- set `result` to an empty string or a short non-analytical title;
- return the validated priorities;
- retain `lens_diagnostic`;
- do not place a second model-written climate assessment into `history`;
- use a compact history label:

```python
{
    "role": "assistant",
    "content": "[Climate-specific priorities generated from validated payload]"
}
```

- [ ] **Step 6: Run Stage 3 and priority tests**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_workflow_contract.py tests/test_sector_lens_app_contract.py tests/test_extract_priorities.py -k "climate or stage3 or priority" -q -p no:cacheprovider
```

Expected: all selected tests pass.

- [ ] **Step 7: Commit**

```powershell
git add -- app.py tests/test_climate_workflow_contract.py tests/test_sector_lens_app_contract.py tests/test_extract_priorities.py
git commit -m "feat: generate climate-specific priorities only"
```

## Task 9: Render fail-closed actions and the canonical climate readout

**Files:**

- Modify: `index.html`
- Modify: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write failing frontend failure-action tests**

Append:

```python
def test_climate_blocking_error_offers_retry_and_full_fcv():
    html = INDEX.read_text(encoding="utf-8")
    assert "showClimateBlockingError" in html
    assert "retryClimateScreening" in html
    assert "runFullFcvAssessment" in html
    assert "Retry Climate-FCV screening" in html
    assert "Run full FCV assessment" in html


def test_old_partial_climate_success_wording_is_removed():
    html = INDEX.read_text(encoding="utf-8")
    assert (
        "retains the core FCV assessment and does not add unvalidated "
        "climate findings"
    ) not in html
```

- [ ] **Step 2: Write failing canonical-order tests**

Append:

```python
def test_climate_canonical_render_order():
    html = INDEX.read_text(encoding="utf-8")
    body = html.split("function renderOut", 1)[1][:12000]
    names = [
        "renderClimateExecutiveSummary",
        "renderClimateBaseline",
        "renderClimateIntegration",
        "renderClimateOperatingContext",
        "renderClimateStrengthsWeaknesses",
        "renderClimateCoreQuestions",
        "renderClimateSupplementaryQuestions",
    ]
    positions = [body.index(name) for name in names]
    assert positions == sorted(positions)


def test_supplementary_questions_render_source_and_text():
    source = INDEX.read_text(encoding="utf-8")
    fn = _extract_js_function(
        source, "renderClimateSupplementaryQuestions"
    )
    esc = _extract_js_function(source, "esc")
    lens = {
        "supplementary_questions": [{
            "question_id": "cq5-hdp-nexus",
            "title": "Does delivery connect to humanitarian coordination?",
            "status_cue": "unconfirmed",
            "source": "Defueling Conflict",
            "text": "The project names displaced households but no forum.",
        }]
    }
    script = (
        f"{esc}\n{fn}\n"
        f"process.stdout.write("
        f"renderClimateSupplementaryQuestions({json.dumps(lens)}));"
    )
    out = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True
    )
    assert out.returncode == 0, out.stderr
    assert "humanitarian coordination" in out.stdout
    assert "Defueling Conflict" in out.stdout
```

- [ ] **Step 3: Run and verify failure**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_lens_frontend.py -k "blocking_error or canonical_render or supplementary_questions" -q -p no:cacheprovider
```

Expected: failures because the new functions do not exist.

- [ ] **Step 4: Add typed failure handling**

Add:

```javascript
let lastClimateFailure=null;

function showClimateBlockingError(payload){
  lastClimateFailure=payload||{};
  const message=esc(lastClimateFailure.error||
    'The required Climate-FCV evidence or analysis could not be completed.');
  const html='<div class="climate-module-notice climate-module-error">'+
    '<h3>Climate-FCV screening could not be completed</h3>'+
    '<p>'+message+'</p>'+
    '<div class="ep-error-actions">'+
    '<button class="btn" onclick="retryClimateScreening()">Retry Climate-FCV screening</button>'+
    '<button class="btn btn-ghost" onclick="runFullFcvAssessment()">Run full FCV assessment</button>'+
    '</div></div>';
  const target=document.getElementById('stage-disp')||
    document.getElementById('ep-summary-1');
  if(target)target.innerHTML=html;
}

function retryClimateScreening(){
  busy=false;
  lastClimateFailure=null;
  if(analysisMode==='express')runExpress();
  else runStage(1);
}

function runFullFcvAssessment(){
  activeLenses=activeLenses.filter(id=>id!=='climate');
  delete resolvedLensVersions.climate;
  lensDiagnostic={};
  lensContextSources=[];
  climateResearch={};
  climateIntegration=null;
  stageOutputs={};
  stageHists={};
  hist=[];
  curS=0;
  busy=false;
  renderLensSelector();
  if(analysisMode==='express')runExpress();
  else runStage(1);
}
```

In both SSE readers, handle a typed climate error before generic `p.error`:

```javascript
if(p.error&&p.error_code&&p.error_code.startsWith('climate_')){
  clearTimeout(activeTimeout);
  clearSbsLoadingTimers();
  showClimateBlockingError(p);
  busy=false;
  return;
}
```

Use the actual express or step-by-step timeout variable at each call site.

- [ ] **Step 5: Add canonical renderers**

Implement pure functions:

```javascript
function renderClimateExecutiveSummary(lens){
  const text=lens&&lens.executive_summary;
  return text?'<section class="climate-section"><h3>Executive summary</h3><p>'+
    esc(text)+'</p></section>':'';
}

function renderClimateBaseline(diagnostic){
  const base=diagnostic&&diagnostic.fcv_baseline;
  if(!base)return '';
  return '<section class="climate-section"><h3>Compact FCV baseline</h3>'+
    '<p><strong>FCV sensitivity: '+esc(base.sensitivity_rating||'')+
    '</strong> '+esc(base.sensitivity_reasoning||'')+'</p>'+
    '<p><strong>FCV responsiveness: '+esc(base.responsiveness_rating||'')+
    '</strong> '+esc(base.responsiveness_reasoning||'')+'</p></section>';
}

function renderClimateOperatingContext(lens){
  const ctx=lens&&lens.operating_context;
  if(!ctx)return '';
  const rows=[
    ['The FCV setting',ctx.fcv_setting],
    ['The climate setting',ctx.climate_setting],
    ['Where they meet',ctx.intersection]
  ].filter(row=>row[1]);
  return rows.length?'<section class="climate-section"><h3>Operating context</h3>'+
    rows.map(row=>'<h4>'+esc(row[0])+'</h4><p>'+esc(row[1])+'</p>').join('')+
    '</section>':'';
}

function renderClimateSupplementaryQuestions(lens){
  const items=Array.isArray(lens&&lens.supplementary_questions)?
    lens.supplementary_questions:[];
  if(!items.length)return '';
  return '<section class="climate-section"><h3>Additional questions raised by the evidence</h3>'+
    items.map(item=>'<article class="climate-question"><h4>'+
      esc(item.title||'Additional Climate-FCV question')+'</h4>'+
      (item.status_cue?'<span class="reflection-chip">'+
        esc(item.status_cue)+'</span>':'')+
      '<p>'+esc(item.text||'')+'</p>'+
      (item.source?'<p class="climate-source">Source: '+
        esc(item.source)+'</p>':'')+'</article>').join('')+
    '</section>';
}
```

Use the existing integration, strengths/weaknesses, core-question, and priority
renderers after these functions. Do not render a generic Stage 3 narrative in
Climate mode.

- [ ] **Step 6: Make progress language mode-aware**

Replace the fixed Stage 2/3 activity messages with functions that return:

- Climate Stage 2: â€œBuilding the climate and FCV assessment from project and
  external evidenceâ€¦â€
- Climate recovery: â€œValidating the structured Climate-FCV assessmentâ€¦â€
- Climate Stage 3: â€œGenerating climate-specific operational adaptationsâ€¦â€

The non-climate messages remain exactly as they are.

- [ ] **Step 7: Run frontend tests**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_lens_frontend.py -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```powershell
git add -- index.html tests/test_climate_lens_frontend.py
git commit -m "feat: render canonical climate assessment"
```

## Task 10: Make DOCX and downloaded/shared HTML use the same payload

**Files:**

- Modify: `app.py` route `/api/download-report`
- Modify: `index.html` function `downloadHTML`
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write failing DOCX parity test**

Add `import copy` if needed, then add to
`tests/test_sector_lens_app_contract.py`:

```python
def canonical_climate_download_payload():
    fixture = json.loads(
        SOUTH_SUDAN_FIXTURE.read_text(encoding="utf-8")
    )
    diagnostic = copy.deepcopy(fixture["diagnostic"])
    diagnostic["schema_version"] = "climate-native-v1"
    diagnostic["fcv_baseline"] = {
        "sensitivity_rating": "Adequate",
        "responsiveness_rating": "Emerging",
        "sensitivity_reasoning": "Delivery constraints are explicit.",
        "responsiveness_reasoning": "Adaptation pathways are partial.",
        "evidence_trail": [{
            "claim": "Flood timing affects landing-site access.",
            "source_ids": ["climate-source-1"],
            "project_anchor": "Landing-site rehabilitation",
        }],
    }
    climate = next(
        item for item in diagnostic["lenses"]
        if item.get("lens_id") == "climate"
    )
    climate["executive_summary"] = (
        "Flood access and benefit allocation are the material intersection."
    )
    climate["operating_context"] = {
        "fcv_setting": "Access and benefit allocation are contested.",
        "climate_setting": "Flood timing affects works and services.",
        "intersection": "Seasonal access affects landing-site delivery.",
    }
    climate["supplementary_questions"] = [{
        "question_id": "cq5-hdp-nexus",
        "title": "Does delivery connect to humanitarian coordination?",
        "status_cue": "unconfirmed",
        "source": "Defueling Conflict",
        "text": "The coordination forum is not named.",
    }]
    priorities = copy.deepcopy(fixture["stage3_block"]["priorities"][:3])
    return {
        "summary": "# South Sudan climate assessment",
        "priorities": priorities,
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Emerging",
        "sensitivity_summary": "Delivery constraints are explicit.",
        "responsiveness_summary": "Adaptation pathways are partial.",
        "active_lenses": [{
            "id": "climate",
            "version": "climate-native-v1",
            "position": "primary",
        }],
        "lens_diagnostic": diagnostic,
        "lens_context_sources": fixture["research_bundle"]["sources"],
        "metadata": {"date_str": "28 July 2026"},
    }


def test_climate_docx_uses_canonical_payload_order():
    payload = canonical_climate_download_payload()
    response = app_module.app.test_client().post(
        "/api/download-report", json=payload
    )

    assert response.status_code == 200
    document = Document(io.BytesIO(response.data))
    text = "\n".join(
        paragraph.text for paragraph in document.paragraphs
    )
    headings = [
        "Executive summary",
        "Compact FCV baseline",
        "How well does the project integrate climate and FCV?",
        "Operating context",
        "How the design holds up on climate and FCV",
        "Core climate and FCV questions",
        "Additional questions raised by the evidence",
        "Priority action areas",
    ]
    positions = [text.index(heading) for heading in headings]
    assert positions == sorted(positions)
    assert "12 operational standards" not in text.lower()
    assert "25 diagnostic questions" not in text.lower()
```



- [ ] **Step 2: Write failing downloaded-HTML parity test**

In `tests/test_climate_lens_frontend.py`, assert `downloadHTML()` invokes the
same canonical renderer functions in the same order as `renderOut()`, including
`renderClimateSupplementaryQuestions`.

- [ ] **Step 3: Run and verify failure**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py -k "canonical_payload_order or downloaded_html" -q -p no:cacheprovider
```

Expected: failures because DOCX and downloaded HTML do not yet render the new
fields.

- [ ] **Step 4: Add DOCX helpers**

Inside `download_report`, add:

```python
def add_climate_executive_summary():
    text = (climate_readout or {}).get("executive_summary")
    if text:
        _add_section_heading("Executive summary")
        _md_to_docx_para(doc, text)


def add_climate_baseline():
    baseline = lens_diagnostic.get("fcv_baseline", {})
    if not baseline:
        return
    _add_section_heading("Compact FCV baseline")
    add_field(
        f"FCV sensitivity - {baseline.get('sensitivity_rating', '')}",
        baseline.get("sensitivity_reasoning"),
    )
    add_field(
        f"FCV responsiveness - {baseline.get('responsiveness_rating', '')}",
        baseline.get("responsiveness_reasoning"),
    )


def add_climate_operating_context():
    context = (climate_readout or {}).get("operating_context", {})
    if not context:
        return
    _add_section_heading("Operating context")
    for heading, key in (
        ("The FCV setting", "fcv_setting"),
        ("The climate setting", "climate_setting"),
        ("Where they meet", "intersection"),
    ):
        if context.get(key):
            _add_single_para(heading, bold=True, space_after=1)
            _md_to_docx_para(doc, context[key])


def add_climate_supplementary_questions():
    items = (climate_readout or {}).get(
        "supplementary_questions", []
    )
    if not items:
        return
    _add_section_heading("Additional questions raised by the evidence")
    for item in items:
        _add_single_para(item.get("title", ""), bold=True)
        _md_to_docx_para(doc, item.get("text", ""))
        if item.get("source"):
            _add_single_para(
                f"Source: {item['source']}",
                size=9,
                color=WB_GRAY,
                italic=True,
            )
```

In Climate mode, call canonical helpers in the approved order and omit
`add_sr_sections`, `add_core_risk_exposure`, generic summary parsing, and wider
FCV context. The standard route remains unchanged.

- [ ] **Step 5: Reuse frontend canonical renderers in downloaded HTML**

`downloadHTML()` must call the same pure functions used by `renderOut()`. Do not
copy their markup into separate template strings.

- [ ] **Step 6: Run export tests**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py -k "docx or export or download or climate" -q -p no:cacheprovider
```

Expected: all selected tests pass.

- [ ] **Step 7: Commit**

```powershell
git add -- app.py index.html tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py
git commit -m "feat: align climate exports with canonical payload"
```

## Task 11: Add typed telemetry and production-like workflow tests

**Files:**

- Modify: `app.py`
- Modify: `tests/test_climate_workflow_contract.py`
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `tests/fixtures/climate/south_sudan_dual_use.json`

- [ ] **Step 1: Update the South Sudan fixture**

Add:

- two accepted external sources;
- `schema_version`;
- `fcv_baseline`;
- `executive_summary`;
- `operating_context`;
- both interaction directions with pathways;
- detailed strengths and weaknesses;
- anchor reflections;
- one distinct supplementary question; and
- three linked climate priorities.

Keep all claims and project anchors tied to the existing South Sudan fixture
facts. Do not introduce new factual content.

- [ ] **Step 2: Write a complete happy-path test**

In `tests/test_climate_workflow_contract.py`, fake:

- country/sector extraction;
- accepted research;
- Stage 1 response;
- complete primary Stage 2 canonical payload;
- Stage 3 priority JSON.

Assert:

```python
assert event_codes.count("stage_done:1") == 1
assert event_codes.count("stage_done:2") == 1
assert event_codes.count("stage_done:3") == 1
assert "climate_recovery_started" not in event_codes
assert final_event["express_done"] is True
assert len(final_event_priorities) == 3
```

The fake recovery client must raise `AssertionError` if invoked.

- [ ] **Step 3: Write production-like failure tests**

Add delayed fake clients and assert:

1. Research exceeds the parent deadline:
   - typed `climate_research_failed`;
   - no Stage 2 call.
2. Research returns one source:
   - typed `climate_research_insufficient`;
   - no Stage 2 call.
3. Stage 2 returns a partial payload:
   - recovery progress and keepalive events appear.
4. Recovery exceeds 90 seconds using a fake clock:
   - typed `climate_recovery_timeout`;
   - no Stage 3 call.
5. Stage 3 produces only unlinked priorities:
   - typed `climate_priority_invalid`;
   - no successful final event.
6. Anthropic 529 before any streamed chunk:
   - existing bounded retry remains active.

- [ ] **Step 4: Centralize safe telemetry**

Add:

```python
def log_climate_workflow_state(
    *,
    assessment_id: str,
    stage: str,
    status: str,
    elapsed_ms: int,
    error_code: str = "",
    sources: int = 0,
    claims: int = 0,
    missing_fields: int = 0,
    priorities: int = 0,
) -> None:
    app.logger.info(
        "Climate workflow assessment_id=%s stage=%s status=%s "
        "elapsed_ms=%d error_code=%s sources=%d claims=%d "
        "missing_fields=%d priorities=%d",
        assessment_id or "unknown",
        stage,
        status,
        max(0, min(int(elapsed_ms), 3_600_000)),
        error_code or "none",
        max(0, min(int(sources), 99)),
        max(0, min(int(claims), 99)),
        max(0, min(int(missing_fields), 99)),
        max(0, min(int(priorities), 9)),
    )
```

Call it at research decision, Stage 2 primary validation, recovery result, and
Stage 3 priority validation. Never log source titles, URLs, claims, project
text, prompts, or model output.

- [ ] **Step 5: Test log privacy**

Use sentinel project text, source URLs, and claims. Assert the log includes
assessment ID, stage, status, counts, and error code, but not any sentinel.

- [ ] **Step 6: Run the production-like test group**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_workflow_contract.py tests/test_climate_research.py tests/test_sector_lens_app_contract.py -q -p no:cacheprovider
```

Expected: all tests pass without real network calls.

- [ ] **Step 7: Commit**

```powershell
git add -- app.py tests/test_climate_workflow_contract.py tests/test_sector_lens_app_contract.py tests/fixtures/climate/south_sudan_dual_use.json
git commit -m "test: cover climate workflow latency and failure modes"
```

## Task 12: Full verification, documentation, parity log, and preview acceptance

**Files:**

- Modify: `CLAUDE.md`
- Modify: `docs/20260728_climate_module_reliability_handoff.md`
- Modify: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`

- [ ] **Step 1: Run the focused climate suite**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest tests/test_climate_native.py tests/test_climate_workflow_contract.py tests/test_climate_research.py tests/test_climate_question_bank.py tests/test_climate_diagnostic_completeness.py tests/test_sector_lens_pipeline.py tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py tests/test_extract_priorities.py tests/test_climate_lens_package.py tests/test_climate_ccdr_context.py -q -p no:cacheprovider
```

Expected: all focused tests pass.

- [ ] **Step 2: Run the complete regression suite**

Run:

```powershell
C:\WBG\Python313\python.exe -m pytest -q -p no:cacheprovider
```

Expected: all tests pass. Investigate every non-climate failure; do not update
expected outputs merely to accommodate accidental standard-route changes.

- [ ] **Step 3: Verify prompt isolation mechanically**

Run:

```powershell
@'
import app
state = app.AnalysisState.from_payload({
    "active_lenses": ["climate"],
    "structured_intake": {"instrument": "IPF", "doc_type": "PAD"},
})
prompt = app.build_design_stage2_prompt(
    state=state,
    instrument_type="IPF",
    document_type="PAD",
    temporal_guardrail="Preparation.",
    regime_header="ESF.",
    project_signals="flood displacement landing sites",
    climate_research={"status": "complete", "sources": [], "claims": []},
    priority_questions=[],
)
banned = (
    "12 OST",
    "%%%UNDER_HOOD_START%%%",
    "25 key diagnostic questions",
    "recommendation-by-recommendation table",
)
found = [value for value in banned if value.lower() in prompt.lower()]
print({"chars": len(prompt), "banned_found": found})
raise SystemExit(1 if found else 0)
'@ | C:\WBG\Python313\python.exe -
```

Expected: exit 0 and `banned_found` is empty.

- [ ] **Step 4: Update repository documentation**

In `CLAUDE.md`, add a version entry that records:

- dedicated climate Stage 2 and Stage 3 routing;
- mandatory fail-closed external research;
- canonical schema version;
- supplementary questions beyond the six anchors;
- observable field-level recovery;
- typed failure actions; and
- standard FCV behavior unchanged.

Update `docs/20260728_climate_module_reliability_handoff.md` with:

- implementation commit range;
- final test count;
- exact preview branch;
- known limitations;
- preview URL;
- South Sudan acceptance result; and
- next integration decision.

- [ ] **Step 5: Update the private parity contract**

Append a dated divergence-log entry to
`C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md` containing:

```text
2026-07-28 - Render climate-native reliability redesign
- Render contract: climate-native-v1.
- Climate selection bypasses generic 12-OST/DNH-9/25-question Stage 2.
- External Climate-FCV research is mandatory and fail-closed.
- Stage 2 canonical fields: fcv_baseline, executive_summary,
  operating_context, integration, interactions, strengths_weaknesses,
  reflections, supplementary_questions, sources.
- Stage 3 is climate-priorities-only.
- Recovery is field-level and preserves valid fields.
- ITS/FastAPI parity is pending; do not mirror until Render preview acceptance.
```

Do not commit the private parity file to Git.

- [ ] **Step 6: Commit documentation**

```powershell
git add -- CLAUDE.md docs/20260728_climate_module_reliability_handoff.md
git commit -m "docs: record climate-native workflow contract"
```

- [ ] **Step 7: Push the feature branch**

```powershell
git status --short --branch
git log -12 --oneline --decorate
git push origin feat/climate-readout-redesign
```

Expected: clean worktree and remote branch updated.

- [ ] **Step 8: Deploy an isolated Render preview**

Configure the preview service to deploy
`feat/climate-readout-redesign`. Do not point the production ITS-compatible
service away from `main`.

Confirm:

```text
/health returns the preview commit hash.
/api/sector-lenses returns the Climate lens.
```

- [ ] **Step 9: Run South Sudan live acceptance**

Use the same South Sudan SSNRL PCN plus CCDR inputs that exposed the original
failure. Record the assessment ID and verify:

- research returns at least two accepted sources and a project-linked claim;
- Stage 2 uses the dedicated prompt;
- the primary diagnostic completes without recovery;
- if recovery is deliberately triggered, keepalives remain visible;
- compact FCV baseline appears without 12-OST/DNH-9/25-question panels;
- both interaction directions appear;
- material anchor and supplementary questions appear;
- insights name project components, locations, groups, and institutions;
- approximately three climate-specific priorities appear;
- every priority has validated climate links and authority basis;
- live HTML, downloaded/shared HTML, and DOCX match; and
- no unvalidated partial result is presented.

- [ ] **Step 10: Exercise deliberate live failures**

Using preview-only configuration or injected test clients:

- force research failure and verify retry/full-FCV actions;
- force an incomplete Stage 2 payload and verify observable recovery;
- force recovery timeout and verify no partial baseline is shown;
- force provider overload before streaming and verify bounded retry.

- [ ] **Step 11: Record preview result**

Update the handoff with the preview commit, URL, assessment IDs, log outcome,
acceptance status, and any remaining issue. Commit and push that documentation
update:

```powershell
git add -- docs/20260728_climate_module_reliability_handoff.md
git commit -m "docs: record climate preview acceptance"
git push origin feat/climate-readout-redesign
```

Do not merge to `main`. Return to the user with the preview evidence and ask for
the integration decision.

## Final acceptance checklist

- [ ] Climate selection never assembles the generic 12-OST, DNH-9, or
  25-question Stage 2 engine.
- [ ] The compact baseline does not enumerate those frameworks internally or
  visibly.
- [ ] Mandatory research either passes the evidence gate or stops the route.
- [ ] Parent and child research deadlines cannot conflict.
- [ ] The normal Stage 2 path produces `climate-native-v1` without recovery.
- [ ] The structured payload is the single source for the readout and exports.
- [ ] Six anchors remain, with distinct supplementary source questions allowed.
- [ ] Stage 3 generates climate-specific priorities only.
- [ ] Recovery requests only missing fields and preserves valid fields.
- [ ] Research, recovery, and model waits remain observable through SSE.
- [ ] Typed errors offer retry or full standard FCV assessment.
- [ ] Specificity and OPCS authority validation remain enforced.
- [ ] Live, shared/downloaded HTML, and DOCX remain in parity.
- [ ] Standard FCV behavior remains unchanged.
- [ ] The South Sudan preview run completes and is documented.
- [ ] Production `main` remains on the ITS-compatible baseline.
