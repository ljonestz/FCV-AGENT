from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "20261015_climate_full_context_replay.py"
MANIFEST = (
    ROOT / "tests" / "fixtures" / "climate"
    / "quality13_full_context_acceptance.json"
)


def _local_artifacts_available() -> bool:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for record in manifest["artifacts"].values():
        relative = Path(record["path"])
        if not (ROOT / relative).is_file() and not (
            ROOT.parent.name == ".worktrees"
            and (ROOT.parent.parent / relative).is_file()
        ):
            return False
    return True


LOCAL_ARTIFACTS = _local_artifacts_available()


def _module():
    spec = importlib.util.spec_from_file_location("quality13_replay", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_manifest_contains_only_source_backed_labels_and_artifact_references():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "quality13-full-context-acceptance-v1"
    assert set(manifest["expectations"]) == {"core", "readiness", "reader"}
    assert set(manifest["expectations"]["core"]) == {
        "REC-001", "REC-002", "REC-003", "REC-004", "REC-005",
    }
    assert set(manifest["expectations"]["readiness"]) == {
        "DIF-001", "DIF-002", "DIF-003", "DIF-004",
    }
    assert set(manifest["expectations"]["reader"]) == {
        "SUM-001", "SUM-002", "NARR-design", "NARR-dividends",
        "NARR-inclusion",
    }
    assert all(
        item["source_refs"] and item["reason"]
        for group in manifest["expectations"].values()
        for item in group.values()
    )
    serialized = json.dumps(manifest)
    assert "raw_response" not in serialized
    assert "explanation\"" not in serialized
    assert "mocked response" in serialized


@pytest.mark.skipif(not LOCAL_ARTIFACTS, reason="local quality12/13 archives absent")
def test_complete_quality13_context_is_rebuilt_without_narrowing(tmp_path):
    module = _module()
    output = tmp_path / "raw-replay.json"

    report = module.run_replay(
        manifest_path=MANIFEST,
        artifact_root=ROOT,
        output_path=output,
    )
    raw = json.loads(output.read_text(encoding="utf-8"))

    assert report["provider_calls"] == 0
    assert report["network_used"] is False
    assert raw["local_artifact_integration"] == {
        "required_artifacts": 5,
        "verified": True,
    }
    assert raw["context_counts"] == {
        "source_blocks": 104,
        "facts": 60,
        "core_recommendations": 5,
        "readiness_flags": 4,
        "reader_objects": 5,
        "reader_support_records": len(raw["reader_review_input"]["support_records"]),
    }
    assert set(raw["conditional_review_input"]["recommendations_by_id"]) == {
        "REC-001", "REC-002", "REC-003", "REC-004", "REC-005",
    }
    assert set(raw["conditional_review_input"]["readiness_flags_by_id"]) == {
        "DIF-001", "DIF-002", "DIF-003", "DIF-004",
    }
    assert set(raw["reader_review_input"]["final_reader_by_id"]) == {
        "SUM-001", "SUM-002", "NARR-design", "NARR-dividends",
        "NARR-inclusion",
    }
    assert raw["artifact_verification"]["all_verified"] is True
    assert raw["source_reconstruction"]["document_id"] == "DOC-ce08d41a57d2a4c6"
    assert raw["source_reconstruction"]["extracted_text_sha256"] == (
        "a2cd1e4df028b094ae855f15fac9aaf50e251ef8214761fe8b0b4dfb1bf98a31"
    )
    lifecycle = raw["recorded_decision_lifecycle"]["core"]
    assert "REC-004" in lifecycle["initial_rejected_core_ids"]
    assert lifecycle["correction_recovered_core_ids"] == ["REC-004"]
    assert "REC-004" in lifecycle["final_accepted_core_ids"]
    assert lifecycle["acceptance_scored_at"] == (
        "final_admission_after_bounded_core_correction"
    )
    illustration = raw["minimal_reader_correction_illustration"]
    assert illustration["changed_object_ids"] == ["NARR-dividends"]
    assert illustration["all_other_records_byte_stable"] is True
    assert illustration["numeric_date_tokens_unchanged"] is True
    assert illustration["native_merge_issues"] == []
    assert illustration["semantic_acceptance_proven"] is False
    assert illustration["review_without_clean_pass_withheld"] is True
    assert illustration["exact_replacements"] == [
        {
            "old": "The immediate benefit is",
            "new": "The intended immediate benefit is",
        },
        {
            "old": "flood-ready border posts",
            "new": "planned flood-resilient border posts",
        },
    ]
    candidate = raw["candidate_reader_review_input"]
    assert candidate["source_passage_count"] == 34
    assert candidate["acceptance_expectations_included"] is False
    assert candidate["semantic_acceptance_proven"] is False
    assert candidate["payload"]["source_passages"]
    assert "source_passages" in candidate["rendered_current_prompt"]
    assert "Recorded quality13 decisions are scored only" in candidate["scope_note"]


@pytest.mark.skipif(not LOCAL_ARTIFACTS, reason="local quality12/13 archives absent")
def test_recorded_quality13_decisions_fail_source_backed_acceptance(tmp_path):
    module = _module()

    report = module.run_replay(
        manifest_path=MANIFEST,
        artifact_root=ROOT,
        output_path=tmp_path / "raw-replay.json",
    )

    assert report["passed"] is False
    assert report["local_artifact_integration"] == {
        "required_artifacts": 5,
        "verified": True,
    }
    failures = {
        (item["stage"], item["object_id"], item["failure"])
        for item in report["failures"]
    }
    assert failures == {
        ("core", "REC-001", "decision_mismatch"),
        ("core", "REC-005", "decision_mismatch"),
        ("readiness", "DIF-003", "decision_mismatch"),
        ("readiness", "DIF-004", "decision_mismatch"),
        ("reader", "SUM-001", "decision_mismatch"),
        ("reader", "NARR-design", "decision_mismatch"),
        ("reader", "NARR-dividends", "forbidden_reason_code"),
    }
    assert report["correction_guard"] == {
        "accepted": False,
        "reason_codes": ["READER_CORRECTION_SUMMARY_NUMBER_UNSUPPORTED"],
        "assessment": "guard_worked_as_designed",
    }
    assert "would not prove model semantic performance" in report["limits"][1]


def test_artifact_hash_verification_is_portable_and_fails_closed(tmp_path):
    module = _module()
    artifact = tmp_path / "frozen.json"
    artifact.write_text('{"frozen":true}', encoding="utf-8")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    manifest = {"artifacts": {"frozen": {
        "path": "frozen.json", "sha256": digest,
    }}}

    resolved, checks = module._verify_artifacts(manifest, tmp_path)

    assert resolved == {"frozen": artifact}
    assert checks["all_verified"] is True
    manifest["artifacts"]["frozen"]["sha256"] = "0" * 64
    with pytest.raises(module.ReplayFailure, match="frozen hash mismatch"):
        module._verify_artifacts(manifest, tmp_path)


def test_evaluator_is_portable_and_rejects_mismatch_or_incomplete_coverage():
    module = _module()
    expectations = {
        "reader": {
            "PASS": {"decision": "accept"},
            "STATUS": {
                "decision": "reject",
                "required_reason_codes": ["PROJECT_FACT_UNSUPPORTED"],
                "forbidden_reason_codes": ["RESIDUAL_GAP_UNSUPPORTED"],
            },
        }
    }
    recorded = {
        "reader": {
            "PASS": {"decision": "reject", "reason_codes": []},
            "STATUS": {
                "decision": "reject",
                "reason_codes": [
                    "PROJECT_FACT_UNSUPPORTED", "RESIDUAL_GAP_UNSUPPORTED",
                ],
            },
        }
    }

    _, failures = module._evaluate(expectations, recorded)

    assert failures == [
        {"stage": "reader", "object_id": "PASS", "failure": "decision_mismatch"},
        {
            "stage": "reader", "object_id": "STATUS",
            "failure": "forbidden_reason_code",
        },
    ]
    del recorded["reader"]["PASS"]
    with pytest.raises(module.ReplayFailure, match="complete reconstructed payload"):
        module._evaluate(expectations, recorded)
