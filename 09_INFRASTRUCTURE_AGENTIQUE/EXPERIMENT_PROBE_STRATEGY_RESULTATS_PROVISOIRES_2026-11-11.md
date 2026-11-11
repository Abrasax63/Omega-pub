# OMEGA-PROBE-001 — contrôle indépendant local, résultats provisoires avant CI GitHub

**11 novembre 2026. STATUT : CALCUL EXACT INDÉPENDANT (script JavaScript exécuté dans une session de calcul distincte du programme Python enregistré). LE CODE PYTHON DU DÉPÔT ET SON AUDIT JS DÉDIÉ NE SONT PAS ENCORE VALIDÉS EN CI.**

## Provenance et gel

- Corpus synthétique : `prism/probe_strategy_cases_2026-11-11.json`, commit **`883cbe181bac982b8f30d5128f8f16a0381f79f9`**, gelé avant code et résultats.
- Méthodes, pertes, coûts, contrôles et comparateurs : `EXPERIMENT_PROBE_STRATEGY_PREREG_2026-11-11.md`, commit `a539c2df214f2dd9fa4f410461f82e8dae38f341`.
- Source des chiffres ci-dessous : recalcul **distinct en JavaScript**, en énumérant les 60 mondes, toutes les permutations de l'ordonnancement fixe, et toutes les branches de la programmation dynamique. Cette vérification n'est pas une exécution du `probe_strategy_benchmark.py` ni du `probe_strategy_independent.mjs` du dépôt. Aucune statistique CI n'est encore disponible.

## Coût moyen exact attendu (à minimiser)

Le coût cumule les prix des sondes effectivement réalisées et une pénalité de **5 par question non résolue**. Les valeurs ci-dessous sont des espérances calculées sur 60 mondes équiprobables, arrondies ici à 6 décimales, **pas des secondes ni des coûts de jetons**.

| Corpus | ZERO | GREEDY1 | OMEGA_LOOKAHEAD2 | FIXED_BEST | ADAPTIVE_DP_EXACT |
|---|---:|---:|---:|---:|---:|
| CAL_12 (calibration) | 25 | **4,5** | 5,75 | **4,5** | **4,5** |
| CAL_30 (calibration) | 25 | 5,766667 | **5,733333** | 5,766667 | **5,733333** |
| TEST_12 | 25 | **6,166667** | **6,166667** | **6,166667** | **6,166667** |
| TEST_60 | 25 | **5,266667** | **5,266667** | **5,266667** | **5,266667** |

Les **sommes exactes**, sans arrondi, sont respectivement :
- CAL_12 : `[1500, 270, 345, 270, 270]` ;
- CAL_30 : `[1500, 346, 344, 346, 344]` ;
- TEST_12 : `[1500, 370, 370, 370, 370]` ;
- TEST_60 : `[1500, 316, 316, 316, 316]`.

L'ordre des nombres est toujours `ZERO, GREEDY1, OMEGA_LOOKAHEAD2, FIXED_BEST, ADAPTIVE_DP_EXACT`.

### Conclusion falsificatrice

- **TEST : aucun avantage** de l'anticipation Omega horizon 2 sur une heuristique gloutonne réévaluée ou sur le meilleur ordre fixe. Les cinq réponses à chaque monde ne créent aucun faux certificat selon la simulation indépendante.
- Sur CAL_30 : gain marginal sur greedy/fixed, **2 unités de perte totale sur 60 mondes**, mais égalité avec DP global.
- Sur CAL_12 : **échec sérieux** de l'horizon 2 : **345 contre 270** pour GREEDY1 et DP global, soit 27,78 % de coût total en plus. C'est une falsification de l'idée que plus d'anticipation recédante garantit une meilleure politique exécutée.
- Important : les valeurs de programmation dynamique **à horizon tronqué calculées pour la première décision** sont monotones (`horizon 2 <= horizon 1`) mais cela **n'entraîne pas la domination de la politique recédante exécutée sur tous les mondes**. Ne pas confondre plan initial et performance effective.

## Statut CI et suite

- PR [#45](https://github.com/Abrasax63/Omega-pub/pull/45) en brouillon, indépendante de Lean #44, branche dérivée de #43.
- Le code Python, 7 tests Python et une seconde vérification JS refaisant les 1 200 traces de décision, les ordres fixes et les valeurs de DP global sont déposés.
- [GitHub Actions #43098446752](https://github.com/Abrasax63/Omega-pub/actions/runs/43098446752) et workflow RCE correspondant étaient encore **`queued`** au dernier contrôle ; aucun statut de succès de test n'a été obtenu. Ne pas annoncer ces chiffres comme reproduits en CI.
- **Prochain contrôle obligatoire** : exécution des scripts déposés, concordance indépendante de toutes les décisions, contrôle des coûts, enregistrement des journaux. **NE PAS** optimiser les hyperparamètres de Lookahead2 après lecture du TEST : les résultats négatifs demeurent valides.

Les coûts sont artificiels et les scénarios construits. Ce n'est ni une expérience sur des preuves réelles ni une supériorité stratégique démontrée pour Omega.

`main`, SQLite, CORE et la PR Lean #44 ne sont pas modifiés.
