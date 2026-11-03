#!/usr/bin/env python3
"""build_competition_xlsx.py - Classeur Excel du rapport concurrence.

Entree : report_data.json enrichi par prepare_competitors.py (bloc competition requis).
Onglets : Part de voix, Comparatif (M-2/M-1/M), Evolution hebdo (graphe natif compare),
Face a face (position par mot-cle client vs concurrents).
"""
import argparse
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, Reference
from openpyxl.utils import get_column_letter

DARK = "2B3A4E"
GREEN_BG = "F0F9E8"
LOSS_BG = "FBE9E7"
WHITE = "FFFFFF"
H_FONT = Font(name="Calibri", bold=True, color=WHITE, size=11)
H_FILL = PatternFill("solid", fgColor=DARK)
GAIN_FILL = PatternFill("solid", fgColor=GREEN_BG)
LOSS_FILL = PatternFill("solid", fgColor=LOSS_BG)
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


def sheet_sov(wb, R):
    comp = R["competition"]
    m = R["meta"]
    ws = wb.active
    ws.title = "Part de voix"
    ws["A1"] = "Rapport concurrence - " + str(m.get("client", "")) + " - " + str(m.get("period_current", ""))
    ws["A1"].font = Font(name="Calibri", bold=True, size=14, color=DARK)
    ws["A2"] = str(m.get("domain", "")) + " - " + str(m.get("engine_label", ""))
    ws["A2"].font = Font(name="Calibri", size=10, color="666666")
    row = 4
    if comp.get("share_of_voice"):
        header_row(ws, row, ["Domaine", "Part de visibilite (%)"], widths=[44, 22])
        row += 1
        for sov in comp["share_of_voice"]:
            ws.cell(row=row, column=1, value=sov["domain"]).border = BORDER
            ws.cell(row=row, column=2, value=sov["visibility"]).border = BORDER
            if sov.get("is_client"):
                for col in (1, 2):
                    ws.cell(row=row, column=col).fill = GAIN_FILL
                    ws.cell(row=row, column=col).font = Font(name="Calibri", bold=True, color=DARK)
            row += 1
    else:
        ws.cell(row=row, column=1, value="(part de voix indisponible)")
    ws.freeze_panes = "A5"
    return ws


def sheet_comparatif(wb, R):
    comp = R["competition"]
    m = R["meta"]
    ws = wb.create_sheet("Comparatif")
    header_row(ws, 1, ["Acteur",
                       "TOP10 " + str(m.get("period_prev2", "M-2")), "TOP10 " + str(m.get("period_prev", "M-1")), "TOP10 " + str(m.get("period_current", "M")),
                       "Pos.moy " + str(m.get("period_prev2", "M-2")), "Pos.moy " + str(m.get("period_prev", "M-1")), "Pos.moy " + str(m.get("period_current", "M"))],
               widths=[30, 12, 12, 12, 13, 13, 13])
    actors = [comp["client"]] + comp["competitors"]
    r = 2
    for a in actors:
        mm = a["monthly"]
        cells = [a["name"], mm["prev2"]["top10"], mm["prev"]["top10"], mm["current"]["top10"],
                 mm["prev2"]["avg"], mm["prev"]["avg"], mm["current"]["avg"]]
        for j, v in enumerate(cells, 1):
            cc = ws.cell(row=r, column=j, value="-" if v is None else v)
            cc.border = BORDER
            cc.alignment = LEFT if j == 1 else CENTER
            if a.get("is_client"):
                cc.fill = GAIN_FILL
        r += 1
    ws.freeze_panes = "A2"
    return ws


def sheet_weekly(wb, R):
    comp = R["competition"]
    ws = wb.create_sheet("Evolution hebdo")
    actors = [comp["client"]] + comp["competitors"]
    labels = comp["client"]["weekly_top10"]["labels"]
    header_row(ws, 1, ["Semaine"] + [a["name"] for a in actors], widths=[14] + [16] * len(actors))
    maps = []
    for a in actors:
        wt = a["weekly_top10"]
        maps.append({lab: val for lab, val in zip(wt["labels"], wt["values"])})
    for i, lab in enumerate(labels):
        rr = 2 + i
        ws.cell(row=rr, column=1, value=lab).border = BORDER
        for j, mp in enumerate(maps, 2):
            ws.cell(row=rr, column=j, value=mp.get(lab)).border = BORDER
    if labels:
        last = 1 + len(labels)
        ch = LineChart()
        ch.title = "Mots-cles en TOP 10 - client vs concurrents"
        ch.height = 9
        ch.width = 22
        ch.style = 2
        data = Reference(ws, min_col=2, max_col=1 + len(actors), min_row=1, max_row=last)
        cats = Reference(ws, min_col=1, min_row=2, max_row=last)
        ch.add_data(data, titles_from_data=True)
        ch.set_categories(cats)
        ws.add_chart(ch, get_column_letter(3 + len(actors)) + "2")
    ws.freeze_panes = "A2"
    return ws


def sheet_face(wb, R):
    comp = R["competition"]
    ws = wb.create_sheet("Face a face")
    comp_names = [c["name"] for c in comp["competitors"]]
    headers = ["Mot-cle", "Volume", "Page", "Client"] + comp_names + ["Meilleur"]
    header_row(ws, 1, headers, widths=[34, 9, 50, 10] + [16] * len(comp_names) + [18])
    r = 2
    for h in comp["head_to_head"]:
        ws.cell(row=r, column=1, value=h["keyword"]).border = BORDER
        ws.cell(row=r, column=2, value=h["volume"]).border = BORDER
        ws.cell(row=r, column=3, value=h["page"]).border = BORDER
        ws.cell(row=r, column=4, value=pos_label(h["client_pos"])).border = BORDER
        for j, c in enumerate(h["comps"], 5):
            ws.cell(row=r, column=j, value=pos_label(c["pos"])).border = BORDER
        ws.cell(row=r, column=4 + len(comp_names) + 1, value=h["best"]).border = BORDER
        fill = GAIN_FILL if h.get("client_wins") else LOSS_FILL
        for col in range(1, 5 + len(comp_names) + 1):
            ws.cell(row=r, column=col).fill = fill
        r += 1
    ws.auto_filter.ref = "A1:" + get_column_letter(5 + len(comp_names)) + str(r - 1)
    ws.freeze_panes = "A2"
    return ws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    with open(args.data, encoding="utf-8") as fh:
        R = json.load(fh)
    if not R.get("competition"):
        raise SystemExit("ERREUR: report_data.json sans bloc competition (lancer prepare_competitors.py)")
    wb = Workbook()
    sheet_sov(wb, R)
    sheet_comparatif(wb, R)
    sheet_weekly(wb, R)
    sheet_face(wb, R)
    wb.save(args.out)
    print("OK xlsx concurrence : " + args.out)


if __name__ == "__main__":
    main()
