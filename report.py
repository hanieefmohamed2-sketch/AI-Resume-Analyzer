"""
report.py

Generates a downloadable PDF report from analysis results, using
ReportLab's Platypus API for automatic text flow and page breaks.
"""

import io

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def _build_styles() -> dict:
    """
    Builds our custom paragraph styles, based on ReportLab's default
    stylesheet, overridden with our project's color/font choices.
    """
    base = getSampleStyleSheet()

    base.add(ParagraphStyle(
        name="ReportTitle",
        parent=base["Title"],
        textColor=colors.HexColor("#2563EB"),
        fontSize=22,
    ))

    base.add(ParagraphStyle(
        name="SectionHeading",
        parent=base["Heading2"],
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=16,
        spaceAfter=6,
    ))

    base.add(ParagraphStyle(
        name="BodyTextCustom",
        parent=base["BodyText"],
        spaceAfter=4,
    ))

    return base


def _bullet_list(items: list, styles: dict) -> list:
    """Converts a list of strings into a list of bullet-point Paragraphs."""
    return [Paragraph(f"&bull; {item}", styles["BodyTextCustom"]) for item in items]


def generate_pdf_report(result: dict, filename: str) -> bytes:
    """
    Builds a complete PDF report from a full analysis result dict
    (the nested structure returned by analyzer.run_full_analysis()).

    Args:
        result: The full analysis result dictionary.
        filename: The original resume's filename, shown in the report header.

    Returns:
        The generated PDF as raw bytes, ready for st.download_button().
    """
    ai_data = result["ai_analysis"]
    ats_data = result["rule_based_ats"]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = _build_styles()
    story = []

    # ---- Title & meta ----
    story.append(Paragraph("AI Resume Analysis Report", styles["ReportTitle"]))
    story.append(Paragraph(f"File: {filename}", styles["BodyTextCustom"]))
    story.append(Spacer(1, 0.2 * inch))

    # ---- Scores table ----
    score_table = Table(
        [
            ["AI ATS Score", "Rule-Based ATS Score"],
            [f"{ai_data.get('ats_score', 'N/A')}/100", f"{ats_data.get('total_score', 'N/A')}/100"],
        ],
        colWidths=[2.5 * inch, 2.5 * inch],
    )
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 1), (-1, 1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.25 * inch))

    # ---- Summary ----
    story.append(Paragraph("Summary", styles["SectionHeading"]))
    story.append(Paragraph(ai_data.get("summary", "No summary available."), styles["BodyTextCustom"]))

    # ---- Skills ----
    story.append(Paragraph("Skills Detected", styles["SectionHeading"]))
    story.append(Paragraph(", ".join(result.get("detected_skills", [])) or "None detected.", styles["BodyTextCustom"]))

    story.append(Paragraph("Missing Skills", styles["SectionHeading"]))
    story.append(Paragraph(", ".join(ai_data.get("missing_skills", [])) or "None identified.", styles["BodyTextCustom"]))

    # ---- Strengths / Weaknesses ----
    story.append(Paragraph("Strengths", styles["SectionHeading"]))
    story.extend(_bullet_list(ai_data.get("strengths", []), styles))

    story.append(Paragraph("Weaknesses", styles["SectionHeading"]))
    story.extend(_bullet_list(ai_data.get("weaknesses", []), styles))

    # ---- Improvement suggestions ----
    story.append(Paragraph("Improvement Suggestions", styles["SectionHeading"]))
    story.extend(_bullet_list(result.get("improvement_suggestions", []), styles))

    # ---- Growth plan ----
    story.append(Paragraph("Recommended Certifications", styles["SectionHeading"]))
    story.extend(_bullet_list(ai_data.get("recommended_certifications", []), styles))

    story.append(Paragraph("Suggested Projects", styles["SectionHeading"]))
    story.extend(_bullet_list(ai_data.get("suggested_projects", []), styles))

    story.append(Paragraph("Recommended Job Roles", styles["SectionHeading"]))
    story.append(Paragraph(", ".join(ai_data.get("recommended_roles", [])) or "None identified.", styles["BodyTextCustom"]))

    # ---- Interview questions ----
    story.append(Paragraph("Likely Interview Questions", styles["SectionHeading"]))
    for i, q in enumerate(result.get("interview_questions", []), start=1):
        story.append(Paragraph(
            f"<b>{i}. [{q.get('type', 'general').title()}]</b> {q.get('question', '')}",
            styles["BodyTextCustom"],
        ))
        story.append(Paragraph(
            f"<i>Based on: {q.get('based_on', '')}</i>",
            styles["BodyTextCustom"],
        ))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes