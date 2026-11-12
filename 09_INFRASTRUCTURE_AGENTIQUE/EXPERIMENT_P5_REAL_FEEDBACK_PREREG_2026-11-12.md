# P5-REAL-01 — Pré-enregistrement d'une boucle adaptative alimentée par de vraies erreurs de modèle

**12 novembre 2026 : protocole écrit AVANT code et inférences de P5-REAL-01.**

## Question scientifique

Une décision de vérification adaptative fondée sur les **réponses effectivement produites** par un modèle ouvert et les **résultats des vérifications qu'elle choisit**, à budget égal, surpasse-t-elle les règles plus simples ? Distinguer **l'erreur ponctuelle** d'un **changement durable de fiabilité** sans accéder aux corrigés de l'évaluation. Un meilleur score purement dû au vérificateur n'est pas attribuable à Omega.

## Source de données et séparation

- Générer pour ce seul protocole **48 réponses réelles** du modèle libre `Qwen/Qwen2.5-0.5B-Instruct`, révision fixée `7ae557604adf67be50417f59c2c2f167def9a775`, greedy, `max_new_tokens=48`. Une réponse par question, **sans rôles Omega** pour isoler la valeur du contrôleur de vérification.
- 4 strates **CRT petits modules, CRT grands modules, taux petits effectifs, taux grands effectifs** ; 12 questions publiques déterministes nouvelles par strate, dérivées exclusivement d'une fonction SHA-256 fixe `P5REAL01|stratum|case_index|field`. Indices 0–3 pour calibration = **16 questions**, indices 4–11 pour test = **32 questions**. Les réponses exactes sont calculées uniquement par des vérificateurs programmatiques, non présentées au modèle.
- Le générateur de questions est l'auteur du protocole, ce jeu n'est **pas** un holdout externe. Aucune donnée privée P5 v0.5 ni clé API.
- L'évaluation des 32 problèmes suit des blocs de huit cas, dans l'ordre **taux petits, CRT grands, taux grands, CRT petits**. L'identité de strate et la taille des nombres sont visibles par le texte ; **ce n'est pas une rupture de monde intrinsèquement cachée**, seulement un changement de population. Le contrôleur ne reçoit aucun indicateur de « phase » supplémentaire.
- Les 16 réponses de calibration peuvent être corrigées avec le résultat exact pour initialiser les paramètres. **Les 32 références de test ne sont jamais données à un contrôleur**, même après une action DIRECT ; ce sont les évaluateurs qui calculent les scores.

## Vérifications réelles et limitées

- Pour CRT, vérificateur limité par la ressource : chercher `x=0..49`. Succès seulement si solution dans cette plage ; `UNRESOLVED` sinon. Pour DATA, comparaison exacte des taux par produits croisés, mais ressource plafonnée : résultat seulement si `sum(total_A)+sum(total_B) <= 100`, sinon `UNRESOLVED`. Ces limites sont **déterministes et artificielles**, mais exécutées par du code réel (non par un tirage simulant une erreur). Elles rendent les vérifications **incomplètes, jamais faussement correctes** sur ce domaine.
- Un deuxième oracle indépendant calcule toutes les références (CRT : inverse modulaire ; DATA : `Fraction`), validé par tests contre la méthode bornée lorsqu'elle résout.
- Les résultats de la vérification sont révélés au décideur **uniquement après qu'il a payé et demandé cette vérification**. Une action DIRECT ou ABSTAIN ne retourne **aucune vérité ni récompense au décideur** ; les scores de ces actions sont calculés hors-ligne par l'évaluateur. Les contrôleurs connaissent les 16 cas de calibration et leur correction ; les contrôles classiques ont exactement la même information.

## Actions, budget et score communs

Chaque contrôleur voit : question publique, famille/strate calculable du texte, réponse brute et réponse extraite (ou `None`), historique de **ses seules vérifications**. Pour 32 décisions, plafond commun de **16 vérifications**, coût de vérification CRT **0,35** unité, taux **0,20** unité. Les coûts sont des **utilités fictives**, pas une facture.

