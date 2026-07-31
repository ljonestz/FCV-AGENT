"""Regression tests for CERC recommendations in FCV screening prompts."""

import app
import background_docs
from sector_lenses.climate_native import (
    build_climate_stage2_prompt,
    build_climate_stage3_prompt,
)


def test_stage_prompts_prohibit_cerc_for_violence_escalation_alone():
    combined = "\n".join([
        app.DEFAULT_PROMPTS["2"],
        app.DEFAULT_PROMPTS["3"],
    ])

    assert "Do NOT recommend a CERC for violence/conflict escalation alone" in combined
    assert "Do NOT flag the absence of CERC readiness as a gap" in combined
    assert "natural-hazard, climate, health, or economic" in combined
    assert "adaptive management, restructuring, SORT updating, and security planning" in combined


def test_cerc_calibration_names_violence_trigger_limit():
    calibration = background_docs.FCV_INSTRUMENT_CALIBRATION

    assert "Do not flag CERC absence as a gap on the basis of conflict escalation" in calibration
    assert "natural-hazard, climate, health, or economic emergency" in calibration
    assert "borrower emergency declaration/request pathway" in calibration


def test_cerc_secondary_knowledge_removes_nonstandard_trigger_workarounds():
    cerc_guidance = background_docs.SECONDARY_KNOWLEDGE["cerc_guidance"]["content"]

    assert "UN Flash Appeal" not in cerc_guidance
    assert "certified statement of facts" not in cerc_guidance
    assert "natural-hazard, climate, health, or economic emergency" in cerc_guidance
    assert "not an escalation of armed conflict, civil unrest, or insecurity alone" in cerc_guidance


def test_no_background_guidance_treats_conflict_escalation_as_cerc_trigger():
    risky_blocks = "\n".join([
        background_docs.WB_INSTRUMENT_GUIDE["IPF"]["ost_applicability"],
        background_docs.DIFFERENTIATED_APPROACHES,
        background_docs.SECONDARY_KNOWLEDGE["procurement_fcv"]["content"],
    ])

    assert "absence should be flagged" not in risky_blocks
    assert "if conflict escalates" not in risky_blocks
    assert "inclusion of a CERC component to enable rapid reallocation" not in risky_blocks


def test_climate_prompts_separate_cerc_from_conflict_response():
    stage2 = build_climate_stage2_prompt(
        instrument_type="IPF",
        document_type="PCN",
        temporal_guardrail="Preparation stage.",
        regime_header="",
        project_signals="South Sudan fisheries project.",
        climate_research={},
        priority_questions=[],
    )
    stage3 = build_climate_stage3_prompt(
        instrument_type="IPF",
        document_type="PCN",
        diagnostic={},
        regime_header="",
    )

    for prompt in (stage2, stage3):
        assert "Never combine a CERC" in prompt
        assert "conflict escalation, insecurity, civil unrest" in prompt
        assert "adaptive management, restructuring, SORT updating" in prompt
        assert (
            "named eligible natural-hazard, climate, health, or economic"
            in prompt
        )
