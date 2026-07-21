"""Discovery and safe loading for file-based sector-lens packages."""

from __future__ import annotations

from pathlib import Path
import re

import yaml

from .models import (
    DetectionConfig,
    LensActivationMode,
    LensDiagnostic,
    LensCompatibility,
    LensLoadError,
    LensLoadStatus,
    LensMetadata,
    LensQuestion,
    LensRegistry,
    LensSource,
    LensStatus,
    SectorLens,
    StageBudgets,
)
from .budgets import PLATFORM_STAGE_BUDGETS


REQUIRED_FILES = ("manifest.yaml", "questions.yaml", "guidance.md", "sources.yaml")
VALID_MAPPING = re.compile(r"^(?:ost:(?:[1-9]|1[0-2])|dnh:[1-9]|shift:[A-D])$")
VALID_VERSION = re.compile(r"^\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?$")
VALID_ID = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")


class LensPackageError(ValueError):
    """An invalid lens package that should be isolated from other packages."""

    def __init__(self, code: str, message: str, file: str | None = None):
        super().__init__(message)
        self.code = code
        self.file = file


def _read_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise LensPackageError("invalid_yaml", str(exc), path.name) from exc
    if not isinstance(data, dict):
        raise LensPackageError("invalid_yaml", "top-level YAML value must be a mapping", path.name)
    return data


def _validate_lens(lens: SectorLens) -> None:
    """Validate cross-file and platform rules after parsing a package."""

    for stage in (1, 2, 3):
        value = lens.budgets.for_stage(stage)
        if value < 1 or value > PLATFORM_STAGE_BUDGETS.for_stage(stage):
            raise LensPackageError("invalid_budget", f"invalid stage{stage} budget", "manifest.yaml")
    if not lens.guidance.strip():
        raise LensPackageError("missing_guidance", "guidance.md cannot be empty")
    if not lens.questions:
        raise LensPackageError("missing_questions", "questions.yaml must declare at least one question")
    if not lens.sources:
        raise LensPackageError("missing_sources", "sources.yaml must declare at least one source")
    if any(not lens.stage_instructions.get(stage, "").strip() for stage in (1, 2, 3)):
        raise LensPackageError("missing_stage_content", "all three stage instructions are required")
    source_ids = [source.id for source in lens.sources]
    question_ids = [question.id for question in lens.questions]
    if len(source_ids) != len(set(source_ids)) or len(question_ids) != len(set(question_ids)):
        raise LensPackageError("duplicate_id", "source and question IDs must be unique")
    known_sources = set(source_ids)
    if not VALID_ID.match(lens.id):
        raise LensPackageError("invalid_id", "lens ID must be a lowercase URL-safe slug")
    invalid_source_ids = [value for value in source_ids if not VALID_ID.match(value)]
    invalid_question_ids = [value for value in question_ids if not VALID_ID.match(value)]
    if invalid_source_ids or invalid_question_ids:
        invalid = ", ".join((*invalid_source_ids, *invalid_question_ids))
        raise LensPackageError(
            "invalid_id",
            f"source and question IDs must be lowercase URL-safe slugs: {invalid}",
        )
    text_values = [
        lens.id, lens.metadata.name, lens.metadata.description, lens.guidance,
        *lens.metadata.aliases, *lens.detection.keywords, *lens.detection.sector_codes,
        *lens.stage_instructions.values(),
    ]
    text_values.extend(question.text + " " + question.condition for question in lens.questions)
    text_values.extend(
        source.title + " " + source.citation + " " + (source.url or "")
        for source in lens.sources
    )
    if any(
        "%%%" in value or "<script" in value.casefold() or "\x00" in value
        for value in text_values
    ):
        raise LensPackageError("unsafe_content", "module text contains a reserved delimiter or unsafe markup")
    for question in lens.questions:
        if set(question.source_ids) - known_sources:
            raise LensPackageError("missing_source", f"question {question.id!r} references a missing source")
        if any(not VALID_MAPPING.match(value) for value in question.core_mappings):
            raise LensPackageError("invalid_mapping", f"question {question.id!r} has an invalid core mapping")


