# Test d'optimalité — préfixe L+1 contre L+2

**Date :** 10 novembre 2026  
**Branche :** `work/omega-locality-lplus1-optimality-2026-11-10`  
**Base :** `work/omega-locality-proof-independent-r2-2026-11-10`  
**Question testée :** le préfixe jusqu'à (T^{L+1}) suffit-il déjà à déterminer l'ombre globale, ou existe-t-il un contre-exemple qui impose (L+2) ?

## Convention non ambiguë

Le préfixe « L+1 » désigne exactement les états aux temps (0,1,ldots,L+1), soit (L+2) états par orbite. L'événement conserve les égalités aux temps (0,ldots,L-1). Le modèle local conserve les contraintes forcées dont les deux extrémités sont dans l'union de ces préfixes et du cycle (B). Il est comparé à l'ombre obtenue avec toutes les contraintes forcées globales et les mêmes égalités événementielles.

Cette convention est distincte du préfixe L+2 précédent, qui allait jusqu'au temps (L+2).

## Protocole indépendant

Le script `research/code/test_v19_locality_l_plus_1.py` ne réutilise aucun code V19 antérieur. Il reconstruit directement :
- les arêtes de fusion (T(u)=T(v)) ;
- les arêtes d'invariance ({T(u),T(v)}={u,v}) ;
- la cohérence par propagation XOR ;
- les cycles de longueur au moins 3 ;
- les égalités événementielles ;
- l'ombre par énumération des colorations du cycle et propagation des contraintes.

Énumération exhaustive des applications (T:[n]	o[n]), pour (1leq nleq6), puis, pour tout système cohérent avec cycle de longueur au moins 3, toutes les paires non ordonnées et (L=2,3).

## Résultat local calculé

Aucun contre-exemple L+1 n'a été trouvé dans ce domaine fini.

- Applications cohérentes par taille : (1,4,23,191,2069,27454), pour (n=1,ldots,6).
- Systèmes cohérents possédant un cycle (qgeq3), pour (n=3,ldots,6) : (2,38,614,10384).
- Comparaisons global/local : (12,456,12280,312720), soit **325 468** comparaisons.
- Les ombres globales et locales coïncident dans les 325 468 cas.

Le workflow CI doit reproduire ces comptes avant que le résultat soit considéré comme reproductible.

## Interprétation — ne pas surconclure

Ce test **ne démontre pas** que L+1 suffit universellement. Il ne démontre donc pas non plus que L+2 est non optimal. Il établit seulement qu'aucun témoin d'échec L+1 n'existe dans l'espace exhaustif testé ((nleq6), (L=2,3)).

À ce stade, l'optimalité de L+2 reste **INDÉTERMINÉE**. Deux voies restent ouvertes :
1. établir un théorème L+1 sous les hypothèses exactes, ce qui rendrait la borne L+2 non optimale ;
2. construire un contre-exemple L+1, éventuellement dans une famille paramétrée, ce qui établirait la nécessité de L+2 dans au moins ce régime.

Le lemme orbital de la preuve L+2 mentionne une transition pouvant nécessiter trois itérations depuis une feuille d'un P4. Cela ne suffit pas à prouver qu'une telle transition change l'ombre projetée : les extrémités pertinentes et les données du cycle peuvent rendre cette information redondante. Le résultat fini observé renforce précisément cette réserve.

## Statut

- Test exhaustif fini L+1, (nleq6), (L=2,3) : **CALCUL EXACT**, sous réserve de succès CI.
- Existence d'un contre-exemple L+1 dans ce domaine : **RÉFUTÉE** par l'énumération exhaustive.
- Suffisance universelle de L+1 : **INDÉTERMINÉE**.
- Optimalité universelle de L+2 : **INDÉTERMINÉE**.
- Aucun ajout à la bibliothèque certifiée ; aucune fusion.


## Reproduction CI

Le workflow GitHub Actions [run 42788979270](https://github.com/Abrasax63/Omega-pub/actions/runs/42788979270) a terminé avec **SUCCESS** sous Python 3.12. Il exécute successivement l'audit indépendant L+2 existant puis le nouveau script L+1. Le nouveau script a donc été exécuté dans la CI ; les assertions de comptes et l'absence de divergence ont passé.

Cette CI confirme la reproduction du test fini décrit ici. Elle ne modifie pas le statut logique : la suffisance universelle de L+1 et l'optimalité universelle de L+2 restent **INDÉTERMINÉES**.
