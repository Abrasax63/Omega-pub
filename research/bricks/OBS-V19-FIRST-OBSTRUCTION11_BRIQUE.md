# OBS-V19-FIRST-OBSTRUCTION11 — Premier ordre d’obstruction de multiplicité

**Type :** brique réutilisable / interface canonique  
**ID scientifique principal :** `OBS-V19-FIRST-OBSTRUCTION11` v2  
**Statut :** DÉMONTRÉ (certification interne RAVI-2)  
**Originalité :** INDÉTERMINÉE  
**Projet source :** Observabilité — V19

## Domaine

Cycle orienté `C5`, observation binaire, horizon `L=3`, contraintes forcées cohérentes. Une occurrence d’une classe est portée par une **paire non ordonnée d’états distincte comme paire** ; deux occurrences peuvent partager un état, mais ne peuvent pas être exactement la même paire.

## Énoncé principal

Soit `k*` le plus petit entier `k` tel qu’il existe un multiset de `k` labels parmi les 14 classes orientées `C5O-00..13` qui ne puisse pas être réalisé simultanément par `k` paires d’états distinctes dans une même endofonction cohérente.

Alors

`k* = 11`.

Cette v2 renforce la v1 : la région complète des multiplicités de labels est désormais connue par `OBS-V19-COEX-REGION`.

## Région complète des labels

Les capacités totales de classes sont :

- `C5O-00 <= 10`
- `C5O-01 <= 10`
- `C5O-02 <= 10`
- `C5O-03 <= 10`
- `C5O-04 <= 40`
- `C5O-05 <= 20`
- `C5O-06` non bornée
- `C5O-07 <= 40`
- `C5O-08` non bornée
- `C5O-09 <= 60`
- `C5O-10` non bornée
- `C5O-11 <= 80`
- `C5O-12` non bornée
- `C5O-13 <= 160`.

**Toute** combinaison entière non négative respectant ces seules bornes est réalisable par des paires distinctes dans un même système admissible.

## Premier ordre interdit

Le minimum des capacités finies de labels vaut `10`, pour quatre classes :

`C5O-00, C5O-01, C5O-02, C5O-03`.

Donc tous les multisets de taille `<=10` sont réalisables et les quatre premiers témoins purs de taille 11 sont :

- `11 x C5O-00` ;
- `11 x C5O-01` ;
- `11 x C5O-02` ;
- `11 x C5O-03`.

La v1 utilisait seulement `11 x C5O-02` comme témoin d’impossibilité. Ce témoin reste correct ; la v2 montre qu’il appartient à une famille de quatre obstructions minimales et fournit la classification globale, pas seulement le premier ordre.

## Niveau géométrique plus fin

Avant quotient par rotations, `OBS-V19-COEX-REGION` donne un ordre critique différent :

`k_geo* = 3`.

Il y a 20 ombres géométriques exactes de capacité `2`, et `3` occurrences d’une même telle ombre sont impossibles. Le passage `3 -> 11` provient donc de l’agrégation des cinq rotations à l’intérieur d’un même label orienté.

## Dépendance causale actuelle

- `OBS-V19-FIRST-OBSTRUCTION11 DEPEND_DE OBS-V19-COEX-REGION`.

Les anciennes preuves via `OBS-V19-UNIVERSAL10` et `OBS-V19-C5-CAPACITY` restent historiquement valides pour la v1, mais la v2 est désormais portée par la classification complète de la région.

## Limites

- Résultat exact pour `C5`, observation binaire, `L=3`.
- Les occurrences sont des paires distinctes ; elles peuvent partager un état.
- Ce résultat concerne les occurrences de paires et leurs ombres. Il ne classe pas encore les supports de **mauvais objets distincts** dans les circuits positifs.
- Les coefficients algébriques des circuits ne sont pas des nombres de paires ; utiliser `BR-OBS-CAP-02`.
- Originalité bibliographique : INDÉTERMINÉE.

## Provenance

Rapport principal v2 : `/Recherche/03_AUDITS_CERTIFICATS/V19_REGION_COEXISTENCE_2026-10-15.md`  
Rapport historique v1 : `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md`  
Code : `/Recherche/04_CODE_DONNEES/v19_coexistence_region.py`