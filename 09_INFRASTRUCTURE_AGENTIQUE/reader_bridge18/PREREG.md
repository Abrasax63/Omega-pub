# Reader18 — ablation appariée Qwen2.5 Instruct 0,5B vs 3B (Q4_K_M)

**Préenregistrement avant code, fiches et inférence. Date : 2026-11-19.**

## Question unique
À interface, jeu, prompt, moteur et quantification comparables, Qwen2.5-3B-Instruct retient-il davantage de lignes de résultats mathématiques **dans six micro-fiches synthétiques inédites pour Reader14/15** que Qwen2.5-0.5B-Instruct et que le témoin mécanique `first 3` ?

## Contrôles et ressources fixés
- Branche expérimentale empilée sur Reader15 PR #184, sans changement de `main`, sans fusion.
- Réutiliser **sans retouche** les fonctions `build_prompt`, `parse_selection`, `proposal_from_lines`, `candidates_from_baseline` de Reader14 et le `gate` de Reader12 ; **mêmes chaînes de messages system/user** que Reader15.
- Deux modèles de la même famille Qwen2.5 **Instruct (pas Coder)**, tous deux GGUF officiels `Q4_K_M`, chargés à tour de rôle dans un **même exécutable llama.cpp** SHA `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`.
- Modèle petit `Qwen/Qwen2.5-0.5B-Instruct-GGUF/qwen2.5-0.5b-instruct-q4_k_m.gguf`, SHA256 `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db`.
- Modèle grand `Qwen/Qwen2.5-3B-Instruct-GGUF/qwen2.5-3b-instruct-q4_k_m.gguf`, SHA256 `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`.
- Même prompt, mêmes 5 candidates par fiche, décodage glouton (température 0), même plafond 64 nouveaux tokens, même serveur CPU (4 threads, contexte 4096), un appel par modèle par fiche, **aucun essai de rattrapage ni retouche**.
- Trois témoins sans LLM : `select all` pour la couverture (5 candidates), `first 3` (3 candidates) et `NONE` (abstention).
- Six fiches créées après le préenregistrement à partir de spécifications numériques figées : modulo m avec exactement 2 énoncés de résultat (somme, produit) vérifiables par une seconde implémentation d'arithmétique entière, 3 distracteurs (hypothèse, définition, question). Ordres des lignes contrebalancés ; toutes les candidates contiennent `=` sous `## Énoncé` pour Reader13/14.
- Les fiches, leurs blobs Git immuables et les indices de résultat sont gelés dans un manifest **avant toute réponse modèle**. Aucun label ne doit dépendre des sorties.
- IMPORTANT : l'oracle numérique est indépendant des **sorties des modèles** mais les rôles/étiquettes sont construits par l'auteur du pilote. **Pas d'annotation humaine externe**. Le benchmark est synthétique, la généralisation aux documents réels reste indéterminée.

## Mesures
- Par fiche × modèle : réponse brute, nombre de jetons entrée/sortie (si fourni), secondes mesurées, validité du parsing, IDs rejetés, abstentions `NONE`, lignes acceptées, lignes gold retenues, faux positifs, précision si prédictions non vides, rappel/F1, coût de préparation/chargement distingué de l'inférence.
- Scores exacts par présence dans l'oracle gelé uniquement ; `precision=null` si abstention ; compter `0` correct sélectionné. Calculer totals micro et résultats par fiche, comparaison à `first 3`. Si 0 gold visible ou candidat, le noter, pas d'imputation.
- Critère primaire prospectif : sur les 6 fiches, F1 micro 3B > F1 micro 0,5B **ET** F1 micro 3B > F1 micro `first 3`. Sinon, pas de gain local démontré.
- Sûreté : parseur strict fail-closed, hashes et sources vérifiés, aucune citation créée par le modèle, aucune certification/règle Horn/promotion, 0 API payante. Tests négatifs pour doublon, `999`, prose/Markdown, changement de source, modèle inaccessible et absence de promotion.
- Un succès local sur six micro-fiches faciles ne prouve ni compréhension mathématique générale, ni aptitude frontière, ni effet causal isolé de la taille (les deux entraînements ne sont pas identiques).
- Si téléchargement, hash, build ou serveur échoue : `INFRA_FAILURE`, **aucune** conclusion de qualité. Rapports bruts archivés même lors d'échec.

## Décision
Ne pas réajuster les six fiches ou le prompt après résultats. Ne lancer aucune API payante, ne fusionner, ne toucher ni `main` ni les PR #183/#184. Toute certification scientifique requiert une cohorte externe et des annotations indépendantes.
