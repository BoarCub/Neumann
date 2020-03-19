from reportlab.pdfgen import canvas #This allows us to generate PDF Documents
from reportlab.platypus import Paragraph #Allows us to create multiline paragraphs
from reportlab.lib.styles import ParagraphStyle #Allows us to style paragraphs
import os

def makePDF(worksheetTitle, subtitle, questions, fileName):

    os.chdir("../Exported Worksheets")

    pdf = canvas.Canvas(fileName)
    pdf.setTitle(worksheetTitle)

    pdf.setFont('Times-Roman', 36)
    pdf.drawCentredString(300, 770, worksheetTitle)

    pdf.setFillColorRGB(0, 0, 255)
    pdf.setFont("Times-Roman", 24)
    pdf.drawCentredString(290, 720, subtitle)

    pdf.line(30, 710, 550, 710)

    pdf.setFillColorRGB(0, 0, 0)

    pdf.setFont("Times-Roman", 12)
    pdf.setFillColorRGB(0, 0, 0)

    y_value = 680
    for x in range(len(questions)):
        text = pdf.beginText(40, y_value)
        text.textLines(str(x+1) + ")" + "  " + questions[x])
        pdf.drawText(text)

        y_value -= 100
        if y_value <= 100:
            pdf.showPage()
            y_value = 780
            pdf.setFont("Times-Roman", 12)
            pdf.setFillColorRGB(0, 0, 0)

    pdf.save()