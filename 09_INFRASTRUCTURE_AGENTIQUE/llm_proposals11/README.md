# Omega 11 — génération libre locale + mémoire des hypothèses

## Ce pilote ajoute deux capacités concrètes

**Générateur local neuronal.** Six cas FOLIO/Yale auparavant inutilisés (validation lignes 61–66, version v0.0) sont fournis à Qwen 2.5 Coder 3B Instruct GGUF Q4_K_M, exécuté par `llama-server` CPU avec HTTP **local uniquement**. Il reçoit les prémisses et la question en anglais, **jamais les annotations formelles ni les labels**, et propose librement jusqu'à deux `idea` + `test` par question. Les idées ne sont pas construites à partir d'une liste de types scientifiques prédéfinis.

**Mémoire vérifiable.** `ledger.py` tient une suite JSONL d'événements avec empreintes en chaîne, identifiants stables, rejouabilité, refus de doublons contradictoires et refus des états `VERIFIED` sans autre voie de certification. Les hypothèses non démontrées peuvent être reprises lors d'une nouvelle exécution **si le fichier JSONL de l'exécution antérieure est réintroduit**. Une exécution GitHub Actions l'archive comme artefact ; elle **ne le réimporte pas automatiquement** lors de la suivante.

## Sécurité épistémique

- `idea` et `test` sont des suggestions de modèle, **pas des découvertes ni des tests exécutés**.
- Les indices de prémisses et les citations exactes sont vérifiés. Une citation incorrecte laisse la proposition visible mais `REJECTED_PROVENANCE`.
- Les textes reçus sont des **données**. Ils ne sont jamais interprétés comme des instructions de shell, de connexion ou de modification.
- Un champ de décision `scientific_verdict` est toujours `UNDETERMINED`, avec `certified=false`. Le modèle ne peut pas promouvoir une hypothèse.
- Les sorties HTTP `/v1/chat/completions` séparent le message généré du prompt, en évitant l'ancien problème d'écho de `llama-cli` de #150.
- L'absence de sortie JSON exploitable reste un échec explicite de génération, et non une abstention du modèle scientifique.

## Reproduction

Les tests logiciels (modèles simulés mais sans appels payants) :

```bash
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/llm_proposals11 -p test_proposer.py -v
```

Le workflow `.github/workflows/omega-llm-proposals11.yml` construit un `llama-server` épinglé et télécharge le modèle public Qwen 3B épinglé par SHA256 si nécessaire. Les appels sont uniquement à `127.0.0.1:8091`. Son rapport et son JSONL sont écrits **hors du dépôt**, archivés pendant 30 jours par GitHub Actions.

Sans un serveur local actif, la commande finale échouera proprement :

```bash
python3 09_INFRASTRUCTURE_AGENTIQUE/llm_proposals11/proposer.py \
  --ledger /tmp/omega11-proposal-events.jsonl \
  --output /tmp/omega11-proposals-raw.json
```

### Reprise manuelle de la mémoire

Pour reprendre un journal ultérieurement, fournir au paramètre `--ledger` son **chemin local conservé**. Son historique est rejoué et vérifié à chaque insertion ; les propositions identiques ne sont pas réinscrites. Sur smartphone, l'artefact GitHub est une option de consultation mais **ne rend pas Omega autonome entre les cycles**. Un raccordement de sauvegarde versionnée sur la branche expérimentale serait une étape distincte, nécessitant contrôle de concurrence et de quota.

## Comparaisons et limites

- Échantillon : les six premières entrées FOLIO validation 61–66, sélection gelée avant code, seulement trois ensembles de prémisses indépendants.
- Comparaison : générateur lexical figé de la PR #165, deux pistes maximum, même source/question. Ce protocole ne valide pas automatiquement la nouveauté ou l'utilité scientifique de l'un ou de l'autre.
- Métriques : appels CPU réels, JSON décodés, propositions, citations exactes, hypothèses rejetées, historique validé et coûts.
- **0 contre-modèle réellement exécuté, 0 nouvelle preuve par cette version**. Même une génération convaincante ne sera pas un gain démontré de justesse.
- Aucune API payante, aucun entraînement de poids, aucune écriture dans `main` ou les PR parentes, aucun déploiement du site ni raccord au cycle horaire.

Source externe [Yale-LILY/FOLIO](https://github.com/Yale-LILY/FOLIO), licence CC BY-SA 4.0, échantillon issu du commit `5d7bb84c7edab3fb358e057d2807f19cf5cf5e2d`.
