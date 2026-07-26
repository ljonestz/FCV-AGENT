# Climate-FCV Readout Redesign (Core-Question Bank + Layout) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When the Climate lens is active, produce a standalone, climate-led, lay-readable readout whose analytical body is a curated set of core climate-FCV questions — driven by a WBG-source question bank behind six stable themes — laid out as: exec summary → 6-tier integration gauge → 3-block operational context → full-detail strengths/weaknesses → core-question answers (two paragraphs each, component-grounded, with source attribution) → ~3 priorities.

**Architecture:** Additive extension of the existing sector-lens climate diagnostic. A new pure `climate_question_bank.py` module holds the bank + trigger selector. The diagnostic contract in `sector_lenses/pipeline.py` gains a `source` field and larger text bound on `reflections`, plus a 6-tier `integration_rating`. Stage 2/3 climate prompts in `app.py` inject the triggered bank and request the new fields. Frontend (`index.html`) and DOCX (`app.py` `download_report`) render the new section order from one set of renderers, kept in parity. Non-climate (core-FCV) mode is byte-for-byte unchanged throughout.

**Tech Stack:** Python 3.13, Flask, Anthropic SDK, vanilla JS (Node for frontend contract tests), pytest.

**Canonical reader view:** `docs/20260725_ss_climate_readout_mock_v4.html`
**Design spec:** `docs/superpowers/specs/2026-07-25-climate-readout-questions-redesign-design.md`

**Run tests from the worktree with:**
```
C:/WBG/Python313/python.exe -m pytest <paths> -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```
Frontend contract tests spawn `node` (v22 available). Commit `docs/superpowers/**` with `git add -f` (gitignored, force-added on this branch). Chain `git add` + `git commit` in one shell call. No `Co-Authored-By` trailer.

---

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `climate_question_bank.py` | The WBG-source question bank (theme + question + source + trigger) and `select_triggered_questions(project_signals)` | **Create** |
| `sector_lenses/pipeline.py` | Diagnostic parse: `reflections` gain `source` + larger text bound; new `integration_rating` (6-tier) | Modify `_normalize_climate_reflections`, climate lens entry (~585–633), add `_CLIMATE_INTEGRATION_RATINGS` + `climate_integration_rating()` |
| `app.py` | Stage 2/3 climate prompts (inject bank, request `source` + `integration_rating`), repair prompt parity, integration payload, DOCX helpers | Modify `build_lens_stage_context` (~933–1099), `repair_lens_diagnostic` (~1480–1520), `climate_integration_payload` (~9005), `add_climate_reflections`/`add_climate_notice`/`add_climate_interactions` (~9321–9540) |
| `index.html` | 6-tier climate gauge, new `renderClimateCoreQuestions`, `renderClimateStrengthsWeaknesses`, lay-intro, new `renderOut`/`downloadHTML` ordering, drop wider-FCV in climate mode | Modify sidebar climate branch (~5550), climate renderers (~2576–2691), `renderOut` (~4454–4469), `downloadHTML` (~5143–5165) |
| `tests/test_climate_question_bank.py` | Bank + trigger selector tests | **Create** |
| `tests/test_sector_lens_pipeline.py` | Contract tests for `source` + `integration_rating` | Modify |
| `tests/test_sector_lens_app_contract.py` | Stage 2/3 climate prompt + repair-prompt assertions | Modify |
| `tests/test_climate_lens_frontend.py` | Gauge 6-tier, core-questions renderer, ordering, source line | Modify |

**Phasing (each phase independently testable):** 1 Bank → 2 Contract → 3 Stage 2 prompt → 4 Stage 3 prompt → 5 Frontend render → 6 DOCX/shared-HTML parity → 7 Integration + live re-validation.

---

## Phase 1 — Question bank module

The bank is authored from the unrestricted WBG climate-FCV source docs in the **main repo** at `C:/Users/wb559324/OneDrive - WBG/Documents/GitHub/FCV-AGENT/docs/climate_module/` (*Maximizing the Peace and Social Dividends of Climate Action*, `climate_fcv_framework.pdf`, the *Defueling Conflict* series, the *Conflict-Sensitive Climate Action Compendium*, the CCDR guidance note). These are NOT the OPCS corpus and may be read. Seed ~3 questions per theme with trigger keywords; the bank is data and can grow later.

### Task 1.1: Create the bank module with schema + seed content

**Files:**
- Create: `climate_question_bank.py`
- Test: `tests/test_climate_question_bank.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_climate_question_bank.py
"""Tests for the WBG-source climate-FCV core-question bank and trigger selector."""

import climate_question_bank as bank


VALID_THEMES = {
    "cq1_interaction", "cq2_maladaptation", "cq3_dividends",
    "cq4_inclusion", "cq5_institutions", "cq6_adaptive",
}


def test_bank_entries_have_required_shape():
    assert bank.CLIMATE_QUESTION_BANK, "bank must not be empty"
    for q in bank.CLIMATE_QUESTION_BANK:
        assert q["theme"] in VALID_THEMES, q
        assert q["id"] and isinstance(q["id"], str)
        assert q["question"].strip()
        assert q["source"].strip()
        assert isinstance(q["triggers"], list) and q["triggers"], q
        # triggers are lowercase keyword tokens matched against project signals
        assert all(isinstance(t, str) and t == t.lower() for t in q["triggers"])


def test_bank_ids_are_unique():
    ids = [q["id"] for q in bank.CLIMATE_QUESTION_BANK]
    assert len(ids) == len(set(ids))


def test_every_theme_has_at_least_one_bank_question():
    covered = {q["theme"] for q in bank.CLIMATE_QUESTION_BANK}
    assert VALID_THEMES <= covered
```

- [ ] **Step 2: Run to verify failure**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_climate_question_bank.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (`ModuleNotFoundError: climate_question_bank`).

- [ ] **Step 3: Create the module with seed bank**

