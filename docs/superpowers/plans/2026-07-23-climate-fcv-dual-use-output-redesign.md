# Climate-FCV Dual-Use Output Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reliable integrated Climate-active assessment that preserves the complete core FCV framework while adding equally substantive, project-specific Climate-FCV research, causal diagnosis, qualitative dividends synthesis, and deterministically linked priority guidance.

**Architecture:** Add a bounded `ClimateResearchBundle` contract and dedicated Climate web-research pass, then feed only normalized claims into the existing three-stage pipeline. Extend the hidden Stage 2 diagnostic with time horizons and stable pathway identifiers, add backward-compatible Climate links to Stage 3 priorities, and drive the live page, shared HTML, and DOCX from the same validated structures. Core-only code paths, prompts, budgets, and output remain byte-for-byte unchanged wherever practical.

**Tech Stack:** Python 3.13, Flask, Anthropic Python SDK with web search, dataclasses/typed dictionaries represented as validated JSON, pytest, vanilla JavaScript/HTML/CSS, Node-based frontend contract tests, python-docx.

---

## File Structure and Responsibilities

- Create `sector_lenses/research.py`: Climate research delimiters, trusted-source validation, claim normalization, prompt construction, compact Stage 1/2 formatting, and retry-query construction.
- Modify `sector_lenses/context.py`: preserve CCDR compatibility while allowing validated Climate research sources to join the existing lens source allowlist.
- Modify `sector_lenses/pipeline.py`: normalize Climate causal pathways, time horizons, stable identifiers, and priority-link targets.
- Modify `sector_lenses/__init__.py`: export the new research and validation helpers.
- Modify `sector_lenses/modules/climate/manifest.yaml`: rebalance Climate-active stage budgets only.
- Modify `sector_lenses/modules/climate/guidance.md`: require project specificity, causal chains, temporal horizons, and evidence gaps.
- Modify `sector_lenses/modules/climate/questions.yaml`: align diagnostic questions with the new two-direction and time-horizon contract.
- Modify `app.py`: orchestrate shared Stage 1 research in both workflows, inject bounded research context, extend Stage 2/recovery and Stage 3 contracts, normalize priority links, render DOCX, and emit safe telemetry.
- Modify `index.html`: persist Climate research state, render analytical interaction sections and causal strips, replace dividend cards with qualitative synthesis, and replace Climate-active priority category notes.
- Create `tests/test_climate_research.py`: pure research-contract and retry tests.
- Modify `tests/test_climate_ccdr_context.py`: CCDR-first and core-only invariance tests.
- Modify `tests/test_sector_lens_pipeline.py`: diagnostic normalization, specificity, horizon, and stable-ID tests.
- Modify `tests/test_sector_lens_app_contract.py`: prompt budgets, priority JSON, Stage 3 synthesis, safe fallback, DOCX, and telemetry tests.
- Modify `tests/test_climate_lens_frontend.py`: live/shared HTML rendering tests.
- Create `tests/fixtures/climate/south_sudan_dual_use.json`: synthetic, non-document-derived regression fixture with locations, project elements, sources, pathways, and five priorities.
- Update `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`: private, untracked divergence entry for additive priority JSON fields and research-context contract.

---

### Task 1: Define and Validate the Climate Research Contract

**Files:**
- Create: `sector_lenses/research.py`
- Modify: `sector_lenses/context.py`
- Modify: `sector_lenses/__init__.py`
- Create: `tests/test_climate_research.py`
- Modify: `tests/test_climate_ccdr_context.py`

- [ ] **Step 1: Write failing normalization tests**

Add tests that define the accepted bundle and prove hostile or generic records are removed:

```python
from sector_lenses.research import (
    CLIMATE_RESEARCH_END,
    CLIMATE_RESEARCH_START,
    format_climate_research_context,
    normalize_climate_research_bundle,
)


def test_climate_research_bundle_keeps_grounded_project_specific_claims():
    raw = {
        "status": "complete",
        "attempts": 1,
        "sources": [{
            "id": "climate-source-1",
            "source_type": "ccdr",
            "title": "Example Country CCDR",
            "url": "https://openknowledge.worldbank.org/example",
            "publication_date": "2025",
        }],
        "claims": [{
            "id": "climate-claim-1",
            "source_ids": ["climate-source-1"],
            "claim": "Changing flood timing affects landing-site access.",
            "geographies": ["Upper Nile"],
            "project_elements": ["Landing-site rehabilitation"],
            "affected_groups": ["Fishing households"],
            "systems_or_assets": ["Access roads"],
            "evidence_status": "observed",
            "confidence": "medium",
            "time_horizons": ["project-lifetime"],
            "evidence_gap": "No site-level design flood standard was found.",
        }],
    }

    result = normalize_climate_research_bundle(raw)

    assert result["status"] == "complete"
    assert result["claims"][0]["id"] == "climate-claim-1"
    assert result["claims"][0]["time_horizons"] == ["project-lifetime"]
    assert "Landing-site rehabilitation" in format_climate_research_context(result)


def test_climate_research_bundle_rejects_generic_or_untrusted_claims():
    raw = {
        "status": "complete",
        "sources": [{
            "id": "climate-source-1",
            "source_type": "blog",
            "title": "Untrusted",
            "url": "http://example.com/post",
        }],
        "claims": [{
            "id": "climate-claim-1",
            "source_ids": [],
            "claim": "Climate change may cause conflict.",
            "geographies": [],
            "project_elements": [],
            "affected_groups": [],
            "systems_or_assets": [],
            "evidence_status": "inferred",
            "confidence": "low",
            "time_horizons": [],
        }],
    }

    result = normalize_climate_research_bundle(raw)

    assert result["sources"] == []
    assert result["claims"] == []
    assert result["status"] == "failed"
```

- [ ] **Step 2: Run the tests to verify RED**

Run:

```powershell
python -m pytest tests/test_climate_research.py -q
```

Expected: collection fails because `sector_lenses.research` does not exist.

- [ ] **Step 3: Implement the bounded contract**

Create `sector_lenses/research.py` with these public values and functions:

