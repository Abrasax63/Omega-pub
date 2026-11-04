# BR-AFFINE-GAUGE-CORE v1

Diagnostic de translation commune ou noyau minimal d'étiquettes

Statut : **DÉMONTRÉ interne**.  
Originalité : **CONNU_OU_CLASSIQUE / APPLICATION_INTERNE** ; aucune priorité revendiquée.

## Énoncé

Pour une famille finie de sous-espaces `S_i <= F_2^d` et de phases linéaires `delta_i:S_i→F_2` relevant du contrat de `BR-AFFINE-GAUGE-GLUE`, choisir une base `B_i` de chaque `S_i` et former les groupes

`E_i={g·s=delta_i(s):s∈B_i}`

en la translation commune inconnue `g`.

- Une translation commune existe ssi l'union des `E_i` est compatible.
- Le verdict ne dépend pas du choix des bases.
- Si elle n'existe pas, `BR-AFFINE-GROUP-CORE` fournit un ensemble d'étiquettes minimal par inclusion sans translation commune, avec certificat XOR `0=1` et témoin de translation après retrait de chaque étiquette retenue.
- Un tel noyau peut être choisi de taille `<= d+1`, borne serrée.

## Domaine

- `F_2`, dimension finie ;
- familles affines cohérentes ;
- mêmes espaces de lignes par étiquette ;
- phases relatives linéaires ;
- minimalité par inclusion uniquement.

## Validation

242 270 familles exhaustives, dont 160 754 incompatibles ; 10 000 familles aléatoires supplémentaires ; 5 000 changements de base ; trois méthodes indépendantes (brute force, relations XOR, élimination avec provenance). Aucun échec.

## Provenance

Rapport : `/GAUGE_CORE_BRIDGE_2026-10-16.md`  
Résultats : `/GAUGE_CORE_BRIDGE_RESULTS_2026-10-16.json`  
Dépendances : `BR-AFFINE-GAUGE-GLUE`, `BR-AFFINE-GROUP-CORE`  
Commit : `COMMIT-RAVI2-2026-10-16-AFFINE-GAUGE-CORE-18`