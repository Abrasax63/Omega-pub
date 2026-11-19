# TRAIN25 — préenregistrement avant données et code (2026-11-19)

## Objectif expérimental
**Mettre réellement à jour des poids entraînables** d'un modèle de langage de petite taille via LoRA supervisé et déterminer si cela améliore la traduction **d'une idée mathématique déjà donnée** en une expression formelle exacte. Cette expérience ne teste **pas** encore la génération spontanée d'une nouvelle représentation ; elle attaque le blocage constaté dans les runs GEN24 #44498989709 et CREATIVE02 #44500325630 : passage idée → langage vérifiable.

Modèle de démonstration choisi pour CPU : `HuggingFaceTB/SmolLM2-135M-Instruct` (Apache 2.0), **pas** les poids du Qwen 3B utilisé par Omega dans GEN24. PeFT LoRA sur `q_proj` et `v_proj` avec rang 8, alpha 16, dropout 0, AdamW, CPU, float32, graine 20261119, 24 mises à jour (batch 1, séquence max 128), lr 0.001, température 0 pour l'évaluation. L'environnement devra enregistrer version, révision, SHA de l'adaptateur et sommes de paramètres avant/après. Aucune exécution du code fourni par le modèle.

## Mission et sorties
Deux familles mathématiques classiques **connues du corpus d'entraînement** :
- Reachability par actions `start XOR move`, `moves` réutilisables → expression canonique stricte `EXPR: rank(moves) == rank(moves + [start ^ target])`.
- Chaîne de parenthèses équilibrée → expression canonique `EXPR: sum_balance(s) == 0 and min_prefix_balance(s) >= 0`.

Ces expressions sont **fournies par le concepteur dans les cibles de formation** ; tout succès ultérieur ne doit jamais être présenté comme l'invention d'une formule ou d'une théorie. `rank`, `sum_balance` et `min_prefix_balance` sont interprétés dans un langage sécurisé et calculés exactement. Une catégorie de requêtes scientifiques hors de ces deux familles exige la réponse `ABSTAIN`, sans invention.

## Jeux et fuites
Prégeler puis committer :
- `TRAIN_FROZEN.json` : 96 exemples d'énoncés variés (48 XOR, 36 parenthèses, 12 abstentions) construits par templates, sans énoncé identique au test.
- `HOLDOUT_FROZEN.json` : 18 requêtes nouvelles (6 XOR, 6 parenthèses, 6 hors portée), avec labels séparés ; aucun prompt identique, schéma grammatical distinct. L'évaluation n'est pas un véritable benchmark externe indépendant.
- Un second **holdout de transfert** de 6 descriptions du troisième domaine (observabilité finie), non entraîné, demande `ABSTAIN` ; la capacité de transfert à une idée utile **non démontrée** s'il s'abstient.
- Les ensembles sont **publics dans le dépôt, mais le script de formation et son job n'ouvrent jamais le holdout** : ceci est une séparation de pipeline, pas un coffre de sécurité contre un adversaire ayant accès au dépôt. Ne pas appeler ce holdout « secret ».

## Évaluation
À génération identique (`greedy`, maximum 45 nouveaux tokens, même format de requête, mêmes 24 cas), calculer **AVANT** et **APRÈS** LoRA :
- reconnaissance de sortie stricte `EXPR: ...` ou `ABSTAIN` et exactitude littérale contre cibles, sans nettoyage/repair ;
- efficacité sémantique sur **tous** les tests finis réservés : 12 cas XOR par description (6 vrais / 6 faux) et 12 mots de parenthèses (6 corrects / 6 incorrects), calcul de la formule par interpréteur sûr ; toute formule non admise = abstention, pas réussite ;
- taux de faux verdicts, abstentions justifiées et injustifiées ; exactitude sur 24 prompts ;
- `D` : référence forte, algorithme classique d'élimination GF2 / pile, **100 % par définition des domaines**, n'est pas dépassable sur cet ensemble.
- pertes d'entraînement et nombre de paramètres LoRA modifiés, empreintes et coûts (durée CPU, tokens) ; méfiance envers un simple gain de format plutôt qu'un gain de raisonnement.
- Barrière de non-régression : ne jamais promouvoir l'adaptateur si des erreurs silencieuses augmentent ; gain doit venir de cas nouveaux correctement traités sans fuite, et pas d'une augmentation des affirmations non vérifiées.

## Critères de vérification
**Réussite technique** : poids LoRA réellement mis à jour (`delta L2 > 0`), unité de sauvegarde existante et réinjectable, score base et score adapté sur les mêmes cas avec même tokenizer et décodeur, SHA des fichiers, journal complet.
**Amélioration de compétence** : `accuracy_post > accuracy_pre` sur le holdout, `false_claims_post <= false_claims_pre` et pas d'échec de l'oracle. Si condition non remplie : `TRAINED_NO_EVIDENCE_OF_GAIN`.
**Créativité autonome** : `NOT_DEMONSTRATED` quel que soit le score, puisque la formule cible fait partie de l'entraînement.
**Régression infra** : disponibilité CPU/Hugging Face/pip insuffisante → `INDETERMINATE_INFRA` ; ne pas inventer une amélioration.

## Contraintes
Aucune API payante, pas d'usage de GPU promis, aucune certification mathématique automatique, aucune fusion ni modification de `main`, pas d'activation sur le site/cycle autonome. Les modèles et scripts externes téléchargés restent un risque de dépendance ; pinner une révision de poids et versions de paquet, publier les coûts de téléchargement et les limites. Les sorties et poids LoRA vont en **artefacts GitHub Actions**, pas dans `main`.

## Suite possible
Si le pilote fonctionne, préparer un test distinct de **génération d'idées non fournies à l'entraînement** et de transfert inter-domaines, avec origine/pertinence évaluées indépendamment. La présente expérience ne justifie pas d'engager un coûteux entraînement Qwen 3B.
