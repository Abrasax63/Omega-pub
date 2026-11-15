# OMEGA-SYMNEU-01 — réparation symbolique bornée avec sélection Qwen

**Statut : expérimental, empilé sur PR #101, `main` inchangé.** [Préenregistrement de la méthode](PREREG_2026-11-15.md) commité **avant** le code, les tests et les appels modèle.

Le moteur répond à une question limitée : une petite grammaire de tests de bits peut-elle retrouver la correction de **la ligne 11 déjà localisée** du programme erroné de PR #100 ? La même méthode pourra-t-elle fournir une liste de candidats **déjà vérifiés** à Qwen2.5-Coder-3B pour qu'il choisisse un identifiant sans écrire de code non contrôlé ?

## Composants existants effectivement raccordés

1. Recherche RCE lexicale en lecture seule de `ALGORITHMIC_PILOT.md` ; l'empreinte SHA-256 et les lignes sont conservées. Ce texte autorise une **priorité humaine préprogrammée** sur `result[i]` et `j`, non un solveur appris.
2. `grammar()` énumère 16 prédicats sur deux familles de masques (`rows`/`result`), deux indices de ligne, deux indices de bit, et leur négation éventuelle ; aucun texte du modèle ne devient du code Python.
3. `simulate` interprète directement le petit langage sans `exec`. Chaque candidate est réfutée par `reference.walks_exact` sur quatre cas publics connus et **64 cas exhaustifs** sur des relations à deux états et horizons 1..4. Conserver les contre-exemples et le rang du premier succès. Deux ordres de recherche sont comparés sur **les mêmes 16 hypothèses** ; tous les survivants doivent être identiques dans les deux ordres.
4. `apply_patch` remplace **la même unique ligne** de la source historique, valide l'AST et envoie les codes survivants à `model_pilot.score`, qui utilise **Docker sans réseau**, sur les trois familles publiques de développement.
5. `symbolic_only` choisit automatiquement le premier candidat vérifié par ID. `symbolic_plus_qwen` envoie à Qwen **uniquement la liste des survivants**, et n'accepte qu'un identifiant exact parmi ceux-ci. Une sortie non conforme conduit à **REJECTED**, sans source de secours présentée comme choix du modèle.
6. Une réserve de cinq familles nouvelles est créée et gelée **avant** l'exploration et l'inférence. Les sélections sont évaluées **une seule fois** sur cette réserve, contre deux classiques forts `square-scan` et `square-lowbit`, avec les oracles exacts Q^h et Δ_h et le gate de non-régression. Si les deux bras choisissent la même source, le même résultat n'est compté **qu'une fois** ; ce n'est pas une seconde reproduction indépendante.
7. P1/P2/P3 et la chaîne d'événements de provenance sont conservés dans l'artefact JSON. Aucune promotion CORE ni fusion automatique.

## Tester

```sh
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/symbolic_neural -p 'test_symbolic_neural.py' -v
python 09_INFRASTRUCTURE_AGENTIQUE/symbolic_neural/symbolic_neural.py \
  --llama-cli /chemin/llama-cli --model-file /chemin/model.gguf \
  --output symbolic-neural-result.json
```

La seconde commande exige Docker et les poids Qwen épinglés, contrôlés par [le workflow](../../.github/workflows/omega-symbolic-neural.yml). Les tests unitaires couvrent les cas à 1–3 états, l'existence de témoins de réfutation, le contrôle des sorties Qwen et l'intégrité des sources RCE.

## Ce que l'expérience ne peut pas prouver

- **Le problème et la ligne à corriger sont déjà connus.** La vraie correction classique est présente dans la grammaire de 16 candidats; le chercheur peut la retrouver par simple énumération. Il s'agit d'un solveur symbolique minuscule, pas d'une découverte mathématique.
- Si une seule proposition survit, **Qwen ne décide rien de substantiel**, même si une invocation réelle a lieu. Un gain de recherche entre les deux ordres viendrait d'un **prior humain codé explicitement**, pas d'une règle que la mémoire a apprise.
- Les tests finis ne sont pas une preuve universelle, les temps Docker sont bruités, les réserves internes ne sont pas scellées par un évaluateur tiers, et une sortie correcte sur une seule famille de bug ne mesure pas l'intelligence générale.

Les conclusions doivent être séparées : **recherche symbolique**, **référence classique**, **sélection par Qwen**, **provenance**, et **statut scientifique**.
