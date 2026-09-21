# Dual-Regime Process Model (Legacy PAD ↔ New Project Paper) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the FCV screener regime-aware on two independent axes — **preparation regime** (legacy PAD/PCN/appraisal ↔ new-model OIS/Project Paper/TD-IR-One-Review) and **E&S regime** (ESF ESS1–10 ↔ legacy safeguards ↔ Performance Standards ↔ instrument-specific) — detecting both from the uploaded document and rendering document type, gate/timing vocabulary, section references, and recommendation authority correctly for each, without changing any legacy-mode output.

**Architecture:** A new pure `regime_router.py` module holds the boundary constants and the three decision tables (preparation regime, one/two-step processing, E&S regime) as side-effect-free functions with exhaustive unit tests. Stage 1 emits a new `%%%REGIME_CONTEXT%%%` delimiter block that a new `extract_regime_context()` parses and `clean_stage1_output()` strips; `AnalysisState` carries the parsed fields. Terminology normalises onto an internal `IPF_APPRAISAL_DOCUMENT` lifecycle class, `pad_sections` is renamed to `appraisal_document_sections` with back-compat, `action_timing` becomes a central regime-aware vocabulary, and a shared `authority_basis` recommendation field is added. Everything defaults safely to `unknown`/`unresolved`/legacy so a missing signal never mis-asserts a regime — legacy output stays byte-for-byte identical.

**Tech Stack:** Python 3.13, Flask, Anthropic SDK, vanilla JS (Node for frontend contract tests), pytest.

**Design spec:** `docs/superpowers/specs/2026-07-26-dual-regime-process-model-design.md`
**Confirmed OPCS rules:** memory `project_opcs_july2026_process_change.md` (all rules cited to Published OPCS documents by Copilot reviews; Claude does not read the corpus).
**Gate-1 review status:** `docs/superpowers/reviews/2026-07-26-dual-regime-spec-gate1-copilot-review-brief.md` — **run this Copilot review and fold in any CORRECT-AS-FOLLOWS fixes BEFORE executing Phase 2 onward.** Phase 1 (pure router, cited directly from the spec's decision tables) can proceed in parallel with the review.

**Branch:** app-wide foundation — recommended on a **fresh branch off `main`** (see "Branch & integration" below). Confirm with the maintainer before Phase 1.

**Run tests from the worktree with:**
```
C:/WBG/Python313/python.exe -m pytest <paths> -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*
```
Frontend contract tests spawn `node` (v22 available). Commit `docs/superpowers/**` with `git add -f`. Chain `git add` + `git commit` in one shell call. No `Co-Authored-By` trailer.

---

## Branch & integration (decide with maintainer before starting)

This is app-wide and touches Stage 1 detection, the stage model, terminology, timing, and instrument reference checks — larger than, and mostly separate from, the climate readout redesign. `main` currently **lacks** the Stage-1 timeout fixes and the climate module that live on `codex/climate-fcv-output-redesign`. Recommended: cut `feat/dual-regime-process-model` **off `main`**, build here, and sequence the integration order (dual-regime → climate rebase, or vice-versa) with the maintainer. The climate plan's Task 4B.3 (`authority_basis`) has a dependency guard so whichever branch lands first owns the shared field.

---

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `regime_router.py` | Boundary constants + three pure decision tables: `classify_preparation_regime`, `classify_processing_model`, `classify_es_regime`, plus `op_7_xx` screen helpers and timing-vocabulary sets | **Create** |
| `app.py` | Stage 1 `%%%REGIME_CONTEXT%%%` prompt block + `extract_regime_context()` + strip in `clean_stage1_output()`; `AnalysisState` fields; terminology normalisation (`IPF_APPRAISAL_DOCUMENT`, `appraisal_document_sections` back-compat); regime-aware `action_timing` resolver + `extract_priorities` validation; `authority_basis`; regime injection into Stage 2/3 prompts; DOCX export | Modify |
| `background_docs.py` | `IPF_PROJECT_PAPER_SECTIONS`, `PFORR_PROGRAM_PAPER_SECTIONS`, corrected regime-gated minimum reference set, regime label/timing strings | Modify |
| `index.html` | Regime-rendered document-type label + timing pills; `appraisal_document_sections` rendering; `authority_basis` chip; export parity | Modify |
| `tests/test_regime_router.py` | Decision-table unit tests (preparation, processing, E&S, screens, timing sets) | **Create** |
| `tests/test_regime_detection.py` | `extract_regime_context` + strip + `AnalysisState` wiring | **Create** |
| `tests/test_regime_terminology.py` | `pad_sections`↔`appraisal_document_sections` back-compat; label rendering | **Create** |
| `tests/test_regime_timing.py` | `action_timing` resolver per regime; "before appraisal" never emitted for new-model | **Create** |
| `tests/test_extract_priorities.py` | `authority_basis` validation/default | Modify |
| `tests/test_regime_regression.py` | Legacy-mode output byte-for-byte unchanged | **Create** |

**Phasing (each phase independently testable):** 1 Pure router → 2 Stage 1 detection → 3 Terminology → 4 Timing vocabulary → 5 Sections & reference checks → 6 `authority_basis` → 7 Regime injection + legacy regression → 8 Integration, docs, live validation.

---

## Phase 1 — Pure regime router (`regime_router.py`)

Side-effect-free decision tables, cited directly to the spec. No app wiring yet. This phase can start before the Gate-1 review returns.

### Task 1.1: Boundary constants + preparation-regime classifier

**Files:**
- Create: `regime_router.py`
- Test: `tests/test_regime_router.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_regime_router.py
import datetime as dt
import regime_router as rr


def test_preparation_boundary_is_18_april_2026():
    assert rr.PREPARATION_BOUNDARY == dt.date(2026, 4, 18)


def test_ois_on_or_after_boundary_is_new_model():
    assert rr.classify_preparation_regime(dt.date(2026, 4, 18)) == "new_model"
    assert rr.classify_preparation_regime(dt.date(2026, 6, 1)) == "new_model"


def test_ois_before_boundary_is_legacy_transitional():
    assert rr.classify_preparation_regime(dt.date(2026, 4, 17)) == "legacy_transitional"
    assert rr.classify_preparation_regime(dt.date(2024, 1, 1)) == "legacy_transitional"


def test_missing_ois_date_is_unresolved():
    assert rr.classify_preparation_regime(None) == "unresolved_policy_source"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_router.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (`ModuleNotFoundError: regime_router`).

- [ ] **Step 3: Write minimal implementation**

```python
# regime_router.py
"""Pure, side-effect-free OPCS regime classifiers for the FCV screener.

Two INDEPENDENT axes (do not conflate — separate governing fields):
  * preparation regime  -> governed by the operation's OIS creation date vs
    18 Apr 2026 [OPS5.03-PROC.281/282, eff 18 Apr 2026].
  * E&S regime          -> governed by the Concept Decision date vs 1 Oct 2018
    [OPS5.03-DIR.123, eff 15 Jan 2026, §III.A ¶1; ESF Policy ¶7/fn12/¶63/fn1].

Every function returns a safe fallback (unresolved/unknown/legacy) rather than
guessing when inputs are missing or contradictory. Sources: memory
`project_opcs_july2026_process_change.md`; spec 2026-07-26-dual-regime-process-model-design.md.
"""

from __future__ import annotations

import datetime as dt
from typing import Optional

# Procedures say "on or after April 17, 2026" = after the 17th = 18 Apr; encode
# 18 Apr with a source caveat (see spec §4.1 / §9).
PREPARATION_BOUNDARY = dt.date(2026, 4, 18)
# ESF applicability trigger: Concept Decision on/after 1 Oct 2018 -> ESF.
ES_REGIME_BOUNDARY = dt.date(2018, 10, 1)

PREPARATION_REGIMES = ("new_model", "legacy_transitional", "unresolved_policy_source")


def classify_preparation_regime(ois_creation_date: Optional[dt.date]) -> str:
    """Classify the preparation regime from the operation's OWN OIS creation date."""
    if ois_creation_date is None:
        return "unresolved_policy_source"
    return "new_model" if ois_creation_date >= PREPARATION_BOUNDARY else "legacy_transitional"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_router.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add regime_router.py tests/test_regime_router.py
git commit -m "feat: preparation-regime classifier + boundary constants"
```

### Task 1.2: One/two-step processing-model classifier

**Files:**
- Modify: `regime_router.py`
- Test: `tests/test_regime_router.py`

- [ ] **Step 1: Write the failing test**

```python
def test_ipf_first_mpa_phase_is_two_step():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Low", es_risk="Low", is_first_mpa_phase=True,
    ) == "two_step"


