from dataclasses import replace

from sector_lenses.climate_recommendations import (
    CandidateRecommendation,
    RecommendationScore,
    ReviewReadinessFlag,
    admit_and_rank,
    admit_readiness_flags,
    validate_recommendation,
)


KNOWN_IDS = {"PW-001", "ER-001", "RG-001", "PF-001", "PF-010"}


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
        drafting_language=None,
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


def test_at_most_three_are_ranked_without_high_badges():
    result = admit_and_rank([_candidate(f"REC-0{i}") for i in range(1, 5)])
    assert len(result) == 3
    assert [item.rank for item in result] == [1, 2, 3]
    assert not hasattr(result[0], "priority_label")


def test_failed_admission_gate_suppresses_candidate():
    candidate = _candidate()
    gates = {**candidate.gate_results, "timing": False}
    assert admit_and_rank([replace(candidate, gate_results=gates)]) == ()


def test_drafting_is_blocked_when_routing_is_unresolved():
    candidate = replace(
        _candidate(),
        routing_status="team_to_confirm",
        instrument_claim_ids=(),
        drafting_language="The POM shall include a trigger.",
    )
    issues = validate_recommendation(candidate, KNOWN_IDS - {"PF-010"})
    assert any(issue.code == "DRAFTING_ROUTING_UNVERIFIED" for issue in issues)


def test_mandatory_language_requires_verified_formal_authority():
    candidate = replace(
        _candidate(),
        authority_basis="none_verified",
        drafting_language="The team must adopt this requirement.",
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


def test_readiness_flags_are_capped_non_scoring_and_evidence_linked():
    flags = [
        ReviewReadinessFlag(
            flag_id=f"RF-{index}",
            category="document_inconsistency",
            flag=f"Inconsistency {index}",
            why_it_matters="It prevents verification.",
            document_basis_ids=("PF-001",),
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
        suggested_verification="Confirm an operational vehicle.",
    )
    admitted = admit_readiness_flags(
        [flag],
        {"PF-001"},
        {"the action has no identified operational home"},
    )
    assert admitted == ()
