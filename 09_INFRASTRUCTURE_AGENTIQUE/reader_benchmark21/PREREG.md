# BENCH21 — GBNF imposée dans llama.cpp, comparaison appariée sur nouvelles fiches

**Préenregistrement écrit avant les nouveaux cas, le code et toute inférence. Date : 2026-11-19.**

## Pourquoi
BENCH20 PR #204 a montré que donner les indices de choix 1–5 et les résoudre strictement vers la ligne Git améliorait le taux de sortie conforme et certains scores. Reste à savoir si demander un format suffit ou s'il vaut mieux **forcer le format dès le décodage**. NE PAS modifier ni rescorrer BENCH19/20.

## Cohorte gelée avant réponses
- 20 nouvelles fonctions finies de Z/mZ dans Z/mZ (10 affines, 10 quadratiques), nouvelles combinaisons de paramètres, des énoncés de la même famille que BENCH20 mais jamais utilisés pour ajuster les résultats.
- Jeu de 20 fichiers Markdown, Git blobs exacts, paramètres et ordre de cinq assertions, oracle exhaustif et scores mécaniques, tous gelés avant la première inférence. 5 propositions par cas, affichées sous ID 1–5 ; citations véritables 9–13.
- Aucun étiquetage sémantique externalisé : la vérité numérique est indépendante des réponses modèle mais reste un benchmark *synthétique*.

## Deux bras appariés, *sans changer de prompt*
- **FREE** : même prompt d'identifiants 1–5 de BENCH20, sorties non contraintes et parseur strict, aucune réparation.
- **GBNF** : exactement les mêmes messages, candidats, température zéro, modèle et limite de 64 tokens, mais envoi d'un champ HTTP `grammar` à llama.cpp. La grammaire autorise précisément `NONE` ou une, deux ou trois étiquettes distinctes parmi `1,2,3,4,5`, séparées par virgules. Elle interdit doublons, prose, Markdown et choix non offerts au niveau du décodage.
- Toutes les **86** chaînes admissibles sont énumérées de façon déterministe : 1 `NONE` + 5 choix d'une étiquette + 20 choix ordonnés de deux + 60 choix ordonnés de trois.
- Vérification préalable indépendante de la grammaire : sur chaque modèle, une requête témoin imposant uniquement `NONE` doit retourner `NONE`. En cas d'échec du témoin, **INFRA_FAILURE** et aucune conclusion.
- Rejouer **exactement les 20 mêmes cas pour les deux bras au sein de chaque modèle** ; mêmes données, aucun gold transmis, aucun retry, aucune modification de réponses. 2 modèles × 2 bras × 20 = **80 réponses expérimentales** (+ 2 requêtes de validation de grammaire).
- Modèles identiques à BENCH20 : Qwen2.5-0.5B-Instruct et Qwen2.5-3B-Instruct GGUF Q4_K_M, SHA256 déjà gelés. Même exécutable llama.cpp `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`, 4 threads CPU, contexte 4096. Pas d'API payante.

## Métriques et décision
- Deux critères **distincts** et préfixés : (1) réduction stricte des sorties rejetées par grammaire ; (2) différence F1 micro de sélection de propositions mathématiquement vraies. Ne jamais confondre conformité et justesse.
- Précision, rappel, FP, FN, abstentions, scores par famille, tokens, secondes, statut de terminaison et réponses brutes pour chaque bras et modèle.
- Le témoin `first3` et `NONE` restent les mêmes dans les deux bras ; `all5` couverture seulement. 40 paires d'observations (20 par modèle), toutes nécessaires à un bilan complet ; toute défaillance de téléchargement, de hash, d'oracle, de grammaire ou de modèle invalide la comparaison et reste archivée comme telle.
- GBNF doit forcer 0 sorties rejetées dans les 40 requêtes contraintes. C'est une **attente de conformité technique**, pas un succès scientifique.
- **Gain de qualité** local démontré seulement si le score F1 du bras GBNF > FREE pour le même modèle sur le même nouveau corpus. L'hypothèse peut être réfutée ; aucune modification a posteriori du prompt, de l'oracle ou des modèles.
- Ne pas comparer le score brut de BENCH21 avec BENCH20 comme si c'était une expérience causale : les jeux diffèrent. Les comparaisons causales d'interface sont **intra-cas** BENCH21 uniquement.
- Chaque ID accepté est résolu 1–5→ligne réelle 9–13, puis **cité depuis le blob Git** et soumis au gate Reader12 inchangé ; toute réponse hors-grille est refusée. Aucun apprentissage, promotion, règle Horn ou certification.

## Garde-fous
- La grammaire restreint la **forme**, pas la vérité. Effet sur une tâche fermée à cinq choix ; aucune preuve de capacité générale, d'AGI, de raisonnement nouveau ni de transfert.
- Une éventuelle inférence qui s'interrompt sans sortie complète doit être signalée. La traçabilité exige le raw complet, le modèle et le SHA du corpus.
- PR en brouillon, branchée sur BENCH20 sans toucher à `main` ni aux PR historiques, aucune fusion automatique.
