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
    size = len(json.dumps(schema, separators=(",", ":")))
    assert size <= 4_100, f"recommendation_compiler schema grew to {size} chars; budget is 4100"


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
            _finding("DIF-5", "missing_operational_home", "Design gap, not a defect.", "B-1"),
            {**_finding("DIF-6", "document_inconsistency", "Mixed ids.", "B-1"),
             "document_basis_ids": ["B-1", "B-UNKNOWN"]},
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


INTRO = "none is a reason to stop the project"


def test_points_to_check_intro_present_in_html_and_docx():
    model = build_reader_model(_assessment())
    html = render_reader_html(model)
    assert INTRO in html
    stream = BytesIO()
    write_reader_docx(model, stream)
    stream.seek(0)
    text = "\n".join(p.text for p in Document(stream).paragraphs)
    assert INTRO in text


def _pipeline_with_integrity_review(passed_ids, *, no_priorities=False, review_override=None):
    from tests.test_climate_verified_pipeline import (
        FakeClient, _arguments, _responses, _native_pass_review,
    )
    from sector_lenses.climate_verified_pipeline import PipelineClients, run_verified_climate_pipeline

    responses = _responses()
    responses[0]["document_integrity_findings"] = [
        _finding("DIF-1", "document_inconsistency", "Six suspended and four cancelled sites disagree.", "DOC-1-B-1"),
        _finding("DIF-2", "material_placeholder", "A material figure remains a placeholder.", "DOC-1-B-1"),
    ]
    if no_priorities:
        responses[-1]["recommendation_candidates"] = []
    def review(**kwargs):
        result = _native_pass_review(**kwargs)
        if passed_ids != "missing":
            result["passed_readiness_ids"] = passed_ids
        if review_override:
            result.update(review_override)
        return result
    assessment = FakeClient(responses, [])
    reviewer = FakeClient([review], [])
    result = run_verified_climate_pipeline(
        **_arguments(), clients=PipelineClients(assessment, reviewer),
    )
    return result, reviewer


def test_integrity_flags_need_explicit_semantic_acceptance():
    result, reviewer = _pipeline_with_integrity_review(["DIF-2"])
    assert [item["flag_id"] for item in result["review_readiness_flags"]] == ["DIF-2"]
    assert len(result["priorities"]) == 1
    assert len(reviewer.calls) == 1
    payload = reviewer.calls[0]["payload"]
    assert {item["flag_id"] for item in payload["readiness_flags"]} == {"DIF-1", "DIF-2"}
    assert payload["source_blocks"]


def test_unreviewed_or_malformed_integrity_acceptance_withholds_flags():
    for ids in ["missing", None, "DIF-1", ["DIF-unknown"], ["DIF-1", "DIF-1"], [42]]:
        result, _ = _pipeline_with_integrity_review(ids)
        assert result["review_readiness_flags"] == [], ids
        assert len(result["priorities"]) == 1
        assert "READINESS_FLAGS_NOT_ACCEPTED" in result["validation"]["reason_codes"]


def test_no_priorities_does_not_add_a_call_to_review_integrity_flags():
    result, reviewer = _pipeline_with_integrity_review([], no_priorities=True)
    assert reviewer.calls == []
    assert result["review_readiness_flags"] == []


def test_readiness_acceptance_schema_is_not_inherited_by_reader_review():
    assert "passed_readiness_ids" in stage_output_schema("conditional_review")["required"]
    assert "passed_readiness_ids" not in stage_output_schema("reader_review")["properties"]


def test_disputed_or_invalid_review_cannot_accept_integrity_flags():
    from sector_lenses.climate_verified_pipeline import _reviewed_readiness_flags
    flags = _integrity_readiness_flags({"document_integrity_findings": [
        _finding("DIF-1", "document_inconsistency", "Six suspended and four cancelled sites disagree.", "B-1"),
    ]}, {"B-1"})
    for review in [
        {"verdict": "unknown", "passed_readiness_ids": ["DIF-1"]},
        {"verdict": "revise", "passed_readiness_ids": ["DIF-1"], "object_ids": ["DIF-1"]},
        {"verdict": "revise", "passed_readiness_ids": ["DIF-1"], "issues": [{"object_id": "DIF-1"}]},
        {"verdict": "pass", "passed_readiness_ids": ["DIF-1"], "reason_codes": ["RESIDUAL_GAP_UNSUPPORTED"]},
    ]:
        assert _reviewed_readiness_flags(flags, review) == []
    assert _reviewed_readiness_flags(flags + flags, {
        "verdict": "pass", "passed_readiness_ids": ["DIF-1"],
    }) == []


def test_disputed_flag_does_not_remove_explicitly_accepted_core():
    for verdict in ["revise", "block", "pass"]:
        result, reviewer = _pipeline_with_integrity_review([], review_override={
            "verdict": verdict, "object_ids": ["DIF-1"],
            "reason_codes": ["RESIDUAL_GAP_UNSUPPORTED"],
            "issues": [{"object_id": "DIF-1", "reason_codes": ["RESIDUAL_GAP_UNSUPPORTED"],
                        "explanation": "Different statuses can both be true."}],
        })
        assert len(result["priorities"]) == 1
        assert result["review_readiness_flags"] == []
        assert len(reviewer.calls) == 1


def test_rejected_flag_cannot_reappear_as_an_unreviewed_minor_point():
    from tests.test_climate_verified_pipeline import FakeClient, _arguments, _responses, _native_pass_review
    from sector_lenses.climate_verified_pipeline import PipelineClients, run_verified_climate_pipeline

    responses = _responses()
    responses[0]["document_integrity_findings"] = [
        _finding("DIF-1", "document_inconsistency", "Secondary climate check.", "DOC-1-B-1"),
    ]
    responses[1]["residual_gaps"].append({
        "gap_id": "RG-002", "gap_type": "evidence_gap", "statement": "Secondary gap.",
        "pathway_ids": ["PW-001"], "project_anchor_ids": ["PF-001"],
        "existing_response_ids": [], "evidence_ids": ["CE-001"], "confidence": "low",
    })
    responses[2]["minor_climate_points"] = [{
        "point": "Secondary climate check.", "why": "Why.", "how_to_check": "Check.",
        "residual_gap_ids": ["RG-002"],
    }]
    def reject_flags(**kwargs):
        return {**_native_pass_review(**kwargs), "passed_readiness_ids": []}
    result = run_verified_climate_pipeline(**_arguments(), clients=PipelineClients(
        FakeClient(responses, []), FakeClient([reject_flags], []),
    ))
    assert result["review_readiness_flags"] == []
    assert result["minor_climate_points"] == []
    assert len(result["priorities"]) == 1
