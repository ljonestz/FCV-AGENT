"""Provider adapter for strict verified Climate-FCV JSON calls."""

from __future__ import annotations

from collections.abc import Callable
import json
import re
import time
from typing import Any

from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_schemas import stage_output_schema


def _never_transient(_error: Exception) -> bool:
    return False


def _bounded_provider_failure_details(
    error: Exception,
) -> dict[str, str | None]:
    """Classify provider failures without retaining unrestricted messages."""

    provider_error_type = None
    message = ""
    body = getattr(error, "body", None)
    if isinstance(body, dict):
        nested = body.get("error")
        if isinstance(nested, dict):
            raw_type = nested.get("type")
            if isinstance(raw_type, str) and re.fullmatch(
                r"[a-z0-9_]{1,64}", raw_type
            ):
                provider_error_type = raw_type
            raw_message = nested.get("message")
            if isinstance(raw_message, str):
                message = raw_message

    normalized = message.lower()
    failure_code = None
    if "schema" in normalized or "output_config.format" in normalized:
        failure_code = "schema_rejected"
    elif provider_error_type == "invalid_request_error":
        failure_code = "invalid_request"

    path_match = re.search(
        r"properties(?:[.][A-Za-z0-9_-]+)+",
        message,
    )
    return {
        "provider_error_type": provider_error_type,
        "provider_failure_code": failure_code,
        "schema_path": path_match.group(0)[:240] if path_match else None,
    }


