# P5-OBS-04 — pré-enregistrement de désaccords EMPIRIQUES entre deux méthodes de vérification

**12 novembre 2026 — pré-enregistrement avant extraction/lecture des résultats des modèles ClaimDB.** Les étiquettes du jeu public et les formats de code des auteurs ont été consultés pour concevoir le protocole, mais **aucune trajectoire de sortie LLM n'a encore été lue** au moment de ce gel. Le jeu de test est **public, préexistant, non aveugle** ; il ne devient pas un holdout nouveau.

## Sources externes et licences

- [ClaimDB, article ACL 2026](https://aclanthology.org/2026.acl-long.1589/) ; [code et résultats](https://github.com/claimdb/claimdb), **commit-source fixe** `e06c3a22cc14a8ef6858bb5d40bca7925241b98d` (lecture avant pré-enregistrement).
- [Public test annoté, 1 000 cas](https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/final-benchmark/test-public.jsonl). Les étiquettes sont `ENTAILED`, `CONTRADICTED`, `NOT ENOUGH INFO`.
- [GPT-5-mini **sans outils**](https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/experiments/public/no_tools/gpt-5-mini.jsonl) : journal public d'ablation de l'équipe ClaimDB ; [GPT-5-mini **avec outil SQL**](https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/experiments/public/gpt-5-mini.jsonl) : journal Git LFS, pointeur `sha256:e31443bd85f46c4edc4a146243bb709634c6330c2914c726630c3f3349edb100`.
- Licence du dépôt ClaimDB : [CC BY-SA 4.0](https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/LICENSE). **Ne pas réhéberger les journaux entiers** ni les databases dans Omega. Le rapport peut répertorier des identifiants et statistiques agrégées, avec attribution et URL/commit des auteurs.
- FEVEROUS [source officielle](https://fever.ai/dataset/feverous.html) et [licence conditionnelle Wikipedia/CC BY-SA 3.0](https://fever.ai/download/feverous/license.html) : **comparateur potentiel**, pas données déclarées exécutées dans cette campagne. Les textes/tables sous licences mixtes nécessitent un audit avant redistribution.

## Hypothèses et question scientifique

Examiner des **désaccords réels et documentés** entre GPT-5-mini sans base et GPT-5-mini utilisant une base SQL sur les **mêmes identifiants** ClaimDB. La présence d'un désaccord de modèle n'est pas, en soi, une contradiction entre **témoins de vérité indépendants**.

Hypothèse à réfuter : un filtre de prudence structurel fondé sur le désaccord (décider seulement si les deux méthodes s'accordent) peut-il réduire le taux de faux verdicts parmi les verdicts publiés ? Rapport de couverture requis. **Ne pas attribuer l'effet à Omega**, car ce témoin est une simple règle classique. Faire aussi l'audit des abstentions `NOT ENOUGH INFO` selon l'étiquette publiée, séparément des refus techniques d'extraction.

## Acquisition et contrôle de fidélité

Exécuter sur GitHub Actions gratuit (sans modèle et sans API payante) :
1. `actions/checkout@v4` du dépôt Omega sur la PR, puis second checkout de `claimdb/claimdb` au commit précis ci-dessus, avec `lfs: true` et `sparse-checkout: final-benchmark, experiments/public/gpt-5-mini.jsonl, experiments/public/no_tools/gpt-5-mini.jsonl`. Installer `git-lfs` si nécessaire. Vérifier que le fichier `gpt-5-mini` **n'est pas un pointeur LFS**, mais une archive de réponses ; vérifier SHA256 == oid du pointeur, sinon marquer `UNAVAILABLE_SOURCE`. Ne jamais remplacer par des étiquettes fictives.
2. Vérifier la présence des **1 000 `claim_id` uniques** dans `test-public.jsonl` ; ne pas supposer que les fichiers de résultats contiennent ces 1 000 observations avant lecture. Le fichier des résultats sans outils est déjà accessible mais son schéma de sortie reste à auditer.
3. Détecter le schéma des journaux de modèles et **exiger une clé explicite de jointure `claim_id`** ou une séquence avec manifeste source prouvant l'alignement. Refuser une jointure par simple ordre sans garantie officielle. Normaliser les verdicts **uniquement lorsqu'ils valent explicitement une des trois étiquettes** ; `UNKNOWN` technique sinon. Aucun texte justificatif interprété comme verdict, aucune référence `gold` utilisée pour décoder la prédiction.
4. Consigner erreurs, trous de logs, clés dupliquées, taux d'étiquettes extraites, empreintes sources et provenance par modèle. Si des trajectoires SQL sont disponibles, ne compter les requêtes **effectivement consignées** ; une instruction de modèle « j'ai consulté » ne vaut pas une preuve que la base a été réellement interrogée.
5. Si les deux méthodes ne peuvent être jointes avec sécurité, **ne produire aucun score apparié**. Publier `INCOMPLETE_UNJOINABLE_MODEL_TRACES`. Conserver seulement des statistiques non appariées si fiables.

## Politiques et critères GELÉS (sans entraînement ni seuil réglé)

Sur l'intersection stricte des `claim_id` où les deux sorties existent et se parsèment :
- `no_tools` : utiliser le verdict sans outils ;
- `sql_tools` : utiliser le verdict du modèle avec SQL ;
- `agree_or_abstain` : publier le verdict seulement si strictement égal, sinon `ABSTAIN` (refus **distinct** de `NOT ENOUGH INFO`).
- `prefer_sql_when_disagree` : retourner `sql_tools` en cas de divergence ; **identique à SQL** et utilisé comme contrôle négatif.
- `oracle_after_disagreement` : choix de la bonne sortie en utilisant **la vérité du jeu** a posteriori, seulement comme **plafond non déployable**, pas un agent réel.
- `reject_all` : refuser toutes les conclusions.

**Mesures** : couverture, décisions fausses, justes et `ABSTAIN`, taux d'erreurs `wrong/published`, proportion de désaccords, exactitude sur désaccords conditionnellement à leur existence, réduction de risque *avec coût d'abstention*, sous-ensembles E/C/NEI ; confiance de Wilson ou intervalle binomial sur nombre de cas mais rappeler la dépendance des cas par base `db_name` (pas des tirages indépendants). **Risque principal :** `+1` si verdict exact, `−2` si faux, `+0,05` pour abstention. Les deux conditions ont des coûts d'accès aux outils inconnus : **ne pas** comparer leurs profits comme si les requêtes SQL étaient gratuites, ni prétendre à un avantage coût/latence.
- Si une réponse du modèle est `NOT ENOUGH INFO` et l'étiquette gold aussi, c'est **une bonne prédiction**, pas un refus `ABSTAIN`.
- Les étiquettes de test ne doivent jamais être visibles par la politique avant sa décision.
- Aucune vérité des 1 000 cas ne peut être présentée comme indépendamment **recalculée** sans téléchargement et exécution des bases BIRD, ce qui n'est pas prévu.

## Conditions de réussite / d'échec

**Succès technique** : logs authentiques des deux bras récupérés et alignés, prédictions vérifiables sans fuite, programme testé, rapport reproductible. **Gain de fiabilité** : `agree_or_abstain` publie moins de faux verdicts que la meilleure méthode seule, **avec couverture déclarée**, mais n'est pas un gain propre Omega. **Échec scientifique** : aucune mesure possible de l'indépendance de deux fournisseurs, car deux bras utilisent **le même modèle de base** et le même étalon ClaimDB ; Omega P1 n'est pas ici un apprenant. Refuser toute annonce de supérieur à un contrôle classique non implémenté.
- Test adversarial : jointure permutée, `claim_id` dupliqué, verdict inventé, perte des originaux LFS, absence de log SQL ou de référence de base, ambiguïté `NEI` / abstention.
- Compléter par FEVEROUS une autre fois pour l'analyse des **ensembles de preuves réels** ; cette campagne se limite à la provenance de deux méthodes de verdict et ne constitue pas une vérification indépendante des bases.

**PR DRAFT, pas de modification de `main` ni promotion de la méthode dans CORE.**
