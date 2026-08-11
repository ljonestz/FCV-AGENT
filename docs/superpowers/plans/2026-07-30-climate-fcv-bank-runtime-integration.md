# Climate-FCV Evidence Bank Runtime Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the approved Climate-FCV country-bank release into both FCV-AGENT workflows so live research enriches assessments but can no longer block them.

**Architecture:** A path-based loader validates the pinned public release, a deterministic selector returns canonical record IDs, and a bounded merger combines materialized bank items with accepted live claims. Step-by-step mode persists only a validated selection manifest; the server reloads canonical bank records before Stage 2. The existing climate-native Stage 2 prompt, diagnostic repair, Stage 3, and standard FCV route remain intact.

**Tech Stack:** Python 3.13, Flask, stdlib JSON/dataclasses/pathlib/hashlib, pytest, vanilla JavaScript, python-docx, Git submodules, Render.

**Depends on:** Approved `climate-fcv-country-bank` South Sudan runtime release and its commit SHA.

**Baseline:** `558 passed` on 2026-07-30 using `C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`.

---

## File Map

- Create `sector_lenses/climate_bank.py`: release path resolution, validation, compatibility, country lookup, and manifest materialization.
- Create `sector_lenses/climate_bank_selector.py`: project-signal normalization, scoring, diversity, and packet bounds.
- Create `sector_lenses/climate_grounding.py`: live/bank merge, grounding states, provenance, and bounded prompt serialization.
- Modify `sector_lenses/climate_native.py`: accept the merged external grounding block without changing the canonical diagnostic schema.
- Modify `sector_lenses/research.py`: cap accepted live claims at six and retain the existing quality gate as a non-blocking acceptance decision.
- Modify `sector_lenses/__init__.py`: export the new contracts.
- Modify `app.py`: load/select before live research, persist manifests, remove mandatory research termination, log grounding state, and thread provenance into both workflows and DOCX.
- Modify `index.html`: persist grounding metadata and show accurate provenance notices.
- Add `.gitmodules` and `data/climate-fcv-country-bank`: pinned public companion repository.
- Add `tests/fixtures/climate_bank/runtime_v1.json`: synthetic release for unit tests.
- Add `tests/test_climate_bank.py`, `tests/test_climate_bank_selector.py`, and `tests/test_climate_grounding.py`.
- Modify climate workflow, research, prompt, frontend, and DOCX contract tests.
- Modify `README.md`, `claude.md`, and `docs/reference/`.
- Modify local `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md` after shared contracts settle; never commit that file.

## Runtime Contracts

```python
CLIMATE_BANK_SCHEMA_VERSION = "1.0.0"
CLIMATE_BANK_TARGET_ITEMS = 8
CLIMATE_BANK_MAX_ITEMS = 12
CLIMATE_BANK_MAX_CHARS = 6_000
CLIMATE_LIVE_TARGET_CLAIMS = 4
CLIMATE_LIVE_MAX_CLAIMS = 6
CLIMATE_COMBINED_MAX_CHARS = 12_000
CLIMATE_GROUNDING_STATES = {
    "bank+research", "bank-only", "research-only", "thematic-only"
}
```

The client-visible grounding envelope contains display-safe provenance and one
canonical bank manifest:

```json
{
  "state": "bank+research",
  "warning_code": "",
  "research_status": "accepted",
  "sources": [
    {"id": "SSD-SRC-001", "title": "Source title", "url": "https://example.org/source", "origin": "bank"}
  ],
  "bank_manifest": {
    "bank_status": "ok",
    "schema_version": "1.0.0",
    "content_version": "2026.07.south-sudan-pilot",
    "country_iso3": "SSD",
    "evidence_ids": ["SSD-E-001"],
    "pathway_ids": ["SSD-P-001"]
  }
}
```

The browser never receives the 6,000-character evidence packet. The server
trusts only validated IDs inside `bank_manifest`, ignores client-supplied prose,
and rematerializes records and sources from the pinned release.

### Task 1: Pin the companion repository and establish loader behavior

**Files:**
- Create: `.gitmodules`
- Create gitlink: `data/climate-fcv-country-bank`
- Create: `sector_lenses/climate_bank.py`
- Create: `tests/fixtures/climate_bank/runtime_v1.json`
- Create: `tests/test_climate_bank.py`

