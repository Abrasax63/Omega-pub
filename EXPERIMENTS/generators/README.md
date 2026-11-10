# Générateurs T1/T3 — v0.1

## Fichiers

- `t1_t3_generators.py` : génération des tâches et séparation des paquets public/privé.
- `test_t1_t3_generators.py` : tests unitaires `unittest`.
- `../T1_T3_TEST_PLAN_V0_1_2026-11-10.md` : plan reproductible des contrôles existants et complémentaires.

## État vérifié au 10 novembre 2026

- GitHub Actions : run [42795937582](https://github.com/Abrasax63/Omega-pub/actions/runs/42795937582), Python 3.12.
- Résultat observé dans les logs : **12 tests exécutés, 12 réussis**.
- Cela valide les tests unitaires présents dans ce commit uniquement.
- Cela ne valide pas encore la cohérence automatique prompt/paramètres, les sérialisations public/privé de bout en bout, ni la comparaison A/B/C.

## Reproduction locale

Depuis la racine du dépôt :

```bash
python -m unittest discover -s EXPERIMENTS/generators -p 'test_*.py' -v
```

La commande ci-dessus est celle utilisée par le workflow CI. Le résultat local doit être consigné séparément du résultat CI.

## Couverture actuellement présente

- T1 : exemple canonique (22), recalcul indépendant de l'oracle depuis les paramètres publics en mémoire, reproductibilité, diversité des graines et rejet d'une profondeur invalide.
- T3 : exemples canoniques (21 et 25), vérification arithmétique des deux témoins, rejet de témoins falsifiés ou donnant la même sortie, sous-détermination sur 100 graines, reproductibilité et contrôle anti-fuite du paquet public.
- Interface : `public_payload()` est destiné au système évalué ; `evaluation_payload()` reste privé pour l'évaluateur.

## Contrôles complémentaires non encore implémentés

- Vérifier que le prompt rendu et les paramètres publics désérialisés décrivent exactement les mêmes équations.
- Sérialiser puis relire les paquets public et privé avant validation de l'oracle.
- Tester explicitement les cas limites de profondeur 1 et 2, coefficients négatifs, coefficients égaux à 1, zéros et grandes amplitudes.
- Tester l'absence de fuite dans les fichiers, journaux, métadonnées et erreurs, pas seulement dans la représentation du paquet public.

## Règle anti-fuite

Ne jamais transmettre au modèle évalué le paquet privé, la graine, les paramètres cachés, les témoins ou les réponses de référence. Les identifiants publics sont dérivés de l'énoncé, pas directement de la graine.

Les tests actuels valident une partie du générateur. Ils ne comparent pas ChatGPT seul, Omega à rôles fixes et Omega adaptatif.
