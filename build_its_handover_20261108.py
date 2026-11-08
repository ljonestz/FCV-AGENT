"""Build the 8 November 2026 ITS handover update: Stage 3 readout and prose,
the Climate-FCV prose layer and the climate reader fixes. House style: Arial
throughout, bold first sentence of every body paragraph, no em dashes.

Writes 20261108_ITS_Handover_prose-and-climate-reader.docx next to this script.
"""

from pathlib import Path
import re

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

FONT = "Arial"
NAVY = RGBColor(0x1F, 0x29, 0x37)
CYAN = RGBColor(0x0B, 0x6B, 0x8A)

OUT = Path(__file__).parent / "20261108_ITS_Handover_prose-and-climate-reader.docx"


def _set_font(run, size=11, bold=False, color=None):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def body(doc, text):
    """Add a body paragraph with its first sentence bolded (house rule)."""
    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(8)
    para.paragraph_format.line_spacing = 1.15
    match = re.match(r"^(.*?[.:?!])(\s+)(.*)$", text, re.DOTALL)
    if match:
        first, gap, rest = match.group(1), match.group(2), match.group(3)
        _set_font(para.add_run(first), bold=True)
        if rest:
            _set_font(para.add_run(gap + rest), bold=False)
    else:
        _set_font(para.add_run(text), bold=True)
    return para


def h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(6)
    _set_font(p.add_run(text), size=15, bold=True, color=NAVY)


def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    _set_font(p.add_run(text), size=12, bold=True, color=CYAN)


def bullet(doc, text):
    para = doc.add_paragraph(style="List Bullet")
    para.paragraph_format.space_after = Pt(4)
    match = re.match(r"^(.*?[.:?!])(\s+)(.*)$", text, re.DOTALL)
    if match:
        _set_font(para.add_run(match.group(1)), bold=True)
        _set_font(para.add_run(match.group(2) + match.group(3)), bold=False)
    else:
        _set_font(para.add_run(text), bold=True)


def table(doc, rows):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = t.cell(r, c)
            cell.text = ""
            _set_font(cell.paragraphs[0].add_run(value), size=10, bold=(r == 0))
    doc.add_paragraph()


doc = Document()
doc.styles["Normal"].font.name = FONT
doc.styles["Normal"].font.size = Pt(11)

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.LEFT
_set_font(title.add_run("FCV Project Screener - ITS Handover Update"), size=20, bold=True, color=NAVY)
sub = doc.add_paragraph()
_set_font(sub.add_run("Stage 3 readout and prose, Climate-FCV reader | 8 November 2026"), size=12, color=CYAN)

body(doc, "This note records the 8 November 2026 changes to the Render build. No ITS code was changed, because only the ITS team edits the ITS build. The changes cover a redesigned Stage 3 readout, a return to connected analytical prose in Stage 3 and on the Climate-FCV route, and four climate defects found and fixed around paid production runs. Section 9 suggests what ITS might port and in what order. The 18 October handover remains valid for everything it describes.")

h1(doc, "1. Changes at a glance")
body(doc, "Five pull requests were merged to main in the Render repository (GitHub ljonestz/FCV-AGENT) and deployed to production in sequence. The table below gives each merge commit so the ITS team can read the diffs directly, and section 10 maps every change to its file, function and tests.")
table(doc, [
    ["PR", "Commit", "What it does", "Section"],
    ["#92", "27a96e6", "Stage 3 readout redesign; per-record climate Summary admission; Stage 3 analytical prose on the core route", "2, 3, 5.1"],
    ["#93", "1ff2219", "Climate-FCV analytical prose layer (switch-controlled); 'Operationalizing climate and FCV' label", "4"],
    ["#94", "b105279", "Climate drafting completeness ignores a trailing reviewer marker; proposals stay visibly proposed", "5.2"],
    ["#95", "8d0a9af", "Climate prose layer on by default, with refinements from a blind review", "4"],
    ["#96", "f5f34ca", "Climate reader admission when the reviewer under-lists records; internal ids removed from Word verify notes", "5.3, 5.4"],
])

