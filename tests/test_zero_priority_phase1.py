"""Zero-priority Phase 1 (2026-11-17): datasheet grids, instrument fallback and choice, prompt rule."""

import base64
from io import BytesIO

from docx import Document

from app import app, apply_instrument_choice, normalize_instrument_choice
from docx_structure import extract_docx_units, reader_parts_from_units
from sector_lenses.climate_verified_prompts import _recommendation_prompt
from sector_lenses.climate_verified_runtime import (
    prepare_verified_sources,
    resolve_verified_operation_context,
)
from tests.test_climate_lens_frontend import INDEX


def _datasheet_docx() -> Document:
    """World Bank PID datasheet layout: a label row above a value row."""
    document = Document()
    table = document.add_table(rows=6, cols=3)
    rows = [
        ("Project Beneficiary(ies)", "Operation ID", "Operation Name"),
        ("Afghanistan", "P514193", "Human Capital and Jobs"),
        ("Financing Instrument", "Borrower(s)", "Implementing Agency"),
        ("Investment Project Financing (IPF)", "Aga Khan Development Network", "UNICEF"),
        ("Environmental and Social Risk Classification", "Concept Review Decision", ""),
        ("Substantial", "Track II", ""),
    ]
    for row, values in zip(table.rows, rows):
        for cell, value in zip(row.cells, values):
            cell.text = value
    document.add_paragraph("The project supports health services.")
    return document


def test_label_row_above_value_row_pairs_by_column_and_keeps_reader_text():
    units = extract_docx_units(_datasheet_docx())
    fields = {u.field_name: u.field_value for u in units if u.field_name}
    assert fields["Financing Instrument"] == "Investment Project Financing (IPF)"
    assert fields["Operation ID"] == "P514193"
    assert fields["Environmental and Social Risk Classification"] == "Substantial"
    assert "Borrower(s)" not in fields.values()
    text = "\n".join(reader_parts_from_units(units))
    for kept in ("Borrower(s)", "Aga Khan Development Network", "Operation Name", "Track II"):
        assert kept in text


def test_same_row_label_is_never_taken_as_a_value():
    document = Document()
    table = document.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Financing Instrument"
    table.rows[0].cells[1].text = "Borrower(s)"
    fields = {u.field_name: u.field_value for u in extract_docx_units(document) if u.field_name}
    assert fields.get("Financing Instrument") != "Borrower(s)"


def _prepared(text, fields, name="Concept Stage Project Information Document (PID).docx"):
    return prepare_verified_sources([{
        "label": "PROJECT DOCUMENT", "name": name, "raw_text": text, "structured_fields": fields,
    }])


def test_unrecognised_structured_value_falls_back_to_unique_document_instrument():
    text = "Datasheet.\n" + ("Background. " * 900) + "\nFinancing: Investment Project Financing (IPF)."
    fields = [{"field_name": "Financing Instrument", "field_value": "See annex", "location": "t:0"}]
    context = resolve_verified_operation_context(_prepared(text, fields))
    assert context.instrument_type == "IPF"
    blank = [{"field_name": "Financing Instrument", "field_value": "", "location": "t:0"}]
    assert resolve_verified_operation_context(_prepared(text, blank)).instrument_type == "Unknown"


def test_user_instrument_fills_only_an_unresolved_route():
    silent = _prepared("A project to improve services. " * 20, [])
    assert resolve_verified_operation_context(silent).instrument_type == "Unknown"
    chosen = resolve_verified_operation_context(silent, user_instrument="pforr")
    assert chosen.instrument_type == "PforR"
    assert "INSTRUMENT_USER_DESIGNATED" in chosen.warning_codes
    stated = _prepared("Financing Instrument: Investment Project Financing (IPF). " * 3, [])
    kept = resolve_verified_operation_context(stated, user_instrument="DPF")
    assert kept.instrument_type == "IPF"
    assert "INSTRUMENT_USER_CHOICE_OVERRIDDEN_BY_DOCUMENT" in kept.warning_codes


def test_normal_route_choice_fills_unknown_only():
    assert normalize_instrument_choice(" pforr ") == "PforR" and normalize_instrument_choice("TA") == ""
    assert apply_instrument_choice("Unknown", "DPF") == "DPO"
    assert apply_instrument_choice("IPF", "PforR") == "IPF"
    assert apply_instrument_choice("Unknown", "") == "Unknown"


def test_detect_instrument_endpoint_reads_the_datasheet_without_a_model():
    buffer = BytesIO()
    _datasheet_docx().save(buffer)
    content = base64.standard_b64encode(buffer.getvalue()).decode("ascii")
    client = app.test_client()
    response = client.post("/api/detect-instrument", json={"document": {
        "name": "Concept Stage Project Information Document (PID).docx", "type": "docx", "content": content}})
    assert response.status_code == 200 and response.get_json() == {"instrument": "IPF"}
    assert client.post("/api/detect-instrument", json={}).get_json() == {"instrument": ""}


def test_compiler_prompt_keeps_actions_when_the_route_is_unresolved():
    prompt = _recommendation_prompt({})
    assert "An\nunresolved route alone is never a reason to fail actionability or timing" in prompt
    assert "If neither destination is safe, fail actionability or timing" not in prompt
    assert "name the project element" in prompt


def test_instrument_selector_is_optional_and_sent_with_both_routes():
    html = INDEX.read_text(encoding="utf-8")
    start = html.index('id="instrument-choice"')
    select = html[start:html.index("</select>", start)]
    assert '<option value="" selected>' in select
    for value in ("IPF", "PforR", "DPF"):
        assert f'value="{value}"' in select
    assert html.count("instrument_choice:instrumentChoice") == 2
    assert "/api/detect-instrument" in html and "Assumed from the document: " in html


def test_conflicting_datasheet_accepts_only_a_named_instrument():
    fields = [
        {"field_name": "Financing Instrument", "field_value": "Investment Project Financing", "location": "t:0"},
        {"field_name": "Financing Instrument", "field_value": "Program-for-Results", "location": "t:1"},
    ]
    prepared = _prepared("Body text. " * 30, fields)
    assert resolve_verified_operation_context(prepared).instrument_type == "Unknown"
    named = resolve_verified_operation_context(prepared, user_instrument="PforR")
    assert named.instrument_type == "PforR"
    other = resolve_verified_operation_context(prepared, user_instrument="DPF")
    assert other.instrument_type == "Unknown"
    assert "INSTRUMENT_USER_CHOICE_NOT_IN_DATASHEET" in other.warning_codes


def test_instrument_choice_is_cleared_between_documents_and_sessions():
    html = INDEX.read_text(encoding="utf-8")
    body = html[html.index("function resetInstrumentChoice()"):]
    body = body[:body.index("\n  }\n")]
    for cleared in ("instrumentChoice=''", "instrumentChoiceTouched=false", "instrumentDetectedFor=''", "sel.value=''"):
        assert cleared in body
    # New run, session load, removed primary file and empty detection all clear it.
    assert html.count("resetInstrumentChoice()") >= 5
    detect = html[html.index("function detectInstrumentForPrimary()"):]
    detect = detect[:detect.index("\n  }\n")]
    assert "if(!f){if(instrumentDetectedFor)resetInstrumentChoice();return;}" in detect
    assert "sel.value='';selectInstrumentChoice('',false);" in detect
