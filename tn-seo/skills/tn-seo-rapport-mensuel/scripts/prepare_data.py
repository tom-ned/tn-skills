#!/usr/bin/env python3
"""prepare_data.py - normalise les dumps Cartograph en un report_data.json unique.

Tous les fichiers de donnees sont OPTIONNELS : un fichier absent => la section correspondante est
marquee "non disponible" dans les livrables. Aucun chiffre n'est invente.
"""
import argparse, json, os, re, unicodedata, glob
from datetime import date, datetime
from urllib.parse import urlparse


def load(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def rows_of(d):
    if not d:
        return []
    if isinstance(d, list):
        return d
    for k in ("rows", "keywords", "data", "items", "results"):
        if isinstance(d.get(k), list):
            return d[k]
    return []


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def is_brand(key, brand_terms):
    k = norm(key)
    return any(bt and norm(bt) in k for bt in brand_terms)


def num(x, d=0.0):
    try:
        return float(x)
    except Exception:
        return d


def wpos(rows):
    """position moyenne ponderee par impressions."""
    ti = sum(num(r.get("impressions")) for r in rows)
    if ti <= 0:
        vals = [num(r.get("position")) for r in rows if r.get("position") not in (None, 0)]
        return round(sum(vals) / len(vals), 1) if vals else None
    return round(sum(num(r.get("position")) * num(r.get("impressions")) for r in rows) / ti, 1)


def kpi_from_query(d, brand_terms):
    rows = rows_of(d)
    if not rows:
        return None
    clicks = sum(num(r.get("clicks")) for r in rows)
    impr = sum(num(r.get("impressions")) for r in rows)
    brand_clicks = sum(num(r.get("clicks")) for r in rows if is_brand(r.get("key"), brand_terms))
    return {
        "clicks": int(clicks),
        "impressions": int(impr),
        "ctr": round(clicks / impr * 100, 1) if impr else 0.0,
        "avg_position": wpos(rows),
        "queries": len(rows),
        "top3": sum(1 for r in rows if 0 < num(r.get("position")) <= 3),
        "top10": sum(1 for r in rows if 0 < num(r.get("position")) <= 10),
        "brand_clicks": int(brand_clicks),
        "nonbrand_clicks": int(clicks - brand_clicks),
        "brand_share": round(brand_clicks / clicks * 100, 1) if clicks else 0.0,
    }


def build_queries(d, brand_terms, limit=400):
    out = []
    for r in rows_of(d):
        out.append({
            "key": r.get("key"),
            "brand": is_brand(r.get("key"), brand_terms),
            "clicks": int(num(r.get("clicks"))),
            "impressions": int(num(r.get("impressions"))),
            "ctr": round(num(r.get("ctr")), 1),
            "position": round(num(r.get("position")), 1) if r.get("position") is not None else None,
            "status": r.get("status"),
            "trend_pct": r.get("trend_pct"),
        })
    out.sort(key=lambda x: x["clicks"], reverse=True)
    return out[:limit]


def build_pages(d, prefix=None, limit=200):
    out = []
    for r in rows_of(d):
        url = r.get("key") or ""
        if prefix and prefix not in url:
            continue
        out.append({
            "url": url,
            "clicks": int(num(r.get("clicks"))),
            "impressions": int(num(r.get("impressions"))),
            "position": round(num(r.get("position")), 1) if r.get("position") is not None else None,
        })
    out.sort(key=lambda x: x["clicks"], reverse=True)
    return out[:limit]


def build_countries(d, limit=30):
    out = []
    for r in rows_of(d):
        out.append({
            "country": r.get("key"),
            "clicks": int(num(r.get("clicks"))),
            "impressions": int(num(r.get("impressions"))),
            "ctr": round(num(r.get("ctr")), 1),
            "position": round(num(r.get("position")), 1) if r.get("position") is not None else None,
        })
    out.sort(key=lambda x: x["clicks"], reverse=True)
    return out[:limit]


def iso_week(dstr):
    try:
        y, w, _ = datetime.strptime(dstr, "%Y-%m-%d").isocalendar()
        return f"{y}-S{w:02d}"
    except Exception:
        return None


def build_trend(d):
    rows = rows_of(d)
    if not rows:
        return None
    months, weeks = {}, {}
    for r in rows:
        dstr = r.get("key")
        c, i, p = num(r.get("clicks")), num(r.get("impressions")), num(r.get("position"))
        mk = (dstr or "")[:7]
        m = months.setdefault(mk, {"clicks": 0, "impressions": 0, "pw": 0.0, "days": 0})
        m["clicks"] += c; m["impressions"] += i; m["pw"] += p * i; m["days"] += 1
        wk = iso_week(dstr)
        if wk:
            w = weeks.setdefault(wk, {"clicks": 0, "impressions": 0, "pw": 0.0, "days": 0})
            w["clicks"] += c; w["impressions"] += i; w["pw"] += p * i; w["days"] += 1
    def fin(dd):
        out = []
        for k in sorted(dd):
            e = dd[k]
            out.append({"key": k, "clicks": int(e["clicks"]), "impressions": int(e["impressions"]),
                        "position": round(e["pw"] / e["impressions"], 1) if e["impressions"] else None,
                        "days": int(e.get("days", 0))})
        return out
    return {"months": fin(months), "weeks": fin(weeks)}


def build_opportunities(opp, gsc_query_m, brand_terms):
    """Utilise les opportunites scorees si presentes, sinon fallback GSC."""
    scored = []
    if opp:
        for o in (opp.get("opportunities") or []):
            scored.append(o)
    if scored:
        return {"source": "enrichi", "items": scored[:30], "coverage": opp.get("coverage", [])[:20]}
    # fallback GSC
    rows = [r for r in rows_of(gsc_query_m) if not is_brand(r.get("key"), brand_terms)]
    if not rows:
        return {"source": "aucune", "items": [], "coverage": []}
    impr_sorted = sorted(rows, key=lambda r: num(r.get("impressions")), reverse=True)
    tercile = num(impr_sorted[max(0, len(impr_sorted) // 3 - 1)].get("impressions")) if impr_sorted else 0
    items = []
    for r in rows:
        pos = num(r.get("position")); impr = num(r.get("impressions"))
        clicks = num(r.get("clicks")); ctr = num(r.get("ctr"))
        typ = None
        if 4 <= pos <= 10 and impr >= tercile:
            typ = "quick win TOP 3"
        elif 11 <= pos <= 20:
            typ = "page 2 -> page 1"
        elif impr >= tercile and ctr < 1.0 and pos <= 10:
            typ = "title / meta à retravailler"
        if typ:
            items.append({"key": r.get("key"), "impressions": int(impr), "clicks": int(clicks),
                          "position": round(pos, 1), "type": typ})
    order = {"quick win TOP 3": 0, "page 2 -> page 1": 1, "title / meta à retravailler": 2}
    items.sort(key=lambda x: (order.get(x["type"], 9), -x["impressions"]))
    return {"source": "fallback_gsc", "items": items[:30], "coverage": []}


def build_ga4(chan, landing):
    if not chan and not landing:
        return None
    channels = []
    for r in rows_of(chan):
        channels.append({"channel": r.get("key"), "sessions": int(num(r.get("sessions"))),
                         "users": int(num(r.get("users"))), "conversions": int(num(r.get("conversions"))),
                         "engagement_rate": round(num(r.get("engagement_rate")), 1),
                         "bounce_rate": round(num(r.get("bounce_rate")), 1),
                         "avg_engagement_s": round(num(r.get("avg_engagement_s")), 1)})
    total = sum(c["sessions"] for c in channels) or 1
    org = next((c for c in channels if norm(c["channel"]) == "organic search"), None)
    ai = next((c for c in channels if norm(c["channel"]) in ("ai assistant", "ai assistants") or norm(c["channel"]).startswith("ai assistant")), None)
    lands = []
    for r in rows_of(landing):
        lands.append({"page": r.get("key"), "sessions": int(num(r.get("sessions"))),
                      "conversions": int(num(r.get("conversions"))),
                      "engagement_rate": round(num(r.get("engagement_rate")), 1)})
    lands.sort(key=lambda x: x["sessions"], reverse=True)
    return {"channels": channels, "landing": lands[:25],
            "organic_share": round((org["sessions"] / total * 100), 1) if org else None,
            "ai_sessions": ai["sessions"] if ai else 0}


def build_tracked(d):
    rows = rows_of(d)
    if not rows:
        return None
    out = []
    for r in rows:
        out.append({
            "keyword": r.get("keyword") or r.get("key"),
            "position": r.get("position"),
            "source": r.get("position_source") or r.get("source"),
            "best": r.get("best") or r.get("best_position"),
            "url": r.get("url") or r.get("ranking_url"),
            "group": r.get("group"),
            "delta": r.get("delta_period") if r.get("delta_period") is not None else r.get("delta"),
        })
    return out


def build_crawl(d):
    if not d:
        return None
    issues = d.get("issues") or d.get("issues_by_type") or d.get("problems") or []
    norm_issues = []
    if isinstance(issues, dict):
        issues = [{"type": k, "count": v} for k, v in issues.items()]
    for it in issues:
        if isinstance(it, dict):
            norm_issues.append({"type": it.get("type") or it.get("name") or it.get("label"),
                                "count": it.get("count") or it.get("n") or it.get("value"),
                                "severity": it.get("severity") or it.get("gravity")})
    norm_issues = [i for i in norm_issues if i["type"]]
    norm_issues.sort(key=lambda x: num(x.get("count")), reverse=True)
    return {"score": d.get("score") or d.get("last_score"),
            "pages": d.get("pages_count") or d.get("last_pages_count") or d.get("pages"),
            "issues": norm_issues[:15], "links": d.get("links") or d.get("links_summary"),
            "raw": {"indexable": d.get("indexable"), "sitemap_total": d.get("sitemap_total"),
                    "crawled_at": d.get("crawled_at"), "run_id": d.get("run_id")}}


def dom(u):
    try:
        h = urlparse(u if "//" in u else "//" + u).netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""


def build_serp(serp_dir, client_domain, competitors):
    if not serp_dir or not os.path.isdir(serp_dir):
        return None
    cdom = dom(client_domain)
    comp = [dom(c) for c in (competitors or [])]
    per_query = []
    tally = {cdom: 0}
    for c in comp:
        tally[c] = 0
    for path in sorted(glob.glob(os.path.join(serp_dir, "*.json"))):
        d = load(path)
        results = None
        for k in ("organic", "results", "organic_results", "serp", "rows"):
            if isinstance((d or {}).get(k), list):
                results = d[k]; break
        if results is None and isinstance(d, list):
            results = d
        if not results:
            continue
        top = []
        for it in results[:10]:
            u = it.get("url") or it.get("link") or it.get("domain") or it.get("displayed_link") or ""
            top.append(dom(u))
        q = (d or {}).get("query") or os.path.splitext(os.path.basename(path))[0]
        present = {"query": q, "client": cdom in top}
        if cdom in top:
            tally[cdom] += 1
        for c in comp:
            present[c] = c in top
            if c in top:
                tally[c] += 1
        present["top"] = top
        per_query.append(present)
    if not per_query:
        return None
    return {"client_domain": cdom, "competitors": comp, "per_query": per_query,
            "tally": tally, "n_queries": len(per_query)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    ap.add_argument("--gsc-query-m"); ap.add_argument("--gsc-query-m1"); ap.add_argument("--gsc-query-m2")
    ap.add_argument("--gsc-page"); ap.add_argument("--gsc-country"); ap.add_argument("--gsc-date")
    ap.add_argument("--ga4-channels"); ap.add_argument("--ga4-landing")
    ap.add_argument("--tracked"); ap.add_argument("--opportunities"); ap.add_argument("--crawl")
    ap.add_argument("--serp-dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    meta = load(a.meta) or {}
    brand_terms = meta.get("brand_terms") or []
    prefix = meta.get("perimeter_prefix")

    qm = load(a.gsc_query_m); qm1 = load(a.gsc_query_m1); qm2 = load(a.gsc_query_m2)
    R = {
        "meta": meta,
        "kpi": {"M": kpi_from_query(qm, brand_terms), "M1": kpi_from_query(qm1, brand_terms),
                "M2": kpi_from_query(qm2, brand_terms)},
        "queries": build_queries(qm, brand_terms) if qm else None,
        "pages": build_pages(load(a.gsc_page), prefix) if a.gsc_page else None,
        "countries": build_countries(load(a.gsc_country)) if a.gsc_country else None,
        "trend": build_trend(load(a.gsc_date)) if a.gsc_date else None,
        "opportunities": build_opportunities(load(a.opportunities), qm, brand_terms) if (a.opportunities or qm) else None,
        "ga4": build_ga4(load(a.ga4_channels), load(a.ga4_landing)) if (a.ga4_channels or a.ga4_landing) else None,
        "tracked": build_tracked(load(a.tracked)) if a.tracked else None,
        "crawl": build_crawl(load(a.crawl)) if a.crawl else None,
        "serp": build_serp(a.serp_dir, meta.get("domain", ""), meta.get("competitors")) if a.serp_dir else None,
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)
    have = [k for k in ("queries", "pages", "countries", "trend", "opportunities", "ga4", "tracked", "crawl", "serp") if R.get(k)]
    print("report_data ecrit:", a.out, "| sections:", ", ".join(have))


if __name__ == "__main__":
    main()
