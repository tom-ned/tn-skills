#!/usr/bin/env python3
"""prepare_competitors.py - Ajoute le bloc "concurrence" au report_data.json (rapport concurrence).

A lancer APRES prepare_data.py. Fusionne dans report_data.json :
- part de voix instantanee (client + concurrents) via getAllCompetitorsMetrics ;
- comparatif mensuel M-2/M-1/M (TOP 10 et position moyenne) client vs concurrents ;
- serie hebdomadaire "mots-cles en TOP 10" par acteur (courbe comparee) ;
- face a face par mot-cle (position du client vs chaque concurrent, mois courant).

Entrees : --data report_data.json ; --comp "Nom|domaine|fichier" (x3, getCompetitorPositions sur
[1er jour M-2 .. aujourd'hui]) ; --sov getAllCompetitorsMetrics ; --client-domain ; --out.
pos>=100 = non positionne. TOP 10 = pos<=10. Position d'un mois = derniere position connue du mois.
Le face a face matche les mots-cles par nom (les concurrents sont suivis sur le meme set de requetes).
"""
import argparse
import json
import unicodedata
from datetime import datetime
from collections import defaultdict


def load_json(path):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "text" in raw[0]:
        try:
            raw = json.loads(raw[0]["text"])
        except Exception:
            pass
    return raw


def norm(s):
    s = (s or "").strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return " ".join(s.split())


def pick_engine(payload, engine_id):
    data = payload.get("data", payload) if isinstance(payload, dict) else payload
    if not isinstance(data, list):
        return None
    for e in data:
        if str(e.get("site_engine_id")) == str(engine_id):
            return e
    return max(data, key=lambda e: len(e.get("keywords", []))) if data else None


def last_pos_in_month(positions, ym):
    pts = [p for p in positions if (p.get("date") or "").startswith(ym)]
    if not pts:
        return None
    pts.sort(key=lambda p: p["date"])
    pos = pts[-1].get("pos")
    try:
        pos = int(pos)
    except (TypeError, ValueError):
        return None
    if pos <= 0 or pos >= 100:
        return None
    return pos


def monthly_metrics(keywords, ym):
    top10 = 0
    poss = []
    for kw in keywords:
        p = last_pos_in_month(kw.get("positions", []), ym)
        if p is None:
            continue
        poss.append(p)
        if p <= 10:
            top10 += 1
    avg = round(sum(poss) / len(poss), 1) if poss else None
    return {"top10": top10, "avg": avg, "ranked": len(poss)}


def weekly_top10(keywords):
    weeks = defaultdict(dict)
    for kw in keywords:
        kid = kw.get("id")
        for p in kw.get("positions", []):
            try:
                d = datetime.strptime(p["date"], "%Y-%m-%d").date()
            except Exception:
                continue
            key = (d.isocalendar()[0], d.isocalendar()[1])
            cur = weeks[key].get(kid)
            if cur is None or p["date"] >= cur[0]:
                weeks[key][kid] = (p["date"], p.get("pos"))
    labels, values = [], []
    for key in sorted(weeks.keys()):
        cnt = 0
        for _, (_, pos) in weeks[key].items():
            try:
                pos = int(pos)
            except (TypeError, ValueError):
                continue
            if 1 <= pos <= 10:
                cnt += 1
        labels.append(str(key[0]) + "-S" + ("%02d" % key[1]))
        values.append(cnt)
    return {"labels": labels, "values": values}


def comp_current_by_name(keywords, ym):
    out = {}
    for kw in keywords:
        out[norm(kw.get("name"))] = last_pos_in_month(kw.get("positions", []), ym)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--comp", action="append", default=[])
    ap.add_argument("--sov")
    ap.add_argument("--client-domain", default="")
    ap.add_argument("--out")
    args = ap.parse_args()

    R = load_json(args.data)
    meta = R["meta"]
    engine_id = meta.get("engine_id")
    ym_c = meta.get("period_current")
    ym_p = meta.get("period_prev")
    ym_p2 = meta.get("period_prev2")

    competitors = []
    comp_name_maps = []
    for spec in args.comp:
        parts = spec.split("|")
        if len(parts) != 3:
            print("WARN: --comp ignore (Nom|domaine|fichier) : " + spec)
            continue
        name, domain, path = parts
        eng = pick_engine(load_json(path), engine_id)
        kws = eng.get("keywords", []) if eng else []
        competitors.append({
            "name": name, "domain": domain,
            "monthly": {"prev2": monthly_metrics(kws, ym_p2), "prev": monthly_metrics(kws, ym_p),
                        "current": monthly_metrics(kws, ym_c)},
            "weekly_top10": weekly_top10(kws),
        })
        comp_name_maps.append((name, comp_current_by_name(kws, ym_c)))

    share = []
    if args.sov:
        sov = load_json(args.sov)
        rows = sov.get("data", sov) if isinstance(sov, dict) else sov
        wanted = {args.client_domain.lower().replace("www.", "")}
        for c in competitors:
            wanted.add(c["domain"].lower().replace("www.", ""))
        for row in rows or []:
            dom = (row.get("domain") or "").lower().replace("www.", "")
            if dom in wanted:
                share.append({"domain": row.get("domain"), "visibility": row.get("visibility"),
                              "is_client": dom == args.client_domain.lower().replace("www.", "")})
        share.sort(key=lambda x: -(x["visibility"] or 0))

    s = R["summary"]
    client_row = {
        "name": meta.get("client", "Client"), "domain": args.client_domain or meta.get("domain", ""),
        "is_client": True,
        "monthly": {"prev2": {"top10": s["prev2"]["top10"], "avg": s["prev2"]["avg_pos"]},
                    "prev": {"top10": s["prev"]["top10"], "avg": s["prev"]["avg_pos"]},
                    "current": {"top10": s["current"]["top10"], "avg": s["current"]["avg_pos"]}},
        "weekly_top10": R["weekly_trend"].get("top10", {"labels": [], "values": []}),
    }

    # Face a face par mot-cle (mois courant)
    def rank_val(p):
        return p if (p is not None) else 999
    head = []
    for k in R["keywords"]:
        nm = norm(k.get("keyword"))
        comps = []
        for name, mp in comp_name_maps:
            comps.append({"name": name, "pos": mp.get(nm)})
        client_pos = k.get("pos_current")
        contenders = [(client_row["name"], client_pos)] + [(c["name"], c["pos"]) for c in comps]
        best = min(contenders, key=lambda x: rank_val(x[1]))[0]
        client_wins = rank_val(client_pos) <= min(rank_val(c["pos"]) for c in comps) if comps else True
        head.append({"keyword": k.get("keyword"), "volume": k.get("volume", 0), "page": k.get("page"),
                     "client_pos": client_pos, "comps": comps, "best": best, "client_wins": client_wins})
    head.sort(key=lambda r: -(r["volume"] or 0))

    R["competition"] = {"client": client_row, "competitors": competitors,
                        "share_of_voice": share, "head_to_head": head}
    out = args.out or args.data
    with open(out, "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)
    print("OK competition : " + str(len(competitors)) + " concurrents, " + str(len(head)) + " mots-cles face a face")


if __name__ == "__main__":
    main()