def test_ipf_high_risk_is_two_step():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Substantial", es_risk="Moderate",
    ) == "two_step"
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Moderate", es_risk="High",
    ) == "two_step"


def test_ipf_low_moderate_both_is_one_step():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Moderate", es_risk="Low",
    ) == "one_step"


def test_ipf_af_is_one_step_even_if_high_risk():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="High", es_risk="High", is_af=True,
    ) == "one_step"


def test_ipf_small_tf_and_urgent_are_one_step():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="High", es_risk="High", small_tf_retf_le_5m=True,
    ) == "one_step"
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="High", es_risk="High", urgent_need_or_capacity=True,
    ) == "one_step"


def test_fmrf_not_af_is_two_step():
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Low", es_risk="Low", is_fmrf=True,
    ) == "two_step"
    assert rr.classify_processing_model(
        instrument="IPF", sort_overall="Low", es_risk="Low", is_fmrf=True, is_af=True,
    ) == "one_step"  # AF-to-existing-FMRF


def test_dpf_first_in_series_two_step_subsequent_one_step():
    assert rr.classify_processing_model(
        instrument="DPO", series_position="first",
    ) == "two_step"
    assert rr.classify_processing_model(
        instrument="DPO", series_position="subsequent",
    ) == "one_step"
    assert rr.classify_processing_model(
        instrument="DPO", series_position="standalone",
    ) == "two_step"
    assert rr.classify_processing_model(
        instrument="DPO", series_position="subsequent", dpf_supplemental_or_scalable=True,
    ) == "one_review"


def test_missing_risk_data_is_unknown():
    assert rr.classify_processing_model(instrument="IPF") == "unknown"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_router.py -k processing -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (`AttributeError: classify_processing_model`).

- [ ] **Step 3: Write minimal implementation** (append to `regime_router.py`)

```python
PROCESSING_MODELS = ("one_step", "two_step", "one_review", "unknown")

_HIGH = {"substantial", "high"}
_LOWMOD = {"low", "moderate"}


def _norm(value: Optional[str]) -> str:
    return str(value or "").strip().lower()


def classify_processing_model(
    instrument: str,
    sort_overall: Optional[str] = None,
    es_risk: Optional[str] = None,
    *,
    is_af: bool = False,
    is_first_mpa_phase: bool = False,
    is_fmrf: bool = False,
    urgent_need_or_capacity: bool = False,
    small_tf_retf_le_5m: bool = False,
    series_position: Optional[str] = None,          # DPF: standalone|first|subsequent
    dpf_supplemental_or_scalable: bool = False,
    hybrid_ipf_component_esrc: Optional[str] = None,  # PforR hybrid
) -> str:
    """One-step vs two-step vs one-review, per OPS5.03-PROC.281/282 (IPF/PforR)
    and OPS5.02-PROC.113 (DPF). Returns 'unknown' when required risk data is absent.
    """
    inst = _norm(instrument)

    # --- DPF [OPS5.02-PROC.113, eff 22 May 2026] -------------------------------
    if inst in {"dpo", "dpf"}:
        pos = _norm(series_position)
        if dpf_supplemental_or_scalable:
            return "one_review"
        if pos == "subsequent":
            return "one_step"
        if pos in {"standalone", "first"}:
            return "two_step"
        return "unknown"

    # --- IPF / PforR [OPS5.03-PROC.281 one-step / .282 two-step] ----------------
    if is_first_mpa_phase:
        return "two_step"
    if is_fmrf and not is_af:
        return "two_step"
    if is_af or urgent_need_or_capacity or small_tf_retf_le_5m:
        return "one_step"

    sort_n, es_n = _norm(sort_overall), _norm(es_risk)
    # PforR hybrid: one-step only if PforR ratings Low/Mod AND IPF-component ESRC Low/Mod.
    ratings = [sort_n, es_n]
    if inst == "pforr" and hybrid_ipf_component_esrc is not None:
        ratings.append(_norm(hybrid_ipf_component_esrc))

    if any(r in _HIGH for r in ratings if r):
        return "two_step"
    if sort_n in _LOWMOD and es_n in _LOWMOD and all(
        (r in _LOWMOD) for r in ratings if r
    ):
        return "one_step"
    return "unknown"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_router.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add regime_router.py tests/test_regime_router.py
git commit -m "feat: one/two-step processing-model classifier (IPF/PforR/DPF)"
```

### Task 1.3: E&S-regime classifier + OP 7.50/7.60 screens

**Files:**
- Modify: `regime_router.py`
- Test: `tests/test_regime_router.py`

- [ ] **Step 1: Write the failing test**

```python
def test_es_non_ipf_is_instrument_specific():
    assert rr.classify_es_regime(instrument="PforR", concept_decision_date=dt.date(2022, 1, 1)) == "INSTRUMENT_SPECIFIC"
    assert rr.classify_es_regime(instrument="DPO", concept_decision_date=dt.date(2010, 1, 1)) == "INSTRUMENT_SPECIFIC"


def test_es_op_bp_4_03_takes_precedence():
    assert rr.classify_es_regime(
        instrument="IPF", concept_decision_date=dt.date(2022, 1, 1), op_bp_4_03_applies=True,
    ) == "PERFORMANCE_STANDARDS_OP_BP_4_03"


def test_es_af_exclusively_cost_overrun_is_legacy():
    assert rr.classify_es_regime(
        instrument="IPF", concept_decision_date=dt.date(2022, 1, 1),
        is_af=True, parent_under_safeguard_policies=True, af_exclusively_cost_overrun_or_gap=True,
    ) == "LEGACY_SAFEGUARDS"


def test_es_af_that_adds_activities_is_not_legacy_exception():
    # AF scales up / adds activities -> the (C) exception does NOT apply; falls to date rule.
    assert rr.classify_es_regime(
        instrument="IPF", concept_decision_date=dt.date(2022, 1, 1),
        is_af=True, parent_under_safeguard_policies=True, af_exclusively_cost_overrun_or_gap=False,
    ) == "ESF_ESS1_TO_ESS10"


def test_es_concept_decision_on_or_after_2018_10_01_is_esf():
    assert rr.classify_es_regime(instrument="IPF", concept_decision_date=dt.date(2018, 10, 1)) == "ESF_ESS1_TO_ESS10"


def test_es_concept_decision_before_2018_10_01_is_legacy():
    assert rr.classify_es_regime(instrument="IPF", concept_decision_date=dt.date(2018, 9, 30)) == "LEGACY_SAFEGUARDS"


def test_es_missing_date_is_unresolved():
    assert rr.classify_es_regime(instrument="IPF", concept_decision_date=None) == "UNRESOLVED"


def test_op_7_screens_independent_of_es_regime():
    assert rr.op_7_50_screen(mentions_international_waterway=True) is True
    assert rr.op_7_60_screen(mentions_disputed_territory=True) is True
    assert rr.op_7_50_screen(mentions_international_waterway=False) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_router.py -k "es_ or op_7" -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (`AttributeError: classify_es_regime`).

- [ ] **Step 3: Write minimal implementation** (append to `regime_router.py`)

```python
ES_REGIMES = (
    "ESF_ESS1_TO_ESS10",
    "LEGACY_SAFEGUARDS",
    "PERFORMANCE_STANDARDS_OP_BP_4_03",
    "INSTRUMENT_SPECIFIC",
    "UNRESOLVED",
)


