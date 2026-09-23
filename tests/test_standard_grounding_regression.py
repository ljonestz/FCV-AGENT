"""Guard against prompt instructions that promote unverified project facts into obligations."""

import re

import app


def test_stage1_and_stage2_preserve_instrument_status_and_document_limits():
    stage1 = app.append_standard_fcv_stage_context(app.DEFAULT_PROMPTS["1"], 1, [])
    stage2 = app.append_standard_fcv_stage_context(app.DEFAULT_PROMPTS["2"], 2, [])
    assert "HEIS approval is not activation" in stage1
    assert "HEIS approval is not activation" in stage2
    assert "activation unverified from this document" in re.sub(r"\s+", " ", stage1)
    assert "activation unverified from this document" in re.sub(r"\s+", " ", stage2)
    assert "not proof that no separate security plan exists" in stage2
    assert "Security Management Plan, TPM/GEMS" not in stage2
    assert "planned GBV Action Plan alone is not a sequencing gap" in stage2


def test_stage3_removes_conflicting_forced_precision_and_sort_routing():
    prompt = app.append_core_concise_stage3_contract(
        app.DEFAULT_PROMPTS["3"], "PAD", {}, "design", []
    )
    assert "Name specific actors, locations, mechanisms, or thresholds where possible" not in prompt
    assert "SORT ROUTING: Any recommendation" not in prompt
    assert "Security Management Plan, TPM/GEMS" not in prompt
    assert "Do not use SORT as an incident log" in prompt
    assert "not source-grounded, leave its target for the team to define" in prompt


def test_playbook_prompt_treats_prior_analysis_as_unverified():
    prompt = app.DEFAULT_PROMPTS["deeper_playbook"]
    assert "The prior screening is an unverified analytical input" in prompt
    assert "Approval or a request is not evidence of activation or nonactivation" in prompt
    assert "do not invent a policy obligation" in prompt
