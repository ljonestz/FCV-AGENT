"""Regression checks for corrections that must reach standard FCV output."""

import json

import pytest

from fcv_evidence_review import EvidenceReviewError, apply_review, build_review_prompt


def test_review_qualifies_claims_in_note_and_priority_cards():
    raw = (
        "HEIS support is activated.\n"
        "%%%JSON_START%%%"
        + json.dumps({"priorities": [{
            "the_gap": "Contractors face extortion at the project corridor.",
            "concise": {"gap": "Contractors face extortion at the project corridor."},
        }]})
        + "%%%JSON_END%%%"
    )
    review = {"issues": [
        {"outcome": "needs confirmation", "quote": "HEIS support is activated.",
         "replacement": "HEIS was approved; whether support has begun needs confirmation.",
         "reason": "Approval does not establish operation."},
        {"outcome": "qualified inference",
         "quote": "Contractors face extortion at the project corridor.",
         "replacement": "Assess whether contractors face extortion along the project corridor.",
         "reason": "Wider crime reporting does not document a corridor event."},
    ]}

    corrected, issues = apply_review(raw, json.dumps(review))

    assert "HEIS support is activated" not in corrected
    assert "whether support has begun needs confirmation" in corrected
    block = corrected.split("%%%JSON_START%%%", 1)[1].split("%%%JSON_END%%%", 1)[0]
    priority = json.loads(block)["priorities"][0]
    assert priority["the_gap"].startswith("Assess whether")
    assert priority["concise"]["gap"].startswith("Assess whether")
    assert len(issues) == 2


def test_review_keeps_conditional_advice_and_documented_commitment():
    raw = (
        "Obtain the ESCP and confirm the security arrangements. "
        "The supplied ESCP commits to a Security Management Plan under action 4.4."
    )
    review = {"issues": [
        {"outcome": "supported", "quote": "Obtain the ESCP and confirm the security arrangements.",
         "reason": "Valid conditional advice when the ESCP is not supplied."},
        {"outcome": "supported", "quote": "The supplied ESCP commits to a Security Management Plan under action 4.4.",
         "reason": "The supplied ESCP states this commitment."},
    ]}

    corrected, issues = apply_review(raw, json.dumps(review))

    assert corrected == raw
    assert [item["outcome"] for item in issues] == ["supported", "supported"]


def test_review_rejects_unapplied_material_correction():
    raw = "Notify the TTL within five business days."
    review = {"issues": [{"outcome": "contradicted or invalid source",
                          "quote": "Notify the Association within five business days.",
                          "replacement": "Check the ESCP incident notification rule.",
                          "reason": "The source does not support the claim."}]}

    with pytest.raises(EvidenceReviewError, match="not found"):
        apply_review(raw, json.dumps(review))


def test_review_prompt_preserves_exact_names_and_source_boundary():
    prompt = build_review_prompt(
        3,
        "Obtain the ESCP and confirm the security arrangements.",
        [{"name": "20260924_public-honduras-escp-p181166.pdf",
          "raw_text": "Action 4.4: assess and implement a Security Management Plan."}],
    )

    assert "20260924_public-honduras-escp-p181166.pdf" in prompt
    assert "supported" in prompt
    assert "qualified inference" in prompt
    assert "needs confirmation" in prompt
    assert "contradicted or invalid source" in prompt
    assert "conditional" in prompt.lower()



def test_both_routes_review_before_final_stage_payloads():
    from pathlib import Path

    source = (Path(__file__).resolve().parents[1] / "app.py").read_text(
        encoding="utf-8"
    )
    step = source.split("def run_stage():", 1)[1].split(
        "def _stream_stage(", 1
    )[0]
    express = source.split("def run_express():", 1)[1].split(
        "def _strip_html", 1
    )[0]
    assert "yield from _iter_standard_evidence_review" in step
    assert express.count("yield from _iter_standard_evidence_review") == 3
    assert step.index("yield from _iter_standard_evidence_review") < step.index(
        "extract_priorities("
    )
    assert express.rindex("yield from _iter_standard_evidence_review") < express.rindex(
        "extract_priorities("
    )


def test_step_route_sends_uploaded_documents_for_later_stage_review():
    from pathlib import Path

    html = (Path(__file__).resolve().parents[1] / "index.html").read_text(
        encoding="utf-8"
    )
    assert "stage===1 || reviewMode==='design'" in html



