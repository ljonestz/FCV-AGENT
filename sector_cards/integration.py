"""Stage wiring for mechanism cards (design v3, sections 2, 6 and 6a).

Pure functions only, so the Flask app (Render) and the FastAPI app (ITS) can share them:

  Stage 1  SECTOR_FACTS_PROMPT -> model emits %%%SECTOR_FACTS%%% -> extract_sector_facts()
           -> route_from_facts() gives the eligible cards and the user-facing reason line.
  Stage 2  build_stage2_card_slice() -> model emits %%%SECTOR_CARDS%%% -> extract_sector_cards().
  Stage 3  build_stage3_card_slice() -> priorities may carry `sector_cards`
           -> apply_sector_cards() + build_readout_fields() give sector_provenance / sector_additional.

Every step is deterministic except the two model blocks, and both blocks are optional: a missing or empty
block means "no sector content", never a recovery call.
"""
from __future__ import annotations

import json
import re
from typing import Any

from .datasheet import _names_in, parse_practice_areas
from .models import FEATURES, PILOT_SECTORS, CardSet, load_cards
from .router import FeatureEvidence, ProjectFacts, route

MAX_SELECTED = 3
MAX_ADDITIONAL = 2
PROJECT_FEATURES = tuple(f for f in FEATURES if not f.startswith("pa_"))
FCV_SETTINGS = ("active_conflict", "criminal_violence", "post_conflict", "institutional_fragility",
                "displacement_hosting", "any")
SECTOR_LABELS = {"transport": "Transport", "water": "Water", "agriculture": "Agriculture",
                 "enrm": "Environment and natural resources", "ews_hydromet": "Early warning and hydromet"}
FEATURE_LABELS = {
    "rural_feeder_roads": "roads and corridors", "civil_works_contracts": "large civil-works contracts",
    "water_points_wash": "water points and supply", "bulk_water_irrigation": "bulk water and irrigation",
    "agri_inputs_pastoral": "agricultural inputs, livestock and value chains",
    "food_security_reserves": "food reserves and food-crisis monitoring",
    "nrm_landscape_forest": "forests, landscapes, fisheries or protected areas",
    "land_acquisition_tenure": "land acquisition or tenure", "local_funds_cdd": "local or community funds",
    "ews_hydromet": "early warning and hydromet",
}

SECTOR_FACTS_PROMPT = """
%%%SECTOR_FACTS_START%%%
practice_area_lead: [the name printed after "Practice Area (Lead)" in the datasheet, copied exactly, or "not found"]
sector_label: [transport | water | agriculture | enrm | ews_hydromet | other | uncertain]
sector_confidence: [high | medium | low]
pdo_names_sector: [true/false]
ews_is_primary: [true/false: true only if early warning or hydromet services are the PDO or most of the financing]
cerc_only: [true/false: true only if the whole operation is a contingent emergency response or a Cat DDO]
fcv_setting: [active_conflict | criminal_violence | post_conflict | institutional_fragility | displacement_hosting | any]
sector_shares: [sector=share pairs from the cost table, e.g. "water=0.62; agriculture=0.31", excluding project management and CERC components; or "not stated"]
features:
- [feature_id] | share=[0.00-1.00 or n/a] | named=[true/false] | evidence=[true/false] | country=[country or n/a] | page=[page or n/a]
%%%SECTOR_FACTS_END%%%

SECTOR_FACTS rules: enrm = environment, natural resources, forests, fisheries or landscapes. List at most 8 features, only
from: rural_feeder_roads (roads, bridges, corridors), civil_works_contracts (large works contracts), water_points_wash
(water points, boreholes, piped supply, WASH), bulk_water_irrigation (dams, abstraction, irrigation, groundwater
pumping), agri_inputs_pastoral (inputs, matching grants, livestock, pastoral or value-chain support),
food_security_reserves (food reserves, food-crisis monitoring), nrm_landscape_forest (protected areas, forests,
landscapes, fisheries, restoration, mining areas), land_acquisition_tenure (land take, titling, resettlement, tenure
reform), local_funds_cdd (community or local-government grants and funds), ews_hydromet (early warning, hydromet,
hazard or conflict data systems), tariff_reform (tariff increases, metering, subsidy or cost-recovery reform financed
or required by the project). share = that feature's share of total financing where the cost table states it.
named = true if it is a named component or subcomponent, a PDO element or a results indicator. evidence = true only if
the document itself describes the conflict-relevant context for that feature (for example competing user groups,
insecurity, displacement, contested land or authority), not merely the asset. country = the country for multi-country
operations. Use fcv_setting = any when the document describes no fragility, conflict or violence context for the
project area. Do not guess: use n/a, false or "not stated" when the document does not say.
"""


