# Réconciliation documentaire — CL-DYN et OBS-V8-FACT-INF

**Date :** 2026-11-04  
**Version :** 0.1  
**But :** distinguer les anciens identifiants CL-DYN des résultats d'observabilité temporelle retrouvés dans la base RAVI-2.

## Résultat de la vérification

Le manifeste actif RAVI-2 du 4 novembre 2026 contient `OBS-V8-FACT-INF`, `OBS-V9-RANK` et `OBS-V9-STAB-N1`. Il ne contient pas d'identifiants `CL-DYN-01` à `CL-DYN-04`.

Les sources documentaires retrouvées pour la factorisation sont :
- `NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md` : polynôme temporel, factorisation à horizon infini, preuve et contrôle exhaustif historique à N≤5 ;
- `NOTE_RECHERCHE_V8_FACTORIZATION_INFINITY.md` : énoncé détaillé et preuve de comptage ;
- `AUDIT_V11_V8_PREUVE_ET_NOUVEAUTE.md` : seconde preuve indépendante et audit bibliographique.

La correspondance certaine est donc : ces trois documents étayent `OBS-V8-FACT-INF`. Ils ne suffisent pas à établir que cette carte est identique à l'une des cartes historiques `CL-DYN-01..04`.

## Décision

1. `OBS-V8-FACT-INF` est migrée dans sa propre fiche, avec statut scientifique source DÉMONTRÉ, originalité externe INDÉTERMINÉE et publication EXPÉRIMENTAL.
2. Aucun identifiant CL-DYN n'est renommé, fusionné ou remplacé.
3. La correction historique de CL-DYN-03 (formulation relative à l'unique cycle finalement atteint) reste à préserver, mais la fiche source correspondante doit être retrouvée avant toute transcription.
4. Le script historique de vérification de V8 n'a pas été retrouvé dans les éléments consultés et n'est pas déclaré transféré ou réexécuté.
5. Les autres cartes V9 ne sont pas fusionnées avec V8 : leurs identifiants et leurs énoncés restent distincts dans le manifeste RAVI-2.

## Sources consultées

- `ACTIVE_RESULTS_MANIFEST_2026-11-04.csv` ;
- `ACTIVE_85_TO_CARDS_RECONCILIATION.csv` ;
- `NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md` ;
- `NOTE_RECHERCHE_V8_FACTORIZATION_INFINITY.md` ;
- `AUDIT_V11_V8_PREUVE_ET_NOUVEAUTE.md` ;
- `ETAT_RECHERCHE_REPRISE_RAVI2_2026-10-14_V1.md`.

## Verdict

**Correspondance CL-DYN ↔ OBS-V8 : INDÉTERMINÉE.**  
**Migration autonome de OBS-V8 : effectuée.**  
**Promotion ou modification des CL-DYN : aucune.**

## Complément de récupération des sources CL-DYN — 4 novembre 2026

Les énoncés historiques et des sources candidates ont maintenant été retrouvés. Les cartes originales CL-DYN ne sont toujours pas retrouvées comme fichiers autonomes et aucune correspondance exacte ID→fichier n'est certifiée. Voir le [dossier de réconciliation CL-DYN-01 à 04](../defauts_recollement/RECONCILIATION_CL_DYN_01_04.md) et ses [sources candidates](../defauts_recollement/README.md).

Les sources étayent séparément les définitions B, E_h, Δ_h, la périodicité ultime, le critère de cycle terminal et les deux contre-exemples P2↛P1 / P3↛P2. Elles ne créent aucun lien de dépendance avec OBS-V8.
