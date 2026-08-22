"""Contract tests for the optional Stage 3 concise FCV readout bundle."""

import copy
import json
import os
import subprocess
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
    "strengths_transition": "These strengths provide a foundation for the actions below.",
    "priorities_transition": "The priorities move from immediate concept decisions to preparation actions.",
    "closing": "Taken together, these changes would turn contextual awareness into practical design choices. The first decisions belong in the PCN; later detail can follow during preparation.",
}

PROJECT_CYCLE = {
    "primary_label": "At concept stage",
    "primary_text": "Commit the design choice in the PCN.",
    "secondary_label": "During preparation",
    "secondary_text": "Translate the commitment into implementation arrangements.",
}

CONCISE_PRIORITY = {
    "title": "Define access triggers",
    "why": "The unresolved choice affects access, inclusion, and delivery.",
    "how": ["Define the trigger and owner.", "Record the response in the current instrument."],
    "suggested_wording": {
        "document_element": "Implementation arrangements",
        "text": "Review access conditions quarterly.",
    },
    "project_cycle": copy.deepcopy(PROJECT_CYCLE),
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
        "project_cycle": copy.deepcopy(PROJECT_CYCLE),
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
    assert result["priorities"][0]["project_cycle"] == PROJECT_CYCLE


def test_missing_one_priority_concise_uses_deterministic_detail_fallback():
    payload = _payload()
    payload["priorities"][1].pop("concise")
    payload["priorities"][1]["actions"] = [
        {
            "document_element": "PCN",
            "guidance": "Name the access trigger in the PCN.",
            "suggested_language": "The PCN will define the access trigger.",
        },
        {
            "document_element": "Implementation arrangements",
            "guidance": "Assign the response owner for Bentiu.",
            "suggested_language": "The TTL will record the response owner.",
        },
    ]

    result = extract_priorities(_wrapped(payload))

    assert result["error"] is False
    assert result["concise_readout"] == CONCISE_READOUT
    fallback = result["priorities"][1]["concise"]
    assert fallback["title"] == payload["priorities"][1]["title"]
    assert fallback["why"] == payload["priorities"][1]["why_it_matters"]
    assert fallback["how"] == [
        "Name the access trigger in the PCN.",
        "Assign the response owner for Bentiu.",
    ]
    assert fallback["suggested_wording"] == {
        "document_element": "PCN",
        "text": "The PCN will define the access trigger.",
    }
    assert fallback["project_cycle"] == PROJECT_CYCLE


def test_concise_bundle_requires_grounded_narrative_bridges():
    for field in ("strengths_transition", "priorities_transition", "closing"):
        payload = _payload()
        payload["concise_readout"].pop(field)

        result = extract_priorities(_wrapped(payload))

        assert result["concise_readout"] is None
        assert all("concise" not in priority for priority in result["priorities"])


def _add_detailed_actions(priority: dict) -> None:
    priority["actions"] = [
        {
            "document_element": "PCN",
            "guidance": "Name the access trigger in the PCN.",
            "suggested_language": "The PCN will define the access trigger.",
        },
        {
            "document_element": "Implementation arrangements",
            "guidance": "Assign the response owner for Bentiu.",
            "suggested_language": "The TTL will record the response owner.",
        },
    ]

@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(
            lambda payload: payload["concise_readout"].update({"overview": "Too short."}),
            id="overview-below-150-words",
        ),
        pytest.param(
            lambda payload: payload["concise_readout"].update(
                {"overview": " ".join(["word"] * 201)}
            ),
            id="overview-above-200-words",
        ),
        pytest.param(
            lambda payload: payload["concise_readout"].update(
                {"strengths": copy.deepcopy(CONCISE_READOUT["strengths"][:2])}
            ),
            id="fewer-than-three-strengths",
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
        priority["project_cycle"].pop("secondary_label")
        priority["project_cycle"].pop("secondary_text")
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


def test_active_lens_default_stage3_prompt_does_not_gain_concise_schema():
    prompt = app.append_core_concise_stage3_contract(
        app.DEFAULT_PROMPTS["3"],
        "PID",
        {"processing_track": "standard"},
        "design",
        [{"id": "agriculture"}],
    )
    assert '"concise_readout"' not in prompt


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
    assert "OUTPUT ORDER OVERRIDE" in contract
    assert "Start the response with %%%JSON_START%%%" in contract
    assert "before any preamble or narrative" in contract
    assert "After %%%JSON_END%%%, write the full detailed Recommendations Note" in contract
    assert "overrides any earlier instruction" in contract
    assert "number of `concise` objects must equal the number of priority objects" in contract
    assert "Never attach `concise` only to the final priority" in contract
    assert (
        "If you emit `concise_readout`, all fields shown below are required"
        in contract
    )
    assert "Add these optional fields" not in contract



@pytest.mark.parametrize(
    "prompt_key,review_mode,doc_type",
    [("3", "design", "PID"), ("impl_3", "implementation", "ISR")],
)
def test_rendered_core_stage3_schema_contains_concise_fields(
    prompt_key, review_mode, doc_type
):
    rendered = app.DEFAULT_PROMPTS[prompt_key].format(
        doc_type=doc_type,
        instrument_guidance="Instrument guidance",
        minimum_reference_set="Minimum references",
        playbook_guidance="Playbook guidance",
        process_guidance="Process guidance",
        regime_header="Regime header",
        seash_gender_card_guidance="SEA/SH guidance",
        temporal_guardrail="Temporal guardrail",
        timing_emphasis="Timing",
    )
    prompt = app.append_core_concise_stage3_contract(
        rendered,
        doc_type,
        {"processing_track": "standard"},
        review_mode,
        [],
    )

    assert '  "concise_readout": {' in prompt
    assert '      "concise": {' in prompt
    assert '"project_cycle": {' in prompt
    assert '"strengths_transition"' in prompt
    assert "must come AFTER all narrative text" not in prompt
    assert "present at the end" not in prompt
def test_default_stage3_json_schema_embeds_concise_fields():
    prompt = app.append_core_concise_stage3_contract(
        app.DEFAULT_PROMPTS["3"],
        "PID",
        {"processing_track": "standard"},
        "design",
        [],
    )
    schema = next(
        segment.split("%%%JSON_END%%%", 1)[0]
        for segment in prompt.split("%%%JSON_START%%%")[1:]
        if '"priorities"' in segment
    )

    assert '"concise_readout"' in schema
    assert '"concise":' in schema
    assert '"project_cycle":' in schema
    assert '"priority_scope": "Not identified"' in schema
    assert schema.index('"concise_readout"') < schema.index('"priorities"')
    assert "must come AFTER all narrative text" not in prompt
    assert "present at the end" not in prompt
    assert (
        '"secondary_text": "Optional follow-on step"\n        }\n'
        '      }\n    }}}}'
    ) in schema


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


def test_step_by_step_uses_effective_doc_type_for_priority_scope(monkeypatch):
    payload = _payload()
    payload["priorities"][0]["priority_scope"] = "mid-cycle"
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
        "doc_type": "AF",
        "instrument_type": "IPF",
        "temporal_context": {},
        "regime_context": {},
    })

    done = next(event for event in _decode_sse(response) if event.get("done"))
    assert done["priorities"][0]["priority_scope"] == "mid-cycle"


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


