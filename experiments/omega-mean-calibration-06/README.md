# OMEGA-CALIBRATION-06 — qualité des prédictions et optimum du coût moyen

**Préenregistrement** : [commit `188336d`](https://github.com/Abrasax63/Omega-pub/commit/188336dfb8629c50e09ed8f0eb3a133e1c7e8c99), avant le code et les premiers tests. Résultats antérieurs inchangés.

## Question
La [PR #132](https://github.com/Abrasax63/Omega-pub/pull/132) a créé BELIEF_VALUE, un régresseur du coût de continuation associé aux ensembles d'états possibles d'une machine de Mealy. Il améliore TOTAL9 sur les structures de cinq états, mais ne bat pas les références fixe/mémoire. Cette expérience distingue :
1. **Prédire** : BELIEF_VALUE estime-t-il correctement la continuation d'un comportement exploratoire uniforme ?
2. **Décider** : le coût de sa politique est-il réellement plus proche de l'**optimum exact du coût moyen** que celui des références ?

Ce sont des questions indépendantes : des prévisions peuvent être bien calibrées sans donner les meilleurs choix.

## Machines et observations
On connaît la table de la machine de Mealy, **seul son état initial est caché**. Le probe reset à ce même état avant chaque entrée. Six mots autorisés `0, 1, 00, 01, 10, 11`, coût = nombre de symboles. Deux entrées, trois sorties, prior **uniforme sur les états initiaux**. Ce n'est ni l'inférence d'un automate complètement inconnu, ni la plasticité d'un LLM.

Modèles **strictement gelés** depuis #132 : exactement les mêmes **56 machines TRAIN_RANDOM4**, les graines de collecte **271, 272, 273**, `collect`, `train_shared`, sept/neuf features, SGD 0,025, kNN 7 et FIXED ; **aucun réentraînement à partir des nouveaux tests**.

Nouveaux ensembles, disjoints par signature canonique avec **858 machines des PR #127–#132** :
- **EVAL_RANDOM4** : 24 machines (seed 23117), même famille mais nouvelles.
- **EVAL_PERM5** : 30 machines à cinq états, deux actions permutations (seed 23118).
- **EVAL_RESET5** : 30 machines à cinq états, une entrée reset et une entrée cycle de cinq états (seed 23119).

Les cas non identifiables restent comptés avec abstention. Trois répétitions des modèles entraînés sur les **mêmes** machines de test — les graines ne forment pas des réplications indépendantes.

## Deux oracles exacts, exclusivement côté évaluation
**Optimum du coût moyen** : `V*(S)=min_a[c(a)+Σ_bloc (|bloc|/|S|)V*(bloc)]`, `V*({s})=0`.

**Coût attendu de l'explorateur uniforme** : `V_uniform(S)=mean_a[c(a)+Σ_bloc(|bloc|/|S|)V_uniform(bloc)]`, `V_uniform({s})=0`, somme sur les seuls probes informatifs.

Tous les calculs de ces deux oracles sont en **fractions rationnelles exactes** ; la politique optimale est rejouée pour chaque état initial pour vérifier la valeur moyenne. Les mêmes ensembles de croyances atteignables (non-singletons) servent au calcul de la MAE de calibration face à `V_uniform` et à deux références simples : ZERO=0 et SIZE=taille du groupe−1. Des trajectoires exploratoires réellement exécutées sur les nouveaux tests permettent également de mesurer une MAE empirique bruitée, **sans entrer dans l'entraînement**.

Les décisions FIXED, MEMORY, TOTAL9 et BELIEF_VALUE sont toutes évaluées sur les quatre ou cinq états initiaux de la machine ; le nouvel oracle fournit le **regret exact moyen**. Le solveur #76 reste la référence indépendante du **pire coût**, à ne pas confondre avec le coût moyen.

## Verdict gelé
Pour statut positif **`DESCRIPTIVE_CALIBRATED_MEAN_GAIN`**, sur **chacune des familles PERM5 et RESET5**, BELIEF_VALUE doit :
1. Avoir une MAE (vis-à-vis de `V_uniform`) **strictement moindre** que ZERO et SIZE.
2. Avoir un regret de coût moyen exact **strictement moindre** que TOTAL9, FIXED et MEMORY.

Tolérance flottante `1e-10`, toutes les valeurs rationnelles de l'oracle conservées. **Un seul échec → `NO_CALIBRATED_MEAN_GAIN`**. Aucun choix de seuil ni d'hyperparamètre après lecture des résultats. Une politique dépassant l'optimum moyen calculé est un **défaut d'implémentation**, pas un progrès.

## Lancer
```sh
python -m unittest discover -s experiments/omega-mean-calibration-06 -p 'test_mean_calibration.py' -v
python experiments/omega-mean-calibration-06/mean_calibration_lab.py --output /tmp/omega-mean-calibration-06.json
```

Python 3.11, bibliothèque standard, sans API payante. Workflow GitHub Actions avec **15 tests**, contrôles des partitions, des étiquettes d'état, de l'oracle moyen rationnel, des paramètres non modifiés, des écarts et des preuves brutes `report.json`, `report.sha256`, `summary.jsonl`. PR **DRAFT** sur branche empilée sur #132 ; **aucune modification de `main`**, aucune fusion.

Résultat positif ou négatif = observation de banc fini, **pas démonstration d'amélioration d'intelligence générale ou d'auto-amélioration autonome**.
