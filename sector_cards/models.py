"""Mechanism-card schema and loader (design v3, 2026-11-27).

A card describes one way a project can create or worsen FCV risk, with sector-specific cues and
cited sources. Cards are advisory prompts for Stage 2; they never assert that a risk exists.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

CARDS_PATH = Path(__file__).with_name("cards.yaml")

PILOT_SECTORS = ("transport", "water", "agriculture", "enrm", "ews_hydromet")
ROUTES = ("sector", "feature", "dpf_prior_action")
FEATURES = (
    "rural_feeder_roads", "civil_works_contracts", "water_points_wash", "bulk_water_irrigation",
    "agri_inputs_pastoral", "food_security_reserves", "nrm_landscape_forest", "land_acquisition_tenure",
    "local_funds_cdd", "ews_hydromet",
    # DPF prior-action reform types
    "pa_tariff_subsidy_reform", "pa_land_tenure_reform", "pa_resource_revenue_transfers",
    "pa_fossil_extractive_phaseout",
)
SR_TYPES = ("S", "R", "S+R")
_CORE_RE = re.compile(r"^(ost:(?:[1-9]|1[0-2])|dnh:[1-9]|shift:[A-D])$")
# Wording rule: cards ask whether the document identifies and manages a risk; never a requirement.
_FORBIDDEN_WORDS = re.compile(r"\b(must|required|shall|mandatory)\b", re.IGNORECASE)
MAX_CARD_TOKENS = 260


class CardError(ValueError):
    """Raised when cards.yaml violates the card schema."""


@dataclass(frozen=True)
class CardSource:
    citation: str
    kind: str  # wbg_public | external_public | internal
    cite_to_user: bool


@dataclass(frozen=True)
class MechanismCard:
    id: str
    mechanism: str
    routes: tuple[str, ...]
    sectors: tuple[str, ...]
    features: tuple[str, ...]
    sr_type: str
    core_mappings: tuple[str, ...]
    applicability: str
    sufficient_evidence: str
    look_for: str
    prompt_text: str
    sources: tuple[CardSource, ...]
    member_questions: tuple[str, ...] = ()
    evidence_note: str = ""

    @property
    def user_citations(self) -> tuple[str, ...]:
        return tuple(s.citation for s in self.sources if s.cite_to_user and s.kind != "internal")

    @property
    def est_tokens(self) -> int:
        # Same conservative approximation the lens composer uses.
        return len(f"{self.prompt_text} {self.look_for} {self.sufficient_evidence}") // 4


@dataclass(frozen=True)
class CardSet:
    version: str
    cards: tuple[MechanismCard, ...] = field(default_factory=tuple)

    def by_id(self) -> dict[str, MechanismCard]:
        return {c.id: c for c in self.cards}


def _tuple(value, name: str, card_id: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise CardError(f"{card_id}: '{name}' must be a list of strings")
    return tuple(v.strip() for v in value)


def _parse_card(raw: dict) -> MechanismCard:
    if not isinstance(raw, dict):
        raise CardError("each card must be a mapping")
    cid = str(raw.get("id", "")).strip()
    if not re.fullmatch(r"mc-\d{2}", cid):
        raise CardError(f"invalid card id {cid!r}")
    routes = _tuple(raw.get("routes"), "routes", cid)
    sectors = _tuple(raw.get("sectors", []), "sectors", cid)
    features = _tuple(raw.get("features", []), "features", cid)
    core = _tuple(raw.get("core_mappings"), "core_mappings", cid)
    bad = [r for r in routes if r not in ROUTES] + [s for s in sectors if s not in PILOT_SECTORS] \
        + [f for f in features if f not in FEATURES] + [m for m in core if not _CORE_RE.match(m)]
    if bad:
        raise CardError(f"{cid}: unknown values {bad}")
    if not routes or not core:
        raise CardError(f"{cid}: routes and core_mappings are required")
    if "sector" in routes and not sectors:
        raise CardError(f"{cid}: a sector-routed card needs sectors")
    if "dpf_prior_action" in routes and not any(f.startswith("pa_") for f in features):
        raise CardError(f"{cid}: the DPF route needs a pa_* feature")
    sr = str(raw.get("sr_type", ""))
    if sr not in SR_TYPES:
        raise CardError(f"{cid}: sr_type must be one of {SR_TYPES}")
    text = {k: " ".join(str(raw.get(k, "")).split()) for k in
            ("mechanism", "applicability", "sufficient_evidence", "look_for", "prompt_text")}
    if not all(text.values()):
        raise CardError(f"{cid}: empty text field")
    if _FORBIDDEN_WORDS.search(text["prompt_text"]):
        raise CardError(f"{cid}: prompt_text breaks the advisory wording rule")
    srcs = []
    for s in raw.get("sources") or []:
        kind = s.get("kind", "")
        if kind not in ("wbg_public", "external_public", "internal"):
            raise CardError(f"{cid}: bad source kind {kind!r}")
        if kind == "internal" and s.get("cite_to_user"):
            raise CardError(f"{cid}: internal sources can never be cited to users")
        srcs.append(CardSource(str(s["citation"]).strip(), kind, bool(s.get("cite_to_user"))))
    if not any(s.cite_to_user for s in srcs):
        raise CardError(f"{cid}: needs at least one source citable to users")
    card = MechanismCard(
        id=cid, mechanism=text["mechanism"], routes=routes, sectors=sectors, features=features, sr_type=sr,
        core_mappings=core, applicability=text["applicability"], sufficient_evidence=text["sufficient_evidence"],
        look_for=text["look_for"], prompt_text=text["prompt_text"], sources=tuple(srcs),
        member_questions=tuple(raw.get("member_questions") or ()), evidence_note=str(raw.get("evidence_note", "")),
    )
    if card.est_tokens > MAX_CARD_TOKENS:
        raise CardError(f"{cid}: {card.est_tokens} tokens exceeds {MAX_CARD_TOKENS}")
    return card


def parse_cards(doc: dict) -> CardSet:
    if not isinstance(doc, dict) or not isinstance(doc.get("cards"), list):
        raise CardError("cards.yaml must contain a 'cards' list")
    cards = tuple(_parse_card(c) for c in doc["cards"])
    ids = [c.id for c in cards]
    if len(ids) != len(set(ids)):
        raise CardError("duplicate card ids")
    return CardSet(version=str(doc.get("version", "")), cards=cards)


@lru_cache(maxsize=1)
def load_cards(path: str | None = None) -> CardSet:
    p = Path(path) if path else CARDS_PATH
    return parse_cards(yaml.safe_load(p.read_text(encoding="utf-8")))
