# Reader21 — module web en lecture seule pour Omega (expérimental)

Ce pilote est disponible sur la branche de la [PR #190](https://github.com/Abrasax63/Omega-pub/pull/190). Il **n'est pas branché** au site ni à la boucle horaire, et ne modifie pas `main`.

## Outils disponibles pour un orchestrateur Python

Depuis le dossier `09_INFRASTRUCTURE_AGENTIQUE/reader_bridge21/` :

```python
from agent_tools import dispatch

search = dispatch("search_bibliography", {"query": "finite dynamical systems observability"})
source = dispatch("read_omega_public_math_source", {})
```

Ces opérations exigent une connexion HTTPS sortante. Elles retournent un objet avec :
- `read_only: true`, `web_content_trust: "UNTRUSTED"`, `max_network_calls: 1` ;
- `result.results[0].status` : `WEB_FETCHED_UNTRUSTED` ou `REMOTE_FETCH_FAILED` ;
- l'URL publique, l'empreinte SHA-256 du corps, sa taille et une heure UTC ;
- jusqu'à trois métadonnées DOI Crossref OU un document Markdown public Omega.

Le module refuse les autres noms d'outils, les URL arbitraires, les commandes, les chemins libres, les hôtes inconnus et les requêtes Crossref trop longues. Les pages ne peuvent autoriser ni exécution ni publication ni certification mathématique. Une **métadonnée Crossref n'est pas une preuve**.

## Utilisation en ligne de commande

```bash
python 09_INFRASTRUCTURE_AGENTIQUE/reader_bridge21/web_access.py \
  --mode search \
  --query "finite automata observability" \
  --output /tmp/references.json

python 09_INFRASTRUCTURE_AGENTIQUE/reader_bridge21/web_access.py \
  --mode source \
  --output /tmp/omega-math-source.json
```

La démonstration `--mode both` effectue **deux** appels, et chaque mode spécialisé en effectue **un** au maximum. Les fichiers JSON gardent les échecs aussi bien que les réussites. Aucun jeton/API payant n'est requis.

## Passerelle de lecture mathématique (distincte du web)

```bash
python 09_INFRASTRUCTURE_AGENTIQUE/reader_bridge21/semantic_bridge.py \
  --output /tmp/french-ast-exact.json
```

Le parseur français n'accepte que des tournures **limitées** et des hypothèses explicites : les six phrases compatibles sont analysées par Reader20, tandis que les six cas trompeurs provoquent l'abstention. Une citation exacte, une traduction syntaxique ou une référence bibliographique **ne valide pas** la vérité générale d'une proposition.

## État mesuré le 19 novembre 2026

- [Run #44489292001](https://github.com/Abrasax63/Omega-pub/actions/runs/44489292001), les jobs de sûreté, de grammaire et de réseau terminent SUCCESS.
- [Résultat des formulations françaises](https://github.com/Abrasax63/Omega-pub/actions/runs/44489292001/artifacts/14511822020) : 6 cas reconnus, 6 refusés, zéro promotion.
- [Résultat web réel](https://github.com/Abrasax63/Omega-pub/actions/runs/44489292001/artifacts/14512276808) : 1 recherche Crossref (3 DOI) et 1 document public Omega téléchargés et hachés SHA-256.
- Aucun test ne démontre encore la compréhension libre du langage, un gain de recherche scientifique, la qualité des références retrouvées ou une intégration de l'agent horaire.

Avant toute intégration à un agent autonome, limiter le nombre de recherches par cycle, conserver les journaux de provenance et faire valider séparément le sens des AST. Ne jamais exécuter d'instructions découvertes dans les résultats web.
