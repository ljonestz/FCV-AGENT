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


from app import extract_focus_questions


def test_extract_focus_questions_happy_path():
    text = (
        "preamble %%%FOCUS_QUESTIONS_START%%%"
        + json.dumps({"responses": [
            {"id": "q1", "question": "Q1", "status": "addressed", "direct_answer": "A1",
             "evidence_basis": "E1", "linked_priorities": ["Priority 1 · Do X"], "confidence_gap_note": "N1"},
            {"id": "q2", "question": "Q2", "status": "partially_addressed", "direct_answer": "A2",
             "evidence_basis": "E2", "linked_priorities": [], "confidence_gap_note": "N2"},
        ]})
        + "%%%FOCUS_QUESTIONS_END%%% trailing"
    )
    out = extract_focus_questions(text)
    assert out['error'] is False
    assert len(out['responses']) == 2
    assert out['summary'] == {'addressed': 1, 'partially_addressed': 1, 'not_yet_addressed': 0}


def test_extract_focus_questions_coerces_bad_status():
    text = ("%%%FOCUS_QUESTIONS_START%%%"
            + json.dumps({"responses": [{"id": "q1", "question": "Q", "status": "maybe", "direct_answer": "A"}]})
            + "%%%FOCUS_QUESTIONS_END%%%")
    out = extract_focus_questions(text)
    assert out['responses'][0]['status'] == 'not_yet_addressed'
    assert out['responses'][0]['linked_priorities'] == []


def test_extract_focus_questions_salvages_truncated_json():
    text = ('%%%FOCUS_QUESTIONS_START%%%\n{"responses": [\n'
            '{"id": "q1", "question": "Q1", "status": "addressed", "direct_answer": "A1",'
            ' "evidence_basis": "E1", "linked_priorities": [], "confidence_gap_note": "N1"},\n'
            '{"id": "q2", "question": "Q2", "status": "addr')  # truncated mid-entry
    out = extract_focus_questions(text)
    assert len(out['responses']) == 1
    assert out['responses'][0]['id'] == 'q1'


def test_extract_focus_questions_empty_on_no_marker():
    out = extract_focus_questions("no markers here")
    assert out['error'] is True
    assert out['responses'] == []


def test_extract_focus_questions_passes_overview():
    text = ("%%%FOCUS_QUESTIONS_START%%%"
            + json.dumps({"overview": "Intro text.", "responses": [
                {"id": "q1", "question": "Q", "status": "addressed", "direct_answer": "A",
                 "evidence_basis": "E", "linked_priorities": [], "confidence_gap_note": "N"}]})
            + "%%%FOCUS_QUESTIONS_END%%%")
    out = extract_focus_questions(text)
    assert out['overview'] == "Intro text."
    assert out['responses'][0]['status'] == 'addressed'
