"""Deterministic parse of the World Bank datasheet's Practice Area fields (design v3, section 3).

Extracted PDF text runs fields together, e.g. "Practice Area (Lead) Contributing Practice Areas Water
Environment, Natural Resources & the Blue Economy Climate Change and Disaster Screening ...". We match
against a fixed list of Practice Area names (plus aliases for retired names) instead of relying on layout:
the first name after the label is the lead, the rest up to the stop label are contributing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Canonical names (current) and aliases -> canonical.
_CANON = (
    "Agriculture and Food", "Climate Change", "Digital Development", "Education", "Energy & Extractives",
    "Environment, Natural Resources & the Blue Economy", "Finance, Competitiveness and Innovation",
    "Fragile, Conflict & Violence", "Gender", "Governance", "Health, Nutrition & Population",
    "Infrastructure, PPPs & Guarantees", "Jobs", "Macroeconomics, Trade and Investment", "Poverty and Equity",
    "Social Protection & Jobs", "Social Sustainability and Inclusion", "Transport",
    "Urban, Resilience and Land", "Water", "Other",
)
_ALIASES = {
    "Social, Urban, Rural and Resilience": "Social, Urban, Rural and Resilience",  # retired, kept distinct
    "Urban, Disaster Risk Management, Resilience and Land": "Urban, Resilience and Land",
    "Environment, Natural Resources and the Blue Economy": "Environment, Natural Resources & the Blue Economy",
    "Environment & Natural Resources": "Environment, Natural Resources & the Blue Economy",
    "Energy and Extractives": "Energy & Extractives",
    "Health, Nutrition and Population": "Health, Nutrition & Population",
    "Social Protection and Jobs": "Social Protection & Jobs",
    "Fragile, Conflict and Violence": "Fragile, Conflict & Violence",
    "Agriculture": "Agriculture and Food",
}
_ALL = sorted(set(_CANON) | set(_ALIASES), key=len, reverse=True)  # longest first
_NAME_RE = re.compile("|".join(re.escape(n) for n in _ALL))
_STOP_RE = re.compile(r"Climate Change and Disaster Screening|OVERALL RISK RATING|SYSTEMATIC OPERATIONS|"
                      r"Financing Instrument|Borrower|Proposed Development Objective", re.IGNORECASE)
_LABEL = "Practice Area (Lead)"
_GEF_RE = re.compile(r"GEF Focal Area[^.]{0,80}", re.IGNORECASE)


def canonical(name: str) -> str:
    return _ALIASES.get(name, name)


@dataclass(frozen=True)
class PracticeAreas:
    lead: str | None = None
    contributing: tuple[str, ...] = ()
    cover_gps: tuple[str, ...] = ()
    found_label: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


def _names_in(segment: str) -> list[str]:
    segment = _GEF_RE.sub(" ", segment)
    out: list[str] = []
    for m in _NAME_RE.finditer(segment):
        c = canonical(m.group(0))
        if c not in out:
            out.append(c)
    return out


def _cover_gps(head: str) -> tuple[str, ...]:
    found = []
    for m in re.finditer(r"([A-Z][A-Za-z,&'\- ]{2,80}?)\s+Global Practices?", head):
        for n in _names_in(m.group(1)):
            if n not in found:
                found.append(n)
    if not found:  # bare name on its own line (e.g. Honduras cover reads "Transport")
        for line in head.splitlines()[:60]:
            line = line.strip()
            if line in _ALL and line != "Other":
                found.append(canonical(line))
                break
    return tuple(found)


def parse_practice_areas(text: str) -> PracticeAreas:
    """Parse lead/contributing Practice Areas from the FIRST datasheet in the document text."""
    text = text or ""
    head = text[:4000]
    covers = _cover_gps(head)
    flat = re.sub(r"\s+", " ", text)
    i = flat.find(_LABEL)
    if i < 0:
        return PracticeAreas(cover_gps=covers, notes=("no Practice Area (Lead) label",))
    after = flat[i + len(_LABEL): i + len(_LABEL) + 700]
    stop = _STOP_RE.search(after)
    window = after[: stop.start()] if stop else after[:400]
    window = window.replace("Contributing Practice Areas", " ").replace("PRACTICE AREA(S)", " ")
    names = _names_in(window)
    notes = []
    if not names:
        # Older PID tables print the value block after several labels; look a little further on.
        names = _names_in(after[:700])[:1]
        notes.append("lead taken from extended window")
    if not names:
        return PracticeAreas(cover_gps=covers, found_label=True, notes=("label found, no name parsed",))
    return PracticeAreas(lead=names[0], contributing=tuple(names[1:]), cover_gps=covers, found_label=True,
                         notes=tuple(notes))