```python
# climate_question_bank.py
"""WBG-source climate-FCV core-question bank and relevance-trigger selector.

The bank is data lifted from the unrestricted climate-FCV frameworks under
docs/climate_module/ (Maximizing the Peace and Social Dividends of Climate
Action; the FCV-Sensitive Climate Action Framework; the Defueling Conflict
series; the Conflict-Sensitive Climate Action Compendium; the CCDR guidance
note). Each question belongs to one of six stable themes, carries a short
source attribution, and fires when its trigger keywords appear in the
project's Stage-1-derived signals. Surfacing stays at the theme level: the
selector returns, per theme, the triggered questions that shape that theme's
answer. Non-climate mode never calls this module.
"""

from typing import Any

# Six stable themes (mirror sector_lenses.pipeline._CLIMATE_REFLECTION_KEYS).
THEMES = (
    "cq1_interaction",
    "cq2_maladaptation",
    "cq3_dividends",
    "cq4_inclusion",
    "cq5_institutions",
    "cq6_adaptive",
)

# id: stable; theme: one of THEMES; question: reader-neutral prompt;
# source: short attribution; triggers: lowercase keyword tokens (any match fires).
CLIMATE_QUESTION_BANK: list[dict[str, Any]] = [
    # cq1 interaction / delivery
    {"id": "cq1-hazard-delivery", "theme": "cq1_interaction",
     "question": "How do the country's material climate hazards interact with conflict/fragility to affect whether the project can be delivered?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["flood", "drought", "cyclone", "heat", "displacement", "conflict", "insecurity", "access"]},
    {"id": "cq1-access-security", "theme": "cq1_interaction",
     "question": "Could climate shocks compound insecurity to cut physical access to project sites, beneficiaries, or markets?",
     "source": "Defueling Conflict",
     "triggers": ["access", "insecurity", "armed", "displacement", "market", "supply", "transport"]},
    # cq2 maladaptation / lock-in
    {"id": "cq2-infra-horizon", "theme": "cq2_maladaptation",
     "question": "Is hard infrastructure sized to future climate regimes rather than the historical record, avoiding stranded-asset lock-in?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["infrastructure", "construction", "asset", "irrigation", "storage", "road", "flood", "coastal"]},
    {"id": "cq2-access-path-dependence", "theme": "cq2_maladaptation",
     "question": "Could siting, registration, or entitlement decisions entrench access patterns that later climate shifts make inequitable or unviable?",
     "source": "Conflict-Sensitive Climate Action Compendium",
     "triggers": ["land", "tenure", "registration", "allocation", "resource", "grazing", "water", "fisher"]},
    # cq3 dividends / root causes
    {"id": "cq3-peace-dividend", "theme": "cq3_dividends",
     "question": "Does the project engage a conflict root cause and create a credible peace or social dividend, not just outputs?",
     "source": "Maximizing the Peace and Social Dividends of Climate Action",
     "triggers": ["governance", "cohesion", "grievance", "resource", "inclusion", "reconciliation", "livelihood"]},
    {"id": "cq3-shared-benefit", "theme": "cq3_dividends",
     "question": "Are benefits structured so that rival or displaced groups share a stake rather than compete?",
     "source": "Maximizing the Peace and Social Dividends of Climate Action",
     "triggers": ["refugee", "host", "displacement", "pastoral", "shared", "benefit", "cross-border"]},
    # cq4 inclusion / vulnerability
    {"id": "cq4-vulnerable-reach", "theme": "cq4_inclusion",
     "question": "Are the most climate- and conflict-vulnerable regions and groups actually reached and protected?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["women", "gender", "youth", "displacement", "refugee", "vulnerable", "food", "poverty"]},
    {"id": "cq4-inclusion-under-stress", "theme": "cq4_inclusion",
     "question": "Will inclusion commitments survive a shock, or erode back to the pre-project pattern when a flood or clash hits?",
     "source": "Conflict-Sensitive Climate Action Compendium",
     "triggers": ["women", "gender", "quota", "displacement", "committee", "community"]},
    # cq5 institutions / HDP
    {"id": "cq5-delivery-institutions", "theme": "cq5_institutions",
     "question": "Is delivery routed through institutions appropriate to the fragility context, with the right balance of community and state?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["community", "government", "institution", "capacity", "co-management", "decentral", "local"]},
    {"id": "cq5-hdp-nexus", "theme": "cq5_institutions",
     "question": "Does the project coordinate across the humanitarian-development-peace nexus where displacement and humanitarian operations overlap?",
     "source": "Defueling Conflict",
     "triggers": ["unhcr", "humanitarian", "refugee", "host", "nexus", "hdp", "displacement"]},
    # cq6 adaptive / horizons
    {"id": "cq6-adaptive-triggers", "theme": "cq6_adaptive",
     "question": "Is the design adaptive to uncertainty, with triggers and monitoring for climate and conflict change rather than a static plan?",
     "source": "CCDR guidance note",
     "triggers": ["monitoring", "adaptive", "trigger", "results framework", "m&e", "uncertainty", "early warning"]},
    {"id": "cq6-time-horizons", "theme": "cq6_adaptive",
     "question": "Does the design account for the different time horizons in play — near-term shock, project-lifetime cycle, asset-lifetime climate shift?",
     "source": "FCV-Sensitive Climate Action Framework",
     "triggers": ["infrastructure", "asset", "long-term", "projection", "horizon", "flood", "climate projection"]},
]

# Named reader-facing sources for the section intro (order = display order).
BANK_SOURCE_HEADLINE = (
    "Maximizing the Peace and Social Dividends of Climate Action",
    "the FCV-Sensitive Climate Action Framework",
    "the Defueling Conflict (peace and social dividends) series",
)


def select_triggered_questions(project_signals: Any) -> dict[str, list[dict[str, Any]]]:
    """Return, per theme, the bank questions whose triggers fire for this project.

    project_signals: any object convertible to a lowercase text blob (a string,
    or a list of strings) built from Stage 1 (instrument, sector, hazards,
    components, geography). Matching is substring-on-token, case-insensitive.
    Themes with no fired question are omitted. cq1 always returns its bank set
    even if triggers are thin, because the two interaction directions are
    always answered (the caller guarantees Q1/Q2).
    """

    if isinstance(project_signals, (list, tuple, set)):
        blob = " ".join(str(s) for s in project_signals)
    else:
        blob = str(project_signals or "")
    blob = blob.lower()

    fired: dict[str, list[dict[str, Any]]] = {}
    for q in CLIMATE_QUESTION_BANK:
        if any(t in blob for t in q["triggers"]):
            fired.setdefault(q["theme"], []).append(q)
    # Guarantee cq1 is present (interactions are always answered).
    if "cq1_interaction" not in fired:
        fired["cq1_interaction"] = [
            q for q in CLIMATE_QUESTION_BANK if q["theme"] == "cq1_interaction"
        ]
    return fired
```