def test_review_prompt_finds_relevant_late_annex_and_keeps_package_source():
    prompt = build_review_prompt(
        1,
        "HEIS support is activated; check the Security Management Plan.",
        [
            {"name": "pad.pdf", "label": "PROJECT DOCUMENT",
             "raw_text": "A" * 80_000 + " HEIS request approved on 22 October 2024."},
            {"name": "context.pdf", "label": "CONTEXT DOCUMENT",
             "raw_text": "C" * 80_000},
            {"name": "escp.pdf", "label": "PACKAGE INSTRUMENT",
             "raw_text": "Action 4.4 Security Management Plan."},
        ],
    )

    assert "HEIS request approved on 22 October 2024" in prompt
    assert "Action 4.4 Security Management Plan." in prompt



def test_review_keeps_its_own_model_result(monkeypatch):
    import app

    response = json.dumps({"issues": [
        {"outcome": "needs confirmation", "segment_id": "p1",
         "replacement": "HEIS activation needs confirmation.",
         "reason": "The PAD records approval only."}
    ]})

    class FakeStream:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        @property
        def text_stream(self):
            return iter([response])

    class FakeMessages:
        def stream(self, **_kwargs):
            return FakeStream()

    class FakeClient:
        messages = FakeMessages()

    monkeypatch.setattr(app, "get_client", lambda: FakeClient())
    monkeypatch.setattr(
        app, "_stream_stage",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("shared stage stream must not handle review")
        ),
    )
    result = app._iter_standard_evidence_review(
        1, "HEIS is active.", [{"name": "pad.pdf", "raw_text": "HEIS approved."}],
        "assessment-1",
    )
    assert next(result).endswith("\n\n")
    while True:
        try:
            next(result)
        except StopIteration as done:
            corrected, issues = done.value
            break

    assert corrected == "HEIS activation needs confirmation."
    assert issues[0]["outcome"] == "needs confirmation"



def test_review_prompt_prioritizes_late_named_fact_over_repeated_early_matches():
    raw = ("Security Management Plan " * 4_000) + (
        "HEIS request approved on 22 October 2024."
    )
    prompt = build_review_prompt(
        1, "HEIS activation and Security Management Plan.",
        [{"name": "pad.pdf", "label": "PROJECT DOCUMENT", "raw_text": raw}],
    )
    assert "HEIS request approved on 22 October 2024" in prompt



def test_review_corrects_wrong_uploaded_name_and_invented_deadline():
    wrong_name = "20260923_public-honduras-escp-p181166.pdf"
    correct_name = "20260924_public-honduras-escp-p181166.pdf"
    raw = (
        "The ESCP requires notification to the TTL within five business days "
        f"[From: {wrong_name}].\n"
        "%%%JSON_START%%%"
        + json.dumps({"priorities": [{
            "actions": [{"guidance": "Notify the TTL within five business days."}],
            "source": f"[From: {wrong_name}]",
        }]})
        + "%%%JSON_END%%%"
    )
    response = json.dumps({"issues": [
        {"outcome": "contradicted or invalid source", "quote": wrong_name,
         "replacement": correct_name, "reason": "Actual uploaded filename differs."},
        {"outcome": "contradicted or invalid source",
         "quote": "Notify the TTL within five business days.",
         "replacement": (
             "Check the ESCP action E: notify the Association within 48 hours "
             "of learning of a qualifying project-related incident or accident."
         ),
         "reason": "Action E has a different recipient, clock and trigger."},
        {"outcome": "contradicted or invalid source",
         "quote": "requires notification to the TTL within five business days",
         "replacement": (
             "commits to notifying the Association within 48 hours of learning "
             "of a qualifying project-related incident or accident"
         ),
         "reason": "Action E has a different recipient, clock and trigger."},
    ]})

    corrected, _ = apply_review(raw, response)

    assert wrong_name not in corrected
    assert correct_name in corrected
    assert "five business days" not in corrected
    assert "the Association within 48 hours" in corrected
    assert json.loads(corrected.split("%%%JSON_START%%%")[1].split(
        "%%%JSON_END%%%")[0])["priorities"][0]["actions"][0]["guidance"].startswith(
            "Check the ESCP action E"
        )



def test_review_blocks_near_match_uploaded_filename_left_in_output():
    from fcv_evidence_review import validate_uploaded_names

    actual = "20260924_public-honduras-escp-p181166.pdf"
    wrong = "20260923_public-honduras-escp-p181166.pdf"

    with pytest.raises(EvidenceReviewError, match="uploaded filename"):
        validate_uploaded_names(f"Source: {wrong}", [actual])
    validate_uploaded_names(f"Source: {actual}", [actual])



