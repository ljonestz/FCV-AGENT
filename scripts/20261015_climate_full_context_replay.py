"""Rebuild and score the frozen quality13 reviewer context without provider calls.

Raw source blocks, saved model responses, and rebuilt review payloads are written
only to the requested output path. The tracked manifest contains hashes and
human-reviewed, source-backed expectations rather than model output.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sector_lenses.climate_final_reader import (
    apply_reader_corrections,
    reader_correction_allowed_numeric_date_tokens,
    reader_support_records,
    reviewed_final_reader,
)
from sector_lenses.climate_operational_guidance import (
    GUIDANCE_REGISTRY_VERSION,
    select_operational_guidance,
)
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_runtime import prepare_verified_sources


DEFAULT_MANIFEST = (
    ROOT / "tests" / "fixtures" / "climate"
    / "quality13_full_context_acceptance.json"
)
DEFAULT_OUTPUT = (
    ROOT / "output" / "playwright"
    / "20261015-quality13-full-context-acceptance-v3.json"
)


class ReplayFailure(RuntimeError):
    """The frozen evidence is incomplete, changed, or internally inconsistent."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_artifact(root: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    candidates = [root / relative]
    # A worktree does not contain the intentionally untracked public benchmark;
    # use the shared repository root when it is present there.
    if root.parent.name == ".worktrees":
        candidates.append(root.parent.parent / relative)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ReplayFailure(f"required artifact is missing: {relative_path}")


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReplayFailure(f"{label} is not readable JSON") from error
    if not isinstance(value, dict):
        raise ReplayFailure(f"{label} must be a JSON object")
    return value


def _verify_artifacts(
    manifest: dict[str, Any], artifact_root: Path,
) -> tuple[dict[str, Path], dict[str, Any]]:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise ReplayFailure("manifest artifacts are required")
    resolved: dict[str, Path] = {}
    checks: dict[str, Any] = {}
    for label, record in artifacts.items():
        if not isinstance(record, dict):
            raise ReplayFailure(f"{label} artifact record is malformed")
        relative_path = record.get("path")
        expected_hash = record.get("sha256")
        if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
            raise ReplayFailure(f"{label} artifact path and hash are required")
        path = _resolve_artifact(artifact_root, relative_path)
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            raise ReplayFailure(
                f"{label} hash mismatch: expected {expected_hash}, got {actual_hash}"
            )
        resolved[label] = path
        checks[label] = {
            "path": relative_path,
            "sha256": actual_hash,
            "bytes": path.stat().st_size,
            "verified": True,
        }
    checks["all_verified"] = True
    return resolved, checks


def _snapshot_json(snapshot: object, label: str) -> Any:
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("json"), str):
        raise ReplayFailure(f"saved {label} snapshot is missing")
    try:
        return json.loads(snapshot["json"])
    except json.JSONDecodeError as error:
        raise ReplayFailure(f"saved {label} snapshot is not complete JSON") from error


def _initial_readiness_flags(review_snapshot: object) -> list[dict[str, Any]]:
    """Recover the complete first field from the intentionally capped snapshot."""

    if not isinstance(review_snapshot, dict) or not isinstance(
        review_snapshot.get("json"), str
    ):
        raise ReplayFailure("saved conditional review input is missing")
    raw = review_snapshot["json"]
    try:
        start = raw.index("[")
        value, _ = json.JSONDecoder().raw_decode(raw[start:])
    except (ValueError, json.JSONDecodeError) as error:
        raise ReplayFailure("saved readiness flags cannot be recovered") from error
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ReplayFailure("saved readiness flags are malformed")
    return value


