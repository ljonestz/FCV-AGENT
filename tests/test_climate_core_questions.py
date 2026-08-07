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


def test_reader_model_carries_core_questions_and_sensitivity_rating():
    model = build_reader_model(_assessment_with_core_questions())
    assert model["core_questions"][0]["question_id"] == "cq2-infra-horizon"
    assert "judgment_reads" not in model  # replaced by the sensitivity rating
    rating = model["climate_sensitivity_rating"]
    # Derived from the retained internal `sensitivity` judgment (value=strong).
    assert rating["value"] == "strong"
    assert rating["label"] == "Strong"
    assert rating["level"] == 4  # 5-point scale: strong is the 4th of 5
    assert rating["scale"] == [
        "Very Limited", "Limited", "Moderate", "Strong", "Very Strong",
    ]
    assert "sensitive" in rating["question"].lower()
    assert rating["caveat"]


def test_sensitivity_rating_maps_each_value():
    for value, (label, level) in {
        "very_strong": ("Very Strong", 5),
        "strong": ("Strong", 4),
        "moderate": ("Moderate", 3),
        "limited": ("Limited", 2),
        "very_limited": ("Very Limited", 1),
        "unclear": ("Not yet clear", 0),
    }.items():
        assessment = _assessment_with_core_questions()
        assessment["judgments"]["sensitivity"]["value"] = value
        rating = build_reader_model(assessment)["climate_sensitivity_rating"]
        assert (rating["label"], rating["level"]) == (label, level)


def test_core_questions_render_in_html_and_docx():
    model = build_reader_model(_assessment_with_core_questions())
    html = render_reader_html(model)
    assert "Core climate-FCV questions" in html
    assert "How sensitive is this project to climate and FCV considerations?" in html
    assert ">Strong<" in html and "Moderate" in html and "Limited" in html  # scale
    assert "Is infrastructure sized for future climate conditions?" in html
    assert "For further insights on why this matters" in html
    # Watch notes are relocated to the standalone Watch section (no inline line).
    assert "What to keep an eye on" in html
    assert "What to watch" not in html
    assert "The tool's overall reads" not in html  # old strip removed
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    text = "\n".join(p.text for p in Document(stream).paragraphs)
    assert "Core climate-FCV questions" in text
    assert "How sensitive is this project" in text
    assert "Rating: Strong" in text
    assert "Is infrastructure sized for future climate conditions?" in text


def test_core_question_summary_renders_as_paragraphs():
    assessment = _assessment_with_core_questions()
    assessment["core_questions"][0]["summary"] = "First paragraph here.\n\nSecond paragraph here."
    html = render_reader_html(build_reader_model(assessment))
    assert "First paragraph here." in html and "Second paragraph here." in html
    assert html.count("First paragraph here.") == 1
    # Two separate <p> blocks, not one run-on.
    assert "First paragraph here.</p>" in html
    assert "Second paragraph here." in html


def test_reader_without_core_questions_still_renders():
    """Guard: an older/blank reader (no core_questions) renders without error."""
    assessment = _assessment_with_core_questions()
    assessment.pop("core_questions")
    model = build_reader_model(assessment)
    assert model["core_questions"] == []
    html = render_reader_html(model)
    assert "Core climate-FCV questions" in html
    assert "How sensitive is this project" in html  # rating still shown
    stream = BytesIO()
    write_reader_docx(model, stream)  # must not raise
