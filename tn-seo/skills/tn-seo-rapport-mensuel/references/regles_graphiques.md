# Regles de visualisation

Ces regles viennent de graphiques refuses par le consultant. Elles ne sont pas cosmetiques :
un graphique faux ou illisible fait prendre de mauvaises decisions.

## Choisir la forme selon le nombre de points

| Points | Forme | Pourquoi |
|---|---|---|
| 1 a 2 | Un chiffre, une tuile KPI | Une courbe a deux points n'a aucune information de forme |
| 3 a 11 | Barres, ou un tableau | Trois points relies donnent une fausse impression de tendance |
| 12 a 40 | Courbe simple, ou barres si les periodes sont discretes | |
| 30 a 120 | Courbe quotidienne + moyenne mobile 7 jours | Texture ET tendance |
| 120 a 500 | Courbe quotidienne attenuee + moyenne mobile 28 jours | |

La question a se poser avant de tracer : **si je retire un point, l'histoire change-t-elle ?**
Si oui, il n'y a pas assez de points pour une courbe.

## Ce qu'on ne trace jamais

- **La position moyenne agregee** d'un site, d'un pays ou d'une langue. Elle varie quand le mix
  de requetes varie : une page qui commence a s'afficher sur une requete lointaine degrade la
  moyenne alors que rien n'a bouge. La position se lit par mot-cle suivi.
- **Deux unites sur un meme graphique** (clics et impressions). Deux graphiques, ou un indice
  base 100 si la comparaison de dynamique est le sujet.
- **Un axe tronque sur des barres.** Sur des barres, l'axe part de zero, sinon les proportions
  mentent. Sur une courbe, un axe tronque est acceptable et souvent souhaitable.
- **Une serie melangeant un mois partiel et des mois complets** sans distinction visuelle. Si le
  mois en cours doit figurer, le colorer differemment et le dire en legende.

## Mise en forme

- Une seule grille de largeurs : toutes les figures pleine largeur au meme format, toutes les
  demi-largeur au meme format, avec le meme rapport centimetres/pouce a l'insertion. Sinon la
  taille du texte varie d'un graphique a l'autre et le document parait bricole.
- Police du graphique identique a celle du document. Carlito est metriquement compatible Calibri
  et disponible sous Linux.
- Titre du graphique en legende Word au-dessus de l'image, pas dans l'image : integration plus
  propre, et une seule police.
- La legende Word porte `keep_with_next` pour ne jamais se retrouver orpheline en bas de page.
- Traits fins (1,4 pt), un seul point marque en fin de courbe, une seule valeur annotee, grille
  tres pale, pas de cadre, quatre graduations maximum.
- Etiquettes directes plutot que legende quand il n'y a qu'une serie.

## Couleurs

Palette de series validee (bande de clarte, plancher de chroma, separation en vision
daltonienne, contraste) :

- Serie 1 : `#2F6FB2`
- Serie 2 : `#7FA817`
- Serie 3 : `#A4568C`
- Residuel ou « autres » : `#B9BEC6`

Les couleurs de marque Suisseo (`#2B3A4E`, `#95C11F`) restent sur les titres et le texte : le
bleu nuit lit comme un gris en aplat de serie, et le vert clair ne tient pas le contraste sur
fond blanc. Toute figure porte des etiquettes de valeurs, ce qui leve la reserve de contraste.

Pour valider une autre palette : `node scripts/validate_palette.js "#hex,#hex" --mode light`
depuis le skill `dataviz`.

## Nombres

Format francais partout : virgule decimale, espace fine insecable pour les milliers, espace
avant le signe pourcent. `79 813`, `84,2 %`, `+18 259 (+29,7 %)`.

Pour une variation de position, ecrire le sens en toutes lettres : « 1,4 place perdue »,
« 2 places gagnees ». Un « -1,4 » se lit comme une amelioration une fois sur deux.

## Controle final

Convertir le document en PDF, le rendre en images, regarder chaque page. Les defauts qui ne se
voient qu'a l'oeil : etiquettes tronquees, colonnes ecrasees, legendes orphelines, tableaux
coupes entre deux pages, chevauchement d'annotations.

```bash
soffice --headless --convert-to pdf rapport.docx --outdir /tmp/preview
pdftoppm -png -r 75 /tmp/preview/rapport.pdf /tmp/preview/page
```