def classify_es_regime(
    instrument: str,
    concept_decision_date: Optional[dt.date] = None,
    *,
    op_bp_4_03_applies: bool = False,
    is_af: bool = False,
    parent_under_safeguard_policies: bool = False,
    af_exclusively_cost_overrun_or_gap: bool = False,
) -> str:
    """E&S regime router [OPS5.03-DIR.123 §III.A ¶1; ESF Policy ¶7/fn12/¶63/fn1].

    Decision order A-F (spec §5.1). Governed by the Concept Decision date, NOT the
    OIS date. ESS1-10 apply to IPF only.
    """
    inst = _norm(instrument)
    # (A) non-IPF -> route to the instrument's own E&S provisions.
    if inst not in {"ipf", "ipf-ddo", "ta", "mpa", ""}:
        return "INSTRUMENT_SPECIFIC"
    # (B) Performance Standards.
    if op_bp_4_03_applies:
        return "PERFORMANCE_STANDARDS_OP_BP_4_03"
    # (C) AF addressing EXCLUSIVELY a cost overrun / financing gap, parent under
    #     Safeguard Policies -> legacy (does NOT apply if the AF adds/changes activities).
    if is_af and parent_under_safeguard_policies and af_exclusively_cost_overrun_or_gap:
        return "LEGACY_SAFEGUARDS"
    # (D)/(E) date rule.
    if concept_decision_date is None:
        return "UNRESOLVED"
    return "ESF_ESS1_TO_ESS10" if concept_decision_date >= ES_REGIME_BOUNDARY else "LEGACY_SAFEGUARDS"


def op_7_50_screen(*, mentions_international_waterway: bool) -> bool:
    """OP/BP 7.50 International Waterways — a separate screen alongside the E&S regime."""
    return bool(mentions_international_waterway)


def op_7_60_screen(*, mentions_disputed_territory: bool) -> bool:
    """OP/BP 7.60 Disputed Territories — a separate screen alongside the E&S regime."""
    return bool(mentions_disputed_territory)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_router.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add regime_router.py tests/test_regime_router.py
git commit -m "feat: E&S-regime classifier + OP 7.50/7.60 screens"
```

### Task 1.4: Regime-aware `action_timing` vocabulary sets

**Files:**
- Modify: `regime_router.py`
- Test: `tests/test_regime_router.py`

- [ ] **Step 1: Write the failing test**

```python
def test_legacy_timing_set_matches_current_enum():
    assert rr.action_timing_vocab("legacy_transitional", "IPF") == (
        "flag-for-preparation", "required-before-appraisal",
        "required-before-board", "next-series", "supervision",
    )


def test_new_model_ipf_timing_has_td_ir_and_no_before_appraisal():
    vocab = rr.action_timing_vocab("new_model", "IPF")
    assert "before-TD-review" in vocab
    assert "before-IR" in vocab
    assert "before-One-Review" in vocab
    assert "required-before-appraisal" not in vocab
    assert not any("appraisal" in v for v in vocab)


def test_resolve_maps_legacy_before_appraisal_to_new_model():
    assert rr.resolve_action_timing("required-before-appraisal", "new_model", "IPF") == "before-TD-review"
    # legacy in legacy stays put
    assert rr.resolve_action_timing("required-before-appraisal", "legacy_transitional", "IPF") == "required-before-appraisal"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_router.py -k timing -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation** (append to `regime_router.py`)

```python
_LEGACY_TIMING = (
    "flag-for-preparation", "required-before-appraisal",
    "required-before-board", "next-series", "supervision",
)
_NEW_IPF_TIMING = (
    "shortly-after-OIS", "before-TD-review", "at-TD-review", "between-TD-and-IR",
    "before-IR", "at-IR", "before-One-Review", "at-One-Review",
    "before-negotiations", "before-Board", "during-implementation-support",
)


def action_timing_vocab(preparation_regime: str, instrument: str) -> tuple:
    """Allowed action_timing values for this regime. Legacy is unchanged from the
    current app enum; new-model IPF/PforR use the OIS/TD/IR/One-Review vocabulary
    (spec §5.3). DPF/PforR extensions layer on the new-model set at the call site.
    """
    if _norm(preparation_regime) == "new_model":
        return _NEW_IPF_TIMING
    return _LEGACY_TIMING


# Best-effort remap of a legacy timing string onto the new-model vocabulary so a
# model that emits the old value in new-model mode is corrected, never "appraisal".
_TIMING_REMAP_TO_NEW = {
    "flag-for-preparation": "shortly-after-OIS",
    "required-before-appraisal": "before-TD-review",
    "required-before-board": "before-Board",
    "next-series": "before-negotiations",
    "supervision": "during-implementation-support",
}


def resolve_action_timing(raw_timing: str, preparation_regime: str, instrument: str) -> str:
    """Validate/normalise a timing string against the regime vocabulary.

    - new-model: if raw is already valid, keep it; else remap a known legacy value;
      else fall back to 'shortly-after-OIS' (never 'before appraisal').
    - legacy: keep valid legacy values; unknown -> 'flag-for-preparation'.
    """
    raw = str(raw_timing or "").strip()
    vocab = action_timing_vocab(preparation_regime, instrument)
    if raw in vocab:
        return raw
    if _norm(preparation_regime) == "new_model":
        return _TIMING_REMAP_TO_NEW.get(raw, "shortly-after-OIS")
    return raw if raw in _LEGACY_TIMING else "flag-for-preparation"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_router.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS (full router suite).

- [ ] **Step 5: Commit**

```bash
git add regime_router.py tests/test_regime_router.py
git commit -m "feat: regime-aware action_timing vocabulary + resolver"
```

---

## Phase 2 — Stage 1 regime detection (prompt block + parser)

Emit and parse a `%%%REGIME_CONTEXT%%%` block. Detection is text-only; the router (Phase 1) turns detected dates/flags into classifications at parse time.

### Task 2.1: `extract_regime_context()` parser + strip

**Files:**
- Modify: `app.py` — add `extract_regime_context()`; extend `clean_stage1_output()` (grep: `def clean_stage1_output`).
- Test: `tests/test_regime_detection.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_regime_detection.py
import app as app_module


