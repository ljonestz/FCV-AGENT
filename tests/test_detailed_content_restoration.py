"""Keep the detailed technical contract independent of management brevity."""

import app


def standard_prompt():
    rendered = app.DEFAULT_PROMPTS["3"].format(
        doc_type="PAD", instrument_guidance="Instrument guidance",
        minimum_reference_set="Minimum references", playbook_guidance="Playbook",
        process_guidance="Process", regime_header="Regime",
        seash_gender_card_guidance="Safeguards", temporal_guardrail="Temporal",
        timing_emphasis="Timing",
    )
    return app.append_core_concise_stage3_contract(rendered, "PAD", {}, "design", [])


def test_detailed_actions_retain_original_document_focused_scope_and_depth():
    prompt = standard_prompt()
    assert "ACTIONS: Provide 2-4 specific actions to address this gap." in prompt
    assert "Do NOT write implementation procedures, operational protocols" in prompt
    assert "Each action = one thing to change in the document." in prompt
    assert "`actions` array contains 2-4 objects" in prompt
    assert "`guidance` (2-4 sentences)" in prompt
    assert "`suggested_language` (2-3 sentences" in prompt


def test_detailed_strengths_keep_original_paired_risk_discussion():
    prompt = standard_prompt()
    assert "3-4 concrete strengths actually present in the project document." in prompt
    assert "For the top 3-4 most significant project strengths" in prompt.replace("\u2013", "-")
    assert "zero to three evidenced strengths" in prompt


def test_management_brevity_is_explicitly_limited_to_concise_fields():
    prompt = standard_prompt()
    assert "only to concise_readout and priority.concise" in prompt
    assert "Do not shorten the detailed narrative or canonical priority fields" in prompt
    assert "not the detailed actions array" in prompt
    assert "bold first sentence" in prompt
    assert "no em-dash" in prompt


def test_summary_uses_same_findings_and_canonical_actions():
    prompt = standard_prompt()
    for expected in (
        "Every Summary gap must reflect its canonical detailed gap",
        "Each concise how action must condense an action in that same priority.actions",
        "Its leading action summarizes",
        "Summary strength must also appear in the detailed Strengths discussion",
        "same qualification",
        "FCV Sensitivity Summary, FCV Responsiveness Summary",
        "two-way FCV Risk",
    ):
        assert expected in prompt
