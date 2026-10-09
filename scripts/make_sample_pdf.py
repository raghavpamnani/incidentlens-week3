"""Generate a reproducible synthetic PDF with headings, a table and page provenance."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
styles = getSampleStyleSheet()
styles["Title"].textColor = colors.HexColor("#173f39")
styles["Heading2"].textColor = colors.HexColor("#196b58")
story = [
    Paragraph("Northstar Commerce", styles["Title"]),
    Paragraph("Operations Reference / Synthetic Demo", styles["Heading2"]),
    Spacer(1, 22),
    Paragraph("Payments API recovery thresholds", styles["Heading2"]),
    Paragraph(
        "Use these thresholds after an operator-approved recovery. This assistant "
        "does not execute infrastructure changes. Confirm the current incident with "
        "traces before applying a historical incident resolution.",
        styles["BodyText"],
    ),
    Spacer(1, 18),
]
table = Table(
    [
        ["Metric", "Recovery target", "Observation window"],
        ["Payment timeout rate", "Below 1%", "10 minutes"],
        ["Connection acquisition p95", "Below 200 ms", "10 minutes"],
        ["Checkout success rate", "Above 99%", "10 minutes"],
    ],
    colWidths=[200, 135, 135],
)
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173f39")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f1f6ee")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cddbc8")),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]
    )
)
story += [
    table,
    Spacer(1, 20),
    Paragraph("Pool configuration", styles["Heading2"]),
    Paragraph(
        "The configured Payments API connection pool limit is 40 per pod. "
        "Increasing it requires an operator capacity review of Ledger Database.",
        styles["BodyText"],
    ),
    PageBreak(),
    Paragraph("Escalation & evidence", styles["Title"]),
    Paragraph("Ownership", styles["Heading2"]),
    Paragraph(
        "Payments Team owns Payments API. Platform Team owns Ledger Database. "
        "Commerce Team owns Checkout Service.",
        styles["BodyText"],
    ),
    Spacer(1, 18),
    Paragraph("Minimum incident evidence", styles["Heading2"]),
    Paragraph(
        "Collect a sanitized correlation ID, error code, deployment version, pool "
        "wait histogram, active connection count, and database slow-query evidence. "
        "Never include raw access tokens or customer contact information.",
        styles["BodyText"],
    ),
]


def footer(canvas, doc):
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#70816c"))
    canvas.drawString(50, 32, "IncidentLens | Fictional data | Read-only investigation reference")
    canvas.drawRightString(545, 32, f"Page {doc.page}")


if __name__ == "__main__":
    SimpleDocTemplate(
        str(ROOT / "corpus/07-operations-reference.pdf"),
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=55,
    ).build(story, onFirstPage=footer, onLaterPages=footer)
    print("Created synthetic operations reference PDF.")
