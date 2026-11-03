#!/usr/bin/env python3
"""
prepare_data.py - Normalise les donnees brutes SE Ranking en un report_data.json unique.

Role : absorber tout le volume (centaines de mots-cles x plusieurs moteurs x 3 mois) hors
du contexte du modele. L'agent ne lit jamais les gros fichiers SE Ranking : il les passe ici,
et ce script produit un report_data.json compact et deja diffe que build_xlsx.py / build_docx.py
consomment.

Entrees (chemins de fichiers JSON tels que sauves par le MCP SE Ranking ; le wrapper MCP
{"data": ...} ou la forme brute sont tous deux acceptes) :
  --kw-current    getKeywordStats fenetre fin de mois courant (with_landing_pages=1)
  --kw-prev       getKeywordStats fenetre fin de M-1
  --kw-prev2      getKeywordStats fenetre fin de M-2
  --hist-vis      getPositionHistory type=visibility_percent sur ~3 mois
  --hist-avgpos   getPositionHistory type=avg_pos sur ~3 mois
  --hist-top10    getPositionHistory type=top10 sur ~3 mois
  --meta          JSON meta (client, domain, project_id, periods, dates, consultant, engine_id?)
  --out           chemin de sortie report_data.json

Choix de conception :
- UN SEUL moteur de recherche est retenu (le Google principal par defaut, sinon --engine-id,
  sinon le moteur avec le plus de mots-cles) pour ne pas tripler les volumes par page.
- La position d'un mois = derniere position disponible dans la fenetre fournie (robuste meme si
  le check n'est pas tombe pile le dernier jour du mois).
- "gain" = amelioration de position (le chiffre baisse). delta = pos_courant - pos_precedent ;
  delta negatif = progression.
"""
import argparse, json, sys
from datetime import datetime
from collections import defaultdict


def load_json(path):
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # Le MCP enveloppe parfois la sortie dans [{"type":"text","text":"...json..."}]
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "text" in raw[0]:
        try:
            raw = json.loads(raw[0]["text"])
        except Exception:
            pass
    return raw


def engines_from_kwstats(payload):
    """Retourne la liste [{site_engine_id, keywords:[...]}] depuis un getKeywordStats."""
    if payload is None:
        return []
    data = payload.get("data", payload) if isinstance(payload, dict) else payload
    if isinstance(data, dict):
        data = data.get("data", [])
    return data or []


def pick_engine(engines, forced_id=None):
    if not engines:
        return None
    if forced_id is not None:
        for e in engines:
            if str(e.get("site_engine_id")) == str(forced_id):
                return e
    # Sinon : le moteur avec le plus de mots-cles (en general le Google principal)
    return max(engines, key=lambda e: len(e.get("keywords", [])))


def last_pos(kw):
    """Derniere position connue dans la fenetre (ou None)."""
    positions = kw.get("positions") or []
    valid = [p for p in positions if p.get("pos") not in (None, 0) or p.get("pos") == 0]
    # pos peut valoir >100 (hors radar). On garde la derniere entree datee.
    dated = [p for p in positions if p.get("date")]
    if not dated:
        return None
    dated.sort(key=lambda p: p["date"])
    pos = dated[-1].get("pos")
    if pos in (None, 0):
        return None
    return int(pos)


def index_keywords(engine):
    """id -> dict keyword pour un moteur."""
    out = {}
    for kw in engine.get("keywords", []):
        out[str(kw.get("id"))] = kw
    return out


def status_for(pos):
    if pos is None:
        return "hors"
    if pos <= 3:
        return "top3"
    if pos <= 10:
        return "top10"
    if pos <= 30:
        return "top30"
    return "hors_top30"


def iso_week_label(d):
    y, w, _ = d.isocalendar()
    return f"{y}-S{w:02d}"


def resample_weekly(history_payload, prefer_avg=True):
    """getPositionHistory -> {labels:[...], values:[...]} hebdo (derniere valeur de la semaine)."""
    if not history_payload:
        return {"labels": [], "values": []}
    series = history_payload.get("data", history_payload)
    if not isinstance(series, list) or not series:
        return {"labels": [], "values": []}
    chosen = None
    if prefer_avg:
        for s in series:
            if s.get("type") == "avg" or s.get("name", "").lower().startswith("average"):
                chosen = s
                break
    if chosen is None:
        chosen = max(series, key=lambda s: len(s.get("data", [])))
    weeks = defaultdict(list)
    for pt in chosen.get("data", []):
        try:
            d = datetime.strptime(pt["date"], "%Y-%m-%d").date()
        except Exception:
            continue
        weeks[(d.isocalendar()[0], d.isocalendar()[1])].append((d, pt.get("value")))
    labels, values = [], []
    for key in sorted(weeks.keys()):
        pts = sorted(weeks[key], key=lambda x: x[0])
        last = pts[-1][1]
        labels.append(f"{key[0]}-S{key[1]:02d}")
        values.append(round(last, 2) if isinstance(last, (int, float)) else None)
    return {"labels": labels, "values": values}