```python
"""Validated, bounded Climate-FCV web-research contracts."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse

CLIMATE_RESEARCH_START = "%%%CLIMATE_RESEARCH_START%%%"
CLIMATE_RESEARCH_END = "%%%CLIMATE_RESEARCH_END%%%"
CLIMATE_TIME_HORIZONS = {
    "current-near-term", "project-lifetime", "asset-system-lifetime",
}
CLIMATE_EVIDENCE_STATUSES = {"observed", "projected", "inferred"}
CLIMATE_CONFIDENCE_LEVELS = {"high", "medium", "low"}
CLIMATE_SOURCE_TYPES = {
    "ccdr", "world-bank", "un", "government", "scientific",
    "specialist", "current-operations",
}
TRUSTED_CLIMATE_HOST_SUFFIXES = (
    "worldbank.org", "ipcc.ch", "un.org", "undp.org", "unep.org",
    "unhcr.org", "wfp.org", "fao.org", "iom.int", "reliefweb.int",
    "cgiar.org", "cgspace.cgiar.org", "adelphi.de", "oecd.org",
)


def _bounded(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _strings(value: Any, count: int, size: int) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(
        _bounded(item, size) for item in value if _bounded(item, size)
    ))[:count]


def _trusted_https(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").casefold()
    return parsed.scheme == "https" and any(
        host == suffix or host.endswith("." + suffix)
        for suffix in TRUSTED_CLIMATE_HOST_SUFFIXES
    )


def normalize_climate_research_bundle(payload: Any) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    sources: list[dict[str, str]] = []
    for item in raw.get("sources", []) if isinstance(raw.get("sources"), list) else []:
        if not isinstance(item, dict):
            continue
        source_id = _bounded(item.get("id"), 80)
        source_type = _bounded(item.get("source_type"), 40)
        url = _bounded(item.get("url"), 1000)
        title = _bounded(item.get("title"), 300)
        if (
            not re.fullmatch(r"climate-source-[1-9][0-9]?", source_id)
            or source_type not in CLIMATE_SOURCE_TYPES
            or not title
            or not _trusted_https(url)
        ):
            continue
        sources.append({
            "id": source_id,
            "lens_id": "climate",
            "source_type": source_type,
            "title": title,
            "url": url,
            "publication_date": _bounded(item.get("publication_date"), 40),
            "location": _bounded(item.get("location"), 200),
        })
        if len(sources) == 10:
            break
    allowed_sources = {item["id"] for item in sources}
    claims: list[dict[str, Any]] = []
    for item in raw.get("claims", []) if isinstance(raw.get("claims"), list) else []:
        if not isinstance(item, dict):
            continue
        claim_id = _bounded(item.get("id"), 80)
        project_elements = _strings(item.get("project_elements"), 4, 180)
        anchors = (
            _strings(item.get("geographies"), 4, 160)
            + _strings(item.get("affected_groups"), 4, 160)
            + _strings(item.get("systems_or_assets"), 4, 180)
        )
        source_ids = [
            value for value in _strings(item.get("source_ids"), 4, 80)
            if value in allowed_sources
        ]
        evidence_status = _bounded(item.get("evidence_status"), 20)
        confidence = _bounded(item.get("confidence"), 20)
        horizons = [
            value for value in _strings(item.get("time_horizons"), 3, 40)
            if value in CLIMATE_TIME_HORIZONS
        ]
        if (
            not re.fullmatch(r"climate-claim-[1-9][0-9]?", claim_id)
            or not _bounded(item.get("claim"), 700)
            or not project_elements
            or not anchors
            or not source_ids
            or evidence_status not in CLIMATE_EVIDENCE_STATUSES
            or confidence not in CLIMATE_CONFIDENCE_LEVELS
            or not horizons
        ):
            continue
        claims.append({
            "id": claim_id,
            "claim": _bounded(item.get("claim"), 700),
            "source_ids": source_ids,
            "geographies": _strings(item.get("geographies"), 4, 160),
            "project_elements": project_elements,
            "affected_groups": _strings(item.get("affected_groups"), 4, 160),
            "systems_or_assets": _strings(item.get("systems_or_assets"), 4, 180),
            "evidence_status": evidence_status,
            "confidence": confidence,
            "time_horizons": horizons,
            "evidence_gap": _bounded(item.get("evidence_gap"), 500),
        })
        if len(claims) == 12:
            break
    requested_status = _bounded(raw.get("status"), 20)
    status = requested_status if requested_status in {"complete", "partial"} else "failed"
    if not claims:
        status = "failed"
    return {
        "status": status,
        "attempts": min(max(int(raw.get("attempts", 0) or 0), 0), 2),
        "sources": sources,
        "claims": claims,
        "failure_reason": _bounded(raw.get("failure_reason"), 240),
    }


def extract_climate_research_bundle(text: str) -> tuple[str, dict[str, Any]]:
    match = re.search(
        re.escape(CLIMATE_RESEARCH_START) + r"(.*?)"
        + re.escape(CLIMATE_RESEARCH_END),
        text or "",
        re.DOTALL,
    )
    visible = re.sub(
        re.escape(CLIMATE_RESEARCH_START) + r".*?(?:"
        + re.escape(CLIMATE_RESEARCH_END) + r"|$)",
        "",
        text or "",
        flags=re.DOTALL,
    ).strip()
    if not match:
        return visible, normalize_climate_research_bundle({})
    try:
        payload = json.loads(match.group(1).strip())
    except (json.JSONDecodeError, TypeError, ValueError):
        payload = {}
    return visible, normalize_climate_research_bundle(payload)


def format_climate_research_context(bundle: Any) -> str:
    normalized = normalize_climate_research_bundle(bundle)
    if not normalized["claims"]:
        return ""
    return json.dumps(
        {"sources": normalized["sources"], "claims": normalized["claims"]},
        ensure_ascii=False,
        separators=(",", ":"),
    )
```

Update `sector_lenses/__init__.py` to export all four constants/functions. Extend `normalize_lens_context_sources()` in `context.py` to accept the normalized Climate sources in addition to the legacy `context-ccdr` record, keeping the existing CCDR path valid.

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python -m pytest tests/test_climate_research.py tests/test_climate_ccdr_context.py -q
```

Expected: all tests pass; existing CCDR tests remain green.

- [ ] **Step 5: Commit**

```powershell
git add -- sector_lenses/research.py sector_lenses/context.py sector_lenses/__init__.py tests/test_climate_research.py tests/test_climate_ccdr_context.py
git commit -m "feat: add climate research contract"
```

---

### Task 2: Add Dedicated Climate Research with One Narrow Retry

**Files:**
- Modify: `sector_lenses/research.py`
- Modify: `app.py:5694-5764`
- Modify: `tests/test_climate_research.py`
- Modify: `tests/test_climate_ccdr_context.py`

- [ ] **Step 1: Write failing research-runner tests**

```python
def test_climate_research_prompt_requires_ccdr_subnational_and_temporal_claims():
    prompt = build_climate_research_prompt(
        country="South Sudan",
        sector="Natural resources",
        project_profile={
            "locations": ["Upper Nile", "Jonglei"],
            "project_elements": ["Landing sites", "Community conservancies"],
            "groups": ["Fishing households", "Pastoralists"],
            "assets": ["Access roads"],
        },
        narrow=False,
    )
    assert "public Country Climate and Development Report" in prompt
    assert "Upper Nile" in prompt
    assert "asset-system-lifetime" in prompt
    assert CLIMATE_RESEARCH_START in prompt