- [ ] **Step 1: Add the public submodule at the approved release commit**

```powershell
git submodule add https://github.com/ljonestz/climate-fcv-country-bank.git data/climate-fcv-country-bank
git -C data/climate-fcv-country-bank checkout main
```

Expected: `.gitmodules` points at the public repository and the gitlink resolves to the merged South Sudan release commit.

- [ ] **Step 2: Write failing loader tests**

```python
# tests/test_climate_bank.py
from pathlib import Path

from sector_lenses.climate_bank import load_climate_bank, materialize_bank_manifest


FIXTURE = Path(__file__).parent / "fixtures" / "climate_bank" / "runtime_v1.json"


def test_valid_release_loads_and_resolves_aliases() -> None:
    result = load_climate_bank(FIXTURE)
    assert result.status == "ok"
    assert result.release["content_version"] == "test-1"
    assert result.resolve_country("South Sudan")["iso3"] == "SSD"
    assert result.resolve_country("ssd")["iso3"] == "SSD"


def test_missing_release_is_nonfatal(tmp_path: Path) -> None:
    result = load_climate_bank(tmp_path / "missing.json")
    assert result.status == "unavailable"
    assert result.warning_code == "bank_missing"
    assert result.release == {}


def test_incompatible_release_is_nonfatal(tmp_path: Path) -> None:
    path = tmp_path / "runtime.json"
    path.write_text('{"schema_version":"2.0.0"}', encoding="utf-8")
    result = load_climate_bank(path)
    assert result.status == "unavailable"
    assert result.warning_code == "bank_incompatible"


def test_manifest_materialization_rejects_client_prose() -> None:
    result = load_climate_bank(FIXTURE)
    packet = materialize_bank_manifest(result, {
        "country_iso3": "SSD", "content_version": "test-1",
        "evidence_ids": ["SSD-E-001"], "pathway_ids": ["SSD-P-001"],
        "statement": "client supplied text",
    })
    assert packet["evidence_records"][0]["evidence_id"] == "SSD-E-001"
    assert "client supplied text" not in str(packet)
```

- [ ] **Step 3: Run tests to verify they fail**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_bank.py -v -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 4: Implement the loader**

```python
# sector_lenses/climate_bank.py
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CLIMATE_BANK_SCHEMA_VERSION = "1.0.0"
DEFAULT_RELEASE = (
    Path(__file__).resolve().parents[1] / "data" / "climate-fcv-country-bank"
    / "releases" / "current" / "runtime.json"
)


def _canonical_checksum(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ClimateBankLoad:
    status: str
    warning_code: str
    release: dict[str, Any]

    def resolve_country(self, value: str) -> dict[str, Any] | None:
        key = str(value or "").strip().casefold()
        for country in self.release.get("countries", {}).values():
            aliases = {
                str(country.get("iso3", "")).casefold(),
                str(country.get("name", "")).casefold(),
                *(str(item).casefold() for item in country.get("aliases", [])),
            }
            if key in aliases:
                return country
        return None


def _release_path(path: str | Path | None) -> Path:
    raw = path or os.environ.get("CLIMATE_COUNTRY_BANK_PATH") or DEFAULT_RELEASE
    candidate = Path(raw)
    return (candidate / "releases" / "current" / "runtime.json"
            if candidate.is_dir() else candidate)


def load_climate_bank(path: str | Path | None = None) -> ClimateBankLoad:
    candidate = _release_path(path)
    if not candidate.is_file():
        return ClimateBankLoad("unavailable", "bank_missing", {})
    try:
        release = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ClimateBankLoad("unavailable", "bank_incompatible", {})
    if release.get("schema_version") != CLIMATE_BANK_SCHEMA_VERSION:
        return ClimateBankLoad("unavailable", "bank_incompatible", {})
    required = (
        "content_version", "countries", "sources", "evidence_records",
        "pathways", "source_manifest_checksum",
    )
    if any(key not in release for key in required):
        return ClimateBankLoad("unavailable", "bank_incompatible", {})
    if _canonical_checksum(release["sources"]) != release["source_manifest_checksum"]:
        return ClimateBankLoad("unavailable", "bank_incompatible", {})
    return ClimateBankLoad("ok", "", release)
```

