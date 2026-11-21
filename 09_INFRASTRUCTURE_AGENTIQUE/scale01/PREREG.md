# SCALE-01 — préenregistrement de montée en charge Omega (2026-11-21)

**État de gel : avant le lancement des nouvelles inférences et benchmarks.** Base : PR #220 (Qwen local + Reader18 gelé). Les autres résultats (#221 cache sur sources externes, #222 cache de recollement à témoins) sont des travaux antérieurs, pas des données inédites.

## Question
Peut-on accroître le **volume de requêtes scientifiques et le nombre d'états finis manipulés**, sans dégrader les sorties contrôlables, dans un budget CPU/RAM donné ? Quelle est la mémoire réellement requise pour les modèles locaux 0,5B et 3B ? La piste ne prouve **pas** que le nombre de paramètres entraînés des modèles augmente.

## Axe A : calcul exact sur recollements et observabilité (pas de LLM)
- Réutiliser sans altération le composant `gluing_cache01/witness_cache.py` de la PR #222 comme référence, épinglé au commit `de3bec0329e2a9a82b3ec7625a0b20c5b9b9b5e2`.
- Ajouter un **routage adaptatif** : première occurrence d'un système `(T, π)` traitée sans cache, mémoisation dès la deuxième demande concernant ce système, capacité de suivi bornée à 32 systèmes, cache limité à 2048 préfixes. Retour au mode exact sans cache en cas d'incompatibilité de capacité.
- Contrôles complets sur mots fantômes `110`, `0001`, collisions macro (`Q` identique mais `W₃` différents), changement de `T` ou `π`, absence de répétition.
- Séries déterministes à **n=8,32,128,512 états** ; longueur de mot 12, 24 requêtes par système ; 2 profils : répétition forte (même `T,π`) et renouvellement (nouveaux systèmes à chaque requête). Comparer baseline, cache permanent, cache adaptatif : mêmes décisions ET témoins, étapes, visites de couples, temps et pic d'allocations Python `tracemalloc`. Identités exactes exigées.
- Ne pas extrapoler de ce benchmark artificiel à la charge mathématique réelle d'Omega. La réduction de travail ne signifie pas réduction en joules.

## Axe B : modèle local et volume de documents (vraie inférence)
- Reprendre **à l'identique** les six documents gelés Reader18 et les fonctions `paired.prepare()`, `paired.messages()`, `paired.one_case()` ; six cas synthétiques avec labels construits par auteur (pas de holdout humain externe).
- Simuler le **volume de documents traités** comme un flux croissant de requêtes `6,12,24` (répétitions ordonnées de ces six documents). La limite de contexte n'est *pas* augmentée : chaque requête reste indépendante.
- Pour chaque modèle, deux conditions avec serveur fraîchement redémarré : cache OFF / cache ON. Même ordre des 42 requêtes, rendu chat par `/apply-template`, température 0, `n_predict=64`, seed 42, `--parallel 1`, `-c 4096`, 4 threads CPU. Seule variable : `cache_prompt`.
- Les modèles et moteur **déjà identifiés** dans Reader18 :
  - Qwen2.5-0.5B-Instruct Q4_K_M (SHA256 `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db`).
  - Qwen2.5-3B-Instruct Q4_K_M (SHA256 `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`).
  - llama.cpp `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`.
- Relever `timings.prompt_n`, `cache_n`, `prompt_ms`, `predicted_n`, `predicted_ms`, temps HTTP par palier (6/12/24), ainsi que la taille réelle du fichier GGUF et le **pic VmHWM du processus llama-server** Linux; observer le temps de démarrage. Aucune estimation de joules.
- Qualité : mêmes réponses textuelles, sélections, statuts, refus de parse et F1 de Reader18 OFF/ON à chaque palier ; ne pas masquer les erreurs sous une moyenne. Un désaccord bloque l'affirmation de parité; un accord sur un faible F1 n'est pas une preuve de haute qualité.
- **Pas de téléchargement 7B ou 14B** à ce stade : un simple coût théorique de poids ne dit pas la RAM réelle, encore moins le gain en qualité. Limiter l'expérience aux poids quantifiés validés préalablement, sans modèles supplémentaires volumineux.

## Axe C : décision d'intégration
- Fournir des artefacts JSON inspectables et un tableau global : capacité de calcul exact avec/ sans cache, coûts du cache sur charges non répétées, coûts d'inférence, pic mémoire réel, scores / divergences.
- Introduire un réglage `off/adaptive/on` **uniquement sur les calculs exacts**, et laisser le cache LLM **off par défaut** parce que la PR #221 a observé 2 divergences de classification appariées sur sources externes.
- Aucune écriture sur `main`, aucun apprentissage des poids, aucune API payante, aucune certification automatique de théorème.
- Si un modèle ne rentre pas dans le budget RAM, noter `RESOURCE_LIMIT` et ne pas présenter la limitation comme échec scientifique du cache. Si réponse ou timing manque, noter `MEASUREMENT_UNAVAILABLE`.

## Critères
- **Réutilisation exacte** : parité des témoins et première obstruction sur toutes les charges.
- **Gain de ressources** : économiser des visites d'états **ET** ne pas consommer plus de RAM que la limite opérationnelle ; sinon aucun gain global.
- **Parité modèle** : si une sortie diffère, conclusion `DIVERGENCE_OBSERVED`. Le bon choix d'activation dépend de la tâche et du contrôleur scientifique.
- **Plus de paramètres** : seulement deux tailles 0,5B et 3B évaluées; aucune conclusion sur la possibilité de faire tenir 7B/14B.

Cet essai prolonge les résultats publics vérifiés dans [#220](https://github.com/Abrasax63/Omega-pub/pull/220), [#221](https://github.com/Abrasax63/Omega-pub/pull/221), [#222](https://github.com/Abrasax63/Omega-pub/pull/222).