def test_climate_research_prompt_treats_ccdr_as_optional_context():
    prompt = build_climate_research_prompt(
        country="Exampleland",
        sector="Water",
        project_profile=PROJECT_PROFILE,
        narrow=False,
    )
    assert "First check for a public Country Climate and Development Report" in prompt
    assert "Use it only where directly relevant" in prompt
    assert "fill material gaps from authoritative" in prompt


def test_climate_research_retries_once_with_narrow_query():
    client = SequencedResearchClient([
        anthropic.APITimeoutError(
            request=httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        ),
        valid_climate_response(),
    ])

    result = app_module.run_climate_web_research(
        "South Sudan", "Natural resources", PROJECT_PROFILE, client
    )

    assert result["status"] == "complete"
    assert result["attempts"] == 2
    assert len(client.calls) == 2
    assert "NARROW RETRY" in client.calls[1]["messages"][0]["content"]


def test_core_research_budget_is_unchanged_without_climate():
    client = _ResearchClient("Visible research")
    app_module.run_fcv_web_research("Exampleland", "Water", client)
    assert client.kwargs["max_tokens"] == 5500
    assert client.kwargs["tools"][0]["max_uses"] == 4
```

- [ ] **Step 2: Run tests to verify RED**

```powershell
python -m pytest tests/test_climate_research.py tests/test_climate_ccdr_context.py -q
```

Expected: failures for missing prompt builder and `run_climate_web_research`.

- [ ] **Step 3: Implement prompts and bounded retry**

Add to `sector_lenses/research.py`:

```python
def build_climate_research_prompt(
    country: str,
    sector: str,
    project_profile: dict[str, Any],
    narrow: bool = False,
) -> str:
    scope = "NARROW RETRY: return at most six strongest claims." if narrow else (
        "Return at most twelve claims, prioritizing material project pathways."
    )
    return f"""
Research Climate-FCV conditions for {country} and this {sector} project.
First check for a public Country Climate and Development Report. Use it only
where directly relevant, then fill material gaps from authoritative World Bank,
UN, scientific, government, or established specialist sources.

PROJECT PROFILE:
{json.dumps(project_profile, ensure_ascii=False, separators=(",", ":"))}

Cover observed and projected hazards, changing seasonality, subnational
locations, differentiated groups, delivery constraints, maladaptation,
distributional effects, and both directions of project influence. Distinguish
current-near-term, project-lifetime, and asset-system-lifetime implications.
Every claim must name a project element and a geography, group, system, or
asset. Do not return generic country statements. {scope}

Return no prose. Return one JSON object between {CLIMATE_RESEARCH_START} and
{CLIMATE_RESEARCH_END} with status, attempts, sources, and claims using the
validated ClimateResearchBundle contract.
""".strip()
```

Add `run_climate_web_research()` to `app.py` beside `run_fcv_web_research()`:

```python
def run_climate_web_research(country, sector, project_profile, api_client):
    for attempt, narrow in ((1, False), (2, True)):
        prompt = build_climate_research_prompt(
            country, sector, project_profile, narrow=narrow
        )
        try:
            response = api_client.beta.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=5000 if not narrow else 3200,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5 if not narrow else 3,
                }],
                messages=[{"role": "user", "content": prompt}],
                betas=["web-search-2025-03-05"],
            )
            text = "\n".join(
                block.text for block in response.content
                if getattr(block, "type", "") == "text"
            )
            _, bundle = extract_climate_research_bundle(text)
            bundle["attempts"] = attempt
            if bundle["claims"]:
                return bundle
        except anthropic.APITimeoutError:
            if attempt == 1:
                continue
            break
        except Exception:
            break
    return normalize_climate_research_bundle({
        "status": "failed",
        "attempts": 2,
        "failure_reason": "Dedicated Climate-FCV research could not be completed.",
    })
```

Remove CCDR instructions from the core research call. Keep `run_fcv_web_research()` defaults exactly at 5,500 tokens and four searches. When Climate is active, its caller may request a reduced core budget through explicit `max_tokens=4000, max_uses=3`; core-only callers must omit those overrides.

- [ ] **Step 4: Run focused tests**

```powershell
python -m pytest tests/test_climate_research.py tests/test_climate_ccdr_context.py -q
```

Expected: all pass, including unchanged core defaults.

- [ ] **Step 5: Commit**

```powershell
git add -- sector_lenses/research.py app.py tests/test_climate_research.py tests/test_climate_ccdr_context.py
git commit -m "feat: research climate fcv context separately"
```

---

### Task 3: Integrate Shared Research into Both Stage 1 Workflows

**Files:**
- Modify: `app.py:6492-6604`
- Modify: `app.py:6975-7202`
- Modify: `index.html:2500-3805`
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write failing orchestration tests**

Add tests for a pure `build_stage1_research_plan()` and both route contracts:

```python
def test_climate_active_research_plan_balances_core_and_climate():
    plan = app_module.build_stage1_research_plan(
        active_lens_ids=["climate"],
        country="South Sudan",
        sector="Natural resources",
        doc_parts=[{
            "label": "PROJECT DOCUMENT",
            "name": "Concept Note",
            "raw_text": "Sites: Upper Nile and Jonglei. Landing sites and conservancies.",
        }],
    )
    assert plan["core"]["max_uses"] == 3
    assert plan["climate"]["enabled"] is True
    assert plan["project_profile"]["locations"]


def test_core_only_research_plan_preserves_current_budget():
    plan = app_module.build_stage1_research_plan(
        active_lens_ids=[],
        country="Exampleland",
        sector="Water",
        doc_parts=[],
    )
    assert plan["core"] == {"max_tokens": 5500, "max_uses": 4}
    assert plan["climate"]["enabled"] is False


def test_express_and_step_routes_emit_climate_research_context():
    source = Path(app_module.__file__).read_text(encoding="utf-8")
    assert source.count("'climate_research': climate_research") >= 2
    assert source.count("format_climate_research_context(climate_research)") >= 2


def test_active_climate_supersedes_lightweight_conditional_check():
    state = app_module.AnalysisState.from_payload({"active_lenses": ["climate"]})
    prompt = app_module.build_lens_stage_context(state, 2)["prompt"]
    assert "supersedes the lightweight supplementary Climate-FCV" in prompt
    assert "do not produce a duplicate supplementary Climate finding" in prompt
