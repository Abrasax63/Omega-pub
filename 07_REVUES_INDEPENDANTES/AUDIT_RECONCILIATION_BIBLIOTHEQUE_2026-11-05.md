# Audit de réconciliation de la bibliothèque — 5 novembre 2026

**Dépôt :** `Abrasax63/Omega-pub`  
**Référence :** `main`  
**Branche historique :** `migration/ravi2-ccs-public-2026-11-04`  
**Branche de travail :** `maintenance/reconciliation-bibliotheque-2026-11-05`  
**Nature :** audit documentaire et d'organisation ; aucune certification mathématique nouvelle.

## 1. Verdict

L'architecture modulaire de `main` est conservée. Les apports complémentaires PR #3 (protocole général) et PR #4 (pilote C4) sont réunis dans cette branche, avec correction du document préliminaire C4 devenu obsolète. La migration historique PR #2 reste une source documentaire séparée : elle ne doit pas être fusionnée en bloc.

Aucune modification de `main`, aucune fusion et aucune suppression de fichier historique n'ont été effectuées.

## 2. Comptage Git vérifié

| Référence | Fichiers suivis |
|---|---:|
| `main` | 43 |
| PR #2 — migration historique | 226 |
| PR #3 — extraction/méthodes | 48 (5 ajouts, 2 modifications) |
| PR #4 — pilote C4 | 51 (8 ajouts) |

Le chiffre 58 précédemment associé à `main` comptait les objets Git, répertoires compris ; le nombre de fichiers (`blob`) est 43. Un ancien rapport PR #2 annonçait 220 chemins : l'arbre actuel en contient 226.

La comparaison de `main` avec PR #2 donne **diverged**, avec 269 commits d'avance pour la branche historique et 63 pour `main`. Base commune : `86ab1d92c968364d92da21e2e71d604557e9b8fd`. La fusion globale est donc inadaptée.

## 3. Composition des 226 fichiers PR #2

| Zone | Fichiers |
|---|---:|
| `.github/workflows/` | 1 |
| Racine | 4 |
| `reproducibility/` | 44 |
| `research/bricks/` | 94 |
| `research/code/` | 5 |
| `research/data/` | 11 |
| `research/method/` | 5 |
| `research/programs/` | 14 |
| `research/bibliography/` | 1 |
| `reviews/` | 47 |
| **Total** | **226** |

L'inventaire détaillé des chemins est dans [INVENTAIRE_FICHIERS_PR2.md](../08_ARCHIVES/MIGRATION_2026-11-05/INVENTAIRE_FICHIERS_PR2.md). La [réconciliation fichier par fichier des 226 éléments](../08_ARCHIVES/MIGRATION_2026-11-05/RECONCILIATION_226_FICHIERS_PR2.md) attribue les quatre statuts de migration : **3 TRANSFÉRÉ ET VÉRIFIÉ, 2 TRANSFÉRÉ MAIS NON VÉRIFIÉ, 183 À TRANSFÉRER, 38 DOUBLON OU ARCHIVE**. Il s'agit d'un statut documentaire ; il ne certifie pas le contenu scientifique.

## 4. Cartes, reconstitutions et provenance

L'audit historique de couverture indique :
- SQLite v33, privée et hors dépôt, recensait 85 résultats admissibles dans le périmètre étudié : 74 DÉMONTRÉ et 11 CALCUL EXACT.
- 26 liaisons d'évidence explicites et 17 candidates par nom ont été recensées. Les 17 candidates ont été comparées sémantiquement (titre, noyau d'énoncé, hypothèses, statut, version) : 17/17 correspondances confirmées, mais les liaisons d'évidence SQLite restent absentes.
- Dix cartes originales supplémentaires ont été retrouvées : BR-AFFINE-GAUGE-GLUE, BR-AFFINE-GROUP-CORE, OBS-AFFINE-GROUP-CORE-VALIDATION, OBS-RESTRICT-AFFINE, OBS-RESTRICT-FORCED-QUOTIENT, BR-AFFINE-TREE-GLUE, OBS-V19-N11-THIRD-ORDER, OBS-V19-N11-MOMENT-GRAM, BR-OBS-REVEAL-KERNEL et OBS-RESTRICT-MULTIMOMENT.
- Trente-deux originaux restent non retrouvés. Les 32 fichiers de `research/bricks/reconstructed/` sont des **reconstitutions non originales**, pas des remplacements des originaux et pas de nouvelles certifications.
- GLOBAL-LOC-01, NS-P55-COMP-01, OSC-ITER-01 et OSC-REAL-01 sont des documents composites hors table des résultats : aucun rattachement artificiel à un `result_id`.
- BR-OBS-KRYLOV-01 existe, mais son typage et sa liaison SQLite restent à corriger.
- Les 15 briques Navier–Stokes signalées dans l'audit restent en staging jusqu'à réconciliation de leurs contrats, identifiants et provenances.

## 5. Code, données et sécurité

