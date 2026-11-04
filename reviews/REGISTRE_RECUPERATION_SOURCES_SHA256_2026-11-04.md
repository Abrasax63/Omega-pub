# Registre de récupération des sources historiques — SHA-256

Date : 4 novembre 2026  
Dépôt : `Abrasax63/Omega-pub`  
Branche examinée : `migration/ravi2-ccs-public-2026-11-04`  
Base de comparaison : `RESEARCH_MEMORY.sqlite`, version 33, consultée en lecture seule.

## Contrôle de la base

- Taille : 819 200 octets.
- SHA-256 : `ef3e9a0de51a44b30599f73f027829751a2eb144e4468175c0f290b5e0159bf4`.
- `PRAGMA integrity_check` : `ok`.
- Violations de clés étrangères : 0.

## Sources originales matérialisées et empreintes calculées

| Source | Taille (octets) | SHA-256 calculé | Comparaison SQLite |
|---|---:|---|---|
| `rapport_spectre_defauts_iteration_1.md` | 15 772 | `89a12fb693e54d8ceb1b1a0ec27d8286a8525c8467681cd308f0759e31b63f7b` | Source `SRC-HIST-DELTA-SPECTRUM` retrouvée ; aucune empreinte de référence enregistrée dans la ligne source/evidence consultée. |
| `Adaptivity boundary - Mealy machines.docx` | 45 939 | `b6a8a334ba427e62a613b43687284afa2ab6ddc0cc08f69c9aaa1942c958e1f7` | **Concordance exacte** avec `SRC-COMMIT-MEALY` et les preuves des quatre cartes Mealy27. |
| `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` | 11 020 | `cfd9b3703b914930e802b940097a451885a1ff2ba89845cb0d749ba4fbe023e7` | **Concordance exacte** avec `SRC-COMMIT-V19` et les preuves SQLite de V19 concernées. |
| `NOTE_RANG_RECOLLEMENT_CONTEXTUEL_2026-09-30.md` | 9 128 | `ca90f76aa2ddb06032a53846347141fa7a102bf2ebdd8946d0ac2c9399d68833` | **Concordance exacte** avec `SRC-COMMIT-RQ4` et les preuves des deux cartes RQ-Q-4. |
| `AUDIT_V10.md` | 13 278 | `4c0f8c35db9e1acc3efe4e04541c4cb25ebf9c7713596423c81bc65dd5d01942` | Source `SRC-HIST-OBS-V10` retrouvée ; aucune empreinte de référence enregistrée dans la ligne source consultée. |
| `rapport_omega_o41_detection_apprise.pdf` | 178 235 | `8a17a828019c7da4f15adfeea8ea7bc0da26a6761156fba9365e751e759e4413` | Source `SRC-HIST-O41-REPORT` retrouvée ; aucune empreinte de référence enregistrée dans la ligne source consultée. |
| `rapport_omega_ac_v1_audit_o41.md` | 28 342 | `c70af91a00d1896a15f50a352d733a5b7f463849252dd4b3cebf09e0f98c2396` | Source `SRC-HIST-O41-AUDIT` retrouvée ; aucune empreinte de référence enregistrée dans la ligne source consultée. |
| `source_129.pdf` | 408 281 | `612819217a2929102a0e55c00cc4fb606b733d1f90dda513d42bf47783e0a92e` | **Concordance exacte** avec les empreintes `PRIMARY_PDF` SQLite des cartes OpenAI concernées. |
| `source_238.pdf` | 781 161 | `0a520da2d4a92a176e8833ef81fd1d4ecf19c117954c9606577f9d819be5d394` | **Concordance exacte** avec l'empreinte `PRIMARY_PDF` SQLite de la carte OpenAI concernée. |

## Conclusions vérifiables

1. Neuf fichiers sources historiques ont été matérialisés depuis la Library et leurs empreintes SHA-256 calculées.
2. Cinq comparaisons ont une empreinte de référence SQLite concordante : Mealy27, V19, RQ-Q-4, prépublication OpenAI 129 et prépublication OpenAI 238.
3. Pour quatre sources (Delta, V10 et les deux documents O41), la source est retrouvée et son empreinte calculée, mais SQLite ne fournit pas d'empreinte de référence comparable dans les enregistrements consultés. Il serait incorrect de qualifier ces cas de concordances.
4. Les références SQLite confirment les associations documentaires : Delta vers `SRC-HIST-DELTA-SPECTRUM), V8/V9 vers `SRC-HIST-OBS-V10), Ω-O4.1 vers ses deux sources, ainsi que les associations Mealy, V19, RQ-Q-4 et OpenAI.
5. Cette récupération concerne les **sources**, rapports et prépublications. Elle ne restaure pas les 32 fichiers Markdown individuels originaux des cartes manquantes.
6. Aucun calcul mathématique n'a été rejoué ici. Aucun statut scientifique n'a été modifié. SQLite v33 n'a pas été écrite. La branche `main` n'a pas été touchée et la PR #2 reste non fusionnée.

## Limite de portée

Les empreintes établissent l'identité binaire entre le fichier matérialisé et la valeur SHA-256 de référence lorsqu'elle existe dans SQLite. Elles ne prouvent ni la validité mathématique du contenu, ni la complétude de tous les artefacts associés, ni l'originalité scientifique des résultats.