```

Add a frontend persistence test asserting `climateResearch`, the Stage 1 event assignment, Stage 2 request payload, report payload, and session reset are all present.

- [ ] **Step 2: Run tests to verify RED**

```powershell
python -m pytest tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py -k "research_plan or climate_research_context or persists_climate_research" -q
```

Expected: failures for missing helper/state fields.

- [ ] **Step 3: Implement one shared research plan and bounded injection**

Add:

```python
def build_stage1_research_plan(
    active_lens_ids: list[str],
    country: str,
    sector: str,
    doc_parts: list[dict[str, Any]],
) -> dict[str, Any]:
    climate_active = "climate" in active_lens_ids
    project_text = "\n".join(
        str(part.get("raw_text", ""))[:8000]
        for part in doc_parts if isinstance(part, dict)
    )
    return {
        "country": country,
        "sector": sector,
        "core": {
            "max_tokens": 4000 if climate_active else 5500,
            "max_uses": 3 if climate_active else 4,
        },
        "climate": {"enabled": climate_active},
        "project_profile": {
            "locations": extract_project_research_anchors(
                project_text, "locations", limit=8
            ),
            "project_elements": extract_project_research_anchors(
                project_text, "project elements", limit=8
            ),
            "groups": extract_project_research_anchors(
                project_text, "affected groups", limit=8
            ),
            "assets": extract_project_research_anchors(
                project_text, "long-lived assets and systems", limit=8
            ),
        },
    }
```

Extract the duplicated research sections from `run_stage()` and `run_express()` into `_run_stage1_research(plan)`. Execute core and Climate futures concurrently. Poll futures every 15 seconds so the outer generators can emit safe `research_status` keepalives. Return:

```python
{
    "core_brief": str,
    "climate_research": ClimateResearchBundle,
    "lens_context_sources": list[dict],
}
```

Inject the core brief under the existing heading. Inject Climate research only as compact JSON:

```python
climate_context = format_climate_research_context(climate_research)
if climate_context:
    content_parts.append({
        "type": "text",
        "text": (
            "\n\n--- VALIDATED CLIMATE-FCV RESEARCH CLAIMS ---\n"
            + climate_context
            + "\n--- END VALIDATED CLIMATE-FCV RESEARCH CLAIMS ---\n"
        ),
    })
```

Add `climate_research` to both Stage 1 completion events. In `index.html`, add `let climateResearch={};`, persist it from Stage 1, send it in Stage 2/3 and report payloads, and clear it on a new analysis.

- [ ] **Step 4: Run Stage 1 and frontend tests**

```powershell
python -m pytest tests/test_climate_research.py tests/test_climate_ccdr_context.py tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py -k "research or core_only" -q
```

Expected: all selected tests pass.

- [ ] **Step 5: Commit**

```powershell
git add -- app.py index.html tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py
git commit -m "feat: integrate balanced climate research"
```

**Review checkpoint after Task 3:** Review research source validation, core-only invariance, retry limits, SSE keepalives, cache separation, and prompt sizes before changing diagnostic schemas.

---

### Task 4: Extend the Climate Diagnostic with Stable Causal Pathways and Horizons

**Files:**
- Modify: `sector_lenses/pipeline.py:174-482`
- Modify: `sector_lenses/modules/climate/manifest.yaml`
- Modify: `sector_lenses/modules/climate/guidance.md`
- Modify: `sector_lenses/modules/climate/questions.yaml`
- Modify: `tests/test_sector_lens_pipeline.py`
- Modify: `tests/test_climate_lens_package.py`

- [ ] **Step 1: Write failing normalization and specificity tests**

```python
def test_climate_interactions_keep_specific_pathways_and_horizons():
    payload = {"lenses": [{
        "lens_id": "climate",
        "applicability": "material",
        "materiality_level": "high",
        "materiality_summary": "Flood timing is material to fisheries delivery.",
        "interaction_readout": [{
            "direction_id": "climate-fcv-on-project",
            "summary": "Flood timing and insecurity jointly affect landing sites.",
            "pathways": [{
                "pathway_id": "climate-fcv-on-project-1",
                "pressure": "More erratic flood timing",
                "mechanism": "Road access and seasonal movement become less predictable.",
                "project_implication": "Landing-site works in Upper Nile may become inaccessible.",
                "design_response": "Use site flood/access thresholds and seasonal work windows.",
                "project_elements": ["Landing-site rehabilitation"],
                "geographies": ["Upper Nile"],
                "affected_groups": ["Fishing households"],
                "time_horizons": ["project-lifetime", "asset-system-lifetime"],
                "research_claim_ids": ["climate-claim-1"],
                "confidence": "medium",
                "evidence_gap": "Site design standards are not documented.",
            }],
        }, {
            "direction_id": "project-on-climate-fcv",
            "summary": "Access rules may redistribute resilience and conflict risk.",
            "pathways": [{
                "pathway_id": "project-on-climate-fcv-1",
                "pressure": "Formalized access rules",
                "mechanism": "Rules change who can use fisheries during variable seasons.",
                "project_implication": "Seasonal users may lose access and adaptive options.",
                "design_response": "Represent seasonal users and monitor distributional effects.",
                "project_elements": ["BFMU governance"],
                "geographies": ["Sudd"],
                "affected_groups": ["Seasonal fishing households"],
                "time_horizons": ["current-near-term", "project-lifetime"],
                "research_claim_ids": ["climate-claim-2"],
                "confidence": "medium",
                "evidence_gap": "",
            }],
        }],
        "readout_sections": [],
        "additional_pathways": [],
    }], "findings": []}

    result = normalize_lens_diagnostic(payload, ["climate"])
    pathways = result["lenses"][0]["interaction_readout"][0]["pathways"]
    assert pathways[0]["pathway_id"] == "climate-fcv-on-project-1"
    assert pathways[0]["time_horizons"][-1] == "asset-system-lifetime"


def test_generic_climate_pathway_is_suppressed():
    generic = valid_payload_with_pathway({
        "pathway_id": "climate-fcv-on-project-1",
        "pressure": "Climate stress",
        "mechanism": "Tensions may increase.",
        "project_implication": "The project may be affected.",
        "design_response": "Monitor climate.",
        "project_elements": [],
        "geographies": [],
        "affected_groups": [],
        "time_horizons": [],
        "research_claim_ids": [],
        "confidence": "low",
    })
    result = normalize_lens_diagnostic(generic, ["climate"])
    assert result["lenses"][0]["interaction_readout"][0]["pathways"] == []
