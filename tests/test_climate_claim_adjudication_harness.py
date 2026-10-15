"""Offline tests for the enumerate->adjudicate harness.

The harness replaces open-ended defect "discovery" (which collapsed to an empty
findings list in the paid experiment) with two separated roles:
1. deterministic enumeration of every atomic claim in the reader (no empty escape);
2. a per-claim adjudication that must judge each enumerated claim individually and
   cannot leave a factual assertion silently unaddressed.

All readers/sources below are clearly labelled SYNTHETIC paraphrases; they only
reproduce the known failure structure (immediate-vs-planned, generic-vs-specific
safeguard, a valid qualified access question, and a faithful weaker paraphrase).
No provider call is made here.
"""

from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "climate_claim_adjudication_harness.py"
PROTOTYPE = ROOT / "scripts" / "climate_claim_repair_prototype.py"


def _load(path: Path, name: str):
    assert path.is_file(), f"{name} is not implemented"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _module():
    return _load(SCRIPT, "climate_claim_adjudication_harness")


def _prototype():
    return _load(PROTOTYPE, "climate_claim_repair_prototype")


def _reader() -> dict:
    return {
        "summary_paragraphs": [{
            "object_id": "SUM-001",
            "text": (
                "The project delivers flood-ready border posts today. "
                "Most displacement is attributed to climate-related disasters."
            ),
            "evidence_ids": ["SRC-PLAN", "SRC-DISPLACE"],
        }],
        "assessment_narratives": [{
            "object_id": "NARR-safeguard",
            "theme": "inclusion",
            "paragraphs": [
                "Environmental risk is managed by exclusion-specific safeguards.",
                "Whether traders near cancelled sites retain access is not established.",
            ],
            "evidence_ids": ["SRC-SAFEGUARD", "SRC-ACCESS"],
        }],
    }


def _sources() -> dict[str, str]:
    return {
        "SRC-PLAN": (
            "SYNTHETIC paraphrase: the project finances redesign and construction of "
            "border posts; the facilities are planned, not yet operational."
        ),
        "SRC-DISPLACE": (
            "SYNTHETIC paraphrase: 92 percent of displacement is caused by "
            "climate-related disasters."
        ),
        "SRC-SAFEGUARD": (
            "SYNTHETIC paraphrase: the project applies general ESF instruments and "
            "recognizes exclusion risk; no exclusion-specific safeguard is described."
        ),
        "SRC-ACCESS": (
            "SYNTHETIC paraphrase: regional activities were redeployed to retained "
            "sites; no arrangement for traders near cancelled sites is described."
        ),
    }


# Sentence spans enumerated from _reader(); used to build adjudications.
S_DELIVER = "The project delivers flood-ready border posts today."
S_DISPLACE = "Most displacement is attributed to climate-related disasters."
S_SAFEGUARD = "Environmental risk is managed by exclusion-specific safeguards."
S_ACCESS = "Whether traders near cancelled sites retain access is not established."


def _ids(module) -> dict[str, str]:
    """Map each enumerated sentence to its deterministic claim_id."""
    inventory = module.enumerate_claims(_reader())
    by_quote = {claim["quoted_text"]: claim["claim_id"] for claim in inventory["claims"]}
    return by_quote


def _good_adjudication(module) -> dict:
    ids = _ids(module)
    return {
        "reviewer_label": "per-claim-adjudicator",
        "claim_judgments": [
            {
                "claim_id": ids[S_DELIVER],
                "role": "factual_assertion",
                "verdict": "contradicted",
                "is_defect": True,
                "defect": {
                    "quoted_text": "delivers flood-ready border posts today",
                    "disposition": "repair",
                    "evidence_classification": "contradicted",
                    "reason": "Sources describe planned construction, not delivered posts.",
                    "source_checks": [{
                        "source_id": "SRC-PLAN",
                        "quoted_text": "planned, not yet operational",
                    }],
                },
                "support_source_checks": [],
            },
            {
                "claim_id": ids[S_DISPLACE],
                "role": "factual_assertion",
                "verdict": "supported",
                "is_defect": False,
                "defect": None,
                "support_source_checks": [{
                    "source_id": "SRC-DISPLACE",
                    "quoted_text": "92 percent of displacement",
                }],
            },
            {
                "claim_id": ids[S_SAFEGUARD],
                "role": "factual_assertion",
                "verdict": "not_established",
                "is_defect": True,
                "defect": {
                    "quoted_text": "exclusion-specific safeguards",
                    "disposition": "repair",
                    "evidence_classification": "not_established",
                    "reason": "Sources show general instruments, no exclusion-specific safeguard.",
                    "source_checks": [{
                        "source_id": "SRC-SAFEGUARD",
                        "quoted_text": "no exclusion-specific safeguard is described",
                    }],
                },
                "support_source_checks": [],
            },
            {
                "claim_id": ids[S_ACCESS],
                "role": "conditional_inference",
                "verdict": "not_established",
                "is_defect": False,
                "defect": None,
                "support_source_checks": [{
                    "source_id": "SRC-ACCESS",
                    "quoted_text": "no arrangement for traders near cancelled sites is described",
                }],
            },
        ],
    }


