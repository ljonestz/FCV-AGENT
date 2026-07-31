"""Load and safely materialize the approved Climate-FCV country evidence bank.

The browser retains only a compact manifest of canonical IDs. Every use of
bank prose is reconstructed here from the pinned server-side release. Invalid,
missing, stale, or incompatible content degrades to a typed unavailable result
and never raises into an assessment workflow.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse


CLIMATE_BANK_SCHEMA_VERSION = "1.0.0"
DEFAULT_RELEASE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "climate-fcv-country-bank"
    / "releases"
    / "current"
    / "runtime.json"
)

_EVIDENCE_ID = re.compile(r"^[A-Z]{3}-E-\d{3}$")
_PATHWAY_ID = re.compile(r"^[A-Z]{3}-P-\d{3}$")
_SOURCE_ID = re.compile(r"^[A-Z]{3}-SRC-\d{3}$")
_ISO3 = re.compile(r"^[A-Z]{3}$")
_REPOSITORY_PATH = re.compile(
    r"^(?![A-Za-z]:)(?![\\/])(?!.*(?:^|[\\/])\.\.(?:[\\/]|$))"
    r"(?!.*(?:^|[\\/])source_documents(?:[\\/]|$))\S+$"
)

_EVIDENCE_FIELDS = frozenset(
    {
        "evidence_id", "iso3", "statement", "compact_statement",
        "evidence_status", "analytical_role", "hazard_tags", "impact_tags",
        "geographies", "affected_groups", "sectors",
        "systems_assets_resources", "institutions", "mediator_tags",
        "interaction_direction", "time_horizons", "scenario", "source_refs",
        "confidence", "uncertainty", "review_status", "review_date",
    }
)
_PATHWAY_FIELDS = frozenset(
    {
        "pathway_id", "iso3", "climate_pressure", "documented_impact",
        "fcv_mediator", "possible_consequence", "geographies",
        "affected_groups", "sectors", "systems_assets_resources",
        "institutions", "supporting_evidence_ids", "link_evidence",
        "evidence_strength", "alternative_explanations", "uncertainty",
        "resilience_factors", "compact_statement", "interaction_direction",
        "review_status", "review_date",
    }
)
_SOURCE_FIELDS = frozenset(
    {
        "source_id", "title", "organization", "publication_date",
        "publication_date_basis", "url", "repository_file", "source_type",
        "analytical_roles", "country_codes", "geographic_coverage",
        "temporal_coverage", "accessed_on", "methodology", "limitations",
        "license_status", "checksum",
    }
)
_EVIDENCE_STATUSES = {"observed", "projected", "inferred"}
_ANALYTICAL_ROLES = {
    "direct-climate-fcv", "vulnerability-capacity", "physical-baseline",
}
_EVIDENCE_DIRECTIONS = {
    "climate-to-fcv", "fcv-to-climate", "bidirectional", "contextual",
}
_PATHWAY_DIRECTIONS = {
    "climate-to-fcv", "fcv-to-climate", "bidirectional",
}
_TIME_HORIZONS = {
    "historical", "current", "near-term", "medium-term", "long-term",
}
_SOURCE_TYPES = {
    "government-report", "un-report", "mdb-report", "ngo-report",
    "think-tank-report", "academic-publication", "dataset", "web-page",
    "pdf-report", "other-report",
}
_PUBLICATION_DATE_BASES = {
    "publication", "submission", "portal-publication", "document-version",
    "version", "not-stated",
}
_LICENSE_STATUSES = {
    "open", "restricted", "permission-required", "unknown",
}


def _canonical_checksum(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _source_manifest(sources: list[Any]) -> list[Any]:
    """Match the companion builder's checksum contract."""

    return [
        (
            {key: value for key, value in source.items() if key != "checksum"}
            if isinstance(source, dict)
            else source
        )
        for source in sources
    ]


@dataclass(frozen=True)
class ClimateBankLoad:
    """Non-throwing result of loading a pinned runtime release."""

    status: str
    warning_code: str
    release: dict[str, Any]

    def resolve_country(self, value: str) -> dict[str, Any] | None:
        key = str(value or "").strip().casefold()
        if not key:
            return None
        countries = self.release.get("countries", {})
        if not isinstance(countries, dict):
            return None
        for country in countries.values():
            if not isinstance(country, dict):
                continue
            aliases = {
                str(country.get("iso3", "")).strip().casefold(),
                str(country.get("name", "")).strip().casefold(),
                *(
                    str(item).strip().casefold()
                    for item in country.get("aliases", [])
                    if isinstance(item, str)
                ),
            }
            if key in aliases:
                return country
        return None


