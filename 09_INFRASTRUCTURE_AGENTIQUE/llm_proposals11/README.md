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

## Checkpoint de mémoire Git — conservation au-delà des artefacts Actions

Après [le premier run Qwen réel #44157203400](https://github.com/Abrasax63/Omega-pub/actions/runs/44157203400), ses **12 événements** ont été conservés dans le fichier versionné `LEDGER_CHECKPOINT_2026-11-17.jsonl.gz.b64` de cette branche. La compression base64+gzip évite de faire grossir Git avec les logs bruts du serveur.

Reconstituer le journal original, sans frais d'API ni modification du dépôt :

```bash
base64 -d 09_INFRASTRUCTURE_AGENTIQUE/llm_proposals11/LEDGER_CHECKPOINT_2026-11-17.jsonl.gz.b64 | gunzip > /tmp/omega11-proposal-events.jsonl
echo '38864b20197b7b2c36f9a65fdffd263c85c4e0d48367a1780475c6cd5b3a23ea  /tmp/omega11-proposal-events.jsonl' | sha256sum -c -
```

Le dernier `event_hash` attendu est `6cd253c378c38bf9be62b25c549cebbb85ebb552502b0dc5da3b3cb5a4225686`. Les tests `test_countermodel_review.py` valident la restauration et l'intégrité de la chaîne.

Ce checkpoint est **persistant tant que cette branche existe**. L'intégration automatique à un cycle horaire reste absente ; le fichier doit être explicitement restauré avant un autre calcul, et une nouvelle version doit être commise pour conserver les événements suivants. La chaîne d'empreintes protège contre les changements non détectés relativement à cette version Git épinglée ; elle ne constitue pas une signature externe d'identité ou de vérité.

## Deux contre-modèles réels — audit POST-HOC

Le premier run a généré plusieurs idées logiquement douteuses. `countermodel_review.py` fait **deux vérifications sémantiques exécutables** : un contre-modèle à la déduction « Mike a nécessairement un visa F1 » et un autre à « Ted ne peut pas être un animal de compagnie ». Chaque contre-modèle satisfait les clauses formalisées des prémisses et falsifie la conclusion que Qwen avançait.

**Limite fondamentale :** les clauses logiques ont été traduites **manuellement à partir des textes FOLIO après lecture des réponses**. L'audit ne démontre donc ni une traduction autonome de l'anglais vers la logique, ni une victoire sur un holdout indépendant ; il démontre une capacité de réfutation sous une formalisation explicite. Il ne faut pas promouvoir d'hypothèses en théorèmes sur cette seule base.

```bash
python3 09_INFRASTRUCTURE_AGENTIQUE/llm_proposals11/countermodel_review.py
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/llm_proposals11 -p 'test_countermodel_review.py' -v
```
