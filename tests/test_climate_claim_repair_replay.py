"""Curated source/claim replay: transport and edit safety, not model accuracy."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "claim_repair_replay", ROOT / "scripts/climate_claim_repair_prototype.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fixture = json.loads((ROOT / "tests/fixtures/climate/claim_repair_replay.json").read_text())
    return module, fixture


def _pending(module, fixture):
    review_input = module.prepare_review_input(fixture["reader"], fixture["sources"])
    plan = module.plan_claim_repairs(review_input, fixture["review"])
    return module.apply_claim_repairs(plan, fixture["correction"], "curated-editor")


def _rereview(pending, fixture):
    return {
        "reviewer_label": "curated-independent-adjudicator",
        "reader_digest": pending["current_digest"],
        "record_reviews": [
            {"object_id": "SUM-001", "finding_outcomes": [], "issues": []},
            {"object_id": "NARR-inclusion", "finding_outcomes": fixture["adjudications"], "issues": []},
        ],
    }


def test_curated_same_paragraph_repairs_preserve_disputed_analysis_and_evidence():
    module, fixture = _load()
    original = deepcopy(fixture["reader"])
    pending = _pending(module, fixture)
    current = pending["current_reader"]
    assert current["summary_paragraphs"] == original["summary_paragraphs"]
    before = original["assessment_narratives"][0]
    after = current["assessment_narratives"][0]
    assert after["paragraphs"][1] == before["paragraphs"][1]
    assert after["evidence_ids"] == before["evidence_ids"]
    expected = before["paragraphs"][0]
    for edit in fixture["correction"]["edits"]:
        expected = expected.replace(edit["old_text"], edit["new_text"])
    assert after["paragraphs"][0] == expected
    assert fixture["reader"] == original
    assert pending["status"] == "pending_independent_review"
    result = module.finalize_claim_repairs(pending, _rereview(pending, fixture))
    assert result["status"] == "accepted_offline_prototype"


def test_disputed_access_finding_cannot_disappear_from_final_review():
    module, fixture = _load()
    pending = _pending(module, fixture)
    rereview = _rereview(pending, fixture)
    rereview["record_reviews"][1]["finding_outcomes"] = fixture["adjudications"][:2]
    with pytest.raises(module.ContractError):
        module.finalize_claim_repairs(pending, rereview)


def test_dispute_requires_source_based_adjudication_not_a_bare_resolved_label():
    module, fixture = _load()
    pending = _pending(module, fixture)
    rereview = _rereview(pending, fixture)
    rereview["record_reviews"][1]["finding_outcomes"][2]["source_checks"] = []
    with pytest.raises(module.ContractError):
        module.finalize_claim_repairs(pending, rereview)
