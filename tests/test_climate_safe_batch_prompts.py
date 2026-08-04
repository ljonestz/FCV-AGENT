from __future__ import annotations

from sector_lenses.climate_verified_prompts import build_verified_stage_prompt


def test_recommendation_prompt_requires_site_instantiation_and_ttl_framing():
    prompt = build_verified_stage_prompt("recommendation_compiler", {})
    lowered = prompt.lower()
    # Name specific sites/entities from the fact registry, not generic placeholders.
    assert "name the specific" in lowered and "location" in lowered
    # Milestone by name, not date (digits stay banned).
    assert "milestone" in lowered and "by name" in lowered
    # Review-risk framing.
    assert "review" in lowered and ("would raise" in lowered or "flag at" in lowered)
    # Sensitivity vs responsiveness framing per recommendation.
    assert "sensitivity" in lowered and "responsiveness" in lowered
