"""Offline claim-level reader repair adapter; never grants publication approval."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sector_lenses.climate_final_reader import apply_reader_corrections


CONTRACT_VERSION = "climate-claim-repair-prototype-v1"
ROLES = {"factual_assertion", "conditional_inference", "proposed_action"}
DISPOSITIONS = {"repair", "disputed", "precision"}
CLASSIFICATIONS = {"contradicted", "not_established"}
OUTCOMES = {"resolved", "upheld", "unresolved"}


class ContractError(ValueError):
    """An offline adapter envelope or invariant is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _digest(value: object) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _exact(record: object, keys: set[str], name: str) -> dict[str, Any]:
    _require(isinstance(record, dict) and set(record) == keys, f"invalid {name}")
    return record


def _label(value: object, name: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), f"invalid {name}")
    return value


def _unique_quote(text: str, quote: object, name: str) -> str:
    _require(isinstance(quote, str) and bool(quote.strip()), f"invalid {name}")
    _require(text.find(quote) >= 0 and text.find(quote) == text.rfind(quote),
             f"{name} must be exact and unique")
    return quote


def _reader_records(reader: object) -> tuple[dict[str, list[str]], list[dict[str, object]]]:
    reader = _exact(
        reader, {"summary_paragraphs", "assessment_narratives"}, "reader",
    )
    _require(isinstance(reader["summary_paragraphs"], list), "invalid summaries")
    _require(isinstance(reader["assessment_narratives"], list), "invalid narratives")
    records: dict[str, list[str]] = {}
    normalized = []
    for key in ("summary_paragraphs", "assessment_narratives"):
        for record in reader[key]:
            _require(isinstance(record, dict), "invalid reader record")
            identifier = _label(record.get("object_id"), "object_id")
            _require(identifier not in records, "duplicate reader object_id")
            if key == "summary_paragraphs":
                text = record.get("text")
                _require(isinstance(text, str) and bool(text.strip()), "invalid summary text")
                paragraphs = [text]
            else:
                paragraphs = record.get("paragraphs")
                _require(
                    isinstance(paragraphs, list) and bool(paragraphs)
                    and all(isinstance(text, str) and text.strip() for text in paragraphs),
                    "invalid narrative paragraphs",
                )
                paragraphs = list(paragraphs)
            records[identifier] = paragraphs
            normalized.append({"object_id": identifier, "paragraphs": paragraphs})
    _require(bool(records), "reader has no records")
    return records, normalized


def _sources(source_registry: object) -> dict[str, str]:
    _require(isinstance(source_registry, dict) and bool(source_registry),
             "invalid source registry")
    _require(all(isinstance(key, str) and key.strip() for key in source_registry),
             "invalid source_id")
    _require(all(isinstance(text, str) and text.strip()
                 for text in source_registry.values()), "invalid source text")
    return source_registry


def _validate_source_checks(checks: object, sources: dict[str, str]) -> None:
    _require(isinstance(checks, list) and bool(checks), "source_checks required")
    seen: set[tuple[str, str]] = set()
    for check in checks:
        check = _exact(check, {"source_id", "quoted_text"}, "source check")
        source_id = _label(check["source_id"], "source_id")
        _require(source_id in sources, "foreign source_id")
        quote = _unique_quote(sources[source_id], check["quoted_text"], "source quote")
        _require((source_id, quote) not in seen, "duplicate source check")
        seen.add((source_id, quote))


def prepare_review_input(reader: dict, source_registry: dict[str, str]) -> dict:
    """Freeze application-owned reader text and sources for one review."""
    reader_copy = deepcopy(reader)
    source_copy = deepcopy(source_registry)
    _, records = _reader_records(reader_copy)
    _sources(source_copy)
    return {
        "contract_version": CONTRACT_VERSION,
        "reader": reader_copy,
        "reader_digest": _digest(reader_copy),
        "records": records,
        "source_registry": source_copy,
        "source_registry_digest": _digest(source_copy),
    }


def _validate_review_input(review_input: object) -> tuple[dict, dict[str, list[str]], dict[str, str]]:
    review_input = _exact(review_input, {
        "contract_version", "reader", "reader_digest", "records",
        "source_registry", "source_registry_digest",
    }, "review input")
    _require(review_input["contract_version"] == CONTRACT_VERSION, "wrong contract")
    records, normalized = _reader_records(review_input["reader"])
    sources = _sources(review_input["source_registry"])
    _require(review_input["reader_digest"] == _digest(review_input["reader"]),
             "reader digest drift")
    _require(review_input["source_registry_digest"] == _digest(sources),
             "source digest drift")
    _require(review_input["records"] == normalized, "record text drift")
    return review_input, records, sources


