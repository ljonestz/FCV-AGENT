from dataclasses import replace

from sector_lenses.climate_recommendations import (
    CandidateRecommendation,
    DraftingBlock,
    RecommendationGroundingContext,
    RecommendationScore,
    ReviewReadinessFlag,
    admit_and_rank,
    admit_readiness_flags,
    deterministic_grounding_failure_codes,
    normalize_optional_enhancement,
    normalize_recommendation_references,
    normalize_unsupported_drafting_precision,
    validate_recommendation,
    normalize_unsupported_core_precision,
)


KNOWN_IDS = {"PW-001", "ER-001", "RG-001", "PF-001", "PF-010"}
def _draft(text: str = "Add proportionate continuity language to this section."):
    return DraftingBlock(
        target_document="PCN",
        target_section="Project Description",
        drafting_status="existing_commitment",
        text=text,
        project_basis_ids=("PF-001",),
        gap_basis_ids=("RG-001",),
        guidance_ids=(),
    )




def test_normalize_references_strips_stray_invalid_ref_and_survives():
    # A single hallucinated reference should be stripped, not suppress the
    # whole recommendation. The valid grounding (gap + response) remains, so
    # RECOMMENDATION_REF_INVALID no longer fires.
    candidate = replace(
        _candidate("REC-01"),
        instrument_claim_ids=("PF-010", "PF-999"),  # PF-999 not in KNOWN_IDS
    )
    repaired, repairs = normalize_recommendation_references(candidate, KNOWN_IDS)
    assert repairs == ("RECOMMENDATION_INVALID_REFS_STRIPPED",)
    assert repaired.instrument_claim_ids == ("PF-010",)
    assert repaired.residual_gap_ids == ("RG-001",)
    assert repaired.gate_results["residuality"] is True
    codes = {issue.code for issue in validate_recommendation(repaired, KNOWN_IDS)}
    assert "RECOMMENDATION_REF_INVALID" not in codes


def test_normalize_references_downgrades_gate_when_grounding_lost():
    # If every residual-gap reference is invalid, stripping leaves the
    # recommendation ungrounded; the residuality gate is downgraded so it
    # still fails admission rather than being admitted on a hollow claim.
    candidate = replace(_candidate("REC-02"), residual_gap_ids=("RG-999",))
    repaired, repairs = normalize_recommendation_references(candidate, KNOWN_IDS)
    assert repairs == ("RECOMMENDATION_INVALID_REFS_STRIPPED",)
    assert repaired.residual_gap_ids == ()
    assert repaired.gate_results["residuality"] is False


def test_normalize_references_noop_when_all_valid():
    candidate = _candidate("REC-03")
    repaired, repairs = normalize_recommendation_references(candidate, KNOWN_IDS)
    assert repairs == ()
    assert repaired is candidate


def _candidate(
    identifier: str = "REC-01",
    score: RecommendationScore | None = None,
) -> CandidateRecommendation:
    return CandidateRecommendation(
        recommendation_id=identifier,
        title=f"Action {identifier}",
        pathway_ids=("PW-001",),
        existing_response_ids=("ER-001",),
        residual_gap_ids=("RG-001",),
        project_anchor_ids=("PF-001",),
        decision="Set a continuity requirement before site approval.",
        minimum_action="Document flood exposure and year-round access.",
        enhanced_action="Conduct a deeper options assessment.",
        enhanced_activation=(
            "Activate where site screening finds compound flood, access, "
            "and local conflict risks."
        ),
        routing_status="verified_existing",
        instrument_claim_ids=("PF-010",),
        responsible_function="Task team safeguards and engineering functions",
        authority_basis="project_commitment",
        recommendation_basis="project_evidence",
        completion_evidence="Updated site-selection methodology",
        completion_evidence_status="output",
        confidence="high",
        limitation="Site thresholds remain for the task team to define.",
        caution="Avoid hardening boundaries that require seasonal mobility.",
        current_document_drafting=_draft(),
        operational_instrument_drafting=None,
        score=score or RecommendationScore(3, 2, 2, 2, 1),
        gate_results={
            "connection": True,
            "residuality": True,
            "materiality": True,
            "actionability": True,
            "timing": True,
            "distinctiveness": True,
        },
    )


