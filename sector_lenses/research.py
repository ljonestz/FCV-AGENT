"""Validated, bounded Climate-FCV web-research contracts."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse


CLIMATE_RESEARCH_START = "%%%CLIMATE_RESEARCH_START%%%"
CLIMATE_RESEARCH_END = "%%%CLIMATE_RESEARCH_END%%%"
CLIMATE_EVIDENCE_PACKET_MAX_CHARS = 12_000
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


def _block_value(item: Any, name: str, default: Any = None) -> Any:
    """Read one field from an SDK object or dictionary-shaped block."""

    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def build_climate_evidence_packet(
    content: Any,
    project_profile: dict[str, Any],
) -> dict[str, Any]:
    """Convert search blocks into bounded, trusted structuring evidence."""

    blocks = content if isinstance(content, list) else []
    note_parts: list[str] = []
    sources: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    def add_source(item: Any) -> None:
        url = _bounded(_block_value(item, "url"), 1000)
        url_key = url.casefold().rstrip("/")
        if not url or not _trusted_https(url) or url_key in seen_urls:
            return
        title = _bounded(_block_value(item, "title"), 220)
        if not title:
            return
        publication_date = _bounded(
            _block_value(item, "publication_date")
            or _block_value(item, "page_age"),
            40,
        )
        excerpt = _bounded(
            _block_value(item, "cited_text")
            or _block_value(item, "snippet")
            or _block_value(item, "text"),
            320,
        )
        seen_urls.add(url_key)
        sources.append({
            "title": title,
            "url": url,
            "publication_date": publication_date,
            "excerpt": excerpt,
        })

    for block in blocks:
        block_type = _bounded(_block_value(block, "type"), 80)
        if block_type == "text":
            note = _bounded(_block_value(block, "text"), 2200)
            if note:
                note_parts.append(note)
            citations = _block_value(block, "citations", [])
            for citation in citations if isinstance(citations, list) else []:
                add_source(citation)
        elif block_type == "web_search_tool_result":
            results = _block_value(block, "content", [])
            for result in results if isinstance(results, list) else []:
                add_source(result)
        if len(sources) >= 4:
            break

    profile = project_profile if isinstance(project_profile, dict) else {}
    packet = {
        "notes": _bounded("\n\n".join(note_parts), 2200),
        "sources": sources[:4],
        "project_profile": {
            "documents": _strings(profile.get("documents"), 4, 180),
            "document_excerpt": _bounded(
                profile.get("document_excerpt"), 1800
            ),
        },
    }
    serialized = json.dumps(packet, ensure_ascii=False, separators=(",", ":"))
    if len(serialized) > CLIMATE_EVIDENCE_PACKET_MAX_CHARS:
        overage = len(serialized) - CLIMATE_EVIDENCE_PACKET_MAX_CHARS
        packet["notes"] = packet["notes"][:-overage] if (
            overage < len(packet["notes"])
        ) else ""
    return packet


def _attempt_count(value: Any) -> int:
    try:
        return min(max(int(value or 0), 0), 2)
    except (TypeError, ValueError):
        return 0


def build_climate_search_prompt(
    country: str,
    sector: str,
    project_profile: dict[str, Any],
) -> str:
    """Build a concise search-only request for two authoritative sources."""

    profile = json.dumps(
        project_profile if isinstance(project_profile, dict) else {},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"""
SEARCH ONLY. Research Climate-FCV conditions for {country} and this {sector}
project. Use exactly two targeted web searches and then stop searching.

Search 1: prioritize a public Country Climate and Development Report or another
authoritative World Bank, government, UN, or scientific climate source.
Search 2: find one complementary authoritative source addressing a material gap
in the first source.

PROJECT PROFILE:
{profile}

Return concise evidence notes, not JSON and not recommendations. For each useful
source, give its exact title, URL, publication date if available, and only the
findings that connect observed or projected climate pressures to the profile's
locations, groups, project elements, systems, or assets. Distinguish current,
project-lifetime, and longer-lived asset or system implications. Exclude generic
country statements and untrusted sources. Keep the entire response under 900 words.
""".strip()


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
{CLIMATE_RESEARCH_END} using this exact shape:
{{"status":"complete|partial|failed","attempts":1,"sources":[{{"id":"climate-source-1","source_type":"ccdr|world-bank|un|government|scientific|specialist|current-operations","title":"...","url":"https://...","publication_date":"...","location":"..."}}],"claims":[{{"id":"climate-claim-1","claim":"...","source_ids":["climate-source-1"],"geographies":["..."],"project_elements":["..."],"affected_groups":["..."],"systems_or_assets":["..."],"evidence_status":"observed|projected|inferred","confidence":"high|medium|low","time_horizons":["current-near-term|project-lifetime|asset-system-lifetime"],"evidence_gap":"..."}}],"failure_reason":""}}

Include four to six claims and at least two distinct cited sources, including at
least one authoritative source. Every claim must cite a listed source, name a
project element, and name at least one geography, affected group, system, or
asset. Use only exact HTTPS source URLs present in the search results.
""".strip()