def _release_path(path: str | Path | None) -> Path:
    raw = path or os.environ.get("CLIMATE_COUNTRY_BANK_PATH") or DEFAULT_RELEASE
    candidate = Path(raw)
    if candidate.is_dir():
        candidate = candidate / "releases" / "current" / "runtime.json"
    return candidate


def _unavailable(code: str) -> ClimateBankLoad:
    return ClimateBankLoad("unavailable", code, {})


def load_climate_bank(path: str | Path | None = None) -> ClimateBankLoad:
    """Load a compatible, checksum-valid release without raising."""

    candidate = _release_path(path)
    if not candidate.is_file():
        return _unavailable("bank_missing")
    try:
        release = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _unavailable("bank_incompatible")
    if not isinstance(release, dict):
        return _unavailable("bank_incompatible")
    if release.get("schema_version") != CLIMATE_BANK_SCHEMA_VERSION:
        return _unavailable("bank_incompatible")
    required = (
        "content_version",
        "generated_at",
        "countries",
        "sources",
        "evidence_records",
        "pathways",
        "source_manifest_checksum",
    )
    if any(key not in release for key in required):
        return _unavailable("bank_incompatible")
    if (
        not isinstance(release["content_version"], str)
        or not release["content_version"].strip()
        or not isinstance(release["countries"], dict)
        or not isinstance(release["sources"], list)
        or not isinstance(release["evidence_records"], list)
        or not isinstance(release["pathways"], list)
        or not isinstance(release["source_manifest_checksum"], str)
    ):
        return _unavailable("bank_incompatible")
    if (
        _canonical_checksum(_source_manifest(release["sources"]))
        != release["source_manifest_checksum"]
    ):
        return _unavailable("bank_incompatible")
    return ClimateBankLoad("ok", "", release)


def _packet_unavailable(code: str) -> dict[str, str]:
    return {"bank_status": "unavailable", "warning_code": code}


def _unique_index(
    records: Any,
    *,
    id_key: str,
    pattern: re.Pattern[str],
) -> dict[str, dict[str, Any]] | None:
    if not isinstance(records, list):
        return None
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            return None
        record_id = record.get(id_key)
        if (
            not isinstance(record_id, str)
            or not pattern.fullmatch(record_id)
            or record_id in result
        ):
            return None
        result[record_id] = record
    return result


def _canonical_id_list(value: Any, pattern: re.Pattern[str]) -> list[str] | None:
    if not isinstance(value, list):
        return None
    if any(not isinstance(item, str) or not pattern.fullmatch(item) for item in value):
        return None
    if len(value) != len(set(value)):
        return None
    return value


def _approved_record(record: dict[str, Any], iso3: str) -> bool:
    if (
        record.get("iso3") != iso3
        or record.get("review_status") != "approved"
        or not isinstance(record.get("review_date"), str)
    ):
        return False
    try:
        date.fromisoformat(record["review_date"])
    except ValueError:
        return False
    return True


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_array(value: Any, *, minimum: int = 0) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= minimum
        and all(_nonempty_string(item) for item in value)
        and len(value) == len(set(value))
    )


def _valid_evidence_record(record: dict[str, Any], iso3: str) -> bool:
    scenario = record.get("scenario")
    return (
        set(record) == _EVIDENCE_FIELDS
        and _approved_record(record, iso3)
        and record["evidence_id"].startswith(f"{iso3}-E-")
        and _nonempty_string(record.get("statement"))
        and _nonempty_string(record.get("compact_statement"))
        and record.get("evidence_status") in _EVIDENCE_STATUSES
        and record.get("analytical_role") in _ANALYTICAL_ROLES
        and all(
            _string_array(record.get(key))
            for key in (
                "hazard_tags", "impact_tags", "geographies",
                "affected_groups", "sectors", "systems_assets_resources",
                "institutions", "mediator_tags",
            )
        )
        and record.get("interaction_direction") in _EVIDENCE_DIRECTIONS
        and _string_array(record.get("time_horizons"), minimum=1)
        and set(record["time_horizons"]).issubset(_TIME_HORIZONS)
        and (scenario is None or _nonempty_string(scenario))
        and record.get("confidence") in {"low", "medium", "high"}
        and _nonempty_string(record.get("uncertainty"))
    )


