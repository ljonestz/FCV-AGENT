from pathlib import Path

import app


ROOT = Path(__file__).resolve().parents[1]


def test_stage3_prompt_requires_concise_readout_in_same_json():
    prompt = app.DEFAULT_PROMPTS["3"]
    assert '"concise_readout"' in prompt
    assert '"concise"' in prompt
    assert "same findings, ratings, priority order, and actions" in prompt
    assert "700-1,000 words" in prompt


def test_concise_stage3_is_scoped_to_core_route():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "supports_concise_stage3" in source
    assert "not lens_context['active_lenses']" in source
    assert "not lens_context_s3['active_lenses']" in source


def test_concise_lifecycle_context_for_standard_pcn():
    text = app.build_concise_lifecycle_context(
        "PCN", {"processing_track": "standard"}
    )
    assert "Commit in the PCN" in text
    assert "Develop during preparation" in text


def test_concise_lifecycle_context_for_consolidated_pcn():
    text = app.build_concise_lifecycle_context(
        "PCN", {"processing_track": "consolidated_condensed"}
    )
    assert "Resolve by Decision Review" in text
    assert "Complete in parallel" in text


def test_concise_lifecycle_context_for_pad_does_not_defer():
    text = app.build_concise_lifecycle_context(
        "PAD", {"processing_track": "standard"}
    )
    assert "Resolve before the review gate" in text
    assert "Do not defer" in text


def test_concise_lifecycle_context_unknown_is_conservative():
    text = app.build_concise_lifecycle_context("PCN", {})
    assert "When to address" in text
    assert "do not assert an unverified procedural gate" in text
