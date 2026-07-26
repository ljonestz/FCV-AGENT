"""Pure, side-effect-free OPCS regime classifiers for the FCV screener.

Two INDEPENDENT axes (do not conflate — separate governing fields):
  * preparation regime  -> governed by the operation's OIS creation date vs
    18 Apr 2026 [OPS5.03-PROC.281/282, eff 18 Apr 2026].
  * E&S regime          -> governed by the Concept Decision date vs 1 Oct 2018
    [OPS5.03-DIR.123, eff 15 Jan 2026, §III.A ¶1; ESF Policy ¶7/fn12/¶63/fn1].

Every function returns a safe fallback (unresolved/unknown/legacy) rather than
guessing when inputs are missing or contradictory, so a missing signal never
mis-asserts a regime. Sources: memory `project_opcs_july2026_process_change.md`;
spec `docs/superpowers/specs/2026-07-26-dual-regime-process-model-design.md`.
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
PROCESSING_MODELS = ("one_step", "two_step", "one_review", "unknown")
ES_REGIMES = (
    "ESF_ESS1_TO_ESS10",
    "LEGACY_SAFEGUARDS",
    "PERFORMANCE_STANDARDS_OP_BP_4_03",
    "INSTRUMENT_SPECIFIC",
    "UNRESOLVED",
)

_HIGH = {"substantial", "high"}
_LOWMOD = {"low", "moderate"}


def _norm(value: Optional[str]) -> str:
    return str(value or "").strip().lower()


# --- Preparation regime ------------------------------------------------------

def classify_preparation_regime(ois_creation_date: Optional[dt.date]) -> str:
    """Classify the preparation regime from the operation's OWN OIS creation date."""
    if ois_creation_date is None:
        return "unresolved_policy_source"
    return "new_model" if ois_creation_date >= PREPARATION_BOUNDARY else "legacy_transitional"


# --- Processing model (one/two-step) -----------------------------------------

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
    if sort_n in _LOWMOD and es_n in _LOWMOD and all((r in _LOWMOD) for r in ratings if r):
        return "one_step"
    return "unknown"


# --- E&S regime + separate operational-policy screens ------------------------

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


# --- Regime-aware action_timing vocabulary -----------------------------------

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
