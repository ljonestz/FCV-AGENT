"""Instrument-conditional SEA/SH and DNH vocabulary tests (Workstream 1)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_dnh_seash_variants_exist_and_are_instrument_true():
    import background_docs as bd

    assert "ESCP" in bd.DNH_SEASH_IPF
    assert "ESS2" in bd.DNH_SEASH_IPF

    assert "ESCP" not in bd.DNH_SEASH_PFORR
    assert "ESS4" not in bd.DNH_SEASH_PFORR
    assert "ESSA" in bd.DNH_SEASH_PFORR
    assert "Core Principle" in bd.DNH_SEASH_PFORR

    assert "ESCP" not in bd.DNH_SEASH_DPF
    assert "ESS4" not in bd.DNH_SEASH_DPF
    assert "PSIA" in bd.DNH_SEASH_DPF
    assert "Adjustment Sequencing" in bd.DNH_SEASH_DPF


def test_get_dnh_seash_guidance_selects_by_instrument():
    from app import get_dnh_seash_guidance
    import background_docs as bd

    assert get_dnh_seash_guidance("IPF") == bd.DNH_SEASH_IPF
    assert get_dnh_seash_guidance("Unknown") == bd.DNH_SEASH_IPF
    assert get_dnh_seash_guidance("PforR") == bd.DNH_SEASH_PFORR
    assert get_dnh_seash_guidance("P4R") == bd.DNH_SEASH_PFORR
    assert get_dnh_seash_guidance("DPO") == bd.DNH_SEASH_DPF


def test_seash_gender_card_variants_exist_and_are_instrument_true():
    import background_docs as bd

    assert "ESS2" in bd.SEASH_GENDER_CARD_IPF
    assert "ESS4" in bd.SEASH_GENDER_CARD_IPF

    assert "ESS2" not in bd.SEASH_GENDER_CARD_PFORR
    assert "ESS4" not in bd.SEASH_GENDER_CARD_PFORR
    assert "ESSA" in bd.SEASH_GENDER_CARD_PFORR
    assert "PAP" in bd.SEASH_GENDER_CARD_PFORR

    assert "ESS2" not in bd.SEASH_GENDER_CARD_DPF
    assert "ESS4" not in bd.SEASH_GENDER_CARD_DPF
    assert "PSIA" in bd.SEASH_GENDER_CARD_DPF


def test_get_seash_gender_card_guidance_selects_by_instrument():
    from app import get_seash_gender_card_guidance
    import background_docs as bd

    assert get_seash_gender_card_guidance("IPF") == bd.SEASH_GENDER_CARD_IPF
    assert get_seash_gender_card_guidance("PforR") == bd.SEASH_GENDER_CARD_PFORR
    assert get_seash_gender_card_guidance("DPO") == bd.SEASH_GENDER_CARD_DPF


def test_default_prompts_use_placeholders_not_hardcoded_escp_language():
    import app

    # Stage 2 prompt must reference the placeholder, not the old hard-coded
    # ESCP-anchored Principle 9 text directly.
    assert "{dnh_seash_guidance}" in app.DEFAULT_PROMPTS["2"]
    assert "does the ESCP include a time-bound commitment" not in app.DEFAULT_PROMPTS["2"]

    # Stage 3 prompt must reference the placeholder, not the old hard-coded
    # Gender-FCV / SEA-SH card rule text directly.
    assert "{seash_gender_card_guidance}" in app.DEFAULT_PROMPTS["3"]
    assert "Explicitly reference the SEA/SH Action Plan (required under ESS2 and ESS4" not in app.DEFAULT_PROMPTS["3"]


def test_get_dnh_seash_guidance_replaces_placeholder_cleanly():
    from app import get_dnh_seash_guidance, DEFAULT_PROMPTS

    for instrument in ("IPF", "PforR", "DPO"):
        guidance = get_dnh_seash_guidance(instrument)
        filled = DEFAULT_PROMPTS["2"].replace("{dnh_seash_guidance}", guidance)
        assert "{dnh_seash_guidance}" not in filled
        assert guidance in filled


def test_get_seash_gender_card_guidance_replaces_placeholder_cleanly():
    from app import get_seash_gender_card_guidance, DEFAULT_PROMPTS

    for instrument in ("IPF", "PforR", "DPO"):
        guidance = get_seash_gender_card_guidance(instrument)
        filled = DEFAULT_PROMPTS["3"].format(
            doc_type="PAD",
            timing_emphasis="Preparation",
            playbook_guidance="",
            instrument_guidance="",
            temporal_guardrail="",
            seash_gender_card_guidance=guidance,
        )
        assert "{seash_gender_card_guidance}" not in filled
        assert guidance in filled