Implement `materialize_bank_manifest()` to require matching content version, approved country status, canonical evidence/pathway IDs, approved records, valid cross-references, and non-expired `review_due`; collect source metadata from referenced evidence. On success return the canonical packet with `bank_status: "ok"` and an empty warning code. On failure return only `bank_status: "unavailable"` and a typed `warning_code`; never return partial canonical content or raise. Reject duplicates, bad URLs, invalid records, or expired content. Never import `background_docs` or restricted OPCS code.

- [ ] **Step 5: Run tests and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_bank.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
git add .gitmodules data/climate-fcv-country-bank sector_lenses/climate_bank.py tests/fixtures/climate_bank tests/test_climate_bank.py
git commit -m "feat: load pinned climate evidence bank release"
```

Expected: loader tests pass; production tests use the explicit synthetic fixture and do not require the submodule.

### Task 2: Implement deterministic project-relevant selection

**Files:**
- Create: `sector_lenses/climate_bank_selector.py`
- Create: `tests/test_climate_bank_selector.py`
- Modify: `sector_lenses/__init__.py`

- [ ] **Step 1: Write failing selector tests**

```python
# tests/test_climate_bank_selector.py
from pathlib import Path

from sector_lenses.climate_bank import load_climate_bank
from sector_lenses.climate_bank_selector import select_bank_manifest


FIXTURE = Path(__file__).parent / "fixtures" / "climate_bank" / "runtime_v1.json"


def _select(signals: str):
    return select_bank_manifest(
        load_climate_bank(FIXTURE), country="South Sudan",
        country_scope="single", resolved_country_count=1,
        sector="Fisheries", project_signals=signals,
    )


def test_fisheries_and_roads_select_different_records() -> None:
    fisheries = _select("Jonglei landing sites fishers BFMU seasonal users")
    roads = _select("Unity feeder roads access markets flood drainage")
    assert fisheries["evidence_ids"] != roads["evidence_ids"]


def test_selection_is_stable() -> None:
    assert _select("Jonglei landing sites fishers") == _select(
        "Jonglei landing sites fishers"
    )


def test_physical_baseline_cannot_crowd_out_qualitative_evidence() -> None:
    manifest = _select("flood drought temperature")
    bank = load_climate_bank(FIXTURE)
    ids = set(manifest["evidence_ids"])
    selected = [item for item in bank.release["evidence_records"]
                if item["evidence_id"] in ids]
    assert sum(item["analytical_role"] == "physical-baseline"
               for item in selected) <= 2


def test_multi_country_scope_is_explicitly_unsupported() -> None:
    result = select_bank_manifest(
        load_climate_bank(FIXTURE), country="South Sudan",
        country_scope="multi", resolved_country_count=2,
        sector="Fisheries", project_signals="Jonglei",
    )
    assert result["bank_status"] == "unavailable"
    assert result["warning_code"] == "bank_scope_unsupported"
```

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement tokenization and scoring**

Use lowercase alphanumeric tokens, strip a trailing `s` from tokens longer than four characters, and apply:

```python
MATCH_WEIGHTS = {
    "geography": 10, "sector": 8, "project_element": 8,
    "affected_group": 6, "institution": 6,
    "system_asset_resource": 6, "mediator": 4, "hazard": 4,
    "direct_climate_fcv_role": 3, "vulnerability_capacity_role": 3,
    "direct_pathway": 3, "triangulated_pathway": 2,
    "recent_source": 1,
}
```

`select_bank_manifest()` resolves country first; scores evidence and pathways separately; selects two relevant pathways when available; fills toward eight total items; caps at twelve; caps physical-baseline evidence at two; avoids more than three items primarily supported by one source when alternatives exist; uses score descending and stable ID ascending; emits canonical IDs only; and drops the lowest-scoring item until materialized compact JSON is at most 6,000 characters.

- [ ] **Step 4: Run tests and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_bank_selector.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
git add sector_lenses/climate_bank_selector.py sector_lenses/__init__.py tests/test_climate_bank_selector.py tests/fixtures/climate_bank/runtime_v1.json
git commit -m "feat: select bounded project relevant climate evidence"
```

Expected: selector tests pass.

### Task 3: Merge bank and live grounding within hard bounds

