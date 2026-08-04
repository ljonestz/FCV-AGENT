from dataclasses import replace

from sector_lenses.climate_recommendations import (
    CandidateRecommendation,
    DraftingBlock,
    DraftingValidationContext,
    RecommendationScore,
    normalize_drafting_blocks,
    normalize_unverified_completion_actor,
    normalize_unsupported_drafting_precision,
    validate_recommendation,
)


KNOWN_IDS = {"PW-001", "ER-001", "RG-001", "PF-001", "PF-010"}


def _draft(
    *,
    document: str = "PCN",
    section: str = "Project Description",
    guidance_id: str = "GUIDE-PCN-DESIGN",
    project_basis_id: str = "PF-001",
    text: str | None = None,
) -> DraftingBlock:
    return DraftingBlock(
        target_document=document,
        target_section=section,
        drafting_status="advisory_proposal",
        text=text or (("Draft language " * 50) + "complete."),
        project_basis_ids=(project_basis_id,),
        gap_basis_ids=("RG-001",),
        guidance_ids=(guidance_id,),
    )


def _candidate() -> CandidateRecommendation:
    return CandidateRecommendation(
        recommendation_id="REC-001",
        title="Protect continuity under compound climate and access disruption",
        pathway_ids=("PW-001",),
        existing_response_ids=("ER-001",),
        residual_gap_ids=("RG-001",),
        project_anchor_ids=("PF-001",),
        decision="Add a proportionate continuity provision.",
        minimum_action="Update the current project document.",
        enhanced_action=None,
        enhanced_activation=None,
        routing_status="standard_document_advisory",
        instrument_claim_ids=(),
        responsible_function="Task team",
        authority_basis="none_verified",
        recommendation_basis="analytical_judgment",
        completion_evidence="Updated project section",
        completion_evidence_status="updated_section",
        confidence="medium",
        limitation="Parameters remain bounded by available evidence.",
        caution="Avoid creating an unsupported formal condition.",
        current_document_drafting=_draft(),
        operational_instrument_drafting=None,
        score=RecommendationScore(3, 2, 2, 2, 1),
        gate_results={
            "connection": True,
            "residuality": True,
            "materiality": True,
            "actionability": True,
            "timing": True,
            "distinctiveness": True,
        },
    )


def _context() -> DraftingValidationContext:
    return DraftingValidationContext(
        known_ids=frozenset(KNOWN_IDS),
        guidance_ids=frozenset({"GUIDE-PCN-DESIGN", "GUIDE-FCV-CONTINUITY"}),
        current_document="PCN",
        standard_targets=frozenset(
            {
                ("pcn", "project description"),
                ("pcn", "concept note risk section"),
            }
        ),
        project_fact_text={
            "PF-001": "The task team prepares the PCN.",
            "PF-010": "The Security Risk Management Plan covers continuity.",
        },
        project_fact_types={"PF-001": "activity", "PF-010": "named_instrument"},
    )


def test_current_document_drafting_is_required() -> None:
    candidate = replace(_candidate(), current_document_drafting=None)
    issues = validate_recommendation(
        candidate,
        KNOWN_IDS,
        drafting_context=_context(),
    )
    assert "DRAFTING_CURRENT_MISSING" in {issue.code for issue in issues}


def test_one_block_is_valid_and_second_block_is_optional() -> None:
    issues = validate_recommendation(
        _candidate(),
        KNOWN_IDS,
        drafting_context=_context(),
    )
    assert issues == ()


def test_repetitive_second_block_is_dropped_without_suppressing_candidate() -> None:
    candidate = replace(_candidate(), operational_instrument_drafting=_draft())
    normalized, repairs = normalize_drafting_blocks(candidate)
    assert normalized.operational_instrument_drafting is None
    assert repairs == ("DRAFTING_SECOND_BLOCK_REDUNDANT",)



def test_drafting_normalization_canonicalizes_current_target_and_drops_unverified_optional():
    optional = _draft(
        document="Project Operations Manual",
        section="Implementation arrangements",
        text=("Use separate operational language for delivery arrangements. " * 16),
    )
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(document="Project Concept Note (PCN)"),
        operational_instrument_drafting=optional,
    )

    normalized, repairs = normalize_drafting_blocks(
        candidate,
        current_document="PCN",
    )

    assert normalized.current_document_drafting.target_document == "PCN"
    assert normalized.operational_instrument_drafting is None
    assert set(repairs) == {"DRAFTING_CURRENT_TARGET_CANONICALIZED", "DRAFTING_OPTIONAL_UNVERIFIED_DROPPED"}

def test_unknown_guidance_reference_blocks_drafting() -> None:
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(guidance_id="GUIDE-INVENTED"),
    )
    issues = validate_recommendation(
        candidate,
        KNOWN_IDS,
        drafting_context=_context(),
    )
    assert "DRAFTING_GUIDANCE_INVALID" in {issue.code for issue in issues}


def test_distinct_named_instrument_block_is_valid() -> None:
    second = _draft(
        document="Security Risk Management Plan",
        section="Continuity arrangements",
        guidance_id="GUIDE-FCV-CONTINUITY",
        project_basis_id="PF-010",
        text=("Add distinct operational continuity language here. " * 18).strip(),
    )
    candidate = replace(
        _candidate(),
        instrument_claim_ids=("PF-010",),
        operational_instrument_drafting=second,
    )
    assert validate_recommendation(
        candidate,
        KNOWN_IDS,
        drafting_context=_context(),
    ) == ()


