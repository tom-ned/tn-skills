---
name: tn-seo-rapport-concurrence
description: >
  Rapport de concurrence SEO pour les clients de l'agence Suisseo, a partir des donnees SE Ranking
  (MCP). Compare le client a 3 concurrents : part de voix (visibilite), comparatif des positions
  M/M-1/M-2 (TOP 10 et position moyenne), courbe hebdomadaire comparee, et face a face mot-cle par
  mot-cle (qui se positionne le mieux). Produit un Word de synthese (charte Suisseo) et un Excel
  pure data, ranges dans [Client]/_livrables/reporting/[AAAA-MM]/. UTILISER des qu'on mentionne :
  "rapport concurrence", "analyse concurrentielle", "comparaison concurrents", "part de voix",
  "share of voice", "ou nous devancent les concurrents", "competitor report", ou le nom d'un client
  Suisseo suivi de "concurrence"/"concurrents". C'est le rapport CONCURRENCE. Pour la performance des
  positions du client seul, utiliser tn-seo-rapport-positions ; pour les opportunites a capter,
  tn-seo-rapport-opportunites.
---

> Modèles : chercher `_templates/` dans le dossier de travail, puis dans `~/.claude/tn-seo/_templates/`, puis dans `../../_templates/` à partir du dossier de ce skill. Le dossier retenu est aussi la `<racine Suisseo>` à passer aux scripts. Si un fichier manque partout, utiliser le skill `maj-templates` au lieu d'inventer la charte ou le logo.

# Rapport concurrence (Suisseo, SE Ranking)

Compare le client a 3 concurrents sur les mots-cles suivis. Deux livrables : un Word de synthese et
un Excel de donnees. Rien d'invente : tout vient de SE Ranking.

## Principes

- `PROJECT_getKeywordStats` et `PROJECT_getCompetitorPositions` renvoient un **volume enorme**
  sauvegarde dans un fichier par le MCP. Ne jamais lire ces fichiers en contexte : recuperer les
  chemins et les passer aux scripts.
- Un seul moteur de recherche par projet (le Google principal). Les scripts le choisissent.
- La part de voix (`getAllCompetitorsMetrics`) n'est historisee que ~14 jours : c'est un instantane du
  mois courant. La comparaison M-2/M-1/M des concurrents vient de getCompetitorPositions.
- Charte et nommage Suisseo. Ne jamais supprimer ; archiver dans `_archive/`.

## Avant de produire : lire les references

1. `references/seranking_protocol.md` : appels MCP, parametres, pieges.
2. `_templates/charte_graphique.md` (racine Suisseo).

## Workflow

1. **Resoudre le projet** : `PROJECT_listProjects`, matcher le client (un projet par langue si multi).
2. **Dates** : `PROJECT_getHistoricalDates` -> `current`. Trois mois calendaires (M, M-1, M-2),
   fenetres de 7 jours en fin de periode pour les keyword stats.
3. **Client** :
   - `PROJECT_getKeywordStats` x3 (M, M-1, M-2) avec `with_landing_pages=1` -> chemins.
   - `PROJECT_getPositionHistory` type=`top10` sur [1er jour M-2 .. aujourd'hui] -> .json (sert a la
     courbe comparee cote client ; visibility_percent et avg_pos facultatifs).
4. **Concurrents** :
   - Resolution, dans l'ordre : (a) concurrents deja documentes dans le dossier client (anciens
     Competitor Report, brief, strategie) ; (b) sinon `PROJECT_listCompetitors` croise avec
     `PROJECT_getAllCompetitorsMetrics` -> les 3 a la plus forte part de voix. Annoncer le choix.
   - `PROJECT_getCompetitorPositions` (un appel par concurrent) sur [1er jour M-2 .. aujourd'hui] ->
     chemins.
   - `PROJECT_getAllCompetitorsMetrics` (date courante) -> .json (part de voix instantanee).
5. **Construire** :

   ```bash
   python3 scripts/prepare_data.py --kw-current <M> --kw-prev <M-1> --kw-prev2 <M-2> \
     --hist-top10 <top10.json> --meta meta.json --out report_data.json
   python3 scripts/prepare_competitors.py --data report_data.json \
     --comp "Concurrent A|www.concurrent-a.ch|<comp1>" \
     --comp "Concurrent B|www.concurrent-b.ch|<comp2>" \
     --comp "Concurrent C|www.concurrent-c.ch|<comp3>" \
     --sov <getAllCompetitorsMetrics> --client-domain www.exemple.ch
   python3 scripts/build_competition_xlsx.py --data report_data.json --out <sortie>.xlsx
   python3 scripts/build_competition_docx.py --data report_data.json --out <sortie>.docx \
     --logo "<racine Suisseo>/_templates/assets/logo_suisseo_dark.png"
   ```

   Note : prepare_data.py accepte des series hebdo absentes (passer au moins --hist-top10). Le
   comparatif a besoin des keyword stats client (M/M-1/M-2) pour les metriques mensuelles du client.
6. **Ranger** : `[Client]/_livrables/reporting/[AAAA-MM]/`, noms
   `Rapport_Concurrence_[Client]_[AAAA-MM].xlsx/.docx`. Archiver avant regeneration.

## Verification finale

- Excel : 4 onglets (Part de voix, Comparatif, Evolution hebdo avec graphe natif compare, Face a
  face avec position par mot-cle client vs concurrents).
- Word : page de garde avec logo, part de voix + rang du client, comparatif des positions, liste des
  mots-cles ou les concurrents devancent le client.
- 3 concurrents bien identifies et coherents. Rangement et archivage faits.

## Notes

- Consultant : Thomas Nedjar. Charte : titres #2B3A4E, accent vert #95C11F, pas d'emojis.
- Face a face : vert = le client est le mieux place, rouge = au moins un concurrent devance le client.
