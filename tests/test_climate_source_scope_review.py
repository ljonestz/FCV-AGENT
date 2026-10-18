from sector_lenses.climate_verified_prompts import build_verified_stage_prompt


MARKER = "SOURCE-TO-CLAIM COMPARISON"
REVIEW_STAGES = {"conditional_review", "reader_review"}
OTHER_STAGES = {
    "fact_extraction",
    "bounded_analysis",
    "judgment_review",
    "recommendation_compiler",
    "reader_compiler",
    "reader_correction",
    "drafting_compiler",
}


def _prompt(stage: str) -> str:
    return build_verified_stage_prompt(stage, {"payload_sentinel": "PAYLOAD-ONLY"})


def test_source_to_claim_comparison_is_scoped_to_review_stages():
    for stage in REVIEW_STAGES:
        assert _prompt(stage).count(MARKER) == 1
    for stage in OTHER_STAGES:
        assert MARKER not in _prompt(stage)


def test_source_to_claim_comparison_has_generic_distinctions_without_case_labels():
    prompt = _prompt("conditional_review")
    block = prompt.split(MARKER, 1)[1].split("\n\nSECURITY AND OUTPUT RULES", 1)[0]

    for required in (
        "population",
        "site",
        "activity",
        "status",
        "affected subgroup",
        "generic safeguards",
        "risk-specific measure",
        "failed protection",
        "qualified analytical inferences",
        "narrow correction",
    ):
        assert required in block
    for case_label in ("Kasindi", "Burundi", "REC-003", "NARR-inclusion"):
        assert case_label not in block


def test_review_prompts_retain_existing_contract_and_payload_boundary():
    conditional = _prompt("conditional_review")
    reader = _prompt("reader_review")

    assert "Act as a source-first verifier, not an editor." in conditional
    assert "Independently verify every final reader paragraph" in reader
    for prompt in (conditional, reader):
        assert prompt.index(MARKER) < prompt.index("INPUT PACKAGE")
        assert '"payload_sentinel":"PAYLOAD-ONLY"' in prompt
