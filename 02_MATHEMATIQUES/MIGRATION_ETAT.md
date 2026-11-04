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

## 2. Résultats CL-DYN — récupération nécessaire

Les identifiants CL-DYN-01, CL-DYN-02, CL-DYN-03 et CL-DYN-04 apparaissent dans l'état de recherche antérieur comme résultats du noyau mathématique. Les éléments récupérés rappellent notamment que CL-DYN-03 doit conserver la formulation corrigée portant sur l'unique cycle finalement atteint.

Cependant, les fiches primaires complètes et leurs preuves n'ont pas été retrouvées dans les éléments examinés pour cette migration. Ils ne sont donc pas encore transférés comme résultats publiés.

**Action requise :** retrouver les fiches sources, reconstruire leur correspondance exacte avec les identifiants, puis vérifier définitions, hypothèses, preuves, contre-tests et dépendances avant transfert.

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
