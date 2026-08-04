from __future__ import annotations

import json

from sector_lenses.climate_verified_schemas import (
    READINESS_SCHEMA,
    stage_output_schema,
)


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


from sector_lenses.climate_verified_prompts import build_verified_stage_prompt


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
