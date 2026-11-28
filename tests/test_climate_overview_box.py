"""2026-11-27 (owner, parity with the normal route): on the climate route a generated summary's first two
sentences fill the overview box at the top instead of the two Climate-FCV S/R tiles. Fallback or withheld
summaries keep the tiles."""
from io import BytesIO

from docx import Document

from sector_lenses.climate_verified_render import build_reader_model, write_reader_docx
from tests.test_fcv_readout import CLIMATE_READER, climate


def test_climate_browser_overview_box_when_summary_generated():
    # The whole first paragraph sits in the box (judgment bold, rest regular); the section starts at
    # paragraph 2 under "Where the design is least settled", so it never opens mid-thought.
    reader = dict(CLIMATE_READER, summary_overview=["First sentence here. Second sentence here. Third explains.",
                                                    "The most consequential remaining risk is X."])
    html = climate(reader)
    top = html[:html.index("fr-exec")]
    assert "fr-sc-overview" in top and '>First sentence here. <span class="fr-sc-ov-rest">Second sentence here. Third explains.</span>' in top
    assert "fr-sc-tile-summary" not in top and "Assessment snapshot" not in html
    section = html[html.index("fr-exec"):]
    assert "First sentence here." not in section and "Third explains." not in section
    assert section.index("Where the design is least settled") < section.index("The most consequential remaining risk is X.")


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
    box = next(t for t in tables if t.startswith("SNAPSHOT"))
    assert "Alpha one. Beta two. Gamma three." in box
    assert "Alpha one." not in body and "Gamma three." not in body
    assert body.upper().index("WHERE THE DESIGN IS LEAST SETTLED") < body.index("Next paragraph.")


def test_climate_word_keeps_tiles_for_fallback_summary():
    model = build_reader_model({"executive_readout": "", "judgments": {}, "priorities": []})
    model["summary_overview"] = ["Fallback text."]
    model["summary_overview_status"] = "fallback"
    tables, _ = _docx(model)
    assert not any(t.startswith("SNAPSHOT") for t in tables)


def test_climate_word_box_keeps_verify_note_highlighted():
    model = build_reader_model({"executive_readout": "", "judgments": {}, "priorities": []})
    model["summary_overview"] = ["Alpha one. Beta two. Gamma three. [Verify before sharing: Confirm the dates.]",
                                 "Next paragraph."]
    model["summary_overview_status"] = "generated"
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    doc = Document(stream)
    cell = next(t.rows[0].cells[0] for t in doc.tables if t.rows[0].cells[0].text.startswith("SNAPSHOT"))
    runs = [r for p in cell.paragraphs for r in p.runs]
    note = next(r for r in runs if "Confirm the dates" in r.text)
    assert note._r.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd") is not None
    bold = "".join(r.text for r in runs if r.bold and not r._r.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd") is not None)
    assert "Alpha one." in bold and "Beta two." not in bold


def test_reader_compiler_prompt_keeps_sum001_and_sum002_to_one_role_each():
    # SUM-001 fills the overview box on its own; delivery risks belong to SUM-002 (owner, 2026-11-27).
    from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
    prompt = " ".join(build_verified_stage_prompt("reader_compiler", {}).split())
    # 2026-11-27: the shared SNAPSHOT AND OPENING RULES replace the earlier SUM-001/SUM-002 wording.
    assert "write summary paragraph SUM-001 as the SNAPSHOT" in prompt
    assert "SUM-002 consists of the segue and the opening paragraph and nothing more" in prompt
    assert "references to the priority actions" in prompt and "caveats" in prompt
