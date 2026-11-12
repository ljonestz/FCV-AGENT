"""Shared live-source policy: URL safety, deny-list, trust tier, type, dates, relevance.

Pure functions, no I/O. Used by FCV core research and Climate research. The
trusted list is a labelling list, not a gate: only denied or unsafe sources
are dropped; everything else is admitted with a tier.
"""
from __future__ import annotations

import ipaddress
import re
import unicodedata
from collections.abc import Iterable
from typing import Any, Literal
from urllib.parse import urlsplit

CAUTION_NOTE = (
    "Source is outside the standard trusted list; "
    "interpret with caution and check the original."
)

DENIED_HOST_SUFFIXES: tuple[str, ...] = (
    "facebook.com", "x.com", "twitter.com", "instagram.com", "tiktok.com",
    "youtube.com", "reddit.com", "quora.com", "medium.com", "substack.com",
    "blogspot.com", "wordpress.com", "linkedin.com", "pinterest.com",
    "telegram.org", "t.me", "youtu.be", "fb.com", "threads.net", "vk.com",
    "tumblr.com",
)
# Blogspot also serves country-code mirrors (blogspot.co.uk, blogspot.fr, ...).

TRUSTED_HOSTS: dict[str, tuple[str, ...]] = {
    "world-bank": ("worldbank.org",),
    "un": (
        "un.org", "undp.org", "unep.org", "unhcr.org", "unicef.org", "unocha.org",
        "reliefweb.int", "wfp.org", "fao.org", "iom.int", "who.int", "ipcinfo.org",
        "unric.org", "undrr.org", "preventionweb.net", "unfccc.int", "ilo.org",
        "ohchr.org", "unhabitat.org", "unwomen.org", "unfpa.org", "unesco.org",
        "unodc.org",
    ),
    "research": (
        "imf.org", "oecd.org", "afdb.org", "adb.org", "iadb.org", "ifad.org",
        "cgiar.org", "ifpri.org", "crisisgroup.org", "acleddata.com",
        "chathamhouse.org", "usip.org", "sipri.org", "odi.org", "brookings.edu",
        "csis.org", "iiss.org", "carnegieendowment.org", "wri.org", "iied.org",
        "adelphi.de", "climate-diplomacy.org", "internal-displacement.org",
        "fews.net", "acaps.org", "hrw.org", "amnesty.org",
        "idea.int", "bti-project.org", "bertelsmann-stiftung.de", "issafrica.org",
        "afrobarometer.org", "latinobarometro.org", "arabbarometer.org",
        "amaniafrica-et.org", "insightcrime.org", "globalinitiative.net",
        "freedomhouse.org", "transparency.org", "clingendael.org",
        "saferworld-global.org", "saferworld.org.uk", "interpeace.org", "cmi.no",
        "gppi.net", "ipinst.org", "wilsoncenter.org", "cfr.org", "rand.org",
        "ecfr.eu", "prio.org", "cgdev.org", "globalr2p.org",
        # Regional and multilateral bodies (no separate type exists).
        "au.int", "ecowas.int", "europa.eu", "oas.org", "cepal.org", "igad.int",
        "sadc.int", "isdb.org", "aiib.org", "ebrd.com", "eib.org",
    ),
    "humanitarian": ("icrc.org", "ifrc.org", "msf.org", "thenewhumanitarian.org"),
    "news": (
        "reuters.com", "apnews.com", "afp.com", "bbc.com", "bbc.co.uk",
        "aljazeera.com", "france24.com", "dw.com", "theguardian.com", "ft.com",
        "nytimes.com", "washingtonpost.com", "economist.com", "bloomberg.com",
        "allafrica.com", "rfi.fr", "cnn.com", "npr.org", "lemonde.fr", "elpais.com",
        "efe.com", "africanews.com", "devex.com", "irinnews.org",
    ),
    "scientific": (
        "ipcc.ch", "nature.com", "science.org", "sciencedirect.com", "springer.com",
        "wiley.com", "tandfonline.com", "doi.org", "copernicus.eu", "noaa.gov",
        "nasa.gov", "wmo.int", "ucdp.uu.se", "worldweatherattribution.org",
        "climateanalytics.org",
    ),
}

_GOVERNMENT_RE = re.compile(r"\.(?:gov|gouv|go|gob|gv)(?:\.[a-z]{2})?$")
_ACADEMIC_RE = re.compile(r"\.(?:edu(?:\.[a-z]{2})?|ac\.[a-z]{2})$")
_RELATIVE_DATE_RE = re.compile(r"\b(?:hours?|days?|weeks?|months?|years?)\s+ago\b", re.IGNORECASE)


def _value(item: Any, name: str, default: Any = None) -> Any:
    return item.get(name, default) if isinstance(item, dict) else getattr(item, name, default)


def _string(value: Any, limit: int = 0) -> str:
    text = str(value or "").strip()
    return text[:limit] if limit else text


