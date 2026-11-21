# KV-EXT-01 — préenregistrement du test complet sur sources externes

Date : 2026-11-21. Préengagement créé **avant** le code d'inférence et les nouveaux résultats.

## Objectif
Mesurer si `llama.cpp` réutilise effectivement le calcul de préfixe sur une petite chaîne Omega : **source externe vérifiée → extraction ou citation immuable → LLM local → parseur strict → garde scientifique sans promotion → rapport**. Comparer la qualité des sorties strictement appariées avec cache OFF et ON.

## Cohorte fixée
- 8 fichiers complets provenant de `marcusm117/ProofNet-Verified`, commit upstream `b7ca411a2abaa6caf3580192b30d865e5bd10bc4`, indices (1,2,3,6,10,22,40,80). Manifest et empreintes Git dans `09_INFRASTRUCTURE_AGENTIQUE/proofnet26/FROZEN_UPSTREAM.json` de la PR Omega #211.
- 12 extraits courts rédigés par des tiers (Math Stack Exchange et Wikipédia FR), figés dans `09_INFRASTRUCTURE_AGENTIQUE/external23/EXTERNAL_SOURCES.json` de la PR #208. **Ce sont des extraits, pas les documents complets**. La provenance par URL est conservée, l'exactitude actuelle de chaque citation en ligne n'est pas recontrôlée ici.
- 20 entrées de sources différentes ; rajouter une répétition exacte de la première source en deuxième position (21 appels par bloc) pour mesurer la résidence.
- Aucune sélection des documents ou prompts ajustée sur les résultats du modèle ; ces 20 entrées ont été utilisées dans d'anciens tests d'Omega, donc **pas un holdout inédit**.

## Moteur et ordre du comparatif
- Poids Qwen2.5-3B-Instruct Q4_K_M `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d` et `llama.cpp` commit `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6` déjà épinglés dans Reader18/KV-Reader18.
- Un seul CPU runner GitHub, 4 threads, contexte 4096, un seul slot, serveur local uniquement.
- Pour chaque source, messages chat inchangés entre conditions. Une consigne système commune demande de classer le *type de texte* parmi `THEOREM`, `OTHER`, `UNSURE`, sans prétendre juger sa vérité. Le texte de chaque source est fourni verbatim comme donnée non fiable.
- `/apply-template` natif puis `/completion`; `n_predict=12`, température 0, seed 42, streaming false, arrêt sur marqueurs du chat. Cache `cache_prompt=false/true` : **seul facteur expérimental**.
- Ordre **OFF / ON / ON / OFF** avec redémarrage du serveur et cache froid au début de chaque bloc. Pas de réparation des mauvaises réponses ni de relance adaptative.

## Garde scientifique/qualité
- `ProofNet26` revalide l'empreinte exacte de chaque fichier, extrait l'énoncé littéral et la référence Lean préexistante, et relance les deux formaliseurs conservateurs et leur contrôle de non-certification. Le texte Lean n'est jamais fourni au LLM classificateur.
- `EXT23` relit les citations gelées et appelle le vérificateur exact `SEM22` sur le texte original : si `UNSUPPORTED_SOURCE` ou `INDETERMINATE`, aucune assertion scientifique externe ne peut être admise.
- Le LLM n'a pas le droit de produire des preuves ou citations, seulement une étiquette de classification ; les sorties refusées restent des refus ; aucune promotion scientifique.
- Appariement exact des 21 textes, catégories, statuts, empreintes de prompt et provenance dans chaque paire OFF/ON.
- Mesurer **format reconnu**, abstentions `UNSURE`, divergence textuelle, erreurs de parsing, erreurs d'ancrage source et tout changement du contrôle scientifique. **Aucun gold sémantique indépendant des étiquettes** : l'égalité des sorties ne prouve ni la vérité ni la qualité réelle du classement.

## Coût et statuts
- `timings.cache_n`, `prompt_n`, `prompt_ms`, `predicted_ms`, latence HTTP ; coût total wall-clock **par bloc** en incluant source et validation des gardes. Exclure la première requête de chaque bloc des sommes de préremplissage. Enregistrer les tokens de génération séparément.
- Réutilisation vérifiée si >0 tokens cachés ON et réduction du `prompt_n` ON vs OFF. Sans champ : `MEASUREMENT_UNAVAILABLE`.
- Régression observée si une sortie/étiquette/état du parseur diffère ou si la garde échoue. Même si toutes les sorties sont identiques, **pas d'assertion de non-perte de compréhension scientifique** en absence de gold.
- Aucun calcul énergétique/joules, aucune estimation de FLOPs réelle ni coût facturé à une API distante.
- Aucune modification de `main`, aucune API payante, aucune formation de poids, aucun merge automatique. Télécharger le modèle GGUF open source peut coûter des minutes de CI.

## Falsification attendue
Un résultat négatif est possible : peu de préfixe partagé, coût de préparation des sources dominant, ou réponses divergentes. **Reporter tous les cas**, conserver les artefacts, y compris les échecs. Aucune généralisation au moteur Colibrì lui-même.

Références : [PR #211](https://github.com/Abrasax63/Omega-pub/pull/211), [PR #208](https://github.com/Abrasax63/Omega-pub/pull/208), [Documentation llama.cpp épinglée](https://github.com/ggml-org/llama.cpp/blob/5a4afd80779ba51166b59986e61a0bfbb9e1a4c6/tools/server/README.md).
