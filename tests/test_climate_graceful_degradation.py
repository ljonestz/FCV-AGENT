"""Regression tests for the 2026-10-18 Honduras PAD production incident.

Two independent deterministic defects surfaced when a PAD triggered unresolved
instrument routing plus an empty recommendation set:

1. Internal routing/provenance warning codes leaked into the reader-facing
   "Sector-lens notice" as title-cased enum prose
   (e.g. "Instrument Route Unresolved").
2. The empty-priority summary statement claimed priorities were "not admitted
   after validation" when in fact none were ever generated
   (raw_candidate_count == 0).

See memory: climate-pilot-prod-incident-2026-10-18.
"""

import app


# --- Fix 1: internal warning codes must never render as raw prose ----------

INTERNAL_INCIDENT_CODES = [
    "PACKAGE_FACT_AUTHORITY_WITHHELD",
    "SOURCE_BLOCKS_BOUNDED",
    "INSTRUMENT_ROUTE_UNRESOLVED",
    "MPA_BASE_INSTRUMENT_UNRESOLVED",
]


def test_internal_warning_codes_are_suppressed_not_titlecased():
    """The four codes that leaked on 2026-10-18 must not reach the reader."""

    messages = app._climate_source_warning_messages(INTERNAL_INCIDENT_CODES)
    assert messages == []


def test_unmapped_warning_codes_never_leak_raw_enum_text():
    """No message may contain a de-underscored, title-cased raw enum token."""

    # A fabricated, deliberately-unknown internal code must be dropped, never
    # surfaced as "Some Future Internal Code".
    messages = app._climate_source_warning_messages(["SOME_FUTURE_INTERNAL_CODE"])
    assert messages == []


def test_reader_facing_warning_codes_still_surface():
    """Allowlisted codes with genuine reader value keep their plain message."""

    regional = app._climate_source_warning_messages(["MULTI_COUNTRY_BANK_WITHHELD"])
    assert len(regional) == 1
    assert "beneficiary country" in regional[0]["message"]

    precedence = app._climate_source_warning_messages(
        ["PRIMARY_DOCUMENT_PRECEDENCE_UNRESOLVED"]
    )
    assert len(precedence) == 1
    assert precedence[0]["message"].startswith("Confirm which document")


def test_mixed_codes_surface_only_reader_facing_ones():
    """A realistic mix drops internal codes and keeps the reader-facing one."""

    mixed = ["INSTRUMENT_ROUTE_UNRESOLVED", "MULTI_COUNTRY_BANK_WITHHELD",
             "SOURCE_BLOCKS_BOUNDED"]
    messages = app._climate_source_warning_messages(mixed)
    assert len(messages) == 1
    assert "beneficiary country" in messages[0]["message"]


# --- Fix 2: empty-priority statement must not overclaim validation ----------

from sector_lenses import climate_verified_render as _render


def test_empty_summary_says_none_generated_when_no_candidates():
    """raw_candidate_count == 0 means nothing reached validation."""

    summary = _render._priority_summary([], {"raw_candidate_count": 0})
    assert summary["count"] == 0
    text = summary["statement"].lower()
    assert "generated" in text
    assert "admitted after validation" not in text


def test_empty_summary_reports_validation_when_candidates_existed():
    """raw_candidate_count > 0 but none admitted -> validation did reject them."""

    summary = _render._priority_summary(
        [], {"raw_candidate_count": 3, "admitted_count": 0}
    )
    assert summary["count"] == 0
    assert "validation" in summary["statement"].lower()


def test_empty_summary_without_diagnostics_is_safe():
    """Missing diagnostics must not raise and must keep a non-empty statement."""

    summary = _render._priority_summary([])
    assert summary["count"] == 0
    assert summary["statement"]


def test_populated_summary_statement_unchanged():
    """The non-empty path keeps its existing reader wording."""

    summary = _render._priority_summary([{"title": "Alpha"}, {"title": "Beta"}])
    assert summary["count"] == 2
    assert "2 main operational priorities" in summary["statement"]
