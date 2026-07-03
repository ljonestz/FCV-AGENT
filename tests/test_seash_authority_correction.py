"""SEA/SH policy-authority correction (OPCS follow-up, MAI Morocco/Nepal review).

MAI confirmed against the PforR policy core-principle set that:
  - PforR Core Principle 6 is about avoiding the *exacerbation of social conflict*,
    NOT SEA/SH. Anchoring SEA/SH to "ESSA Core Principle #6" is a misattribution.
  - "OPS5.04-POL.125 para 9(f)" is ESF/IPF citation architecture, not PforR.
  - SEA/SH obligations in a PforR flow from the public/worker-safety and
    vulnerable-groups core principles plus the Bank's Good Practice Note on SEA/SH,
    operationalized through the ESSA findings and the Program Action Plan (PAP).
This suite locks in the corrected framing so the misattribution cannot regress.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_pforr_seash_not_anchored_to_core_principle_6():
    import background_docs as bd

    for const in (bd.DNH_SEASH_PFORR, bd.SEASH_GENDER_CARD_PFORR):
        assert "Core Principle #6" not in const
        assert "Core Principle 6" not in const
        # The ESF-style sub-paragraph citation must not appear on a PforR.
        assert "para 9(f)" not in const
        assert "9(f)" not in const


def test_pforr_seash_uses_correct_authority():
    import background_docs as bd

    for const in (bd.DNH_SEASH_PFORR, bd.SEASH_GENDER_CARD_PFORR):
        # Correct governing authority for SEA/SH in a PforR.
        assert "Good Practice Note" in const
        # Still routed through the correct PforR instruments.
        assert "ESSA" in const
        assert "PAP" in const or "Program Action Plan" in const


def test_pforr_seash_grm_not_routed_through_esms_only():
    """GRM must be framed as the borrower's own systems assessed in the ESSA,
    not as an IPF-style ESMS deliverable (MAI Morocco issue 2)."""
    import background_docs as bd

    # The narrow, defensible reframe: GRM design lives in the borrower's own
    # systems as assessed in the ESSA (gaps closed via PAP/POM), not "through
    # the ESMS" as a project deliverable.
    assert "through the ESMS" not in bd.SEASH_GENDER_CARD_PFORR
    assert "through the ESMS" not in bd.DNH_SEASH_PFORR


def test_vocabulary_scrub_map_does_not_reintroduce_core_principle_6():
    import app

    pforr_scrub = app._VOCABULARY_SCRUB_MAP["PFORR"]
    for replacement in pforr_scrub.values():
        assert "Core Principle #6" not in replacement
        assert "Core Principle 6" not in replacement


def test_ipf_seash_flows_from_ess1_risk_assessment_and_gpn():
    """MAI (mild): the IPF SEA/SH *requirement* flows from the ESS1 risk
    assessment and the SEA/SH Good Practice Note, operationalized through
    ESS2/ESS4 — not 'required under ESS2 and ESS4' as the source authority."""
    import background_docs as bd

    assert "Good Practice Note" in bd.SEASH_GENDER_CARD_IPF
    # ESS2/ESS4 are still named as the operationalizing standards.
    assert "ESS2" in bd.SEASH_GENDER_CARD_IPF
    assert "ESS4" in bd.SEASH_GENDER_CARD_IPF
