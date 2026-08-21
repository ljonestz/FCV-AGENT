"""Contract tests for the optional Stage 3 concise FCV readout bundle."""

import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
from app import extract_priorities


CONCISE_READOUT = {
    "headline": "FCV risks are recognized, but key delivery choices remain unresolved.",
    "overview": " ".join(
        ["The operation faces material access, exclusion, and legitimacy risks."] * 18
    ),
    "strengths": [
        {"title": "Context awareness", "text": "The document identifies the main FCV pressures."},
        {"title": "Community feedback", "text": "The design includes beneficiary feedback channels."},
        {"title": "Adaptive delivery", "text": "Implementation arrangements allow bounded adjustment."},
    ],
}

CONCISE_PRIORITY = {
    "title": "Define access triggers",
    "why": "The unresolved choice affects access, inclusion, and delivery.",
    "how": ["Define the trigger and owner.", "Record the response in the current instrument."],
    "suggested_wording": {
        "document_element": "Implementation arrangements",
        "text": "Review access conditions quarterly.",
    },
    "project_cycle": {
        "primary_label": "Address during implementation",
        "primary_text": "Agree the trigger, response, and owner now.",
        "secondary_label": "Track through the ISR",
        "secondary_text": "Report activation through routine implementation reporting.",
    },
}


def _detailed_priority(number: int) -> dict:
    return {
        "number": number,
        "title": f"Priority {number} - access in Bentiu",
        "dimension": "Inclusion",
        "tag": "[S+R]",
        "risk_level": "High",
        "the_gap": "Access arrangements do not yet account for changing conditions in Bentiu.",
        "why_it_matters": "Unclear access decisions can exclude affected groups and weaken trust.",
        "recommendation": "Define an access trigger and document the response in the implementation arrangements.",
        "who_acts": "TTL",
        "when": "During implementation",
        "resources": "Minimal",
        "concise": copy.deepcopy(CONCISE_PRIORITY),
    }


def _payload() -> dict:
    return {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Emerging",
        "sensitivity_summary": "The operation recognizes material FCV delivery risks.",
        "responsiveness_summary": "The operation has several adaptive entry points.",
        "risk_exposure": {
            "risks_to": "Conflict conditions may disrupt delivery.",
            "risks_from": "Unequal access may reinforce exclusion.",
        },
        "concise_readout": copy.deepcopy(CONCISE_READOUT),
        "priorities": [_detailed_priority(1), _detailed_priority(2)],
    }


def _wrapped(payload: dict) -> str:
    return (
        "Narrative.\n%%%JSON_START%%%\n"
        + json.dumps(payload)
        + "\n%%%JSON_END%%%"
    )


def _assert_concise_disabled_but_detailed_preserved(result: dict) -> None:
    assert result["error"] is False
    assert len(result["priorities"]) == 2
    assert result["priorities"][0]["the_gap"]
    assert result["priorities"][1]["recommendation"]
    assert result["concise_readout"] is None
    assert all("concise" not in priority for priority in result["priorities"])


def test_complete_bundle_returns_normalized_readout_and_priority_cards():
    result = extract_priorities(_wrapped(_payload()))

    assert result["error"] is False
    assert result["concise_readout"] == CONCISE_READOUT
    assert result["priorities"][0]["concise"] == CONCISE_PRIORITY
    assert result["priorities"][1]["concise"] == CONCISE_PRIORITY


def test_missing_one_priority_concise_disables_the_entire_bundle_without_detail_loss():
    payload = _payload()
    payload["priorities"][1].pop("concise")

    result = extract_priorities(_wrapped(payload))

    _assert_concise_disabled_but_detailed_preserved(result)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(
            lambda payload: payload["concise_readout"].update({"overview": "Too short."}),
            id="overview-below-100-words",
        ),
        pytest.param(
            lambda payload: payload["concise_readout"].update(
                {"strengths": copy.deepcopy(CONCISE_READOUT["strengths"][:2])}
            ),
            id="fewer-than-three-strengths",
        ),
        pytest.param(
            lambda payload: payload["priorities"][0]["concise"].update(
                {"how": ["Define the trigger and owner."]}
            ),
            id="fewer-than-two-how-actions",
        ),
        pytest.param(
            lambda payload: payload["priorities"][0]["concise"]["project_cycle"].update(
                {"primary_text": ""}
            ),
            id="missing-primary-lifecycle-text",
        ),
        pytest.param(
            lambda payload: payload.update({"concise_readout": ["not", "an", "object"]}),
            id="readout-not-an-object",
        ),
    ],
)
def test_invalid_concise_bundle_is_disabled_atomically(mutate):
    payload = _payload()
    mutate(payload)

    result = extract_priorities(_wrapped(payload))

    _assert_concise_disabled_but_detailed_preserved(result)


@pytest.mark.parametrize("missing_rating", ["fcv_rating", "fcv_responsiveness_rating"])
def test_both_fcv_ratings_are_required_for_concise_bundle(missing_rating):
    payload = _payload()
    payload.pop(missing_rating)

    result = extract_priorities(_wrapped(payload))

    _assert_concise_disabled_but_detailed_preserved(result)


