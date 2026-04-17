"""Tests for country classification and secondary knowledge selection.

Run with: python -m pytest tests/test_classification.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFoundationConstants:

    def test_op730_countries_imported(self):
        from background_docs import OP730_COUNTRIES
        assert isinstance(OP730_COUNTRIES, list)
        assert len(OP730_COUNTRIES) >= 4

    def test_op730_contains_known_members(self):
        from background_docs import OP730_COUNTRIES
        members = [c.lower() for c in OP730_COUNTRIES]
        assert 'afghanistan' in members
        assert 'myanmar' in members
        assert 'sudan' in members
        assert 'yemen' in members

    def test_fcs_countries_current_imported(self):
        from background_docs import FCS_COUNTRIES_CURRENT
        assert isinstance(FCS_COUNTRIES_CURRENT, frozenset)
        assert len(FCS_COUNTRIES_CURRENT) >= 35

    def test_fcs_countries_contains_known_members(self):
        from background_docs import FCS_COUNTRIES_CURRENT
        assert 'Nigeria' in FCS_COUNTRIES_CURRENT
        assert 'Somalia' in FCS_COUNTRIES_CURRENT
        assert 'Ukraine' in FCS_COUNTRIES_CURRENT

    def test_secondary_knowledge_imported(self):
        from background_docs import SECONDARY_KNOWLEDGE
        assert isinstance(SECONDARY_KNOWLEDGE, dict)
        assert len(SECONDARY_KNOWLEDGE) >= 1

    def test_secondary_knowledge_snippet_structure(self):
        from background_docs import SECONDARY_KNOWLEDGE
        # Every snippet must have required keys
        for sid, snippet in SECONDARY_KNOWLEDGE.items():
            assert 'title' in snippet, f"{sid} missing title"
            assert 'source' in snippet, f"{sid} missing source"
            assert 'triggers' in snippet, f"{sid} missing triggers"
            assert 'content' in snippet, f"{sid} missing content"
            t = snippet['triggers']
            for field in ('country_category', 'instrument', 'sector', 'flags', 'doc_type'):
                assert field in t, f"{sid}.triggers missing {field}"

    def test_differentiated_approaches_imported(self):
        from background_docs import DIFFERENTIATED_APPROACHES
        assert isinstance(DIFFERENTIATED_APPROACHES, str)
        assert len(DIFFERENTIATED_APPROACHES) > 2000


class TestClassifyCountry:

    def test_op730_country_returns_in_crisis(self):
        from app import classify_country
        result = classify_country('Afghanistan')
        assert result['category'] == 'In Crisis'
        assert result['confidence'] == 'high'

    def test_op730_case_insensitive(self):
        from app import classify_country
        result = classify_country('myanmar')
        assert result['category'] == 'In Crisis'

    def test_fcs_country_returns_conflict_affected(self):
        from app import classify_country
        result = classify_country('Nigeria')
        assert result['category'] == 'Conflict-Affected'
        assert result['confidence'] == 'high'

    def test_fcs_country_not_op730(self):
        from app import classify_country
        result = classify_country('Somalia')
        assert result['category'] == 'Conflict-Affected'

    def test_unknown_country_returns_none_category(self):
        from app import classify_country
        result = classify_country('France')
        assert result['category'] is None

    def test_returns_dict_with_required_keys(self):
        from app import classify_country
        result = classify_country('Nigeria')
        assert 'category' in result
        assert 'confidence' in result
        assert 'reasoning' in result


class TestExtractCountryClassification:

    def test_extracts_category(self):
        from app import extract_country_classification
        text = """Some output.
%%%COUNTRY_CLASSIFICATION_START%%%
category: Conflict-Affected
confidence: high
reasoning: Nigeria is on the FCS list since 2020.
%%%COUNTRY_CLASSIFICATION_END%%%
More output."""
        result = extract_country_classification(text)
        assert result['category'] == 'Conflict-Affected'
        assert result['confidence'] == 'high'
        assert 'Nigeria' in result['reasoning']

    def test_returns_general_when_no_block(self):
        from app import extract_country_classification
        result = extract_country_classification("No classification block here.")
        assert result['category'] == 'General'
        assert result['error'] is True


class TestExtractContextFlags:

    def test_extracts_true_flags(self):
        from app import extract_context_flags
        text = """%%%CONTEXT_FLAGS_START%%%
