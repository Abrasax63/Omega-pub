# Omega 15 — plusieurs lectures, format de sortie contraint, audit de fidélité

Suite au diagnostic de la PR #174 (6 appels Qwen réussis, 5 JSON exploitables, mais aucune formalisation de problème complète), ce pilote expérimente trois changements distincts :

- Demander explicitement à `llama-server` local **un schéma JSON** : `response_format={"type":"json_schema","schema":...}`. La compatibilité avec le serveur réellement épinglé et la production d'un **texte complet** sont contrôlées en CI ; un JSON schématiquement correct ne signifie pas une représentation scientifiquement correcte.
- **Préserver jusqu'à deux lectures candidates** d'une même question, même quand leurs clauses sont incomplètes ou incorrectes ; conserver les idées libres plutôt que les supprimer. Le nombre de candidates et le coût sont consignés.
- **Auditer chaque prémisse séparément** : index, citation littérale, AST typée, négation/quantificateurs/connecteurs détectables en surface, motifs explicites de refus. Ces contrôles sont des **alertes de fidélité**, pas une garantie d'équivalence logique. `semantic_fidelity_verified=false` toujours.

## Chaîne d'exécution

`FOLIO anglais brut → modèle Qwen local (candidates[...]) → audit par prémisse → AST compositionnelle de #175 → contre-modèle fini rejoué (si AST intégrale et sans alarme majeure)`.

Le refus d'une formalisation n'entraîne pas l'effacement des idées. Un témoin fini sur la représentation extraite est uniquement un résultat **conditionnel à cette formalisation** ; jamais une réfutation certifiée de la phrase originale. Les formalisations alternatives peuvent se contredire sans qu'Omega en choisisse une arbitrairement.

Le code utilise uniquement des outils locaux/standard Python, un modèle GGUF public déjà employé par les expériences précédentes, et les fonctions mathématiques exactes existantes. Aucun entraînement, aucune API payante.

## Comparaison et preuve d'antériorité

Protocole figé avant code : `PREREG_2026-11-17.md`; données FOLIO validation **91–96** figées au préalable depuis Yale-LILY/FOLIO v0.0 (commit `5d7bb84c`, CC BY-SA 4.0). Empreinte Git du morceau `d5c4e541dbc2552874f41ef361f19a6b9c813407`. Les précédents 85–90 ont déjà été consommés par #175 et **ne** sont pas un nouveau holdout. Le niveau de rigueur attendu est une expérience exploratoire même sur 91–96 : prompt et schéma choisis par le même auteur.

La référence machine #175 possède un budget de génération différent (900 contre 1600 jetons), donc on ne déduira **aucun** gain architectural à coût égal de ce comparatif non apparié. Une base déterministe #172 est inspectée sans appel supplémentaire, uniquement comme contrôle.

## Test reproductible

```bash
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/multi_fidelity15 -p test_runner.py -v
```

Lancer un serveur Qwen2.5-Coder-3B-Instruct fixé à `127.0.0.1:8091`, puis restaurer le checkpoint et lancer :

```bash
base64 -d 09_INFRASTRUCTURE_AGENTIQUE/llm_proposals11/LEDGER_CHECKPOINT_2026-11-17.jsonl.gz.b64 | gunzip > /tmp/omega15-memory.jsonl
python3 09_INFRASTRUCTURE_AGENTIQUE/multi_fidelity15/runner.py \
  --ledger /tmp/omega15-memory.jsonl --output /tmp/omega15-raw-report.json
```

Le workflow `omega-multi-fidelity15.yml` effectue ces étapes et archive les sorties brutes, alarmes par source, idées alternatives, éventuels contre-modèles et journal chaîné. **La copie étendue du journal reste dans l'artefact, non automatiquement commitée en mémoire intercycles**.

Aucune modification de `main`, aucune fusion, aucun raccord automatique au RCE ou au cycle horaire. Les idées non certifiées restent exploratoires.
