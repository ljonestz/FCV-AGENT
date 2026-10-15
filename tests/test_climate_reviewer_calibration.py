from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "climate" / "reviewer_calibration.json"
SCRIPT = ROOT / "scripts" / "20261015_climate_reviewer_check.py"


def _module():
    spec = importlib.util.spec_from_file_location("climate_reviewer_check", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.call_metrics = []

    def complete_json(self, **kwargs):
        self.calls.append(kwargs)
        response = self.responses.pop(0)
        self.call_metrics.append({
            "stage": kwargs["stage"],
            "status": "returned",
            "model": "reviewer-model",
            "usage": {"input_tokens": 10, "output_tokens": 5},
        })
        return response


def _passing_responses(cases):
    responses = []
    for case in cases:
        expected = case["expected"]
        if expected["accepted"]:
            response = {
                "verdict": "pass",
                "reason_codes": [],
                "object_ids": [],
                "issues": [],
            }
            if case["stage"] == "conditional_review":
                response["passed_core_ids"] = expected["passed_core_ids"]
                response["passed_readiness_ids"] = []
        else:
            object_ids = expected["object_ids"]
            required_codes = expected["reason_codes_by_object"]
            issues = [{
                "object_id": object_id,
                "reason_codes": [required_codes[object_id][0]],
                "explanation": "The factual premise is not supported by the cited records.",
            } for object_id in object_ids]
            response = {
                "verdict": "revise",
                "reason_codes": sorted({
                    code for issue in issues for code in issue["reason_codes"]
                }),
                "object_ids": object_ids,
                "issues": issues,
            }
            if case["stage"] == "conditional_review":
                response["passed_core_ids"] = []
                response["passed_readiness_ids"] = []
        responses.append(response)
    return responses


def test_fixture_has_four_calibration_cases_and_keeps_labels_out_of_payloads():
    module = _module()
    assert "jsonschema" not in SCRIPT.read_text(encoding="utf-8")
    fixture = module.load_fixture(FIXTURE)
    cases = fixture["cases"]

    assert [(case["stage"], case["expected"]["accepted"]) for case in cases] == [
        ("reader_review", True),
        ("reader_review", False),
        ("conditional_review", True),
        ("conditional_review", False),
    ]
    assert all(case.get("provenance") for case in cases)
    for case in cases:
        prompt = module.render_case_prompt(case)
        assert "expected" not in case["payload"]
        assert json.dumps(case["expected"], sort_keys=True) not in prompt
        assert case["case_id"] not in prompt

    positive_reader = cases[0]
    reader_records = (
        positive_reader["payload"]["final_reader"]["summary_paragraphs"]
        + positive_reader["payload"]["final_reader"]["assessment_narratives"]
    )
    assert [record["object_id"] for record in reader_records] == [
        "SUM-001", "NARR-dividends", "NARR-design",
    ]
    assert all(len(record["evidence_ids"]) <= 2 for record in reader_records)
    assert positive_reader["payload"]["support_records"]["PF-BURUNDI"][
        "epistemic_status"
    ] == "explicit"

    negative_reader = cases[1]
    assert negative_reader["expected"]["object_ids"] == [
        "SUM-001", "SUM-002", "NARR-design", "NARR-inclusion",
    ]
    assert negative_reader["expected"]["reason_codes_by_object"] == {
        "SUM-001": ["PROJECT_FACT_UNSUPPORTED"],
        "SUM-002": [
            "EXISTING_MITIGATION_MISREPRESENTED",
            "RESIDUAL_GAP_UNSUPPORTED",
        ],
        "NARR-design": ["TIMING_UNSUPPORTED"],
        "NARR-inclusion": ["PROJECT_FACT_UNSUPPORTED"],
    }
    assert "actual launch or awards" not in json.dumps(
        negative_reader["payload"]["support_records"], ensure_ascii=False
    )
    negative_core = cases[3]
    assert negative_core["expected"]["object_ids"] == [
        "REC-NO-CRITERIA", "REC-LINKAGE", "REC-MOST-EXPOSED",
    ]
    assert negative_core["expected"]["passed_core_ids"] == []
    assert negative_core["expected"]["reason_codes_by_object"] == {
        "REC-NO-CRITERIA": ["RESIDUAL_GAP_UNSUPPORTED"],
        "REC-LINKAGE": ["PROJECT_FACT_UNSUPPORTED"],
        "REC-MOST-EXPOSED": ["PROJECT_FACT_UNSUPPORTED"],
    }
    assert "no source ranks" not in json.dumps(
        negative_core["payload"]["facts"], ensure_ascii=False
    )

    positive_core = cases[2]["payload"]
    assert positive_core["operation_context"]["instrument_type"] == "IPF"
    assert positive_core["analysis"]["pathways"]
    assert positive_core["analysis"]["residual_gaps"]


def test_offline_is_default_and_never_calls_client(tmp_path):
    module = _module()
    client = FakeClient([])

    report = module.run_checks(client=client, fixture_path=FIXTURE,
                               output_dir=tmp_path)

    assert report["mode"] == "offline"
    assert report["coverage"] == {"cases": 4, "reader_review": 2,
                                  "conditional_review": 2}
    assert client.calls == []
    assert list(tmp_path.iterdir()) == []


def test_live_fake_client_uses_strict_call_budgets_and_writes_new_result(tmp_path):
    module = _module()
    cases = module.load_fixture(FIXTURE)["cases"]
    client = FakeClient(_passing_responses(cases))

    report = module.run_checks(client=client, live=True, fixture_path=FIXTURE,
                               output_dir=tmp_path)

    assert report["passed"] is True
    assert len(client.calls) == 4
    assert all(call["max_transient_retries"] == 0 for call in client.calls)
    assert all(call["max_output_tokens"] <= 1_600 for call in client.calls)
    assert all(call["timeout_seconds"] <= 90 for call in client.calls)
    assert all(len(module.build_verified_stage_prompt(call["stage"], call["payload"]))
               <= 30_000 for call in client.calls)
    outputs = list(tmp_path.glob("*_climate-reviewer-check.json"))
    assert len(outputs) == 1
    saved = json.loads(outputs[0].read_text(encoding="utf-8"))
    assert all(result["passed"] for result in saved["results"])
    assert "raw_response" in saved["results"][0]
    assert saved["results"][0]["call_metrics"][0]["model"] == "reviewer-model"
    with pytest.raises(FileExistsError):
        module.write_report(report, outputs[0])


@pytest.mark.parametrize("mutate", ["missing", "extra", "false_positive"])
def test_mismatched_or_false_positive_reviews_fail_closed(tmp_path, mutate):
    module = _module()
    cases = module.load_fixture(FIXTURE)["cases"]
    responses = _passing_responses(cases)
    if mutate == "missing":
        responses[3]["object_ids"] = []
        responses[3]["issues"] = []
    elif mutate == "extra":
        responses[2]["passed_core_ids"] = ["REC-VALID", "REC-EXTRA"]
    else:
        responses[0] = {
            "verdict": "revise",
            "reason_codes": ["PROJECT_FACT_UNSUPPORTED"],
            "object_ids": ["SUM-001"],
            "issues": [{
                "object_id": "SUM-001",
                "reason_codes": ["PROJECT_FACT_UNSUPPORTED"],
                "explanation": "Incorrect false positive.",
            }],
        }

    with pytest.raises(module.CalibrationFailure):
        module.run_checks(client=FakeClient(responses), live=True,
                          fixture_path=FIXTURE, output_dir=tmp_path)


def test_live_call_cap_is_checked_before_provider(tmp_path):
    module = _module()
    fixture = module.load_fixture(FIXTURE)
    fixture["cases"] = fixture["cases"] * 2
    oversized = tmp_path / "oversized.json"
    oversized.write_text(json.dumps(fixture), encoding="utf-8")
    client = FakeClient([])

    with pytest.raises(module.CalibrationFailure, match="call cap"):
        module.run_checks(client=client, live=True, fixture_path=oversized,
                          output_dir=tmp_path)

    assert client.calls == []


@pytest.mark.parametrize(
    "mutate",
    [
        "duplicate_object_id",
        "duplicate_issue",
        "blank_explanation",
        "empty_issue_codes",
        "wrong_code_union",
    ],
)
def test_malformed_diagnostics_never_match_expected_rejections(mutate):
    module = _module()
    cases = module.load_fixture(FIXTURE)["cases"]
    case = cases[1]
    response = _passing_responses(cases)[1]
    if mutate == "duplicate_object_id":
        response["object_ids"].append(response["object_ids"][0])
    elif mutate == "duplicate_issue":
        response["issues"].append(dict(response["issues"][0]))
    elif mutate == "blank_explanation":
        response["issues"][0]["explanation"] = "   "
    elif mutate == "empty_issue_codes":
        response["issues"][0]["reason_codes"] = []
    else:
        response["reason_codes"] = ["RESIDUAL_GAP_UNSUPPORTED"]

    passed, _ = module._evaluate(case, response)

    assert passed is False


def test_generic_wrong_reason_code_cannot_pass_all_negative_cases(tmp_path):
    module = _module()
    cases = module.load_fixture(FIXTURE)["cases"]
    responses = _passing_responses(cases)
    for index in (1, 3):
        responses[index]["reason_codes"] = ["PROJECT_FACT_UNSUPPORTED"]
        for issue in responses[index]["issues"]:
            issue["reason_codes"] = ["PROJECT_FACT_UNSUPPORTED"]

    with pytest.raises(module.CalibrationFailure):
        module.run_checks(client=FakeClient(responses), live=True,
                          fixture_path=FIXTURE, output_dir=tmp_path)
