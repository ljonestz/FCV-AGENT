from live_source_policy import (
    CAUTION_NOTE,
    country_relevance,
    extract_project_ids,
    is_denied,
    is_own_project_source,
    publication_date,
    safe_public_url,
    source_type,
    trust_tier,
)


def test_tiers():
    assert trust_tier("https://www.crisisgroup.org/africa/x") == "standard"
    assert trust_tier("https://apnews.com/article/x") == "standard"
    assert trust_tier("https://moa.gov.et/report") == "standard"
    assert trust_tier("https://www.ox.ac.uk/paper") == "standard"
    assert trust_tier("https://example-blog.net/post") == "caution"
    assert trust_tier("https://army.mil/x") == "caution"


def test_spoofed_hosts_are_not_standard():
    for url in ("https://reuters.com.evil.example/a", "https://notworldbank.org/a"):
        assert trust_tier(url) == "caution"
    assert safe_public_url("https://worldbank.org@evil.example/a") == ""


def test_deny_list_includes_subdomains():
    assert is_denied("https://m.facebook.com/p") and is_denied("https://x.blogspot.com/a")
    assert not is_denied("https://www.reuters.com/a")


def test_source_types():
    assert source_type("https://documents.worldbank.org/x") == "world-bank"
    assert source_type("https://reliefweb.int/x") == "un"
    assert source_type("https://www.reuters.com/x") == "news"
    assert source_type("https://acleddata.com/x") == "research"
    assert source_type("https://www.icrc.org/x") == "humanitarian"
    assert source_type("https://www.nature.com/x") == "scientific"
    assert source_type("https://foo.gov.ng/x") == "government"
    assert source_type("https://random.example/x") == "other"


def test_publication_date_reads_page_age_and_blanks_relative():
    assert publication_date({"page_age": "2026-10-27"}) == "2026-10-27"
    assert publication_date({"page_age": "3 days ago"}) == ""


def test_country_relevance_disambiguates():
    assert country_relevance("Nigeria", "Niger floods 2026", "Niger saw floods") == (False, False)
    assert country_relevance("Niger", "Sahel floods", "Niger saw floods") == (True, False)
    assert country_relevance("Kenya", "East Africa drought", "Regional drought") == (False, True)


def test_caution_note_copy():
    assert CAUTION_NOTE == ("Source is outside the standard trusted list; "
                            "interpret with caution and check the original.")


def test_world_bank_inverted_names_match_short_names():
    cases = {
        "Yemen, Republic of": "Floods displaced families in Yemen.",
        "Egypt, Arab Republic of": "Heat stress in Egypt rose.",
        "Iran, Islamic Republic of": "Drought in Iran deepened.",
        "Venezuela, RB": "Rainfall in Venezuela fell.",
        "Gambia, The": "Coastal erosion in The Gambia accelerated.",
    }
    for country, text in cases.items():
        assert country_relevance(country, "Climate report", text) == (True, False), country


def test_inverted_congo_names_use_drc_and_roc_rules():
    drc_text = "Floods hit the Democratic Republic of the Congo."
    roc_text = "Floods hit Brazzaville in the Republic of the Congo."
    for drc in ("Congo, Democratic Republic of", "Congo, Dem. Rep."):
        assert country_relevance(drc, "Report", drc_text) == (True, False), drc
        assert country_relevance(drc, "Report", roc_text) == (False, False), drc
    for roc in ("Congo, Republic of", "Congo, Rep."):
        assert country_relevance(roc, "Report", roc_text) == (True, False), roc
        assert country_relevance(roc, "Report", drc_text) == (False, False), roc


def test_sudan_and_south_sudan_are_disambiguated():
    assert country_relevance("Sudan", "Report", "Floods hit South Sudan.") == (False, False)
    assert country_relevance("Sudan", "Report", "Floods hit Sudan.") == (True, False)
    assert country_relevance("Sudan", "Report", "Floods hit Sudan and South Sudan.") == (True, False)
    assert country_relevance("South Sudan", "Report", "Floods hit South Sudan.") == (True, False)
    assert country_relevance("South Sudan", "Report", "Floods hit Darfur, Sudan.") == (False, False)
    assert country_relevance("Sudan, Republic of", "Report", "Floods hit South Sudan.") == (False, False)


def test_deny_list_covers_short_links_and_blogspot_cctlds():
    for url in (
        "https://youtu.be/abc", "https://fb.com/p", "https://www.threads.net/@x",
        "https://vk.com/wall", "https://someone.tumblr.com/post",
        "https://x.blogspot.co.uk/a", "https://x.blogspot.fr/a", "https://blogspot.de/a",
    ):
        assert is_denied(url), url
    assert not is_denied("https://notblogspot.example/a")
    assert not is_denied("https://www.reuters.com/a")


def test_publication_date_skips_relative_value_and_continues():
    assert publication_date({"date": "3 days ago", "page_age": "2026-10-01"}) == "2026-10-01"
    assert publication_date({"publication_date": "2 weeks ago", "date": "3 days ago"}) == ""


def test_extract_project_ids_unique_ordered_upper():
    text = "Project P179017 and P123456, again P179017. Not P1790170 or XP111111."
    assert extract_project_ids(text) == ["P179017", "P123456"]
    assert extract_project_ids("") == []
    many = " ".join(f"P{100000 + i}" for i in range(20))
    assert len(extract_project_ids(many)) == 8
    assert len(extract_project_ids(many, limit=3)) == 3


def test_own_project_source_title_and_url_matches():
    ids = ["P179017"]
    assert is_own_project_source(
        "https://x.example/a", "The World Bank Guinea Water and Sanitation Project (P179017)", ids
    )
    assert is_own_project_source(
        "https://documents1.worldbank.org/curated/en/P179017-36e7abc/pad.pdf", "PAD", ids
    )
    assert is_own_project_source("https://projects.worldbank.org/x?id=p179017", "Page", ids)


def test_own_project_source_no_false_matches():
    ids = ["P179017"]
    assert not is_own_project_source("https://x.example/P1790170", "Project P1790170", ids)
    assert not is_own_project_source("https://x.example/XP179017", "XP179017", ids)
    assert not is_own_project_source("https://x.example/a", "P179017", [])
    assert not is_own_project_source("https://x.example/a", "Guinea water", ids)

