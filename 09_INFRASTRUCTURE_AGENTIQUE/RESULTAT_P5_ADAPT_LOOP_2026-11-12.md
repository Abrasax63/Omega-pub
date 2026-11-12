# P5-ADAPT-01 — audit de la boucle adaptative

**12 novembre 2026. Verdict : HYPOTHÈSE D'AVANTAGE RÉFUTÉE DANS CETTE SIMULATION ; toute généralisation à Omega sur problèmes réels reste INDÉTERMINÉE.**

## Sources vérifiables

- Pré-enregistrement **avant code et résultats** : [EXPERIMENT_P5_ADAPT_LOOP_PREREG_2026-11-12.md](EXPERIMENT_P5_ADAPT_LOOP_PREREG_2026-11-12.md), commit `a4e610f0038a3e630c47148fc3346499463caf5b`.
- [GitHub Actions run 43192601799 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43192601799), 7 tests unitaires réussis sur Python 3.12, 128 épisodes synthétiques terminés.
- [Archive JSON des trajectoires et agrégats](https://github.com/Abrasax63/Omega-pub/actions/runs/43192601799/artifacts/13932151093) (rétention GitHub limitée).
- Empreinte monde : `20de3c956fe0570969b438353b04c9f8297031f15cf98f7c689c9f842f7b825f`.
- **0 génération de modèle de langage / 0 API payante / 0 données privées / 0 calcul sur smartphone.**
- 4 régimes × 32 épisodes × 180 décisions × 10 politiques = **230 400 décisions simulées**.

## Résultat primaire : pseudo-regret dynamique moyen sur 180 décisions

**Plus petit = meilleur.** Les meilleurs témoins sont identifiés **a posteriori par régime** et ne représentent donc pas une seule stratégie déployable connaissant d'avance l'environnement.

| Régime | Meilleur témoin classique | Score témoin | Omega candidat | Sans mémoire | Sans rollback | Delta Omega − témoin |
|---|---|---:|---:|---:|---:|---:|
| Stable | UCB stationnaire | **23,872** | 50,139 | 52,343 | 47,856 | +26,267 |
| Ruptures brutales | Toujours vérifier | **16,800** | 44,004 | 44,897 | 40,053 | +27,204 |
| Situations récurrentes | UCB stationnaire | **47,727** | 60,700 | 59,850 | 54,238 | +12,973 |
| Changement progressif | Toujours vérifier | **1,097** | 47,043 | 47,172 | 44,118 | +45,946 |

**Le candidat ne bat le meilleur témoin classique dans aucun des quatre régimes en moyenne.** Comparaisons appariées des 32 réalisations : 0/32 victoires en stable, abrupt, progressif ; **3 victoires / 29 défaites** en récurrent. C'est un résultat de falsification sur cet environnement synthétique, pas une preuve qu'Omega ne possède aucune valeur dans l'absolu.

### Alarmes et mémorisation

| Régime | Nombre d'alarmes Omega (32 épisodes) | Retours arrière Omega | Différence moyenne de regret candidat − sans rollback |
|---|---:|---:|---:|
| Stable | **90** | 15 | +2,283 |
| Ruptures brutales | 103 | 38 | +3,951 |
| Récurrent | 164 | 70 | +6,462 |
| Progressif | 103 | 20 | +2,925 |

Dans le régime stable, **aucun véritable changement de profil n'existe** ; les 90 alarmes sont donc des faux positifs par construction. Retirer la règle de rollback **améliore le score moyen dans les quatre régimes**. Cela ne prouve pas que tout rollback est inutile : la règle testée est trop susceptible de restaurer des connaissances obsolètes et d'effacer les observations de la fenêtre active. Le journal `all_observed` conserve néanmoins les retours bruts : absence de fuite de données, mais politique de sélection déficiente.

La mémoire n'apporte pas d'amélioration robuste : le candidat complet gagne légèrement sur l'ablation sans mémoire dans trois régimes (stable, abrupt, progressif), mais perd en récurrent. Ces effets sont descriptifs et ne justifient aucune affirmation générale.

### Comparaison à des contrôles adaptés au changement

Même les témoins simplifiés `sw_ucb`, `discount_ucb` et `restart_ucb` ne sont pas systématiquement les meilleurs; le choix des probabilités de réussite fait que `fixed_verify` est un contrôle particulièrement fort en abrupt/progressif. L'extension Omega ne dépasse **pas non plus** `sw_ucb` en pseudo-regret moyen dans les quatre régimes, ce qui évite de dépendre exclusivement de la comparaison a posteriori.

## Audit de validité interne

- Les politiques reçoivent uniquement `t`, l'action jouée et la récompense observée. Les probabilités cachées et les issues contrefactuelles servent uniquement à l'évaluateur.
- Les observations sont déterministes via SHA-256 pour chaque (régime, réalisation, temps, action) ; comparaisons à flux contrefactuels communs. Les tests interdisent l'accès à `_world_probabilities` depuis `choose` et `observe`.
- Le candidat invoque `planner.plan_mission` une fois pour le plan de vérification, puis exécute une **nouvelle politique numérique expérimentale**. Le vrai P1 actuel ne contient **pas** à lui seul une boucle d'apprentissage ou un détecteur de changement. Ne pas présenter cette extension comme une capacité Omega déjà en production.
- Les quatre environnements, les coûts fictifs (bon +1, mauvais −2, vérification −0,20, abstention +0,08), les alarmes et leurs seuils sont entièrement **conçus par l'auteur**. Les implémentations UCB sont des variantes simplifiées, non des références académiques certifiées. Aucune évaluation extérieure n'a été réalisée.
- Le pseudo-regret est calculé depuis les probabilités cachées uniquement **après** les actions ; ce n'est ni une métrique de qualité de réponse LLM, ni une validation de mémoire scientifique réelle.
- La sélection du meilleur témoin classique par régime utilise la connaissance `a posteriori`. Les comparaisons avec les témoins individuels `sw_ucb` et `ucb_stationary` restent indispensables.

## Déduction et prochaine itération autorisée

**Constat testable** : accumuler une mémoire d'observations et activer un rollback ne suffit pas ; un détecteur de changement mal calibré dégrade un système, même si toutes les étapes sont traçables. Il est possible que la conception de l'alarme et le traitement des observations soient les principaux verrous, mais **leur causalité propre n'a pas été isolée** au-delà des ablations rapportées.

La prochaine version doit avoir **un nouveau pré-enregistrement avant toute exécution**, avec : (1) un témoin de détecteur de changement robuste et calibré sur un jeu séparé ; (2) un témoin à même politique sans reset ni rollback ; (3) le vrai coût des actions et une pénalisation explicite des fausses alarmes ; (4) un test avec retours authentiques de modèle ou de vérificateur, distinct de toute simulation ; (5) un bloc de validation inaccessible pendant l'ajustement.

**Décision : ne pas fusionner cette politique de contrôle dans `main` ou dans le Prisme P1.** Conserver la PR en DRAFT comme résultat négatif documenté.
