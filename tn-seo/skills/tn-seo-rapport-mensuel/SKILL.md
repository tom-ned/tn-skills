---
name: tn-seo-rapport-mensuel
description: >-
  Rapport SEO mensuel client (Suisseo) a partir des donnees REELLES du compte SEO Cartograph
  (Search Console, GA4, rank tracker, crawl). Produit UN SEUL Word de synthese et UN SEUL Excel
  de donnees, quel que soit le nombre de langues du site : les versions linguistiques sont des
  sections du rapport, pas des fichiers separes. Commence TOUJOURS par un QCM de qualification
  (client, objectif, langues, marche, marque, mois). UTILISER des qu'on demande : "rapport
  mensuel", "reporting mensuel", "le rapport du mois", "reporting client", "fais le rapport pour
  [client]", "bilan SEO mensuel", ou le nom d'un client suivi de "rapport". Ne pas confondre avec
  l'audit technique (tn-seo-audit-technique) ni l'optimisation de site (tn-seo-opti-site).
---

> Modèles : chercher `_templates/` dans le dossier de travail, puis dans `~/.claude/tn-seo/_templates/`, puis dans `../../_templates/` à partir du dossier de ce skill. Le dossier retenu est aussi la `<racine Suisseo>` à passer aux scripts. Si un fichier manque partout, utiliser le skill `maj-templates` au lieu d'inventer la charte ou le logo.

# Rapport SEO mensuel

Un livrable client qui repond a une question simple : est-ce que le travail avance, et que
fait-on le mois prochain. Deux fichiers, quel que soit le nombre de langues.

- `Reporting_SEO_[Client]_[AAAA-MM].docx` : la lecture, 6 a 8 pages.
- `Reporting_SEO_[Client]_[AAAA-MM].xlsx` : la donnee complete et verifiable.

Aucun chiffre invente. Une couche de donnees absente est ecrite comme absente.

---

## Etape 0 : QCM de qualification (obligatoire)

Avant tout appel de donnees, poser en une fois, via AskUserQuestion :

1. **Client et domaine.** Si ambigu, lister les domaines de `list_crawl_sites`.
2. **Objectif du site**, en clair, decide avec le client : recruter, credibilite
   institutionnelle, vendre, collecter des dons, sensibiliser. C'est ce qui rend le rapport
   pertinent. Sans objectif, aucun chiffre n'est bon ni mauvais et le rapport devient un bulletin
   meteo. Si le client n'en a pas formule, le dire dans le rapport plutot que d'en inventer un.
3. **Langues** a traiter (multi-select). Elles deviennent des sections d'un rapport unique.
4. **Marche prioritaire** (Suisse, France, DACH, monde).
5. **Termes de marque** a exclure de l'analyse non-marque.
6. **Mois de reference**, par defaut le dernier mois calendaire COMPLET. Ne jamais melanger un
   mois partiel a des mois complets dans une meme serie.
7. **Concurrents** (0 a 4), optionnel, coute des credits SERP.

---

## Les cinq regles qui font la difference

Elles viennent de rapports refuses. Les respecter evite de refaire le travail trois fois.

### 1. Le non-marque est la mesure du SEO

Sur un site installe, 80 a 90 % des clics viennent du nom de la marque. Ces clics sont produits
par la notoriete, la presse, les mailings, pas par le referencement. Mettre le total en titre
revient a feliciter ou accabler le SEO pour un travail fait ailleurs.

Le chiffre d'ouverture est donc le trafic non-marque et son evolution. La marque figure comme
ligne de contexte, sous l'etiquette notoriete.

### 2. Comparer au meme mois de l'annee precedente, toujours

La plupart des sites sont saisonniers. Un rapport sur trois mois glissants presentera un creux
d'ete comme un decrochage structurel. Avant d'ecrire la moindre phrase de tendance, recuperer le
meme mois l'annee precedente (`explore_search_console` dimension=date, un appel) et le comparer.

Si le mois est en baisse sur M-1 mais en hausse sur N-1, la phrase juste est « creux saisonnier,
site en avance sur son historique », pas « le trafic s'effondre ».

### 3. Un graphique se juge au nombre de points

- Moins de 12 points : **jamais de courbe**. Trois points ne font pas une tendance, ils font
  trois points relies par des segments. Utiliser un tableau ou des barres.
- Serie de 30 a 120 jours : **donnee quotidienne + moyenne mobile 7 jours**. Le trait clair donne
  l'amplitude reelle, le trait epais la tendance. C'est ce qui distingue un graphique vivant d'un
  graphique plat.
- Ne jamais tracer la **position moyenne agregee** d'un site ou d'un pays : elle bouge quand le
  mix de requetes bouge, pas quand les classements bougent. C'est la metrique la plus mal lue de
  Search Console. La position se lit par mot-cle suivi, dans le rank tracker.
- Deux mesures d'unites differentes ne partagent jamais un axe. Deux graphiques, ou un indice
  base 100.
- Detail complet dans `references/regles_graphiques.md`.

### 4. Les recommandations sont editoriales

