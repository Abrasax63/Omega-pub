# Prisme adaptatif — P1/P2

## P1 — Planification

`planner.py` expose `plan_mission(mission)`. Il retourne un plan explicable
avec les rôles RCE activés, les questions assignées, les motifs, les critères
d'échec, les conditions d'arrêt et les rôles écartés.

La mission peut également transporter `mission_id`, `domain`, `scope`,
`exclusions`, `known_ids` et `constraints`. Ces champs sont conservés pour
la préparation du contexte ; ils ne changent pas automatiquement les règles
de routage.

## P2 — Préparation des contextes

`context.py` expose `prepare_contexts(root, plan, max_documents=12)`.
La fonction réutilise directement les fonctions en lecture seule de la
passerelle MCP existante :

- `memory_search` une fois par rôle planifié ;
- `memory_get` pour les identifiants exacts explicitement fournis et ceux
  retrouvés dans les résultats d'index ;
- un paquet distinct par rôle, conservant le résultat de recherche, les
  enregistrements exacts, les statuts, les références, les candidats et les
  limites de couverture.

Exemple depuis ce dossier :

```python
from pathlib import Path
from planner import plan_mission
from context import prepare_contexts

mission = {
    "question": "Auditer le lemme sur les noyaux et périodes",
    "mission_type": "mathematical",
    "domain": "dynamique finie",
    "scope": "Énoncé et hypothèses explicitement fournis",
    "exclusions": ["aucune extrapolation hors du périmètre"],
    "known_ids": ["BR-R90-01"],
}
plan = plan_mission(mission)
bundle = prepare_contexts(Path("/chemin/vers/Omega-pub"), plan)
```

## Garanties et limites

- Le dépôt est lu localement ; aucune écriture n'est effectuée.
- Les identifiants exacts non trouvés restent explicitement non trouvés.
- Les éléments de migration en attente gardent leur type et leur statut.
- Les documents candidats ne deviennent pas des dépendances établies.
- Le moteur reste lexical et local ; il ne consulte pas le Web.
- Aucun modèle n'est appelé et aucune perspective n'est exécutée.
- Aucun verdict scientifique ni certificat RAVI-2 n'est produit.
- Les rôles restent des perspectives préparées pour l'agent principal, pas
  des agents autonomes ou indépendants.

## Tests

Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism/` :

```bash
python -m unittest -v
```

Les tests d'intégration du workflow vérifient aussi le RCE, la passerelle MCP
et les tests de fumée des index du dépôt.