# --- Stage 1 ---------------------------------------------------------------------------------------------

def _bool(v: str) -> bool:
    return str(v).strip().lower() in ("true", "yes", "1")


def _share(v: str) -> float | None:
    try:
        x = float(str(v).strip().rstrip("%"))
    except ValueError:
        return None
    x = x / 100 if x > 1 else x
    return x if 0 <= x <= 1 else None


def extract_sector_facts(stage1_output: str, document_text: str = "", prior_actions: list | None = None,
                         multi_country: bool = False) -> dict[str, Any]:
    """Parse the Stage 1 %%%SECTOR_FACTS%%% block and the datasheet. Always returns a JSON-safe dict.
    Prior actions and country scope are stored with the facts for re-use at Stages 2 and 3."""
    pa = parse_practice_areas(document_text or "")
    facts: dict[str, Any] = {
        "prior_actions": [str(p) for p in (prior_actions or [])][:20], "multi_country": bool(multi_country),
        "error": True, "pa_lead_parsed": pa.lead, "pa_contributing": list(pa.contributing),
        "cover_gps": list(pa.cover_gps), "pa_lead_model": None, "sector_label": None, "sector_confidence": "",
        "pdo_names_sector": False, "ews_is_primary": False, "cerc_only": False, "fcv_setting": "any",
        "sector_shares": {}, "features": [],
    }
    src = stage1_output or ""
    a = src.find("%%%SECTOR_FACTS_START%%%")
    b = src.find("%%%SECTOR_FACTS_END%%%", a + 1) if a >= 0 else -1
    if a < 0 or b < 0:
        return facts
    facts["error"] = False
    for line in src[a + len("%%%SECTOR_FACTS_START%%%"):b].splitlines():
        line = line.strip()
        if line.startswith("-"):
            parts = [p.strip() for p in line.lstrip("- ").split("|")]
            feat = parts[0].strip("[] ").lower()
            if feat not in PROJECT_FEATURES or len(facts["features"]) >= 8:
                continue
            kv = dict(p.split("=", 1) for p in parts[1:] if "=" in p)
            kv = {k.strip().lower(): v.strip() for k, v in kv.items()}
            na = ("", "n/a", "na", "none")
            facts["features"].append({
                "feature": feat, "financing_share": _share(kv.get("share", "")),
                "named": _bool(kv.get("named", "")), "mechanism_evidence": _bool(kv.get("evidence", "")),
                "country": None if kv.get("country", "").lower() in na else kv.get("country"),
                "page": None if kv.get("page", "").lower() in na else kv.get("page"),
            })
            continue
        if ":" not in line:
            continue
        key, val = (s.strip() for s in line.split(":", 1))
        key = key.lower()
        if key == "practice_area_lead":
            names = _names_in(val)
            facts["pa_lead_model"] = names[0] if names else None
        elif key == "sector_label":
            facts["sector_label"] = val.lower() if val.lower() in PILOT_SECTORS else None
        elif key == "sector_confidence":
            facts["sector_confidence"] = val.lower() if val.lower() in ("high", "medium", "low") else ""
        elif key in ("pdo_names_sector", "ews_is_primary", "cerc_only"):
            facts[key] = _bool(val)
        elif key == "fcv_setting":
            facts["fcv_setting"] = val.lower() if val.lower() in FCV_SETTINGS else "any"
        elif key == "sector_shares":
            for pair in re.split(r"[;,]", val):
                if "=" in pair:
                    k, v = (s.strip() for s in pair.split("=", 1))
                    if k.lower() in PILOT_SECTORS and _share(v) is not None:
                        facts["sector_shares"][k.lower()] = _share(v)
    return facts


