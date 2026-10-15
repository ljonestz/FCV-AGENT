"""Run four bounded Climate reviewer calibration cases; offline by default."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Protocol

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sector_lenses.climate_runtime_config import load_verified_climate_runtime
from sector_lenses.climate_verified_client import AnthropicVerifiedJsonClient
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_schemas import stage_output_schema


DEFAULT_FIXTURE = ROOT / "tests" / "fixtures" / "climate" / "reviewer_calibration.json"
DEFAULT_OUTPUT_DIR = ROOT / "output"
MAX_CALLS = 6
MAX_PROMPT_CHARS = 30_000
MAX_OUTPUT_TOKENS = 1_600
TIMEOUT_SECONDS = 90
MAX_SAVED_RESPONSE_CHARS = 12_000
ALLOWED_STAGES = {"reader_review", "conditional_review"}


class ReviewerClient(Protocol):
    call_metrics: list[dict[str, object]]

    def complete_json(self, **kwargs: object) -> dict[str, object]: ...


class CalibrationFailure(RuntimeError):
    """The bounded calibration contract was not met."""


def load_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise CalibrationFailure("fixture must contain a cases array")
    if not isinstance(data.get("provenance"), dict):
        raise CalibrationFailure("fixture provenance is required")
    return data


def render_case_prompt(case: dict[str, object]) -> str:
    return build_verified_stage_prompt(str(case["stage"]), case["payload"])


def _validate_fixture(fixture: dict[str, object]) -> dict[str, int]:
    cases = fixture["cases"]
    counts = Counter()
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise CalibrationFailure("every case must be an object")
        case_id = case.get("case_id")
        stage = case.get("stage")
        payload = case.get("payload")
        expected = case.get("expected")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise CalibrationFailure("case IDs must be non-empty and unique")
        seen.add(case_id)
        if stage not in ALLOWED_STAGES:
            raise CalibrationFailure(f"unsupported stage in {case_id}")
        if not isinstance(payload, dict) or not isinstance(expected, dict):
            raise CalibrationFailure(f"payload and expected are required in {case_id}")
        if "expected" in payload or not isinstance(case.get("provenance"), list):
            raise CalibrationFailure(f"labels and provenance are not separated in {case_id}")
        prompt = render_case_prompt(case)
        if case_id in prompt or json.dumps(expected, sort_keys=True) in prompt:
            raise CalibrationFailure(f"expected labels leaked into {case_id}")
        if len(prompt) > MAX_PROMPT_CHARS:
            raise CalibrationFailure(f"prompt too large before provider: {case_id}")
        schema = stage_output_schema(stage)
        if not expected.get("accepted"):
            object_ids = expected.get("object_ids")
            requirements = expected.get("reason_codes_by_object")
            allowed_codes = set(
                schema["properties"]["reason_codes"]["items"]["enum"]
            )
            if (
                not isinstance(object_ids, list)
                or not isinstance(requirements, dict)
                or set(requirements) != set(object_ids)
                or any(
                    not isinstance(codes, list)
                    or not codes
                    or not all(isinstance(code, str) for code in codes)
                    or not set(codes) <= allowed_codes
                    for codes in requirements.values()
                )
            ):
                raise CalibrationFailure(
                    f"invalid reason-code expectations in {case_id}"
                )
        counts[stage] += 1
    if len(cases) != 4 or counts != {"reader_review": 2, "conditional_review": 2}:
        raise CalibrationFailure("fixture must cover two reader and two core cases")
    return {"cases": len(cases), **dict(counts)}


def _review_shape_error(stage: str, response: object) -> str | None:
    """Check the small review result shape without adding a runtime dependency."""

    if not isinstance(response, dict):
        return "review must be an object"
    schema = stage_output_schema(stage)
    required = set(schema["required"])
    if set(response) != required:
        return "review fields do not match the native schema"
    verdicts = set(schema["properties"]["verdict"]["enum"])
    if response["verdict"] not in verdicts:
        return "invalid verdict"
    list_fields = {"reason_codes", "object_ids", "issues"}
    if stage == "conditional_review":
        list_fields.update({"passed_core_ids", "passed_readiness_ids"})
    if any(not isinstance(response[field], list) for field in list_fields):
        return "review array field is malformed"
    string_arrays = list_fields - {"issues"}
    if any(not all(isinstance(value, str) for value in response[field])
           for field in string_arrays):
        return "review ID or code is not a string"
    allowed_codes = set(
        schema["properties"]["reason_codes"]["items"]["enum"]
    )
    if not set(response["reason_codes"]) <= allowed_codes:
        return "unknown reason code"
    for issue in response["issues"]:
        if not isinstance(issue, dict) or set(issue) != {
            "object_id", "reason_codes", "explanation",
        }:
            return "issue fields do not match the native schema"
        if (
            not isinstance(issue["object_id"], str)
            or not isinstance(issue["explanation"], str)
            or not isinstance(issue["reason_codes"], list)
            or not all(isinstance(code, str) for code in issue["reason_codes"])
            or not set(issue["reason_codes"]) <= allowed_codes
        ):
            return "issue value is malformed"
    return None


def _evaluate(case: dict[str, object], response: dict[str, object]) -> tuple[bool, str]:
    stage = str(case["stage"])
    expected = case["expected"]
    shape_error = _review_shape_error(stage, response)
    if shape_error:
        return False, f"malformed review: {shape_error}"

    accepted = bool(expected["accepted"])
    expected_ids = set(expected.get("object_ids", []))
    object_ids = response.get("object_ids", [])
    issues = response.get("issues", [])
    reason_codes = response.get("reason_codes", [])
    issue_ids = [issue.get("object_id") for issue in issues]
    if (
        len(object_ids) != len(set(object_ids))
        or len(issue_ids) != len(set(issue_ids))
        or len(reason_codes) != len(set(reason_codes))
    ):
        return False, "duplicate diagnostic IDs or codes"
    issue_code_union: set[str] = set()
    for issue in issues:
        codes = issue.get("reason_codes", [])
        if (
            not codes
            or len(codes) != len(set(codes))
            or not str(issue.get("explanation") or "").strip()
        ):
            return False, "incomplete issue diagnostic"
        issue_code_union.update(codes)
    if issue_code_union != set(reason_codes):
        return False, "top-level reason code union mismatch"
    if stage == "conditional_review":
        expected_cores = expected.get("passed_core_ids", [])
        actual_cores = response.get("passed_core_ids", [])
        readiness_ids = response.get("passed_readiness_ids", [])
        if len(actual_cores) != len(set(actual_cores)):
            return False, "duplicate passed_core_ids"
        if len(readiness_ids) != len(set(readiness_ids)):
            return False, "duplicate passed_readiness_ids"
        if set(actual_cores) != set(expected_cores):
            return False, "passed_core_ids mismatch"
        if readiness_ids != []:
            return False, "unexpected readiness acceptance"

    if accepted:
        clean = (
            response.get("verdict") == "pass"
            and response.get("reason_codes") == []
            and response.get("object_ids") == []
            and response.get("issues") == []
        )
        return clean, "expected clean pass" if not clean else "matched"

    rejected = (
        response.get("verdict") in {"revise", "block"}
        and bool(reason_codes)
        and set(object_ids) == expected_ids
        and set(issue_ids) == expected_ids
        and len(object_ids) == len(expected_ids)
        and len(issues) == len(expected_ids)
    )
    if rejected:
        requirements = expected.get("reason_codes_by_object", {})
        rejected = all(
            set(issue["reason_codes"]) & set(requirements[issue["object_id"]])
            for issue in issues
        )
        if not rejected:
            return False, "per-object reason code mismatch"
    return rejected, "expected exact rejection targets" if not rejected else "matched"


def _bounded_response(response: object) -> object:
    raw = json.dumps(response, ensure_ascii=False, separators=(",", ":"))
    if len(raw) <= MAX_SAVED_RESPONSE_CHARS:
        return response
    return {"truncated": True, "characters": len(raw),
            "prefix": raw[:MAX_SAVED_RESPONSE_CHARS]}


def write_report(report: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _new_output_path(output_dir: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    return output_dir / f"{stamp}_climate-reviewer-check.json"


def _live_client() -> AnthropicVerifiedJsonClient:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise CalibrationFailure("ANTHROPIC_API_KEY is required for --live")
    import anthropic

    runtime_environment = {"CLIMATE_VERIFIED_RUN_MODE": "quality"}
    reviewer_override = os.environ.get("CLIMATE_VERIFIED_REVIEW_MODEL")
    if reviewer_override is not None:
        runtime_environment["CLIMATE_VERIFIED_REVIEW_MODEL"] = reviewer_override
    runtime = load_verified_climate_runtime(runtime_environment)
    return AnthropicVerifiedJsonClient(
        anthropic.Anthropic(api_key=api_key),
        model=runtime.reviewer_model,
    )


def run_checks(
    client: ReviewerClient | None = None,
    *,
    live: bool = False,
    fixture_path: Path = DEFAULT_FIXTURE,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, object]:
    fixture = load_fixture(fixture_path)
    cases = fixture["cases"]
    if live and len(cases) > MAX_CALLS:
        raise CalibrationFailure(f"live call cap is {MAX_CALLS}")
    coverage = _validate_fixture(fixture)
    if not live:
        return {"mode": "offline", "passed": True, "coverage": coverage,
                "prompt_chars": {case["case_id"]: len(render_case_prompt(case))
                                 for case in cases}}

    client = client or _live_client()
    results = []
    any_failure = False
    for case in cases:
        metric_start = len(getattr(client, "call_metrics", []))
        try:
            response = client.complete_json(
                stage=case["stage"],
                payload=case["payload"],
                timeout_seconds=TIMEOUT_SECONDS,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                max_transient_retries=0,
            )
            passed, detail = _evaluate(case, response)
            error = None
        except Exception as exc:
            response = None
            passed, detail = False, "provider or validation error"
            error = type(exc).__name__
        metrics = getattr(client, "call_metrics", [])[metric_start:]
        any_failure = any_failure or not passed
        results.append({
            "case_id": case["case_id"],
            "stage": case["stage"],
            "passed": passed,
            "detail": detail,
            "error": error,
            "raw_response": _bounded_response(response),
            "usage": [metric.get("usage", {}) for metric in metrics
                      if isinstance(metric, dict)],
            "call_metrics": _bounded_response(metrics),
        })

    report = {
        "schema_version": "climate-reviewer-check-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "live",
        "passed": not any_failure,
        "production_readiness_certified": False,
        "coverage": coverage,
        "results": results,
    }
    write_report(report, _new_output_path(output_dir))
    if any_failure:
        raise CalibrationFailure("one or more calibration cases failed")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true",
                        help="make four bounded reviewer calls")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    try:
        report = run_checks(live=args.live, fixture_path=args.fixture,
                            output_dir=args.output_dir)
    except CalibrationFailure as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
