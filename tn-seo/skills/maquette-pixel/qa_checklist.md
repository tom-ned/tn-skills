# QA checklist - Maquette Suisseo

A passer AVANT de livrer une maquette au client.

## Header (client)

- [ ] HEADER fetche depuis le vrai site client (pas reconstruit)
- [ ] Toutes les URLs `href`, `src`, `srcset` sont absolutisees vers le domaine client
- [ ] Logo header utilise les bonnes dimensions HTML `width`/`height` (vrai ratio du PNG)
- [ ] Logo header demande a Vercel/Next en `w=320` (ou max 640 pour 2x), pas en `w=1536`
- [ ] CSS bundle client charge (link tags) ET inline styles client preserves
- [ ] Aucun script Nuxt/Next d'hydratation laisse (peuvent casser la page)

## Body (Suisseo)

- [ ] Aucun contenu invente, tout vient du site client (verifier via grep des phrases clefs)
- [ ] H1 unique en hero
- [ ] Hierarchie H2 par section, H3 dans cards si necessaire
- [ ] Boutons : primary (jaune/yellow client), outline secondaire
- [ ] Listes a check avec mask SVG (pas de checkmark unicode "✓")
- [ ] Images : `loading="eager"` sur hero, `loading="lazy"` sur le reste
- [ ] Alt texts descriptifs (pas "image" ou "logo" tout court)
- [ ] Pas de gradient flashy, pas de cards a ombre clinquantes
- [ ] Pas d'emojis decoratifs

## Footer (Suisseo)

- [ ] CSS du footer scope `.site-footer` (PAS `.site-footer.maq-body` ou autre combo fragile)
- [ ] CSS du footer present dans le `<head>` (verifier avec grep)
- [ ] 4 colonnes alignees : Logo+adresses / Col2 / Col3 / Newsletter+social
- [ ] Logo footer en `width="106" height="32"` ou ratio respecte
- [ ] Social SVG inline (LinkedIn + Instagram), pas de texte "in"/"ig"
- [ ] Mention "Maquette projective - Suisseo, proposition Thomas"

## SEO

- [ ] Title 50-65 caracteres avec mot-cle cible
- [ ] Meta description 145-160 caracteres avec value prop
- [ ] Canonical absolue
- [ ] Open Graph complet (og:type, og:title, og:description, og:image, og:url)
- [ ] Twitter Card large image
- [ ] JSON-LD : Service / Product / Organization selon la nature
- [ ] `lang="xx"` sur `<html>`
- [ ] Robots index,follow
- [ ] Preconnect vers le CDN client

## Overlay Suisseo

- [ ] Bandeau `.suisseo-banner` en bas a droite present
- [ ] Email `thomas.nedjar@suisseo.ch` cliquable dans l'overlay
- [ ] Label de la page (ex : "Page Sport") dans l'overlay

## Responsive

- [ ] 1280px : grilles a 4 colonnes (footer) et 2 colonnes (hero, CTA)
- [ ] 1024px : grilles a 2 colonnes
- [ ] 640px : grilles a 1 colonne
- [ ] Header : nav cachee sur mobile (display:none)
- [ ] Tableaux : `overflow-x:auto` pour eviter les debordements

## Tests automatises (grep)

```bash
F=maquette.html
grep -c '<header' $F  # 1
grep -c '<footer' $F  # 1
grep -c '<h1' $F  # 1
grep -c 'class="site-footer"' $F  # 1
grep -c 'suisseo-banner' $F  # 1
grep -c 'thomas.nedjar@suisseo.ch' $F  # 1+
grep -c 'application/ld\+json' $F  # 1+
grep -c 'og:title' $F  # 1+
grep -c 'canonical' $F  # 1+
```

## Verification visuelle (si possible)

- [ ] Screenshot rendu (chromium / playwright) sur 1280x desktop ET 640x mobile
- [ ] Visuellement : aucun chevauchement, aucune image cassee, logos nets
- [ ] Liens header fonctionnent (route vers les bonnes pages client)
- [ ] CTA bottom : configurator + contact pointent vers les bonnes URL client

## En cas de probleme

- Footer claque -> verifier que le CSS `.site-footer` est bien injecte dans le `<head>`
- Logo flou -> ajuster `w=320`/`w=640`, verifier `width`/`height` HTML
- Layout casse -> verifier que les inline styles client sont presents (vars de couleur)
- Header pas fonctionnel -> les data-reka, data-slot etc. font partie du composant Reka, c'est normal qu'ils ne fassent rien sans JS

