from sector_lenses.climate_analysis_prompts import build_analysis_prompt


def test_analysis_prompt_makes_evidence_entitlements_explicit():
    prompt = build_analysis_prompt(
        project_facts=[{"claim_id": "PF-001", "subject": "landing site"}],
        derived_assertions=[],
        context_evidence=[{
            "evidence_id": "CE-001",
            "evidence_class": "country",
            "scope": "national",
            "statement": "Flood exposure is widespread.",
        }],
    )
    assert "Country evidence may support plausible context and pathways" in prompt
    assert "must not establish a project site fact" in prompt
    assert "Represent every material documented response" in prompt
    assert "maximum three pathways in each direction" in prompt
    assert "maximum eight residual gaps" in prompt


def test_existing_responses_precede_residual_gaps():
    prompt = build_analysis_prompt([], [], [])
    assert prompt.index("existing_response_register") < prompt.index(
        "residual_gap_register"
    )
