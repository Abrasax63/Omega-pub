# État de migration de la bibliothèque mathématique

**Version :** 0.1  
**Date :** 2026-11-04

Ce document distingue les fiches sources retrouvées dans la bibliothèque interne des dossiers dont les preuves primaires restent à retrouver et à examiner. Un résultat n'est pas considéré comme intégralement publié parce que son identifiant apparaît dans un résumé ou un snapshot.

## 1. Fiches transférées dans ce dépôt

| Identifiant | Sujet | Statut scientifique dans la source | Statut de publication ici | Limite actuelle |
|---|---|---|---|---|
| BR-R90-01 | Noyaux et période récurrente de Règle 90 | DÉMONTRÉ | EXPÉRIMENTAL | Audit détaillé source non transféré |
| BR-R90-02 | Uniformité Majority–Walsh | DÉMONTRÉ | EXPÉRIMENTAL | Audit détaillé source non transféré |

Les fiches transférées sont des transcriptions documentaires de fiches internes existantes. Aucune nouvelle preuve, compilation formelle ou exécution de code n'est revendiquée.

## 2. Résultats CL-DYN — sources retrouvées, cartes originales absentes

Les identifiants CL-DYN-01 à CL-DYN-04 apparaissent dans l'historique de recherche du 25 septembre 2026. Les fiches originales autonomes et leurs liaisons d'évidence n'ont pas été retrouvées dans les inventaires actuels.

Des sources mathématiques de contenu concordant sont toutefois récupérées dans un dossier séparé :
- rapport de spectres de défauts et scripts d'énumération ;
- notes de recollement et de stratégie de couverture ;
- témoins P2 sans P1 et P3 sans P2 ;
- correction du critère de finitude de τ portant sur l'unique cycle terminal effectivement atteint.

Le rapprochement des énoncés historiques avec ces sources reste documentaire et n'est pas une correspondance d'ID certifiée. Les statuts CORE/CERTIFIED rapportés dans l'historique ne sont pas réactivés. Aucun résultat CL-DYN n'est ajouté à l'index global comme fiche publiée.

Voir [réconciliation détaillée CL-DYN-01 à 04](defauts_recollement/RECONCILIATION_CL_DYN_01_04.md).

**Écart à auditer :** un ancien résumé mentionne 360 cas P3 sans P2 à N=5 ; le script source retrouvé et rejoué donne 240 spectres finis non vides. Le nombre 360 reste en quarantaine jusqu'à identification de sa définition ou de sa version de calcul.

## 3. Autres briques d'observation

CL-H-01, CL-OBSINF-01, CL-REFL-01 et CL-HO-01 sont signalées dans les états antérieurs comme briques du corpus. Leurs fiches primaires n'ont pas encore été réunies dans ce dépôt. Aucun transfert n'est effectué sur la seule base d'un résumé.

## 4. Quarantaines à préserver

Le manifeste de quarantaine du 15 octobre 2026 signale notamment des revendications historiques relatives au semi-groupe (H(T,\pi)), aux anciens résultats τ prédictifs et à certaines formulations sur les cycles décorés. Ces éléments sont marqués UNVERIFIED dans le manifeste documentaire. Ils ne doivent pas être réintroduits comme prémisses certifiées sans réaudit.

Les anciennes constructions Δτ_tr et les anciennes bornes τ mentionnées dans les décisions de recherche antérieures ne sont pas rétablies par cette migration.

## 5. Prochaine séquence de migration

1. Récupérer les sources primaires CL-DYN-01/02/03/04 et leurs éventuels certificats.
2. Contrôler la correction de formulation de CL-DYN-03.
3. Récupérer CL-H-01, CL-OBSINF-01, CL-REFL-01 et CL-HO-01.
4. Refaire l'index des dépendances et relier chaque fiche à son audit.
5. Migrer ensuite les dossiers expérimentaux C4 dans une zone explicitement expérimentale, sans promotion automatique.

## 6. Règle de clôture

Une migration documentaire ne vaut pas certification scientifique. Les statuts sont conservés depuis les fiches sources seulement lorsque celles-ci sont disponibles ; les résumés et snapshots servent à retrouver les sources, pas à les remplacer.