def test_optional_wording_and_secondary_lifecycle_fields_normalize_to_empty_strings():
    payload = _payload()
    for priority in payload["priorities"]:
        priority["concise"].pop("suggested_wording")
        priority["concise"]["project_cycle"].pop("secondary_label")
        priority["concise"]["project_cycle"].pop("secondary_text")

    result = extract_priorities(_wrapped(payload))

    assert result["concise_readout"] == CONCISE_READOUT
    for priority in result["priorities"]:
        concise = priority["concise"]
        assert concise["suggested_wording"] == {
            "document_element": "",
            "text": "",
        }
        assert concise["project_cycle"]["secondary_label"] == ""
        assert concise["project_cycle"]["secondary_text"] == ""


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("fcv_rating", None, id="null-sensitivity-rating"),
        pytest.param(
            "fcv_responsiveness_rating",
            ["Emerging"],
            id="list-responsiveness-rating",
        ),
    ],
)
def test_non_string_or_null_fcv_ratings_disable_concise_bundle(field, value):
    payload = _payload()
    payload[field] = value

    result = extract_priorities(_wrapped(payload))

    assert result["error"] is False
    assert len(result["priorities"]) == 2
    assert result[field] == str(value).strip()
    assert result["concise_readout"] is None
    assert all("concise" not in priority for priority in result["priorities"])


@pytest.mark.parametrize("include_valid", [False, True], ids=["only-invalid", "valid-plus-invalid"])
def test_non_object_raw_priority_disables_concise_bundle(include_valid):
    payload = _payload()
    valid_priority = payload["priorities"][0]
    payload["priorities"] = [valid_priority, None] if include_valid else [None]

    result = extract_priorities(_wrapped(payload))

    assert result["error"] is False
    assert len(result["priorities"]) == (1 if include_valid else 0)
    assert result["concise_readout"] is None
    assert all("concise" not in priority for priority in result["priorities"])

@pytest.mark.parametrize(
    ("doc_type", "temporal_context", "review_mode", "expected_label"),
    [
        ("PCN", {"processing_track": "standard"}, "design", "Commit in the PCN"),
        ("PCN", {"processing_track": "consolidated_condensed"}, "design", "Resolve by Decision Review"),
        ("PAD", {}, "design", "Resolve before the review gate"),
        ("PID", {}, "design", "Resolve before the review gate"),
        ("ISR", {}, "implementation", "Address during implementation"),
        ("Additional Financing", {}, "implementation", "Include in the current package"),
        ("Restructuring Paper", {}, "implementation", "Include in the current package"),
        ("Unknown", {}, "design", "When to address"),
    ],
)
def test_concise_lifecycle_context_matches_review_stage(
    doc_type, temporal_context, review_mode, expected_label
):
    text = app.build_concise_lifecycle_context(doc_type, temporal_context, review_mode)
    assert expected_label in text


@pytest.mark.parametrize("review_mode", ["design", "implementation"])
def test_core_stage3_prompt_gets_concise_contract_for_every_review(review_mode):
    prompt = app.append_core_concise_stage3_contract(
        "BASE", "PCN", {"processing_track": "standard"}, review_mode, []
    )
    assert prompt.startswith("BASE")
    assert '"concise_readout"' in prompt
    assert '"concise"' in prompt


def test_active_lens_stage3_prompt_is_unchanged():
    prompt = app.append_core_concise_stage3_contract(
        "BASE", "PCN", {"processing_track": "standard"}, "design", [{"id": "climate"}]
    )
    assert prompt == "BASE"


def test_concise_contract_preserves_detail_and_covers_overall_assessment():
    contract = app.CONCISE_STAGE3_OUTPUT_CONTRACT
    assert "same analysis and same json block" in contract.lower()
    assert "detailed findings" in contract.lower()
    assert "both FCV ratings" in contract
    assert "priority count, order, and actions" in contract
    assert "150-200 word" in contract
    for required in (
        "headline judgment",
        "review-stage context",
        "principal FCV exposure",
        "two-way risk",
        "sensitivity versus responsiveness",
        "strongest feature",
        "most consequential gap",
        "bottom-line implication",
        "exactly 3",
    ):
        assert required in contract
    assert "Do not generate advisory" in contract


def test_stage3_prompt_contract_is_wired_to_both_workflows():
    source = open(app.__file__, encoding="utf-8").read()
    assert source.count("append_core_concise_stage3_contract(") == 3


def _decode_sse(response):
    return [
        json.loads(chunk[6:])
        for chunk in response.get_data(as_text=True).split("\n\n")
        if chunk.startswith("data: ")
    ]