def test_review_outcomes_are_returned_for_live_qa_inspection():
    from pathlib import Path

    source = (Path(__file__).resolve().parents[1] / "app.py").read_text(
        encoding="utf-8"
    )
    assert source.count("'evidence_review': _review_issues") >= 4



def test_review_prompt_uses_cited_public_context_without_promoting_site_claims():
    prompt = build_review_prompt(
        3,
        "National reporting suggests security risks; assess project corridor exposure.",
        [{"name": "pad.pdf", "label": "PROJECT DOCUMENT",
          "raw_text": "The PAD mentions illicit activities in the project area."}],
        public_research=(
            "Source: public report, 2025. Crime reported nationally, "
            "without corridor-level incident evidence."
        ),
    )
    assert "<public_research>" in prompt
    assert "Crime reported nationally" in prompt
    assert "not site-specific evidence" in prompt



def test_review_stage_timeout_labels_match_actual_budget():
    from pathlib import Path

    html = (Path(__file__).resolve().parents[1] / "index.html").read_text(
        encoding="utf-8"
    )
    assert "3:'13 minutes'" in html
    assert "const _stageTimeoutLabel=stage===1?'18':'13';" in html



def test_review_prompt_finds_late_title_case_place_and_number():
    prompt = build_review_prompt(
        1, "Violence in Choluteca requires a response within 48 hours.",
        [{"name": "pad.pdf", "label": "PROJECT DOCUMENT",
          "raw_text": "F" * 80_000 + "Choluteca corridor commitment: 48 hours."}],
    )
    assert "Choluteca corridor commitment: 48 hours." in prompt


def test_review_rejects_ambiguous_or_overlapping_corrections():
    repeated = "The plan was approved. Another plan was approved."
    issue = {"outcome": "needs confirmation", "quote": "approved",
             "replacement": "proposed", "reason": "Status unclear."}
    with pytest.raises(EvidenceReviewError, match="ambiguous"):
        apply_review(repeated, json.dumps({"issues": [issue]}))

    overlapping = {"issues": [
        {"outcome": "needs confirmation", "quote": "The plan was approved",
         "replacement": "Confirm plan approval", "reason": "Status unclear."},
        {"outcome": "needs confirmation", "quote": "approved",
         "replacement": "proposed", "reason": "Status unclear."},
    ]}
    with pytest.raises(EvidenceReviewError, match="overlap"):
        apply_review("The plan was approved.", json.dumps(overlapping))


def test_review_validates_source_names_with_spaces_and_office_extensions():
    from fcv_evidence_review import validate_uploaded_names

    for ext in ("pdf", "docx", "pptx", "txt"):
        actual = f"Honduras project source 2026.{ext}"
        wrong = f"Honduras project source 2025.{ext}"
        with pytest.raises(EvidenceReviewError, match="uploaded filename"):
            validate_uploaded_names(f"[From: {wrong}]", [actual])
        validate_uploaded_names(f"[From: {actual}]", [actual])


def test_standard_stream_hides_draft_chunks_and_keeps_connection_alive(monkeypatch):
    import app

    class FakeStream:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        @property
        def text_stream(self):
            return iter(["HEIS ", "is active."])

        def get_final_message(self):
            return type("Message", (), {"stop_reason": "end_turn"})()

    class FakeClient:
        messages = type("Messages", (), {"stream": lambda self, **_: FakeStream()})()

    monkeypatch.setattr(app, "get_client", lambda: FakeClient())
    events = list(app._stream_stage([{"role": "user", "content": "prompt"}],
                                    100, 1, reveal_chunks=False))
    assert all('"chunk"' not in event for event in events)
    assert app._stream_stage._last_result == "HEIS is active."


def test_express_review_failure_tracks_active_stage():
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    express = source.split("def run_express():", 1)[1].split("def _strip_html", 1)[0]
    assert "failed_stage = _active_stage" in express
    assert "_active_stage = 2" in express
    assert "_active_stage = 3" in express
    assert express.count("reveal_chunks=not _standard_review_s") == 3


