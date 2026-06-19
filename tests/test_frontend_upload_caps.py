"""Static checks for upload-zone caps in the single-page frontend."""
from pathlib import Path


INDEX_HTML = Path(__file__).resolve().parents[1] / "index.html"


def _html():
    return INDEX_HTML.read_text(encoding="utf-8")


def test_primary_upload_is_single_file():
    html = _html()
    primary_input = '<input type="file" id="ip" name="project_doc"'
    start = html.index(primary_input)
    end = html.index(">", start)
    assert "multiple" not in html[start:end]


def test_package_and_context_caps_are_defined():
    html = _html()
    assert "const MAX_PRIMARY = 1;" in html
    assert "const MAX_PACK = 10;" in html
    assert "const MAX_CTX = 3;" in html


def test_formdata_fallback_collects_package_docs():
    html = _html()
    assert "fd.getAll('package_doc')" in html


def test_polling_fallback_uses_named_caps():
    html = _html()
    assert "pkF.length < MAX_PACK" in html
    assert "cF.length < MAX_CTX" in html