def _source_context(
    source_path: Path, expected_text_hash: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reader = PdfReader(str(source_path))
    raw_text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    prepared = prepare_verified_sources([{
        "label": "PROJECT DOCUMENT",
        "name": source_path.name,
        "raw_text": raw_text,
    }])
    if len(prepared.documents) != 1:
        raise ReplayFailure("public source did not produce one source document")
    document = prepared.documents[0]
    if document.sha256 != expected_text_hash:
        raise ReplayFailure(
            "public source extracted-text hash mismatch: "
            f"expected {expected_text_hash}, got {document.sha256}"
        )
    return [asdict(block) for block in prepared.blocks], {
        "document_id": document.document_id,
        "extracted_text_sha256": document.sha256,
        "pages": len(reader.pages),
        "source_blocks": len(prepared.blocks),
    }


def _drafting_artifacts(
    assessment: dict[str, Any], candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    suppressions = assessment["diagnostic_trace"].get("drafting_suppressions", [])
    pre_review_suppressed = {
        (item.get("recommendation_id"), item.get("artifact"))
        for item in suppressions
        if isinstance(item, dict) and "artifact" in item
    }
    artifacts = []
    for candidate in candidates:
        recommendation_id = candidate.get("recommendation_id")
        for block in candidate.get("drafting_blocks", []):
            if not isinstance(block, dict):
                continue
            role = block.get("drafting_role")
            field = f"{role}_drafting"
            if (recommendation_id, field) in pre_review_suppressed:
                continue
            artifacts.append({
                "object_id": f"{recommendation_id}::{role}",
                "recommendation_id": recommendation_id,
                "block": block,
            })
    return artifacts


def _rebuild_inputs(
    state: dict[str, Any], source_blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    assessment = state.get("assessment")
    if not isinstance(assessment, dict):
        raise ReplayFailure("quality13 assessment is missing")
    trace = assessment.get("diagnostic_trace")
    if not isinstance(trace, dict):
        raise ReplayFailure("quality13 diagnostic trace is missing")

    recommendations = _snapshot_json(
        trace.get("reviewed_recommendations"), "reviewed recommendations"
    )
    candidates = _snapshot_json(
        trace.get("recommendation_candidates"), "recommendation candidates"
    )
    readiness = _initial_readiness_flags(trace.get("review_input"))
    if not isinstance(recommendations, list) or not isinstance(candidates, list):
        raise ReplayFailure("saved recommendation registers are malformed")
    operation_context = assessment.get("operation_context", {})
    guidance = select_operational_guidance(
        doc_type=str(operation_context.get("document_type") or "Unknown"),
        instrument_type=str(operation_context.get("instrument_type") or "Unknown"),
        is_mpa=bool(operation_context.get("is_mpa")),
    )
    conditional_payload = {
        "readiness_flags": readiness,
        "source_blocks": source_blocks,
        "facts": assessment.get("facts", []),
        "analysis": assessment.get("analysis", {}),
        "context_evidence": assessment.get("context_evidence", []),
        "judgments": assessment.get("judgments", {}),
        "recommendations": recommendations,
        "drafting_artifacts": _drafting_artifacts(assessment, candidates),
        "operation_context": operation_context,
        "current_document": operation_context.get("document_type", "Unknown"),
        "guidance_registry_version": GUIDANCE_REGISTRY_VERSION,
        "operational_guidance": [item.as_record() for item in guidance],
    }
    reader_assessment = {
        "facts": assessment.get("facts", []),
        "derived_assertions": assessment.get("derived_assertions", []),
        "analysis": assessment.get("analysis", {}),
        "context_evidence": assessment.get("context_evidence", []),
        "judgments": assessment.get("judgments", {}),
        "executive_readout": assessment.get("executive_readout", {}),
        "priorities": assessment.get("priorities", []),
    }
    support_records = reader_support_records(reader_assessment)
    initial_reader = _snapshot_json(
        trace.get("final_reader", {}).get("initial"), "initial final reader"
    )
    if not isinstance(initial_reader, dict):
        raise ReplayFailure("saved initial final reader is malformed")
    reader_payload = {
        "support_records": support_records,
        "judgments": assessment.get("judgments", {}),
        "executive_readout": assessment.get("executive_readout", {}),
        "accepted_recommendation_ids": [
            item.get("recommendation_id")
            for item in assessment.get("priorities", [])
            if isinstance(item, dict)
        ],
        "operation_context": operation_context,
        "final_reader": initial_reader,
    }
    return {
        "conditional": conditional_payload,
        "reader": reader_payload,
        "recorded_conditional_review": _snapshot_json(
            trace.get("semantic_review"), "semantic review"
        ),
        "recorded_reader_review": _snapshot_json(
            trace.get("final_reader", {}).get("meaning_reviews", [None])[0],
            "reader meaning review",
        ),
    }


def _decisions(
    assessment: dict[str, Any], inputs: dict[str, Any],
) -> dict[str, dict[str, dict[str, Any]]]:
    accepted_core = {
        item.get("recommendation_id")
        for item in assessment.get("priorities", [])
        if isinstance(item, dict)
    }
    all_core = {
        item.get("recommendation_id")
        for item in inputs["conditional"]["recommendations"]
        if isinstance(item, dict)
    }
    accepted_readiness = {
        item.get("flag_id")
        for item in assessment.get("review_readiness_flags", [])
        if isinstance(item, dict)
    }
    all_readiness = {
        item.get("flag_id")
        for item in inputs["conditional"]["readiness_flags"]
        if isinstance(item, dict)
    }
    reader_review = inputs["recorded_reader_review"]
    rejected_reader = set(reader_review.get("object_ids", []))
    issues_by_id = {
        item.get("object_id"): item
        for item in reader_review.get("issues", [])
        if isinstance(item, dict)
    }
    records = (
        inputs["reader"]["final_reader"].get("summary_paragraphs", [])
        + inputs["reader"]["final_reader"].get("assessment_narratives", [])
    )
    all_reader = {
        item.get("object_id") for item in records if isinstance(item, dict)
    }
    return {
        "core": {
            identifier: {
                "decision": "accept" if identifier in accepted_core else "reject",
                "reason_codes": [],
            }
            for identifier in all_core
        },
        "readiness": {
            identifier: {
                "decision": "accept" if identifier in accepted_readiness else "reject",
                "reason_codes": [],
            }
            for identifier in all_readiness
        },
        "reader": {
            identifier: {
                "decision": "reject" if identifier in rejected_reader else "accept",
                "reason_codes": issues_by_id.get(identifier, {}).get(
                    "reason_codes", []
                ),
            }
            for identifier in all_reader
        },
    }


def _core_decision_lifecycle(
    assessment: dict[str, Any], inputs: dict[str, Any],
) -> dict[str, Any]:
    review = inputs["recorded_conditional_review"]
    core_ids = {
        item.get("recommendation_id")
        for item in inputs["conditional"]["recommendations"]
        if isinstance(item, dict)
    }
    initially_rejected = set(review.get("object_ids", [])) & core_ids
    initially_passed = set(review.get("passed_core_ids", [])) & core_ids
    correction = assessment["diagnostic_trace"].get(
        "recommendation_correction", {}
    )
    recovered = set(correction.get("recovered_ids", [])) & core_ids
    final_accepted = {
        item.get("recommendation_id")
        for item in assessment.get("priorities", [])
        if isinstance(item, dict)
    }
    return {
        "initial_passed_core_ids": sorted(initially_passed),
        "initial_rejected_core_ids": sorted(initially_rejected),
        "correction_recovered_core_ids": sorted(recovered),
        "final_accepted_core_ids": sorted(final_accepted),
        "acceptance_scored_at": "final_admission_after_bounded_core_correction",
    }


def _evaluate(
    expectations: dict[str, Any], recorded: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    failures = []
    results = []
    if set(expectations) != set(recorded):
        raise ReplayFailure("expectation stages do not match reconstructed stages")
    for stage, expected_objects in expectations.items():
        actual_objects = recorded[stage]
        if set(expected_objects) != set(actual_objects):
            raise ReplayFailure(
                f"{stage} expectations do not cover the complete reconstructed payload"
            )
        for object_id, expected in expected_objects.items():
            actual = actual_objects[object_id]
            object_failures = []
            if expected.get("decision") != actual.get("decision"):
                object_failures.append("decision_mismatch")
            actual_codes = set(actual.get("reason_codes", []))
            for code in expected.get("required_reason_codes", []):
                if code not in actual_codes:
                    object_failures.append("required_reason_code_missing")
            for code in expected.get("forbidden_reason_codes", []):
                if code in actual_codes:
                    object_failures.append("forbidden_reason_code")
            results.append({
                "stage": stage,
                "object_id": object_id,
                "expected_decision": expected.get("decision"),
                "recorded_decision": actual.get("decision"),
                "recorded_reason_codes": sorted(actual_codes),
                "passed": not object_failures,
            })
            failures.extend({
                "stage": stage,
                "object_id": object_id,
                "failure": failure,
            } for failure in object_failures)
    return results, failures


def _correction_guard(assessment: dict[str, Any]) -> dict[str, Any]:
    correction = assessment["diagnostic_trace"]["final_reader"].get(
        "correction", {}
    )
    codes = []
    for issue in correction.get("issues", []):
        if isinstance(issue, dict):
            for code in issue.get("reason_codes", []):
                if isinstance(code, str) and code not in codes:
                    codes.append(code)
    accepted = not codes
    return {
        "accepted": accepted,
        "reason_codes": codes,
        "assessment": (
            "guard_worked_as_designed"
            if codes == ["READER_CORRECTION_SUMMARY_NUMBER_UNSUPPORTED"]
            else "unexpected_guard_result"
        ),
    }


def _minimal_reader_correction_illustration(
    initial_reader: dict[str, Any],
    assessment: dict[str, Any],
) -> dict[str, Any]:
    """Run two exact edits through the native merger without semantic admission."""

    replacements = [
        ("The immediate benefit is", "The intended immediate benefit is"),
        ("flood-ready border posts", "planned flood-resilient border posts"),
    ]
    response = {"corrections": [{
        "object_id": "NARR-dividends",
        "edits": [
            {"paragraph_index": 0, "old_text": old, "new_text": new}
            for old, new in replacements
        ],
    }]}
    merge_issues: list[dict[str, Any]] = []
    corrected = apply_reader_corrections(
        initial_reader, response, {"NARR-dividends"}, issues=merge_issues
    )
    if corrected is None:
        raise ReplayFailure(f"native correction illustration failed: {merge_issues}")

    def digest(record: dict[str, Any]) -> str:
        raw = json.dumps(record, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    original_records = {
        item["object_id"]: item
        for item in initial_reader.get("summary_paragraphs", [])
        + initial_reader.get("assessment_narratives", [])
    }
    corrected_records = {
        item["object_id"]: item
        for item in corrected.get("summary_paragraphs", [])
        + corrected.get("assessment_narratives", [])
    }
    changed = [
        identifier for identifier in original_records
        if digest(original_records[identifier]) != digest(corrected_records[identifier])
    ]
    original_tokens = reader_correction_allowed_numeric_date_tokens(
        original_records["NARR-dividends"]
    )
    corrected_tokens = reader_correction_allowed_numeric_date_tokens(
        corrected_records["NARR-dividends"]
    )
    withheld_summary, withheld_narratives = reviewed_final_reader(
        corrected, {}, assessment
    )
    return {
        "changed_object_ids": changed,
        "exact_replacements": [
            {"old": old, "new": new} for old, new in replacements
        ],
        "all_other_records_byte_stable": changed == ["NARR-dividends"],
        "numeric_date_tokens_unchanged": original_tokens == corrected_tokens,
        "native_merge_issues": merge_issues,
        "corrected_record": corrected_records["NARR-dividends"],
        "semantic_acceptance_proven": bool(
            withheld_summary or withheld_narratives
        ),
        "review_without_clean_pass_withheld": not (
            withheld_summary or withheld_narratives
        ),
        "scope_note": (
            "This illustrates a bounded status correction only. It does not "
            "repair or accept any core recommendation or simulate reviewer judgment."
        ),
    }


def _candidate_reader_review_input(
    historical_reader_input: dict[str, Any],
    facts: list[dict[str, Any]],
    source_blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the current candidate payload separately from the historical baseline."""

    cited_ids = {
        block_id
        for fact in facts if isinstance(fact, dict)
        for block_id in fact.get("source_block_ids", [])
        if isinstance(block_id, str)
    }
    source_passages = [
        block for block in source_blocks if block.get("block_id") in cited_ids
    ]
    payload = deepcopy(historical_reader_input)
    payload["source_passages"] = source_passages
    return {
        "payload": payload,
        "rendered_current_prompt": build_verified_stage_prompt(
            "reader_review", payload
        ),
        "source_passage_count": len(source_passages),
        "acceptance_expectations_included": False,
        "semantic_acceptance_proven": False,
        "scope_note": (
            "This is the repaired candidate input shape using the current local "
            "prompt and original cited passages. Recorded quality13 decisions are "
            "scored only against the separate historical baseline input."
        ),
    }


def run_replay(
    *, manifest_path: Path = DEFAULT_MANIFEST, artifact_root: Path = ROOT,
    output_path: Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    """Run a deterministic, network-free comparison of the frozen decisions."""

    manifest = _load_json(manifest_path, "expectation manifest")
    resolved, artifact_checks = _verify_artifacts(manifest, artifact_root)
    state = _load_json(resolved["quality13_state"], "quality13 state")
    session = _load_json(resolved["quality13_session"], "quality13 session")
    # Parse historical artifacts as part of fail-closed provenance verification.
    _load_json(resolved["quality12_state"], "quality12 state")
    _load_json(resolved["quality12_session"], "quality12 session")
    assessment = state.get("assessment")
    if not isinstance(assessment, dict):
        raise ReplayFailure("quality13 assessment is missing")
    session_assessment = session.get("climateVerifiedAssessment")
    if (
        not isinstance(session_assessment, dict)
        or session_assessment.get("run_id") != assessment.get("run_id")
    ):
        raise ReplayFailure("quality13 state and session run IDs do not match")

    source_record = manifest["artifacts"]["public_source"]
    source_blocks, source_reconstruction = _source_context(
        resolved["public_source"], source_record["extracted_text_sha256"]
    )
    inputs = _rebuild_inputs(state, source_blocks)
    recorded = _decisions(assessment, inputs)
    core_lifecycle = _core_decision_lifecycle(assessment, inputs)
    expectations = manifest.get("expectations")
    if not isinstance(expectations, dict):
        raise ReplayFailure("manifest expectations are required")
    decision_results, failures = _evaluate(expectations, recorded)
    correction_guard = _correction_guard(assessment)
    correction_illustration = _minimal_reader_correction_illustration(
        inputs["reader"]["final_reader"], assessment
    )
    candidate_reader_input = _candidate_reader_review_input(
        inputs["reader"], assessment.get("facts", []), source_blocks
    )

    reader_records = (
        inputs["reader"]["final_reader"]["summary_paragraphs"]
        + inputs["reader"]["final_reader"]["assessment_narratives"]
    )
    local_integration = {
        "required_artifacts": len(resolved),
        "verified": artifact_checks["all_verified"],
    }
    raw_bundle = {
        "schema_version": manifest["schema_version"],
        "provider_calls": 0,
        "network_used": False,
        "local_artifact_integration": local_integration,
        "artifact_verification": artifact_checks,
        "source_reconstruction": source_reconstruction,
        "input_fidelity": {
            "conditional_review": (
                "complete semantic context reconstructed from the public source "
                "and saved registers; pre-normalization drafting candidate text "
                "is included because the capped diagnostic cannot prove exact bytes"
            ),
            "reader_review": (
                "deterministic input rebuilt from saved accepted registers; initial "
                "reader output and recorded review are captured exactly"
            ),
        },
        "conditional_review_input": {
            "payload": inputs["conditional"],
            "recommendations_by_id": {
                item["recommendation_id"]: item
                for item in inputs["conditional"]["recommendations"]
            },
            "readiness_flags_by_id": {
                item["flag_id"]: item
                for item in inputs["conditional"]["readiness_flags"]
            },
        },
        "reader_review_input": {
            "payload": inputs["reader"],
            "support_records": inputs["reader"]["support_records"],
            "final_reader_by_id": {
                item["object_id"]: item for item in reader_records
            },
        },
        "candidate_reader_review_input": candidate_reader_input,
        "recorded_reviews": {
            "conditional_review": inputs["recorded_conditional_review"],
            "reader_review": inputs["recorded_reader_review"],
        },
        "recorded_decisions": recorded,
        "recorded_decision_lifecycle": {"core": core_lifecycle},
        "decision_semantics": manifest.get("decision_semantics", {}),
        "decision_results": decision_results,
        "failures": failures,
        "correction_guard": correction_guard,
        "minimal_reader_correction_illustration": correction_illustration,
        "context_counts": {
            "source_blocks": len(source_blocks),
            "facts": len(assessment.get("facts", [])),
            "core_recommendations": len(inputs["conditional"]["recommendations"]),
            "readiness_flags": len(inputs["conditional"]["readiness_flags"]),
            "reader_objects": len(reader_records),
            "reader_support_records": len(inputs["reader"]["support_records"]),
        },
        "limits": manifest.get("limits", []),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as handle:
        json.dump(raw_bundle, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return {
        "passed": not failures,
        "provider_calls": 0,
        "network_used": False,
        "local_artifact_integration": local_integration,
        "failures": failures,
        "decision_results": decision_results,
        "correction_guard": correction_guard,
        "limits": manifest.get("limits", []),
        "raw_bundle_path": str(output_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay frozen quality13 reviewer decisions offline."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--artifact-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        report = run_replay(
            manifest_path=args.manifest,
            artifact_root=args.artifact_root,
            output_path=args.output,
        )
    except ReplayFailure as error:
        print(json.dumps({"passed": False, "error": str(error)}))
        return 2
    print(json.dumps({
        "passed": report["passed"],
        "provider_calls": 0,
        "failure_count": len(report["failures"]),
        "raw_bundle_path": report["raw_bundle_path"],
    }))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