- [ ] **Step 4: Run to verify pass**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_climate_question_bank.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add climate_question_bank.py tests/test_climate_question_bank.py
git commit -m "feat: WBG-source climate-FCV core-question bank + schema tests"
```

### Task 1.2: Trigger selector behaviour

**Files:**
- Modify: `tests/test_climate_question_bank.py`

- [ ] **Step 1: Add failing tests**

```python
def test_selector_fires_relevant_questions_by_signal():
    # A fisheries/flood/refugee project fires interaction, inclusion, HDP, infra.
    signals = ["IPF fisheries", "Sudd flooding and displacement",
               "refugee and host communities", "cold storage infrastructure",
               "community co-management"]
    fired = bank.select_triggered_questions(signals)
    assert "cq1_interaction" in fired
    assert any(q["id"] == "cq2-infra-horizon" for q in fired.get("cq2_maladaptation", []))
    assert any(q["id"] == "cq5-hdp-nexus" for q in fired.get("cq5_institutions", []))


def test_selector_omits_unfired_themes_but_always_keeps_cq1():
    fired = bank.select_triggered_questions("a project with no matching keywords zzz")
    assert "cq1_interaction" in fired  # always guaranteed
    # A theme with no trigger match is omitted entirely (curation, not padding).
    assert "cq2_maladaptation" not in fired


def test_selector_accepts_plain_string():
    fired = bank.select_triggered_questions("drought and grazing and conservancy governance")
    assert "cq1_interaction" in fired
    assert "cq3_dividends" in fired  # 'governance' fires cq3-peace-dividend
```

- [ ] **Step 2: Run to verify pass** (selector already implemented in 1.1)

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_climate_question_bank.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (6 tests). If a keyword assertion fails, adjust the seed `triggers` (data, not logic) until green.

- [ ] **Step 3: Commit**

```bash
git add tests/test_climate_question_bank.py
git commit -m "test: climate question-bank trigger selection"
```

---

## Phase 2 — Diagnostic contract: source + 6-tier rating

Extend the parsed climate lens entry so each reflection (theme answer) carries a `source`, allows a longer two-paragraph `text`, and the entry carries a 6-tier `integration_rating` for the new gauge (keeping `integration_level` for back-compat).

### Task 2.1: Reflections gain `source` and a larger text bound

**Files:**
- Modify: `sector_lenses/pipeline.py:187-207` (`_normalize_climate_reflections`)
- Test: `tests/test_sector_lens_pipeline.py`

- [ ] **Step 1: Write failing test** (append near the reflection tests, ~line 640)

```python
def test_climate_reflection_carries_source_and_long_text():
    long_text = "Paragraph one about maladaptation lock-in. " * 20 + "\n\n" + \
                "Paragraph two naming Sub-component 1.2 cold storage. " * 20
    block = (
        "%%%LENS_DIAGNOSTIC_START%%%"
        '{"lenses":[{"lens_id":"climate","applicability":"material",'
        '"materiality_level":"high","reflections":[{"question_key":"cq2_maladaptation",'
        '"title":"Could the design lock in maladaptation?","status_cue":"partial gap",'
        '"source":"FCV-Sensitive Climate Action Framework","text":' + __import__("json").dumps(long_text) + '}],'
        '"source_ids":[],"readout_sections":[],"interaction_readout":[],'
        '"additional_pathways":[],"other_pathways":[]}],"findings":[]}'
        "%%%LENS_DIAGNOSTIC_END%%%"
    )
    lens = extract_lens_diagnostic(block, ["climate"])["lenses"][0]
    r = lens["reflections"][0]
    assert r["source"] == "FCV-Sensitive Climate Action Framework"
    assert len(r["text"]) > 900  # two-paragraph depth preserved (not truncated to 700)
    assert "\n\n" in r["text"]   # paragraph break kept
```

- [ ] **Step 2: Run to verify failure**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_sector_lens_pipeline.py::test_climate_reflection_carries_source_and_long_text -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (`KeyError: 'source'` or text truncated to 700).

- [ ] **Step 3: Implement** — replace `_normalize_climate_reflections` body (`sector_lenses/pipeline.py:187-207`)

```python
def _normalize_climate_reflections(value: Any) -> list[dict[str, Any]]:
    """Validate and bound climate diagnostic reflection (theme answer) entries.

    Each entry is a stable-theme answer: question_key + reader title + softened
    status cue + a two-paragraph answer (text, up to ~1800 chars, paragraph
    breaks preserved) + a short source attribution.
    """

    reflections: list[dict[str, Any]] = []
    for raw in _list_values(value):
        if not isinstance(raw, dict):
            continue
        key = str(raw.get("question_key", ""))
        text = str(raw.get("text", "")).strip()[:1800]
        if key not in _CLIMATE_REFLECTION_KEYS or not text:
            continue
        reflections.append({
            "question_key": key,
            "title": str(raw.get("title", "")).strip()[:160],
            "status_cue": _soften_status_cue(raw.get("status_cue", ""))[:40],
            "source": str(raw.get("source", "")).strip()[:120],
            "text": text,
        })
        if len(reflections) >= 6:
            break
    return reflections
