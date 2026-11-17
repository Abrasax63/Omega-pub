# OMEGA-THREE-POLICY-BANDIT-01 — sélection apprenante sous contrôle

**Objet :** falsifier un gain attribué à l'apprentissage par retours d'expérience, sur une tâche finie de détection de divergence. Hérite des moteurs de génération/observation de [PR #143](https://github.com/Abrasax63/Omega-pub/pull/143) et du simulateur/adaptateur de [PR #145](https://github.com/Abrasax63/Omega-pub/pull/145), sans modifier ces fichiers.

## Hypothèse testée

Trois stratégies sur les mêmes 24 machines de test : ordre fixe, désaccord adaptatif sans apprentissage, et **bandit à deux actions** dont la valeur est mise à jour sur 48 machines d'entraînement à partir de vraies réponses payées. Chaque stratégie reçoit au maximum huit probes de dix symboles. L'unique succès scientifique local possible est un gain simultané contre les deux références, sans perte de détection.

**À ne pas confondre** : détecter une divergence de séquence sur une machine finie n'est ni prouver un théorème, ni certifier une source mathématique, ni développer un agent scientifique autonome. Ce projet n'entraîne aucun LLM.

## Démarche et garde-fous

Lire d'abord [le préenregistrement](PREREG_2026-11-17.md), commité avant le code. Les machines du TEST de PR #145 sont exclues ; aucun label d'action optimale ou résultat test ne rentre dans l'entraînement. Un vérificateur exact examine les réponses observées après chaque requête. Un rapport complet contient les résultats négatifs et les empreintes, le coût observé et les cas perdants. Les compteurs du bandit sont gelés avant le holdout.

## Exécution

Dépendances : Python 3.11, bibliothèque standard uniquement ; aucun compte ni API payante.

```bash
python -m unittest discover -s experiments/omega-three-policy-bandit-01 -p 'test_pilot.py' -v
python experiments/omega-three-policy-bandit-01/pilot.py --output evidence/report.json
sha256sum evidence/report.json
```

Le workflow GitHub dédié vérifie les contrôles avant de lancer une seule évaluation réservée sur PR brouillon, archive `report.json` et calcule l'empreinte SHA-256. Un succès CI signifie seulement que le protocole a été correctement exécuté ; il ne démontre pas de gain.

**Statut initial :** protocole + code proposés, résultats scientifiques **indéterminés avant lecture du run**, `main` et CORE inchangés, pas de fusion.
