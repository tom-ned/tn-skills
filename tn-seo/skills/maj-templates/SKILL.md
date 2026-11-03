---
name: maj-templates
description: Vérifie, cherche et met à jour les modèles Suisseo (charte graphique, logo, spécifications d'audit) utilisés par les skills tn-seo. À utiliser quand un skill tn-seo ne trouve pas un fichier `_templates/`, ou quand l'utilisateur veut mettre à jour, remplacer ou retrouver ses modèles.
---

# Mise à jour des modèles

Fichiers attendus dans `_templates/` :

- `charte_graphique.md`
- `assets/logo_suisseo_dark.png`
- `skills/audit_technique_seo.md`

Emplacements, du prioritaire au dernier recours :

1. `_templates/` du dossier de travail
2. `~/.claude/tn-seo/_templates/` : copie personnelle, conservée quand le plugin change
3. `../../_templates/` à partir du dossier de ce skill : version livrée avec le plugin, parfois ancienne

## Déroulé

1. Afficher un tableau : chaque fichier, l'emplacement où il est trouvé, sa date de modification.
2. Si un fichier manque ou si l'utilisateur veut le changer, chercher ce nom de fichier dans son dossier personnel (Bureau, Documents, Téléchargements, OneDrive), sans `node_modules`.
3. Poser la question avec l'outil de question interactive, en proposant :
   - chaque dossier trouvé, avec la date de ses fichiers
   - indiquer un autre dossier
   - garder les modèles du plugin
   - continuer sans le fichier manquant
4. Après le choix d'un dossier, copier seulement les trois fichiers attendus vers `~/.claude/tn-seo/_templates/`, en créant les dossiers. Si un fichier y existe déjà et diffère, montrer les deux dates et faire confirmer le remplacement.
5. Réafficher le tableau et reprendre le skill qui avait besoin du modèle.

Sans accès aux fichiers de l'ordinateur (Chat sur claude.ai) : demander à l'utilisateur de joindre le fichier à la conversation et l'utiliser pour cette conversation seulement, car il ne sera pas conservé.

Ne jamais inventer une charte ni un logo pour combler un manque.
