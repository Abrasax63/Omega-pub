# Registre transversal des résultats

**Version :** 0.2  
**Date :** 2026-11-04  
**Périmètre :** fiches de résultats effectivement présentes dans le dépôt public.

Ce registre est une vue transversale de navigation. Il ne remplace pas les fiches sources et ne constitue pas une validation scientifique supplémentaire.

## Comment retrouver une brique

Sur GitHub, utilisez la recherche du navigateur (Rechercher dans la page) avec :
- l'identifiant exact, par exemple `BR-R90-01` ;
- un domaine, par exemple `Règle 90`, `observation`, `SAT` ;
- un statut, par exemple `EXPÉRIMENTAL`, `DÉMONTRÉ` ou `INDÉTERMINÉ` ;
- un mot-clé de l'énoncé.

Pour les recherches dans tout le dépôt, utilisez la recherche GitHub avec l'identifiant ou le mot-clé souhaité.

## Registre des fiches présentes

| ID | Domaine | Mots-clés | Énoncé court | Statut scientifique source | Publication | Version | Preuve / audit | Dépendances | Fiche |
|---|---|---|---|---|---|---|---|---|---|
| BR-R90-01 | Mathématiques · Règle 90 | noyau, rang, transitoire, période, corps fini | Dimension du noyau de (A_N^t), rang et période maximale récurrente pour (N=2^a m), (m) impair | DÉMONTRÉ (fiche interne) | EXPÉRIMENTAL | 0.1 | Audit source cité, non encore transféré intégralement : `AUDIT_TEMPS_REGLE90_2026-08-22.md`, sections 2 et 4 | Aucune dépendance formelle déclarée | [Ouvrir la fiche](../02_MATHEMATIQUES/temps_regle90/BR-R90-01_NOYAUX_PERIODES.md) |
| BR-R90-02 | Mathématiques · Règle 90 / observation | Majority, Walsh, Fourier, uniformité, entropie | Uniformité exacte du mot observé (W_h) si (N\geq 2h+3) | DÉMONTRÉ (fiche interne) | EXPÉRIMENTAL | 0.1 | Audit source cité, non encore transféré intégralement : `AUDIT_TEMPS_REGLE90_2026-08-22.md`, section 3 | Aucune dépendance formelle déclarée | [Ouvrir la fiche](../02_MATHEMATIQUES/temps_regle90/BR-R90-02_MAJORITY_WALSH.md) |
| PILOTE-EXT-C4-L2-2026-11-04 | Mathématiques · observation binaire / V19 | C4, L=2, huit classes, témoin 9 états, petit modèle | Réalisation simultanée des classes C4O-00…07 et minimalité N=9 sous V19(2) | CALCUL EXACT (périmètre spécifié) | EXPÉRIMENTAL | 0.2 | Deux vérificateurs globaux, un local ; raccord primaire et audit de quotients joints | Dépendances documentées dans le dossier, pas de transfert général | [Ouvrir le dossier](../02_MATHEMATIQUES/defauts_recollement/PILOTE_EXTRACTION_C4_L2_2026-11-04.md) |

## Lecture des statuts

- **Statut scientifique source** : statut rapporté par la fiche interne ou par son dossier de validation. Il n'est pas réévalué par la présence dans ce registre.
- **Statut de publication** : niveau de complétude et de disponibilité du dossier dans ce dépôt.
- **Preuve / audit** : indique où se trouvent les éléments justificatifs et s'ils sont effectivement accessibles dans le dépôt.
- **Dépendances** : seules les dépendances formellement déclarées dans la fiche sont reprises. « Aucune déclarée » ne signifie pas qu'aucune dépendance mathématique implicite n'existe.

## Éléments en attente de migration — non comptés comme fiches publiques

Cette section sert de liste de travail, pas de registre de résultats publiés.

| Identifiants / dossier | Domaine | État documentaire | Condition avant inscription comme fiche |
|---|---|---|---|
| CL-DYN-01 à CL-DYN-04 | Mathématiques · dynamique | Fiches primaires et preuves non encore réunies dans le dépôt | Retrouver les sources, vérifier énoncés, hypothèses, preuves, contre-tests et dépendances |
| CL-H-01, CL-OBSINF-01, CL-REFL-01, CL-HO-01 | Mathématiques · observation | Fiches primaires non encore réunies dans le dépôt | Même contrôle source, sans reconstruire les preuves depuis un résumé |
| Autres dossiers C4 (hors pilote C4, L=2) | Mathématiques · catalogue expérimental | Le pilote C4, L=2 est documenté séparément ; les autres dossiers restent à inventorier | Définition exécutable, rapport de calcul, certificat de coexistence ou d'incompatibilité et statut précis |
| SAT / #SAT / P-NP | Informatique théorique | Travaux non recensés ici comme résultats certifiés | Énoncés précis, réductions, preuves ou certificats, contre-tests et revue bibliographique |

Pour le détail des travaux mathématiques en attente, voir [l'état de migration](../02_MATHEMATIQUES/MIGRATION_ETAT.md). Les éléments de cette section ne doivent pas être interprétés comme des résultats validés ou même comme des fiches publiques existantes.

## Règle de mise à jour

À chaque ajout, retrait ou changement substantiel d'une fiche :
1. mettre à jour la fiche source en premier ;
2. vérifier son ID, sa version et ses deux statuts ;
3. renseigner les mots-clés, l'accès à la preuve et les dépendances ;
4. mettre à jour ce registre et l'[index global](INDEX_GLOBAL.md) dans le même changement documentaire ;
5. conserver l'historique et expliquer toute modification de statut.

Le registre doit rester dérivé des fiches : aucune affirmation ne doit apparaître ici sans source correspondante.

## Historique

- 0.1 — Création du registre transversal à partir des deux fiches BR-R90 effectivement présentes dans le dépôt. Les dossiers non migrés sont isolés dans une liste d'attente documentaire.\n- 0.2 — Ajout du pilote C4, L=2 avec statut scientifique CALCUL EXACT limité au contrat V19(2), et statut de publication EXPÉRIMENTAL.
