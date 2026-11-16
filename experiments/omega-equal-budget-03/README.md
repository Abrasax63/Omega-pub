# OMEGA-EQUAL-BUDGET-03 — contrôle à dépense d'observation égale

[Préenregistrement scientifique](PREREG_2026-11-16.md) : [commit `3fac324`](https://github.com/Abrasax63/Omega-pub/commit/3fac324fb89307d14eb152b31de3011ad4dbf9a0), créé avant le code et les résultats.

## Question
Une politique de choix d'expériences qui apprend sur les conséquences de **ses propres actions** (ON, epsilon=0,2) bat-elle la même régression de coût entraînée sur des actions uniformes (OFF), à **dépense totale de probes identique**, et transférée à deux familles de tarifs non vues ?

Comme dans les PR #127–#129, les machines de Mealy sont **connues**, à quatre états (deux entrées, trois sorties). Seul l'état initial est inconnu. Chaque probe redémarre au même état caché. **On ne prétend pas apprendre une machine inconnue, entraîner un LLM ou programmer un agent autonome.**

## Contrôle des coûts
Chaque bras reçoit le même plafond **prépayé** dans les deux environnements d'entraînement : **120+120, 240+240 ou 360+360 unités**. Le bras débite le prix réel de chaque probe. S'il ne reste pas assez pour terminer l'épisode courant, les observations partielles sont conservées **sans alimenter l'apprentissage** : pas de faux coût de retour non observé. La fraction restante est dépensée en probes réels de calibration à coût 1 sur le même monde, sans mise à jour. Les journaux distinguent `episode_cost_used`, `filler_cost`, `charged_cost`, `unspent_due_to_cohort_exhaustion`. **Égalité du budget dépensé ne veut pas dire égalité d'observations utiles, d'épisodes complets ou de CPU.** Si l'ensemble des machines s'épuise avant la dépense, la comparaison est invalidée.

Modèle et SGD restent ceux de #128 ; le choix epsilon-greedy est celui de #129. La **seule question causale** est ON (collecte guidée par modèle) contre OFF (collecte uniforme). Les références FIXED, MEMORY_OFF et MEMORY_ON sont conservées.

## Cohortes et barèmes
Deux groupes TRAIN de 64 machines distinctes, quatre ensembles EVAL (24 A, 24 B, 28 C, 28 D), tous disjoints par isomorphisme aux 362 machines de #127–#129. Trois graines d'exploration 881/882/883 se répètent sur le **même** holdout : pas d'indépendance artificielle.

- A : chaque symbole vaut 1 ; B : 0 vaut 3, 1 vaut 1 (**TRAIN**).
- C : 0 vaut 1, 1 vaut 3 ; D : chaque probe de longueur 1 vaut 2 et chaque longueur 2 vaut 1 (**EVAL réservée uniquement**).

**Critère primaire**, uniquement au budget **240+240** : moyenne ON−OFF du coût moyen d'identification sur les machines identifiables C et D, avec mêmes quatre états cachés, sur trois répétitions. Négatif = avantage descriptif ; positif = régression ; égalité = aucun avantage. La politique FIXED et les deux mémoires fortes doivent être citées, même si elles réfutent le bénéfice supposé d'ON.

Le solveur fini exact [PR #76](https://github.com/Abrasax63/Omega-pub/pull/76) est utilisé **uniquement dans la fonction d'évaluation** pour les bornes minimax, jamais pour donner des labels aux politiques pendant l'entraînement.

## Exécution
```sh
python -m unittest discover -s experiments/omega-equal-budget-03 -p test_equal_budget.py -v
python experiments/omega-equal-budget-03/equal_budget_lab.py --output /tmp/omega-budget-report.json
```

Python 3.11, bibliothèque standard uniquement ; sans API payante ni GPU. GitHub Actions doit lancer **12 tests**, les trois budgets, les trois graines, les deux familles réservées et archiver `report.json`, `summary.jsonl`, empreintes SHA256 et les épisodes favorables/défavorables.

Conserver les résultats négatifs, toutes les machines impossibles et toutes les dépenses improductives. Ne fusionner aucune PR automatiquement ; `main`, CORE et les anciens résultats restent inchangés.
