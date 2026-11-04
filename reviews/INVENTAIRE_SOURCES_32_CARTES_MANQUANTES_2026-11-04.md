# Inventaire des sources — 32 cartes individuelles encore manquantes

Date : 4 novembre 2026  
Base de référence : SQLite v33, SHA-256 `ef3e9a0de51a44b30599f73f027829751a2eb144e4468175c0f290b5e0159bf4`  
Branche : `migration/ravi2-ccs-public-2026-11-04`

## Objet et méthode

Cet inventaire prolonge la réconciliation des 42 résultats sans carte individuelle. Dix cartes originales ont maintenant été retrouvées et restaurées ; les 32 identifiants ci-dessous restent sans fichier individuel restaurable.

Contrôles effectués :
- inventaire paginé de la bibliothèque privée : 1 440 fichiers, huit pages, sans curseur restant ;
- recherche des noms/identifiants de cartes sur l'ensemble des fichiers ;
- inspection des archives de preuves pertinentes et de leurs membres ;
- lecture des documents de provenance cités par SQLite ;
- comparaison exacte des cartes restaurées avec les enregistrements SQLite lorsqu'une carte originale a été retrouvée.

**Règle de classement :** un rapport de preuve, un audit, un script, un PDF primaire, un jeu de données ou une note de recherche n'est pas une carte individuelle. Même lorsqu'un rapport contient un énoncé complet ou une section intitulée « carte », il n'est pas transformé automatiquement en fichier de carte. Aucune fiche n'est reconstruite de mémoire ou à partir d'un résumé.

## Résultat de la recherche

La recherche par nom dans les 1 440 fichiers ne retrouve aucun fichier individuel portant l'un des 32 identifiants restants. Les documents ci-dessous sont des sources et preuves disponibles, pas des cartes restaurées.

