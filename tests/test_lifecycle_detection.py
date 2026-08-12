"""Tests for Workstream 5 — lifecycle detection (QA Issue 5)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_stage1_prompt_asks_for_lifecycle_status_field():
    from app import DEFAULT_PROMPTS

    stage1 = DEFAULT_PROMPTS["1"]
    block_start = stage1.index("%%%TEMPORAL_CONTEXT_START%%%")
    block_end = stage1.index("%%%TEMPORAL_CONTEXT_END%%%")
    block = stage1[block_start:block_end]
    assert "lifecycle_status:" in block
    assert "closed" in block.lower() or "completion" in block.lower()


def test_stage1_prompt_asks_for_evidence_gated_processing_track():
    from app import DEFAULT_PROMPTS

    stage1 = DEFAULT_PROMPTS["1"]
    block_start = stage1.index("%%%TEMPORAL_CONTEXT_START%%%")
    block_end = stage1.index("%%%TEMPORAL_CONTEXT_END%%%")
    block = stage1[block_start:block_end]
    assert "processing_track:" in block
    assert "standard" in block
    assert "consolidated_condensed" in block
    assert "Unknown" in block
    assert "Do not infer" in block


def test_extract_temporal_context_parses_lifecycle_status():
    from app import extract_temporal_context

    text = (
        "%%%TEMPORAL_CONTEXT_START%%%\n"
        "approval_date: 2015-03\n"
        "closing_date: 2021-06\n"
        "safeguards_framework: OP-BP\n"
        "other_temporal_markers: None identified\n"
        "lifecycle_status: closed - ICR language detected\n"
        "%%%TEMPORAL_CONTEXT_END%%%\n"
    )
    ctx = extract_temporal_context(text)
    assert ctx["lifecycle_status"] == "closed - ICR language detected"


def test_extract_temporal_context_parses_consolidated_condensed_processing_track():
    from app import extract_temporal_context

    text = (
        "%%%TEMPORAL_CONTEXT_START%%%\n"
        "approval_date: 2024-01\n"
        "closing_date: 2029-01\n"
        "safeguards_framework: ESF\n"
        "other_temporal_markers: None identified\n"
        "processing_track: consolidated_condensed\n"
        "%%%TEMPORAL_CONTEXT_END%%%\n"
    )
    ctx = extract_temporal_context(text)
    assert ctx["processing_track"] == "consolidated_condensed"


def test_extract_temporal_context_rejects_unsupported_processing_track():
    from app import extract_temporal_context

    text = (
        "%%%TEMPORAL_CONTEXT_START%%%\n"
        "processing_track: accelerated_v2\n"
        "%%%TEMPORAL_CONTEXT_END%%%\n"
    )
    ctx = extract_temporal_context(text)
    assert ctx["processing_track"] == "Unknown"


def test_extract_temporal_context_requires_exact_processing_track_field():
    from app import extract_temporal_context

    text = (
        "%%%TEMPORAL_CONTEXT_START%%%\n"
        "proposed_processing_track: standard\n"
        "%%%TEMPORAL_CONTEXT_END%%%\n"
    )
    ctx = extract_temporal_context(text)
    assert ctx["processing_track"] == "Unknown"


def test_extract_temporal_context_defaults_legacy_processing_track_to_unknown():
    from app import extract_temporal_context

    text = (
        "%%%TEMPORAL_CONTEXT_START%%%\n"
        "approval_date: 2024-01\n"
        "closing_date: 2029-01\n"
        "safeguards_framework: ESF\n"
        "other_temporal_markers: None identified\n"
        "%%%TEMPORAL_CONTEXT_END%%%\n"
    )
    ctx = extract_temporal_context(text)
    assert ctx["processing_track"] == "Unknown"


def test_extract_temporal_context_missing_block_defaults_processing_track_to_unknown():
    from app import extract_temporal_context

    ctx = extract_temporal_context("no delimiter block here")
    assert ctx["processing_track"] == "Unknown"


def test_extract_temporal_context_defaults_lifecycle_status_when_absent():
    from app import extract_temporal_context

    # Old-format block (pre-Workstream-5) with no lifecycle_status line at all.
    text = (
        "%%%TEMPORAL_CONTEXT_START%%%\n"
        "approval_date: 2024-01\n"
        "closing_date: 2029-01\n"
        "safeguards_framework: ESF\n"
        "other_temporal_markers: None identified\n"
        "%%%TEMPORAL_CONTEXT_END%%%\n"
    )
    ctx = extract_temporal_context(text)
    assert ctx["lifecycle_status"] == "active"


def test_extract_temporal_context_missing_block_defaults_lifecycle_status_unknown():
    from app import extract_temporal_context

    ctx = extract_temporal_context("no delimiter block here")
    assert ctx["lifecycle_status"] == "Unknown"
    assert ctx["error"] is True