def _valid_pathway_record(record: dict[str, Any], iso3: str) -> bool:
    return (
        set(record) == _PATHWAY_FIELDS
        and _approved_record(record, iso3)
        and record["pathway_id"].startswith(f"{iso3}-P-")
        and all(
            _nonempty_string(record.get(key))
            for key in (
                "climate_pressure", "documented_impact", "fcv_mediator",
                "possible_consequence", "uncertainty", "compact_statement",
            )
        )
        and all(
            _string_array(record.get(key))
            for key in (
                "geographies", "affected_groups", "sectors",
                "systems_assets_resources", "institutions",
                "resilience_factors",
            )
        )
        and _string_array(record.get("alternative_explanations"), minimum=1)
        and record.get("evidence_strength")
        in {"direct", "triangulated", "analytical-inference"}
        and record.get("interaction_direction") in _PATHWAY_DIRECTIONS
    )


def _valid_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _valid_publication_date(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    if re.fullmatch(r"\d{4}", value):
        return True
    if re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        return True
    return _valid_date(value) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))


def _safe_source_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _normalized_source_url(value: Any) -> str | None:
    if not _safe_source_url(value):
        return None
    parsed = urlparse(value)
    path = re.sub(r"/+", "/", parsed.path or "").rstrip("/")
    query = f"?{parsed.query}" if parsed.query else ""
    return (
        f"{parsed.scheme.casefold()}://{parsed.netloc.casefold()}"
        f"{path}{query}"
    )


def _valid_source(
    source: dict[str, Any],
    *,
    expected_id: str,
    iso3: str,
) -> bool:
    country_codes = source.get("country_codes")
    publication_date = source.get("publication_date")
    publication_basis = source.get("publication_date_basis")
    repository_file = source.get("repository_file")
    checksum = source.get("checksum")
    return (
        set(source) == _SOURCE_FIELDS
        and source.get("source_id") == expected_id
        and expected_id.startswith(f"{iso3}-SRC-")
        and bool(_SOURCE_ID.fullmatch(expected_id))
        and all(
            _nonempty_string(source.get(key))
            for key in (
                "title", "organization", "temporal_coverage", "methodology",
                "limitations",
            )
        )
        and _valid_publication_date(publication_date)
        and publication_basis in _PUBLICATION_DATE_BASES
        and (
            (publication_date is None and publication_basis == "not-stated")
            or (publication_date is not None and publication_basis != "not-stated")
        )
        and _safe_source_url(source.get("url"))
        and source.get("source_type") in _SOURCE_TYPES
        and _string_array(source.get("analytical_roles"), minimum=1)
        and set(source["analytical_roles"]).issubset(_ANALYTICAL_ROLES)
        and _string_array(country_codes, minimum=1)
        and iso3 in country_codes
        and all(bool(_ISO3.fullmatch(code)) for code in country_codes)
        and _string_array(source.get("geographic_coverage"), minimum=1)
        and _valid_date(source.get("accessed_on"))
        and source.get("license_status") in _LICENSE_STATUSES
        and (
            (repository_file is None and checksum is None)
            or (
                _nonempty_string(repository_file)
                and bool(_REPOSITORY_PATH.fullmatch(repository_file))
                and isinstance(checksum, str)
                and bool(re.fullmatch(r"[a-f0-9]{64}", checksum))
            )
        )
    )


def _valid_evidence_refs(
    record: dict[str, Any],
    source_index: dict[str, dict[str, Any]],
) -> bool:
    refs = record.get("source_refs")
    if not isinstance(refs, list) or not refs:
        return False
    seen: set[tuple[str, str]] = set()
    for ref in refs:
        if not isinstance(ref, dict):
            return False
        source_id = ref.get("source_id")
        locator = ref.get("locator")
        key = (str(source_id), str(locator))
        if (
            set(ref) != {"source_id", "locator"}
            or not isinstance(source_id, str)
            or not _SOURCE_ID.fullmatch(source_id)
            or source_id not in source_index
            or not isinstance(locator, str)
            or not locator.strip()
            or key in seen
        ):
            return False
        seen.add(key)
    return True


def _valid_pathway_refs(
    record: dict[str, Any],
    evidence_index: dict[str, dict[str, Any]],
) -> bool:
    supporting = _canonical_id_list(
        record.get("supporting_evidence_ids"), _EVIDENCE_ID
    )
    links = record.get("link_evidence")
    if (
        supporting is None
        or not supporting
        or not isinstance(links, dict)
        or set(links) != {"pressure", "impact", "mediator", "consequence"}
    ):
        return False
    if any(item not in evidence_index for item in supporting):
        return False
    supporting_set = set(supporting)
    for key in ("pressure", "impact", "mediator", "consequence"):
        ids = _canonical_id_list(links.get(key), _EVIDENCE_ID)
        if (
            ids is None
            or not ids
            or any(item not in evidence_index for item in ids)
            or not set(ids).issubset(supporting_set)
        ):
            return False
    return True