def _validate_finding(
    finding: object,
    object_id: str,
    records: dict[str, list[str]],
    sources: dict[str, str],
) -> dict:
    finding = _exact(finding, {
        "finding_id", "paragraph_index", "quoted_text", "role", "disposition",
        "evidence_classification", "reason", "source_checks",
    }, "finding")
    finding_id = _label(finding["finding_id"], "finding_id")
    index = finding["paragraph_index"]
    _require(type(index) is int and 0 <= index < len(records[object_id]),
             "invalid finding paragraph")
    _unique_quote(records[object_id][index], finding["quoted_text"], "finding quote")
    _require(isinstance(finding["role"], str) and finding["role"] in ROLES,
             "invalid finding role")
    _require(isinstance(finding["disposition"], str)
             and finding["disposition"] in DISPOSITIONS,
             "invalid finding disposition")
    _require(isinstance(finding["evidence_classification"], str)
             and finding["evidence_classification"] in CLASSIFICATIONS,
             "invalid evidence classification")
    _label(finding["reason"], "finding reason")
    _validate_source_checks(finding["source_checks"], sources)
    result = deepcopy(finding)
    result["finding_id"] = finding_id
    result["object_id"] = object_id
    return result


def plan_claim_repairs(review_input: dict, review: dict) -> dict:
    """Validate complete claim review and preserve every finding."""
    review_input, records, sources = _validate_review_input(review_input)
    review = _exact(review, {"reviewer_label", "record_reviews"}, "review")
    reviewer = _label(review["reviewer_label"], "reviewer_label")
    _require(isinstance(review["record_reviews"], list), "invalid record reviews")
    covered: set[str] = set()
    finding_ids: set[str] = set()
    findings = []
    for record_review in review["record_reviews"]:
        record_review = _exact(record_review, {"object_id", "findings"}, "record review")
        object_id = _label(record_review["object_id"], "object_id")
        _require(object_id in records and object_id not in covered,
                 "unknown or duplicate review object_id")
        covered.add(object_id)
        _require(isinstance(record_review["findings"], list), "invalid findings")
        for raw in record_review["findings"]:
            finding = _validate_finding(raw, object_id, records, sources)
            _require(finding["finding_id"] not in finding_ids, "duplicate finding_id")
            finding_ids.add(finding["finding_id"])
            findings.append(finding)
    _require(covered == set(records), "review does not cover every record")
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "planned",
        "original_reader": deepcopy(review_input["reader"]),
        "original_digest": review_input["reader_digest"],
        "original_records": deepcopy(review_input["records"]),
        "source_registry": deepcopy(sources),
        "source_registry_digest": review_input["source_registry_digest"],
        "initial_reviewer_label": reviewer,
        "findings": findings,
    }


def _validate_plan(plan: object) -> tuple[dict, dict[str, list[str]], dict[str, str]]:
    plan = _exact(plan, {
        "contract_version", "status", "original_reader", "original_digest",
        "original_records", "source_registry", "source_registry_digest",
        "initial_reviewer_label", "findings",
    }, "plan")
    _require(plan["contract_version"] == CONTRACT_VERSION and plan["status"] == "planned",
             "invalid plan state")
    records, normalized = _reader_records(plan["original_reader"])
    sources = _sources(plan["source_registry"])
    _require(plan["original_digest"] == _digest(plan["original_reader"]),
             "original digest drift")
    _require(plan["original_records"] == normalized, "original record drift")
    _require(plan["source_registry_digest"] == _digest(sources), "source digest drift")
    _label(plan["initial_reviewer_label"], "initial reviewer")
    _require(isinstance(plan["findings"], list), "invalid plan findings")
    seen = set()
    for finding in plan["findings"]:
        object_id = finding.get("object_id") if isinstance(finding, dict) else None
        _require(object_id in records, "invalid planned finding object")
        raw = {key: value for key, value in finding.items() if key != "object_id"}
        checked = _validate_finding(raw, object_id, records, sources)
        _require(checked["finding_id"] not in seen, "duplicate planned finding")
        seen.add(checked["finding_id"])
    return plan, records, sources


