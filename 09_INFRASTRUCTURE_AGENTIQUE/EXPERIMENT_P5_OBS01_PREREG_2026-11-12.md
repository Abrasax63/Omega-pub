# P5-OBS-01 — Pré-enregistrement : observabilité contrôlée et vérification à valeur future

**12 novembre 2026 — protocole gelé avant tout code et tout résultat P5-OBS-01.**

## Sources internes : ni théorème nouveau, ni transfert implicite

1. [DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md](../02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md) : filtre des ensembles survivants `B_{i+1}=T(B_i)∩π^{-1}(y_{i+1})`, exact pour les mots observés ; contre-exemple minimal `T=(0,2,2)`, `π=(0,0,1)`, `001` localement autorisé mais irréalisable, bien que `Δ_h=∅` pour tout horizon. Les défauts aux extrémités ne détectent pas tous les fantômes internes.
2. [DELTA_H_STRATEGIE_COUVERTURE_2026-09-29.md](../02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_STRATEGIE_COUVERTURE_2026-09-29.md) : extension à actions et avertissement : certains rangs de coalitions ne sont pas invariants sous deux présentations de même langage ; préférer ensembles compatibles, résiduels et témoins de discrimination au « rang de coalition » brut.
3. Recherche externe : [survey sur observabilité de réseaux booléens contrôlés](https://link.springer.com/article/10.1007/s11768-022-00122-x) ; [observabilité et diagnosabilité des systèmes finis](https://doi.org/10.1016/j.automatica.2017.02.042) ; [active sensing / belief POMDP](https://doi.org/10.1145/3583068) ; [bandits with costly reward observations, UAI/PMLR 2023](https://proceedings.mlr.press/v216/tucker23a.html). Ces champs précèdent Omega, pas de revendication d'originalité.

## Question testée et modèle exact

**Question :** dans un espace d'hypothèses cachées fini, deux vérifications peuvent-elles avoir **une valeur conjointe** même si aucune ne change à elle seule la décision ? Une politique basée sur l'ensemble exact des états compatibles peut-elle détecter ce mécanisme ; que donne la comparaison à l'optimisation bayésienne exacte et à la valeur immédiate myope ?

Monde **synthétique, déterministe et entièrement énumérable**, sans LLM ni données privées :
- `X={(u,v,z): u,v ∈ {0,1}, z ∈ {0,1,2,3}}`, 16 états équiprobables.
- L'étiquette finale à décider est `y=u XOR v`. La variable `z` est une nuisance sans effet sur le verdict.
- Observation initiale `π(x)=*` constante : les 16 états sont d'abord indiscernables.
- Trois vérifications observables et déterministes : `PROBE_U` renvoie `u`, coût `0.12` ; `PROBE_V` renvoie `v`, coût `0.12` ; `PROBE_Z` renvoie `z`, coût `0.05`. Il s'agit d'une **extension contrôlée** `T_a=id, π_a(x)` ; ne pas traiter cela comme le résultat autonome sur `Δ_h`.
- Budget maximum **deux vérifications différentes**. Après chaque résultat, mise à jour exacte de l'ensemble des hypothèses possibles et conservation de la trace complète.
- Décision finale : prédire `0` ou `1` avec +1 si juste et −2 si faux, ou s'abstenir avec +0.05. La politique paie le coût des vérifications. Aucun contrôleur n'observe le véritable état avant l'action ou le résultat d'une vérification non effectuée.
- Les hypothèses sont uniformes ; l'unique objet d'incertitude est cet ensemble fini.

## Politiques et témoins pré-enregistrés

1. `no_probe` : pas de vérification, décider au mieux ou s'abstenir.
2. `myopic_decision_voi` : à chaque étape, évaluer un contrôle par l'amélioration de **la décision terminale immédiatement après une seule vérification** moins son coût ; s'arrêter si aucun gain positif.
3. `entropy_greedy` : choisir à chaque étape le probe maximisant la réduction d'entropie des **états microscopiques complets** (non de l'étiquette cible), ignorer l'utilité décisionnelle jusqu'au budget épuisé ; coûts soustraits ensuite. Le témoin doit choisir la nuisance `Z` d'abord (2 bits d'information sur le micro-état).
4. `exact_bayesian_dp` : programmation dynamique exhaustive sur états de croyance et budget, maximisant **exactement** l'espérance de gain terminale moins coûts; algorithme standard fort, implémentation indépendante.
5. `omega_observable_candidate` : extension **expérimentale** ; filtrage exact des survivants (analogue à `B_i`, ici `T_a=id`), test de possibilité de la décision dans chaque fibre et récursion prospective sur résultats de vérifications; appel au véritable `planner.plan_mission` uniquement pour l'explicabilité. Ce n'est PAS un apprenant déjà présent dans P1. Il doit égaler `exact_bayesian_dp`, sans revendiquer une nouveauté algorithmique.
6. `fixed_u_then_v` : témoin séquentiel prédéfini qui connaît les deux vérifications pertinentes et sert de **contrôle négatif contre toute prétendue originalité** : ce témoin devrait aussi obtenir la politique optimale sur ce monde.