```

(Changes: `text` bound 700→1800; `title` 80→160; add `source`; cap 5→6.)

- [ ] **Step 4: Run to verify pass** — also run the full pipeline suite to catch regressions

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_sector_lens_pipeline.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (existing reflection tests still pass — `source` defaults to `""` when absent).

- [ ] **Step 5: Commit**

```bash
git add sector_lenses/pipeline.py tests/test_sector_lens_pipeline.py
git commit -m "feat: climate reflections carry source + two-paragraph text bound"
```

### Task 2.2: 6-tier `integration_rating`

**Files:**
- Modify: `sector_lenses/pipeline.py` (add constant + helper near line 37; set field in climate lens entry ~622-633)
- Test: `tests/test_sector_lens_pipeline.py`

- [ ] **Step 1: Write failing test**

```python
def test_climate_integration_rating_six_tier():
    def _mk(rating):
        return (
            "%%%LENS_DIAGNOSTIC_START%%%"
            '{"lenses":[{"lens_id":"climate","applicability":"material",'
            '"materiality_level":"high","integration_rating":"' + rating + '",'
            '"source_ids":[],"readout_sections":[],"interaction_readout":[],'
            '"additional_pathways":[],"other_pathways":[]}],"findings":[]}'
            "%%%LENS_DIAGNOSTIC_END%%%"
        )
    ok = extract_lens_diagnostic(_mk("Adequate"), ["climate"])["lenses"][0]
    assert ok["integration_rating"] == "Adequate"
    # Invalid → safe default (empty string; UI shows 'Analysing…'/no fill).
    bad = extract_lens_diagnostic(_mk("Amazing"), ["climate"])["lenses"][0]
    assert bad["integration_rating"] == ""
    # Absent → empty string, and integration_level still defaults as before.
    absent = extract_lens_diagnostic(
        _mk("Adequate").replace('"integration_rating":"Adequate",', ""), ["climate"]
    )["lenses"][0]
    assert absent["integration_rating"] == ""
    assert absent["integration_level"] == "insufficient_evidence"
```

- [ ] **Step 2: Run to verify failure**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_sector_lens_pipeline.py::test_climate_integration_rating_six_tier -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (`KeyError: 'integration_rating'`).

- [ ] **Step 3: Implement**

Add after `_CLIMATE_INTEGRATION_LEVELS` (line 37):

```python
# 6-tier display scale (matches the default app gauge labels in index.html).
_CLIMATE_INTEGRATION_RATINGS = (
    "Extremely Low", "Very Low", "Low",
    "Adequate", "Well Embedded", "Very Well Embedded",
)


def climate_integration_rating(value: Any) -> str:
    """Return a valid 6-tier rating label, or '' if absent/invalid."""
    raw = str(value or "").strip()
    return raw if raw in _CLIMATE_INTEGRATION_RATINGS else ""
```

In the climate branch that computes fields (before building `normalized_lens`, ~line 592), add:

```python
            integration_rating = climate_integration_rating(item.get("integration_rating"))
```

In the `if lens_id == "climate": normalized_lens.update({...})` block (~622), add the key:

```python
                "integration_rating": integration_rating,
```

- [ ] **Step 4: Run to verify pass**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_sector_lens_pipeline.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add sector_lenses/pipeline.py tests/test_sector_lens_pipeline.py
git commit -m "feat: 6-tier integration_rating on climate diagnostic"
```

### Task 2.3: Completeness check unaffected

**Files:**
- Modify: `sector_lenses/pipeline.py:821` (`climate_readout_is_complete`) — verify only.
- Test: `tests/test_climate_diagnostic_completeness.py`

- [ ] **Step 1: Add a guard test** confirming completeness still keys on ≥1 grounded reflection + non-empty `integration_summary` (unchanged), and that a `source`-bearing reflection counts as grounded.

```python
def test_completeness_unchanged_with_source_field():
    import sector_lenses.pipeline as p
    entry = {"lens_id": "climate",
             "reflections": [{"question_key": "cq2_maladaptation", "title": "t",
                              "status_cue": "gap", "source": "X", "text": "grounded answer"}],
             "integration_summary": "aware but untreated"}
    assert p.climate_readout_is_complete(entry) is True
```

- [ ] **Step 2: Run** — Expected: PASS (no code change needed; this locks the contract).
- [ ] **Step 3: Commit**

```bash
git add tests/test_climate_diagnostic_completeness.py
git commit -m "test: completeness check unaffected by reflection source field"
```

---

## Phase 3 — Stage 2 climate-native prompt

Inject the triggered bank, request per-theme two-paragraph answers with `source`, and the 6-tier `integration_rating`. Keep the v9.20 completeness + recovery fallback (Task 3.3 mirrors the fields into the recovery prompt).

### Task 3.1: Inject the triggered bank + new field requests into the Stage 2 climate suffix

**Files:**
- Modify: `app.py` — `build_lens_stage_context` climate Stage 2 suffix (the `for` block ending ~line 1029) and its imports.
- Test: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing test** (append near `test_stage2_climate_prompt_requires_reflections_and_intersection`, ~line 764)

```python
def test_stage2_climate_prompt_injects_bank_and_requests_source_and_rating():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"], "lens_versions": {}, "doc_type": "PAD",
    })
    ctx = app_module.build_lens_stage_context(
        state, 2,
        climate_research={"status": "failed", "attempts": 0, "sources": [], "claims": [], "failure_reason": ""},
        project_signals="IPF fisheries flooding displacement cold storage community co-management",
    )
    prompt = ctx["prompt"]
    # Bank questions surface as guidance
    assert "core climate-FCV questions" in prompt.lower()
    assert "FCV-Sensitive Climate Action Framework" in prompt  # a bank source
    # New field requests
    assert "integration_rating" in prompt
    assert "Extremely Low" in prompt and "Very Well Embedded" in prompt  # 6-tier scale
    assert "source" in prompt  # per-reflection source
    # Two-paragraph depth instruction
    assert "two" in prompt.lower() and "paragraph" in prompt.lower()
```

- [ ] **Step 2: Run to verify failure**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_sector_lens_app_contract.py::test_stage2_climate_prompt_injects_bank_and_requests_source_and_rating -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (`TypeError: unexpected keyword 'project_signals'` or assertions).

- [ ] **Step 3: Implement**

At the top of `app.py`, add import:

```python
import climate_question_bank
```

Change `build_lens_stage_context` signature (line 855) to accept an optional signal string:

```python
def build_lens_stage_context(
    state,
    stage,
    registry=None,
    lens_diagnostic=None,
    climate_research=None,
    project_signals: str = "",
    ...  # keep existing remaining params exactly as they are
):
```

Inside the Stage 2 climate suffix branch (after the existing `reflections`/`integration_level` instructions, before `Validated Climate research claims:`), append a bank block. Build the injected text from the selector:

