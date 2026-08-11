import pytest

from sector_lenses.climate_analysis import (
    ClimatePathway,
    ContextEvidenceRef,
    ExistingResponse,
    ResidualGap,
    evidence_can_support,
    validate_analysis_registers,
)


def _pathway(**overrides) -> ClimatePathway:
    values = {
        "pathway_id": "PW-CF-1",
        "direction": "climate_to_fcv",
        "chain": ("flood", "access loss", "service interruption"),
        "project_anchor_ids": ("PF-001",),
        "evidence_ids": ("CE-001",),
        "confidence": "high",
    }
    values.update(overrides)
    return ClimatePathway(**values)


def test_country_context_cannot_support_project_design_or_site_claim():
    source = ContextEvidenceRef(
        evidence_id="CE-001",
        evidence_class="country",
        scope="national",
        statement="Flooding can restrict seasonal access.",
        source_ref="bank:ssd:hazard-01",
        confidence="high",
    )
    assert evidence_can_support(source, "contextual_pathway") is True
    assert evidence_can_support(source, "project_design_fact") is False
    assert evidence_can_support(source, "site_specific_conclusion") is False


def test_pathways_are_bounded_to_three_per_direction():
    pathways = [
        _pathway(pathway_id=f"PW-CF-{index}")
        for index in range(4)
    ]
    with pytest.raises(ValueError, match="three"):
        validate_analysis_registers(
            [], pathways, [], {"PF-001"}, {"CE-001"}
        )


def test_residual_gap_must_reference_existing_response():
    response = ExistingResponse(
        response_id="ER-001",
        project_fact_ids=("PF-010",),
        pathway_ids=("PW-CF-1",),
        description="Participatory boundary delineation is included.",
        limitation="Adaptive triggers are not defined.",
    )
    gap = ResidualGap(
        gap_id="RG-001",
        gap_type="partial_response",
        statement="Continuity arrangements are not yet specified.",
        pathway_ids=("PW-CF-1",),
        project_anchor_ids=("PF-001",),
        existing_response_ids=("ER-999",),
        evidence_ids=("PF-001", "CE-001"),
        confidence="medium",
    )
    issues = validate_analysis_registers(
        [response],
        [_pathway()],
        [gap],
        {"PF-001", "PF-010"},
        {"CE-001"},
    )
    assert any(issue.code == "GAP_RESPONSE_REF_INVALID" for issue in issues)


def test_confirmed_omission_requires_confirmed_absence_fact():
    gap = ResidualGap(
        gap_id="RG-002",
        gap_type="confirmed_omission",
        statement="The project explicitly excludes continuity planning.",
        pathway_ids=(),
        project_anchor_ids=("PF-001",),
        existing_response_ids=(),
        evidence_ids=("PF-001",),
        confidence="high",
    )
    issues = validate_analysis_registers(
        [],
        [],
        [gap],
        {"PF-001"},
        set(),
        confirmed_absence_fact_ids=set(),
    )
    assert issues[0].code == "CONFIRMED_OMISSION_NOT_EXPLICIT"


def test_residual_gap_register_is_capped_at_eight():
    gaps = [
        ResidualGap(
            gap_id=f"RG-{index}",
            gap_type="evidence_gap",
            statement="Evidence is incomplete.",
            pathway_ids=(),
            project_anchor_ids=(),
            existing_response_ids=(),
            evidence_ids=(),
            confidence="low",
        )
        for index in range(9)
    ]
    with pytest.raises(ValueError, match="eight"):
        validate_analysis_registers([], [], gaps, set(), set())