```

- [ ] **Step 2: Run tests to verify RED**

```powershell
python -m pytest tests/test_sector_lens_pipeline.py tests/test_climate_lens_package.py -k "pathway or horizon or specificity" -q
```

Expected: missing normalized `pathways` and new package instructions.

- [ ] **Step 3: Implement the additive diagnostic fields**

In `pipeline.py`, normalize at most four pathways per direction. A pathway is retained only when it has:

```python
required = (
    pathway_id matches rf"{direction_id}-[1-4]",
    pressure,
    mechanism,
    project_implication,
    design_response,
    at least one project_element,
    at least one of geography/affected_group/system_or_asset,
    at least one valid time_horizon,
    at least one climate research claim ID or an explicit evidence_gap,
    confidence in {"high", "medium", "low"},
)
```

Return this exact bounded shape:

```python
{
    "pathway_id": pathway_id,
    "pressure": text[:300],
    "mechanism": text[:500],
    "project_implication": text[:600],
    "design_response": text[:600],
    "project_elements": bounded_strings(..., 4, 180),
    "geographies": bounded_strings(..., 4, 160),
    "affected_groups": bounded_strings(..., 4, 160),
    "systems_or_assets": bounded_strings(..., 4, 180),
    "time_horizons": valid_horizons[:3],
    "research_claim_ids": matching_ids[:4],
    "confidence": confidence,
    "evidence_gap": text[:500],
}
```

Add stable `pathway_id` to every dividend item and additional pathway. Use declared item IDs for standard pathways and `additional-{section_id}-1|2` for extensions. Update Climate manifest/guidance/questions to require the new fields and the three time horizons. Increase the Climate Stage 1 budget only inside its existing module limit and reduce redundant Stage 2 guidance so the platform ceilings remain unchanged.

- [ ] **Step 4: Run pipeline and package tests**

```powershell
python -m pytest tests/test_sector_lens_pipeline.py tests/test_climate_lens_package.py -q
```

Expected: all pass.

- [ ] **Step 5: Commit**

```powershell
git add -- sector_lenses/pipeline.py sector_lenses/modules/climate/manifest.yaml sector_lenses/modules/climate/guidance.md sector_lenses/modules/climate/questions.yaml tests/test_sector_lens_pipeline.py tests/test_climate_lens_package.py
git commit -m "feat: structure climate causal pathways"
```

---

### Task 5: Update Stage 2 Prompt, Recovery, and Specificity Validation

**Files:**
- Modify: `app.py:784-946`
- Modify: `app.py:1002-1310`
- Modify: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing prompt and recovery tests**

```python
def test_climate_stage2_requires_project_specific_causal_contract():
    state = app_module.AnalysisState.from_payload({"active_lenses": ["climate"]})
    prompt = app_module.build_lens_stage_context(
        state,
        2,
        climate_research=valid_climate_bundle(),
    )["prompt"]
    for value in (
        "pressure → mediated mechanism → project implication → design response",
        "current-near-term",
        "project-lifetime",
        "asset-system-lifetime",
        "research_claim_ids",
        "Suppress generic pathways",
    ):
        assert value in prompt


def test_recovery_rejects_two_directions_without_specific_pathways():
    repaired, recovered = run_recovery_with_payload(
        diagnostic_with_empty_interaction_pathways()
    )
    assert recovered is False
    assert "specific causal pathway" in app_module.lens_diagnostic_failure_message(
        repaired, ["climate"]
    )
```

- [ ] **Step 2: Run tests to verify RED**

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -k "causal_contract or specific_pathways" -q
```

Expected: failures because Stage 2 does not accept research context or require pathways.

- [ ] **Step 3: Extend Stage 2 and recovery contracts**

Add `climate_research` to `build_lens_stage_context()`. Inject only the compact normalized bundle. Extend the Climate Stage 2 suffix and recovery shape with:

```text
For each interaction direction include 1-4 pathways. Each pathway must follow
pressure → mediated mechanism → project implication → design response and name
a project element plus a location, group, institution, system, or asset.
Include current-near-term, project-lifetime, or asset-system-lifetime and cite
research_claim_ids. Suppress generic pathways rather than filling the schema.
```

Update `lens_diagnostic_failure_message()` so High and Medium require both
directions and at least one valid pathway per direction. Low requires at least
one compact pathway overall when an interaction is displayed. Update the
6,000-token recovery prompt to cap each direction at two pathways and preserve
the 12,000-character target.

- [ ] **Step 4: Run Stage 2/recovery tests**

```powershell
python -m pytest tests/test_sector_lens_app_contract.py tests/test_sector_lens_pipeline.py -k "stage2 or diagnostic or recovery or pathway" -q
```

Expected: all selected tests pass.

- [ ] **Step 5: Commit**

```powershell
git add -- app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: validate specific climate interactions"
```

---

### Task 6: Add Backward-Compatible Priority Climate Links

**Files:**
- Modify: `app.py:1330-3780`
- Modify: `app.py:4800-4965`
- Modify: `sector_lenses/pipeline.py`
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `tests/test_sector_lens_pipeline.py`
- Update privately: `C:\Users\wb559324\.claude\FCV_BUILD_PARITY.md`

- [ ] **Step 1: Write failing priority-link tests**

Define the additive field:

```json
"climate_links": {
  "status": "linked",
  "interaction_pathway_ids": ["climate-fcv-on-project-1"],
  "dividend_pathway_ids": ["institutional-capacity-legitimacy"],
  "finding_ids": ["climate-finding-1"],
  "contribution": "The priority strengthens inclusive seasonal access rules.",
  "strengthening_effect": "It reduces exclusion and preserves adaptive options.",
  "reason": ""
}
```

Or, for a core priority:

```json
"climate_links": {
  "status": "no-material-pathway",
  "interaction_pathway_ids": [],
  "dividend_pathway_ids": [],
  "finding_ids": [],
  "contribution": "",
  "strengthening_effect": "",
  "reason": "Retained because the SEA/SH risk is material on core FCV grounds."
}
```

Add tests:

```python
def test_priority_parser_derives_climate_provenance_from_valid_links():
    parsed = app_module.extract_priorities(
        stage3_json(priority_with_climate_links()),
        active_lens_ids=["climate"],
        lens_diagnostic=valid_linked_diagnostic(),
    )
    priority = parsed["priorities"][0]
    assert priority["lens_ids"] == ["climate"]
    assert priority["climate_links"]["status"] == "linked"


def test_every_climate_priority_requires_link_or_no_material_reason():
    parsed = app_module.extract_priorities(
        stage3_json(priority_without_climate_links()),
        active_lens_ids=["climate"],
        lens_diagnostic=valid_linked_diagnostic(),
    )
    assert parsed["error"] is True
    assert "Climate priority linkage" in parsed["message"]


def test_unknown_climate_link_ids_are_removed():
    links = normalize_priority_climate_links(
        priority_with_unknown_ids()["climate_links"],
        valid_linked_diagnostic(),
    )
    assert links["interaction_pathway_ids"] == []
```