```python
        fired = climate_question_bank.select_triggered_questions(project_signals or "")
        if fired:
            bank_lines = []
            for theme in climate_question_bank.THEMES:
                for q in fired.get(theme, []):
                    bank_lines.append(f"- [{theme}] {q['question']} (source: {q['source']})")
            bank_text = "\n".join(bank_lines)
            suffix += (
                " CORE-QUESTION BANK (triggered for this project). Treat these as "
                "the battery of core climate-FCV questions to reason through; answer "
                "only the themes that are materially relevant to THIS project and "
                "drop the rest rather than padding. For each answered theme produce a "
                "reflections[] entry whose title is the reader-facing question, whose "
                "text is TWO solid, nuanced paragraphs (not a summary) naming the "
                "project's specific components, sub-components, institutions, sites and "
                "figures throughout, and whose source names the framework it draws on. "
                "Always answer the two interaction directions (Q1/Q2) via interaction_readout. "
                "Also return integration_rating using exactly one of: Extremely Low, "
                "Very Low, Low, Adequate, Well Embedded, Very Well Embedded (the same "
                "6-tier scale the app uses), reflecting how well the project integrates "
                "climate and FCV. Bank questions:\n" + bank_text + "\n"
            )
```

Add `"source"` to the reflections field list in the existing instruction text (the sentence at ~line 985 that lists `question_key, title, status_cue, and text`) so it reads `question_key, title, status_cue, source, and text`.

Wire `project_signals` at the two Stage 2 call sites (express ~line 8069 and step-by-step ~line 7397, wherever `build_lens_stage_context(analysis_state, 2, ...)` is called for climate) by passing a compact signal string assembled from Stage 1 (instrument + sector + doc_type + first ~2k chars of the primary doc). Example at the express Stage 2 call:

```python
                _signals = " ".join([
                    instrument_type or "", (sector_context or {}).get("name", "") if isinstance(sector_context, dict) else "",
                    doc_type or "", (doc_parts[0]["raw_text"][:2000] if doc_parts else ""),
                ])
                lens_context_s2 = build_lens_stage_context(analysis_state, 2, ..., project_signals=_signals)
```

(Keep the existing other kwargs. If the call sites already pass `climate_research=`, add `project_signals=_signals` alongside.)

- [ ] **Step 4: Run to verify pass** + full app-contract suite

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_sector_lens_app_contract.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS. (Existing Stage 2 tests call without `project_signals`; default `""` → `select_triggered_questions("")` returns only the guaranteed cq1, so the bank block still appends and the older assertions are unaffected.)

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: inject triggered core-question bank + source/rating into Stage 2 climate prompt"
```

### Task 3.2: Drop the verbose generic engine framing in climate Stage 2 (climate-native)

**Files:**
- Modify: `app.py` Stage 2 climate branch (the part that still asks for the 12-OST table / DNH-9 / 25-question map as visible output when climate is active).
- Test: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing test**

```python
def test_climate_stage2_is_native_not_generic_engine():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"], "lens_versions": {}, "doc_type": "PAD",
    })
    prompt = app_module.build_lens_stage_context(
        state, 2, climate_research={"status": "failed", "attempts": 0, "sources": [], "claims": [], "failure_reason": ""},
    )["prompt"]
    # Climate-native: the readout is organised around the core questions, not the
    # verbose 25-question / 12-OST visible tables.
    assert "core climate-FCV questions" in prompt.lower()
    # Sanity: a non-climate PAD Stage 2 still uses the generic engine unchanged.
    plain = app_module.AnalysisState.from_payload({"active_lenses": [], "lens_versions": {}, "doc_type": "PAD"})
    plain_prompt = app_module.build_lens_stage_context(plain, 2)["prompt"]
    assert "core climate-FCV questions" not in plain_prompt.lower()
