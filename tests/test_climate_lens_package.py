"""Contract tests for the production Climate-FCV lens package."""

from pathlib import Path

from sector_lenses import (
    LensActivationMode,
    build_stage_slice,
    load_registry,
)


MODULE_ROOT = Path(__file__).resolve().parents[1] / "sector_lenses" / "modules"


def test_climate_package_is_enabled_manual_and_bounded():
    climate = load_registry(MODULE_ROOT).get("climate")

    assert climate is not None
    assert climate.enabled is True
    assert climate.version == "1.1.0"
    assert climate.metadata.activation is LensActivationMode.MANUAL
    assert [section.id for section in climate.readout_sections] == [
        "invest-in", "deliver-through",
    ]
    assert [section.title for section in climate.readout_sections] == [
        "Where the project could build climate, peace, and social dividends",
        "How project design and delivery could strengthen those dividends",
    ]
    for stage, ceiling in ((1, 600), (2, 2000), (3, 1200)):
        assert build_stage_slice([climate], stage).estimated_tokens <= ceiling


def test_climate_package_has_complete_sources_and_question_families():
    climate = load_registry(MODULE_ROOT).get("climate")

    assert {source.id for source in climate.sources} == {
        "peace-social-dividends", "ccdr-fcv-approach",
        "fcv-climate-compendium", "defueling-conflict",
        "defueling-field-notes", "adelphi-conflict-sensitivity",
        "cgiar-climate-security", "adaptation-review",
    }
    assert len(climate.questions) == 19
    assert all(
        question.source_ids and question.core_mappings
        for question in climate.questions
    )


def test_source_notes_are_auditable_but_never_enter_runtime_prompts():
    climate = load_registry(MODULE_ROOT).get("climate")
    note = climate.path / "source_notes" / "peace_social_dividends.md"

    assert "Audit-only anchor: triple-burden proportionality test." in note.read_text(
        encoding="utf-8"
    )
    for stage in (1, 2, 3):
        assert "Audit-only anchor: triple-burden proportionality test." not in (
            build_stage_slice([climate], stage).content
        )


def test_climate_package_requires_causal_pathways_and_time_horizons():
    climate = load_registry(MODULE_ROOT).get("climate")
    stage2 = build_stage_slice([climate], 2).content

    assert "pathway_id" in stage2
    assert "pressure" in stage2
    assert "project implication" in stage2
    assert "design response" in stage2
    assert "current-near-term" in stage2
    assert "project-lifetime" in stage2
    assert "asset-system-lifetime" in stage2


def test_stage_instructions_reference_reflections_and_dedicated_focus():
    climate = load_registry(MODULE_ROOT).get("climate")
    s2 = climate.stage_instructions.get(2, "")
    s3 = climate.stage_instructions.get(3, "")
    assert "reflection" in s2.lower()
    assert "intersection" in s2.lower()
    assert "prose" in s3.lower()
    assert "causal strip" not in (s2 + s3).lower()
    for stage, ceiling in ((1, 600), (2, 2000), (3, 1200)):
        assert build_stage_slice([climate], stage).estimated_tokens <= ceiling
