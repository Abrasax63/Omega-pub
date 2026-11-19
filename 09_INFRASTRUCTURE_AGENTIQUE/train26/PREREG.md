# Omega TRAIN26 — préenregistrement avant données, code, résultats (2026-11-19)

**Hypothèse réfutable** : après TRAIN25 (`0/24` sorties de formalisation utiles malgré un LoRA réellement modifié), un entraînement supervisé complet sur **320 exemples structurés de raisonnement, critique et correction** peut augmenter la fidélité de la traduction entre intuition mathématique et représentation vérifiable sur **48 demandes non utilisées pour l'entraînement**.

**Ce n'est pas** une preuve de découverte scientifique ni de créativité autonome : toutes les familles et transformations jugées correctes sont préparées par le concepteur; le modèle reste `HuggingFaceTB/SmolLM2-135M-Instruct` utilisé dans TRAIN25, **pas Qwen 3B**. Cet entraînement comprend les trois domaines ; un résultat positif sur des paraphrases réservées n'est donc **pas un transfert à une théorie jamais étudiée**.

## Domaines et vérités mathématiques
- `xor` : reachability de commutateurs réutilisables `s -> s xor move`. Transformation : `rank(moves) == rank(moves + [start ^ target])`, rang sur GF(2). Témoin exact BFS indépendant et pivot GF2.
- `paren` : chaînes de parenthèses équilibrées. Transformation : `sum_balance(s) == 0 and min_prefix_balance(s) >= 0`. Témoin exact par pile indépendant.
- `observability` : états finis déterministes, même suite d'observations sur h instants. Transformation : `partition_code(T, pi, h, x) == partition_code(T, pi, h, y)`. Témoin exact par comparaison directe des trajectoires, indépendamment du raffinement de partitions.
- `unsupported` : questions non suffisamment spécifiées et **quatrième domaine non entraîné**, exigeant `ABSTAIN`, sans prétendre apprendre un solveur universel.

