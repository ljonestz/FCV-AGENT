import json

from sector_lenses.climate_verified_schemas import (
    STAGE_OUTPUT_SCHEMAS,
    stage_output_schema,
)


STAGES = {
    "fact_extraction",
    "bounded_analysis",
    "judgment_review",
    "recommendation_compiler",
    "drafting_compiler",
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
    assert "current_document_drafting" not in properties
    assert "operational_instrument_drafting" not in properties
    assert "drafting_blocks" not in properties
    drafting_schema = stage_output_schema("drafting_compiler")
    drafting_set = drafting_schema["properties"]["drafting_sets"]["items"]
    assert "drafting_blocks" in drafting_set["required"]
    drafting = drafting_set["properties"]["drafting_blocks"]["items"]
    assert drafting["properties"]["drafting_role"]["enum"] == [
        "current_document",
        "operational_instrument",
    ]
    assert set(properties["routing_status"]["enum"]) == {
        "verified_existing",
        "verified_with_scope_change",
        "standard_document_advisory",
        "not_applicable",
    }
    assert drafting["properties"][
        "drafting_status"
    ]["enum"] == ["existing_commitment", "advisory_proposal"]
    readiness = schema["properties"]["readiness_flags"]["items"]
    assert "residual_gap_ids" in readiness["required"]
    assert readiness["properties"]["residual_gap_ids"] == {
        "type": "array",
        "items": {"type": "string"},
    }


def test_recommendation_transport_schema_stays_below_complexity_budget() -> None:
    schema = stage_output_schema("recommendation_compiler")
    drafting_schema = stage_output_schema("drafting_compiler")

    assert len(json.dumps(schema, separators=(",", ":"))) <= 4_100
    assert '"drafting_status": {' not in json.dumps(schema)
    assert len(json.dumps(drafting_schema, separators=(",", ":"))) <= 1_500
    assert json.dumps(drafting_schema).count('"drafting_status": {') == 1


def test_semantic_review_schema_allows_only_recommendation_defect_codes() -> None:
    schema = stage_output_schema("conditional_review")
    codes = schema["properties"]["reason_codes"]["items"]["enum"]

    assert "ROUTING_SCOPE_UNVERIFIED" in codes
    assert "INCOMPLETE_OPERATIONALIZATION" not in codes
    assert "MISSING_CONTINGENCY_PROTOCOL" not in codes
