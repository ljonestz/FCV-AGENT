"""Unit tests for extract_priorities() — JSON parsing path.

Run with: python -m pytest tests/test_extract_priorities.py -v
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import app as app_module
from app import extract_priorities


# ── Fixtures ──────────────────────────────────────────────────────────────────

VALID_JSON_FIXTURE = '''Some narrative text here.
%%%JSON_START%%%
{
  "fcv_rating": "Adequate",
  "fcv_responsiveness_rating": "Low",
  "sensitivity_summary": "The project has adequate sensitivity.",
  "responsiveness_summary": "Responsiveness is limited.",
  "risk_exposure": {
    "risks_to": "Insecurity in the north of Karamoja poses delivery risk.",
    "risks_from": "Benefit capture risk in Moroto district."
  },
  "priorities": [
    {
      "number": 1,
      "title": "Priority 1 · Strengthen targeting in Karamoja",
      "dimension": "Inclusion",
      "tag": "[S+R]",
      "risk_level": "High",
      "the_gap": "Beneficiary selection criteria in Karamoja district do not account for IDP households in Moroto.",
      "why_it_matters": "Exclusion of IDPs risks deepening grievances in Kotido. Tagged [S+R] per Pillar 1.",
      "recommendation": "Revise the Project Operations Manual targeting criteria to explicitly include IDP households in Karamoja and Moroto sub-counties.",
      "who_acts": "TTL",
      "when": "Before appraisal",
      "resources": "Minimal"
    },
    {
      "number": 2,
      "title": "Priority 2 · Embed adaptive management in Gulu",
      "dimension": "Resilience",
      "tag": "[S]",
      "risk_level": "Medium",
      "the_gap": "No CERC component exists in the current design for Gulu region.",
      "why_it_matters": "Without adaptive provisions the project cannot respond to sudden insecurity in Acholi sub-region.",
      "recommendation": "Add a zero-dollar CERC to Annex 2 to allow rapid reallocation in crisis.",
      "who_acts": "TTL",
      "when": "At design stage",
      "resources": "Minimal"
    },
    {
      "number": 3,
      "title": "Priority 3 · Strengthen GRM in Kotido",
      "dimension": "Institutional Legitimacy",
      "tag": "[S]",
      "risk_level": "Low",
      "the_gap": "GRM not adapted for low-literacy communities in Kotido and Abim districts.",
      "why_it_matters": "Inaccessible GRM prevents complaint filing by marginalised Karamojong pastoralists.",
      "recommendation": "Add oral complaint intake and mobile GRM officers to the Stakeholder Engagement Plan for Kotido.",
      "who_acts": "PIU",
      "when": "During implementation",
      "resources": "Moderate"
    },
    {
      "number": 4,
      "title": "Priority 4 · Conflict-sensitive M&E in Lira",
      "dimension": "Security",
      "tag": "[S]",
      "risk_level": "Medium",
      "the_gap": "No conflict indicators in the results framework for Lira and Apac districts.",
      "why_it_matters": "Without conflict tracking in Northern Uganda harm cannot be detected early.",
      "recommendation": "Add two disaggregated conflict-sensitive indicators to the results framework for Lira district.",
      "who_acts": "TTL",
      "when": "Before appraisal",
      "resources": "Minimal"
    }
  ]
}
%%%JSON_END%%%
'''

MALFORMED_JSON_FIXTURE = '''Some text.
%%%JSON_START%%%
{ invalid json content here }
%%%JSON_END%%%
'''

NO_JSON_BLOCK_FIXTURE = '''Stage 4 output with no JSON block at all.
%%%PRIORITY_START%%%
TITLE: Priority 1 · Old format
%%%PRIORITY_END%%%
'''

def _make_vague_fixture():
    """Build a valid JSON fixture where priority 0 has generic (vague) language."""
    data = json.loads(re.search(
        r'%%%JSON_START%%%(.*?)%%%JSON_END%%%', VALID_JSON_FIXTURE, re.DOTALL
    ).group(1))
    data['priorities'][0]['the_gap'] = 'the project lacks adequate stakeholder engagement.'
    data['priorities'][0]['recommendation'] = 'consider improving the approach to community outreach.'
    return f'%%%JSON_START%%%\n{json.dumps(data)}\n%%%JSON_END%%%\n'


def _make_citation_fixture(extra_cite):
    data = json.loads(re.search(
        r'%%%JSON_START%%%(.*?)%%%JSON_END%%%', VALID_JSON_FIXTURE, re.DOTALL
    ).group(1))
    data['priorities'][0]['the_gap'] += f' {extra_cite}'
    return f'%%%JSON_START%%%\n{json.dumps(data)}\n%%%JSON_END%%%\n'


# ── Happy-path tests ──────────────────────────────────────────────────────────

class TestExtractPrioritiesJsonPath:

    def test_valid_json_returns_dict(self):
        result = extract_priorities(VALID_JSON_FIXTURE)
        assert isinstance(result, dict)

    def test_no_error_flag(self):
        result = extract_priorities(VALID_JSON_FIXTURE)
        assert result.get('error') is False

    def test_returns_four_priorities(self):
        result = extract_priorities(VALID_JSON_FIXTURE)
        assert len(result['priorities']) == 4

    def test_priority_has_all_required_fields(self):
        result = extract_priorities(VALID_JSON_FIXTURE)
        pr = result['priorities'][0]
        for field in ['title', 'dimension', 'tag', 'risk_level', 'the_gap',
                      'why_it_matters', 'recommendation', 'who_acts', 'when', 'resources']:
            assert field in pr, f"Missing field: {field}"

    def test_top_level_metadata_present(self):
        result = extract_priorities(VALID_JSON_FIXTURE)
        assert result['fcv_rating'] == 'Adequate'
        assert result['fcv_responsiveness_rating'] == 'Low'
        assert result['sensitivity_summary']
        assert result['responsiveness_summary']

    def test_risk_exposure_mapped_correctly(self):
        result = extract_priorities(VALID_JSON_FIXTURE)
        assert result['risk_exposure']['risks_to']
        assert result['risk_exposure']['risks_from']

    def test_body_field_built_from_components(self):
        result = extract_priorities(VALID_JSON_FIXTURE)
        pr = result['priorities'][0]
        assert pr['the_gap'] in pr['body']
        assert pr['recommendation'] in pr['body']

    def test_specific_priority_has_no_specificity_warning(self):
        """All priorities name specific places — none should be flagged."""
        result = extract_priorities(VALID_JSON_FIXTURE)
        for pr in result['priorities']:
            assert pr['specificity_warning'] is False, (
                f"Unexpected specificity warning on: {pr['title']}"
            )

    def test_country_category_relevance_optional(self):
        """country_category_relevance should be present on each priority (may be None or empty string)."""
        result = extract_priorities(VALID_JSON_FIXTURE)
        for pr in result['priorities']:
            assert 'country_category_relevance' in pr, (
                f"Missing country_category_relevance on priority: {pr.get('title', '?')}"
            )

    def test_rra_driver_alignment_optional(self):
        """rra_driver_alignment should be present on each priority (may be None or empty string)."""
        result = extract_priorities(VALID_JSON_FIXTURE)
        for pr in result['priorities']:
            assert 'rra_driver_alignment' in pr, (
                f"Missing rra_driver_alignment on priority: {pr.get('title', '?')}"
            )


# ── Error-path tests ──────────────────────────────────────────────────────────

class TestExtractPrioritiesErrorPath:

    def test_malformed_json_returns_error_dict(self):
        result = extract_priorities(MALFORMED_JSON_FIXTURE)
        assert isinstance(result, dict)
        assert result.get('error') is True

    def test_malformed_json_error_has_message(self):
        result = extract_priorities(MALFORMED_JSON_FIXTURE)
        assert 'message' in result
        assert len(result['message']) > 0

    def test_malformed_json_has_empty_priorities(self):
        result = extract_priorities(MALFORMED_JSON_FIXTURE)
        assert result['priorities'] == []

    def test_no_json_block_returns_error_dict(self):
        result = extract_priorities(NO_JSON_BLOCK_FIXTURE)
        assert result.get('error') is True

    def test_error_message_user_friendly(self):
        result = extract_priorities(MALFORMED_JSON_FIXTURE)
        assert 're-run' in result['message'].lower()


# ── Specificity check tests ───────────────────────────────────────────────────

class TestSpecificityCheck:

    def test_vague_text_flagged(self):
        fixture = _make_vague_fixture()
        result = extract_priorities(fixture)
        assert result['priorities'][0]['specificity_warning'] is True

    def test_specific_text_not_flagged(self):
        result = extract_priorities(VALID_JSON_FIXTURE)
        assert result['priorities'][0]['specificity_warning'] is False


# ── Citation check tests ──────────────────────────────────────────────────────

class TestCitationCheck:

    def test_org_whitelist_not_flagged(self):
        fixture = _make_citation_fixture('[From: ACLED data]')
        result = extract_priorities(fixture, uploaded_doc_names=[])
        unverified = result['priorities'][0]['unverified_citations']
        assert not any('ACLED' in c for c in unverified)

    def test_unknown_citation_flagged(self):
        fixture = _make_citation_fixture('[From: Uganda RRA 2023]')
        result = extract_priorities(fixture, uploaded_doc_names=[])
        unverified = result['priorities'][0]['unverified_citations']
        assert any('Uganda RRA 2023' in c for c in unverified)

    def test_uploaded_doc_name_not_flagged(self):
        fixture = _make_citation_fixture('[From: Uganda RRA 2023]')
        result = extract_priorities(fixture, uploaded_doc_names=['Uganda RRA 2023'])
        unverified = result['priorities'][0]['unverified_citations']
        assert len(unverified) == 0

    def test_training_knowledge_not_flagged(self):
        fixture = _make_citation_fixture('[From: training knowledge]')
        result = extract_priorities(fixture)
        unverified = result['priorities'][0]['unverified_citations']
        assert len(unverified) == 0


# ── FCS classification regression tests ─────────────────────────────────────

from app import classify_country

class TestClassifyCountry:

    def test_short_name_match(self):
        """Short name that exactly matches FCS list entry."""
        result = classify_country("Ethiopia")
        assert result['category'] is not None, "Ethiopia should match the FCS list"

    def test_long_form_name_match(self):
        """Long-form name where FCS entry is a substring of the extracted name."""
        result = classify_country("Federal Democratic Republic of Ethiopia")
        assert result['category'] is not None, \
            "Long-form 'Federal Democratic Republic of Ethiopia' should match via bidirectional check"

    def test_non_fcs_country(self):
        """Country not on FCS list returns no deterministic match."""
        result = classify_country("Canada")
        assert result['category'] is None, "Canada should not match the FCS list"

    def test_case_insensitive(self):
        """Matching should be case-insensitive."""
        result = classify_country("ethiopia")
        assert result['category'] is not None, "Lowercase 'ethiopia' should still match"


# ── FCV_INSTRUMENT_CALIBRATION content tests ─────────────────────────────────

from background_docs import FCV_INSTRUMENT_CALIBRATION

class TestInstrumentCalibrationContent:

    def test_cerc_calibration_block_present(self):
        assert 'CERC — FCV Calibration' in FCV_INSTRUMENT_CALIBRATION

    def test_cerc_emergency_redirect_risk(self):
        assert 'not usually advised for emergency operations' in FCV_INSTRUMENT_CALIBRATION

    def test_cerc_op730_trigger_caveat(self):
        assert 'OPCS legal and operational clearance' in FCV_INSTRUMENT_CALIBRATION

    def test_cerc_effectiveness_qualified_as_practitioner(self):
        assert 'practitioner experience' in FCV_INSTRUMENT_CALIBRATION

    def test_pforr_calibration_block_present(self):
        assert 'PforR — FCV Calibration' in FCV_INSTRUMENT_CALIBRATION

    def test_pforr_iva_access_risk(self):
        assert 'IVA' in FCV_INSTRUMENT_CALIBRATION

    def test_pforr_op730_incompatibility(self):
        assert 'strongly constrained rather than categorically barred' in FCV_INSTRUMENT_CALIBRATION

    def test_mpa_calibration_block_present(self):
        assert 'MPA — FCV Calibration' in FCV_INSTRUMENT_CALIBRATION

    def test_mpa_phase_financing_not_guaranteed(self):
        assert 'NOT guaranteed' in FCV_INSTRUMENT_CALIBRATION


# ── action_timing enum tests ─────────────────────────────────────────────────

def _make_timing_fixture(timing_value: str) -> str:
    """Return a minimal valid Stage 3 output with the given action_timing value."""
    priority = {
        "number": 1,
        "title": "Priority 1 · Test priority in Karamoja",
        "fcv_dimension": "Inclusion",
        "tag": "[S]",
        "refresh_shift": "Shift A: Anticipate",
        "risk_level": "High",
        "the_gap": "Gap in Moroto district targeting.",
        "why_it_matters": "Exclusion of IDPs in Kotido risks grievance.",
        "actions": [{"document_element": "PAD Annex 2", "guidance": "Add IDP targeting criteria.", "suggested_language": ""}],
        "who_acts": "TTL",
        "when": "Preparation",
        "action_timing": timing_value,
        "resources": "Minimal (existing budget)",
        "pad_sections": "Annex 2",
        "country_category_relevance": "Relevant in conflict-affected context.",
        "implementation_note": "Address at design stage.",
        "cpf_alignment": None
    }
    payload = {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "Adequate sensitivity.",
        "responsiveness_summary": "Low responsiveness.",
        "risk_exposure": {"risks_to": "Insecurity risk.", "risks_from": "Elite capture risk."},
        "priorities": [priority]
    }
    return f"Narrative.\n%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%"


class TestActionTiming:

    def test_flag_for_preparation_accepted(self):
        result = extract_priorities(_make_timing_fixture('flag-for-preparation'))
        assert result['priorities'][0]['action_timing'] == 'flag-for-preparation'

    def test_required_before_appraisal_accepted(self):
        result = extract_priorities(_make_timing_fixture('required-before-appraisal'))
        assert result['priorities'][0]['action_timing'] == 'required-before-appraisal'

    def test_required_before_board_accepted(self):
        result = extract_priorities(_make_timing_fixture('required-before-board'))
        assert result['priorities'][0]['action_timing'] == 'required-before-board'

    def test_next_series_accepted(self):
        result = extract_priorities(_make_timing_fixture('next-series'))
        assert result['priorities'][0]['action_timing'] == 'next-series'

    def test_supervision_accepted(self):
        result = extract_priorities(_make_timing_fixture('supervision'))
        assert result['priorities'][0]['action_timing'] == 'supervision'

    def test_pre_appraisal_remapped_to_required_before_appraisal(self):
        """Backward compat: old 'pre-appraisal' value from cached sessions maps to new name."""
        result = extract_priorities(_make_timing_fixture('pre-appraisal'))
        assert result['priorities'][0]['action_timing'] == 'required-before-appraisal'

    def test_invalid_timing_nulled(self):
        result = extract_priorities(_make_timing_fixture('invalid-value'))
        assert result['priorities'][0]['action_timing'] is None

    def test_empty_timing_nulled(self):
        result = extract_priorities(_make_timing_fixture(''))
        assert result['priorities'][0]['action_timing'] is None


def test_lens_provenance_is_filtered_bounded_and_has_no_type_quota():
    fixture = _make_timing_fixture('supervision')
    payload = json.loads(re.search(
        r'%%%JSON_START%%%(.*?)%%%JSON_END%%%', fixture, re.DOTALL
    ).group(1))
    payload['priorities'][0]['lens_ids'] = ['climate', 'invented', 'climate']
    payload['priorities'][0]['lens_relevance'] = 'r' * 700
    payload['priorities'][0]['priority_type'] = 'climate'
    wrapped = f"%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%"

    result = extract_priorities(wrapped, active_lens_ids=['climate'])
    priority = result['priorities'][0]

    assert priority['lens_ids'] == ['climate']
    assert len(priority['lens_relevance']) == 500
    assert 'priority_type' not in priority


def test_active_lens_output_is_capped_at_five_priorities_only():
    fixture = _make_timing_fixture('supervision')
    payload = json.loads(re.search(
        r'%%%JSON_START%%%(.*?)%%%JSON_END%%%', fixture, re.DOTALL
    ).group(1))
    payload['priorities'] = [
        {**payload['priorities'][0], 'title': f'Priority {index + 1}'}
        for index in range(6)
    ]
    wrapped = f"%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%"

    active = extract_priorities(wrapped, active_lens_ids=['climate'])
    core_only = extract_priorities(wrapped)

    payload['priorities'].append({
        **payload['priorities'][0],
        'title': 'Mandatory SEA/SH standalone safeguard',
    })
    with_exception = extract_priorities(
        f"%%%JSON_START%%%\n{json.dumps(payload)}\n%%%JSON_END%%%",
        active_lens_ids=['climate'],
    )

    assert len(active['priorities']) == 5
    assert len(core_only['priorities']) == 6
    assert len(with_exception['priorities']) == 6
    assert with_exception['priorities'][-1]['title'] == (
        'Mandatory SEA/SH standalone safeguard'
    )


def test_extract_priorities_captures_wider_fcv_context():
    text = (
        "%%%JSON_START%%%"
        '{"fcv_rating":"Moderate","fcv_responsiveness_rating":"Moderate",'
        '"sensitivity_summary":"s","responsiveness_summary":"r",'
        '"risk_exposure":{"risks_to":"some risk","risks_from":"some risk"},'
        '"wider_fcv_context":"Reliance on contested state structures is a non-climate FCV risk.",'
        '"priorities":[{"title":"Test priority in Karamoja","fcv_dimension":"Inclusion",'
        '"tag":"[S]","risk_level":"High","the_gap":"Gap in Kotido district.","why_it_matters":"Why.",'
        '"actions":[],"who_acts":"TTL","when":"Before appraisal","resources":"Minimal",'
        '"action_timing":"required-before-appraisal"}]}'
        "%%%JSON_END%%%"
    )
    result = extract_priorities(text)
    assert result["wider_fcv_context"].startswith("Reliance on contested")


def test_extract_priorities_wider_fcv_defaults_none():
    text = (
        "%%%JSON_START%%%"
        '{"fcv_rating":"Moderate",'
        '"priorities":[{"title":"Test priority in Karamoja","fcv_dimension":"Inclusion",'
        '"tag":"[S]","risk_level":"High","the_gap":"Gap in Kotido.","why_it_matters":"Why.",'
        '"actions":[],"who_acts":"TTL","when":"Before appraisal","resources":"Minimal",'
        '"action_timing":"required-before-appraisal"}]}'
        "%%%JSON_END%%%"
    )
    assert extract_priorities(text).get("wider_fcv_context") is None


# ── policy_status and specialist_referral field tests ────────────────────────

def _wrap_priorities(priorities_json):
    return (
        "%%%JSON_START%%%"
        '{"fcv_rating":"Moderate","fcv_responsiveness_rating":"Moderate",'
        '"sensitivity_summary":"s","responsiveness_summary":"r",'
        '"risk_exposure":{"risks_to":[],"risks_from":[]},'
        '"priorities":[' + priorities_json + "]}"
        "%%%JSON_END%%%"
    )


def test_priority_policy_status_and_referral_parse():
    pr = (
        '{"title":"Negotiate water allocation in Baidoa","fcv_dimension":"Inclusion",'
        '"tag":"[S]","refresh_shift":"Shift A: Anticipate","action_timing":"required-before-appraisal",'
        '"risk_level":"High","the_gap":"Gap in Baidoa district.","why_it_matters":"Why it matters.",'
        '"actions":[{"document_element":"PAD","guidance":"Add targeting criteria.","suggested_language":"y"}],'
        '"who_acts":"TTL","when":"Before appraisal","resources":"Minimal","pad_sections":"Annex 2",'
        '"implementation_note":"n","cpf_alignment":null,'
        '"policy_status":"document_commitment",'
        '"specialist_referral":{"required":true,"route":"Task Team E&S specialist","reason":"Possible conflict with ESCP action on water use."}}'
    )
    result = extract_priorities(_wrap_priorities(pr))
    p = result["priorities"][0]
    assert p["policy_status"] == "document_commitment"
    assert p["specialist_referral"]["route"] == "Task Team E&S specialist"
    assert p["specialist_referral"]["required"] is True


def test_priority_policy_status_invalid_defaults_not_determined():
    pr = (
        '{"title":"Strengthen committees in Kismayo","fcv_dimension":"Inclusion",'
        '"tag":"[R]","refresh_shift":"Shift A: Anticipate","action_timing":"supervision",'
        '"risk_level":"High","the_gap":"Gap in Kismayo.","why_it_matters":"Why.",'
        '"actions":[{"document_element":"PAD","guidance":"x","suggested_language":"y"}],'
        '"who_acts":"TTL","when":"now","resources":"Minimal","pad_sections":"S",'
        '"implementation_note":"n","cpf_alignment":null,'
        '"policy_status":"totally_made_up","specialist_referral":{"route":"NotARealRoute","reason":""}}'
    )
    result = extract_priorities(_wrap_priorities(pr))
    p = result["priorities"][0]
    assert p["policy_status"] == "not_determined"
    assert p["specialist_referral"] is None


def test_priority_policy_status_absent_defaults():
    pr = (
        '{"title":"Map exclusion risk in Gedo","fcv_dimension":"Inclusion",'
        '"tag":"[S]","refresh_shift":"Shift A: Anticipate","action_timing":"supervision",'
        '"risk_level":"Low","the_gap":"Gap in Gedo district.","why_it_matters":"Why.",'
        '"actions":[{"document_element":"PAD","guidance":"x","suggested_language":"y"}],'
        '"who_acts":"TTL","when":"now","resources":"Minimal","pad_sections":"S",'
        '"implementation_note":"n","cpf_alignment":null}'
    )
    p = extract_priorities(_wrap_priorities(pr))["priorities"][0]
    assert p["policy_status"] == "not_determined"
    assert p["specialist_referral"] is None


# ── Task 1: Graceful per-priority climate_links gate ─────────────────────────

def _stage3_block(priorities):
    payload = {
        "fcv_rating": "Moderate", "fcv_responsiveness_rating": "Moderate",
        "sensitivity_summary": "s", "responsiveness_summary": "r",
        "risk_exposure": {"risks_to": "x", "risks_from": "y"},
        "priorities": priorities,
    }
    return "%%%JSON_START%%%" + json.dumps(payload) + "%%%JSON_END%%%"


def _climate_diag_for_test():
    return {"lenses": [{
        "lens_id": "climate", "applicability": "material",
        "materiality_level": "high", "materiality_summary": "m",
        "integration_level": "partly_integrated", "integration_summary": "ok",
        "reflections": [{"question_key": "cq1_interaction", "title": "t",
                         "status_cue": "ok", "text": "grounded"}],
        "interaction_readout": [{
            "direction_id": "climate-fcv-on-project", "summary": "s",
            "pathways": [{"pathway_id": "climate-fcv-on-project-1",
                          "pressure": "p", "mechanism": "m",
                          "project_implication": "i", "design_response": "d"}],
        }],
        "readout_sections": [], "additional_pathways": [],
        "sensitivity_evidence": [], "responsiveness_evidence": [], "less_central": "",
    }], "findings": []}


def _priority_for_test(title, climate_links):
    return {
        "title": title, "fcv_dimension": "Contextual awareness", "tag": "[S]",
        "refresh_shift": "Shift A: Anticipate", "risk_level": "High",
        "the_gap": "g in Bentiu", "why_it_matters": "w", "actions": [
            {"document_element": "PAD", "guidance": "do X in Bentiu", "suggested_language": ""}],
        "who_acts": "TTL", "when": "before appraisal",
        "action_timing": "required-before-appraisal", "resources": "r",
        "pad_sections": "SORT", "implementation_note": "n", "cpf_alignment": None,
        "climate_links": climate_links,
    }


def test_climate_links_failure_keeps_priorities_and_counts_unlinked():
    good = {"status": "linked",
            "interaction_pathway_ids": ["climate-fcv-on-project-1"],
            "contribution": "c", "strengthening_effect": "s"}
    priorities = [_priority_for_test("Good one", good), _priority_for_test("Bad one", {"status": "bogus"})]
    result = app_module.extract_priorities(
        _stage3_block(priorities), ["Doc.pdf"], ["climate"], _climate_diag_for_test())
    assert result["error"] is False
    assert len(result["priorities"]) == 2
    assert result["climate_unlinked"] == 1
    assert result["climate_total"] == 2
    assert "climate" in result["priorities"][0]["lens_ids"]
    assert "climate" not in result["priorities"][1]["lens_ids"]
    assert result["priorities"][1]["climate_links"] is None



def test_climate_priority_completion_gate_keeps_only_valid_linked_priorities():
    diagnostic = _climate_diag_for_test()
    linked = _priority_for_test("Linked Bentiu priority", {
        "status": "linked",
        "interaction_pathway_ids": ["climate-fcv-on-project-1"],
        "dividend_pathway_ids": [], "finding_ids": [],
        "contribution": "Protects seasonal access in Bentiu.",
        "strengthening_effect": "Makes delivery more reliable.", "reason": "",
    })
    unlinked = _priority_for_test("Unlinked Bentiu priority", {
        "status": "linked", "interaction_pathway_ids": ["invented-id"],
        "contribution": "Unsupported.", "strengthening_effect": "", "reason": "",
    })
    parsed = app_module.extract_priorities(
        _stage3_block([linked, unlinked]), ["Doc.pdf"], ["climate"], diagnostic,
    )
    completed = app_module.enforce_climate_priority_provenance(parsed, diagnostic)
    assert [p["title"] for p in completed["priorities"]] == ["Linked Bentiu priority"]
    assert completed["priorities"][0]["lens_ids"] == ["climate"]
    assert completed["error"] is False


def test_climate_priority_completion_gate_fails_when_none_validate():
    parsed = {"error": False, "priorities": [{"climate_links": {"status": "linked", "interaction_pathway_ids": ["invented-id"]}}]}
    completed = app_module.enforce_climate_priority_provenance(
        parsed, _climate_diag_for_test()
    )
    assert completed["priorities"] == []
    assert completed["error"] is True
    assert completed["message"] == (
        "No validated climate-specific operational priority was produced."
    )


# -- Concise Stage 3 presentation layer --------------------------------------

def _concise_fixture(priority_concise=True, top_level=True):
    payload = {
        "fcv_rating": "Adequate",
        "fcv_responsiveness_rating": "Low",
        "sensitivity_summary": "Detailed sensitivity summary.",
        "responsiveness_summary": "Detailed responsiveness summary.",
        "risk_exposure": {"risks_to": "Risk to.", "risks_from": "Risk from."},
        "mid_cycle_watch": [],
        "dpf_watch": [],
        "p4r_watch": [],
        "regional_watch": [],
        "priorities": [{
            "title": "Priority 1 - Plan for disruption",
            "fcv_dimension": "Security",
            "tag": "[S]",
            "refresh_shift": "Shift A: Anticipate",
            "risk_level": "High",
            "the_gap": "Jonglei delivery depends on local committees.",
            "why_it_matters": "Conflict could interrupt delivery.",
            "actions": [{
                "document_element": "Project Description",
                "guidance": "Add three delivery modes.",
                "suggested_language": "The project will use flexible delivery arrangements."
            }],
            "who_acts": "TTL",
            "when": "Identification",
            "action_timing": "flag-for-preparation",
            "resources": "Minimal (existing budget)",
            "pad_sections": "Project Description",
            "country_category_relevance": "Relevant in a conflict-affected context.",
            "implementation_note": "Complete operating rules during preparation.",
            "cpf_alignment": None,
            "rra_driver_alignment": None,
            "change_type": None,
            "restructuring_level": None,
            "priority_scope": None,
            "governance_level": None,
        }]
    }
    if top_level:
        payload["concise_readout"] = {
            "headline": "Strong concept; delivery needs a fallback.",
            "overview": "The project has a sound foundation but needs adaptive delivery.",
            "strengths": [
                {"title": "Conflict-aware design", "text": "Governance is a project outcome."}
            ],
            "priority_intro": "Five actions would strengthen delivery."
        }
    if priority_concise:
        payload["priorities"][0]["concise"] = {
            "title": "Plan for disruption to local committees",
            "why": "Conflict may interrupt the bodies on which delivery depends.",
            "how": ["Add three delivery modes.", "Define triggers during preparation."],
            "suggested_wording": {
                "document_element": "Project Description",
                "text": "The project will use flexible delivery arrangements."
            },
            "project_cycle": {
                "primary_label": "Commit in the PCN",
                "primary_text": "State the adaptive logic now.",
                "secondary_label": "Develop during preparation",
                "secondary_text": "Define triggers and responsibilities."
            }
        }
    return "%%%JSON_START%%%\n" + json.dumps(payload) + "\n%%%JSON_END%%%"


def test_extract_priorities_returns_concise_layer():
    result = extract_priorities(_concise_fixture())
    assert result["concise_readout"]["headline"].startswith("Strong concept")
    assert result["priorities"][0]["concise"]["how"] == [
        "Add three delivery modes.",
        "Define triggers during preparation.",
    ]


def test_extract_priorities_legacy_payload_has_no_concise_layer():
    result = extract_priorities(_concise_fixture(False, False))
    assert result["concise_readout"] is None
    assert result["priorities"][0]["concise"] is None


def test_extract_priorities_discards_malformed_concise_layer_only():
    text = _concise_fixture().replace(
        '"strengths": [{"title": "Conflict-aware design", "text": "Governance is a project outcome."}]',
        '"strengths": "not-a-list"',
    )
    result = extract_priorities(text)
    assert result["error"] is False
    assert result["concise_readout"] is None
    assert result["priorities"][0]["concise"] is not None


def test_extract_priorities_caps_concise_lists():
    text = _concise_fixture().replace(
        '"how": ["Add three delivery modes.", "Define triggers during preparation."]',
        '"how": ["one", "two", "three", "four", "five"]',
    )
    result = extract_priorities(text)
    assert result["priorities"][0]["concise"]["how"] == ["one", "two", "three", "four"]