def _load_package(path: Path) -> SectorLens:
    missing = [name for name in REQUIRED_FILES if not (path / name).is_file()]
    if missing:
        raise LensPackageError("missing_file", f"missing required files: {', '.join(missing)}")

    manifest = _read_yaml(path / "manifest.yaml")
    metadata = LensMetadata(
        id=str(manifest["id"]),
        name=str(manifest["name"]),
        version=str(manifest["version"]),
        description=str(manifest["description"]),
        status=LensStatus(str(manifest["status"])),
        aliases=tuple(str(value) for value in manifest.get("aliases", [])),
        activation=LensActivationMode(str(manifest.get("activation", "suggested"))),
    )
    if not all((metadata.id, metadata.name, metadata.version, metadata.description)):
        raise LensPackageError("missing_metadata", "lens metadata fields cannot be empty", "manifest.yaml")
    if not VALID_VERSION.match(metadata.version):
        raise LensPackageError("invalid_version", "version must use semantic version syntax", "manifest.yaml")
    if metadata.id != path.name:
        raise LensPackageError(
            "id_mismatch",
            f"manifest id {metadata.id!r} does not match directory {path.name!r}",
            "manifest.yaml",
        )

    detection_data = manifest.get("detection", {})
    detection = DetectionConfig(
        keywords=tuple(str(value) for value in detection_data.get("keywords", [])),
        sector_codes=tuple(str(value) for value in detection_data.get("sector_codes", [])),
        threshold=int(detection_data.get("threshold", 1)),
    )
    if detection.threshold < 1:
        raise LensPackageError("invalid_detection", "detection threshold must be positive", "manifest.yaml")
    budget_data = manifest["budgets"]
    budgets = StageBudgets(
        stage1=int(budget_data["stage1"]),
        stage2=int(budget_data["stage2"]),
        stage3=int(budget_data["stage3"]),
    )
    for stage in (1, 2, 3):
        value = budgets.for_stage(stage)
        if value < 1 or value > PLATFORM_STAGE_BUDGETS.for_stage(stage):
            raise LensPackageError(
                "invalid_budget",
                f"stage{stage} budget must be between 1 and {PLATFORM_STAGE_BUDGETS.for_stage(stage)}",
                "manifest.yaml",
            )
    instruction_data = manifest.get("stage_instructions", {})
    stage_instructions = {
        stage: str(instruction_data.get(f"stage{stage}", "")).strip()
        for stage in (1, 2, 3)
    }
    compatibility_data = manifest.get("compatibility", {}) or {}
    compatibility = LensCompatibility(
        compatible_with=tuple(str(value) for value in compatibility_data.get("compatible_with", ["*"])),
        incompatible_with=tuple(str(value) for value in compatibility_data.get("incompatible_with", [])),
    )

    source_data = _read_yaml(path / "sources.yaml").get("sources", [])
    sources = tuple(
        LensSource(
            id=str(item["id"]),
            title=str(item["title"]),
            citation=str(item.get("citation", "")),
            url=str(item["url"]) if item.get("url") else None,
        )
        for item in source_data
    )
    source_ids = [source.id for source in sources]
    if len(source_ids) != len(set(source_ids)):
        raise LensPackageError("duplicate_id", "source IDs must be unique", "sources.yaml")
    question_data = _read_yaml(path / "questions.yaml").get("questions", [])
    questions = tuple(
        LensQuestion(
            id=str(item["id"]),
            text=str(item["text"]),
            source_ids=tuple(str(value) for value in item.get("source_ids", [])),
            core_mappings=tuple(str(value) for value in item.get("core_mappings", [])),
            priority=int(item.get("priority", 100)),
            condition=str(item.get("condition", "always")).strip() or "always",
        )
        for item in question_data
    )
    question_ids = [question.id for question in questions]
    if len(question_ids) != len(set(question_ids)):
        raise LensPackageError("duplicate_id", "question IDs must be unique", "questions.yaml")
    known_sources = set(source_ids)
    for question in questions:
        missing_sources = set(question.source_ids) - known_sources
        if missing_sources:
            raise LensPackageError(
                "missing_source",
                f"question {question.id!r} references missing sources: {', '.join(sorted(missing_sources))}",
                "questions.yaml",
            )
        invalid_mappings = [value for value in question.core_mappings if not VALID_MAPPING.match(value)]
        if invalid_mappings:
            raise LensPackageError(
                "invalid_mapping",
                f"question {question.id!r} has invalid core mappings: {', '.join(invalid_mappings)}",
                "questions.yaml",
            )

    lens = SectorLens(
        metadata=metadata,
        detection=detection,
        budgets=budgets,
        stage_instructions=stage_instructions,
        guidance=(path / "guidance.md").read_text(encoding="utf-8").strip(),
        questions=questions,
        sources=sources,
        path=path,
        compatibility=compatibility,
    )
    _validate_lens(lens)
    return lens


def load_registry(root: str | Path) -> LensRegistry:
    """Load every direct child package while quarantining invalid packages."""

    root_path = Path(root)
    lenses: dict[str, SectorLens] = {}
    diagnostics: list[LensDiagnostic] = []
    try:
        if not root_path.exists():
            return LensRegistry(root=root_path, lenses=lenses, diagnostics=())
        package_paths = sorted(
            (entry for entry in root_path.iterdir() if entry.is_dir()),
            key=lambda item: item.name,
        )
    except OSError as exc:
        return LensRegistry(
            root=root_path,
            lenses={},
            diagnostics=(LensDiagnostic(
                module_id="<registry>",
                status=LensLoadStatus.INVALID,
                errors=(LensLoadError("registry_unavailable", str(exc)),),
            ),),
        )

    for path in package_paths:
        try:
            lens = _load_package(path)
        except (KeyError, TypeError, ValueError, OSError, LensPackageError) as exc:
            if isinstance(exc, LensPackageError):
                error = LensLoadError(code=exc.code, message=str(exc), file=exc.file)
            else:
                error = LensLoadError(code="invalid_package", message=str(exc))
            diagnostics.append(
                LensDiagnostic(module_id=path.name, status=LensLoadStatus.INVALID, errors=(error,))
            )
            continue

        if lens.id in lenses:
            diagnostics.append(
                LensDiagnostic(
                    module_id=path.name,
                    status=LensLoadStatus.INVALID,
                    errors=(LensLoadError("duplicate_id", f"duplicate lens ID: {lens.id}"),),
                )
            )
            continue
        lenses[lens.id] = lens
        status = LensLoadStatus.LOADED if lens.enabled else LensLoadStatus.DISABLED
        diagnostics.append(LensDiagnostic(module_id=lens.id, status=status))

    return LensRegistry(root=root_path, lenses=lenses, diagnostics=tuple(diagnostics))
