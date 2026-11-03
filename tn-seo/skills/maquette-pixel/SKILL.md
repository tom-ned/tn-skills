---
name: maquette-pixel
description: >
  Production de maquettes HTML pixel-pres pour les clients de l'agence Suisseo.
  Reproduit le header EXACT du site client (fetch direct + CSS bundle), associe
  un body propre SEO-friendly (hero + sections + specs + FAQ + double CTA) et
  un footer Suisseo standardise. Utiliser ce skill des qu'on parle de :
  "maquette HTML", "maquette pixel-pres", "page d'optimisation pour [client]",
  "refaire la page [X] de [client]", "exemple de page [use-case] pour [client]",
  "maquette page produit", "maquette page industrie", "maquette page service".
  Complementaire au skill opti-site : opti-site = strategie globale (audit + plan + maquettes),
  maquette-pixel = recette concrete pour produire UNE maquette.
  Ne pas inventer de contenu non source. Toujours fetcher la vraie page d'abord.
---

# Maquette pixel-pres -- Recette Suisseo

## Quand declencher

Des qu'on doit produire une maquette HTML qui ressemble au site d'un client. Exemples :
- "Refais-moi la page produit de [client]"
- "Maquette de page service pour Client X"
- "Exemple d'optimisation de la page X"
- "Page use-case pour la verticale Y du client Z"

## Principe directeur

Trois blocs distincts :
1. **HEADER** : HTML EXACT du site client (fetch + absolutise + CSS bundle leur)
2. **BODY** : design propre Suisseo, sobre et SEO-friendly
3. **FOOTER** : footer Suisseo standardise (le footer du client est souvent claque)

Le user a explicitement valide cette repartition. Ne pas mixer (ex : mettre le footer client) sauf demande contraire.

Aucun contenu invente : extraire les vrais textes du site (HTML + payload JSON Nuxt/Next/etc.) avant de rediger.

## Etape 1 : Fetch et extraction

```bash
# Fetcher la page cible et au moins une page connexe (pour avoir leur header/footer)
curl -s "https://www.client.com/page-cible" -o page_target.html
curl -s "https://www.client.com/produits/exemple" -o page_ref.html
```

Si le site est full Nuxt/Next, fetcher aussi le payload JSON pour avoir tous les textes :

```bash
# URL Nuxt typique
curl -s "https://www.client.com/page-cible/_payload.json?BUILD_HASH" -o page_target_payload.json
```

Recuperer ensuite, dans le HTML d'une page produit du site :
- Balise `<header>...</header>` complete
- Liens CSS (`<link rel="stylesheet">`)
- Blocs `<style>` inline (variables de couleurs, icones SVG en mask, etc.)

```python
import re
with open('page_ref.html') as f: html=f.read()

header=re.search(r'<header[^>]*>.*?</header>',html,re.DOTALL).group(0)
inline_styles='\n'.join(re.findall(r'<style[^>]*>.*?</style>',html,re.DOTALL))
css_links=re.findall(r'<link rel="stylesheet"[^>]+>',html)
```

## Etape 2 : Absolutiser les URLs du header et CSS

Le header reference des images et chemins relatifs (`/img/...`, `/_vercel/image?url=/img/...`). Les rendre absolus :

```python
def absolutize(s, base_url='https://www.client.com'):
    s=re.sub(r'(href|src|srcset)="(/[^"]*)"',
             lambda m: f'{m.group(1)}="{base_url}{m.group(2)}"', s)
    return s

header=absolutize(header)
css_links=[absolutize(c) for c in css_links]
```

Important : si le srcset contient plusieurs URLs (1x, 2x), s'assurer qu'elles sont TOUTES absolutisees.

## Etape 3 : Logo header, ratio et qualite

Probleme classique : le srcset Vercel/Next sert le logo en `w=1536` alors qu'on l'affiche a `h-10` (40px de haut). Resultat = blur ou alourdissement de la page.

Verifier les dimensions reelles du logo :

