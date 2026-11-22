# OMEGA-SEMANTIC-TRANSFER-04

**Objectif** : éprouver la limite du progrès observé dans [SFT01 (PR #236)](https://github.com/Abrasax63/Omega-pub/pull/236) : un LoRA qui résout 11/12 réparations de *syntaxe* a-t-il appris à corriger aussi des **erreurs de logique dans des programmes déjà compilables** ?

Ce pilote **ne réentraîne pas le modèle**. Il réutilise exactement l'adaptateur SmolLM2-135M du [run #45073297901](https://github.com/Abrasax63/Omega-pub/actions/runs/45073297901), enregistré dans l'artefact GitHub 14774003555. Les poids Qwen3B d'Omega ne sont pas modifiés.

Le [préenregistrement](PREREG.md) et le jeu [HOLDOUT_SEMANTIC_FROZEN.json](HOLDOUT_SEMANTIC_FROZEN.json) ont été créés **avant tout nouvel appel au modèle**, avec empreinte de Git blob \`00c48008244f787cfcd38fad278a4ed57452ebe5\`.

### Examen

- 12 programmes, 6 nouvelles fonctions, 2 erreurs logiques par fonction, toutes syntaxiquement valides.
- Deux observations visibles par fonction défectueuse, puis cinq tests cachés pour l'évaluation.
- Trois approches : SmolLM2 original, SmolLM2 + LoRA SFT01, correcteur classique à mutations locales déterministes.
- Deux mesures du texte d'un modèle : **strict** (code seul) et **permissif préenregistré** (une fonction sûre extractible d'un texte explicatif ou bloc Markdown). Aucun deuxième appel au modèle.
- Les programmes sont exécutés par le sandbox Python à AST limité du laboratoire existant. Les sorties des tests cachés restent dans le rapport, **jamais utilisées pour choisir une correction**.

### Comment interpréter

Une victoire du LoRA au-delà de la syntaxe serait un signal de transfert sémantique exploratoire. Une victoire du correcteur symbolique montrerait que des erreurs locales peuvent être mieux réparées sans entraînement lourd, mais ce correcteur est **volontairement limité à des mutations prédéfinies**. Un score nul ou une régression restent des résultats valides.

Les nouveaux 12 programmes deviennent **consommés après ce run** et ne devront pas être représentés comme un holdout nouveau lors d'un entraînement ultérieur. Ce pilote ne met pas en production de compétence, ne crée pas de tâche horaire et ne touche pas à \`main\`.

### Fichiers

- \`core.py\` : vérification d'empreinte, sélection symbolique à partir des **seuls exemples publics**, parseurs strict/permissif, score aveugle.
- \`model_run.py\` : recharge l'adaptateur enregistré, exécute une seule génération par tâche et modèle, puis seulement après calcule les scores.
- \`test_semantic04.py\` : contre-épreuves sur source correcte, programme défectueux, fuite de holdout, score, import de l'ancien adaptateur.
- \`.github/workflows/omega-semantic-transfer04.yml\` : CPU Github Actions sans API payante, lecture seule, pas de nouveau LoRA.

**Statut épistémique avant le run : PRÉENREGISTRÉ / PAS DE NOUVELLE GÉNÉRALISATION DÉMONTRÉE.**
