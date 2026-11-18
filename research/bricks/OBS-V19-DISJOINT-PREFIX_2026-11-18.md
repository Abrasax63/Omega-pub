# V19 — deux terminaux distincts inconnus imposent des préfixes disjoints

18 novembre 2026, 10 h 32 (Paris). Branche `work/omega-math-brick-pilot-2026-11-14`, départ [2388771](https://github.com/Abrasax63/Omega-pub/commit/2388771cbb79014e83e9baaefb1906835b395a30), [dernier calcul](OBS-V19-GROUPED-FIRST-READ_2026-11-18.md). [Dernier cycle de provenance](https://github.com/Abrasax63/Omega-pub/commit/2c620e141c0b365a8c196e6e84a6c1669d58722a).

L’ombre globale est la projection sur le cycle des colorations extensibles à toutes les contraintes. Sources : [fiche d’audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index historique #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Question : deux chemins au même horizon peuvent-ils se croiser alors que leurs terminaux restent distincts et inconnus ? Une image est déjà connue si son origine appartient aux sources du préfixe, ou au cycle distingué observé. Critère de réfutation : un croisement qui conserve les deux terminaux admissibles. Budget fixé avant exécution : tous les prolongements de trois patrons à horizon 2 avec C4 et 10 états. Témoin disjoint pour valider le filtre. Référence : transitions effectivement lues sur les deux chemins et le cycle.

| Patron | Complétions | Cohérentes | Terminaux admissibles |
| --- | ---: | ---: | ---: |
| Croisement décalé | 1 000 | 800 | 0 |
| Croisement simultané | 1 000 | 599 | 0 |
| Chemins disjoints | 100 | 92 | 92 |

Le témoin disjoint donne 148 premières lectures qui sortent des terminaux. Les patrons croisés n’atteignent pas le seuil d’admissibilité à la projection. Temps du calcul 0,027 s.

**Preuve du lemme de disjonction.** Soient les préfixes `x_i=T^i(x)` et `y_i=T^i(y)` pour `0 ≤ i ≤ L`. Supposons `x_i=y_j`. Si `i=j`, la déterministicité donne `x_L=y_L`. Si `i<j`, itérer `L−j` fois donne `y_L=x_{i+L−j}` avec `i+L−j<L`. La transition en ce sommet est donc lue dans le premier préfixe. Si `j<i`, le même raisonnement donne que la transition issue de `x_L` est déjà lue. Chaque possibilité contredit deux terminaux distincts et inconnus. Ce lemme utilise seulement la déterministicité et l’horizon commun. La suffisance de la première lecture hors terminaux reste indéterminée dans le cas disjoint. Originalité non évaluée.

**EXÉCUTÉ**, calcul exact fini en plus de la preuve structurelle. Le garde existant concorde à nouveau avec le projecteur exhaustif sur 2 projections du témoin à cinq états et 4 536 de la famille C5. Le test de lecture simple passe. Aucun changement du vérificateur.

Rejouer depuis `research/code` avec `python audit_v19_crossed_prefix.py`, `python audit_v19_shadow_guard.py`, `python audit_v19_single_read.py`. SHA-256 du nouveau harnais `ede52806f04f50f43d791a98d8cede0751e5ad95170a52637500586304673ea9`.

Prochain test mathématique : reprendre la comparaison groupée sur C4 avec des chemins disjoints, en réservant un état hors des chemins afin de varier sa transition en même temps que celle du terminal non lu. Prochain cycle alterné : provenance.
