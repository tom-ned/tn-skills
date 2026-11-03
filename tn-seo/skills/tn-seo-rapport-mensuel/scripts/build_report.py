#!/usr/bin/env python3
"""build_report.py - Word de synthese du reporting SEO mensuel (charte Suisseo).

Registre : livrable client. Une idee par section, les donnees brutes restent dans l'Excel.
Trois echelles de mesure assumees et expliquees : site, perimetre de langue, marche suisse.
Entree : report_data.json (prepare_data.py). Sortie : --out .docx
"""
import argparse, json, os, tempfile
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------------------------------------------------------------- charte
DARK = RGBColor(0x2B, 0x3A, 0x4E); GREEN = RGBColor(0x95, 0xC1, 0x1F)
TEXT = RGBColor(0x33, 0x33, 0x33); GREY = RGBColor(0x6B, 0x72, 0x80)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
POS = RGBColor(0x5F, 0x81, 0x14); NEG = RGBColor(0xB0, 0x3A, 0x2B)
DARK_HEX = "2B3A4E"; GREYBG_HEX = "F4F6F8"; LINE_HEX = "E3E6EA"; TILE_HEX = "F7F9FA"

# ---------------------------------------------------------------- graphiques
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

# Palette de series validee via validate_palette.js (bande de clarte, plancher de
# chroma, separation CVD, plancher vision normale). Les couleurs de marque Suisseo
# restent sur les titres et le texte du document.
C1 = "#2F6FB2"; C2 = "#7FA817"; C3 = "#A4568C"
INK = "#333333"; MUTED = "#8A9099"; GRID = "#EDEFF2"; SURFACE = "white"
CHART_DIR = None
FULL_IN = 7.0; FULL_CM = 15.6
HALF_IN = 3.30; HALF_CM = 7.30
matplotlib.rcParams.update({
    "font.family": "Carlito", "font.size": 8.5,
    "axes.edgecolor": GRID, "axes.linewidth": 0.8,
    "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
})
NBSP = " "


def fr(v, pct=False, dec=None, signed=False):
    """Nombre au format francais : espace fine, virgule decimale."""
    if v is None:
        return "-"
    if isinstance(v, str):
        return v
    try:
        f = float(v)
    except Exception:
        return str(v)
    sign = "+" if (signed and f > 0) else ""
    if pct:
        d = 2 if (0 < abs(f) < 0.1) else 1
        return sign + f"{f:.{d}f}".replace(".", ",") + NBSP + "%"
    if dec is not None:
        return sign + f"{f:.{dec}f}".replace(".", ",")
    if abs(f - round(f)) < 1e-9:
        return sign + f"{int(round(f)):,}".replace(",", NBSP)
    return sign + f"{f:.1f}".replace(".", ",")


def _rel(url, domain):
    """URL raccourcie : on retire le protocole et le domaine."""
    u = str(url or "")
    for p in ("https://", "http://"):
        if u.startswith(p):
            u = u[len(p):]
    d = str(domain or "").replace("https://", "").replace("http://", "").strip("/")
    for cand in (d, "www." + d):
        if d and u.startswith(cand):
            return u[len(cand):] or "/"
    return "/" + u.split("/", 1)[1] if "/" in u else u


def pct_var(cur, prev):
    if cur is None or prev in (None, 0):
        return None
    return round((cur - prev) / abs(prev) * 100, 1)


def _base(ax, horizontal=False):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0, labelsize=8.5, pad=4)
    if horizontal:
        ax.xaxis.grid(True, color=GRID, linewidth=0.7); ax.yaxis.grid(False)
        ax.spines["bottom"].set_visible(False)
    else:
        ax.yaxis.grid(True, color=GRID, linewidth=0.7); ax.xaxis.grid(False)
        ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.set_axisbelow(True)


def _save(fig, name):
    path = os.path.join(CHART_DIR, name)
    fig.savefig(path, dpi=240, bbox_inches="tight", pad_inches=0.06, facecolor=SURFACE)
    plt.close(fig)
    return path


def chart_line(labels, values, name, color=C1, invert=False, dec=0, half=False):
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return None
    w, h = (HALF_IN, 2.05) if half else (FULL_IN, 2.35)
    fig, ax = plt.subplots(figsize=(w, h))
    ax.plot(range(len(values)), values, color=color, linewidth=1.4, solid_capstyle="round", zorder=3)
    ax.plot([len(values) - 1], [values[-1]], marker="o", markersize=4.2, color=color,
            markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=4)
    _base(ax)
    long_lbl = max(len(str(l)) for l in labels) > 9
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=40 if long_lbl else 0, ha="right" if long_lbl else "center")
    if invert:
        ax.invert_yaxis()
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: fr(v, dec=dec if dec else None)))
    ax.margins(y=0.28, x=0.12 if half else 0.04)
    ax.annotate(fr(values[-1], dec=dec if dec else None), (len(values) - 1, values[-1]),
                textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8, color=INK)
    return _save(fig, name)