class AnthropicVerifiedJsonClient:
    """Small Anthropic SDK adapter with pipeline-owned retry policy."""

    def __init__(
        self,
        sdk_client: Any,
        *,
        model: str,
        is_transient: Callable[[Exception], bool] | None = None,
        diagnostic_sink: Callable[[dict[str, object]], None] | None = None,
    ) -> None:
        self._sdk_client = sdk_client
        self._model = model
        self._is_transient = is_transient or _never_transient
        self._diagnostic_sink = diagnostic_sink
        self.call_metrics: list[dict[str, object]] = []
        self.last_output_tokens: int | None = None

    def _thinking_off(self) -> dict[str, str]:
        """Return the 'turn thinking off' config for this model. Sonnet 5.5
        rejects {"type": "disabled"} and requires {"type": "between_tools"};
        Haiku 5.5 uses {"type": "disabled"}. This call has no tools, so both
        suppress thinking output entirely (no pre-response thinking, no
        inter-tool updates), freeing the full output budget for the JSON."""
        model = (self._model or "").lower()
        if "sonnet" in model or "opus" in model:
            return {"type": "between_tools"}
        return {"type": "disabled"}

    def _emit_failure_diagnostic(
        self,
        *,
        stage: str,
        attempt: int,
        elapsed_ms: int,
        error: Exception,
        prompt_chars: int,
        timeout_seconds: int,
        remaining_seconds: int,
    ) -> None:
        if self._diagnostic_sink is None:
            return
        diagnostic = {
            "stage": stage,
            "attempt": attempt,
            "elapsed_ms": elapsed_ms,
            "exception_type": type(error).__name__,
            "status_code": getattr(error, "status_code", None),
            "prompt_chars": prompt_chars,
            "timeout_seconds": timeout_seconds,
            "remaining_seconds": remaining_seconds,
        }
        diagnostic.update(_bounded_provider_failure_details(error))
        try:
            self._diagnostic_sink(diagnostic)
        except Exception:
            pass

    @staticmethod
    def _retry_budget_error(stage: str, error: Exception) -> TimeoutError:
        status_code = getattr(error, "status_code", None)
        status_suffix = (
            f" status={status_code}" if status_code is not None else ""
        )
        return TimeoutError(
            f"{stage} exceeded its retry budget after "
            f"{type(error).__name__}{status_suffix}"
        )

    def complete_json(
        self,
        *,
        stage: str,
        payload: dict[str, object],
        timeout_seconds: int,
        max_output_tokens: int,
        max_transient_retries: int,
    ) -> dict[str, object]:
        prompt = build_verified_stage_prompt(stage, payload)
        self.last_output_tokens = None
        scope = payload.get('call_scope', 'reader' if stage.startswith('reader_') else 'initial')
        if scope not in {'initial', 'core_correction', 'draft_correction', 'reader', 'reader_correction'}:
            scope = 'initial'
        configured_model = self._model if re.fullmatch(r'[a-zA-Z0-9_.-]{1,100}', self._model or '') else 'configured'
        response = None
        started = time.monotonic()
        remaining = timeout_seconds
        attempt_started = started
        for attempt in range(max_transient_retries + 1):
            if remaining < 1:
                raise TimeoutError(f"{stage} exceeded its retry budget")
            configured = self._sdk_client.with_options(
                timeout=remaining,
                max_retries=0,
            )
            try:
                response = configured.messages.create(
                    model=self._model,
                    max_tokens=max_output_tokens,
                    # Deterministic JSON extraction — no reasoning needed. The
                    # CALL_BUDGETS were sized for the 4.6 models (no thinking);
                    # the 5.5 models think by default, consuming the output
                    # budget and truncating the JSON. Turn thinking off to
                    # restore the original calibration. The "off" param differs
                    # by model: Sonnet 5.5 requires {"type": "between_tools"}
                    # (it rejects "disabled"); Haiku 5.5 uses "disabled". With no
                    # tools in this call, both yield no thinking output.
                    thinking=self._thinking_off(),
                    messages=[{"role": "user", "content": prompt}],
                    output_config={
                        "format": {
                            "type": "json_schema",
                            "schema": stage_output_schema(stage),
                        }
                    },
                )
                break
            except Exception as error:
                attempt_finished = time.monotonic()
                elapsed_seconds = attempt_finished - started
                remaining = max(0, int(timeout_seconds - elapsed_seconds))
                self.call_metrics.append({
                    'stage': stage, 'scope': scope, 'configured_model': configured_model,
                    'model': None, 'attempt': attempt + 1, 'status': 'failed',
                    'usage': {}, 'usage_available': False,
                    'elapsed_ms': int((attempt_finished - attempt_started) * 1000),
                    'exception_type': type(error).__name__, 'status_code': getattr(error, 'status_code', None),
                    'max_output_tokens': max_output_tokens,
                })
                self._emit_failure_diagnostic(
                    stage=stage,
                    attempt=attempt + 1,
                    elapsed_ms=int(elapsed_seconds * 1000),
                    error=error,
                    prompt_chars=len(prompt),
                    timeout_seconds=timeout_seconds,
                    remaining_seconds=remaining,
                )
                if attempt >= max_transient_retries or not self._is_transient(error):
                    raise
                if remaining < 1:
                    raise self._retry_budget_error(stage, error) from error
                attempt_started = attempt_finished
        if response is None:
            raise RuntimeError(f"No response returned for {stage}")
        usage = getattr(response, 'usage', None)
        counts = {}
        for name in ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens'):
            value = usage.get(name) if isinstance(usage, dict) else getattr(usage, name, None)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                counts[name] = min(value, 99_999_999)
        actual_model = getattr(response, 'model', None)
        model = actual_model if isinstance(actual_model, str) and re.fullmatch(r'[a-zA-Z0-9_.-]{1,100}', actual_model) else configured_model
        self.last_output_tokens = counts.get('output_tokens')
        self.call_metrics.append({
            'stage': stage, 'scope': scope, 'configured_model': configured_model,
            'model': model, 'actual_model_available': bool(isinstance(actual_model, str) and re.fullmatch(r'[a-zA-Z0-9_.-]{1,100}', actual_model)),
            'attempt': attempt + 1, 'status': 'returned',
            'stop_reason': getattr(response, 'stop_reason', 'unknown') if getattr(response, 'stop_reason', '') in {'end_turn', 'max_tokens', 'refusal', 'stop_sequence'} else 'unknown',
            'usage': counts, 'usage_available': bool(counts),
            'elapsed_ms': int((time.monotonic() - attempt_started) * 1000),
            'timeout_seconds': timeout_seconds, 'max_output_tokens': max_output_tokens,
            'thinking': self._thinking_off()['type'],
        })
        content = getattr(response, "content", None)
        if not isinstance(content, list) or not content:
            raise ValueError(f"{stage} returned no text content")
        text = "".join(
            str(getattr(item, "text", ""))
            for item in content
            if getattr(item, "text", "")
        )
        stop_reason = getattr(response, "stop_reason", None) or "unknown"
        if stop_reason in {"max_tokens", "refusal"}:
            raise ValueError(
                f"Structured climate output incomplete "
                f"(stage={stage}; stop_reason={stop_reason}; "
                f"characters={len(text)})"
            )
        try:
            parsed = json.loads(text)
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError(
                f"Expected valid structured JSON "
                f"(stage={stage}; stop_reason={stop_reason}; "
                f"characters={len(text)})"
            ) from error
        if not isinstance(parsed, dict):
            raise ValueError(
                f"Expected a structured JSON object "
                f"(stage={stage}; stop_reason={stop_reason}; "
                f"characters={len(text)})"
            )
        return parsed
