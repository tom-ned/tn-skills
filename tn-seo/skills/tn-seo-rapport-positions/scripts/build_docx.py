#!/usr/bin/env python3
"""build_docx.py - Synthese Word du reporting mensuel (charte Suisseo).

Entree : report_data.json (prepare_data.py, eventuellement enrichi par prepare_competitors.py)
Sortie : --out chemin .docx ; --logo chemin logo_suisseo_dark.png (optionnel)
"""
import argparse
import json
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DARK = RGBColor(0x2B, 0x3A, 0x4E)
GREEN = RGBColor(0x95, 0xC1, 0x1F)
TEXT = RGBColor(0x33, 0x33, 0x33)
GREY = RGBColor(0x66, 0x66, 0x66)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_HEX = "2B3A4E"
GREYBG_HEX = "E8EAED"
GREEN_BG_HEX = "F0F9E8"


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:fill"), hex_color)
    tcPr.append(sh)


def set_cell(cell, text, bold=False, color=TEXT, size=9, align="left", bg=None):
    cell.text = ""
    p = cell.paragraphs[0]
    amap = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER}
    p.alignment = amap.get(align, WD_ALIGN_PARAGRAPH.LEFT)
    r = p.add_run(str(text))
    r.bold = bold
    r.font.color.rgb = color
    r.font.size = Pt(size)
    r.font.name = "Calibri"
    if bg:
        shade(cell, bg)


def heading(doc, text, level=1):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.color.rgb = DARK
    r.font.size = Pt(15 if level == 1 else 12)
    return p


def body(doc, text, size=10, color=TEXT):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(size)
    r.font.color.rgb = color
    return p


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10)
    r.font.color.rgb = TEXT
    return p


def evol_pos(delta):
    if delta is None:
        return "-"
    if delta == 0:
        return "stable"
    return ("+" + str(-delta) + " places") if delta < 0 else ("-" + str(delta) + " places")


def pos_label(p):
    return ">100" if p is None else p


def add_header_footer(doc, R):
    sec = doc.sections[0]
    m = R["meta"]
    h = sec.header.paragraphs[0]
    h.text = "Suisseo - Reporting SEO - " + str(m.get("client", "")) + " - " + str(m.get("period_current", ""))
    for r in h.runs:
        r.font.size = Pt(8)
        r.font.color.rgb = GREY
        r.font.name = "Calibri"
    f = sec.footer.paragraphs[0]
    f.text = "Consultant : " + str(m.get("consultant", "Thomas Nedjar")) + "  |  Donnees SE Ranking"
    for r in f.runs:
        r.font.size = Pt(8)
        r.font.color.rgb = GREY
        r.font.name = "Calibri"


def kpi_table(doc, R):
    s = R["summary"]
    m = R["meta"]
    rows = [
        ["Indicateur", m.get("period_prev2", "M-2"), m.get("period_prev", "M-1"), m.get("period_current", "M")],
        ["Mots-cles positionnes", s["prev2"]["tracked"], s["prev"]["tracked"], s["current"]["tracked"]],
        ["TOP 3", s["prev2"]["top3"], s["prev"]["top3"], s["current"]["top3"]],
        ["TOP 10", s["prev2"]["top10"], s["prev"]["top10"], s["current"]["top10"]],
        ["TOP 30", s["prev2"]["top30"], s["prev"]["top30"], s["current"]["top30"]],
        ["Position moyenne", s["prev2"]["avg_pos"], s["prev"]["avg_pos"], s["current"]["avg_pos"]],
    ]
    t = doc.add_table(rows=len(rows), cols=4)
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for j, val in enumerate(rows[0]):
        set_cell(t.rows[0].cells[j], val, bold=True, color=WHITE, align="center" if j else "left", bg=DARK_HEX)
    for i in range(1, len(rows)):
        for j, val in enumerate(rows[i]):
            set_cell(t.rows[i].cells[j], "-" if val is None else val, bold=(j == 0),
                     color=DARK if j == 0 else TEXT, align="center" if j else "left",
                     bg=GREYBG_HEX if j == 0 else None)
    return t


def highlight_block(doc, title, items):
    heading(doc, title, level=2)
    if not items:
        body(doc, "Aucun element ce mois-ci.", color=GREY)
        return
    for k in items[:8]:
        txt = (str(k["keyword"]) + " (vol. " + str(k["volume"]) + ") : "
               + str(pos_label(k["pos_prev"])) + " > " + str(pos_label(k["pos_current"]))
               + " (" + evol_pos(k["delta"]) + ") - " + str(k["page"]))
        bullet(doc, txt)


def competition_section(doc, R, num):
    comp = R.get("competition")
    if not comp:
        return num
    m = R["meta"]
    heading(doc, str(num) + ". Concurrence")
    sov = comp.get("share_of_voice") or []
    client_sov = next((x for x in sov if x.get("is_client")), None)
    if client_sov:
        rank = sov.index(client_sov) + 1
        body(doc, "Part de voix instantanee : " + str(client_sov["domain"]) + " a "
             + str(client_sov["visibility"]) + "% de visibilite, rang " + str(rank)
             + " parmi les " + str(len(sov)) + " acteurs compares.")
    names = ", ".join(c["name"] for c in comp["competitors"])
    body(doc, "Comparaison sur les mots-cles suivis face a : " + names
         + ". Le detail hebdomadaire (courbe comparee TOP 10) figure dans l'Excel, onglet Concurrence.")
    actors = [comp["client"]] + comp["competitors"]
    t = doc.add_table(rows=len(actors) + 1, cols=3)
    head = ["Acteur", "TOP 10 (" + str(m.get("period_current", "M")) + ")",
            "Position moyenne (" + str(m.get("period_current", "M")) + ")"]
    for j, val in enumerate(head):
        set_cell(t.rows[0].cells[j], val, bold=True, color=WHITE, align="center" if j else "left", bg=DARK_HEX)
    for i, a in enumerate(actors, 1):
        cur = a["monthly"]["current"]
        is_c = a.get("is_client", False)
        bg = GREEN_BG_HEX if is_c else None
        set_cell(t.rows[i].cells[0], a["name"], bold=is_c, color=DARK if is_c else TEXT, bg=bg)
        set_cell(t.rows[i].cells[1], cur.get("top10", "-"), align="center", bg=bg)
        set_cell(t.rows[i].cells[2], "-" if cur.get("avg") is None else cur.get("avg"), align="center", bg=bg)
    return num + 1


