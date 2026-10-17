"""Contract checks for useful conditional analysis and limitations-only reports."""
from io import BytesIO

from docx import Document
import pytest

from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_render import render_reader_html, write_reader_docx
from tests.test_climate_evidence_trail import _reader_with_trail


@pytest.mark.parametrize("stage", ["bounded_analysis", "judgment_review", "reader_compiler", "reader_review"])
def test_conditional_dividends_guidance_reaches_analysis_writer_and_reviewer(stage):
    prompt = build_verified_stage_prompt(stage, {})
    for concept in (
        "institutional legitimacy", "collective action", "FCV-related maladaptation",
        "The premises need source support; the inferred outcome need not be stated",
        "Potential is not a demonstrated impact or an automatic higher rating",
    ):
        assert concept in prompt


def test_limits_remain_without_method_or_duplicate_source_catalogue():
    model = _reader_with_trail()
    model["evidence_trail"]["methodology_note"] = "INTERNAL METHOD SENTINEL"
    model["evidence_trail"]["limitations"] = "Site-level information is not yet available."
    model["sources"] = [{"title": "DUPLICATE SOURCE SENTINEL"}]
    html = render_reader_html(model)
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    word = "\n".join(p.text for p in Document(stream).paragraphs)
    for text in (html, word):
        assert "Limitations" in text
        assert "Site-level information is not yet available." in text
        for removed in ("INTERNAL METHOD SENTINEL", "DUPLICATE SOURCE SENTINEL",
                        "How this analysis was produced", "Method, limitations, and sources"):
            assert removed not in text
    assert model["evidence_trail"]["methodology_note"] == "INTERNAL METHOD SENTINEL"
