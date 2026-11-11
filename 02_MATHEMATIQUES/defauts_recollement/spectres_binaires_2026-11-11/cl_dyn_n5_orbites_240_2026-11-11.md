# CL-DYN — Deux classes d’isomorphisme P3 sans P2 à cinq états

11 novembre 2026. **CALCUL EXACT** sur les endofonctions étiquetées de cinq états et les partitions non étiquetées des états. Le spectre D contient les horizons h≥1 tels que Q^h diffère de la relation observée après h pas, E_h. P3 sans P2 équivaut à D fini non vide.

## Résultats

| Catégorie | Couples étiquetés |
|---|---:|
| D vide | 54 380 |
| D fini non vide | 240 |
| D infini | 107 880 |
| Total | 162 500 |

Les 240 cas se répartissent en **deux classes d’isomorphisme**, de taille 120 chacune. Les représentants ci-dessous sont donnés dans l’ordre des états 0 à 4.

| T | Partition π | Spectre D | Taille de l’orbite |
|---|---|---|---:|
| (0,0,0,1,2) | (0,1,2,2,3) | {2} | 120 |
| (0,0,0,1,3) | (0,1,2,2,3) | {2} | 120 |

Les deux classes ont quatre blocs et un stabilisateur trivial. Leurs graphes fonctionnels sont distincts, avec une profondeur maximale de 2 et de 3 respectivement.

## Reproduction

1. Générer les 3 125 tables T et les 52 partitions de cinq états. Encoder chaque partition en renommant les blocs par ordre de première apparition.
2. Regrouper les tables par conjugaison sous S₅. Pour chaque représentant T, calculer son centralisateur C dans S₅. Grouper les partitions par l’action de C sur les états et recanoniser les noms de blocs. Une orbite de partitions de taille m contribue 120m/|C| couples au total. Le parcours donne 47 représentants de T et 1 652 représentants de couples. Le poids total est 162 500.
3. Pour chaque bloc b, partir de S=b (ensemble des microétats du bloc) et A={b} (ensemble de blocs). Comparer π(S) à A puis itérer S←T(S), A←Q(A). Le premier retour du couple (S,A) sépare le transitoire du cycle. Un écart récurrent dans au moins un bloc rend D infini. Sinon D est exactement l’union des horizons d’écart dans les transitoires. Le temps 0 est toujours égal et n’entre pas dans D.
4. Contre-vérification indépendante du découpage en orbites : parcourir directement les 162 500 couples, suivre (T^h,Q^h) jusqu’à répétition et comparer Q^h à E_h à chaque étape. Recanoniser les seuls cas finis non vides sous les 120 permutations. Les deux méthodes donnent les mêmes comptes et les mêmes deux orbites.

## Évaluation Omega et provenance

À dossier égal, deux sessions isolées ont proposé le quotient par symétries comme contrôle de repli. L’une a choisi la récurrence globale, l’autre une récurrence bloc par bloc. Les deux plans fournissent un calcul exact avec les pièces disponibles. La consigne stratégique supplémentaire n’a pas produit d’avantage mesurable sur ce cas. Le temps des sessions n’a pas été mesuré.

La [note de réconciliation CL-DYN](https://github.com/Abrasax63/Omega-pub/blob/b42b861fee12bc4e488e7f1c66e31699fe62541e/02_MATHEMATIQUES/defauts_recollement/RECONCILIATION_CL_DYN_01_04.md) rapportait déjà 240 et D={2}. La contribution de cet essai est le découpage en deux orbites et le contrôle pondéré. Le nombre historique 360 reste sans provenance primaire retrouvée. Il ne correspond pas au périmètre et aux définitions utilisés ici. Aucune modification de GitHub ni de SQLite.
