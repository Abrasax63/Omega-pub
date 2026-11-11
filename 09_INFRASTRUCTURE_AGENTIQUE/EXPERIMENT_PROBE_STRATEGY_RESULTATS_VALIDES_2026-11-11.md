# OMEGA-PROBE-001 — résultats finaux reproductibles après contrôle CI

**11 novembre 2026. Statuts : CALCUL EXACT sur corpus SYNTHÉTIQUE, TESTS CI REPRODUITS, AVANTAGE SPÉCIFIQUE OMEGA NON DÉMONTRÉ.**

## 1. Provenance et verrou temporel

- Corpus figé **avant implémentation et avant mesure** : commit [`883cbe181bac982b8f30d5128f8f16a0381f79f9`](https://github.com/Abrasax63/Omega-pub/commit/883cbe181bac982b8f30d5128f8f16a0381f79f9), `prism/probe_strategy_cases_2026-11-11.json` : 4 scénarios, dont 2 de calibration et 2 de test, 60 mondes équiprobables chacun.
- Contrat et baselines gelés au commit [`a539c2df214f2dd9fa4f410461f82e8dae38f341`](https://github.com/Abrasax63/Omega-pub/commit/a539c2df214f2dd9fa4f410461f82e8dae38f341).
- Correction **après** premier échec de CI : erreur de sérialisation `s.split` (méthode) remplacée par `s.split_name` (champ de texte), commit `dd105784dae3bf2a22e2abde8c5264ce7577655e`, suivie d'un test de non-régression de sérialisation (commit `39b7ec39902713d1926bd4a95fd977bba63c3f9c`). **Aucun changement** des mondes, des coûts, des politiques ou de la fonction de perte en corrigeant cette erreur.
- Exécution réussie du **dernier commit algorithmique/testé** : [GitHub Actions #43100530361](https://github.com/Abrasax63/Omega-pub/actions/runs/43100530361), `SUCCESS`. [Tests RCE du même commit #43100530382](https://github.com/Abrasax63/Omega-pub/actions/runs/43100530382), `SUCCESS`.

## 2. Question et fonction de perte

L'environnement cache un entier `x∈{0,…,59}`, uniforme. Les cinq requêtes de chaque scénario sont des congruences modulaires. Chaque sonde révèle un booléen exact et coûte une somme entière fixée. Pour tous les mondes, la politique décide sa prochaine vérification, replanifie éventuellement, puis répond seulement si **tous les mondes encore possibles** vérifient ou réfutent la requête. Toute autre réponse doit rester indéterminée. **Une fausse conclusion certaine constitue une erreur critique.**

**Perte** : `coût des sondes + 5 × nombre de questions encore indéterminées`. Unités **abstraites**, non secondes ni jetons. Toutes les politiques connaissent exactement le même modèle, toutes les sondes et leurs prix **avant** l'expérience, mais pas le monde caché.

Contrôles :
- `ZERO` (aucune sonde) ;
- `GREEDY1` (plan à horizon 1, réévalué à chaque observation) ;
- `OMEGA_LOOKAHEAD2` (horizon 2, réévalué à chaque observation) : **adaptateur expérimental, PAS le planificateur Omega complet** ;
- `FIXED_BEST` (ordre fixe optimal trouvé en explorant toutes les permutations ; peut arrêter en fonction des résultats déjà vus) ;
- `ADAPTIVE_DP_EXACT` (optimum adaptatif global, par programmation dynamique, connaissant le modèle mais **pas** le monde réel à l'avance).

## 3. Résultats CI et vérification indépendante

| Scénario | ZERO | GREEDY1 | OMEGA_LOOKAHEAD2 | FIXED_BEST | ADAPTIVE_DP_EXACT |
|---|---:|---:|---:|---:|---:|
| CAL_12 (calibration) | 25 | **4,500000** | 5,750000 | **4,500000** | **4,500000** |
| CAL_30 (calibration) | 25 | 5,766667 | **5,733333** | 5,766667 | **5,733333** |
| TEST_12 | 25 | **6,166667** | **6,166667** | **6,166667** | **6,166667** |
| TEST_60 | 25 | **5,266667** | **5,266667** | **5,266667** | **5,266667** |

**Valeurs exactes (somme de perte sur les 60 mondes)**, dans l'ordre des cinq méthodes :
- CAL_12 : `[1500,270,345,270,270]` ;
- CAL_30 : `[1500,346,344,346,344]` ;
- TEST_12 : `[1500,370,370,370,370]` ;
- TEST_60 : `[1500,316,316,316,316]`.

**Le verdict falsificateur est confirmé** : sur CAL_12, le contrôle à horizon 2 a une perte 345 au lieu de 270 pour GREEDY1, **27,78 % plus élevée**, malgré une estimation à deux étapes meilleure au premier état que l'estimation à une seule étape. La monotonie des **valeurs calculées à l'horizon tronqué** n'implique pas la domination des **politiques réoptimisées à chaque observation**. La cause immédiate du cas est une dépense supplémentaire de vérifications (coût moyen 3,25 au lieu de 2, sans gain de couverture : 4,5 questions résolues en moyenne pour les deux politiques). Ne pas inventer une causalité psychologique ou agentique.

CAL_30 présente un gain **minime** : deux unités de perte totale sur les 60 mondes par rapport à la politique gloutonne, et égalité avec l'optimum adaptatif. **Aucun gain à TEST** : deux scénarios TEST, perte égale avec toutes les politiques non nulles. `FIXED_BEST` égale également l'optimum aux deux TEST. **Aucun avantage propre à Omega et aucune performance générale supplémentaire démontrés.**

## 4. Double voie de vérification effectivement exécutée

- **Python** : sept tests initiaux plus un test supplémentaire de JSON complet = **huit tests spécialisés réussis** ; génération et export des 1 200 traces `4 scénarios × 60 mondes × 5 politiques`.
- **JavaScript indépendant** (`probe_strategy_independent.mjs`) : refait en `BigInt` la simulation, la programmation dynamique exacte, les choix gloutons/horizon 2, toutes les permutations fixes et les **1 200 traces** ; valide **2 775 actions**, vérifie les coûts et les réponses exactes, parcourt **324 457 états de politiques calculés** (d'après le rapport de la seconde voie) et constate **0 fausse conclusion certaine** dans ce corpus.
- [Archive ZIP du registre complet](https://github.com/Abrasax63/Omega-pub/actions/runs/43100530361/artifacts/13891611455).
- **RCE** : [run #43100530382](https://github.com/Abrasax63/Omega-pub/actions/runs/43100530382), `SUCCESS`, **243 tests du Prisme**, six MCP et fumées de l'index réussis.
- Les deux voies utilisent les mêmes jeux synthétiques et le même modèle exact ; **il ne s'agit pas d'une double preuve indépendante de l'utilité sur des tâches réelles**.

## 5. Important : le blocage GitHub et ses limites

Les premiers essais GitHub Actions de cette PR sont restés dans la file `queued` sans job, puis une nouvelle exécution a démarré et a révélé le bug JSON de présentation. La correction a permis un [run complet réussi #43100530361](https://github.com/Abrasax63/Omega-pub/actions/runs/43100530361).

Cela montre que **la PR #45 dispose désormais de tests exécutés**, mais ne prouve ni que l'incident de lancement GitHub est résolu pour toute la plateforme, ni que **Lean #44** a reçu un runner. Au dernier contrôle indépendant, les runs Lean #44 étaient encore `queued`. **Aucun théorème Lean #44 ne peut être annoncé vérifié pour cette seule raison.**

## 6. Décision scientifique

Le test est **prêt dans son périmètre synthétique**, mais il refuse la promotion d'un `LOOKAHEAD2` comme politique stratégique améliorée. Garder l'optimum dynamique et les stratégies simples comme adversaires forts.

La question utile suivante est la **méta-décision** : combien de raisonnement facturer avant de sélectionner une sonde ? L'évaluer séparément avec des coûts réels de calcul ou des coûts de nœuds comparables, sans réutiliser comme données de test aveugles les quatre scénarios de ce corpus, désormais observés. Ne pas présenter la « sélection adaptative » existante comme une capacité générale d'Omega.

**Statuts : EXACT sur le modèle et les calculs, VALIDÉ en CI sur ces tests, AVANTAGE OMEGA INDÉTERMINÉ/NON DÉMONTRÉ sur recherche ouverte.** PR #45 en brouillon, `main`, CORE, SQLite et branche Lean #44 inchangés.
