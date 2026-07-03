"""Tests for Workstream 4 — FCV classification prompt tightening (QA Issue 3)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_stage1_prompt_requires_geographic_footprint_anchoring():
    from app import DEFAULT_PROMPTS

    stage1 = DEFAULT_PROMPTS["1"]
    assert "project's specific geographic/administrative footprint" in stage1
    assert "before being cited" in stage1


def test_stage1_prompt_requires_general_category_trigger_line():
    from app import DEFAULT_PROMPTS

    stage1 = DEFAULT_PROMPTS["1"]
    assert "trigger: [One-line statement" in stage1


def test_classification_block_schema_includes_trigger_field():
    from app import DEFAULT_PROMPTS

    stage1 = DEFAULT_PROMPTS["1"]
    assert "%%%COUNTRY_CLASSIFICATION_START%%%" in stage1
    block_start = stage1.index("%%%COUNTRY_CLASSIFICATION_START%%%")
    block_end = stage1.index("%%%COUNTRY_CLASSIFICATION_END%%%")
    block = stage1[block_start:block_end]
    assert "trigger:" in block


def test_extract_country_classification_parses_trigger():
    from app import extract_country_classification

    text = (
        "%%%COUNTRY_CLASSIFICATION_START%%%\n"
        "category: General\n"
        "confidence: moderate\n"
        "reasoning: Project operates in stable regions.\n"
        "trigger: Country is on the FY26 FCS list due to institutional fragility.\n"
        "%%%COUNTRY_CLASSIFICATION_END%%%\n"
    )
    result = extract_country_classification(text)
    assert result["trigger"] == "Country is on the FY26 FCS list due to institutional fragility."
