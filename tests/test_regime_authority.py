"""Phase 6 — authority_basis recommendation field (dual-regime §5.5; shared with climate §12)."""

from pathlib import Path

import app as app_module


def _block(extra):
    return (
        '%%%JSON_START%%%{"fcv_rating":"Moderately addressed",'
        '"fcv_responsiveness_rating":"Emerging","sensitivity_summary":"x",'
        '"responsiveness_summary":"y","risk_exposure":{"risks_to":"a","risks_from":"b"},'
        '"priorities":[{"title":"T","fcv_dimension":"Contextual","tag":"[S]","the_gap":"g",'
        '"why_it_matters":"w","actions":[],"who_acts":"TTL","when":"soon","resources":"r",'
        '"pad_sections":"IV"' + extra + '}]}%%%JSON_END%%%'
    )


def test_authority_basis_defaults_reviewer_judgment_when_missing():
    r = app_module.extract_priorities(_block(""), uploaded_doc_names=[])
    assert r["priorities"][0]["authority_basis"] == "reviewer_judgment"


def test_authority_basis_invalid_coerced():
    r = app_module.extract_priorities(_block(',"authority_basis":"made-up"'), uploaded_doc_names=[])
    assert r["priorities"][0]["authority_basis"] == "reviewer_judgment"


def test_authority_basis_valid_preserved_and_normalised():
    r = app_module.extract_priorities(_block(',"authority_basis":"Directive"'), uploaded_doc_names=[])
    assert r["priorities"][0]["authority_basis"] == "directive"


def test_authority_basis_in_schema_ui_and_docx():
    assert "authority_basis" in app_module.DEFAULT_PROMPTS["3"]
    root = Path(__file__).resolve().parent.parent
    html = (root / "index.html").read_text(encoding="utf-8")
    assert "authority_basis" in html            # UI chip + downloadHTML export
    appsrc = (root / "app.py").read_text(encoding="utf-8")
    # validation + Stage 3 schema + DOCX export = at least 3 references
    assert appsrc.count("authority_basis") >= 3