def context_from(flags: dict | None, fcv_setting: str) -> frozenset[str]:
    """Context conditions some cards require, from Stage 1 context flags and the FCV setting."""
    flags = flags if isinstance(flags, dict) else {}
    ctx = set()
    if flags.get("displacement_context") or fcv_setting == "displacement_hosting":
        ctx.add("displacement")
    if flags.get("security_risks_noted") or flags.get("armed_forces_mentioned")             or fcv_setting in ("active_conflict", "criminal_violence"):
        ctx.add("insecurity")
    if flags.get("tpi_mentioned"):
        ctx.add("parallel_delivery")
    return frozenset(ctx)


def _project_facts(facts: dict, instrument: str, prior_actions: list | None, multi_country: bool,
                   context_flags: dict | None = None) -> ProjectFacts:
    feats = []
    for f in facts.get("features") or []:
        if isinstance(f, dict) and f.get("feature") in PROJECT_FEATURES:
            feats.append(FeatureEvidence(
                feature=f["feature"], financing_share=f.get("financing_share"), named=bool(f.get("named")),
                mechanism_evidence=bool(f.get("mechanism_evidence")), country=f.get("country"), page=f.get("page")))
    return ProjectFacts(
        instrument=instrument or "", cerc_only=bool(facts.get("cerc_only")), multi_country=bool(multi_country),
        pa_lead_parsed=facts.get("pa_lead_parsed"), pa_lead_model=facts.get("pa_lead_model"),
        pa_contributing=tuple(facts.get("pa_contributing") or ()), cover_gps=tuple(facts.get("cover_gps") or ()),
        stage1_sector=facts.get("sector_label"), stage1_confidence=facts.get("sector_confidence") or "",
        pdo_names_sector=bool(facts.get("pdo_names_sector")),
        sector_financing_share=dict(facts.get("sector_shares") or {}),
        ews_is_primary=bool(facts.get("ews_is_primary")), fcv_setting=facts.get("fcv_setting") or "any",
        features=tuple(feats), prior_actions=tuple(str(p) for p in (prior_actions or [])),
        context=context_from(context_flags if context_flags is not None else facts.get("context_flags"),
                             facts.get("fcv_setting") or "any"),
    )


def route_from_facts(facts: dict | None, instrument: str = "", prior_actions: list | None = None,
                     multi_country: bool = False, disabled: bool = False, disabled_cards: list | None = None,
                     cards: CardSet | None = None, context_flags: dict | None = None) -> dict[str, Any]:
    """Deterministic eligibility, serialised for the done event and for re-use at Stages 2 and 3."""
    cards = cards or load_cards()
    empty = {"sectors": [], "sector_reason": "", "eligible": [], "rejected": [], "trace": [], "reason_line": "",
             "disabled": bool(disabled), "card_version": cards.version}
    if not isinstance(facts, dict) or disabled:
        return empty
    # Facts saved at Stage 1 carry the prior actions and country scope, so later stages need no extra echo.
    if prior_actions is None:
        prior_actions = facts.get("prior_actions") or []
    multi_country = bool(multi_country or facts.get("multi_country"))
    res = route(_project_facts(facts, instrument, prior_actions, multi_country, context_flags), cards)
    off = set(disabled_cards or [])
    by_id = cards.by_id()
    eligible = [{**e, "mechanism": by_id[e["card_id"]].mechanism} for e in res.eligible if e["card_id"] not in off]
    rejected = res.rejected + [{"card_id": c, "reason": "switched off by the user"} for c in off]
    return {**empty, "sectors": res.sectors, "sector_reason": res.sector_reason, "eligible": eligible,
            "rejected": rejected, "trace": res.trace, "reason_line": _reason_line(res.sectors, res.sector_reason,
                                                                                  eligible)}


def _reason_line(sectors: list, sector_reason: str, eligible: list) -> str:
    if not sectors and not eligible:
        return ""
    bits = []
    if sectors:
        why = "lead Practice Area" if "lead Practice Area" in sector_reason else (
            "cover Global Practice" if "cover" in sector_reason else "Stage 1 classification")
        bits.append(", ".join(SECTOR_LABELS[s] for s in sectors) + f" ({why})")
    routes = {e["route"] for e in eligible}
    if "feature" in routes:
        bits.append("material project features")
    if "dpf_prior_action" in routes:
        bits.append("prior actions")
    return f"Sector lens: {'; '.join(bits)}. {len(eligible)} sector card(s) may be considered at Stage 2."