def chart_multi(labels, series, name):
    """Plusieurs series sur une meme unite (indice base 100). Legende + labels de fin."""
    fig, ax = plt.subplots(figsize=(FULL_IN, 2.6))
    colors = [C1, C2, C3]
    for i, (lbl, vals) in enumerate(series):
        c = colors[i % 3]
        ax.plot(range(len(vals)), vals, color=c, linewidth=1.5, label=lbl, solid_capstyle="round", zorder=3)
        ax.plot([len(vals) - 1], [vals[-1]], marker="o", markersize=4.2, color=c,
                markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=4)
        ax.annotate(fr(vals[-1]), (len(vals) - 1, vals[-1]), textcoords="offset points",
                    xytext=(8, -3), ha="left", fontsize=8, color=c)
    ax.axhline(100, color=GRID, linewidth=1.0, zorder=1)
    _base(ax)
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels)
    ax.margins(y=0.24, x=0.10)
    leg = ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.10),
                    ncol=3, handlelength=1.2, columnspacing=1.6, handletextpad=0.5)
    for t in leg.get_texts():
        t.set_color(INK)
    return _save(fig, name)


def chart_bars(labels, values, name, color=C1, pct=False, half=False):
    if not values or any(v is None for v in values):
        return None
    w, h = (HALF_IN, 2.05) if half else (FULL_IN, 2.35)
    fig, ax = plt.subplots(figsize=(w, h))
    b = ax.bar(labels, values, color=color, width=0.42)
    _base(ax); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: fr(v)))
    ax.margins(y=0.24)
    for rect, v in zip(b, values):
        ax.annotate(fr(v, pct=pct), (rect.get_x() + rect.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8, color=INK)
    return _save(fig, name)


def chart_stack(labels, s1, s2, l1, l2, name, half=False):
    if any(v is None for v in list(s1) + list(s2)):
        return None
    w, h = (HALF_IN, 2.35) if half else (FULL_IN, 2.55)
    fig, ax = plt.subplots(figsize=(w, h))
    ax.bar(labels, s1, color=C1, width=0.42, label=l1, edgecolor=SURFACE, linewidth=1.4)
    ax.bar(labels, s2, bottom=s1, color=C2, width=0.42, label=l2, edgecolor=SURFACE, linewidth=1.4)
    tot = max(a + b for a, b in zip(s1, s2))
    for i, (a, b_) in enumerate(zip(s1, s2)):
        if a / tot > 0.12:
            ax.annotate(fr(a), (i, a / 2), ha="center", va="center", fontsize=8, color=SURFACE)
        if b_ / tot > 0.12:
            ax.annotate(fr(b_), (i, a + b_ / 2), ha="center", va="center", fontsize=8, color=SURFACE)
        else:
            ax.annotate(fr(b_), (i, a + b_), textcoords="offset points", xytext=(0, 4),
                        ha="center", fontsize=8, color=INK)
    _base(ax); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: fr(v)))
    ax.margins(y=0.18)
    leg = ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12),
                    ncol=2, handlelength=0.9, handleheight=0.9, columnspacing=1.4, handletextpad=0.5)
    for t in leg.get_texts():
        t.set_color(INK)
    return _save(fig, name)


def chart_barh(labels, values, name, color=C1):
    if not values:
        return None
    fig, ax = plt.subplots(figsize=(FULL_IN, 0.26 * len(labels) + 0.5))
    b = ax.barh(labels[::-1], values[::-1], color=color, height=0.55)
    _base(ax, horizontal=True)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: fr(v)))
    ax.margins(x=0.12)
    for rect, v in zip(b, values[::-1]):
        ax.annotate(fr(v), (v, rect.get_y() + rect.get_height() / 2), textcoords="offset points",
                    xytext=(5, 0), va="center", fontsize=8, color=INK)
    return _save(fig, name)


GREY_SERIE = "#B9BEC6"


def _roll(vals, w=28):
    out = []
    for i in range(len(vals)):
        a = max(0, i - w + 1)
        out.append(sum(vals[a:i + 1]) / (i - a + 1))
    return out


def chart_daily(rows, name, key="clicks", color=C1, roll=7):
    """Série quotidienne longue : trait fin brut + moyenne mobile épaisse."""
    if len(rows) < 30:
        return None
    vals = [r[key] for r in rows]
    dates = [r["key"] for r in rows]
    fig, ax = plt.subplots(figsize=(FULL_IN, 2.6))
    ax.plot(range(len(vals)), vals, color=color, linewidth=0.55, alpha=0.35, zorder=2)
    rm = _roll(vals, roll)
    ax.plot(range(len(vals)), rm, color=color, linewidth=2.0, solid_capstyle="round", zorder=3,
            label=f"moyenne sur {roll} jours")
    _base(ax)
    ticks, labels = [], []
    MOIS = {"01": "Janv.", "02": "Févr.", "03": "Mars", "04": "Avril", "05": "Mai", "06": "Juin",
            "07": "Juil.", "08": "Août", "09": "Sept.", "10": "Oct.", "11": "Nov.", "12": "Déc."}
    step = 1 if len(dates) <= 40 else (7 if len(dates) <= 120 else 30)
    for i, d in enumerate(dates):
        marque_mois = d[8:10] == "01"
        if marque_mois or (i % step == 0):
            ticks.append(i)
            labels.append(MOIS[d[5:7]] + "\n" + d[8:10] if marque_mois else d[8:10])
    ax.set_xticks(ticks); ax.set_xticklabels(labels, fontsize=7.5)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: fr(v)))
    ax.margins(x=0.01, y=0.12)
    ax.set_ylim(bottom=0)
    ax.annotate(fr(round(rm[-1])), (len(vals) - 1, rm[-1]), textcoords="offset points",
                xytext=(6, 4), ha="left", fontsize=8, color=color)
    leg = ax.legend(frameon=False, fontsize=8, loc="upper left", handlelength=1.4)
    for t in leg.get_texts():
        t.set_color(INK)
    return _save(fig, name)


