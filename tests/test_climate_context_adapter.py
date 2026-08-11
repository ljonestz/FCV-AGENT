from sector_lenses.climate_analysis import evidence_can_support
from sector_lenses.climate_context_adapter import adapt_grounding_evidence
from sector_lenses.climate_grounding import merge_climate_grounding


def _candidate_bank_packet() -> dict:
    return {
        "bank_status": "ok",
        "content_version": "2026.08",
        "country_iso3": "SSD",
        "candidate_preview": True,
        "sources": [{
            "source_id": "SSD-SRC-001",
            "url": "https://example.org/reviewed",
            "title": "Reviewed source",
        }],
        "evidence_records": [{
            "evidence_id": "SSD-E-001",
            "compact_statement": "Flooding can restrict seasonal access.",
            "evidence_class": "climate-pressure",
            "administrative_level": "state",
            "geographies": ["Unity"],
            "source_refs": [{
                "source_id": "SSD-SRC-001",
                "locator": "p. 4",
            }],
            "confidence": "high",
        }],
        "pathways": [{
            "pathway_id": "SSD-P-001",
            "compact_statement": "Flooding can disrupt access and services.",
            "interaction_direction": "climate-to-fcv",
            "geographies": ["Unity"],
            "supporting_evidence_ids": ["SSD-E-001"],
            "evidence_strength": "moderate",
        }],
    }


def _research_bundle() -> dict:
    return {
        "status": "complete",
        "sources": [{
            "id": "climate-source-1",
            "url": "https://example.org/live",
            "title": "Current bulletin",
        }],
        "claims": [{
            "id": "climate-claim-1",
            "claim": "A current bulletin reports access disruption.",
            "source_ids": ["climate-source-1"],
            "geographies": ["Unity"],
            "confidence": "medium",
            "time_horizons": ["current-near-term"],
        }],
    }


def test_candidate_grounding_preserves_preview_and_context_metadata():
    grounding = merge_climate_grounding(_candidate_bank_packet(), {})
    evidence = adapt_grounding_evidence(grounding)

    record = next(item for item in evidence if item.evidence_id == "CE-BANK-SSD-E-001")
    assert record.evidence_class == "country"
    assert record.context_class == "climate-pressure"
    assert record.scope == "state: Unity"
    assert record.source_kind == "country_bank"
    assert record.preview_status == "preview; not approved"
    assert record.source_ref == "bank-preview:2026.08:SSD-E-001"
    assert evidence_can_support(record, "project_design_fact") is False


def test_bank_pathway_remains_contextual_and_preview_labelled():
    grounding = merge_climate_grounding(_candidate_bank_packet(), {})
    evidence = adapt_grounding_evidence(grounding)
    pathway = next(item for item in evidence if item.evidence_id == "CE-BANK-SSD-P-001")
    assert pathway.context_class == "climate-to-fcv-pathway"
    assert pathway.preview_status == "preview; not approved"
    assert pathway.source_ref == "bank-preview:2026.08:SSD-P-001"


def test_live_claim_keeps_url_scope_and_retrieval_context():
    grounding = merge_climate_grounding({}, _research_bundle())
    evidence = adapt_grounding_evidence(grounding)
    claim = evidence[0]
    assert claim.evidence_id == "CE-LIVE-climate-claim-1"
    assert claim.source_kind == "live_research"
    assert claim.scope == "Unity"
    assert claim.source_ref == "live:https://example.org/live:climate-claim-1"
    assert claim.preview_status is None


def test_live_claim_with_any_unresolved_source_is_rejected():
    bundle = _research_bundle()
    bundle["claims"][0]["source_ids"] = [
        "climate-source-1",
        "missing-source",
    ]
    grounding = merge_climate_grounding({}, bundle)

    assert adapt_grounding_evidence(grounding) == ()


def test_malformed_or_unsourced_context_is_discarded():
    grounding = {
        "bank_evidence_records": [{"evidence_id": "SSD-E-001"}],
        "bank_pathways": [{"pathway_id": "SSD-P-001"}],
        "live_sources": [],
        "live_claims": [{"id": "claim-1", "claim": "Unsupported"}],
    }
    assert adapt_grounding_evidence(grounding) == ()


def test_rich_selected_bank_records_keep_verified_context_contract():
    packet = _candidate_bank_packet()
    packet["selected_evidence_ids"] = ["SSD-E-001"]
    packet["selected_pathway_ids"] = ["SSD-P-001"]
    packet["project_relevance"] = {
        "SSD-E-001": {
            "score": 29,
            "matched_fields": ["geographies", "systems_assets"],
        },
    }
    record = packet["evidence_records"][0]
    record["affected_groups"] = ["seasonal road users"]
    record["systems_assets_resources"] = ["feeder roads"]
    record["uncertainty"] = "County-level variation remains material."

    evidence = adapt_grounding_evidence(
        merge_climate_grounding(packet, {})
    )
    by_id = {item.evidence_id: item for item in evidence}

    selected = by_id["CE-BANK-SSD-E-001"]
    assert selected.scope == "state: Unity"
    assert selected.confidence == "high"
    assert selected.context_class == "climate-pressure"
    assert selected.source_ref == "bank-preview:2026.08:SSD-E-001"
    assert selected.preview_status == "preview; not approved"
    assert evidence_can_support(selected, "project_design_fact") is False
    pathway = by_id["CE-BANK-SSD-P-001"]
    assert pathway.context_class == "climate-to-fcv-pathway"
    assert pathway.source_ref == "bank-preview:2026.08:SSD-P-001"
