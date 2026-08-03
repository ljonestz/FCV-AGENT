from sector_lenses.climate_semantic_review import (
    ReviewRisk,
    build_reviewer_prompt,
    semantic_review_required,
    split_repair_actions,
)


def test_verified_instrument_name_alone_does_not_trigger_review():
    assert semantic_review_required(
        ReviewRisk(verified_instrument_name=True)
    ) is False


def test_material_fuzzy_formal_or_scope_claim_triggers_review():
    assert semantic_review_required(
        ReviewRisk(material_fuzzy_match=True)
    ) is True
    assert semantic_review_required(
        ReviewRisk(mandatory_language=True)
    ) is True
    assert semantic_review_required(
        ReviewRisk(verified_scope_change=True)
    ) is True


def test_repair_policy_allows_one_semantic_repair_only():
    deterministic, semantic = split_repair_actions(
        [
            "normalize_enum",
            "sort_ranks",
            "rewrite_unsupported_routing",
            "rewrite_second_semantic_issue",
        ]
    )
    assert deterministic == ("normalize_enum", "sort_ranks")
    assert semantic == ("rewrite_unsupported_routing",)


def test_reviewer_receives_sources_and_objects_not_prose_alone():
    prompt = build_reviewer_prompt(
        source_blocks=[{"block_id": "B-1", "text": "Named POM."}],
        fact_registry=[{"claim_id": "PF-1", "source_block_ids": ["B-1"]}],
        analysis={"residual_gaps": [{"gap_id": "RG-1"}]},
        recommendations=[{"recommendation_id": "REC-1"}],
        warning_codes=["ROUTING_SCOPE_UNVERIFIED"],
    )
    assert prompt.index("source_blocks") < prompt.index("recommendations")
    assert "pass, revise, or block" in prompt
    assert "claim IDs and reason codes" in prompt
    assert "current-document and operational-instrument drafting" in prompt
    assert "existing mitigation" in prompt
    assert "actor, timing, and authority" in prompt
    assert "unsupported technical precision" in prompt
    assert "target existence and scope" in prompt
