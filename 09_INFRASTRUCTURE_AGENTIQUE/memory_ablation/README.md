# OMEGA-MEMORY-AB-01 — mémoire RCE comme cause testable de proposition de code

**Expérience exploratoire sur branche distincte de PR #98. Ni amélioration cognitive ni découverte algorithmique présumées.**

## Principe

Même Qwen2.5-Coder-3B Q4_K_M, **une inférence par bras** :

- `sans_memoire` : spécification mathématique commune, sans note du référentiel.
- `placebo_rce` : le RCE récupère `ARCHITECTURE.md` et transmet un extrait historique relatif à la gouvernance, non à l'algorithme.
- `memoire_rce` : le **même moteur RCE** recherche puis transmet un extrait de `09_INFRASTRUCTURE_AGENTIQUE/auto_research/ALGORITHMIC_PILOT.md` (méthodes de calcul et leur vérification), publié avant cette expérience.

Les deux extraits ont exactement la même longueur en **caractères** (maximum 700), **mais pas nécessairement en jetons**. Leurs chemins, rangs de récupération, positions de lignes et empreintes sont consignés. Les documents sont traités comme des **données non fiables**, et non des instructions. Le prompt commun **ne dit pas explicitement d'utiliser l'exponentiation binaire**, afin que les notes RCE puissent éventuellement avoir un effet visible. Les trois bras reçoivent le même budget maximum de génération (400 tokens), sans feedback ni deuxième tentative.

La comparaison primaire est `memoire_rce - placebo_rce` ; `sans_memoire` est un contrôle secondaire. La réussite scientifique ne se juge pas uniquement face à une version affaiblie du modèle : deux algorithmes classiques forts restent références.

## Étapes contrôlables

1. `integrated_cycle.prepare(ROOT)` exécute P1 et P2 ; le RCE recherche ensuite les deux documents **dans les fichiers du checkout GitHub effectivement testé**.
2. Générer cinq familles de réserve avec `secrets.randbits(48)` et leur `Q^h` de référence par programmation dynamique ensembliste, **avant toute inférence**. Le manifeste est gelé par SHA-256 et imprimé dans le log GitHub.
3. Construire et archiver trois prompts avec leurs empreintes SHA-256.
4. Exécuter trois inférences CPU avec le même modèle et la même limite de sortie ; conserver sources, SHA de source et SHA sémantique AST.
5. Tester les candidats sur trois cas publics de développement, dans Docker sans réseau. Un candidat qui n'est pas correct sur les trois ne passe **pas** la réserve.
6. Tester au plus une fois chaque candidat admissible sur les cinq cas réservés ; chaque réponse est confrontée à `reference.walks_exact` (Q^h) et `reference.actual_h_relation` (Δ_h) via `model_pilot.score`.
7. Comparer aux deux algorithmes `square-scan` et `square-lowbit` sur les mêmes cinq cas. Le `gate.py` existant assure la non-régression. Un éventuel `REVIEW_REQUIRED` exige, **en plus**, un gain brut d'au moins 15 % face au meilleur classique et l'absence de duplication historique de source. Aucune écriture ni promotion automatique.
8. P3 enregistre uniquement la perspective computational effectivement exécutée. `event_store` construit et vérifie la chaîne locale de provenance ; le rapport entier est archivé.

## Reproduction

Prérequis : Python 3.12, Docker, llama.cpp CPU binaire épinglé, poids Qwen2.5-Coder-3B Q4_K_M SHA-256 préenregistré.

```bash
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/memory_ablation -p test_memory_ablation.py -v
python 09_INFRASTRUCTURE_AGENTIQUE/memory_ablation/memory_ablation.py \
  --llama-cli /chemin/llama-cli \
  --model-file /chemin/model.gguf \
  --output memory-ablation-result.json
```

Le [workflow dédié](../../.github/workflows/omega-memory-ablation.yml) vérifie les sources, lance les tests lexicaux et les trois appels réels au modèle, puis archive un JSON reprenant les chemins et lignes consultés, les prompts injectés, les sources et leurs empreintes, les scores, la chaîne d'événements et les raisons du refus.

**Limites** : un seul modèle, un échantillon par bras, ordre de bras fixe, contexte comparable en caractères et non en jetons, benchmarks synthétiques internes, coût Docker bruité. Un gain ponctuel ne démontre **ni apprentissage neuronal des poids, ni intelligence supérieure, ni originalité algorithmique, ni indépendance scientifique**. Le modèle « sans mémoire » conserve évidemment ses connaissances de pré-entraînement ; il est seulement privé du contexte RCE dans cette requête.

Lire [PREREG_2026-11-15.md](PREREG_2026-11-15.md) pour le protocole préenregistré et sa chronologie.
