"""Server-only model routing for the verified Climate-FCV pipeline."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os


QUALITY_MODEL = "claude-sonnet-4-6"
SMOKE_MODEL = "claude-haiku-4-5-20251001"
_ALLOWED_MODES = {"quality", "smoke"}


@dataclass(frozen=True)
class VerifiedClimateRuntime:
    """Immutable runtime settings selected from the server environment."""

    mode: str
    assessment_model: str
    reviewer_model: str


def load_verified_climate_runtime(
    environment: Mapping[str, str] | None = None,
) -> VerifiedClimateRuntime:
    """Load the verified runtime without accepting browser request values."""

    values = os.environ if environment is None else environment
    mode = str(values.get("CLIMATE_VERIFIED_RUN_MODE") or "quality").strip().lower()
    if mode not in _ALLOWED_MODES:
        raise ValueError(
            "CLIMATE_VERIFIED_RUN_MODE must be either 'quality' or 'smoke'"
        )
    default_model = SMOKE_MODEL if mode == "smoke" else QUALITY_MODEL
    assessment_model = str(
        values.get("CLIMATE_VERIFIED_ASSESSMENT_MODEL") or default_model
    ).strip()
    reviewer_model = str(
        values.get("CLIMATE_VERIFIED_REVIEW_MODEL") or default_model
    ).strip()
    if not assessment_model or not reviewer_model:
        raise ValueError("Verified Climate-FCV model names must not be blank")
    return VerifiedClimateRuntime(
        mode=mode,
        assessment_model=assessment_model,
        reviewer_model=reviewer_model,
    )
