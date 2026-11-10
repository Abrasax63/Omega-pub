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

## Connexion d'un client MCP distant

Endpoint Preview (alias de branche Vercel, à privilégier pour éviter de figer une URL de déploiement éphémère) :

`https://omega-pub-rce-gateway-git-architecture-memoir-45b844-omega-61f0.vercel.app/mcp`

La protection Vercel de l'équipe reste active. Un client externe doit donc envoyer **deux en-têtes secrets**, sans les placer dans l'URL :

- `Authorization: Bearer <OMEGA_GATEWAY_TOKEN>`
- `x-vercel-protection-bypass: <VERCEL_AUTOMATION_BYPASS_SECRET>`

Le premier est la clé d'accès propre à ce serveur ; le second contourne uniquement l'écran d'authentification Vercel pour les appels automatisés. Ne jamais les committer, les coller dans un ticket ou les exposer dans des logs. Ils doivent être stockés dans le gestionnaire de secrets du client.

Exemple de forme de configuration (syntaxe indicative ; le format exact dépend du client MCP) :

```json
{
  "mcpServers": {
    "omega-memory": {
      "url": "https://omega-pub-rce-gateway-git-architecture-memoir-45b844-omega-61f0.vercel.app/mcp",
      "headers": {
        "Authorization": "Bearer ${OMEGA_GATEWAY_TOKEN}",
        "x-vercel-protection-bypass": "${VERCEL_AUTOMATION_BYPASS_SECRET}"
      }
    }
  }
}
```

Le serveur n'implémente pas encore le flux OAuth 2.1 de la spécification d'autorisation MCP : il s'agit d'une authentification statique par Bearer, adaptée à un prototype mono-client si les deux secrets sont conservés séparément et protégés. Le client doit envoyer `MCP-Protocol-Version: 2025-11-25` sur les requêtes qui suivent `initialize`, et `Accept: application/json, text/event-stream` sur les POST.

Les appels sans en-tête `Origin` sont acceptés pour les clients serveur-à-serveur. Si un client envoie un en-tête `Origin`, son origine doit être ajoutée explicitement à `OMEGA_ALLOWED_ORIGINS`. Ne pas autoriser `*`.

**Limite ChatGPT :** ce dépôt et Vercel ne peuvent pas, à eux seuls, enregistrer ce serveur comme application personnalisée dans l'interface ChatGPT. La connexion effective dépend d'un client qui permet de déclarer un endpoint MCP distant et des en-têtes personnalisés.
