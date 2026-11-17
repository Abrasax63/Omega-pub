# OMEGA-PROVENANCE-ORACLE-06 — optimiser l'ordre de vérification des origines

Ce module transpose le calcul de stratégies exactes de la [PR #168](https://github.com/Abrasax63/Omega-pub/pull/168) à une **question de provenance**, plutôt qu'à l'identification intégrale d'une machine finie.

**Question scientifique locale :** quatre pièces apparentées sont-elles issues d'**au moins trois exécutions originales distinctes**, ou certaines sont-elles de simples copies d'une même exécution ? La réponse doit être établie à partir de vérifications payées, sans compter deux fois un miroir. Les quinze partitions possibles de quatre pièces en origines réelles constituent un monde fermé, initialement équiprobable. Les six comparaisons possibles « même origine d'exécution ? » sont supposées exactes une fois vérifiées.

**Cette expérience ne lit pas encore de vrais journaux GitHub.** Il s'agit d'un modèle synthétique de provenance, et les coûts sont des unités d'effort artificielles. Le résultat ne démontrera pas que l'agent sait reconstruire automatiquement les identifiants d'origine depuis un dossier de pièces brutes.

## Références

La politique exacte `EXACT_VERDICT_ORACLE` minimise l'espérance du coût **pour décider le verdict**, et peut s'arrêter avant de reconstruire toute la partition. Elle est comparée à `CHEAP_FIRST`, `PARTITION_SPLIT_PER_COST` et `DECISION_GAIN_PER_COST`, cette dernière connaissant elle aussi la question à décider. Tous les arbres sont rejoués sur **15/15 mondes possibles**, avec vérification indépendante des réponses, certificats, coûts et dénominateurs.

La préinscription [`PREREG_2026-11-17.md`](PREREG_2026-11-17.md), commit `ce03dc1af00af9521a3ca7ddc80993d2718d5091`, a été enregistrée avant tout code et tout score. Les tests et la calibration portent sur les indices 0–11. Les **24 cas tarifaires réservés** utilisent les indices 100–123 et sont ouverts uniquement par workflow PR. Cela n'est pas un nouveau jeu de structures : uniquement de nouveaux prix sur les mêmes quinze partitions.

## Reproduction sans API

```bash
python -m unittest discover -s experiments/omega-provenance-oracle-06 -p 'test_provenance_oracle.py' -v
python experiments/omega-provenance-oracle-06/provenance_oracle.py --mode calibration --output evidence/calibration.json
python experiments/omega-provenance-oracle-06/audit_report.py evidence/calibration.json
# Le holdout n'est lancé dans la CI qu'après réussite des tests.
```

Toutes les sorties sont datées, les chemins et les scores négatifs sont conservés et un auditeur distinct recalcule l'optimum par énumération sans utiliser le solveur. Un run réussi certifie la **cohérence interne de ce modèle**, pas une augmentation d'intelligence d'un LLM. Pas de fusion, pas de modification de `main` ou CORE.

**Étape ultérieure** : réaliser un pilote différent sur de **vrais journaux GitHub bruts**, avec un corrigé de regroupement fondé sur `run_id`, `run_attempt` et l'identité des artefacts, puis mesurer les éventuels faux certificats, refus et coûts d'extraction. Le solveur actuel ne fait pas ce travail réel.
