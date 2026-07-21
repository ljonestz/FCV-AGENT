"""Resolve active lenses and compose bounded stage-specific prompt slices."""

from __future__ import annotations

from math import ceil
from typing import Iterable, Mapping, Sequence

from .budgets import MAX_ACTIVE_LENSES, PLATFORM_STAGE_BUDGETS
from .models import (
    ActiveLensSelection,
    LensRegistry,
    LensSelectionWarning,
    SectorLens,
    StageSlice,
)


def estimate_tokens(text: str) -> int:
    """Use a conservative, dependency-free approximation for input budgeting."""

    return ceil(len(text) / 4) if text else 0


def resolve_active_lenses(
    registry: LensRegistry,
    requested_ids: Iterable[str] | None,
    expected_versions: Mapping[str, str] | None = None,
) -> ActiveLensSelection:
    """Resolve ordered IDs against authoritative server modules without blocking core analysis."""

    requested = tuple(str(value) for value in (requested_ids or ()))
    versions = expected_versions or {}
    selected: list[SectorLens] = []
    warnings: list[LensSelectionWarning] = []
    seen: set[str] = set()

    for lens_id in requested:
        if lens_id in seen:
            continue
        seen.add(lens_id)
        lens = registry.get(lens_id)
        if lens is None:
            warnings.append(
                LensSelectionWarning(
                    "unknown_lens",
                    f"Sector lens '{lens_id}' is unknown and was ignored.",
                    lens_id,
                )
            )
            continue
        if not lens.enabled:
            warnings.append(
                LensSelectionWarning(
                    "disabled_lens",
                    f"Sector lens '{lens_id}' is disabled and was ignored.",
                    lens_id,
                )
            )
            continue
        expected = versions.get(lens_id)
        if expected and expected != lens.version:
            warnings.append(
                LensSelectionWarning(
                    "version_mismatch",
                    f"Sector lens '{lens_id}' uses server version {lens.version}, not {expected}.",
                    lens_id,
                )
            )
        if len(selected) >= MAX_ACTIVE_LENSES:
            warnings.append(
                LensSelectionWarning(
                    "lens_limit",
                    f"At most {MAX_ACTIVE_LENSES} sector lenses may be active; '{lens_id}' was ignored.",
                    lens_id,
                )
            )
            continue
        incompatible = next((
            other for other in selected
            if (
                other.id in lens.compatibility.incompatible_with
                or lens.id in other.compatibility.incompatible_with
                or (
                    "*" not in lens.compatibility.compatible_with
                    and other.id not in lens.compatibility.compatible_with
                )
                or (
                    "*" not in other.compatibility.compatible_with
                    and lens.id not in other.compatibility.compatible_with
                )
            )
        ), None)
        if incompatible:
            warnings.append(
                LensSelectionWarning(
                    "incompatible_lens",
                    f"Sector lens '{lens_id}' is incompatible with '{incompatible.id}' and was ignored.",
                    lens_id,
                )
            )
            continue
        selected.append(lens)

    return ActiveLensSelection(requested, tuple(selected), tuple(warnings))


def _lens_blocks(lens: SectorLens, stage: int) -> list[tuple[str | None, str]]:
    heading = f"### Sector lens: {lens.metadata.name} ({lens.id}, v{lens.version})"
    instruction = lens.stage_instructions.get(stage, "").strip()
    blocks: list[tuple[str | None, str]] = [(None, heading)]
    if instruction:
        blocks.append((None, instruction))
    if stage == 2:
        if lens.readout_sections:
            lines = [
                f"- {section.id}: {section.title}; allowed items: "
                f"{', '.join(section.item_ids)}"
                for section in lens.readout_sections
            ]
            blocks.append((
                None,
                "Declared diagnostic readout sections:\n" + "\n".join(lines),
            ))
        if lens.guidance:
            blocks.append((None, f"Guidance:\n{lens.guidance}"))
        source_lookup = {source.id: source for source in lens.sources}
        for question in sorted(lens.questions, key=lambda item: (item.priority, item.id)):
            sources = ", ".join(question.source_ids) or "none"
            mappings = ", ".join(question.core_mappings) or "none"
            blocks.append(
                (
                    question.id,
                    f"Question [{question.id}]: {question.text}\n"
                    f"Condition: {question.condition}\n"
                    f"Source IDs: {sources}\nCore mappings: {mappings}",
                )
            )
        cited = [
            f"- [{source_id}] {source_lookup[source_id].title}"
            for source_id in sorted(source_lookup)
        ]
        if cited:
            blocks.append((None, "Declared sources:\n" + "\n".join(cited)))
    return blocks


def build_stage_slice(
    lenses: Sequence[SectorLens], stage: int, token_limit: int | None = None
) -> StageSlice:
    """Compose deterministic content within platform and per-module token ceilings."""

    if stage not in (1, 2, 3):
        raise ValueError(f"unsupported stage: {stage}")
    if len(lenses) > MAX_ACTIVE_LENSES:
        raise ValueError(f"at most {MAX_ACTIVE_LENSES} sector lenses may be active")
    if not lenses:
        return StageSlice(stage, "", 0, ())

    platform_limit = PLATFORM_STAGE_BUDGETS.for_stage(stage)
    if token_limit is not None:
        platform_limit = min(platform_limit, max(1, token_limit))
    shares = (platform_limit,) if len(lenses) == 1 else (
        platform_limit * 2 // 3,
        max(1, platform_limit - (platform_limit * 2 // 3) - 1),
    )
    sections: list[str] = []
    omitted: list[str] = []
    truncated = False

    for lens, share in zip(lenses, shares):
        lens_limit = min(share, lens.budgets.for_stage(stage))
        accepted: list[str] = []
        for question_id, block in _lens_blocks(lens, stage):
            candidate = "\n\n".join((*accepted, block))
            if estimate_tokens(candidate) <= lens_limit:
                accepted.append(block)
            else:
                truncated = True
                if question_id:
                    omitted.append(question_id)
        if accepted:
            sections.append("\n\n".join(accepted))

    content = "\n\n".join(sections)
    if estimate_tokens(content) > platform_limit:
        raise ValueError("stage slice exceeded the platform token ceiling")
    return StageSlice(
        stage=stage,
        content=content,
        estimated_tokens=estimate_tokens(content),
        lens_ids=tuple(lens.id for lens in lenses),
        truncated=truncated,
        omitted_question_ids=tuple(omitted),
    )
