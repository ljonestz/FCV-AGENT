"""Prepare or run two reasoning-enabled Climate reviewer calls; offline by default."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_schemas import stage_output_schema


MODEL = "claude-sonnet-5-5"
MAX_TOKENS = 8192
TIMEOUT_SECONDS = 180
STAGES = ("conditional_review", "reader_review")


class HarnessFailure(RuntimeError):
    """The bounded comparison contract was not met."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def load_cases(path: Path, expected_sha256: str) -> list[dict[str, object]]:
    raw = path.read_bytes()
    actual = _sha256(raw)
    if actual != expected_sha256.lower():
        raise HarnessFailure(f"case sha256 mismatch: {actual}")
    try:
        cases = json.loads(raw)
    except json.JSONDecodeError as error:
        raise HarnessFailure("cases are not valid JSON") from error
    if not isinstance(cases, list) or len(cases) != 2:
        raise HarnessFailure("cases must contain exactly two calls")
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"stage", "payload"}:
            raise HarnessFailure("case envelope must be exactly {stage,payload}")
        if not isinstance(case["payload"], dict):
            raise HarnessFailure("case payload must be an object")
    if tuple(case["stage"] for case in cases) != STAGES:
        raise HarnessFailure("case order must be conditional_review then reader_review")
    return cases


def build_requests(cases: list[dict[str, object]]) -> list[dict[str, object]]:
    requests = []
    for case in cases:
        stage = str(case["stage"])
        prompt = build_verified_stage_prompt(stage, case["payload"])
        schema = stage_output_schema(stage)
        provider_request = {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "thinking": {"type": "adaptive", "display": "omitted"},
            "messages": [{"role": "user", "content": prompt}],
            "output_config": {
                "effort": "high",
                "format": {"type": "json_schema", "schema": schema},
            },
        }
        requests.append({
            "stage": stage,
            "prompt": prompt,
            "schema": schema,
            "provider_request": provider_request,
        })
    if tuple(request["stage"] for request in requests) != STAGES:
        raise HarnessFailure("request order or count changed")
    return requests


def start_lock_path(output_dir: Path) -> Path:
    return output_dir.parent / f".{output_dir.name}.start.lock"