Le classement de probes à égalité : `U, V, Z`. Aucune inférence de modèle. Un contrôleur dont les décisions dépendent du vrai `(u,v,z)` avant une observation est invalidé.

## Hypothèses et résultats prédits AVANT calcul

- Sans aucune observation : chaque étiquette est possible avec probabilité 1/2, donc réponse directe moyenne `0.5*1+0.5*(-2)=-0.5`, abstention `+0.05` optimale.
- Après `U` seul ou `V` seul : la parité reste exactement 1/2–1/2 ; aucun gain terminal immédiat, donc VOI myope s'abstient. `Z` seul également sans pertinence pour `y`.
- Avec `U` puis `V`, toutes les branches identifient la parité et la valeur nette est `1-0.12-0.12=0.76`, meilleure que l'abstention.
- Stratégie entropie micro-état : `Z` révèle 2 bits, `U` et `V` chacun 1 bit ; budget deux, Z suivi de U/V ne permet pas de prédire la parité ; valeur nette attendue `0.05-0.05-0.12=-0.12`.
- Valeur de la politique exacte dynamique bayésienne et candidat Omega : **0.76** pour les 16 états, et les politiques arrêtées après un seul probe doivent préférer l'abstention. Le témoin `fixed_u_then_v` doit aussi produire **0.76** : une égalité empêche d'attribuer une originalité à Omega.
- L'exemple interne `001` doit produire `B_i=∅` à la troisième observation, mais rester localement compatible avec `Q` ; les défauts `Δ_h` d'extrémités sont vides pour h=1,...,20, le théorème de tous les horizons restant sourcé au travail antérieur, non ré-établi ici.

## Critères de validation, falsification, limites

- Exécuter **les 16 états cachés exhaustivement** pour chaque politique, rejouer décisions/actions et observations sans fuite du vrai état, certifier la valeur moyenne empirique exacte égale à l'espérance calculée par chaque planificateur.
- **Contrôle croisé obligatoire** entre deux implémentations indépendantes du DP (énumération des sous-arbres finis et récursion d'ensembles survivants). Un écart invalide la campagne.
- Tests anti-fuite : seule réponse de la vérification choisie communiquée ; une réponse incompatible avec l'ensemble survivant doit produire une erreur et aucune décision finale.
- Tests adversariaux : un budget d'une seule vérification, une observation nuisance, un historique impossible `001`, un système rendu entièrement observable à l'initialisation (aucune vérification ne doit alors être achetée), un probe répété non autorisé.
- **Conclusion autorisée** : la représentation d'observabilité permet une **analyse structurelle exacte** et une amélioration de décision sur ce monde contre une valeur d'information *myope* ; l'optimiseur bayésien exact et un témoin trivial atteignent le même résultat, donc **aucun gain propre à Omega**. Ce n'est **ni une validation sur des erreurs réelles de modèles, ni sur une mémoire scientifique, ni une extension démontrée du théorème `Δ_h` aux POMDP**.
- Statut `EXACT_FINITE_SYNTHETIC_OBSERVABILITY_NOT_REAL_OMEGA_ADVANTAGE`. P1 et `main` inchangés, PR en DRAFT. Exécuter le calcul Python sur GitHub Actions (0 API et aucune inférence payante) et conserver le résultat JSON.