- [ ] **Step 2: Run tests to verify RED**

```powershell
python -m pytest tests/test_sector_lens_app_contract.py tests/test_sector_lens_pipeline.py -k "climate_provenance or priority_link or no_material_reason" -q
```

Expected: failures for the missing field and normalizer.

- [ ] **Step 3: Implement deterministic link normalization**

Add `normalize_priority_climate_links(raw, diagnostic)` in
`sector_lenses/pipeline.py`. Build allowlists from normalized interaction
pathways, dividend pathways, and findings. Require:

```python
if status == "linked":
    keep only recognized IDs
    require at least one recognized ID
    require contribution and strengthening_effect
elif status == "no-material-pathway":
    require no IDs and a non-empty reason
else:
    return {}
```

Extend `extract_priorities()` with optional `lens_diagnostic`. For active
Climate, reject the structured priority set if any substantive priority lacks a
valid `climate_links` object. Derive `lens_ids=["climate"]` when status is
`linked`; do not depend on model-provided `lens_ids`. Preserve existing fields
and behavior for core-only and old sessions.

Update the Stage 3 JSON example and required-field instructions in `app.py` so
every Climate-active priority includes `climate_links`. Do not add it to
`_REQUIRED_PRIORITY_FIELDS` globally; it is conditional on active Climate.

- [ ] **Step 4: Run parser and contract tests**

```powershell
python -m pytest tests/test_sector_lens_app_contract.py tests/test_sector_lens_pipeline.py -k "priority or climate_link or provenance" -q
```

Expected: all selected tests pass, including the former High-materiality warning case.

- [ ] **Step 5: Record the shared contract and commit**

Append this private parity entry without committing the private file:

```text
2026-07-23 | Render Climate dual-use v2 | Stage 3 priority JSON adds optional
climate_links {status, interaction_pathway_ids, dividend_pathway_ids,
finding_ids, contribution, strengthening_effect, reason}. Required only when
Climate is active; core-only and existing fields remain unchanged. Mirror in
the companion build before enabling the redesigned Climate renderer there.
```

Then:

```powershell
git add -- app.py sector_lenses/pipeline.py tests/test_sector_lens_app_contract.py tests/test_sector_lens_pipeline.py
git commit -m "feat: link climate pathways to priorities"
```

**Review checkpoint after Task 6:** Review backward compatibility, priority JSON
parity, failure semantics, deterministic provenance, and the no-forced-benefit
rule before changing Stage 3 narrative and UI.

---

### Task 7: Rebalance and Integrate the Stage 3 Narrative

**Files:**
- Modify: `app.py:826-946`
- Modify: `app.py:3500-3780`
- Modify: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing Stage 3 design tests**

```python
def test_climate_stage3_integrates_core_narrative_and_qualitative_dividends():
    context = app_module.build_lens_stage_context(
        climate_state(),
        3,
        lens_diagnostic=valid_linked_diagnostic(),
        climate_research=valid_climate_bundle(),
    )
    prompt = context["prompt"]
    for value in (
        "bold opening assessment",
        "operational context",
        "strengths",
        "gaps",
        "FCV sensitivity",
        "FCV responsiveness",
        "qualitative Climate, peace and social dividends synthesis",
        "Do not produce dividend cards",
        "no more than five substantive priorities",
        "Adaptation and resilience are primary",
        "deep mitigation only when",
    ):
        assert value in prompt


def test_core_only_stage3_prompt_is_unchanged():
    before = app_module.build_lens_stage_context(core_state(), 3)["prompt"]
    assert before == ""


def test_climate_stage3_does_not_duplicate_lightweight_climate_check():
    prompt = app_module.build_lens_stage_context(
        climate_state(),
        3,
        lens_diagnostic=valid_linked_diagnostic(),
    )["prompt"]
    assert "lightweight conditional Climate-FCV check" not in prompt
    assert prompt.count("two substantive interaction narratives") == 1
```

- [ ] **Step 2: Run tests to verify RED**

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -k "qualitative_dividends or core_only_stage3" -q
```

Expected: Climate Stage 3 assertions fail; core-only remains green.

- [ ] **Step 3: Implement the bounded integrated Stage 3 prompt**

Update the Stage 3 Climate prefix to require:

```text
Preserve the full core FCV structure. Integrate material Climate-FCV evidence
into the bold opening assessment, operational context, strengths, gaps, FCV
sensitivity, and FCV responsiveness without duplicate Climate paragraphs.
The active Climate diagnostic supersedes the lightweight conditional
Climate-FCV check used by core-only runs; do not emit both. Adaptation and
resilience are primary. Include deep mitigation only when the evidence shows a
clear project-to-emissions or transition pathway and explains its FCV effects.
Use the validated pathways to write two substantive interaction narratives.
After each narrative provide a compact causal strip using pressure -> mechanism
-> project implication -> design response and time-horizon labels.
Write one qualitative Climate, peace and social dividends synthesis explaining
current contribution, supported versus potential pathways, watchpoints, and
links to numbered priorities. Do not produce dividend cards or a checklist.
```

Keep the existing 900-token platform Stage 3 lens budget. Compact the
diagnostic with `_bounded_stage3_lenses()` by prioritizing:

1. materiality;
2. two direction summaries;
3. two strongest pathways per direction;
4. up to four dividend pathways;
5. candidate finding IDs and mappings.

Do not pass raw Climate research to Stage 3; it receives only the validated
Stage 2 diagnostic.

- [ ] **Step 4: Run Stage 3 and budget tests**

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -k "stage3 or budget or core_only" -q
```

Expected: all selected tests pass and `estimated_tokens <= 900`.

- [ ] **Step 5: Commit**

```powershell
git add -- app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: integrate climate across fcv narrative"
```

---

### Task 8: Redesign Live and Shared HTML Climate Sections

**Files:**
- Modify: `index.html:345-367`
- Modify: `index.html:2526-2685`
- Modify: `index.html:5210-5250`
- Modify: `index.html:5740-5850`
- Modify: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write failing renderer tests**

Replace the old dividend-card expectations with:

