"""2026-11-27 (owner, parity with the normal route): on the climate route a generated summary's first two
sentences fill the overview box at the top instead of the two Climate-FCV S/R tiles. Fallback or withheld
summaries keep the tiles."""
from io import BytesIO

from docx import Document

from sector_lenses.climate_verified_render import build_reader_model, write_reader_docx
from tests.test_fcv_readout import CLIMATE_READER, climate


def test_climate_browser_overview_box_when_summary_generated():
    # The whole first paragraph sits in the box (judgment bold, rest regular); the section starts at
    # paragraph 2 under "Main remaining risk", so it never opens mid-thought.
    reader = dict(CLIMATE_READER, summary_overview=["First sentence here. Second sentence here. Third explains.",
                                                    "The most consequential remaining risk is X."])
    html = climate(reader)
    top = html[:html.index("fr-exec")]
    assert "fr-sc-overview" in top and "First sentence here. Second sentence here." in top
    assert '<span class="fr-sc-ov-rest">Third explains.</span>' in top
    assert "fr-sc-tile-summary" not in top and "Assessment snapshot" not in html
    section = html[html.index("fr-exec"):]
    assert "First sentence here." not in section and "Third explains." not in section
    assert section.index("Main remaining risk") < section.index("The most consequential remaining risk is X.")


def test_climate_browser_keeps_tiles_for_fallback_summary():
    html = climate(dict(CLIMATE_READER, reader_contract="final-reader-v1", summary_overview_status="fallback"))
    assert "fr-sc-overview" not in html and html.count("fr-sc-tile-summary") == 2


def _docx(model):
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    doc = Document(stream)
    tables = ["\n".join(c.text for c in t.rows[0].cells) for t in doc.tables]
    return tables, "\n".join(p.text for p in doc.paragraphs)


def test_climate_word_overview_box_when_summary_generated():
    model = build_reader_model({"executive_readout": "", "judgments": {}, "priorities": []})
    model["summary_overview"] = ["Alpha one. Beta two. Gamma three.", "Next paragraph."]
    model["summary_overview_status"] = "generated"
    tables, body = _docx(model)
    box = next(t for t in tables if t.startswith("OVERVIEW"))
    assert "Alpha one. Beta two. Gamma three." in box
    assert "Alpha one." not in body and "Gamma three." not in body
    assert body.upper().index("MAIN REMAINING RISK") < body.index("Next paragraph.")


def test_climate_word_keeps_tiles_for_fallback_summary():
    model = build_reader_model({"executive_readout": "", "judgments": {}, "priorities": []})
    model["summary_overview"] = ["Fallback text."]
    model["summary_overview_status"] = "fallback"
    tables, _ = _docx(model)
    assert not any(t.startswith("OVERVIEW") for t in tables)
