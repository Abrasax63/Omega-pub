# OMEGA-STRAT-001 — pré-enregistrement : choix du premier contrôle et transfert GitHub

**11 novembre 2026. Statut : benchmark prospectif public, non aveugle aux auteurs ; pas un test LLM ni une validation multi-domaines.**

## Question falsifiable
Omega, à informations et budget identiques, fait-il un meilleur choix du **premier contrôle** qu'une règle simple appris sur le même historique ? La réponse doit être évaluée sur des PR non employées au réglage. Il ne suffit pas de comparer Omega avec une paire fixe qui effectue systématiquement les deux appels.

## Décision, vérité et coûts
Pour chaque PR : `Y = merged AND touched_tests`, où `merged` est le booléen renvoyé par GitHub `get_pr_info` et `touched_tests` signifie qu'au moins un chemin de fichier modifié contient exactement un répertoire `test` ou `tests`, commence par `test_` ou se termine par `_test.py` (convention héritée de la PR #29). Une PR fermée non fusionnée est `merged=false`. La liste des chemins est récupérée par `list_pr_changed_filenames`.

On dispose de deux contrôles binaires : `merged` et `touched_tests`, chacun facturé **une consultation**. Toute stratégie peut s'arrêter immédiatement quand le premier résultat est faux. Plafond strict : deux consultations. Toute absence/erreur d'outil produit **ABSTAIN**, pas un faux. Le score primaire est le nombre de consultations pour aboutir à la réponse exacte, calculé en rejeu des réponses réellement collectées auprès de GitHub ; les appels réseau de collecte ne sont **pas** comptés comme des exécutions séparées des politiques. Zéro coût modèle ou argent mesuré.

## Données d'apprentissage fixes et publiques
Instantané des **12 PR** de la PR #29 : `prism/live_github_pr_gate_observations_2026-11-11.json`. Les valeurs `merged` et `touched_tests` sont l'unique information d'apprentissage autorisée. Aucune valeur de l'échantillon cible ne peut modifier la politique avant le verdict. Chaque fréquence des quatre états reçoit **un pseudo-compte de Laplace = 1**, à la fois globalement et par dépôt, pour éviter les zéros.

## Cohorte cible gelée AVANT consultation des deux critères (24 PR)
Le choix repose sur les identifiants repérés dans des résultats de recherche de PR par titre ; certains titres avaient été vus lors de l'exploration du 11 novembre, mais les deux critères `merged` et `touched_tests` ne sont pas examinés pour ces 24 PR avant ce gel.

- `python/cpython`: #161266, #161728, #161727, #155070, #161162, #160875, #161755, #152702.
- `pallets/flask`: #6155, #6156, #6147, #6145, #6144, #6142, #6124, #6043.
- `psf/requests`: #7586, #7049, #7051, #7499, #5220, #6991, #7023, #6675.

Ces PR ne sont pas un échantillon aléatoire ; certains titres et backports se ressemblent, et les dates/états GitHub évoluent. Regrouper les résultats par dépôt et ne pas traiter les PR liées comme des observations indépendantes.

## Politiques gelées avant les vérités cibles
0. `always_merged` : lire `merged` d'abord, puis `touched_tests` si nécessaire.
1. `always_tests` : lire `touched_tests` d'abord, puis `merged` si nécessaire.
2. `global_marginal` : sur les 12 cas d'apprentissage, choisir la propriété dont la valeur `true` est la **moins fréquente**, puisqu'une réponse `false` suffit à rejeter. En cas d'égalité, `merged` d'abord.
3. `repo_marginal` : même règle calculée séparément sur les quatre cas historiques du dépôt ; si aucun historique, retomber sur `global_marginal`.
4. `Omega_global` : moteur `optimize_policy(max_depth=2,max_cost_milli=2)` sur les quatre mondes `(merged,touched_tests)` avec poids appris globaux +1, décisions `accept/reject`, observations `yes/no`, et un coût fictif de `cost_milli=1` pour chaque contrôle. Ne donner aucune étiquette cible au planificateur.
5. `Omega_repo` : exactement le même moteur, mais avec les fréquences historiques du dépôt +1 ; mode fallback global hors historique.
6. `both_always` : lire systématiquement les deux contrôles, référence non compétitive afin d'exposer le coût de l'absence de court-circuit.

Le code du planificateur Omega doit être utilisé réellement, et sa politique déroulée sur les valeurs cibles après le gel. Les règles simples doivent être autorisées à s'arrêter après un premier `false`. Elles n'ont aucune information inférieure à Omega. Les politiques seront figées à partir du seul historique avant lecture des cibles.

## Mesures
- **Principales** : exactitude, abstentions et nombre de consultations de chaque bras sur les 24 cas ; distribution par dépôt et comparaison appariée `Omega_repo - repo_marginal` et `Omega_global - global_marginal`.
- **Secondaires** : regret face au meilleur ordre déterminé **a posteriori** (oracle de cohorte, jamais un bras admissible) et variation face au pire ordre ; analyse de stabilité si les pseudo-comptes passent de 1 à 2, rapportée comme sensibilité et non optimisation rétrospective.
- **Tests négatifs** : la politique ne lit pas deux fois le même contrôle, ne dépasse pas deux appels, ne conclut pas sans justification, n'interprète pas `closed` comme `merged`, ne profite pas d'une étiquette GitHub provenant du titre, et a une règle de fallback pour dépôts inconnus.
- **Limites** : tous les bras peuvent atteindre 100 % de justesse lorsque les deux réponses sont véridiques et disponibles. L'avantage possible ne porte **que** sur le nombre de consultations ; aucun raisonnement sur les sources hors de GitHub ou un avantage général de résolution de problèmes n'est testé. Un gain de `Omega_repo` sur `always_merged` qui disparaît contre `repo_marginal` **n'est pas un gain stratégique propre à Omega**.

## Processus
1. Enregistrer le présent pré-enregistrement et son commit SHA.
2. Écrire le code d'entraînement/rejeu et vérifier qu'il consomme seulement l'historique.
3. Acquérir les 24 couples de faits depuis GitHub ; enregistrer URL, SHA de PR, date et erreurs. Seconde lecture `fetch_pr` pour le `merged` et le SHA, sans prétendre qu'il s'agit d'un fournisseur indépendant.
4. Rejouer les sept politiques sous mêmes plafonds ; établir résultats et contre-exemples.
5. Lancer les tests dans GitHub Actions ; laisser la PR en brouillon, `main`, SQLite et CORE inchangés.

## Arrêt
Arrêt après 24 cas, aucune substitution de cas malcommodes, aucune adaptation des politiques pendant l'épreuve. Si des valeurs sont indisponibles, publier les `ABSTAIN` et le nombre réellement valide. Ne pas conclure à un avantage adaptatif si une stratégie simple bat ou égale Omega.
