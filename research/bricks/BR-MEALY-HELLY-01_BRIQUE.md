# BR-MEALY-HELLY-01 v1

Borne de Helly du nerf de compatibilité des résolveurs Mealy

Statut : **DÉMONTRÉ interne**.  
Originalité : **INDÉTERMINÉE** ; aucune priorité revendiquée.

## Énoncé

Pour une machine de Mealy finie, complète et déterministe avec `q` sorties et `r_IO=1`, fixer un état de connaissance accessible `K` et une entrée `a`. Sur les branches `K(a,y)` dont le langage de résolution preset `R_y` est non vide, former le nerf de compatibilité par intersections non vides des `R_y`.

- Toute non-face minimale a taille `<= q-1`.
- La famille des langages est donc `(q-1)`-Helly.
- Pour `q=2`, elle est 1-Helly.
- Pour tout `q>=3`, la borne `q-1` est atteinte par `C(q,q-1)` ; chaque arité `2..q-1` est réalisable.

## Mécanisme

Une branche indispensable d'une non-face minimale doit contenir au moins deux identités et posséder un résolveur ; elle est donc fertile. `OBS-M27-FERTILE` borne le nombre de branches fertiles par `q-1`. `OBS-M27-SPECTRUM` donne les exemples qui saturent la borne.

## Validation

21 machines `C(q,k)` pour `q=3..8`, 492 états de connaissance accessibles et 1 337 nerfs testés par recherche indépendante de PDS communs ; zéro violation ; sharpness exacte à la racine dans tous les cas.

## Limites

Aucune borne sur la longueur/complexité du PDS commun, aucune extension sans `r_IO=1`, aucune originalité externe certifiée.

## Provenance

Rapport : `/MEALY_HELLY_BRIDGE_2026-10-16.md`  
Résultats : `/MEALY_HELLY_RESULTS_2026-10-16.json`  
Dépendances : `OBS-M27-FERTILE`, `OBS-M27-SPECTRUM`  
Commit : `COMMIT-RAVI2-2026-10-16-MEALY-HELLY-19`