#!/usr/bin/env python3
"""build_opportunities_xlsx.py - Classeur Excel du rapport opportunites SEO.

Entree : report_data.json enrichi par analyze_opportunities.py. Sortie : --out .xlsx
Onglets : Synthese, Quick wins TOP 3, Quick wins TOP 10, Page 2-3, A aller chercher,
Pages a optimiser. Chaque liste est triee par volume (priorite trafic).
"""
import argparse
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DARK = "2B3A4E"
GREEN = "95C11F"
GREEN_BG = "F0F9E8"
GREYBG = "E8EAED"
WHITE = "FFFFFF"
H_FONT = Font(name="Calibri", bold=True, color=WHITE, size=11)
H_FILL = PatternFill("solid", fgColor=DARK)
THIN = Side(style="thin", color="CCCCCC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center")
LEFT = Alignment(horizontal="left", vertical="center")


def header_row(ws, row, headers, widths=None):
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = H_FONT
        c.fill = H_FILL
        c.alignment = CENTER
        c.border = BORDER
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def pos_label(p):
    return ">100" if p is None else p


def list_sheet(wb, name, items):
    ws = wb.create_sheet(name)
    header_row(ws, 1, ["Mot-cle", "Volume", "Position actuelle", "Cible", "Places a gagner", "Page"],
               widths=[34, 9, 16, 16, 16, 60])
    for i, it in enumerate(items, 2):
        ws.cell(row=i, column=1, value=it["keyword"]).border = BORDER
        ws.cell(row=i, column=2, value=it["volume"]).border = BORDER
        ws.cell(row=i, column=3, value=pos_label(it["pos"])).border = BORDER
        ws.cell(row=i, column=4, value=it["cible"]).border = BORDER
        ws.cell(row=i, column=5, value="-" if it.get("gain") is None else it["gain"]).border = BORDER
        ws.cell(row=i, column=6, value=it["page"]).border = BORDER
    if not items:
        ws.cell(row=2, column=1, value="(aucune)")
    ws.auto_filter.ref = "A1:F" + str(max(2, len(items) + 1))
    ws.freeze_panes = "A2"
    return ws


def sheet_synthese(wb, R):
    ws = wb.active
    ws.title = "Synthese"
    m = R["meta"]
    o = R["opportunities"]["totals"]
    ws["A1"] = "Rapport opportunites SEO - " + str(m.get("client", "")) + " - " + str(m.get("period_current", ""))
    ws["A1"].font = Font(name="Calibri", bold=True, size=14, color=DARK)
    ws["A2"] = str(m.get("domain", "")) + " - " + str(m.get("engine_label", ""))
    ws["A2"].font = Font(name="Calibri", size=10, color="666666")
    rows = [
        ("Indicateur", "Valeur"),
        ("Volume de recherche total (mots-cles suivis)", o["volume_total"]),
        ("Volume capte en TOP 10", o["volume_top10"]),
        ("Volume capte en TOP 3", o["volume_top3"]),
        ("Volume NON capte (hors TOP 10)", o["volume_non_capte"]),
        ("Quick wins TOP 3 (positions 4-10)", o["n_quick_top3"]),
        ("Quick wins TOP 10 (positions 11-20)", o["n_quick_top10"]),
        ("Mots-cles a aller chercher (>30 / absents)", o["n_to_chase"]),
    ]
    header_row(ws, 4, rows[0], widths=[44, 18])
    for i, (lab, val) in enumerate(rows[1:], 5):
        a = ws.cell(row=i, column=1, value=lab)
        a.border = BORDER
        a.fill = PatternFill("solid", fgColor=GREYBG)
        a.font = Font(name="Calibri", bold=True, color=DARK)
        b = ws.cell(row=i, column=2, value=val)
        b.border = BORDER
        b.alignment = CENTER
    ws.freeze_panes = "A5"
    return ws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    with open(args.data, encoding="utf-8") as fh:
        R = json.load(fh)
    if not R.get("opportunities"):
        raise SystemExit("ERREUR: report_data.json sans bloc opportunities (lancer analyze_opportunities.py)")
    o = R["opportunities"]
    wb = Workbook()
    sheet_synthese(wb, R)
    list_sheet(wb, "Quick wins TOP 3", o["quick_top3"])
    list_sheet(wb, "Quick wins TOP 10", o["quick_top10"])
    list_sheet(wb, "Page 2-3", o["page23"])
    list_sheet(wb, "A aller chercher", o["to_chase"])
    # Pages a optimiser
    ws = wb.create_sheet("Pages a optimiser")
    header_row(ws, 1, ["Page", "Nb mots-cles", "Volume cumule", "Position moyenne", "Mots-cles TOP 10"],
               widths=[60, 13, 14, 16, 16])
    for i, p in enumerate(o["weak_pages"], 2):
        ws.cell(row=i, column=1, value=p["page"]).border = BORDER
        ws.cell(row=i, column=2, value=p["n_keywords"]).border = BORDER
        ws.cell(row=i, column=3, value=p["sum_volume"]).border = BORDER
        ws.cell(row=i, column=4, value="-" if p["avg_pos"] is None else p["avg_pos"]).border = BORDER
        ws.cell(row=i, column=5, value=p["top10"]).border = BORDER
    if not o["weak_pages"]:
        ws.cell(row=2, column=1, value="(aucune)")
    ws.freeze_panes = "A2"
    wb.save(args.out)
    print("OK xlsx opportunites : " + args.out)


if __name__ == "__main__":
    main()