**Files:**
- Create: `sector_lenses/climate_grounding.py`
- Create: `tests/test_climate_grounding.py`
- Modify: `sector_lenses/research.py`
- Modify: `tests/test_climate_research.py`
- Modify: `sector_lenses/__init__.py`

- [ ] **Step 1: Write failing grounding-state and budget tests**

```python
# tests/test_climate_grounding.py
from sector_lenses.climate_grounding import merge_climate_grounding


def test_all_four_grounding_states() -> None:
    bank = {
        "content_version": "test-1",
        "sources": [{"source_id": "SSD-SRC-001", "url": "https://sipri.org/a"}],
        "evidence_records": [{"evidence_id": "SSD-E-001",
                              "compact_statement": "Reviewed evidence."}],
        "pathways": [],
    }
    research = {
        "status": "complete",
        "sources": [{"id": "climate-source-1", "url": "https://un.org/a",
                     "title": "Current evidence", "source_type": "un"}],
        "claims": [{"id": "climate-claim-1", "claim": "Current claim.",
                    "source_ids": ["climate-source-1"],
                    "project_elements": ["Road"], "geographies": ["Unity"],
                    "affected_groups": [], "systems_or_assets": ["Road"],
                    "evidence_status": "observed", "confidence": "medium",
                    "time_horizons": ["current-near-term"], "evidence_gap": ""}],
    }
    assert merge_climate_grounding(bank, research)["state"] == "bank+research"
    assert merge_climate_grounding(bank, {})["state"] == "bank-only"
    assert merge_climate_grounding({}, research)["state"] == "research-only"
    assert merge_climate_grounding({}, {})["state"] == "thematic-only"


def test_combined_grounding_is_bounded() -> None:
    bank = {"sources": [], "pathways": [], "evidence_records": [
        {"evidence_id": f"SSD-E-{index:03d}", "compact_statement": "x" * 900}
        for index in range(1, 13)
    ]}
    merged = merge_climate_grounding(bank, {})
    assert len(merged["prompt_context"]) <= 12_000
    assert merged["bank_character_count"] <= 6_000
```

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL because the merger does not exist.

- [ ] **Step 3: Implement normalization, deduplication, and bounds**

`merge_climate_grounding()` accepts at most six live claims; preserves bank and live provenance separately; deduplicates sources by normalized URL while retaining source aliases; never rewrites approved compact statements; retains conflicts and sets `has_conflicting_evidence`; emits one four-state value; caps bank context at 6,000 characters and combined context at 12,000; and returns content-free counts for logs.

Modify `normalize_climate_research_bundle()` to stop after six claims and `build_climate_research_prompt()` to request four to six claims. Keep `climate_research_evidence_gate()` as the quality decision, but remove "mandatory" language.

- [ ] **Step 4: Run tests and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_grounding.py tests/test_climate_research.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
git add sector_lenses/climate_grounding.py sector_lenses/research.py sector_lenses/__init__.py tests/test_climate_grounding.py tests/test_climate_research.py
git commit -m "feat: merge bounded bank and live climate grounding"
```

Expected: grounding and research tests pass.

### Task 4: Select the bank before live research in both workflows

**Files:**
- Modify: `app.py` near `build_stage1_research_plan()` and `_iter_stage1_research()`
- Modify: `tests/test_climate_workflow_contract.py`
- Modify: `tests/test_climate_research.py`

- [ ] **Step 1: Write failing shared-preprocessing tests**

Add tests that patch the loader, selector, and live-research function:

```python
import threading


def _climate_plan():
    return {
        "country": "South Sudan",
        "sector": "Fisheries",
        "core": {"max_tokens": 4000, "max_uses": 3},
        "climate": {"enabled": True},
        "project_profile": {
            "documents": ["South Sudan PCN.docx"],
            "document_excerpt": "Jonglei landing sites BFMU seasonal users",
        },
        "country_scope": "single",
        "resolved_country_count": 1,
    }