Un client final ne commandera pas une redirection ni un correctif de canonical a partir d'un
rapport mensuel. Les trois actions du mois sont des **sujets a ecrire**, tires des recherches que
les internautes font deja et sur lesquelles le site apparait sans etre choisi.

Le volet technique existe, mais il tient dans une section courte, formulee en termes de contenu
(« ces pages sont vides », « la moitie du site est absente du sitemap, ce qui retarde la prise en
compte des nouveaux articles »), et il ne prend jamais la place des sujets.

Proposer le potentiel **dans chaque langue du site**, pas seulement dans la plus grosse.

### 5. Verifier le rendu, pas seulement les chiffres

Avant de livrer : convertir le Word en PDF (`soffice --headless --convert-to pdf`), le
transformer en images (`pdftoppm -png -r 75`) et REGARDER chaque page. C'est ce qui fait
apparaitre les legendes orphelines, les etiquettes tronquees, les colonnes ecrasees et les
tableaux coupes. Le controle des chiffres ne remplace pas le controle visuel.

---

## Avant de produire : lire les references

1. `references/cartograph_protocol.md` : sequence exacte d'appels, parametres, pieges.
2. `references/report_structure.md` : contenu attendu de chaque section et de chaque onglet.
3. `references/regles_graphiques.md` : regles de visualisation et palette validee.

---

## Chaine de production

```bash
# 1. Un prepare_data par langue (le prefixe filtre les pages)
python3 scripts/prepare_data.py --meta meta_fr.json \
  --gsc-query-m gsc_query_M.json --gsc-query-m1 gsc_query_M1.json --gsc-query-m2 gsc_query_M2.json \
  --gsc-page gsc_page.json --gsc-country gsc_country.json --gsc-date gsc_date.json \
  --ga4-channels ga4_channels.json --ga4-landing ga4_landing_fr.json \
  --opportunities opportunities.json --crawl crawl_overview.json \
  --out report_data_fr.json
# (idem pour chaque langue)

# 2. Fusion en UN SEUL jeu de donnees
python3 scripts/merge_langues.py --base report_data_fr.json \
  --langue fr:Francais:/fr/:report_data_fr.json \
  --langue en:Anglais:/en/:report_data_en.json \
  --gsc-page gsc_page.json --gsc-date gsc_date.json --ga4-landing ga4_landing.json \
  --out report_data_global.json

# 3. Potentiel par langue et matiere des sujets
python3 scripts/analyse_potentiel.py --gsc-query-m gsc_query_M.json \
  --brand "marque,variante" --langues fr,en,de \
  --out-potentiel potentiel_langues.json --out-sujets sujets_candidats.json

# 4. Injecter potentiel + sujets rediges + lecture + actions dans report_data_global.json
#    (voir _templates/meta_exemple.json pour les champs attendus)

# 5. Livrables
python3 scripts/build_report.py --data report_data_global.json \
  --out Reporting_SEO_[Client]_[AAAA-MM].docx --logo <racine>/_templates/assets/logo_suisseo_dark.png
python3 scripts/build_xlsx.py --data report_data_global.json \
  --out Reporting_SEO_[Client]_[AAAA-MM].xlsx
```

`analyse_potentiel.py` sort des groupes de requetes avec leur cumul d'impressions et un champ
`titre` vide : **le titre editorial se redige a la main**, c'est le seul endroit du processus ou
le jugement humain ne se remplace pas. Un bon sujet regroupe plusieurs formulations d'une meme
question : un seul article les couvre toutes.

---

## Champs de meta a remplir

Voir `_templates/meta_exemple.json`. Les champs qui portent l'analyse et qui ne se calculent
pas : `objectif`, `lecture` (2 a 3 paragraphes de synthese), `sujets` (titres editoriaux),
`actions` (les trois priorites), `crawl_prios`, `crawl_constat`, `a_instruire`.

---

## Verification finale

- Un seul Word, un seul Excel, correctement nommes et ranges dans
  `[Client]/_livrables/reporting/[AAAA-MM]/`. Version precedente archivee dans `_archive/`.
- Aucun mois partiel melange a des mois complets.
- Comparaison N-1 presente des qu'une tendance est commentee.
- Aucune courbe de moins de 12 points, aucune courbe de position moyenne agregee.
- Les trois actions sont des sujets a ecrire, pas des correctifs techniques.
- Le potentiel est propose dans chaque langue traitee.
- Chiffres au format francais : virgule decimale, espace fine pour les milliers, espace avant le
  signe pourcent.
- Rendu PDF relu page par page.
- Toute couche absente signalee explicitement.

## Notes

- Consultant : Thomas Nedjar. Charte : titres #2B3A4E, accent vert #95C11F, texte #333333,
  Calibri. Pas d'emojis, pas de tirets cadratins.
- Series de graphiques : #2F6FB2, #7FA817, #A4568C, palette validee (contraste, daltonisme).
  Les couleurs de marque restent sur les titres et le texte.
- « gain » de position = le chiffre baisse. Ecrire « 2 places gagnees », jamais « -2 ».
- Ne JAMAIS comparer une position serp a une position gsc.
