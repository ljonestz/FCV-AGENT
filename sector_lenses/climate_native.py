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


_MISSING = object()


def _value_at_path(value: Any, path: tuple[str, ...]) -> Any:
    current = value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return _MISSING
        current = current[key]
    return current


def _set_path(
    target: dict[str, Any],
    path: tuple[str, ...],
    value: Any,
) -> None:
    current = target
    for key in path[:-1]:
        child = current.get(key)
        if not isinstance(child, dict):
            child = {}
            current[key] = child
        current = child
    current[path[-1]] = deepcopy(value)


def merge_climate_repair(
    primary: dict[str, Any],
    repair: dict[str, Any],
    requested_fields: list[str],
) -> dict[str, Any]:
    """Deep-copy only explicitly requested canonical Climate paths."""

    result = deepcopy(primary) if isinstance(primary, dict) else {}
    incoming = repair if isinstance(repair, dict) else {}
    allowed = set(requested_fields)

    if "schema_version" in allowed and "schema_version" in incoming:
        result["schema_version"] = deepcopy(incoming["schema_version"])

    repair_baseline = incoming.get("fcv_baseline")
    if "fcv_baseline" in allowed and isinstance(repair_baseline, dict):
        result["fcv_baseline"] = deepcopy(repair_baseline)
    else:
        for requested in sorted(allowed):
            prefix = "fcv_baseline."
            if not requested.startswith(prefix):
                continue
            relative_path = tuple(requested[len(prefix):].split("."))
            incoming_value = _value_at_path(
                repair_baseline, relative_path
            )
            if incoming_value is _MISSING:
                continue
            result_baseline = result.get("fcv_baseline")
            if not isinstance(result_baseline, dict):
                result_baseline = {}
                result["fcv_baseline"] = result_baseline
            _set_path(result_baseline, relative_path, incoming_value)

    raw_result_lenses = result.get("lenses")
    result_lenses = (
        raw_result_lenses
        if isinstance(raw_result_lenses, list)
        else None
    )
    repair_climate = _climate_lens(incoming)
    result_climate = _climate_lens(result)

    if "lenses.climate" in allowed and isinstance(repair_climate, dict):
        replacement_lens = deepcopy(repair_climate)
        if result_lenses is None:
            result_lenses = []
            result["lenses"] = result_lenses
        if result_climate is None:
            result_lenses.append(replacement_lens)
        else:
            climate_index = next(
                index
                for index, item in enumerate(result_lenses)
                if item is result_climate
            )
            result_lenses[climate_index] = replacement_lens
        result_climate = replacement_lens
    else:
        for requested in sorted(allowed):
            prefix = "lenses.climate."
            if not requested.startswith(prefix):
                continue
            relative_path = tuple(requested[len(prefix):].split("."))
            incoming_value = _value_at_path(
                repair_climate, relative_path
            )
            if incoming_value is _MISSING:
                continue
            if result_climate is None:
                if result_lenses is None:
                    result_lenses = []
                    result["lenses"] = result_lenses
                result_climate = {"lens_id": "climate"}
                result_lenses.append(result_climate)
            _set_path(result_climate, relative_path, incoming_value)

    if not isinstance(result.get("findings"), list):
        result["findings"] = []
    return result
