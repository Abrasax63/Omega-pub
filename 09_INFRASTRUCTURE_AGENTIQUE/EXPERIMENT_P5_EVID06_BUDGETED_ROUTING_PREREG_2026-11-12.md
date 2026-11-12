# P5-EVID-06 — allocation sous budget de véritables consultations SQL et contrôles BIRD

**12 novembre 2026. Pré-enregistrement AVANT implémentation et évaluation du nouveau protocole.**

## Question scientifique et cadre

Sur des **sorties réelles historiques** de GPT-5-mini avec et sans outils SQL, un contrôleur choisit-il mieux **quelles affirmations envoyer à la méthode avec SQL** quand il ne peut payer que **2 consultations par lot de 8** ? Les ensembles d'observations et les certificats de provenance donnent-ils un avantage au-delà d'une règle classique contextuelle ? Résultats potentiellement négatifs publiés sans réajuster le test.

La méthode `with-SQL` est une **autre réponse du même modèle produite antérieurement dans ClaimDB**. Ce n'est **ni un vérificateur exact ni un fournisseur indépendant**, et ses traces d'appels ne sont pas des preuves SQL validées. Les labels de référence sont les **annotations publiques de ClaimDB**, non un oracle independently reconstitué.

Sources épinglées (ClaimDB Theologitis et al., ACL 2026) :
- commit source `e06c3a22cc14a8ef6858bb5d40bca7925241b98d`
- 1000 claims : `final-benchmark/test-public.jsonl` SHA256 `b87d7062307cfcf5ae862bf03bd7e82f7123ff39cf0b69d3dc5cc25caaaea810`
- GPT-5-mini avec SQL : `experiments/public/gpt-5-mini.jsonl` SHA256 `e31443bd85f46c4edc4a146243bb709634c6330c2914c726630c3f3349edb100`
- GPT-5-mini sans SQL : `experiments/public/no_tools/gpt-5-mini.jsonl` SHA256 `552531cba335298816a998f7a2b6fb548d9cd0eb7f9b47e5d1272809620a9aa6`
- base BIRD authentique `superhero.sqlite` (fournisseur miroir Tarzanagh/QAFD-RAG, commit `2a3a42c8ea4e9c416de0a7fe53c04fab50b756ef`, SHA256 `75e94a2c3236ee3bb2c01fb97a1c4b4c1c269bcefd4eab1d04be323d2d0825b1`), à télécharger **seulement** dans GitHub Actions.

## Cohorte et découpage **sans dépendre du label**

Restreindre aux affirmations de la base `superhero` (120 dans le test ClaimDB). Exclure **les cinq sentinelles déjà étudiées** #4267, #4179, #4324, #3930, #4419 et **les trois nouvelles sentinelles SQL** #15601, #3730, #3971 qui ne sont pas utilisées dans les politiques. Réordonner le reste selon `SHA256("EVID06|2026-11-12|"+str(claim_id))` croissant (hex), puis claim_id. Premier bloc de **24 calibrations**, suivant bloc de **64 évaluations inédites pour cette simulation**, 8 lots de 8 ; les autres claims sont laissées de côté. Ces 64 éléments restent **publiquement accessibles depuis l'origine, donc pas un holdout indépendant**. Aucun tri sur labels, qualité, difficulté ou écart entre modes.

## Information disponible aux contrôleurs

Avant achat : `claim_id`, `claim`, `extra_info`, `db_name`, `verdict_no_tools`, coût conventionnel fixe `0.20`, et taille du lot. **Jamais** le label ClaimDB, le verdict with-SQL, les appels/outils futurs, leurs sorties ou une indicatrice de leur correction. Après achat : `verdict_with_sql`, présence et nombre des événements `function_call_output`, origine de journal `claimdb/claimdb`. Les vérités de test restent accessibles **seulement** à l'évaluateur hors politique. Ne pas attribuer à des observations la connaissance de la correction si elle n'est pas observable.

Classes contextuelles fixées avant analyse :
- `hypothetical` si une clause anglaise contient des marqueurs `if ... would, if ... were, hypothetical, counterfactual` ;
- sinon `subjective` si `most appealing, more impressive, widely regarded, ideal, preferable, better than, compelling, popular among` ;
- sinon `numeric` si chiffre arabe, `exactly, number of, count of, how many, average, percentage, total` ;
- sinon `other`.
Ce sont des heuristiques lexicales **imparfaites**, pas les catégories gold cachées.

## Score et règles sous budget

