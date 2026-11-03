# Protocole d'appels Cartograph

Toutes les donnees viennent du MCP SEO Cartograph, en lecture seule. Ecrire chaque reponse
volumineuse dans un fichier `.json` et passer le CHEMIN aux scripts. Ne jamais charger ces
sorties en contexte : c'est la regle qui rend la production fiable et rapide.

## Fenetres de dates

- Mois de reference M = dernier mois calendaire COMPLET. Comparaisons M-1 et M-2.
- **Meme mois de l'annee precedente : obligatoire.** Un appel `dimension=date` sur ce mois
  suffit. Sans lui, un creux saisonnier sera presente comme un decrochage.
- Search Console couvre environ 16 mois, fraicheur J-2 ou J-3. GA4 fraicheur J-1.
- Ne jamais melanger un mois partiel a des mois complets dans une meme serie. Si le mois en
  cours doit figurer, le distinguer visuellement et l'ecrire.

## 1. Resolution de la propriete

- `list_crawl_sites` : confirme le domaine exact et donne `last_run_id`. Le domaine renvoye ici
  est celui a passer partout.
- `explore_search_console` `dimension=language` sur M : verifie les langues reellement presentes
  (prefixes d'URL). Ne retenir que les langues cochees au QCM ET presentes ici.
- Si le domaine n'apparait pas dans `list_crawl_sites` mais que Search Console repond, la
  propriete existe sans crawl : la section hygiene sera vide, l'ecrire.
- Un projet peut exister sous une autre forme du domaine (avec ou sans `www`) et ne pas etre
  partage avec le compte. Le message d'erreur le dit ; le signaler plutot que de conclure a
  l'absence de donnees.

## 2. Search Console

`summary=false` pour avoir toutes les lignes, `limit` 1000 a 5000.

- `dimension=query` sur M, M-1, M-2 -> `gsc_query_M.json`, `_M1`, `_M2`
- `dimension=page` sur M -> `gsc_page.json` (non filtre : le filtrage par langue se fait ensuite
  sur le prefixe, cote script)
- `dimension=country` sur M, M-1, M-2 -> `gsc_country.json` (cle = ISO3 : che, deu, fra, usa)
- `dimension=date` du 1er de M-2 a la fin de M -> `gsc_date.json`. C'est la serie quotidienne qui
  alimente les courbes ; c'est aussi la seule source coherente pour les KPI du site sur
  plusieurs mois.
- `dimension=date` sur le meme mois l'annee precedente -> comparaison N-1.
- `dimension=language`, un appel par mois, si l'evolution par langue doit etre tracee.

Format d'une ligne query ou page : `key`, `clicks`, `impressions`, `ctr`, `position`,
`active_30d`, `trend_pct`, `status`. Le statut separe une requete vivante d'un fantome.

Attention : les totaux de la dimension `query` sont inferieurs a ceux de la dimension `date`
(anonymisation des requetes rares). Les deux sont justes, ils ne mesurent pas la meme chose. Ne
jamais les additionner ni les comparer directement.

## 3. GA4

- `explore_analytics` `dimension=sessionDefaultChannelGroup` sur M -> `ga4_channels.json`
- `explore_analytics` `dimension=landingPage`, `filter_dimension=sessionDefaultChannelGroup`,
  `filter_value="Organic Search"` -> `ga4_landing.json`

Piege : le canal Direct est souvent enorme et a fort rebond. Il sert de contexte, jamais
d'indicateur de performance SEO.

## 4. Rank tracker

`get_tracked_positions` `include_history=true` sur M -> `tracked_positions.json`.

`position_source` dit toujours d'ou sort le chiffre : `serp` (releve exact) ou `gsc` (moyenne
Search Console). Ne JAMAIS comparer une position `serp` a une position `gsc`. `delta_period` est
deja calcule a provenance egale.

Si aucun mot-cle n'est suivi, poser le suivi vaut mieux que de s'en passer : sans lui, les
positions ne sont pas comparables d'un mois sur l'autre. `track_keywords` avec `enriched=false`
est gratuit et ne consomme aucun credit. Ranger les mots-cles en groupes qui correspondent aux
objectifs du client, pas aux rubriques du site.

## 5. Opportunites

`get_opportunities` `locale=<marche>` -> `opportunities.json`.

Piege majeur : quand `tracked_enriched_count = 0`, `opportunities[]` est VIDE et volume, CPC et
valeur sont nuls. Dans ce cas `prepare_data.py` bascule automatiquement sur un repli calcule
depuis les requetes Search Console.

Ce repli trie par impressions. **Il ne sait pas si une requete sert l'objectif du client.** Une
requete de dictionnaire a fort volume remontera en tete alors qu'elle n'amenera ni client ni
candidat ni donateur. Filtrer par intention avant de proposer, en s'appuyant sur l'objectif
recueilli au QCM.

## 6. Crawl

`get_crawl_overview` `run_id=<last_run_id>` -> `crawl_overview.json`.

Le crawl tourne sur la machine du client via l'application desktop, pas sur le serveur : une
demande peut mettre des heures a revenir.

Avant de conclure d'un compteur d'erreurs, verifier a quelles pages il correspond :
`list_crawl_pages` avec `issue=<typologie>`. Un compteur de 208 meta descriptions manquantes qui
porte sur des archives sans trafic ne raconte pas la meme histoire qu'un compteur equivalent sur
les pages positionnees. Ouvrir aussi `get_page_details` sur deux ou trois pages qui portent le
trafic : c'est ce qui evite de recommander un chantier de balises sur des pages deja
irreprochables.

## 7. Concurrence (optionnel, coute des credits SERP)

`get_serp` sur 3 a 8 requetes non-marque cles, une reponse par fichier dans `serp/`. C'est une
photo a l'instant T, pas un suivi historique, et le rapport doit l'ecrire ainsi.

## Ordre economique des appels

1 `list_crawl_sites`, 1 `dimension=language`, puis : 3 `query` + 1 `page` + 3 `country` +
1 `date` sur trois mois + 1 `date` sur le mois N-1, 2 GA4, 1 `tracked_positions`,
1 `opportunities`, 1 `crawl_overview`, 0 a 8 `serp`. Regrouper les appels independants. Ne pas
relancer un crawl sauf demande explicite.
