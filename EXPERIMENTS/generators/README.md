# Générateurs T1/T3 — v0.3

## Fichiers

- `t1_t3_generators.py` : génération des tâches, rendus canoniques T1/T3 et séparation des paquets public/privé.
- `test_t1_t3_generators.py` : tests unitaires `unittest`.
- `../T1_T3_TEST_PLAN_V0_1_2026-11-10.md` : plan reproductible, couverture présente et contrôles restants.

## Rendus canoniques et validation

- `render_t1_prompt(public_parameters)` reconstruit le prompt T1 depuis les paramètres publics.
- `render_t3_prompt(public_parameters)` reconstruit le prompt T3 sans accéder au paramètre caché.
- `validate_prompt_consistency(public_payload)` compare exactement le prompt transmis au rendu canonique correspondant à la famille.
- Les générateurs utilisent eux-mêmes ces fonctions de rendu ; les tests de mutation vérifient que les divergences entre texte et paramètres sont rejetées.
- Le validateur retourne `False` pour les familles inconnues, les champs absents, les paramètres mal formés ou un prompt divergent.

## Exécution CI

Le workflow [run 42801786605](https://github.com/Abrasax63/Omega-pub/actions/runs/42801786605), Python 3.12.16, a exécuté **22 tests : 22 réussis**. Les logs contiennent `Ran 22 tests` puis `OK`.

Deux tests supplémentaires de cas limites forcés (profondeurs T1 et coefficients affines limites) ont été ajoutés après ce run. Leur résultat CI n'est pas encore confirmé. Le fichier contient donc actuellement 24 méthodes de test, dont 22 couvertes par le run cité.

## Reproduction

Depuis la racine du dépôt :

```bash
python -m unittest discover -s EXPERIMENTS/generators -p 'test_*.py' -v
```

Le workflow GitHub Actions `.github/workflows/t1-t3-generators.yml` exécute cette commande sous Python 3.12.

## Limites restantes

- Audit exhaustif des fuites dans les identifiants, fichiers, journaux et erreurs : à faire.
- Le validateur de prompt ne remplace pas un validateur exhaustif du schéma public/privé.
- Revue indépendante du contrat et des oracles : à faire.
- Aucun benchmark A/B/C n'a été exécuté ; aucune supériorité d'Omega n'est établie.

## Règle anti-fuite

Ne jamais transmettre au modèle évalué le paquet privé, la graine, les paramètres cachés, les témoins ou les réponses de référence. Les identifiants publics sont dérivés de l'énoncé, pas directement de la graine.
