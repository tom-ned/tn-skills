# Deploiement sur un nouveau client

1. Copier `meta_exemple.json` en `meta_[langue].json`, un par langue, et remplir les crochets.
   Le `perimeter_prefix` change a chaque langue, le reste est commun.
2. Collecter les donnees Cartograph selon `references/cartograph_protocol.md`, un fichier .json
   par appel. Ne jamais charger ces sorties en contexte : passer les CHEMINS aux scripts.
3. Derouler la chaine decrite dans SKILL.md : prepare_data par langue, merge_langues,
   analyse_potentiel, puis build_report et build_xlsx.
4. Rediger a la main : `lecture`, les titres de `sujets`, `actions`, `crawl_prios`,
   `crawl_constat`. Le reste est calcule.
5. Relire le PDF page par page avant de livrer.

Le logo attendu par build_report.py est `--logo <racine>/_templates/assets/logo_suisseo_dark.png`.
Sans logo, la couverture se genere quand meme.
