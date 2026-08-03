"""Provider adapter for strict verified Climate-FCV JSON calls."""

from __future__ import annotations

from collections.abc import Callable
import json
import time
from typing import Any

from sector_lenses.climate_verified_prompts import build_verified_stage_prompt
from sector_lenses.climate_verified_schemas import stage_output_schema


def _never_transient(_error: Exception) -> bool:
    return False


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
        response = None
        started = time.monotonic()
        remaining = timeout_seconds
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
                    temperature=0,
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
                elapsed_seconds = time.monotonic() - started
                remaining = max(0, int(timeout_seconds - elapsed_seconds))
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
        if response is None:
            raise RuntimeError(f"No response returned for {stage}")
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
