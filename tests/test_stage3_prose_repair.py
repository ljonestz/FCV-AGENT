"""Stage 3 opening-section list detection and safe prose repair."""
import re

import stage3_prose as sp

LISTY = """## EXECUTIVE SUMMARY

### Opening Assessment

**Verdict sentence.**

### Operational Context

**Context thesis.** Connected prose about the CNRD transition and 30 percent tariffs.

### Strengths

**Strengths lead.** Several measures respond to MEHH interference:
- HEIS for procurement;
- a PCU in MEHH.

### Gaps

**Five gaps stand out.**
1. **No early warning.** Nothing monitors reversal of the 2026 tariff step.
2. **SEA/SH.** No action plan for 1,500 workers.

%%%PRIORITIES_START%%%
"""


def _fake_ok(prompt):
    body = prompt[len(sp.REPAIR_INSTRUCTIONS) + 2:]
    body = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", body, flags=re.MULTILINE)
    return re.sub(r"\*\*([^*\n]{2,60})[.:]\*\*(?=\s)", r"\1 is a concern:", body)


def test_detects_only_list_sections():
    assert [s[0] for s in sp.listy_sections(LISTY)] == ["### Strengths", "### Gaps"]


def test_repair_replaces_list_sections_and_keeps_rest():
    out, report = sp.repair(LISTY, _fake_ok)
    assert report["repaired"] is True
    assert sp.listy_sections(out) == []
    assert "Connected prose about the CNRD transition" in out
    assert out.rstrip().endswith("%%%PRIORITIES_START%%%")


def test_repair_rejects_dropped_figure_and_keeps_original():
    out, report = sp.repair(LISTY, lambda p: _fake_ok(p).replace("1,500", "many"))
    assert report["repaired"] is False and report["reason"].startswith("figures_missing")
    assert out == LISTY


def test_repair_rejects_dropped_acronym_and_failed_call():
    out, report = sp.repair(LISTY, lambda p: _fake_ok(p).replace("HEIS", "support"))
    assert out == LISTY and report["reason"].startswith("terms_missing")

    def boom(_):
        raise RuntimeError("down")

    out, report = sp.repair(LISTY, boom)
    assert out == LISTY and report["reason"] == "call_failed:RuntimeError"


def test_no_call_when_already_prose():
    prose = LISTY.split("### Strengths")[0]
    out, report = sp.repair(prose, lambda p: (_ for _ in ()).throw(AssertionError("should not call")))
    assert out == prose and report["listy"] == []


def test_repair_events_can_be_disabled(monkeypatch):
    import app
    monkeypatch.setenv("FCV_STAGE3_PROSE_REPAIR", "0")
    holder = {}
    assert list(app._stage3_prose_repair_events(LISTY, "t", holder)) == []
    assert holder["text"] == LISTY


def test_missing_headings_reported():
    assert sp.missing_headings(LISTY) == []
    assert sp.missing_headings("## EXECUTIVE SUMMARY\n\n**All prose, no subheadings.**\n") == ["Operational Context", "Strengths", "Gaps"]
