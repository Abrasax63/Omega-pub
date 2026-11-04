# RAVI-2 — statut des scripts et précautions d'exécution

Ce dossier contient des artefacts historiques de vérification, de calcul et de commit scientifique. **Le contenu de ce dossier n'est pas un ensemble homogène de scripts autonomes à exécuter tel quel.**

## Classification issue de l'audit de migration du 4 novembre 2026

### Scripts historiques qui écrivent dans SQLite

Les dix scripts suivants contiennent des opérations d'écriture SQLite (transactions, INSERT/UPDATE, commit, copie de sauvegarde ou restauration). Ils ont été écrits pour des environnements de travail historiques sous `/mnt/data`, avec des fichiers d'entrée et des bases locales qui ne sont pas fournis dans ce dépôt :

- `checks/audit_v19_min_obstruction_spectrum_2026-10-19.py`
- `checks/commit_q_predictive_hidden_20261020.py`
- `commit_acc_state_20261020.py`
- `commit_affine_gauge_core_bridge.py`
- `commit_affine_tree_core_bridge.py`
- `commit_catchup_20261019.py`
- `commit_mealy_helly_bridge.py`
- `commit_single_gap_complexity_20261019.py`
- `commit_time_predictive_20261019.py`
- `commit_two_gap_20261020.py`

**Ne pas les lancer sur une base de travail ou sur une copie unique de la base.** Ils peuvent créer une sauvegarde puis modifier une base SQLite présente au chemin attendu. Les fichiers `RESEARCH_MEMORY.sqlite` et les autres bases privées ne sont pas inclus dans ce dépôt. La présence de ces scripts ne signifie pas que leur exécution est nécessaire pour lire ou reproduire les résultats publiés.

Pour une réutilisation, travailler sur une copie jetable, vérifier chaque chemin et chaque opération SQL, puis contrôler l'intégrité et les clés étrangères. Ces scripts ne sont pas des migrations génériques ni des outils de mise à jour supportés.

### Contrôles dépendants d'un environnement historique

Les trois scripts suivants écrivent leurs sorties dans des chemins fixes sous `/mnt/data` et supposent la présence d'artefacts externes au dépôt :

- `checks/check_q_predictive_hidden.py`
- `checks/single_gap_factor_complexity_checks_2026-10-19.py`
- `checks/time_predictive_checks_2026-10-19.py`

Ils ne sont pas autonomes dans un clone propre sans adaptation des chemins et récupération des entrées historiques.

### Contrôle à sortie locale

`commit_audit_checks.py` effectue des vérifications finies et écrit `commit_audit_checks.json` dans le répertoire courant. Il ne met pas à jour SQLite. Son périmètre est celui explicitement indiqué dans le JSON et le code ; il ne constitue pas une validation globale de RAVI-2.

## Distinction des artefacts

- Les fichiers JSON de résultats sont des sorties ou des contrôles archivés ; leur présence ne prouve pas qu'ils ont été régénérés depuis le clone public.
- Les scripts nommés `commit_*.py` sont des scripts historiques de commit de la base, pas des scripts de reproduction à lancer automatiquement.
- Les contrôles V19 C5–L=3 qui sont autonomes et intégrés au workflow GitHub sont documentés dans `research/data/v19_c5/README.md` et `research/code/audit_v19_c5_independent_2026-11-04.py`. Ce workflow n'exécute aucun des scripts historiques ci-dessus.
- Les 62 tests enregistrés `PASS` dans SQLite v33 ne sont pas tous rejoués par cette migration.

## Limites de cet inventaire

La classification est une inspection statique des chemins, opérations SQLite et écritures de fichiers dans les scripts présents. Elle ne constitue pas une analyse dynamique de tous les scripts, ni un audit mathématique des résultats. Aucun script de commit n'a été exécuté pendant cette revue.
