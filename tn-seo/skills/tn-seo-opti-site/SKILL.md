---
name: tn-seo-opti-site
description: >
  Optimisation SEO et UX/conversion d'un site web existant pour l'agence Suisseo.
  Analyse un site (URL + brief), evalue la techno et la difficulte d'intervention,
  propose une guideline d'actions priorisees realisables en 6h, et genere des maquettes
  HTML standalone montrant les pages optimisees.
  UTILISER CE SKILL des qu'on mentionne : "optimiser un site", "opti site", "opti landing",
  "optimisation de site", "optimisation de pages", "maquettes d'optimisation",
  "ameliorer le site de [client]", "opti pour [client]", "refonte SEO", "opti UX",
  "landing page optimisee", "maquettes HTML", ou toute demande combinant analyse de site
  + recommandations actionnables + maquettes visuelles.
  Meme si la demande est courte ("opti pour client x" ou "on optimise le site de client y"),
  ce skill doit se declencher. Ne pas confondre avec l'audit SEO technique (qui est un diagnostic
  sans maquettes). Ici on produit des livrables actionnables avec des maquettes.
---

> Modèles : chercher `_templates/` dans le dossier de travail, puis dans `~/.claude/tn-seo/_templates/`, puis dans `../../_templates/` à partir du dossier de ce skill. Le dossier retenu est aussi la `<racine Suisseo>` à passer aux scripts. Si un fichier manque partout, utiliser le skill `maj-templates` au lieu d'inventer la charte ou le logo.

# Opti Site -- Optimisation SEO + UX/Conversion

## Contexte

Tu travailles pour l'agence Suisseo (Lausanne). Un client a un site existant qu'il faut optimiser. L'objectif est de produire un plan d'actions concret et des maquettes HTML qui montrent concretement a quoi les pages devraient ressembler apres optimisation.

Le budget temps est de 6 heures de travail. Tout ce que tu proposes doit etre realisable dans cette enveloppe. C'est un cadre operationnel, pas un audit exhaustif.

## Etape 1 : Decouverte et cadrage

### Informations necessaires

Demander a l'utilisateur :

1. **URL du site** (obligatoire)
2. **Brief / objectif** : quel est le but business ? (generer des leads, vendre, prendre des RDV, augmenter la visibilite locale, etc.)
3. **Pages prioritaires** : si l'utilisateur a deja une idee des pages a optimiser, les noter. Sinon, on les identifiera au scraping.

### Scraping et analyse technique

Une fois l'URL obtenue :

1. Fetch la page d'accueil et 3-5 pages cles (prestations, contact, a propos, blog si present)
2. Identifier la technologie :
   - CMS : WordPress, Drupal, Joomla, Wix, Squarespace, Webflow, custom
   - Builder/theme : Elementor, Divi, Avada, Astra, Oxygen, theme custom
   - Plugins SEO : Yoast, Rank Math, All in One SEO, aucun
   - Autres : Google Tag Manager, analytics, cookies, formulaires
3. Evaluer le niveau de difficulte d'intervention

### Grille de difficulte

La difficulte determine ce qu'on peut faire en 6h et qui doit intervenir.

**Facile (on fait tout nous-memes)** :
WordPress + Elementor, Divi, ou WPBakery avec acces admin. Wix, Squarespace, Webflow avec acces editeur. On peut modifier le contenu, les balises, la structure des pages directement.

**Moyen (on fait le contenu, le webmaster fait la technique)** :
WordPress avec theme custom ou builder inconnu. Acces admin mais modifications de template limitees. On redige le contenu optimise, on prepare les specs, le webmaster implemente.

**Difficile (webmaster necessaire pour quasi tout)** :
Drupal, Joomla, site full custom, framework JS (Next, Nuxt, React). CMS proprietaire. Pas d'acces au back-office. On produit un cahier des charges detaille, le webmaster execute.

**Bloque (on ne peut pas intervenir)** :
Pas d'acces, pas de contact webmaster, techno obsolete ou propriitaire fermee. On documente les recommandations mais on previent que l'implementation depend de tiers.

### Restitution du cadrage

Avant de produire quoi que ce soit, presenter a l'utilisateur :

```
Site : [URL]
Techno : [CMS + builder + plugins detectes]
Difficulte : [Facile / Moyen / Difficile / Bloque]
Qui intervient : [Nous seuls / Nous + webmaster / Webmaster seul]
Pages cibles proposees : [liste des 3-5 pages prioritaires, classees par impact]
Axes d'optimisation : [SEO on-page / UX-conversion / les deux]
Page recommandee pour commencer : [la page avec le plus d'impact]
```

Attendre la validation. L'utilisateur choisit par quelle page commencer. On travaille UNE PAGE A LA FOIS : guideline + maquette pour cette page, puis on passe a la suivante.

## Etape 2 : Travailler page par page

On traite UNE PAGE a la fois. Pour la page choisie, produire deux livrables :

### 2a. Fiche d'optimisation de la page

