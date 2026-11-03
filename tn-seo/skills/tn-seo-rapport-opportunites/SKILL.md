---
name: tn-seo-rapport-opportunites
description: >
  Rapport d'opportunites SEO (gaps a capter) pour les clients de l'agence Suisseo, a partir des
  donnees SE Ranking (MCP). Identifie automatiquement les paliers non franchis et ou cibler l'effort :
  quick wins TOP 3 (positions 4-10), quick wins TOP 10 (positions 11-20), mots-cles page 2-3, mots-cles
  a fort volume hors radar, pages a optimiser (volume cumule mais position moyenne faible) et volume de
  recherche non capte. Produit un Word oriente action et un Excel pure data, ranges dans
  [Client]/_livrables/reporting/[AAAA-MM]/. UTILISER des qu'on mentionne : "opportunites SEO",
  "quick wins", "gaps", "mots-cles a capter", "ou cibler", "objectifs SEO", "potentiel non capte",
  "volume non capte", "ou progresser", ou le nom d'un client Suisseo suivi de "opportunites"/"quick
  wins". C'est le rapport OPPORTUNITES. Pour la performance des positions, utiliser
  tn-seo-rapport-positions ; pour la comparaison aux concurrents, tn-seo-rapport-concurrence.
---

> Modèles : chercher `_templates/` dans le dossier de travail, puis dans `~/.claude/tn-seo/_templates/`, puis dans `../../_templates/` à partir du dossier de ce skill. Le dossier retenu est aussi la `<racine Suisseo>` à passer aux scripts. Si un fichier manque partout, utiliser le skill `maj-templates` au lieu d'inventer la charte ou le logo.

# Rapport opportunites SEO (Suisseo, SE Ranking)

Montre ou se trouvent les paliers non franchis et lesquels cibler en priorite (meilleur rapport
volume/effort). Cibles deduites automatiquement de la position actuelle. Deux livrables : un Word
oriente action et un Excel de listes priorisees. Rien d'invente.

## Cibles deduites automatiquement

- Position 4-10 -> cible TOP 3 (quick win, on est juste au-dessus).
- Position 11-20 -> cible TOP 10 (haut de page 2, gros levier de trafic).
- Position 21-30 -> cible page 1.
- Position >30 ou non positionne, avec volume -> a aller chercher (contenu a moyen terme).
- Pages a optimiser : volume cumule consequent mais position moyenne faible.
- Volume non capte : somme des volumes hors TOP 10.

Tout est trie par volume de recherche decroissant (priorite trafic).

## Principes

- Partir des **vraies listes de mots-cles suivies** du projet. Ne rien inventer.
- `PROJECT_getKeywordStats` renvoie un **volume enorme** sauvegarde dans un fichier par le MCP. Ne
  jamais le lire en contexte : recuperer le chemin et le passer aux scripts.
- Un seul moteur de recherche par projet (le Google principal). Les scripts le choisissent.
- Charte et nommage Suisseo. Ne jamais supprimer ; archiver dans `_archive/`.

## Avant de produire : lire la reference

`references/seranking_protocol.md` : appels MCP, parametres, pieges. Pour ce rapport, seuls les
keyword stats sont indispensables (l'historique hebdo n'est pas requis).

## Workflow

1. **Resoudre le projet** : `PROJECT_listProjects`, matcher le client (un par langue si multi).
2. **Dates** : `PROJECT_getHistoricalDates` -> `current`. La position actuelle suffit ; pour le diff
   de contexte, fournir aussi M-1 et M-2 si disponibles (facultatif ici).
3. **Donnees** : `PROJECT_getKeywordStats` (fenetre 7 jours fin de mois courant) avec
   `with_landing_pages=1` -> recuperer le chemin. M-1 et M-2 facultatifs (les scripts gerent leur
   absence ; passer au minimum --kw-current).
4. **Construire** :

   ```bash
   python3 scripts/prepare_data.py --kw-current <M> [--kw-prev <M-1> --kw-prev2 <M-2>] \
     --meta meta.json --out report_data.json
   python3 scripts/analyze_opportunities.py --data report_data.json
   python3 scripts/build_opportunities_xlsx.py --data report_data.json --out <sortie>.xlsx
   python3 scripts/build_opportunities_docx.py --data report_data.json --out <sortie>.docx \
     --logo "<racine Suisseo>/_templates/assets/logo_suisseo_dark.png"
   ```

   `prepare_data.py` fonctionne meme sans series hebdo ni M-1/M-2 : les opportunites se calculent sur
   la position actuelle. Fournir M-1/M-2 enrichit seulement le contexte.
5. **Ranger** : `[Client]/_livrables/reporting/[AAAA-MM]/`, noms
   `Rapport_Opportunites_[Client]_[AAAA-MM].xlsx/.docx`. Archiver avant regeneration.

## Verification finale

- Excel : Synthese (volume capte vs non capte) + 5 listes (Quick wins TOP 3, Quick wins TOP 10,
  Page 2-3, A aller chercher, Pages a optimiser), triees par volume.
- Word : synthese chiffree + listes priorisees + tableau des pages a optimiser, avec le logo Suisseo.
- Cibles coherentes avec les positions reelles. Rangement et archivage faits.

## Notes

- Consultant : Thomas Nedjar. Charte : titres #2B3A4E, accent vert #95C11F, pas d'emojis.
- Le seuil de volume des pages a optimiser est reglable : `--weak-page-min-volume` sur
  analyze_opportunities.py (defaut 100).