```bash
curl -s -o /tmp/logo.png "https://www.client.com/img/logos/logo.png"
python3 -c "from PIL import Image; img=Image.open('/tmp/logo.png'); print(img.size)"
```

Recalculer les attributs `width` et `height` HTML pour respecter le ratio. Exemple : logo 1575x474, affichage h-10 (40px) :
- height = 40
- width = 40 * (1575/474) = 133

Reduire la taille demandee a Vercel pour eviter le scaling : `w=320` pour 1x, `w=640` pour 2x.

Template logo header pixel-net :

```html
<img class="h-10 w-auto shrink-0"
     src="https://www.client.com/_vercel/image?url=%2Fimg%2Flogos%2Flogo.png&w=320&q=100"
     srcset="https://www.client.com/_vercel/image?url=%2Fimg%2Flogos%2Flogo.png&w=320&q=100 1x,
             https://www.client.com/_vercel/image?url=%2Fimg%2Flogos%2Flogo.png&w=640&q=100 2x"
     width="133" height="40"
     alt="Client Logo" loading="eager" decoding="async">
```

## Etape 4 : Body propre SEO

Voir `templates/body_template.html` pour la structure complete. Composants types :

1. **Breadcrumb** semantique (`<nav aria-label="Breadcrumb">`, `aria-current="page"`)
2. **Hero** : eyebrow + H1 (avec `<em>` pour accent couleur primary) + lead + 2 CTA (primary jaune yellow + outline)
3. **Trust strip** : 4 marqueurs sobres separes par des dots
4. **3 sections split** image/texte alternees avec liste a check
5. **Specs** sobre en `<dl>` (4 lignes : configurations, performances, options, disponibilité)
6. **FAQ** en `<details><summary>` (rendu natif deroulant)
7. **Final CTA double** : Configurator + Talk to expert (gradient bleu fonce du client)

Ne PAS utiliser :
- Cards a ombres flashy
- Gradients clinquants ailleurs que la final CTA
- Emojis decoratifs
- Lignes accent sous les titres (signature IA)

## Etape 5 : Footer Suisseo standardise

Voir `templates/footer_suisseo.html`. 4 colonnes :
1. Logo client + adresses
2. Produits / Industries (selon site)
3. Services / Other links
4. Newsletter + social SVG (LinkedIn, Instagram)

CSS du footer scope avec selecteur `.site-footer` et NON `.site-footer.maq-body` ou autre combinaison fragile. Toujours injecter le CSS du footer dans le `<head>`.

## Etape 6 : SEO-friendly, indispensable

Toute maquette livree doit avoir :
- Title 50-65 caracteres avec mot-cle cible
- Meta description 145-160 caracteres avec value prop
- Canonical absolue
- Open Graph complet (og:type, og:title, og:description, og:image, og:url)
- Twitter Card large image
- JSON-LD : Product / Service / Organization selon la nature
- H1 unique en hero, H2 par section, H3 dans cards
- Alt texts descriptifs (jamais "logo" tout court)
- `lang="en"` ou la langue de la page
- `loading="eager"` sur l'image hero, `loading="lazy"` sur le reste
- Preconnect vers le CDN client

## Etape 7 : Overlay Suisseo (signature maquette)

CHAQUE maquette livree doit porter l'overlay Suisseo en bas a droite. Ne jamais oublier.

Snippet a coller dans le `<head>` :

```html
<style>
.suisseo-banner{
  position:fixed;right:16px;bottom:16px;z-index:9999;
  background:#1E2A38;color:#fff;font-size:11px;
  padding:9px 14px;border-radius:8px;
  box-shadow:0 6px 16px rgba(0,0,0,.18);
  font-family:system-ui,sans-serif;line-height:1.4
}
.suisseo-banner b{color:#95C11F}
.suisseo-banner a{color:rgba(255,255,255,.65);text-decoration:none}
.suisseo-banner a:hover{color:#fff}
</style>
```

Snippet a coller juste avant `</body>` :