def _extract_js_function(source: str, name: str) -> str:
    marker = f"function {name}("
    start = source.find(marker)
    assert start >= 0, f"Missing JS helper {name}()"
    brace = source.find("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError(f"Unterminated JS helper {name}()")


def test_frontend_declares_shared_summary_state_capability_and_fallback():
    source = open(os.path.join(os.path.dirname(app.__file__), "index.html"), encoding="utf-8").read()

    for expected in (
        "let stageConciseReadout",
        "function supportsConciseStage3View(",
        "function supportsAnyStage3Summary(",
        "function renderNormalFcvSummary(",
        "function renderFcvRatingIndicators(",
        "function renderStage3Summary(",
        "concise_readout_unavailable",
        "The summary was unavailable for this run; the full analysis is shown.",
    ):
        assert expected in source
    assert "stage3View=supportsAnyStage3Summary()?'summary':'detailed'" in source


def test_frontend_rejects_incomplete_saved_readout_and_keeps_fallback_diagnostic():
    source = open(os.path.join(os.path.dirname(app.__file__), "index.html"), encoding="utf-8").read()
    supports = _extract_js_function(source, "supportsConciseStage3View")
    unavailable = _extract_js_function(source, "conciseUnavailableHtml")
    script = f"""
let activeLenses=[];
let stageThreePriorities={json.dumps(_payload()["priorities"])};
let stageConciseReadout={json.dumps(CONCISE_READOUT)};
{supports}
{unavailable}
for(const field of ['strengths_transition','priorities_transition','closing']){{
  const missing={{...stageConciseReadout}};
  delete missing[field];
  stageConciseReadout=missing;
  if(supportsConciseStage3View())throw new Error('accepted saved readout missing '+field);
  stageConciseReadout={{...missing,[field]:'   '}};
  if(supportsConciseStage3View())throw new Error('accepted saved readout blank '+field);
  stageConciseReadout={json.dumps(CONCISE_READOUT)};
}}
stageConciseReadout=null;
const fallback=conciseUnavailableHtml();
for(const expected of ['data-diagnostic="concise_readout_unavailable"','The summary was unavailable for this run; the full analysis is shown.']){{
  if(!fallback.includes(expected))throw new Error('missing fallback diagnostic '+expected);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_frontend_normal_summary_renderer_includes_required_sections():
    source = open(os.path.join(os.path.dirname(app.__file__), "index.html"), encoding="utf-8").read()
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "renderFcvRatingIndicators",
            "getConcisePriority",
            "renderSummaryPriorityAccordion",
            "renderNormalFcvSummary",
        )
    )
    script = f"""
const esc=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
let stageConciseReadout={json.dumps({**CONCISE_READOUT, "strengths_transition": "Strengths bridge <strong>", "priorities_transition": "Priorities bridge & tradeoffs", "closing": "Closing note <em>"})};
let openSummaryPriority=0;
let stageThreePriorities={json.dumps(_payload()["priorities"])};
let fcvRating='Adequate';
let fcvResponsivenessRating='Emerging';
const renderStage3AdvisoryTransition=()=>'<p>advisory</p>';
{helpers}
const html=renderNormalFcvSummary();
for(const expected of ['Five-minute readout','Overall assessment','What is already working','FCV sensitivity','FCV responsiveness','Priority actions for the task team']){{
  if(!html.includes(expected))throw new Error('missing '+expected+' | '+html);
}}
for(const expected of ['Strengths bridge &lt;strong&gt;','Priorities bridge &amp; tradeoffs','Closing note &lt;em&gt;']){{
  if(!html.includes(expected))throw new Error('missing escaped readout field '+expected+' | '+html);
}}
const order=['Overall assessment','Strengths bridge &lt;strong&gt;','What is already working','Priorities bridge &amp; tradeoffs','advisory','Priority actions for the task team','summary-priority-accordion','Closing note &lt;em&gt;'];
for(let i=1;i<order.length;i++){{
  const previous=html.indexOf(order[i-1]);
  const current=html.indexOf(order[i]);
  if(previous<0||current<0||previous>=current)throw new Error('wrong summary narrative order: '+order[i-1]+' -> '+order[i]+' | '+html);
}}
console.log(html);
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_summary_priority_accordion_is_single_open_and_accessible():
    source = open(os.path.join(os.path.dirname(app.__file__), "index.html"), encoding="utf-8").read()
    helpers = "\n".join(
        _extract_js_function(source, name)
        for name in (
            "getConcisePriority",
            "renderSummaryPriorityAccordion",
            "toggleSummaryPriority",
        )
    )
    priorities = [_detailed_priority(index) for index in range(1, 5)]
    script = f"""
const esc=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
let stageThreePriorities={json.dumps(priorities)};
let openSummaryPriority=0;
let currentPriority=0;
let focused='';
const host={{innerHTML:''}};
const document={{getElementById:id=>id==='summary-priority-accordion'?host:{{focus:()=>{{focused=id;}}}}}};
{helpers}
const initial=renderSummaryPriorityAccordion();
if((initial.match(/class="summary-priority-toggle/g)||[]).length!==4)throw new Error('wrong header count');
if((initial.match(/aria-expanded="true"/g)||[]).length!==1)throw new Error('wrong expanded count');
if(!initial.includes('id="summary-priority-panel-0"')||/id="summary-priority-panel-0"[^>]* hidden/.test(initial))throw new Error('first not open');
if(!initial.includes('aria-controls="summary-priority-panel-3"'))throw new Error('missing aria controls');
toggleSummaryPriority(2);
if(currentPriority!==2)throw new Error('detailed priority selection not synchronized');
if(!host.innerHTML.includes('id="summary-priority-toggle-2"')||!host.innerHTML.includes('aria-expanded="true"'))throw new Error('third not open');
if(!/id="summary-priority-panel-0"[^>]* hidden/.test(host.innerHTML))throw new Error('first not collapsed');
if(focused!=='summary-priority-toggle-2')throw new Error('focus not restored');
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_shared_advisory_is_controlled_and_used_by_both_routes():
    source = open(os.path.join(os.path.dirname(app.__file__), "index.html"), encoding="utf-8").read()
    advisory = _extract_js_function(source, "renderStage3AdvisoryTransition")
    climate = _extract_js_function(source, "renderClimateVerifiedSummary")
    normal = _extract_js_function(source, "renderNormalFcvSummary")
    script = f"""
let reviewMode='design';
{advisory}
const html=renderStage3AdvisoryTransition('normal')+renderStage3AdvisoryTransition('climate');
for(const expected of ['not mandatory requirements','FCV Country Coordinator','Global Practice experts']){{
  if(!html.includes(expected))throw new Error('missing '+expected);
}}
"""
    result = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert "renderStage3AdvisoryTransition('normal')" in normal
    assert "renderStage3AdvisoryTransition('climate')" in climate
    assert "aria-expanded" in source
    assert "aria-controls" in source


def test_stage3_view_uses_the_active_tab_as_its_panel_label():
    source = open(os.path.join(os.path.dirname(app.__file__), "index.html"), encoding="utf-8").read()

    assert 'role="tabpanel"' in source
    assert "view==='summary'?'stage3-summary-tab':'stage3-detailed-tab'" in source


def test_concise_summary_persists_with_priorities_and_restores_before_view_selection():
    source = open(os.path.join(os.path.dirname(app.__file__), "index.html"), encoding="utf-8").read()
    express_store = _extract_js_function(source, "epSafeStore")
    save_session = _extract_js_function(source, "saveSession")
    load_session = _extract_js_function(source, "loadSession")

    for block in (express_store, save_session):
        assert "stageConciseReadout" in block
        assert "stageThreePriorities" in block
        assert "fcvRating" in block
        assert "fcvResponsivenessRating" in block

    express_restore = source[source.index("const savedLensState="):source.index("// Partial state:")]
    assert "stageConciseReadout=savedLensState.stageConciseReadout||null" in express_restore
    assert "stageThreePriorities=Array.isArray(savedLensState.stageThreePriorities)" in express_restore
    assert "fcvRating=savedLensState.fcvRating||''" in express_restore
    assert "fcvResponsivenessRating=savedLensState.fcvResponsivenessRating||''" in express_restore
    assert "if(outputs[3]&&supportsAnyStage3Summary())" in express_restore
    assert "if(outputs[3]&&climateVerifiedAssessment&&climateVerifiedReader)" not in express_restore
    assert express_restore.index("stageConciseReadout=savedLensState") < express_restore.index(
        "stage3View=supportsAnyStage3Summary()?'summary':'detailed'"
    )

    assert "stageConciseReadout = state.stageConciseReadout || null" in load_session
    assert "stageThreePriorities = Array.isArray(state.stageThreePriorities)" in load_session
    assert "fcvRating = state.fcvRating || ''" in load_session
    assert "fcvResponsivenessRating = state.fcvResponsivenessRating || ''" in load_session
    assert load_session.index("stageConciseReadout = state.stageConciseReadout") < load_session.index(
        "stage3View=supportsAnyStage3Summary()?'summary':'detailed'"
    )

    reset = _extract_js_function(source, "reset")
    for expected in (
        "stageThreePriorities=[]",
        "stageConciseReadout=null",
        "openSummaryPriority=0",
        "fcvRating=''",
        "fcvResponsivenessRating=''",
    ):
        assert expected in reset


def test_downloads_remain_detailed_only():
    source = open(os.path.join(os.path.dirname(app.__file__), "index.html"), encoding="utf-8").read()
    exports = "\n".join(
        _extract_js_function(source, name)
        for name in ("downloadReport", "downloadHTML")
    )
    for forbidden in (
        "renderNormalFcvSummary",
        "renderClimateVerifiedSummary",
        "renderStage3AdvisoryTransition",
        "renderSummaryPriorityAccordion",
        "stageConciseReadout",
    ):
        assert forbidden not in exports


def test_concise_cycle_mismatch_uses_canonical_priority_fallback():
    payload = _payload()
    priority = payload["priorities"][1]
    _add_detailed_actions(priority)
    priority["concise"]["project_cycle"]["primary_text"] = "Different timing."
    result = extract_priorities(_wrapped(payload))

    assert result["concise_readout"] == CONCISE_READOUT
    assert result["priorities"][1]["concise"]["project_cycle"] == PROJECT_CYCLE


def test_malformed_one_priority_concise_uses_deterministic_detail_fallback():
    payload = _payload()
    priority = payload["priorities"][1]
    _add_detailed_actions(priority)
    priority["concise"]["how"] = ["Only one action"]
    result = extract_priorities(_wrapped(payload))

    assert result["concise_readout"] == CONCISE_READOUT
    assert result["priorities"][1]["concise"]["how"] == [
        "Name the access trigger in the PCN.", "Assign the response owner for Bentiu."
    ]


def test_fallback_uses_first_guidance_bearing_action_for_suggested_wording():
    payload = _payload()
    priority = payload["priorities"][1]
    priority["actions"] = [
        {"document_element": "", "guidance": "", "suggested_language": ""},
        {
            "document_element": "PCN",
            "guidance": "Name the access trigger in the PCN.",
            "suggested_language": "The PCN will define the access trigger.",
        },
        {
            "document_element": "Implementation arrangements",
            "guidance": "Assign the response owner for Bentiu.",
            "suggested_language": "The TTL will record the response owner.",
        },
    ]
    priority["concise"]["how"] = ["Only one action"]

    result = extract_priorities(_wrapped(payload))

    fallback = result["priorities"][1]["concise"]
    assert fallback["how"] == [
        "Name the access trigger in the PCN.",
        "Assign the response owner for Bentiu.",
    ]
    assert fallback["suggested_wording"] == {
        "document_element": "PCN",
        "text": "The PCN will define the access trigger.",
    }


def test_invalid_canonical_project_cycle_keeps_detailed_but_disables_summary():
    payload = _payload()
    payload["priorities"][0]["project_cycle"]["primary_text"] = ""
    result = extract_priorities(_wrapped(payload))

    _assert_concise_disabled_but_detailed_preserved(result)
    assert result["priorities"][0]["project_cycle"] is None