def pages_table(doc, R, top=10):
    rows = R["pages"][:top]
    t = doc.add_table(rows=len(rows) + 1, cols=5)
    head = ["Page", "Mots-cles", "Volume cumule", "Pos. moy.", "TOP 10"]
    for j, val in enumerate(head):
        set_cell(t.rows[0].cells[j], val, bold=True, color=WHITE, align="center" if j else "left", bg=DARK_HEX)
    for i, p in enumerate(rows, 1):
        set_cell(t.rows[i].cells[0], p["page"], size=8)
        set_cell(t.rows[i].cells[1], p["n_keywords"], align="center")
        set_cell(t.rows[i].cells[2], p["sum_volume"], align="center")
        set_cell(t.rows[i].cells[3], "-" if p["avg_pos"] is None else p["avg_pos"], align="center")
        set_cell(t.rows[i].cells[4], p["top10"], align="center")
    return t


def cover(doc, m, logo):
    if logo:
        try:
            doc.add_paragraph().add_run().add_picture(logo, width=Cm(5))
        except Exception:
            pass
    doc.add_paragraph()
    title = doc.add_paragraph()
    r = title.add_run("Reporting SEO mensuel")
    r.bold = True
    r.font.size = Pt(26)
    r.font.color.rgb = DARK
    r.font.name = "Calibri"
    sub = doc.add_paragraph()
    r = sub.add_run(str(m.get("client", "")))
    r.bold = True
    r.font.size = Pt(16)
    r.font.color.rgb = GREEN
    r.font.name = "Calibri"
    body(doc, str(m.get("domain", "")) + "  -  " + str(m.get("engine_label", "")), color=GREY)
    body(doc, "Periode analysee : " + str(m.get("period_current", "")) + "  (comparaison vs "
         + str(m.get("period_prev", "")) + " et " + str(m.get("period_prev2", "")) + ")", color=GREY)
    body(doc, "Date d'edition : " + str(m.get("generated_at", "")) + "  -  Consultant : "
         + str(m.get("consultant", "Thomas Nedjar")), color=GREY)


def synthese_text(doc, R, m):
    s = R["summary"]
    d10 = (s["current"]["top10"] or 0) - (s["prev"]["top10"] or 0)
    sens = "progression" if d10 > 0 else ("recul" if d10 < 0 else "stabilite")
    sign = "+" if d10 > 0 else ""
    body(doc, "Le projet suit " + str(R["counts"]["keywords"]) + " mots-cles repartis sur "
         + str(R["counts"]["pages"]) + " pages. Ce mois-ci, " + str(s["current"]["top10"])
         + " mots-cles se positionnent en TOP 10 (" + sign + str(d10) + " vs "
         + str(m.get("period_prev", "M-1")) + "), dont " + str(s["current"]["top3"])
         + " en TOP 3. Tendance globale : " + sens + ".")


def hebdo_text(doc, R):
    vis = R["weekly_trend"]["visibility_percent"]["values"]
    first = next((v for v in vis if v is not None), None)
    last = next((v for v in reversed(vis) if v is not None), None)
    if first is not None and last is not None:
        d = round(last - first, 1)
        sign = "+" if d > 0 else ""
        body(doc, "Sur la periode, la visibilite passe de " + str(first) + "% a " + str(last)
             + "% (" + sign + str(d) + " pt). Le detail hebdomadaire et les courbes figurent dans "
             + "le classeur Excel, onglet Evolution hebdo.")
    else:
        body(doc, "Le detail hebdomadaire figure dans le classeur Excel, onglet Evolution hebdo.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--logo")
    args = ap.parse_args()
    with open(args.data, encoding="utf-8") as fh:
        R = json.load(fh)
    m = R["meta"]
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10)
    st.font.color.rgb = TEXT

    cover(doc, m, args.logo)
    add_header_footer(doc, R)
    doc.add_page_break()

    heading(doc, "1. Synthese du mois")
    synthese_text(doc, R, m)
    kpi_table(doc, R)

    heading(doc, "2. Faits marquants")
    highlight_block(doc, "Plus fortes progressions", R["highlights"]["gains"])
    highlight_block(doc, "Entrees en TOP 3 / TOP 10", R["highlights"]["top_entries"])
    highlight_block(doc, "Fort volume en TOP 10", R["highlights"]["high_volume"])
    highlight_block(doc, "Points de vigilance (pertes de positions)", R["highlights"]["top_exits"])

    heading(doc, "3. Evolution hebdomadaire")
    hebdo_text(doc, R)

    next_num = competition_section(doc, R, 4)

    heading(doc, str(next_num) + ". Pages les plus contributrices")
    body(doc, "Classement des pages par volume de recherche cumule des mots-cles qu'elles captent. "
         "La ventilation complete est dans l'Excel, onglet Par page.")
    pages_table(doc, R, top=10)

    doc.save(args.out)
    print("OK docx : " + args.out)


if __name__ == "__main__":
    main()