def chart_months(serie, name, key="clicks", color=C1, hl_color=C3):
    """Barres mensuelles sur une longue période. Le mois partiel est distingué."""
    if len(serie) < 6:
        return None
    fig, ax = plt.subplots(figsize=(FULL_IN, 2.6))
    vals = [s[key] for s in serie]
    cols = [(hl_color if s.get("partial") else color) for s in serie]
    ax.bar(range(len(vals)), vals, color=cols, width=0.62)
    _base(ax)
    MOIS = {"01": "Janv.", "02": "Févr.", "03": "Mars", "04": "Avril", "05": "Mai", "06": "Juin",
            "07": "Juil.", "08": "Août", "09": "Sept.", "10": "Oct.", "11": "Nov.", "12": "Déc."}
    ax.set_xticks(range(len(serie)))
    ax.set_xticklabels([MOIS[s["month"][5:7]] for s in serie], fontsize=8)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: fr(v)))
    ax.margins(y=0.16)
    imax = vals.index(max(vals))
    for i in (0, imax, len(vals) - 1):
        ax.annotate(fr(vals[i]), (i, vals[i]), textcoords="offset points", xytext=(0, 4),
                    ha="center", fontsize=7.5, color=INK)
    return _save(fig, name)


def chart_lang_months(lm, name):
    """Barres empilées par langue."""
    if len(lm) < 2:
        return None
    fig, ax = plt.subplots(figsize=(FULL_IN, 2.9))
    keys = [("en", "Anglais", C1), ("fr", "Français", C2), ("de", "Allemand", C3),
            ("global", "Sans préfixe", GREY_SERIE)]
    bottom = [0] * len(lm)
    for k, lbl, col in keys:
        vals = [m.get(k, 0) or 0 for m in lm]
        ax.bar(range(len(lm)), vals, bottom=bottom, color=col, width=0.62, label=lbl,
               edgecolor=SURFACE, linewidth=0.6)
        bottom = [b + v for b, v in zip(bottom, vals)]
    _base(ax)
    MOIS = {"01": "Janv.", "02": "Févr.", "03": "Mars", "04": "Avril", "05": "Mai", "06": "Juin",
            "07": "Juil.", "08": "Août", "09": "Sept.", "10": "Oct.", "11": "Nov.", "12": "Déc."}
    ax.set_xticks(range(len(lm)))
    ax.set_xticklabels([MOIS[m["month"][5:7]] for m in lm], fontsize=8)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: fr(v)))
    ax.margins(y=0.12)
    leg = ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.14),
                    ncol=4, handlelength=0.9, handleheight=0.9, columnspacing=1.4, handletextpad=0.5)
    for t in leg.get_texts():
        t.set_color(INK)
    return _save(fig, name)


# ---------------------------------------------------------------- briques Word
def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    el = OxmlElement("w:shd"); el.set(qn("w:val"), "clear"); el.set(qn("w:fill"), hex_color)
    tcPr.append(el)


def no_margins(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for side in ("top", "start", "bottom", "end"):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:w"), "0"); e.set(qn("w:type"), "dxa"); mar.append(e)
    tcPr.append(mar)


def no_borders(table):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}"); e.set(qn("w:val"), "none"); e.set(qn("w:sz"), "0")
        borders.append(e)
    tblPr.append(borders)


def run(par, txt, size=10, bold=False, color=TEXT, italic=False):
    r = par.add_run(str(txt)); r.font.size = Pt(size); r.font.bold = bold
    r.font.italic = italic; r.font.color.rgb = color; r.font.name = "Calibri"
    return r


def body(doc, txt, size=10, color=TEXT, space_after=6, bold=False):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    run(p, txt, size=size, color=color, bold=bold)
    return p


def heading(doc, txt, num=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16); p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    if num:
        run(p, f"{num}  ", size=13, bold=True, color=GREEN)
    run(p, txt, size=13, bold=True, color=DARK)
    pPr = p._p.get_or_add_pPr()
    bd = OxmlElement("w:pBdr"); bo = OxmlElement("w:bottom")
    bo.set(qn("w:val"), "single"); bo.set(qn("w:sz"), "6"); bo.set(qn("w:space"), "4")
    bo.set(qn("w:color"), "95C11F"); bd.append(bo); pPr.append(bd)
    return p


def caption(doc, txt):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run(p, txt, size=9, bold=True, color=DARK)


def note(doc, txt):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
    run(p, txt, size=8, color=GREY)


def put(doc, path, cap=None, width_cm=FULL_CM):
    if not path:
        return
    if cap:
        caption(doc, cap)
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
    try:
        p.add_run().add_picture(path, width=Cm(width_cm))
    except Exception:
        pass


