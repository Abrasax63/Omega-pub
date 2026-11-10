# Générateurs T1/T3 — v0.1

## Fichiers

- `t1_t3_generators.py` : génération des tâches et séparation des paquets public/privé.
- `test_t1_t3_generators.py` : squelette de tests unitaires avec `unittest`.

## Exécution locale (à faire après disponibilité de l'environnement)

Depuis ce dossier :

```bash
python -m unittest -v
```

**État :** les tests sont écrits mais n'ont pas encore été exécutés. Aucun résultat de test n'est revendiqué.

## Couverture prévue

- T1 : exemple canonique (22), recalcul indépendant de l'oracle depuis les paramètres publics, reproductibilité, diversité des graines et rejet d'une profondeur invalide.
- T3 : exemples canoniques (21 et 25), vérification arithmétique des deux témoins sur les paramètres visibles, rejet de témoins produisant la même sortie, détection de la sous-détermination sur 100 graines, reproductibilité et contrôle anti-fuite.
- Interface : seul `task.public_payload()` est transmis au système évalué. `task.evaluation_payload()` reste privé pour l'évaluateur.

## Règle anti-fuite

Ne jamais transmettre au modèle évalué le paquet privé, la graine, les paramètres cachés, les témoins ou les réponses de référence. Les identifiants publics sont dérivés de l'énoncé, pas de la graine.

Ces tests valident les générateurs seulement. Ils ne comparent pas ChatGPT seul, Omega à rôles fixes et Omega adaptatif.
