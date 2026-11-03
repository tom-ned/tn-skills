---
name: tn-seo-rapport-positions
description: >
  Rapport SEO de performance (positions) pour les clients de l'agence Suisseo, a partir des donnees
  SE Ranking (MCP). Pour un domaine/client donne, produit un Word de synthese (charte Suisseo) et un
  Excel pure data : KPI mois en cours vs M-1 et M-2, courbes hebdomadaires natives (visibilite,
  position moyenne, TOP 10), volumes par page, mots-cles par page, et mots-cles highlight
  (progressions, fort volume, entrees/sorties TOP 3 et TOP 10). Range dans
  [Client]/_livrables/reporting/[AAAA-MM]/. UTILISER des qu'on mentionne : "rapport SEO",
  "rapport de positions", "reporting positions", "suivi de positions", "rapport mensuel SEO",
  "performance SEO du mois", ou le nom d'un client Suisseo suivi de "rapport positions"/"perf SEO".
  C'est le rapport de PERFORMANCE (positions du client). Pour la comparaison aux concurrents,
  utiliser tn-seo-rapport-concurrence ; pour les opportunites a capter, tn-seo-rapport-opportunites.
---

> Modèles : chercher `_templates/` dans le dossier de travail, puis dans `~/.claude/tn-seo/_templates/`, puis dans `../../_templates/` à partir du dossier de ce skill. Le dossier retenu est aussi la `<racine Suisseo>` à passer aux scripts. Si un fichier manque partout, utiliser le skill `maj-templates` au lieu d'inventer la charte ou le logo.

# Rapport SEO de positions (Suisseo, SE Ranking)

Transforme les positions suivies dans SE Ranking en deux livrables factuels : un Word de synthese et
un Excel de donnees, mois en cours vs M-1 vs M-2. Pas de remplissage, pas de chiffres inventes.

## Principes

- Partir des **vraies listes de mots-cles suivies** du projet. Ne rien inventer. Parcourir tous les
  mots-cles.
- `PROJECT_getKeywordStats` renvoie un **volume enorme** sauvegarde dans un fichier par le MCP. Ne
  jamais lire ce fichier en contexte : recuperer le chemin et le passer aux scripts. C'est la regle
  qui rend le skill fiable.
- Un seul moteur de recherche par projet (le Google principal). Les scripts le choisissent seuls.
- Charte et nommage Suisseo (voir plus bas). Ne jamais supprimer ; archiver dans `_archive/`.

## Avant de produire : lire les references

1. `references/seranking_protocol.md` : sequence d'appels MCP, parametres, pieges (sortie volumineuse,
   choix du moteur, dates). A lire integralement.
2. `references/report_structure.md` : contenu attendu de chaque onglet et section.
3. `_templates/charte_graphique.md` (racine Suisseo) : couleurs et polices. Deja appliquees dans les
   scripts.

## Workflow

1. **Resoudre le projet** : `PROJECT_listProjects`, matcher le client. Variantes de langue = un couple
   de livrables par langue (suffixe de langue). Doublons techniques = projet actif le plus complet.
2. **Dates** : `PROJECT_getHistoricalDates` donne `current`. Trois mois calendaires (M, M-1, M-2),
   fenetre de 7 jours en fin de chaque periode.
3. **Donnees** (voir parametres exacts dans la reference) :
   - `PROJECT_getKeywordStats` x3 (M, M-1, M-2) avec `with_landing_pages=1` -> recuperer les chemins.
   - `PROJECT_getPositionHistory` x3 : `visibility_percent`, `avg_pos`, `top10` sur [1er jour M-2 ..
     aujourd'hui] -> ecrire chaque reponse en .json.
   - `PROJECT_getSummary` (optionnel).
4. **Construire** : meta.json puis

   ```bash
   python3 scripts/prepare_data.py --kw-current <M> --kw-prev <M-1> --kw-prev2 <M-2> \
     --hist-vis <vis.json> --hist-avgpos <avgpos.json> --hist-top10 <top10.json> \
     --meta meta.json --out report_data.json
   python3 scripts/build_xlsx.py --data report_data.json --out <sortie>.xlsx
   python3 scripts/build_docx.py --data report_data.json --out <sortie>.docx \
     --logo "<racine Suisseo>/_templates/assets/logo_suisseo_dark.png"
   ```

5. **Continuite** : lire le rapport du mois precedent dans
   `[Client]/_livrables/reporting/[AAAA-(MM-1)]/` pour le fil narratif (les chiffres viennent de SE
   Ranking, pas du fichier).
6. **Ranger** : `[Client]/_livrables/reporting/[AAAA-MM]/`, noms
   `Reporting_SEO_[Client]_[AAAA-MM].xlsx/.docx` (suffixe de langue si multi). Archiver un fichier de
   meme nom dans `[AAAA-MM]/_archive/` avant regeneration.

## Verification finale

- Excel : 5 onglets (Synthese, Evolution hebdo avec 3 graphes natifs, Mots cles complet, Par page,
  Highlights). Nombre de mots-cles coherent avec le projet.
- Word : page de garde avec logo, tableau KPI M-2/M-1/M, listes highlight, tableau des pages.
- Client, domaine, periode corrects partout. Rangement et archivage faits.

## Notes

- Consultant : Thomas Nedjar. Charte : titres #2B3A4E, accent vert #95C11F, pas d'emojis.
- "gain" = amelioration de position (le chiffre baisse), affiche "+N places".
- Le calcul lourd est dans les scripts ; le role du modele est d'orchestrer les appels MCP et de
  ranger les livrables.
