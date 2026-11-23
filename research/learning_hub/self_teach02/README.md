# OMEGA-SELF-TEACH-02 — apprentissage autonome, vrai témoin et nouvelle cohorte

**Date : 23 novembre 2026. Expérience isolée en PR DRAFT, sans modification de `main`.**

## Éléments repris sans redondance
- Moteur local Qwen2.5-3B + sandbox AST borné de #232.
- Normaliseur de transport `\\n` de #242, testé sur des sorties réelles ; aucune correction sémantique n'est introduite.
- Politique de meilleure version du cursus #234 et verrou de préparation LoRA #235.
- Les résultats et données de SELF-TEACH-01 restent inchangés et **consommés** : original 0/15 A = B, diagnostic rétrospectif 5/15 A = B.

## Expérience réellement nouvelle
Le `PREREG.md` et les trois jeux de données gelés ont été créés avant le moteur. Les vérifications de SHA des blobs empêchent une modification silencieuse. Deux familles de pratique, trois familles de test inédites et **18 nouveaux cas cachés**.

A : trois réponses directes. P : trois réponses avec un conseil neutre qui contrôle approximativement l'ajout d'une consigne. B : trois réponses avec une leçon issue du modèle **uniquement si** la correction du problème choisi automatiquement est sûre, réussit les huit cas de développement et améliore le résultat initial ; sinon même conseil neutre que P. C : LoRA bloqué, 0 mise à jour de poids. A, P, B utilisent exactement le même plafond d'inférence par problème et la même validation du format.

Le choix pédagogique observe les scores de départ des deux familles, prend la plus faible, applique deux réparations au maximum sans montrer de solution de référence ni aucun cas caché. Le test aveugle s'ouvre dans `score.py` seulement après sauvegarde des 9 réponses A/P/B et des tentatives de pratique.

Même si B réussit mieux, le résultat sera seulement **exploratoire**, car les consignes et le nombre total d'appels diffèrent. Nous publions donc les appels, les tokens déclarés par le serveur, les erreurs et les cas exacts séparément. Un score CI vert n'est pas une preuve d'apprentissage.

## Commandes

```sh
python -m unittest discover -s research/learning_hub/self_teach02 -p test_self_teach02.py -v
# Avec le serveur Qwen2.5-3B GGUF épinglé via llama.cpp :
python research/learning_hub/self_teach02/runner.py --server http://127.0.0.1:8080 --output /tmp/omega02-raw.json
python research/learning_hub/self_teach02/score.py --raw /tmp/omega02-raw.json --output /tmp/omega02-score.json
```

Le workflow `.github/workflows/omega-self-teach02.yml` exécute une fois l'examen via CPU GitHub Actions, sans API payante, avec sorties brutes archivées. Une reprise du même examen n'est **jamais** une nouvelle réplication. Les tests peuvent conclure à l'absence de mémoire et à l'absence de gain.

**Statut avant les runs** : préenregistré, implémenté, résultat scientifique inconnu.
