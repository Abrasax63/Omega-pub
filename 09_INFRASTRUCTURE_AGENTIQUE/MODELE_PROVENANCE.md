# Modèle de provenance des recherches et des agents

**Version :** 0.1 — **Statut :** proposition non implémentée

## 1. Objet

Le modèle doit permettre de répondre à quatre questions :

1. Quelle affirmation ou quel artefact est présenté ?
2. Quelle activité l'a produit, modifié ou vérifié ?
3. Quel agent, humain ou outil a participé ?
4. De quelles sources, versions, données et activités dépend-il ?

Le modèle reprend les concepts généraux de provenance (entités, activités, agents, relations de génération, utilisation, attribution et dérivation). Il s'agit d'une proposition de modélisation interne ; aucune conformité technique à un standard n'est revendiquée à ce stade.

## 2. Entités à identifier

- **KnowledgeItem** : résultat, définition, conjecture, objection, référence bibliographique ou autre contenu scientifique.
- **Artifact** : fichier, code, jeu de données, rapport, preuve formelle, sortie de calcul ou paquet de contexte.
- **Activity** : recherche, extraction, calcul, simulation, formalisation, audit, revue, migration ou publication.
- **Agent** : agent logiciel, modèle/version, personne ou service ayant joué un rôle.
- **Run** : exécution concrète d'une activité, avec paramètres et environnement.
- **SourceSnapshot** : version précise d'une source externe ou interne consultée.

Chaque objet possède un identifiant stable ; les contenus modifiables possèdent une version. Un artefact binaire ou textuel peut être associé à une empreinte cryptographique, sans que l'empreinte seule soit interprétée comme une preuve de validité.

## 3. Relations minimales

| Relation | Sens |
|---|---|
| `used` | Une activité a utilisé une entité ou un artefact |
| `generated` | Une activité a produit un artefact |
| `wasAssociatedWith` | Une activité a été réalisée avec un agent |
| `wasDerivedFrom` | Un artefact dérive d'un artefact antérieur |
| `wasRevisionOf` | Une version révise une version précédente |
| `wasAttributedTo` | Un artefact est attribué à un agent |
| `dependsOn` | Un résultat déclare une dépendance scientifique |
| `reviewed` | Une activité de revue examine un objet/version |
| `contradicts` | Un élément documenté contredit un énoncé dans un périmètre précis |

Les relations doivent être typées et datées. Une similarité sémantique ne doit pas être enregistrée comme `dependsOn`.

## 4. Manifeste minimal d'une exécution agentique

Chaque exécution devrait enregistrer :

- run ID, mission ID, horodatage ;
- rôle et identifiant de l'agent ;
- fournisseur, nom et version du modèle lorsque disponibles ;
- version du prompt système ou du contrat de rôle ;
- version de l'orchestrateur et des outils utilisés ;
- empreinte du paquet de contexte ;
- références exactes aux sources consultées ;
- entrées, paramètres, commandes et environnement ;
- sorties et artefacts produits ;
- limites, erreurs, interruptions et actions non exécutées ;
- relations de dérivation vers les travaux antérieurs ;
- statut de revue et décision ultérieure, le cas échéant.

Les secrets, clés API, données personnelles et contenus privés non nécessaires ne doivent pas être consignés dans le manifeste.

## 5. Indépendance de vérification

L'indépendance n'est pas un booléen déduit du fait que deux agents sont différents. Elle doit être décrite par dimensions :

- indépendance des sources ;
- indépendance de la méthode ;
- indépendance de l'implémentation ;
- indépendance des données ;
- indépendance de l'environnement d'exécution ;
- indépendance de l'agent et de sa configuration ;
- indépendance de la revue.

Une revue peut être indépendante sur certaines dimensions et dépendante sur d'autres. Le rapport doit le dire explicitement.

## 6. Graphe de provenance et cycles

Le graphe de provenance doit conserver les chaînes de dérivation et signaler les cycles. Un cycle dans le graphe de citations n'invalide pas nécessairement tous les objets, mais il interdit de présenter la boucle comme une justification indépendante.

Exemple de boucle à détecter :

`A1 produit une hypothèse → A2 la reprend → A1 cite A2 comme confirmation.`

Cette boucle n'ajoute aucune preuve externe à l'hypothèse initiale.

## 7. Conservation

Les événements de provenance sont ajoutés plutôt que réécrits. Une correction crée une nouvelle version et référence l'ancienne. Les règles de rétention, de confidentialité et de suppression doivent toutefois primer sur l'archivage : aucune donnée supprimée pour raison de sécurité ou de droit ne doit subsister dans un journal secondaire.
