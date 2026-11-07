"""index.html is wired to static/fcv_readout.js and drops the old Summary/rail/stepper."""

import json
import subprocess
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"
MODULE = Path(__file__).resolve().parents[1] / "static" / "fcv_readout.js"


def html():
    return INDEX.read_text(encoding="utf-8")


def test_module_and_styles_loaded():
    source = html()
    assert '<script src="/static/fcv_readout.js"></script>' in source
    assert '<style id="fcv-readout-style">' in source
    assert "function frApi(" in source
    assert ".fr-scorecard{" in source and ".fr-pc-hdr{" in source and "@media(max-width:760px)" in source


def test_normal_route_uses_readout_module():
    source = html()
    assert "function renderNormalReadoutHtml(" in source
    assert "frApi().renderNormal(" in source
    assert "function renderGoDeeperHtml(idx)" in source
    assert "priorityExtras:" in source


def test_climate_route_uses_readout_module():
    source = html()
    start = source.index("function renderClimateVerifiedAssessment(")
    body = source[start:source.index("\n  }\n", start)]
    assert "frApi().renderClimate(" in body
    assert "Draft - human review required." not in body  # generic preamble removed upstream (2026-10-28)
    assert "stage3AdvisoryText('climate')" in body


def test_summary_tab_rail_and_stepper_removed():
    source = html()
    for gone in ["function stage3ViewToggleHtml(", "function renderStage3Summary(", "function renderNormalFcvSummary(",
                 "function setStage3View(", "function renderPriorityStepper(",
                 'id="priority-stepper"', 'id="priority-card-area"', "function renderClimateVerifiedSummary(",
                 "function renderSummaryPriorityAccordion("]:
        assert gone not in source, gone
    start = source.index("function renderManagementBriefControls(")
    assert "stage3View" not in source[start:source.index("}", start)]


def test_share_html_export_reuses_readout():
    source = html()
    start = source.index("async function downloadHTML(")
    body = source[start:source.index("\n  }\n", start)]
    assert "buildNormalReadout(" in body
    assert "screenerCaveatHtml()" in body
    assert "_buildExportPriorityCard" not in body


def function_body(source, signature):
    start = source.index(signature)
    return source[start:source.index("\n  }\n", start)]


def test_screen_and_export_share_normal_readout_builder():
    source = html()
    builder = function_body(source, "function buildNormalReadout(")
    for part in ["stage3NoticesHtml(", "stage3DocChecksHtml()", "renderClimateGroundingSources(", "wrapSRTerms(", "renderNormalReadoutHtml("]:
        assert part in builder, part
    notices = function_body(source, "function stage3NoticesHtml(")
    for part in ["isClosedOrCompletedProject()", "isFinalizedPAD()", "stage-awareness-badge", "state.notice"]:
        assert part in notices, part
    assert "_outBodyContent=buildNormalReadout(result);" in function_body(source, "function renderOut(")
    export = function_body(source, "async function downloadHTML(")
    assert "buildNormalReadout(stageOutputs[3]||'',true)" in export
    assert "renderNormalReadoutHtml(" not in export
    assert "priorityExtras:forExport?renderNormalExportPriorityExtras:renderNormalPriorityExtras" in source
    assert "renderGoDeeperHtml" not in function_body(source, "function renderNormalExportPriorityExtras(")


def test_print_opens_readout_disclosures():
    source = html()
    handler = function_body(source, "function installClimatePrintDisclosureHandler(")
    for sel in ["details.fr-pc", "details.fr-disc", "details.priority-context-disclosure"]:
        assert sel in handler, sel
    assert "\n  installClimatePrintDisclosureHandler(document);" in source
    assert "climatePrintDisclosureScript()" in function_body(source, "async function downloadHTML(")
    assert ".fr-pc-body,.fr-disc-body{display:block" not in source


def test_copy_text_drops_go_deeper_and_warnings():
    body = function_body(html(), "function reportPlainText(")
    assert "details.go-deeper" in body and ".warn-badge" in body


def test_removed_summary_state_is_gone():
    source = html()
    for gone in ["stage3View", "openSummaryPriority", "supportsAnyStage3Summary", "renderFcvRatingIndicators",
                 "_supportsClimateStage3", ".priority-stepper", ".ps-step", ".horizon-panel", ".summary-priority-",
                 "#summary-priority-accordion", ".stage3-viewbar", ".concise-readout", ".pi-lead"]:
        assert gone not in source, gone


def test_parser_splits_bold_lead_from_supporting_text():
    script = ("const FR=require(" + json.dumps(str(MODULE)) + ");"
              "process.stdout.write(JSON.stringify(FR.parseStage3Sections("
              + json.dumps("## Executive Summary\n\n**Verdict sentence.** More detail here.\n\n### Strengths\n\nS.")
              + ")));")
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    sections = json.loads(result.stdout)
    assert sections["snapshot"] == "Verdict sentence."
    assert any("More detail here." in o["body"] for o in sections["other"])
