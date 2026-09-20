"""Render the standard FCV management projection as print HTML or editable Word.

Callers must first admit the bundle through the canonical Stage 3 validator.
The two formats share one projection and never modify the detailed assessment.
"""

from html import escape
from io import BytesIO
import re
from typing import Any

from docx import Document
from docx.shared import Mm, Pt, RGBColor


ADVISORY = (
    "AI-assisted suggestions for professional review, not requirements. "
    "Assess their relevance with the task team and relevant specialists."
)
INTERPRETATION = (
    "Sensitivity concerns how the project is designed for its FCV context. "
    "Responsiveness concerns contributions to FCV drivers; it is not an expectation "
    "for every operation."
)
DETAIL_NOTE = (
    "This brief presents the leading action for each priority. See the full "
    "assessment for all actions, supporting evidence, formal ratings and suggested wording."
)


def _text(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("A complete validated management brief is required.")
    return value.strip()


def _projection(readout: dict, priorities: list) -> dict:
    """Select the same concise fields in both export formats, without truncation."""
    if not isinstance(readout, dict) or not isinstance(priorities, list):
        raise ValueError("A complete validated management brief is required.")
    if not 1 <= len(priorities) <= 5:
        raise ValueError("A management brief requires one to five priorities.")
    strengths_raw = readout.get("strengths")
    if not isinstance(strengths_raw, list) or len(strengths_raw) > 3:
        raise ValueError("A management brief supports up to three strengths.")
    strengths = []
    for strength in strengths_raw:
        if not isinstance(strength, dict):
            raise ValueError("Invalid strength.")
        strengths.append((_text(strength.get("title")), _text(strength.get("text"))))
    cards = []
    for priority in priorities:
        concise = priority.get("concise") if isinstance(priority, dict) else None
        if not isinstance(concise, dict):
            raise ValueError("Every priority needs an admitted concise projection.")
        actions = concise.get("how")
        if not isinstance(actions, list) or not actions:
            raise ValueError("Every priority needs a leading action.")
        cards.append({
            "title": _text(concise.get("title")),
            "why": _text(concise.get("why")),
            "action": _text(actions[0]),
        })
    return {
        "headline": _text(readout.get("headline")),
        "overview": _text(readout.get("overview")),
        "strengths": strengths,
        "priorities": cards,
    }


def render_management_brief_html(readout: dict, priorities: list) -> str:
    """Return self-contained, escaped A4 HTML suitable for Print / Save as PDF."""
    brief = _projection(readout, priorities)
    parts = [
        '<!doctype html><html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>FCV management brief</title>',
        '<style>body{font:11pt/1.35 Arial,sans-serif;color:#172536;max-width:760px;',
        'margin:32px auto;padding:0 20px;overflow-wrap:anywhere}',
        'h1{font-size:19pt;color:#000;margin:0 0 12px}h2{font-size:12pt;color:#000;',
        'margin:16px 0 6px}h3{font-size:11pt;color:#000;margin:0 0 4px}',
        'p{margin:0 0 8px}li{margin-bottom:4px}.priority{margin-bottom:10px;',
        'break-inside:avoid}.note{font-size:9pt;color:#435166}',
        '@page{size:A4;margin:16mm}@media print{body{margin:0;padding:0;',
        'max-width:none;font-size:10.5pt;line-height:1.25}h1{font-size:16pt}',
        'h2{margin-top:10px}.priority{margin-bottom:8px}p{margin-bottom:5px}}</style>',
        '</head><body><main><h1>FCV management brief</h1>',
        f'<p><strong>{escape(brief["headline"])}</strong></p>',
        f'<p>{escape(brief["overview"])}</p>',
    ]
    if brief["strengths"]:
        parts.append('<h2>What the project does well</h2><ul>')
        for title, text in brief["strengths"]:
            parts.append(f'<li><strong>{escape(title)}:</strong> {escape(text)}</li>')
        parts.append('</ul>')
    parts.append('<h2>Suggested priorities</h2>')
    for number, card in enumerate(brief["priorities"], 1):
        parts.extend([
            f'<section class="priority"><h3>{number}. {escape(card["title"])}</h3>',
            f'<p><strong>Why it matters:</strong> {escape(card["why"])}</p>',
            f'<p><strong>Suggested action:</strong> {escape(card["action"])}</p></section>',
        ])
    parts.extend(f'<p class="note">{escape(text)}</p>' for text in (
        INTERPRETATION, DETAIL_NOTE, ADVISORY,
    ))
    parts.append('</main></body></html>')
    return ''.join(parts)


def _paragraph(document, text: str, *, label: str = "", style=None):
    """Use a bold lead-in while keeping body text editable and free of markup."""
    paragraph = document.add_paragraph(style=style)
    if label:
        paragraph.add_run(label + " ").bold = True
        paragraph.add_run(text)
    else:
        first = re.match(r".*?[.!?](?:\s|$)", text)
        end = first.end() if first else len(text)
        paragraph.add_run(text[:end]).bold = True
        paragraph.add_run(text[end:])
    return paragraph


def render_management_brief_docx(readout: dict, priorities: list) -> bytes:
    """Return an editable A4 brief; allow overflow rather than cutting findings."""
    brief = _projection(readout, priorities)
    document = Document()
    document.core_properties.title = "FCV management brief"
    document.core_properties.author = ""
    document.core_properties.last_modified_by = ""
    section = document.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = section.bottom_margin = Mm(16)
    section.left_margin = section.right_margin = Mm(17)
    for name in ("Normal", "Title", "Heading 1", "Heading 2", "List Bullet"):
        style = document.styles[name]
        style.font.name = "Arial"
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_after = Pt(4)
    normal = document.styles["Normal"]
    normal.font.size = Pt(10.5)
    normal.paragraph_format.line_spacing = 1.05
    normal.paragraph_format.widow_control = True
    document.styles["Title"].font.size = Pt(17)
    # Some bundled Word templates put an accent border under the Title style.
    for border in document.styles["Title"].element.xpath(".//w:pBdr"):
        border.getparent().remove(border)
    for name, size in (("Heading 1", 11.5), ("Heading 2", 10.5)):
        style = document.styles[name]
        style.font.size = Pt(size)
        style.font.bold = True
        style.paragraph_format.space_before = Pt(7)
        style.paragraph_format.keep_with_next = True
    document.add_paragraph("FCV management brief", style="Title")
    _paragraph(document, brief["headline"])
    _paragraph(document, brief["overview"])
    if brief["strengths"]:
        document.add_heading("What the project does well", level=1)
        for title, text in brief["strengths"]:
            _paragraph(document, text, label=title + ":", style="List Bullet")
    document.add_heading("Suggested priorities", level=1)
    for number, card in enumerate(brief["priorities"], 1):
        document.add_heading(f'{number}. {card["title"]}', level=2)
        reason = _paragraph(document, card["why"], label="Why it matters:")
        reason.paragraph_format.keep_with_next = True
        _paragraph(document, card["action"], label="Suggested action:")
    for text in (INTERPRETATION, DETAIL_NOTE, ADVISORY):
        paragraph = document.add_paragraph(text)
        for run in paragraph.runs:
            run.font.size = Pt(8.5)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()
