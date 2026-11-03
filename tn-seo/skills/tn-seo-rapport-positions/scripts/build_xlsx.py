#!/usr/bin/env python3
"""build_xlsx.py - Classeur Excel "pure data" du reporting mensuel SE Ranking.

Entree : report_data.json (prepare_data.py, eventuellement enrichi par prepare_competitors.py)
Sortie : --out chemin .xlsx
Feuilles : Synthese, Evolution hebdo (3 graphes natifs), Mots cles, Par page,
Concurrence (si presente), Highlights.
"""
import argparse
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, Reference
from openpyxl.utils import get_column_letter

GREEN = "95C11F"
DARK = "2B3A4E"
GREYBG = "E8EAED"
GREEN_BG = "F0F9E8"
RED_BG = "FBE9E7"
WHITE = "FFFFFF"

H_FONT = Font(name="Calibri", bold=True, color=WHITE, size=11)
H_FILL = PatternFill("solid", fgColor=DARK)
SUB_FILL = PatternFill("solid", fgColor=GREYBG)
GAIN_FILL = PatternFill("solid", fgColor=GREEN_BG)
LOSS_FILL = PatternFill("solid", fgColor=RED_BG)
THIN = Side(style="thin", color="CCCCCC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center")
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=False)


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


def evol_str(cur, prev):
    if cur is None or prev is None:
        return "-"
    d = cur - prev
    if d == 0:
        return "="
    return ("+" + str(d)) if d > 0 else str(d)


def evol_str_avg(cur, prev):
    if cur is None or prev is None:
        return "-"
    d = round(cur - prev, 1)
    if d == 0:
        return "="
    return ("+" + str(d)) if d > 0 else str(d)


def pos_label(p):
    return ">100" if p is None else p


def evol_pos(delta):
    if delta is None:
        return "-"
    if delta == 0:
        return "="
    return ("+" + str(-delta)) if delta < 0 else ("-" + str(delta))


def sheet_synthese(wb, R):
    ws = wb.active
    ws.title = "Synthese"
    m = R["meta"]
    ws["A1"] = "Reporting SEO mensuel"
    ws["A1"].font = Font(name="Calibri", bold=True, size=16, color=DARK)
    ws["A2"] = str(m.get("client", "")) + " - " + str(m.get("domain", "")) + " - " + str(m.get("engine_label", ""))
    ws["A2"].font = Font(name="Calibri", size=11, color="666666")
    ws["A3"] = "Periode : " + str(m.get("period_current", "")) + " (vs " + str(m.get("period_prev", "")) + " et " + str(m.get("period_prev2", "")) + ")"
    ws["A3"].font = Font(name="Calibri", size=10, color="666666")
    s = R["summary"]
    rows = [
        ("Indicateur", m.get("period_prev2", "M-2"), m.get("period_prev", "M-1"), m.get("period_current", "M"), "Evol. M-1>M"),
        ("Mots-cles suivis (positionnes)", s["prev2"]["tracked"], s["prev"]["tracked"], s["current"]["tracked"], evol_str(s["current"]["tracked"], s["prev"]["tracked"])),
        ("TOP 3", s["prev2"]["top3"], s["prev"]["top3"], s["current"]["top3"], evol_str(s["current"]["top3"], s["prev"]["top3"])),
        ("TOP 10", s["prev2"]["top10"], s["prev"]["top10"], s["current"]["top10"], evol_str(s["current"]["top10"], s["prev"]["top10"])),
        ("TOP 30", s["prev2"]["top30"], s["prev"]["top30"], s["current"]["top30"], evol_str(s["current"]["top30"], s["prev"]["top30"])),
        ("Position moyenne", s["prev2"]["avg_pos"], s["prev"]["avg_pos"], s["current"]["avg_pos"], evol_str_avg(s["current"]["avg_pos"], s["prev"]["avg_pos"])),
    ]
    start = 5
    header_row(ws, start, rows[0], widths=[34, 14, 14, 14, 14])
    for r_i, row in enumerate(rows[1:], start + 1):
        for c_i, val in enumerate(row, 1):
            c = ws.cell(row=r_i, column=c_i, value=val)
            c.border = BORDER
            c.alignment = LEFT if c_i == 1 else CENTER
            if c_i == 1:
                c.fill = SUB_FILL
                c.font = Font(name="Calibri", bold=True, color=DARK)
    ws.freeze_panes = "A6"
    return ws


