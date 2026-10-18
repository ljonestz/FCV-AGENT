"""Exact reader edits preserve surrounding prose and fail closed on bad anchors."""
from copy import deepcopy

import pytest

from sector_lenses.climate_final_reader import apply_reader_corrections


def original():
    return {"summary_paragraphs": [{"object_id": "SUM-001", "text": "Existing measures remain.  Flood-ready border posts build trust. Benefits remain conditional.", "evidence_ids": ["PF-001"]}], "assessment_narratives": [{"object_id": "NARR-design", "paragraphs": ["First paragraph remains.", "Studies were planned in 2028. Another qualification remains."], "evidence_ids": ["PF-002"]}]}


def patch(old="Flood-ready border posts", new="Planned flood-resilient border posts", index=0):
    return {"paragraph_index": index, "old_text": old, "new_text": new}


def apply(edits, payload=None, identifier="SUM-001"):
    payload = payload or original()
    snapshot = deepcopy(payload)
    issues = []
    result = apply_reader_corrections(payload, {"corrections": [{"object_id": identifier, "edits": edits}]}, {identifier}, issues=issues)
    assert payload == snapshot
    return result, issues


def test_exact_edit_preserves_all_unaffected_bytes_and_metadata():
    result, issues = apply([patch()])
    expected = original()
    expected["summary_paragraphs"][0]["text"] = expected["summary_paragraphs"][0]["text"].replace("Flood-ready border posts", "Planned flood-resilient border posts")
    assert result == expected
    assert issues == []


def test_empty_edits_preserve_disputed_record():
    result, issues = apply([])
    assert result == original()
    assert issues == []


def test_sentence_deletion_and_second_paragraph_edit():
    result, issues = apply([patch("Another qualification remains.", "", 1)], identifier="NARR-design")
    assert result["assessment_narratives"][0]["paragraphs"] == ["First paragraph remains.", "Studies were planned in 2028. "]
    assert issues == []


def test_nonoverlapping_edits_use_original_offsets():
    result, issues = apply([patch("Benefits remain conditional", "Benefits could follow"), patch()])
    assert result["summary_paragraphs"][0]["text"] == "Existing measures remain.  Planned flood-resilient border posts build trust. Benefits could follow."
    assert issues == []


@pytest.mark.parametrize("edits,reason", [
    ([patch("missing")], "ANCHOR_INVALID"),
    ([patch("remain")], "ANCHOR_INVALID"),
    ([patch("", "insertion")], "TEXT_INVALID"),
    ([patch(index=True)], "PARAGRAPH_INVALID"),
    ([patch(index=-1)], "PARAGRAPH_INVALID"),
    ([patch(index=1)], "PARAGRAPH_INVALID"),
    ([patch(), patch("border posts", "sites")], "OVERLAP_INVALID"),
    ([patch(), patch()], "OVERLAP_INVALID"),
    ([patch("Existing measures remain.  Flood-ready border posts build trust.", "Everything changes.")], "SENTENCE_SCOPE_INVALID"),
    ([patch(new="Planned sites. Delivered benefits.")], "SENTENCE_SCOPE_INVALID"),
    ([patch(new="987654 sites")], "SUMMARY_NUMBER_UNSUPPORTED"),
    ([dict(patch(), evidence_ids=["PF-new"])], "EDIT_FIELDS_INVALID"),
])
def test_invalid_edits_fail_closed(edits, reason):
    result, issues = apply(edits)
    assert result is None
    assert issues[0]["reason_codes"] == ["READER_CORRECTION_" + reason]


def test_new_date_still_rejected():
    result, issues = apply([patch("2028", "June 2028", 1)], identifier="NARR-design")
    assert result is None
    assert issues[0]["reason_codes"] == ["READER_CORRECTION_SUMMARY_DATE_UNSUPPORTED"]


def test_native_schema_requires_edits_not_paragraph_replacement():
    from sector_lenses.climate_verified_schemas import stage_output_schema
    import jsonschema
    schema = stage_output_schema("reader_correction")
    jsonschema.validate({"corrections": [{"object_id": "SUM-001", "edits": [patch()]}]}, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"corrections": [{"object_id": "SUM-001", "paragraphs": ["Rewrite."]}]}, schema)


@pytest.mark.parametrize("corrections,targets,reason", [
    ([], {"SUM-001"}, "TARGETS_MISSING"),
    ([{"object_id": "SUM-unknown", "edits": []}], {"SUM-unknown"}, "TARGET_INVALID"),
    ([{"object_id": "SUM-001", "edits": []}] * 2, {"SUM-001"}, "TARGET_INVALID"),
    ([{"object_id": "NARR-design", "edits": []}], {"SUM-001"}, "TARGET_INVALID"),
    ([{"object_id": "SUM-001", "edits": [], "evidence_ids": []}], {"SUM-001"}, "FIELDS_INVALID"),
])
def test_record_scope_guards(corrections, targets, reason):
    issues = []
    payload = original()
    snapshot = deepcopy(payload)
    assert apply_reader_corrections(payload, {"corrections": corrections}, targets, issues=issues) is None
    assert issues[0]["reason_codes"] == ["READER_CORRECTION_" + reason]
    assert payload == snapshot


def test_decimal_sentence_edit_is_permitted():
    payload = original()
    payload["summary_paragraphs"][0]["text"] = "The amount is 59.025 million. Other context stays."
    result, issues = apply([patch("The amount is 59.025 million.", "The planned amount is 59.025 million.")], payload)
    assert issues == []
    assert result["summary_paragraphs"][0]["text"] == "The planned amount is 59.025 million. Other context stays."
