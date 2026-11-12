# P5 ROUTE-02 — Pré-enregistrement d'un test de routage de vérification non trivial

**12 novembre 2026 — enregistré avant le code d'évaluation et avant l'exécution de ROUTE-02.**

## Question

La politique d'allocation de vérifications d'Omega permet-elle un meilleur arbitrage **exactitude / coût / risque** qu'une règle simple, lorsque **toutes les missions ont le même `mission_type=general`**, et que le bon choix dépend d'informations propres à chaque cas ?

**Aucune plus-value exclusive d'Omega n'est présumée.** Le planificateur P1 actuel ne gère pas encore l'allocation de vérifications ni leur budget. Nous testons donc une **extension candidate** séparée et la comparons à l'algorithme standard d'optimisation équivalent. Une égalité avec ce témoin signifie absence de nouveauté algorithmique propre à Omega.

## Périmètre, préengagement et indépendance

**Simulation déterministe publique** sans LLM, sans API, sans corpus privé, ni évaluation indépendante. 128 épisodes de validation « calibrés » et 128 épisodes de robustesse « décalés », **6 hypothèses par épisode**. Chaque hypothèse a exactement le même type de mission (`general`), mais un type de contrôle, un indice public de risque de défaillance, un impact en cas de non-détection, et un coût de vérification hétérogènes. Budget identique **8 unités/épisode** pour toutes les politiques. Les indices publics et résultats cachés sont produits par un générateur déterministe distinct, à partir de `SHA256("P5ROUTE02|regime|episode|candidate|field")`; aucune politique ne reçoit le résultat de l'oracle. Les graines sont publiques, le jeu est conçu par le même auteur que les stratégies : ceci ne constitue pas un holdout aveugle.

Le risque affiché est une estimation **exogène fournie**, ce n'est pas une probabilité inférée par Omega. Sur le régime calibré, la fréquence des fautes suit cette estimation; sur le régime décalé, cette relation est **inversée**. Le second régime mesure précisément la fragilité d'un décideur trop confiant dans le score annoncé.

La vérification simulée est parfaite : si une hypothèse contient effectivement une erreur, elle la révèle. **Cela ne prétend pas modéliser les erreurs ni coûts réels de vérificateurs logiciels ou humains.**

## Comparateurs pré-enregistrés

1. `none` : vérifier 0 hypothèse.
2. `fixed` : ordre fixe par identifiant, sans tenir compte du contenu, sous budget.
3. `risk_first` : sélectionner les risques annoncés décroissants, sous budget.
4. `impact_first` : sélectionner les impacts décroissants, sous budget.
5. `ratio` : tri glouton par risque × impact / coût, sous budget.
6. `exact_knapsack` : maximiser exactement la somme des gains attendus par énumération exhaustive des sous-ensembles valides sous budget; **contrôle standard fort**, utilisant les mêmes informations.
7. `omega_candidate` : couche distincte qui consulte le vrai `planner.plan_mission` puis applique un choix d'utilité espérée tenant compte du coût. Cette extension ne sera créditée que d'un avantage **supérieur** à `exact_knapsack`; sinon elle ne prouve aucune nouveauté propre à Omega.
8. `hindsight_oracle` : sélection des erreurs effectivement présentes **avec accès interdit à l'oracle**; plafond descriptif non déployable.

Critère d'optimisation `expected_net = Σ sélectionnés (risque_estime × impact − 0.20 × coût)`. Budget = 8. En cas d'égalité, choix déterministe lexicographique par IDs. `ratio`, `risk_first` et `impact_first` s'arrêtent quand la prochaine vérification ne procure pas d'utilité attendue positive; sinon le contrôle gaspillerait artificiellement le budget. `fixed` reste aveugle aux scores mais peut renoncer à une vérification dont l'utilité attendue est négative pour conserver l'équité minimale.

## Mesures et falsification

Score réalisé : `realized_net = Σ sélectionnés (is_fault × impact − 0.20 × coût)`. Mesurer aussi : coûts consommés, nombre de contrôles, nombre d'erreurs réellement interceptées, poids des erreurs ratées, comparaison par épisode et écart exact au témoin `exact_knapsack`. Aucune conclusion de performance statistique autonome issue des seules données de simulation.

- **Critère réfutant l'avantage Omega** : `omega_candidate <= exact_knapsack` dans les deux régimes ; égalité attendue si la couche Omega ne fait que résoudre le sac à dos.
- **Critère de robustesse** : sur le régime décalé, signaler si la décision fondée sur des probabilités inexactes perd du bénéfice réel face à une règle naïve ; ne pas ajuster les politiques après lecture.
- **Invariant** : jamais d'accès aux fautes cachées lors de la sélection; pas de sélecteur qui s'appelle lui-même « agent » s'il ne fait que choisir des outils.

Les résultats doivent être écrits avec le statut `SYNTHETIC_CALIBRATION_NOT_EMPIRICAL_VALIDATION`. Aucun appel de modèle, ni aucune facture, ne sont effectués.

## Décision après test

Une réussite de `omega_candidate` face aux heuristiques faibles **sans victoire sur `exact_knapsack` ne démontre aucune innovation**. La suite scientifique exigera des résultats de vérificateurs imparfaits et de vrais échecs de modèle, puis une cohorte indépendante; nous ne modifierons pas le protocole rétroactivement.

`main`, les PR #47-49, le holdout privé et la mémoire scientifique ne sont pas modifiés.
