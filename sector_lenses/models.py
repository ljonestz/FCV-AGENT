"""Typed value objects for sector-lens packages and registry diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Mapping


class LensStatus(str, Enum):
    """Whether a valid lens is available for runtime selection."""

    ENABLED = "enabled"
    DISABLED = "disabled"


class LensLoadStatus(str, Enum):
    """Outcome recorded while discovering a module directory."""

    LOADED = "loaded"
    DISABLED = "disabled"
    INVALID = "invalid"


@dataclass(frozen=True)
class StageBudgets:
    """Estimated-token ceilings for the three analysis stages."""

    stage1: int
    stage2: int
    stage3: int

    def for_stage(self, stage: int) -> int:
        """Return the configured ceiling for a one-based stage number."""

        try:
            return {1: self.stage1, 2: self.stage2, 3: self.stage3}[stage]
        except KeyError as exc:
            raise ValueError(f"unsupported stage: {stage}") from exc


@dataclass(frozen=True)
class DetectionConfig:
    """Deterministic signals available to a future lens detector."""

    keywords: tuple[str, ...] = ()
    sector_codes: tuple[str, ...] = ()
    threshold: int = 1


@dataclass(frozen=True)
class LensCompatibility:
    """Declarative two-lens compatibility constraints."""

    compatible_with: tuple[str, ...] = ("*",)
    incompatible_with: tuple[str, ...] = ()


@dataclass(frozen=True)
class LensMetadata:
    """Identity and release metadata read from ``manifest.yaml``."""

    id: str
    name: str
    version: str
    description: str
    status: LensStatus
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class LensQuestion:
    """A structured Stage-2 diagnostic question."""

    id: str
    text: str
    source_ids: tuple[str, ...]
    core_mappings: tuple[str, ...] = ()
    priority: int = 100
    condition: str = "always"


@dataclass(frozen=True)
class LensSource:
    """A citable source declared by a lens package."""

    id: str
    title: str
    citation: str = ""
    url: str | None = None


@dataclass(frozen=True)
class SectorLens:
    """A fully parsed and validated runtime lens."""

    metadata: LensMetadata
    detection: DetectionConfig
    budgets: StageBudgets
    stage_instructions: Mapping[int, str]
    guidance: str
    questions: tuple[LensQuestion, ...]
    sources: tuple[LensSource, ...]
    path: Path
    compatibility: LensCompatibility = field(default_factory=LensCompatibility)

    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def version(self) -> str:
        return self.metadata.version

    @property
    def enabled(self) -> bool:
        return self.metadata.status is LensStatus.ENABLED


@dataclass(frozen=True)
class LensLoadError:
    """One actionable validation or parsing problem for a module."""

    code: str
    message: str
    file: str | None = None


@dataclass(frozen=True)
class LensDiagnostic:
    """Load status retained even when a module cannot be activated."""

    module_id: str
    status: LensLoadStatus
    errors: tuple[LensLoadError, ...] = ()


@dataclass(frozen=True)
class LensRegistry:
    """Successfully parsed lenses plus non-fatal discovery diagnostics."""

    root: Path
    lenses: Mapping[str, SectorLens] = field(default_factory=dict)
    diagnostics: tuple[LensDiagnostic, ...] = ()

    def get(self, lens_id: str) -> SectorLens | None:
        return self.lenses.get(lens_id)

    @property
    def enabled_lenses(self) -> tuple[SectorLens, ...]:
        return tuple(lens for lens in self.lenses.values() if lens.enabled)


@dataclass(frozen=True)
class ActiveLensSelection:
    """Server-resolved lenses; versions always come from registry entries."""

    requested_ids: tuple[str, ...]
    lenses: tuple[SectorLens, ...]
    warnings: tuple["LensSelectionWarning", ...] = ()

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(lens.id for lens in self.lenses)

    @property
    def server_versions(self) -> Mapping[str, str]:
        return {lens.id: lens.version for lens in self.lenses}


@dataclass(frozen=True)
class StageSlice:
    """Bounded, deterministic runtime content for one analysis stage."""

    stage: int
    content: str
    estimated_tokens: int
    lens_ids: tuple[str, ...]
    truncated: bool = False
    omitted_question_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class LensSelectionWarning:
    """A non-fatal problem encountered while resolving client lens IDs."""

    code: str
    message: str
    lens_id: str | None = None
