# ROUTE-02 — audit de sélection de vérifications sous budget

**12 novembre 2026 — statut : SIMULATION EXACTE EXÉCUTÉE / 0 MODÈLE / 0 API / AUCUN AVANTAGE SPÉCIFIQUE À OMEGA DÉMONTRÉ.**

## Provenance

- Protocole pré-enregistré **avant le code**, commit `f974a90e804bee7e874ff06b112310f7b58deaa1` : [prereg](EXPERIMENT_P5_ROUTING_NONTRIVIAL_PREREG_2026-11-12.md).
- [GitHub Actions 43187231019 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43187231019) : **6 tests réussis**, 256 épisodes synthétiques complets ; aucune clé ni inférence de modèle.
- [Archive JSON, 256 épisodes](https://github.com/Abrasax63/Omega-pub/actions/runs/43187231019/artifacts/13928214952) (rétention GitHub limitée).
- Empreinte SHA-256 des entrées publiques concaténées : `4a19de3a3b752d6cfb03e0b8a298802a86b3073cd79035d51dc129a74bc53ac3`.
- 128 épisodes calibrés + 128 épisodes à estimations de risque inversées, 6 hypothèses par épisode, tous `mission_type=general`. Budget 8 unités par épisode. Coût pénalisé à hauteur de 0,20 unité d'utilité par unité de vérification.
- Critère : `realized_net = somme(impact des fautes trouvées) − 0,20 × somme(coût des contrôles)`. C'est une **convention de simulation**, sans valeur monétaire ni utilité réelle mesurée.

## Résultats agrégés (utilité nette sur chaque bloc de 128 épisodes)

| Politique | Risque calibré | Risque inversé |
|---|---:|---:|
| Aucune vérification | 0,0 | 0,0 |
| Ordre fixe | 1 822,8 | 1 900,4 |
| Risque décroissant | 2 360,2 | 1 583,6 |
| Impact décroissant | 2 695,8 | **2 557,8** |
| Gain attendu/coût glouton | 2 747,6 | 2 292,0 |
| Optimiseur exact de l'utilité attendue | **2 784,2** | 2 235,0 |
| Extension candidate Omega | **2 784,2** | 2 235,0 |
| Oracle *a posteriori* non déployable | 3 318,2 | 3 455,2 |

L'extension candidate a sélectionné 401 contrôles (sur 768 hypothèses) dans chaque régime. Elle a trouvé 221 fautes quand les risques étaient calibrés et 190 lorsqu'ils étaient inversés ; elle a raté des fautes de poids total 1 363 et 2 024 respectivement.

### Contrôles appariés

- Face à l'**optimiseur exact** : **0 victoire, 128 égalités et 0 défaite**, dans chacun des deux régimes. Les deux sélecteurs donnent exactement les mêmes choix, validés par deux implémentations différentes (programmation dynamique et énumération exhaustive).
- Face au glouton gain/coût : risques calibrés, 15 victoires / 100 égalités / 13 défaites ; risques inversés, 7 victoires / 101 égalités / 20 défaites.
- Face à la priorité à l'impact : risques calibrés, 33 victoires / 72 égalités / 23 défaites ; risques inversés, 23 victoires / 61 égalités / 44 défaites.

Estimations descriptives par rééchantillonnage des **128 épisodes synthétiques** (4 000 tirages, graine fixe, intervalle percentile 95 % ; ces intervalles ne portent **pas** sur la performance dans le monde réel) :
- Extension Omega − impact d'abord, calibré : différence moyenne **+0,69** unité/épisode, intervalle **[−0,48 ; +1,82]** ; gain non robuste.
- Extension Omega − impact d'abord, risques inversés : différence moyenne **−2,52** unités/épisode, intervalle **[−4,03 ; −1,07]** ; dégradation marquée **dans ce simulateur**.
- Extension Omega − optimiseur exact : **0,00** dans chaque épisode.

## Point méthodologique central

**Le planificateur P1 actuellement présent dans Omega n'optimise pas ce choix.** La politique `omega_candidate` appelle `planner.plan_mission` pour constater le besoin de vérification et y ajoute **une nouvelle couche de programmation dynamique classique**. Cette couche reçoit, comme les autres algorithmes, une probabilité de faute fournie de l'extérieur, un impact et un coût : **elle n'apprend pas les probabilités**, ne prouve pas que le dossier est vrai ou faux, et n'exécute aucun outil de vérification réel.

Par construction, cette extension est équivalente au problème standard du sac à dos sous le modèle d'utilité pré-enregistré. Les tests l'ont confirmé ; ne pas la revendiquer comme une intelligence stratégique originale. La meilleure performance en environnement calibré repose sur des probabilités qui ont été données et conçues par l'auteur.

Le renversement en environnement à risques trompeurs démontre une faiblesse pratique possible : une stratégie optimisant **parfaitement la mauvaise estimation** peut faire moins bien qu'une heuristique rudimentaire.

## Statut et étapes scientifiques suivantes

1. **STRUCTURE VALIDÉE** : tests exhaustifs sur deux implémentations, invariance des champs visibles, coût/plafond respectés, anti-fuite des vérités cachées.
2. **SYNTHÉTIQUE UNIQUEMENT** : vérifications supposées parfaites, probabilités fournies et artificielles, résultats d'erreur simulés ; pas de holdout indépendant, pas de modèle exécuté dans ROUTE-02.
3. **AUCUNE SUPÉRIORITÉ OMEGA** : l'extension ne dépasse pas l'optimiseur standard, et perd contre `impact_first` sous décalage.
4. **PROCHAIN VERROU** : estimer la fiabilité de chaque réponse **à partir d'observations réelles et vérifiables** (contradictions de sources, preuve manquante, calculs échoués), calibrer les risques sur un échantillon distinct, mesurer le coût/erreur des vérificateurs et définir une politique d'abstention avant de tester un holdout externe.
5. **FALSIFICATION PRÉALABLE** : comparer systématiquement une politique de décision à au moins un algorithme classique fort, à l'impact d'abord, et au glouton gain/coût sur le **même** budget. Une conclusion crédible exige des cas nouveaux et une évaluation indépendante.

**Aucun dépôt CORE, `main`, PR #47–49, holdout privé ou autre infrastructure n'a été modifié.**