BLOCK = (
    "Intro text.\n"
    "%%%REGIME_CONTEXT_START%%%\n"
    "ois_creation_date: 2026-05-02\n"
    "preparation_regime_source: OIS datasheet\n"
    "concept_decision_or_equivalent_date: 2022-03-01\n"
    "concept_date_source: Project Datasheet\n"
    "op_bp_4_03_applies: false\n"
    "additional_financing_exception_applies: false\n"
    "op_7_50_screen: true\n"
    "op_7_60_screen: false\n"
    "evidence_markers: Project Paper; Technical Design Review; ANNEX 1: Results Framework\n"
    "conflicting_evidence: none\n"
    "%%%REGIME_CONTEXT_END%%%\n"
    "Body continues."
)


def test_extract_regime_context_classifies_both_axes():
    ctx = app_module.extract_regime_context(BLOCK)
    assert ctx["preparation_regime"] == "new_model"
    assert ctx["es_regime"] == "ESF_ESS1_TO_ESS10"
    assert ctx["op_7_50_screen"] is True
    assert ctx["op_7_60_screen"] is False


def test_missing_block_defaults_safely():
    ctx = app_module.extract_regime_context("no block here")
    assert ctx["preparation_regime"] == "unresolved_policy_source"
    assert ctx["es_regime"] == "UNRESOLVED"


def test_clean_stage1_strips_regime_block():
    cleaned = app_module.clean_stage1_output(BLOCK)
    assert "REGIME_CONTEXT_START" not in cleaned
    assert "ois_creation_date" not in cleaned
    assert "Body continues." in cleaned
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_detection.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (`AttributeError: extract_regime_context`).

- [ ] **Step 3: Write minimal implementation**

Add near the other `extract_*` parsers in `app.py` (grep: `def extract_temporal_context`):

```python
import datetime as _dt
import regime_router as _regime


def _parse_iso_date(value):
    value = (value or "").strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return _dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def extract_regime_context(text):
    """Parse %%%REGIME_CONTEXT_START/END%%% and classify both regime axes via
    regime_router. Missing block or fields default safely to unresolved/legacy so a
    missing signal never mis-asserts a regime."""
    default = {
        "preparation_regime": "unresolved_policy_source",
        "preparation_regime_source": "",
        "processing_model": "unknown",
        "ois_creation_date": "",
        "concept_decision_or_equivalent_date": "",
        "concept_date_source": "",
        "es_regime": "UNRESOLVED",
        "es_regime_source": "",
        "op_bp_4_03_applies": False,
        "additional_financing_exception_applies": False,
        "op_7_50_screen": False,
        "op_7_60_screen": False,
        "evidence_markers": "",
        "conflicting_evidence": "",
        "verification_flag": False,
        "verification_reason": "",
    }
    m = re.search(r"%%%REGIME_CONTEXT_START%%%(.*?)%%%REGIME_CONTEXT_END%%%", text, re.DOTALL)
    if not m:
        return default
    fields = dict(default)
    for line in m.group(1).strip().splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if key in fields:
            if isinstance(default.get(key), bool):
                fields[key] = val.strip().lower() in {"true", "yes", "1"}
            else:
                fields[key] = val
    ois = _parse_iso_date(fields.get("ois_creation_date"))
    concept = _parse_iso_date(fields.get("concept_decision_or_equivalent_date"))
    fields["preparation_regime"] = _regime.classify_preparation_regime(ois)
    # instrument comes from the existing INSTRUMENT_TYPE line; pass it in at the call
    # site if available. Default IPF for the E&S router keeps ESS routing conservative.
    fields["es_regime"] = _regime.classify_es_regime(
        instrument="IPF",
        concept_decision_date=concept,
        op_bp_4_03_applies=fields["op_bp_4_03_applies"],
        is_af=fields["additional_financing_exception_applies"],
        parent_under_safeguard_policies=fields["additional_financing_exception_applies"],
        af_exclusively_cost_overrun_or_gap=fields["additional_financing_exception_applies"],
    )
    if fields["preparation_regime"] == "unresolved_policy_source" or fields["es_regime"] == "UNRESOLVED":
        fields["verification_flag"] = True
        fields["verification_reason"] = fields.get("verification_reason") or "regime signal missing or contradictory"
    return fields
```

In `clean_stage1_output()`, add the strip alongside the other blocks:

```python
    text = re.sub(r"%%%REGIME_CONTEXT_START%%%.*?%%%REGIME_CONTEXT_END%%%", "", text, flags=re.DOTALL)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_detection.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_regime_detection.py
git commit -m "feat: extract_regime_context parser + Stage 1 strip"
```

### Task 2.2: Stage 1 prompt emits the regime block + detection guidance

**Files:**
- Modify: `app.py` — `DEFAULT_PROMPTS["1"]` (grep: `%%%INSTRUMENT_TYPE`), add the regime block spec + detection precedence + source discipline.
- Test: `tests/test_regime_detection.py`

- [ ] **Step 1: Write the failing test**

```python
def test_stage1_prompt_requests_regime_block():
    p = app_module.DEFAULT_PROMPTS["1"]
    assert "%%%REGIME_CONTEXT_START%%%" in p
    assert "ois_creation_date" in p
    assert "concept_decision_or_equivalent_date" in p
    assert "18 April 2026" in p or "2026-04-18" in p
    assert "1 October 2018" in p or "2018-10-01" in p
    # Source discipline: do not equate Public with Published.
    assert "Published" in p and "Public" in p
    # "PID" alone is not decisive.
    assert "PID" in p
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_detection.py::test_stage1_prompt_requests_regime_block -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation** — insert into `DEFAULT_PROMPTS["1"]` immediately after the `%%%INSTRUMENT_TYPE%%%` / `%%%TEMPORAL_CONTEXT%%%` instructions:

```text
After the temporal block, emit a regime-detection block EXACTLY in this shape (all
fields present; use "Unknown"/"false" when a signal is absent — never guess):

%%%REGIME_CONTEXT_START%%%
ois_creation_date: [YYYY-MM-DD from the OIS/Datasheet, else Unknown]
preparation_regime_source: [where the date/markers came from]
concept_decision_or_equivalent_date: [YYYY-MM-DD of Concept Decision/equivalent, else Unknown]
concept_date_source: [where it came from]
op_bp_4_03_applies: [true|false — PS1-PS8 / Performance Standards present]
additional_financing_exception_applies: [true if this is an AF addressing EXCLUSIVELY a cost overrun/financing gap]
op_7_50_screen: [true if an international waterway is implicated]
op_7_60_screen: [true if a disputed territory is implicated]
evidence_markers: [semicolon list of the exact strings you keyed on]
conflicting_evidence: [any contradictory signals, else none]
%%%REGIME_CONTEXT_END%%%

DETECTION RULES (do not decide the regime from the document LABEL alone):
- Preparation regime is governed by the operation's OWN OIS creation date vs
  18 April 2026 [OPS5.03-PROC.281/282]. New-model markers: "Project Paper"/"Program
  Paper", "Technical Design Review", "Implementation Readiness Review", "One Review",
  "Project Assessment Summary", "Operation Information Summary". Legacy markers: PCN,
  "Concept Review", "Track 1/2", "Project Appraisal Document"/PAD, "Appraisal
  Stage/Package", "Decision Review". "PID" ALONE is NOT decisive (both regimes use it);
  a guidance catalogue number is NOT proof an operation is new-regime.