# --- Stage 2 ---------------------------------------------------------------------------------------------

def build_stage2_card_slice(routing: dict | None, cards: CardSet | None = None) -> str:
    """Prompt slice for the eligible cards, or '' when none are eligible (then no block is expected)."""
    if not isinstance(routing, dict) or routing.get("disabled") or not routing.get("eligible"):
        return ""
    by_id = (cards or load_cards()).by_id()
    lines = [
        "\n\n--- SECTOR MECHANISM CARDS (deterministically eligible for this project; advisory) ---",
        ("These cards describe specific ways this kind of project can create or worsen FCV risk. They are eligible "
        "because of the reason given; that does not mean the risk exists. Select AT MOST 3 cards, and only where the "
        "document gives page-anchored evidence that the card's conditions hold. Selecting none is a complete and "
        "valid answer. Stop when the next card would only restate a core Do No Harm or OST finding."),
        ("Write each finding in 1-2 advisory sentences in the project's own terms (component, place, groups). Ask "
        "whether the document identifies and manages the risk; do not assert that it exists, do not name armed, "
        "political or criminal actors unless the document does, and never use 'must' or 'required'."),
    ]
    for e in routing["eligible"]:
        c = by_id.get(e["card_id"])
        if not c:
            continue
        lines.append(f"\n[{c.id}] {c.mechanism} (eligible: {e['reason']})\nQuestion: {c.prompt_text}\n"
                     f"Sufficient evidence: {c.sufficient_evidence}\nWhat to look for: {c.look_for}\n"
                     f"Core items: {', '.join(c.core_mappings)}")
    lines.append(
        "\nAfter your analysis, append exactly one block (use {\"cards\": []} when no card applies):\n"
        "%%%SECTOR_CARDS_START%%%\n"
        '{"cards": [{"card_id": "mc-00", "applies_because": "<fact from the document>", "page_ref": "<page>", '
        '"finding": "<1-2 advisory sentences>", "beyond_core": "<what the mapped core item would miss>"}]}\n'
        "%%%SECTOR_CARDS_END%%%")
    return "\n".join(lines)


def extract_sector_cards(stage2_output: str, routing: dict | None) -> list[dict]:
    """Validated card findings from Stage 2. Missing or malformed block -> [] (never a recovery call)."""
    if not isinstance(routing, dict) or routing.get("disabled"):
        return []
    allowed = {e["card_id"] for e in routing.get("eligible") or []}
    src = stage2_output or ""
    a = src.find("%%%SECTOR_CARDS_START%%%")
    b = src.find("%%%SECTOR_CARDS_END%%%", a + 1) if a >= 0 else -1
    if a < 0 or b < 0 or not allowed:
        return []
    try:
        data = json.loads(src[a + len("%%%SECTOR_CARDS_START%%%"):b].strip())
    except (json.JSONDecodeError, ValueError):
        return []
    out, seen = [], set()
    for item in (data.get("cards") if isinstance(data, dict) else None) or []:
        if not isinstance(item, dict):
            continue
        cid = str(item.get("card_id", "")).strip().lower()
        finding = " ".join(str(item.get("finding", "")).split())
        page = str(item.get("page_ref", "")).strip()
        if cid not in allowed or cid in seen or not finding or not page or re.search(r"\bmust\b", finding, re.IGNORECASE):
            continue
        seen.add(cid)
        out.append({"card_id": cid, "finding": finding, "page_ref": page,
                    "applies_because": " ".join(str(item.get("applies_because", "")).split()),
                    "beyond_core": " ".join(str(item.get("beyond_core", "")).split())})
        if len(out) == MAX_SELECTED:
            break
    return out


