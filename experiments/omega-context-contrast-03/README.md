# OMEGA-CONTEXT-CONTRAST-03 — apprentissage conditionnel à observations partielles

**Contexte** : la PR #158 ne discriminait pas l'intérêt d'apprendre par situation : 29 mises à jour informatives dans un seul contexte, politiques identiques. Cette nouvelle expérience ne modifie pas le code de #158 ; elle définit **une autre tâche**, où l'objectif est d'identifier la vraie machine parmi 16 hypothèses grâce au **dernier bit** des traces payées.

Deux proposants non apprenants se confrontent : **BALANCED** (coupe le plus équilibrée) et **PRICE_AWARE** (gain de séparation par coût de sonde). Deux bandits à récompense observée, GLOBAL et CONTEXTUAL, tentent de les arbitrer. Le contexte public tient compte du tarif des symboles et de la taille d'ensemble compatible.

Le [préenregistrement](PREREG_2026-11-17.md) (commit `05017609751aeae1a3d181e9ef6eefc000d833e4`) a été déposé **avant le code et toute exécution**.

## Deux stages sans fuite

1. **CALIBRATION** sur 24 machines non réservées : vérifier que les deux générateurs sont vraiment distincts dans les deux tarifs et qu'il existe au moins une victoire pour chaque bras. Si échec, le pilote renvoie `UNINFORMATIVE_CONTEXTS`, aucun apprentissage et **aucune ouverture du holdout**.
2. **TRAIN / HOLDOUT** seulement si CALIB réussit : 48 instances train, 24 test disjointes jusque dans leurs **hypothèses candidates**, 12 sondes max à prix exact. Les poids des deux bandits sont gelés pendant le test ; la vraie machine n'est accessible qu'au simulateur puis au vérificateur après chaque sonde payée.

Le critère scientifique exige que CONTEXTUAL identifie correctement les 24 mondes et batte **les trois références** en coût moyen, sans augmenter le nombre moyen de sondes. Autrement, résultat négatif conservé.

## Exécution reproductible

Python 3.11, bibliothèque standard, aucune API payante :

```bash
python -m unittest discover -s experiments/omega-context-contrast-03 -p 'test_context_contrast.py' -v
python experiments/omega-context-contrast-03/context_contrast.py --mode calibration --output evidence/calibration.json
# Uniquement après validation du gate (PR DRAFT) :
python experiments/omega-context-contrast-03/context_contrast.py --mode full --output evidence/report.json
```

GitHub Actions sépare les étapes, vérifie les critères et archive les traces brutes. Tout statut `SUCCESS` de CI signifie exécution technique seulement. Le pilote ne montre pas l'amélioration d'un LLM, la vérification d'une preuve mathématique réelle, ni un gain autonome généralisé. Les coûts CPU ne sont pas égalisés.

**État initial** : code + protocole présents. Résultat scientifique **INDÉTERMINÉ** avant inspection des exécutions. `main`, CORE, PR #157 et #158 inchangés ; PR en brouillon, aucune fusion.