- E&S regime is a SEPARATE axis governed by the Concept Decision date vs
  1 October 2018 [OPS5.03-DIR.123 §III.A ¶1] — NOT by the OIS date. ESS1-10 apply to
  IPF only; DPF/PforR have their own E&S provisions. ESF markers: ESRC/ESRS/ESCP/SEP/
  ESS1-10; legacy markers: Environmental Category A/B/C/FI, ISDS, "Safeguard Policies
  triggered", OP/BP 4.xx.
- SOURCE DISCIPLINE: cite the marker you used; distinguish policy text from your own
  inference; do NOT equate "Public" (an Access-to-Information designation) with
  "Published" (a publication status). When signals conflict or a governing date is
  missing, leave the date Unknown and note it in conflicting_evidence.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_detection.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_regime_detection.py
git commit -m "feat: Stage 1 prompt emits regime-detection block + rules"
```

### Task 2.3: Carry regime fields on `AnalysisState` + pass instrument to the E&S router

**Files:**
- Modify: `app.py` — `AnalysisState` (grep: `class AnalysisState`), and the Stage-1 handler where `extract_regime_context` is called so the real `instrument_type` is passed to `classify_es_regime` (replace the conservative default in Task 2.1).
- Test: `tests/test_regime_detection.py`

- [ ] **Step 1: Write the failing test**

```python
def test_analysis_state_carries_regime_fields():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": [], "lens_versions": {}, "doc_type": "PAD",
        "regime_context": {"preparation_regime": "new_model", "es_regime": "ESF_ESS1_TO_ESS10",
                           "processing_model": "two_step"},
    })
    assert state.preparation_regime == "new_model"
    assert state.es_regime == "ESF_ESS1_TO_ESS10"
    assert state.processing_model == "two_step"


def test_analysis_state_regime_defaults_when_absent():
    state = app_module.AnalysisState.from_payload({"active_lenses": [], "lens_versions": {}, "doc_type": "PAD"})
    assert state.preparation_regime == "unresolved_policy_source"
    assert state.es_regime == "UNRESOLVED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_detection.py -k analysis_state -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (`AttributeError: preparation_regime`).

- [ ] **Step 3: Write minimal implementation** — add fields to `AnalysisState` (mirror how `from_payload` reads existing keys such as `doc_type`):

```python
        regime = (payload.get("regime_context") or {}) if isinstance(payload, dict) else {}
        self.preparation_regime = regime.get("preparation_regime", "unresolved_policy_source")
        self.es_regime = regime.get("es_regime", "UNRESOLVED")
        self.processing_model = regime.get("processing_model", "unknown")
```

At the Stage-1 handler call site, pass the real instrument (grep the two `extract_regime_context(` call sites — express + step-by-step), and set `processing_model` via `regime_router.classify_processing_model(...)` from the parsed risk ratings if available.

- [ ] **Step 4: Run test to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_detection.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_regime_detection.py
git commit -m "feat: AnalysisState carries regime fields; real instrument to E&S router"
```

---

## Phase 3 — Terminology normalisation

### Task 3.1: `IPF_APPRAISAL_DOCUMENT` label rendering + `pad_sections` ↔ `appraisal_document_sections` back-compat

**Files:**
- Modify: `app.py` — add a label resolver; extend `extract_priorities` to accept both `pad_sections` and `appraisal_document_sections`.
- Modify: `background_docs.py` — add regime label strings.
- Test: `tests/test_regime_terminology.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_regime_terminology.py
import app as app_module


def test_appraisal_document_label_per_regime():
    assert app_module.appraisal_document_label("new_model", "IPF") == "Project Paper"
    assert app_module.appraisal_document_label("new_model", "PforR") == "Program Paper"
    assert app_module.appraisal_document_label("new_model", "DPO") == "Program Document"
    assert app_module.appraisal_document_label("legacy_transitional", "IPF") == "Project Appraisal Document (PAD)"


def test_pad_sections_backcompat_reads_either_key():
    block_new = (
        '%%%JSON_START%%%{"fcv_rating":"Moderately addressed",'
        '"fcv_responsiveness_rating":"Emerging","sensitivity_summary":"x",'
        '"responsiveness_summary":"y","risk_exposure":{"risks_to":"a","risks_from":"b"},'
        '"priorities":[{"title":"T","fcv_dimension":"Contextual","tag":"[S]","the_gap":"g",'
        '"why_it_matters":"w","actions":[],"who_acts":"TTL","when":"soon","resources":"r",'
        '"appraisal_document_sections":"IV.C"}]}%%%JSON_END%%%'
    )
    r = app_module.extract_priorities(block_new, uploaded_doc_names=[])
    p = r["priorities"][0]
    assert p["appraisal_document_sections"] == "IV.C"
    assert p["pad_sections"] == "IV.C"  # legacy alias preserved for existing renderers
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_terminology.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

```python
def appraisal_document_label(preparation_regime, instrument):
    inst = str(instrument or "").strip().lower()
    if str(preparation_regime or "").strip().lower() == "new_model":
        if inst in {"dpo", "dpf"}:
            return "Program Document"
        if inst == "pforr":
            return "Program Paper"
        return "Project Paper"
    return "Project Appraisal Document (PAD)"
```

In `extract_priorities`, in the per-priority loop, reconcile the two keys (keep both populated for renderer back-compat):

```python
        sections = pr.get("appraisal_document_sections")
        if sections is None:
            sections = pr.get("pad_sections", "")
        pr["appraisal_document_sections"] = sections or ""
        pr["pad_sections"] = pr["appraisal_document_sections"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_terminology.py tests/test_extract_priorities.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py background_docs.py tests/test_regime_terminology.py
git commit -m "feat: regime document-label resolver + appraisal_document_sections back-compat"
```

### Task 3.2: Render the regime label in Stage 1 output + frontend

**Files:**
- Modify: `app.py` — inject `appraisal_document_label(...)` where the doc-type/instrument is surfaced to Stage 2/3 prompts.
- Modify: `index.html` — where the document type is displayed, prefer the regime-rendered label (grep: `DOC_TYPE` / the doc-type chip).
- Test: `tests/test_regime_terminology.py` (+ a frontend assertion in `tests/test_regime_detection.py` if a JS contract test exists).

- [ ] **Step 1: Write the failing test**

```python
def test_stage2_prompt_uses_regime_label(monkeypatch):
    state = app_module.AnalysisState.from_payload({
        "active_lenses": [], "lens_versions": {}, "doc_type": "PAD",
        "regime_context": {"preparation_regime": "new_model", "es_regime": "ESF_ESS1_TO_ESS10"},
        "instrument_type": "IPF",
    })
    prompt = app_module.build_lens_stage_context(state, 3)["prompt"] if hasattr(app_module, "build_lens_stage_context") else ""
    # In new-model mode the memo must not tell the user to edit "the PAD"; it uses "Project Paper".
    # (If the Stage 3 label injection lives in DEFAULT_PROMPTS['3'] formatting, assert there instead.)
    assert "Project Paper" in prompt or "Project Paper" in app_module.DEFAULT_PROMPTS["3"]
```