def test_bank_selection_precedes_live_research(monkeypatch):
    calls = []
    caller_thread = threading.get_ident()
    monkeypatch.setattr(app_module, "load_climate_bank",
                        lambda: calls.append(("load", threading.get_ident()))
                        or object())
    monkeypatch.setattr(app_module, "select_bank_manifest",
                        lambda *args, **kwargs:
                        calls.append(("select", threading.get_ident())) or {
                            "bank_status": "ok", "warning_code": "",
                            "schema_version": "1.0.0",
                            "content_version": "test-1",
                            "country_iso3": "SSD",
                            "evidence_ids": ["SSD-E-001"],
                            "pathway_ids": ["SSD-P-001"],
                        })
    monkeypatch.setattr(app_module, "run_fcv_web_research",
                        lambda *args, **kwargs: {"brief": ""})
    monkeypatch.setattr(app_module, "run_climate_web_research",
                        lambda *args, **kwargs:
                        calls.append(("research", threading.get_ident()))
                        or _valid_research())
    result = list(app_module._iter_stage1_research(
        _climate_plan(), assessment_id="a-1"
    ))[-1]["result"]
    names = [name for name, _thread_id in calls]
    assert names.index("select") < names.index("research")
    assert result["climate_grounding"]["country_iso3"] == "SSD"
    assert next(thread_id for name, thread_id in calls
                if name == "select") == caller_thread
    assert next(thread_id for name, thread_id in calls
                if name == "research") != caller_thread
```

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL because research results do not contain `climate_grounding`.

- [ ] **Step 3: Extend the shared plan and result**

Change `build_stage1_research_plan()` to accept `country_scope` and `resolved_country_count`. At the start of `_iter_stage1_research()`:

1. load the bank;
2. select a manifest using country, sector, document excerpt, scope, and count;
3. store it in `results["climate_grounding"]`; and
4. only then submit core and live-research futures.

Both `/api/run-stage` and `/api/run-express` pass the same resolved state. Missing, invalid, stale, unsupported, or unavailable bank content is a warning and never raises.

- [ ] **Step 4: Run tests and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_research.py tests/test_climate_workflow_contract.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
git add app.py tests/test_climate_research.py tests/test_climate_workflow_contract.py
git commit -m "feat: select climate bank before live research"
```

Expected: shared-preprocessing tests pass for both workflows.

### Task 5: Make live Climate research non-fatal

**Files:**
- Modify: `app.py` mandatory gate blocks in `/api/run-stage` and `/api/run-express`
- Modify: `tests/test_climate_workflow_contract.py`

- [ ] **Step 1: Replace the obsolete blocking tests**

Replace `test_climate_research_failure_blocks_both_workflows_before_model` with parameterized route tests:

```python
@pytest.mark.parametrize("endpoint", ["/api/run-stage", "/api/run-express"])
def test_climate_research_failure_continues_with_bank(
    monkeypatch, endpoint, caplog
):
    caplog.set_level("INFO")
    manifest = {
        "bank_status": "ok", "warning_code": "",
        "schema_version": "1.0.0", "content_version": "test-1",
        "country_iso3": "SSD", "evidence_ids": ["SSD-E-001"],
        "pathway_ids": ["SSD-P-001"],
    }
    packet = {
        "content_version": "test-1",
        "sources": [{"source_id": "SSD-SRC-001",
                     "title": "Reviewed source",
                     "url": "https://www.sipri.org/example"}],
        "evidence_records": [{"evidence_id": "SSD-E-001",
                              "compact_statement": "Reviewed evidence."}],
        "pathways": [{"pathway_id": "SSD-P-001",
                      "compact_statement": "Reviewed pathway."}],
    }
    merged = {
        "state": "bank-only", "warning_code": "research_timeout",
        "research_status": "timeout", "bank_manifest": manifest,
        "sources": packet["sources"], "prompt_context": "Reviewed evidence.",
        "bank_character_count": 18, "selected_item_count": 2,
    }
    monkeypatch.setattr(app_module, "extract_country_name",
                        lambda text, client: "South Sudan")
    monkeypatch.setattr(app_module, "extract_sector_name",
                        lambda text, client: "Fisheries")
    monkeypatch.setattr(app_module, "get_fast_client", lambda: object())
    monkeypatch.setattr(
        app_module, "_iter_stage1_research",
        lambda *args, **kwargs: iter([{"result": {
            "core_brief": "Compact FCV research.",
            "climate_research": _failed_research(),
            "lens_context_sources": [], "climate_grounding": manifest,
        }}]),
    )
    monkeypatch.setattr(app_module, "materialize_bank_manifest",
                        lambda *args, **kwargs: packet)
    monkeypatch.setattr(app_module, "merge_climate_grounding",
                        lambda *args, **kwargs: merged)
    model_calls = []

    def stop_after_model_entry(messages, max_tokens, stage, **kwargs):
        model_calls.append(stage)
        raise RuntimeError("intentional test stop after model entry")
        yield  # pragma: no cover

    monkeypatch.setattr(app_module, "_stream_stage", stop_after_model_entry)
    payload = {
        "active_lenses": ["climate"], "document_type": "PAD",
        "instrument_type": "IPF", "review_mode": "design",
        "documents": [{"name": "Project.txt", "type": "text",
                       "docRole": "primary",
                       "content": "Jonglei fisheries landing sites. " * 10}],
    }
    if endpoint == "/api/run-stage":
        payload["stage"] = 1
    events = _decode_sse(app_module.app.test_client().post(endpoint, json=payload))
    assert any(event.get("status") == "preparing_analysis" for event in events)
    assert model_calls == [1]
    assert not any(
        event.get("error_code", "").startswith("climate_research")
        for event in events
    )
    assert "grounding_state=bank-only" in caplog.text
```

