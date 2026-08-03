from sector_lenses.climate_verified_schemas import (
    STAGE_OUTPUT_SCHEMAS,
    stage_output_schema,
)


STAGES = {
    "fact_extraction",
    "bounded_analysis",
    "judgment_review",
    "recommendation_compiler",
    "conditional_review",
}


def _assert_closed_objects(schema: object) -> None:
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            assert schema.get("additionalProperties") is False
        for value in schema.values():
            _assert_closed_objects(value)
    elif isinstance(schema, list):
        for value in schema:
            _assert_closed_objects(value)


def test_all_verified_stages_have_closed_native_output_schemas() -> None:
    assert set(STAGE_OUTPUT_SCHEMAS) == STAGES
    for stage in STAGES:
        schema = stage_output_schema(stage)
        assert schema["type"] == "object"
        assert schema["required"]
        _assert_closed_objects(schema)


def test_schema_lookup_returns_an_independent_copy() -> None:
    schema = stage_output_schema("fact_extraction")
    schema["required"].append("mutated")
    assert "mutated" not in stage_output_schema("fact_extraction")["required"]


def test_recommendation_schema_requires_structured_current_and_optional_drafting() -> None:
    schema = stage_output_schema("recommendation_compiler")
    candidate = schema["properties"]["recommendation_candidates"]["items"]
    properties = candidate["properties"]

    assert "drafting_language" not in properties
    assert "current_document_drafting" in candidate["required"]
    assert "operational_instrument_drafting" in candidate["required"]
    assert properties["current_document_drafting"]["type"] == "object"
    assert properties["operational_instrument_drafting"]["type"] == [
        "object",
        "null",
    ]
    assert set(properties["routing_status"]["enum"]) == {
        "verified_existing",
        "verified_with_scope_change",
        "standard_document_advisory",
        "not_applicable",
    }
    assert properties["current_document_drafting"]["properties"][
        "drafting_status"
    ]["enum"] == ["existing_commitment", "advisory_proposal"]
    readiness = schema["properties"]["readiness_flags"]["items"]
    assert "residual_gap_ids" in readiness["required"]
    assert readiness["properties"]["residual_gap_ids"] == {
        "type": "array",
        "items": {"type": "string"},
    }
