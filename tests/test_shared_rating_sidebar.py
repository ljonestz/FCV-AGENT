"""Shared sidebar layout with native Climate rating categories."""

import json
import re
import subprocess

from tests.test_climate_lens_frontend import INDEX, _extract_js_function, _js_escape_helper


def render_cards(responsiveness="moderate"):
    source = INDEX.read_text(encoding="utf-8")
    reader = {"judgments": [
        {"dimension": "sensitivity", "value": "moderate", "rationale": "Recognises risk."},
        {"dimension": "responsiveness", "value": responsiveness, "rationale": "Scope matters."},
    ]}
    script = (_js_escape_helper()
              + _extract_js_function(source, "climateVerifiedRatingCards")
              + "\nconsole.log(climateVerifiedRatingCards(" + json.dumps(reader) + "));")
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_verified_climate_has_two_native_rating_cards():
    html = render_cards()
    assert 'data-rating-key="climate-sensitivity"' in html
    assert 'data-rating-key="climate-responsiveness"' in html
    assert "Climate &amp; FCV sensitivity" in html
    assert "Moderate contribution" in html
    assert "Recognises risk." in html and "Scope matters." in html
    assert html.count('aria-valuemax="5"') == 2
    assert "integration rating" not in html


def test_not_expected_and_unclear_are_not_low_responsiveness_scores():
    for value, label in [("not_expected", "Not expected"), ("unclear", "Unclear")]:
        html = render_cards(value).split('data-rating-key="climate-responsiveness"')[1]
        assert label in html
        assert 'role="progressbar"' not in html
        assert "Scope matters." in html


def test_sidebar_glosses_are_short_and_full_rationale_is_collapsed():
    html = render_cards()
    glosses = re.findall(r'<p class="stage3-rating-meaning">(.*?)</p>', html)
    assert len(glosses) == 2
    assert all(len(gloss.split()) <= 20 for gloss in glosses)
    assert "Recognises risk." not in glosses
    assert html.count('<details class="stage3-rating-explanation">') == 2
    assert "<summary>Why this rating</summary>" in html


def test_responsiveness_is_additional_contribution_and_legacy_is_unscored():
    html = render_cards("emerging").split('data-rating-key="climate-responsiveness"')[1]
    assert "Emerging (legacy scale)" in html
    assert 'role="progressbar"' not in html
    assert "Contributing to responsiveness is often a sign of going above and beyond." in html
    assert "The expected contribution depends on the project&#039;s scope." in html


def test_responsiveness_contract_has_five_levels_and_unscored_exceptions():
    from sector_lenses.climate_judgments import ALLOWED
    assert ALLOWED["responsiveness"] == {
        "very_limited", "limited", "moderate", "strong", "very_strong",
        "not_expected", "unclear",
    }


def test_summary_keeps_shared_sidebar_and_verified_climate_uses_it():
    source = INDEX.read_text(encoding="utf-8")
    assert '.stage3-reading-shell[data-stage3-view="summary"]{grid-template-columns:1fr}' not in source
    assert '.stage3-reading-shell[data-stage3-view="summary"] .stage3-rating-rail' not in source
    assert 'const _showDetailedRail=isLast;' in source
    assert 'climateVerifiedRatingCards(climateVerifiedReader)' in source


def test_live_detailed_avoids_duplicate_old_sensitivity_panel():
    source = INDEX.read_text(encoding="utf-8")
    assert 'renderClimateVerifiedAssessment(climateVerifiedReader,true)' in source
    assert "ratingsInSidebar?'':" in _extract_js_function(source, "renderClimateVerifiedAssessment")