| Identifiants | Sources retrouvées | Nature de la source / limite |
|---|---|---|
| `APP-OBS-SPARSE-DISJOINT` | `DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md` ; Dell–Husfeldt–Wahlén, ECCC TR10-078 (2010) | Rapport d'application et source théorique externe ; pas de fichier de carte individuel. La preuve globale de sparsification est importée, non reconstruite intégralement. |
| `DELTA-P3-N5`, `DELTA-SPECTRUM-CLASS` | `rapport_spectre_defauts_iteration_1.md` ; note ultérieure `BINARY_SPECTRA_RESEARCH_2026-10-21.md` | Rapport historique contenant les démonstrations/calculs et une recherche ultérieure distincte sur deux états observables ; aucun fichier individuel de carte retrouvé. Ne pas confondre les périmètres. |
| `DESC-SUM-01` | `detection_correlations_2026-10-14.md` ; `COMMIT_AUDIT_RAVI2_2026-10-14.md` ; `commit_audit_checks.py` ; `commit_audit_checks.json` | Preuve source, audit et vérification calculatoire ; pas de carte autonome. |
| `EXT-OAI-MARG-REPAIR`, `EXT-OAI-MATCH-RANK`, `EXT-OAI-REL-SELECT` | `EXTRACTION_BRIQUES_OPENAI_2026-10-15.md` ; `source_129.pdf` ; `source_238.pdf` | Rapport d'extraction avec sections de cartes et prépublications primaires ; pas de fichiers de cartes individuelles. |
| `EXT-OAI-MATCH-CORNER`, `EXT-OAI-REL-CORNER`, `EXT-OAI-UNIT-LIFT` | `DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md` ; prépublication OpenAI famille 129 | Rapport de décomposition avec énoncés et preuves reconstruites ; pas de fichiers de cartes individuelles. |
| `OBS-M27-BINARY`, `OBS-M27-CONFLICT`, `OBS-M27-FERTILE`, `OBS-M27-SPECTRUM` | `Adaptivity boundary - Mealy machines.docx` ; `COMMIT_AUDIT_RAVI2_2026-10-14.md` ; `commit_audit_checks.py` ; `commit_audit_checks.json` | Manuscrit source, audit, code et sorties. Aucun fichier individuel de carte trouvé. |
| `OBS-RESTRICT-COUNT`, `OBS-RESTRICT-GREEDY` | `CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md` ; archive `PREUVES_MULTIAGENT_OBSERVABILITE_2026-10-15.zip` | Rapport de transfert et archive de preuves/scripts/Lean ; l'archive ne contient pas de fichiers de cartes individuelles pour ces identifiants. |
| `OBS-RESTRICT-OVERLAP`, `OBS-RESTRICT-PROFILE` | `TEST_SYNTHESE_INVERSE_2026-10-15.md` ; archive `PREUVES_SYNTHESE_INVERSE_2026-10-15.zip` | Rapport et archive de preuves/contre-exemples ; pas de fichiers de cartes individuelles. |
| `OBS-V19-C5-13`, `OBS-V19-C5-ORIENTED14`, `OBS-V19-FORCED-P4`, `OBS-V19-GAMMA-CONNECTED`, `OBS-V19-LOCAL-L2`, `OBS-V19-PAIR-COMPLETE14`, `OBS-V19-TRIPLE-COMPLETE13`, `OBS-V19-UNIVERSAL10` | `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE.md` et variantes ; `V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` ; `V19_MULTIPLICITE_CAPACITE_2026-10-15.md` ; `COMMIT_AUDIT_RAVI2_2026-10-14.md) ; scripts et CSV/JSON exacts associés | Notes de recherche, rapports d'audit, checkers et données exactes ; aucun fichier individuel de carte retrouvé pour ces huit identifiants. |
| `OBS-V8-FACT-INF`, `OBS-V9-RANK`, `OBS-V9-STAB-N1` | `AUDIT_V10.md` ; source historique associée | Audit historique consultable ; la preuve source est référencée, mais aucun fichier individuel de carte n'a été retrouvé. |
| `OMEGA-O41-DET-V11` | `rapport_omega_o41_detection_apprise.pdf` ; `rapport_omega_ac_v1_audit_o41.md` ; audit PDF associé | Rapport scientifique et audit Ω-AC ; aucun fichier individuel de carte retrouvé. Le statut demeure celui enregistré dans SQLite. |
| `Q-RQ4-COMMON-RANK`, `Q-RQ4-PAULI-ROBUST` | `NOTE_RANG_RECOLLEMENT_CONTEXTUEL_2026-09-30.md` ; `COMMIT_AUDIT_RAVI2_2026-10-14.md` ; `commit_audit_checks.py` ; `commit_audit_checks.json` | Note technique, audit et contrôles exacts ; pas de fichiers individuels de cartes. |

## Archives de preuves examinées

Les archives pertinentes ouvertes incluent notamment :
- `PREUVES_AFFINE_GROUP_CORE_2026-10-15.zip`
- `PREUVES_COMPOSITION_AFFINE_2026-10-15.zip`
- `PREUVES_DECOMPOSITION_LOT2_2026-10-15.zip`
- `PREUVES_MEALY_HELLY_2026-10-16.zip`
- `PREUVES_MULTIAGENT_OBSERVABILITE_2026-10-15.zip`
- `PREUVES_SYNTHESE_INVERSE_2026-10-15.zip`
- `PREUVES_TRANSFERT_AFFINE_V19_2026-10-15.zip`
- `PREUVES_V19_N11_MOMENTS_2026-10-15.zip`
- `PREUVES_V19_TROISIEME_ORDRE_2026-10-15.zip)
- archives historiques Delta_h, V8/V9, V12–V19 et archives de vérification quantique pertinentes.

Une carte originale supplémentaire a été retrouvée à la fois dans la bibliothèque racine et dans l'archive `PREUVES_V19_TROISIEME_ORDRE_2026-10-15.zip) : `OBS-RESTRICT-MULTIMOMENT_BRIQUE.md`. Les deux copies sont identiques octet pour octet (SHA-256 `48b9861443ad2864e836d7a3ab0b968bcd48e5a709e11d4d95cc7060862907f9`) et correspondent à SQLite v33. Elle a été restaurée dans la branche.

Les autres membres de ces archives sont des rapports, scripts, données, certificats ou cartes déjà restaurées. Ils ne justifient pas de créer de nouvelles cartes individuelles.

## État et prochaine opération

- Reliquat initial : 42 résultats.
- Cartes originales restaurées : 10.
- Cartes individuelles restantes : 32.
- Sources et preuves : retrouvées pour plusieurs groupes, mais elles ne remplacent pas les cartes individuelles.
- Aucun changement de statut scientifique ; aucun recalcul ni test rejoué.
- SQLite v33 reste inchangée ; PR #2 reste en brouillon et non fusionnée.

La prochaine action admissible est de retrouver une carte originale non encore identifiée, ou de documenter explicitement l'indisponibilité de sa carte individuelle. Une extraction d'énoncé depuis un rapport ne sera pas présentée comme restauration d'un original.
