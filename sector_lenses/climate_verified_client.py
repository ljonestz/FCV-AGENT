"""Provider adapter for strict verified Climate-FCV JSON calls."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sector_lenses.climate_truth_prompts import parse_climate_json
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt


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
    ) -> None:
        self._sdk_client = sdk_client
        self._model = model
        self._is_transient = is_transient or _never_transient

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
        configured = self._sdk_client.with_options(
            timeout=timeout_seconds,
            max_retries=0,
        )
        response = None
        for attempt in range(max_transient_retries + 1):
            try:
                response = configured.messages.create(
                    model=self._model,
                    max_tokens=max_output_tokens,
                    temperature=0,
                    messages=[{"role": "user", "content": prompt}],
                )
                break
            except Exception as error:
                if attempt >= max_transient_retries or not self._is_transient(error):
                    raise
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
        return parse_climate_json(text)
