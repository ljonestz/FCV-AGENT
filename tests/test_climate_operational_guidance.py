import re

from sector_lenses.climate_operational_guidance import (
    GUIDANCE_REGISTRY_VERSION,
    OPERATIONAL_GUIDANCE,
    select_operational_guidance,
)


def test_registry_has_stable_unique_ids_and_bounded_authority() -> None:
    assert GUIDANCE_REGISTRY_VERSION == "climate-guidance-v1"
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


def test_known_pcn_with_unknown_instrument_gets_document_scoped_guidance() -> None:
    packet = select_operational_guidance(
        doc_type="PCN",
        instrument_type="Unknown",
    )

    assert packet
    assert all("pcn" in entry.document_types for entry in packet)
    assert all(
        any(target[0] == "pcn" for target in entry.permitted_targets)
        for entry in packet
    )
