# RAVI-2 v1.3 — couche stricte phase 5

Date : 16 octobre 2026.

## Delta scientifique

Le commit `COMMIT-RAVI2-2026-10-16-MEALY-HELLY-19` ajoute `BR-MEALY-HELLY-01`, avec deux dépendances causales vers `OBS-M27-FERTILE` et `OBS-M27-SPECTRUM`.

## Couverture stricte

- 77 résultats, 73 admissibles, 44 `DEPEND_DE`.
- 43 contrats stricts, 20 adaptateurs.
- 44/44 interfaces strictes certifiées.
- 39 `COMPOSITION`, 1 `VALIDATION_REFERENCE`, 2 `DATA_REFERENCE`, 2 `DEFINITION_REFERENCE`.
- 0 dépendance causale non couverte.

Le contrat `OBS-M27-SPECTRUM`, jusque-là sans dépendance causale et donc hors couche stricte, est maintenant formalisé comme extrémité du nouveau raccordement.

## Nouvelles interfaces

- relation 76 : `BR-MEALY-HELLY-01 -> OBS-M27-FERTILE`, `CONCLUSION_IMPORT`; sortie consommée `FERTILE_WIDTH_LE_Q_MINUS_1`.
- relation 77 : `BR-MEALY-HELLY-01 -> OBS-M27-SPECTRUM`, `GUARDED_CONCLUSION_IMPORT` sous `q>=3`; sorties consommées : réalisabilité des arités et noyau racine de taille `k`.

## Reconstruction indépendante

Un miroir vierge reconstruit depuis la base principale et le registre phase 5 restaure 43/43 contrats, 44/44 revues et 44/44 certificats, sans élément stale. Il contient 39 compositions certifiées ; intégrité SQLite `ok`, zéro erreur de clé étrangère. Les 26 tables communes avec la base principale sont identiques ligne par ligne.

## Limite

La couche stricte certifie la compatibilité interne des contrats et de leurs versions. Elle ne constitue ni une preuve formelle externe ni une certification de nouveauté bibliographique.