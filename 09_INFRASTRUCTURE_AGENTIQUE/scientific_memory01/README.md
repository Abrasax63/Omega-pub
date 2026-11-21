# Omega — registre scientifique durable (expérimental)

Cette branche est une **archive Git persistante et contrôlable par revue**, séparée de `main`. Contrairement aux artefacts temporaires GitHub Actions, les fichiers de mémoire une fois committés restent accessibles dans l'historique du dépôt tant que celui-ci est conservé.

**Ordre de confiance :**
1. `verified_ledger.jsonl` : seulement les observations explicitement vérifiées (empreintes originales et paires NL/Lean de source, contrôles arithmétiques **bornés**, métriques d'expérience **empiriques**), jamais un théorème nouveau proclamé prouvé.
2. `model_quarantine.jsonl` : toutes les réponses du LLM, y compris refus, erreurs et divergences. Elles ne constituent **pas** des preuves.
3. `index.json` : empreinte SHA256 de fin de chaîne, nombre de records, ID du workflow d'origine, empreinte du rapport.

Les lignes du ledger forment une chaîne `previous_record_sha256 → record_sha256`. `read_memory.py` vérifie chaque liaison et les statuts autorisés. Une source tierce appariée à Lean et marquée `sorry` n'est **pas** une preuve Lean recompilée localement.

**Processus de publication :** le workflow d'inférence de [EXTERNAL-MEMORY-01](https://github.com/Abrasax63/Omega-pub/pull/227) prépare un artefact candidat seulement. Après vérification des données brutes, les records validés sont recopiés ici sur branche distincte et le lecteur est testé. La mémoire n'est jamais écrite automatiquement dans `main`.

Le journal ne stocke pas les poids de modèles et ne constitue pas un entraînement. Les scores A/B de Qwen mesurent des associations de références existantes et non l'équivalence mathématique sémantique. Les preuves et capacités scientifiques au-delà des contrôles finis bornés restent **INDÉTERMINÉES**.
