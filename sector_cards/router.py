"""Deterministic eligibility for mechanism cards (design v3, sections 3-4a).

The router decides which cards the Stage 2 model may consider. It never selects findings: the model picks
0-3 of the eligible cards with page evidence. Every decision is recorded in the trace.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import CardSet, MechanismCard

MATERIAL_SHARE = 0.10          # feature route: share of financing that counts as material
SECOND_SECTOR_SHARE = 0.30     # second sector: attributable financing share
MAX_SECTORS = 2
MAX_ELIGIBLE = 6               # keeps Stage 2 within the ~1,000-token card budget
HIGH = "high"

# Lead Practice Area -> pilot sector. EWS-type leads need the EWS check (ews_is_primary).
PA_TO_SECTOR = {
    "Transport": "transport",
    "Water": "water",
    "Agriculture and Food": "agriculture",
    "Environment, Natural Resources & the Blue Economy": "enrm",
    "Climate Change": "enrm",
}
EWS_LEADS = ("Urban, Resilience and Land", "Social, Urban, Rural and Resilience")

# DPF prior-action reform types (design v3, section 4a).
PRIOR_ACTION_PATTERNS = {
    "pa_tariff_subsidy_reform": r"tariff|subsid|cost[- ]recovery|meter",
    "pa_land_tenure_reform": r"land (?:registration|titl|tenure|administration|law|code)|titling|expropriat|concession",
    "pa_resource_revenue_transfers": r"revenue[- ]sharing|royalt|extractive (?:fund|revenue)|fiscal transfer|"
                                     r"intergovernmental transfer|transfers to (?:local|subnational|municipal)",
    "pa_fossil_extractive_phaseout": r"fuel subsid|fossil|coal|charcoal|phase[- ]?(?:out|down)",
}


@dataclass(frozen=True)
class FeatureEvidence:
    feature: str
    financing_share: float | None = None   # 0-1 of total financing, if stated
    named: bool = False                     # named subcomponent, PDO element or result indicator
    mechanism_evidence: bool = False        # document gives direct evidence of the mechanism
    country: str | None = None              # required for multi-country operations
    page: str | None = None


@dataclass(frozen=True)
class ProjectFacts:
    instrument: str = ""                    # IPF / PforR / DPF / MPA ...
    cerc_only: bool = False                 # CERC-only or contingent instrument (e.g. Cat DDO)
    multi_country: bool = False
    pa_lead_parsed: str | None = None       # deterministic datasheet parse
    pa_lead_model: str | None = None        # Stage 1 model reading of the same field (optional)
    pa_contributing: tuple[str, ...] = ()
    cover_gps: tuple[str, ...] = ()
    stage1_sector: str | None = None        # controlled label from Stage 1
    stage1_confidence: str = ""
    pdo_names_sector: bool = False
    sector_financing_share: dict[str, float | None] = field(default_factory=dict)  # PIU/CERC excluded
    ews_is_primary: bool = False            # early warning / hydromet is the PDO or most of the financing
    fcv_setting: str = "any"                # 'any' or a specific setting (active_conflict, criminal_violence, ...)
    features: tuple[FeatureEvidence, ...] = ()
    prior_actions: tuple[str, ...] = ()


@dataclass
class RoutingResult:
    sectors: list[str] = field(default_factory=list)
    sector_reason: str = ""
    eligible: list[dict] = field(default_factory=list)   # {card_id, route, reason, score}
    rejected: list[dict] = field(default_factory=list)   # {card_id, reason}
    trace: list[str] = field(default_factory=list)

    @property
    def eligible_ids(self) -> list[str]:
        return [e["card_id"] for e in self.eligible]


def _lead_to_sector(lead: str | None, ews_is_primary: bool) -> str | None:
    if not lead:
        return None
    if lead in EWS_LEADS:
        return "ews_hydromet" if ews_is_primary else None
    sector = PA_TO_SECTOR.get(lead)
    if sector == "enrm" and ews_is_primary:
        return "ews_hydromet"   # EWS/hydromet takes precedence over the broader ENRM label
    return sector


def resolve_sectors(f: ProjectFacts) -> tuple[list[str], str, list[str]]:
    """Apply the decision table. Returns (sectors, reason, trace)."""
    trace: list[str] = []
    instrument = (f.instrument or "").upper()
    if f.cerc_only:
        return [], "CERC-only or contingent instrument: nothing fires", ["step5: cerc_only"]
    if instrument == "DPF":
        return [], "DPF: no sector (prior-action route only)", ["step5: dpf"]
    if f.pa_lead_parsed and f.pa_lead_model and f.pa_lead_parsed != f.pa_lead_model:
        return [], "datasheet parse and model disagree on the lead Practice Area: nothing fires", [
            f"disagree: parsed={f.pa_lead_parsed!r} model={f.pa_lead_model!r}"]

    lead = f.pa_lead_parsed
    if lead:  # steps 1-2
        primary = _lead_to_sector(lead, f.ews_is_primary)
        if not primary:
            return [], f"lead Practice Area '{lead}' is not a pilot sector", ["step2"]
        sectors, reason = [primary], f"{primary}: lead Practice Area '{lead}'"
        trace.append("step1")
        for contrib in f.pa_contributing:  # step 4, only via step 1
            second = _lead_to_sector(contrib, False)
            share = f.sector_financing_share.get(second or "", None)
            if second and second not in sectors and share is not None and share >= SECOND_SECTOR_SHARE \
                    and f.stage1_confidence == HIGH:
                sectors.append(second)
                reason += f"; {second}: contributing Practice Area with {share:.0%} attributable financing"
                trace.append(f"step4: {second}")
                break
        return sectors[:MAX_SECTORS], reason, trace

    # step 3: single-GP cover line, else the Stage 1 route
    if len(f.cover_gps) == 1:
        sector = _lead_to_sector(f.cover_gps[0], f.ews_is_primary)
        if sector:
            return [sector], f"{sector}: single Global Practice on the cover", ["step3: cover"]
        return [], f"cover Global Practice '{f.cover_gps[0]}' is not a pilot sector", ["step3: cover non-pilot"]
    s = f.stage1_sector
    share = f.sector_financing_share.get(s or "", None)
    if s in PA_TO_SECTOR.values() or s == "ews_hydromet":
        if f.stage1_confidence == HIGH and f.pdo_names_sector and share is not None and share > 0.5:
            return [s], f"{s}: Stage 1 classification (high confidence, PDO, {share:.0%} of financing)", ["step3: stage1"]
        return [], "Stage 1 route did not meet all three tests", ["step3: stage1 failed"]
    return [], "no datasheet signal and no pilot-sector classification", ["step3: none"]


def _material(fe: FeatureEvidence) -> bool:
    return fe.named or (fe.financing_share is not None and fe.financing_share >= MATERIAL_SHARE)


def _prior_action_features(actions: tuple[str, ...]) -> set[str]:
    found = set()
    for a in actions:
        for feat, pat in PRIOR_ACTION_PATTERNS.items():
            if re.search(pat, a or "", re.IGNORECASE):
                found.add(feat)
    return found


def route(facts: ProjectFacts, cards: CardSet) -> RoutingResult:
    res = RoutingResult()
    res.sectors, res.sector_reason, res.trace = resolve_sectors(facts)
    if facts.cerc_only:
        return res
    fragile = (facts.fcv_setting or "any") != "any"
    by_feature: dict[str, list[FeatureEvidence]] = {}
    for fe in facts.features:
        by_feature.setdefault(fe.feature, []).append(fe)
    dpf = (facts.instrument or "").upper() == "DPF"
    pa_feats = _prior_action_features(facts.prior_actions) if dpf else set()

    candidates: list[dict] = []
    for card in cards.cards:
        if dpf:
            hit = [f for f in card.features if f in pa_feats]
            if "dpf_prior_action" in card.routes and hit and fragile:
                candidates.append({"card_id": card.id, "route": "dpf_prior_action",
                                       "reason": f"prior action of type {hit[0]}", "score": 2.0})
            elif "dpf_prior_action" in card.routes and hit:
                res.rejected.append({"card_id": card.id, "reason": "prior action found but FCV setting is 'any'"})
            continue
        decision = _eligible_project_card(card, facts, by_feature, res.sectors, fragile)
        if decision.get("route"):
            candidates.append(decision)
        elif decision.get("reason"):
            res.rejected.append(decision)

    candidates.sort(key=lambda d: (-d["score"], d["card_id"]))
    res.eligible = candidates[:MAX_ELIGIBLE]
    for d in candidates[MAX_ELIGIBLE:]:
        res.rejected.append({"card_id": d["card_id"], "reason": f"over the {MAX_ELIGIBLE}-card budget (score {d['score']:.2f})"})
    res.trace.append(f"eligible={res.eligible_ids}")
    return res


def _eligible_project_card(card: MechanismCard, f: ProjectFacts, by_feature, sectors, fragile) -> dict:
    if card.routes == ("dpf_prior_action",):
        return {}
    present = [fe for feat in card.features for fe in by_feature.get(feat, [])]
    if f.multi_country:
        present = [fe for fe in present if fe.country]  # findings must be scoped to a country
    in_sector = bool(set(card.sectors) & set(sectors))
    if not present:
        return {"card_id": card.id, "reason": "no relevant feature in the document"} if in_sector else {}
    best = max(present, key=lambda fe: (fe.financing_share or 0.0, fe.named, fe.mechanism_evidence))
    score = (best.financing_share or 0.0) + (0.5 if best.named else 0.0) + (0.5 if best.mechanism_evidence else 0.0)
    if in_sector and "sector" in card.routes:
        # A fired sector lowers the materiality bar but the feature must still be present.
        return {"card_id": card.id, "route": "sector", "score": score + 1.0,
                    "reason": f"sector {min(set(card.sectors) & set(sectors))}; feature {best.feature}"
                           + (f" (p.{best.page})" if best.page else "")}
    if "feature" not in card.routes:
        return {}
    if not fragile:
        return {"card_id": card.id, "reason": f"feature {best.feature} present but FCV setting is 'any'"}
    material = [fe for fe in present if _material(fe) and fe.mechanism_evidence]
    if not material:
        return {"card_id": card.id, "reason": f"feature {best.feature} not material or no mechanism evidence"}
    m = max(material, key=lambda fe: (fe.financing_share or 0.0, fe.named))
    share = f"{m.financing_share:.0%} of financing" if m.financing_share is not None else "named in design"
    return {"card_id": card.id, "route": "feature", "score": score,
                "reason": f"material feature {m.feature} ({share})" + (f", {m.country}" if m.country else "")}
