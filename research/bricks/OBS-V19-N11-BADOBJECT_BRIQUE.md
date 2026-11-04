# OBS-V19-N11-BADOBJECT — Reconstruction exacte des cinq premiers gaps au niveau des mauvais objets

**Type :** brique d'application / certificat fini  
**ID scientifique :** `OBS-V19-N11-BADOBJECT` v2  
**Statut :** CALCUL EXACT (certification interne RAVI-2)  
**Originalité :** INDÉTERMINÉE  
**Dépendances :** `BR-OBS-BAD-01`, `BR-OBS-CIRCUIT-01`.

## Domaine

Observation binaire, horizon `L=3`, cinq endofonctions historiques de taille `N=11` identifiées comme premières ruptures d'intégralité. Les mauvais objets sont les sous-espaces affines

`B_p = {c : contraintes forcées, c(T^t x)=c(T^t y), t=0,1,2}`

pour les paires non ordonnées `p={x,y}`.

## Reconstruction indépendante

Un checker nouveau, sans réutiliser les anciens solveurs V14–V17, reconstruit les contraintes forcées, canonise chaque `B_p` par RREF affine augmentée, déduplique les mauvais objets, puis résout les problèmes de 1-recouvrement, packing disjoint et 2-recouvrement.

Les nombres de mauvais objets distincts sont exactement :

`42, 36, 36, 37, 38`.

Ils coïncident avec le fichier historique des cinq premières ruptures.

Les nombres de paires propres avant déduplication sont :

`48, 48, 48, 47, 50`.

Dans ces cinq systèmes, les fibres observées de `p→B_p` ont taille 1 ou 2 et aucun mauvais objet propre ne mélange deux ombres géométriques différentes.

Depuis `OBS-V19-BAD-FIBER2`, la borne `|{p:B_p=B}|≤2` est désormais **démontrée universellement dans le domaine cohérent C5, binaire, L=3, pour les mauvais objets non vides à ombre propre**. Les nombres particuliers de fibres de cette carte restent cependant des `CALCUL EXACT` propres aux cinq systèmes.

## Gap d'intégralité recertifié

Pour chacun des cinq systèmes, le checker établit exactement :

- aucune partition exacte des mauvais objets ;
- taille maximale d'une famille de mauvais objets deux à deux disjoints : `7` ;
- existence d'un 2-recouvrement exact par `16` mauvais objets distincts ;
- rang des 16 colonnes centrées : `15` ;
- nullité : `1` ;
- noyau positif correspondant au 2-recouvrement ;
- graphe de chevauchement du témoin reconstruit non biparti.

Les cinq supports déterministes reconstruits possèdent un cycle impair de longueur 5. La non-bipartition, et non ce choix particulier de longueur, est l'invariant causal pour l'absence de partition selon `BR-OBS-CIRCUIT-01`.

## Représentation C5

Les supports exacts de 2-recouvrement ne sont pas uniques. Les témoins générés par le nouveau checker se projettent sur des profils `8 lignes + 8 plans` ou `6 lignes + 10 plans`, compatibles avec les familles déjà observées dans V16/V17. Le fait qu'un même système puisse fournir plusieurs circuits selon l'objectif du solveur reste inchangé.

## Limites

- Certification finie sur les cinq mappings `N=11`, pas sur les 34 cas `N=12`.
- La borne universelle fibre≤2 est maintenant fournie séparément par `OBS-V19-BAD-FIBER2`; cette carte N11 ne dépend pas causalement de ce théorème pour ses comptages, qui restent reconstruits directement.
- Le résultat ne classe pas tous les circuits positifs d'un système donné.
- Les coefficients algébriques d'un circuit restent distincts du nombre de paires préimages (`BR-OBS-CAP-02`).

## Provenance

Source historique copiée : `/Recherche/04_CODE_DONNEES/V19_N11_SOURCE_MAPPINGS_2026-10-15.csv`  
Checker : `/Recherche/04_CODE_DONNEES/v19_badobject_n11_exact.py`  
Résultats : `/Recherche/04_CODE_DONNEES/V19_N11_BADOBJECT_RECONSTRUCTION_2026-10-15.csv`  
Témoins : `/Recherche/04_CODE_DONNEES/V19_N11_2COVER_WITNESSES_2026-10-15.json`  
Audit : `/Recherche/03_AUDITS_CERTIFICATS/V19_BADOBJECT_N11_2026-10-15.md`.

## Relation au théorème fibre≤2

Cette carte **illustre** `OBS-V19-BAD-FIBER2` mais n’en dépend pas pour sa certification finie : ses 42/36/36/37/38 objets et ses fibres sont recomptés directement par le checker N11.