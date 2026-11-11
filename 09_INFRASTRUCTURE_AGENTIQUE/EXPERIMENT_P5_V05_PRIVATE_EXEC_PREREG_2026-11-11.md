# P5 v0.5 — protocole d'exécution privée pré-enregistré avant toute génération

Date : **11 novembre 2026**. Branche `experiment/p5-v05-private-runner-2026-11-11` basée sur la PR #46. **Statut : PRIVATE_CANDIDATE, NON AVEUGLE CERTIFIÉ, MODÈLE NON EXÉCUTÉ.**

## Population et confidentialité

- 16 problèmes candidats nouvellement générés (4 formalisation finie, 4 congruences exactes, 4 décisions documentaires synthétiques, 4 analyses de taux stratifiés), **16 × A/B/C × 2 répétitions = 96 générations prévues**.
- Prompts et corrigés **séparés**, conservés dans la **Bibliothèque privée de l'utilisateur** : `/Omega-Private/P5V05-Candidate-2026-11-11/inputs_private.json`, `answers_private.json`. Le dépôt GitHub public ne doit recevoir **aucune copie**, aucun corrigé, aucune transcription des questions, aucune graine ni identifiant de réponse.
- Engagement des fichiers avant modèle : `prompt_only_sha256=10a922b187ecf5752c13a4d2da1e690b1606e9da525b78051e56ab3b1d4099d9` ; `private_gold_sha256_commitment=ecfa7e4e4544840219379b507f496d65625ec1f0575352bda1b66a87f605417b`. Manifeste public `evaluation/p5_v05_candidate_public_manifest.json`, commit **`ce9a5818928e05d8ec0d1330d5f27a00b732149d`**.
- **Attention épistémique :** les 16 cas et leurs corrigés ont été **produits par le concepteur de ce banc**, pas par deux examinateurs externes indépendants. L'empreinte prouve la stabilité des octets, **pas** l'indépendance du corrigé ni la validité scientifique de la cohorte. Aucun résultat sur ces cas ne peut être présenté comme « vrai holdout indépendant ». Une révision extérieure doit précéder toute revendication.
- Le protocole est reproductible sur les cas gelés ; il n'est pas représentatif de la recherche ouverte, de la consultation d'Internet, des preuves authentifiées ni des systèmes multi-agents complets.

## Hypothèse causale et comparateurs

A : même modèle, réponse directe. B : même modèle, cinq perspectives fixes et prédéterminées. C : **même modèle**, sélection des perspectives par le code existant `planner.plan_mission`, appelé uniquement avec `question` et `mission_type`. Le reste du prompt est rigoureusement identique octet pour octet dans chaque triplet A/B/C.

Primaire : différence appariée **C−B** en exactitude et faux énoncés assurés, ainsi qu'en tokens et coût réel fournisseur. Secondaires C−A et B−A. Les rôles sont des perspectives, pas des sous-agents. Hypothèse nulle : pas de progrès.

## Préflight obligatoire et budget

1. Vérifier sur les fichiers **privés** le hash SHA-256 des **octets sur disque** contre le manifeste public. Le runner ne charge jamais le corrigé, ni pour les prompts ni pour le choix des rôles. Rejeter la moindre clé contenant la réponse, la vérité, une étiquette d'attaque, ou une source non fournie.
2. Préparer **96 requêtes** en randomisant de façon cryptographiquement reproductible (graine privée) l'ordre des bras pour chaque cas et répétition ; ne pas révéler cette correspondance au correcteur. Utiliser un seul snapshot explicite de modèle, des appels stateless (`store=False`, aucune mémoire de conversation et aucune réutilisation d'une réponse comme contexte), `tools=[]`, zéro retry silencieux et même raisonnement paramétré si disponible.
3. Pour chaque requête, `responses.input_tokens.count` compte **réellement** les tokens d'entrée avec **exactement les mêmes champs** que la génération. Une seule limite de tokens de sortie commune et un seul plafond total par bras doivent être respectés. Ne pas prétendre que des chiffres issus de tests mock sont des tokens réels.
4. **Aucune génération implicite** : `--execute` explicite, `--max-generation-calls` explicite égal au nombre requis, et identifiant exact du modèle obligatoire. Une clé API fournie par une configuration externe/système est nécessaire ; elle ne sera jamais enregistrée dans GitHub ni affichée.
5. Refuser toute campagne dont le plafond n'est pas disponible ou ne peut être contrôlé **avant** génération. Préflight seul par défaut. Réponse fournisseur incomplète, tokens absents, dépassement de budget, erreur de transport : campagne **INCOMPLETE**, jamais réussite.
6. Journaliser SHA du prompt, identifiant opaque, modèle effectivement retourné, nombre d'appels, tokens d'entrée/sortie réels, durée mesurée, coûts en devise **seulement si barème contractuel publié/gelé** (sinon `null`), sortie brute et erreurs. Ne pas stocker de résultat dans GitHub public.
7. Les sorties des trois bras ne sont pas autorisées à se voir mutuellement. Les deux répétitions doivent être isolées.

## Critères d'arrêt et évaluation

- Sans **accès API autorisé**, aucun appel n'est lancé. Une offre ChatGPT n'est pas assimilée à un crédit API.
- Sans **deux évaluateurs réellement indépendants** et un audit séparé du corrigé, produire **uniquement un registre de générations** avec statut `RUN_UNGRADED`, jamais un score de victoire Omega. Les scores calculables automatiquement sur les quatre types de cas peuvent servir de **contrôles exploratoires internes**, mais ne sont pas un double aveugle.
- Aucun usage des cas ou corrigés privés en tant qu'exemples de prompt ; aucun post-tuning sur les mêmes cas. Publier uniquement des agrégats approuvés et accompagnés des limites.
- **N'utiliser aucun secret API de GitHub Actions** sur des PR publiques par défaut. L'exécution réelle doit être isolée sur le client autorisé, avec un budget de dépenses confirmé.
- Première étape : tests **mocks** (0 génération fournisseur) pour sécurité du runner, hachages, refus des fuites, parité des entrées, tirage de l'ordre, temps et tokens. Tests mocks ne sont pas un résultat expérimental.

## Statuts stricts

- `PREFLIGHT_ONLY` : préparation vérifiée, 0 génération.
- `RUN_UNGRADED` : 96 générations réelles isolées, données complètes, aucune notation indépendamment vérifiée.
- `PILOT_GRADED_INTERNAL` : évaluation automatisée ou par un seul correcteur ; pas de revendication indépendante.
- `P5_BLIND_EVALUATED` : seulement après deux correcteurs réellement indépendants et vérification des engagements, des conditions d'aveuglement et des budgets.
- `INCOMPLETE` : toute défaillance ou perte d'informations interrompt la validité.

La réussite de cette CI ne signifie pas que le modèle a été appelé. **main, CORE, SQLite, PR #44 et #45 inchangés.**