def sheet_weekly(wb, R):
    ws = wb.create_sheet("Evolution hebdo")
    vis = R["weekly_trend"]["visibility_percent"]
    avg = R["weekly_trend"]["avg_pos"]
    top = R["weekly_trend"]["top10"]
    labels = vis["labels"] or avg["labels"] or top["labels"]
    header_row(ws, 1, ["Semaine", "Visibilite (%)", "Position moyenne", "Mots-cles TOP 10"], widths=[14, 16, 18, 18])

    def val_at(series, i):
        return series["values"][i] if i < len(series["values"]) else None

    for i, lab in enumerate(labels):
        ws.cell(row=2 + i, column=1, value=lab).border = BORDER
        ws.cell(row=2 + i, column=2, value=val_at(vis, i)).border = BORDER
        ws.cell(row=2 + i, column=3, value=val_at(avg, i)).border = BORDER
        ws.cell(row=2 + i, column=4, value=val_at(top, i)).border = BORDER
    n = len(labels)
    if n == 0:
        ws.cell(row=2, column=1, value="(pas de donnees hebdomadaires disponibles)")
        return ws
    last = 1 + n
    cats = Reference(ws, min_col=1, min_row=2, max_row=last)

    def add_chart(col, title, anchor):
        ch = LineChart()
        ch.title = title
        ch.height = 7
        ch.width = 16
        ch.style = 2
        data = Reference(ws, min_col=col, min_row=1, max_row=last)
        ch.add_data(data, titles_from_data=True)
        ch.set_categories(cats)
        ch.legend = None
        ws.add_chart(ch, anchor)

    add_chart(2, "Visibilite (%)", "F2")
    add_chart(3, "Position moyenne", "F18")
    add_chart(4, "Mots-cles en TOP 10", "F34")
    ws.freeze_panes = "A2"
    return ws


def sheet_keywords(wb, R):
    ws = wb.create_sheet("Mots cles")
    m = R["meta"]
    headers = ["Mot-cle", "Volume", "Page de destination",
               "Pos " + str(m.get("period_prev2", "M-2")), "Pos " + str(m.get("period_prev", "M-1")),
               "Pos " + str(m.get("period_current", "M")), "Evolution", "Statut"]
    header_row(ws, 1, headers, widths=[34, 9, 60, 11, 11, 11, 11, 10])
    for i, k in enumerate(R["keywords"], 2):
        ws.cell(row=i, column=1, value=k["keyword"]).border = BORDER
        ws.cell(row=i, column=2, value=k["volume"]).border = BORDER
        ws.cell(row=i, column=3, value=k["page"]).border = BORDER
        ws.cell(row=i, column=4, value=pos_label(k["pos_prev2"])).border = BORDER
        ws.cell(row=i, column=5, value=pos_label(k["pos_prev"])).border = BORDER
        ws.cell(row=i, column=6, value=pos_label(k["pos_current"])).border = BORDER
        evc = ws.cell(row=i, column=7, value=evol_pos(k["delta"]))
        evc.border = BORDER
        evc.alignment = CENTER
        ws.cell(row=i, column=8, value=k["status"].upper()).border = BORDER
        if k["delta"] is not None and k["delta"] < 0:
            for c in range(1, 9):
                ws.cell(row=i, column=c).fill = GAIN_FILL
        elif k["delta"] is not None and k["delta"] > 0:
            for c in range(1, 9):
                ws.cell(row=i, column=c).fill = LOSS_FILL
    ws.auto_filter.ref = "A1:H" + str(len(R["keywords"]) + 1)
    ws.freeze_panes = "A2"
    return ws


def sheet_pages(wb, R):
    ws = wb.create_sheet("Par page")
    header_row(ws, 1, ["Page", "Nb mots-cles", "Volume cumule", "Position moyenne", "Mots-cles TOP 10", "Mots-cles (liste)"],
               widths=[60, 13, 14, 16, 16, 80])
    for i, p in enumerate(R["pages"], 2):
        ws.cell(row=i, column=1, value=p["page"]).border = BORDER
        ws.cell(row=i, column=2, value=p["n_keywords"]).border = BORDER
        ws.cell(row=i, column=3, value=p["sum_volume"]).border = BORDER
        ws.cell(row=i, column=4, value=p["avg_pos"]).border = BORDER
        ws.cell(row=i, column=5, value=p["top10"]).border = BORDER
        ws.cell(row=i, column=6, value=", ".join(p["keywords"])).border = BORDER
    ws.auto_filter.ref = "A1:F" + str(len(R["pages"]) + 1)
    ws.freeze_panes = "A2"
    return ws


