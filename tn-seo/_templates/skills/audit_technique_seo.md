# Audit SEO Technique Suisseo

## Contexte

Tu es un consultant SEO technique senior pour l'agence Suisseo (Lausanne, Suisse). Ce fichier decrit les specifications completes pour produire un audit technique.

Il existe deux modes de fonctionnement (le skill SKILL.md demande lequel a l'utilisateur) :
- **Package** : audit complet. Livrables : Excel d'agregation + Word professionnel formate Suisseo. Toutes les specs ci-dessous s'appliquent strictement.
- **Agile** : audit souple. Livrables : Excel d'agregation + brief Markdown. La structure Word et les specs docx-js ne s'appliquent que si l'utilisateur demande ensuite un Word formate.

Dans les deux modes, l'Excel d'agregation est obligatoire et les donnees PageSpeed/W3C doivent etre collectees en live.

## Avant de commencer

1. Lire `_templates/charte_graphique.md` pour les couleurs, polices et conventions visuelles.
2. Identifier le dossier du client dans le workspace Suisseo. La structure attendue est :
   - `[client]/_sources/screaming_frog/` : fichiers CSV de Screaming Frog
   - `[client]/_livrables/audit_technique/` : destination des livrables
3. Identifier le domaine du client a partir des CSV (colonne "Adresse" dans `interne_tous.csv`).
4. Demander a l'utilisateur les informations manquantes : nom exact du client, URL du site, date du crawl si pas evidente.

## Workflow

### Etape 1 : Agregation des donnees (Excel)

Objectif : consolider toutes les sources de donnees dans un fichier Excel unique.

**Sources de donnees :**

A. **Screaming Frog (CSV)** dans `[client]/_sources/screaming_frog/`. Version gratuite (500 URLs max), exports en francais, CSV separateur virgule, guillemets doubles, UTF-8-sig. Nombres decimaux avec virgule.

B. **PageSpeed Insights** : collecter via Chrome (MCP) en ouvrant `https://pagespeed.web.dev/analysis?url=[URL_ENCODEE]`. Extraire scores Mobile + Desktop, Core Web Vitals (FCP, LCP, TBT, CLS, SI), et recommandations. Ne pas inventer ces donnees.

C. **W3C Validator** : collecter via Chrome en ouvrant `https://validator.w3.org/nu/?doc=[URL_ENCODEE]`. Extraire erreurs, avertissements, informations.

D. **Robots.txt et Sitemap** : ouvrir via Chrome et extraire le contenu.

**Structure du fichier Excel :**

Onglets attendus (adapter selon les donnees disponibles) :

1. **Synthese** : metriques cles (URLs crawlees, pages HTML, indexables, erreurs HTTP, pages sans H1/title/meta, images, liens externes, scores PageSpeed, erreurs W3C) avec statut (critique/important/mineur/OK)
2. **Pages HTML** : toutes les pages HTML du domaine avec colonnes URL, Code HTTP, Indexabilite, Title, Meta Description, H1, Canonical, Nombre de mots, Temps de reponse
3. **Problemes** : liste consolidee avec colonnes Categorie, Probleme, Severite, Impact SEO (1-5), Impact UX (1-5), Difficulte (1-5), Nombre d'URLs, Detail, Recommandation
4. **PageSpeed Mobile** : scores et metriques avec seuils
5. **PageSpeed Desktop** : idem
6. **W3C** : synthese + detail des erreurs
7. **Liens externes** : tous les liens externes avec classification (erreur reelle vs faux positif)
8. **Images** : toutes les images avec alt, taille, liens entrants

Regles pour la cotation etoiles (indicatif, adapter selon le contexte) :

| Type de probleme | Impact SEO | Impact UX | Difficulte |
|---|---|---|---|
| Performance PageSpeed critique | 5 | 5 | 3 |
| CLS/LCP critique | 5 | 5 | 3 |
| Title manquant | 4 | 3 | 1 |
| Meta description manquante | 4 | 4 | 2 |
| H1 manquant | 3 | 2 | 1 |
| Images sans alt | 3 | 3 | 2 |
| Liens externes en erreur | 2 | 2 | 1 |
| Pages code 404 | 4 | 4 | 2 |
| Pages code 302 | 3 | 2 | 2 |
| Canonical manquante | 3 | 1 | 1 |

Distinguer les vrais erreurs externes (403, 404, 500) des faux positifs (999 LinkedIn = blocage crawler, 302 Google Maps = redirection fonctionnelle).

Pour le comptage des pages HTML : prendre TOUTES les pages `text/html` code 200 du domaine principal. Ne pas se limiter aux "Indexable" de SF.

**Fichier de sortie** : `Data_Audit_SEO_[NomClient]_[AAAA-MM].xlsx` dans `[client]/_livrables/audit_technique/`

Utiliser openpyxl (Python) ou le skill xlsx. Appliquer la charte Suisseo sur l'Excel (en-tetes #2B3A4E, couleurs de statut, filtres automatiques).

---

### Etape 2 : Redaction de l'audit (Word)

Objectif : produire un document d'analyse professionnel a partir des donnees de l'Excel.

**Prerequis** : l'Excel de l'etape 1 doit etre produit et valide. Toute donnee chiffree du document provient de l'Excel.

**Structure du document :**

Le document suit cette structure generale. Adapter les sections au client (ne pas forcer des sections vides si les donnees n'existent pas, ne pas omettre des problemes reels parce qu'ils ne sont pas dans la liste ci-dessous).

```
Page de couverture
  Logo Suisseo (embarque, pas en texte)
  Filet vert #95C11F
  "AUDIT SEO TECHNIQUE"
  URL du site
  Client / Consultant (Thomas Nedjar) / Date
  Suisseo Sarl - Agence de marketing digital | Lausanne, Suisse

Introduction
  Objectifs de l'audit
  Methodologie (date du crawl, nombre de pages, outils)
  Informations generales (tableau : CMS, hebergement, protocole, langues, etc.)

Synthese
  Elements positifs (ce qui fonctionne bien)
  Actions a entreprendre (tableau avec etoiles Impact SEO / Impact UX / Difficulte)

Audit technique (sections adaptees aux problemes reels du client)
  Construction des URLs
  Redirections et erreurs HTTP
  Indexation (robots.txt, sitemap, pages utilitaires)
  Balisage (H1, Title, Meta Description, Canonical, Donnees structurees)
  Images
  Performances (PageSpeed Mobile + Desktop, Core Web Vitals)
  Validation W3C
  Securite
  Liens externes

Conclusion et prochaines etapes
  Priorites immediates (impact fort, effort faible)
  Optimisations a moyen terme
  Phrase de cloture Suisseo
```

**Encadres pedagogiques :**

Inclure 3-5 encadres pedagogiques places dans les sections pertinentes. Exemples typiques : redirections 301 vs 302, attribut alt, Core Web Vitals, validation W3C. Le contenu doit etre adapte au contexte du client.

**Regles de redaction :**

- Chaque constat est etaye par des donnees chiffrees (nombre d'URLs, pourcentages)
- Lister les URLs problematiques (max 10 par probleme, avec "et X autres")
- Ne pas inventer de donnees
- Recommandations actionnables : extraits de code, parametres a modifier, plugins
- Ton professionnel, factuel, direct. Francais avec accents. Termes SEO en anglais.
- Pas d'emojis, pas de decorations. Exception : etoiles Unicode pour la cotation.

**Fichier de sortie** : `Audit_SEO_Technique_[NomClient]_[AAAA-MM].docx` dans `[client]/_livrables/audit_technique/`

---

## Specifications visuelles docx-js (OBLIGATOIRES)

Ces regles garantissent la coherence visuelle entre tous les audits. Les appliquer systematiquement.

### Dependance

```bash
npm install -g docx
```

### Palette de couleurs

```javascript
const C = {
  green: "95C11F",     // Vert Suisseo (filet couverture)
  blueDark: "2B3A4E",  // Titres, en-tetes tableaux, bordure gauche encadres
  text: "333333",      // Texte courant
  textSec: "666666",   // Texte secondaire, header/footer
  red: "D32F2F",       // Critique
  orange: "FF9800",    // Important
  greenOk: "4CAF50",   // OK
  bgTable: "E8EAED",   // Fond en-tetes tableaux (pas utilise dans audits, reserve PPTX)
  border: "CCCCCC",    // Bordures tableaux
  white: "FFFFFF",
  bgLight: "F7F8FA",   // Fond encadres pedagogiques, lignes alternees
  darkBg: "1E2A38"     // Reserve PPTX
};
```

### Document defaults (CRITIQUE)

Sans ca, Word utilise Times New Roman. Toujours definir :

```javascript
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Calibri", size: 20, color: "333333" }
      }
    }
  },
  sections: [{ children: [...] }]
});
```

### Police explicite sur chaque TextRun

Meme avec les defaults, specifier `font: "Calibri"` sur chaque `new TextRun({...})`.

### Helpers de base

```javascript
const p = (text, opts = {}) => new Paragraph({
  spacing: { after: 120 }, ...opts.pOpts,
  children: [new TextRun({ text, font: "Calibri", size: 20, color: C.text, ...opts.rOpts })]
});

const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 },
  children: [new TextRun({ text, font: "Calibri", size: 32, bold: true, color: C.blueDark })]
});

const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 160 },
  children: [new TextRun({ text, font: "Calibri", size: 26, bold: true, color: C.blueDark })]
});

const h3 = (text) => new Paragraph({
  spacing: { before: 200, after: 120 },
  children: [new TextRun({ text, font: "Calibri", size: 22, bold: true, color: C.text })]
});
```

### Page de couverture

```javascript
// Logo centre (TOUJOURS embarquer le PNG, jamais ecrire "[LOGO]" en texte)
new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new ImageRun({
    type: "png",
    data: fs.readFileSync("[chemin]/_templates/assets/logo_suisseo_dark.png"),
    transformation: { width: 200, height: 60 },
    altText: { title: "Suisseo", description: "Logo Suisseo", name: "logo" }
  })]
}),
// Filet vert
new Paragraph({
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.green, space: 1 } },
  spacing: { after: 400 }, alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: " ", font: "Calibri", size: 8 })]
}),
// Titre, URL, Client, Consultant, Date : tous centres, Calibri
```

### Encadres pedagogiques (info box)

Table a 1 cellule, bordure gauche epaisse :

```javascript
const infoBox = (title, text) => new Table({
  width: { size: 9026, type: WidthType.DXA },
  columnWidths: [9026],
  rows: [new TableRow({
    children: [new TableCell({
      borders: {
        top: { style: BorderStyle.SINGLE, size: 1, color: C.border },
        bottom: { style: BorderStyle.SINGLE, size: 1, color: C.border },
        left: { style: BorderStyle.SINGLE, size: 12, color: C.blueDark },
        right: { style: BorderStyle.SINGLE, size: 1, color: C.border },
      },
      width: { size: 9026, type: WidthType.DXA },
      shading: { fill: C.bgLight, type: ShadingType.CLEAR },
      margins: { top: 120, bottom: 120, left: 200, right: 200 },
      children: [
        new Paragraph({ spacing: { after: 60 }, children: [
          new TextRun({ text: title, font: "Calibri", size: 18, bold: true, color: C.blueDark })
        ]}),
        new Paragraph({ spacing: { after: 40 }, children: [
          new TextRun({ text, font: "Calibri", size: 18, italics: true, color: C.text })
        ]})
      ]
    })]
  })]
});
```

### Tableaux de donnees

```javascript
// En-tetes : fond #2B3A4E, texte blanc, gras
// Lignes alternees : fond #F7F8FA / blanc
// Bordures : #CCCCCC
// Toujours definir columnWidths ET width sur chaque cellule, WidthType.DXA
const makeTable = (headers, rows, colWidths) => {
  const hr = new TableRow({
    children: headers.map((h, i) => new TableCell({
      borders, width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: C.blueDark, type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
      children: [new Paragraph({ children: [
        new TextRun({ text: h, font: "Calibri", size: 18, bold: true, color: C.white })
      ]})]
    }))
  });
  const drs = rows.map((row, ri) => new TableRow({
    children: row.map((cell, ci) => new TableCell({
      borders, width: { size: colWidths[ci], type: WidthType.DXA },
      shading: ri % 2 === 0 ? { fill: C.bgLight, type: ShadingType.CLEAR } : undefined,
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
      children: [new Paragraph({ children: Array.isArray(cell) ? cell : [
        new TextRun({ text: String(cell || ""), font: "Calibri", size: 18, color: C.text })
      ]})]
    }))
  }));
  return new Table({ width: { size: colWidths.reduce((a,b)=>a+b,0), type: WidthType.DXA }, columnWidths: colWidths, rows: [hr, ...drs] });
};
```

### Etoiles de cotation

```javascript
const starsStr = (n) => "\u2605".repeat(n) + "\u2606".repeat(5 - n);
// starsStr(3) => "★★★☆☆"
```

### Header et Footer

Header : texte #666666 taille 16, filet bas #2B3A4E. Contenu : "Audit SEO Technique | [Nom Client]".
Footer : numero de page, filet haut #2B3A4E, texte #666666. Contenu : "Suisseo Sarl | Confidentiel".

```javascript
headers: {
  default: new Header({
    children: [new Paragraph({
      border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: C.blueDark, space: 4 } },
      children: [new TextRun({ text: "Audit SEO Technique | NOM CLIENT", font: "Calibri", size: 16, color: C.textSec })]
    })]
  })
},
footers: {
  default: new Footer({
    children: [new Paragraph({
      border: { top: { style: BorderStyle.SINGLE, size: 2, color: C.blueDark, space: 4 } },
      alignment: AlignmentType.RIGHT,
      children: [
        new TextRun({ text: "Suisseo Sarl | Confidentiel  ", font: "Calibri", size: 16, color: C.textSec }),
        new TextRun({ children: [PageNumber.CURRENT], font: "Calibri", size: 16, color: C.textSec })
      ]
    })]
  })
}
```

---

## Rappels importants

- Ne pas copier des donnees d'un autre client. Chaque audit est unique.
- Les scores PageSpeed et W3C doivent etre collectes en live via Chrome, pas inventes.
- Si des donnees manquent (pas de CSV, pas d'acces Chrome), le signaler a l'utilisateur plutot que d'inventer.
- Le nom du client doit etre correct partout : couverture, header, introduction, conclusion.
- Le consultant est toujours Thomas Nedjar.
