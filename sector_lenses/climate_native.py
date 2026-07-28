"""Pure contracts for the dedicated Climate-FCV route."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


CLIMATE_NATIVE_SCHEMA_VERSION = "climate-native-v1"
CLIMATE_REQUIRED_DIRECTIONS = {
    "climate-fcv-on-project",
    "project-on-climate-fcv",
}
CLIMATE_REQUIRED_LENS_FIELDS = {
    "materiality_level",
    "materiality_summary",
    "executive_summary",
    "integration_rating",
    "integration_summary",
    "operating_context",
    "interaction_readout",
    "strengths_weaknesses",
    "reflections",
}
_CLIMATE_BASELINE_FIELDS = (
    "sensitivity_rating",
    "responsiveness_rating",
    "sensitivity_reasoning",
    "responsiveness_reasoning",
    "evidence_trail",
)
_CLIMATE_CONTEXT_FIELDS = (
    "fcv_setting",
    "climate_setting",
    "intersection",
)


def _climate_lens(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    lenses = payload.get("lenses")
    if not isinstance(lenses, list):
        return None
    return next(
        (
            item
            for item in lenses
            if isinstance(item, dict) and item.get("lens_id") == "climate"
        ),
        None,
    )


def climate_missing_fields(payload: Any) -> list[str]:
    """Return stable dotted paths absent from a canonical Climate payload."""

    if not isinstance(payload, dict):
        return ["schema_version", "fcv_baseline", "lenses.climate"]

    missing: list[str] = []
    if payload.get("schema_version") != CLIMATE_NATIVE_SCHEMA_VERSION:
        missing.append("schema_version")

    baseline = payload.get("fcv_baseline")
    if not isinstance(baseline, dict):
        missing.append("fcv_baseline")
    else:
        for key in _CLIMATE_BASELINE_FIELDS:
            if not baseline.get(key):
                missing.append(f"fcv_baseline.{key}")

    climate = _climate_lens(payload)
    if climate is None:
        missing.append("lenses.climate")
        return missing

    for key in sorted(CLIMATE_REQUIRED_LENS_FIELDS):
        if not climate.get(key):
            missing.append(f"lenses.climate.{key}")

    operating_context = climate.get("operating_context")
    if isinstance(operating_context, dict):
        for key in _CLIMATE_CONTEXT_FIELDS:
            if not operating_context.get(key):
                missing.append(f"lenses.climate.operating_context.{key}")

    interactions = climate.get("interaction_readout")
    directions = {
        item.get("direction_id")
        for item in interactions
        if isinstance(item, dict)
    } if isinstance(interactions, list) else set()
    for direction in sorted(CLIMATE_REQUIRED_DIRECTIONS - directions):
        missing.append(f"lenses.climate.interaction_readout.{direction}")
    return missing


def merge_climate_repair(
    primary: dict[str, Any],
    repair: dict[str, Any],
    requested_fields: list[str],
) -> dict[str, Any]:
    """Merge only explicitly requested canonical Climate sections."""

    result = deepcopy(primary) if isinstance(primary, dict) else {}
    incoming = repair if isinstance(repair, dict) else {}
    allowed = set(requested_fields)

    if "schema_version" in allowed:
        result["schema_version"] = incoming.get("schema_version")

    baseline_requested = any(
        path == "fcv_baseline" or path.startswith("fcv_baseline.")
        for path in allowed
    )
    if baseline_requested:
        existing_baseline = result.get("fcv_baseline")
        repair_baseline = incoming.get("fcv_baseline")
        result["fcv_baseline"] = {
            **(
                existing_baseline
                if isinstance(existing_baseline, dict)
                else {}
            ),
            **(
                repair_baseline
                if isinstance(repair_baseline, dict)
                else {}
            ),
        }

    result_lenses = result.get("lenses")
    if not isinstance(result_lenses, list):
        result_lenses = []
        result["lenses"] = result_lenses
    result_climate = _climate_lens(result)
    repair_climate = _climate_lens(incoming)
    climate_paths = sorted(
        path for path in allowed if path.startswith("lenses.climate.")
    )
    if (
        result_climate is None
        and climate_paths
        and isinstance(repair_climate, dict)
    ):
        result_climate = {"lens_id": "climate"}
        result_lenses.append(result_climate)

    if isinstance(result_climate, dict) and isinstance(repair_climate, dict):
        for path in climate_paths:
            key = path[len("lenses.climate."):].split(".", 1)[0]
            if key in repair_climate:
                result_climate[key] = deepcopy(repair_climate[key])

    if not isinstance(result.get("findings"), list):
        result["findings"] = []
    return result