```javascript
const interactions = renderClimateInteractions(high);
if (!interactions.includes('climate-interaction-narrative')) throw new Error(interactions);
if (!interactions.includes('causal-strip')) throw new Error(interactions);
if (!interactions.includes('Project lifetime')) throw new Error(interactions);
if (!interactions.includes('Landing-site rehabilitation')) throw new Error(interactions);

const synthesis = renderClimateDividendSynthesis(high, priorities);
if (!synthesis.includes('How the current design contributes')) throw new Error(synthesis);
if (!synthesis.includes('Priority 2')) throw new Error(synthesis);
if (synthesis.includes('climate-dividend-card')) throw new Error(synthesis);

const linked = renderPriorityClimateContribution(priorityWithLinks);
if (!linked.includes('Climate, peace and social dividend contribution')) throw new Error(linked);
const unlinked = renderPriorityClimateContribution(priorityWithoutMaterialPathway);
if (!unlinked.includes('No material dividend pathway identified')) throw new Error(unlinked);
```

Also assert the shared HTML exporter and live card renderer both call
`renderPriorityClimateContribution()` when Climate is active and retain the
existing differentiated note when it is not.

- [ ] **Step 2: Run frontend tests to verify RED**

```powershell
python -m pytest tests/test_climate_lens_frontend.py -q
```

Expected: failures for missing narrative, synthesis, causal-strip, and priority helpers.

- [ ] **Step 3: Implement semantic render helpers**

Implement:

```javascript
function renderClimatePathwayStrip(pathway) {
  const horizons = (pathway.time_horizons||[]).map(renderHorizonBadge).join('');
  return `<div class="causal-strip">
    <div><span>Pressure</span>${esc(pathway.pressure)}</div>
    <div><span>Mechanism</span>${esc(pathway.mechanism)}</div>
    <div><span>Project implication</span>${esc(pathway.project_implication)}</div>
    <div><span>Design response</span>${esc(pathway.design_response)}</div>
  </div><div class="horizon-badges">${horizons}</div>`;
}

function renderPriorityClimateContribution(priority) {
  const links = priority && priority.climate_links;
  if (!links) return '';
  if (links.status === 'no-material-pathway') {
    return climateContributionZone(
      'No material dividend pathway identified',
      links.reason
    );
  }
  return climateContributionZone(
    'Climate, peace and social dividend contribution',
    `${esc(links.contribution)} ${esc(links.strengthening_effect)}`
  );
}
```

Rewrite `renderClimateInteractions()` as two stacked analytical sections with
summary, pathways, evidence gap/confidence, and causal strips. Replace
`renderClimateDividends()` with `renderClimateDividendSynthesis(lens,
priorities)`, producing two or three narrative paragraphs and numbered priority
links. Update both live and shared HTML priority cards to use the Climate panel
instead of `country_category_relevance` only when Climate is active.

Use existing escaping helpers for every model-derived string. Add responsive CSS
that collapses each four-step strip vertically below 768px.

- [ ] **Step 4: Run frontend tests**

```powershell
python -m pytest tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py -k "frontend or html or renderer or priority" -q
```

Expected: all selected tests pass.

- [ ] **Step 5: Commit**

```powershell
git add -- index.html tests/test_climate_lens_frontend.py tests/test_sector_lens_app_contract.py
git commit -m "feat: redesign climate output sections"
```

---

### Task 9: Make DOCX Export Match the Redesigned Output

**Files:**
- Modify: `app.py:8000-8085`
- Modify: `app.py:8120-8725`
- Modify: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing DOCX parity tests**

```python
def test_climate_docx_uses_narratives_strips_synthesis_and_priority_links():
    response = client.post("/api/export-report", json=climate_report_payload())
    document = Document(io.BytesIO(response.data))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert "How Climate-FCV dynamics could affect this project" in text
    assert "Pressure:" in text
    assert "Mechanism:" in text
    assert "Project implication:" in text
    assert "Design response:" in text
    assert "Asset/system lifetime" in text
    assert "How the current design contributes" in text
    assert "Climate, peace and social dividend contribution" in text
    assert "Differentiated approach note" not in text


def test_core_only_docx_retains_differentiated_approach_note():
    response = client.post("/api/export-report", json=core_report_payload())
    text = docx_text(response.data)
    assert "Differentiated approach note" in text
```

- [ ] **Step 2: Run DOCX tests to verify RED**

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -k "docx and climate" -q
```

Expected: redesigned headings and priority panel are missing.

- [ ] **Step 3: Implement DOCX helpers from normalized structures**

Replace `add_climate_interactions()` and `add_climate_dividends()` with:

```python
def add_causal_strip(pathway):
    add_field("Pressure", pathway.get("pressure"))
    add_field("Mechanism", pathway.get("mechanism"))
    add_field("Project implication", pathway.get("project_implication"))
    add_field("Design response", pathway.get("design_response"))
    horizons = ", ".join(
        horizon_display(value)
        for value in pathway.get("time_horizons", [])
    )
    add_field("Time horizon", horizons)


def add_priority_climate_contribution(priority):
    links = priority.get("climate_links") or {}
    _add_section_heading(
        "Climate, peace and social dividend contribution", level=4
    )
    if links.get("status") == "no-material-pathway":
        _add_single_para("No material dividend pathway identified.", bold=True)
        _add_single_para(links.get("reason", ""))
    else:
        _add_single_para(links.get("contribution", ""))
        _add_single_para(links.get("strengthening_effect", ""))
```

Use the same normalized lens diagnostic and priorities as HTML. Add the
qualitative synthesis before the priority table. In Climate-active reports,
omit the per-priority differentiated note and call
`add_priority_climate_contribution()`. Preserve core-only behavior.

- [ ] **Step 4: Run DOCX and app contract tests**

```powershell
python -m pytest tests/test_sector_lens_app_contract.py -q
```

Expected: all app contract tests pass.

- [ ] **Step 5: Commit**

```powershell
git add -- app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: export redesigned climate assessment"
```

**Review checkpoint after Task 9:** Compare live HTML, shared HTML, and DOCX
section order, wording, priority panels, core-only invariance, escaping, and
mobile/print layout before adding final telemetry and regression fixtures.

---

### Task 10: Add Safe Research and Specificity Telemetry

**Files:**
- Modify: `app.py`
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `tests/test_climate_research.py`

- [ ] **Step 1: Write failing privacy-safe telemetry tests**

```python
def test_climate_research_telemetry_is_structural_and_private(caplog):
    sentinel = "SECRET PROJECT CLAIM MUST NOT LEAK"
    bundle = valid_climate_bundle(claim=sentinel)
    with caplog.at_level("INFO", logger=app_module.app.logger.name):
        app_module.log_climate_research_summary(
            "assessment-1", bundle, elapsed_ms=1234
        )
    assert "assessment-1" in caplog.text
    assert "claims=2" in caplog.text
    assert "sources=2" in caplog.text
    assert sentinel not in caplog.text


