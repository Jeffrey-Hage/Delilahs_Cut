"""
File for generating pdf report based on the results

"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
)
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

resultsReport = []


def get_base_dir():
    """
    Returns the base directory of the executable. This will be the directory
    where the exe is located when packaged, or the script's directory in development.
    """
    if getattr(sys, "frozen", False):
        # The application is frozen (packaged by PyInstaller)
        base_dir = os.path.dirname(sys.executable)
    else:
        # The application is running as a normal Python script
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return base_dir


def get_output_file_path(filename):
    """
    Returns the path to the output PDF file, assuming it should be written to a 'PDF_Outputs' directory.
    """
    base_dir = get_base_dir()
    return os.path.join(base_dir, "PDF_Outputs", filename)


def generate_results_pdf(reports, fileName):
    # Get the path for saving the PDF file in the 'PDF_Outputs' directory
    path = get_output_file_path(fileName)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    pdf = SimpleDocTemplate(path, pagesize=letter)
    story = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#333333"),  # Dark gray instead of yellow
        spaceAfter=20,
    )
    default_style = ParagraphStyle(
        "Default",
        parent=styles["BodyText"],
        fontSize=12,
        textColor=colors.black,  # Black for neutral text
    )
    positive_style = ParagraphStyle(
        "Positive",
        parent=styles["BodyText"],
        fontSize=12,
        textColor=colors.HexColor("#4CAF50"),  # Green for positive
    )
    negative_style = ParagraphStyle(
        "Negative",
        parent=styles["BodyText"],
        fontSize=12,
        textColor=colors.HexColor("#F44336"),  # Red for negative
    )

    # Add title
    story.append(Paragraph("Results of Analysis", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Add the reports to the PDF
    for report in reports:
        for line in report:
            if "positive" in line.lower():
                style = positive_style
            elif "negative" in line.lower():
                style = negative_style
            else:
                style = default_style

            story.append(Paragraph(line, style))
            story.append(Spacer(1, 0.1 * inch))

        # Add a page break after each report
        story.append(PageBreak())

    # Build the PDF
    pdf.build(story)