def strip_sector_blocks(text: str) -> str:
    """Remove the two sector delimiter blocks from display text (history keeps them)."""
    out = text or ""
    for tag in ("SECTOR_FACTS", "SECTOR_CARDS"):
        while True:
            a = out.find(f"%%%{tag}_START%%%")
            if a < 0:
                break
            b = out.find(f"%%%{tag}_END%%%", a)
            out = out[:a] if b < 0 else out[:a] + out[b + len(f"%%%{tag}_END%%%"):]
    return out


# --- Stage 3 ---------------------------------------------------------------------------------------------

def build_stage3_card_slice(findings: list[dict]) -> str:
    if not findings:
        return ""
    lines = ["\n\n--- SECTOR CARD FINDINGS FROM STAGE 2 (advisory) ---",
             ("Where one of these findings strengthens an existing priority, reflect it in that priority and add the "
             "card id to that priority's optional \"sector_cards\" list (e.g. \"sector_cards\": [\"mc-03\"]). Do not "
             "create a priority only to carry a sector finding unless it is among the most important issues. Do not "
             "repeat findings verbatim.")]
    lines += [f"[{f['card_id']}] {f['finding']} (p.{f['page_ref']})" for f in findings]
    return "\n".join(lines)


def apply_sector_cards(priorities: list[dict], findings: list[dict]) -> list[dict]:
    """Keep only selected card ids on each priority (in place); returns the priorities."""
    allowed = {f["card_id"] for f in findings}
    for p in priorities or []:
        raw = p.get("sector_cards") if isinstance(p, dict) else None
        if isinstance(p, dict):
            p["sector_cards"] = [c for c in dict.fromkeys(str(x).strip().lower() for x in (raw or [])
                                                          if isinstance(raw, list)) if c in allowed]
    return priorities


def build_readout_fields(routing: dict | None, findings: list[dict], priorities: list[dict],
                         cards: CardSet | None = None) -> dict[str, Any]:
    """Option C: one provenance line plus at most 2 additional considerations (empty when nothing applied)."""
    empty = {"sector_provenance": "", "sector_additional": []}
    if not isinstance(routing, dict) or routing.get("disabled") or not routing.get("eligible"):
        return empty
    by_id = (cards or load_cards()).by_id()
    used: dict[str, list[int]] = {}
    for i, p in enumerate(priorities or [], 1):
        for cid in (p.get("sector_cards") or []) if isinstance(p, dict) else []:
            used.setdefault(cid, []).append(i)
    bits = []
    if routing.get("sectors"):
        bits.append(", ".join(SECTOR_LABELS[s] for s in routing["sectors"]) + " (lead Practice Area)"
                    if "lead Practice Area" in routing.get("sector_reason", "")
                    else ", ".join(SECTOR_LABELS[s] for s in routing["sectors"]))
    feats = sorted({e["reason"].split("material feature ", 1)[1] for e in routing["eligible"]
                    if e["route"] == "feature" and "material feature " in e["reason"]})
    if feats:
        bits.append("; ".join(_pretty_feature(f) for f in feats[:2]))
    if any(e["route"] == "dpf_prior_action" for e in routing["eligible"]):
        bits.append("prior actions")
    line = "Sector lens: " + "; ".join(bits) + "."
    shaped = sorted({i for ids in used.values() for i in ids})
    if shaped:
        line += " Reflected in " + ("priority " if len(shaped) == 1 else "priorities ") + \
                ", ".join(str(i) for i in shaped[:-1]) + (" and " if len(shaped) > 1 else "") + str(shaped[-1]) + "."
    additional = []
    for f in findings:
        if f["card_id"] in used or len(additional) == MAX_ADDITIONAL:
            continue
        c = by_id.get(f["card_id"])
        additional.append({"card_id": f["card_id"], "mechanism": c.mechanism if c else "", "text": f["finding"],
                           "page_ref": f["page_ref"], "sources": list(c.user_citations[:2]) if c else []})
    if not findings:
        line += " No additional sector considerations were identified."
    return {"sector_provenance": line, "sector_additional": additional}


def _pretty_feature(reason_tail: str) -> str:
    # "water_points_wash (14% of financing), Chad" -> "water points and supply (14% of financing), Chad"
    key = reason_tail.split(" ", 1)[0]
    return FEATURE_LABELS.get(key, key) + reason_tail[len(key):]
