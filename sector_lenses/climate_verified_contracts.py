"""Stable contracts for the automatic Climate-FCV verified pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum


CLIMATE_VERIFIED_SCHEMA_VERSION = "climate-verified-v2"
DEFAULT_FACT_LIMIT = 60
HARD_FACT_LIMIT = 100


class EpistemicStatus(str, Enum):
    EXPLICIT = "explicit"
    CONFIRMED_ABSENCE = "confirmed_absence"
    NOT_FOUND = "not_found"
    NOT_YET_SPECIFIED = "not_yet_specified"
    CONTRADICTORY = "contradictory"
    NOT_APPLICABLE = "not_applicable"


class ExcerptMatchStatus(str, Enum):
    VERBATIM = "verbatim"
    NORMALIZED_EXACT = "normalized_exact"
    BOUNDED_FUZZY = "bounded_fuzzy"
    UNRESOLVED = "unresolved"


class EvidenceClass(str, Enum):
    PROJECT = "project"
    PROJECT_PACKAGE = "project_package"
    COUNTRY = "country"
    GUIDANCE = "guidance"
    INFERENCE = "inference"


@dataclass(frozen=True)
class CallBudget:
    input_tokens: int
    output_tokens: int
    timeout_seconds: int


CALL_BUDGETS = {
    "fact_extraction": CallBudget(24_000, 10_000, 150),
    "bounded_analysis": CallBudget(20_000, 6_000, 180),
    "judgment_review": CallBudget(12_000, 2_000, 60),
    "recommendation_compiler": CallBudget(16_000, 5_000, 240),
    "conditional_review": CallBudget(12_000, 2_500, 120),
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    object_id: str | None
    blocking: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