```html
<div class="suisseo-banner">
  Maquette <b>Suisseo</b> &middot; Page [NOM_PAGE]<br>
  <a href="mailto:thomas.nedjar@suisseo.ch">thomas.nedjar@suisseo.ch</a>
</div>
```

Adapter `[NOM_PAGE]` (ex : "Page Sport", "Page Produit", "Page Pricing").

## Etape 8 : QA avant livraison

Checks obligatoires :

1. **Pas de `<a:t>` ou autre artefact** d'un autre format
2. **CSS du footer present** : `grep ".site-footer .footer-grid" maquette.html`
3. **Tous les srcset absolutises** : aucune URL `/_vercel/...` sans domaine
4. **Logo header pas force avec ratio incorrect** : verifier `width/height`
5. **Pas de scope `.site-footer.maq-body`** ou combinaison fragile (le user nous a tape sur les doigts pour ca)
6. **Header logo en `w=320` pas `w=1536`** : sinon blur garanti
7. **Aucun text invente** : verifier que le contenu vient bien du site fetched
8. **Overlay Suisseo present** : `grep "suisseo-banner" maquette.html`
9. **Email thomas.nedjar@suisseo.ch dans l'overlay**

Verification visuelle si possible (chromium/playwright). Si pas dispo dans le sandbox, faire des checks textuels stricts via grep.

Test responsive minimal :
- 1280px desktop : grilles a 4 colonnes
- 1024px tablette : grilles a 2 colonnes
- 640px mobile : grilles a 1 colonne

## Cas particuliers

### Site full custom sans CSS exposable

Si pas de `<link rel="stylesheet">` accessible (CSS inline minifie, pas de bundle), tout inliner en CSS custom Suisseo. Recreer les couleurs en variables a partir des couleurs du site (extraction via `grep -oE '#[0-9A-Fa-f]{6}'`).

### Site WordPress avec Yoast / Elementor

Le footer WP est souvent claque (widgets vides, politique cookies dans les liens utiles). Toujours prendre uniquement le HEADER et utiliser le footer Suisseo.

### Contenu non extractible

Si le HTML est rendu cote client (SPA Vue/React sans SSR), regarder le payload `_nuxt/payload.json` ou le `__NEXT_DATA__` pour les vrais textes. En dernier recours, demander a l'utilisateur de copier-coller le contenu.

## Anti-patterns (ne pas faire)

- Ecrire un body design "marketing pump" avec gradients partout : ca fait IA-generated
- Inventer des chiffres clients ("trusted by 500+ brands")
- Utiliser le footer du client si il est moche : prendre Suisseo
- Forcer width/height du logo sans verifier le ratio reel
- Linker le bundle CSS client SANS l'avoir teste (peut casser au prochain redeploy)
- Oublier l'overlay Suisseo et l'email thomas.nedjar@suisseo.ch
- Mettre des sections "use cases / case studies" inventees : verifier d'abord si le site en a deja

## Livraison finale

Une maquette = un fichier HTML autonome :
- Inline tous les CSS critiques
- Reference le CDN du client pour les images (pas de copy local)
- Place dans le dossier client `[Nom_Client]/maquette_[nom_page].html`
- Mentionner les versions precedentes dans `_a_supprimer/` si refonte iterative

Dans le commit message ou le mail au client :
- Lister les sources de chaque texte (URL fetched)
- Preciser que le CSS de leur header est lie a leur CDN actuel
- Pointer les ameliorations SEO concretes vs leur version actuelle (title, meta, schema, alt, hierarchie Hn)

## Resources

Templates a copier dans `templates/` :
- `body_template.html` : structure complete d'une page d'industrie / use case
- `footer_suisseo.html` : footer 4 colonnes + social SVG
- `head_template.html` : meta + JSON-LD + overlay CSS

Scripts utiles dans `scripts/` :
- `extract_header.py` : extrait header + CSS d'une URL et absolutise tout
- `build_page.py` : assemble head + header client + body + footer Suisseo + overlay

