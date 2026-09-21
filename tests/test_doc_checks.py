"""General-screener document-integrity scan (A4): parser + strip."""
from __future__ import annotations

from app import clean_stage1_output, extract_doc_checks


def test_extract_doc_checks_parses_findings():
    s1 = (
        "Body text.\n%%%DOC_CHECKS_START%%%"
        '{"findings":[{"finding":"Component 1 budget shows xx as a placeholder",'
        '"why_it_matters":"the target cannot be read","where":"Sub-component 1.1"}]}'
        "%%%DOC_CHECKS_END%%%\nMore body."
    )
    out = extract_doc_checks(s1)
    assert len(out) == 1
    assert out[0]["finding"].startswith("Component 1 budget")
    assert out[0]["why_it_matters"] == "the target cannot be read"
    assert out[0]["where"] == "Sub-component 1.1"


def test_extract_doc_checks_empty_when_absent_or_empty():
    assert extract_doc_checks("no block here") == []
    assert extract_doc_checks(
        '%%%DOC_CHECKS_START%%%{"findings":[]}%%%DOC_CHECKS_END%%%'
    ) == []
    # Malformed JSON degrades to empty, never raises.
    assert extract_doc_checks("%%%DOC_CHECKS_START%%%not json%%%DOC_CHECKS_END%%%") == []


def test_extract_doc_checks_caps_at_five():
    items = ",".join(
        '{"finding":"f%d","why_it_matters":"w","where":"x"}' % i for i in range(8)
    )
    s1 = "%%%DOC_CHECKS_START%%%{\"findings\":[" + items + "]}%%%DOC_CHECKS_END%%%"
    assert len(extract_doc_checks(s1)) == 5


def test_clean_stage1_output_strips_doc_checks_block():
    s1 = (
        "Visible text.\n%%%DOC_CHECKS_START%%%{\"findings\":[]}%%%DOC_CHECKS_END%%%"
        "\nMore visible text."
    )
    cleaned = clean_stage1_output(s1)
    assert "DOC_CHECKS" not in cleaned
    assert "Visible text." in cleaned and "More visible text." in cleaned
