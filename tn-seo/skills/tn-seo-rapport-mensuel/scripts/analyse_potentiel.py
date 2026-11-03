#!/usr/bin/env python3
"""analyse_potentiel.py - potentiel par LANGUE et regroupement en SUJETS d'articles.

Deux sorties, a injecter dans le report_data global :
  - potentiel_langues : les requetes hors marque ou le site est deja entre la 3e
    et la 25e place, ventilees par langue de la requete ;
  - sujets_candidats : ces memes requetes regroupees par mot pivot, avec le cumul
    d'impressions du groupe. C'est la matiere brute d'un sujet d'article : le
    titre editorial, lui, reste a ecrire par un humain.

    python3 analyse_potentiel.py --gsc-query-m gsc_query_M.json \
        --brand "marque,variante" --langues fr,en,de \
        --out-potentiel potentiel_langues.json --out-sujets sujets_candidats.json

La detection de langue est lexicale (FR, DE, IT, EN par defaut) : elle est faite
pour separer trois ou quatre versions d'un site, pas pour de la linguistique.
"""
import argparse, json, re, unicodedata, collections

ACCENTS = {"fr": "éèêàçùôîï", "de": "äöüß", "it": "àèéìòù"}
MOTS = {
    "fr": {"comment", "pourquoi", "quoi", "quel", "quelle", "combien", "definition", "metier",
           "salaire", "formation", "devenir", "prix", "avis", "guide", "que", "est-ce", "faire"},
    "de": {"wie", "was", "warum", "welche", "wer", "wo", "kosten", "beruf", "ausbildung",
           "werden", "preis", "erfahrungen", "anleitung", "ist", "sind", "tun"},
    "it": {"come", "perche", "quale", "quanto", "significato", "lavoro", "formazione", "prezzo"},
}
STOP = {
    "fr": {"le", "la", "les", "de", "des", "du", "un", "une", "et", "en", "sur", "pour", "dans",
           "au", "aux", "est", "que", "qui", "quoi", "comment", "pourquoi", "avec", "sans", "par"},
    "de": {"der", "die", "das", "und", "in", "im", "auf", "fur", "mit", "von", "zu", "den", "dem",
           "ein", "eine", "ist", "sind", "was", "wie", "wo", "man", "wenn", "auch"},
    "en": {"the", "a", "an", "of", "and", "in", "on", "for", "to", "is", "are", "what", "how",
           "why", "with", "from", "do", "does", "it", "you", "your"},
    "it": {"il", "lo", "la", "di", "e", "in", "per", "con", "che", "come"},
}


def deacc(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def detect(k, langues):
    x = str(k or "")
    w = set(re.findall(r"[a-zà-ÿ]+", x.lower()))
    for lg in langues:
        if lg == "en":
            continue
        if any(ch in x for ch in ACCENTS.get(lg, "")) or (w & MOTS.get(lg, set())):
            return lg
    return "en" if "en" in langues else langues[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gsc-query-m", required=True)
    ap.add_argument("--brand", default="", help="termes de marque separes par des virgules")
    ap.add_argument("--langues", default="fr,en,de")
    ap.add_argument("--pos-min", type=float, default=3.0)
    ap.add_argument("--pos-max", type=float, default=25.0)
    ap.add_argument("--top", type=int, default=6, help="requetes listees par langue")
    ap.add_argument("--min-groupe", type=int, default=3, help="requetes minimum pour former un sujet")
    ap.add_argument("--out-potentiel", required=True)
    ap.add_argument("--out-sujets", required=True)
    a = ap.parse_args()

    langues = [x.strip() for x in a.langues.split(",") if x.strip()]
    brand = [deacc(b) for b in a.brand.split(",") if b.strip()]
    rows = json.load(open(a.gsc_query_m, encoding="utf-8"))["rows"]

    retenues = collections.defaultdict(list)
    for r in rows:
        k = r.get("key") or ""
        if brand and any(b in deacc(k) for b in brand):
            continue
        pos = r.get("position") or 0
        if not (a.pos_min <= pos <= a.pos_max):
            continue
        retenues[detect(k, langues)].append(r)

    LBL = {"fr": "Français", "en": "Anglais", "de": "Allemand", "it": "Italien"}
    potentiel = []
    for lg in langues:
        lst = sorted(retenues.get(lg, []), key=lambda r: -r["impressions"])
        potentiel.append({
            "code": lg, "label": LBL.get(lg, lg.upper()),
            "n": len(lst), "total_impressions": sum(r["impressions"] for r in lst),
            "rows": [{"key": r["key"], "impressions": r["impressions"], "clicks": r["clicks"],
                      "position": round(r["position"], 1)} for r in lst[:a.top]],
        })

    # regroupement par mot pivot : la matiere d'un sujet d'article
    sujets = []
    for lg in langues:
        lst = retenues.get(lg, [])
        groupes = collections.defaultdict(list)
        for r in lst:
            for mot in set(re.findall(r"[a-zà-ÿ]{4,}", deacc(r["key"]))):
                if mot in STOP.get(lg, set()):
                    continue
                groupes[mot].append(r)
        vus = set()
        cands = []
        for mot, g in sorted(groupes.items(), key=lambda x: -sum(r["impressions"] for r in x[1])):
            g = [r for r in g if r["key"] not in vus]
            if len(g) < a.min_groupe:
                continue
            im = sum(r["impressions"] for r in g)
            cands.append({
                "langue": lg, "pivot": mot, "impressions": im,
                "clics": sum(r["clicks"] for r in g),
                "position": round(sum(r["position"] * r["impressions"] for r in g) / im, 1) if im else None,
                "n_requetes": len(g),
                "requetes": [r["key"] for r in sorted(g, key=lambda r: -r["impressions"])[:8]],
                "titre": "",
            })
            vus.update(r["key"] for r in g)
            if len(cands) >= 5:
                break
        sujets += cands

    json.dump(potentiel, open(a.out_potentiel, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(sujets, open(a.out_sujets, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for p in potentiel:
        print(f"{p['label']:10} {p['n']:5} requetes  {p['total_impressions']:7} impressions")
    print("\nsujets candidats (le champ titre est a remplir a la main) :")
    for s in sujets:
        print(f"  [{s['langue']}] pivot « {s['pivot']} » : {s['impressions']:6} impr, "
              f"{s['n_requetes']} requetes, pos {s['position']}")


if __name__ == "__main__":
    main()
