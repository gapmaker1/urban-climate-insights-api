import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer


def build_story(markdown_text: str):
    styles = getSampleStyleSheet()
    heading1 = ParagraphStyle(
        "Heading1Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=8,
        textColor="#0F172A",
    )
    heading2 = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        spaceAfter=6,
        textColor="#0F172A",
    )
    heading3 = ParagraphStyle(
        "Heading3Custom",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceAfter=4,
        textColor="#0F172A",
    )
    body = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6,
        textColor="#1F2937",
    )
    bullet = ParagraphStyle(
        "BulletCustom",
        parent=body,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3,
    )
    code = ParagraphStyle(
        "CodeCustom",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        leftIndent=8,
        textColor="#111827",
    )

    story = []
    paragraph_buffer: list[str] = []
    code_buffer: list[str] = []
    in_code_block = False

    def flush_paragraph():
        if paragraph_buffer:
            text = " ".join(part.strip() for part in paragraph_buffer if part.strip())
            if text:
                story.append(Paragraph(escape(text).replace("\n", "<br/>"), body))
            paragraph_buffer.clear()

    def flush_code():
        if code_buffer:
            story.append(Preformatted("\n".join(code_buffer), code))
            story.append(Spacer(1, 4))
            code_buffer.clear()

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()

        if line.startswith("```"):
            flush_paragraph()
            if in_code_block:
                flush_code()
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            story.append(Spacer(1, 4))
            continue

        if line.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(escape(line[2:].strip()), heading1))
            continue

        if line.startswith("## "):
            flush_paragraph()
            story.append(Spacer(1, 4))
            story.append(Paragraph(escape(line[3:].strip()), heading2))
            continue

        if line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(escape(line[4:].strip()), heading3))
            continue

        if line.startswith("- "):
            flush_paragraph()
            story.append(Paragraph(f"• {escape(line[2:].strip())}", bullet))
            continue

        paragraph_buffer.append(line)

    flush_paragraph()
    flush_code()
    return story


def render_markdown_to_pdf(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )
    markdown_text = source.read_text(encoding="utf-8")
    story = build_story(markdown_text)
    document.build(story)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python scripts/render_markdown_pdf.py <source.md> <output.pdf>")

    render_markdown_to_pdf(Path(sys.argv[1]), Path(sys.argv[2]))

