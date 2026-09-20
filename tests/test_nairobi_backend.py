"""Contract tests for the standard FCV Nairobi management brief backend."""

import copy
import json

import pytest

import app
from app import extract_priorities


_CYCLE = {
    "primary_label": "At concept stage",
    "primary_text": "Commit the design choice in the PCN.",
    "secondary_label": "During preparation",
    "secondary_text": "Translate the commitment into implementation arrangements.",
}


def _priority(number: int) -> dict:
    title = f"Protect access in Nairobi wards {number}"
    return {
        "title": title,
        "fcv_dimension": "Inclusion",
        "tag": "[S]",
        "refresh_shift": "Shift B: Differentiate",
        "risk_level": "High",
        "the_gap": (
            f"Access arrangements for Nairobi wards {number} do not yet identify "
            "how the project will reach excluded households."
        ),
        "why_it_matters": (
            "Unclear access arrangements can delay delivery and deepen exclusion "
            "in communities that already distrust public services."
        ),
        "actions": [
            {
                "document_element": "Implementation Arrangements",
                "guidance": "Define the access trigger and responsible owner for Nairobi wards.",
                "suggested_language": "The project will define an access trigger for Nairobi wards.",
            }
        ],
        "who_acts": "TTL; PIU",
        "when": "Preparation",
        "action_timing": "flag-for-preparation",
        "resources": "Minimal (existing budget)",
        "pad_sections": "Implementation Arrangements; SORT",
        "implementation_note": "Confirm the arrangement during preparation.",
        "cpf_alignment": None,
        "rra_driver_alignment": None,
        "country_category_relevance": "Nairobi access constraints make inclusion material.",
        "change_type": "",
        "restructuring_level": "",
        "priority_scope": "",
        "project_cycle": copy.deepcopy(_CYCLE),
        "governance_level": None,
        "authority_basis": "reviewer_judgment",
        "concise": {
            "title": title,
            "why": "Nairobi access gaps can delay delivery and exclude households.",
            "how": ["Define the access trigger and owner."],
            "suggested_wording": {
                "document_element": "Implementation Arrangements",
                "text": "The project will define an access trigger for Nairobi wards.",
            },
            "project_cycle": copy.deepcopy(_CYCLE),
        },
    }


def _readout(*, legacy: bool = False) -> dict:
    if legacy:
        overview = " ".join(["The operation recognizes access and legitimacy risks."] * 24)
        strengths = [
            {"title": "Context awareness", "text": "The design identifies Nairobi access pressures."},
            {"title": "Feedback", "text": "The design includes feedback channels."},
            {"title": "Adaptation", "text": "The design permits bounded adjustment."},
        ]
    else:
        overview = " ".join(
            [
                "The operation links its Nairobi service investments to an FCV context, "
                "but access and delivery dependencies remain partly unresolved."
            ]
            * 3
        )
        strengths = [
            {"title": "Context awareness", "text": "The design identifies Nairobi access pressures."},
            {"title": "Feedback", "text": "The design includes feedback channels."},
        ]
    return {
        "headline": "The project recognizes FCV risks while key access choices remain open.",
        "overview": overview,
        "strengths": strengths,
        "strengths_transition": "These strengths provide a basis for focused action.",
        "priorities_transition": "The priorities address the most material delivery risks.",
        "closing": "The team can refine these choices at the current project gate.",
    }


def _payload(count: int = 1, *, legacy: bool = False) -> dict:
    priorities = [_priority(number) for number in range(1, count + 1)]
    if legacy:
        # Legacy concise cards remain valid on the standard parser.
        for priority in priorities:
            priority["concise"]["how"] = [
                "Define the access trigger and owner.",
                "Record the response in the implementation arrangements.",
            ]
    return {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "The operation recognizes material access risks.",
        "responsiveness_summary": "Low responsiveness reflects limited direct FCV transformation scope.",
        "risk_exposure": {"risks_to": "Insecurity may disrupt delivery.", "risks_from": "Unequal access may deepen exclusion."},
        "concise_readout": _readout(legacy=legacy),
        "priorities": priorities,
    }


def _wrapped(payload: dict) -> str:
    return "%%%JSON_START%%%\n" + json.dumps(payload) + "\n%%%JSON_END%%%"


@pytest.mark.parametrize("count", [1, 2, 5])
def test_standard_route_admits_one_to_five_material_priorities(count):
    result = extract_priorities(_wrapped(_payload(count)), active_lens_ids=[])

    assert result["error"] is False
    assert len(result["priorities"]) == count
    assert result["concise_readout"]["strengths"]
    assert all(1 <= len(priority["concise"]["how"]) <= 2 for priority in result["priorities"])


def test_standard_route_rejects_more_than_five_without_truncating():
    result = extract_priorities(_wrapped(_payload(6)), active_lens_ids=[])

    assert result["error"] is True
    assert result["priorities"] == []
    assert "five" in result["message"].lower()


def test_standard_route_accepts_legacy_concise_bounds():
    result = extract_priorities(
        _wrapped(_payload(2, legacy=True)), active_lens_ids=[]
    )

    assert result["error"] is False
    assert 150 <= len(result["concise_readout"]["overview"].split()) <= 200
    assert len(result["concise_readout"]["strengths"]) == 3
    assert all(len(priority["concise"]["how"]) == 2 for priority in result["priorities"])


