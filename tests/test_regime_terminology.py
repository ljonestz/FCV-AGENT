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
