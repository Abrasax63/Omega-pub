# OMEGA-STRAT-004 — résultats vérifiés : information sur les méthodes, sans information sur la vérité

**11 novembre 2026 — statut CALCUL EXACT sur corpus public artificiel. Aucun résultat sur problèmes nouveaux indépendants ou modèles LLM.**

## Gel avant toute exécution

- Données, 64 enveloppes, 32 TRAIN + 32 TEST : commit **`dff3ceeb90d2523dba0c3146f1bbf32ec5e1de01`** (fichier `prism/intermediate_evidence_cases_v01.json`).
- Objectifs, budgets, arrêt, et six politiques : commit **`232bc81443cbb902fabe989acfd981ceb64bb48f`**, avant implémentation.
- Quatre familles : proposition de congruence universelle (preuve formelle), existence de circuit eulérien (critère + recherche indépendante), comparaison de taux rationnels (produits croisés + `Fraction`), portée normative POST→GET des redirections HTTP (RFC 9110, table locale).
- Politique ne connaît que l'identifiant opaque et le résultat effectivement payé. `probe` lit le schéma du dossier et annonce la méthode susceptible de certifier, **sans donner `yes/no`**. Cette interface scellée est une hypothèse synthétique importante ; le champ de la charge utile est accessible aux vérificateurs et au correcteur mais non aux politiques.
- Une panne de vérificateur par famille et par partition est simulée (4 TRAIN + 4 TEST), et inconnue de la politique avant l'appel. Le coût d'un appel est une unité de consultation ; objectif `réponse certifiée - 0,02*appel`. Budget maximum : **2 appels par tâche**.

## Résultats principaux, 32 nouvelles enveloppes de TEST

| Stratégie | Certificats justes | Abstentions | Erreurs | Appels comptés | Score fictif (certifiés – appels/50) |
|---|---:|---:|---:|---:|---:|
| A : meilleur ordre fixe parmi toutes les actions | 14/32 | 18 | 0 | 57 | 12,86 |
| B : meilleur ordre fixe des 4 spécialistes | 14/32 | 18 | 0 | 57 | 12,86 |
| C : **Omega actuel `optimize_policy`, horizon 2** | **28/32** | 4 | 0 | **64** | **26,72** |
| D : DP orienté certificats, horizon 2 | **28/32** | 4 | 0 | **64** | **26,72** |
| E : meilleure politique conditionnelle forte, **calculée indépendamment** | **28/32** | 4 | 0 | **64** | **26,72** |
| F : sélection gloutonne à une étape | 14/32 | 18 | 0 | 57 | 12,86 |

Les six politiques sont calculées **une seule fois sur TRAIN**, avant la notation des TEST. Toutes les consultations dans le tableau sont des exécutions locales du moteur de preuve sur les mêmes paramètres gelés ; aucune campagne de requêtes réseau distincte par bras ni aucun appel LLM.

**Résultat : +14 certificats** (28 plutôt que 14, +43,75 points de couverture) en utilisant 7 vérifications de plus que l'ordre fixe. Le signal intermédiaire sert à identifier la méthode ; il ne livre pas à lui seul une réponse.

**Mais** C, D et E ont **les mêmes traces exactes sur chacun des 32 cas**, et non simplement les mêmes totaux. La version originale d'Omega sait déjà calculer l'avantage de cette observation à deux étapes. L'objectif certificat n'améliore pas le score dans cette expérience. Une baseline conditionnelle exhaustive, non attribuée à Omega, obtient la même performance. **Aucune preuve de supériorité particulière d'Omega.**

## Résultat mathématique : information stratégique sans gain immédiat sur la réponse

Sur chacune des partitions (TRAIN et TEST), il existe quatre modes en parts égales. Dans chaque mode, quatre réponses sont vraies et quatre fausses. Ainsi :

`P(Y=vrai) = 1/2` et `P(Y=vrai | probe=route_i) = 1/2` pour chacun des quatre modes.

Par conséquent, sous la loi empirique uniforme du corpus :

`I(Y ; probe) = 0 bit`.

Mais `probe` révèle quel vérificateur est pertinent. Les quatre spécialistes sont mutuellement exclusifs ; une politique fixe de deux vérifications n'en couvre que deux. Il y a 7 preuves disponibles sur 8 par mode (un outil indisponible par mode). L'ordre fixe idéal couvre au plus `2×7=14` dossiers ; la politique `probe` puis vérificateur approprié couvre `4×7=28` dossiers, sans dépasser deux consultations.

C'est un résultat exact sur un **modèle fini spécifié**, et non une loi universelle d'intelligence adaptative. Il révèle qu'une valeur de contrôle peut porter sur la qualité du choix de méthode, même si l'entropie de l'énoncé final n'est pas réduite par le premier résultat.

