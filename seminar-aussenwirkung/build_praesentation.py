# -*- coding: utf-8 -*-
"""Baut die Seminarpräsentation 'Wie wirke ich auf andere? Außenwirkung unter der Lupe'
auf Basis der Manager-Akademie-Vorlage (Crashkurs Datenschutz)."""
import copy, re, sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml import etree

TEMPLATE, OUT = sys.argv[1], sys.argv[2]

BLUE, NAVY, MID, DARK = "0B5394", "1C2F5E", "3D85C6", "1F2A36"
LBLUE, GREY, GREY2 = "DCE8F3", "EFEFEF", "D8D8D8"
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
A = "{%s}" % NS["a"]
R = "{%s}" % NS["r"]
W = "https://de.wikipedia.org/wiki/"
WEN = "https://en.wikipedia.org/wiki/"

prs = Presentation(TEMPLATE)
tpl = list(prs.slides)
title_slide, welcome, toc1, toc2, div_proto, proto, end_slide = tpl[0], tpl[1], tpl[2], tpl[3], tpl[4], tpl[5], tpl[-1]
layout = proto.slide_layout


def by_ph(slide, t):
    for sh in slide.shapes:
        if sh.is_placeholder and sh.placeholder_format.type == t:
            return sh._element


P_BODY = by_ph(proto, 2)
P_FOOT = by_ph(proto, 15)
P_NUM = by_ph(proto, 13)
P_ICON = [sh for sh in proto.shapes if sh.shape_type == 13][0]._element
ICON_PART = proto.part.related_part(P_ICON.find(".//a:blip", NS).get(R + "embed"))
D_BODY = by_ph(div_proto, 2)

# ---------------------------------------------------------------- Text
FONT = '<a:latin typeface="Arial"/><a:ea typeface="Arial"/><a:cs typeface="Arial"/><a:sym typeface="Arial"/>'


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def rpr(sz, color=None, b=False, i=False):
    fill = '<a:solidFill><a:schemeClr val="dk1"/></a:solidFill>' if color is None else \
        '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % color
    return '<a:rPr lang="de-DE" sz="%d"%s%s>%s%s</a:rPr>' % (sz, ' b="1"' if b else "", ' i="1"' if i else "", fill, FONT)


def runs(text, sz, color=None, b=False, i=False):
    out = []
    for k, part in enumerate(re.split(r"\*\*", text)):
        if part:
            out.append('<a:r>%s<a:t xml:space="preserve">%s</a:t></a:r>' % (rpr(sz, color, b or k % 2 == 1, i), esc(part)))
    return "".join(out) or '<a:endParaRPr lang="de-DE" sz="%d"/>' % sz


def ppr(before, marL=0, indent=0, lvl=0, bu=None, algn="l"):
    if bu is None:
        b = '<a:buNone/>'
    elif bu == "num":
        b = '<a:buClr><a:srgbClr val="%s"/></a:buClr><a:buSzPts val="1600"/><a:buFont typeface="Arial"/><a:buAutoNum type="arabicPeriod"/>' % BLUE
    elif bu == "●":
        b = '<a:buClr><a:srgbClr val="%s"/></a:buClr><a:buSzPts val="1600"/><a:buFont typeface="Arial"/><a:buChar char="●"/>' % BLUE
    else:
        b = '<a:buClr><a:schemeClr val="dk1"/></a:buClr><a:buSzPts val="1600"/><a:buFont typeface="Arial"/><a:buChar char="○"/>'
    return ('<a:pPr indent="%d" lvl="%d" marL="%d" rtl="0" algn="%s"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc>'
            '<a:spcBef><a:spcPts val="%d"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft>%s</a:pPr>'
            % (indent, lvl, marL, algn, before, b))


def para(kind, text="", sz=None):
    if kind == "h":      # Kapitelzeile (wie Vorlage)
        return '<a:p>%s%s</a:p>' % (ppr(0), runs(text, sz or 1900, BLUE, b=True))
    if kind == "sh":     # Folienthema
        return '<a:p>%s%s</a:p>' % (ppr(900), runs(text, sz or 1800, BLUE, b=True))
    if kind == "p":
        return '<a:p>%s%s</a:p>' % (ppr(900), runs(text, sz or 1600))
    if kind == "i":
        return '<a:p>%s%s</a:p>' % (ppr(900), runs(text, sz or 1600, i=True))
    if kind == "c":      # zentriert
        return '<a:p>%s%s</a:p>' % (ppr(600, algn="ctr"), runs(text, sz or 1600))
    if kind == "cb":
        return '<a:p>%s%s</a:p>' % (ppr(600, algn="ctr"), runs(text, sz or 2400, BLUE, b=True))
    if kind in ("b", "n", "b2"):
        s = sz or 1600
        pp = ppr(300, 914400, -336550, 1, "○") if kind == "b2" else ppr(600, 457200, -336550, 0, "num" if kind == "n" else "●")
        if "::" in text:
            lab, rest = text.split("::", 1)
            body = runs(lab + ":", s, BLUE, b=True) + runs(rest, s)
        else:
            body = runs(text, s)
        return '<a:p>%s%s</a:p>' % (pp, body)
    raise ValueError(kind)


def set_body(sp_el, items, anchor=None):
    txBody = sp_el.find("p:txBody", NS)
    for p in txBody.findall("a:p", NS):
        txBody.remove(p)
    xml = "".join(para(*it) if isinstance(it, tuple) else para("p", it) for it in items)
    for p in etree.fromstring('<x xmlns:a="%s">%s</x>' % (NS["a"], xml)):
        txBody.append(p)
    bp = txBody.find("a:bodyPr", NS)
    af = bp.find("a:normAutofit", NS)
    if af is not None:
        for k in list(af.attrib):
            del af.attrib[k]
    if anchor:
        bp.set("anchor", anchor)


def set_h(sp_el, h):
    sp_el.find("p:spPr/a:xfrm/a:ext", NS).set("cy", str(int(Inches(h))))


# ---------------------------------------------------------------- Folien
def base_slide(notes=None):
    s = prs.slides.add_slide(layout)
    tree = s.shapes._spTree
    for sp in list(s.shapes):
        tree.remove(sp._element)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s, tree


def add_icon(s, tree, url):
    pic = copy.deepcopy(P_ICON)
    pic.find(".//a:blip", NS).set(R + "embed", s.part.relate_to(ICON_PART, RT.IMAGE))
    pic.find(".//a:hlinkClick", NS).set(R + "id", s.part.relate_to(url, RT.HYPERLINK, is_external=True))
    tree.append(pic)


def new_slide(items, url, body_h=None, notes=None):
    s, tree = base_slide(notes)
    b, f, n = (copy.deepcopy(e) for e in (P_BODY, P_FOOT, P_NUM))
    for e in (b, f, n):
        tree.append(e)
    set_body(b, items)
    if body_h:
        set_h(b, body_h)
    add_icon(s, tree, url)
    return s


def hexrgb(h):
    return RGBColor.from_string(h)


def _nostyle(sh):
    st = sh._element.find("p:style", NS)
    if st is not None:
        sh._element.remove(st)


def box(s, x, y, w, h, fill=BLUE, lines=(), size=14, color="FFFFFF", bold=False, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line=None, margin=0.08):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = 0.1
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = hexrgb(fill)
    if line:
        sh.line.color.rgb = hexrgb(line)
        sh.line.width = Pt(1.25)
    else:
        sh.line.fill.background()
    _nostyle(sh)
    tf = sh.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(margin + 0.04)
    tf.margin_top = tf.margin_bottom = Inches(margin)
    if isinstance(lines, str):
        lines = [lines]
    first = True
    for ln in lines:
        if isinstance(ln, str):
            ln = (ln, size, bold, color)
        txt, sz, bd, col = ln
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        for k, part in enumerate(re.split(r"\*\*", txt)):
            if part:
                r = p.add_run()
                r.text = part
                r.font.size, r.font.bold, r.font.name = Pt(sz), bd or (k % 2 == 1), "Arial"
                r.font.color.rgb = hexrgb(col)
    return sh


def chev(s, x, y, w, h, fill, lines, first=False):
    box(s, x, y, w, h, fill, [], shape=MSO_SHAPE.PENTAGON if first else MSO_SHAPE.CHEVRON)
    ind = 0.12 if first else h * 0.45
    return box(s, x + ind, y, w - ind - h * 0.4, h, None, lines, margin=0.02)


def table(s, x, y, w, rows, colw, size=12, rowh=0.4, first_col_bold=True):
    gt = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(rowh * len(rows)))
    tb = gt.table
    for j, cw in enumerate(colw):
        tb.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        tb.rows[i].height = Inches(rowh)
        for j, val in enumerate(row):
            c = tb.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = hexrgb(BLUE if i == 0 else (LBLUE if i % 2 == 0 else "FFFFFF"))
            c.margin_left = c.margin_right = Inches(0.08)
            c.margin_top = c.margin_bottom = Inches(0.04)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = c.text_frame.paragraphs[0]
            c.text_frame.word_wrap = True
            for k, part in enumerate(re.split(r"\*\*", val)):
                if part:
                    r = p.add_run()
                    r.text = part
                    r.font.size, r.font.name = Pt(size), "Arial"
                    r.font.bold = i == 0 or (j == 0 and first_col_bold) or k % 2 == 1
                    r.font.color.rgb = hexrgb("FFFFFF" if i == 0 else (BLUE if j == 0 and first_col_bold else DARK))
    tblPr = gt._element.graphic.graphicData.tbl.tblPr
    tblPr.set("bandRow", "0")
    return gt


