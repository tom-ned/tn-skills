# Skill maquette-pixel

Recette Suisseo pour produire des maquettes HTML pixel-pres pour les clients.

## Installation

Copier ce dossier dans le skills folder de Claude :
```
[skills_folder]/maquette-pixel/
  SKILL.md
  README.md
  qa_checklist.md
  templates/
    head_template.html
    body_template.html
    footer_suisseo.html
  scripts/
    extract_header.py
    build_page.py
    config_example.json
```

## Usage manuel rapide

```bash
# 1. Extraire le header client
python scripts/extract_header.py https://www.client.com/example-product ./extracted/

# 2. Editer config.json (copier config_example.json et adapter)

# 3. Assembler la page
python scripts/build_page.py config.json maquette_page.html

# 4. Verifier
# Voir qa_checklist.md
```

## Patch a appliquer dans opti-site/SKILL.md

Ajouter en haut du SKILL.md de opti-site, apres la section "Contexte" :

```
## Voir aussi : skill maquette-pixel

Pour produire les maquettes HTML detaillees etape 3, deleguer au skill `maquette-pixel`.
Il standardise : header pixel-pres du client, body sobre SEO-friendly, footer Suisseo,
overlay Suisseo avec email thomas.nedjar@suisseo.ch.
```
