"""Reader-integrity placeholder scrub (regression for the paid-run hard-fail).

A quality-model run failed at Stage 2 with ``READER_INTEGRITY:
UNRESOLVED_PLACEHOLDER`` because the full model emitted a stray bracketed
placeholder (e.g. ``[insert region]``). One cosmetic cue must not nuke an
entire paid run: ``build_reader_model`` now deterministically scrubs such cues
before the integrity gate, while ``validate_reader_model`` keeps its detector
as a backstop (covered by test_climate_verified_render).
"""

from __future__ import annotations

from sector_lenses.climate_verified_render import (
    build_reader_model,
    validate_reader_model,
)
from tests.test_climate_verified_render import _assessment


def test_build_reader_model_scrubs_bracket_placeholder_so_run_survives():
    assessment = _assessment()
    base = (
        "The project shows a material Climate-FCV pathway and documented "
        "responses remain at an early operational stage. "
    )
    assessment["executive_readout"] = (
        base * 30
        + "Focus delivery in [insert priority regions] before appraisal."
    )
    assessment["priorities"][0]["minimum_action"] = (
        "Complete the proportionate minimum action [TBD] before the decision."
    )

    model = build_reader_model(assessment)

    # No placeholder cue survives anywhere in the reader-facing model...
    assert "[insert priority regions]" not in model["executive_readout"]
    assert "[TBD]" not in model["priorities"][0]["minimum_action"]
    # ...and the integrity gate no longer hard-fails the (paid) run.
    assert "UNRESOLVED_PLACEHOLDER" not in validate_reader_model(model)
    # Surrounding prose is preserved (not blanked).
    assert "material Climate-FCV pathway" in model["executive_readout"]
    assert model["priorities"][0]["minimum_action"].startswith(
        "Complete the proportionate minimum action"
    )
    assert model["priorities"][0]["minimum_action"].endswith(".")


def test_bare_tbd_and_todo_tokens_are_scrubbed():
    assessment = _assessment()
    assessment["priorities"][0]["caution"] = (
        "Avoid unintended exclusion; TODO refine later."
    )
    assessment["priorities"][1]["limitation"] = "tbd pending confirmation of scope."

    model = build_reader_model(assessment)

    assert "TODO" not in model["priorities"][0]["caution"]
    assert "tbd" not in model["priorities"][1]["limitation"].lower()
    assert "UNRESOLVED_PLACEHOLDER" not in validate_reader_model(model)


def test_scrub_is_noop_on_a_clean_assessment():
    model = build_reader_model(_assessment())

    # A clean assessment is unchanged and still passes the full integrity gate.
    assert validate_reader_model(model) == ()
    assert "material Climate-FCV pathway" in model["executive_readout"]