def test_unverified_named_instrument_target_is_blocking() -> None:
    second = _draft(
        document="Project Operations Manual",
        section="Continuity arrangements",
        guidance_id="GUIDE-FCV-CONTINUITY",
        project_basis_id="PF-001",
        text=("Add distinct operational continuity language here. " * 18).strip(),
    )
    candidate = replace(
        _candidate(),
        operational_instrument_drafting=second,
    )
    issues = validate_recommendation(
        candidate,
        KNOWN_IDS,
        drafting_context=_context(),
    )
    assert "DRAFTING_INSTRUMENT_UNVERIFIED" in {
        issue.code for issue in issues
    }


def test_current_drafting_target_must_match_current_document() -> None:
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(document="PAD"),
    )
    issues = validate_recommendation(
        candidate,
        KNOWN_IDS,
        drafting_context=_context(),
    )
    assert "DRAFTING_CURRENT_TARGET_INVALID" in {issue.code for issue in issues}


def test_team_confirmation_is_not_an_admissible_route() -> None:
    candidate = replace(_candidate(), routing_status="team_to_confirm")
    issues = validate_recommendation(
        candidate,
        KNOWN_IDS,
        drafting_context=_context(),
    )
    assert "ROUTING_STATUS_INVALID" in {issue.code for issue in issues}


def _drafting_issue_codes(text: str) -> set[str]:
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(text=text),
    )
    return {
        issue.code
        for issue in validate_recommendation(
            candidate,
            KNOWN_IDS,
            drafting_context=_context(),
        )
    }


def test_invented_psc_security_plan_focal_point_is_blocked() -> None:
    codes = _drafting_issue_codes(
        "The PSC Security Risk Management Plan focal point will coordinate "
        "continuity decisions and report implementation constraints through "
        "the project governance structure."
    )
    assert "DRAFTING_ACTOR_UNVERIFIED" in codes


def test_unsupported_before_effectiveness_timing_is_blocked() -> None:
    codes = _drafting_issue_codes(
        "The task team will complete and approve the continuity arrangements "
        "before effectiveness, with implementation following the documented "
        "decision."
    )
    assert "DRAFTING_TIMING_UNVERIFIED" in codes


def test_invented_project_operations_manual_is_blocked() -> None:
    codes = _drafting_issue_codes(
        "The Project Operations Manual will establish the continuity process "
        "and assign responsibilities for disrupted access."
    )
    assert "DRAFTING_INSTRUMENT_UNVERIFIED" in codes


def test_unsupported_hydrometeorological_system_is_blocked() -> None:
    codes = _drafting_issue_codes(
        "The project will establish a hydrometeorological system to support "
        "site-level early warning and continuity decisions."
    )
    assert "DRAFTING_SYSTEM_UNVERIFIED" in codes


def test_linked_named_instrument_can_be_used_in_drafting_text() -> None:
    candidate = replace(
        _candidate(),
        instrument_claim_ids=("PF-010",),
        current_document_drafting=_draft(
            project_basis_id="PF-010",
            text=(
                "The Security Risk Management Plan covers continuity and the "
                "project description will explain how that existing measure "
                "addresses the supported access disruption pathway."
            ),
        ),
    )
    codes = {
        issue.code
        for issue in validate_recommendation(
            candidate,
            KNOWN_IDS,
            drafting_context=_context(),
        )
    }
    assert "DRAFTING_INSTRUMENT_UNVERIFIED" not in codes


def test_implausibly_short_drafting_is_blocked() -> None:
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(text="Add continuity language."),
    )
    issues = validate_recommendation(
        candidate,
        KNOWN_IDS,
        drafting_context=_context(),
    )
    assert "DRAFTING_LENGTH_INVALID" in {issue.code for issue in issues}


def test_normalization_drops_optional_block_with_mismatched_instrument_target():
    optional = _draft(
        document="Project Operations Manual",
        section="Implementation arrangements",
        project_basis_id="PF-010",
        text=("Use distinct operational language for delivery arrangements. " * 16),
    )
    candidate = replace(
        _candidate(),
        instrument_claim_ids=("PF-010",),
        operational_instrument_drafting=optional,
    )

    normalized, repairs = normalize_drafting_blocks(
        candidate,
        current_document="PCN",
        drafting_context=_context(),
    )

    assert normalized.operational_instrument_drafting is None
    assert "DRAFTING_OPTIONAL_UNVERIFIED_DROPPED" in repairs


def test_unverified_completion_actor_is_generalized_before_validation() -> None:
    candidate = replace(
        _candidate(),
        completion_evidence="Coordination unit records the agreed update.",
    )

    normalized, repairs = normalize_unverified_completion_actor(
        candidate,
        _context(),
    )

    assert normalized.completion_evidence == (
        "Responsible project function records the agreed update."
    )
    assert repairs == ("COMPLETION_EVIDENCE_ACTOR_GENERALIZED",)
    assert "DRAFTING_ACTOR_UNVERIFIED" not in {
        issue.code
        for issue in validate_recommendation(
            normalized,
            KNOWN_IDS,
            drafting_context=_context(),
        )

    }

def test_unsupported_drafting_number_is_removed_without_suppressing_candidate():
    text = (
        "Update Component 1.2 language with a proportionate description of "
        "the supported continuity action and its implementation approach. " * 8
    )
    candidate = replace(
        _candidate(),
        current_document_drafting=_draft(text=text),
        supported_numeric_tokens=(),
    )

    normalized, repairs = normalize_unsupported_drafting_precision(candidate)

    assert "1.2" not in normalized.current_document_drafting.text
    assert repairs == ("DRAFTING_UNSUPPORTED_PRECISION_REMOVED",)
    assert "RECOMMENDATION_NUMBER_UNSUPPORTED" not in {
        issue.code
        for issue in validate_recommendation(
            normalized,
            KNOWN_IDS,
            drafting_context=_context(),
        )
    }