- [ ] **Step 2: Run to verify** — adjust the assertion target to wherever the label is injected (prompt `.format` kwarg vs a prefix string). Expected: FAIL until the label is threaded in.
- [ ] **Step 3: Implement** — thread `appraisal_document_label(state.preparation_regime, instrument_type)` into the Stage 3 prompt as a `{appraisal_document_label}` kwarg, replacing hard-coded "PAD" references in the memo instructions with the rendered label; in `index.html` show the label in the doc-type chip when `regime_context.preparation_regime === "new_model"`.
- [ ] **Step 4: Run** `tests/test_regime_terminology.py` — Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add app.py index.html tests/test_regime_terminology.py
git commit -m "feat: render regime-appropriate appraisal-document label in Stage 3 + UI"
```

---

## Phase 4 — Regime-aware `action_timing`

### Task 4.1: Validate `action_timing` against the regime vocabulary in `extract_priorities`

**Files:**
- Modify: `app.py` — `extract_priorities` (thread `preparation_regime` + `instrument` in; use `regime_router.resolve_action_timing`).
- Test: `tests/test_regime_timing.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_regime_timing.py
import app as app_module


def _block(timing):
    return (
        '%%%JSON_START%%%{"fcv_rating":"Moderately addressed",'
        '"fcv_responsiveness_rating":"Emerging","sensitivity_summary":"x",'
        '"responsiveness_summary":"y","risk_exposure":{"risks_to":"a","risks_from":"b"},'
        '"priorities":[{"title":"T","fcv_dimension":"Contextual","tag":"[S]","the_gap":"g",'
        '"why_it_matters":"w","actions":[],"who_acts":"TTL","when":"soon","resources":"r",'
        '"pad_sections":"IV","action_timing":"' + timing + '"}]}%%%JSON_END%%%'
    )


def test_new_model_remaps_before_appraisal():
    r = app_module.extract_priorities(_block("required-before-appraisal"), uploaded_doc_names=[],
                                      preparation_regime="new_model", instrument="IPF")
    t = r["priorities"][0]["action_timing"]
    assert t == "before-TD-review"
    assert "appraisal" not in t


def test_legacy_keeps_before_appraisal():
    r = app_module.extract_priorities(_block("required-before-appraisal"), uploaded_doc_names=[],
                                      preparation_regime="legacy_transitional", instrument="IPF")
    assert r["priorities"][0]["action_timing"] == "required-before-appraisal"
```

- [ ] **Step 2: Run to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_timing.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL (`TypeError: unexpected keyword 'preparation_regime'`).

- [ ] **Step 3: Implement** — add `preparation_regime="unresolved_policy_source"` and `instrument=""` kwargs to `extract_priorities`; after the existing `action_timing` remap (grep: `pre-appraisal` back-compat), pass the value through the resolver:

```python
        pr["action_timing"] = _regime.resolve_action_timing(
            pr.get("action_timing", ""), preparation_regime, instrument,
        )
```

Thread the two new kwargs from the Stage 3 call sites (express + step-by-step) using `state.preparation_regime` and the parsed instrument. **Legacy default keeps existing behaviour** (unresolved/legacy → legacy vocabulary → unchanged).

- [ ] **Step 4: Run to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_timing.py tests/test_extract_priorities.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_regime_timing.py
git commit -m "feat: regime-aware action_timing resolution in extract_priorities"
```

### Task 4.2: New-model timing pills in the frontend

**Files:**
- Modify: `index.html` — `action_timing` pill map (grep: `timing_map` / the pill colour switch in `showPriority`).
- Test: `tests/test_regime_timing.py` (or the frontend contract test if present).

- [ ] **Step 1: Write the failing test** — assert the pill map contains the new-model keys (`before-TD-review`, `before-IR`, `before-One-Review`, `during-implementation-support`) with a colour class each, and that unknown keys fall back to a neutral pill.
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — extend the pill map in `showPriority()` and the DOCX `timing_map` with the 11 new-model IPF values; keep the 5 legacy values. Label text: humanise (`before-TD-review` → "Before Technical Design review").
- [ ] **Step 4: Run** the frontend test — Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add index.html app.py tests/test_regime_timing.py
git commit -m "feat: new-model TD/IR/One-Review timing pills (UI + DOCX)"
```

---

## Phase 5 — Document sections & instrument reference checks

### Task 5.1: Project Paper / Program Paper section constants + regime-gated minimum reference set

**Files:**
- Modify: `background_docs.py` — add `IPF_PROJECT_PAPER_SECTIONS`, `PFORR_PROGRAM_PAPER_SECTIONS`, and a corrected `NEW_MODEL_MINIMUM_REFERENCE_SET`.
- Modify: `app.py` — a selector `appraisal_reference_set(preparation_regime, es_regime, instrument)` returning the right set.
- Test: `tests/test_regime_terminology.py`

- [ ] **Step 1: Write the failing test**

```python
def test_new_model_ipf_reference_set_corrections():
    refs = app_module.appraisal_reference_set("new_model", "ESF_ESS1_TO_ESS10", "IPF")
    joined = " ".join(refs).lower()
    assert "results framework" in joined            # mandatory Annex 1
    assert "readiness esrs" in joined               # ADDED
    assert "economic analysis" in joined            # ADDED
    assert "operations manual" not in joined        # REMOVED from universal minimum
    assert "ess1" not in joined                     # replaced by "applicable ESSs"
    assert "applicable esss" in joined


def test_non_esf_instrument_omits_ess_checks():
    refs = app_module.appraisal_reference_set("new_model", "INSTRUMENT_SPECIFIC", "PforR")
    assert not any("ess" in r.lower() for r in refs)


def test_legacy_reference_set_unchanged():
    refs = app_module.appraisal_reference_set("legacy_transitional", "ESF_ESS1_TO_ESS10", "IPF")
    # Legacy path returns the existing PAD minimum set verbatim (regression guard).
    assert app_module.appraisal_reference_set("legacy_transitional", "LEGACY_SAFEGUARDS", "IPF") == \
        app_module.LEGACY_PAD_MINIMUM_REFERENCE_SET