La zone `reproducibility/` contient 44 fichiers (17 CCS et 27 RAVI-2 selon l'inventaire historique). L'audit statique signale 10 scripts avec écritures SQLite et 3 dépendants de chemins locaux fixes. Aucun n'a été exécuté pendant cet audit.

**Ne pas lancer ces scripts sur SQLite v33 ni sur la base de travail.** Toute reprise doit se faire sur copie isolée et sauvegardée, après lecture complète du code et de ses dépendances.

Le DOCX source Mealy–Helly reste dans la Library ; seul un extrait textuel est dans la branche. `conflict_nerve_certificate.py`, mentionné par la source, n'a pas été retrouvé.

L'audit historique signale une adresse d'auteur non-`noreply` dans les métadonnées de commits de PR #2. Elle n'est pas reproduite ici. La confidentialité des métadonnées doit être vérifiée avant toute fusion. Les workflows doivent être contrôlés sur la tête finale retenue ; les anciens rapports correspondent à des instantanés différents.

## 6. PR #3 et PR #4 : consolidation

PR #3 apporte le protocole d'extraction, le modèle de fiche d'instrument, le registre et un état préliminaire C4. PR #4 apporte le pilote C4 actualisé, le raccord primaire V19(2), deux vérificateurs globaux, un vérificateur local et l'audit des quotients.

Le document préliminaire PR #3 disait qu'aucun calcul C4 n'avait été exécuté. Cette affirmation est désormais dépassée : V19(2) a été retrouvée intégralement, relue et raccordée au contrat C4, L=2. La version corrigée renvoie aux rapports détaillés PR #4.

Le pilote C4 est un cas issu du corpus interne V19 ; il ne démontre pas à lui seul l'extraction d'un instrument depuis le corpus externe OpenAI.

## 7. Source primaire V19(2) restaurée

La note primaire de 359 lignes a été copiée sans modification de contenu depuis la branche historique PR #2 vers [sources/V19/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE_2.md](../02_MATHEMATIQUES/defauts_recollement/sources/V19/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE_2.md). Le Git blob SHA-1 de la source sur la branche historique est `a76d304c31d0858f625cda89ac9bc1b98a937022`. Un contrôle lexical ciblé du texte copié n'a trouvé ni adresse électronique, ni chemin local privé, ni marqueur usuel de secret ; ce contrôle n'est pas un scanner de sécurité exhaustif.

## 8. Statut exact du pilote C4, L=2

- Témoin simultané à 9 états : **CALCUL EXACT** sous la définition primaire interne V19(2), pour C4, L=2 et C4O-00…07.
- Absence de témoin pour N=4,…,8 : **CALCUL EXACT**, énumération exhaustive sous le contrat raccordé.
- Vérification : deux programmes globaux et un vérificateur local indépendant.
- Quotients : 49 congruences obtenues par deux algorithmes ; 9 préservent cycle, paires et cohérence ; seule la partition discrète à 9 états préserve les huit classes. Le script d'audit de quotients n'est pas revendiqué comme exécuté directement ; une réimplémentation séparée l'a été.
- Originalité bibliographique : **INDÉTERMINÉE**.
- Formalisation Lean : **NON RÉALISÉE**.
- Publication : **EXPÉRIMENTAL**, en attente de revue.

Aucune généralisation à d'autres q ou L n'est revendiquée.

## 9. Décisions et ordre de migration

1. Garder `main` comme référence.
2. Réunir PR #3 et PR #4 dans une branche de maintenance, sans mélanger protocole, registre d'instruments et dossier C4.
3. Garder PR #2 comme branche source documentaire ; ne pas la fusionner en bloc.
4. Conserver les 32 reconstitutions séparément des originaux.
5. Migrer les briques originales après rapprochement du texte, de la version, des hypothèses, des audits, des dépendances et de la provenance.
6. Examiner les 44 fichiers de reproductibilité par lots, après contrôle de sécurité.
7. Relier les 47 revues aux identifiants et versions exacts.
8. Garder SQLite v33, les mémoires de conversation et les documents privés hors du dépôt public.

Ordre des lots : sources primaires CL-DYN/CL-H/CL-OBSINF/CL-REFL/CL-HO ; cartes originales ; code et données ; rapports ; sécurité et historique Git.

## 10. Limites

Cet audit utilise les arbres GitHub et les rapports déjà présents sur la branche historique. Il ne constitue pas une lecture intégrale des 226 contenus, une revue mathématique tierce, un audit exhaustif de secrets ni un rejeu de tous les scripts. Les éléments non lus ou non rejoués restent non vérifiés.


## 11. Complément — intégration V19 C5, L=3 (5 novembre 2026)

Le dossier indépendant C5, L=3 a été transféré depuis la branche historique vers `02_MATHEMATIQUES/v19_c5/` et `research/data/v19_c5/`, avec son script sous `research/code/`. Le transfert conserve les fichiers historiques et les exports réparés ; il n'écrase aucune source.

La comparaison des témoins triples D5 confirme 455 lignes dans chaque export, 429 lignes inchangées et 26 modifiées ; les changements portent sur `pair_b` (25) et `pair_c` (3). Les témoins de paires simples ont 2 réparations sur 105. Le rapport source annonce 13 classes D5, 14 classes C5 orientées, une séparation chirale D5-06 → C5O-06/C5O-09, 455/560 combinaisons orientées couvertes par les triples D5, et un témoin U42 à 42 états qui vérifie les 560 triples orientés.

Une anomalie de migration a été détectée : le JSON détaillé de la branche source est tronqué et invalide. Il n'a pas été recopié comme rapport valide ; un résumé JSON distinct est conservé. Le script a été corrigé pour déposer son JSON détaillé dans `research/data/v19_c5/`, conformément au README. **La commande n'a pas été rejouée sur la tête actuelle de la PR** pendant cette opération.

Ce dossier ne redémontre pas le lemme général de localité V19, ne revendique aucune généralisation à d'autres q ou L, et reste expérimental. Originalité bibliographique : INDÉTERMINÉE ; Lean : NON RÉALISÉ.