h1(doc, "2. Stage 3 readout redesign")
body(doc, "One readout now drives the screen view, Copy and the Share .html export on both routes. Built in static/fcv_readout.js, it mirrors the Word report. It shows a scorecard with an advisory lead, numbered sections with a jump list, priority cards with level, focus, timing and source basis, and Suggested Text blocks that each carry a Copy button. The Smaller Points, Guidance and Limitations sections start collapsed and show item counts.")
body(doc, "The normal route gains three sections. Smaller Points to Check During Preparation draws on the Stage 2 supplementary dimensions. Relevant WBG Guidance lists seven curated, link-checked resources, and Limitations records the documents used, the research retrieval date and any partial-run flag. Separately, the Country Partnership Framework (CPF) and RRA alignment panel was removed from the browser and Word views on Render, while the prompt fields that feed it are unchanged. ITS can keep or remove its own panel; removing it keeps the two builds' reports alike.")
body(doc, "The climate route shows three pinned WBG reports, each with a curated blurb. When an item is withheld, Limitations explains why, and no substitute text appears if the Summary is withheld.")

h1(doc, "3. Stage 3 analytical prose (core route)")
body(doc, "Stage 3 openings became clipped and list-like after Render moved Stage 3 to Opus 5.5 in October. Opus applied a Render-only plain management language instruction too literally. The ITS example notes the project owner supplied, produced on Sonnet 4.6, already read as the connected prose the owner wants, so the cause appears specific to Render. The ITS team should confirm this against its own current output before deciding anything.")
body(doc, "The fix is applied when the Render prompt is assembled, so the DEFAULT_PROMPTS[\"3\"] text in the repository is unchanged. The narrative is now written as connected analytical prose, and plain language applies only to the JSON summary fields. The instruction describes what makes a strong opening and gives no sample text, because sample text in earlier prompts was copied almost word for word. Three supporting changes follow: a final format check, a 48,000-token output cap (up from 32,000, because Opus thinking counts against the cap), and a one-call prose repair that is kept only if every figure and acronym survives.")
body(doc, "Render also widens the opening section word ranges at assembly. The base prompt text still carries the old ranges, so these are the one change that would alter wording the two builds share if ITS chose to adopt it. The table compares the base values with what Render now uses.")
table(doc, [
    ["Section", "Base prompt (unchanged)", "Now on Render"],
    ["Opening Assessment", "one sentence, 25-35 words", "one sentence, 35-60 words, naming the central tension"],
    ["Operational Context", "150-200 words", "180-240 words, explaining how the risks compound"],
    ["Strengths", "80-150 words", "150-220 words, one or two paragraphs"],
    ["Gaps", "100-130 words", "150-220 words, one or two paragraphs"],
])
body(doc, "Both behaviours default to on and have switches. FCV_STAGE3_PROSE_STYLE=legacy restores the previous wording, and FCV_STAGE3_PROSE_REPAIR=0 turns off the repair.")

h1(doc, "4. Climate-FCV analytical prose")
body(doc, "The climate reader text had the same problem in a different form. It read as a formulaic inventory (\"The project already builds\", \"The main remaining challenge is\") because its prompts asked for plain sentences for a first-time reader. sector_lenses/climate_prose_layer.py now adjusts the reader_compiler, bounded_analysis, judgment_review and drafting_compiler prompts at assembly. The layer changes four parts of the reader output.")
bullet(doc, "Summary. It opens with an analytical judgment naming the project's central climate-FCV tension, then explains how hazards, fragility and the design interact and what the design's value depends on.")
bullet(doc, "Register. The reader text uses connected expert prose. It leaves out internal terms and formula openers, spells out acronyms on first use, states judgments firmly where the evidence supports them, and ends without a stock closing line.")
bullet(doc, "Design responses and gaps. Each is written as connected analysis that states the condition on which the response's value depends, and planned features are described as planned.")
bullet(doc, "Suggested Text. It is written in the project document's own voice rather than as advice to the team. Proposals stay visibly proposed, with phrases such as \"The project proposes to\", \"would\" and \"to be agreed during preparation\".")
body(doc, "The evidence-binding, reader review and correction prompts are unchanged, and a test asserts this. The layer is on by default; CLIMATE_PROSE_STYLE=legacy switches it off. The operationalization judgment is now labelled \"Operationalizing climate and FCV\" and carries a one-line definition in the browser and Word views.")