## Les quatre opérations entraînées
1. `FORMALIZE` : à partir d'une **idée verbale** et de ses invariants, fournir une expression exacte au format `EXPR: ...`.
2. `REPAIR` : rejeter implicitement une transformation qui perd l'information, et proposer l'expression exacte préenseignée ; documenter la classe de faute dans la source (le modèle voit l'hypothèse contestée, pas le corrigé).
3. `CRITIQUE` : décider `ACCEPT` ou `REJECT` pour une transformation proposée et ses hypothèses, incluant des contrôles invalides.
4. `ABSTAIN` : refuser une formalisation non prise en charge.

**Répartition gelée avant génération** : 3 domaines × (40 FORMALIZE + 28 REPAIR + 28 CRITIQUE, dont 14 valides / 14 invalides) + 32 ABSTAIN = **320 exemples**. Exemples écrits avec paraphrases et catégories de faute identifiées ; les cibles sont des vérités contrôlées par oracle et non des idées nouvellement découvertes. Les préfixes/formats de sortie sont strictement `EXPR: ...`, `ACCEPT`, `REJECT`, `ABSTAIN`, une seule ligne.

**Jeu réservé** : 3 domaines × (4 FORMALIZE + 4 REPAIR + 4 CRITIQUE [2 valides/2 invalides]) + 12 hors domaine = **48 requêtes**. Énoncés exacts et catégories sont gelés dans le dépôt avant code, avec gold séparé. Les seules familles sont partagées avec l'entraînement ; l'évaluation est **paraphrase & combinaison**, pas découverte d'une nouvelle famille. Un contrôle d'exclusion lexicale exact et un contrôle de duplication de l'ensemble des prompts sont obligatoires.

**Vérification de sémantique** : geler 32 instances finies distinctes par famille, mélange de cas vrais/faux. Pour les réponses `EXPR` (FORMALIZE/REPAIR), un interpréteur AST fermé (pas de `eval` / code généré) évalue l'expression sur les **32** instances et la compare à l'oracle indépendant. Pour CRITIQUE, les deux candidats connus valides/invalides des tests ont un statut calculé ou contredit par les témoins finis ; `ACCEPT` ou `REJECT` ne vaut pas certification au-delà de cette grammaire. Pour les 12 hors domaine, seul `ABSTAIN` est sûr. Aucun score n'est attribué à du bavardage explicatif hors format.

## Entraînement et comparaison gelés
- Base : `SmolLM2-135M-Instruct`, révision déjà vérifiée `ee72e5415c002e8fc0566a191a07c0b2b708875a` (Apache-2.0). Torch CPU, Transformers 4.49.0, PEFT 0.15.2, LoRA `r=8,alpha=16,dropout=0` sur `q_proj,v_proj`, AdamW `lr=0.0005`, batch 1, `seed=20261119`, max 384 tokens, 2 époques complètes **640 mises à jour**, pas d'arrêt précoce ni réentraînement sur holdout. En cas de panne matérielle, reporter `INDETERMINATE_INFRA` ; pas de nouvelle configuration silencieuse.
- Comparaison **AVANT vs APRÈS**, base inchangée, même modèle initial, tokenizer, texte système et décodeur greedy (`max_new_tokens=96`), prompts et métriques.
- **Témoin D** : solveurs classiques exacts sur les mêmes instances. D doit être perfectible ni par le LoRA ni par un mécanisme de copie sur ce banc : les scores du modèle sont des compétences de *formalisation/rejet*, pas une supériorité de calcul.
- Métriques primaires (unité=une requête réservée, n=48) : (a) taux de réponses exactes de format, (b) nombre de formalisations mathématiquement fidèles pour FORMALIZE/REPAIR (32 par domaine), (c) acceptations/rejets justifiés, (d) abstentions correctes, (e) **erreurs silencieuses** (formule fausse acceptée ou candidate invalide acceptée / affirmation hors domaine). Les erreurs doivent être conservées avec premier contre-exemple.
- Gain strict uniquement si `score_sémantique_après > score_sémantique_avant` ET `erreurs_silencieuses_après <= avant`, et sans fuites exactes d'entrée ; sinon `TRAINED_NO_EVIDENCE_OF_GAIN`. Une bonne imitation de format sans correction mathématique ne remplit pas le critère.
- Le modèle candidat et la référence D ne sont **pas au même coût** : mesurer temps/tokens mais ne pas annoncer un avantage à budget égal. 48 cas et un seul run ne permettent pas une estimation robuste de généralisation.

## Séparation des preuves
1. Commits : d'abord ce préenregistrement, puis `TRAIN_FROZEN.json`, `HOLDOUT_PROMPTS_FROZEN.json`, `HOLDOUT_GOLD_EVAL_ONLY.json`, `ORACLE_CASES_FROZEN.json` ; ensuite les sources d'entraînement/évaluation.
2. Le job de formation charge **uniquement** le train, et ignore même la présence du holdout. L'évaluation se déroule en job séparé, et n'est appelée qu'après sauvegarde de l'adaptateur. Le contenu est public dans le dépôt : c'est une séparation de processus, pas une garantie cryptographique de secret.
3. Tests unitaires de mise en danger : AST dangereux, faux raisonnement plausible, cas limites, erreurs d'échantillonnage, observation pi hors alphabet, fausse certification. Échec du test = CI rouge. Adapter les **outils** à une erreur technique avec erratum documenté, jamais les **données** ou les objectifs après lecture des sorties de test.
4. Conserver perte/pas, paramètres et norme L2 de changement, SHA du modèle/adaptateur, réponses brutes individuelles, classement avant/après, témoins exacts et cas sans interprétation. `main` inchangée, zéro API payante, aucune fusion, aucun poids auto-promu, aucun cycle autonome affecté.

**Condition d'arrêt :** publier les résultats, y compris négatifs. **Prochaine étude distincte**, non autorisée par ce test à elle seule : recueillir des propositions nouvelles générées par le modèle, en garder les seules transformations vérifiées, puis étudier si un apprentissage par récompense exact peut améliorer le taux de découvertes hors familles d'entraînement.
