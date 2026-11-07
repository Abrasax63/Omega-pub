# Contrat du Research Context Engine

**Version :** 0.1 — **Statut :** proposition non implémentée

## 1. Mission

Le Research Context Engine (RCE) prépare le contexte scientifique nécessaire à une mission d'agent. Il ne produit pas de verdict scientifique et ne réécrit pas les fiches sources. Il résout, sélectionne, relie et présente des connaissances existantes en préservant leur provenance.

## 2. Entrée de requête

Une requête de contexte doit préciser :

- `mission_id` et version ;
- question et domaine scientifique ;
- termes, identifiants ou résultats connus ;
- périmètre et exclusions ;
- type d'agent et rôle attendu ;
- niveau de détail demandé ;
- droits d'accès ;
- contraintes de fraîcheur pour les sources externes.

Le RCE ne doit pas interpréter une demande vague comme une autorisation de lire des contenus privés.

## 3. Pipeline de récupération

1. **Résolution exacte :** retrouver d'abord les IDs, versions, chemins et références explicitement cités.
2. **Dépendances :** récupérer les dépendances déclarées, en conservant leur statut propre.
3. **Recherche lexicale :** rechercher les termes, symboles, noms de fichiers et identifiants.
4. **Recherche sémantique :** proposer des contenus proches, étiquetés comme candidats et non comme dépendances établies.
5. **Contre-recherche :** rechercher activement les réfutations, objections, résultats négatifs, corrections et limites.
6. **Littérature :** interroger les sources externes pertinentes, avec date et identifiant de version.
7. **Déduplication :** regrouper les copies sans perdre les provenances distinctes.
8. **Assemblage :** construire un paquet ordonné, avec références et statuts visibles.
9. **Contrôle :** vérifier que chaque assertion présentée possède une référence résoluble ou est explicitement marquée non sourcée.

La recherche sémantique ne crée jamais un lien de dépendance scientifique. Elle ne fait que proposer des candidats à examiner.

## 4. Contrat de sortie

Le paquet de contexte doit inclure :

- un manifeste versionné ;
- la requête initiale et ses paramètres ;
- la liste des éléments récupérés avec ID, version, statut, espace, URI et emplacement ;
- les dépendances explicites et les rapprochements seulement candidats ;
- les sources externes et dates de consultation ;
- les objections et contre-exemples associés ;
- les éléments manquants ou non accessibles ;
- les limites de couverture ;
- une empreinte du contenu assemblé.

Si la recherche est incomplète, le RCE doit le signaler. Il ne doit jamais remplacer silencieusement une source introuvable par un résumé ou une reconstitution.

## 5. Adaptation au rôle sans altération de la source

Le RCE peut ordonner et filtrer les éléments selon le rôle :
- chercheur : état de l'art, lacunes, pistes et dépendances ;
- réfutateur : hypothèses, cas limites, objections, contre-exemples et alternatives ;
- formaliste : définitions exactes, énoncés, hypothèses et dépendances formelles ;
- computationnel : données, scripts, versions, commandes, sorties et certificats ;
- bibliographe : affirmations à vérifier, références primaires et travaux contradictoires.

Le filtrage ne doit pas masquer les informations qui pourraient invalider la mission. Les agents doivent pouvoir demander un complément et citer les éléments exacts du paquet.

## 6. Critères de qualité

Un paquet est acceptable si :
- chaque élément a un identifiant ou une référence traçable ;
- les statuts sont conservés ;
- les versions sont explicites ;
- les dépendances déclarées ne sont pas confondues avec les similarités sémantiques ;
- les contre-éléments sont inclus lorsque pertinents ;
- les droits d'accès sont respectés ;
- les lacunes de récupération sont visibles ;
- le paquet peut être reconstruit à partir de son manifeste, dans la limite de la disponibilité des sources.

## 7. Hors périmètre

Le RCE ne décide pas de la vérité d'une proposition, ne certifie pas une preuve, ne déduit pas l'originalité scientifique d'une recherche web et ne promeut pas automatiquement les sorties des agents. Ces décisions relèvent des procédures de recherche et de validation applicables.
