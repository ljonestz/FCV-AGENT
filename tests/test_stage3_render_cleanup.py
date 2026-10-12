"""Regression tests for Stage 3 display cleanup (delimiter leaks)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app


def test_orphan_risk_narrative_marker_and_duplicate_are_stripped():
    # Model dropped the END marker (truncation / format drift): the orphan START and
    # the duplicated FCV Risk Exposure prose must not leak (the card renders it from JSON).
    s = (
        "## EXECUTIVE SUMMARY\n\n### Operational Context\n\nContext para about sites.\n\n"
        "%%%RISK_NARRATIVE_START%%%\n\n### FCV Risk Exposure\n\n"
        "**Risks to project:** threat x.\n\n"
        "**How project could affect fragility:** harm y.\n\n"
        "### Strengths\n\nReal strength prose."
    )
    out = app.clean_stage3_output(s)
    assert "%%%" not in out
    assert "FCV Risk Exposure" not in out
    assert "Context para about sites" in out
    assert "Real strength prose" in out


def test_paired_risk_narrative_still_stripped():
    s = (
        "Context.\n\n%%%RISK_NARRATIVE_START%%%\n### FCV Risk Exposure\nbody\n"
        "%%%RISK_NARRATIVE_END%%%\n\n### Strengths\n\nStrength prose."
    )
    out = app.clean_stage3_output(s)
    assert "%%%" not in out
    assert "FCV Risk Exposure" not in out
    assert "Strength prose" in out


def test_stray_delimiter_token_catch_all():
    s = "Normal prose.\n\n%%%SOME_ORPHAN_TOKEN%%%\n\nMore prose."
    out = app.clean_stage3_output(s)
    assert "%%%" not in out
    assert "Normal prose" in out
    assert "More prose" in out