Add parallel cases for `research-only` and `thematic-only`.

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL because both routes still return `climate_blocking_failure_event`.

- [ ] **Step 3: Replace termination with grounding merge**

In both routes:

- normalize and quality-gate live research;
- discard rejected live claims but retain the typed failure reason;
- materialize the server-validated bank manifest;
- call `merge_climate_grounding()`;
- continue for all four states;
- emit `climate_grounding` in Stage 1 and Stage 2 completion events; and
- reserve `climate_blocking_failure_event()` for invalid canonical diagnostics and recovery failures.
- on a later Stage 2 request, read only `data["climate_grounding"]["bank_manifest"]`, rematerialize it from the pinned release, and ignore client-supplied source/prose fields;

Emit one content-free log line:

```text
Climate grounding assessment_id=<id> bank_version=<version|none>
iso3=<iso3|none> selected_items=<0..12> bank_chars=<0..6000>
research_status=<accepted|empty|timeout|provider_529|rejected>
grounding_state=<four-state enum> warning_code=<typed code|none>
```

- [ ] **Step 4: Run tests and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_workflow_contract.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
git add app.py tests/test_climate_workflow_contract.py
git commit -m "fix: make live climate research non fatal"
```

Expected: all four states continue and standard non-Climate route tests remain unchanged.

### Task 6: Feed canonical grounding into the existing Climate Stage 2 prompt

**Files:**
- Modify: `sector_lenses/climate_native.py`
- Modify: `app.py` `build_design_stage2_prompt()` and both call sites
- Modify: `tests/test_climate_native.py`
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `tests/test_climate_workflow_contract.py`

- [ ] **Step 1: Write failing prompt-boundary tests**

```python
def test_native_prompt_contains_bank_and_live_provenance():
    grounding = {
        "state": "bank+research",
        "prompt_context": (
            "SSD-E-001 observed reviewed evidence. "
            "SSD-P-001 analytical-inference pathway. "
            "climate-claim-1 current evidence."
        ),
    }
    prompt = build_climate_stage2_prompt(
        instrument_type="IPF", document_type="PCN",
        temporal_guardrail="Preparation stage.",
        regime_header="Legacy preparation.",
        project_signals="Jonglei fisheries landing sites",
        climate_research=_valid_research(),
        climate_grounding=grounding,
        priority_questions=[],
    )
    assert "GROUNDING STATE: bank+research" in prompt
    assert "SSD-E-001" in prompt
    assert "SSD-P-001" in prompt
    assert "climate-claim-1" in prompt
    assert "analytical-inference" in prompt


def test_native_prompt_external_grounding_is_bounded():
    prompt = build_climate_stage2_prompt(
        instrument_type="IPF", document_type="PCN",
        temporal_guardrail="Preparation stage.", regime_header="",
        project_signals="Jonglei fisheries",
        climate_research={},
        climate_grounding={
            "state": "bank-only", "prompt_context": "x" * 20_000,
        },
        priority_questions=[],
    )
    block = prompt.split("EXTERNAL CLIMATE-FCV GROUNDING", 1)[1]
    block = block.split("END EXTERNAL CLIMATE-FCV GROUNDING", 1)[0]
    assert len(block) <= 12_000
