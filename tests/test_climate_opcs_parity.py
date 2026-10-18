"""Regression cases from the October 2026 Climate/OPCS source review."""

import pytest

from sector_lenses.climate_verified_runtime import (
    prepare_verified_sources, resolve_verified_operation_context,
)
from sector_lenses.climate_operational_guidance import select_operational_guidance
from sector_lenses.climate_verified_render import _project_cycle_for_operation


def context(text, **hints):
    sources = prepare_verified_sources([{
        "label": "PROJECT DOCUMENT", "name": "operation.txt", "raw_text": text,
    }])
    return resolve_verified_operation_context(sources, **hints)


def test_dpf_pad_hint_is_normalized_but_unknown_stage_is_not_invented():
    assert context("Development Policy Financing", doc_type="PAD").document_type == "Program Document"
    assert context("Development Policy Financing").document_type == "Unknown"


@pytest.mark.parametrize("document", ["Program Document", "Project Paper", "PID"])
def test_ambiguous_titles_do_not_establish_preparation_regime(document):
    assert context(document).preparation_regime == "unresolved_policy_source"


def test_pid_ois_date_has_no_false_legacy_conflict_and_resolves_esf():
    result = context("PID. IPF. OIS creation date: 2026-05-01")
    assert result.es_regime == "ESF_ESS1_TO_ESS10"
    assert "PREPARATION_MARKER_DATE_CONFLICT" not in result.warning_codes


@pytest.mark.parametrize("phrase, expected", [
    ("One-step processing", "one_step"),
    ("Two-step processing", "two_step"),
    ("One Review", "one_review"),
    ("One-step processing and Two-step processing", "unknown"),
])
def test_explicit_processing_models_and_conflicts(phrase, expected):
    assert context("IPF. " + phrase).processing_model == expected


def test_new_model_risk_routing_and_unknown_hybrid_risk():
    text = "PforR. OIS creation date: 2026-05-01. Overall SORT: Moderate. Environmental and social risk: Moderate."
    assert context(text).processing_model == "one_step"
    assert context(text + " Includes an IPF component.").processing_model == "unknown"


def test_af_title_outranks_project_paper_and_preserves_es_exception():
    result = context("Project Paper. Additional Financing. IPF. OIS creation date: 2026-05-01. Safeguard policies apply.", doc_type="AF")
    assert result.document_type == "AF"
    assert result.es_regime == "LEGACY_SAFEGUARDS"
    assert "GUIDE-IPF-MID-CYCLE-DESIGN" in {g.guidance_id for g in select_operational_guidance(doc_type=result.document_type, instrument_type=result.instrument_type)}


def test_ipf_ddo_hint_uses_ipf_guidance():
    result = context("Operation overview", doc_type="PAD", instrument_type="IPF-DDO")
    assert result.instrument_type == "IPF"
    assert select_operational_guidance(doc_type="PAD", instrument_type="IPF-DDO")


def test_ta_is_explicitly_unresolved():
    result = context("Technical assistance", doc_type="PAD", instrument_type="TA")
    assert result.instrument_type == "Unknown"
    assert "INSTRUMENT_ROUTE_UNRESOLVED" in result.warning_codes


def test_dpf_mpa_is_rejected():
    result = context("Program Document. DPF. MPA.")
    assert "MPA_INSTRUMENT_INCOMPATIBLE" in result.warning_codes
    assert not select_operational_guidance(doc_type="Program Document", instrument_type="DPF", is_mpa=True)


@pytest.mark.parametrize("document", ["AF", "Restructuring"])
def test_pforr_mid_cycle_has_systems_guidance(document):
    packet = select_operational_guidance(doc_type=document, instrument_type="PforR")
    assert packet
    assert any("program action plan" in section for g in packet for _, section in g.permitted_targets)


def test_new_model_reader_uses_review_sequence_without_implying_current_status():
    labels = _project_cycle_for_operation({"document_type": "PID", "preparation_regime": "new_model", "processing_model": "two_step"}, {})
    assert "Technical Design" in labels["primary_label"]
    assert "Implementation Readiness" in labels["secondary_label"]


def test_appraisal_climate_checks_survive_packet_limit_with_mpa():
    for document, instrument in [("PAD", "IPF"), ("Project Paper", "IPF"), ("Program Paper", "PforR")]:
        packet = select_operational_guidance(doc_type=document, instrument_type=instrument, is_mpa=True)
        assert len(packet) <= 6
        rules = " ".join(g.application_rule for g in packet)
        assert "Paris Alignment" in rules
        assert "climate co-benefits" in rules
        assert "GUIDE-MPA-PROGRAM-LAYER" in {g.guidance_id for g in packet}


def test_first_mpa_phase_and_fmrf_do_not_take_low_risk_shortcut():
    text = "IPF. OIS creation date: 2026-05-01. Overall SORT: Moderate. Environmental and social risk: Moderate. "
    assert context(text + "MPA first phase.").processing_model == "two_step"
    assert context(text + "MPA.").processing_model == "unknown"
    assert context(text + "Full Mutual Reliance Framework.").processing_model == "two_step"


def test_mixed_es_frameworks_are_not_silently_resolved():
    result = context("IPF. Project Paper. OIS creation date: 2026-05-01. Safeguard policies and ESF are discussed.")
    assert result.es_regime == "UNRESOLVED"
    assert "ES_REGIME_CONFLICT" in result.warning_codes
