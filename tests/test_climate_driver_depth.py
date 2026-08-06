"""Driver-depth lens: triggered political-economy questions, climate-linked."""
from __future__ import annotations

import climate_question_bank as qb
from sector_lenses.climate_verified_pipeline import (
    _CORE_QUESTION_CAP,
    _core_questions_to_answer,
)


def test_every_driver_question_is_climate_linked_and_a_design_question():
    assert qb.CLIMATE_DRIVER_QUESTIONS, "expected a driver sub-bank"
    valid_sources = {e["title"] for e in qb.CLIMATE_LITERATURE_REFERENCES}
    for q in qb.CLIMATE_DRIVER_QUESTIONS:
        # Explicitly tied to the climate/environmental dimension (not generic FCV).
        assert "climate" in q["question"].lower(), q["id"]
        # Worded as a design question, never a prediction.
        assert q["question"].strip().endswith("?"), q["id"]
        # Sourced from the reader's existing literature.
        assert q["source"] in valid_sources, q["id"]
        assert q["id"].startswith("dq-") and q["triggers"]


def test_select_triggered_drivers_fires_on_relevant_signals():
    fired = qb.select_triggered_drivers([
        "Fisheries value chain with cold chain and processing",
        "Community wildlife conservancy co-management committee",
        "Land tenure verification and boundary delineation",
    ])
    ids = {q["id"] for q in fired}
    assert "dq-value-chain" in ids
    assert "dq-representation" in ids
    assert "dq-tenure-displacement" in ids
    assert "dq-rents-capture" in ids  # 'fisheries' fires the rents driver
    assert all({"id", "theme", "question", "source"} <= set(q) for q in fired)


def test_select_triggered_drivers_empty_on_unrelated_signals():
    fired = qb.select_triggered_drivers(["digital literacy classroom laptop tablet"])
    assert fired == []


def test_core_questions_to_answer_includes_triggered_drivers():
    facts = [
        {"subject": "Fisheries value chain", "predicate": "includes", "object": "cold chain and traders"},
        {"subject": "Community conservancy", "predicate": "establishes", "object": "co-management committee"},
    ]
    posed = _core_questions_to_answer(facts)
    ids = {q["id"] for q in posed}
    assert "dq-value-chain" in ids
    assert "dq-representation" in ids
    # Deduped and each carries the fields the judgment stage needs.
    assert len(ids) == len(posed)
    assert all({"id", "theme", "question", "source"} <= set(q) for q in posed)


def test_core_question_cap_raised_to_seven():
    assert _CORE_QUESTION_CAP == 7
