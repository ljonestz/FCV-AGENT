"""Word export strips internal evidence ids from reviewer notes, as the browser does."""
import pytest

from fcv_docx_style import clean_verify_marker, clean_verify_note

# Notes taken from the 2026-11-08 production climate reports.
CASES = [
    (("Check PF-001, PF-003 and the problem statement in DOC-091a2db1a79ccd61-B-6325ed05305d: "
      "the road is meant to provide access."),
     "Check the problem statement: the road is meant to provide access."),
    ("Check PF-003 source block DOC-091a2db1a79ccd61-B-25ee58a4e454: confirm it describes San Pedro Sula.",
     "Confirm it describes San Pedro Sula."),
    (("Check PF-007, PF-050 and PF-023 against source blocks DOC-091a2db1a79ccd61-B-bd7e9d7bde1d and "
      "DOC-091a2db1a79ccd61-B-d88ab919d0aa: confirm that the exclusion is a scope limit."),
     "Confirm that the exclusion is a scope limit."),
    (("Check the Results Framework, POM and monitoring sections (PF-045, PF-046 source blocks) for any "
      "disaggregation."), "Check the Results Framework, POM and monitoring sections for any disaggregation."),
    ("Check against Subcomponent 2.2 (PF-012, PF-024 and source block 4b36c2298630): confirm y.",
     "Check against Subcomponent 2.2: confirm y."),
    ("Check PF-038 and the Mid-Term Review passage (DOC block 64a28bb371dc): it confirms scope.",
     "Check the Mid-Term Review passage: it confirms scope."),
    ("Check PF-003 block DOC-0a1b-B-2c3d: confirm flooding, and that the wording matches.",
     "Confirm flooding, and that the wording matches."),
    ("Confirm the targeting rule in the Project Operations Manual.",
     "Confirm the targeting rule in the Project Operations Manual."),
]


@pytest.mark.parametrize("raw,expected", CASES)
def test_clean_verify_note(raw, expected):
    assert clean_verify_note(raw) == expected


def test_marker_keeps_prefix_and_drops_empty_notes():
    assert clean_verify_marker("[Verify before sharing: Check PF-001: confirm x.]") == \
        "[Verify before sharing: Confirm x.]"
    assert clean_verify_marker("[Verify before sharing: PF-001]") == ""


def test_word_body_has_no_internal_ids():
    from fcv_docx_style import Report
    doc = Report("climate", {"title": "t", "project_line": "p", "running_label": "r", "date": "d",
                             "classification": "c", "generator": "g", "disclaimer": "x"})
    p = doc.body("The road is designed to cut flood closures (PF-003). [Verify before sharing: Check PF-001 "
                 "and the problem statement in DOC-0a1b2c3d4e5f-B-6325ed05305d: confirm scope.]")
    text = p.text
    assert "PF-" not in text and "DOC-" not in text
    assert "[Verify before sharing: Check the problem statement: confirm scope.]" in text
