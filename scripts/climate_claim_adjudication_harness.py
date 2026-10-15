"""Offline enumerate->adjudicate harness; never grants publication approval.

Rationale. In the paid experiment the single open-ended "discovery" reviewer
returned an empty findings list for every record, missing both known factual
defects, while the second reviewer correctly judged the same claims once they were
PRESENTED to it. The failure mechanism was the task shape: asking one conservative
prompt to VOLUNTEER defects makes the empty set the cheapest compliant answer.

This harness separates the two roles:
1. ``enumerate_claims`` deterministically lists every atomic claim (sentence) in the
   reader. It makes no judgement, so there is no empty-set escape hatch.
2. ``adjudicate_claims`` validates a per-claim judgement that must address every
   enumerated claim exactly once and cannot leave a contradicted factual assertion
   silently unflagged. Its output is a ``review`` that feeds the existing, validated
   ``climate_claim_repair_prototype`` pipeline unchanged.

Traceability is enforced (exact unique quotes, real source ids, full coverage).
Entailment and claim-inventory completeness remain model/human judgements: exact
quotes prove traceability, not meaning, and enumeration recall must be verified
out of band. Nothing here authorises publication or a paid run.
"""

from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path
import re
import sys


_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


def _load_prototype():
    path = _HERE / "climate_claim_repair_prototype.py"
    spec = importlib.util.spec_from_file_location("climate_claim_repair_prototype", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_P = _load_prototype()

# Reuse the prototype's error type and validated primitives so both stages share
# one contract vocabulary.
ContractError = _P.ContractError
_require = _P._require
_digest = _P._digest
_label = _P._label
_unique_quote = _P._unique_quote
_sources = _P._sources
_reader_records = _P._reader_records
_validate_source_checks = _P._validate_source_checks

CONTRACT_VERSION = "climate-claim-adjudication-harness-v1"
ROLES = _P.ROLES
VERDICTS = {"supported", "contradicted", "not_established"}
DEFECT_CLASSIFICATIONS = {"contradicted", "not_established"}
DISPOSITIONS = _P.DISPOSITIONS

# Split on sentence-final punctuation followed by whitespace. Decimals such as
# "67.1 percent" are untouched because the period is not followed by a space.
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.?!])\s+")


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_BOUNDARY.split(text.strip()) if part.strip()]


def enumerate_claims(reader: dict) -> dict:
    """Deterministically list every atomic claim (sentence) in the reader."""
    reader_copy = deepcopy(reader)
    _, normalized = _reader_records(reader_copy)
    claims: list[dict] = []
    for record in normalized:
        object_id = record["object_id"]
        for paragraph_index, paragraph in enumerate(record["paragraphs"]):
            sentences = _split_sentences(paragraph)
            _require(bool(sentences), "paragraph has no enumerable claim")
            for position, sentence in enumerate(sentences):
                _unique_quote(paragraph, sentence, "enumerated claim")
                claims.append({
                    "claim_id": f"{object_id}#p{paragraph_index}#s{position}",
                    "object_id": object_id,
                    "paragraph_index": paragraph_index,
                    "quoted_text": sentence,
                })
    _require(bool(claims), "reader has no enumerable claims")
    _require(len({claim["claim_id"] for claim in claims}) == len(claims),
             "duplicate claim_id")
    return {
        "contract_version": CONTRACT_VERSION,
        "reader": reader_copy,
        "reader_digest": _digest(reader_copy),
        "claims": claims,
    }


def _validate_inventory(inventory: object) -> tuple[dict, dict[str, dict]]:
    inventory = _P._exact(inventory, {
        "contract_version", "reader", "reader_digest", "claims",
    }, "inventory")
    _require(inventory["contract_version"] == CONTRACT_VERSION, "wrong contract")
    _require(inventory["reader_digest"] == _digest(inventory["reader"]),
             "inventory reader digest drift")
    records, _ = _reader_records(inventory["reader"])
    _require(isinstance(inventory["claims"], list) and bool(inventory["claims"]),
             "invalid claims")
    by_id: dict[str, dict] = {}
    for claim in inventory["claims"]:
        claim = _P._exact(
            claim, {"claim_id", "object_id", "paragraph_index", "quoted_text"}, "claim",
        )
        claim_id = _label(claim["claim_id"], "claim_id")
        _require(claim_id not in by_id, "duplicate claim_id")
        object_id = _label(claim["object_id"], "claim object_id")
        _require(object_id in records, "claim names unknown record")
        index = claim["paragraph_index"]
        _require(type(index) is int and 0 <= index < len(records[object_id]),
                 "invalid claim paragraph_index")
        _unique_quote(records[object_id][index], claim["quoted_text"], "claim quote")
        by_id[claim_id] = claim
    return inventory, by_id


def _validate_defect(defect: object, claim: dict, sources: dict[str, str]) -> dict:
    defect = _P._exact(defect, {
        "quoted_text", "disposition", "evidence_classification", "reason",
        "source_checks",
    }, "defect")
    _unique_quote(claim["quoted_text"], defect["quoted_text"], "defect span")
    _require(defect["disposition"] in DISPOSITIONS, "invalid defect disposition")
    _require(defect["evidence_classification"] in DEFECT_CLASSIFICATIONS,
             "invalid defect classification")
    _label(defect["reason"], "defect reason")
    _validate_source_checks(defect["source_checks"], sources)
    return defect


