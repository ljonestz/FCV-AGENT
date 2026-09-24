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


def test_ipf_seash_guidance_requires_project_specific_authority():
    import background_docs as bd

    stage2 = app.DEFAULT_PROMPTS["2"].replace(
        "{dnh_seash_guidance}", app.get_dnh_seash_guidance("IPF")
    )
    stage3 = app.DEFAULT_PROMPTS["3"].replace(
        "{seash_gender_card_guidance}",
        app.get_seash_gender_card_guidance("IPF"),
    )
    assert "Do not infer a SEA/SH rating from overall E&S risk" in stage2
    assert "An action plan incorporated into an ESIA or ESMP is not missing" in stage2
    assert "Do not treat a missing standalone plan as a gap" in stage3
    assert "the relevant ESCP commitment, if supplied" in stage3
    assert "Set seash_standalone_flag: TRUE if risk is Substantial or High" not in bd.DNH_SEASH_IPF


def test_esf_knowledge_distinguishes_requirements_from_design_options():
    from pathlib import Path
    from runpy import run_path

    knowledge = run_path(
        str(Path(__file__).resolve().parents[1] / "background_docs.py")
    )["SECONDARY_KNOWLEDGE"]
    core = knowledge["esf_framework_core"]["content"]
    assert "ESS4 paragraphs 24-27 govern security personnel" in core
    assert (
        "ESS2 is relevant in FCV settings specifically for its security personnel provisions"
        not in core
    )
    assert "Do not infer a missing security plan from a PAD alone" in core
    assert "A separate or third-party channel is a design option" in core


def test_security_knowledge_keeps_plan_conditional_on_project_instrument():
    from pathlib import Path
    from runpy import run_path

    knowledge = run_path(
        str(Path(__file__).resolve().parents[1] / "background_docs.py")
    )["SECONDARY_KNOWLEDGE"]
    card = knowledge["esf_security_personnel"]["content"]
    assert "Bank and Borrower agree whether a stand-alone SMP is required" in card
    assert "Check the project-specific ESCP before naming a required plan" in card
    assert "A full SMP is required for high-risk projects" not in card
    assert "SMP must be reviewed at each supervision mission" not in card
