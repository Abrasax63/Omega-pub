# KV-READER18-01 — comparaison de cache sur les vrais lecteurs scientifiques d'Omega
Date : 2026-11-21. **Préenregistrement avant exécution de ce protocole.**

## Objectif
Mesurer la réutilisation de préfixe dans `llama.cpp` sur les **six fiches scientifiques gelées** de Reader18 (PR #202) et évaluer la conservation des **sorties, sélections de lignes et gardes de provenance**. Ne pas modifier les codes Reader12/Reader14/Reader18, leurs documents ni leurs labels.

## Base immuable
- Branche créée depuis la tête Reader18 `a84d9d414ffa4f426c89405893c2e642334bc3d3`. PR empilée sur #202, `main` inchangée.
- Deux vrais modèles du pilote Reader18 : Qwen2.5-0.5B-Instruct GGUF Q4_K_M SHA256 `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db` et Qwen2.5-3B-Instruct GGUF Q4_K_M SHA256 `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`.
- `llama.cpp` `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`, CPU, `-t 4 -c 4096 --parallel 1`.
- `reader_bridge18/paired.py:prepare()` et `messages()` non modifiés, prompt rendu par le `/apply-template` natif du moteur vers `/completion` pour pouvoir faire varier **uniquement** `cache_prompt`; même modèle, mêmes tokens d'entrée, mêmes options de génération.
- Paramètres `n_predict=64`, `temperature=0`, `seed=42`, `id_slot=0`, `stream=false`. Règle d'arrêt explicite identique dans les deux conditions.
- Quatre blocs à serveur redémarré : OFF / ON / ON / OFF (ABBA), pour **chaque** modèle.
- Sept requêtes par bloc : S01, S01 (identique, répétée pour mesurer la résidence), S02, S03, S04, S05, S06. La réplication immédiate S01 est distincte des six problèmes uniques.
- Les six fiches et leurs 12 lignes « résultats » possèdent un oracle arithmétique indépendant, mais les étiquettes de rôle ont été construites par l'auteur de Reader18. Pas de holdout humain externe.

## Critères de mesure et décisions
- Réutilisation **démontrée sur ce moteur** seulement si ON comporte `cache_n > 0`, et `prompt_n` total inférieur à OFF pour les requêtes 2 à 7 de chaque bloc. Les premières requêtes ne comptent pas.
- Résultats bruts sans régularisation : texte et `timings.cache_n/prompt_n/prompt_ms`, durée HTTP, `predicted_n/predicted_ms`; si champ absent, marqueur `MEASUREMENT_UNAVAILABLE`.
- Conservation des sorties : les sept réponses appariées doivent être identiques, sinon lister chaque divergence textuelle, sans réparation.
- **Qualité** : réutiliser **à l'identique** `parse_selection()`, `source_selection()`, `metrics()` et l'oracle gelé de Reader18. Comparer précision, rappel, F1, refus de parse, abstentions, faux positifs, et compte de lignes valides. Ne pas déclarer conservation de qualité uniquement en cas d'abstentions partout.
- Aucune promotion de théorèmes, aucune règle Horn ni certificat ; aucune tolérance pour sources modifiées.
- Régression : un verdict admis/parse ou F1 moindre dans la condition ON entraîne verdict prudent `QUALITY_REGRESSION_OBSERVED`. Le gain mécanique ne prévaut pas sur la validité.
- S'il y a identité des réponses mais F1 nul dans les deux groupes, classer `PARITY_OF_WEAK_BASELINE`, pas « qualité préservée ».
- Absence de baisse du nombre de tokens réévalués -> `NO_REUSE_DEMONSTRATED`. Artefacts et messages d'erreur conservés, pas de faux zéro.

## Limites
Ce test reste sur seulement 6 documents **synthétiques** de Reader18, déjà vus dans les travaux. Ce n'est pas une validation sur textes scientifiques externes, ni une mesure de FLOPs ou d'énergie. L'utilisation du cache natif de `llama.cpp` n'est pas l'intégration du moteur MoE Colibrì ; c'est une adaptation expérimentale de l'idée de calcul réutilisable. Aucune API payante. Ne pas fusionner avant validation reproductible.

Référence : https://github.com/ggml-org/llama.cpp/blob/5a4afd80779ba51166b59986e61a0bfbb9e1a4c6/tools/server/README.md