def _fold(value: Any) -> str:
    text = unicodedata.normalize("NFKD", _string(value).replace("’", "'")).encode(
        "ascii", "ignore"
    ).decode("ascii")
    return re.sub(r"\s+", " ", text.casefold()).strip()


def safe_public_url(value: Any) -> str:
    url = _string(value, 2000)
    if not url or any(ord(char) < 32 for char in url):
        return ""
    try:
        parsed = urlsplit(url)
        hostname = (parsed.hostname or "").rstrip(".").casefold()
        scheme = parsed.scheme.casefold()
    except ValueError:
        return ""
    if scheme not in {"http", "https"} or not hostname:
        return ""
    if parsed.username or parsed.password:
        return ""
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(
        (".local", ".internal", ".localhost")
    ):
        return ""
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None and (
        address.is_private or address.is_loopback or address.is_link_local
        or address.is_reserved or address.is_multicast or address.is_unspecified
    ):
        return ""
    if address is None and "." not in hostname and ":" not in hostname:
        return ""
    return url


def publication_date(item: Any) -> str:
    """Return the first absolute date field; relative ages are skipped."""
    for name in ("publication_date", "published_date", "date", "page_age"):
        value = _string(_value(item, name), 80)
        if value and not _RELATIVE_DATE_RE.search(value):
            return value
    return ""


_DRC_TAIL_RE = re.compile(r"^(?:democratic republic of(?: the)?|dem\.? rep\.?)$")
_ROC_TAIL_RE = re.compile(r"^(?:republic of(?: the)?|rep\.?)$")
_OFFICIAL_PREFIX_RE = re.compile(
    r"^(?:the )?(?:(?:arab|islamic|federal|democratic|people's|bolivarian|united) )*"
    r"republic of (?:the )?"
)
_SUDAN_RE = r"(?<![a-z0-9-])(?<!south )sudan(?![a-z0-9-])"
_SOUTH_SUDAN_RE = r"south[\s-]+sudan"


def _country_key(country: str) -> str:
    """Fold a country name and canonicalise World Bank inverted official names.

    "Congo, Dem. Rep." and "Congo, Democratic Republic of" become the DRC
    name; "Congo, Rep." becomes the Republic of the Congo; any other
    "X, <qualifier>" form (Yemen, Republic of; Gambia, The; Venezuela, RB;
    Egypt, Arab Republic of) keeps the short name X.
    """
    key = _fold(country)
    if "," in key:
        head, tail = (part.strip() for part in key.split(",", 1))
        if head == "congo" and _DRC_TAIL_RE.match(tail):
            return "democratic republic of the congo"
        if head == "congo" and _ROC_TAIL_RE.match(tail):
            return "republic of the congo"
        key = head or tail
    return key


def _country_regex(country: str) -> tuple[list[str], list[str]]:
    key = _country_key(country)
    if key in {"guinea", "republic of guinea", "guinea conakry"}:
        return [r"(?<![a-z0-9-])guinea(?![a-z0-9-])"], [
            r"guinea[\s-]+bissau",
            r"equatorial[\s-]+guinea",
            r"papua[\s-]+new[\s-]+guinea",
        ]
    if key in {"nigeria", "federal republic of nigeria"}:
        return [r"(?<![a-z0-9-])nigeria(?![a-z0-9-])"], [r"(?<![a-z0-9-])niger(?![a-z0-9-])"]
    if key in {"guinea bissau", "republic of guinea bissau"}:
        return [r"guinea[\s-]+bissau", r"bissau"], []
    if key in {"niger", "republic of niger"}:
        return [r"(?<![a-z0-9-])niger(?![a-z0-9-])"], [r"nigeria"]
    if key in {
        "democratic republic of the congo", "democratic republic of congo",
        "drc", "dr congo", "congo kinshasa",
    }:
        return [
            r"democratic[\s-]+republic[\s-]+(?:of[\s-]+(?:the[\s-]+)?)?congo",
            r"(?<![a-z0-9-])drc(?![a-z0-9-])", r"dr[\s-]+congo",
            r"congo[\s-]+kinshasa",
        ], [
            r"republic[\s-]+of[\s-]+the[\s-]+congo",
            r"congo[\s-]+brazzaville", r"brazzaville",
        ]
    if key in {"republic of the congo", "republic of congo", "congo brazzaville", "congo"}:
        return [
            r"republic[\s-]+of[\s-]+the[\s-]+congo",
            r"republic[\s-]+of[\s-]+congo", r"congo[\s-]+brazzaville",
            r"(?<![a-z0-9-])brazzaville(?![a-z0-9-])",
        ], [
            r"democratic[\s-]+republic[\s-]+(?:of[\s-]+(?:the[\s-]+)?)?congo",
            r"(?<![a-z0-9-])drc(?![a-z0-9-])", r"congo[\s-]+kinshasa",
            r"kinshasa",
        ]
    if key in {"sudan", "the sudan", "republic of sudan", "republic of the sudan"}:
        return [_SUDAN_RE], [_SOUTH_SUDAN_RE]
    if key in {"south sudan", "republic of south sudan"}:
        return [_SOUTH_SUDAN_RE], [_SUDAN_RE]
    # Official long forms ("Republic of Yemen") are matched by their short name.
    key = _OFFICIAL_PREFIX_RE.sub("", key) or key
    escaped = r"[\s-]+".join(re.escape(part) for part in key.split())
    return [rf"(?<![a-z0-9-]){escaped}(?![a-z0-9-])"], []


