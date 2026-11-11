# OMEGA-STRAT-001 — résultat d'un test prospectif du choix de première vérification

**11 novembre 2026 — EMPIRIQUE SUR OBSERVATIONS GITHUB + CALCUL EXACT EN REJEU. NON AVEUGLE.**

## Question et gel avant observation

Comment distinguer l'avantage réel d'un sélecteur de stratégie de la simple exploitation d'une règle mathématique ?

- Pré-enregistrement de la cohorte, des mesures, des bras et de l'arrêt : commit **`8cc991b1d734b280825ce10a73458aacc3f06c7a`**.
- Code de choix de politique `prism/strategic_first_check_transfer.py` figé avant collecte : commit **`b3b36a1a290892c8bd2ee22212a6b9f44677d04c`**.
- Historique d'apprentissage : les 12 PR de #29 (données publiques archivées) ; **aucun des 24 cas nouveaux** n'y figure.
- Cohorte externe de 24 PR gelée : huit de `python/cpython`, huit de `pallets/flask`, huit de `psf/requests`. Les identifiants ont été sélectionnés parmi des recherches de titres consultées auparavant, ce qui rend l'échantillon **non aléatoire et potentiellement biaisé**. Certaines PR concernent des modifications voisines.
- Observation ensuite : `get_pr_info.merged` et `list_pr_changed_filenames`, avec la même définition syntaxique `touched_tests` que #29. La seconde lecture `fetch_pr` concorde sur `merged` et le SHA de tête pour les 24 cas. Les deux lectures utilisent **GitHub**, pas des fournisseurs indépendants.
- Quatre blocs bruts `prism/strategy_holdout_parts/part_00.json` à `part_03.json`, avec les listes de fichiers ; fusion contrôlée dans `prism/strategic_first_check_holdout_2026-11-11.json`.
- Capture complète enregistrée à **2026-11-11T15:02:27Z**. Cette date est celle de l'agrégation après consultation, pas l'horodatage serveur certifié de chaque PR.

## Résultat principal

Le prédicat est **fusionnée ET touche au moins un chemin de test**. Toutes les stratégies possèdent les mêmes deux vérifications exactes et le même plafond : **au plus deux consultations**. Les politiques sont entraînées sur les douze anciennes observations, puis **rejouées** sur les réponses effectivement collectées pour les 24 nouvelles PR. Les consultations du tableau sont des **coûts reconstitués**, pas sept campagnes indépendantes d'appels API.

| Politique | Décisions correctes | Consultations en rejeu |
|---|---:|---:|
| Fusion d'abord (sans apprentissage) | 24/24 | **26** |
| Tests d'abord (sans apprentissage) | 24/24 | 39 |
| Règle des taux marginaux, entraînement global | 24/24 | 39 |
| Règle des taux marginaux, entraînement par dépôt | 24/24 | 31 |
| **Omega optimize_policy** avec prior global appris | 24/24 | **39** |
| **Omega optimize_policy** avec priors par dépôt appris | 24/24 | **31** |
| Deux consultations systématiques | 24/24 | 48 |

Toutes les politiques donnent une décision correcte car les valeurs sont supposées exactes, disponibles et logiquement suffisantes. L'expérience ne mesure donc pas de gain de justesse, mais seulement un coût de consultation.

Dans le jeu d'entraînement, `merged` vaut vrai pour **5/12** et `touched_tests` pour **3/12**. Les modèles entraînés globalement choisissent donc d'abord les fichiers de test, comme la règle simple. Dans le nouveau lot, seules **2/24** PR sont fusionnées, tandis que **15/24** touchent des chemins de test. L'ordre le plus efficace s'inverse : lire `merged` d'abord coûte **26**, et lire `touched_tests` d'abord **39** consultations.

Par dépôt, la règle apprise choisit `merged` pour Python et Flask, mais `touched_tests` pour Requests. Elle obtient 31 consultations, exactement comme l'Omega adapté par dépôt. Un ordre fixe `merged` choisi sans apprentissage bat les deux sur cette cohorte, de **5 consultations**.

Le meilleur ordre déterminé après observation (oracle rétrospectif) est 26 consultations sur toute la cohorte et, ici, également 26 si l'ordre est autorisé à varier par dépôt. Cet oracle n'est pas une politique évaluée prospectivement.

## Pourquoi les deux politiques apprises sont égales

Pour un prédicat `A ET B` et deux vérifications parfaites, au même coût unitaire, l'ordre qui minimise le nombre attendu de consultations consiste à vérifier en premier le prédicat de probabilité marginale de vérité la plus faible.

