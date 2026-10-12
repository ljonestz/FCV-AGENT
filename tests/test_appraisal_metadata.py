"""Deterministic PID country metadata and model response handling."""

from types import SimpleNamespace
from pathlib import Path

import app
from sector_lenses.climate_verified_runtime import prepare_verified_sources, resolve_verified_operation_context


PID = """Project Information Document. Additional Financing. IPF.
Beneficiary Country/Countries
Geographical Identifier
Burundi, Congo, Democratic Republic of
DRC - Angola
Practice Area (Lead)
Transport
"""


def test_pid_beneficiary_field_routes_region_without_model_call():
    assert app.extract_country_name(PID, None) == "Burundi; Congo, Democratic Republic of"
    prepared = prepare_verified_sources([{"label": "PROJECT DOCUMENT", "name": "af.pdf", "raw_text": PID}])
    assert resolve_verified_operation_context(prepared).country_scope == "multi"


def test_pdf_extractor_combined_columns_excludes_geographic_neighbor():
    text = "Beneficiary Country/Countries Geographical Identifier \nBurundi, Congo, Democratic Republic of DRC - Angola \nPractice Area (Lead)"
    assert app.extract_country_name(text, None) == "Burundi; Congo, Democratic Republic of"


def test_comma_inside_country_name_does_not_make_single_country_regional():
    text = PID.replace("Burundi, ", "")
    assert app.extract_country_name(text, None) == "Congo, Democratic Republic of"
    prepared = prepare_verified_sources([{"label": "PROJECT DOCUMENT", "name": "af.pdf", "raw_text": text}])
    assert resolve_verified_operation_context(prepared).country_scope == "single"


def test_context_upload_cannot_establish_beneficiary_scope():
    prepared = prepare_verified_sources([
        {"label": "PROJECT DOCUMENT", "name": "pcn.txt", "raw_text": "IPF. Single-country project."},
        {"label": "CONTEXT DOCUMENT", "name": "pid.txt", "raw_text": PID},
    ])
    assert resolve_verified_operation_context(prepared).country_scope == "single"


def test_explicit_esf_evidence_beyond_front_matter_is_used():
    text = PID + ("General project background. " * 400) + "\nThe Environmental and Social Commitment Plan (ESCP) will be updated."
    prepared = prepare_verified_sources([{"label": "PROJECT DOCUMENT", "name": "af.pdf", "raw_text": text}])
    assert resolve_verified_operation_context(prepared).es_regime == "ESF_ESS1_TO_ESS10"


def test_metadata_helpers_disable_thinking_and_select_text_blocks():
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text="Somalia")])
    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    assert app.extract_country_name("Project narrative", client) == "Somalia"
    assert app.extract_sector_name("Project narrative", client) == "Somalia"
    assert all(call["thinking"] == {"type": "disabled"} for call in calls)
    assert all(call["max_tokens"] >= 128 for call in calls)


def test_unresolved_preparation_notice_has_browser_and_export_parity():
    root = Path(app.__file__).parent
    notice = "Preparation route: confirm the OIS date and applicable review; the upload does not establish them."
    assert (root / "index.html").read_text(encoding="utf-8").count(notice) == 2
    assert (root / "sector_lenses/climate_verified_render.py").read_text(encoding="utf-8").count(notice) == 2
