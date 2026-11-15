# OMEGA-MEMORY-REPAIR-01 — connaissances récupérées → tests exécutables → correction

**Pilote expérimental**. Pour les hypothèses et décisions figées **avant** la première inférence, voir [PREREG_2026-11-15.md](PREREG_2026-11-15.md).

## Système réellement raccordé

- Le RCE existant lit en accès **lecture seule** la fiche [ALGORITHMIC_PILOT.md](../auto_research/ALGORITHMIC_PILOT.md), consigne ses rangs/lignes et l'empreinte SHA-256 du fichier. Le compilateur `compile_rce_tests` vérifie la présence des concepts `Q^h`, exactitude, exponentiation et lowbit dans le fichier récupéré.
- Sur cette base, il sélectionne **quatre tests Python fixés à l'avance** (identité à h=0, cycle à h=2, embranchement et cycle long) et calcule les réponses avec l'implémentation indépendante `reference.walks_exact`. **Ce n'est pas de l'apprentissage libre ni une preuve universelle :** c'est un assemblage de tests à partir d'une bibliothèque limitée.
- Le même Qwen2.5-Coder-3B, température 0, **deux appels par bras** : proposition initiale, tests sur développement, puis proposition corrigée. Dans le contrôle, la correction reçoit le contre-exemple public et un texte RCE placebo ; dans le bras mémoire, elle reçoit le **même contre-exemple** et les quatre assertions exécutables. Les deux compléments ont la même longueur en caractères, pas nécessairement en tokens.
- Les quatre essais de génération sont effectués réellement dans GitHub Actions sans API payante. Le code produit est vérifié en AST et testé **seulement dans Docker sans réseau**. Aucun repli silencieux vers un algorithme classique n'est permis.
- Les deux bras subissent les mêmes trois exemples de développement et **les mêmes quatre tests**. Un programme qui ne passe pas tous les tests de développement n'est pas exécuté sur les cinq cas réservés.
- La réserve est nouvelle, tirée de graines aléatoires avant le premier appel au modèle, et son empreinte SHA-256 est loguée. Les deux classiques forts `square-scan` et `square-lowbit` la résolvent ; le banc examine Q^h et Δ_h.
- Le gate de non-régression donne au maximum un statut `REVIEW_REQUIRED` si une proposition correcte est plus rapide d'au moins 15 % que le meilleur classique et sans duplication de source. **Aucune fusion, publication CORE ou mutation de main.**
- Le plan P1, le paquet de contexte P2, le registre P3 (une perspective computationnelle effectivement exécutée et autres rôles non exécutés) et les événements de provenance SHA-256 font partie du rapport JSON.

## Commandes

Test de compilation et de provenance (sans modèle) :

```bash
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/memory_repair -p 'test_memory_repair.py' -v
```

Exécution complète : Python 3.12, Docker, llama.cpp CPU et Qwen2.5-Coder-3B GGUF (empreinte vérifiée dans le [workflow](../../.github/workflows/omega-memory-repair.yml)).

```bash
python 09_INFRASTRUCTURE_AGENTIQUE/memory_repair/memory_repair.py \
  --llama-cli /chemin/llama-cli \
  --model-file /chemin/model.gguf \
  --output memory-repair-result.json
```

**Limites scientifiques** : une seule paire de trajectoires de correction, aucune égalité stricte en tokens, pas d'évaluateur extérieur, réserve internalisée au run, temps Docker très bruité, modèles et sources historiques connus, aucun apprentissage des poids de Qwen. L'origine RCE est authentifiable par l'empreinte du checkout mais pas par une vérification bibliographique indépendante. Un programme plus correct dans ce petit pilote indiquerait au mieux un **signal local** de l'utilité d'assertions, pas une nouvelle théorie ou une auto-amélioration générale.
