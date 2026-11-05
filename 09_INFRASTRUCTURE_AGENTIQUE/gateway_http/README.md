# Passerelle MCP HTTP — prototype 0.1

**Statut :** prototype distant expérimental, lecture seule.  
**Transport :** MCP Streamable HTTP, réponses JSON sans session ni SSE.  
**Runtime cible :** FastAPI sur Vercel Functions (Python 3.12).

## Architecture

- `app.py` expose le point d'entrée FastAPI attendu par Vercel et le endpoint `POST /mcp`.
- Le serveur HTTP réutilise les fonctions du serveur MCP STDIO existant dans `09_INFRASTRUCTURE_AGENTIQUE/gateway/server.py`.
- Le moteur RCE dans `prototype/rce.py` reste la seule source de recherche et de récupération.
- Le transport STDIO local n'est ni remplacé ni modifié.

Le serveur est sans état : aucun identifiant de session MCP n'est émis. Les appels POST produisent des réponses JSON ; les notifications reconnues produisent HTTP 202 sans corps. GET n'est pas pris en charge (HTTP 405). Les versions MCP prises en charge sont 2025-11-25, 2025-06-18 et 2025-03-26.

## Configuration obligatoire avant exposition

Définir dans l'environnement Vercel, sans placer les valeurs dans Git :

- `OMEGA_GATEWAY_TOKEN` : secret aléatoire long, utilisé comme jeton Bearer.
- `OMEGA_ALLOWED_ORIGINS` : liste séparée par des virgules des origines clientes autorisées. Une requête sans en-tête Origin est admise ; toute origine présente mais non listée est refusée.

Si le secret n'est pas configuré, le serveur répond HTTP 503 et n'expose aucun outil. Une authentification absente ou invalide reçoit HTTP 401. Une origine non autorisée reçoit HTTP 403. Aucun mécanisme CORS permissif n'est activé.

Ne jamais mettre le jeton dans le dépôt, les logs, les paramètres d'URL ou une configuration cliente partagée. Le client doit envoyer `Authorization: Bearer <token>`.

## Outils

Les trois outils restent identiques à la passerelle locale :

- `gateway_status`
- `memory_search`
- `memory_get`

Aucun outil d'écriture, de commit, de push, de certification ou d'exécution de calcul n'est exposé. Les arguments inconnus sont refusés. La récupération des fiches conserve les limites du serveur local (chemins dans le checkout, extensions autorisées, taille maximale et extrait borné).

## Tests locaux

Python 3.12 :

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/gateway_http -v
```

Le workflow GitHub Actions dédié exécute les tests HTTP sur chaque modification de la passerelle ou de son point d'entrée.

## Limites explicites

- Prototype sans session, sans SSE et sans notifications serveur.
- Les requêtes de recherche restent lexicales et rescannent les documents présents dans le checkout.
- Le contenu consultable est celui du dépôt déployé ; aucun espace privé ou compte externe n'est connecté.
- L'authentification par jeton est une protection minimale de prototype, pas un remplacement d'une gestion OAuth multi-utilisateur.
- La passerelle ne certifie aucun résultat et ne modifie aucun statut scientifique.
- Le déploiement Vercel et la connexion d'un client MCP sont des étapes distinctes, non réalisées par ce commit.
