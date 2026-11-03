#!/usr/bin/env python3
"""analyze_opportunities.py - Deduit les opportunites SEO (gaps a capter) depuis report_data.json.

A lancer APRES prepare_data.py. Ajoute un bloc "opportunities" au report_data.json.
Cibles deduites automatiquement a partir de la position actuelle (pos_current) :
  - position 4-10  -> cible TOP 3   (quick win, on est juste au-dessus)
  - position 11-20 -> cible TOP 10  (page 2 haute, gros levier de trafic)
  - position 21-30 -> cible page 1  (page 2/3)
  - >30 ou non positionne, avec volume -> a aller chercher (cible : entrer dans le radar)
Plus les pages a optimiser (volume cumule consequent mais position moyenne faible) et le volume de
recherche non capte (somme des volumes hors TOP 10 / hors TOP 3).

L'idee : montrer ou se trouvent les paliers non franchis pour cibler l'effort la ou le rapport
volume/effort est le meilleur. Tout est trie par volume de recherche decroissant (priorite trafic).
"""
import argparse
import json


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def gap_to(pos, target):
    if pos is None:
        return None
    return max(0, pos - target)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out")
    ap.add_argument("--weak-page-min-volume", type=int, default=100,
                    help="Volume cumule minimal pour qu'une page soit candidate a l'optimisation")
    args = ap.parse_args()
    R = load(args.data)
    kws = R["keywords"]

    quick_top3, quick_top10, page23, to_chase = [], [], [], []
    for k in kws:
        p = k.get("pos_current")
        vol = k.get("volume") or 0
        base = {"keyword": k["keyword"], "volume": vol, "page": k["page"], "pos": p}
        if p is None:
            if vol > 0:
                to_chase.append({**base, "cible": "Entrer dans le radar", "gain": None})
            continue
        if 4 <= p <= 10:
            quick_top3.append({**base, "cible": "TOP 3", "gain": gap_to(p, 3)})
        elif 11 <= p <= 20:
            quick_top10.append({**base, "cible": "TOP 10", "gain": gap_to(p, 10)})
        elif 21 <= p <= 30:
            page23.append({**base, "cible": "Page 1", "gain": gap_to(p, 10)})
        elif p > 30:
            if vol > 0:
                to_chase.append({**base, "cible": "Entrer TOP 30", "gain": gap_to(p, 30)})

    for lst in (quick_top3, quick_top10, page23, to_chase):
        lst.sort(key=lambda x: -(x["volume"] or 0))

    # Pages a optimiser : volume cumule consequent mais position moyenne faible (>10) ou 0 en TOP 10
    weak_pages = []
    for pg in R.get("pages", []):
        avg = pg.get("avg_pos")
        if pg["sum_volume"] >= args.weak_page_min_volume and (avg is None or avg > 10 or pg["top10"] == 0):
            weak_pages.append({"page": pg["page"], "n_keywords": pg["n_keywords"],
                               "sum_volume": pg["sum_volume"], "avg_pos": avg, "top10": pg["top10"]})
    weak_pages.sort(key=lambda x: -(x["sum_volume"] or 0))

    total_vol = sum((k.get("volume") or 0) for k in kws)
    vol_top10 = sum((k.get("volume") or 0) for k in kws if k.get("pos_current") and k["pos_current"] <= 10)
    vol_top3 = sum((k.get("volume") or 0) for k in kws if k.get("pos_current") and k["pos_current"] <= 3)

    R["opportunities"] = {
        "quick_top3": quick_top3,
        "quick_top10": quick_top10,
        "page23": page23,
        "to_chase": to_chase,
        "weak_pages": weak_pages,
        "totals": {
            "volume_total": total_vol,
            "volume_top10": vol_top10,
            "volume_top3": vol_top3,
            "volume_non_capte": total_vol - vol_top10,
            "n_quick_top3": len(quick_top3),
            "n_quick_top10": len(quick_top10),
            "n_to_chase": len(to_chase),
        },
    }
    out = args.out or args.data
    with open(out, "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)
    print("OK opportunities : TOP3 " + str(len(quick_top3)) + ", TOP10 " + str(len(quick_top10))
          + ", page2-3 " + str(len(page23)) + ", a chercher " + str(len(to_chase))
          + ", pages a optimiser " + str(len(weak_pages)))


if __name__ == "__main__":
    main()