- `DIRECT` : si la réponse extraite est correcte, gain +1 ; si erronée, −2 ; si non extraite, l'action devient abstention +0,05.
- `VERIFY` : si l'outil conclut, publier son résultat exact : gain +1 moins coût ; sinon s'abstenir, gain +0,05 moins coût. Seule cette action reçoit un retour exploitable par le contrôleur, incluant le fait que la réponse initiale était correcte ou non **lorsque l'outil aboutit**.
- `ABSTAIN` : +0,05. Jamais de réponse inventée si l'outil n'aboutit pas.
- Aucune politique ne dépasse 16 vérifications. Comparaisons d'utilité totale appariées, erreurs réellement laissées, erreurs évitées, abstentions, vérifications, coûts, décisions de changement et recours à la mémoire.

## Contrôles et candidat — architecture gelée

1. `direct` : toutes les réponses du modèle, sans vérification.
2. `verify_budget` : vérifier les 16 premiers cas, ensuite direct (témoin fort naïf).
3. `abstain` : aucune réponse.
4. `kind_rule` : exploiter l'exactitude et le taux de réussite du vérificateur **mesurés sur calibration**, par type CRT/DATA ; choisir l'action de meilleure utilité attendue.
5. `stratum_rule` : idem par strate taille/type (contrôle simple fort), sans mise à jour.
6. `online_beta` : `stratum_rule` avec moyenne de Laplace mise à jour sur ses vérifications de test ; historique append-only, **sans** détecteur.
7. `omega_candidate` : même pré-calibration et mises à jour que `online_beta`, mais propose une remise en cause uniquement si au moins **3 vérifications récentes** dans une strate et `abs(mean_3 - mean_calibration)>=0.40` ; inscrit alors une alarme dans un journal, réévalue l'utilité avec les dernières vérifications et peut revenir au modèle global si ce signal disparaît. Chaque alarme doit être traçable ; elle peut être un faux positif. Ce n'est **pas** le Prisme P1 actuel, mais une extension de contrôle utilisant son planificateur pour justifier une vérification initiale.
8. `omega_no_alarm` : même estimation en ligne, sans alarme ni révision. C'est un témoin de causalité ; le signal d'alarme ne doit pas obtenir gratuitement des corrigés.

Pour les règles d'utilité : `p` estimé par Laplace `(bonnes+1)/(cas+2)`; si réponse absente -> DIRECT vaut +0,05 ; sinon DIRECT vaut `3p−2`. Couverture de vérification estimée de même, VERIFY vaut `coverage*1 + (1−coverage)*0.05 − cost`; ABSTAIN vaut `0.05`. Choisir l'action estimée la plus favorable, égalités `ABSTAIN`, puis `DIRECT`, puis `VERIFY`. Budget de 16, sans information sur les cas futurs. Pour les cas non parsés, DIRECT devient abstention, pas une erreur.

## Résultat attendu et falsification

**Mesure primaire :** `total_utility(omega_candidate) − total_utility(online_beta)` sur les 32 cas de test, avec comparaison supplémentaire à `stratum_rule` et `verify_budget`. L'affirmation de plus-value spécifique d'Omega est **réfutée sur cette expérience** si le gain est nul/négatif, si les alarmes n'affectent aucune décision, ou si un témoin simple fait mieux. Ne pas inventer une démonstration si l'échantillon est trop petit.

Rapporter en outre la séparation des réponses fausses des réponses non parsées, la fiabilité et les échecs du vérificateur, le nombre de changements de stratégie, et les classements par quatre strates. Le test est exploratoire, sans inférence de généralisation statistique. Si la politique ne reçoit jamais assez de confirmations pour déclencher une alarme, rapporter cette **absence d'information**, pas un « succès de stabilité ».

## Ressources, sécurité et statut

GitHub Actions sur un runner standard du dépôt **public**, 0 OpenAI API, 0 accès aux données privées, 0 calcul sur smartphone. La génération de 48 sorties est réelle et coûte du CPU distant, tandis que le contrôleur est déterministe. Statut obligatoire `REAL_MODEL_PUBLIC_PILOT_NOT_INDEPENDENT_HOLDOUT`. P5-REAL-01 n'est pas une évaluation de la mémoire scientifique complète ni de GPT-6. Aucun changement de `main` ou des PR #47–52.
