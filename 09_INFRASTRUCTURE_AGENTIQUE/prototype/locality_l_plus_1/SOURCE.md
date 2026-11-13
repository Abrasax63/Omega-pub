# PR #18 — Calcul de localité L+1, 325 468 comparaisons

Contrôle de calcul exhaustif pour n ≤ 6 et L = 2 ou 3.
La sortie ne contient aucun contre-exemple sur ce périmètre.
Le préfixe inclut les temps de 0 à L+1. La suffisance universelle reste ouverte.

- PR : https://github.com/Abrasax63/Omega-pub/pull/18
- Exécution : https://github.com/Abrasax63/Omega-pub/actions/runs/42788979270/job/129737263482
- Checkout CI : ac1a76e9c01491bd4a1365be6be425d0e26b9d45

`run.log` est un extrait du journal de ce job. `check.py` est la copie du
script à ce checkout. Les empreintes épinglées dans le vérificateur ont été
calculées à partir du journal et du script récupérés auprès de GitHub.

Depuis la racine du dépôt, retrouver la fiche avec le moteur de contexte,
contrôler ses pièces, puis relancer le calcul :

```bash
python3 09_INFRASTRUCTURE_AGENTIQUE/prototype/verify_locality.py 'Quel calcul soutient les 325 468 comparaisons ?' --replay
```

Sans `--replay`, la commande vérifie l'archive locale. Cette intégration est
spécifique à la PR #18 et utilise des références épinglées. Le rejeu utilise
la même implémentation que la CI.