def apply_claim_repairs(plan: dict, correction: dict, editor_label: str) -> dict:
    """Apply one bounded correction pass and hold for independent review."""
    plan, records, sources = _validate_plan(plan)
    editor = _label(editor_label, "editor_label")
    correction = _exact(correction, {"edits", "disputed_finding_ids"}, "correction")
    _require(isinstance(correction["edits"], list), "invalid edits")
    disputes = correction["disputed_finding_ids"]
    _require(isinstance(disputes, list) and all(isinstance(item, str) for item in disputes),
             "invalid disputed finding IDs")
    _require(len(disputes) == len(set(disputes)), "duplicate disputed finding ID")
    findings = {item["finding_id"]: item for item in plan["findings"]}
    edited: set[str] = set()
    spans: dict[tuple[str, int], list[tuple[int, int]]] = {}
    grouped: dict[str, list[dict]] = {}
    for edit in correction["edits"]:
        edit = _exact(edit, {
            "finding_id", "object_id", "paragraph_index", "old_text", "new_text",
        }, "edit")
        finding_id = _label(edit["finding_id"], "edit finding_id")
        _require(finding_id in findings and finding_id not in edited,
                 "fabricated or duplicate edit finding_id")
        finding = findings[finding_id]
        _require(finding["disposition"] != "disputed", "disputed finding cannot be edited")
        _require(
            edit["object_id"] == finding["object_id"]
            and edit["paragraph_index"] == finding["paragraph_index"]
            and edit["old_text"] == finding["quoted_text"],
            "edit exceeds authorized span",
        )
        _require(isinstance(edit["new_text"], str), "invalid new text")
        text = records[finding["object_id"]][finding["paragraph_index"]]
        start = text.find(finding["quoted_text"])
        end = start + len(finding["quoted_text"])
        key = (finding["object_id"], finding["paragraph_index"])
        _require(not any(start < prior_end and prior_start < end
                         for prior_start, prior_end in spans.setdefault(key, [])),
                 "correction spans overlap")
        spans[key].append((start, end))
        grouped.setdefault(finding["object_id"], []).append({
            "paragraph_index": edit["paragraph_index"],
            "old_text": edit["old_text"],
            "new_text": edit["new_text"],
        })
        edited.add(finding_id)
    disputed = set(disputes)
    _require(disputed <= set(findings) and not disputed.intersection(edited),
             "invalid disputed finding IDs")
    repairs = {identifier for identifier, item in findings.items()
               if item["disposition"] == "repair"}
    _require(repairs == edited.intersection(repairs) | disputed.intersection(repairs),
             "every repair finding must be edited or disputed")

    corrected = deepcopy(plan["original_reader"])
    if grouped:
        response = {"corrections": [
            {"object_id": object_id, "edits": edits}
            for object_id, edits in grouped.items()
        ]}
        issues: list[dict] = []
        corrected = apply_reader_corrections(
            plan["original_reader"], response, set(grouped), issues=issues,
        )
        _require(corrected is not None, "existing correction validator rejected edit")
    current_records, normalized = _reader_records(corrected)
    _require(set(current_records) == set(records), "reader records changed")
    for object_id in set(records) - set(grouped):
        original = next(record for key in plan["original_reader"].values()
                        for record in key if record["object_id"] == object_id)
        current = next(record for key in corrected.values()
                       for record in key if record["object_id"] == object_id)
        _require(current == original, "unrelated reader record changed")
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "pending_independent_review",
        "original_reader": deepcopy(plan["original_reader"]),
        "original_digest": plan["original_digest"],
        "original_records": deepcopy(plan["original_records"]),
        "current_reader": corrected,
        "current_digest": _digest(corrected),
        "current_records": normalized,
        "source_registry": deepcopy(sources),
        "source_registry_digest": plan["source_registry_digest"],
        "initial_reviewer_label": plan["initial_reviewer_label"],
        "editor_label": editor,
        "editor_disputed_finding_ids": sorted(disputed),
        "findings": deepcopy(plan["findings"]),
    }


