# RAVI-2 v1.3 — formalisation stricte phase 3

Date : 16 octobre 2026.

## Objet

Fermer les 8 `DEPEND_DE` encore hors du périmètre strict après la phase 2, sans modifier les résultats scientifiques, leurs statuts ni le graphe causal.

## Résultat

- Relations nouvellement auditées : `16, 18, 19, 20, 21, 34, 39, 44`.
- Les 40/40 `DEPEND_DE` ont maintenant une revue stricte `VERIFIED_APPLICABILITY`.
- 35 interfaces sont classées `COMPOSITION`.
- 1 est `VALIDATION_REFERENCE`, 2 sont `DATA_REFERENCE`, 2 sont `DEFINITION_REFERENCE`.
- Les deux références de définition sont `BR-OBS-CAP-02 → BR-OBS-CAP-01` et `BR-OBS-CAP-03 → BR-OBS-CAP-01`; elles réutilisent la définition de `Cap(ω)` mais ne sont pas comptées comme compositions.
- 40 contrats stricts et 19 adaptateurs vérifiés sont persistés.

## Les six nouvelles compositions

- `OBS-RESTRICT-GREEDY → OBS-RESTRICT-COUNT` : formule exacte des probabilités conditionnelles utilisée dans la méthode des espérances conditionnelles.
- `APP-OBS-SPARSE-DISJOINT → OBS-RESTRICT-COUNT` : COUNT fournit la CNF couleur exacte de largeur ≤2L avant application du théorème externe de sparsification disjointe.
- `OBS-RESTRICT-PROFILE → OBS-RESTRICT-COUNT` : la loi sous restriction factorise la formule COUNT composante par composante.
- `EXT-OAI-MATCH-CORNER → EXT-OAI-MATCH-RANK` : comptabilité rang/support du monoïde de Brauer.
- `EXT-OAI-UNIT-LIFT → EXT-OAI-MATCH-CORNER` : utilisation du morphisme de compression `R_e` dans le coin minimal.
- `EXT-OAI-UNIT-LIFT → EXT-OAI-MATCH-RANK` : monotonie du rang le long des puissances utilisée pour forcer le plein rang réduit.

## Barrières conservées

- Le théorème sparse reste une application d’un résultat externe connu : cette phase ne recertifie pas sa preuve globale.
- Les outils Brauer restent confinés au domaine des diagrammes/coins où leurs hypothèses sont explicites ; aucun transfert vers automates ou quantique n’est ajouté.
- `DEFINITION_REFERENCE` ne compte jamais comme `COMPOSITION`.
- Une interface stricte reste versionnée : une modification d’une extrémité invalide sa restauration tant qu’elle n’est pas réauditée.

## Invariants

- Base principale inchangée : 75 résultats, 71 admissibles, 40 `DEPEND_DE`.
- 23 tables scientifiques communes identiques ligne par ligne.
- `PRAGMA integrity_check = ok`, 0 erreur de clé étrangère.
- Aucune nouvelle brique scientifique ni promotion épistémique.

## Reproduction

- registre : `/Recherche/04_CODE_DONNEES/RAVI2_STRICT/ravi2_strict_registry_phase3.json`
- vérification : `/Recherche/04_CODE_DONNEES/RAVI2_STRICT/RAVI2_STRICT_PHASE3_VERIFY_2026-10-16.json`
- script : `/Recherche/04_CODE_DONNEES/RAVI2_STRICT/ravi2_strict_phase3_deploy.py`


## Reconstruction indépendante

Le moteur strict-aware phase 3 a été exécuté sur un miroir vierge reconstruit depuis la base principale et le registre phase 3. Il restaure **40/40 contrats**, **40/40 revues** et **40/40 certificats d'interface**, sans contrat ni revue stale. Le miroir reconstruit contient **35 compositions**, **1 `VALIDATION_REFERENCE`**, **2 `DATA_REFERENCE`** et **2 `DEFINITION_REFERENCE`**. Les 23 tables scientifiques communes restent identiques à la base principale ; `PRAGMA integrity_check = ok` et aucune erreur de clé étrangère n'est détectée.

Cette reconstruction confirme que la couverture 40/40 n'est pas dépendante de l'état courant du miroir expérimental.