def test_step_by_step_completion_payload_transports_concise_bundle(monkeypatch):
    raw = _wrapped(_payload())

    def fake_stream(_messages, _max_tokens, _stage, **_kwargs):
        fake_stream._last_result = raw
        fake_stream._last_stop_reason = "end_turn"
        yield 'data: {"chunk": "stage3"}\n\n'

    monkeypatch.setattr(app, "_stream_stage", fake_stream)
    response = app.app.test_client().post("/api/run-stage", json={
        "stage": 3,
        "active_lenses": [],
        "review_mode": "design",
        "history": [{"role": "assistant", "content": "Stage 2 analysis."}],
        "document_type": "PAD",
        "doc_type": "PAD",
        "instrument_type": "IPF",
        "temporal_context": {},
        "regime_context": {},
    })

    done = next(event for event in _decode_sse(response) if event.get("done"))
    assert done["concise_readout"] == CONCISE_READOUT
    assert done["priorities"][0]["concise"] == CONCISE_PRIORITY


def test_step_by_step_completion_payload_preserves_detail_on_invalid_bundle(monkeypatch):
    payload = _payload()
    payload["concise_readout"]["overview"] = "Too short."
    raw = _wrapped(payload)

    def fake_stream(_messages, _max_tokens, _stage, **_kwargs):
        fake_stream._last_result = raw
        fake_stream._last_stop_reason = "end_turn"
        yield 'data: {"chunk": "stage3"}\n\n'

    monkeypatch.setattr(app, "_stream_stage", fake_stream)
    response = app.app.test_client().post("/api/run-stage", json={
        "stage": 3,
        "active_lenses": [],
        "review_mode": "design",
        "history": [{"role": "assistant", "content": "Stage 2 analysis."}],
        "document_type": "PAD",
        "doc_type": "PAD",
        "instrument_type": "IPF",
        "temporal_context": {},
        "regime_context": {},
    })

    done = next(event for event in _decode_sse(response) if event.get("done"))
    assert done["concise_readout"] is None
    assert done["priorities"][0]["the_gap"]
    assert done["fcv_rating"] == payload["fcv_rating"]
    assert done["fcv_responsiveness_rating"] == payload["fcv_responsiveness_rating"]


@pytest.mark.parametrize("valid_bundle", [True, False], ids=["valid", "invalid"])
def test_express_completion_payload_transports_concise_bundle(monkeypatch, valid_bundle):
    payload = _payload()
    if not valid_bundle:
        payload["concise_readout"]["overview"] = "Too short."
    raw = _wrapped(payload)

    def fake_stream(_messages, _max_tokens, stage, **_kwargs):
        fake_stream._last_result = (
            "Stage 1 project extraction."
            if stage == 1
            else "Stage 2 assessment."
            if stage == 2
            else raw
        )
        fake_stream._last_stop_reason = "end_turn"
        yield 'data: {"chunk": "stage"}\n\n'

    def fake_research(*_args, **_kwargs):
        yield {"result": {
            "core_brief": "Compact FCV research.",
            "climate_research": {},
            "lens_context_sources": [],
            "climate_grounding": {},
        }}

    monkeypatch.setattr(app, "_stream_stage", fake_stream)
    monkeypatch.setattr(app, "_iter_stage1_research", fake_research)
    monkeypatch.setattr(app, "extract_country_name", lambda *_args: "Exampleland")
    monkeypatch.setattr(app, "extract_sector_name", lambda *_args: "Transport")
    monkeypatch.setattr(app, "get_fast_client", lambda: object())
    monkeypatch.setattr(app, "extract_instrument_type", lambda _text: "IPF")
    monkeypatch.setattr(app, "extract_temporal_context", lambda _text: {})
    monkeypatch.setattr(app, "extract_regime_context", lambda _text, _instrument: {})
    monkeypatch.setattr(app, "extract_country_classification", lambda _text: {"category": "General"})
    monkeypatch.setattr(app, "extract_context_flags", lambda _text: {})
    monkeypatch.setattr(app, "extract_sector_context", lambda _text: {"primary_sector": "Transport"})
    monkeypatch.setattr(app, "extract_change_types", lambda _text: [])
    monkeypatch.setattr(app, "extract_prior_actions", lambda _text: [])
    monkeypatch.setattr(app, "extract_dlis", lambda _text: [])
    monkeypatch.setattr(app, "extract_country_set", lambda _text: {"is_multi_country": False})
    monkeypatch.setattr(app, "extract_mpa_context", lambda _text: {"is_mpa": False})
    monkeypatch.setattr(app, "extract_lens_evidence", lambda *_args: {})

    response = app.app.test_client().post("/api/run-express", json={
        "active_lenses": [],
        "review_mode": "design",
        "document_type": "PAD",
        "instrument_type": "IPF",
        "documents": [{
            "name": "PAD.txt",
            "type": "text",
            "docRole": "primary",
            "content": "Named transport project activities. " * 10,
        }],
    })

    done = next(
        event for event in _decode_sse(response) if event.get("stage_done") == 3
    )
    if valid_bundle:
        assert done["concise_readout"] == CONCISE_READOUT
        assert done["priorities"][0]["concise"] == CONCISE_PRIORITY
    else:
        assert done["concise_readout"] is None
        assert done["priorities"][0]["the_gap"]
        assert done["fcv_rating"] == payload["fcv_rating"]
        assert done["fcv_responsiveness_rating"] == payload["fcv_responsiveness_rating"]
