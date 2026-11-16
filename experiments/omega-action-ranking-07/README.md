# OMEGA-ACTION-RANKING-07 — diagnostiquer les erreurs de classement des expériences

**Préenregistrement avant code :** [commit e274149](https://github.com/Abrasax63/Omega-pub/commit/e274149fd8e42658f68b8c6320a2c39e41b2f119), [contrat complet](PREREG_2026-11-16.md).

## Pourquoi

Dans la [PR #133](https://github.com/Abrasax63/Omega-pub/pull/133), Omega BELIEF_VALUE prédisait la continuation de l'explorateur uniforme avec une MAE nettement meilleure que des références naïves, mais ne battait pas systématiquement FIXED et MEMORY pour le coût moyen d'identification. Ce pilote teste où les classements de probes divergent de l'optimum exact, sans entraîner un nouveau modèle.

## Trois Q-values par action, par croyance

Sur une machine de Mealy connue (4 ou 5 états, seulement état initial caché, six probes réinitialisés), le résultat conserve :

- Q*(S,a) = prix(a) + E[V*(S_après)] — coût optimal moyen exact, en rationnels.
- Q_uniform(S,a) = prix(a) + E[V_uniform(S_après)] — coût en jouant l'action puis en explorant uniformément, en rationnels.
- Q_modele(S,a) = prix(a) + E[V_BELIEF_VALUE(S_après)] — coût prédit à partir de la continuation apprise, en flottants.

Deux mécanismes potentiels, non exclusifs :
1. **Inadéquation de cible** : l'action déterministe préférée par Q_uniform est sous-optimale pour Q*. Même un V_uniform parfait ne résoudrait pas cette décision.
2. **Désaccord d'approximation** : l'action préférée par Q_modele n'appartient pas aux minimisants de Q_uniform. Cela ne suffit pas à prouver une erreur de décision pour Q*.

Le rapport publie aussi Q*(action choisie) − V*(S), regret local exact (suite optimisée), et des regrets end-to-end distincts, calculés sur tous les états initiaux. Les ex aequo exacts ne comptent pas comme erreurs.

## Holdout jamais utilisé pour entraîner

Les poids, la mémoire, les trajectoires TRAIN et les graines 271/272/273 sont inchangés par rapport aux PR #132–#133. Trois cohortes **nouvelles**, distinctes par signature canonique des 942 machines des PR #127–#133 :

| Cohorte | Machines | Graine | Structure |
|---|---:|---:|---|
| EVAL_RANDOM4 | 24 | 24117 | Quatre états, transitions non constantes et pas deux permutations |
| EVAL_PERM5 | 30 | 24118 | Cinq états, deux actions permutations |
| EVAL_RESET5 | 30 | 24119 | Cinq états, action reset et cycle de longueur cinq |

Les impossibles sont conservés. Les trois graines d'entraînement partagent **les mêmes machines réservées**, ce ne sont pas trois observations indépendantes.

## Mesures et falsification

- Taux de décisions localement sous-optimales BELIEF_VALUE, taux d'inadéquation de cible, taux de désaccord d'approximation, tableau croisé, regrets locaux exacts et marges d'optimalité.
- Tailles des croyances 2, 3, 4, 5 ; scores rationnels Q* et Q_uniform de chaque probe, scores prédits Q_modele.
- Coûts réels des politiques MEAN_EXACT, UNIFORM_EXACT_GREEDY, FIXED, MEMORY, TOTAL9, BELIEF_VALUE ; oracle optimal moyen de #133 et contrôle minimax de #76 exclusivement en évaluation.
- L'hypothèse « seulement une erreur d'approximation » est mise en défaut dès qu'une croyance a une action Q_uniform déterministe sous-optimale pour Q*. Ne pas modifier les modèles après observation.
- Résultat scientifique négatif ou indéterminé légitime ; une CI verte ne vaut pas certification.

## Reproduction (Python 3.11, bibliothèque standard)

    python -m unittest discover -s experiments/omega-action-ranking-07 -p test_action_ranking.py -v
    python experiments/omega-action-ranking-07/action_ranking_lab.py --output /tmp/omega-action-ranking-07-report.json

15 tests, CI avec artefacts et empreintes, PR DRAFT empilée sur #133, branche principale inchangée, aucune API payante.

**Limites :** machines connues, état initial inconnu ; regret local supposant la suite optimale ; ni apprentissage de machines inconnues ni entraînement LLM ni auto-programmation.