Dans le docx de guideline (utiliser le skill docx). Appliquer la charte Suisseo si disponible dans `_templates/`, sinon formatage simple (Calibri, titres en gras, tableaux propres).

Pour la page en cours :
- URL
- Title actuel vs Title propose (avec longueur en caracteres)
- Meta description actuelle vs Meta description proposee (avec longueur)
- H1 actuel vs H1 propose
- Structure Hn actuelle (schema simplifie) vs structure Hn proposee
- Contenu : forces, faiblesses, modifications proposees
- CTA : existant vs propose
- Maillage interne : liens a ajouter/modifier
- Actions concretes pour cette page (tableau : action, qui, temps estime, impact)

Le docx de guideline est un document evolutif : on y ajoute chaque page au fur et a mesure. La premiere iteration cree le fichier avec la synthese generale + la premiere page. Les iterations suivantes ajoutent les pages suivantes.

### Structure du document guideline

```
Titre : Guideline d'optimisation - [Nom du client]
Date : [Mois Annee]
Consultant : Thomas Nedjar
Suisseo Sarl | Lausanne

1. Synthese
   - Techno et difficulte
   - Objectif du client (rappel du brief)
   - Perimetre : pages cibles, budget 6h
   - Qui fait quoi (nous vs webmaster)

2. Page : [URL de la page 1]
   - Etat des lieux
   - Optimisations proposees
   - Actions (tableau)
   - Specs webmaster si necessaire

3. Page : [URL de la page 2]
   ...

N. Recapitulatif des actions (ajoute une fois toutes les pages traitees)
   Tableau consolide avec le total des temps.
```

### 2b. Maquette HTML de la page

ECRIRE DE ZERO un fichier HTML standalone pour cette page. Le but est de montrer la page optimisee, pas de copier le site existant.

### Regle fondamentale : ecrire du code neuf

Le scraping du site client (etape 1) sert uniquement a comprendre le contenu, la structure et l'identite visuelle. Les maquettes doivent etre ecrites from scratch avec du HTML/CSS propre.

Ne jamais :
- Copier-coller le code source HTML du site client
- Inclure le CSS du CMS (Divi, Elementor, WordPress, etc.)
- Lier vers les feuilles de style du site client (pas de href vers le domaine client)
- Inclure les classes CSS du builder (et_pb_, elementor-, divi-, etc.)
- Inclure les scripts JS du site client (jQuery, plugins WP, etc.)

Toujours :
- Ecrire un HTML propre et semantique depuis zero
- Utiliser Tailwind CSS via CDN comme unique framework CSS
- Ajouter du CSS custom dans une balise <style> si besoin
- Garder le fichier 100% autonome (ouvrable en local sans connexion au site client)

Le test de validation : le fichier HTML ne doit contenir AUCUNE reference au domaine du client dans les balises link, script ou style. Les seules references autorisees au domaine client sont les URLs des images (src des img) et les liens href de navigation.

### Deux modes selon le contexte

Demander a l'utilisateur quel mode il prefere :

**Mode "maquette"** : reference visuelle pour guider les modifications sur le site existant. Bandeau Suisseo en haut. Le webmaster s'en sert pour reproduire les changements dans le CMS.

**Mode "landing deployable"** : fichier HTML autonome pret a mettre en ligne (Netlify drag-and-drop, hebergement statique). Pas de bandeau, formulaire fonctionnel, tracking pre-configure.

En cas de doute, demander. Si le brief mentionne une campagne, privilegier le mode landing.

### Construction de la maquette

#### 1. Extraire l'identite visuelle du site (lors du scraping etape 1)

Lors du fetch initial, noter :
- Couleur principale (ex: #2B3A4E)
- Couleur secondaire / accent (ex: #95C11F)
- Couleur de fond (ex: #FFFFFF ou #F5F5F5)
- Couleur du texte (ex: #333333)
- Police utilisee (Google Fonts : Open Sans, Montserrat, etc. ou systeme)
- Style general : coins arrondis ou droits, ombres ou flat, style des boutons

#### 2. Ecrire le HTML avec Tailwind

Structure type :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Title optimise - max 60 car.]</title>
  <meta name="description" content="[Meta description optimisee - max 155 car.]">
  <meta property="og:title" content="[OG title]">
  <meta property="og:description" content="[OG description]">
  <meta property="og:type" content="website">
  <meta property="og:url" content="[URL de la page]">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=[Police+du+client]:wght@400;600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            primary: '#[couleur principale du client]',
            secondary: '#[couleur secondaire]',
            accent: '#[couleur accent]',
          },
          fontFamily: {
            sans: ['[Police du client]', 'sans-serif'],
          }
        }
      }
    }
  </script>
  <style>
    /* CSS custom complementaire si necessaire */
  </style>
  <!-- SUISSEO: remplacer GTM-XXXXXX par l'ID GTM du client -->