def put_pair(doc, p1, c1, p2, c2):
    if not p1 or not p2:
        put(doc, p1 or p2, c1 if p1 else c2)
        return
    t = doc.add_table(rows=2, cols=2); t.autofit = False; no_borders(t)
    for j, (pp, cc) in enumerate(((p1, c1), (p2, c2))):
        top = t.rows[0].cells[j]; bot = t.rows[1].cells[j]
        for c in (top, bot):
            c.width = Cm(HALF_CM + 0.5); no_margins(c)
        par = top.paragraphs[0]
        par.paragraph_format.space_before = Pt(10); par.paragraph_format.space_after = Pt(2)
        par.paragraph_format.keep_with_next = True
        run(par, cc, size=9, bold=True, color=DARK)
        try:
            bot.paragraphs[0].add_run().add_picture(pp, width=Cm(HALF_CM))
        except Exception:
            pass


def tiles(doc, items):
    """Rangee de tuiles KPI : grand chiffre, libelle, variation."""
    t = doc.add_table(rows=1, cols=len(items)); t.autofit = False; no_borders(t)
    for i, (label, value, delta, good) in enumerate(items):
        c = t.rows[0].cells[i]; c.width = Cm(15.6 / len(items)); shade(c, TILE_HEX)
        p0 = c.paragraphs[0]; p0.paragraph_format.space_before = Pt(6); p0.paragraph_format.space_after = Pt(0)
        run(p0, value, size=18, bold=True, color=DARK)
        p1 = c.add_paragraph(); p1.paragraph_format.space_after = Pt(0)
        run(p1, label, size=8, color=GREY)
        p2 = c.add_paragraph(); p2.paragraph_format.space_after = Pt(6)
        if delta:
            run(p2, delta, size=9, bold=True, color=(POS if good else NEG) if good is not None else GREY)
        else:
            run(p2, " ", size=9)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def _fixed_layout(t, widths=None):
    tblPr = t._tbl.tblPr
    el = OxmlElement("w:tblLayout"); el.set(qn("w:type"), "fixed"); tblPr.append(el)
    if widths:
        grid = t._tbl.find(qn("w:tblGrid"))
        if grid is not None:
            t._tbl.remove(grid)
        grid = OxmlElement("w:tblGrid")
        for w in widths:
            gc = OxmlElement("w:gridCol"); gc.set(qn("w:w"), str(int(w * 567))); grid.append(gc)
        tblPr.addnext(grid)


def _repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader"); el.set(qn("w:val"), "true"); trPr.append(el)


def _cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit"); el.set(qn("w:val"), "true"); trPr.append(el)