def test_admission_requires_six_points_and_medium_materiality():
    admitted = _candidate("REC-01", RecommendationScore(3, 2, 2, 2, 1))
    weak = _candidate("REC-02", RecommendationScore(1, 2, 2, 1, 1))
    result = admit_and_rank([weak, admitted])
    assert [item.recommendation_id for item in result] == ["REC-01"]
    assert result[0].rank == 1


def test_up_to_five_are_ranked_without_high_badges():
    result = admit_and_rank([_candidate(f"REC-0{i}") for i in range(1, 7)])
    assert len(result) == 5
    assert [item.rank for item in result] == [1, 2, 3, 4, 5]
    assert not hasattr(result[0], "priority_label")


def test_failed_admission_gate_suppresses_candidate():
    candidate = _candidate()
    gates = {**candidate.gate_results, "timing": False}
    assert admit_and_rank([replace(candidate, gate_results=gates)]) == ()


def test_team_confirmation_is_not_an_admissible_route():
    candidate = replace(
        _candidate(),
        routing_status="team_to_confirm",
        instrument_claim_ids=(),
        operational_instrument_drafting=None,
    )
    issues = validate_recommendation(candidate, KNOWN_IDS - {"PF-010"})
    assert any(issue.code == "ROUTING_STATUS_INVALID" for issue in issues)


def test_mandatory_language_requires_verified_formal_authority():
    candidate = replace(
        _candidate(),
        authority_basis="none_verified",
        current_document_drafting=_draft("The team must adopt this requirement."),
    )
    issues = validate_recommendation(candidate, KNOWN_IDS)
    assert any(issue.code == "MANDATORY_AUTHORITY_UNVERIFIED" for issue in issues)


def test_enhanced_action_requires_activation_condition():
    issues = validate_recommendation(
        replace(_candidate(), enhanced_activation=None),
        KNOWN_IDS,
    )
    assert any(issue.code == "ENHANCED_ACTIVATION_MISSING" for issue in issues)


def test_completion_evidence_can_be_team_to_define():
    candidate = replace(
        _candidate(),
        completion_evidence="Task team to define",
        completion_evidence_status="team_to_define",
    )
    issues = validate_recommendation(candidate, KNOWN_IDS)
    assert not any(issue.code.startswith("COMPLETION") for issue in issues)


def test_unsupported_date_or_number_is_blocking():
    candidate = replace(
        _candidate(),
        decision="Complete the assessment by 2027 for 12 sites.",
    )
    issues = validate_recommendation(candidate, KNOWN_IDS)
    assert any(
        issue.code == "RECOMMENDATION_NUMBER_UNSUPPORTED"
        for issue in issues
    )


def test_numbered_list_markers_are_not_treated_as_numeric_claims():
    candidate = replace(
        _candidate(),
        minimum_action=(
            "Use these checks: (1) exposure; (2) access; (3) inclusion; "
            "(4) monitoring; (5) verification; (6) escalation; "
            "(7) feedback; (8) adaptation."
        ),
    )
    issues = validate_recommendation(candidate, KNOWN_IDS)
    assert not any(
        issue.code == "RECOMMENDATION_NUMBER_UNSUPPORTED"
        for issue in issues
    )


def test_internal_reference_suffixes_are_not_treated_as_numeric_claims():
    candidate = replace(
        _candidate(),
        decision="Resolve PF-055 against RG-029 before appraisal.",
    )
    issues = validate_recommendation(candidate, KNOWN_IDS)
    assert not any(
        issue.code == "RECOMMENDATION_NUMBER_UNSUPPORTED"
        for issue in issues
    )


def test_source_linked_numeric_tokens_are_allowed():
    candidate = replace(
        _candidate(),
        decision="Use the documented Year 1 decision point.",
        supported_numeric_tokens=("1",),
    )
    issues = validate_recommendation(candidate, KNOWN_IDS)
    assert not any(
        issue.code == "RECOMMENDATION_NUMBER_UNSUPPORTED"
        for issue in issues
    )


def test_supported_drafting_label_is_preserved_whole():
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(
            "Add this under Sub-component 1.4 before the risk discussion."
        ),
        supported_numeric_tokens=("1.4",),
    )

    normalized, repairs = normalize_unsupported_drafting_precision(candidate)

    assert normalized.current_document_drafting.text == (
        "Add this under Sub-component 1.4 before the risk discussion."
    )
    assert repairs == ()