SECTIONS = []


def divider(num, name, questions, url, notes=None):
    SECTIONS.append(name)
    s, tree = base_slide(notes)
    b, f, n = (copy.deepcopy(e) for e in (D_BODY, P_FOOT, P_NUM))
    for e in (b, f, n):
        tree.append(e)
    set_body(b, [("c", ""), ("c", "Modul %d" % num, 1600), ("cb", name, 2800)])
    for k, q in enumerate(questions):
        x = 1.35 + k * 3.55
        box(s, x, 3.65, 3.3, 1.75, "FFFFFF", [("Leitfrage %d" % (k + 1), 12, True, MID), (q, 14, False, DARK)],
            anchor=MSO_ANCHOR.TOP, margin=0.18)
    add_icon(s, tree, url)
    return s


def exercise(sec, title, ziel, schritte, dauer, form, url, notes=None):
    s = new_slide([("h", sec), ("sh", "Übung: " + title), ("i", ziel)], url, body_h=1.75, notes=notes)
    for k, st in enumerate(schritte):
        y = 2.75 + k * 0.85
        box(s, 1.0, y, 0.55, 0.55, BLUE, [(str(k + 1), 16, True, "FFFFFF")], shape=MSO_SHAPE.OVAL, margin=0)
        box(s, 1.7, y - 0.12, 6.6, 0.8, None, [(st, 15, False, DARK)], align=PP_ALIGN.LEFT, margin=0.02)
    box(s, 8.75, 2.75, 3.6, 3.3, LBLUE, [("Rahmen", 16, True, BLUE), ("", 6, False, DARK), ("Dauer: " + dauer, 14, False, DARK),
                                        ("", 6, False, DARK), ("Form: " + form, 14, False, DARK)],
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.25)
    return s


