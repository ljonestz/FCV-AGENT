"""Mechanism cards for sector content in the FCV screener (design v3, 2026-11-27).

Not yet wired into the stage pipeline: this package holds the card schema, the datasheet parser and the
deterministic eligibility router, with tests. Prompt, route and readout wiring follow in later commits.
"""
from .datasheet import PracticeAreas, parse_practice_areas
from .models import CardError, CardSet, MechanismCard, load_cards, parse_cards
from .router import FeatureEvidence, ProjectFacts, RoutingResult, resolve_sectors, route

__all__ = [
    "CardError", "CardSet", "FeatureEvidence", "MechanismCard", "PracticeAreas", "ProjectFacts", "RoutingResult",
    "load_cards", "parse_cards", "parse_practice_areas", "resolve_sectors", "route",
]
