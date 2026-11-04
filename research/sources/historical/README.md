# Sources historiques restaurées — RAVI-2 / observabilité

Date de restauration : 4 novembre 2026.
Branche : `migration/ravi2-ccs-public-2026-11-04`.

## V8 / V9 — audit historique V10

- [`AUDIT_V10.md`](AUDIT_V10.md) est une copie textuelle du document historique retrouvé dans la bibliothèque.
- Il contient la reconstruction indépendante de V8, le comptage des facteurs de fibres et des cycles, les vérifications finies rapportées et les réserves de nouveauté.
- **Ce document est une source de preuve/audit pour V8, pas la carte originale V8.** La carte Markdown autonome originale n'a pas été retrouvée dans les arbres GitHub inspectés. La fiche `OBS-V8-FACT-INF_RECONSTITUTION.md` reste donc explicitement une reconstitution.

## Ω-O4.1 / V11

- [Rapport O4.1 — extraction textuelle](OMEGA_O41_REPORT_EXTRACTED.txt)
- [Audit contradictoire Ω-AC v1.1 — extraction textuelle](OMEGA_AC_AUDIT_EXTRACTED.txt)

Les deux originaux sont des PDF présents dans la bibliothèque privée. Les fichiers de ce dépôt sont des extractions textuelles, pas les PDF binaires. Le rapport O4.1 distingue le résultat mathématique dans un modèle fini de ses hypothèses structurelles ; l'audit Ω-AC conclut `SURVÉCU_AUDIT`, et précise que cela ne vaut ni vérification formelle ni validation indépendante.

## Identifiants CL-DYN-01 à CL-DYN-04

Recherche exacte menée dans :
- `MEMORY_INDEX.md` ;
- `INDEX_BRIQUES.md` ;
- `ACTIVE_RESULTS_MANIFEST_2026-11-04.csv` ;
- l'arbre de la branche source privée `migration/bibliotheque-ravi2-2026-11-03` ;
- l'arbre de la branche publique `migration/ravi2-ccs-public-2026-11-04`.

Aucune occurrence des identifiants `CL-DYN-01` à `CL-DYN-04` ni aucun fichier correspondant n'a été trouvé dans ces périmètres. Verdict documentaire : **NON RETROUVÉS / INDÉTERMINÉ**, et non « inexistants ». Aucune correspondance avec V8, V9 ou une autre brique n'est inférée.

## CCS — limite de vérification

Le script `ccs_audit_v10.py` est présent dans les deux dépôts avec un contenu identique. Il annonce explicitement `lean_status=NOT_EXECUTED` et `translation_status=NOT_CERTIFIED`. Le contrôle fini Python ne doit pas être présenté comme une compilation Lean ou une certification générale.

## Intégrité de la migration

- Aucune écriture dans SQLite v33.
- Aucun statut scientifique promu ou modifié.
- Aucun changement sur `main`.
- Ces restaurations sont documentaires et restent sur la branche de migration.