def _expected() -> dict:
    return {
        "true_defects": [
            {"object_id": "SUM-001", "paragraph_index": 0, "fragment": "flood-ready border posts"},
            {"object_id": "NARR-safeguard", "paragraph_index": 0, "fragment": "exclusion-specific safeguards"},
        ],
        "protected_claims": [
            {"object_id": "SUM-001", "paragraph_index": 0, "fragment": "Most displacement"},
            {"object_id": "NARR-safeguard", "paragraph_index": 1, "fragment": "retain access is not established"},
        ],
    }


# --- Enumeration -----------------------------------------------------------

def test_enumeration_is_deterministic_and_covers_every_sentence():
    module = _module()
    inventory = module.enumerate_claims(_reader())
    assert inventory["contract_version"] == module.CONTRACT_VERSION
    quotes = [claim["quoted_text"] for claim in inventory["claims"]]
    assert quotes == [S_DELIVER, S_DISPLACE, S_SAFEGUARD, S_ACCESS]
    # Re-running produces identical claim_ids (no randomness / ordering drift).
    again = module.enumerate_claims(_reader())
    assert again == inventory
    # Every claim is pinned to a real, unique span in its paragraph.
    for claim in inventory["claims"]:
        assert set(claim) == {"claim_id", "object_id", "paragraph_index", "quoted_text"}


# --- Adjudication contract -------------------------------------------------

def test_adjudication_requires_every_enumerated_claim_judged_once():
    module = _module()
    inventory = module.enumerate_claims(_reader())
    adjudication = _good_adjudication(module)
    adjudication["claim_judgments"].pop()  # drop the access claim
    with pytest.raises(module.ContractError):
        module.adjudicate_claims(inventory, _sources(), adjudication)


def test_adjudication_rejects_unknown_or_duplicate_claim_ids():
    module = _module()
    inventory = module.enumerate_claims(_reader())

    unknown = _good_adjudication(module)
    unknown["claim_judgments"][0]["claim_id"] = "SUM-001#p0#s99"
    with pytest.raises(module.ContractError):
        module.adjudicate_claims(inventory, _sources(), unknown)

    duplicate = _good_adjudication(module)
    duplicate["claim_judgments"][1]["claim_id"] = duplicate["claim_judgments"][0]["claim_id"]
    with pytest.raises(module.ContractError):
        module.adjudicate_claims(inventory, _sources(), duplicate)


def test_factual_assertion_judged_contradicted_cannot_be_marked_non_defect():
    """Closes the recall escape hatch: a contradicted factual claim must be a defect."""
    module = _module()
    inventory = module.enumerate_claims(_reader())
    adjudication = _good_adjudication(module)
    hatch = adjudication["claim_judgments"][0]
    hatch["is_defect"] = False
    hatch["defect"] = None
    with pytest.raises(module.ContractError):
        module.adjudicate_claims(inventory, _sources(), adjudication)


def test_supported_claim_cannot_carry_a_defect():
    module = _module()
    inventory = module.enumerate_claims(_reader())
    adjudication = _good_adjudication(module)
    supported = adjudication["claim_judgments"][1]
    supported["is_defect"] = True
    supported["defect"] = {
        "quoted_text": "Most displacement",
        "disposition": "repair",
        "evidence_classification": "contradicted",
        "reason": "invalid",
        "source_checks": [{"source_id": "SRC-DISPLACE", "quoted_text": "92 percent of displacement"}],
    }
    with pytest.raises(module.ContractError):
        module.adjudicate_claims(inventory, _sources(), adjudication)


