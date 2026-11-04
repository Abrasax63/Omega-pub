# RAVI-2 — borne de Helly du nerf de compatibilité Mealy

Date : 16 octobre 2026  
Commit proposé : `COMMIT-RAVI2-2026-10-16-MEALY-HELLY-19`

## Objet

Fermer le verrou ouvert « complexes de compatibilité / bornes de type Helly » du programme Mealy27 sans reformuler le spectre de conflits déjà présent.

Le résultat porte sur **tout** état de connaissance accessible et toute entrée, pas seulement sur le nœud spécial extrait d'une ADS sans PDS dans `OBS-M27-CONFLICT`.

## Énoncé

Soit une machine de Mealy finie, complète et déterministe, avec alphabet de sorties `Γ`, `q=|Γ|`, et langage observable exactement 1-step (`r_IO=1`). Fixons un état de connaissance accessible `K` et une entrée `a`.

Pour chaque sortie `y` telle que `K(a,y)` est non vide et possède un langage de résolution preset non vide `R_y = R(K(a,y))`, définir le nerf

`N_res(a,K) = { S : intersection_{y in S} R_y != empty }`.

Alors :

1. toute non-face minimale de `N_res(a,K)` a une taille au plus `q-1` ;
2. équivalemment, la famille `{R_y}` est **(q-1)-Helly** : si toute sous-famille d'au plus `q-1` langages a une intersection non vide, alors l'intersection de toute la famille est non vide ;
3. pour `q=2`, la famille est 1-Helly : l'individualité des résolveurs suffit déjà à un résolveur commun ;
4. pour chaque `q>=3`, la borne `q-1` est optimale : la famille `C(q,q-1)` possède un nerf racine dont l'unique non-face minimale a taille `q-1` ; plus généralement chaque arité `k in {2,...,q-1}` est réalisable par `C(q,k)`.

## Preuve

Soit `C` une non-face minimale du nerf restreint aux branches individuellement résolubles. Chaque singleton appartient au nerf par définition.

Une branche contenant une seule identité initiale a `R_y = Sigma*`; elle ne peut donc être indispensable dans une non-face minimale, car sa suppression ne change aucune intersection. Ainsi chaque branche essentielle de `C` contient au moins deux identités encore à distinguer.

Comme `R_y` est non vide, il existe un mot preset qui résout cette branche. Deux identités de la branche produisent donc deux sorties futures différentes sous un même mot futur : le symbole de sortie `(a,y)` est **fertile** au sens de `OBS-M27-FERTILE`.

Toutes les branches d'une non-face minimale sont donc des sorties fertiles de la même entrée `a`. Sous `r_IO=1`, `OBS-M27-FERTILE` donne au plus `q-1` sorties fertiles. D'où `|C| <= q-1`.

La formulation de Helly est équivalente : si l'intersection totale était vide, une sous-famille minimale d'intersection vide existerait ; la preuve précédente impose qu'elle ait taille au plus `q-1`.

Pour la sharpness, `OBS-M27-SPECTRUM` fournit `C(q,k)`. Après l'entrée racine `a`, les `k` branches paires sont individuellement résolubles. Toute sous-famille propre omet un indice `j` et le mot `t_j` résout simultanément toutes ses branches ; la famille complète n'a aucun résolveur commun. Le nerf possède donc une non-face minimale de taille `k`. En prenant `k=q-1`, la borne de Helly est atteinte.

## Validation indépendante exécutée

Un programme indépendant de la preuve et des anciens certificats a reconstruit les machines `C(q,k)` pour `q=3..8` et tous `2<=k<=q-1`.

Il ne vérifie pas seulement le nerf racine :

- il parcourt tous les états de connaissance accessibles ;
- il décide l'existence d'un PDS commun par BFS sur les blocs d'identités encore non séparées ;
- il reconstruit tous les nerfs des branches individuellement résolubles ;
- il énumère toutes les non-faces minimales.

Résultats :

- 21 machines `C(q,k)` ;
- 492 états de connaissance accessibles ;
- 1 337 couples `(K,a)` avec nerf effectivement testé ;
- aucune non-face minimale de taille supérieure à `q-1` ;
- maximum observé : 7 pour `q=8` ;
- pour chaque cas, le nerf racine possède la non-face attendue de taille exactement `k`.

Sortie : `/MEALY_HELLY_RESULTS_2026-10-16.json`.

## Audit de redondance

`OBS-M27-CONFLICT` prouve qu'une ADS sans PDS **produit quelque part** un noyau de conflit de taille `2..q-1`. Il ne formule pas une propriété de Helly valable pour tout `(K,a)`.

`OBS-M27-SPECTRUM` construit les exemples `C(q,k)` et réalise les arités permises, mais ne donne pas à lui seul la borne universelle pour un nerf arbitraire.

La présente brique est donc un corollaire de raccordement : elle transforme la largeur fertile en une propriété structurale globale de tous les nerfs de branches individuellement résolubles et utilise le spectre pour prouver l'optimalité.

Le manuscrit *Adaptivity boundary - Mealy machines* pose explicitement comme question ouverte la recherche de bornes de Helly **plus petites que** `|Gamma|-1` sous hypothèses supplémentaires ; il ne contient pas cet énoncé comme théorème autonome. Une recherche bibliographique ciblée sur les formulations Mealy/ADS/PDS/Helly n'a pas localisé l'énoncé exact. C'est une absence de correspondance, pas une preuve de nouveauté.

## Statut proposé

`BR-MEALY-HELLY-01 v1` : **DÉMONTRÉ interne**.

Originalité : **INDÉTERMINÉE** ; aucune priorité revendiquée.

Dépendances causales minimales :

- `BR-MEALY-HELLY-01 DEPEND_DE OBS-M27-FERTILE` ;
- `BR-MEALY-HELLY-01 DEPEND_DE OBS-M27-SPECTRUM`.

`OBS-M27-CONFLICT` reste un corollaire/application importante mais n'est pas requis comme prémisse de la preuve générale.

## Limites

- machine finie, complète, déterministe ;
- `r_IO=1` exact ;
- nerf restreint aux branches dont le langage de résolution preset est non vide ;
- la borne porte sur le nombre de branches/langages, pas sur la longueur du résolveur commun ni la complexité algorithmique de le trouver ;
- aucune borne plus petite que `q-1` n'est affirmée sans hypothèse supplémentaire ;
- aucune nouveauté externe certifiée.

## Reproduction

- script : `/Recherche/04_CODE_DONNEES/mealy_helly_bridge.py`
- résultats : `/MEALY_HELLY_RESULTS_2026-10-16.json`
- archive : `/PREUVES_MEALY_HELLY_2026-10-16.zip`