## Vérifications, certification et limites de sécurité

- `prism/intermediate_evidence_gateway.py` effectue les **vraies opérations** (congruence sur coefficients, graphe fini, produits croisés, table RFC). Le correcteur utilise une deuxième méthode : k=0/1 pour congruences, parcours DFS pour Euler, `Fraction` pour taux et références normatives pour HTTP. Il ne s'agit pas d'une revue humaine indépendante.
- Le certificat d'une méthode effectivement appelée est exigé avant d'affirmer `yes/no`. Un résultat `route:*` ou `unknown:*` est non conclusif.
- Une route falsifiée (champ `route:*` différent de la structure d'origine) est rejetée par le vérificateur d'invariant du simulateur ; **cela ne signifie pas** qu'un véritable fournisseur réseau ou qu'un document source serait cryptographiquement authentifié.
- Les 4 abstentions des bras adaptatifs concernent les 4 pannes synthétiques des spécialistes pertinents sur TEST. Aucun autre spécialiste n'a de certificat pour ces dossiers.
- `main`, SQLite et CORE non modifiés ; PR brouillon empilée sur #35.

## Important contre-test a posteriori — catégorie initiale visible

**EXPÉRIENCE ALTERNATIVE, NON ADMISSIBLE COMME COMPARATEUR DU PROTOCOLE INITIAL.**

Après les résultats, on révèle gratuitement la catégorie de l'enveloppe à une règle simple, avant de consulter un outil. Cette règle choisit directement la méthode pertinente : **28/32 certificats pour 32 consultations**, au lieu de 28/32 pour 64 consultations avec le diagnostic payant.

Ce comparateur voit **plus d'information initiale** que les six bras de l'expérience gelée ; il ne faut donc pas l'utiliser pour inférer un échec de C dans le cadre opaque. Il sert à falsifier une généralisation trop forte : dans des questions réelles dont la structure est déjà visible dans l'énoncé, le diagnostic préalable pourrait être une dépense inutile. L'intérêt démontré dépend de la nécessité réelle de découvrir la classe ou la provenance de l'élément à vérifier.

## Actions et journal CI réellement vérifiés

- [Run 43059466748](https://github.com/Abrasax63/Omega-pub/actions/runs/43059466748), **SUCCESS**, 175 tests du Prisme, 6 tests MCP, tests d'index et migrations réussis.
- [Run 43059795322](https://github.com/Abrasax63/Omega-pub/actions/runs/43059795322), **SUCCESS**, 177 tests du Prisme. Audit du zéro bit et traces C=D=E.
- [Run 43060023494](https://github.com/Abrasax63/Omega-pub/actions/runs/43060023494), **SUCCESS**, 178 tests du Prisme. Ablation de catégorie visible et non-régression.

Reproduction sur `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```bash
python intermediate_evidence_policy.py
python intermediate_evidence_audit.py
python visible_schema_ablation.py
python -m unittest -v test_intermediate_evidence_policy test_intermediate_evidence_audit test_visible_schema_ablation
```

## Références primaires pour les assertions documentaires
RFC 9110 §15.4.2 (301), §15.4.3 (302), §15.4.8 (307), §15.4.9 (308) ; également RFC 9205 §4.6.1, qui présente les quatre cas dans une seule table :
- https://www.rfc-editor.org/rfc/rfc9110
- https://www.rfc-editor.org/rfc/rfc9205#section-4.6.1

## Conclusion et verrou suivant

**DÉMONTRÉ DANS LE MODÈLE FINI** : une observation peut n'apporter aucune information sur la vérité cible tout en ayant une valeur positive pour choisir une méthode ultérieure. Le choix conditionnel l'exploite efficacement, mais le planificateur Omega existant, son extension certificat et l'exhaustif indépendant sont ici strictement équivalents.

**INDÉTERMINÉ HORS MODÈLE** : capacité d'Omega à inférer en langage naturel le type de preuve nécessaire, à découvrir de nouvelles méthodes, à détecter les contradictions de sources externes, à généraliser lorsque la classe est connue ou partiellement visible, et à dépasser un solveur conditionnel bien conçu.

Prochain verrou : **problèmes naturels dont l'information partielle n'est ni une simple classe dissimulée ni une étiquette donnée par un oracle**. Figer un corpus externe indépendant, comparer le meilleur plan conditionnel utilisant les mêmes retours, tester des preuves primaires contradictoires et le coût des transitions de stratégie. Ne promouvoir aucun résultat expérimental en CORE avant certification supplémentaire.