Réponse publiée : +1 si égale à l'annotation ClaimDB, −2 sinon. Abstention : +0.05 ; tout achat de la méthode avec SQL coûte **0.20 unité fictive**, même s'il échoue. **Deux achats maximum par lot**, 16 sur 64 tests. On choisit selon `p(correct)` estimé **uniquement sur les 24 calibrations** avec lissage de Laplace +1/+1. Valeur immédiate attendue de DIRECT = max(0.05,3p_no−2). Valeur attendue de SQL = max(0.05,3p_sql−2)−0.20. Gain marginal de consultation = SQL−DIRECT. Une décision non achetée (DIRECT ou ABSTAIN) suit le premier maximum ; une décision achetée suit la règle SQL (avec résultat seulement après achat). En cas d'égalité, préférer l'abstention. **Ce modèle de coût ne mesure pas la véritable consommation de tokens ni le prix d'API d'origine**.

Pour éviter un fort surajustement de 24 calibrations, les estimations contextuelles doivent avoir minimum 3 cas de calibration par catégorie, sinon repli sur le prior global. Aucune mise à jour de la qualité des réponses à partir des labels test (ils ne sont pas observables).

## Politiques pré-enregistrées

1. `no_purchase` : aucune consultation, réponses sans outils selon la confiance de calibration.
2. `position_first_two` : acheter deux premières candidates par lot, contrôle non apprenant.
3. `hash_random_two` : acheter deux candidates par hachage déterministe, indépendant de label.
4. `global_voi` : acheter au plus deux candidats si gain marginal global positif, ordre stable du rang de hash.
5. `context_voi` : valeur de l'information **contextuelle** par classe lexicale, tri des gains positifs décroissants (même lissage et seuil).
6. `context_trace_gate` : même `context_voi`, et **après achat** s'abstenir si aucun outil n'a rendu de sortie, même si la réponse SQL est fournie. Contrôle classique de provenance.
7. `omega_observability_candidate` : même contexte et même filtre de traçabilité que `context_trace_gate`, plus certificat `fournisseur unique, source non indépendante, statut de témoignage` ; **il doit égaler le contrôle classique** tant qu'aucune contradiction de preuve exécutable nouvelle n'est disponible. P1 est utilisé au plus pour justification sans modification des résultats de test.
8. `hindsight_oracle` : sélection optimale en connaissant **tous** les labels et modes (borne supérieure non déployable, non comparateur opérationnel).

Aucune politique ne peut prétendre avoir un retour sur la correction de sa réponse à partir du seul retour de SQL. Dans le cas où toutes les politiques fortes produisent la même allocation, signaler **BENCHMARK_NON_DISCRIMINATING**. Dans le cas où Omega est égal à `context_trace_gate`, signaler **NO_SPECIFIC_GAIN**.

## Contrôle SQL réel supplémentaire (séparé de l'évaluation de routage)

Avant téléchargement et exécution de la base BIRD, geler **trois nouvelles affirmations réelles** :
- ClaimDB **#15601** : `40 superheroes tied at top Speed`. Refaire par SQL `COUNT` des héros avec attribut Speed égal au maximum, selon deux formulations distinctes (JOIN versus sous-requête). Témoins : cardinal et valeur maximum.
- ClaimDB **#3730** : `Exactly 42 heroes with the Super Strength power are taller than 200 cm`. Deux méthodes de dénombrement distinctes (JOIN versus IN) et conserver le nombre observé.
- ClaimDB **#3971** : `Invisibility is more prevalent than Super Strength`. Comparer deux cardinalités `DISTINCT hero_id`, via deux SQL structurellement différentes.
Les labels publics sont connus mais **jamais utilisés pour choisir le SQL** ; les trois claims sont exclues du routage test. Empreintes, SQL, nombres et contre-témoins (si pertinents) archiver. **La correspondance phrase/requête est rédigée par l'assistant et n'est pas revue par un évaluateur externe indépendant** ; indiquer explicitement `semantic_review_status=INTERNAL_ONLY`. Toute erreur de schéma ou conflit SQL donne `STOP` sans ajustement rétrospectif.

## Arrêt, critique et gouvernance

- Réaliser les tests anti-fuite et la cohorte exacte avant les téléchargements.
- Vérifier les SHA des **quatre** sources ; ne jamais utiliser des labels manquants, résultats de mode SQL non disponibles ou tables substituées.
- Le test de classification/abstention et ses scores proviennent des annotations de ClaimDB. Il n'est pas une nouvelle expérience GPT-5-mini et ne prouve pas que le contrôleur pourrait reproduire ses décisions sous latence réelle.
- Les requêtes sur la même SQLite ont **une seule source de données**. Aucune promotion de la qualité d'Omega si elle n'est pas supérieure à `context_trace_gate`.
- PR DRAFT, `main` et les PR antérieures inchangées, pas de rediffusion binaire BIRD, pas de coût d'API.

**Statut projeté à contrôler, non anticipé :** `REAL_PAIRED_MODEL_BUDGET_ROUTING_AND_BIRD_SQL_SECONDARY_AUDIT`.
