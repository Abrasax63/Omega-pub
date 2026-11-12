# P5-ADAPT-02 — calibration séparée, observations conservées et adoption validée

**Pré-enregistrement — 12 novembre 2026. Ce document est créé AVANT toute exécution de la version 02.**

## Question et verdict falsifiable

Le résultat P5-ADAPT-01 [PR #51](https://github.com/Abrasax63/Omega-pub/pull/51) a montré de nombreuses alarmes en environnement stationnaire et un rollback dommageable. Tester si la **calibration du détecteur** et une **adoption conditionnelle** réduisent ces défauts, **en comparaison des contrôles classiques de P5-ADAPT-01 et d'une version sans validation**. Aucune supériorité propre à Omega n'est présumée. La boucle testée est un *candidat expérimental externe à P1*, et `planner.plan_mission` est appelé uniquement pour la traçabilité du plan.

## Univers fixe et séparation des données

Réutiliser **sans changement** `_reward`, `_expected_rewards`, `REGIMES`, `HORIZON=180` et les trois actions de `p5_adapt01_loop.py`. Il s'agit de **récompenses synthétiques**, pas de performances de modèles de langage.

- **Calibration :** les épisodes avec indices 0–31, déjà utilisés par P5-ADAPT-01, sur les quatre régimes ; leurs résultats ne sont donc pas un holdout.
- **Évaluation tenue hors calibration :** indices **100–163**, 64 épisodes par régime, jamais interrogés lors du choix d'hyperparamètres dans P5-ADAPT-02. Ces épisodes sont séparés par graine, mais utilisent le même générateur connu de l'auteur : ce n'est **pas** un holdout indépendant/externe.
- Toutes les politiques reçoivent seulement `t`, leur **action effectuée** et la récompense effectivement obtenue ; aucune probabilité, date de rupture ou récompense contrefactuelle ne leur est passée. L'évaluateur seul calcule le pseudo-regret.
- Les observations sont append-only et restent accessibles dans la trace d'audit même lorsque la politique change de stratégie. Ni le mode « rollback » ni les alarmes n'effacent une observation.

## Détecteur et calibration pré-spécifiés

Détecteur à deux blocs de **8 retours observés par même action** (DIRECT ou VERIFY), comparer les taux d'issues positives des blocs successifs, déclencher si `abs(mean_recent - mean_old) >= threshold`. Une action est positive si la récompense (coût de vérification compris) est supérieure à zéro. Il s'agit d'une **heuristique**, pas d'une garantie d'alarme statistique sous échantillonnage adaptatif.

Grille figée : `threshold ∈ {0.375, 0.50, 0.625, 0.75}`, délai réfractaire **28 décisions** après une alarme. Choisir **uniquement sur calibration** les seuils qui déclenchent au maximum **0,50 alarme par épisode stationnaire**, puis parmi eux celui ayant le plus petit pseudo-regret moyen sur les trois régimes changeants. Égalité : seuil le plus élevé. Si aucun seuil ne satisfait le garde-fou, choisir 0,75 et consigner l'échec de calibration ; aucune correction après lecture du test.

## Validation de changement et mémoire

- Comportement ordinaire : politique UCB à fenêtre 36 décisions, le contrôle connu `sw_ucb` de P5-ADAPT-01.
- Après une alarme causée par DIRECT ou VERIFY : prendre l'action actuellement suggérée par la fenêtre comme **incumbent**. Choisir une **alternative** différente, parmi DIRECT/VERIFY/ABSTAIN, d'après ses récompenses observées. Si absence d'observations pour une alternative, la valeur de repli est la récompense neutre `+0.08`, sans fuite d'oracle.
- **Probation** : durant **20 décisions**, intercaler exactement **10 actions incumbent et 10 challenger**, une de chaque par paire ; pas de récompenses contrefactuelles, donc les deux moyennes ne reposent pas sur les mêmes pas. Cette limitation est à déclarer. Seuil de promotion : `mean(challenger) - mean(incumbent) > 0.25`.
- Si promotion : adopter le challenger pendant 20 décisions puis revenir à la sélection par fenêtre. Si rejet : **annuler la proposition sans effacer de données**, conserver l'incumbent pendant 20 décisions. Rejet ≠ preuve qu'un changement de monde était absent.
- La politique complète conserve tout le journal ; pour choisir le challenger, elle calcule les moyennes **sur les 48 dernières observations par action**, tandis que l'ablation `no_memory` ne conserve que les 12 dernières. Il s'agit de mémoire de retours numériques, **pas** de bibliothèque scientifique.
- Ablation `no_gate` : adopte immédiatement le challenger 20 décisions après alarme, sans probation ; même seuil calibré. Ablation `no_memory` : probation identique, mais champ de comparaison plus court. Aucune de ces variantes ne doit recevoir d'information supplémentaire.

## Témoins, métriques, règles d'arrêt

Comparer aux contrôles `fixed_verify`, `ucb_stationary`, `sw_ucb`, `discount_ucb`, `restart_ucb` de P5-ADAPT-01, sur **les mêmes indices de test** et même monde. La sélection du meilleur témoin a posteriori est explicitement descriptive; `sw_ucb` est le **comparateur principal fixé à l'avance**.

Primaire : pseudo-regret dynamique moyen de la politique complète moins celui de `sw_ucb` par régime sur les 64 épisodes. Report secondaire : comparaison au meilleur témoin classique a posteriori, utilité réalisée, nombre de mauvaises réponses, abstentions, vérifications, alarmes et coûts. Alarmes en stationnaire = faux positifs. Pour ruptures abruptes/récurrentes, calculer part des ruptures suivies d'une alarme dans les 30 décisions et délai de la première alarme ; ces dates ne sont visibles **qu'à l'évaluateur**.

**Falsification stricte** : si la politique complète ne bat pas `sw_ucb` dans les trois environnements changeants **sans détériorer le stationnaire**, ou si `no_gate` est meilleur, aucune plus-value démontrée. Signaler tout coût en récompenses perdues dû à la probation.

Exécution GitHub Actions Python 3.12 standard, **0 OpenAI API, 0 modèle, 0 dépense API**, pas de puissance du smartphone, aucun holdout privé. Statut `SYNTHETIC_ONLY_NO_INDEPENDENT_MODEL_VALIDATION`. Ne rien fusionner dans `main` sans revue humaine de la causalité des résultats.