def summarize(keywords, key_pos):
    """Statistiques agregees pour un mois donne (key_pos: 'pos_current'|'pos_prev'|'pos_prev2')."""
    tracked = 0
    top3 = top10 = top30 = 0
    poss = []
    for k in keywords:
        p = k.get(key_pos)
        if p is None:
            continue
        tracked += 1
        poss.append(p)
        if p <= 3:
            top3 += 1
        if p <= 10:
            top10 += 1
        if p <= 30:
            top30 += 1
    avg = round(sum(poss) / len(poss), 1) if poss else None
    return {"tracked": tracked, "top3": top3, "top10": top10, "top30": top30, "avg_pos": avg}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kw-current", required=True)
    ap.add_argument("--kw-prev")
    ap.add_argument("--kw-prev2")
    ap.add_argument("--hist-vis")
    ap.add_argument("--hist-avgpos")
    ap.add_argument("--hist-top10")
    ap.add_argument("--meta", required=True)
    ap.add_argument("--engine-id")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    meta = load_json(args.meta) or {}
    forced = args.engine_id or meta.get("engine_id")

    cur_engines = engines_from_kwstats(load_json(args.kw_current))
    cur_engine = pick_engine(cur_engines, forced)
    if cur_engine is None:
        print("ERREUR: aucun moteur dans kw-current", file=sys.stderr)
        sys.exit(1)
    engine_id = cur_engine.get("site_engine_id")

    prev_engine = pick_engine(engines_from_kwstats(load_json(args.kw_prev)), engine_id) if args.kw_prev else None
    prev2_engine = pick_engine(engines_from_kwstats(load_json(args.kw_prev2)), engine_id) if args.kw_prev2 else None

    cur_idx = index_keywords(cur_engine)
    prev_idx = index_keywords(prev_engine) if prev_engine else {}
    prev2_idx = index_keywords(prev2_engine) if prev2_engine else {}

    keywords = []
    for kid, kw in cur_idx.items():
        pages = kw.get("landing_pages") or []
        page = pages[0].get("url") if pages else None
        pos_c = last_pos(kw)
        pos_p = last_pos(prev_idx[kid]) if kid in prev_idx else None
        pos_p2 = last_pos(prev2_idx[kid]) if kid in prev2_idx else None
        delta = (pos_c - pos_p) if (pos_c is not None and pos_p is not None) else None
        keywords.append({
            "keyword": kw.get("name"),
            "volume": kw.get("volume") or 0,
            "page": page or "(non attribuee)",
            "pos_current": pos_c,
            "pos_prev": pos_p,
            "pos_prev2": pos_p2,
            "delta": delta,            # negatif = progression
            "status": status_for(pos_c),
            "status_prev": status_for(pos_p),
        })

    keywords.sort(key=lambda k: (-(k["volume"] or 0), k["keyword"] or ""))

    # ---- Agregation par page ----
    pages = defaultdict(lambda: {"keywords": [], "sum_volume": 0, "positions": [], "top10": 0})
    for k in keywords:
        p = pages[k["page"]]
        p["keywords"].append(k["keyword"])
        p["sum_volume"] += k["volume"] or 0
        if k["pos_current"] is not None:
            p["positions"].append(k["pos_current"])
            if k["pos_current"] <= 10:
                p["top10"] += 1
    page_rows = []
    for url, p in pages.items():
        avg = round(sum(p["positions"]) / len(p["positions"]), 1) if p["positions"] else None
        page_rows.append({
            "page": url,
            "n_keywords": len(p["keywords"]),
            "sum_volume": p["sum_volume"],
            "avg_pos": avg,
            "top10": p["top10"],
            "keywords": sorted(set(p["keywords"])),
        })
    page_rows.sort(key=lambda r: -r["sum_volume"])

    # ---- Highlights ----
    movers = [k for k in keywords if k["delta"] is not None]
    gains = sorted([k for k in movers if k["delta"] < 0], key=lambda k: (k["delta"], -(k["volume"] or 0)))[:15]
    high_volume = sorted([k for k in keywords if k["pos_current"] and k["pos_current"] <= 10],
                         key=lambda k: -(k["volume"] or 0))[:15]
    top_entries = [k for k in keywords
                   if k["status_prev"] in ("hors", "top30", "hors_top30") and k["status"] in ("top3", "top10")
                   or (k["status_prev"] == "top10" and k["status"] == "top3")]
    top_entries = sorted(top_entries, key=lambda k: -(k["volume"] or 0))[:15]
    top_exits = [k for k in keywords
                 if k["status_prev"] in ("top3", "top10") and k["status"] in ("hors", "top30", "hors_top30")
                 or (k["status_prev"] == "top3" and k["status"] == "top10")]
    top_exits = sorted(top_exits, key=lambda k: -(k["volume"] or 0))[:15]

    summary = {
        "current": summarize(keywords, "pos_current"),
        "prev": summarize(keywords, "pos_prev"),
        "prev2": summarize(keywords, "pos_prev2"),
    }

    weekly = {
        "visibility_percent": resample_weekly(load_json(args.hist_vis)),
        "avg_pos": resample_weekly(load_json(args.hist_avgpos)),
        "top10": resample_weekly(load_json(args.hist_top10)),
    }

    report = {
        "meta": {**meta, "engine_id": engine_id,
                 "engine_label": meta.get("engine_label") or f"moteur {engine_id}"},
        "summary": summary,
        "keywords": keywords,
        "pages": page_rows,
        "highlights": {
            "gains": gains,
            "high_volume": high_volume,
            "top_entries": top_entries,
            "top_exits": top_exits,
        },
        "weekly_trend": weekly,
        "counts": {"keywords": len(keywords), "pages": len(page_rows)},
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"OK report_data.json : {len(keywords)} mots-cles, {len(page_rows)} pages, moteur {engine_id}")


if __name__ == "__main__":
    main()