def summarize_climate_structuring_response(
    text: str,
    *,
    usage: Any = None,
    stop_reason: Any = "",
    gate_code: Any = "",
) -> dict[str, Any]:
    """Return bounded, content-free structural telemetry."""

    limit = 9_999_999
    allowed_fields = (
        "status",
        "attempts",
        "sources",
        "claims",
        "failure_reason",
    )
    allowed_stop_reasons = {
        "end_turn",
        "max_tokens",
        "stop_sequence",
        "pause_turn",
        "refusal",
    }
    allowed_gate_codes = {
        "ok",
        "climate_research_failed",
        "climate_research_insufficient",
    }

    def bounded_integer(value: Any, default: int = 0) -> int:
        try:
            return min(max(int(value), 0), limit)
        except (TypeError, ValueError):
            return default

    def usage_value(name: str) -> int:
        value = (
            usage.get(name)
            if isinstance(usage, dict)
            else getattr(usage, name, 0)
        )
        return bounded_integer(value)

    response_text = text if isinstance(text, str) else ""
    start_present = CLIMATE_RESEARCH_START in response_text
    end_present = CLIMATE_RESEARCH_END in response_text
    fields_present = tuple(
        field
        for field in allowed_fields
        if re.search(rf'"{re.escape(field)}"\s*:', response_text)
    )
    json_status = "absent"
    top_level_object = False
    sources_count = -1
    source_id_valid = -1
    source_type_valid = -1
    source_title_present = -1
    source_url_trusted = -1
    source_fully_valid = -1
    claims_count = -1

    if start_present and end_present:
        payload_text = response_text.split(CLIMATE_RESEARCH_START, 1)[1]
        payload_text = payload_text.split(CLIMATE_RESEARCH_END, 1)[0]
        try:
            payload = json.loads(payload_text.strip())
        except (json.JSONDecodeError, TypeError, ValueError):
            json_status = "invalid"
        else:
            json_status = "valid"
            top_level_object = isinstance(payload, dict)
            if top_level_object:
                fields_present = tuple(
                    field for field in allowed_fields if field in payload
                )
                sources = payload.get("sources")
                claims = payload.get("claims")
                if isinstance(sources, list):
                    sources_count = min(len(sources), limit)
                    source_id_valid = 0
                    source_type_valid = 0
                    source_title_present = 0
                    source_url_trusted = 0
                    source_fully_valid = 0
                    for source in sources[:99]:
                        if not isinstance(source, dict):
                            continue
                        id_ok = bool(re.fullmatch(
                            r"climate-source-[1-9][0-9]?",
                            _bounded(source.get("id"), 80),
                        ))
                        type_ok = (
                            _bounded(source.get("source_type"), 40)
                            in CLIMATE_SOURCE_TYPES
                        )
                        title_ok = bool(_bounded(source.get("title"), 300))
                        url_ok = _trusted_https(
                            _bounded(source.get("url"), 1000)
                        )
                        source_id_valid += int(id_ok)
                        source_type_valid += int(type_ok)
                        source_title_present += int(title_ok)
                        source_url_trusted += int(url_ok)
                        source_fully_valid += int(
                            id_ok and type_ok and title_ok and url_ok
                        )
                if isinstance(claims, list):
                    claims_count = min(len(claims), limit)
    elif start_present or end_present:
        json_status = "incomplete"

    normalized_stop_reason = str(stop_reason or "unknown")
    if normalized_stop_reason not in allowed_stop_reasons:
        normalized_stop_reason = "unknown"
    normalized_gate_code = str(gate_code or "ok")
    if normalized_gate_code not in allowed_gate_codes:
        normalized_gate_code = "climate_research_failed"

    return {
        "stop_reason": normalized_stop_reason,
        "input_tokens": usage_value("input_tokens"),
        "output_tokens": usage_value("output_tokens"),
        "response_chars": min(len(response_text), limit),
        "start_present": start_present,
        "end_present": end_present,
        "json_status": json_status,
        "top_level_object": top_level_object,
        "fields_present": fields_present,
        "sources_count": sources_count,
        "source_id_valid": source_id_valid,
        "source_type_valid": source_type_valid,
        "source_title_present": source_title_present,
        "source_url_trusted": source_url_trusted,
        "source_fully_valid": source_fully_valid,
        "claims_count": claims_count,
        "gate_code": normalized_gate_code,
    }


def normalize_climate_research_bundle(payload: Any) -> dict[str, Any]:
    """Validate untrusted model output into a bounded research bundle."""

    raw = payload if isinstance(payload, dict) else {}
    raw_sources = raw.get("sources")
    sources: list[dict[str, str]] = []
    source_id_aliases: dict[str, str] = {}
    for item in raw_sources if isinstance(raw_sources, list) else []:
        if not isinstance(item, dict):
            continue
        raw_source_id = _bounded(item.get("id"), 80)
        source_type = _bounded(item.get("source_type"), 40)
        url = _bounded(item.get("url"), 1000)
        title = _bounded(item.get("title"), 300)
        if (
            not raw_source_id
            or raw_source_id in source_id_aliases
            or source_type not in CLIMATE_SOURCE_TYPES
            or not title
            or not _trusted_https(url)
        ):
            continue
        source_id = f"climate-source-{len(sources) + 1}"
        source_id_aliases[raw_source_id] = source_id
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
        claim_id = f"climate-claim-{len(claims) + 1}"
        project_elements = _strings(item.get("project_elements"), 4, 180)
        anchors = (
            _strings(item.get("geographies"), 4, 160)
            + _strings(item.get("affected_groups"), 4, 160)
            + _strings(item.get("systems_or_assets"), 4, 180)
        )
        source_ids = [
            source_id_aliases[value]
            for value in _strings(item.get("source_ids"), 4, 80)
            if value in source_id_aliases
            and source_id_aliases[value] in allowed_sources
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
            not claim
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
    if (
        code == "climate_research_failed"
        and "structuring was truncated" in failure_reason
    ):
        message = (
            "Climate-FCV web evidence was found but could not be structured "
            "into a validated research bundle. Retry the climate assessment."
        )
    elif code == "climate_research_failed" and (
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
