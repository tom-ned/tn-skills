---
name: tn-seo-audit-technique
description: >
  Audit SEO technique complet pour les clients de l'agence Suisseo (Lausanne).
  Produit un fichier Excel d'agregation de donnees et un document Word (.docx) professionnel
  avec formatage Suisseo (logo, charte graphique, encadres pedagogiques, cotation etoiles).
  UTILISER CE SKILL des qu'on mentionne : "audit technique", "audit SEO", "audit seo technique",
  "lancer un audit", "generer l'audit", ou le nom d'un client Suisseo suivi de "audit".
  Meme si la demande est courte ou informelle ("audit technique pour [client]"), ce skill doit
  se declencher. Ne pas poser de questions sur le type d'audit ou le format attendu : c'est
  toujours un audit SEO technique Suisseo en 2 etapes (Excel + Word).
---

> Modèles : chercher `_templates/` dans le dossier de travail, puis dans `~/.claude/tn-seo/_templates/`, puis dans `../../_templates/` à partir du dossier de ce skill. Le dossier retenu est aussi la `<racine Suisseo>` à passer aux scripts. Si un fichier manque partout, utiliser le skill `maj-templates` au lieu d'inventer la charte ou le logo.

# Audit SEO Technique Suisseo

## Premiere chose a faire : choix du mode

Avant toute action, poser UNE question a l'utilisateur :

**"Mode package ou mode agile ?"**

- **Package** : audit complet et formate. Livrables : Excel d'agregation + Word professionnel avec charte Suisseo (logo, encadres, etoiles, header/footer). Tout est cadre, les specs visuelles sont appliquees strictement.
- **Agile** : on avance etape par etape. Livrables minimum : Excel d'agregation + brief Markdown avec les constats principaux. Le reste se decide dans la conversation.

Si l'utilisateur ne repond pas clairement ou dit juste "audit pour [client]", partir en **package** par defaut.

---

## Mode Package

### Premiere etape : lire les specs

1. `_templates/skills/audit_technique_seo.md` : specifications completes du workflow, de la structure, et du formatage docx-js. C'est le document de reference. Le lire integralement avant de produire quoi que ce soit.
2. `_templates/charte_graphique.md` : couleurs, polices et conventions visuelles Suisseo.

### Workflow

**Etape 1 : Excel d'agregation**

- Localiser les CSV Screaming Frog dans `[client]/_sources/screaming_frog/`
- Identifier le domaine du client depuis les CSV
- Collecter les donnees PageSpeed et W3C via Chrome (en live, ne pas inventer)
- Generer un Excel structure avec openpyxl ou le skill xlsx
- Deposer dans `[client]/_livrables/audit_technique/`

**Etape 2 : Document Word**

- Lire l'Excel de l'etape 1
- Generer un .docx avec docx-js (Node.js, `npm install -g docx`)
- Appliquer les specs de formatage du fichier de reference (docDefaults Calibri, helpers, couleurs, logo embarque, encadres, etoiles, header/footer)
- Deposer dans `[client]/_livrables/audit_technique/`

### Points critiques (mode package)

- Toujours lire les specs dans `_templates/skills/audit_technique_seo.md` AVANT de generer quoi que ce soit
- Ne jamais copier des donnees d'un autre client
- Ne jamais inventer de scores PageSpeed ou W3C : les collecter via Chrome
- Le logo Suisseo est dans `_templates/assets/logo_suisseo_dark.png` : l'embarquer dans le docx, jamais ecrire "[LOGO]" en texte
- Le nom du consultant est Thomas Nedjar
- Le nom du client doit etre correct partout (couverture, header, introduction, conclusion)
- Les specs docx-js du fichier de reference (palette, docDefaults, helpers, infoBox, makeTable, starsStr, header/footer) sont OBLIGATOIRES pour la coherence visuelle

---

## Mode Agile

### Premiere etape : lire les bases

1. `_templates/charte_graphique.md` : pour que les couleurs et polices Suisseo soient respectees meme en mode libre.
2. `_templates/skills/audit_technique_seo.md` : parcourir les sections "Sources de donnees" et "Cotation etoiles" comme reference, sans obligation de suivre toute la structure.

### Workflow

**Etape 1 : Excel d'agregation** (obligatoire)

Meme logique que le mode package : CSV Screaming Frog + PageSpeed + W3C via Chrome. L'Excel est toujours produit comme base factuelle.

**Etape 2 : Brief Markdown** (minimum)

Un fichier Markdown avec :
- Synthese des constats principaux (5-10 points)
- Tableau des actions priorisees (avec cotation etoiles)
- Recommandations cles

Le brief est depose dans `[client]/_livrables/audit_technique/`.

Si l'utilisateur demande ensuite un Word formate, basculer sur les specs du mode package pour l'etape Word.

### Points critiques (mode agile)

- L'Excel est toujours produit, pas negociable
- Les donnees PageSpeed/W3C sont toujours collectees en live
- Le brief doit etre factuel et chiffre, pas un survol
- Si l'utilisateur demande plus, on peut toujours passer en mode package pour le Word
