"""Phase 4 — regime-aware action_timing resolution in extract_priorities."""

import app as app_module


def _block(timing):
    return (
        '%%%JSON_START%%%{"fcv_rating":"Moderately addressed",'
        '"fcv_responsiveness_rating":"Emerging","sensitivity_summary":"x",'
        '"responsiveness_summary":"y","risk_exposure":{"risks_to":"a","risks_from":"b"},'
        '"priorities":[{"title":"T","fcv_dimension":"Contextual","tag":"[S]","the_gap":"g",'
        '"why_it_matters":"w","actions":[],"who_acts":"TTL","when":"soon","resources":"r",'
        '"pad_sections":"IV","action_timing":"' + timing + '"}]}%%%JSON_END%%%'
    )


def test_new_model_remaps_before_appraisal_to_td_review():
    r = app_module.extract_priorities(
        _block("required-before-appraisal"), uploaded_doc_names=[],
        preparation_regime="new_model", instrument="IPF",
    )
    t = r["priorities"][0]["action_timing"]
    assert t == "before-TD-review"
    assert "appraisal" not in t


def test_new_model_keeps_valid_new_model_timing():
    r = app_module.extract_priorities(
        _block("before-IR"), uploaded_doc_names=[],
        preparation_regime="new_model", instrument="IPF",
    )
    assert r["priorities"][0]["action_timing"] == "before-IR"


def test_legacy_keeps_before_appraisal():
    r = app_module.extract_priorities(
        _block("required-before-appraisal"), uploaded_doc_names=[],
        preparation_regime="legacy_transitional", instrument="IPF",
    )
    assert r["priorities"][0]["action_timing"] == "required-before-appraisal"


def test_default_call_unchanged_legacy_behaviour():
    # No regime kwargs (existing callers) -> legacy validation, unchanged.
    r = app_module.extract_priorities(_block("required-before-appraisal"), uploaded_doc_names=[])
    assert r["priorities"][0]["action_timing"] == "required-before-appraisal"
    # An invalid legacy value still nulls out, as before.
    r2 = app_module.extract_priorities(_block("whenever-you-like"), uploaded_doc_names=[])
    assert r2["priorities"][0]["action_timing"] is None


def test_new_model_timing_labels_wired_into_ui_and_docx():
    """Task 4.2: the 11 new-model timings render as pills (3 index.html maps) + DOCX."""
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    html = (root / "index.html").read_text(encoding="utf-8")
    appsrc = (root / "app.py").read_text(encoding="utf-8")
    # Human label present in all three index.html timing maps (summary, pill, downloadHTML)
    assert html.count("Before Technical Design review") >= 3
    assert html.count("During implementation support") >= 3
    for key in ("shortly-after-OIS", "before-TD-review", "before-IR", "before-One-Review", "before-Board"):
        assert key in html, key
    # DOCX timing_map (app.py) carries the labels too
    assert "Before Technical Design review" in appsrc
    assert "'before-One-Review': 'Before One Review'" in appsrc
