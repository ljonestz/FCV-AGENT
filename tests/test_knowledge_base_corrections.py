"""Regression tests for Workstream 3 knowledge-base corrections.

Each test asserts the corrected text is present and the incorrect text is
gone, for one background_docs.py constant or app.py inline string.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_mpa_guide_does_not_list_dpf_as_a_phase_instrument():
    from background_docs import MPA_MODULE_GUIDE

    assert "IPF, DPF, or P4R" not in MPA_MODULE_GUIDE
    assert "IPF or P4R operation" in MPA_MODULE_GUIDE


def test_mpa_guide_approval_authority_is_not_absolute():
    from background_docs import MPA_MODULE_GUIDE

    assert "Management (RVP) approves subsequent phases" not in MPA_MODULE_GUIDE
    assert "may return to the Board" in MPA_MODULE_GUIDE


def test_af_guide_does_not_claim_rvp_approved_waiver_is_the_only_route():
    from background_docs import AF_GUIDE

    assert "RVP-approved exception" not in AF_GUIDE
    assert "policy waiver" in AF_GUIDE.lower()


def test_p4r_guide_does_not_claim_cross_references_op_7_30_unconditionally():
    from background_docs import P4R_MODULE_GUIDE

    # The policy citation should describe OP 7.30 as a feasibility constraint
    # to check, not assert the PforR policy itself formally cross-references it.
    assert "cross-referencing **OP 7.30**" not in P4R_MODULE_GUIDE
    assert "OP 7.30 as a feasibility constraint" in P4R_MODULE_GUIDE


def test_p4r_guide_removes_category_a_equivalent_mislabel():
    from background_docs import P4R_MODULE_GUIDE

    assert "Category-A-equivalent" not in P4R_MODULE_GUIDE


def test_p4r_guide_mentions_rapid_response_option():
    from background_docs import P4R_MODULE_GUIDE

    assert "Rapid Response Option" in P4R_MODULE_GUIDE
    assert "RRO" in P4R_MODULE_GUIDE


def test_calibration_notes_edp_term_flagged_for_verification_not_asserted():
    from background_docs import FCV_INSTRUMENT_CALIBRATION

    # The unverified "Extended Data Pathway (EDP)" acronym must not be
    # asserted as fact; replace with a conservative, verification-flagged note.
    assert "Extended Data Pathway (EDP)" not in FCV_INSTRUMENT_CALIBRATION
    assert "[Verify with regional FCV coordinator" in FCV_INSTRUMENT_CALIBRATION


def test_app_py_whr_summary_does_not_lump_whr_into_fcve():
    with open("app.py", encoding="utf-8") as f:
        content = f.read()
    assert 'summary="Governing source for PRA, RECA, TAA, WHR and related FCV Envelope advice."' not in content
    assert "Governing source for PRA, RECA, TAA (the FCV Envelope allocations)" in content


def test_app_py_stage1_prompt_does_not_group_whr_with_fcve_windows():
    with open("app.py", encoding="utf-8") as f:
        content = f.read()
    assert "IDA FCV Envelope financing windows (PRA, RECA, TAA, WHR)" not in content
    assert "IDA FCV Envelope financing windows (PRA, RECA, TAA), or the related but separate WHR" in content