def test_review_retries_unusable_correction_before_releasing_output(monkeypatch):
    import app

    responses = iter([
        json.dumps({"issues": [{"outcome": "needs confirmation",
                               "segment_id": "p1",
                               "replacement": "HEIS is active.",
                               "reason": "Approval only."}]}),
        json.dumps({"issues": [{"outcome": "needs confirmation",
                               "segment_id": "p1",
                               "replacement": "HEIS operation needs confirmation.",
                               "reason": "Approval only."}]}),
    ])

    class FakeStream:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        @property
        def text_stream(self):
            return iter([next(responses)])

    class FakeClient:
        messages = type("Messages", (), {"stream": lambda self, **_: FakeStream()})()

    monkeypatch.setattr(app, "get_client", lambda: FakeClient())
    stream = app._iter_standard_evidence_review(
        1, "HEIS is active.", [{"name": "pad.pdf", "raw_text": "HEIS approved."}],
        "assessment-retry",
    )
    while True:
        try:
            next(stream)
        except StopIteration as done:
            corrected, issues = done.value
            break
    assert corrected == "HEIS operation needs confirmation."
    assert len(issues) == 1


def test_review_rewrites_repeated_full_sentence_claims():
    sentence = "The project security management plan has been approved and is operating."
    raw = sentence + "\nAnother section: " + sentence
    review = {"issues": [{"outcome": "needs confirmation", "quote": sentence,
                          "replacement": "The plan's approval and operation need confirmation.",
                          "reason": "The PAD does not establish plan status."}]}
    corrected, _ = apply_review(raw, json.dumps(review))
    assert corrected.count("The plan's approval and operation need confirmation.") == 2
    assert sentence not in corrected


def test_indexed_review_targets_prose_and_stage3_fields_by_id():
    from fcv_evidence_review import index_output, apply_indexed_review

    original = (
        "HEIS is active.\n"
        "%%%JSON_START%%%"
        + json.dumps({"priorities": [{"gap": "Extortion has occurred at the corridor.",
                                      "concise": {"gap": "Extortion has occurred at the corridor."}}]})
        + "%%%JSON_END%%%"
    )
    segments = index_output(original)
    prose = next(item for item in segments if item["text"] == "HEIS is active.")
    gap = next(item for item in segments if item["text"] == "Extortion has occurred at the corridor.")
    response = json.dumps({"issues": [
        {"outcome": "needs confirmation", "segment_id": prose["id"],
         "replacement": "HEIS operation needs confirmation.", "reason": "PAD records approval only."},
        {"outcome": "qualified inference", "segment_id": gap["id"],
         "replacement": "Assess potential corridor extortion risk.",
         "reason": "No site event is documented."},
    ]})
    corrected, issues = apply_indexed_review(original, response, segments)
    assert "HEIS operation needs confirmation." in corrected
    data = json.loads(corrected.split("%%%JSON_START%%%", 1)[1].split("%%%JSON_END%%%", 1)[0])
    assert data["priorities"][0]["gap"] == "Assess potential corridor extortion risk."
    assert data["priorities"][0]["concise"]["gap"] == "Assess potential corridor extortion risk."
    assert len(issues) == 2


def test_indexed_review_rejects_invalid_id_without_releasing_text():
    from fcv_evidence_review import index_output, apply_indexed_review

    raw = "HEIS is active."
    response = json.dumps({"issues": [{"outcome": "needs confirmation",
        "segment_id": "p999", "replacement": "Confirm HEIS status.",
        "reason": "PAD approval only."}]})
    with pytest.raises(EvidenceReviewError, match="segment"):
        apply_indexed_review(raw, response, index_output(raw))


def test_review_prompt_uses_numbered_editable_segments():
    prompt = build_review_prompt(1, "HEIS is active.",
                                 [{"name": "pad.pdf", "raw_text": "HEIS approved."}])
    assert '"id": "p1"' in prompt
    assert '"text": "HEIS is active."' in prompt
    assert "segment_id" in prompt
    assert '"quote":"exact text"' not in prompt


def test_indexed_review_never_exposes_machine_metadata_as_editable_segment():
    from fcv_evidence_review import index_output

    raw = ("A project claim.\n%%%DOC_CHECKS_START%%%\n"
           "ipf_component: false\n%%%DOC_CHECKS_END%%%\n"
           "A second project claim.")
    segments = index_output(raw)
    assert [item["text"] for item in segments] == [
        "A project claim.", "A second project claim."
    ]


def test_review_prompt_prioritizes_site_and_commitment_errors():
    prompt = build_review_prompt(1, "Gangs operate at this project corridor.",
                                 [{"name": "pad.pdf", "raw_text": "Illicit activities in the project area."}])
    assert "First prioritize" in prompt
    assert "site-specific" in prompt