def test_unsupported_drafting_label_is_replaced_as_a_whole_phrase():
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(
            "Add this under Sub-component 1.4 before the risk discussion."
        ),
        supported_numeric_tokens=(),
    )

    normalized, repairs = normalize_unsupported_drafting_precision(candidate)

    assert normalized.current_document_drafting.text == (
        "Add this under the relevant sub-component before the risk discussion."
    )
    assert "under Sub-component" not in normalized.current_document_drafting.text
    assert repairs == ("DRAFTING_UNSUPPORTED_PRECISION_REMOVED",)


def test_unsupported_year_label_uses_preparation_year_wording():
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(
            "Record the review in Year 2 and update Annex 3."
        ),
        supported_numeric_tokens=(),
    )

    normalized, _ = normalize_unsupported_drafting_precision(candidate)

    assert normalized.current_document_drafting.text == (
        "Record the review during the relevant preparation year and update "
        "the relevant annex."
    )


def _grounding_context(**overrides):
    values = {
        "gap_types": {"RG-001": "not_yet_specified"},
        "gap_pathway_ids": {"RG-001": frozenset({"PW-001"})},
        "fact_source_blocks": {"PF-001": frozenset({"DOC-1-B-1"})},
        "integrity_source_blocks": frozenset({"DOC-1-B-1"}),
    }
    values.update(overrides)
    return RecommendationGroundingContext(**values)