def _validate_pending(pending: object) -> tuple[dict, dict[str, list[str]], dict[str, str]]:
    pending = _exact(pending, {
        "contract_version", "status", "original_reader", "original_digest",
        "original_records", "current_reader", "current_digest", "current_records",
        "source_registry", "source_registry_digest", "initial_reviewer_label",
        "editor_label", "editor_disputed_finding_ids", "findings",
    }, "pending result")
    _require(pending["contract_version"] == CONTRACT_VERSION
             and pending["status"] == "pending_independent_review", "invalid pending state")
    original, original_normalized = _reader_records(pending["original_reader"])
    current, current_normalized = _reader_records(pending["current_reader"])
    sources = _sources(pending["source_registry"])
    _require(pending["original_digest"] == _digest(pending["original_reader"]),
             "original digest drift")
    _require(pending["current_digest"] == _digest(pending["current_reader"]),
             "current digest drift")
    _require(pending["original_records"] == original_normalized, "original text drift")
    _require(pending["current_records"] == current_normalized, "current text drift")
    _require(set(original) == set(current), "record coverage drift")
    _require(pending["source_registry_digest"] == _digest(sources), "source digest drift")
    _label(pending["initial_reviewer_label"], "initial reviewer")
    _label(pending["editor_label"], "editor")
    _require(isinstance(pending["editor_disputed_finding_ids"], list), "invalid disputes")
    _require(isinstance(pending["findings"], list), "invalid findings")
    ids = set()
    for finding in pending["findings"]:
        object_id = finding.get("object_id") if isinstance(finding, dict) else None
        _require(object_id in original, "invalid pending finding object")
        checked = _validate_finding(
            {key: value for key, value in finding.items() if key != "object_id"},
            object_id, original, sources,
        )
        _require(checked["finding_id"] not in ids, "duplicate pending finding")
        ids.add(checked["finding_id"])
    _require(set(pending["editor_disputed_finding_ids"]) <= ids,
             "fabricated pending dispute")
    return pending, current, sources


def finalize_claim_repairs(pending: dict, rereview: dict) -> dict:
    """Validate a distinct full re-review; success is not publication approval."""
    pending, records, sources = _validate_pending(pending)
    rereview = _exact(
        rereview, {"reviewer_label", "reader_digest", "record_reviews"}, "rereview",
    )
    reviewer = _label(rereview["reviewer_label"], "rereviewer_label")
    _require(reviewer not in {
        pending["editor_label"], pending["initial_reviewer_label"],
    }, "rereview must use a distinct execution label")
    _require(rereview["reader_digest"] == pending["current_digest"],
             "rereview digest mismatch")
    _require(isinstance(rereview["record_reviews"], list), "invalid rereview records")
    findings = {item["finding_id"]: item for item in pending["findings"]}
    covered: set[str] = set()
    outcomes: dict[str, str] = {}
    has_issues = False
    for record_review in rereview["record_reviews"]:
        record_review = _exact(
            record_review, {"object_id", "finding_outcomes", "issues"},
            "rereview record",
        )
        object_id = _label(record_review["object_id"], "rereview object_id")
        _require(object_id in records and object_id not in covered,
                 "unknown or duplicate rereview object_id")
        covered.add(object_id)
        _require(isinstance(record_review["finding_outcomes"], list),
                 "invalid finding outcomes")
        for outcome in record_review["finding_outcomes"]:
            outcome = _exact(outcome, {
                "finding_id", "outcome", "reason", "source_checks",
            }, "finding outcome")
            finding_id = _label(outcome["finding_id"], "outcome finding_id")
            _require(finding_id in findings and finding_id not in outcomes,
                     "fabricated or duplicate finding outcome")
            _require(findings[finding_id]["object_id"] == object_id,
                     "finding outcome assigned to wrong record")
            _require(isinstance(outcome["outcome"], str)
                     and outcome["outcome"] in OUTCOMES,
                     "invalid finding outcome")
            _label(outcome["reason"], "outcome reason")
            _validate_source_checks(outcome["source_checks"], sources)
            outcomes[finding_id] = outcome["outcome"]
        _require(isinstance(record_review["issues"], list), "invalid rereview issues")
        for issue in record_review["issues"]:
            issue = _exact(issue, {"reason", "source_checks"}, "rereview issue")
            _label(issue["reason"], "issue reason")
            _validate_source_checks(issue["source_checks"], sources)
        has_issues = has_issues or bool(record_review["issues"])
    _require(covered == set(records), "rereview does not cover every current record")
    _require(set(outcomes) == set(findings), "rereview does not adjudicate every finding")
    precision_ids = {
        identifier for identifier, finding in findings.items()
        if finding["disposition"] == "precision"
    }
    passed = not has_issues and all(
        outcomes[identifier] == "resolved" for identifier in set(findings) - precision_ids
    )
    return {
        "status": "accepted_offline_prototype" if passed else "withheld",
        "reader_digest": pending["current_digest"],
        "publication_approved": False,
        "optional_precision_findings": [
            {"finding_id": identifier, "outcome": outcomes[identifier]}
            for identifier in sorted(precision_ids)
        ],
    }
