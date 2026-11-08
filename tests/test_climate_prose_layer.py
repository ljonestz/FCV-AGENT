"""Render-only analytical prose layer for verified Climate-FCV prompts."""
import pytest

from sector_lenses import climate_prose_layer as layer
from sector_lenses.climate_verified_prompts import build_verified_stage_prompt


def _prompt(stage, monkeypatch, style=None):
    monkeypatch.delenv("CLIMATE_PROSE_STYLE", raising=False)
    if style:
        monkeypatch.setenv("CLIMATE_PROSE_STYLE", style)
    return build_verified_stage_prompt(stage, {})


@pytest.mark.parametrize("stage", sorted(layer._REPLACEMENTS))
def test_every_replacement_matches_once_and_applies(stage, monkeypatch):
    legacy = _prompt(stage, monkeypatch)
    for old, _new in layer._REPLACEMENTS[stage]:
        assert legacy.count(old) == 1, old[:60]
    styled = _prompt(stage, monkeypatch, "analytical")
    for old, new in layer._REPLACEMENTS[stage]:
        assert old not in styled and new in styled


def test_off_by_default(monkeypatch):
    assert "READER REGISTER AND WORDING" not in _prompt("reader_compiler", monkeypatch)
    assert "ordinary words" in _prompt("reader_compiler", monkeypatch)


def test_reader_layer_bans_internal_terms_and_formula_openers(monkeypatch):
    p = _prompt("reader_compiler", monkeypatch, "analytical")
    assert "READER REGISTER AND WORDING" in p
    assert "accepted priorities, accepted actions" in p
    assert 'The project already builds' in p  # named as a formula to avoid
    assert "crafted analytical judgment" in p


def test_fact_checking_contracts_unchanged(monkeypatch):
    # The reviewer and correction prompts are not touched by the layer.
    for stage in ("reader_review", "reader_correction", "conditional_review"):
        assert _prompt(stage, monkeypatch) == _prompt(stage, monkeypatch, "analytical")
    p = _prompt("reader_compiler", monkeypatch, "analytical")
    assert "Add no facts, actors, numbers, dates, authority or commitments." in p
    assert "Keep evidence IDs out of the displayed prose." in p


def test_drafting_voice(monkeypatch):
    p = _prompt("drafting_compiler", monkeypatch, "analytical")
    assert "project document's own voice" in p
    assert "Do not\nturn them into assertions that a PIU will decide" in p