En effet, si la première réponse est fausse, on s'arrête avec un verdict certain. Si elle est vraie, une seconde lecture est nécessaire. Pour l'ordre A puis B :

`E[consultations | A puis B] = 1 + P(A vrai)`.

Aucune indépendance probabiliste entre A et B n'est requise pour cette identité.

Sous ces hypothèses, le sélecteur `optimize_policy`, qui optimise une erreur de décision + un faible coût de consultation, n'a aucune structure supplémentaire à exploiter au-delà des fréquences de vérité pour le premier choix. La CI vérifie l'équivalence sur **81 configurations indépendantes de poids des quatre mondes binaires** (poids 1, 2 ou 3) et sur les politiques apprises de l'historique. Le test de sensibilité au lissage de Laplace 1 -> 2 conserve les premiers choix.

**Le gain stratégique propre au planificateur est NUL dans ce modèle** par rapport à la bonne règle marginale utilisant la même information, et non `INDÉTERMINÉ` sur ces cas précis. Aucun résultat général hors de cette structure n'en découle.

## Audit de reproductibilité

- Exécution initiale [GitHub Actions #43044624265](https://github.com/Abrasax63/Omega-pub/actions/runs/43044624265) : **SUCCESS**, 144 tests du Prisme dont six nouveaux.
- Exécution [GitHub Actions #43044979203](https://github.com/Abrasax63/Omega-pub/actions/runs/43044979203) : **SUCCESS**, **146 tests du Prisme** dont deux tests supplémentaires : l'exhaustif de 81 distributions et l'analyse de sensibilité au lissage. Tests MCP, RCE et de l'index : réussis.
- Fichiers : `prism/strategic_first_check_transfer.py`, `prism/test_strategic_first_check_transfer.py`, `prism/test_strategy_structure_stress.py` et les JSON des observations.

## Limites et critique du protocole

1. **Trois dépôts GitHub seulement**, corpus sélectionné à partir de titres de PR : ni représentatif de l'ensemble de GitHub, ni aveugle aux auteurs, ni preuve sur problèmes scientifiques nouveaux.
2. Certains titres sont corrélés à la probabilité de fusion (par exemple des soumissions refusées) ; toutes les politiques ont accès au même identifiant de dépôt, mais pas aux titres. La distribution de 22 PR non fusionnées et les dépendances entre backports limitent l'interprétation du transfert.
3. `touched_tests` est une convention basée sur les chemins : elle ne certifie pas la présence ou la pertinence de véritables tests.
4. Une seule capture externe a fourni les réponses aux évaluateurs : le nombre d'appels par bras est **simulé**, pas mesuré réseau. Ni latence contrôlée ni coût monétaire/LLM mesuré.
5. Le modèle d'observation est déterministe et les deux contrôles ont le même coût. La falsification des contenus, l'indisponibilité, le changement temporel, les conflits d'autorité et la qualité de preuves ne sont pas testés ici.
6. L'absence de bénéfice concerne cette tâche AND et les priors définis, non l'ensemble des stratégies ou l'efficacité d'Omega comme architecture générale.

## Étape suivante : test véritable de sélection de méthode

Le programme Omega doit maintenant être évalué sur **un ensemble hétérogène de problèmes non réductibles à la même règle de court-circuit**. Pré-enregistrer, avant les cas :
- Quatre stratégies réellement distinctes : preuve formelle / calcul exact / vérification d'autorité normative / recherche de réfutation.
- Comparateur fort qui choisit une stratégie fixe par type de problème, même bibliothèque, même budget.
- Sélection adaptative permettant de changer de représentation ou d'outil seulement à la suite d'une observation qui peut affecter la décision.
- Cas où l'adaptation est inutile et coûteuse, plus cas où elle est réellement nécessaire.
- Holdout indépendant, mêmes modèles si génération LLM, même nombre et coût de consultations et notation de la qualité finale en aveugle.

La question pertinente n'est plus « adaptatif > toujours deux consultations », mais **« adaption > meilleure règle conditionnelle accessible avec les mêmes informations ? »**

**Statut de cette PR : expérimental en brouillon. Ne pas fusionner dans `main`, écrire SQLite, ni promouvoir un résultat dans CORE.**

## Reproduction

Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```sh
python strategic_first_check_transfer.py
python -m unittest -v test_strategic_first_check_transfer test_strategy_structure_stress
```
