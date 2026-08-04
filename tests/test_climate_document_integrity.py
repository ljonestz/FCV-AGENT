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
