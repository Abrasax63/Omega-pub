# Réconciliation détaillée des 42 résultats sans carte individuelle — SQLite v33

Date : 4 novembre 2026  
Dépôt : `Abrasax63/Omega-pub`  
Branche : `migration/ravi2-ccs-public-2026-11-04`  
Base examinée : `RESEARCH_MEMORY.sqlite`, version 33, SHA-256 `ef3e9a0de51a44b30599f73f027829751a2eb144e4468175c0f290b5e0159bf4`.

## 1. Résultat de cette passe

Les 42 identifiants ci-dessous correspondent au reliquat documentaire annoncé dans l'audit de migration : résultat actif SQLite sans carte individuelle identifiée dans le dossier migré, après les 26 correspondances explicites et les 17 cartes candidates relues le 4 novembre.

La base a été relue en mode SQLite lecture seule. Les statuts ci-dessous sont copiés des lignes `certified_active_results` ; ils ne sont ni réévalués ni promus par ce rapport.

- 42 résultats listés ;
- 33 au statut enregistré `DÉMONTRÉ` ;
- 9 au statut enregistré `CALCUL EXACT` ;
- aucun statut modifié ;
- aucune écriture dans SQLite.

## 2. Liste exhaustive du reliquat

| ID | Statut enregistré | Titre |
|---|---|---|
| APP-OBS-SPARSE-DISJOINT | DÉMONTRÉ | Sparsification disjointe des contraintes globales d’observabilité |
| BR-AFFINE-GAUGE-GLUE | DÉMONTRÉ | Raccordements affines par paires et obstruction collective |
| BR-AFFINE-GROUP-CORE | DÉMONTRÉ | Noyau incompatible affine par groupes et certificat de minimalité |
| BR-AFFINE-TREE-GLUE | DÉMONTRÉ | Composition affine sur arbre et comptage par interfaces |
| BR-OBS-REVEAL-KERNEL | DÉMONTRÉ | Noyau des covariances et couvertures exactes conservés sous révélation |
| DELTA-P3-N5 | CALCUL EXACT | Séparation minimale P3 sans P2 à n=5 |
| DELTA-SPECTRUM-CLASS | DÉMONTRÉ | Classification complète des spectres de défauts Δ_h |
| DESC-SUM-01 | DÉMONTRÉ | Détecteur — somme des deux évidences |
| EXT-OAI-MARG-REPAIR | DÉMONTRÉ | Réparation simultanée des marginales de permutations |
| EXT-OAI-MATCH-CORNER | DÉMONTRÉ | Compression fidèle des coins de Brauer et support commun |
| EXT-OAI-MATCH-RANK | DÉMONTRÉ | Rang et support des diagrammes de Brauer |
| EXT-OAI-REL-CORNER | DÉMONTRÉ | Isomorphisme exact du coin de relations par restriction |
| EXT-OAI-REL-SELECT | DÉMONTRÉ | Sélecteurs élémentaires de relations |
| EXT-OAI-UNIT-LIFT | DÉMONTRÉ | Relèvement des unités au coin de rang minimal |
| OBS-AFFINE-GROUP-CORE-VALIDATION | CALCUL EXACT | Validation exacte du détecteur et essais de blocages collectifs |
| OBS-M27-BINARY | DÉMONTRÉ | Mealy27 — collapse binaire |
| OBS-M27-CONFLICT | DÉMONTRÉ | Mealy27 — noyaux de conflit bornés |
| OBS-M27-FERTILE | DÉMONTRÉ | Mealy27 — largeur fertile q−1 |
| OBS-M27-SPECTRUM | DÉMONTRÉ | Mealy27 — spectre aigu des conflits |
| OBS-RESTRICT-AFFINE | DÉMONTRÉ | Moments conjoints de restrictions affines : phase relative et poids de révélation |
| OBS-RESTRICT-COUNT | DÉMONTRÉ | Précoloration : comptage exact des collisions et CNF des traces |
| OBS-RESTRICT-FORCED-QUOTIENT | DÉMONTRÉ | Révélation sous oppositions forcées : quotient affine pondéré et transfert V19 |
| OBS-RESTRICT-GREEDY | DÉMONTRÉ | Construction de coloration par espérance conditionnelle des collisions |
| OBS-RESTRICT-MULTIMOMENT | DÉMONTRÉ | Moments conjoints affines à tout ordre sous révélation |
| OBS-RESTRICT-OVERLAP | DÉMONTRÉ | Invariant de recouvrement : covariance, Fourier–Walsh et Tutte |
| OBS-RESTRICT-PROFILE | DÉMONTRÉ | Loi exacte et reconstruction du profil des composantes sous restriction |
| OBS-V19-C5-13 | CALCUL EXACT | V19 corrigé — 13 types orbitaux locaux sur C5 |
| OBS-V19-C5-ORIENTED14 | CALCUL EXACT | V19 — raffinement orienté C5 : 14 classes |
| OBS-V19-FORCED-P4 | DÉMONTRÉ | V19 — composantes forcées P1 à P4 |
| OBS-V19-GAMMA-CONNECTED | DÉMONTRÉ | V19 — grammaire Γ des ombres dans un bassin connecté vers Cq |
| OBS-V19-LOCAL-L2 | DÉMONTRÉ | V19 — petit modèle temporel L+2 |
| OBS-V19-N11-MOMENT-GRAM | CALCUL EXACT | N11 : matrices exactes des moments et conservation des cinq circuits de 2-recouvrement |
| OBS-V19-N11-THIRD-ORDER | CALCUL EXACT | N11 : lois par paires identiques, intersections triples différentes |
| OBS-V19-PAIR-COMPLETE14 | CALCUL EXACT | V19 — compatibilité paire complète des 14 classes orientées |
| OBS-V19-TRIPLE-COMPLETE13 | CALCUL EXACT | V19 — compatibilité ternaire complète des 13 classes D5 |
| OBS-V19-UNIVERSAL10 | CALCUL EXACT | V19 — témoin universel U42 jusqu’à multiplicité 10 |
| OBS-V8-FACT-INF | DÉMONTRÉ | V8 — factorisation exacte du polynôme d’observabilité à horizon infini |
| OBS-V9-RANK | DÉMONTRÉ | V9 — rang des orbites de paires |
| OBS-V9-STAB-N1 | DÉMONTRÉ | V9 — stabilisation universelle à N−1 |
| OMEGA-O41-DET-V11 | DÉMONTRÉ | Ω-O4.1 v1.1 — détection empirique sans noyaux diagnostiques |
| Q-RQ4-COMMON-RANK | DÉMONTRÉ | RQ-Q-4 — rang commun et factorisation |
| Q-RQ4-PAULI-ROBUST | DÉMONTRÉ | RQ-Q-4 — seuil Pauli et borne scalaire optimale |

