# Passerelle MCP Omega-pub — prototype 0.1

**Statut :** prototype local expérimental, lecture seule.  
**Transport :** MCP sur stdio (JSON-RPC 2.0).  
**Dépendances :** Python 3.10+, bibliothèque standard uniquement.

Cette passerelle rend le moteur RCE existant appelable par un client compatible MCP. Elle ne crée pas une seconde mémoire : elle lit le checkout Omega-pub fourni au démarrage et réutilise les fonctions de \`prototype/rce.py\`.

## Outils exposés

| Outil | Fonction | Limite |
|---|---|---|
| \`gateway_status\` | Vérifie les index et annonce les capacités réelles | État du checkout local uniquement |
| \`memory_search\` | Recherche lexicale, rôles RCE, index et extraits | Les résultats sont des candidats documentaires |
| \`memory_get\` | Résout un ID exact et lit sa fiche liée si elle est sûre et présente | Pas d'historique ni de certification |

Les dossiers en attente de migration sont renvoyés séparément et ne sont jamais présentés comme des fiches certifiées.

## Démarrage

Depuis la racine du dépôt :

\`\`\`bash
python 09_INFRASTRUCTURE_AGENTIQUE/gateway/server.py --repo .
\`\`\`

Le processus parle exclusivement sur stdin/stdout. Les messages de diagnostic ne doivent pas être écrits sur stdout, réservé au protocole MCP. Pour un client MCP local, configurez un serveur stdio avec la commande \`python\`, les arguments ci-dessus et le chemin absolu du checkout.

## Exemple de configuration client

Adaptez le chemin local à votre machine :

\`\`\`json
{
  "mcpServers": {
    "omega-pub": {
      "command": "python",
      "args": [
        "/CHEMIN/ABSOLU/Omega-pub/09_INFRASTRUCTURE_AGENTIQUE/gateway/server.py",
        "--repo",
        "/CHEMIN/ABSOLU/Omega-pub"
      ]
    }
  }
}
\`\`\`

## Garanties et limites

- Aucun outil d'écriture, de commit, de push ou de modification de statut n'est exposé.
- Aucun accès réseau, aucune recherche web et aucune orchestration de modèles.
- Les chemins de fiches sont résolus à l'intérieur du checkout ; les traversées de répertoire et les liens vers des fichiers exclus sont refusés.
- La lecture de fiche est bornée à 20 000 caractères ; la taille du fichier est également limitée.
- Une entrée d'index, un extrait ou une réponse d'agent ne constitue pas une preuve ni une certification.
- Le serveur n'accède pas aux fichiers privés ou aux autres espaces de stockage de l'utilisateur.
- Le serveur ne fournit pas d'outil \`memory_history\` : aucun journal historique exploitable n'est encore implémenté.
- Le serveur ne fournit pas d'outil de calcul : l'exécution de code scientifique doit rester isolée et faire l'objet d'un contrat séparé.

## Tests

Depuis la racine du dépôt :

\`\`\`bash
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/gateway -v
\`\`\`

Le workflow GitHub Actions exécute ces tests en complément des tests RCE existants.
