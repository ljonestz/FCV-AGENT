"""Zero-priority Phase 3 (2026-11-17): normal-route Stage 3 failure codes and JSON recovery."""

import json

from app import (
    _blocking_with_keepalive,
    _stage3_json_template,
    extract_priorities,
    recover_stage3_priorities,
)

PRIORITY = {"title": "Codify selection rules", "the_gap": "Gap.", "why_it_matters": "Why.", "actions": []}


def _note(payload):
    return "## Note\nNarrative.\n%%%JSON_START%%%" + json.dumps(payload) + "%%%JSON_END%%%"


def test_each_empty_outcome_has_its_own_failure_code_and_message():
    missing = extract_priorities("## Note\nNarrative only, cut off")
    assert missing["parse_failure"] == "missing" and "cut off" in missing["message"]
    invalid = extract_priorities("%%%JSON_START%%%{not json%%%JSON_END%%%")
    assert invalid["parse_failure"] == "invalid"
    empty = extract_priorities(_note({"priorities": []}))
    assert empty["parse_failure"] == "empty" and "did not return any priority" in empty["message"]
    malformed = extract_priorities(_note({"priorities": ["just a string"]}))
    assert malformed["error"] and malformed["parse_failure"] == "malformed"
    too_many = extract_priorities(_note({"priorities": [PRIORITY] * 6}), active_lens_ids=[])
    assert too_many["parse_failure"] == "too_many"
    ok = extract_priorities(_note({"priorities": [PRIORITY]}))
    assert ok["error"] is False and len(ok["priorities"]) == 1


def test_recovery_reemits_the_json_block_and_reparses():
    broken = "## Note\nPriority 1: Codify selection rules.\n%%%JSON_START%%%{\"priorities\": [{\"title\": \"Codify"
    parsed = extract_priorities(broken)
    prompts = []

    def fake(prompt):
        prompts.append(prompt)
        return "%%%JSON_START%%%" + json.dumps({"priorities": [PRIORITY]}) + "%%%JSON_END%%%"

    text, recovered = recover_stage3_priorities(broken, parsed, extract_priorities,
                                                template=_stage3_json_template(), call=fake)
    assert len(prompts) == 1 and "add nothing new" in prompts[0]
    assert recovered["error"] is False and recovered["json_recovered"] == "missing"
    assert text.count("%%%JSON_START%%%") == 1 and text.startswith("## Note")


def test_recovery_keeps_the_original_failure_when_the_follow_up_fails():
    broken = "## Note\ncut off"
    parsed = extract_priorities(broken)

    def unusable(prompt):
        return "I cannot help with that."

    def raises(prompt):
        raise RuntimeError("provider down")

    for call in (unusable, raises):
        text, result = recover_stage3_priorities(broken, parsed, extract_priorities, call=call)
        assert text == broken and result is parsed


def test_recovery_is_skipped_for_successful_or_non_recoverable_parses():
    good = extract_priorities(_note({"priorities": [PRIORITY]}))
    calls = []
    _text, result = recover_stage3_priorities("x", good, extract_priorities, call=calls.append)
    assert result is good and calls == []


def test_template_comes_from_the_stage3_prompt():
    assert '"priorities"' in _stage3_json_template()


def test_blocking_call_yields_keepalives_and_stores_result():
    import time
    holder = {}
    events = list(_blocking_with_keepalive(lambda: (time.sleep(0.35), 42)[1], holder, interval=0.1, stage=3))
    assert holder["result"] == 42
    assert events and all('"keepalive": true' in e for e in events)
    failing = {}
    list(_blocking_with_keepalive(lambda: 1 / 0, failing, interval=0.05))
    assert isinstance(failing["error"], ZeroDivisionError)


def test_climate_reader_names_the_unresolved_route_when_no_priority_is_produced():
    from sector_lenses.climate_verified_render import (
        ROUTE_UNRESOLVED_NO_PRIORITY_MESSAGE,
        build_reader_model,
    )
    base = {"judgments": {"sensitivity": {"value": "moderate"}, "responsiveness": {"value": "moderate"}}}
    unresolved = build_reader_model({**base, "validation": {"reason_codes": ["OPERATIONAL_GUIDANCE_WITHHELD"]}})
    assert unresolved["recommendation_message"] == ROUTE_UNRESOLVED_NO_PRIORITY_MESSAGE
    assert unresolved["recommendation_status"] == "partial"
    resolved = build_reader_model({**base, "validation": {"reason_codes": []}})
    assert resolved["recommendation_message"] != ROUTE_UNRESOLVED_NO_PRIORITY_MESSAGE


def test_more_than_five_priorities_is_not_recovered_by_truncation():
    too_many = extract_priorities(_note({"priorities": [PRIORITY] * 6}), active_lens_ids=[])
    calls = []
    _text, result = recover_stage3_priorities("x", too_many, extract_priorities, call=calls.append)
    assert result is too_many and calls == []
