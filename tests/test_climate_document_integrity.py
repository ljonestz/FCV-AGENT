from __future__ import annotations

import json
from io import BytesIO

from docx import Document

from sector_lenses.climate_recommendations import ReviewReadinessFlag
from sector_lenses.climate_verified_pipeline import (
    _integrity_readiness_flags,
    _merge_readiness_flags,
)
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_render import (
    build_reader_model,
    render_reader_html,
    write_reader_docx,
)
from sector_lenses.climate_verified_schemas import (
    READINESS_SCHEMA,
    stage_output_schema,
)
from tests.test_climate_verified_render import _assessment


def test_fact_extraction_schema_exposes_document_integrity_findings():
    schema = stage_output_schema("fact_extraction")
    props = schema["properties"]
    assert "document_integrity_findings" in props
    assert "document_integrity_findings" in schema["required"]
    items = props["document_integrity_findings"]["items"]
    # Same shape as a readiness flag.
    assert items["properties"].keys() == READINESS_SCHEMA["properties"].keys()


def test_recommendation_schema_still_within_budget():
    schema = stage_output_schema("recommendation_compiler")
    assert len(json.dumps(schema, separators=(",", ":"))) <= 4_100


def test_fact_prompt_requests_generic_document_integrity_scan():
    prompt = build_verified_stage_prompt("fact_extraction", {})
    lowered = prompt.lower()
    # It asks for the new output and defines the four generic classes.
    assert "document_integrity_findings" in prompt
    assert "contradict" in lowered            # class 1: contradiction
    assert "empty" in lowered                 # class 2: present-but-empty
    assert "placeholder" in lowered           # class 3: drafter residue
    assert "unmarked" in lowered              # class 4: expected-but-unmarked
    # It must stay inside the document (no external inference) and be source-linked.
    assert "do not infer" in lowered or "not infer" in lowered
    assert "document_basis_ids" in prompt


def _finding(flag_id, category, flag, block_id):
    return {
        "flag_id": flag_id,
        "category": category,
        "flag": flag,
        "why_it_matters": "A reviewer will question this at the gate.",
        "document_basis_ids": [block_id],
        "suggested_verification": "Confirm against the source document.",
        "residual_gap_ids": [],
    }


def test_integrity_findings_require_a_known_block_and_valid_category():
    payload = {
        "document_integrity_findings": [
            _finding("DIF-1", "document_inconsistency", "Totals disagree.", "B-1"),
            _finding("DIF-2", "material_placeholder", "Placeholder left.", "B-UNKNOWN"),
            _finding("DIF-3", "not_a_category", "Bad category.", "B-1"),
            {**_finding("DIF-4", "material_placeholder", "No basis.", "B-1"),
             "document_basis_ids": []},
        ]
    }
    flags = _integrity_readiness_flags(payload, {"B-1", "B-2"})
    kept = {f.flag_id for f in flags}
    assert kept == {"DIF-1"}  # unknown block and bad category dropped


def test_merge_prioritises_integrity_findings_dedupes_and_caps():
    integrity = [
        ReviewReadinessFlag("DIF-1", "document_inconsistency", "Totals disagree.",
                            "why", ("B-1",), "verify", ()),
    ]
    model = [
        ReviewReadinessFlag("RF-1", "document_inconsistency", "totals disagree",
                            "why", ("PF-1",), "verify", ()),  # dupe of DIF-1 by text+category
        ReviewReadinessFlag("RF-2", "unresolved_indicator", "Indicator blank.",
                            "why", ("PF-2",), "verify", ()),
    ]
    merged = _merge_readiness_flags(integrity, model, cap=4)
    ids = [f.flag_id for f in merged]
    assert ids[0] == "DIF-1"          # integrity first
    assert "RF-1" not in ids          # deduped against DIF-1
    assert "RF-2" in ids              # distinct model flag retained


def test_integrity_flags_drop_residual_gap_references():
    payload = {
        "document_integrity_findings": [
            {**_finding("DIF-1", "document_inconsistency", "Totals disagree.", "B-1"),
             "residual_gap_ids": ["RG-9"]},
        ]
    }
    flags = _integrity_readiness_flags(payload, {"B-1"})
    assert len(flags) == 1
    assert flags[0].residual_gap_ids == ()


INTRO = "Confirm these before the decision meeting"


def test_points_to_check_intro_present_in_html_and_docx():
    model = build_reader_model(_assessment())
    html = render_reader_html(model)
    assert INTRO in html
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    text = "\n".join(p.text for p in Document(stream).paragraphs)
    assert INTRO in text
