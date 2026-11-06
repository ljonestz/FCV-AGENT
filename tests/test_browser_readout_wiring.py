"""index.html is wired to static/fcv_readout.js and drops the old Summary/rail/stepper."""

from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"


def html():
    return INDEX.read_text(encoding="utf-8")


def test_module_and_styles_loaded():
    source = html()
    assert '<script src="/static/fcv_readout.js"></script>' in source
    assert '<style id="fcv-readout-style">' in source
    assert "function frApi(" in source
    assert ".fr-scorecard{" in source and ".fr-pc-hdr{" in source and "@media(max-width:760px)" in source
