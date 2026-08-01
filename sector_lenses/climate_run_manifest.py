"""Reproducibility manifest and privacy-safe Climate-FCV telemetry."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    schema_version: str
    prompt_versions: dict[str, str]
    reviewer_version: str
    extraction_version: str
    normalization_version: str
    renderer_version: str
    model_aliases: dict[str, str]
    sampling: dict[str, int | float | str]
    source_fingerprints: tuple[str, ...]
    applicability_fingerprint: str
    bank_release_id: str | None
    live_research_timestamps: tuple[str, ...]
    validation_reason_codes: tuple[str, ...]
    repair_actions: tuple[str, ...]
    suppressed_counts: dict[str, int]
    latency_ms: dict[str, int]
    token_usage: dict[str, int]
    cache_state: dict[str, str]


def build_cache_key(
    *,
    source_fingerprints: tuple[str, ...],
    schema_version: str,
    prompt_version: str,
    reviewer_version: str,
    model_alias: str,
    applicability_fingerprint: str,
) -> str:
    payload = json.dumps(
        {
            "source_fingerprints": sorted(source_fingerprints),
            "schema_version": schema_version,
            "prompt_version": prompt_version,
            "reviewer_version": reviewer_version,
            "model_alias": model_alias,
            "applicability_fingerprint": applicability_fingerprint,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def safe_log_summary(manifest: RunManifest) -> dict[str, object]:
    data = asdict(manifest)
    return {
        "run_id": data["run_id"],
        "schema_version": data["schema_version"],
        "prompt_versions": data["prompt_versions"],
        "reviewer_version": data["reviewer_version"],
        "extraction_version": data["extraction_version"],
        "normalization_version": data["normalization_version"],
        "renderer_version": data["renderer_version"],
        "model_aliases": data["model_aliases"],
        "source_count": len(data["source_fingerprints"]),
        "applicability_fingerprint": data["applicability_fingerprint"],
        "bank_release_id": data["bank_release_id"],
        "live_research_count": len(data["live_research_timestamps"]),
        "validation_reason_codes": list(data["validation_reason_codes"]),
        "repair_actions": list(data["repair_actions"]),
        "suppressed_counts": data["suppressed_counts"],
        "latency_ms": data["latency_ms"],
        "token_usage": data["token_usage"],
        "cache_state": data["cache_state"],
    }
