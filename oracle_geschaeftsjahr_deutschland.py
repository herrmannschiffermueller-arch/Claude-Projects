from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

doc = SimpleDocTemplate(
    "Oracle_Geschaeftsjahr_Deutschland.pdf",
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=18, spaceAfter=12)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#C74634"))
body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=15, spaceAfter=6, alignment=TA_LEFT)
small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=colors.grey)

elements = []

elements.append(Paragraph("Das Geschäftsjahr von Oracle in Deutschland", title_style))
elements.append(Paragraph("Recherchestand: 21. Juni 2026", small))
elements.append(Spacer(1, 0.4*cm))

elements.append(Paragraph("1. Geschäftsjahr von Oracle Corporation (global)", h2))
elements.append(Paragraph(
    "Oracle Corporation, der US-amerikanische Softwarekonzern mit Sitz in Austin, Texas, "
    "nutzt weltweit ein vom Kalenderjahr abweichendes Geschäftsjahr. Das Geschäftsjahr "
    "(Fiscal Year, FY) beginnt jeweils am 1. Juni und endet am 31. Mai des folgenden Jahres. "
    "Das Geschäftsjahr 2026 (FY2026) umfasst somit den Zeitraum vom 1. Juni 2025 bis zum "
    "31. Mai 2026.", body))

elements.append(Paragraph("2. Quartalsstruktur", h2))
elements.append(Paragraph(
    "Da das Geschäftsjahr im Juni beginnt, verschieben sich auch die Quartale entsprechend:", body))

data = [
    ["Quartal", "Zeitraum", "Typischer Berichtstermin"],
    ["Q1 FY", "Juni – August", "September"],
    ["Q2 FY", "September – November", "Dezember"],
    ["Q3 FY", "Dezember – Februar", "März"],
    ["Q4 FY", "März – Mai", "Juni"],
]
table = Table(data, colWidths=[3*cm, 6*cm, 6*cm])
table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#C74634")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 9.5),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
    ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
elements.append(table)
elements.append(Spacer(1, 0.3*cm))
elements.append(Paragraph(
    "Beispiel FY2026: Q1 wurde am 9. September 2025 berichtet, Q2 am 10. Dezember 2025, "
    "Q3 am 10. März 2026 und Q4 (Jahresabschluss) am 10. Juni 2026.", body))

elements.append(Paragraph("3. Oracle in Deutschland", h2))
elements.append(Paragraph(
    "Die deutsche Gesellschaft <b>ORACLE Deutschland B.V. &amp; Co. KG</b> mit Sitz in der "
    "Riesstraße 25, 80992 München (Registergericht München, HRA 95603) ist die zentrale "
    "operative Einheit des Konzerns in Deutschland. Als Tochtergesellschaft des US-Konzerns "
    "übernimmt sie für die handelsrechtliche Bilanzierung üblicherweise das konzerneinheitliche "
    "Geschäftsjahr vom 1. Juni bis 31. Mai, um eine konsolidierte Berichterstattung mit der "
    "US-Muttergesellschaft zu ermöglichen.", body))
elements.append(Paragraph(
    "Dies deckt sich mit dem Eintrag im Lobbyregister des Deutschen Bundestages für Oracle "
    "Deutschland, der ein Geschäftsjahr von 06/2024 bis 05/2025 ausweist – also exakt dem "
    "Konzern-Geschäftsjahr vom 1. Juni bis 31. Mai entsprechend.", body))
elements.append(Paragraph(
    "Die Umsatzzahlen von Oracle Deutschland werden in den einschlägigen Statistiken "
    "(z.B. Statista) ebenfalls nach diesen Geschäftsjahren ausgewiesen, z.B. ca. 1,75 Mrd. "
    "US-Dollar Umsatz im Geschäftsjahr 2023 (1. Juni 2022 – 31. Mai 2023).", body))

elements.append(Paragraph("4. Offenlegung von Jahresabschlüssen", h2))
elements.append(Paragraph(
    "Als haftungsbeschränkte Personengesellschaft (GmbH &amp; Co. KG-ähnliche Struktur, hier "
    "B.V. &amp; Co. KG) unterliegt Oracle Deutschland den deutschen Offenlegungspflichten nach "
    "§§ 325 ff. HGB. Der Jahresabschluss muss spätestens 12 Monate nach Ende des Geschäftsjahres "
    "offengelegt werden. Seit August 2022 erfolgt die Veröffentlichung nicht mehr über den "
    "Bundesanzeiger selbst, sondern über das Unternehmensregister (unternehmensregister.de).", body))

elements.append(Paragraph("5. Zusammenfassung", h2))
elements.append(Paragraph(
    "<b>Oracle</b> verwendet weltweit – und damit auch für die deutsche Tochtergesellschaft "
    "ORACLE Deutschland B.V. &amp; Co. KG – ein Geschäftsjahr, das vom <b>1. Juni bis 31. Mai</b> "
    "des Folgejahres läuft. Dies weicht vom in Deutschland üblichen Kalenderjahr als "
    "Geschäftsjahr ab, ist aber als konzernweit einheitlicher Bilanzierungszeitraum bei "
    "internationalen US-Konzernen mit deutschen Tochtergesellschaften nicht unüblich.", body))

elements.append(Spacer(1, 0.5*cm))
elements.append(Paragraph("Quellen", h2))
sources = [
    "Oracle Investor Relations – Quartalsmitteilungen FY2026 (investor.oracle.com)",
    "Oracle Pressemitteilung: Q1 FY26 Earnings Release (oracle.com/de/news)",
    "Lobbyregister beim Deutschen Bundestag, Registereintrag R001882 (lobbyregister.bundestag.de)",
    "Statista – Umsatz von Oracle in Deutschland bis 2023 (de.statista.com)",
    "Northdata – Handelsregistereintrag ORACLE Deutschland B.V. & Co. KG, HRA 95603",
    "bsteuern.com – Offenlegungspflichten Jahresabschluss / Unternehmensregister",
]
for s in sources:
    elements.append(Paragraph("• " + s, small))

doc.build(elements)
print("PDF erstellt")
