from __future__ import annotations

from climate_question_bank import CLIMATE_LITERATURE_REFERENCES


EXPECTED_TITLES = {
    "Maximizing the Peace and Social Dividends of Climate Action",
    "FCV-Sensitive Climate Action Framework",
    "Defueling Conflict",
    "Conflict-Sensitive Climate Action Compendium",
    "CCDR guidance note",
}


def test_references_cover_all_five_frameworks_with_safe_urls():
    titles = {e["title"] for e in CLIMATE_LITERATURE_REFERENCES}
    assert EXPECTED_TITLES.issubset(titles)
    for entry in CLIMATE_LITERATURE_REFERENCES:
        assert isinstance(entry["title"], str) and entry["title"]
        url = entry["url"]
        assert url is None or (isinstance(url, str) and url.startswith("https://"))