def _mentions(text: str, patterns: list[str]) -> bool:
    folded = _fold(text)
    return any(re.search(pattern, folded) for pattern in patterns)


def _target_mentions(
    country: str,
    text: str,
    target_patterns: list[str],
    wrong_patterns: list[str],
) -> bool:
    folded = _fold(text)
    key = _country_key(country)
    if key in {"guinea", "republic of guinea", "guinea conakry"}:
        for pattern in wrong_patterns:
            folded = re.sub(pattern, " ", folded)
    elif key in {
        "republic of the congo", "republic of congo", "congo brazzaville",
        "congo",
    }:
        drc_patterns = (
            r"democratic[\s-]+republic[\s-]+(?:of[\s-]+(?:the[\s-]+)?)?congo",
            r"(?<![a-z0-9-])drc(?![a-z0-9-])",
            r"congo[\s-]+kinshasa",
            r"(?<![a-z0-9-])kinshasa(?![a-z0-9-])",
        )
        for pattern in drc_patterns:
            folded = re.sub(pattern, " ", folded)
    return any(re.search(pattern, folded) for pattern in target_patterns)


def country_relevance(country: str, title: str, cited_text: str) -> tuple[bool, bool]:
    target, wrong = _country_regex(country)
    title_target = _target_mentions(country, title, target, wrong)
    quote_target = _target_mentions(country, cited_text, target, wrong)
    title_wrong = _mentions(title, wrong)
    quote_wrong = _mentions(cited_text, wrong)
    has_target = title_target or quote_target
    if (quote_wrong or title_wrong) and not has_target:
        return False, False
    if quote_wrong or title_wrong:
        if quote_target:
            return True, False
        if title_target and not quote_wrong:
            return True, False
        return False, True
    if has_target:
        return True, False
    return False, True


def _host(url: str) -> str:
    try:
        return (urlsplit(_string(url)).hostname or "").rstrip(".").casefold()
    except ValueError:
        return ""


def _host_matches(host: str, suffixes: tuple[str, ...]) -> bool:
    return any(host == suffix or host.endswith("." + suffix) for suffix in suffixes)


def is_denied(url: str) -> bool:
    host = _host(url)
    # Any blogspot.<tld> variant (blogspot.co.uk, x.blogspot.fr): a 'blogspot'
    # label followed by at least one more label. Label split, no regex (ReDoS).
    labels = host.split(".")
    return _host_matches(host, DENIED_HOST_SUFFIXES) or "blogspot" in labels[:-1]


def source_type(url: str) -> str:
    host = _host(url)
    if not host:
        return "other"
    for kind in ("world-bank", "un", "research", "humanitarian", "news", "scientific"):
        if _host_matches(host, TRUSTED_HOSTS[kind]):
            return kind
    if _GOVERNMENT_RE.search(host):
        return "government"
    if _ACADEMIC_RE.search(host):
        return "scientific"
    return "other"


def trust_tier(url: str) -> Literal["standard", "caution"]:
    return "standard" if source_type(url) != "other" else "caution"


PROJECT_ID_RE = re.compile(r"\bP\d{6}\b")


def extract_project_ids(text: str, limit: int = 8) -> list[str]:
    """Unique World Bank project ids (P + six digits), first-seen order, upper-case."""
    found = (match.upper() for match in PROJECT_ID_RE.findall(_string(text)))
    return list(dict.fromkeys(found))[: max(0, limit)]


def clean_project_ids(project_ids: Iterable[str] | str | None) -> list[str]:
    """Normalise to well-formed upper-case ids; a bare string is one id, junk is dropped."""
    if isinstance(project_ids, str):
        project_ids = [project_ids]
    cleaned = (_string(item).upper() for item in (project_ids or ()))
    return [pid for pid in cleaned if PROJECT_ID_RE.fullmatch(pid)]


def is_own_project_source(url: str, title: str, project_ids: Iterable[str]) -> bool:
    """True when a live source carries one of the screened project's own ids.

    The id must stand as a whole token, so P1790170 and XP179017 never match
    P179017, while "/P179017-36e7..." and "?id=P179017" do.
    """
    haystack = f"{_string(url)} {_string(title)}"
    for pid in clean_project_ids(project_ids):
        if re.search(
            rf"(?<![A-Za-z0-9]){re.escape(pid)}(?![0-9])", haystack, re.IGNORECASE
        ):
            return True
    return False
