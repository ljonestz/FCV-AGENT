from live_source_policy import (
    CAUTION_NOTE,
    country_relevance,
    is_denied,
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