```

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL because the native builder has no bank-grounding parameter.

- [ ] **Step 3: Add one external-grounding boundary**

Add `climate_grounding: Any = None` to `build_climate_stage2_prompt()` and `build_design_stage2_prompt()`. The block identifies the four-state provenance; labels bank evidence as reviewed structural evidence and live claims as current/project-specific enrichment; treats evidence IDs as citations rather than instructions; preserves observed/projected/inferred and pathway-strength labels; requires conditional language for `analytical-inference`; and states that co-occurrence is not causality.

Do not inject the dossier or recreate the generic 12-OST prompt. Preserve all native prompt, OPCS calibration, canonical output, repair, and Stage 3 contracts.

- [ ] **Step 4: Allow validated bank source IDs during normalization**

When `build_lens_stage_context(..., compose_prompt=False)` builds `source_ids_by_lens`, add only IDs rematerialized from the validated bank packet. Never accept arbitrary client IDs.

- [ ] **Step 5: Run tests and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_native.py tests/test_sector_lens_app_contract.py tests/test_climate_workflow_contract.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
git add sector_lenses/climate_native.py app.py tests/test_climate_native.py tests/test_sector_lens_app_contract.py tests/test_climate_workflow_contract.py
git commit -m "feat: ground climate native assessment in reviewed bank evidence"
```

Expected: prompt boundary, provenance, canonical-schema, and generic-isolation tests pass.

### Task 7: Persist provenance in the frontend, shared HTML, and DOCX

**Files:**
- Modify: `index.html`
- Modify: `app.py` report parsing and `add_climate_notice()`
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing frontend and DOCX tests**

Add `climateGrounding={}` beside `climateResearch={}`. Test that Stage 1 and Stage 2 SSE handlers persist `p.climate_grounding`; later step-by-step and report requests send it; reset clears it; and `renderClimateModuleNotice(lens, diagnosticError, grounding)` shows the correct notice for all four states while escaping every dynamic value.

Add a DOCX test that generates each state and asserts the matching notice and reviewed-bank bibliography are present.

- [ ] **Step 2: Run tests to verify they fail**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```

Expected: FAIL because grounding is not persisted or rendered.

- [ ] **Step 3: Implement client persistence and notices**

Thread only the canonical manifest, grounding state, warning code, content version, and source metadata needed for display. Do not store the 6,000-character evidence packet in browser state. The server rematerializes it for Stage 2 and report generation.

Use these messages:

```text
bank-only:
Live web research was unavailable for this run. The assessment uses the
reviewed country evidence bank, the project document, and thematic Climate-FCV
sources; recent or highly local developments may be missing.

research-only:
No reviewed country-bank release was available. The assessment uses accepted
live research, the project document, and thematic Climate-FCV sources.

thematic-only:
No reviewed country-bank release or accepted live research was available. The
assessment relies on the project document and thematic Climate-FCV sources and
flags country-specific evidence limitations.
```

Show no warning for `bank+research`. Add a source appendix subsection named `Reviewed country evidence bank` with content version and bank source titles/URLs. Keep live sources under `Country context used`.

- [ ] **Step 4: Run tests and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
git add index.html app.py tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py
git commit -m "feat: surface climate grounding provenance in reports"
```

Expected: live HTML, shared HTML, and DOCX provenance are in parity.

### Task 8: Documentation, deployment contract, and dual-build parity

**Files:**
- Modify: `README.md`
- Modify: `claude.md`
- Modify: `docs/reference/reference_prompt_architecture.md`
- Modify: `docs/reference/reference_backend_routes.md`
- Modify: `docs/reference/reference_sector_lenses.md`
- Modify locally only: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`
- Test: `tests/test_climate_bank_deployment_contract.py`

- [ ] **Step 1: Write the failing deployment-contract test**

```python
# tests/test_climate_bank_deployment_contract.py
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_submodule_and_override_are_documented() -> None:
    modules = (ROOT / ".gitmodules").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "data/climate-fcv-country-bank" in modules
    assert "https://github.com/ljonestz/climate-fcv-country-bank.git" in modules
    assert "CLIMATE_COUNTRY_BANK_PATH" in readme


