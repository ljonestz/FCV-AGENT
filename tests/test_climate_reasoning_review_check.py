from __future__ import annotations

import builtins
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_schemas import stage_output_schema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "20261015_climate_reasoning_review_check.py"


def _module():
    spec = importlib.util.spec_from_file_location("climate_reasoning_check", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _cases_file(tmp_path: Path) -> tuple[Path, str]:
    path = tmp_path / "cases.json"
    path.write_text(json.dumps([
        {"stage": "conditional_review", "payload": {}},
        {"stage": "reader_review", "payload": {}},
    ]), encoding="utf-8")
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def _response(stage: str, *, stop_reason: str = "end_turn"):
    body = {"stage": stage, "accepted": True}
    return SimpleNamespace(
        content=[
            SimpleNamespace(type="thinking", thinking="SECRET_THOUGHT", signature="SECRET_SIG"),
            SimpleNamespace(type="text", text=json.dumps(body)),
        ],
        usage=SimpleNamespace(input_tokens=101, output_tokens=17),
        model="claude-sonnet-5-5",
        stop_reason=stop_reason,
    )


def _prepare_manifest(module, path: Path, digest: str, tmp_path: Path) -> Path:
    prepared = tmp_path / "prepared"
    module.run_comparison(path, digest, prepared)
    return prepared / "manifest.json"


class FakeSdk:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.options = []
        self.messages = self

    def with_options(self, **kwargs):
        self.options.append(kwargs)
        return self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


def test_load_and_build_use_exact_current_prompts_schemas_and_reasoning_config(tmp_path):
    module = _module()
    path, digest = _cases_file(tmp_path)

    cases = module.load_cases(path, digest)
    requests = module.build_requests(cases)

    assert [case["stage"] for case in cases] == ["conditional_review", "reader_review"]
    for case, request in zip(cases, requests, strict=True):
        assert request["prompt"] == build_verified_stage_prompt(case["stage"], case["payload"])
        assert request["schema"] == stage_output_schema(case["stage"])
        provider = request["provider_request"]
        assert provider["model"] == "claude-sonnet-5-5"
        assert provider["max_tokens"] == 8192
        assert provider["thinking"] == {"type": "adaptive", "display": "omitted"}
        assert provider["output_config"] == {
            "effort": "high",
            "format": {"type": "json_schema", "schema": request["schema"]},
        }
        assert provider["messages"] == [{"role": "user", "content": request["prompt"]}]


def test_hash_mismatch_fails_before_output_or_calls(tmp_path):
    module = _module()
    path, _ = _cases_file(tmp_path)
    client = FakeSdk([])
    output = tmp_path / "run"
    manifest = _prepare_manifest(module, path, hashlib.sha256(path.read_bytes()).hexdigest(), tmp_path)

    with pytest.raises(module.HarnessFailure, match="sha256"):
        module.run_comparison(
            path, "0" * 64, output, run_paid=True, sdk_client=client,
            expected_manifest_path=manifest,
        )

    assert client.calls == []
    assert not output.exists()


def test_offline_default_writes_requests_and_manifest_without_importing_anthropic(tmp_path, monkeypatch):
    module = _module()
    path, digest = _cases_file(tmp_path)
    output = tmp_path / "offline"
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "anthropic":
            raise AssertionError("offline mode imported Anthropic")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    result = module.run_comparison(path, digest, output)

    assert result["mode"] == "offline"
    assert (output / "requests.json").is_file()
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["case_sha256"] == digest
    assert manifest["prepared_at_utc"].startswith("20")
    assert len(manifest["requests"]) == 2
    saved_requests = json.loads((output / "requests.json").read_text(encoding="utf-8"))
    for fingerprint, request in zip(manifest["requests"], saved_requests, strict=True):
        assert fingerprint["prompt_sha256"] == hashlib.sha256(
            request["prompt"].encode("utf-8")
        ).hexdigest()
        assert fingerprint["schema_sha256"] == hashlib.sha256(json.dumps(
            request["schema"], sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")).hexdigest()
    assert not list(output.glob("response-*.json"))


def test_existing_output_or_start_lock_prevents_any_paid_call(tmp_path):
    module = _module()
    path, digest = _cases_file(tmp_path)
    output = tmp_path / "run"
    module.run_comparison(path, digest, output)
    manifest = output / "manifest.json"
    client = FakeSdk([])

    with pytest.raises((module.HarnessFailure, FileExistsError)):
        module.run_comparison(
            path, digest, output, run_paid=True, sdk_client=client,
            expected_manifest_path=manifest,
        )
    assert client.calls == []

    other = tmp_path / "locked"
    module.start_lock_path(other).write_text("reserved", encoding="utf-8")
    with pytest.raises((module.HarnessFailure, FileExistsError)):
        module.run_comparison(
            path, digest, other, run_paid=True, sdk_client=client,
            expected_manifest_path=manifest,
        )
    assert client.calls == []


def test_paid_mode_requires_matching_frozen_manifest_before_output_or_calls(tmp_path):
    module = _module()
    path, digest = _cases_file(tmp_path)
    output = tmp_path / "paid"
    client = FakeSdk([])

    with pytest.raises(module.HarnessFailure, match="expected-manifest"):
        module.run_comparison(path, digest, output, run_paid=True, sdk_client=client)
    assert not output.exists() and client.calls == []

    manifest_path = _prepare_manifest(module, path, digest, tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["requests"][0]["prompt_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(module.HarnessFailure, match="does not match"):
        module.run_comparison(
            path, digest, output, run_paid=True, sdk_client=client,
            expected_manifest_path=manifest_path,
        )
    assert not output.exists() and client.calls == []


def test_paid_run_makes_exactly_two_no_retry_calls_and_hides_thinking(tmp_path):
    module = _module()
    path, digest = _cases_file(tmp_path)
    output = tmp_path / "paid"
    client = FakeSdk([_response("conditional_review"), _response("reader_review")])
    manifest = _prepare_manifest(module, path, digest, tmp_path)

    result = module.run_comparison(
        path, digest, output, run_paid=True, sdk_client=client,
        expected_manifest_path=manifest,
    )

    assert result["mode"] == "paid"
    assert len(client.calls) == 2
    assert client.options == [
        {"timeout": 180, "max_retries": 0},
        {"timeout": 180, "max_retries": 0},
    ]
    saved = "\n".join(item.read_text(encoding="utf-8") for item in output.glob("*.json"))
    assert "SECRET_THOUGHT" not in saved and "SECRET_SIG" not in saved
    response = json.loads((output / "response-01-conditional_review.json").read_text(encoding="utf-8"))
    assert response["content_block_types"] == ["thinking", "text"]
    assert response["metrics"]["usage"] == {"input_tokens": 101, "output_tokens": 17}
    assert response["request_fingerprint"] == result["manifest"]["requests"][0]


@pytest.mark.parametrize(
    "first",
    [
        RuntimeError("provider failed"),
        _response("conditional_review", stop_reason="max_tokens"),
        _response("conditional_review", stop_reason="pause_turn"),
        SimpleNamespace(
            content=[SimpleNamespace(type="text", text="not-json")],
            usage=SimpleNamespace(input_tokens=3, output_tokens=2),
            model="claude-sonnet-5-5",
            stop_reason="end_turn",
        ),
    ],
    ids=["provider-error", "truncation", "unexpected-stop", "invalid-json"],
)
def test_first_call_failure_is_persisted_and_never_retried_or_followed_up(tmp_path, first):
    module = _module()
    path, digest = _cases_file(tmp_path)
    output = tmp_path / "failed"
    client = FakeSdk([first, _response("reader_review")])
    manifest = _prepare_manifest(module, path, digest, tmp_path)

    with pytest.raises(module.HarnessFailure):
        module.run_comparison(
            path, digest, output, run_paid=True, sdk_client=client,
            expected_manifest_path=manifest,
        )

    assert len(client.calls) == 1
    assert len(client.options) == 1
    failure = json.loads((output / "response-01-conditional_review.json").read_text(encoding="utf-8"))
    assert failure["status"] == "failed"
    if first is not None and not isinstance(first, Exception):
        assert failure["metrics"]["usage"]["output_tokens"] == first.usage.output_tokens


def test_case_envelope_and_order_are_exact(tmp_path):
    module = _module()
    path, _ = _cases_file(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data[0]["expected"] = {"accepted": True}
    path.write_text(json.dumps(data), encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(module.HarnessFailure, match="envelope"):
        module.load_cases(path, digest)

    data[0].pop("expected")
    data.reverse()
    path.write_text(json.dumps(data), encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(module.HarnessFailure, match="order"):
        module.load_cases(path, digest)