h1(doc, "5. Climate defects fixed")
body(doc, "Four defects predate the prose work, and each could withhold good output or fail a run. None depends on the model, and all fixes are deterministic and covered by tests. The usual symptom is a clean-looking run whose Summary is replaced by a \"not shown\" notice, or a run that fails at the end of Stage 2.")
h2(doc, "5.1 Per-record Summary admission (#92)")
bullet(doc, "Final-reader records are now admitted one at a time; before, one failing record could withhold the whole reader. A failing narrative no longer removes a clean Summary. Numbers bind to a fact only when exactly one fact matches, corrections merge per record, and a block that names only findings withholds only those findings. Render also reserves 3,000 of its 9,000-token repair allowance for the reader correction; that is a Render budget setting, relevant to ITS only if it has the same ceiling.")
h2(doc, "5.2 Trailing reviewer marker (#94)")
bullet(doc, "A Suggested Text ending in a \"[Verify before sharing: ...]\" marker was judged incomplete and failed the whole run with DRAFTING_TEXT_INCOMPLETE. The completeness check now ignores one trailing marker but still requires the draft itself to end a sentence. It uses linear string checks after CodeQL flagged a regular expression.")
h2(doc, "5.3 Reviewer under-listing its records (#96)")
bullet(doc, "A strict consistency check withheld an admissible Summary. On a Syria run, the reviewer's object_ids list omitted SUM-002 while raising an anchored minor issue against it, and valid_reader_revision required an exact match, so it rejected the whole review. Every named record must still have an anchored issue, but anchored issues on unlisted records are now applied instead of discarding the reader.")
h2(doc, "5.4 Internal ids in Word verify notes (#96)")
bullet(doc, "The Word export now removes internal ids from verify notes, as the browser already did. Before, notes such as \"Check PF-001 and DOC-...-B-...\" reached the report. fcv_docx_style.clean_verify_note mirrors the browser rule using linear token passes, and notes without ids are left exactly as written.")

h1(doc, "6. Evidence")
body(doc, "Both prose changes were judged blind against five example notes supplied by the project owner, four of them from ITS. Model reviewers who did not know which version was which scored each output for closeness to the examples and checked for copied wording. For Stage 3, 13 replays on three projects (a Guinea water PAD, an Afghanistan health PAD and a Great Lakes additional financing and restructuring) met the standard on two projects and came close on the third. A production end-to-end run on the Guinea PAD then completed in 8.5 minutes with all headings, no lists and five priorities.")
body(doc, "For the climate route, paid production runs on Honduras, Afghanistan and Syria were compared with earlier outputs. The new prose scored 7 against 5 for closeness on Honduras and 7 against 2 on Afghanistan, and Syria was rated close to the standard. A final run on the Sahel Recovery and Stabilization additional financing Project Paper (P173830) on f5f34ca admitted the Summary and all three findings with five priorities, and its Word notes carried no internal ids.")
body(doc, "The samples are small. Most climate projects had one paid run each, so the results show direction rather than a measured rate. The records, including the blind review packets, are in output/20261108_stage3-benchmark/ and output/20261108_climate-benchmark/ in the Render working copy and are available from the project owner on request.")

