# Architecture scientifique d'Omega-pub

## 1. Objectif

Omega-pub est organisé comme une bibliothèque scientifique modulaire. Les domaines sont séparés pour éviter les confusions de périmètre, tandis qu'un socle transversal assure l'identification des résultats, leur provenance, leurs dépendances et leur historique.

Cette architecture est une convention de travail du projet. Elle ne constitue pas en elle-même une validation scientifique des contenus.

## 2. Principes

1. **Un domaine, un périmètre explicite.** Chaque module définit son objet, ses conventions et ses limites.
2. **Un résultat, une fiche identifiable.** Tout résultat présenté comme établi doit être rattaché à un énoncé précis, une version, des hypothèses et des éléments de vérification.
3. **Séparation des statuts.** Le statut scientifique est distinct du statut de publication.
4. **Traçabilité.** Les corrections ne doivent pas effacer silencieusement les versions antérieures.
5. **Reproductibilité proportionnée.** Les calculs et programmes doivent préciser les entrées, versions, dépendances et commandes nécessaires.
6. **Pas de transfert automatique de validation.** La validation d'un résultat ne valide pas automatiquement ses dépendances, ses analogies ou les résultats voisins.
7. **Pas de fusion forcée.** Une relation entre deux modules doit être explicitement définie et justifiée.

## 3. Modules

- `00_GOUVERNANCE/` : index global, conventions, statuts, provenance et architecture.
- `01_RAVI2/` : méthode, protocoles, certifications et audits.
- `02_MATHEMATIQUES/` : résultats mathématiques, notamment systèmes dynamiques et théorie de l'observation.
- `03_INFORMATIQUE_THEORIQUE/` : SAT, complexité, réductions et questions P/NP.
- `04_CCS/` : définitions, structures et résultats propres à CCS.
- `05_OMEGA_SRR/` : littérature, définitions et recherches propres à cet axe.
- `06_CALCUL_SCIENTIFIQUE/` : programmes, simulations, données partageables et procédures de reproduction.
- `07_REVUES_INDEPENDANTES/` : rapports, contre-exemples, critiques et réponses.
- `08_ARCHIVES/` : versions et dossiers retirés de l'index actif, conservés pour traçabilité.\n- `09_INFRASTRUCTURE_AGENTIQUE/` : contrats de mémoire partagée, moteur de contexte, provenance des agents et dépôt contrôlé de propositions. Ce module décrit une architecture cible ; il ne signifie pas qu'un orchestrateur ou un moteur de mémoire est déjà déployé.

Les modules sont des frontières d'organisation, pas des affirmations d'indépendance mathématique.

## 4. Infrastructure agentique native\n\nLe multi-agent est conçu comme un composant de l'écosystème documentaire, et non comme une mémoire parallèle. Le module `09_INFRASTRUCTURE_AGENTIQUE/` définit le contrat de consultation des trois espaces (certifié interne, expérimental interne, externe), le paquet de contexte par mission, l'identification des agents et des exécutions, ainsi que la traçabilité des dérivations.\n\nLes agents disposent d'un accès en lecture selon leurs droits et peuvent déposer des propositions. Ils ne peuvent pas promouvoir seuls un résultat au statut certifié. Les propositions passent par les procédures RAVI-2. La répétition d'une affirmation par plusieurs agents ne constitue pas une vérification indépendante.\n\nCette spécification est une proposition documentaire ; les services logiciels correspondants restent à construire et à tester.\n\n## 5. Statut scientifique et statut de publication

Le statut scientifique décrit le niveau de justification d'un énoncé. Le statut de publication décrit sa disponibilité.

Statuts scientifiques autorisés :
- DÉMONTRÉ
- CALCUL EXACT
- SIMULÉ
- EMPIRIQUE
- CONJECTURÉ
- RÉFUTÉ
- INDÉTERMINÉ
- À RÉEXAMINER

Statuts de publication proposés :
- PUBLIC : dossier consultable dans ce dépôt.
- EXPÉRIMENTAL : contenu de recherche en cours, explicitement signalé.
- PRIVÉ : contenu non publié ; ne doit pas être transféré sans autorisation.
- ARCHIVÉ : contenu conservé pour l'historique, non présenté comme résultat actif.

Ces deux dimensions doivent être renseignées séparément. Un contenu public peut être conjectural ; un résultat démontré peut ne pas encore être publié.

## 6. Identifiants et versions

Chaque résultat reçoit un identifiant stable, par exemple `MATH-OBS-001` ou `SAT-001`. Une version est attachée à chaque modification substantielle de l'énoncé, de ses hypothèses, de sa preuve ou de son statut.

Une correction doit indiquer :
- l'identifiant et la version antérieure ;
- la modification apportée ;
- sa justification ;
- les dépendances potentiellement affectées ;
- le nouvel état de validation.

Les commits Git documentent les modifications du dépôt ; ils ne remplacent pas la version scientifique de la fiche.

## 7. Dépendances entre résultats

Les dépendances doivent être déclarées dans les fiches, avec l'identifiant et la version exacte du résultat utilisé. Une dépendance non vérifiée doit être signalée comme telle. Les cycles de dépendances doivent être explicités et examinés : aucun résultat ne peut se justifier uniquement par un autre résultat qui dépend lui-même du premier.

## 8. Reproductibilité

Pour un calcul ou un programme, documenter autant que possible :
- langage et version ;
- dépendances et versions ;
- données d'entrée et provenance ;
- commande exacte ;
- graine aléatoire, si pertinente ;
- sortie attendue ou certificat ;
- environnement et limites connues.

Une simulation ne constitue pas une preuve générale. Ne jamais déclarer une exécution qui n'a pas effectivement eu lieu.

## 9. Publication et archivage

GitHub héberge les sources et l'historique de développement. Les versions scientifiques destinées à être citées pourront ensuite être archivées sur une infrastructure adaptée (par exemple Zenodo), avec métadonnées de citation. Cette étape ne doit être réalisée qu'après vérification du contenu à archiver et des droits de diffusion.

## 10. État de cette architecture

Cette architecture est une première version de gouvernance documentaire. Elle ne certifie aucun résultat scientifique et ne signifie pas que tous les modules sont déjà renseignés. L'index global indique explicitement les contenus effectivement publiés.