def test_defect_requires_source_check_and_unique_span():
    module = _module()
    inventory = module.enumerate_claims(_reader())

    no_source = _good_adjudication(module)
    no_source["claim_judgments"][0]["defect"]["source_checks"] = []
    with pytest.raises(module.ContractError):
        module.adjudicate_claims(inventory, _sources(), no_source)

    bad_span = _good_adjudication(module)
    bad_span["claim_judgments"][0]["defect"]["quoted_text"] = "not in the sentence"
    with pytest.raises(module.ContractError):
        module.adjudicate_claims(inventory, _sources(), bad_span)

    foreign = _good_adjudication(module)
    foreign["claim_judgments"][0]["defect"]["source_checks"][0]["source_id"] = "SRC-NOPE"
    with pytest.raises(module.ContractError):
        module.adjudicate_claims(inventory, _sources(), foreign)


def test_valid_qualified_inference_is_preserved_not_forced_into_a_defect():
    module = _module()
    inventory = module.enumerate_claims(_reader())
    result = module.adjudicate_claims(inventory, _sources(), _good_adjudication(module))
    flagged = {finding["quoted_text"] for rr in result["review"]["record_reviews"]
               for finding in rr["findings"]}
    assert not any("access" in quote for quote in flagged)


# --- Downstream compatibility ---------------------------------------------

def test_adjudication_review_feeds_existing_repair_pipeline():
    module = _module()
    prototype = _prototype()
    inventory = module.enumerate_claims(_reader())
    result = module.adjudicate_claims(inventory, _sources(), _good_adjudication(module))

    review_input = prototype.prepare_review_input(_reader(), _sources())
    plan = prototype.plan_claim_repairs(review_input, result["review"])
    assert {finding["finding_id"] for finding in plan["findings"]} == set(result["defect_ids"])
    assert len(plan["findings"]) == 2


# --- Falsifiable acceptance scoring ---------------------------------------

def test_scoring_passes_when_true_defects_found_and_no_false_positives():
    module = _module()
    inventory = module.enumerate_claims(_reader())
    result = module.adjudicate_claims(inventory, _sources(), _good_adjudication(module))
    score = module.score_against_expected(result, _expected())
    assert score["passed"] is True
    assert score["missed_defects"] == []
    assert score["false_positives"] == []


def test_scoring_fails_on_a_missed_true_defect():
    """The exact failure mode of the paid run: a real defect goes unflagged."""
    module = _module()
    inventory = module.enumerate_claims(_reader())
    adjudication = _good_adjudication(module)
    # Downgrade the safeguard defect to a supported claim (recall miss).
    miss = adjudication["claim_judgments"][2]
    miss["verdict"] = "supported"
    miss["is_defect"] = False
    miss["defect"] = None
    result = module.adjudicate_claims(inventory, _sources(), adjudication)
    score = module.score_against_expected(result, _expected())
    assert score["passed"] is False
    assert any("exclusion-specific" in miss["fragment"] for miss in score["missed_defects"])


def test_scoring_fails_on_a_false_positive_against_protected_analysis():
    module = _module()
    inventory = module.enumerate_claims(_reader())
    adjudication = _good_adjudication(module)
    # Wrongly flag the valid qualified access question as a factual defect.
    access = adjudication["claim_judgments"][3]
    access["role"] = "factual_assertion"
    access["verdict"] = "not_established"
    access["is_defect"] = True
    access["defect"] = {
        "quoted_text": "retain access is not established",
        "disposition": "repair",
        "evidence_classification": "not_established",
        "reason": "over-flagged valid analysis",
        "source_checks": [{
            "source_id": "SRC-ACCESS",
            "quoted_text": "no arrangement for traders near cancelled sites is described",
        }],
    }
    result = module.adjudicate_claims(inventory, _sources(), adjudication)
    score = module.score_against_expected(result, _expected())
    assert score["passed"] is False
    assert score["false_positives"]
