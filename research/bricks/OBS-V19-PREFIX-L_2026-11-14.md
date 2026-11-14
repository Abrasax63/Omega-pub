# V19 — borne inférieure sur la longueur du préfixe

14 novembre 2026. Base `c6323404ac2ac22b667a7b27b0daf42ac06e5aea`. Le [cycle précédent](OBS-V19-LPLUS1-PATHS_2026-11-14.md) fixe la définition d’extension globale, les hypothèses, et les sources épinglées des PR #2, #5 et #18. On conserve le cycle distingué et les deux trajectoires étiquetées jusqu’au temps indiqué, inclus.

## Résultat démontré pour L=2

Sur X={0,…,8}, prendre B=(0,1,2), la paire (0,6) et les applications suivantes, données par leurs valeurs dans l’ordre de X :

- T=(1,2,0,4,3,0,3,5,6).
- U=(1,2,0,3,4,0,3,5,6).

Le cycle et les préfixes jusqu’au temps L−1 sont identiques : (0,1) et (6,3). Dans T, les arêtes forcées sont (2,5), (3,4), (4,6), de parité 1. Dans U, elles sont (2,5), (3,4), (3,6), de parité 1. Les deux graphes forcés sont des chemins disjoints, donc cohérents. Les égalités événementielles imposent c(0)=c(6) et c(1)=c(3). Pour T, le chemin 3–4–6 impose c(3)=c(6) et donc c(0)=c(1). Pour U, l’arête 3–6 impose c(0)≠c(1). Dans les deux cas ces conditions suffisent pour étendre la coloration : fixer c(5)=1−c(2) et c(4)=1−c(3), puis appliquer les deux égalités événementielles. Les ombres sont distinctes, respectivement les masques {0,3,4,7} et {1,2,5,6}, le bit i désignant c(i). Par conséquent, le cycle et les préfixes au temps L−1 ne déterminent pas toujours l’ombre.

## Calcul fini pour le temps L

Sur la famille de 20 systèmes à neuf états du cycle précédent, pour toutes les paires et L=2,3,4,5, la projection exhaustive du sous-graphe visible au temps L correspond à l’ombre globale dans les 2 880 cas. Au temps L−1, elle diffère dans 68 cas. Le garde concorde avec l’oracle sur les 5 760 projections locales. Le lot reprend la famille précédente et teste deux nouvelles troncatures. Temps observé du balayage avec oracle : 2,267 s sur le premier passage. Aucun changement du vérificateur.

Depuis `research/code` :

```sh
python3 audit_v19_prefix_l.py
python3 audit_v19_lplus1_paths.py
python3 audit_v19_shadow_guard.py
python3 test_v19_locality_l_plus_1.py
```

Les trois contrôles existants passent. SHA-256 du harnais `1d9e277d88f7329fdf6d3546bfeaf1bb57c697cde1f0a30c0d959ff53899f8fd`.

Suffisance générale de L : conjecture ouverte. La borne inférieure démontrée est au temps L pour L=2. Originalité bibliographique non évaluée. Prochain test mathématique : examiner si un noyau invariant devenu invisible au temps L peut relier deux ancrages dont la relation n’est pas déjà imposée par les égalités événementielles. Prochain cycle : provenance.
