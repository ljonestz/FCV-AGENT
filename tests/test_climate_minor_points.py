"""WS3: smaller climate & fragility points-to-check from non-admitted gaps."""
from __future__ import annotations

from io import BytesIO

from docx import Document

from sector_lenses.climate_verified_pipeline import _admit_minor_climate_points
from sector_lenses.climate_verified_render import (
    build_reader_model,
    render_reader_html,
    write_reader_docx,
)


def test_admit_minor_points_gates_on_non_admitted_gaps_and_dedup():
    known = {"RG-001", "RG-009", "RG-011"}
    admitted = {"RG-001"}          # covered by a priority
    reserved = {"placeholder value in the results framework"}  # a readiness-flag text
    payload = {
        "minor_climate_points": [
            # kept: references a known, non-admitted gap
            {"point": "Heat exposure for site workers is not addressed",
             "why": "Rising temperatures noted but no worker-safety measures.",
             "how_to_check": "Consider a heat-safety line in the ESMP.",
             "residual_gap_ids": ["RG-009"]},
            # dropped: gap is admitted (covered by a priority)
            {"point": "Site criteria unclear", "why": "x", "how_to_check": "y",
             "residual_gap_ids": ["RG-001"]},
            # dropped: unknown gap id
            {"point": "Something else", "why": "x", "how_to_check": "y",
             "residual_gap_ids": ["RG-777"]},
            # dropped: duplicates a reserved (readiness-flag) text
            {"point": "Placeholder value in the results framework",
             "why": "x", "how_to_check": "y", "residual_gap_ids": ["RG-011"]},
        ]
    }
    result = _admit_minor_climate_points(payload, known, admitted, reserved)
    assert [p["point"] for p in result] == [
        "Heat exposure for site workers is not addressed"
    ]
    assert result[0]["residual_gap_ids"] == ["RG-009"]


def _assessment(minor=True) -> dict[str, object]:
    assessment = {
        "schema_version": "climate-verified-v2.1",
        "run_id": "run-mp",
        "evidence_status": "approved",
        "executive_readout": "Executive readout paragraph. " * 20,
        "judgments": {
            "relevance": {"value": "high", "rationale": "Material."},
            "sensitivity": {"value": "strong", "rationale": "Recognized."},
            "responsiveness": {"value": "emerging", "rationale": "Developing."},
            "operationalization": {"value": "partial", "rationale": "Incomplete."},
        },
        "priorities": [],
        "review_readiness_flags": [
            {"flag": "Placeholder value in the results framework",
             "why_it_matters": "Target cannot be read.",
             "document_basis_ids": ["B-1"],
             "suggested_verification": "Insert the intended figure."},
        ],
    }
    if minor:
        assessment["minor_climate_points"] = [
            {"point": "Heat exposure for site workers is not addressed",
             "why": "Rising temperatures are noted but not worker heat-safety.",
             "how_to_check": "Consider a heat-safety line in the ESMP or POM.",
             "residual_gap_ids": ["RG-009"]},
        ]
    return assessment


def test_reader_and_render_show_two_points_to_check_groups():
    model = build_reader_model(_assessment(minor=True))
    assert model["minor_climate_points"][0]["point"].startswith("Heat exposure")
    html = render_reader_html(model)
    assert "Document points to confirm" in html
    assert "Smaller climate &amp; fragility points to consider" in html
    assert "Heat exposure for site workers is not addressed" in html
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    text = "\n".join(p.text for p in Document(stream).paragraphs)
    assert "Document points to confirm" in text
    assert "Smaller climate & fragility points to consider" in text
    assert "Heat exposure for site workers is not addressed" in text


def test_render_without_minor_points_omits_second_group():
    model = build_reader_model(_assessment(minor=False))
    assert model["minor_climate_points"] == []
    html = render_reader_html(model)
    assert "Smaller climate &amp; fragility points to consider" not in html
    # The document flags group still renders.
    assert "Placeholder value in the results framework" in html
    stream = BytesIO()
    write_reader_docx(model, stream)  # must not raise
