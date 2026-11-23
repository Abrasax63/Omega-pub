# OMEGA-SELF-TEACH-02 — préenregistrement AVANT nouveau modèle (23 novembre 2026)

## Origine et question
Successeur de [#242](https://github.com/Abrasax63/Omega-pub/pull/242).
Le premier run #45118652661 a produit 0/15 strict A et B, puis 5/15 A et B en lecture de format rétrospective ; aucune mémoire admise. Les anciens 15 cas cachés sont **consommés** et ne peuvent plus constituer un holdout.
Question : avec une lecture étroite préenregistrée des sauts de ligne échappés et deux tentatives supplémentaires d'auto-correction guidées par les seuls cas de développement, Omega peut-il construire une leçon vérifiée et améliorer son transfert vers **des familles nouvelles** ?

## Jeux gelés AVANT le code et l'inférence
- `TRAIN_FROZEN.json` : deux tâches pédagogiques nouvelles, quatre exemples publics et huit cas de développement par famille ; un oracle déterministe créé par le concepteur, **pas une découverte du modèle**.
- `EVAL_PUBLIC_FROZEN.json` : trois familles inédites de transformation de chaînes, avec deux exemples publics par tâche.
- `EVAL_SEALED_FROZEN.json` : dix-huit cas cachés, six par famille, visibles uniquement par le scoreur **après sauvegarde complète des générations**.
- Les trois fichiers sont gelés par SHA de blob Git. Pas de chevauchement d'identifiants ni de familles train/test. Ce jeu devient consommé après sa première notation.
- Le code du modèle, les contrôles et le protocole sont écrits **après** ce gel. Les données d'évaluation ne doivent jamais être importées dans le module de génération.

## Bras préspécifiés
- **A direct** : Qwen2.5-3B-Instruct-Q4_K_M local, 3 générations (660 tokens max chacune).
- **P témoin de consigne** : trois générations avec une consigne pédagogique neutre, sans leçon issue des exercices ; même plafond de génération.
- **B pratique + mémoire vérifiée** : trois générations avec une note synthétisée par le modèle à partir de sa pratique, admise *uniquement* si la version corrigée passe 8/8 cas de développement et dépasse le score de départ. Sinon B reçoit la même consigne neutre que P et l'absence de mémoire est explicitement conservée.
- **C LoRA** : désactivé (`TRAINING_NOT_AUTHORIZED`) ; aucun gradient, aucun réentraînement, aucun changement de `main`.

Apprentissage en contexte : deux essais initiaux de pratique, choix automatique du score le plus faible (départage déterministe), au maximum deux corrections sur les **seuls échecs de développement** et un unique appel de résumé si vérification réussie. Chaque proposition passe dans le même sandbox AST existant. Aucune solution de référence d'entraînement n'est montrée au modèle ; il voit ses erreurs de tests seulement.

## Lecture / vérification
- Enregistrer le texte brut, l'état du parseur original et celui du **normaliseur strict de format** (récupération `\\n` seulement hors littéraux Python, puis sandbox AST). Ce normaliseur ne doit pas réparer d'algorithme ni inventer de code.
- Appliquer **exactement le même normaliseur** aux trois bras, sans seconde génération ni intervention manuelle.
- Mesurer exactitude de tous les cas cachés (0–18), problèmes intégralement exacts (0–3), nombre de solutions sûres, erreurs fonctionnelles silencieuses, abstentions, appels de modèle, tokens et temps.
- Analyser deux effets séparés : B-A et B-P, les régressions par problème et le taux de mémoire admise. Le coût d'acquisition pédagogique doit être ajouté au coût B. La longueur des prompts reste différente : pas de causalité attribuée sans vérification supplémentaire.

## Décision falsifiable et statut
- Gain exploratoire attribuable à l'usage de la leçon **seulement si** une leçon est admise, B > A **et** B > P sur le nombre de tests exacts et aucune tâche entièrement réussie par A ou P ne régresse dans B.
- Sinon : aucun gain pédagogique autonome démontré, y compris si les jobs CI sont verts ou si A/P/B réussissent des programmes par eux-mêmes.
- Aucune généralisation scientifique, compréhension mathématique, autonomie générale ni capacité de gradient n'est certifiée ici.
- Tests de non-régression avant réel modèle : validation SHA, frontières train/test, contrôles positifs et négatifs, code dangereux interdit, fuite de gold, normaliseur, échec de mémorisation, altération des sorties, C désactivé.
- GitHub Actions CPU sans clés ni API payantes ; un seul premier run sur une PR DRAFT, `main` intact. Ne jamais relancer un test consommé en le présentant comme indépendant.
