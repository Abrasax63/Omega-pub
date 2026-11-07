# Feuille de route — mémoire scientifique auto-référentielle

**Version :** 0.1 — **Statut :** proposition non implémentée

## Règle de conduite

Construire par incréments vérifiables, sans réorganiser à nouveau toute la bibliothèque, sans déplacer les résultats scientifiques et sans toucher à `main` directement. Les composants existants (index, registre transversal, fiches, statuts, protocole RAVI-2 et CI) sont réutilisés.

## Phase 0 — Audit et contrat (préalable)

- [x] Examiner l'architecture publique, le README, les index, les statuts, le modèle de fiche et le protocole de revue sur `main`.
- [x] Identifier le manque spécifique : absence, dans les documents examinés, d'un contrat opérationnel de mémoire partagée et de provenance des interventions agentiques.
- [x] Rédiger le contrat de mémoire, le contrat du Context Engine, le modèle de provenance et les critères de réalisation.
- [ ] Vérifier les documents et chemins présents sur les branches de travail actives avant toute intégration.
- [ ] Faire relire la proposition et corriger les conflits avec les PR en cours.

## Phase A — Référentiel consultable (lecture seule)

Objectif : permettre à un agent de retrouver une connaissance précise sans altérer son statut.

Livrables :
- registre d'IDs et versions résolubles ;
- index des fiches, documents, scripts, données et références externes ;
- recherche exacte, puis sémantique en complément ;
- paquet de contexte versionné ;
- citations internes stables et liens vers les sources primaires.

Critères d'acceptation :
- un ID et une version retrouvent la bonne fiche ;
- une dépendance absente est signalée, jamais devinée ;
- les statuts et les espaces certifié/expérimental/externe restent visibles ;
- le paquet inclut les objections et contre-tests pertinents ;
- une reconstruction du paquet retrouve les mêmes références, sous réserve de la disponibilité des sources.

## Phase B — Journal des activités multi-agents

Objectif : rendre chaque intervention d'agent consultable et réutilisable.

Livrables :
- registre des agents et versions ;
- identifiants de mission et d'exécution ;
- manifeste de contexte ;
- journal des outils et artefacts produits ;
- graphe de provenance et relations de dérivation ;
- étiquettes d'indépendance multidimensionnelles.

Critères d'acceptation :
- chaque rapport agentique renvoie à son contexte et à ses sources ;
- deux agents utilisant la même source intermédiaire sont identifiés comme dépendants sur ce point ;
- une boucle de citation est détectable ;
- les actions non exécutées et les erreurs sont conservées comme telles.

## Phase C — Proposition et validation contrôlées

Objectif : faire contribuer les agents à la bibliothèque sans leur permettre de certifier leurs propres sorties.

Livrables :
- zone de dépôt des propositions ;
- génération de fiches candidates ;
- liens automatiques vers les dépendances et sources ;
- contrôles de schéma, liens, identifiants et versions ;
- soumission en branche/PR ;
- raccord explicite aux contrôles RAVI-2.

Critères d'acceptation :
- aucune sortie agentique ne modifie directement la mémoire certifiée ;
- aucune promotion de statut n'est automatique ;
- une décision de validation est documentée et attribuée ;
- les corrections préservent l'historique et déclenchent l'examen des dépendances affectées.

## Phase D — Découverte assistée

Objectif : utiliser le graphe et l'index pour proposer de nouvelles pistes.

Capacités candidates :
- détection de résultats proches mais non reliés ;
- détection de contradictions entre énoncés ou hypothèses ;
- repérage de dépendances manquantes ;
- identification de domaines insuffisamment explorés ;
- proposition d'expériences discriminantes et de contre-tests ;
- recherche bibliographique de nouveauté.

Une relation détectée automatiquement est une **piste**, pas un résultat scientifique. Elle doit être examinée avant d'être ajoutée comme relation formelle.

## Choix techniques différés

Ne pas sélectionner prématurément une base graphe, une base vectorielle, un orchestrateur ou un fournisseur de modèles. Commencer par les contrats de données, l'inventaire des systèmes existants et un prototype de lecture seule. Favoriser les formats ouverts, exportables et versionnables.

## Hors périmètre

- réécrire RAVI-2 ;
- fusionner les axes mathématiques sans preuve de correspondance ;
- importer en bloc les archives privées ;
- promouvoir des statuts à partir de votes multi-agents ;
- exécuter automatiquement des scripts historiques qui modifient des bases ou des fichiers ;
- fusionner des PR existantes ou modifier `main` sans revue.