def cards(s, items, y0, cols=3, w=None, h=1.6, gap=0.25, x0=1.0, total=11.35, head=16, body=13, fills=(LBLUE, GREY)):
    w = w or (total - gap * (cols - 1)) / cols
    for k, (hd, t) in enumerate(items):
        x = x0 + (k % cols) * (w + gap)
        y = y0 + (k // cols) * (h + gap)
        box(s, x, y, w, h, fills[k % len(fills)], [(hd, head, True, BLUE), (t, body, False, DARK)],
            align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.16)


# ================================================================= INHALT
S1, S2, S3, S4 = "Wahrnehmung und erster Eindruck", "Selbstbild und Fremdbild", "Körpersprache", "Stimme und Sprache"
S5, S6, S7, S8 = "Erscheinungsbild und Auftreten", "Souveränität und Präsenz", "Wirkung in Schlüsselsituationen", "Transfer in den Alltag"
TITLE = "Wie wirke ich auf andere?"
SUB = "Außenwirkung unter der Lupe"

# --- Folie 2: Willkommen
wb = by_ph(welcome, 2)
done = {"Chrashkurs": SUB, "am 27": "am [Datum] in [Ort]"}
for p in wb.findall(".//a:p", NS):
    ts = p.findall(".//a:t", NS)
    full = "".join(t.text or "" for t in ts)
    for key, new in done.items():
        if full.startswith(key):
            ts[0].text = new
            for t in ts[1:]:
                t.text = ""
    if full.startswith("Herzlich willkommen"):
        ts[0].text = "Herzlich willkommen zum Seminar"
# Seminartitel als eigene Zeile vor dem Untertitel
for p in wb.findall(".//a:p", NS):
    if "".join(t.text or "" for t in p.findall(".//a:t", NS)) == SUB:
        t2 = copy.deepcopy(p)
        t2.findall(".//a:t", NS)[0].text = TITLE
        p.addprevious(t2)
        for t in p.findall(".//a:t", NS):
            r = t.getparent().find("a:rPr", NS)
            if r is not None:
                r.set("sz", "2400")
        break
# eine Leerzeile oben entfernen, damit das Quellen-Icon frei bleibt
wb.findall(".//a:p", NS)[0].getparent().remove(wb.findall(".//a:p", NS)[0])
welcome.notes_slide.notes_text_frame.text = "Begrüßung, Organisatorisches (Zeiten, Pausen, Handys), Hinweis auf Videofeedback und Vertraulichkeit."

# --- Folie 5: Agenda
s = new_slide([("h", "Seminarüberblick"), ("sh", "Tagesablauf")], W + "Kommunikation", body_h=1.1)
table(s, 1.0, 1.95, 11.35, [
    ["Uhrzeit", "Inhalt", "Methodik"],
    ["09:00", "Begrüßung, Ziele, Vorstellungsrunde", "Plenum"],
    ["09:30", "Modul 1: Wahrnehmung und erster Eindruck", "Impuls, Übung in Paaren"],
    ["10:15", "Modul 2: Selbstbild und Fremdbild", "Selbsteinschätzung, Feedback"],
    ["11:00", "Pause", ""],
    ["11:15", "Modul 3: Körpersprache", "Impuls, Körperübungen"],
    ["12:30", "Mittagspause", ""],
    ["13:15", "Modul 4: Stimme und Sprache", "Stimm- und Sprechübungen"],
    ["14:00", "Modul 5: Erscheinungsbild und Auftreten", "Impuls, Diskussion"],
    ["14:30", "Modul 6: Souveränität und Präsenz", "Kurzpräsentation mit Videofeedback"],
    ["15:30", "Pause", ""],
    ["15:45", "Modul 7: Wirkung in Schlüsselsituationen", "Rollenspiele"],
    ["16:30", "Modul 8: Transfer, Feedback, Abschluss", "Transferplan, Blitzlicht"],
], [1.4, 6.35, 3.6], size=12, rowh=0.36)

# --- Seminarziele
s = new_slide([("h", "Seminarüberblick"), ("sh", "Seminarziele"), ("p", "Nach diesem Seminar können Sie …")],
              W + "Selbstdarstellung", body_h=1.5)
cards(s, [("Verstehen", "wie Menschen Eindrücke bilden – und welche Denkfehler dabei wirken"),
          ("Erkennen", "wie Sie selbst wirken: Selbstbild und Fremdbild abgleichen"),
          ("Einsetzen", "Körpersprache, Stimme und Sprache bewusst und stimmig nutzen"),
          ("Auftreten", "Erscheinungsbild und Verhalten passend zu Rolle und Anlass wählen"),
          ("Überzeugen", "souverän und präsent in Meetings, Präsentationen und Gesprächen wirken"),
          ("Umsetzen", "einen persönlichen Plan für Ihre Wirkung im Alltag erstellen")], 2.5, h=1.75)

# --- Vorstellungsrunde
exercise("Seminarüberblick", "Vorstellungsrunde", "Ankommen – und zum ersten Mal über die eigene Wirkung nachdenken.",
         ["Name, Funktion und Unternehmen", "Wie möchte ich auf andere wirken? (drei Eigenschaften)",
          "Welche Rückmeldung zu meiner Wirkung habe ich schon einmal bekommen?", "Mein Ziel für den heutigen Tag"],
         "ca. 2 Min. pro Person", "Plenum, im Stehen", W + "Selbstdarstellung",
         notes="Die drei Wunsch-Eigenschaften auf Moderationskarten notieren lassen – sie werden in Modul 2 wieder gebraucht.")

# ================= Modul 1
divider(1, S1, ["Wie entstehen Eindrücke – und wie schnell?", "Nach welchen Kriterien beurteilen wir andere?",
                "Welche Wahrnehmungsfehler verzerren das Bild?"], W + "Wahrnehmung")

s = new_slide([("h", S1), ("sh", "Wahrnehmung ist ein aktiver Prozess"),
               ("p", "Wir sehen nicht die Welt, wie sie ist – sondern wie wir sie **auswählen, ordnen und deuten**.")],
              W + "Wahrnehmung", body_h=1.55)
steps = [("Reiz", "Aussehen, Stimme, Verhalten"), ("Auswahl", "Was fällt mir auf?"), ("Ordnung", "Einordnen in bekannte Muster"),
         ("Deutung", "Was bedeutet das?"), ("Urteil", "sympathisch, kompetent …?")]
for k, (h, t) in enumerate(steps):
    x = 1.0 + k * 2.3
    chev(s, x, 2.75, 2.25, 0.95, BLUE if k < 4 else NAVY, [(h, 15, True, "FFFFFF")], first=(k == 0))
    box(s, x, 3.9, 2.05, 1.1, GREY, [(t, 13, False, DARK)], margin=0.1)
box(s, 1.0, 5.3, 11.35, 1.0, LBLUE, [("„Wahr ist nicht, was A sagt, sondern was B versteht.“ – Die Wirkung entsteht beim Empfänger. "
                                      "Wir können sie beeinflussen, aber nie vollständig kontrollieren.", 14, False, DARK)],
    align=PP_ALIGN.LEFT, margin=0.2)

s = new_slide([("h", S1), ("sh", "Der erste Eindruck entsteht in Sekunden")],
              WEN + "Thin-slicing", body_h=1.0,
              notes="Quellen: Willis & Todorov (2006), Psychological Science; Ambady & Rosenthal (1993), JPSP; Asch (1946).")
stats = [("0,1 Sek.", "reichen, um aus einem Gesicht Vertrauenswürdigkeit und Kompetenz abzuleiten (Willis & Todorov, 2006)"),
         ("30 Sek.", "stummes Video eines Dozenten sagten seine Bewertung am Semesterende gut vorher (Ambady & Rosenthal, 1993)"),
         ("1. Info", "prägt das Gesamturteil stärker als spätere Informationen – der Primacy-Effekt (Asch, 1946)")]
for k, (big, t) in enumerate(stats):
    x = 1.0 + k * 3.85
    box(s, x, 2.0, 3.6, 3.3, GREY, [(big, 40, True, BLUE if k != 1 else MID), ("", 8, False, DARK), (t, 14, False, DARK)],
        anchor=MSO_ANCHOR.TOP, margin=0.25)
box(s, 1.0, 5.55, 11.35, 0.7, None, [("Der erste Eindruck ist kein Endurteil – aber er färbt, wie alle weiteren Informationen gedeutet werden.", 15, True, BLUE)],
    align=PP_ALIGN.LEFT, margin=0.02)

s = new_slide([("h", S1), ("sh", "Die zwei Grunddimensionen: Wärme und Kompetenz"),
               ("p", "Menschen beurteilen andere vor allem nach zwei Fragen: **Was hat sie/er mit mir vor?** (Wärme) und "
                     "**Kann sie/er das umsetzen?** (Kompetenz).")],
              WEN + "Stereotype_content_model", body_h=1.6)
quad = [("Kalt + kompetent", "Respekt, aber Distanz – oft Neid oder Misstrauen", MID, 1.0, 2.75),
        ("Warm + kompetent", "Bewunderung, Vertrauen, Kooperation", BLUE, 4.55, 2.75),
        ("Kalt + wenig kompetent", "Ablehnung, Desinteresse", "7F8C99", 1.0, 4.4),
        ("Warm + wenig kompetent", "Sympathie, aber wenig Einfluss – oft Mitleid", MID, 4.55, 4.4)]
for h, t, c, x, y in quad:
    box(s, x, y, 3.45, 1.55, c, [(h, 16, True, "FFFFFF"), (t, 12, False, "FFFFFF")], shape=MSO_SHAPE.RECTANGLE)
box(s, 8.4, 2.75, 3.95, 3.2, LBLUE, [("Für die Praxis", 16, True, BLUE), ("", 6, False, DARK),
                                    ("Wärme wird zuerst beurteilt – und wiegt schwerer.", 13, True, DARK), ("", 6, False, DARK),
                                    ("Erst Verbindung herstellen, dann Kompetenz zeigen („Connect, then lead“).", 13, False, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.22)

s = new_slide([("h", S1), ("sh", "Mythos 7-38-55: Was Mehrabian wirklich untersucht hat"),
               ("p", "Oft zitiert: Wirkung entstehe zu **7 % aus Worten, 38 % aus der Stimme und 55 % aus der Körpersprache**. "
                     "Das ist so nicht richtig.")],
              WEN + "Albert_Mehrabian", body_h=1.6)
box(s, 1.0, 2.75, 5.5, 3.4, GREY, [("Was die Studien zeigten", 17, True, BLUE), ("", 6, False, DARK),
                                  ("• Laborversuche mit **einzelnen Wörtern** (z. B. „vielleicht“)", 14, False, DARK),
                                  ("• Es ging um **Gefühle und Einstellungen** (Mögen / Nicht-Mögen)", 14, False, DARK),
                                  ("• Nur bei **widersprüchlichen** Signalen verlassen wir uns stärker auf Stimme und Mimik", 14, False, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.25)
box(s, 6.85, 2.75, 5.5, 3.4, LBLUE, [("Was wir daraus ableiten können", 17, True, BLUE), ("", 6, False, DARK),
                                    ("• Inhalt zählt – besonders bei Fachthemen", 14, False, DARK),
                                    ("• Entscheidend ist die **Stimmigkeit (Kongruenz)** von Wort, Stimme und Körper", 14, False, DARK),
                                    ("• Passen sie nicht zusammen, glauben wir eher dem Nonverbalen", 14, False, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.25)

s = new_slide([("h", S1), ("sh", "Typische Wahrnehmungsfehler")], W + "Halo-Effekt", body_h=1.0)
table(s, 1.0, 1.95, 11.35, [
    ["Effekt", "Was passiert?", "Beispiel"],
    ["Halo-Effekt", "Eine auffällige Eigenschaft überstrahlt alle anderen", "Attraktive Menschen werden für kompetenter gehalten"],
    ["Primacy-Effekt", "Erste Informationen wiegen schwerer als spätere", "Ein holpriger Start prägt den ganzen Vortrag"],
    ["Recency-Effekt", "Das Letzte bleibt besonders gut in Erinnerung", "Der Abschluss eines Gesprächs bleibt hängen"],
    ["Bestätigungsfehler", "Wir suchen Belege für unser erstes Urteil", "„Wusste ich doch, dass er unzuverlässig ist.“"],
    ["Ähnlichkeitseffekt", "Wer uns ähnlich ist, wirkt sympathischer", "Gleiches Hobby, gleiche Uni, gleicher Dialekt"],
    ["Stereotype", "Urteil auf Basis von Gruppenzugehörigkeit", "Alter, Geschlecht, Herkunft, Beruf"],
], [2.6, 4.5, 4.25], size=13, rowh=0.58)

s = new_slide([("h", S1), ("sh", "Erwartungen wirken: Die selbsterfüllende Prophezeiung"),
               ("p", "Im **Pygmalion-Experiment** (Rosenthal & Jacobson, 1968) erhielten Lehrkräfte die Information, einige Kinder "
                     "seien „Spätzünder“ mit großem Potenzial. Diese Kinder – in Wahrheit zufällig ausgewählt – steigerten ihre "
                     "Leistung stärker als die anderen.")],
              W + "Rosenthal-Effekt", body_h=2.1)
loop = [("Erwartung", "„Die neue Kollegin ist unsicher.“"), ("Verhalten", "Weniger Verantwortung, mehr Kontrolle"),
        ("Reaktion", "Sie traut sich weniger zu"), ("Bestätigung", "„Sehen Sie – unsicher!“")]
for k, (h, t) in enumerate(loop):
    x = 1.0 + k * 2.95
    box(s, x, 3.35, 2.6, 1.6, BLUE if k % 2 == 0 else MID, [(h, 16, True, "FFFFFF"), (t, 13, False, "FFFFFF")], margin=0.12)
    if k < 3:
        box(s, x + 2.62, 3.95, 0.32, 0.4, MID, [], shape=MSO_SHAPE.RIGHT_ARROW)
box(s, 1.0, 5.25, 11.35, 0.9, LBLUE, [("Das gilt auch umgekehrt: Wie wir uns selbst sehen, beeinflusst unser Auftreten – und damit, wie andere uns begegnen.", 14, True, DARK)],
    align=PP_ALIGN.LEFT, margin=0.2)

exercise(S1, "Der erste Eindruck", "Erleben, wie schnell und wie unterschiedlich erste Eindrücke entstehen.",
         ["Paare bilden – möglichst mit Personen, die sich nicht kennen.",
          "30 Sekunden schweigend ansehen, dann notieren: Beruf? Hobby? Drei Eigenschaften?",
          "Eindrücke austauschen: Was stimmt – was nicht?",
          "Reflexion: Woran haben Sie Ihr Urteil festgemacht?"],
         "15 Minuten", "Paararbeit, Auswertung im Plenum", WEN + "Thin-slicing",
         notes="Auswertung: Welche Signale wurden genannt (Kleidung, Haltung, Mimik, Accessoires)? Überleitung zu Selbstbild/Fremdbild.")

# ================= Modul 2
divider(2, S2, ["Wie sehe ich mich selbst?", "Wie sehen mich andere?", "Wie schließe ich die Lücke?"], W + "Johari-Fenster")

s = new_slide([("h", S2), ("sh", "Drei Bilder von mir"),
               ("p", "Außenwirkung ist die Schnittmenge aus dem, was ich zeige, und dem, was andere wahrnehmen.")],
              W + "Selbstbild", body_h=1.55)
for k, (h, t, x, c) in enumerate([("Selbstbild", "So sehe ich mich", 1.3, BLUE), ("Wunschbild", "So möchte ich wirken", 3.55, MID),
                                   ("Fremdbild", "So sehen mich andere", 5.8, NAVY)]):
    sh = box(s, x, 2.7, 3.2, 3.2, c, [(h, 17, True, "FFFFFF"), (t, 12, False, "FFFFFF")], shape=MSO_SHAPE.OVAL, margin=0.3)
    sh.fill.fore_color.rgb = hexrgb(c)
box(s, 9.5, 2.7, 2.85, 3.2, LBLUE, [("Ziel", 16, True, BLUE), ("", 6, False, DARK),
                                   ("Die drei Bilder möglichst weit zur Deckung bringen – durch Selbstreflexion, Feedback und bewusstes Verhalten.", 13, False, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.2)

s = new_slide([("h", S2), ("sh", "Das Johari-Fenster")], W + "Johari-Fenster", body_h=1.0)
jo = [("Öffentliche Person", "Mir bekannt – anderen bekannt", BLUE), ("Blinder Fleck", "Mir unbekannt – anderen bekannt", MID),
      ("Privatperson", "Mir bekannt – anderen unbekannt", MID), ("Unbekanntes", "Mir unbekannt – anderen unbekannt", "7F8C99")]
box(s, 1.5, 1.95, 7.0, 0.35, None, [("bekannt        ←  Selbst  →        unbekannt", 12, True, "4A5561")], margin=0)
for k, (h, t, c) in enumerate(jo):
    box(s, 1.5 + (k % 2) * 3.55, 2.35 + (k // 2) * 1.95, 3.45, 1.85, c, [(h, 17, True, "FFFFFF"), (t, 12, False, "FFFFFF")],
        shape=MSO_SHAPE.RECTANGLE)
box(s, 8.85, 2.35, 3.5, 3.75, LBLUE, [("Die „Arena“ vergrößern", 16, True, BLUE), ("", 6, False, DARK),
                                     ("Feedback einholen → blinder Fleck wird kleiner", 13, False, DARK), ("", 6, False, DARK),
                                     ("Sich zeigen → Privatbereich wird kleiner", 13, False, DARK), ("", 6, False, DARK),
                                     ("Große Arena = mehr Vertrauen, weniger Missverständnisse", 13, True, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.2)

s = new_slide([("h", S2), ("sh", "Warum wir uns oft falsch einschätzen")], WEN + "Illusory_superiority", body_h=1.0,
              notes="Quellen: Svenson (1981), Acta Psychologica; Gilovich, Medvec & Savitsky (2000), JPSP; Kruger & Dunning (1999), JPSP.")
bias = [("93 %", "Überdurchschnittlich-Effekt", "der befragten US-Autofahrer hielten sich für besser als der Durchschnitt (Svenson, 1981)."),
        ("≈ 50 % vs. 23 %", "Spotlight-Effekt", "Studierende im peinlichen T-Shirt schätzten, dass die Hälfte es bemerkt – tatsächlich war es knapp ein Viertel (Gilovich et al., 2000)."),
        ("Dunning-Kruger", "Selbstüberschätzung", "Gerade bei geringer Kompetenz fehlt oft das Wissen, die eigenen Lücken zu erkennen (Kruger & Dunning, 1999).")]
for k, (big, h, t) in enumerate(bias):
    x = 1.0 + k * 3.85
    box(s, x, 2.0, 3.6, 4.1, GREY, [(big, 28, True, BLUE if k != 1 else MID), (h, 15, True, DARK), ("", 6, False, DARK), (t, 13, False, DARK)],
        anchor=MSO_ANCHOR.TOP, margin=0.22)

s = new_slide([("h", S2), ("sh", "Feedback: Der Schlüssel zum Fremdbild"),
               ("p", "Ohne Rückmeldung bleibt der blinde Fleck unsichtbar. Gutes Feedback ist **konkret, beschreibend und wohlwollend**.")],
              W + "Feedback", body_h=1.55)
box(s, 1.0, 2.75, 5.5, 3.45, LBLUE, [("Feedback geben", 17, True, BLUE), ("", 6, False, DARK),
                                    ("• Ich-Botschaften: „Auf mich wirkst du …“", 14, False, DARK),
                                    ("• Beobachtung beschreiben, nicht bewerten", 14, False, DARK),
                                    ("• Konkret statt pauschal", 14, False, DARK),
                                    ("• Positives zuerst und ehrlich", 14, False, DARK),
                                    ("• Veränderbares ansprechen", 14, False, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.25)
box(s, 6.85, 2.75, 5.5, 3.45, GREY, [("Feedback nehmen", 17, True, BLUE), ("", 6, False, DARK),
                                    ("• Zuhören, ausreden lassen", 14, False, DARK),
                                    ("• Nicht rechtfertigen oder verteidigen", 14, False, DARK),
                                    ("• Verständnisfragen stellen", 14, False, DARK),
                                    ("• Bedanken – Feedback ist ein Geschenk", 14, False, DARK),
                                    ("• Selbst entscheiden, was man annimmt", 14, False, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.25)

exercise(S2, "Selbstbild – Fremdbild", "Die eigene Wirkung mit der Wahrnehmung anderer abgleichen.",
         ["Wählen Sie aus der Eigenschaftsliste fünf Begriffe, die Sie beschreiben.",
          "Zwei andere Teilnehmende wählen je fünf Begriffe für Sie.",
          "Vergleichen Sie: Wo gibt es Übereinstimmung, wo Abweichungen?",
          "Notieren Sie Ihren wichtigsten „blinden Fleck“."],
         "25 Minuten", "Dreiergruppen", W + "Johari-Fenster",
         notes="Eigenschaftsliste als Handout: z. B. souverän, zurückhaltend, dominant, herzlich, sachlich, humorvoll, strukturiert, spontan, nahbar, distanziert …")

# ================= Modul 3
divider(3, S3, ["Was verrät mein Körper über mich?", "Welche Signale wirken souverän?", "Wie deute ich Körpersprache richtig?"],
        W + "Körpersprache")

s = new_slide([("h", S3), ("sh", "Vier Kanäle der Wirkung")], W + "Nonverbale_Kommunikation", body_h=1.0)
ch = [("Verbal", "Was ich sage", "Wortwahl, Inhalt, Struktur, Argumente"),
      ("Paraverbal", "Wie ich es sage", "Stimme, Tempo, Lautstärke, Betonung, Pausen"),
      ("Nonverbal", "Was mein Körper zeigt", "Haltung, Gestik, Mimik, Blick, Distanz"),
      ("Extraverbal", "Was mich umgibt", "Kleidung, Pünktlichkeit, Umgebung, Unterlagen")]
for k, (h, q, t) in enumerate(ch):
    x = 1.0 + k * 2.9
    box(s, x, 2.0, 2.65, 1.2, [BLUE, MID, NAVY, "7F8C99"][k], [(h, 18, True, "FFFFFF"), (q, 12, False, "FFFFFF")], margin=0.1)
    box(s, x, 3.35, 2.65, 1.8, GREY, [(t, 14, False, DARK)], anchor=MSO_ANCHOR.TOP, margin=0.18)
box(s, 1.0, 5.45, 11.35, 0.75, LBLUE, [("Überzeugend wirkt, wer auf allen Kanälen dieselbe Botschaft sendet – das nennt man Kongruenz.", 15, True, BLUE)],
    margin=0.1)

s = new_slide([("h", S3), ("sh", "Haltung und Stand"),
               ("b", "Stabiler Stand:: Füße hüftbreit, Gewicht auf beiden Beinen, Knie locker"),
               ("b", "Aufrechte Haltung:: Brustbein leicht angehoben, Schultern locker, Kopf gerade"),
               ("b", "Raum einnehmen:: nicht klein machen, aber auch nicht breitbeinig dominieren"),
               ("b", "Ruhe:: kein Wippen, Tänzeln oder Anlehnen"),
               ("sh", "Was sagt die Forschung zum „Power Posing“?"),
               ("p", "Die viel zitierte Studie von Carney, Cuddy & Yap (2010) fand Hormoneffekte nach zwei Minuten „Siegerpose“. "
                     "Diese ließen sich **nicht replizieren** (Ranehill et al., 2015). Belegt ist eher ein kleiner Effekt auf das "
                     "**subjektive Gefühl** von Stärke."),
               ("i", "Fazit: Eine aufrechte Haltung wirkt auf andere – Wundermittel ist sie nicht.")],
              WEN + "Power_posing")

s = new_slide([("h", S3), ("sh", "Gestik: Hände, die überzeugen")], W + "Gestik", body_h=1.0)
table(s, 1.0, 1.95, 11.35, [
    ["Signal", "Mögliche Wirkung", "Tipp"],
    ["Offene Handflächen", "ehrlich, zugewandt, einladend", "Beim Erklären und Fragen einsetzen"],
    ["Gesten im Bereich Taille bis Schulter", "engagiert, positiv", "„Positive Zone“ nutzen"],
    ["Hände in den Taschen", "lässig oder desinteressiert", "Im Business eher vermeiden"],
    ["Verschränkte Arme", "abwartend, distanziert – oder einfach bequem", "Kontext beachten, Arme lösen"],
    ["Zeigefinger auf Personen", "belehrend, aggressiv", "Mit offener Hand zeigen"],
    ["Spielen mit Stift, Ring, Haaren", "nervös, abgelenkt", "Hände ruhig ablegen"],
], [3.6, 4.0, 3.75], size=13, rowh=0.6)
box(s, 1.0, 6.25, 11.35, 0.4, None, [("Wichtig: Gesten haben keine feste Bedeutung – erst Kontext und Kombination machen sie deutbar.", 13, True, MID)],
    align=PP_ALIGN.LEFT, margin=0)

s = new_slide([("h", S3), ("sh", "Mimik und Blickkontakt"),
               ("sh", "Mimik", 1600),
               ("b", "Echtes Lächeln:: erreicht die Augen (Duchenne-Lächeln) – ein aufgesetztes Lächeln erkennt man oft"),
               ("b", "Das Gesicht spricht mit:: Mimik sollte zum Inhalt passen, besonders bei ernsten Themen"),
               ("b", "Entspannte Stirn:: dauerhaftes Stirnrunzeln wirkt kritisch oder angestrengt"),
               ("sh", "Blickkontakt", 1600),
               ("b", "Im Gespräch:: Blickkontakt halten, aber nicht starren – natürliche Pausen zulassen"),
               ("b", "Vor Gruppen:: jeweils einer Person einen Gedanken lang in die Augen sehen, dann wechseln"),
               ("b", "Nicht ausweichen:: Blick auf Boden, Decke oder Folien wirkt unsicher"),
               ("b", "Kultur beachten:: Intensität und Dauer von Blickkontakt werden international unterschiedlich bewertet")],
              W + "Mimik")

s = new_slide([("h", S3), ("sh", "Distanzzonen nach Edward T. Hall"),
               ("p", "Jeder Mensch hat einen persönlichen Raum. Wer ihn unaufgefordert betritt, löst Unbehagen aus.")],
              W + "Proxemik", body_h=1.55)
zones = [("Öffentliche Zone", "ab ca. 3,6 m – Vortrag, Bühne", "B7C9DD", 4.0), ("Soziale Zone", "ca. 1,2–3,6 m – Geschäftskontakte", "8FB0D3", 3.1),
         ("Persönliche Zone", "ca. 0,45–1,2 m – Kollegen, Freunde", MID, 2.2), ("Intime Zone", "bis ca. 0,45 m – Partner, Familie", NAVY, 1.3)]
cx, cy = 3.55, 4.4
for k, (h, t, c, r) in enumerate(zones):
    box(s, cx - r * 0.62, cy - r * 0.45, r * 1.24, r * 0.9, c, [], shape=MSO_SHAPE.OVAL)
for k, (h, t, c, r) in enumerate(zones):
    y = 2.75 + k * 0.85
    box(s, 7.1, y, 0.45, 0.45, c, [], shape=MSO_SHAPE.OVAL)
    box(s, 7.7, y - 0.12, 4.65, 0.75, None, [(h, 15, True, BLUE), (t, 13, False, DARK)], align=PP_ALIGN.LEFT, margin=0.02)

s = new_slide([("h", S3), ("sh", "Körpersprache richtig deuten: Die vier K")], W + "Körpersprache", body_h=1.0)
cards(s, [("Kontext", "In welcher Situation zeigt sich das Signal? Kälte, Stuhl, Müdigkeit können Ursachen sein."),
          ("Kombination", "Nie ein Einzelsignal deuten – erst mehrere gleichgerichtete Signale ergeben ein Bild."),
          ("Kongruenz", "Passen Worte, Stimme und Körper zusammen? Widersprüche sind der eigentliche Hinweis."),
          ("Kalibrierung", "Wie verhält sich die Person normalerweise? Veränderungen sind aussagekräftiger als Zustände.")],
      2.0, cols=2, h=1.85, head=18, body=14)
box(s, 1.0, 6.1, 11.35, 0.5, None, [("Es gibt kein „Lexikon der Körpersprache“ – Vorsicht vor schnellen Deutungen.", 14, True, MID)],
    align=PP_ALIGN.LEFT, margin=0)

exercise(S3, "Körpersprache-Parcours", "Die eigene Körpersprache bewusst erleben und Feedback erhalten.",
         ["Station 1: Den Raum betreten, Blickkontakt aufnehmen, begrüßen.",
          "Station 2: 60 Sekunden frei stehen und über ein Hobby sprechen.",
          "Station 3: Dieselbe Aussage einmal mit offener, einmal mit geschlossener Haltung.",
          "Feedback der Gruppe und Videoaufzeichnung (freiwillig)."],
         "40 Minuten", "Kleingruppen à 4–5 Personen, Videofeedback", W + "Körpersprache",
         notes="Einverständnis für Videoaufnahmen einholen; Aufnahmen werden nach dem Seminar gelöscht.")

# ================= Modul 4
divider(4, S4, ["Wie wirkt meine Stimme?", "Welche Wörter schwächen meine Botschaft?", "Wie kommt das Gemeinte auch an?"],
        W + "Prosodie")

s = new_slide([("h", S4), ("sh", "Die Stimme: Visitenkarte der Persönlichkeit")], W + "Prosodie", body_h=1.0)
cards(s, [("Stimmlage", "Eine entspannte, eher tiefere Lage wirkt ruhig und kompetent – Hochdruck macht die Stimme eng und hoch."),
          ("Tempo", "Zu schnell wirkt gehetzt, zu langsam zäh. Wichtiges langsamer sagen."),
          ("Lautstärke", "Angemessen laut wirkt präsent. Leise gesprochene Satzenden wirken unsicher."),
          ("Betonung", "Gezielte Betonung lenkt die Aufmerksamkeit. Monotonie ermüdet."),
          ("Pausen", "Pausen geben Gewicht, Zeit zum Denken – und wirken souverän."),
          ("Artikulation", "Deutliche Aussprache signalisiert Klarheit und Respekt vor dem Publikum.")], 2.0, h=1.9)

s = new_slide([("h", S4), ("sh", "Stimme wirkt – auch auf Entscheidungen"),
               ("p", "In Experimenten wählten Versuchspersonen Kandidatinnen und Kandidaten mit **tieferen Stimmen** häufiger als "
                     "Führungspersonen (Klofstad, Anderson & Peters, 2012). Tiefere Stimmen werden oft als kompetenter und "
                     "stärker wahrgenommen."),
               ("sh", "Praxistipps für eine tragfähige Stimme"),
               ("n", "**Atmen:** in den Bauch atmen (Zwerchfellatmung) – das senkt die Stimme und beruhigt"),
               ("n", "**Aufwärmen:** vor wichtigen Terminen summen, gähnen, Lippen flattern lassen"),
               ("n", "**Satzmelodie:** Aussagen am Ende nach unten führen – nach oben klingt es wie eine Frage"),
               ("n", "**Wasser trinken:** stilles Wasser, Raumtemperatur, kein Räuspern"),
               ("n", "**Aufnehmen:** die eigene Stimme per Smartphone anhören – ungewohnt, aber sehr lehrreich")],
              W + "Stimme")

s = new_slide([("h", S4), ("sh", "Sprache: Klar statt weich")], W + "Rhetorik", body_h=1.0)
table(s, 1.0, 1.95, 11.35, [
    ["Weichmacher", "Wirkung", "Klare Alternative"],
    ["„Ich würde mal sagen …“", "zögerlich", "„Ich schlage vor …“"],
    ["„Eigentlich / irgendwie / quasi“", "unverbindlich", "Füllwort streichen"],
    ["„Nur eine kurze Frage …“", "macht das Anliegen klein", "„Ich habe eine Frage.“"],
    ["„Vielleicht könnten wir eventuell …“", "unsicher", "„Lassen Sie uns … – einverstanden?“"],
    ["„Sorry, dass ich störe …“", "unterwürfig", "„Danke, dass Sie sich Zeit nehmen.“"],
    ["„Man müsste mal …“", "niemand fühlt sich zuständig", "„Ich kümmere mich bis Freitag um …“"],
], [4.1, 2.9, 4.35], size=13, rowh=0.6)
box(s, 1.0, 6.2, 11.35, 0.45, None, [("Klar heißt nicht hart: Höflichkeit und Klarheit schließen sich nicht aus.", 14, True, MID)],
    align=PP_ALIGN.LEFT, margin=0)

s = new_slide([("h", S4), ("sh", "Kommunikation nach Paul Watzlawick"),
               ("p", "Zwei seiner fünf Axiome sind für die eigene Wirkung besonders wichtig.")],
              W + "Paul_Watzlawick", body_h=1.5)
box(s, 1.0, 2.6, 5.5, 3.6, BLUE, [("„Man kann nicht nicht kommunizieren.“", 19, True, "FFFFFF"), ("", 8, False, "FFFFFF"),
                                 ("Auch Schweigen, Wegsehen oder Zuspätkommen senden eine Botschaft. Wir wirken immer – ob wir wollen oder nicht.", 14, False, "FFFFFF")],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.3)
box(s, 6.85, 2.6, 5.5, 3.6, MID, [("Inhalts- und Beziehungsebene", 19, True, "FFFFFF"), ("", 8, False, "FFFFFF"),
                                 ("Jede Nachricht hat einen Sach- und einen Beziehungsaspekt. Die Beziehungsebene bestimmt, wie der Inhalt "
                                  "verstanden wird – wie beim Eisberg liegt der größere Teil unter der Oberfläche.", 14, False, "FFFFFF")],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.3)

s = new_slide([("h", S4), ("sh", "Das Vier-Seiten-Modell nach Schulz von Thun"),
               ("p", "Jede Nachricht hat vier Seiten – und die Wirkung entscheidet sich auf dem „Ohr“, mit dem der Empfänger hört.")],
              W + "Vier-Seiten-Modell", body_h=1.5)
box(s, 4.85, 3.3, 3.65, 1.9, GREY, [("„Sie sind ja heute schon da.“", 16, True, DARK)], shape=MSO_SHAPE.OVAL, margin=0.3)
for k, (h, t, x, y) in enumerate([("Sachinhalt", "Sie sind anwesend.", 1.0, 2.75), ("Selbstoffenbarung", "Ich bin überrascht.", 8.85, 2.75),
                                   ("Beziehung", "Sonst sind Sie unzuverlässig.", 1.0, 4.7), ("Appell", "Seien Sie öfter pünktlich!", 8.85, 4.7)]):
    box(s, x, y, 3.5, 1.4, BLUE if k in (0, 3) else MID, [(h, 16, True, "FFFFFF"), (t, 13, False, "FFFFFF")], margin=0.1)

exercise(S4, "Betonung verändert die Botschaft", "Erleben, wie stark Stimme und Betonung die Wirkung eines Satzes verändern.",
         ["Satz: „Ich habe nicht gesagt, dass Sie das Projekt verschieben sollen.“",
          "Sprechen Sie den Satz sieben Mal – jedes Mal mit Betonung auf einem anderen Wort.",
          "Die Gruppe beschreibt jeweils, was „gemeint“ ist.",
          "Danach: eigenen Kernsatz aus dem Berufsalltag mit Pause und Satzmelodie üben."],
         "20 Minuten", "Plenum, danach Paare", W + "Prosodie")

# ================= Modul 5
divider(5, S5, ["Was sagt mein Äußeres über mich?", "Welcher Dresscode passt zu welchem Anlass?", "Wie wirke ich digital?"],
        W + "Dresscode")

s = new_slide([("h", S5), ("sh", "Extraverbale Signale: Mehr als Kleidung")], W + "Selbstdarstellung", body_h=1.0)
cards(s, [("Kleidung und Pflege", "Passform, Zustand, Sauberkeit – Details wie Schuhe und Hände werden wahrgenommen."),
          ("Pünktlichkeit", "Pünktlich sein signalisiert Respekt und Verlässlichkeit."),
          ("Unterlagen und Technik", "Saubere Präsentation, funktionierende Technik, ordentliche Unterlagen."),
          ("Arbeitsplatz", "Schreibtisch, Hintergrund im Videocall, Auto beim Kundentermin."),
          ("Schriftliches", "E-Mail-Stil, Signatur, Rechtschreibung – oft der allererste Eindruck."),
          ("Umgang mit anderen", "Wie behandle ich Empfang, Service, Assistenz? Das wird beobachtet.")], 2.0, h=1.9)

s = new_slide([("h", S5), ("sh", "Dresscodes im Business")], W + "Dresscode", body_h=1.0)
table(s, 1.0, 1.95, 11.35, [
    ["Dresscode", "Typisch", "Passende Anlässe"],
    ["Business Formal", "Dunkler Anzug oder Kostüm, Hemd/Bluse, ggf. Krawatte, klassische Schuhe", "Vorstand, Banken, Verhandlungen, offizielle Anlässe"],
    ["Business Casual", "Stoffhose oder Rock, Hemd/Bluse, Sakko optional, gepflegte Schuhe", "Büroalltag, interne Meetings, Kundenbesuche"],
    ["Smart Casual", "Chino, Poloshirt oder Pullover, Sneaker in gepflegter Form", "Start-ups, Teamevents, Workshops"],
    ["Casual", "Jeans, T-Shirt, Freizeitschuhe", "Freitage in lockeren Unternehmen, Freizeit"],
], [2.6, 5.0, 3.75], size=13, rowh=0.82)
box(s, 1.0, 6.2, 11.35, 0.45, None, [("Faustregel: eine Stufe über dem Durchschnitt der Zielgruppe – besonders beim ersten Termin.", 14, True, MID)],
    align=PP_ALIGN.LEFT, margin=0)

s = new_slide([("h", S5), ("sh", "Passung statt Perfektion"),
               ("p", "Das Erscheinungsbild wirkt dann überzeugend, wenn es zu vier Faktoren passt.")],
              WEN + "Enclothed_cognition", body_h=1.5)
for k, (h, t) in enumerate([("Rolle", "Was erwarten andere von meiner Funktion?"), ("Anlass", "Kundentermin, Workshop oder Betriebsfeier?"),
                             ("Branche und Kultur", "Was ist üblich – und wo darf ich abweichen?"), ("Persönlichkeit", "Fühle ich mich wohl und authentisch?")]):
    x = 1.0 + k * 2.9
    box(s, x + 0.55, 2.55, 1.55, 1.55, BLUE if k % 2 == 0 else MID, [(str(k + 1), 28, True, "FFFFFF")], shape=MSO_SHAPE.OVAL, margin=0)
    box(s, x, 4.25, 2.65, 1.3, GREY, [(h, 15, True, BLUE), (t, 12, False, DARK)], anchor=MSO_ANCHOR.TOP, margin=0.12)
box(s, 1.0, 5.75, 11.35, 0.7, LBLUE, [("Kleidung wirkt auch nach innen: Adam & Galinsky (2012) sprechen von „Enclothed Cognition“ – die Befunde sind allerdings nicht einheitlich repliziert.", 13, False, DARK)],
    align=PP_ALIGN.LEFT, margin=0.15)

s = new_slide([("h", S5), ("sh", "Digitale Außenwirkung"),
               ("sh", "Im Videocall", 1600),
               ("b", "Kamera auf Augenhöhe:: in die Kamera sehen, wenn Sie sprechen – das ist „Blickkontakt“"),
               ("b", "Licht von vorn:: Fenster oder Lampe vor Ihnen, nicht im Rücken"),
               ("b", "Ruhiger Hintergrund:: aufgeräumt oder dezent unscharf, keine Ablenkung"),
               ("b", "Ton vor Bild:: ein gutes Headset ist wichtiger als eine gute Kamera"),
               ("sh", "Online-Profil und Schriftverkehr", 1600),
               ("b", "Profilfoto:: aktuell, professionell, freundlich – Gesicht gut erkennbar"),
               ("b", "Profiltext:: Nutzen statt Aufzählung – wofür stehen Sie?"),
               ("b", "E-Mails:: klarer Betreff, kurze Absätze, freundlicher Ton, sorgfältige Rechtschreibung")],
              W + "Videokonferenz")

# ================= Modul 6
divider(6, S6, ["Was macht souveräne Menschen aus?", "Wie gehe ich mit Nervosität um?", "Wie authentisch darf ich sein?"],
        W + "Keith_Johnstone")

s = new_slide([("h", S6), ("sh", "Hochstatus und Tiefstatus nach Keith Johnstone"),
               ("p", "Status ist nicht die Position, sondern das **Verhalten**, mit dem wir uns im Verhältnis zu anderen einordnen.")],
              W + "Keith_Johnstone", body_h=1.55)
table(s, 1.0, 2.7, 11.35, [
    ["Signal", "Hochstatus", "Tiefstatus"],
    ["Haltung", "aufrecht, ruhig, raumgreifend", "eingesunken, klein, unruhig"],
    ["Blick", "hält Blickkontakt, ruhiger Blick", "weicht aus, schnelle Blickwechsel"],
    ["Kopf", "gerade, wenig Bewegung", "geneigt, viel Nicken"],
    ["Sprache", "vollständige Sätze, Pausen", "Füllwörter, Rechtfertigungen, Entschuldigungen"],
    ["Tempo", "gelassen", "hastig"],
], [2.6, 4.4, 4.35], size=13, rowh=0.5)
box(s, 1.0, 5.9, 11.35, 0.6, LBLUE, [("Souverän ist, wer den Status situativ wählen kann – z. B. Hochstatus in der Verhandlung, Tiefstatus beim Zuhören und Entschuldigen.", 13, True, DARK)],
    align=PP_ALIGN.LEFT, margin=0.15)

s = new_slide([("h", S6), ("sh", "Präsenz: Erst Wärme, dann Stärke"),
               ("p", "Cuddy, Kohut & Neffinger (2013) empfehlen Führungskräften: **„Connect, then lead.“** Wer zuerst Vertrauen "
                     "aufbaut, dessen Kompetenz wird eher akzeptiert.")],
              WEN + "Stereotype_content_model", body_h=1.6)
box(s, 1.0, 2.8, 5.5, 3.4, LBLUE, [("Wärme zeigen", 17, True, BLUE), ("", 6, False, DARK),
                                  ("• Echtes Lächeln und Interesse", 14, False, DARK), ("• Namen merken und verwenden", 14, False, DARK),
                                  ("• Zuhören und nachfragen", 14, False, DARK), ("• Gemeinsamkeiten ansprechen", 14, False, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.25)
box(s, 6.85, 2.8, 5.5, 3.4, GREY, [("Stärke zeigen", 17, True, BLUE), ("", 6, False, DARK),
                                  ("• Klare Aussagen und Empfehlungen", 14, False, DARK), ("• Ruhige Haltung und Stimme", 14, False, DARK),
                                  ("• Verantwortung übernehmen", 14, False, DARK), ("• Vorbereitung sichtbar machen", 14, False, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.25)

s = new_slide([("h", S6), ("sh", "Authentisch oder angepasst?"),
               ("p", "Mark Snyder (1974) beschreibt, wie stark Menschen ihr Verhalten an die Situation anpassen (**Self-Monitoring**).")],
              WEN + "Self-monitoring", body_h=1.5)
box(s, 1.0, 2.6, 5.5, 3.1, GREY, [("Hohes Self-Monitoring", 17, True, BLUE), ("", 6, False, DARK),
                                 ("+ flexibel, kommt in vielen Situationen gut an", 14, False, DARK),
                                 ("– kann beliebig oder schwer greifbar wirken", 14, False, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.25)
box(s, 6.85, 2.6, 5.5, 3.1, GREY, [("Niedriges Self-Monitoring", 17, True, BLUE), ("", 6, False, DARK),
                                  ("+ berechenbar, glaubwürdig, „echt“", 14, False, DARK),
                                  ("– kann starr oder unpassend wirken", 14, False, DARK)],
    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.25)
box(s, 1.0, 5.85, 11.35, 0.7, LBLUE, [("Authentisch heißt nicht „immer so, wie mir gerade ist“, sondern: Mein Verhalten passt zu meinen Werten – "
                                      "die Form darf ich der Situation anpassen.", 14, True, DARK)], align=PP_ALIGN.LEFT, margin=0.15)

s = new_slide([("h", S6), ("sh", "Nervosität und Lampenfieber"),
               ("p", "Lampenfieber ist normal – und in Maßen sogar hilfreich. Andere bemerken es meist **weniger**, als wir glauben."),
               ("sh", "Umdeuten statt beruhigen"),
               ("p", "Alison Wood Brooks (2014): Wer sich vor einer Rede sagte **„Ich bin aufgeregt“** (im Sinne von begeistert), "
                     "schnitt besser ab als jemand, der versuchte, sich zu beruhigen."),
               ("sh", "Was außerdem hilft"),
               ("b", "Vorbereitung:: die ersten drei Sätze auswendig können"),
               ("b", "Atmung:: länger aus- als einatmen (z. B. 4 Sek. ein, 6 Sek. aus)"),
               ("b", "Bewegung:: vorher kurz gehen, Schultern lockern"),
               ("b", "Freundliche Gesichter:: zu Beginn Blickkontakt mit wohlwollenden Personen suchen")],
              W + "Lampenfieber")

s = new_slide([("h", S6), ("sh", "Strategien der Selbstdarstellung (Impression Management)")],
              W + "Impression-Management", body_h=1.0)
table(s, 1.0, 1.95, 11.35, [
    ["Strategie", "Ziel", "Risiko bei Übertreibung"],
    ["Sich beliebt machen", "sympathisch wirken", "wirkt anbiedernd"],
    ["Eigenwerbung", "kompetent wirken", "wirkt arrogant"],
    ["Vorbildlichkeit", "moralisch integer wirken", "wirkt scheinheilig"],
    ["Einschüchterung", "gefährlich / mächtig wirken", "Angst, Widerstand, Abwendung"],
    ["Hilfsbedürftigkeit", "Unterstützung erhalten", "wirkt inkompetent"],
], [3.3, 3.8, 4.25], size=14, rowh=0.65)
box(s, 1.0, 6.0, 11.35, 0.5, None, [("Nach Jones & Pittman (1982). Jede Strategie ist legitim – in Maßen und passend zur Situation.", 13, True, MID)],
    align=PP_ALIGN.LEFT, margin=0)

exercise(S6, "Kurzpräsentation mit Videofeedback", "Die eigene Wirkung vor einer Gruppe erleben und gezielt verbessern.",
         ["Bereiten Sie eine 2-minütige Vorstellung vor: „Wer ich bin und wofür ich stehe.“",
          "Präsentieren Sie stehend vor der Gruppe (Videoaufnahme freiwillig).",
          "Feedback: je eine Stärke und ein Tipp zu Haltung, Stimme und Sprache.",
          "Zweiter Durchgang mit einem konkreten Verbesserungsziel."],
         "60 Minuten", "Plenum oder zwei Gruppen", W + "Lampenfieber",
         notes="Feedbackbogen mit den Kategorien Stand, Blick, Gestik, Stimme, Sprache, Gesamteindruck austeilen.")

# ================= Modul 7
divider(7, S7, ["Wie gelingt der Einstieg ins Gespräch?", "Wie verschaffe ich mir in Meetings Gehör?",
                "Wie bleibe ich in kritischen Situationen souverän?"], W + "Smalltalk")

s = new_slide([("h", S7), ("sh", "Die ersten Sekunden: Begrüßung und Smalltalk")], W + "Smalltalk", body_h=1.0)
for k, (h, t) in enumerate([("Blick", "Blickkontakt aufnehmen, lächeln"), ("Name", "Sich vorstellen, Namen des Gegenübers verwenden"),
                             ("Händedruck", "Fest, kurz, trocken – mit Blickkontakt"), ("Smalltalk", "Offene Fragen, Anlass, gemeinsame Themen"),
                             ("Überleitung", "Zum Anliegen kommen: „Lassen Sie uns …“")]):
    x = 1.0 + k * 2.3
    chev(s, x, 2.1, 2.25, 0.95, BLUE if k % 2 == 0 else MID, [(h, 14, True, "FFFFFF")], first=(k == 0))
    box(s, x, 3.25, 2.05, 1.5, GREY, [(t, 13, False, DARK)], anchor=MSO_ANCHOR.TOP, margin=0.12)
box(s, 1.0, 5.05, 11.35, 1.25, LBLUE, [("Gute Smalltalk-Themen: Anreise, Veranstaltung, Branche, aktuelle positive Ereignisse. "
                                       "Zu meiden: Politik, Religion, Geld, Krankheit und Klatsch.", 14, False, DARK)],
    align=PP_ALIGN.LEFT, margin=0.2)

s = new_slide([("h", S7), ("sh", "Wirkung in Meetings"),
               ("b", "Früh etwas sagen:: Wer in den ersten Minuten spricht, wird eher als aktiv wahrgenommen"),
               ("b", "Sitzposition:: Blickkontakt zur leitenden Person und gute Sichtbarkeit wählen"),
               ("b", "Kernbotschaft zuerst:: Aussage – Begründung – Beispiel – Schluss"),
               ("b", "Unterbrechungen souverän begegnen:: „Einen Moment noch – ich komme gleich zum Punkt.“"),
               ("b", "Ideen sichern:: „Wie ich vorhin vorgeschlagen habe …“ – eigene Beiträge wieder aufgreifen"),
               ("b", "Zusammenfassen:: Wer den Stand zusammenfasst, wirkt strukturiert und führend"),
               ("b", "Zuhören zeigen:: Andere zitieren und wertschätzen stärkt die eigene Position"),
               ("sh", "Merksatz"),
               ("i", "Nicht wer am meisten spricht, wirkt am stärksten – sondern wer zur richtigen Zeit das Richtige sagt.")],
              W + "Besprechung")

s = new_slide([("h", S7), ("sh", "Der Elevator Pitch: sich in 60 Sekunden vorstellen")], W + "Elevator_Pitch", body_h=1.0)
for k, (h, t, e) in enumerate([("Wer?", "Name und Rolle", "„Ich bin … und leite …“"),
                                ("Was?", "Was ich tue", "„Wir sorgen dafür, dass …“"),
                                ("Wozu?", "Nutzen für andere", "„Das bedeutet für unsere Kunden …“"),
                                ("Beleg", "Beispiel oder Erfolg", "„Zuletzt haben wir …“"),
                                ("Weiter?", "Nächster Schritt", "„Wollen wir dazu kurz sprechen?“")]):
    x = 1.0 + k * 2.3
    chev(s, x, 2.1, 2.25, 0.95, BLUE if k % 2 == 0 else MID, [(h, 15, True, "FFFFFF")], first=(k == 0))
    box(s, x, 3.25, 2.05, 0.8, None, [(t, 14, True, DARK)], anchor=MSO_ANCHOR.TOP, margin=0.05)
    box(s, x, 4.05, 2.05, 1.5, LBLUE, [(e, 13, False, DARK)], anchor=MSO_ANCHOR.TOP, margin=0.12)
box(s, 1.0, 5.85, 11.35, 0.5, None, [("Nutzen vor Titel: Menschen merken sich, was Sie für sie tun – nicht Ihre Positionsbezeichnung.", 14, True, MID)],
    align=PP_ALIGN.LEFT, margin=0)

s = new_slide([("h", S7), ("sh", "Souverän bleiben in kritischen Momenten")], W + "Schlagfertigkeit", body_h=1.0)
table(s, 1.0, 1.95, 11.35, [
    ["Situation", "Souveräne Reaktion", "Beispiel"],
    ["Unsachliche Kritik", "Ruhig bleiben, Sachkern herausfiltern", "„Was genau stört Sie an dem Vorschlag?“"],
    ["Angriff vor der Gruppe", "Pause, Blickkontakt, Metaebene", "„Ich merke, das Thema ist Ihnen wichtig. Lassen Sie uns …“"],
    ["Frage, die ich nicht beantworten kann", "Ehrlich sein, Nachlieferung zusagen", "„Das prüfe ich und melde mich bis morgen.“"],
    ["Blackout", "Atmen, zusammenfassen, Stichwort nutzen", "„Ich fasse kurz zusammen, wo wir stehen …“"],
    ["Eigener Fehler", "Kurz eingestehen, Lösung anbieten", "„Da lag ich falsch – korrekt ist …“"],
], [3.0, 3.8, 4.55], size=13, rowh=0.72)

exercise(S7, "Schlüsselsituationen", "Die Werkzeuge des Tages in realistischen Situationen anwenden.",
         ["Wählen Sie eine Situation: Kundentermin, Meeting-Beitrag, Kritikgespräch oder Präsentation.",
          "Spielen Sie die ersten zwei Minuten der Situation im Rollenspiel.",
          "Beobachtende achten auf Körpersprache, Stimme, Sprache und Status.",
          "Feedback und zweiter Durchgang mit einer bewussten Veränderung."],
         "40 Minuten", "Dreiergruppen: Akteur/in, Gegenüber, Beobachter/in", W + "Rollenspiel",
         notes="Situationen möglichst aus dem Berufsalltag der Teilnehmenden wählen lassen.")

# ================= Modul 8
divider(8, S8, ["Was ist mein persönliches Wirkungsziel?", "Woran arbeite ich konkret?", "Wer gibt mir Feedback?"],
        W + "Feedback")

s = new_slide([("h", S8), ("sh", "Selbstcheck: Mein Wirkungsprofil"),
               ("p", "Bewerten Sie sich von **1 (trifft nicht zu)** bis **5 (trifft voll zu)** – und lassen Sie eine Vertrauensperson "
                     "denselben Bogen für Sie ausfüllen.")],
              W + "Selbstbild", body_h=1.55)
table(s, 1.0, 2.65, 11.35, [
    ["Bereich", "Aussage", "Selbst", "Fremd"],
    ["Erster Eindruck", "Ich begrüße Menschen offen, mit Blickkontakt und Namen.", "", ""],
    ["Körpersprache", "Ich stehe und sitze aufrecht und ruhig.", "", ""],
    ["Körpersprache", "Meine Gestik unterstützt, was ich sage.", "", ""],
    ["Stimme", "Ich spreche deutlich, mit Pausen und angemessenem Tempo.", "", ""],
    ["Sprache", "Ich formuliere klar und ohne Weichmacher.", "", ""],
    ["Erscheinungsbild", "Mein Äußeres passt zu Rolle und Anlass.", "", ""],
    ["Souveränität", "Auch unter Druck bleibe ich ruhig und freundlich.", "", ""],
], [2.6, 6.55, 1.1, 1.1], size=13, rowh=0.44)

s = new_slide([("h", S8), ("sh", "Mein persönlicher Transferplan"),
               ("p", "Beantworten Sie die Fragen schriftlich – konkret, realistisch und mit Termin.")],
              W + "Selbstmanagement", body_h=1.5)
for k, t in enumerate(["So möchte ich künftig wirken (drei Eigenschaften):", "Das behalte ich bei – das wirkt schon gut:",
                        "Diese eine Verhaltensweise verändere ich ab morgen:", "In dieser Situation probiere ich es zuerst aus:",
                        "Diese Person bitte ich in vier Wochen um Feedback:"]):
    box(s, 1.0, 2.6 + k * 0.75, 11.35, 0.63, LBLUE if k % 2 == 0 else GREY, [(t, 15, True, BLUE)], align=PP_ALIGN.LEFT, margin=0.2)

s = new_slide([("h", S8), ("sh", "Zusammenfassung: Die wichtigsten Erkenntnisse")], W + "Kommunikation", body_h=1.0)
for k, (h, t) in enumerate([("Wirkung entsteht beim anderen", "Wir können sie gestalten, aber nicht kontrollieren."),
                             ("Der erste Eindruck zählt", "Wärme zuerst, dann Kompetenz – in den ersten Sekunden."),
                             ("Das Fremdbild kennen", "Feedback verkleinert den blinden Fleck."),
                             ("Kongruenz überzeugt", "Wort, Stimme und Körper senden dieselbe Botschaft."),
                             ("Souveränität ist Verhalten", "Haltung, Pausen und klare Sprache lassen sich trainieren."),
                             ("Authentisch bleiben", "Die Form anpassen, die eigenen Werte behalten.")]):
    x = 1.0 + (k % 2) * 5.75
    y = 2.0 + (k // 2) * 1.4
    box(s, x, y, 0.8, 0.8, BLUE if k % 2 == 0 else MID, [(str(k + 1), 20, True, "FFFFFF")], shape=MSO_SHAPE.OVAL, margin=0)
    box(s, x + 0.95, y - 0.1, 4.6, 1.2, None, [(h, 16, True, BLUE), (t, 13, False, DARK)], align=PP_ALIGN.LEFT,
        anchor=MSO_ANCHOR.TOP, margin=0.02)

s = new_slide([("h", S8), ("sh", "Literaturempfehlungen"),
               ("b", "Cuddy, A. (2016):: Dein Körper spricht für dich. München: Mosaik."),
               ("b", "Johnstone, K. (2010):: Improvisation und Theater. Berlin: Alexander Verlag."),
               ("b", "Molcho, S. (2013):: Alles über Körpersprache. München: Goldmann."),
               ("b", "Navarro, J. (2011):: Menschen lesen. München: mvg."),
               ("b", "Schulz von Thun, F. (1981):: Miteinander reden 1. Reinbek: Rowohlt."),
               ("b", "Watzlawick, P., Beavin, J. & Jackson, D. (2016):: Menschliche Kommunikation. Bern: Hogrefe."),
               ("b", "Kahneman, D. (2012):: Schnelles Denken, langsames Denken. München: Siedler."),
               ("b", "Fiske, S., Cuddy, A. & Glick, P. (2007):: Universal dimensions of social cognition. Trends in Cognitive Sciences, 11(2).")],
              W + "Kommunikation")

# --- Inhaltsverzeichnis (Folien 3/4) aus den Modulen erzeugen
toc = {S1: ["Wie Wahrnehmung funktioniert", "Der erste Eindruck – Wärme und Kompetenz", "Mythos 7-38-55 und Wahrnehmungsfehler"],
       S2: ["Selbstbild, Wunschbild, Fremdbild", "Johari-Fenster und blinde Flecken", "Feedback geben und nehmen"],
       S3: ["Vier Kanäle der Wirkung", "Haltung, Gestik, Mimik, Blickkontakt", "Distanzzonen und Deutung"],
       S4: ["Stimme als Visitenkarte", "Klare Sprache statt Weichmacher", "Watzlawick und das Vier-Seiten-Modell"],
       S5: ["Extraverbale Signale", "Dresscodes und Passung", "Digitale Außenwirkung"],
       S6: ["Hochstatus und Tiefstatus", "Präsenz, Authentizität und Lampenfieber", "Strategien der Selbstdarstellung"],
       S7: ["Begrüßung und Smalltalk", "Wirkung in Meetings und Elevator Pitch", "Souverän in kritischen Momenten"],
       S8: ["Wirkungsprofil und Transferplan", "Zusammenfassung"]}
for sl, secs, label in ((toc1, [S1, S2, S3, S4], "INHALTE /1"), (toc2, [S5, S6, S7, S8], "INHALTE /2")):
    items = [("h", label, 1800)]
    for sec in secs:
        items.append(("sh", sec, 1800))
        items += [("b", t, 1500) for t in toc[sec]]
    set_body(by_ph(sl, 2), items)

# --- Abschlussfolie: themenfremdes Bild entfernen
for sh in list(end_slide.shapes):
    if sh.shape_type == 13:
        sh._element.getparent().remove(sh._element)
end_slide.notes_slide.notes_text_frame.text = "Blitzlicht: Was nehme ich mit? Feedbackbogen, Verabschiedung."

# --- Folienreihenfolge: Titel, Willkommen, Inhalte 1/2, neue Folien, Abschluss
lst = prs.slides._sldIdLst
ids = list(lst)
n_tpl = len(tpl)
keep_front = ids[:4]
end_id = ids[n_tpl - 1]
for sid in ids[4:n_tpl - 1]:
    prs.part.drop_rel(sid.get(R + "id"))
    lst.remove(sid)
lst.remove(end_id)
lst.append(end_id)

prs.save(OUT)
print("Folien:", len(prs.slides))
