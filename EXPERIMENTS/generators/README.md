# Générateurs T1/T3 — v0.2

## Fichiers

- `t1_t3_generators.py` : génération des tâches, rendus canoniques T1/T3 et séparation des paquets public/privé.
- `test_t1_t3_generators.py` : tests unitaires `unittest`.
- `../T1_T3_TEST_PLAN_V0_1_2026-11-10.md` : plan reproductible, couverture présente et contrôles restants.

## Rendus canoniques et validation

- `render_t1_prompt(public_parameters)` reconstruit le prompt T1 depuis les paramètres publics.
- `render_t3_prompt(public_parameters)` reconstruit le prompt T3 sans accéder au paramètre caché.
- `validate_prompt_consistency(public_payload)` compare exactement le prompt transmis au rendu canonique correspondant à la famille.
- Les générateurs utilisent eux-mêmes ces fonctions de rendu : la génération et la validation partagent donc un format canonique unique, tandis que les tests de mutation vérifient que les divergences entre texte et paramètres sont rejetées.
- Le validateur retourne `False` pour les familles inconnues, les champs absents, les paramètres mal formés ou un prompt divergent.

## Exécution

Depuis la racine du dépôt :

```bash
python -m unittest discover -s EXPERIMENTS/generators -p 'test_*.py' -v
```

Le workflow GitHub Actions `.github/workflows/t1-t3-generators.yml` exécute cette commande sous Python 3.12.

## Couverture

Les 12 tests de la version précédente ont réussi sur le run [42795937582](https://github.com/Abrasax63/Omega-pub/actions/runs/42795937582).

Dix nouveaux tests sont maintenant ajoutés pour :
- la cohérence canonique T1 et T3 ;
- l'aller-retour JSON public T1/T3 et privé T3 ;
- le recalcul de l'oracle T1 depuis les données publiques désérialisées ;
- les mutations du prompt et des paramètres ;
- la suppression d'une étape T1 et la mutation du champ manquant T3.

Le fichier contient donc 22 méthodes de test. Le résultat CI correspondant au commit qui ajoute ces tests doit être consulté avant de déclarer cette nouvelle version validée.

## Limites restantes

- Les cas limites forcés (`k=1`, `k=2`, coefficients négatifs, `a_i=1`, `b_i=0`) restent à compléter.
- L'audit exhaustif des fuites dans les identifiants, fichiers, journaux et erreurs reste à faire.
- Le validateur de prompt ne remplace pas un validateur exhaustif du schéma public/privé.
- Aucun benchmark A/B/C n'a été exécuté ; aucune supériorité d'Omega n'est établie.

## Règle anti-fuite

Ne jamais transmettre au modèle évalué le paquet privé, la graine, les paramètres cachés, les témoins ou les réponses de référence. Les identifiants publics sont dérivés de l'énoncé, pas directement de la graine.
