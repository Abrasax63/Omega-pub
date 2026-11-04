# BR-AFFINE-TREE-CORE v1

Diagnostic complet sur arbre : composition ou noyau incompatible minimal

Statut : **DÉMONTRÉ interne**.  
Originalité : **CONNU_OU_CLASSIQUE / APPLICATION_INTERNE** ; aucune priorité revendiquée.

## Énoncé

Pour une famille finie de relations affines sur `F₂` portée par un arbre satisfaisant l'intersection courante :

- le filtrage exact de `BR-AFFINE-TREE-GLUE` décide le joint global et fournit le comptage/prolongement lorsque le joint est non vide ;
- si le joint est vide, représenter chaque module par son groupe équivalent d'équations affines puis appliquer `BR-AFFINE-GROUP-CORE` fournit un sous-ensemble de modules minimal par inclusion dont la conjonction est incompatible, avec certificat XOR `0=1` et témoin satisfaisant après suppression de chaque module retenu.

Le résultat donne donc un certificat positif ou négatif dans le même pipeline, sans conclure à une minimalité en cardinalité.

## Domaine et hypothèses

- relations affines binaires finies ;
- variables partagées identifiées littéralement ;
- arbre de portées vérifiant l'intersection courante ;
- représentation exacte de chaque relation par ses équations affines ;
- contrats de `BR-AFFINE-TREE-GLUE` et `BR-AFFINE-GROUP-CORE`.

## Validation

Validation exhaustive sur 15 972 familles : 15 972 verdicts concordants avec énumération brute ; 7 470 joints vides ; 7 470 noyaux minimaux par inclusion vérifiés indépendamment par suppression et énumération. Représentation équationnelle locale vérifiée exactement pour chaque module traité.

## Limites

Aucune extension aux relations non affines, aux hypergraphes cycliques généraux, à la minimalité de cardinalité, à un gain de complexité, ni à une loi universelle de composition de briques.

## Provenance

Rapport : `/AFFINE_TREE_CORE_BRIDGE_2026-10-16.md`  
Archive : `/PREUVES_AFFINE_TREE_CORE_BRIDGE_2026-10-16.zip`  
Dépendances : `BR-AFFINE-TREE-GLUE`, `BR-AFFINE-GROUP-CORE`  
Commit : `COMMIT-RAVI2-2026-10-16-AFFINE-TREE-CORE-17`