h1(doc, "7. Deployment state")
bullet(doc, "Production. fcv-agent.onrender.com runs main at f5f34ca, deployed manually on 8 November; auto-deploy stays off.")
bullet(doc, "Rollback. 474b3cf is the build before this work, and 1168a8f remains the pre-climate-pilot reference.")
bullet(doc, "Test service. The climate smoke service has its spending limit set to effectively zero again, and its free plan is too slow for full runs.")

h1(doc, "8. Known limitations")
h2(doc, "Relevant to both builds")
bullet(doc, "Repetition. The climate Summary and findings still overlap in places.")
bullet(doc, "Reviewer notes. Verify notes are written by the reviewer and can keep unexpanded acronyms, and once a source's French decimal comma passed through as \"49,17 percent\".")
h2(doc, "Render only")
bullet(doc, "Memory. Production has 512 MB, and an orphaned run plus a new upload caused one out-of-memory restart on 8 November.")

h1(doc, "9. For the ITS team to consider")
body(doc, "Most changes address Render-specific causes, so the useful candidates are few. No delimiters, Stage 3 priority JSON fields, routes or knowledge-base content changed. A suggested order follows, starting with fixes that do not depend on the model.")
bullet(doc, "First, if ITS runs the verified climate pipeline. Where ITS has valid_reader_revision or an equivalent reviewer check, port 5.3; it is a one-line rule change with two tests. Then port 5.2 and 5.4, each a small self-contained function, and 5.1 if ITS still withholds the whole reader when one record fails.")
bullet(doc, "Second, optional for consistency. The Stage 3 section word ranges in section 3, the \"Operationalizing climate and FCV\" label and the readout redesign keep the two builds' reports alike. The readout is the largest of these.")
bullet(doc, "Do not copy. The Stage 3 style layer, the 48,000-token cap and the prose repair answer an Opus 5.5 behaviour. Adopt the climate prose layer only if ITS climate output shows the same inventory style.")
body(doc, "The project owner keeps a parity log of every change that affects both builds and can share the 8 November entries; the Render repository's docs/claude-journal.md holds the full record. Questions go to the project owner, Lindsey Jones.")

h1(doc, "10. Where to find each change")
body(doc, "Paths are relative to the Render repository root at f5f34ca. Run the tests with python -m pytest -q followed by the test file. On Windows, set PYTHONUTF8=1 first: without it, two tests in tests/test_climate_lens_frontend.py fail on console text encoding when they pass JavaScript to Node, not on the code.")
table(doc, [
    ["Change", "File and function", "Tests"],
    ["Readout", "static/fcv_readout.js (create, parseStage3Sections, cleanVerifyNote)", "tests/test_fcv_readout.py"],
    ["Stage 3 prose layer", "app.py: _stage3_prose_layer_enabled, _stage3_contract_text, _stage3_apply_section_specs", "tests/test_stage3_prose_layer.py"],
    ["Stage 3 prose repair", "stage3_prose.py: repair; app.py: _stage3_prose_repair_events", "tests/test_stage3_prose_repair.py"],
    ["Climate prose layer", "sector_lenses/climate_prose_layer.py: apply, called from build_verified_stage_prompt in climate_verified_prompts.py", "tests/test_climate_prose_layer.py"],
    ["5.1 admission", "sector_lenses/climate_final_reader.py: reviewed_final_reader, apply_reader_corrections; climate_verified_pipeline.py reader loop", "tests/test_climate_summary_admission.py"],
    ["5.2 marker", "sector_lenses/climate_verified_render.py: drafting_text_complete", "tests/test_climate_prose_layer.py"],
    ["5.3 under-listing", "sector_lenses/climate_final_reader.py: valid_reader_revision", "tests/test_climate_proportionate_review.py, tests/test_climate_summary_admission.py"],
    ["5.4 Word notes", "fcv_docx_style.py: clean_verify_note, clean_verify_marker", "tests/test_docx_verify_note_ids.py"],
])

doc.save(str(OUT))
print("Wrote", OUT)
