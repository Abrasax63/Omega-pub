# OMEGA-CONTEXTUAL-BANDIT-02 — apprentissage contextuel expérimental

**Question** : un sélecteur apprenant du coût des requêtes et de l'incertitude observée fait-il mieux que la meilleure stratégie active non apprenante ?

Le premier bandit (PR #157) ne battait pas ACTIVE. Cette expérience introduit deux tarifs publics de symboles et une variable de taille d'espace d'hypothèses. Deux types d'apprentissage, GLOBAL et CONTEXTUAL, choisissent entre deux proposants : ACTIVE (désaccord de PR #145) et COST_AWARE (désaccord par unité de coût réel). Ils doivent battre **les deux** stratégies non apprenantes, ainsi que GLOBAL pour apporter un gain attribuable au contexte.

Les machines cachées sont des modèles Mealy synthétiques binaires à 3 états. Chaque politique paie ses seules vraies requêtes ; le résultat de l'action non exécutée n'est pas fourni à l'apprenant. Les deux politiques entraînables reçoivent 48 mondes et leurs tarifs ; leurs trajectoires peuvent différer. Les 24 autres mondes sont exclusivement réservés au test.

Consulter le [préenregistrement](PREREG_2026-11-17.md), commité en premier (SHA `10f94b228d1806f9576dda9078be226d8bba07a6`). Aucun seed, récompense, seuil ni choix de politique ne doit changer après la première lecture des scores HOLDOUT.

## Reproduction

Python 3.11 et bibliothèque standard, aucun compte/API payant :

```bash
python -m unittest discover -s experiments/omega-contextual-bandit-02 -p 'test_contextual.py' -v
python experiments/omega-contextual-bandit-02/contextual_lab.py --output evidence/report.json
sha256sum evidence/report.json
```

Le workflow dédié exécute 14 tests avant une unique comparaison réservée sur événement PR, reconstruit indépendamment les statistiques depuis le JSON, et archive les journaux incluant les résultats négatifs.

**Limites** : modèle de sélection en tableau de récompenses, pas de LLM réentraîné, de preuve mathématique nouvelle, ni de certification autonome. Les prix symboliques sont synthétiques ; le coût CPU n'est pas normalisé. PR DRAFT, `main` inchangée.
