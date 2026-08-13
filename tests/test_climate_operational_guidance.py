import re

from sector_lenses.climate_operational_guidance import (
    GUIDANCE_REGISTRY_VERSION,
    OPERATIONAL_GUIDANCE,
    select_operational_guidance,
)


def test_registry_has_stable_unique_ids_and_bounded_authority() -> None:
    assert GUIDANCE_REGISTRY_VERSION == "climate-guidance-v2"
    ids = [entry.guidance_id for entry in OPERATIONAL_GUIDANCE]
    assert len(ids) == len(set(ids))
    assert all(identifier.startswith("GUIDE-") for identifier in ids)
    assert {
        entry.authority_class for entry in OPERATIONAL_GUIDANCE
    } <= {"operational_guidance", "reviewer_judgment"}


def test_pcn_packet_is_stage_aware_and_bounded() -> None:
    packet = select_operational_guidance(
        doc_type="PCN",
        instrument_type="IPF",
    )
    assert 1 <= len(packet) <= 6
    assert "GUIDE-PCN-DESIGN" in {entry.guidance_id for entry in packet}
    assert all("pcn" in entry.document_types for entry in packet)
    assert all("ipf" in entry.instrument_types for entry in packet)
    assert all(entry.permitted_targets for entry in packet)


def test_registry_does_not_claim_mandates_or_policy_paragraphs() -> None:
    registry_text = " ".join(
        entry.application_rule + " " + " ".join(entry.prohibited_overstatements)
        for entry in OPERATIONAL_GUIDANCE
    ).casefold()
    assert not re.search(r"\b(?:must|shall|required)\b", registry_text)
    assert not re.search(r"\b(?:paragraph|para\.?)\s*\d+", registry_text)


def test_unknown_document_type_returns_no_guidance() -> None:
    assert select_operational_guidance(
        doc_type="unknown",
        instrument_type="IPF",
    ) == ()


def test_known_pcn_with_unknown_instrument_fails_closed() -> None:
    packet = select_operational_guidance(
        doc_type="PCN",
        instrument_type="Unknown",
    )

    assert packet == ()


def test_pforr_packet_uses_essa_pap_and_dli_targets_not_esf_instruments() -> None:
    packet = select_operational_guidance(
        doc_type="Program Paper",
        instrument_type="PforR",
    )
    targets = " ".join(
        value for entry in packet for target in entry.permitted_targets for value in target
    ).casefold()

    assert packet
    assert "essa" in targets
    assert "program action plan" in targets
    assert "dli" in targets
    assert not re.search(r"\b(?:escp|sep|ess[1-9])\b", targets)


def test_dpf_packet_uses_program_document_policy_targets_not_esf_instruments() -> None:
    packet = select_operational_guidance(
        doc_type="Program Document",
        instrument_type="DPF",
    )
    targets = " ".join(
        value for entry in packet for target in entry.permitted_targets for value in target
    ).casefold()

    assert packet
    assert "prior actions" in targets
    assert "poverty and social" in targets
    assert "environment" in targets
    assert not re.search(r"\b(?:escp|sep|ess[1-9]|essa)\b", targets)


def test_mpa_packet_adds_program_layer_to_base_instrument_guidance() -> None:
    packet = select_operational_guidance(
        doc_type="Project Paper",
        instrument_type="IPF",
        is_mpa=True,
    )

    ids = {entry.guidance_id for entry in packet}
    assert "GUIDE-MPA-PROGRAM-LAYER" in ids
    assert any("ipf" in entry.instrument_types for entry in packet)


def test_mpa_program_layer_is_not_sliced_off_for_ipf_pad() -> None:
    packet = select_operational_guidance(
        doc_type="PAD",
        instrument_type="IPF",
        is_mpa=True,
    )

    assert len(packet) <= 6
    assert "GUIDE-MPA-PROGRAM-LAYER" in {
        entry.guidance_id for entry in packet
    }