def sheet_competition(wb, R):
    comp = R.get("competition")
    if not comp:
        return None
    ws = wb.create_sheet("Concurrence")
    m = R["meta"]
    row = 1
    if comp.get("share_of_voice"):
        c = ws.cell(row=row, column=1, value="Part de voix - " + str(m.get("period_current", "")) + " (visibilite projet, instantane)")
        c.font = Font(name="Calibri", bold=True, color=WHITE)
        c.fill = H_FILL
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        row += 1
        header_row(ws, row, ["Domaine", "Part de visibilite (%)"], widths=[42, 22])
        row += 1
        for sov in comp["share_of_voice"]:
            cc = ws.cell(row=row, column=1, value=sov["domain"])
            cc.border = BORDER
            ws.cell(row=row, column=2, value=sov["visibility"]).border = BORDER
            if sov.get("is_client"):
                for col in (1, 2):
                    ws.cell(row=row, column=col).fill = GAIN_FILL
                    ws.cell(row=row, column=col).font = Font(name="Calibri", bold=True, color=DARK)
            row += 1
        row += 2
    title = ws.cell(row=row, column=1, value="Comparatif mots-cles en TOP 10 et position moyenne")
    title.font = Font(name="Calibri", bold=True, color=WHITE)
    title.fill = H_FILL
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
    row += 1
    header_row(ws, row, ["Acteur",
                         "TOP10 " + str(m.get("period_prev2", "M-2")), "TOP10 " + str(m.get("period_prev", "M-1")), "TOP10 " + str(m.get("period_current", "M")),
                         "Pos.moy " + str(m.get("period_prev2", "M-2")), "Pos.moy " + str(m.get("period_prev", "M-1")), "Pos.moy " + str(m.get("period_current", "M"))],
               widths=[30, 12, 12, 12, 13, 13, 13])
    row += 1
    actors = [comp["client"]] + comp["competitors"]
    for a in actors:
        mm = a["monthly"]
        cells = [a["name"], mm["prev2"]["top10"], mm["prev"]["top10"], mm["current"]["top10"],
                 mm["prev2"]["avg"], mm["prev"]["avg"], mm["current"]["avg"]]
        for j, v in enumerate(cells, 1):
            cc = ws.cell(row=row, column=j, value="-" if v is None else v)
            cc.border = BORDER
            cc.alignment = LEFT if j == 1 else CENTER
            if a.get("is_client"):
                cc.fill = GAIN_FILL
                if j == 1:
                    cc.font = Font(name="Calibri", bold=True, color=DARK)
        row += 1
    row += 2
    th = ws.cell(row=row, column=1, value="Evolution hebdomadaire - mots-cles en TOP 10")
    th.font = Font(name="Calibri", bold=True, color=WHITE)
    th.fill = H_FILL
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=1 + len(actors))
    row += 1
    labels = comp["client"]["weekly_top10"]["labels"]
    headers = ["Semaine"] + [a["name"] for a in actors]
    header_row(ws, row, headers, widths=[14] + [16] * len(actors))
    data_start = row + 1
    maps = []
    for a in actors:
        wt = a["weekly_top10"]
        maps.append({lab: val for lab, val in zip(wt["labels"], wt["values"])})
    for i, lab in enumerate(labels):
        r = data_start + i
        ws.cell(row=r, column=1, value=lab).border = BORDER
        for j, mp in enumerate(maps, 2):
            ws.cell(row=r, column=j, value=mp.get(lab)).border = BORDER
    data_end = data_start + len(labels) - 1
    if labels:
        ch = LineChart()
        ch.title = "Mots-cles en TOP 10 - client vs concurrents"
        ch.height = 8
        ch.width = 20
        ch.style = 2
        cats = Reference(ws, min_col=1, min_row=data_start, max_row=data_end)
        data = Reference(ws, min_col=2, max_col=1 + len(actors), min_row=data_start - 1, max_row=data_end)
        ch.add_data(data, titles_from_data=True)
        ch.set_categories(cats)
        anchor_col = get_column_letter(3 + len(actors))
        ws.add_chart(ch, anchor_col + str(max(2, data_start - 6)))
    return ws


def sheet_highlights(wb, R):
    ws = wb.create_sheet("Highlights")
    H = R["highlights"]
    blocks = [
        ("Plus fortes progressions (M-1 > M)", H["gains"]),
        ("Fort volume en TOP 10", H["high_volume"]),
        ("Entrees TOP 3 / TOP 10", H["top_entries"]),
        ("Sorties / vigilance (perte de TOP)", H["top_exits"]),
    ]
    row = 1
    for title, items in blocks:
        c = ws.cell(row=row, column=1, value=title)
        c.font = Font(name="Calibri", bold=True, color=WHITE)
        c.fill = PatternFill("solid", fgColor=GREEN if ("progress" in title.lower() or "Entrees" in title) else DARK)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
        row += 1
        header_row(ws, row, ["Mot-cle", "Volume", "Page", "Pos M-1 > M", "Evolution"], widths=[34, 9, 60, 14, 12])
        row += 1
        if not items:
            ws.cell(row=row, column=1, value="(aucun)")
            row += 2
            continue
        for k in items:
            ws.cell(row=row, column=1, value=k["keyword"]).border = BORDER
            ws.cell(row=row, column=2, value=k["volume"]).border = BORDER
            ws.cell(row=row, column=3, value=k["page"]).border = BORDER
            ws.cell(row=row, column=4, value=str(pos_label(k["pos_prev"])) + " > " + str(pos_label(k["pos_current"]))).border = BORDER
            ws.cell(row=row, column=5, value=evol_pos(k["delta"])).border = BORDER
            row += 1
        row += 1
    return ws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    with open(args.data, encoding="utf-8") as fh:
        R = json.load(fh)
    wb = Workbook()
    sheet_synthese(wb, R)
    sheet_weekly(wb, R)
    sheet_keywords(wb, R)
    sheet_pages(wb, R)
    sheet_competition(wb, R)
    sheet_highlights(wb, R)
    wb.save(args.out)
    print("OK xlsx : " + args.out)


if __name__ == "__main__":
    main()
