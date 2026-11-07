# Exemple de mission — paquet de contexte multi-agent

Cette mission illustre l'usage du prototype ; elle ne rapporte aucun résultat scientifique nouveau.

## Question

Quelles hypothèses, objections et contre-exemples sont documentés pour une classification de graphes forcés P1–P4 ?

## Exécution par rôle

```bash
python 09_INFRASTRUCTURE_AGENTIQUE/prototype/rce.py --repo . \
  --question "classification graphes forcés P1 P4 hypothèses contre-exemples" \
  --role researcher --output /tmp/context-researcher.json

python 09_INFRASTRUCTURE_AGENTIQUE/prototype/rce.py --repo . \
  --question "classification graphes forcés P1 P4 hypothèses contre-exemples" \
  --role refuter --output /tmp/context-refuter.json

python 09_INFRASTRUCTURE_AGENTIQUE/prototype/rce.py --repo . \
  --question "classification graphes forcés P1 P4 hypothèses contre-exemples" \
  --role formalist --output /tmp/context-formalist.json
```

## Règles de partage

- Les trois paquets sont produits à partir du même checkout et de la même question.
- Les rôles changent les priorités de recherche, pas les statuts des sources.
- Chaque agent rapporte les identifiants, chemins et lignes réellement reçus.
- Un désaccord est ajouté comme proposition/objection, jamais injecté comme correction de la mémoire certifiée.
- Une conclusion reprise d'un paquet d'un autre agent conserve cette dépendance dans sa provenance.
