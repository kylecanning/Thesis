from fpdf import FPDF
import time
import datetime


def simple_table(table, name, spacing=1):

    data = [["Name", "Contact", "Employer", "DosimeterID", "EntryTime", "ExitTime", "Total Visit Dose", "ReactorStatus", "Notes"]]

    pdf = FPDF()
    pdf.set_margins(2.54, 2.54, 2.54)
    pdf.add_page()

    pdf.set_font("Arial", size=6)

    col_width = pdf.w / (9+0.2)
    row_height = pdf.font_size + 0.2
    for row in data:
        for item in row:
            pdf.cell(col_width, row_height * spacing, txt=str(item), border=1)
        pdf.ln(row_height * spacing)

    for row in table:
        for item in row:
            pdf.cell(col_width, row_height * spacing, txt=str(item), border=1)
        pdf.ln(row_height * spacing)

    pdf.output(name)