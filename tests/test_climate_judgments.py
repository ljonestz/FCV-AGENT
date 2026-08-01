from sector_lenses.climate_judgments import (
    ClimateJudgments,
    Judgment,
    deterministic_summary,
    validate_judgments,
)


def test_high_relevance_can_coexist_with_partial_operationalization():
    judgments = ClimateJudgments(
        relevance=Judgment("high", ("PW-001",), "Material PDO pathway."),
        sensitivity=Judgment("moderate", ("ER-001",), "Risks recognized."),
        responsiveness=Judgment(
            "emerging",
            ("ER-002",),
            "Some resilience benefits are intended.",
        ),
        operationalization=Judgment(
            "partial",
            ("ER-001", "RG-001"),
            "Delivery arrangements remain incomplete.",
        ),
    )
    known = {"PW-001", "ER-001", "ER-002", "RG-001"}
    assert validate_judgments(judgments, known) == ()
    assert deterministic_summary(judgments) == (
        "High Climate-FCV relevance; moderate sensitivity; "
        "emerging responsiveness; partial operationalization."
    )


def test_missing_evidence_blocks_confident_values():
    judgments = ClimateJudgments(
        relevance=Judgment("high", (), "No evidence."),
        sensitivity=Judgment("strong", (), "No evidence."),
        responsiveness=Judgment("strong", (), "No evidence."),
        operationalization=Judgment("embedded", (), "No evidence."),
    )
    issues = validate_judgments(judgments, set())
    assert {issue.code for issue in issues} == {
        "RELEVANCE_EVIDENCE_MISSING",
        "SENSITIVITY_EVIDENCE_MISSING",
        "RESPONSIVENESS_EVIDENCE_MISSING",
        "OPERATIONALIZATION_EVIDENCE_MISSING",
        "OPERATIONALIZATION_DELIVERY_EVIDENCE_MISSING",
    }


def test_not_expected_is_valid_only_for_responsiveness():
    judgments = ClimateJudgments(
        relevance=Judgment("not_expected", ("PW-001",), "Invalid."),
        sensitivity=Judgment("moderate", ("ER-001",), "Valid."),
        responsiveness=Judgment("not_expected", ("PF-001",), "Valid."),
        operationalization=Judgment("partial", ("ER-001",), "Valid."),
    )
    issues = validate_judgments(
        judgments,
        {"PW-001", "ER-001", "PF-001"},
    )
    assert issues[0].code == "RELEVANCE_VALUE_INVALID"


def test_embedded_operationalization_requires_delivery_evidence():
    judgments = ClimateJudgments(
        relevance=Judgment("medium", ("PW-001",), "Material."),
        sensitivity=Judgment("moderate", ("ER-001",), "Recognized."),
        responsiveness=Judgment("limited", ("ER-001",), "Limited."),
        operationalization=Judgment(
            "embedded",
            ("PW-001",),
            "No implementation evidence.",
        ),
    )
    issues = validate_judgments(judgments, {"PW-001", "ER-001"})
    assert any(
        issue.code == "OPERATIONALIZATION_DELIVERY_EVIDENCE_MISSING"
        for issue in issues
    )
