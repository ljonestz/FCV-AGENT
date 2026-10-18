"""Readable block layout and internal-marker cleanup on saved model prose."""

import json
import subprocess

from tests.test_climate_lens_frontend import INDEX, _extract_js_function


def _render(text):
    source = INDEX.read_text(encoding="utf-8")
    script = (_extract_js_function(source, "normalizeVisibleText")
              + _extract_js_function(source, "md")
              + "\nprocess.stdout.write(md(" + json.dumps(text) + "));")
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_context_bullets_have_no_paragraphs_or_breaks_between_blocks():
    html = _render("### Operational Context\n\nOpening.\n\n"
                   "- **Eastern DRC:** First context.\n\n"
                   "- **Haut-Katanga:** Second context.\n\n"
                   "- **Burundi:** Third context.\n\nAcross all sites, context.")
    assert html.count("<ul>") == 1 and html.count("<li>") == 3
    assert "<br>" not in html
    assert "<p><ul>" not in html and "</ul></p>" not in html
    assert "<p><h3>" not in html and "</h3></p>" not in html
    assert "<p>Across all sites, context.</p>" in html


def test_drifted_markers_are_removed_without_losing_prose_or_percentages():
    for marker in ("%%%RISK_NARRATIVE_START%%%", "%%RISK_NARRATIVE_START%%",
                   "%%%DOC_TYPE:AF%%%"):
        html = _render("Context.\n\n" + marker + "\n\nCoverage is 50%. Next paragraph.")
        assert "RISK_NARRATIVE" not in html and "DOC_TYPE" not in html
        assert "Context." in html and "Coverage is 50%." in html
        assert "<br>" not in html


def test_multiline_prose_and_tables_keep_their_structure():
    html = _render("First line.\nSecond line.\n\n| Name | Value |\n|---|---|\n| A | 50% |")
    assert "First line.<br>Second line." in html
    assert "<table>" in html and "<td>50%</td>" in html
    assert "<p><table>" not in html and "</table></p>" not in html


def test_checkbox_list_keeps_a_valid_block_without_extra_breaks():
    html = _render("\u25a1 First check.\n\n\u25a1 Second check.\n\nNext paragraph.")
    assert html.count('<li style="list-style:none">') == 2
    assert html.count("<ul>") == 1 and "<br>" not in html
    assert "<p><li" not in html and "<p>Next paragraph.</p>" in html
