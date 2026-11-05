# Index global des résultats

**Version de l'index :** 0.3  
**Dernière mise à jour :** 2026-11-05  
**Rôle :** inventaire des résultats effectivement documentés dans Omega-pub.

## Navigation

- [Guide de lecture](GUIDE_LECTURE.md) — parcours lecteur, vérificateur et contributeur.
- [Registre transversal](REGISTRE_TRANSVERSAL.md) — recherche par identifiant, domaine, mots-clés, statut, preuve et dépendances.
- [Référentiel des statuts](STATUTS.md) — définitions des statuts.

## Règle de lecture

Une ligne n'est ajoutée que lorsqu'une fiche dédiée existe dans le dépôt. Le statut scientifique est repris de la fiche source ; le statut de publication décrit la complétude du dossier public. Ces deux statuts ne sont pas interchangeables.

## Fiches de résultats présentes dans ce dépôt

| ID | Domaine | Énoncé / titre | Version | Statut scientifique source | Statut de publication | Fiche |
|---|---|---|---|---|---|---|
| BR-R90-01 | Mathématiques / Règle 90 | Noyaux et période récurrente | 0.1 | DÉMONTRÉ (fiche interne) | EXPÉRIMENTAL — audit détaillé à joindre | [Fiche](../02_MATHEMATIQUES/temps_regle90/BR-R90-01_NOYAUX_PERIODES.md) |
| BR-R90-02 | Mathématiques / Règle 90 | Uniformité Majority–Walsh avant repliement cyclique | 0.1 | DÉMONTRÉ (fiche interne) | EXPÉRIMENTAL — audit détaillé à joindre | [Fiche](../02_MATHEMATIQUES/temps_regle90/BR-R90-02_MAJORITY_WALSH.md) |
| PILOTE-EXT-C4-L2-2026-11-04 | Mathématiques / observation binaire | Témoin global à 9 états et minimalité pour C4O-00…07 sous V19(2) | 0.2 | CALCUL EXACT (périmètre V19(2), C4, L=2) | EXPÉRIMENTAL — revue tierce et Lean non réalisés | [Dossier](../02_MATHEMATIQUES/defauts_recollement/PILOTE_EXTRACTION_C4_L2_2026-11-04.md) |

## Résultats non encore migrés

Les fiches originales CL-DYN-01/02/03/04 restent non migrées, bien que des sources candidates aient été retrouvées ; voir la [réconciliation CL-DYN](../02_MATHEMATIQUES/defauts_recollement/RECONCILIATION_CL_DYN_01_04.md). CL-H-01, CL-OBSINF-01, CL-REFL-01 et CL-HO-01 restent à récupérer depuis leurs fiches primaires. Voir aussi [l'état de migration mathématique](../02_MATHEMATIQUES/MIGRATION_ETAT.md).

Le pilote C4, L=2 est désormais inventorié comme calcul exact dans son périmètre V19(2), avec statut de publication EXPÉRIMENTAL ; il n'est pas présenté comme certification tierce ou formalisation Lean. Les autres dossiers C4 et les travaux SAT ne sont pas déclarés certifiés.

## Dépendances

Les dépendances seront renseignées dans chaque fiche et reportées ici lorsqu'une vue transversale est utile. Une dépendance non vérifiée doit rester explicitement signalée.

## Historique

- 0.1 — Création de l'index ; aucun résultat scientifique n'était déclaré.
- 0.2 — Ajout de deux fiches source BR-R90-01 et BR-R90-02, publiées à titre expérimental faute de transfert de leurs audits détaillés.
- 0.3 — Ajout du pilote C4, L=2 comme CALCUL EXACT sous V19(2), publication EXPÉRIMENTALE.