def test_no_restricted_opcs_dependency_in_bank_modules() -> None:
    source = "\n".join(
        (ROOT / "sector_lenses" / name).read_text(encoding="utf-8")
        for name in (
            "climate_bank.py", "climate_bank_selector.py",
            "climate_grounding.py",
        )
    )
    assert "ppf_indexer" not in source
    assert "from background_docs import" not in source
```

- [ ] **Step 2: Run the test to verify documentation is incomplete**

Expected: FAIL because the README has no override documentation.

- [ ] **Step 3: Update tracked documentation**

Document the public submodule and `CLIMATE_COUNTRY_BANK_PATH`; Render's root `.gitmodules` cloning; approved-only release and safe degradation; selection/context bounds; four grounding states; non-fatal live enrichment; South Sudan single-country scope; no self-citation or raw PDF redistribution; native Stage 2 preservation; and standard-route non-regression. Add a new `claude.md` version entry without altering v9.22.

- [ ] **Step 4: Update the private parity log**

Record release schema version, manifest fields, grounding enum, warning codes, SSE fields, diagnostic source-ID admission, and the deferred ITS/FastAPI port in `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`. Do not stage or commit it.

- [ ] **Step 5: Run tests and commit**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_bank_deployment_contract.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
git add README.md claude.md docs/reference tests/test_climate_bank_deployment_contract.py
git commit -m "docs: document climate evidence bank runtime contract"
```

Expected: deployment-contract tests pass.

### Task 9: Full verification and South Sudan live acceptance

**Files:**
- Modify only if a verified defect is found
- Capture: local test output and Render log evidence by assessment ID

- [ ] **Step 1: Run targeted contract suites**

```powershell
C:/WBG/Python313/python.exe -m pytest tests/test_climate_bank.py tests/test_climate_bank_selector.py tests/test_climate_grounding.py tests/test_climate_research.py tests/test_climate_native.py tests/test_climate_workflow_contract.py tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```

Expected: all targeted tests pass.

- [ ] **Step 2: Run the complete suite**

```powershell
C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```

Expected: at least the 558-test baseline plus all new tests pass with zero failures.

- [ ] **Step 3: Verify git and submodule state**

```powershell
git status --short --branch
git diff --check
git submodule status
git diff --submodule=log feat/climate-readout-redesign...HEAD
```

Expected: clean worktree, no whitespace errors, and the submodule pinned to the approved release.

- [ ] **Step 4: Push and open a draft pull request**

```powershell
git push -u origin feat/climate-country-bank
gh pr create --draft --base feat/climate-readout-redesign --head feat/climate-country-bank --title "feat: add reliable Climate-FCV country-bank grounding" --body "Adds the pinned public evidence bank, deterministic project selection, bounded grounding merge, non-fatal live research, provenance notices, and South Sudan pilot coverage."
```

Expected: Render creates a preview deployment for the draft pull request.

- [ ] **Step 5: Run one bank-only South Sudan acceptance**

Run the full Express route locally with the existing South Sudan fisheries PCN
and the live-research client patched to return the typed timeout bundle. This is
an end-to-end route acceptance, not a production-code bypass.

Confirm assessment completion; `bank-only` state; fisheries/landing-site/seasonal-user/Jonglei/Sudd or institutional selection rather than generic hazards; canonical Stage 2 without routine recovery; conditional causal language; amber notice in live HTML, shared HTML, and DOCX; and matching local log counts and budgets.

- [ ] **Step 6: Run one bank-plus-research South Sudan acceptance**

Deploy the draft branch to Render and rerun the same PCN once with live research. Confirm `bank+research`; recent or finer-grained enrichment; retained structural vulnerability/capacity evidence; all bounds; accurate HTML/DOCX provenance; and an unaffected standard non-Climate run.

Stop after one failed live verification. Capture assessment ID, Render log slice, grounding manifest, and exported report before changing code or prompts.

- [ ] **Step 7: Mark the branch ready only after verification**

```powershell
gh pr ready
```

Expected: the pull request is ready for final review.

## Integration Completion Gate

The track is complete only when both workflows select the same evidence for the same signals; live failure never terminates a Climate run; all four states and all bounds are tested; step-by-step rematerializes canonical records; provenance retains canonical IDs; multi-country runs warn and continue; missing or incompatible bank content degrades safely; native prompt and recovery contracts stay green; standard FCV is unchanged; Render clones the public submodule; and both South Sudan acceptance runs are captured.