</head>
<body class="font-sans text-gray-800 bg-white">

  <!-- HEADER -->
  <header class="bg-white shadow-sm sticky top-0 z-50">
    <nav class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
      <img src="[URL logo client]" alt="[Nom client]" class="h-10">
      <div class="hidden md:flex gap-6">
        <a href="#" class="text-gray-700 hover:text-primary">Accueil</a>
        <!-- nav items -->
      </div>
      <a href="#contact" class="bg-primary text-white px-6 py-2 rounded hover:opacity-90">
        Devis gratuit
      </a>
    </nav>
  </header>

  <!-- HERO -->
  <section class="relative bg-gray-100 py-20">
    <div class="max-w-6xl mx-auto px-4">
      <!-- OPTI: H1 optimise avec mots-cles -->
      <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
        [H1 optimise]
      </h1>
      <p class="text-xl text-gray-600 mb-8 max-w-2xl">
        [Accroche optimisee]
      </p>
      <a href="#contact" class="bg-primary text-white px-8 py-3 rounded-lg text-lg hover:opacity-90">
        [CTA principal]
      </a>
    </div>
  </section>

  <!-- SECTIONS DE CONTENU -->
  <!-- Utiliser les classes Tailwind : max-w-6xl mx-auto px-4 py-16 -->
  <!-- Alterner fond blanc / fond gris clair pour rythmer -->

  <!-- FOOTER -->
  <footer class="bg-gray-900 text-gray-400 py-12">
    <div class="max-w-6xl mx-auto px-4">
      <!-- coordonnees, liens legaux, copyright -->
    </div>
  </footer>

</body>
</html>
```

#### 3. Images

- Mode maquette : utiliser des div avec fond colore et texte descriptif (ex: `<div class="bg-gray-200 h-64 flex items-center justify-center text-gray-500">Photo cuisine moderne</div>`)
- Mode landing : utiliser les vraies images du site client via URL absolue (ex: `<img src="https://exemple.ch/wp-content/uploads/2023/photo.jpg" alt="..." class="w-full h-64 object-cover">`)

### Mode maquette : specificites

- Bandeau fixe en haut de page :
```html
<div class="bg-[#2B3A4E] text-white text-center py-2 text-sm sticky top-0 z-[60]">
  Maquette Suisseo - [NomClient] - [Page] - Les zones modifiees sont annotees en commentaires HTML
</div>
```
- Commentaires HTML signalant chaque optimisation : `<!-- OPTI: nouveau H1 avec mots-cles -->`

### Mode landing : specificites

- Pas de bandeau
- Formulaire Formspree : `<form action="https://formspree.io/f/FORM_ID" method="POST">` avec commentaire `<!-- SUISSEO: remplacer FORM_ID -->`
- Placeholder GTM dans le head
- Lien mentions legales du client dans le footer

### Ce que la maquette contient

- Header (navigation simplifiee, logo du client si disponible)
- Hero section avec H1 optimise et CTA principal
- Sections de contenu avec structure Hn optimisee
- Preuves sociales (temoignages, logos clients, chiffres) si disponibles sur le site
- CTA optimises (boutons, formulaires)
- Footer avec coordonnees et liens legaux
- Meta tags complets dans le head

### Nommage

Mode maquette : `Maquette_[NomClient]_[slug-page].html`
Mode landing : `Landing_[NomClient]_[slug-page].html`

## Livrables

Deposer tous les fichiers dans le dossier du client : `[client]/_livrables/opti_site/`

1. `Guideline_Opti_[NomClient]_[AAAA-MM].docx`
2. `Maquette_[NomClient]_[page1].html` ou `Landing_[NomClient]_[page1].html`
3. `Maquette_[NomClient]_[page2].html` ou `Landing_[NomClient]_[page2].html`
4. ... (une par page cible)

## Flux page par page

Le workflow complet pour un client :

1. Cadrage (etape 1) : fetch, analyse techno, proposition de pages prioritaires
2. Validation par l'utilisateur : choix de la premiere page
3. Pour la page choisie : fiche d'optimisation dans le docx + maquette HTML
4. Livraison des deux fichiers, feedback de l'utilisateur
5. Page suivante : l'utilisateur dit "on passe a la suivante" ou choisit une autre page
6. Repeter jusqu'a epuisement du budget 6h ou des pages prioritaires
7. Ajouter le recapitulatif des actions dans le docx

Ne pas enchainer les pages sans feedback. Chaque page est un cycle : produire, montrer, valider, passer a la suivante.

## Points importants

- Ne jamais produire les livrables sans avoir d'abord presente le cadrage (etape 1) et obtenu validation
- Le budget est 6h. Si l'optimisation necessaire depasse ce budget, le signaler et proposer un perimetre reduit qui tient dans 6h
- Les maquettes sont des fichiers de communication, pas du code de production
- Adapter le niveau de detail des specs webmaster a la difficulte : plus c'est difficile techniquement, plus les specs doivent etre precises
- Si l'utilisateur fournit un brief strategique (mots-cles cibles, persona, positionnement), l'integrer dans les optimisations. Sinon, proposer une direction basee sur l'analyse du site et du secteur
- Travailler page par page. Ne jamais generer toutes les maquettes en un bloc.
