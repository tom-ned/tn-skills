#!/usr/bin/env python3
"""merge_langues.py - assemble un rapport UNIQUE multilingue.

Prend les report_data.json produits par prepare_data.py (un par langue) et les
fusionne en un seul jeu de donnees : KPI du site sur la dimension date, bloc par
langue, historique quotidien, marche prioritaire.

    python3 merge_langues.py --base report_data_fr.json \
        --langue fr:Francais:/fr/:report_data_fr.json \
        --langue en:Anglais:/en/:report_data_en.json \
        --langue de:Allemand:/de/:report_data_de.json \
        --gsc-page gsc_page.json --gsc-date gsc_date.json \
        --ga4-landing ga4_landing.json \
        --out report_data_global.json

Le fichier de sortie se donne ensuite a build_report.py et build_xlsx.py.
"""
import argparse, json, collections


def load(p):
    if not p:
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="un report_data.json quelconque, sert de socle")
    ap.add_argument("--langue", action="append", default=[],
                    help="code:Libelle:/prefixe/:chemin_report_data.json (repetable)")
    ap.add_argument("--gsc-page", help="gsc_page.json non filtre (toutes langues)")
    ap.add_argument("--gsc-date", help="gsc_date.json couvrant M-2 a M")
    ap.add_argument("--ga4-landing", help="ga4_landing.json non filtre")
    ap.add_argument("--top-pages", type=int, default=5, help="pages listees par langue (defaut 5)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    R = load(a.base)
    meta = dict(R["meta"])
    meta["language"] = "Site entier"
    meta["perimeter_prefix"] = ""
    meta.pop("lang_kpi", None)

    pages = (load(a.gsc_page) or {}).get("rows") or []
    langues = []
    for spec in a.langue:
        code, label, prefix, path = spec.split(":", 3)
        rd = load(path) or {}
        lk = (rd.get("meta") or {}).get("lang_kpi") or {}
        ps = [p for p in pages if prefix in p.get("key", "")]
        ps.sort(key=lambda p: -p.get("clicks", 0))
        langues.append({
            "code": code, "label": label, "prefix": prefix, "kpi": lk,
            "n_pages": len(ps),
            "top_pages": [{"url": p["key"], "clicks": p["clicks"], "impressions": p["impressions"],
                           "position": round(p.get("position") or 0, 1)} for p in ps[:a.top_pages]],
        })
    if langues:
        meta["langues"] = langues
        meta["language"] = "Site entier (" + ", ".join(l["code"].upper() for l in langues) + ")"

    # KPI du site : dimension date, la seule coherente sur plusieurs mois
    dates = (load(a.gsc_date) or {}).get("rows") or []
    if dates:
        mois = collections.OrderedDict()
        for r in dates:
            k = r["key"][:7]
            m = mois.setdefault(k, {"clicks": 0, "impressions": 0, "days": 0})
            m["clicks"] += r.get("clicks", 0)
            m["impressions"] += r.get("impressions", 0)
            m["days"] += 1
        ks = list(mois)
        sk = {}
        for lbl, k in zip(("M2", "M1", "M"), ks[-3:]):
            v = mois[k]
            sk[lbl] = {"clicks": v["clicks"], "impressions": v["impressions"],
                       "ctr": round(v["clicks"] / v["impressions"] * 100, 2) if v["impressions"] else None}
        meta["site_kpi"] = sk
        for r in dates:
            r["ctr"] = round(r["clicks"] / r["impressions"] * 100, 2) if r.get("impressions") else 0
        meta["historique"] = {
            "daily": dates,
            "months": [{"month": k, "clicks": v["clicks"], "impressions": v["impressions"],
                        "days": v["days"], "partial": v["days"] < 28,
                        "ctr": round(v["clicks"] / v["impressions"] * 100, 2) if v["impressions"] else 0}
                       for k, v in mois.items()],
            "lang_months": [],
        }

    R["meta"] = meta
    if pages:
        R["pages"] = [{"url": p["key"], "clicks": p["clicks"], "impressions": p["impressions"],
                       "position": round(p.get("position") or 0, 1)}
                      for p in sorted(pages, key=lambda p: -p.get("clicks", 0))[:200]]
    land = (load(a.ga4_landing) or {}).get("rows") or []
    if land and R.get("ga4"):
        R["ga4"]["landing"] = [{"page": r["key"], "sessions": r["sessions"],
                                "conversions": r.get("conversions", 0),
                                "engagement_rate": r.get("engagement_rate")}
                               for r in sorted(land, key=lambda r: -r["sessions"])[:25]]
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False)
    print("rapport unique ecrit :", a.out, "|", len(langues), "langues |",
          len((meta.get("historique") or {}).get("daily") or []), "jours")


if __name__ == "__main__":
    main()
