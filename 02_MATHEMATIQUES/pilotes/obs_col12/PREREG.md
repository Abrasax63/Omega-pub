# OBS-COL-12 — Pré-enregistrement : garde de conformité à oracle boîte noire

Date : 16 novembre 2026. Branche `experiment/obs-col12-blackbox-conformance-gate-2026-11-16`, empilée sur PR #114 ; aucune modification directe de `main`. **Engagement enregistré avant le code et avant le premier run OBS-COL-12.**

## Déjà étudié — ne pas refaire

- PR #81 : laboratoire de synthèse/évaluation de vérificateurs, sans application vérifiée à l'apprentissage actif de modèles Moore.
- PR #76 : stratégies de vérification à budget de calcul exact sur un univers fini *connu*.
- PR #90 / #92 : falsification de familles et alertes hors horizon avec sondes proposées.
- PR #114 : **contrôle exact post hoc** par BFS du graphe produit, qui **connaît le vrai automate** et n'est donc pas transmissible à un agent qui n'a qu'un accès boîte noire. Exactement 3 des 20 modèles étaient incorrects, tous sur `register5.dot` ; contre-exemple exact `F L F L F L F L L`.

Il manque un contrôle **AVANT l'acceptation, à l'aide du seul oracle d'observation** de la cible, avec coût mesuré. Cette expérience est un *diagnostic de reprise sur résultats dévoilés*, **pas** un nouveau holdout aveugle.

## Modèles préengagés, résultats connus AVANT ce pilote

Réutiliser uniquement les fichiers Radboud `register3.dot` (contrôle correct) et `register5.dot` (difficulté connue), empreintes verrouillées dans `obs_col11/SOURCE_SHA_LOCK.json`. Aucun changement de modèles, règle d'apprentissage ou graines. Sur register3 : modèles `fixed` et `omega_candidate`. Sur register5 : `fixed`, `coverage_only`, `omega_candidate`, `KV`. Le composant d'apprentissage est le vrai `fit_one` figé en PR #114, sans aucun accès à l'audit exact lors de sa décision.

## Les trois vérificateurs boîte noire

Comparaison sur chaque même candidat **déjà appris et gelé** :
- **W AALpy original** : `aalpy.oracles.WMethodEqOracle`, méthode classique de conformité, hypothèse d'une borne d'états `max_number_of_states = n_hypothese + 1` ;
- **Wp AALpy original** : `aalpy.oracles.WpMethodEqOracle`, même borne déclarée et même alphabet ;
- **Wp réordonné** : *exactement* les mêmes tests que le générateur Wp publié d'AALpy (`first_phase_it`, `second_phase_it`), mais triés avec la fonction `coverage_ranking(..., memory=True)` de la PR #110, en utilisant uniquement le **modèle hypothétique** et les préfixes observés pendant l'apprentissage. Vrai P1 avant chacun des resets. Ce n'est **pas** un nouveau théorème, ni une méthode Omega originale.

**Borne `n+1`** : une **hypothèse de test**, jamais le nombre réel d'états connu seulement du contrôle exact post hoc. Pour les modèles 27 états de register5 alors que la cible en a 32, cette borne est fausse. Même l'absence de contre-exemple après W/Wp ne certifiera **aucune** équivalence. Le test de référence `fixed` exact ne devrait pas être déclaré fautif.

## Budget, vérité, attribution

- Chaque (modèle candidat, vérificateur) reçoit une **nouvelle instance** du simulateur source verrouillé, **600 réinitialisations max et 8000 symboles d'action max**, strictement pour la vérification **après apprentissage**. Les coûts d'apprentissage, déjà publiés par #114, sont additionnés séparément.
- Les comparateurs et le candidat ne voient jamais le vrai graphe ; la source est encapsulée dans `AutomatonSUL` ; les sorties arrivent uniquement par `step`. Pas de `PerfectKnowledgeEqOracle`. L'évaluateur exact peut contrôler après coup, **jamais guider** les tests de vérification.
- Pour Wp réordonné, dédupliquer les mêmes mots que Wp dans l'ordre naturel (conformément à son cache), réordonner sans retirer de mots, enregistrer SHA-256 des candidats et de la permutation (après préparation, avant interrogation). Le classement doit utiliser les préfixes d'entraînement (non les sorties réservées).
- Le vérificateur retourne `REFUTED_BY_MEASURED_COUNTEREXAMPLE` seulement en cas de divergence de sortie **vraiment mesurée** à état de reset identique, avec le mot minimal *dans l'exécution de la sonde détectrice* ; sinon `NO_COUNTEREXAMPLE_WITHIN_BUDGET` ou `BUDGET_EXHAUSTED`. Aucune certification sur absence de divergence.
- Si les vérifications ne retrouvent pas le contre-exemple connu sur register5, **résultat négatif et informatif**, sans ajouter a posteriori le mot connu au catalogue.
- Viser un signal d'intérêt : **taux de détection sur les 3 modèles incorrects connus**; signaler les faux positifs sur 3 corrects, nombres de resets, symboles et CPU total. Ne pas revendiquer de généralisation sur ces cibles déjà révélées ni gain propre à Omega si une Wp classique fait aussi bien ou mieux.
- Aucun recalibrage sur le témoin `F L F L F L F L L`, aucun appel LLM payant, aucun envoi d'e-mail, aucune fusion ni mutation de CORE.

## Considérations de rigueur

La méthode W/Wp exige une borne supérieure de taille du système implémenté pour ses garanties de conformité. Ici, nous ne possédons **pas** cette borne de l'environnement au moment de l'apprentissage : le banc compare des détecteurs sous budget, pas une certification formelle. Les contrôles exacts de #114 sont connus de l'évaluateur seulement. La politique `coverage_ranking` est une heuristique classique préexistante, pas une intelligence auto-inventée.
