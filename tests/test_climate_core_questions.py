"""WS2: core climate-FCV questions - selection, evidence-gating, and render."""
from __future__ import annotations

from io import BytesIO

from docx import Document

from sector_lenses.climate_verified_pipeline import (
    _admit_core_questions,
    _core_questions_to_answer,
)
from sector_lenses.climate_verified_render import (
    build_reader_model,
    render_reader_html,
    write_reader_docx,
)


def _facts() -> list[dict[str, object]]:
    # Plain dicts (the signal builder falls back to a mapping for non-dataclasses).
    return [
        {"subject": "Irrigation infrastructure", "predicate": "is planned at",
         "object": "flood-prone fisheries landing sites"},
        {"subject": "Women's committees", "predicate": "have a", "object": "membership quota"},
        {"subject": "The results framework", "predicate": "includes", "object": "monitoring indicators"},
    ]


def test_core_questions_to_answer_selects_triggered_bank_items():
    posed = _core_questions_to_answer(_facts())
    assert posed, "expected at least one triggered bank question"
    assert all({"id", "theme", "question", "source"} <= set(item) for item in posed)
    # Infrastructure/flood signals should trigger the maladaptation horizon question.
    assert any(item["id"] == "cq2-infra-horizon" for item in posed)


def test_admit_core_questions_is_evidence_gated_and_bank_scoped():
    allowed = {"cq2-infra-horizon", "cq6-adaptive-triggers"}
    known = {"RG-003", "PF-024"}
    payload = {
        "core_questions": [
            # kept: posed id + a resolvable evidence id
            {"question_id": "cq2-infra-horizon", "theme": "cq2_maladaptation",
             "question": "Sized for future climate?", "source": "FCV-Sensitive Climate Action Framework",
             "summary": "Siting uses present-day data only.", "evidence_ids": ["RG-003", "ZZ-9"],
             "watch": "Check projections."},
            # dropped: evidence does not resolve
            {"question_id": "cq6-adaptive-triggers", "theme": "cq6_adaptive",
             "question": "Adaptive?", "source": "CCDR guidance note",
             "summary": "No triggers described.", "evidence_ids": ["NOPE-1"], "watch": "x"},
            # dropped: question was never posed
            {"question_id": "cq3-peace-dividend", "theme": "cq3_dividends",
             "question": "Shared benefit?", "source": "x",
             "summary": "text", "evidence_ids": ["PF-024"], "watch": "x"},
        ]
    }
    admitted = _admit_core_questions(payload, allowed, known)
    assert [q["question_id"] for q in admitted] == ["cq2-infra-horizon"]
    assert admitted[0]["evidence_ids"] == ["RG-003"]  # unresolved ZZ-9 stripped


def _assessment_with_core_questions() -> dict[str, object]:
    return {
        "schema_version": "climate-verified-v2.1",
        "run_id": "run-cq",
        "evidence_status": "approved",
        "executive_readout": "Executive readout paragraph one. " * 20,
        "judgments": {
            "relevance": {"value": "high", "rationale": "Material."},
            "sensitivity": {"value": "strong", "rationale": "Recognized."},
            "responsiveness": {"value": "emerging", "rationale": "Developing."},
            "operationalization": {"value": "partial", "rationale": "Incomplete."},
        },
        "core_questions": [
            {"question_id": "cq2-infra-horizon", "theme": "cq2_maladaptation",
             "question": "Is infrastructure sized for future climate conditions?",
             "source": "FCV-Sensitive Climate Action Framework",
             "summary": "Landing sites appear designed around present-day catch levels.",
             "evidence_ids": ["RG-003"], "watch": "Confirm forward-looking projections."},
        ],
        "priorities": [],
        "review_readiness_flags": [],
    }


def test_reader_model_carries_core_questions_and_reads_strip():
    model = build_reader_model(_assessment_with_core_questions())
    assert model["core_questions"][0]["question_id"] == "cq2-infra-horizon"
    labels = [r["label"] for r in model["judgment_reads"]]
    # Reads strip keeps the three calibration dimensions and omits relevance.
    assert labels == ["Sensitivity", "Responsiveness", "From intent to delivery"]
    assert all(r["value"] for r in model["judgment_reads"])


def test_core_questions_render_in_html_and_docx():
    model = build_reader_model(_assessment_with_core_questions())
    html = render_reader_html(model)
    assert "Core climate-FCV questions" in html
    assert "The tool's overall reads" in html
    assert "Is infrastructure sized for future climate conditions?" in html
    assert "For further insights on why this matters" in html
    assert "What to watch" in html
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    text = "\n".join(p.text for p in Document(stream).paragraphs)
    assert "Core climate-FCV questions" in text
    assert "overall reads" in text
    assert "Is infrastructure sized for future climate conditions?" in text


def test_reader_without_core_questions_still_renders():
    """Guard: an older/blank reader (no core_questions) renders without error."""
    assessment = _assessment_with_core_questions()
    assessment.pop("core_questions")
    model = build_reader_model(assessment)
    assert model["core_questions"] == []
    html = render_reader_html(model)
    assert "Core climate-FCV questions" in html
    assert "The tool's overall reads" in html  # reads strip still shown
    stream = BytesIO()
    write_reader_docx(model, stream)  # must not raise
