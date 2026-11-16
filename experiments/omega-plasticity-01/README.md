# OMEGA-PLASTICITY-01 — apprendre, s'adapter et réapprendre sans oracle d'entraînement

Expérience **préenregistrée le 16 novembre 2026** au [commit a97fff4](https://github.com/Abrasax63/Omega-pub/commit/a97fff4b57bebb01ed28c412d05f1e66a9e2cb9f), avant toute implémentation et tout test GitHub.

## Objet précis
On réutilise **sans modification** les machines de Mealy déterministes de [PR #127](https://github.com/Abrasax63/Omega-pub/pull/127), avec quatre états, deux entrées, trois sorties, six probes de longueur 1 ou 2. Chaque probe repart du **même état initial caché**. La table de transitions et de sorties est **connue** ; il ne s'agit PAS d'apprendre le modèle de la machine depuis une boîte noire. La tâche est uniquement d'identifier l'état initial au moindre coût.

Les expériences A et A' coûtent 1 unité par symbole (probes de longueur 1 coût 1 ; longueur 2 coût 2). En B, une requête simple coûte 3 et un lot de deux symboles coûte 1 : **seul le tarif exogène change**, pas les automates. Il s'agit de coûts synthétiques, non de coûts CPU.

La question : **un contrôleur qui a appris à partir d'expériences réellement observées en A puis B retrouve-t-il de bonnes décisions sur des nouvelles machines A' plus vite qu'un contrôleur identique qui repart de zéro ?**

## Politique et comparaison
- **FIXED** : séparateur Gini/coût inchangé.
- **MEMORY** : k=7 voisins sur les mêmes traces d'expériences réalisées, sans paramètres appris.
- **WARM** : politique linéaire de 9 features, entraînée en ligne par régression du coût réellement observé à partir des épisodes A puis B, puis A'.
- **COLD** : même architecture, paramètres initiaux nuls, entraînée exclusivement sur les **mêmes expériences A'**, dans le même ordre que WARM.

**Aucun optimum oracle ni label d'action optimale n'entre dans WARM ou MEMORY.** Un comportement exploratoire uniforme, à graine fixe, génère un jeu d'épisodes **commun** aux deux contrôleurs. Le simulateur seul connaît l'état caché et délivre la réponse à la requête effectivement choisie. L'algorithme dispose de la table connue, des coûts, de l'historique réel et des états encore possibles, **jamais de l'état caché**.

Le solveur exact [PR #76](https://github.com/Abrasax63/Omega-pub/pull/76) est appelé **exclusivement pendant l'évaluation** pour certifier l'identifiabilité et calculer les bornes minimax du pire coût, pas pour entraîner les stratégies. Des tests rejettent les fuites accidentelles.

## Cohortes fixées
| Phase | Nombre | Graine | Coût |
|---|---:|---:|---|
| TRAIN_A | 36 | 3017 | A |
| TRAIN_B | 36 | 4017 | B |
| RELEARN_A | 16 | 5017 | A' |
| EVAL_A | 18 | 6017 | A |
| EVAL_B | 18 | 7017 | B |
| EVAL_Aprime | 24 | 8017 | A' |

Les machines sont exclues si isomorphes par renommage d'états à l'une des autres machines **ou aux 90 machines déjà employées par #127**. Chaque machine non identifiable demeure dans les comptages et entraîne une abstention justifiée. Chacune des machines identifiables est évaluée sur **ses quatre états initiaux**.

## Mesures verrouillées avant le premier run
- Primaire : différence moyenne WARM−COLD sur EVAL_Aprime aux trois checkpoints **0/8/16** machines de réapprentissage. Négatif = meilleur coût moyen WARM **descriptif**, pas généralisation prouvée.
- Rétention : différence de coût WARM sur le **même EVAL_A** après B vs après A (positif = oubli/dégradation).
- Plasticité : coût WARM sur EVAL_Aprime après 16 vs au début du réapprentissage (négatif = amélioration).
- Adaptation : coûts FIXED/MEMORY/WARM sur EVAL_B après TRAIN_B.
- Nouvelles informations : nombre d'exemples et de mises à jour, poids avant/après et SHA, cas favorables/défavorables, coût minimax, abstentions.
- Règles : résultats négatifs archivés, **aucune sélection de cas après résultat**, pas de modification des hyperparamètres sur ce holdout.

## Exécuter
```sh
python -m unittest discover -s experiments/omega-plasticity-01 -p 'test_plasticity.py' -v
python experiments/omega-plasticity-01/plasticity_lab.py --output /tmp/omega-plasticity-report.json
```
Python 3.11, bibliothèque standard uniquement, aucune API payante ni modèle externe. GitHub Actions `.github/workflows/omega-plasticity-01.yml` exige **15 tests** puis conserve `report.json`, son SHA-256 et les résultats des trois phases.

## Portée scientifique et limites
Le pilote teste **l'effet d'une histoire d'apprentissage sur le réapprentissage** au sens strict, pas la plasticité d'un grand réseau ni une capacité de découverte de théorie. WARM a vu les épisodes A+B ; COLD non : la comparaison n'est pas une égalité de quantité totale de données historiques. Elle est équitable sur le **jeu d'expériences marginales A'**, rigoureusement identique. Les programmes ont des coûts de calcul différents non égalisés ; le coût du benchmark est celui des probes. Aucune modification du modèle de langage, aucune fusion ni modification de `main` et des PR #76/#127.
