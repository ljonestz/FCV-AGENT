"""Phase 3 — terminology normalisation: regime document label + section back-compat."""

import app as app_module


def test_appraisal_document_label_per_regime():
    assert app_module.appraisal_document_label("new_model", "IPF") == "Project Paper"
    assert app_module.appraisal_document_label("new_model", "PforR") == "Program Paper"
    assert app_module.appraisal_document_label("new_model", "DPO") == "Program Document"
    assert app_module.appraisal_document_label("legacy_transitional", "IPF") == "Project Appraisal Document (PAD)"
    # Unresolved regime falls back to the legacy PAD label (safe default).
    assert app_module.appraisal_document_label("unresolved_policy_source", "IPF") == "Project Appraisal Document (PAD)"


def _priority_block(section_field, section_value):
    return (
        '%%%JSON_START%%%{"fcv_rating":"Moderately addressed",'
        '"fcv_responsiveness_rating":"Emerging","sensitivity_summary":"x",'
        '"responsiveness_summary":"y","risk_exposure":{"risks_to":"a","risks_from":"b"},'
        '"priorities":[{"title":"Flood-resilient siting","fcv_dimension":"Contextual",'
        '"tag":"[S]","the_gap":"g","why_it_matters":"w","actions":[],'
        '"who_acts":"TTL","when":"soon","resources":"r","' + section_field + '":"' + section_value + '"}]}'
        '%%%JSON_END%%%'
    )


def test_pad_sections_backcompat_reads_new_key():
    r = app_module.extract_priorities(_priority_block("appraisal_document_sections", "IV.C"), uploaded_doc_names=[])
    p = r["priorities"][0]
    assert p["appraisal_document_sections"] == "IV.C"
    assert p["pad_sections"] == "IV.C"  # legacy alias mirrored for existing renderers


def test_pad_sections_backcompat_reads_legacy_key():
    r = app_module.extract_priorities(_priority_block("pad_sections", "SORT; ESCP"), uploaded_doc_names=[])
    p = r["priorities"][0]
    assert p["pad_sections"] == "SORT; ESCP"
    assert p["appraisal_document_sections"] == "SORT; ESCP"  # new key populated from legacy


# ── Phase 5 Task 5.1: regime-gated minimum reference set ──────────────────────

def test_new_model_ipf_reference_set_corrections():
    refs = app_module.appraisal_reference_set("new_model", "ESF_ESS1_TO_ESS10", "IPF")
    joined = " ".join(refs).lower()
    assert "results framework" in joined            # mandatory Annex 1
    assert "readiness esrs" in joined               # ADDED
    assert "economic analysis" in joined            # ADDED
    assert "operations manual" not in joined        # REMOVED from universal minimum
    assert "ess1" not in joined                     # standalone ESS1 replaced
    assert "applicable esss" in joined              # replaces standalone ESS1


def test_non_esf_instrument_omits_ess_checks():
    refs = app_module.appraisal_reference_set("new_model", "INSTRUMENT_SPECIFIC", "PforR")
    assert not any("ess" in r.lower() for r in refs)


def test_new_model_non_ipf_esf_regime_still_omits_ess():
    # ESF regime label but instrument is not IPF -> ESS checks do not apply.
    refs = app_module.appraisal_reference_set("new_model", "ESF_ESS1_TO_ESS10", "PforR")
    assert not any("ess" in r.lower() for r in refs)


def test_legacy_reference_set_unchanged():
    # Legacy path returns the existing PAD minimum set verbatim, regardless of es_regime.
    assert app_module.appraisal_reference_set("legacy_transitional", "ESF_ESS1_TO_ESS10", "IPF") == \
        app_module.LEGACY_PAD_MINIMUM_REFERENCE_SET
    assert app_module.appraisal_reference_set("legacy_transitional", "LEGACY_SAFEGUARDS", "IPF") == \
        app_module.LEGACY_PAD_MINIMUM_REFERENCE_SET


def test_unresolved_regime_uses_legacy_reference_set():
    # The safe default (no regime detected) must not switch to the new-model set.
    assert app_module.appraisal_reference_set("unresolved_policy_source", "UNRESOLVED", "IPF") == \
        app_module.LEGACY_PAD_MINIMUM_REFERENCE_SET
