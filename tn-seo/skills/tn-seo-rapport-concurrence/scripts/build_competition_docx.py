#!/usr/bin/env python3
"""build_competition_docx.py - Word du rapport concurrence (charte Suisseo).

Entree : report_data.json enrichi par prepare_competitors.py. Sortie : --out .docx ; --logo optionnel.
Sections : Part de voix, Comparatif positions, Evolution hebdo (courbe dans xlsx), Ou les
concurrents nous devancent.
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
GREEN_BG_HEX = "F0F9E8"
LOSS_HEX = "FBE9E7"


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--logo")
    args = ap.parse_args()
    with open(args.data, encoding="utf-8") as fh:
        R = json.load(fh)
    comp = R.get("competition")
    if not comp:
        raise SystemExit("ERREUR: report_data.json sans bloc competition")
    m = R["meta"]
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
    r = t.add_run("Rapport concurrence")
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
    sec.header.paragraphs[0].text = "Suisseo - Rapport concurrence - " + str(m.get("client", "")) + " - " + str(m.get("period_current", ""))
    for rr in sec.header.paragraphs[0].runs:
        rr.font.size = Pt(8)
        rr.font.color.rgb = GREY
    doc.add_page_break()

    # 1. Part de voix
    heading(doc, "1. Part de voix")
    sov = comp.get("share_of_voice") or []
    client_sov = next((x for x in sov if x.get("is_client")), None)
    if client_sov:
        rank = sov.index(client_sov) + 1
        body(doc, str(client_sov["domain"]) + " : " + str(client_sov["visibility"]) + "% de visibilite, rang " + str(rank) + " sur " + str(len(sov)) + " acteurs compares ce mois-ci.")
    if sov:
        tt = doc.add_table(rows=len(sov) + 1, cols=2)
        tt.alignment = WD_TABLE_ALIGNMENT.LEFT
        set_cell(tt.rows[0].cells[0], "Domaine", bold=True, color=WHITE, bg=DARK_HEX)
        set_cell(tt.rows[0].cells[1], "Visibilite (%)", bold=True, color=WHITE, align="center", bg=DARK_HEX)
        for i, x in enumerate(sov, 1):
            is_c = x.get("is_client")
            set_cell(tt.rows[i].cells[0], x["domain"], bold=is_c, color=DARK if is_c else TEXT, bg=GREEN_BG_HEX if is_c else None)
            set_cell(tt.rows[i].cells[1], x["visibility"], align="center", bg=GREEN_BG_HEX if is_c else None)

    # 2. Comparatif positions
    heading(doc, "2. Comparatif des positions")
    actors = [comp["client"]] + comp["competitors"]
    tt = doc.add_table(rows=len(actors) + 1, cols=4)
    head = ["Acteur", "TOP 10 (" + str(m.get("period_current", "M")) + ")", "Pos. moyenne", "TOP 10 (" + str(m.get("period_prev", "M-1")) + ")"]
    for j, v in enumerate(head):
        set_cell(tt.rows[0].cells[j], v, bold=True, color=WHITE, align="center" if j else "left", bg=DARK_HEX)
    for i, a in enumerate(actors, 1):
        is_c = a.get("is_client", False)
        bg = GREEN_BG_HEX if is_c else None
        set_cell(tt.rows[i].cells[0], a["name"], bold=is_c, color=DARK if is_c else TEXT, bg=bg)
        set_cell(tt.rows[i].cells[1], a["monthly"]["current"].get("top10", "-"), align="center", bg=bg)
        set_cell(tt.rows[i].cells[2], "-" if a["monthly"]["current"].get("avg") is None else a["monthly"]["current"]["avg"], align="center", bg=bg)
        set_cell(tt.rows[i].cells[3], a["monthly"]["prev"].get("top10", "-"), align="center", bg=bg)

    # 3. Evolution hebdo
    heading(doc, "3. Evolution hebdomadaire")
    body(doc, "La courbe comparee du nombre de mots-cles en TOP 10 (client vs concurrents) figure dans l'Excel, onglet Evolution hebdo.")

    # 4. Ou les concurrents nous devancent
    heading(doc, "4. Ou les concurrents nous devancent")
    losses = [h for h in comp["head_to_head"] if not h.get("client_wins") and (h["volume"] or 0) > 0][:12]
    if not losses:
        body(doc, "Aucun mot-cle a fort volume ou un concurrent devance le client ce mois-ci.", color=GREY)
    else:
        body(doc, "Mots-cles a plus fort volume ou au moins un concurrent est mieux positionne que le client. Cibles de reconquete prioritaires.")
        for h in losses:
            best_comp = min((c for c in h["comps"]), key=lambda c: c["pos"] if c["pos"] is not None else 999)
            line = str(h["keyword"]) + " (vol. " + str(h["volume"]) + ") : client " + str(pos_label(h["client_pos"])) + ", " + str(best_comp["name"]) + " " + str(pos_label(best_comp["pos"]))
            p = doc.add_paragraph(style="List Bullet")
            rr = p.add_run(line)
            rr.font.name = "Calibri"
            rr.font.size = Pt(10)
            rr.font.color.rgb = TEXT

    doc.save(args.out)
    print("OK docx concurrence : " + args.out)


if __name__ == "__main__":
    main()
