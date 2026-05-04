"""Regression tests for keeping Stage 3 payloads bounded."""

from app import (
    DEFAULT_PRIOR_ASSISTANT_CHARS,
    STAGE3_PRIOR_ASSISTANT_CHARS,
    collect_prior_assistant_outputs,
    compact_history_for_stage,
)


def test_stage3_prior_outputs_use_smaller_limit():
    history = [
        {"role": "user", "content": "[Stage 1 label]"},
        {"role": "assistant", "content": "A" * (STAGE3_PRIOR_ASSISTANT_CHARS + 5000)},
        {"role": "user", "content": "[Stage 2 label]"},
        {"role": "assistant", "content": "B" * (STAGE3_PRIOR_ASSISTANT_CHARS + 5000)},
    ]

    outputs = collect_prior_assistant_outputs(history, stage=3)

    assert len(outputs) == 2
    assert len(outputs[0]) < STAGE3_PRIOR_ASSISTANT_CHARS + 100
    assert outputs[0].endswith("...[truncated for Stage 3 context]")
    assert outputs[1].endswith("...[truncated for Stage 3 context]")


def test_non_stage3_prior_outputs_keep_default_limit():
    history = [
        {"role": "assistant", "content": "A" * (STAGE3_PRIOR_ASSISTANT_CHARS + 5000)}
    ]

    outputs = collect_prior_assistant_outputs(history, stage=2)

    assert len(outputs[0]) == STAGE3_PRIOR_ASSISTANT_CHARS + 5000
    assert len(outputs[0]) < DEFAULT_PRIOR_ASSISTANT_CHARS


def test_compact_history_for_stage3_preserves_user_turns_and_trims_assistants():
    history = [
        {"role": "user", "content": "[Stage 1 label]"},
        {"role": "assistant", "content": "A" * (STAGE3_PRIOR_ASSISTANT_CHARS + 5000)},
        {"role": "user", "content": "[Stage 2 label]"},
        {"role": "assistant", "content": "B" * (STAGE3_PRIOR_ASSISTANT_CHARS + 5000)},
    ]

    compacted = compact_history_for_stage(history, stage=3)

    assert compacted[0]["content"] == "[Stage 1 label]"
    assert compacted[2]["content"] == "[Stage 2 label]"
    assert compacted[1]["content"].endswith("...[truncated for Stage 3 context]")
    assert compacted[3]["content"].endswith("...[truncated for Stage 3 context]")
