from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "climate_claim_repair_prototype.py"


def _module():
    assert SCRIPT.is_file(), "claim-level repair prototype is not implemented"
    spec = importlib.util.spec_from_file_location("climate_claim_repair", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _reader() -> dict:
    return {
        "summary_paragraphs": [{
            "object_id": "SUM-001",
            "text": (
                "The project has delivered flood-ready sites and guarantees displaced "
                "traders access; if access works, livelihoods could stabilize."
            ),
            "evidence_ids": ["PF-1", "PF-2"],
        }],
        "assessment_narratives": [{
            "object_id": "NARR-design",
            "theme": "design",
            "paragraphs": ["The design remains conditional."],
            "evidence_ids": ["PF-1"],
        }],
    }


def _sources() -> dict[str, str]:
    return {
        "PF-1": "The project plans flood-resilient design specifications for retained sites.",
        "PF-2": (
            "Regional activities were redeployed to retained sites; no subgroup access "
            "arrangement is described."
        ),
    }


def _review() -> dict:
    return {
        "reviewer_label": "initial-reviewer",
        "record_reviews": [
            {
                "object_id": "SUM-001",
                "findings": [
                    {
                        "finding_id": "F-STATUS",
                        "paragraph_index": 0,
                        "quoted_text": "has delivered flood-ready sites",
                        "role": "factual_assertion",
                        "disposition": "repair",
                        "evidence_classification": "contradicted",
                        "reason": "The source describes planned specifications, not delivery.",
                        "source_checks": [{
                            "source_id": "PF-1",
                            "quoted_text": "plans flood-resilient design specifications",
                        }],
                    },
                    {
                        "finding_id": "F-ACCESS",
                        "paragraph_index": 0,
                        "quoted_text": "guarantees displaced traders access",
                        "role": "factual_assertion",
                        "disposition": "repair",
                        "evidence_classification": "not_established",
                        "reason": "Regional redeployment does not establish subgroup access.",
                        "source_checks": [{
                            "source_id": "PF-2",
                            "quoted_text": "Regional activities were redeployed",
                        }],
                    },
                ],
            },
            {"object_id": "NARR-design", "findings": []},
        ],
    }


def _prepared(module):
    review_input = module.prepare_review_input(_reader(), _sources())
    return module.plan_claim_repairs(review_input, _review())


def _correction() -> dict:
    return {
        "edits": [
            {
                "finding_id": "F-STATUS",
                "object_id": "SUM-001",
                "paragraph_index": 0,
                "old_text": "has delivered flood-ready sites",
                "new_text": "plans flood-ready sites",
            },
            {
                "finding_id": "F-ACCESS",
                "object_id": "SUM-001",
                "paragraph_index": 0,
                "old_text": "guarantees displaced traders access",
                "new_text": "could support trader access",
            },
        ],
        "disputed_finding_ids": [],
    }


def _final_review(pending: dict, *, outcomes: list[dict] | None = None) -> dict:
    if outcomes is None:
        outcomes = [
            {
                "finding_id": "F-STATUS",
                "outcome": "resolved",
                "reason": "The current text now states planning rather than delivery.",
                "source_checks": [{
                    "source_id": "PF-1",
                    "quoted_text": "plans flood-resilient design specifications",
                }],
            },
            {
                "finding_id": "F-ACCESS",
                "outcome": "resolved",
                "reason": "The current text makes access conditional rather than guaranteed.",
                "source_checks": [{
                    "source_id": "PF-2",
                    "quoted_text": "Regional activities were redeployed",
                }],
            },
        ]
    return {
        "reviewer_label": "independent-reviewer",
        "reader_digest": pending["current_digest"],
        "record_reviews": [
            {"object_id": "SUM-001", "finding_outcomes": outcomes, "issues": []},
            {"object_id": "NARR-design", "finding_outcomes": [], "issues": []},
        ],
    }


def test_two_defects_are_repaired_without_removing_valid_inference_or_mutating_evidence():
    module = _module()
    original = _reader()
    plan = _prepared(module)

    pending = module.apply_claim_repairs(plan, _correction(), "editor-run")

    assert pending["status"] == "pending_independent_review"
    assert pending["original_reader"] == original
    current = pending["current_reader"]
    text = current["summary_paragraphs"][0]["text"]
    assert "plans flood-ready sites" in text
    assert "could support trader access" in text
    assert "if access works, livelihoods could stabilize" in text
    assert current["summary_paragraphs"][0]["evidence_ids"] == ["PF-1", "PF-2"]
    assert current["assessment_narratives"] == original["assessment_narratives"]
    assert {finding["finding_id"] for finding in pending["findings"]} == {
        "F-STATUS", "F-ACCESS",
    }

    result = module.finalize_claim_repairs(pending, _final_review(pending))
    assert result == {
        "status": "accepted_offline_prototype",
        "reader_digest": pending["current_digest"],
        "publication_approved": False,
        "optional_precision_findings": [],
    }


@pytest.mark.parametrize("damage", ["duplicate", "missing-record", "foreign-source"])
def test_plan_rejects_duplicate_ids_missing_coverage_and_foreign_sources(damage):
    module = _module()
    review_input = module.prepare_review_input(_reader(), _sources())
    review = _review()
    if damage == "duplicate":
        review["record_reviews"][0]["findings"][1]["finding_id"] = "F-STATUS"
    elif damage == "missing-record":
        review["record_reviews"].pop()
    else:
        review["record_reviews"][0]["findings"][0]["source_checks"][0][
            "source_id"
        ] = "PF-FOREIGN"

    with pytest.raises(module.ContractError):
        module.plan_claim_repairs(review_input, review)


def test_overlapping_authorized_spans_are_rejected_before_existing_applier():
    module = _module()
    review = _review()
    access = review["record_reviews"][0]["findings"][1]
    access["quoted_text"] = "flood-ready sites and guarantees displaced traders access"
    review_input = module.prepare_review_input(_reader(), _sources())
    plan = module.plan_claim_repairs(review_input, review)
    correction = _correction()
    correction["edits"][1]["old_text"] = access["quoted_text"]

    with pytest.raises(module.ContractError, match="overlap"):
        module.apply_claim_repairs(plan, correction, "editor-run")


def test_correction_rejects_new_numbers_fabricated_ids_and_evidence_mutation():
    module = _module()
    plan = _prepared(module)

    numbered = _correction()
    numbered["edits"][0]["new_text"] = "has delivered 12 flood-ready sites"
    with pytest.raises(module.ContractError):
        module.apply_claim_repairs(plan, numbered, "editor-run")

    fabricated = _correction()
    fabricated["edits"][0]["finding_id"] = "F-MADE-UP"
    with pytest.raises(module.ContractError):
        module.apply_claim_repairs(plan, fabricated, "editor-run")

    evidence_mutation = _correction()
    evidence_mutation["edits"][0]["evidence_ids"] = ["PF-FOREIGN"]
    with pytest.raises(module.ContractError):
        module.apply_claim_repairs(plan, evidence_mutation, "editor-run")


def test_every_repair_finding_must_be_edited_or_explicitly_disputed():
    module = _module()
    plan = _prepared(module)
    correction = _correction()
    correction["edits"].pop()

    with pytest.raises(module.ContractError):
        module.apply_claim_repairs(plan, correction, "editor-run")

    correction["disputed_finding_ids"] = ["F-ACCESS"]
    pending = module.apply_claim_repairs(plan, correction, "editor-run")
    incomplete = _final_review(pending, outcomes=[
        _final_review(pending)["record_reviews"][0]["finding_outcomes"][0]
    ])
    with pytest.raises(module.ContractError):
        module.finalize_claim_repairs(pending, incomplete)

    unresolved = deepcopy(incomplete)
    unresolved["record_reviews"][0]["finding_outcomes"].append({
        "finding_id": "F-ACCESS",
        "outcome": "unresolved",
        "reason": "The initial dispute remains unresolved.",
        "source_checks": [{
            "source_id": "PF-2",
            "quoted_text": "Regional activities were redeployed",
        }],
    })
    assert module.finalize_claim_repairs(pending, unresolved)["status"] == "withheld"


def test_finalize_rejects_same_execution_missing_evidence_and_digest_drift():
    module = _module()
    pending = module.apply_claim_repairs(_prepared(module), _correction(), "editor-run")

    same_execution = _final_review(pending)
    same_execution["reviewer_label"] = "editor-run"
    with pytest.raises(module.ContractError):
        module.finalize_claim_repairs(pending, same_execution)

    same_initial = _final_review(pending)
    same_initial["reviewer_label"] = "initial-reviewer"
    with pytest.raises(module.ContractError):
        module.finalize_claim_repairs(pending, same_initial)

    bare_resolution = _final_review(pending)
    bare_resolution["record_reviews"][0]["finding_outcomes"][0]["source_checks"] = []
    with pytest.raises(module.ContractError):
        module.finalize_claim_repairs(pending, bare_resolution)

    drifted = deepcopy(pending)
    drifted["current_reader"]["summary_paragraphs"][0]["text"] += " Changed later."
    with pytest.raises(module.ContractError):
        module.finalize_claim_repairs(drifted, _final_review(pending))


def test_finalize_withholds_upheld_or_new_issues_and_rejects_fabricated_outcomes():
    module = _module()
    pending = module.apply_claim_repairs(_prepared(module), _correction(), "editor-run")

    upheld = _final_review(pending)
    upheld["record_reviews"][0]["finding_outcomes"][0]["outcome"] = "upheld"
    assert module.finalize_claim_repairs(pending, upheld)["status"] == "withheld"

    new_issue = _final_review(pending)
    new_issue["record_reviews"][1]["issues"] = [{
        "reason": "A new issue remains.",
        "source_checks": [{
            "source_id": "PF-1",
            "quoted_text": "plans flood-resilient design specifications",
        }],
    }]
    assert module.finalize_claim_repairs(pending, new_issue)["status"] == "withheld"

    fabricated = _final_review(pending)
    fabricated["record_reviews"][0]["finding_outcomes"][0]["finding_id"] = "F-NEW"
    with pytest.raises(module.ContractError):
        module.finalize_claim_repairs(pending, fabricated)


def test_unresolved_optional_precision_is_traced_without_blocking_factual_acceptance():
    module = _module()
    review = _review()
    review["record_reviews"][0]["findings"].append({
        "finding_id": "F-PRECISION",
        "paragraph_index": 0,
        "quoted_text": "if access works, livelihoods could stabilize",
        "role": "conditional_inference",
        "disposition": "precision",
        "evidence_classification": "not_established",
        "reason": "The conditional mechanism could be stated more precisely.",
        "source_checks": [{
            "source_id": "PF-2",
            "quoted_text": "Regional activities were redeployed",
        }],
    })
    review_input = module.prepare_review_input(_reader(), _sources())
    plan = module.plan_claim_repairs(review_input, review)
    pending = module.apply_claim_repairs(plan, _correction(), "editor-run")
    final = _final_review(pending)
    final["record_reviews"][0]["finding_outcomes"].append({
        "finding_id": "F-PRECISION",
        "outcome": "unresolved",
        "reason": "This remains an optional wording suggestion.",
        "source_checks": [{
            "source_id": "PF-2",
            "quoted_text": "Regional activities were redeployed",
        }],
    })

    result = module.finalize_claim_repairs(pending, final)

    assert result["status"] == "accepted_offline_prototype"
    assert result["optional_precision_findings"] == [{
        "finding_id": "F-PRECISION", "outcome": "unresolved",
    }]


def test_malformed_enum_shapes_raise_contract_error():
    module = _module()
    review_input = module.prepare_review_input(_reader(), _sources())
    review = _review()
    review["record_reviews"][0]["findings"][0]["role"] = []

    with pytest.raises(module.ContractError):
        module.plan_claim_repairs(review_input, review)