def test_specificity_telemetry_does_not_log_rejected_pathway_text(caplog):
    sentinel = "SECRET GENERIC PATHWAY"
    app_module.log_climate_specificity_summary(
        "assessment-1",
        {"accepted": 2, "rejected": 1, "rejected_text": sentinel},
    )
    assert "accepted=2" in caplog.text
    assert "rejected=1" in caplog.text
    assert sentinel not in caplog.text
```

- [ ] **Step 2: Run tests to verify RED**

```powershell
python -m pytest tests/test_climate_research.py tests/test_sector_lens_app_contract.py -k "telemetry" -q
```

Expected: failures for missing log helpers.

- [ ] **Step 3: Implement allowlisted summaries**

Log only:

```python
{
    "assessment_id": assessment_id,
    "status": status,
    "attempts": attempts,
    "elapsed_ms": elapsed_ms,
    "source_count": len(sources),
    "claim_count": len(claims),
    "source_types": sorted(allowlisted_source_types),
    "horizon_counts": horizon_counts,
    "accepted_pathways": accepted,
    "rejected_pathways": rejected,
    "priority_linked_count": linked,
    "priority_no_material_count": no_material,
}
```

Do not log titles, URLs, claims, prompts, evidence, project elements, locations,
groups, or arbitrary payload keys. Emit warnings only for terminal research
failure, invalid diagnostic, or invalid priority linkage.

- [ ] **Step 4: Run telemetry tests**

```powershell
python -m pytest tests/test_climate_research.py tests/test_sector_lens_app_contract.py -k "telemetry or log" -q
```

Expected: all selected tests pass with sentinels absent.

- [ ] **Step 5: Commit**

```powershell
git add -- app.py tests/test_climate_research.py tests/test_sector_lens_app_contract.py
git commit -m "chore: trace climate research structure"
```

---

### Task 11: Add End-to-End South Sudan and Low-Materiality Regression Fixtures

**Files:**
- Create: `tests/fixtures/climate/south_sudan_dual_use.json`
- Modify: `tests/test_sector_lens_app_contract.py`
- Modify: `tests/test_climate_lens_frontend.py`
- Modify: `tests/test_climate_research.py`

- [ ] **Step 1: Create synthetic fixtures and failing end-to-end assertions**

The fixture must contain no uploaded-document text. Use synthetic records:

```json
{
  "country": "South Sudan",
  "project_elements": ["Landing-site rehabilitation", "BFMU governance", "Community conservancies"],
  "geographies": ["Upper Nile", "Jonglei", "Sudd"],
  "groups": ["Fishing households", "Seasonal users", "Pastoralists"],
  "expected": {
    "materiality": "high",
    "interaction_directions": 2,
    "minimum_specific_pathways": 2,
    "time_horizons": ["current-near-term", "project-lifetime", "asset-system-lifetime"],
    "substantive_priorities": 5
  }
}
```

Add an integration test that passes the synthetic research bundle through
normalization, diagnostic validation, Stage 3 context, priority parsing, HTML
render helper execution, and DOCX export. Assert:

```python
assert climate["materiality_level"] == "high"
assert all(interaction["pathways"] for interaction in climate["interaction_readout"])
assert len(priorities) == 5
assert all(priority["climate_links"] for priority in priorities)
assert "climate-dividend-card" not in shared_html
assert "No material dividend pathway identified" in shared_html
```

Add a Low-materiality fixture inline with one compact pathway, no forced linked
priority, and a valid `no-material-pathway` panel.

- [ ] **Step 2: Run integration tests to verify RED**

```powershell
python -m pytest tests/test_climate_research.py tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py -k "south_sudan or low_materiality" -q
```

Expected: failures until every pipeline stage and renderer consumes the new structures.

- [ ] **Step 3: Make only integration-level corrections**

Fix mismatched field names, missing payload propagation, or renderer ordering
revealed by the fixture. Do not weaken specificity, evidence, horizon, or link
validation to make the fixture pass.

- [ ] **Step 4: Run the entire test suite**

```powershell
python -m pytest -q
```

Expected: all tests pass. The only acceptable warning is the existing
environment-specific pytest cache permission warning.

- [ ] **Step 5: Commit**

```powershell
git add -- tests/fixtures/climate/south_sudan_dual_use.json tests/test_climate_research.py tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py app.py index.html sector_lenses
git commit -m "test: cover dual-use climate output"
```

---

### Task 12: Final Verification and Review Handoff

**Files:**
- Modify if necessary: `docs/20260722_climate_module_unresolved_failure_handoff.md` only if the user explicitly asks to update the untracked handoff
- Verify: all changed source, tests, specification, plan, and private parity log

- [ ] **Step 1: Run contract-focused verification**

```powershell
python -m pytest tests/test_climate_research.py tests/test_climate_ccdr_context.py tests/test_climate_lens_package.py tests/test_sector_lens_pipeline.py tests/test_sector_lens_app_contract.py tests/test_climate_lens_frontend.py -q
```

Expected: all focused tests pass.

- [ ] **Step 2: Run full verification**

```powershell
python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 3: Inspect repository and parity state**

```powershell
git diff --check
git status --short --branch
git log --oneline --decorate -15
```

Expected:

- no unstaged implementation changes;
- only the user-owned untracked handoff remains;
- branch is `codex/climate-fcv-output-redesign`;
- commits are separated by the tasks above;
- private parity log contains the additive `climate_links` entry and remains untracked.

- [ ] **Step 4: Review against every success criterion**

Verify from tests and a local synthetic render:

```text
Core-only unchanged.
Climate remains manual.
Climate-active research is dedicated, trusted-source, retried once, and bounded.
Climate-active core research is reduced only in that mode.
Both interaction directions contain specific causal narratives and strips.
Current, project, and asset/system horizons are visible.
Dividend cards are removed in favor of qualitative synthesis.
Every Climate-active priority has linked or no-material Climate contribution.
HTML and DOCX agree.
Invalid research/diagnostics degrade to core without generic claims.
No output exceeds five substantive priorities.
```

- [ ] **Step 5: Stop for review**

Do not merge, push, or deploy without fresh user direction. Report:

- task commits;
- test commands and counts;
- any pytest cache warning;
- private parity update;
- the remaining untracked user handoff;
- that a production South Sudan rerun is still required after deployment.
