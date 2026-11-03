# Structure attendue des livrables

Les scripts produisent deja cette structure. Ce document sert de reference qualite : ce a quoi un
bon livrable doit ressembler, pour verifier la sortie.

## Excel (build_xlsx.py) - "pure data", mise en forme legere

5 onglets :

1. **Synthese** : titre, client/domaine/moteur, periode. Tableau KPI a 4 colonnes
   (Indicateur | M-2 | M-1 | M) + colonne evolution M-1>M. Lignes : mots-cles positionnes, TOP 3,
   TOP 10, TOP 30, position moyenne. En-tete fond bleu Suisseo, premiere colonne grisee.

2. **Evolution hebdo** : tableau Semaine | Visibilite (%) | Position moyenne | Mots-cles TOP 10,
   une ligne par semaine ISO. Plus **3 graphes natifs Excel** (LineChart) a droite : visibilite,
   position moyenne, TOP 10. Natifs = modifiables dans Excel, pas des images.

3. **Mots cles** : une ligne par mot-cle suivi (tous). Colonnes : Mot-cle | Volume | Page de
   destination | Pos M-2 | Pos M-1 | Pos M | Evolution | Statut. Filtre auto, volets figes.
   Fond vert clair si progression, fond rouge clair si recul. Trie par volume decroissant.

4. **Par page** : une ligne par URL. Colonnes : Page | Nb mots-cles | Volume cumule |
   Position moyenne | Mots-cles TOP 10 | Liste des mots-cles. Trie par volume cumule decroissant.
   C'est la reponse a "volumes par page et mots-cles par page".

5. **Highlights** : 4 blocs (progressions, fort volume en TOP 10, entrees TOP 3/TOP 10,
   sorties/vigilance). Chaque bloc : Mot-cle | Volume | Page | Pos M-1>M | Evolution.

## Word (build_docx.py) - synthese charte Suisseo

- **Page de garde** : logo Suisseo, titre "Reporting SEO mensuel", nom client en vert, domaine,
  moteur, periode analysee + comparaison, date et consultant. Header et footer Suisseo.
- **1. Synthese du mois** : 3-4 phrases factuelles (nombre de mots-cles, TOP 10, evolution vs M-1,
  tendance) + tableau KPI M-2/M-1/M.
- **2. Faits marquants** : 4 listes a puces - plus fortes progressions, entrees TOP 3/TOP 10,
  fort volume en TOP 10, points de vigilance. Chaque item : mot-cle, volume, pos M-1>M, page.
  Limite a 8 items par bloc pour rester lisible.
- **3. Evolution hebdomadaire** : 1-2 phrases sur la tendance de visibilite, renvoi au xlsx pour
  les courbes (non dupliquees en images).
- **4. Pages les plus contributrices** : tableau des 10 pages a plus fort volume cumule.

Le Word reste court et factuel. Pas de paragraphes de remplissage, pas de recommandations
inventees. Si l'utilisateur veut des recommandations, c'est une demande separee.

## Regles highlight (appliquees par prepare_data.py)

- **Progressions** : delta de position negatif (gain), trie par plus fort gain puis volume. Max 15.
- **Fort volume** : mots-cles en TOP 10 tries par volume decroissant. Max 15.
- **Entrees TOP** : statut passe de hors-TOP/TOP30 a TOP10/TOP3, ou de TOP10 a TOP3. Trie par volume.
- **Sorties / vigilance** : statut passe de TOP3/TOP10 vers TOP30/hors, ou de TOP3 a TOP10. Trie par volume.

Statuts : top3 (<=3), top10 (<=10), top30 (<=30), hors_top30 (>30), hors (non positionne).