```

- [ ] **Step 2: Run to verify** — the first assertion should already pass from 3.1; the second guards non-climate mode is untouched. If it fails because the bank text leaks into non-climate mode, gate the entire bank block on `"climate" in active_ids`. Fix and re-run.
- [ ] **Step 3: Commit**

```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "test: climate Stage 2 is native; non-climate engine unchanged"
```

### Task 3.3: Recovery prompt parity (source + rating + two-paragraph)

**Files:**
- Modify: `app.py:1480-1520` (`repair_lens_diagnostic` prompt + compact shape).
- Test: `tests/test_sector_lens_app_contract.py` (extend the existing recovery-prompt assertion added earlier).

- [ ] **Step 1: Add failing assertions** to the recovery-prompt test (the one capturing `messages.request["messages"][0]["content"]`)

```python
    assert "integration_rating" in prompt
    assert "source" in prompt
    assert "two" in prompt.lower() and "paragraph" in prompt.lower()
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — in the recovery prompt string (~1477-1500), extend the reflections instruction to request `source` and two-paragraph `text`, and add an `integration_rating` request; update the compact-shape JSON template to include `"source":"..."` in the reflection object and `"integration_rating":"Adequate"` at the lens level.
- [ ] **Step 4: Run** the recovery tests + `tests/test_climate_diagnostic_completeness.py` — Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: recovery prompt parity for source/rating/two-paragraph reflections"
```

---

## Phase 4 — Stage 3 climate prompt (drop wider-FCV surfacing)

The dedicated module no longer surfaces `wider_fcv_context`. Keep the field parsed for back-compat but stop instructing the model to produce it in climate mode, and stop rendering it (render change in Phase 5).

### Task 4.1: Remove the wider_fcv_context instruction from the Stage 3 climate branch

**Files:**
- Modify: `app.py` Stage 3 climate branch (~1094-1099, the `Add a top-level wider_fcv_context string ...` prefix).
- Test: `tests/test_sector_lens_app_contract.py`

- [ ] **Step 1: Write failing test**

```python
def test_climate_stage3_does_not_request_wider_fcv_context():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": ["climate"], "lens_versions": {}, "doc_type": "PAD",
    })
    payload = {"lenses": [{"lens_id": "climate", "materiality_level": "high"}], "findings": []}
    prompt = app_module.build_lens_stage_context(state, 3, lens_diagnostic=payload)["prompt"]
    assert "wider_fcv_context" not in prompt
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — delete the `prefix += ("Add a top-level wider_fcv_context string ...")` block in the climate Stage 3 branch. Leave `extract_priorities` parsing of `wider_fcv_context` intact (back-compat; simply always null in climate mode now).
- [ ] **Step 4: Run** `tests/test_sector_lens_app_contract.py` + `tests/test_extract_priorities.py` — Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: drop wider_fcv_context from Stage 3 climate prompt (dedicated module)"
```

---

## Phase 5 — Frontend rendering

New reader order in climate mode: exec summary → **6-tier gauge** → operational context → **full-detail strengths/weaknesses** → **core-question section** (lay intro + Q1/Q2 interactions + theme answers with source) → priorities. Drop the standalone dividends section (absorbed into cq3) and the wider-FCV callout.

> Note: the mock's "operational context" and "executive summary" prose are produced by the Stage 1/3 model text, not by a structured field; keep rendering the model narrative as today. The structured changes below are the gauge, the core-question section, and ordering.

### Task 5.1: 6-tier climate integration gauge

**Files:**
- Modify: `index.html` sidebar climate branch (~5550) + the fill logic in `updateSidebar` (~5617) + `climate_integration_payload` in `app.py` (~9005) to pass `rating`.
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write failing test**

```python
def test_climate_gauge_uses_six_tier_rating():
    html = INDEX.read_text(encoding="utf-8")
    # The climate sidebar gauge renders the 6-tier rating + need phrase.
    assert "climateIntegrationRatingFraction" in html
    fn = _extract_js_function(html, "climateIntegrationRatingFraction")
    out = subprocess.run(["node", "-e",
        f"{fn}\nconsole.log([climateIntegrationRatingFraction('Extremely Low'),"
        f"climateIntegrationRatingFraction('Adequate'),"
        f"climateIntegrationRatingFraction('Very Well Embedded'),"
        f"climateIntegrationRatingFraction('')].join(','))"],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    vals = out.stdout.strip().split(",")
    # Extremely Low > 0 (tier 1 of 6), Adequate = 4/6, top = 1, invalid = 0
    assert abs(float(vals[1]) - (4/6)) < 0.01
    assert vals[2] == "1"
    assert vals[3] == "0"
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement**

Add near the existing `LEVELS`/`integrationGaugeFraction` (~5527-5542):

```javascript
  const CLIMATE_RATING_ORDER = ['Extremely Low','Very Low','Low','Adequate','Well Embedded','Very Well Embedded'];
  function climateIntegrationRatingFraction(rating){
    const i = CLIMATE_RATING_ORDER.indexOf(String(rating||''));
    return i < 0 ? 0 : (i + 1) / CLIMATE_RATING_ORDER.length;
  }
```

In `sidebarHtml()` climate branch (~5550), keep the arc SVG (`#fcv-int-arc`), set `#fcv-int-label` to the rating and `#fcv-int-summary` to the `NEED_LABELS[rating]` phrase (reuse the existing `NEED_LABELS` map keyed on the 6-tier labels). In `updateSidebar()` climate branch (~5617), fill `#fcv-int-arc` using `climateIntegrationRatingFraction(climateIntegration && climateIntegration.rating)` × `ARC_LEN`, and set the label text to `climateIntegration.rating || 'Analysing…'`.

In `app.py` `climate_integration_payload` (~9005-9013), add the rating to the payload:

```python
    return {
        "level": lens.get("integration_level", ""),
        "rating": lens.get("integration_rating", ""),
        "summary": lens.get("integration_summary", ""),
    }
```

- [ ] **Step 4: Run** `tests/test_climate_lens_frontend.py` + `tests/test_sector_lens_app_contract.py` — Expected: PASS. (Update `test_single_integration_gauge_present_in_module_mode` if it asserted the old 4-level fractions.)
- [ ] **Step 5: Commit**

```bash
git add index.html app.py tests/test_climate_lens_frontend.py
git commit -m "feat: 6-tier climate integration gauge (rating + need phrase)"
```

### Task 5.2: `renderClimateCoreQuestions` — lay intro + Q1/Q2 + theme answers with source

**Files:**
- Modify: `index.html` — add `renderClimateCoreQuestions(lens)`; it replaces the separate `renderClimateReflections` + `renderClimateDividendSynthesis` calls in the climate assembly.
- Test: `tests/test_climate_lens_frontend.py`

- [ ] **Step 1: Write failing test**

```python
def test_core_questions_render_intro_interactions_and_theme_answers_with_source():
    html = INDEX.read_text(encoding="utf-8")
    assert "renderClimateCoreQuestions" in html
    fn = _extract_js_function(html, "renderClimateCoreQuestions")
    dep1 = _extract_js_function(html, "renderClimatePathwayStrip")
    esc = _extract_js_function(html, "esc")
    lens = {
        "interaction_readout": [
            {"direction_id": "climate-fcv-on-project", "summary": "Flood risk.",
             "narrative": "Para one.\n\nPara two names Boma Fisheries Management Units.", "pathways": []},
            {"direction_id": "project-on-climate-fcv", "summary": "Cohesion.",
             "narrative": "Governance forum.", "pathways": []},
        ],
        "reflections": [
            {"question_key": "cq2_maladaptation", "title": "Could the design lock in maladaptation?",
             "status_cue": "partial gap", "source": "FCV-Sensitive Climate Action Framework",
             "text": "Answer para one.\n\nAnswer para two."},
        ],
    }
    script = f"{esc}\n{dep1}\n{fn}\nprocess.stdout.write(renderClimateCoreQuestions({json.dumps(lens)}));"
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    # Lay-reader intro names the source literature
    assert "Maximizing the Peace and Social Dividends of Climate Action" in out.stdout
    # Both interaction directions present
    assert "How could climate and FCV affect this project" in out.stdout or "climate and FCV" in out.stdout
    # Theme answer with its title, source line, and paragraph split
    assert "Could the design lock in maladaptation?" in out.stdout
    assert "FCV-Sensitive Climate Action Framework" in out.stdout
    assert out.stdout.count("<p") >= 4  # multi-paragraph answers
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — add the renderer (near the existing climate renderers ~2648). It renders: a fixed lay intro (naming `Maximizing…`, the `FCV-Sensitive Climate Action Framework`, the `Defueling Conflict` series), then the two `interaction_readout` directions (prefer `.narrative`, split on blank lines into `<p class="climate-interaction-prose">`, fall back to `renderClimatePathwayStrip`), then each `reflections[]` entry as a titled block with the status word, the two-paragraph `text` split on blank lines, and a subtle `source` line. Use the mock v4 markup/classes (`.q`, `.qhead`, `.qnum`, `.qtitle`, `.qstatus`, `.q .src`, `.tag.in/.out`) — copy the corresponding CSS from `docs/20260725_ss_climate_readout_mock_v4.html` into the `<style>` block.

- [ ] **Step 4: Run** `tests/test_climate_lens_frontend.py` — Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: renderClimateCoreQuestions (lay intro + interactions + theme answers + source)"
```

### Task 5.3: Full-detail strengths/weaknesses renderer

**Files:**
- Modify: `index.html` — add `renderClimateStrengthsWeaknesses(lens)` reading a structured `strengths_weaknesses` field (see contract note below), rendered as the two-column full-detail block from mock v4.
- Also: add `strengths_weaknesses` to the diagnostic contract in `sector_lenses/pipeline.py` (list of `{side: "strength"|"gap", title, text}`) + Stage 2 prompt request + parser test.
- Test: `tests/test_climate_lens_frontend.py`, `tests/test_sector_lens_pipeline.py`

- [ ] **Step 1 (contract): failing pipeline test**

```python
def test_climate_strengths_weaknesses_parsed():
    block = (
        "%%%LENS_DIAGNOSTIC_START%%%"
        '{"lenses":[{"lens_id":"climate","applicability":"material","materiality_level":"high",'
        '"strengths_weaknesses":[{"side":"strength","title":"Community delivery","text":"Fits weak centre and adapts to floods."},'
        '{"side":"gap","title":"Flood-displacement","text":"Named but no design response."}],'
        '"source_ids":[],"readout_sections":[],"interaction_readout":[],"additional_pathways":[],"other_pathways":[]}],"findings":[]}'
        "%%%LENS_DIAGNOSTIC_END%%%"
    )
    lens = extract_lens_diagnostic(block, ["climate"])["lenses"][0]
    sw = lens["strengths_weaknesses"]
    assert [x["side"] for x in sw] == ["strength", "gap"]
    assert sw[0]["title"] == "Community delivery"
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3 (contract): implement** — add a `_normalize_climate_sw(value)` helper (bound: ≤4 per side, `title` ≤160, `text` ≤600, `side` ∈ {strength,gap}) and set `strengths_weaknesses` in the climate lens entry. Add the request to the Stage 2 climate suffix (§3.1 block): "Also return strengths_weaknesses: up to 4 strengths and 4 gaps, each {side, title, text}, climate-FCV-scoped, each naming the specific design element it attaches to." Add the field to the recovery compact shape.
- [ ] **Step 4 (contract): run pipeline suite** — PASS. Commit.

```bash
git add sector_lenses/pipeline.py app.py tests/test_sector_lens_pipeline.py
git commit -m "feat: structured climate strengths_weaknesses in diagnostic + prompts"
```

- [ ] **Step 5 (frontend): failing test**

```python
def test_strengths_weaknesses_two_column_full_detail():
    html = INDEX.read_text(encoding="utf-8")
    assert "renderClimateStrengthsWeaknesses" in html
    fn = _extract_js_function(html, "renderClimateStrengthsWeaknesses")
    esc = _extract_js_function(html, "esc")
    lens = {"strengths_weaknesses": [
        {"side": "strength", "title": "Community delivery", "text": "Fits weak centre and adapts to floods."},
        {"side": "gap", "title": "Flood-displacement", "text": "Named but no design response."}]}
    out = subprocess.run(["node", "-e",
        f"{esc}\n{fn}\nprocess.stdout.write(renderClimateStrengthsWeaknesses({json.dumps(lens)}));"],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "Where the design is strong" in out.stdout
    assert "Community delivery" in out.stdout
    assert "Named but no design response." in out.stdout
```

- [ ] **Step 6 (frontend): implement** the renderer (two-column, `.sw` markup/CSS from mock v4). Empty/absent → `''`.
- [ ] **Step 7: Run** frontend suite — PASS. Commit.

```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: renderClimateStrengthsWeaknesses (full-detail two-column)"
```

### Task 5.4: Re-order the climate assembly in `renderOut` and drop dividends/wider-FCV

**Files:**
- Modify: `index.html` `renderOut` climate block (~4454-4469).
- Test: `tests/test_climate_lens_frontend.py` (update `test_live_and_shared_orders_boxes_reflections_dividends_wider`).

- [ ] **Step 1: Update the ordering test** to the new order and absence of dividends/wider in climate mode:

```python
def test_live_climate_order_gauge_context_sw_questions():
    html = INDEX.read_text(encoding="utf-8")
    body = html.split("function renderOut", 1)[1][:9000]
    i_notice = body.index("renderClimateModuleNotice")
    i_sw = body.index("renderClimateStrengthsWeaknesses")
    i_q = body.index("renderClimateCoreQuestions")
    assert i_notice < i_sw < i_q
    # Dividends + wider-FCV renderers are no longer called in the climate block
    seg = body[i_notice:i_q + 400]
    assert "renderClimateDividendSynthesis" not in seg
    assert "renderWiderFcvContext" not in seg
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — replace the climate assembly (`renderClimateInteractions + renderClimateReflections + renderClimateDividendSynthesis + renderWiderFcvContext`) with:

```javascript
          renderClimateStrengthsWeaknesses(_climateEntry)+
          renderClimateCoreQuestions(_climateEntry)
```

Keep `renderClimateModuleNotice` first (it carries the exec/materiality + partial-notice). The 6-tier gauge is in the sidebar (Task 5.1); operational-context + exec-summary prose come from the model narrative already rendered above the climate block. Remove the now-unused `renderClimateDividendSynthesis`/`renderWiderFcvContext`/`renderClimateReflections` calls from the climate path (leave the functions defined but uncalled, or delete if no other caller — verify with grep).

- [ ] **Step 4: Run** frontend suite — PASS.
- [ ] **Step 5: Commit**

```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: climate readout order = notice/gauge -> context -> S&W -> core questions"
```

---

## Phase 6 — DOCX + shared-HTML export parity

### Task 6.1: Shared HTML (`downloadHTML`) parity

**Files:**
- Modify: `index.html` `downloadHTML` climate block (~5143-5165).
- Test: `tests/test_climate_lens_frontend.py` (`test_download_html_uses_same_climate_sections_and_order`).

- [ ] **Step 1: Update the test** to assert `downloadHTML` calls `renderClimateStrengthsWeaknesses` then `renderClimateCoreQuestions`, and does NOT call `renderClimateDividendSynthesis`/`renderWiderFcvContext` in climate mode.
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — mirror the Task 5.4 change in `downloadHTML` (~5160-5165).
- [ ] **Step 4: Run** — PASS. Commit.

```bash
git add index.html tests/test_climate_lens_frontend.py
git commit -m "feat: shared-HTML export parity for new climate order"
```

### Task 6.2: DOCX (`download_report`) parity

**Files:**
- Modify: `app.py` DOCX climate helpers (~9321-9540): replace `add_climate_reflections` with `add_climate_core_questions` (lay intro + interactions + theme answers with source), add `add_climate_strengths_weaknesses`, and drop the dividend/wider-FCV DOCX sections in climate mode; update the call order.
- Test: `tests/test_sector_lens_app_contract.py` (or the DOCX test module if present).

- [ ] **Step 1: Write failing test** — build a minimal climate diagnostic + priorities, call the report route/helper, and assert the generated DOCX text contains: the lay intro source names, both interaction direction headings, each reflection title + its source, the S&W headings, and does NOT contain a "Wider FCV context" heading. (Follow the existing DOCX test pattern in the repo; if none asserts text, use `python-docx` to read `doc.paragraphs` from the returned bytes.)
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** the DOCX helpers to match the frontend renderers (same content, `python-docx` paragraphs/headings). Wire the new call order in the climate branch of `download_report`.
- [ ] **Step 4: Run** the DOCX + app-contract suites — PASS.
- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_sector_lens_app_contract.py
git commit -m "feat: DOCX export parity for new climate core-questions layout"
```

---

## Phase 7 — Integration, full suite, live re-validation

### Task 7.1: Update the South Sudan regression fixture

**Files:**
- Modify: `tests/fixtures/climate/south_sudan_dual_use.json`

- [ ] **Step 1** — extend the fixture so its climate lens entry carries `integration_rating`, `strengths_weaknesses`, and `reflections` with `source` + two-paragraph `text`, mirroring mock v4. Update any fixture-driven assertions.
- [ ] **Step 2: Run** the focused climate suite:

```
C:/WBG/Python313/python.exe -m pytest tests/test_sector_lens_pipeline.py tests/test_extract_priorities.py tests/test_sector_lens_app_contract.py tests/test_climate_lens_package.py tests/test_climate_lens_frontend.py tests/test_climate_research.py tests/test_climate_ccdr_context.py tests/test_climate_diagnostic_completeness.py tests/test_climate_question_bank.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```
Expected: PASS.
- [ ] **Step 3: Commit.**

### Task 7.2: Full suite green + non-climate regression

- [ ] **Step 1: Run** the full suite:

```
C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```
Expected: all pass (baseline this branch was 375; new tests add to that). Investigate any non-climate failure — non-climate output must be unchanged.
- [ ] **Step 2: Commit** any fixups.

### Task 7.3: Update dev docs

**Files:**
- Modify: `claude.md` (version history entry), `docs/reference/reference_prompt_architecture.md` (climate diagnostic contract: `reflections.source`, `integration_rating`, `strengths_weaknesses`; core-question bank), `docs/reference/reference_sector_lenses.md`.

- [ ] **Step 1** — add a `v9.21` changelog entry summarising the redesign and the contract additions; update the reference docs.
- [ ] **Step 2: Commit** (`git add -f` for any gitignored doc).

### Task 7.4: Deploy + live re-validation (maintainer-run)

- [ ] Push the branch (Render auto-deploys this branch). Wake the free-tier service.
- [ ] Run the **South Sudan SSNRL PCN + CCDR** in Express; download the HTML.
- [ ] Confirm against mock v4: 6-tier gauge (arc filled, labelled); 3-block operational context; full-detail S&W; core-questions section with the lay intro naming the source literature, Q1/Q2 interactions, and theme answers with two paragraphs + status + source; no dividends/wider-FCV sections; ≤5 (≈3) priorities; DOCX == live == shared HTML.
- [ ] Capture the Render log slice by `assessment_id` if anything stalls; distinguish app-stage error vs worker limit.

---

## Self-Review

**Spec coverage:** §3 reader layout → Phases 5–6 (gauge 5.1; core questions 5.2; S&W 5.3; order 5.4; exports 6). §4 bank + themes → Phase 1 + Task 3.1. §4.3 contract additions (`source`, `integration_rating`, `strengths_weaknesses`) → Phase 2 + Tasks 5.3/3.1. §5 pipeline (climate-native Stage 2, wider-FCV drop) → Tasks 3.2, 4.1. §6 export parity → Phase 6. §7 content-quality bar → prompt text in Task 3.1 (two-paragraph + component-specificity). §8 invariants → completeness guard (2.3), non-climate regression (3.2, 7.2). §9 out-of-scope (CCDR-size, ITS parity) → not implemented, correct. §10 testing → Phase 7. §11 open items (bank size, cq5 fold) → bank is data (Phase 1, extensible); cq5 fold handled by curation (selector omits unfired themes).

**Placeholder scan:** DOCX test (6.2) and fixture update (7.1) reference "the existing DOCX test pattern / fixture-driven assertions" rather than inlined code — flagged as the two tasks the implementer must read the current file to complete; all other steps carry concrete code. Acceptable given they mirror renderers defined earlier in the plan.

**Type/name consistency:** `integration_rating` (pipeline field, payload key, prompt token, `climateIntegrationRatingFraction`) consistent; `reflections[].source` consistent across 2.1/3.1/3.3/5.2/6.2; `strengths_weaknesses` (side/title/text) consistent across pipeline/prompt/render/DOCX; `select_triggered_questions` / `CLIMATE_QUESTION_BANK` / `THEMES` / `BANK_SOURCE_HEADLINE` consistent between module and callers; `renderClimateCoreQuestions` / `renderClimateStrengthsWeaknesses` consistent across 5.2/5.3/5.4/6.1.