cerc_mentioned: true
tpi_mentioned: false
rra_referenced: true
security_risks_noted: false
displacement_context: false
private_sector_focus: false
vulnerable_groups: false
emergency_component: false
procurement_issues: false
fiduciary_risks: false
cpf_uploaded: false
scd_mentioned: false
prevention: false
early_warning: false
armed_forces_mentioned: false
%%%CONTEXT_FLAGS_END%%%"""
        result = extract_context_flags(text)
        assert result['cerc_mentioned'] is True
        assert result['tpi_mentioned'] is False
        assert result['rra_referenced'] is True

    def test_returns_all_false_when_no_block(self):
        from app import extract_context_flags
        result = extract_context_flags("No flags block here.")
        assert isinstance(result, dict)
        assert result.get('error') is True


class TestExtractSectorContext:

    def test_extracts_primary_sector(self):
        from app import extract_sector_context
        text = """%%%SECTOR_CONTEXT_START%%%
primary_sector: water and sanitation
secondary_sectors: health, community development
%%%SECTOR_CONTEXT_END%%%"""
        result = extract_sector_context(text)
        assert result['primary_sector'] == 'water and sanitation'
        assert 'health' in result['secondary_sectors']

    def test_returns_unknown_when_no_block(self):
        from app import extract_sector_context
        result = extract_sector_context("No sector block.")
        assert result['primary_sector'] == 'Unknown'


class TestSelectSecondaryKnowledge:

    def test_returns_list(self):
        from app import select_secondary_knowledge
        result = select_secondary_knowledge('In Crisis', 'IPF', 'PAD', 'water', {})
        assert isinstance(result, list)

    def test_in_crisis_triggers_op730_snippet(self):
        from app import select_secondary_knowledge
        from background_docs import SECONDARY_KNOWLEDGE
        # Patch content so snippet is non-empty
        SECONDARY_KNOWLEDGE['op730_engagement']['content'] = 'OP730 content here.'
        result = select_secondary_knowledge('In Crisis', 'IPF', 'PAD', 'water', {})
        contents = [r['content'] for r in result]
        assert any('OP730' in c or 'op730' in c.lower() for c in contents) or \
               any(r['id'] == 'op730_engagement' for r in result)
        SECONDARY_KNOWLEDGE['op730_engagement']['content'] = ''  # reset

    def test_cap_at_five_snippets(self):
        from app import select_secondary_knowledge
        from background_docs import SECONDARY_KNOWLEDGE
        # Temporarily fill all contents
        for sid in SECONDARY_KNOWLEDGE:
            SECONDARY_KNOWLEDGE[sid]['content'] = 'x' * 100
        result = select_secondary_knowledge('In Crisis', 'IPF', 'PAD', 'health', {
            'cerc_mentioned': True, 'tpi_mentioned': True, 'security_risks_noted': True,
            'displacement_context': True, 'vulnerable_groups': True,
            'emergency_component': True, 'rra_referenced': True
        })
        assert len(result) <= 5
        for sid in SECONDARY_KNOWLEDGE:
            SECONDARY_KNOWLEDGE[sid]['content'] = ''  # reset

    def test_no_snippets_for_general_category(self):
        from app import select_secondary_knowledge
        from background_docs import SECONDARY_KNOWLEDGE
        # Fill all contents
        for sid in SECONDARY_KNOWLEDGE:
            SECONDARY_KNOWLEDGE[sid]['content'] = 'x' * 100
        result = select_secondary_knowledge('General', 'Unknown', 'Unknown', 'Unknown', {})
        # Should only match snippets with empty country_category (wildcards)
        # None of the current snippets have all empty triggers, so some may still match on flags
        # Key test: no snippet with country_category constraint fires for 'General'
        for item in result:
            sid = item['id']
            triggers = SECONDARY_KNOWLEDGE[sid]['triggers']
            if triggers['country_category']:
                assert False, f"Snippet {sid} should not fire for General category"
        for sid in SECONDARY_KNOWLEDGE:
            SECONDARY_KNOWLEDGE[sid]['content'] = ''  # reset

    def test_empty_content_snippets_excluded(self):
        from app import select_secondary_knowledge
        result = select_secondary_knowledge('In Crisis', 'IPF', 'PAD', 'water', {})
        # All contents are '' in scaffold — should return empty list
        assert result == []
