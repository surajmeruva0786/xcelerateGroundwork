"""
PDF report generation for industrial plot compliance.

We use ReportLab to build a structured, printable summary that can be
attached to government files and shared with CSIDC officials.
"""

from __future__ import annotations

from io import BytesIO
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from app.models.models import IndustrialArea, SatelliteRun, PlotAnalysisResult, Plot


def _format_percentage(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f}%"


def generate_satellite_run_report_pdf(
    db: Session,
    satellite_run: SatelliteRun,
) -> bytes:
    """Generate a multi-plot compliance report for a given satellite run."""
    industrial_area: IndustrialArea = satellite_run.industrial_area

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    story: List = []

    title = f"Industrial Land Compliance Report – {industrial_area.name}"
    story.append(Paragraph(title, styles["Title"]))
    story.append(
        Paragraph(
            f"Analysis period: T1 = {satellite_run.t1_date.date()} | "
            f"T2 = {satellite_run.t2_date.date()}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 12))

    # Aggregate metrics
    results: List[PlotAnalysisResult] = (
        db.query(PlotAnalysisResult)
        .filter(PlotAnalysisResult.satellite_run_id == satellite_run.id)
        .all()
    )

    total_plots = len(results)
    enc_plots = sum(1 for r in results if r.has_encroachment)
    vacant_plots = sum(1 for r in results if r.is_vacant)
    closed_plots = sum(1 for r in results if r.is_closed)
    high_risk = sum(1 for r in results if r.risk_level == "HIGH")
    medium_risk = sum(1 for r in results if r.risk_level == "MEDIUM")

    story.append(Paragraph("Compliance Summary", styles["Heading2"]))

    summary_data = [
        ["Total plots", str(total_plots)],
        ["Encroached plots", f"{enc_plots}"],
        ["Vacant plots", f"{vacant_plots}"],
        ["Closed plots (approx.)", f"{closed_plots}"],
        ["High risk plots", f"{high_risk}"],
        ["Medium risk plots", f"{medium_risk}"],
    ]
    table = Table(summary_data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 18))

    # Encroached plots list
    story.append(Paragraph("Encroached Plots", styles["Heading2"]))

    enc_rows = [["Plot No.", "Encroached Area (m²)", "Risk Level", "Recommended Action"]]
    for r in results:
        if not r.has_encroachment:
            continue
        plot: Plot = r.plot
        enc_rows.append(
            [
                plot.plot_number,
                f"{r.encroached_area_m2:.1f}",
                r.risk_level,
                r.recommended_action,
            ]
        )

    if len(enc_rows) == 1:
        story.append(Paragraph("No encroachments detected in this run.", styles["Normal"]))
    else:
        enc_table = Table(enc_rows, hAlign="LEFT")
        enc_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(enc_table)

    story.append(Spacer(1, 18))

    # Per-plot snapshot
    story.append(Paragraph("Per-Plot Metrics", styles["Heading2"]))

    per_plot_rows = [
        [
            "Plot No.",
            "Built-up (m²)",
            "Vacant %",
            "Enc. (m²)",
            "Risk",
            "NDVI",
            "NDBI",
        ]
    ]
    for r in results:
        plot: Plot = r.plot
        per_plot_rows.append(
            [
                plot.plot_number,
                f"{r.built_up_area_m2:.1f}",
                _format_percentage(r.vacant_percentage),
                f"{r.encroached_area_m2:.1f}",
                r.risk_level,
                f"{r.mean_ndvi:.2f}",
                f"{r.mean_ndbi:.2f}",
            ]
        )

    per_plot_table = Table(per_plot_rows, hAlign="LEFT", repeatRows=1)
    per_plot_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(per_plot_table)

    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "Note: Built-up and vegetation metrics are derived from Sentinel-2 NDVI/NDBI "
            "indices with cloud-masked, monthly composites.",
            styles["Italic"],
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


