import json
from app import (
    normalize_priority_questions,
    build_priority_questions_block,
    PRIORITY_QUESTIONS_MAX,
)


def test_normalize_trims_dedupes_and_ids():
    raw = ["  How well does it address gender?  ", "How well does it address gender?", "", "Second question"]
    out = normalize_priority_questions(raw)
    assert [q['question'] for q in out] == ["How well does it address gender?", "Second question"]
    assert [q['id'] for q in out] == ["q1", "q2"]


def test_normalize_accepts_dicts_and_caps():
    raw = [{"question": f"Q{i}"} for i in range(PRIORITY_QUESTIONS_MAX + 5)]
    out = normalize_priority_questions(raw)
    assert len(out) == PRIORITY_QUESTIONS_MAX


def test_build_block_empty_when_no_questions():
    assert build_priority_questions_block([], 2) == ''


def test_build_block_stage2_has_rating_guardrail():
    qs = [{"id": "q1", "question": "Feasible in the security context?"}]
    s1 = build_priority_questions_block(qs, 1)
    s2 = build_priority_questions_block(qs, 2)
    assert "Do NOT attempt to answer them directly" in s1
    assert "GUARDRAIL" not in s1
    assert "must NOT change your Sensitivity" in s2
