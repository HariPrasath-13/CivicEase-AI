"""
Report Generator for CivicEase AI.
Generates comprehensive PDF, Markdown, and JSON audit reports.
"""
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import REPORTS_DIR
from database.models import AnalysisRecord, DocumentRecord
from utils.helpers import format_timestamp
from utils.logging import get_logger

logger = get_logger(__name__)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class ReportGenerator:
    """Creates downloadable audit reports in PDF, Markdown, and JSON formats."""

    def generate_markdown_report(self, doc: DocumentRecord, analysis: AnalysisRecord) -> str:
        """Builds a formatted Markdown accessibility audit report."""
        rule_metrics = analysis.rule_metrics or {}
        readability = rule_metrics.get("readability", {})
        severity_counts = rule_metrics.get("severity_counts", {"HIGH": 0, "MEDIUM": 0, "LOW": 0})
        missing_info = analysis.missing_info or {}
        breakdown = analysis.score_breakdown or {}

        lines = [
            f"# CivicEase AI — Government Document Accessibility Audit Report",
            f"**Document**: {doc.filename} | **Pages**: {doc.page_count} | **Audit Date**: {format_timestamp()}",
            f"",
            f"---",
            f"",
            f"## 1. Executive Summary",
            f"- **CivicEase AI Composite Accessibility Score**: **{analysis.composite_score} / 100** ({analysis.score_tier})",
            f"- **High Severity Barriers**: {severity_counts.get('HIGH', 0)}",
            f"- **Medium Severity Issues**: {severity_counts.get('MEDIUM', 0)}",
            f"- **Low Severity Notices**: {severity_counts.get('LOW', 0)}",
            f"- **Flesch Reading Ease**: {readability.get('flesch_reading_ease', 'N/A')} ({readability.get('interpretation', 'N/A')})",
            f"- **Average Sentence Length**: {readability.get('avg_sentence_length', 'N/A')} words",
            f"",
            f"### Score Breakdown (Weighted Dimensions)",
            f"- **Language Simplicity (20%)**: {breakdown.get('language_simplicity', 'N/A')}/100",
            f"- **Instruction Clarity (25%)**: {breakdown.get('instruction_clarity', 'N/A')}/100",
            f"- **Information Completeness (25%)**: {breakdown.get('information_completeness', 'N/A')}/100",
            f"- **Readability (15%)**: {breakdown.get('readability', 'N/A')}/100",
            f"- **Terminology (10%)**: {breakdown.get('terminology', 'N/A')}/100",
            f"- **Actionability (5%)**: {breakdown.get('actionability', 'N/A')}/100",
            f"",
            f"---",
            f"",
            f"## 2. Public Service Information Completeness Matrix",
            f"| Mandatory Field | Status | Details |",
            f"| :--- | :--- | :--- |",
        ]

        for field in missing_info.get("fields", []):
            icon = field.get("badge_icon", "")
            name = field.get("display_name", "")
            status = field.get("status", "")
            details = field.get("details", "").replace("\n", " ")
            lines.append(f"| **{name}** | {icon} {status} | {details} |")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 3. Prioritized Actionable Recommendations",
        ])

        for idx, rec in enumerate(analysis.recommendations, 1):
            lines.append(f"{idx}. **[{rec.get('priority', 'MEDIUM')} PRIORITY] {rec.get('category', '')}**")
            lines.append(f"   - **Action**: {rec.get('recommendation', '')}")
            lines.append(f"   - **Rationale**: {rec.get('rationale', '')}")
            lines.append(f"")

        lines.extend([
            f"---",
            f"",
            f"## 4. Detected Issues & Page-by-Page Traceability",
        ])

        for idx, issue in enumerate(analysis.detected_issues, 1):
            page_str = f"Page {issue.get('page', 'N/A')}"
            orig = issue.get("original_text", "").replace("\n", " ").strip()
            lines.append(f"### Issue #{idx}: {issue.get('issue', 'Issue')} ({issue.get('severity', 'MEDIUM')} Severity — {page_str})")
            lines.append(f"- **Category**: {issue.get('category', 'General')}")
            lines.append(f"- **Original Excerpt**: *\"{orig[:200]}{'...' if len(orig) > 200 else ''}\"*")
            lines.append(f"- **Problem Analysis**: {issue.get('explanation', '')}")
            if "recommendation" in issue:
                lines.append(f"- **Recommended Fix**: {issue.get('recommendation', '')}")
            elif "suggestion" in issue:
                lines.append(f"- **Recommended Fix**: {issue.get('suggestion', '')}")
            lines.append(f"")

        lines.extend([
            f"---",
            f"*Generated by CivicEase AI — Government Information Accessibility Analyzer*",
            f"*Disclaimer: The CivicEase Composite Accessibility Score is a project-defined multi-metric index and does not represent an official government statutory standard.*"
        ])

        return "\n".join(lines)

    def generate_pdf_report(self, doc: DocumentRecord, analysis: AnalysisRecord) -> bytes:
        """Generates a professional PDF report with tables and styles."""
        if not HAS_REPORTLAB:
            # Fallback to UTF-8 encoded text buffer
            md_content = self.generate_markdown_report(doc, analysis)
            return md_content.encode("utf-8")

        buffer = io.BytesIO()
        doc_template = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1E3A8A")
        )
        h2_style = ParagraphStyle(
            "Heading2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0F766E"),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1F2937")
        )
        table_header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=colors.white
        )

        story = []

        # Header Title
        story.append(Paragraph("CivicEase AI — Government Accessibility Audit Report", title_style))
        story.append(Paragraph(f"Document: <b>{doc.filename}</b> | Pages: {doc.page_count} | Generated: {format_timestamp()}", body_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=12))

        # Executive Metrics Table
        rule_metrics = analysis.rule_metrics or {}
        readability = rule_metrics.get("readability", {})
        severity_counts = rule_metrics.get("severity_counts", {"HIGH": 0, "MEDIUM": 0, "LOW": 0})
        
        exec_data = [
            [
                Paragraph("<b>CivicEase Accessibility Score:</b>", body_style),
                Paragraph(f"<b>{analysis.composite_score} / 100 ({analysis.score_tier})</b>", body_style),
                Paragraph("<b>High Severity Issues:</b>", body_style),
                Paragraph(f"<b>{severity_counts.get('HIGH', 0)}</b>", body_style)
            ],
            [
                Paragraph("<b>Flesch Reading Ease:</b>", body_style),
                Paragraph(f"{readability.get('flesch_reading_ease', 'N/A')} ({readability.get('interpretation', 'N/A')})", body_style),
                Paragraph("<b>Medium Severity Issues:</b>", body_style),
                Paragraph(f"{severity_counts.get('MEDIUM', 0)}", body_style)
            ],
            [
                Paragraph("<b>Avg Sentence Length:</b>", body_style),
                Paragraph(f"{readability.get('avg_sentence_length', 'N/A')} words", body_style),
                Paragraph("<b>Low Severity Issues:</b>", body_style),
                Paragraph(f"{severity_counts.get('LOW', 0)}", body_style)
            ]
        ]
        exec_table = Table(exec_data, colWidths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.6 * inch])
        exec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F4F6")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(exec_table)
        story.append(Spacer(1, 10))

        # Completeness Matrix
        story.append(Paragraph("1. Public Service Information Completeness", h2_style))
        matrix_rows = [[
            Paragraph("Service Dimension", table_header_style),
            Paragraph("Status", table_header_style),
            Paragraph("Audit Finding", table_header_style)
        ]]
        for f in (analysis.missing_info or {}).get("fields", []):
            status_text = f"{f.get('badge_icon', '')} {f.get('status', '')}"
            matrix_rows.append([
                Paragraph(f"<b>{f.get('display_name', '')}</b>", body_style),
                Paragraph(status_text, body_style),
                Paragraph(f.get("details", "")[:120], body_style),
            ])
        matrix_table = Table(matrix_rows, colWidths=[2.0 * inch, 1.2 * inch, 3.8 * inch])
        matrix_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(matrix_table)
        story.append(Spacer(1, 10))

        # Recommendations
        story.append(Paragraph("2. Actionable Improvement Recommendations", h2_style))
        for idx, rec in enumerate(analysis.recommendations[:5], 1):
            p_text = f"<b>{idx}. [{rec.get('priority', 'MED')}] {rec.get('category', '')}:</b> {rec.get('recommendation', '')}"
            story.append(Paragraph(p_text, body_style))
            story.append(Spacer(1, 3))

        # Build document
        doc_template.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes


# Global instance
report_generator = ReportGenerator()