@pytest.mark.parametrize("prompt_key", ["3", "impl_3"])
def test_standard_rendered_prompt_uses_materiality_contract_without_old_quota(prompt_key):
    rendered = app.DEFAULT_PROMPTS[prompt_key].format(
        doc_type="PID",
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
        rendered, "PID", {"processing_track": "standard"}, "design", []
    )

    lowered = prompt.lower()
    for phrase in ("pdo relevance", "beneficiary scope", "severity of harm", "delivery dependenc"):
        assert phrase in lowered
    assert "1 to 5" in lowered
    assert "generate between 4 and 5 strategic priorities" not in lowered
    assert "4-5 priorities total" not in lowered
    assert "actions: provide 2-4 specific actions" not in lowered
    assert "budget is informative" in lowered
    assert "low responsiveness" in lowered
    assert "not an obligation" in lowered


def test_specialist_stage3_prompt_keeps_existing_contract_untouched():
    prompt = app.append_core_concise_stage3_contract(
        app.DEFAULT_PROMPTS["3"],
        "PID",
        {"processing_track": "standard"},
        "design",
        [{"id": "climate"}],
    )
    assert prompt == app.DEFAULT_PROMPTS["3"]


def _export_payload(**overrides):
    payload = _payload(1)
    payload.update({"doc_type": "PID", "active_lenses": [], "format": "html"})
    payload.update(overrides)
    return payload


def test_management_brief_route_returns_html_and_docx_attachments():
    client = app.app.test_client()
    html_response = client.post(
        "/api/download-management-brief", json=_export_payload(format="html")
    )
    docx_response = client.post(
        "/api/download-management-brief", json=_export_payload(format="docx")
    )

    assert html_response.status_code == 200
    assert "text/html" in html_response.content_type
    assert "FCV management brief" in html_response.get_data(as_text=True)
    assert docx_response.status_code == 200
    assert "wordprocessingml.document" in docx_response.content_type
    assert docx_response.data[:2] == b"PK"


@pytest.mark.parametrize(
    "payload, status",
    [
        (_export_payload(active_lenses=["climate"]), 400),
        (_export_payload(format="pdf"), 400),
        (_export_payload(format=[]), 400),
        (_export_payload(format={}), 400),
        (_export_payload(concise_readout=None), 422),
        ({"format": "html"}, 422),
    ],
)
def test_management_brief_route_rejects_invalid_export_requests(payload, status):
    response = app.app.test_client().post("/api/download-management-brief", json=payload)
    assert response.status_code == status


def test_management_brief_route_rejects_non_object_json_payload():
    response = app.app.test_client().post(
        "/api/download-management-brief",
        data=json.dumps([_export_payload()]),
        content_type="application/json",
    )
    assert response.status_code == 400


@pytest.mark.parametrize("words", [40, 80, 100, 150, 200])
def test_standard_concise_admission_accepts_short_and_legacy_lengths(words):
    payload = _payload()
    payload["concise_readout"]["overview"] = " ".join(["Evidence"] * words)
    payload["concise_readout"]["strengths"] = []
    result = extract_priorities(_wrapped(payload), active_lens_ids=[])
    assert result["concise_readout"] is not None
    assert result["concise_readout"]["strengths"] == []


@pytest.mark.parametrize("instrument", ["IPF", "PforR", "DPO"])
@pytest.mark.parametrize("regime", ["legacy", "new_model"])
def test_final_standard_prompt_removes_quotas_but_keeps_instrument_safeguards(instrument, regime):
    rendered = app.DEFAULT_PROMPTS["3"].format(
        doc_type="PAD", instrument_guidance="Instrument guidance",
        minimum_reference_set=app.build_minimum_reference_block(regime, "ESF_ESS1_TO_ESS10", instrument),
        playbook_guidance="Playbook", process_guidance="Process", regime_header="Regime",
        seash_gender_card_guidance=app.get_seash_gender_card_guidance(instrument),
        temporal_guardrail="Temporal", timing_emphasis="Timing",
    )
    prompt = app.append_core_concise_stage3_contract(rendered, "PAD", {}, "design", [])
    for obsolete in ("4-5 priorities", "between 4 and 5", "card is mandatory", "must each be referenced at least once", "at least one priority must reference", "array contains 2-4 objects"):
        assert obsolete not in prompt, obsolete
    assert "SEA/SH" in prompt
    assert "gender_fcv_flag" in prompt
    expected = {"IPF": "ESS2", "PforR": "PAP", "DPO": "PSIA"}[instrument]
    assert expected in prompt
    assert "Distinguish confirmed policy obligations from advisory suggestions" in prompt


def test_standard_stage2_removes_priority_quota_and_lens_prompt_is_unchanged():
    prompt = app.DEFAULT_PROMPTS["2"]
    standard = app.append_standard_fcv_stage_context(prompt, 2, [])
    assert "At least 3 of the 4-5" not in standard
    assert "implementation dependencies" in standard
    assert app.append_standard_fcv_stage_context(prompt, 2, [{"id": "climate"}]) == prompt
