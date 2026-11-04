# RAVI-2 v1.3 — formalisation stricte phase 1

Date : 16 octobre 2026.

## Objet

Déployer dans le miroir expérimental v1.3 la formalisation machine-lisible testée en parallèle, d'abord sur V19/affine et Mealy, sans modifier la base scientifique principale, les statuts épistémiques ni le graphe `DEPEND_DE`.

## Résultat

La phase 1 formalise **20 contrats stricts**. Sur les **32 dépendances `DEPEND_DE`** touchant V19, affine ou Mealy :

- **18 interfaces de dépendance** sont certifiées au niveau v1.3 ;
- parmi elles, **17** sont des raccordements/compositions réutilisables ;
- **1** est classée séparément comme `VALIDATION_REFERENCE` et n'est pas comptée comme composition ;
- **14** restent `DEFERRED_SEMANTIC_ADAPTER` et ne sont pas promues.

La base principale reste à **75 résultats / 71 admissibles / 40 DEPEND_DE**. Les **23 tables scientifiques communes** entre la base principale et le miroir expérimental restent identiques ligne par ligne.

## Typage des dépendances

Le schéma distingue désormais :

- `APPLICABILITY` : le domaine source implique directement les préconditions du résultat cible ;
- `CONCLUSION_IMPORT` : la preuve source consomme explicitement une conclusion certifiée du résultat cible ;
- `GUARDED_APPLICABILITY` / `GUARDED_CONCLUSION_IMPORT` : même chose, mais seulement sous une branche logique déclarée ;
- `VALIDATION_REFERENCE` : le résultat cible sert de spécification de validation et non de brique de composition ;
- `UNCLASSIFIED` : raccordement non encore formalisé, impossible à certifier.

Deux dimensions supplémentaires sont obligatoires avant certification : `guard_match` et `interface_match`. Elles s'ajoutent aux contrôles de domaine, quantificateurs, hypothèses et constantes.

## Contrats stricts déployés

Le lot couvre :

- V19 : FORCED-P4, LOCAL-L2, C5-13, C5-ORIENTED14, COEX-SMALLMODEL, PAIR-COMPLETE14, TRIPLE-COMPLETE13, C5-CAPACITY, UNIVERSAL10, COEX-REGION, FIRST-OBSTRUCTION11, BAD-FIBER2 ;
- transfert V19/affine : RESTRICT-FORCED-QUOTIENT ;
- Mealy27 : FERTILE, CONFLICT, BINARY ;
- affine : GROUP-CORE, GROUP-CORE-VALIDATION, TREE-GLUE, TREE-CORE.

Cinq adaptateurs logiques explicites sont enregistrés, notamment `C5 => cycle q=5`, `L=3 => L>=2`, `q=5 => q>=3`, et la représentation exacte d'une relation affine par son groupe d'équations.

## Interfaces certifiées

Relations certifiées : `6, 7, 11, 12, 22, 23, 24, 25, 27, 28, 29, 41, 42, 50, 58, 67, 72, 73`.

Trois raccordements conditionnels sont maintenant explicitement représentés :

- relation 50 : `V19_ENDOFUNCTION_BINARY_L_GE_2_BRANCH` ;
- relation 67 : `INCOMPATIBLE_INPUT_ONLY` ;
- relation 73 : `JOINT_EMPTY` ;
- la relation 72 possède également une garde d'applicabilité TREE-GLUE imposant les préconditions locales de cette branche.

Le premier essai de déploiement a correctement refusé la relation 50 parce que `L>=2` n'avait pas encore été encodé dans la garde. La correction a consisté à compléter le contrat de branche, pas à relâcher le test.

## Dépendances volontairement différées

Les 14 interfaces restantes du périmètre exigent une sémantique plus riche que l'inclusion de préconditions : application témoin→motif de capacité, quotient affine, transfert de moments, application Krylov, identité de fixtures N11, correspondances de noyaux/couvertures, etc.

Elles restent non classifiées dans `composition_checks` et ne peuvent donc pas recevoir de certificat v1.3.

## Gardes et tests adversariaux

Le trigger de certification refuse maintenant tout raccordement si l'un des éléments suivants n'est pas vérifié : domaine, quantificateurs, hypothèses, constantes, garde, interface, version courante des deux résultats et certification courante de ces résultats.

Tests négatifs exécutés :

- tentative de certification d'une dépendance `UNCLASSIFIED` : rejetée ;
- garde forcée à `UNVERIFIED` : certification rejetée ;
- interface forcée à `UNVERIFIED` : certification rejetée.

## Test de péremption de version

Une copie de test a simulé le passage de `OBS-V19-C5-13` de v3 à v4 sans réaudit de son contrat strict. Le moteur strict-aware a alors :

- restauré 19 contrats sur 20 ;
- déclaré `OBS-V19-C5-13` stale ;
- refusé de restaurer les certifications des relations 7 et 25 ;
- réduit les interfaces certifiées de 18 à 16.

Ainsi une nouvelle version scientifique n'hérite pas silencieusement d'un ancien certificat d'interface.

## Moteur reproductible

`ravi2_v13_engine.py` devient strict-aware. L'ancien moteur conservateur est archivé comme `ravi2_v13_engine_base.py`.

Un registre indépendant est aussi persisté dans `/Recherche/04_CODE_DONNEES/RAVI2_STRICT/ravi2_strict_registry_phase1.json`. Une reconstruction depuis zéro (aucun miroir expérimental présent) a restauré 20/20 contrats, 32/32 revues et 18/18 certificats d'interface.

Lors d'une reconstruction future depuis la base principale, le moteur :

1. reconstruit le miroir v1.3 de base ;
2. ne restaure un contrat strict que si la version scientifique référencée est inchangée ;
3. ne restaure une interface certifiée que si la relation, ses extrémités et leurs versions restent identiques ;
4. laisse tomber toute certification devenue stale au lieu de la repromouvoir.

## Vérification

Audit machine : `/Recherche/04_CODE_DONNEES/RAVI2_STRICT/RAVI2_STRICT_PHASE1_VERIFY_2026-10-16.json`.

État vérifié : intégrité SQLite `ok`, 0 erreur de clé étrangère, 20 contrats stricts, 18 interfaces certifiées, 17 compositions, 1 référence de validation, 14 interfaces différées, 23 tables scientifiques communes identiques.

## Statut épistémique

Ce travail est une **amélioration d'architecture et de certification interne**. Il ne crée aucune nouvelle brique scientifique, ne modifie aucune vérité scientifique existante et ne revendique aucune validation formelle externe.