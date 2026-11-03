# Protocole de recuperation des donnees SE Ranking (MCP)

Tous les outils sont prefixes par le serveur MCP SE Ranking (`PROJECT_*`). Les `site_id` ci-dessous
sont des exemples ; toujours les resoudre via `PROJECT_listProjects`.

## 1. Resolution du projet

`PROJECT_listProjects` -> liste de projets `{id, title, name (domaine), is_active, keyword_count}`.
- Matcher le client par `title`/`name`.
- Garder les projets `is_active = 1`.
- Variantes de langue = un projet par langue (ex : `exemple.ch - FR`, `exemple.ch - DE`, `exemple.ch - EN`).
- Doublons techniques memes langue/domaine = garder le `keyword_count` le plus eleve.

## 2. Dates

`PROJECT_getHistoricalDates` (site_id) -> `{first, 30days, 90days, current, ...}`.
- `current` = date du jour analysable.
- Calculer les mois calendaires M, M-1, M-2 a partir de `current`.
- Fenetres a passer aux appels keyword stats (7 jours) :
  - M    : du (current - 6 jours) a current
  - M-1  : les 7 derniers jours du mois M-1 (ex mois M-1 = mai -> 2026-05-25 a 2026-05-31)
  - M-2  : les 7 derniers jours du mois M-2
- Si besoin de confirmer qu'un check existe : `PROJECT_getCheckDates` (date_from, date_to).

## 3. Mots-cles + positions + pages (le gros morceau)

`PROJECT_getKeywordStats` :
- Parametres : `site_id`, `date_from`, `date_to` (la fenetre 7 jours), `with_landing_pages = "1"`.
- Ne PAS filtrer par `in_top` : on veut tous les mots-cles.
- Sortie : par moteur (`site_engine_id`) puis `keywords[]`. Chaque mot-cle :
  `{id, name, volume, competition, cpc, results, landing_pages:[{url,...}], positions:[{date,pos,change}]}`.
- **La sortie depasse la limite de tokens et est sauvegardee dans un fichier .txt par le MCP.**
  Recuperer le chemin affiche ("Output has been saved to ...") et le passer tel quel au script.
  Ne jamais demander a lire ce fichier en entier.
- Faire 3 appels : un par fenetre (M, M-1, M-2). Noter les 3 chemins.

Choix du moteur : les scripts retiennent automatiquement le moteur avec le plus de mots-cles
(en general le Google principal). Pour forcer, passer `--engine-id <site_engine_id>` a prepare_data.py
ou mettre `engine_id` dans meta.json. Renseigner `engine_label` dans meta.json pour l'affichage
(ex "Google Switzerland").

## 4. Courbes hebdomadaires

`PROJECT_getPositionHistory` :
- Parametres : `site_id`, `date_from` = 1er jour de M-2, `date_to` = current, `type`.
- Trois appels : `type="visibility_percent"`, `type="avg_pos"`, `type="top10"`.
- Sortie : une serie par moteur + une serie `{"name":"Average for all","type":"avg"}`. Les scripts
  utilisent la serie "Average for all" et reechantillonnent en hebdomadaire (derniere valeur de
  chaque semaine ISO).
- Si la reponse revient inline (souvent le cas, ~90 points), l'ecrire dans un fichier .json du
  dossier de travail avant de la passer au script. Si elle est sauvegardee par le MCP, prendre le chemin.

## 5. Complement (optionnel)

`PROJECT_getSummary` (site_id) -> `{today_avg, top5, top10, top30, visibility, visibility_percent,
index_google, domain_trust}`. Utile pour un chiffre de contexte (autorite, pages indexees). Non requis.

## meta.json a construire

```json
{
  "client": "Client X",
  "domain": "www.exemple.ch",
  "project_id": 123456,
  "engine_id": 654321,
  "engine_label": "Google Switzerland",
  "period_current": "2026-06",
  "period_prev": "2026-05",
  "period_prev2": "2026-04",
  "date_current": "2026-06-26",
  "date_prev": "2026-05-31",
  "date_prev2": "2026-04-30",
  "consultant": "Thomas Nedjar",
  "generated_at": "2026-06-26"
}
```

## Pieges a eviter

- Lire un fichier getKeywordStats en entier dans le contexte : interdit, ca sature le contexte.
- Additionner les volumes sur plusieurs moteurs : fausse les volumes par page. Un seul moteur.
- Confondre "gain" et signe du delta : delta negatif (la position baisse) = progression.
- Inventer des positions pour des mots-cles non checkes : laisser None, les scripts affichent ">100".