def _request_fingerprint(request: dict[str, object]) -> dict[str, str]:
    return {
        "stage": str(request["stage"]),
        "prompt_sha256": _sha256(str(request["prompt"]).encode("utf-8")),
        "schema_sha256": _sha256(json.dumps(
            request["schema"], sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")),
    }


def _request_manifest(
    requests: list[dict[str, object]], case_sha256: str,
) -> dict[str, object]:
    return {
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "case_sha256": case_sha256,
        "model": MODEL,
        "max_calls": 2,
        "max_tokens": MAX_TOKENS,
        "timeout_seconds": TIMEOUT_SECONDS,
        "max_retries": 0,
        "thinking": {"type": "adaptive", "display": "omitted"},
        "effort": "high",
        "requests": [_request_fingerprint(request) for request in requests],
    }


def _verify_expected_manifest(path: Path, current: dict[str, object]) -> None:
    try:
        expected = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as error:
        raise HarnessFailure("expected manifest is unreadable") from error
    keys = {
        "case_sha256", "model", "max_calls", "max_tokens", "timeout_seconds",
        "max_retries", "thinking", "effort", "requests",
    }
    if not isinstance(expected, dict) or not isinstance(
        expected.get("prepared_at_utc"), str,
    ) or set(expected) != keys | {"prepared_at_utc"}:
        raise HarnessFailure("expected manifest has an invalid envelope")
    if {key: expected[key] for key in keys} != {key: current[key] for key in keys}:
        raise HarnessFailure("rendered request does not match expected manifest")


def _reserve_output(output_dir: Path) -> None:
    lock = start_lock_path(output_dir)
    if output_dir.exists() or lock.exists():
        raise HarnessFailure("output directory or start lock already exists")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("x", encoding="utf-8") as handle:
        handle.write("reserved\n")
    output_dir.mkdir(parents=False, exist_ok=False)


def _value(item: object, name: str, default: object = None) -> object:
    return item.get(name, default) if isinstance(item, dict) else getattr(item, name, default)


def _usage(response: object) -> dict[str, int]:
    usage = _value(response, "usage")
    counts = {}
    for name in ("input_tokens", "output_tokens", "cache_read_input_tokens",
                 "cache_creation_input_tokens"):
        value = _value(usage, name)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            counts[name] = value
    return counts


def _content(response: object) -> tuple[list[str], str]:
    content = _value(response, "content", [])
    if not isinstance(content, list):
        return [], ""
    types = [str(_value(block, "type", "unknown")) for block in content]
    text = "".join(
        str(_value(block, "text", "")) for block in content
        if _value(block, "type") == "text" and _value(block, "text", "")
    )
    return types, text


def _response_path(output_dir: Path, index: int, stage: str) -> Path:
    return output_dir / f"response-{index:02d}-{stage}.json"


def run_paid_requests(
    requests: list[dict[str, object]], output_dir: Path, sdk_client: Any,
) -> list[dict[str, object]]:
    if len(requests) != 2:
        raise HarnessFailure("paid run requires exactly two requests")
    results = []
    for index, request in enumerate(requests, 1):
        stage = str(request["stage"])
        fingerprint = _request_fingerprint(request)
        started = time.monotonic()
        try:
            configured = sdk_client.with_options(timeout=TIMEOUT_SECONDS, max_retries=0)
            response = configured.messages.create(**request["provider_request"])
        except Exception as error:
            artifact = {
                "stage": stage,
                "request_fingerprint": fingerprint,
                "status": "failed",
                "error_type": type(error).__name__,
                "content_block_types": [],
                "metrics": {"usage": {}, "elapsed_ms": int((time.monotonic() - started) * 1000)},
            }
            _write_new(_response_path(output_dir, index, stage), artifact)
            raise HarnessFailure(f"{stage} provider call failed") from error

        types, text = _content(response)
        stop_reason = str(_value(response, "stop_reason", "unknown"))
        metrics = {
            "usage": _usage(response),
            "model": str(_value(response, "model", "unknown")),
            "stop_reason": stop_reason,
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "max_tokens": MAX_TOKENS,
            "timeout_seconds": TIMEOUT_SECONDS,
            "max_retries": 0,
            "thinking": "adaptive",
            "effort": "high",
        }
        artifact: dict[str, object] = {
            "stage": stage,
            "request_fingerprint": fingerprint,
            "status": "returned",
            "content_block_types": types,
            "metrics": metrics,
        }
        failure = None
        if stop_reason != "end_turn" or "refusal" in types:
            failure = f"incomplete structured output: {stop_reason}"
        else:
            try:
                parsed = json.loads(text)
                if not isinstance(parsed, dict):
                    raise ValueError("response is not an object")
                artifact["response"] = parsed
            except (json.JSONDecodeError, ValueError):
                failure = "invalid structured JSON"
        if failure:
            artifact["status"] = "failed"
            artifact["error"] = failure
        _write_new(_response_path(output_dir, index, stage), artifact)
        if failure:
            raise HarnessFailure(f"{stage}: {failure}")
        results.append(artifact)
    return results


def run_comparison(
    cases_path: Path,
    expected_sha256: str,
    output_dir: Path,
    *,
    run_paid: bool = False,
    sdk_client: Any | None = None,
    expected_manifest_path: Path | None = None,
) -> dict[str, object]:
    cases = load_cases(cases_path, expected_sha256)
    requests = build_requests(cases)
    manifest = _request_manifest(requests, expected_sha256.lower())
    if run_paid:
        if expected_manifest_path is None:
            raise HarnessFailure("paid mode requires --expected-manifest")
        _verify_expected_manifest(expected_manifest_path, manifest)
    _reserve_output(output_dir)
    _write_new(output_dir / "requests.json", requests)
    _write_new(output_dir / "manifest.json", manifest)
    if not run_paid:
        return {"mode": "offline", "manifest": manifest}
    if sdk_client is None:
        import anthropic
        sdk_client = anthropic.Anthropic(max_retries=0)
    results = run_paid_requests(requests, output_dir, sdk_client)
    return {"mode": "paid", "manifest": manifest, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-manifest", type=Path)
    parser.add_argument("--run-paid", action="store_true")
    args = parser.parse_args()
    try:
        result = run_comparison(
            args.cases, args.expected_sha256, args.output_dir,
            run_paid=args.run_paid,
            expected_manifest_path=args.expected_manifest,
        )
    except (HarnessFailure, FileExistsError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps({"mode": result["mode"], "output_dir": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