def adjudicate_claims(inventory: dict, source_registry: dict, adjudication: dict) -> dict:
    """Validate a per-claim judgement and emit a repair-pipeline review."""
    inventory, by_id = _validate_inventory(inventory)
    sources = _sources(deepcopy(source_registry))
    adjudication = _P._exact(
        adjudication, {"reviewer_label", "claim_judgments"}, "adjudication",
    )
    reviewer = _label(adjudication["reviewer_label"], "reviewer_label")
    _require(isinstance(adjudication["claim_judgments"], list)
             and bool(adjudication["claim_judgments"]), "invalid claim_judgments")

    judged: set[str] = set()
    findings_by_object: dict[str, list[dict]] = {claim["object_id"]: []
                                                 for claim in by_id.values()}
    defect_ids: list[str] = []
    defects: list[dict] = []
    for judgment in adjudication["claim_judgments"]:
        judgment = _P._exact(judgment, {
            "claim_id", "role", "verdict", "is_defect", "defect",
            "support_source_checks",
        }, "claim judgment")
        claim_id = _label(judgment["claim_id"], "judgment claim_id")
        _require(claim_id in by_id and claim_id not in judged,
                 "unknown or duplicate judged claim_id")
        judged.add(claim_id)
        claim = by_id[claim_id]
        _require(judgment["role"] in ROLES, "invalid claim role")
        _require(judgment["verdict"] in VERDICTS, "invalid verdict")
        _require(type(judgment["is_defect"]) is bool, "invalid is_defect flag")
        _require(isinstance(judgment["support_source_checks"], list),
                 "invalid support_source_checks")
        if judgment["support_source_checks"]:
            _validate_source_checks(judgment["support_source_checks"], sources)

        # A supported claim is never a defect; a contradicted/not-established
        # FACTUAL assertion must be flagged (this closes the recall escape hatch).
        _require(not (judgment["verdict"] == "supported" and judgment["is_defect"]),
                 "supported claim cannot be a defect")
        if judgment["role"] == "factual_assertion" and judgment["verdict"] in DEFECT_CLASSIFICATIONS:
            _require(judgment["is_defect"],
                     "contradicted factual assertion must be a defect")

        if judgment["is_defect"]:
            defect = _validate_defect(judgment["defect"], claim, sources)
            findings_by_object[claim["object_id"]].append({
                "finding_id": claim_id,
                "paragraph_index": claim["paragraph_index"],
                "quoted_text": defect["quoted_text"],
                "role": judgment["role"],
                "disposition": defect["disposition"],
                "evidence_classification": defect["evidence_classification"],
                "reason": defect["reason"],
                "source_checks": deepcopy(defect["source_checks"]),
            })
            defect_ids.append(claim_id)
            defects.append({
                "finding_id": claim_id,
                "object_id": claim["object_id"],
                "paragraph_index": claim["paragraph_index"],
                "quoted_text": defect["quoted_text"],
                "evidence_classification": defect["evidence_classification"],
            })
        else:
            _require(judgment["defect"] is None, "non-defect carries a defect object")

    _require(judged == set(by_id), "adjudication does not judge every enumerated claim")

    record_reviews = [
        {"object_id": object_id, "findings": findings_by_object[object_id]}
        for object_id in findings_by_object
    ]
    return {
        "contract_version": CONTRACT_VERSION,
        "reviewer_label": reviewer,
        "coverage": sorted(judged),
        "review": {"reviewer_label": reviewer, "record_reviews": record_reviews},
        "defect_ids": defect_ids,
        "defects": defects,
    }


def _overlaps(span: str, fragment: str) -> bool:
    return fragment in span or span in fragment


def score_against_expected(adjudication_result: dict, expected: dict) -> dict:
    """Falsifiable acceptance: find the true defects and raise no false positives."""
    expected = _P._exact(expected, {"true_defects", "protected_claims"}, "expected")
    defects = adjudication_result["defects"]

    matched: set[int] = set()
    missed: list[dict] = []
    for target in expected["true_defects"]:
        hit = None
        for position, defect in enumerate(defects):
            if (defect["object_id"] == target["object_id"]
                    and defect["paragraph_index"] == target["paragraph_index"]
                    and _overlaps(defect["quoted_text"], target["fragment"])):
                hit = position
                break
        if hit is None:
            missed.append(target)
        else:
            matched.add(hit)

    false_positives: list[dict] = []
    for position, defect in enumerate(defects):
        if position in matched:
            continue
        protected = any(
            guard["object_id"] == defect["object_id"]
            and guard["paragraph_index"] == defect["paragraph_index"]
            and _overlaps(defect["quoted_text"], guard["fragment"])
            for guard in expected["protected_claims"]
        )
        false_positives.append({
            "finding_id": defect["finding_id"],
            "quoted_text": defect["quoted_text"],
            "protected_analysis": protected,
        })

    return {
        "passed": not missed and not false_positives,
        "missed_defects": missed,
        "false_positives": false_positives,
    }
