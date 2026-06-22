from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

doc = SimpleDocTemplate(
    "SI_Seminar_Institut_Finanzzahlen.pdf",
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=17, spaceAfter=12)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#1F4E79"))
body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=15, spaceAfter=6, alignment=TA_LEFT)
small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=colors.grey)

elements = []

elements.append(Paragraph("SI Seminar-Institut, München – Recherche zu Unternehmens- und Finanzdaten", title_style))
elements.append(Paragraph("Recherchestand: 22. Juni 2026", small))
elements.append(Spacer(1, 0.4*cm))

elements.append(Paragraph("1. Unternehmensprofil", h2))
data1 = [
    ["Firma", "SI Seminar-Institut e.K."],
    ["Rechtsform", "Einzelkaufmann (e.K. / Einzelunternehmen)"],
    ["Sitz", "Trimburgstraße 2, 81249 München (Stadtbezirk Aubing)"],
    ["Registergericht", "Amtsgericht München"],
    ["Registernummer", "HRA 102681"],
    ["Geschäftsgegenstand", "Durchführung und Vertrieb von Seminaren, Vorträgen und Kursen "
                            "(Schwerpunkt: Management-, Führungskräfte- und Persönlichkeitstrainings)"],
    ["Inhaber", "Laut Registerangaben als Einzelkaufmann geführt (Namensangaben in Quellen uneinheitlich)"],
    ["USt-IdNr.", "DE296113199"],
]
t1 = Table(data1, colWidths=[4*cm, 11*cm])
t1.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#DCE6F1")),
    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 9.5),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
elements.append(t1)

elements.append(Paragraph("2. Finanzzahlen der letzten 10 Jahre", h2))
elements.append(Paragraph(
    "Eine systematische Recherche (Web-Suche, Handelsregister, Unternehmensregister/Bundesanzeiger, "
    "Northdata) ergab: Für SI Seminar-Institut e.K. liegen <b>keine öffentlich zugänglichen "
    "Jahresabschlüsse oder Finanzkennzahlen</b> für die letzten 10 Jahre vor.", body))
elements.append(Paragraph(
    "<b>Grund:</b> Das Unternehmen ist als Einzelkaufmann (e.K.) eingetragen, nicht als "
    "Kapitalgesellschaft (z.B. GmbH oder AG). Die handelsrechtliche Offenlegungspflicht nach "
    "§§ 325 ff. HGB (Veröffentlichung von Bilanz, Gewinn- und Verlustrechnung etc. über das "
    "Unternehmensregister) gilt grundsätzlich nur für Kapitalgesellschaften sowie bestimmte "
    "haftungsbeschränkte Personenhandelsgesellschaften (z.B. GmbH &amp; Co. KG). Einzelkaufleute "
    "sind von dieser Pflicht ausgenommen, solange sie nicht die Schwellenwerte einer "
    "\"großen Personenhandelsgesellschaft ohne natürliche Person als Vollhafter\" überschreiten "
    "– was bei einem e.K. begrifflich ohnehin nicht zutrifft.", body))
elements.append(Paragraph(
    "Auch kommerzielle Datenbanken wie Northdata, die Bundesanzeiger-Veröffentlichungen "
    "auswerten und auf dieser Basis Umsatz- und Gewinnschätzungen erstellen, weisen für dieses "
    "Unternehmen folgerichtig <b>keine Finanzkennzahlen</b> aus, da keine entsprechenden "
    "Veröffentlichungen existieren.", body))

elements.append(Paragraph("3. Tabelle: Verfügbarkeit von Finanzdaten 2016–2025", h2))
years = list(range(2016, 2026))
data2 = [["Geschäftsjahr", "Umsatz", "Bilanzsumme", "Mitarbeiterzahl", "Quelle"]]
for y in years:
    data2.append([str(y), "nicht veröffentlicht", "nicht veröffentlicht", "nicht veröffentlicht", "—"])
t2 = Table(data2, colWidths=[2.5*cm, 3.2*cm, 3.2*cm, 3.2*cm, 2.9*cm])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F4E79")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
elements.append(t2)
elements.append(Spacer(1, 0.3*cm))
elements.append(Paragraph(
    "Hinweis: Es werden hier ausdrücklich keine geschätzten oder erfundenen Zahlen dargestellt. "
    "Die Tabelle dokumentiert den tatsächlichen Rechercheergebnisstand: Für jedes der letzten "
    "10 Geschäftsjahre liegen keine belastbaren, öffentlich verifizierbaren Finanzdaten vor.", body))

elements.append(Paragraph("4. Mögliche weitere Schritte", h2))
elements.append(Paragraph(
    "Falls belastbare Finanzzahlen benötigt werden, kämen folgende Wege in Betracht: "
    "(a) direkte Anfrage beim Unternehmen, (b) Auskunft über eine kostenpflichtige Wirtschaftsauskunftei "
    "(z.B. Creditreform, Bürgel, Schufa für Unternehmen) mit Bonitätsschätzungen, oder "
    "(c) Prüfung, ob es sich um die identische Rechtsperson handelt wie das ähnlich benannte, "
    "umfangreichere Bildungsunternehmen \"SEMINAR-INSTITUT\" (seminar-institut.de) – sofern dort "
    "eine andere, offenlegungspflichtige Rechtsform vorliegt, wofür in der Recherche jedoch keine "
    "Hinweise gefunden wurden.", body))

elements.append(Spacer(1, 0.5*cm))
elements.append(Paragraph("Quellen", h2))
sources = [
    "Northdata – SI Seminar-Institut e.K., München, HRA 102681 (northdata.de)",
    "Handelsregisterauszug-Aggregatoren: firmen-informer.de, oeffnungszeitenbuch.de, wlw.de",
    "seminar-institut.de – Impressum und Unternehmensangaben",
    "Help Center Northdata – Methodik zu Umsatzschätzungen und Offenlegungspflichten",
    "§§ 238–342e HGB – Vorschriften zur Rechnungslegung und Offenlegung",
]
for s in sources:
    elements.append(Paragraph("• " + s, small))

doc.build(elements)
print("PDF erstellt")
