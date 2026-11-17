# OMEGA-EXACT-ORACLE-05 — avenant RÉTROSPECTIF, 17 novembre 2026

**Pourquoi cet avenant existe** : les contrôles du contrat prospectif initial `dc02ab7` ont échoué sur [run CI #44158601275](https://github.com/Abrasax63/Omega-pub/actions/runs/44158601275) : il n'existe pas 32 modèles admissibles inédits après exclusion des pools #143/#145/#157/#158/#159/#160. Un second échec est un test qui lisait le premier choix avant d'appeler `solve()`; ce test sera corrigé **sans changer l'algorithme ni les critères originaux**.

**Décision méthodologique** : on maintient `INSUFFICIENT_NEW_MODELS` comme résultat définitif du **projet de holdout prospectif**, sans ouvrir un faux holdout et sans changer les exclusions après coup. Le nouveau travail ci-dessous est explicitement **une calibration post-hoc**, non une validation scientifique indépendante et non un remplacement des engagements `dc02ab7`.

## Analyse rétrospective sans entraînement

- Reconstruire exactement les **24 ensembles de 16 hypothèses déjà exposés** du HOLDOUT de la [PR #160](https://github.com/Abrasax63/Omega-pub/pull/160), via `cost_to_go.fresh_pools` et `cost_to_go.build_instances(..., 24, 2000)`, mêmes tarifs alternés (1,5)/(5,1), menu figé de 64 questions.
- Ces 24 ensembles sont **déjà publics** : le score obtenu ici ne sera jamais présenté comme un nouveau holdout indépendant ni utilisé pour justifier l'apprentissage d'une nouvelle variante sans jeu distinct.
- Évaluer l'oracle **exact** `F(S)=min_q |S|c(q)+F(S0)+F(S1)`, PRICE_AWARE et BALANCED sur chacun des **16 mondes possibles** par ensemble, avec observations terminales payées et prior uniforme. Ces méthodes **ne sont pas réentraînées**.
- Journaliser les coûts, profondeurs, numérateurs exacts `F(root)`, certificats de rejouage et les écarts `PRICE_AWARE-OPTIMUM`. Étiqueter le résultat final `RETROSPECTIVE_ONLY_NO_FRESH_HOLDOUT`, quelle que soit l'ampleur de l'écart.
- Préserver à titre **descriptif** les statistiques `instances_at_least_10pct_gap`, le budget 12, les moyennes, sans prétendre satisfaire le critère primaire indépendant du protocole initial.
- Effectuer les tests d'exhaustivité sur micro-cas et le vérificateur indépendant des chemins, sans réutiliser le score pour retoucher le solveur.
- Ajouter un champ `provenance` indiquant le run prospectif avorté, la PR #160, ce commit de portée, les règles d'exposition et le statut d'interprétation.
- Si même le calcul rétrospectif échoue, rendre l'indétermination explicite et conserver les logs sans substituer une heuristique au résultat exact.

Ce travail détermine si **le solveur de référence** fonctionne et caractérise la marge théorique **sur des problèmes historiques**, mais pas si l'apprentissage d'Omega s'améliore, ni si la performance se généralise. Rester en DRAFT ; ne rien fusionner dans `main`.
