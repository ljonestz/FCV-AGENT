"""2026-11-27 (owner): Stage 2 no longer shows the S/R tags, the FCV Strategy shift notes or the "Reading
this assessment" legend. The prompt is unchanged (ITS parity); index.html strips them for display."""
import json
import re
import subprocess
from pathlib import Path

INDEX = (Path(__file__).resolve().parent.parent / "index.html").read_text(encoding="utf-8")


def _strip(text: str) -> str:
    start = INDEX.index("  const STAGE2_LEGACY_COL_RE")
    end = INDEX.index("  // Wraps \"FCV Sensitivity\"", start)
    script = INDEX[start:end] + f"\nprocess.stdout.write(stripStage2LegacyTags({json.dumps(text)}));"
    res = subprocess.run(["node", "-"], input=script, capture_output=True, text=True, encoding="utf-8")
    assert res.returncode == 0, res.stderr
    return res.stdout


def test_legend_removed_and_stage2_render_strips_tags():
    assert "Reading this assessment" not in INDEX and "buildTagLegend" not in INDEX
    assert "md(stage===2 ? stripStage2LegacyTags(cleanResult) : cleanResult)" in INDEX
    assert "md(stripStage2LegacyTags(content))" in INDEX and "md(stripStage2LegacyTags(uh.recs_table))" in INDEX


def test_strip_removes_tags_and_shift_notes_in_prose():
    text = ("Record which zones are deferred and why (Good Practice Notes). **[S]** *FCV Strategy Shift: Differentiate*\n\n"
            "**Shift A is partially addressed.** **[S+R]** Tagged [R] because it builds resilience.\n\nKeep [Sources] intact.")
    out = _strip(text)
    assert "[S]" not in out and "[S+R]" not in out and "FCV Strategy Shift" not in out and "Tagged" not in out
    assert "Record which zones are deferred and why (Good Practice Notes)." in out
    assert "**Shift A is partially addressed.**" in out and "Keep [Sources] intact." in out


def test_strip_drops_sr_and_shift_table_columns():
    table = ("| # | Operational Standard | Status | S/R Tag | Shift(s) |\n|---|---|---|---|---|\n"
             "| 1 | Use DRRs | Weakly addressed | [S] | Differentiate |")
    out = _strip(table)
    rows = [r for r in out.splitlines() if r.strip()]
    assert rows[0] == "| # | Operational Standard | Status |"
    assert re.fullmatch(r"\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|", rows[1])
    assert rows[2] == "| 1 | Use DRRs | Weakly addressed |"