```

- [ ] **Step 2: Run to verify it fails**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_terminology.py -k reference_set -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: FAIL.

- [ ] **Step 3: Implement** — in `background_docs.py`:

```python
IPF_PROJECT_PAPER_SECTIONS = (
    "I Strategic Context (A Country, B Sectoral & Institutional)",
    "II Project Description (PDO; ToC + PDO indicators; Beneficiaries; Components; Partners; Lessons)",
    "III Implementation (Institutional/Implementation; Results M&E/Verification; Disbursement)",
    "IV Project Assessment Summary (A Technical/Economic/Financial; B Fiduciary [FM, Procurement]; C Environmental/Social/Legal)",
    "V Key Risks",
    "Annex 1 Results Framework (only mandatory annex)",
)
PFORR_PROGRAM_PAPER_SECTIONS = IPF_PROJECT_PAPER_SECTIONS + (
    "Program Scope", "Disbursement-Linked Indicators", "IPF-Component summary",
    "Program Action Plan (IV.E)",
)
# New-model IPF minimum reference set (spec §5.4 corrections). ESS checks gate on es_regime==ESF & IPF.
NEW_MODEL_MINIMUM_REFERENCE_SET = (
    "SORT", "SEP / ESS10", "ESCP", "Results Framework (mandatory Annex 1)",
    "applicable ESSs + ES risk assessment", "Readiness ESRS", "Economic Analysis",
    "FM assessment", "Procurement Plan (at readiness)", "Legal Agreements / DFIL (separate)", "PID",
    "SEA/SH Action Plan (conditional)",
)
```

Preserve the current PAD set under a stable name for the regression guard:

```python
LEGACY_PAD_MINIMUM_REFERENCE_SET = (  # the existing v9.x set, moved here verbatim
    "SORT", "ESS1", "SEA/SH Action Plan", "SEP / ESS10", "ESCP",
    "Operations Manual", "PPSD", "Results Framework",
)
```

In `app.py`:

```python
def appraisal_reference_set(preparation_regime, es_regime, instrument):
    if str(preparation_regime).strip().lower() != "new_model":
        return background_docs.LEGACY_PAD_MINIMUM_REFERENCE_SET
    refs = list(background_docs.NEW_MODEL_MINIMUM_REFERENCE_SET)
    esf = str(es_regime).strip().upper() == "ESF_ESS1_TO_ESS10" and str(instrument).strip().lower() == "ipf"
    if not esf:
        refs = [r for r in refs if "ess" not in r.lower()]
    return tuple(refs)
```

- [ ] **Step 4: Run to verify it passes**

Run: `C:/WBG/Python313/python.exe -m pytest tests/test_regime_terminology.py -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add background_docs.py app.py tests/test_regime_terminology.py
git commit -m "feat: Project/Program Paper sections + regime-gated minimum reference set"
```

### Task 5.2: Inject the regime-appropriate section/reference set into the Stage 3 prompt

**Files:**
- Modify: `app.py` — Stage 3 prompt build (thread `appraisal_reference_set(...)` + the section list as `{appraisal_document_sections_ref}` / `{minimum_reference_set}` kwargs, replacing the hard-coded "PAD minimum instrument reference set").
- Test: `tests/test_regime_terminology.py`

- [ ] **Step 1: Write the failing test** — assert that with `preparation_regime="new_model"`, the Stage 3 prompt text contains "Project Assessment Summary" and "Readiness ESRS" and does NOT contain the hard-coded legacy "Operations Manual" minimum; and that legacy mode still contains the legacy set.
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — replace the hard-coded reference-set string in `DEFAULT_PROMPTS["3"]` with a `{minimum_reference_set}` placeholder filled from `appraisal_reference_set(...)`; add the section list for context. Wire both Stage 3 call sites (express `.format` kwarg + step-by-step). **Express Stage 3 uses the `.format` kwarg, not a post-format `.replace`** (mirror the v9.14 fix that avoided a `KeyError` blanking all placeholders).
- [ ] **Step 4: Run** `tests/test_regime_terminology.py` + `tests/test_sector_lens_app_contract.py` — Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_regime_terminology.py
git commit -m "feat: inject regime section/reference set into Stage 3 prompt (both routes)"
```

---

## Phase 6 — Recommendation authority tagging (`authority_basis`)

> If the climate plan's Task 4B.3 already landed this field, **skip Task 6.1** and only confirm the schema mentions it in the non-climate Stage 3 prompt (Task 6.2). Check first: `grep -n "authority_basis" app.py`.

### Task 6.1: `authority_basis` field validation + default

**Files:**
- Modify: `app.py` — `extract_priorities` validation.
- Test: `tests/test_extract_priorities.py`

- [ ] **Step 1: Write the failing test**

```python
def test_authority_basis_default_and_coercion():
    base = (
        '%%%JSON_START%%%{"fcv_rating":"Moderately addressed",'
        '"fcv_responsiveness_rating":"Emerging","sensitivity_summary":"x",'
        '"responsiveness_summary":"y","risk_exposure":{"risks_to":"a","risks_from":"b"},'
        '"priorities":[{"title":"T","fcv_dimension":"Contextual","tag":"[S]","the_gap":"g",'
        '"why_it_matters":"w","actions":[],"who_acts":"TTL","when":"soon","resources":"r",'
        '"pad_sections":"IV"%s}]}%%%JSON_END%%%'
    )
    missing = app_module.extract_priorities(base % "", uploaded_doc_names=[])
    assert missing["priorities"][0]["authority_basis"] == "reviewer_judgment"
    bad = app_module.extract_priorities(base % ',"authority_basis":"nonsense"', uploaded_doc_names=[])
    assert bad["priorities"][0]["authority_basis"] == "reviewer_judgment"
    good = app_module.extract_priorities(base % ',"authority_basis":"Directive"', uploaded_doc_names=[])
    assert good["priorities"][0]["authority_basis"] == "directive"
```

- [ ] **Step 2: Run to verify it fails.**
- [ ] **Step 3: Implement** in the per-priority loop:

```python
        allowed_authority = {"policy", "directive", "procedure", "guidance", "reviewer_judgment"}
        ab = str(pr.get("authority_basis") or "").strip().lower().replace(" ", "_")
        pr["authority_basis"] = ab if ab in allowed_authority else "reviewer_judgment"
```

  (Do NOT add it to `_REQUIRED_PRIORITY_FIELDS` — it defaults safely.)
- [ ] **Step 4: Run** `tests/test_extract_priorities.py` — Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_extract_priorities.py
git commit -m "feat: authority_basis field validation + safe default"
```

### Task 6.2: `authority_basis` in the (non-climate) Stage 3 schema + render + export

**Files:**
- Modify: `app.py` — `DEFAULT_PROMPTS["3"]` JSON schema (add the field with its enum + one-line meaning) + DOCX export line.
- Modify: `index.html` — `showPriority()` chip + `downloadHTML()` line.
- Test: `tests/test_regime_terminology.py` (prompt schema) + frontend contract test.

- [ ] **Step 1: Write the failing test** — assert `"authority_basis"` and the five enum values appear in `DEFAULT_PROMPTS["3"]`.
- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — add `"authority_basis": "policy | directive | procedure | guidance | reviewer_judgment (strength of the underlying OPCS source)"` to the per-priority schema; render a muted chip in `showPriority()` and a metadata line in DOCX + `downloadHTML()`.
- [ ] **Step 4: Run** the prompt-schema + frontend tests — Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add app.py index.html tests/test_regime_terminology.py
git commit -m "feat: authority_basis in Stage 3 schema + UI chip + exports"
```

---

## Phase 7 — Regime injection into Stage 2/3 + legacy regression

### Task 7.1: Inject the detected regime framing into Stage 2/3 prompts

