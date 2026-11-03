#!/usr/bin/env python3
"""build_opportunities_docx.py - Word du rapport opportunites SEO (charte Suisseo).

Entree : report_data.json enrichi par analyze_opportunities.py. Sortie : --out .docx ; --logo opt.
Document oriente action : ou se trouvent les paliers non franchis et lesquels cibler en priorite.
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


def shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:fill"), hexc)
    tcPr.append(sh)


def set_cell(cell, text, bold=False, color=TEXT, size=9, align="left", bg=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if align == "center" else WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(str(text))
    r.bold = bold
    r.font.color.rgb = color
    r.font.size = Pt(size)
    r.font.name = "Calibri"
    if bg:
        shade(cell, bg)


def heading(doc, text, size=15):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.color.rgb = DARK
    r.font.size = Pt(size)
    return p


def body(doc, text, color=TEXT, size=10):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(size)
    r.font.color.rgb = color
    return p


def pos_label(p):
    return ">100" if p is None else p


def bullets(doc, items, n=10):
    if not items:
        body(doc, "Aucun element.", color=GREY)
        return
    for it in items[:n]:
        gain = "" if it.get("gain") in (None, 0) else (" (" + str(it["gain"]) + " places a gagner)")
        line = str(it["keyword"]) + " (vol. " + str(it["volume"]) + ") : position " + str(pos_label(it["pos"])) + " -> cible " + str(it["cible"]) + gain + " - " + str(it["page"])
        p = doc.add_paragraph(style="List Bullet")
        r = p.add_run(line)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = TEXT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--logo")
    args = ap.parse_args()
    with open(args.data, encoding="utf-8") as fh:
        R = json.load(fh)
    if not R.get("opportunities"):
        raise SystemExit("ERREUR: report_data.json sans bloc opportunities")
    m = R["meta"]
    o = R["opportunities"]
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10)
    st.font.color.rgb = TEXT

    if args.logo:
        try:
            doc.add_paragraph().add_run().add_picture(args.logo, width=Cm(5))
        except Exception:
            pass
    doc.add_paragraph()
    t = doc.add_paragraph()
    r = t.add_run("Rapport opportunites SEO")
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
    body(doc, "Periode : " + str(m.get("period_current", "")) + "  -  Consultant : " + str(m.get("consultant", "Thomas Nedjar")), color=GREY)
    sec = doc.sections[0]
    sec.header.paragraphs[0].text = "Suisseo - Opportunites SEO - " + str(m.get("client", "")) + " - " + str(m.get("period_current", ""))
    for rr in sec.header.paragraphs[0].runs:
        rr.font.size = Pt(8)
        rr.font.color.rgb = GREY
    doc.add_page_break()

    tot = o["totals"]
    heading(doc, "1. Synthese")
    pct = round(100 * tot["volume_top10"] / tot["volume_total"], 1) if tot["volume_total"] else 0
    body(doc, "Sur " + str(tot["volume_total"]) + " de volume de recherche cumule sur les mots-cles suivis, "
         + str(tot["volume_top10"]) + " sont captes en TOP 10 (" + str(pct) + "%). "
         + "Volume non capte : " + str(tot["volume_non_capte"]) + ". "
         + str(tot["n_quick_top3"]) + " quick wins TOP 3, " + str(tot["n_quick_top10"]) + " quick wins TOP 10, "
         + str(tot["n_to_chase"]) + " mots-cles a aller chercher.")

    heading(doc, "2. Quick wins TOP 3 (positions 4-10)")
    body(doc, "Mots-cles juste au-dessus du TOP 3 : le meilleur rapport effort/trafic. A cibler en priorite.", color=GREY)
    bullets(doc, o["quick_top3"], 10)

    heading(doc, "3. Quick wins TOP 10 (positions 11-20)")
    body(doc, "Haut de page 2 : passer en page 1 debloque l'essentiel du trafic.", color=GREY)
    bullets(doc, o["quick_top10"], 10)

    heading(doc, "4. Pages a optimiser")
    body(doc, "Pages a volume cumule consequent mais position moyenne faible : un travail on-page y a le plus d'impact.", color=GREY)
    wp = o["weak_pages"][:10]
    if not wp:
        body(doc, "Aucune.", color=GREY)
    else:
        tt = doc.add_table(rows=len(wp) + 1, cols=4)
        tt.alignment = WD_TABLE_ALIGNMENT.LEFT
        for j, v in enumerate(["Page", "Mots-cles", "Volume cumule", "Pos. moyenne"]):
            set_cell(tt.rows[0].cells[j], v, bold=True, color=WHITE, align="center" if j else "left", bg=DARK_HEX)
        for i, p in enumerate(wp, 1):
            set_cell(tt.rows[i].cells[0], p["page"], size=8)
            set_cell(tt.rows[i].cells[1], p["n_keywords"], align="center")
            set_cell(tt.rows[i].cells[2], p["sum_volume"], align="center")
            set_cell(tt.rows[i].cells[3], "-" if p["avg_pos"] is None else p["avg_pos"], align="center")

    heading(doc, "5. A aller chercher (fort volume, hors radar)")
    body(doc, "Mots-cles a fort volume non encore positionnes ou hors TOP 30 : cibles de contenu a moyen terme.", color=GREY)
    bullets(doc, o["to_chase"], 10)

    doc.save(args.out)
    print("OK docx opportunites : " + args.out)


if __name__ == "__main__":
    main()