## 3. Provenances retrouvées dans SQLite

Les 42 résultats ne sont pas tous dépourvus de provenance. Les locateurs présents dans `evidence` et `result_sources` renvoient notamment aux groupes suivants :

- **Affine / noyaux / arbres** : `V19_TROISIEME_ORDRE_2026-10-15.md`, `AFFINE_GROUP_CORE_2026-10-15.md`, `COMPOSITION_AFFINE_2026-10-15.md`.
- **Delta-h** : source historique `SRC-HIST-DELTA-SPECTRUM`, ainsi que le fichier source référencé dans l'ancienne bibliothèque.
- **Mealy27** : `Adaptivity boundary - Mealy machines.docx`, `COMMIT_AUDIT_RAVI2_2026-10-14.md`, `commit_audit_checks.py` et son JSON de sortie.
- **Restrictions affines / V19** : `TRANSFERT_AFFINE_V19_2026-10-15.md`, `CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md`, `TEST_SYNTHESE_INVERSE_2026-10-15.md`, `V19_ASSEMBLAGE_ORIENTE_2026-10-15.md`, `V19_MULTIPLICITE_CAPACITE_2026-10-15.md`, `V19_BADOBJECT_N11_2026-10-15.md), et les scripts/CSV/JSON associés.
- **Navier–Stokes / RQ4 / OAI** : audits internes et sources primaires ou prépublications cités dans les lignes SQLite ; la présence d'un locateur ne garantit pas que le fichier correspondant soit dans la PR.

Ces références sont des pistes de provenance, pas des preuves que chaque artefact source est actuellement accessible dans la branche publique.

## 4. Écart de comptage à ne pas masquer

Le contrôle direct de cette version SQLite retrouve 25 résultats actifs avec une preuve de type carte (`REUSABLE_CARD` ou `RESULT_CARD`) et 22 relations de rôle `INTERFACE_CARD`. Le bilan antérieur de migration mentionne 26 liaisons explicites. Ces métriques ne sont donc pas strictement équivalentes et leur écart doit être réconcilié avant toute modification de SQLite.

Un cas particulier a été repéré : `BR-OBS-KRYLOV-01` possède un fichier de carte dans la branche (`research/bricks/BR-OBS-KRYLOV-01_GENERATOR_RECOVERY.md`) et un locateur de carte dans `evidence`, mais ce dernier est enregistré sous un type générique et sans relation `INTERFACE_CARD`. Il ne fait donc pas partie des 42 fichiers de carte manquants ; il constitue une anomalie de typage/liaison à traiter séparément.

## 5. Conclusion opérationnelle

Le blocage principal n'est pas l'absence totale de sources : plusieurs résultats disposent déjà d'audits, de scripts ou de données référencés. Le manque porte sur la **carte individuelle et/ou le transfert vérifiable de la pièce source** dans la branche publique.

Ordre de traitement recommandé :
1. rapprocher les artefacts déjà présents dans la PR des 42 résultats, sans créer de carte de remplacement ;
2. récupérer les fichiers sources encore accessibles dans la bibliothèque privée et vérifier leurs empreintes/contenus ;
3. pour les pièces introuvables, marquer explicitement `SOURCE_NON_RETROUVEE` ou `CARTE_NON_RECONSTITUABLE`, sans reconstituer de mémoire un document manquant ;
4. corriger ensuite les relations SQLite dans une nouvelle version, après audit et sauvegarde.

**Aucun statut scientifique n'est modifié par ce rapport.** La PR reste en brouillon ; aucune fusion ni écriture dans la base n'est effectuée.


## 6. Avancement après récupération dans la bibliothèque privée

Après la rédaction de ce relevé, huit cartes source supplémentaires ont été retrouvées dans la bibliothèque privée, comparées aux lignes SQLite v33 correspondantes (identifiant, titre, énoncé, domaine, hypothèses et statut), puis copiées sans réécriture dans `research/bricks/` :

- `BR-AFFINE-GAUGE-GLUE`
- `BR-AFFINE-GROUP-CORE`
- `OBS-AFFINE-GROUP-CORE-VALIDATION`
- `OBS-RESTRICT-AFFINE`
- `OBS-RESTRICT-FORCED-QUOTIENT`
- `BR-AFFINE-TREE-GLUE`
- `OBS-V19-N11-THIRD-ORDER`
- `OBS-V19-N11-MOMENT-GRAM`

L'index public `research/bricks/INDEX_BRIQUES.md` a été complété avec ces huit entrées. Les fichiers ont été créés sur la branche de migration, pas sur `main`.

**État du reliquat initial : 8 cartes restaurées ; 34 des 42 restent à retrouver ou à établir comme indisponibles.** Cette progression est documentaire uniquement : les statuts scientifiques n'ont pas changé et les scripts/calculs associés n'ont pas été rejoués.

Un contrôle séparé a repéré `BR-OBS-KRYLOV-01` dans la branche et dans la bibliothèque, bien qu'il n'appartienne pas à la liste des 42 fichiers de carte absents. Sa relation de carte dans SQLite reste à examiner.


## 7. Passe complémentaire de recherche dans toute la bibliothèque — 4 novembre 2026

Une recherche par identifiants et noms de fichiers a été complétée par un inventaire paginé de la bibliothèque privée (1 494 fichiers parcourus, huit pages, sans curseur restant). Une carte individuelle supplémentaire correspondant exactement à un résultat du reliquat a été retrouvée à la racine de la bibliothèque : `BR-OBS-REVEAL-KERNEL_BRIQUE.md`.

Le contenu intégral a été lu. Son identifiant, son titre, son statut, son domaine, ses hypothèses et ses renvois de preuve concordent avec l'entrée SQLite et l'index historique. La carte a été copiée sans réécriture dans `research/bricks/BR-OBS-REVEAL-KERNEL_BRIQUE.md` sur la branche de migration. L'index public a été complété.

**État actualisé du reliquat initial : 9 cartes restaurées sur 42 ; 33 restent sans carte individuelle retrouvée.** Les autres résultats repérés dans les index, snapshots, audits, scripts ou données ne sont pas comptés comme cartes individuelles. Aucun document manquant n'a été reconstitué à partir d'un résumé. Aucun statut scientifique n'a été modifié, aucun calcul ni test n'a été rejoué, SQLite n'a pas été modifiée et la PR reste en brouillon.
