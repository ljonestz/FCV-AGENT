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