def materialize_bank_manifest(
    bank: ClimateBankLoad,
    manifest: Any,
) -> dict[str, Any]:
    """Reconstruct canonical records from a client-safe ID manifest."""

    if not isinstance(bank, ClimateBankLoad) or bank.status != "ok":
        code = (
            bank.warning_code
            if isinstance(bank, ClimateBankLoad) and bank.warning_code
            else "bank_unavailable"
        )
        return _packet_unavailable(code)
    if not isinstance(manifest, dict):
        return _packet_unavailable("bank_manifest_invalid")

    release = bank.release
    if manifest.get("content_version") != release.get("content_version"):
        return _packet_unavailable("bank_version_mismatch")
    iso3 = manifest.get("country_iso3")
    if not isinstance(iso3, str):
        return _packet_unavailable("bank_manifest_invalid")
    country = release.get("countries", {}).get(iso3)
    if not isinstance(country, dict):
        return _packet_unavailable("bank_country_unavailable")
    if country.get("status") != "approved":
        return _packet_unavailable("bank_country_unapproved")
    try:
        review_due = date.fromisoformat(str(country.get("review_due", "")))
    except ValueError:
        return _packet_unavailable("bank_manifest_invalid")
    if review_due < date.today():
        return _packet_unavailable("bank_content_expired")

    selected_evidence_ids = _canonical_id_list(
        manifest.get("evidence_ids"), _EVIDENCE_ID
    )
    selected_pathway_ids = _canonical_id_list(
        manifest.get("pathway_ids"), _PATHWAY_ID
    )
    country_evidence_ids = _canonical_id_list(
        country.get("evidence_ids"), _EVIDENCE_ID
    )
    country_pathway_ids = _canonical_id_list(
        country.get("pathway_ids"), _PATHWAY_ID
    )
    if (
        selected_evidence_ids is None
        or selected_pathway_ids is None
        or country_evidence_ids is None
        or country_pathway_ids is None
        or any(item not in country_evidence_ids for item in selected_evidence_ids)
        or any(item not in country_pathway_ids for item in selected_pathway_ids)
    ):
        return _packet_unavailable("bank_manifest_invalid")

    source_index = _unique_index(
        release.get("sources"), id_key="source_id", pattern=_SOURCE_ID
    )
    evidence_index = _unique_index(
        release.get("evidence_records"),
        id_key="evidence_id",
        pattern=_EVIDENCE_ID,
    )
    pathway_index = _unique_index(
        release.get("pathways"), id_key="pathway_id", pattern=_PATHWAY_ID
    )
    if source_index is None or evidence_index is None or pathway_index is None:
        return _packet_unavailable("bank_manifest_invalid")

    normalized_urls: set[str] = set()
    for source in source_index.values():
        normalized_url = _normalized_source_url(source.get("url"))
        if normalized_url is None or normalized_url in normalized_urls:
            return _packet_unavailable("bank_manifest_invalid")
        normalized_urls.add(normalized_url)

    selected_evidence: list[dict[str, Any]] = []
    selected_pathways: list[dict[str, Any]] = []
    supporting_ids: set[str] = set(selected_evidence_ids)
    for pathway_id in selected_pathway_ids:
        pathway = pathway_index.get(pathway_id)
        if (
            pathway is None
            or not _valid_pathway_record(pathway, iso3)
            or not _valid_pathway_refs(pathway, evidence_index)
        ):
            return _packet_unavailable("bank_manifest_invalid")
        selected_pathways.append(pathway)
        supporting_ids.update(pathway["supporting_evidence_ids"])

    source_ids: set[str] = set()
    for evidence_id in sorted(supporting_ids):
        evidence = evidence_index.get(evidence_id)
        if (
            evidence is None
            or not _valid_evidence_record(evidence, iso3)
            or not _valid_evidence_refs(evidence, source_index)
        ):
            return _packet_unavailable("bank_manifest_invalid")
        selected_evidence.append(evidence)
        source_ids.update(ref["source_id"] for ref in evidence["source_refs"])

    selected_sources: list[dict[str, Any]] = []
    for source_id in sorted(source_ids):
        source = source_index[source_id]
        if not _valid_source(source, expected_id=source_id, iso3=iso3):
            return _packet_unavailable("bank_manifest_invalid")
        selected_sources.append(source)

    return {
        "bank_status": "ok",
        "warning_code": "",
        "schema_version": release["schema_version"],
        "content_version": release["content_version"],
        "country_iso3": iso3,
        "country_name": country.get("name", iso3),
        "reviewed_on": country.get("reviewed_on"),
        "review_due": country.get("review_due"),
        "sources": deepcopy(selected_sources),
        "evidence_records": deepcopy(selected_evidence),
        "pathways": deepcopy(selected_pathways),
    }