def table(doc, headers, rows, widths=None, aligns=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT; t.autofit = False; _fixed_layout(t, widths)
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; shade(c, DARK_HEX)
        p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (aligns and aligns[i] == "c") else WD_ALIGN_PARAGRAPH.LEFT
        run(p, h, size=9, bold=True, color=WHITE)
    for k, r in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(r):
            if k % 2 == 1:
                shade(cells[i], GREYBG_HEX)
            p = cells[i].paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (aligns and aligns[i] == "c") else WD_ALIGN_PARAGRAPH.LEFT
            col = TEXT
            s = str(v)
            if s.startswith("+") and "place" not in s:
                col = POS
            elif s.startswith("-") and "place" not in s and s != "-":
                col = NEG
            run(p, v, size=9, color=col, bold=(i == 0 and len(headers) > 2 and aligns and aligns[0] == "l"))
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Cm(w)
    _repeat_header(t.rows[0])
    for row in t.rows:
        _cant_split(row)
    return t


def header_footer(doc, m):
    sec = doc.sections[0]
    sec.left_margin = Cm(2.2); sec.right_margin = Cm(2.2)
    sec.top_margin = Cm(1.8); sec.bottom_margin = Cm(1.8)
    h = sec.header.paragraphs[0]; h.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run(h, f"{m.get('client','')} - Reporting SEO {m.get('month_name','')} - {m.get('language','')}",
        size=8, color=GREY)
    f = sec.footer.paragraphs[0]; f.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(f, m.get("footer", "Suisseo - Thomas Nedjar - thomas.nedjar@suisseo.ch"), size=8, color=GREY)


def cover(doc, m, logo):
    if logo and os.path.exists(logo):
        p = doc.add_paragraph()
        try:
            p.add_run().add_picture(logo, width=Cm(4.2))
        except Exception:
            pass
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(2)
    run(p, "Reporting SEO mensuel", size=26, bold=True, color=DARK)
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(18)
    run(p, m.get("client", ""), size=20, bold=True, color=GREEN)
    t = doc.add_table(rows=0, cols=2); no_borders(t)
    for lbl, val in [("Domaine", m.get("domain", "")),
                     ("Périmètre", f"{m.get('language','')}"),
                     ("Marché", m.get("market", "")),
                     ("Période", f"{m.get('month_name','')}  (comparaison {m.get('month_m1','')} et {m.get('month_m2','')})"),
                     ("Sources", "Google Search Console et Google Analytics 4, via Cartograph"),
                     ("Consultant", m.get("consultant", "Thomas Nedjar"))]:
        if not val:
            continue
        cells = t.add_row().cells
        cells[0].width = Cm(3.4); cells[1].width = Cm(12.2)
        for c in cells:
            no_margins(c)
        p0 = cells[0].paragraphs[0]; p0.paragraph_format.space_after = Pt(4)
        run(p0, lbl, size=10, bold=True, color=DARK)
        p1 = cells[1].paragraphs[0]; p1.paragraph_format.space_after = Pt(4)
        run(p1, val, size=10, color=TEXT)
    doc.add_page_break()


# ---------------------------------------------------------------- sections
def sec_grille(doc, R):
    m = R["meta"]
    heading(doc, "Grille de lecture", "0")
    body(doc, "Ce rapport lit la performance à trois échelles. Elles ne se superposent pas et "
              "leurs positions moyennes ne sont pas comparables entre elles : chacune est calculée "
              "sur un découpage différent de la Search Console. Chaque section indique l'échelle "
              "qu'elle utilise.")
    table(doc,
          ["Échelle", "Ce qu'elle mesure", "Découpage Search Console"],
          [["Site " + m.get("domain", ""), "Toutes langues, tous pays", "Dimension requête"],
           ["Versions linguistiques", "Pages /fr/, /en/ et /de/ prises séparément", "Dimension page et langue"],
           ["Marché suisse", "Recherches faites depuis la Suisse, toutes langues", "Dimension pays"]],
          widths=[4.4, 6.0, 5.2], aligns=["l", "l", "l"])
    note(doc, "Une requête n'est rattachée ni à une langue ni à un pays par la Search Console : "
              "les analyses par requête (marque, opportunités) restent donc au niveau du site.")


def sec_apercu(doc, R):
    m = R["meta"]; sk = m.get("site_kpi") or {}
    S = sk.get("M") or {}; SY = sk.get("Y") or {}
    K = R["kpi"]; M, M1 = K.get("M") or {}, K.get("M1") or {}
    hist = m.get("historique") or {}
    serie = hist.get("months") or []
    daily = hist.get("daily") or []
    heading(doc, "Le mois en un coup d'œil", "1")

    dcy = pct_var(S.get("clicks"), SY.get("clicks"))
    diy = pct_var(S.get("impressions"), SY.get("impressions"))
    dctr = None
    if S.get("ctr") is not None and SY.get("ctr") is not None:
        dctr = round(S["ctr"] - SY["ctr"], 2)
    an = m.get("month_year_ago", "l'an dernier")
    tiles(doc, [
        ("Clics organiques", fr(S.get("clicks")),
         (fr(dcy, pct=True, signed=True) + " vs " + an) if dcy is not None else "", (dcy or 0) >= 0),
        ("Impressions", fr(S.get("impressions")),
         (fr(diy, pct=True, signed=True) + " vs " + an) if diy is not None else "", (diy or 0) >= 0),
        ("Taux de clic", fr(S.get("ctr"), pct=True),
         (fr(dctr, dec=2, signed=True) + " pt vs " + an) if dctr is not None else "", (dctr or 0) >= 0),
        ("Part de marque", fr(M.get("brand_share"), pct=True), "des clics", None),
    ])
    note(doc, "Échelle : site entier, toutes langues et tous pays. Comparaison au même mois de l'année précédente, "
              "seule comparaison valable sur un site saisonnier.")

    if m.get("lecture"):
        for par in m["lecture"]:
            body(doc, par)

    if len(daily) >= 60:
        put(doc, chart_daily(daily, "daily.png"),
            "Clics organiques par jour, " + (m.get("historique_debut") or "") + " à " + (m.get("month_name") or ""))
        note(doc, "Le trait clair est la donnée quotidienne, le trait épais la moyenne sur 7 jours. "
                  "C'est la moyenne mobile qui porte la tendance ; le quotidien sert à voir l'amplitude réelle.")
    if len(serie) >= 3:
        put(doc, chart_daily(daily, "ctr_daily.png", key="ctr", color=C2),
            "Taux de clic par jour, en pourcentage")
        note(doc, "C'est la courbe structurante : le site est de plus en plus affiché et de moins en moins cliqué.")


def sec_langues(doc, R):
    m = R["meta"]; langs = m.get("langues") or []
    hist = m.get("historique") or {}
    lm = hist.get("lang_months") or []
    if not langs:
        return
    heading(doc, "Les trois versions linguistiques", "2")
    if len(lm) >= 3:
        put(doc, chart_lang_months(lm, "langues.png"), "Clics par version linguistique, mois par mois")
        if m.get("incident"):
            note(doc, m["incident"])
    rows = []
    for l in langs:
        k = l["kpi"]; M_, M1_ = k.get("M") or {}, k.get("M1") or {}
        v = pct_var(M_.get("clicks"), M1_.get("clicks"))
        vs = "stable" if (v is not None and abs(v) < 0.05) else (fr(v, pct=True, signed=True) if v is not None else "-")
        rows.append([f'{l["label"]} ({l["prefix"]})', fr(M_.get("clicks")), fr(M_.get("impressions")),
                     fr(M_.get("ctr"), pct=True), fr(M_.get("position"), dec=1),
                     fr(M_.get("share"), pct=True), vs])
    table(doc, ["Version", "Clics", "Impressions", "CTR", "Position", "Part du site", "vs M-1"], rows,
          widths=[3.4, 1.8, 2.4, 1.7, 1.9, 2.2, 2.2],
          aligns=["l", "c", "c", "c", "c", "c", "c"])
    for l in langs:
        k = l["kpi"]; M_ = k.get("M") or {}; M1_ = k.get("M1") or {}
        v = pct_var(M_.get("clicks"), M1_.get("clicks"))
        caption(doc, f'{l["label"]} ({l["prefix"]})')
        if v is None:
            sens = "sans comparaison disponible"
        elif abs(v) < 0.05:
            sens = "stable"
        elif v > 0:
            sens = "en hausse de " + fr(v, pct=True)
        else:
            sens = "en baisse de " + fr(abs(v), pct=True)
        body(doc, f'{fr(M_.get("clicks"))} clics sur {fr(l.get("n_pages"))} pages, {sens} vs {m.get("month_m1","")}. '
                  f'Position moyenne {fr(M_.get("position"), dec=1)}, taux de clic {fr(M_.get("ctr"), pct=True)}.',
             size=9.5)
        tp = l.get("top_pages") or []
        if tp:
            table(doc, ["Page", "Clics", "Impressions", "Position"],
                  [[_rel(p["url"], m.get("domain", "")), fr(p["clicks"]), fr(p["impressions"]),
                    fr(p["position"], dec=1)] for p in tp],
                  widths=[8.6, 2.1, 2.5, 2.4], aligns=["l", "c", "c", "c"])
    note(doc, "Le détail complet page par page est dans l'Excel, onglet Par page.")


def sec_echelles(doc, R):
    m = R["meta"]; ck = m.get("ch_kpi") or {}
    if not ck:
        return
    C, C1_, C2m = ck.get("M") or {}, ck.get("M1") or {}, ck.get("M2") or {}
    heading(doc, "Le marché suisse", "3")
    body(doc, f"Recherches faites depuis la Suisse, toutes langues confondues : {fr(C.get('clicks'))} clics et "
              f"{fr(C.get('impressions'))} impressions, taux de clic {fr(C.get('ctr'), pct=True)}. La Suisse "
              f"représente {fr(C.get('share'), pct=True)} des clics du site et c'est de loin le marché où le site "
              f"est le mieux placé, avec une position moyenne de {fr(C.get('position'), dec=1)} contre "
              f"{fr((m.get('site_kpi') or {}).get('M', {}).get('position'), dec=1)} pour le site entier.")
    table(doc, ["Indicateur", m.get("month_m2", "M-2"), m.get("month_m1", "M-1"), m.get("month_name", "M")],
          [["Clics depuis la Suisse", fr(C2m.get("clicks")), fr(C1_.get("clicks")), fr(C.get("clicks"))],
           ["Impressions", fr(C2m.get("impressions")), fr(C1_.get("impressions")), fr(C.get("impressions"))],
           ["Taux de clic", fr(C2m.get("ctr"), pct=True), fr(C1_.get("ctr"), pct=True), fr(C.get("ctr"), pct=True)],
           ["Part des clics du site", fr(C2m.get("share"), pct=True), fr(C1_.get("share"), pct=True),
            fr(C.get("share"), pct=True)]],
          widths=[6.0, 3.2, 3.2, 3.2], aligns=["l", "c", "c", "c"])
    note(doc, "Source : Search Console, dimension pays. Trois mois ne font pas une tendance : ce tableau situe le "
              "marché suisse, il ne mesure pas son évolution.")


def sec_marque(doc, R):
    K = R["kpi"]; M, M1, M2 = K.get("M"), K.get("M1"), K.get("M2")
    if not M:
        return
    m = R["meta"]
    heading(doc, "Marque et non-marque", "4")
    body(doc, f"Sur {fr(M['clicks'])} clics mesurés au niveau du site, {fr(M['brand_clicks'])} viennent de "
              f"recherches contenant le nom de la marque ({fr(M['brand_share'], pct=True)}) et "
              f"{fr(M['nonbrand_clicks'])} de recherches non-marque. C'est le non-marque qui mesure la "
              f"capacité du site à capter une audience qui ne connaît pas encore {m.get('client') or 'la marque'}.")
    labs = [short_month(m.get("month_m2", "")), short_month(m.get("month_m1", "")), short_month(m.get("month_name", ""))]
    br = [(M2 or {}).get("brand_clicks"), (M1 or {}).get("brand_clicks"), M.get("brand_clicks")]
    nb = [(M2 or {}).get("nonbrand_clicks"), (M1 or {}).get("nonbrand_clicks"), M.get("nonbrand_clicks")]
    put_pair(doc,
             chart_stack(labs, br, nb, "Marque", "Non-marque", "marque.png", half=True),
             "Clics de marque et non-marque",
             chart_bars(labs, [(M2 or {}).get("brand_share"), (M1 or {}).get("brand_share"), M.get("brand_share")],
                        "part.png", color=C2, pct=True, half=True),
             "Part de marque dans les clics")
    note(doc, "Échelle : site entier, dimension requête. Une requête est comptée comme marque si elle "
              "contient l'un des termes de marque définis pour ce rapport.")


def sec_potentiel(doc, R):
    m = R["meta"]
    pot = m.get("potentiel_langues") or []
    heading(doc, "Où est le potentiel, langue par langue", "5")
    if not pot:
        return
    body(doc, "Requêtes hors marque sur lesquelles le site apparaît déjà entre la 3e et la 25e place. "
              "Elles sont vues mais presque jamais cliquées : c'est là que se trouve la marge la plus accessible, "
              "sans avoir à partir de zéro.")
    for p in pot:
        caption(doc, f'{p["label"]} : {fr(p.get("n"))} requêtes concernées, {fr(p.get("total_impressions"))} impressions')
        rws = []
        for r in p.get("rows", []):
            i = r.get("impressions") or 0
            c = r.get("clicks") or 0
            rws.append([r.get("key"), fr(i), fr(c), fr(r.get("position"), dec=1),
                        fr(round(c / i * 100, 2), pct=True) if i else "-"])
        if rws:
            table(doc, ["Requête", "Impressions", "Clics", "Position", "Taux de clic"], rws,
                  widths=[6.4, 2.6, 1.8, 2.2, 2.6], aligns=["l", "c", "c", "c", "c"])
    note(doc, "Échelle : site entier, dimension requête, mois de référence. La file complète est dans l'Excel, "
              "onglet Opportunités.")


def sec_sujets(doc, R):
    m = R["meta"]
    suj = m.get("sujets") or []
    if not suj:
        return
    heading(doc, "Les sujets à écrire", "6")
    body(doc, "Chaque sujet ci-dessous regroupe des recherches que les internautes font déjà et sur lesquelles "
              "le site apparaît sans être choisi. Ce sont des articles de vulgarisation, pas des pages techniques : "
              "un rédacteur peut les traiter sans connaissance SEO particulière.")
    LBL = {"fr": "Français", "en": "Anglais", "de": "Allemand"}
    for lg in ("fr", "de", "en"):
        items = [s for s in suj if s.get("langue") == lg]
        if not items:
            continue
        caption(doc, LBL.get(lg, lg))
        for s in items:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(7); p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.keep_with_next = True
            run(p, "• ", size=10, bold=True, color=GREEN)
            run(p, s.get("titre", ""), size=10, bold=True, color=DARK)
            d = doc.add_paragraph(); d.paragraph_format.space_after = Pt(1)
            d.paragraph_format.left_indent = Cm(0.5)
            run(d, f'{fr(s.get("impressions"))} impressions par mois sur {fr(s.get("n_requetes"))} recherches, '
                   f'position moyenne actuelle {fr(s.get("position"), dec=1)}, '
                   f'{fr(s.get("clics"))} clic{"s" if (s.get("clics") or 0) > 1 else ""} seulement.', size=9.5)
            q = doc.add_paragraph(); q.paragraph_format.space_after = Pt(3)
            q.paragraph_format.left_indent = Cm(0.5)
            run(q, "Recherches couvertes : " + ", ".join(s.get("requetes", [])[:6]), size=9, color=GREY)
    note(doc, "Impressions relevées sur le mois de référence. Un sujet regroupe volontairement plusieurs "
              "formulations d'une même question : un seul article les couvre toutes.")


def sec_ga4(doc, R):
    g = R.get("ga4")
    if not g:
        return
    heading(doc, "Comportement des visiteurs", "7")
    org = next((c for c in g["channels"] if str(c["channel"]).lower() == "organic search"), None)
    txt = f"L'organique apporte {fr(g.get('organic_share'), pct=True)} des sessions du site."
    if org:
        txt += (f" Ces sessions s'engagent mieux que la moyenne : {fr(org['engagement_rate'], pct=True)} "
                f"de taux d'engagement et {fr(org['conversions'])} conversions attribuées.")
    if g.get("ai_sessions"):
        txt += f" Les moteurs conversationnels apportent {fr(g['ai_sessions'])} sessions, un signal à suivre."
    body(doc, txt)
    ch = [c for c in g["channels"] if c.get("sessions")][:8]
    if ch:
        put(doc, chart_barh([c["channel"] for c in ch], [c["sessions"] for c in ch], "ga4.png"),
            "Sessions par canal d'acquisition")
    note(doc, "Source : Google Analytics 4, mois de référence. Le canal Direct est conservé pour le "
              "contexte mais n'est pas un indicateur de performance SEO.")


def sec_hygiene(doc, R):
    c = R.get("crawl"); m = R.get("meta") or {}
    heading(doc, "Hygiène technique", "8")
    if not c:
        body(doc, "Aucun crawl du site n'est disponible dans Cartograph pour ce domaine sur la période. "
                  "Cette section reste vide plutôt que d'avancer des chiffres qui n'existent pas.", color=GREY)
        return
    raw = c.get("raw") or {}
    tiles(doc, [
        ("Score de crawl", fr(c.get("score")), "", None),
        ("Pages analysées", fr(c.get("pages")), "", None),
        ("Pages indexables", fr(raw.get("indexable")), "", None),
        ("URL dans le sitemap", fr(raw.get("sitemap_total")), "", None),
    ])
    note(doc, f"Crawl du {m.get('crawl_date','')} (Cartograph).")
    if m.get("crawl_constat"):
        body(doc, m["crawl_constat"])
    prios = m.get("crawl_prios") or []
    if prios:
        caption(doc, "Les trois corrections qui comptent")
        for i, p in enumerate(prios, 1):
            par = doc.add_paragraph()
            par.paragraph_format.space_before = Pt(8); par.paragraph_format.space_after = Pt(1)
            par.paragraph_format.keep_with_next = True
            run(par, f"{i}. ", size=10, bold=True, color=GREEN)
            run(par, p.get("titre", ""), size=10, bold=True, color=DARK)
            d = doc.add_paragraph(); d.paragraph_format.space_after = Pt(2)
            d.paragraph_format.left_indent = Cm(0.6)
            run(d, p.get("detail", ""), size=9.5)
    iss = [i for i in c.get("issues", []) if i.get("count")][:10]
    if len(iss) >= 2:
        put(doc, chart_barh([str(i.get("type"))[:36] for i in iss],
                            [int(float(i.get("count"))) for i in iss], "crawl.png", color=C2),
            "Pages concernées par typologie de problème")
    if m.get("crawl_bruit"):
        body(doc, m["crawl_bruit"], size=9.5)
    note(doc, "Le détail page par page est exportable depuis Cartograph.")


def sec_actions(doc, R):
    m = R.get("meta") or {}
    heading(doc, "Par quoi commencer", "9")
    acts = []
    for a in (m.get("actions") or []):
        acts.append((a.get("titre", ""), a.get("pourquoi", "")))
    if not acts:
        o = R.get("opportunities") or {}
        items = o.get("items") or []
        import unicodedata as _ud

        def _norm(k):
            k = _ud.normalize("NFKD", str(k or "")).encode("ascii", "ignore").decode().lower()
            return "".join(ch for ch in k if ch.isalnum())

        vus = set()
        for it in items:
            if len(acts) >= 3:
                break
            cle = _norm(it.get("key"))
            if cle in vus:
                continue
            vus.add(cle)
            nc = int(float(it.get("clicks") or 0))
            acts.append((f"Travailler « {it.get('key')} »",
                         f"Position {fr(it.get('position'), dec=1)} pour {fr(it.get('impressions'))} impressions "
                         f"et {fr(nc)} clic{'s' if nc > 1 else ''}."))
    if not acts:
        body(doc, "Données insuffisantes ce mois pour prioriser trois actions.", color=GREY)
        return
    for i, (titre, pourquoi) in enumerate(acts[:3], 1):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.keep_with_next = True
        run(p, f"{i}. ", size=10, bold=True, color=GREEN)
        run(p, titre, size=10, bold=True, color=DARK)
        d = doc.add_paragraph(); d.paragraph_format.space_after = Pt(2)
        d.paragraph_format.left_indent = Cm(0.6)
        run(d, pourquoi, size=9.5)
    if m.get("a_instruire"):
        caption(doc, "À instruire avant d'engager un chantier éditorial")
        body(doc, m["a_instruire"], size=9.5)


def sec_annexe(doc, R):
    heading(doc, "Ce que contient l'Excel joint", "10")
    body(doc, "Le Word donne la lecture, l'Excel garde la donnée complète et vérifiable.")
    onglets = [["Synthèse", "Les trois échelles, mois par mois"],
               ["Langues", "Les trois versions linguistiques, mois par mois"],
               ["Historique", "Données quotidiennes de la période"],
               ["Requêtes", "Toutes les requêtes du mois, marque signalée, statut d'évolution"],
               ["Par page", "Toutes les pages du périmètre, clics, impressions, position"],
               ["Pays", "Répartition géographique complète"],
               ["Tendance", "Courbes hebdomadaires et mensuelles, graphiques natifs modifiables"],
               ["Opportunités", "La file complète des requêtes à travailler"],
               ["GA4", "Canaux d'acquisition et pages d'entrée organiques"]]
    if R.get("crawl"):
        onglets.append(["Hygiène", "Score du crawl et problèmes par typologie"])
    table(doc, ["Onglet", "Contenu"], onglets, widths=[4.0, 11.6], aligns=["l", "l"])


MOIS_ABBR = {"janvier": "Janv.", "février": "Févr.", "mars": "Mars", "avril": "Avril", "mai": "Mai",
             "juin": "Juin", "juillet": "Juil.", "août": "Août", "septembre": "Sept.",
             "octobre": "Oct.", "novembre": "Nov.", "décembre": "Déc."}


def short_month(lbl):
    s = str(lbl or "").strip()
    base = s.split()[0] if s else s
    return MOIS_ABBR.get(base.lower(), base[:5])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--logo")
    a = ap.parse_args()
    global CHART_DIR
    CHART_DIR = tempfile.mkdtemp(prefix="charts_")
    R = json.load(open(a.data, encoding="utf-8")); m = R["meta"]
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10)
    st.paragraph_format.space_after = Pt(6)
    header_footer(doc, m)
    cover(doc, m, a.logo)
    sec_grille(doc, R)
    sec_apercu(doc, R)
    sec_langues(doc, R)
    sec_echelles(doc, R)
    sec_marque(doc, R)
    sec_potentiel(doc, R)
    sec_sujets(doc, R)
    sec_ga4(doc, R)
    sec_hygiene(doc, R)
    sec_actions(doc, R)
    sec_annexe(doc, R)
    doc.save(a.out)
    print("docx:", a.out)


if __name__ == "__main__":
    main()
