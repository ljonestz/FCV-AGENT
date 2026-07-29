"""Validated, bounded Climate-FCV web-research contracts."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse


CLIMATE_RESEARCH_START = "%%%CLIMATE_RESEARCH_START%%%"
CLIMATE_RESEARCH_END = "%%%CLIMATE_RESEARCH_END%%%"
CLIMATE_TIME_HORIZONS = {
    "current-near-term",
    "project-lifetime",
    "asset-system-lifetime",
}
CLIMATE_EVIDENCE_STATUSES = {"observed", "projected", "inferred"}
CLIMATE_CONFIDENCE_LEVELS = {"high", "medium", "low"}
CLIMATE_SOURCE_TYPES = {
    "ccdr",
    "world-bank",
    "un",
    "government",
    "scientific",
    "specialist",
    "current-operations",
}
TRUSTED_CLIMATE_HOST_SUFFIXES = (
    "worldbank.org",
    "ipcc.ch",
    "un.org",
    "undp.org",
    "unep.org",
    "unhcr.org",
    "wfp.org",
    "fao.org",
    "iom.int",
    "reliefweb.int",
    "cgiar.org",
    "cgspace.cgiar.org",
    "adelphi.de",
    "oecd.org",
)


def _bounded(value: Any, limit: int) -> str:
    """Return a stripped string no longer than ``limit`` characters."""

    return str(value or "").strip()[:limit]


def _strings(value: Any, count: int, size: int) -> list[str]:
    """Normalize, deduplicate, and bound a list of strings."""

    if not isinstance(value, list):
        return []
    values = (_bounded(item, size) for item in value)
    return list(dict.fromkeys(item for item in values if item))[:count]


def _trusted_https(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").casefold()
    return parsed.scheme.casefold() == "https" and any(
        host == suffix or host.endswith("." + suffix)
        for suffix in TRUSTED_CLIMATE_HOST_SUFFIXES
    )


def _attempt_count(value: Any) -> int:
    try:
        return min(max(int(value or 0), 0), 2)
    except (TypeError, ValueError):
        return 0


def build_climate_research_prompt(
    country: str,
    sector: str,
    project_profile: dict[str, Any],
    narrow: bool = False,
) -> str:
    """Build the bounded dedicated Climate-FCV research request."""

    scope = (
        "FOCUSED REQUEST: return four to six strongest claims."
        if narrow
        else "Return at most twelve claims, prioritizing material project pathways."
    )
    profile = json.dumps(
        project_profile if isinstance(project_profile, dict) else {},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"""
Research Climate-FCV conditions for {country} and this {sector} project.
First check for a public Country Climate and Development Report.
Use it only where directly relevant, then fill material gaps from authoritative
World Bank, UN, scientific, government, or established specialist sources.

PROJECT PROFILE:
{profile}

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


def normalize_climate_research_bundle(payload: Any) -> dict[str, Any]:
    """Validate untrusted model output into a bounded research bundle."""

    raw = payload if isinstance(payload, dict) else {}
    raw_sources = raw.get("sources")
    sources: list[dict[str, str]] = []
    for item in raw_sources if isinstance(raw_sources, list) else []:
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
    raw_claims = raw.get("claims")
    claims: list[dict[str, Any]] = []
    for item in raw_claims if isinstance(raw_claims, list) else []:
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
            value
            for value in _strings(item.get("source_ids"), 4, 80)
            if value in allowed_sources
        ]
        evidence_status = _bounded(item.get("evidence_status"), 20)
        confidence = _bounded(item.get("confidence"), 20)
        horizons = [
            value
            for value in _strings(item.get("time_horizons"), 3, 40)
            if value in CLIMATE_TIME_HORIZONS
        ]
        claim = _bounded(item.get("claim"), 700)
        if (
            not re.fullmatch(r"climate-claim-[1-9][0-9]?", claim_id)
            or not claim
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
            "claim": claim,
            "source_ids": source_ids,
            "geographies": _strings(item.get("geographies"), 4, 160),
            "project_elements": project_elements,
            "affected_groups": _strings(item.get("affected_groups"), 4, 160),
            "systems_or_assets": _strings(
                item.get("systems_or_assets"), 4, 180
            ),
            "evidence_status": evidence_status,
            "confidence": confidence,
            "time_horizons": horizons,
            "evidence_gap": _bounded(item.get("evidence_gap"), 500),
        })
        if len(claims) == 12:
            break

    requested_status = _bounded(raw.get("status"), 20)
    status = (
        requested_status
        if requested_status in {"complete", "partial"}
        else "failed"
    )
    if not claims:
        status = "failed"
    return {
        "status": status,
        "attempts": _attempt_count(raw.get("attempts")),
        "sources": sources,
        "claims": claims,
        "failure_reason": _bounded(raw.get("failure_reason"), 240),
    }


