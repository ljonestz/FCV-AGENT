"""Unit tests for extract_priorities() — JSON parsing path.

Run with: python -m pytest tests/test_extract_priorities.py -v
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
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
        assert 'effectively unusable' in FCV_INSTRUMENT_CALIBRATION

    def test_mpa_calibration_block_present(self):
        assert 'MPA — FCV Calibration' in FCV_INSTRUMENT_CALIBRATION

    def test_mpa_phase_financing_not_guaranteed(self):
        assert 'NOT guaranteed' in FCV_INSTRUMENT_CALIBRATION