**Files:**
- Modify: `app.py` — Stage 2 + Stage 3 prompt builds (both routes) inject a compact regime header (preparation_regime, processing_model, es_regime, document label, timing vocabulary) so gate/timing/section language renders per regime.
- Test: `tests/test_regime_regression.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_regime_regression.py
import app as app_module


def test_new_model_stage3_prompt_names_td_ir_gates():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": [], "lens_versions": {}, "doc_type": "PAD", "instrument_type": "IPF",
        "regime_context": {"preparation_regime": "new_model", "processing_model": "two_step",
                           "es_regime": "ESF_ESS1_TO_ESS10"},
    })
    prompt = app_module.build_lens_stage_context(state, 3)["prompt"] if hasattr(app_module, "build_lens_stage_context") else app_module.DEFAULT_PROMPTS["3"]
    assert "Technical Design" in prompt and "Implementation Readiness" in prompt
    assert "before appraisal" not in prompt.lower()


def test_legacy_stage3_prompt_unchanged_wording():
    state = app_module.AnalysisState.from_payload({
        "active_lenses": [], "lens_versions": {}, "doc_type": "PAD", "instrument_type": "IPF",
        "regime_context": {"preparation_regime": "legacy_transitional", "es_regime": "LEGACY_SAFEGUARDS"},
    })
    prompt = app_module.build_lens_stage_context(state, 3)["prompt"] if hasattr(app_module, "build_lens_stage_context") else app_module.DEFAULT_PROMPTS["3"]
    # Legacy still speaks the appraisal/Decision-Review vocabulary.
    assert "appraisal" in prompt.lower()
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement** — build a compact regime header string and inject it as a `{regime_header}` kwarg in the Stage 2/3 prompts (both routes). For `unresolved_policy_source`/`UNRESOLVED`, the header states the ambiguity and instructs the model to hedge gate/timing language and add a verify note — never assert a regime. Legacy header reproduces today's wording so legacy output is unchanged.
- [ ] **Step 4: Run** `tests/test_regime_regression.py` — Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_regime_regression.py
git commit -m "feat: inject regime header into Stage 2/3 prompts (both routes)"
```

### Task 7.2: Legacy-mode output regression guard (full suite)

**Files:**
- Test: `tests/test_regime_regression.py` + the full suite.

- [ ] **Step 1: Add a regression test** asserting that with **no** `regime_context` on the payload (the pre-existing behaviour), every regime-sensitive helper returns its legacy value: `appraisal_document_label(...)` → PAD; `appraisal_reference_set(...)` → `LEGACY_PAD_MINIMUM_REFERENCE_SET`; `resolve_action_timing("required-before-appraisal", "unresolved_policy_source", "IPF")` → `required-before-appraisal`.
- [ ] **Step 2: Run the FULL suite**

Run: `C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS — the prior green baseline (375) **plus** the new regime tests; **zero** pre-existing tests changed. If any legacy test changed output, the default path leaked a new-model behaviour — fix the default before proceeding.

- [ ] **Step 3: Commit**

```bash
git add tests/test_regime_regression.py
git commit -m "test: legacy-mode regime regression guard; full suite green"
```

---

## Phase 8 — Integration, docs, live validation

### Task 8.1: Update developer docs

**Files:**
- Modify: `CLAUDE.md` (version history entry + Stage 1 pipeline note for the regime block), `docs/reference/reference_prompt_architecture.md` (regime block schema), `docs/reference/reference_backend_routes.md` (`extract_regime_context` signature), `FCV_BUILD_PARITY.md` (ITS parity: `regime_router` + `%%%REGIME_CONTEXT%%%` + `authority_basis`).

- [ ] **Step 1** Add a `v9.x — Dual-regime process model` version-history block to `CLAUDE.md` (two independent axes; `regime_router.py`; `%%%REGIME_CONTEXT%%%`; terminology normalisation; regime-aware `action_timing`; `authority_basis`).
- [ ] **Step 2** Document the regime block schema + `extract_regime_context` in the two reference docs.
- [ ] **Step 3** Note the ITS/FastAPI parity surface in `FCV_BUILD_PARITY.md`.
- [ ] **Step 4: Commit**

```bash
git add -f CLAUDE.md docs/reference/*.md
git commit -m "docs: document dual-regime process model + regime block schema"
```

### Task 8.2: Full suite + non-regime regression + deploy (maintainer-run)

- [ ] **Step 1** Full suite green:

Run: `C:/WBG/Python313/python.exe -m pytest -q -p no:cacheprovider --ignore-glob=pytest-cache-files-*`
Expected: PASS.

- [ ] **Step 2** Maintainer-run live validation on Render: one legacy PAD (expect PAD/appraisal vocabulary unchanged) and one new-model Project Paper fixture (expect Project Paper label + TD/IR/One-Review timing + corrected reference set). Capture the Render log line for the regime block on each.
- [ ] **Step 3** Open the PR; sequence the integration with the climate branch per "Branch & integration".

---

## Self-Review

**1. Spec coverage:**
- §3 two axes → Phase 1 (`regime_router`) Tasks 1.1/1.3.
- §4.1 preparation boundary + AF-by-own-OIS/restructuring-bypass/MPA → Task 1.1 + the detection rules in Task 2.2 (restructuring-bypass/AF-by-own-OIS are detection-time facts fed to the router; the router itself is date-driven). **Gap check:** the restructuring-bypass and MPA-later-phase *routing* are documented as prompt detection rules (Task 2.2) rather than a dedicated router function because they change *which date* is fed in, not the classification maths — acceptable; add a router helper only if a test needs it.
- §4.2 one/two-step/DPF → Task 1.2.
- §4.3 gates & death of appraisal → Tasks 4.1 (timing), 7.1 (prompt header).
- §5.1 Stage 1 detection block + E&S router → Phase 2 + Task 1.3.
- §5.2 terminology normalisation → Phase 3.
- §5.3 regime-aware timing → Phase 1 Task 1.4 + Phase 4.
- §5.4 sections & reference checks → Phase 5.
- §5.5 authority tagging → Phase 6.
- §6 climate consumption → the climate plan's Task 4B (cross-referenced; `authority_basis` dependency guard in both plans).
- §7 preserved invariants → Task 7.2 regression guard + safe defaults throughout.
- §8 testing → every phase is TDD; Task 7.2 is the legacy byte-for-byte guard.
- §9 verify-with-OPCS → Gate-1 review brief (run before Phase 2); `dpf_sections` full TOC left as a documented open item in Task 5.1 (Program Paper/PD sections are best-effort until the DPF PD template is confirmed).

**2. Placeholder scan:** Phase 1 tasks carry complete runnable code. Integration tasks (Phases 2–7) give complete code for the new functions and name the exact helper + a grep anchor for each app.py/index.html insertion point (line numbers omitted deliberately — `app.py` is ~9k lines and shifts between sessions; grep anchors are stable). No "TBD"/"add error handling"/"similar to Task N".

**3. Type consistency:** `preparation_regime` values (`new_model` | `legacy_transitional` | `unresolved_policy_source`), `es_regime` values (5), `processing_model` values (4), and the `action_timing` sets are defined once in `regime_router.py` and referenced by string throughout. `appraisal_document_sections`/`pad_sections` kept as mirrored keys. `authority_basis` enum identical in both plans.

---

## Execution Handoff

Plan complete. Two execution options:
1. **Subagent-Driven (recommended)** — a fresh subagent per task, review between tasks. Best for this plan because Phase 1 is fully specified and self-contained, while Phases 2–7 need a quick grep to anchor each insertion.
2. **Inline Execution** — batch with checkpoints via `superpowers:executing-plans`.

**Do not start before:** (a) the maintainer confirms the branch (fresh `feat/dual-regime-process-model` off `main`), and (b) the Gate-1 Copilot review (`.../reviews/2026-07-26-dual-regime-spec-gate1-copilot-review-brief.md`) has returned and any CORRECT-AS-FOLLOWS fixes are folded into the spec + memory. Phase 1 (pure router) may begin in parallel with the review since it is cited directly from the confirmed decision tables.