def test_document_completion_candidate_is_reserved_for_document_checks():
    candidate = replace(
        _candidate(),
        decision="Populate the placeholder target in the results table.",
        minimum_action="Complete the unfinished document section.",
        enhanced_action=None,
        enhanced_activation=None,
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ("ADMISSION_DUPLICATES_DOCUMENT_CHECK",)


def test_plural_document_targets_are_reserved_for_document_checks():
    candidate = replace(
        _candidate(),
        decision="Populate numeric targets in the results framework.",
        minimum_action="Complete the unfinished risk section.",
        enhanced_action=None,
        enhanced_activation=None,
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ("ADMISSION_DUPLICATES_DOCUMENT_CHECK",)


def test_independent_climate_fcv_design_gap_sharing_block_is_retained():
    candidate = replace(
        _candidate(),
        decision="Define a continuity response for flood-related access disruption.",
    )
    context = _grounding_context(
        gap_types={"RG-001": "partial_response"},
    )

    assert deterministic_grounding_failure_codes(candidate, context) == ()


def test_document_candidate_needs_structural_source_overlap_to_be_suppressed():
    candidate = replace(
        _candidate(),
        decision="Populate the placeholder target in the results table.",
    )
    context = _grounding_context(
        integrity_source_blocks=frozenset({"DOC-1-B-9"}),
    )

    assert deterministic_grounding_failure_codes(candidate, context) == ()


def test_document_candidate_with_operational_action_is_retained():
    candidate = replace(
        _candidate(),
        decision="Populate the placeholder and implement access safeguards.",
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ()


def test_document_candidate_with_substantive_enhancement_is_retained():
    candidate = replace(
        _candidate(),
        decision="Populate the placeholder target in the results table.",
        minimum_action="Complete the unfinished document section.",
        enhanced_action="Assess options for maintaining seasonal access.",
        enhanced_activation="Use the options where access disruption is material.",
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ()


def test_context_only_candidate_cannot_mandate_new_protocol():
    candidate = replace(
        _candidate(),
        recommendation_basis="country_context",
        instrument_claim_ids=(),
        decision="Establish a herder-fisher agreement at each project site.",
        minimum_action="Create a site protocol and assign a new coordination actor.",
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ("RECOMMENDATION_CONTEXT_PROMOTION_UNSUPPORTED",)


def test_unrelated_instrument_does_not_authorize_context_only_obligation():
    candidate = replace(
        _candidate(),
        recommendation_basis="country_context",
        instrument_claim_ids=("PF-010",),
        decision="Establish a herder-fisher agreement at each project site.",
        minimum_action="Create a site protocol and assign a new coordination actor.",
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ("RECOMMENDATION_CONTEXT_PROMOTION_UNSUPPORTED",)


def test_context_only_candidate_cannot_develop_plural_obligations():
    candidate = replace(
        _candidate(),
        recommendation_basis="country_context",
        decision="Develop site agreements for seasonal resource use.",
        minimum_action="Designate coordination actors and create protocols.",
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ("RECOMMENDATION_CONTEXT_PROMOTION_UNSUPPORTED",)


def test_context_only_candidate_may_verify_applicability():
    candidate = replace(
        _candidate(),
        recommendation_basis="country_context",
        instrument_claim_ids=(),
        decision="Assess whether seasonal resource conflict applies at project sites.",
        minimum_action="Confirm applicability before deciding a response.",
    )

    assert deterministic_grounding_failure_codes(
        candidate, _grounding_context()
    ) == ()


def test_project_evidence_can_support_proportionate_project_action():
    candidate = replace(
        _candidate(),
        recommendation_basis="project_evidence",
        decision="Update the documented site-selection method.",
    )

    assert deterministic_grounding_failure_codes(
        candidate,
        _grounding_context(gap_types={"RG-001": "partial_response"}),
    ) == ()


def test_readiness_flags_are_capped_non_scoring_and_evidence_linked():
    flags = [
        ReviewReadinessFlag(
            flag_id=f"RF-{index}",
            category="document_inconsistency",
            flag=f"Inconsistency {index}",
            why_it_matters="It prevents verification.",
            document_basis_ids=("PF-001",),
            residual_gap_ids=(),
            suggested_verification="Confirm the controlling value.",
        )
        for index in range(5)
    ]
    admitted = admit_readiness_flags(flags, {"PF-001"}, set())
    assert len(admitted) == 4
    assert all(not hasattr(flag, "score") for flag in admitted)


def test_readiness_duplicate_of_residual_gap_is_suppressed():
    flag = ReviewReadinessFlag(
        flag_id="RF-1",
        category="missing_operational_home",
        flag="The action has no identified operational home.",
        why_it_matters="Routing cannot be verified.",
        document_basis_ids=("PF-001",),
        residual_gap_ids=("RG-001",),
        suggested_verification="Confirm an operational vehicle.",
    )
    admitted = admit_readiness_flags(
        [flag],
        {"PF-001"},
        {"the action has no identified operational home"},
        known_gap_ids={"RG-001"},
        admitted_gap_ids={"RG-001"},
    )
    assert admitted == ()


def test_readiness_paraphrase_is_suppressed_by_shared_gap_id():
    flag = ReviewReadinessFlag(
        flag_id="RF-2",
        category="missing_operational_home",
        flag="Clarify where the proposed response will be housed.",
        why_it_matters="The implementation destination is unresolved.",
        document_basis_ids=("PF-001",),
        residual_gap_ids=("RG-001",),
        suggested_verification="Confirm the appropriate project section.",
    )
    admitted = admit_readiness_flags(
        [flag],
        {"PF-001"},
        set(),
        known_gap_ids={"RG-001"},
        admitted_gap_ids={"RG-001"},
    )
    assert admitted == ()


def test_structured_drafting_types_are_available():
    import sector_lenses.climate_recommendations as recommendations

    assert hasattr(recommendations, "DraftingBlock")
    assert hasattr(recommendations, "DraftingValidationContext")
    assert hasattr(recommendations, "normalize_drafting_blocks")


def test_unsupported_optional_enhancement_is_dropped_without_weakening_core():
    candidate = replace(
        _candidate(),
        enhanced_action="Review 14 additional sites.",
        enhanced_activation="Activate within 30 days.",
        supported_numeric_tokens=(),
    )

    normalized, repairs = normalize_optional_enhancement(candidate)

    assert normalized.decision == candidate.decision
    assert normalized.minimum_action == candidate.minimum_action
    assert normalized.enhanced_action is None
    assert normalized.enhanced_activation is None
    assert repairs == ("ENHANCED_UNSUPPORTED_PRECISION_DROPPED",)


def test_unsupported_core_number_is_removed_without_dropping_action():
    candidate = replace(
        _candidate(),
        minimum_action="Update the 2023 risk framework for implementation.",
        supported_numeric_tokens=(),
    )

    normalized, repairs = normalize_unsupported_core_precision(candidate)

    assert normalized.decision == candidate.decision
    assert normalized.minimum_action == (
        "Update the risk framework for implementation."
    )
    assert normalized.completion_evidence == candidate.completion_evidence
    assert repairs == ("RECOMMENDATION_UNSUPPORTED_PRECISION_REMOVED",)


def test_unsupported_component_numbers_do_not_leave_dangling_grammar():
    candidate = replace(
        _candidate(),
        minimum_action="Update Components 1 and 2 before the 2027 review.",
        supported_numeric_tokens=(),
    )

    normalized, _ = normalize_unsupported_core_precision(candidate)

    assert normalized.minimum_action == "Update Components before the review."
