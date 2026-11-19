# V19 — le temps L+1 est nécessaire dans le pire cas

17 novembre 2026, cycle mathématique. Branche `work/omega-math-brick-pilot-2026-11-14`, base `0442190f890d892507d691ea0f1f59277aa85a03`. Dernier cycle de provenance : `20a23455c9f7470c409e5904b6b92f60e850109c`. Le [dernier cycle mathématique](OBS-V19-PREFIX-L_2026-11-14.md) distinguait L−1 de L. Sources : [fiche d’audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [définition et structure #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/02_MATHEMATIQUES/defauts_recollement/AUDIT_INDEPENDANT_LOCALITE_V19_L_PLUS_2_2026-11-05.md), [test #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/research/code/test_v19_locality_l_plus_1.py). L’ombre est l’ensemble des colorations de B qui s’étendent à des solutions de toutes les contraintes forcées et événementielles.

## Question et test

Hypothèse à réfuter : sur les endofonctions cohérentes au sens des contraintes forcées, B et les deux préfixes étiquetés jusqu’au temps L déterminent l’ombre. Avant exécution, fixer deux endofonctions sur dix états, L=2, B=(0,1,2), paire (8,9), et utiliser l’énumération exhaustive des 1 024 colorations par système comme oracle. Le cas négatif attendu est une ombre vide. Critère de réfutation : mêmes données observables, deux ombres distinctes.

- T=(1,2,0,3,4,0,3,4,6,7).
- U=(1,2,0,4,5,3,3,4,6,7).

Les préfixes communs sont (8,6,3) et (9,7,4), ainsi que le cycle B. T a le chemin forcé 6–3–4–7, avec une inégalité par arête. Il impose c(6)≠c(7), alors que l’événement exige c(6)=c(7) et c(8)=c(9). L’ombre est vide. U a deux arêtes forcées disjointes (3,7) et (5,6). La coloration c(6)=c(7)=c(8)=c(9)=0, c(3)=c(5)=1, c(4)=0 permet toute coloration de B. Les deux graphes forcés sont cohérents.

**RÉFUTÉ** : la suffisance informationnelle de L. **VÉRIFIÉ par calcul exact** : 0 contre 8 masques. Même en restreignant les arêtes globales au même ensemble visible, le test obtient 0 et 8. Les arêtes ont été calculées à partir de T ou U en entier avant restriction. Leur disponibilité n’est pas garantie par le préfixe au temps L, ce qui explique pourquoi un test global/induit pouvait trouver zéro divergence.

## Borne supérieure, argument soumis à revue

Reprendre la structure de la PR #5 : une composante forcée est un chemin, avec au plus une arête centrale d’invariance et une feuille de fusion par extrémité. Soit A l’ensemble des ancrages, constitué de B et des états rencontrés jusqu’au temps L−1. Poser K=A∪T(A). Le préfixe jusqu’à L+1 donne l’image de chaque sommet de K, les images dans B étant connues. On peut donc reconstruire les arêtes forcées entre sommets de K.

Tout chemin forcé entre deux ancrages est dans K. Pour une arête seule, ses extrémités sont ancrées. Pour un noyau de deux points fixes, chaque sommet interne du noyau est l’image de la feuille ancrée à son extrémité, ou est déjà ancré. Pour un noyau formé d’un 2-cycle, considérer un sommet interne v du noyau et le côté opposé du chemin : l’extrémité ancrée est le partenaire w de v ou sa feuille de fusion. Dans les deux cas son image vaut v. Les relations forcées entre ancrages sont donc reconstructibles sur K. La cohérence de F autorise l’extension sur les composantes sans ancrage. Les égalités événementielles portent exclusivement sur A. La projection sur B est donc déterminée par ces données. Sous ces hypothèses, L+1 est une borne uniforme, et le témoin établit qu’on ne peut uniformément la réduire à L. L’optimalité pour chaque L séparément et l’originalité bibliographique restent à examiner.

## Rejeu

Depuis `research/code` :

```sh
python3 audit_v19_prefix_information.py
python3 audit_v19_shadow_guard.py
python3 test_v19_locality_l_plus_1.py
```

Témoin exact et contrôles terminés. Le garde retrouve les deux ombres et donne zéro écart sur ses 4 536 projections réservées. La campagne historique termine ses 325 468 comparaisons, selon sa propre sémantique. Aucun changement du vérificateur. Temps du témoin et de ses vérifications : 0,039 s localement. SHA-256 du harnais : `0b1ae9422ac559107fae7618ff1122ff1f66bea2a1f851ea3f06e7eb4e7cbcca`.

Prochain test mathématique : implémenter un contrôle qui reçoit seulement B et les préfixes, reconstruit F sur K et vérifie sa concordance avec l’oracle sur une famille distincte, puis rechercher une généralisation du témoin à L arbitraire. Prochain cycle de l’alternance : provenance.
