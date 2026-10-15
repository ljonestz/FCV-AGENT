"""Regression boundaries for reviewer evidence roles and source-scope calibration."""
from copy import deepcopy

from sector_lenses.climate_final_reader import reader_support_records
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_schemas import validate_summary_fragment


def test_accepted_action_cannot_launder_its_narrative_as_documentary_support():
    assessment = {"priorities": [{
        "recommendation_id": "REC-001", "title": "Check access arrangements",
        "decision": "Decide how to address access barriers.",
        "minimum_action": "Document the proposed access arrangements.",
        "enhanced_action": None, "enhanced_activation": None,
        "project_anchor_ids": ["PF-001"], "pathway_ids": ["PW-001"],
        "residual_gap_ids": ["RG-001"], "existing_response_ids": [],
        "narrative": "Displaced traders from cancelled sites were relocated in June 2029.",
        "limitation": "The document does not state any siting criteria.",
        "caution": "A repeated unverified assertion is not source evidence.",
        "current_document_drafting": {"text": "Unreviewed draft."},
        "rank": 1,
    }]}
    before = deepcopy(assessment)
    support = reader_support_records(assessment)["REC-001"]
    assert support["support_role"] == "accepted_proposed_action"
    assert support["minimum_action"] == before["priorities"][0]["minimum_action"]
    assert support["project_anchor_ids"] == ["PF-001"]
    assert not {"narrative", "limitation", "caution", "current_document_drafting", "rank"} & support.keys()
    diagnostics = {}
    assert not validate_summary_fragment(
        "The traders were relocated in June 2029.", canonical_text=support,
        semantic_review_required=True, diagnostics=diagnostics,
    )
    assert diagnostics["reason"] == "SUMMARY_NUMBER_UNSUPPORTED"
    support["project_anchor_ids"].append("PF-unknown")
    assert assessment == before


def test_all_generation_and_review_stages_preserve_relations_and_existing_provisions():
    for stage in ("fact_extraction", "bounded_analysis", "judgment_review",
                  "recommendation_compiler", "conditional_review", "drafting_compiler",
                  "reader_compiler", "reader_correction", "reader_review"):
        prompt = " ".join(build_verified_stage_prompt(stage, {}).lower().split())
        assert "separate facts do not establish a relationship" in prompt
        assert "missing one dimension does not mean all criteria are absent" in prompt
        assert "proposed action is not documentary evidence" in prompt


def test_fact_extraction_preserves_material_selection_criteria():
    prompt = " ".join(build_verified_stage_prompt("fact_extraction", {}).lower().split())
    assert "selection, siting and sequencing criteria" in prompt
    assert "atomic facts" in prompt


def test_reader_review_distinguishes_entailment_inference_and_attribution():
    for stage in ("reader_compiler", "reader_review"):
        prompt = " ".join(build_verified_stage_prompt(stage, {}).lower().split())
        assert "subject, predicate and object_value together" in prompt
        assert "supporting_excerpt is a provenance anchor" in prompt
        assert "weaker paraphrase" in prompt
        assert "qualified consequence of an explicit constraint" in prompt
        assert "documented intent" in prompt
        assert "independent project-fact support" in prompt
        assert "cite each supporting project fact directly in evidence_ids" in prompt
        assert "or linked fact ids" not in prompt
    review = " ".join(build_verified_stage_prompt("reader_review", {}).lower().split())
    assert "exact unsupported proposition" in review
    assert "vocabulary difference alone" in review
    assert "prior action acceptance does not certify" in review


def test_core_review_checks_absence_against_source_blocks_not_only_extraction():
    prompt = " ".join(build_verified_stage_prompt("conditional_review", {}).lower().split())
    assert "every core recommendation" in prompt
    assert "absence from the extracted registry" in prompt
    assert "relevant source_blocks" in prompt
