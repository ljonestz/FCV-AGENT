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