CLIMATE_AUTHORITATIVE_SOURCE_TYPES = {
    "ccdr", "world-bank", "un", "government", "scientific",
}
CLIMATE_RESEARCH_MIN_SOURCES = 2


def climate_research_evidence_gate(payload: Any) -> dict[str, Any]:
    """Return a safe decision for the mandatory Climate-FCV research gate."""
    bundle = normalize_climate_research_bundle(payload)
    sources = bundle["sources"]
    claims = bundle["claims"]
    cited_source_ids = {
        source_id
        for claim in claims
        for source_id in claim["source_ids"]
    }
    distinct_cited_sources = []
    seen_source_ids = set()
    seen_urls = set()
    for source in sources:
        source_id = source["id"]
        url_key = source["url"].lower().rstrip("/")
        if (
            source_id not in cited_source_ids
            or source_id in seen_source_ids
            or url_key in seen_urls
        ):
            continue
        distinct_cited_sources.append(source)
        seen_source_ids.add(source_id)
        seen_urls.add(url_key)
    authoritative = any(
        source["source_type"] in CLIMATE_AUTHORITATIVE_SOURCE_TYPES
        for source in distinct_cited_sources
    )
    project_claim = any(
        claim["project_elements"]
        and (
            claim["geographies"]
            or claim["affected_groups"]
            or claim["systems_or_assets"]
        )
        for claim in claims
    )
    ok = (
        bundle["status"] in {"complete", "partial"}
        and len(distinct_cited_sources) >= CLIMATE_RESEARCH_MIN_SOURCES
        and authoritative
        and project_claim
    )
    if ok:
        return {"ok": True, "code": "", "message": "", "bundle": bundle}
    code = (
        "climate_research_failed"
        if bundle["status"] == "failed" and not sources and not claims
        else "climate_research_insufficient"
    )
    failure_reason = str(bundle.get("failure_reason", "")).casefold()
    if code == "climate_research_failed" and (
        "deadline" in failure_reason or "timed out" in failure_reason
    ):
        message = (
            "The required Climate-FCV web research timed out before validated "
            "evidence could be returned. Retry the climate assessment."
        )
    else:
        message = (
            "The required Climate-FCV web research did not return at least two "
            "relevant sources, including authoritative climate evidence tied to "
            "this project's locations, groups, systems, or assets."
        )
    return {"ok": False, "code": code, "message": message, "bundle": bundle}


def extract_climate_research_bundle(
    text: str,
) -> tuple[str, dict[str, Any]]:
    """Strip and validate one hidden Climate-FCV research block."""

    match = re.search(
        re.escape(CLIMATE_RESEARCH_START)
        + r"(.*?)"
        + re.escape(CLIMATE_RESEARCH_END),
        text or "",
        re.DOTALL,
    )
    visible = re.sub(
        re.escape(CLIMATE_RESEARCH_START)
        + r".*?(?:"
        + re.escape(CLIMATE_RESEARCH_END)
        + r"|$)",
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
    """Serialize validated sources and claims for bounded prompt injection."""

    normalized = normalize_climate_research_bundle(bundle)
    if not normalized["claims"]:
        return ""
    return json.dumps(
        {
            "sources": normalized["sources"],
            "claims": normalized["claims"],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
