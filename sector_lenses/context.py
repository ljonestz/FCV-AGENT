"""Validated dynamic country context for sector lenses."""

from __future__ import annotations

import json
import re
from typing import Any, Iterable
from urllib.parse import urlparse


CCDR_CONTEXT_START = "%%%CCDR_CONTEXT_START%%%"
CCDR_CONTEXT_END = "%%%CCDR_CONTEXT_END%%%"

CCDR_RESEARCH_INSTRUCTIONS = """
Because the user selected the Climate-FCV lens, check whether the World Bank has
published a Country Climate and Development Report for {country}. If one exists,
extract only project-relevant hazards, locations, groups, sector impacts,
institutional constraints, uncertainty, and climate-development priorities.
Do not turn the CCDR into a routine recommendation. Append one JSON object between
%%%CCDR_CONTEXT_START%%% and %%%CCDR_CONTEXT_END%%% with keys available, title,
publication_date, url, location, and summary. Use available=false when no verified
World Bank CCDR exists.
""".strip()


def _strip_ccdr_block(text: str) -> str:
    return re.sub(
        re.escape(CCDR_CONTEXT_START) + r".*?(?:" +
        re.escape(CCDR_CONTEXT_END) + r"|$)",
        "",
        text or "",
        flags=re.DOTALL,
    ).strip()


def _bounded_text(value: Any, limit: int) -> str:
    return str(value).strip()[:limit] if value is not None else ""


def _is_world_bank_https(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").casefold()
    return (
        parsed.scheme.casefold() == "https"
        and (host == "worldbank.org" or host.endswith(".worldbank.org"))
    )


def extract_ccdr_context(text: str, country: str) -> tuple[str, dict[str, str]]:
    """Strip and validate one hidden CCDR metadata block."""

    visible = _strip_ccdr_block(text)
    match = re.search(
        re.escape(CCDR_CONTEXT_START) + r"(.*?)" +
        re.escape(CCDR_CONTEXT_END),
        text or "",
        flags=re.DOTALL,
    )
    if not match:
        return visible, {}
    try:
        payload = json.loads(match.group(1).strip())
    except (json.JSONDecodeError, TypeError, ValueError):
        return visible, {}
    if not isinstance(payload, dict) or payload.get("available") is not True:
        return visible, {}
    title = _bounded_text(payload.get("title"), 300)
    publication_date = _bounded_text(payload.get("publication_date"), 300)
    url = _bounded_text(payload.get("url"), 1000)
    location = _bounded_text(payload.get("location"), 300)
    summary = _bounded_text(payload.get("summary"), 2000)
    if not title or not summary or not _is_world_bank_https(url):
        return visible, {}
    return visible, {
        "id": "context-ccdr",
        "lens_id": "climate",
        "source_type": "ccdr",
        "country": _bounded_text(country, 300),
        "title": title,
        "publication_date": publication_date,
        "url": url,
        "location": location,
        "summary": summary,
    }


def has_uploaded_ccdr(doc_parts: Iterable[dict[str, Any]] | None) -> bool:
    """Return whether an uploaded file already supplies CCDR context."""

    markers = ("ccdr", "country climate and development report")
    for part in doc_parts or ():
        if not isinstance(part, dict):
            continue
        sample = " ".join((
            _bounded_text(part.get("name"), 500),
            _bounded_text(part.get("raw_text"), 2000),
        )).casefold()
        if any(marker in sample for marker in markers):
            return True
    return False
