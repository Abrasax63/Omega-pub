# Récupération historique des 32 résultats sans carte individuelle

Date : 4 novembre 2026  
Périmètre : bibliothèque privée RAVI-2 v33 et historique documentaire disponible.  
Branche de publication : `migration/ravi2-ccs-public-2026-11-04`.

## Verdict de récupération

Le contrôle direct de `RESEARCH_MEMORY.sqlite` v33 retrouve **32 enregistrements sur 32** pour les identifiants de l'inventaire des cartes manquantes. Les lignes contiennent les champs scientifiques structurés de la table `results` : identifiant, titre, énoncé, domaine, hypothèses, statut épistémique, originalité et version. Les preuves associées sont dans `evidence`, et l'historique des changements dans `events` et `result_versions`.

Répartition des statuts enregistrés : **26 DÉMONTRÉ**, **6 CALCUL EXACT**. Il s'agit des statuts inscrits dans la base, pas d'une nouvelle validation scientifique.

Cela corrige une ambiguïté importante de l'inventaire précédent : les 32 résultats ne sont pas absents de la mémoire scientifique SQLite. Ce qui manque est leur **fichier Markdown individuel d'origine**. La base SQLite n'est pas un substitut à ces fichiers et ne contient pas leur mise en page ni leur intégralité documentaire.

## Versions historiques retrouvées

Trois résultats V19 possèdent plusieurs lignes dans `result_versions`, avec les versions précédentes conservées :

- `OBS-V19-C5-13` : v1 `BASELINE-PRE-COMMIT`, v2 `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM`, v3 `COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04` (active).
- `OBS-V19-PAIR-COMPLETE14` : v1 `COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04`, v2 `COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05` (active).
- `OBS-V19-TRIPLE-COMPLETE13` : v1 `COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04`, v2 `COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05` (active).

Ces objets sont des versions de lignes de résultats SQLite (`row_json`), pas des versions de fichiers Markdown. Elles permettent de retracer l'évolution des énoncés enregistrés, sans prétendre restituer un document original absent.

## Registre de provenance des 32 identifiants

| Identifiants | Commit / état d'origine enregistré | Source ou preuve référencée |
|---|---|---|
| `DELTA-P3-N5`, `DELTA-SPECTRUM-CLASS` | `BASELINE-PRE-COMMIT` | Alias historique `SRC-HIST-DELTA-SPECTRUM` ; `rapport_spectre_defauts_iteration_1.md`. Références historiques datées du 21 août et du 17 septembre 2026. |
| `OBS-V8-FACT-INF`, `OBS-V9-RANK`, `OBS-V9-STAB-N1` | `BASELINE-PRE-COMMIT` | Alias `SRC-HIST-OBS-V10` ; `AUDIT_V10.md` et sources historiques associées. |
| `OMEGA-O41-DET-V11` | `BASELINE-PRE-COMMIT` | Alias `SRC-HIST-O41-REPORT` et `SRC-HIST-O41-AUDIT` ; rapport O41 et audit Ω-AC v1.1. |
| `DESC-SUM-01` | `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM` | `detection_correlations_2026-10-14.md`, `COMMIT_AUDIT_RAVI2_2026-10-14.md`, checker Python et sortie JSON. |
| `OBS-M27-BINARY`, `OBS-M27-CONFLICT`, `OBS-M27-FERTILE`, `OBS-M27-SPECTRUM` | `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM` | `Adaptivity boundary - Mealy machines.docx`, audit du commit, checker et sortie JSON. |
| `Q-RQ4-COMMON-RANK`, `Q-RQ4-PAULI-ROBUST` | `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM` | `NOTE_RANG_RECOLLEMENT_CONTEXTUEL_2026-09-30.md`, audit du commit, checker et sortie JSON. |
| `EXT-OAI-MARG-REPAIR`, `EXT-OAI-MATCH-RANK`, `EXT-OAI-REL-SELECT` | `COMMIT-RAVI2-2026-10-15-OAI-BRICKS-01` | `EXTRACTION_BRIQUES_OPENAI_2026-10-15.md` ; sources PDF primaires 238 et 129. |
| `APP-OBS-SPARSE-DISJOINT`, `EXT-OAI-MATCH-CORNER`, `EXT-OAI-REL-CORNER`, `EXT-OAI-UNIT-LIFT` | `COMMIT-RAVI2-2026-10-15-OAI-DECOMPOSE-03` | `DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md` ; source primaire externe pour la sparsification. |
| `OBS-RESTRICT-COUNT`, `OBS-RESTRICT-GREEDY` | `COMMIT-RAVI2-2026-10-15-OBS-RESTRICTIONS-02` | `CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md` et archive de preuves multiagent. |
| `OBS-RESTRICT-OVERLAP`, `OBS-RESTRICT-PROFILE` | `COMMIT-RAVI2-2026-10-15-SYNTHESIS-09` | `TEST_SYNTHESE_INVERSE_2026-10-15.md` et archive de preuves associée. |
| `OBS-V19-C5-13`, `OBS-V19-C5-ORIENTED14`, `OBS-V19-PAIR-COMPLETE14`, `OBS-V19-TRIPLE-COMPLETE13` | `COMMIT-RAVI2-2026-10-15-V19-ASSEMBLY-04` (avec versions ultérieures indiquées plus haut) | `V19_ASSEMBLAGE_ORIENTE_2026-10-15.md`, `v19_assembly_exact.py`, CSV de classes et témoins. |
| `OBS-V19-PAIR-COMPLETE14`, `OBS-V19-TRIPLE-COMPLETE13`, `OBS-V19-UNIVERSAL10` | `COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05` (version active des deux premiers ; création du troisième) | `V19_MULTIPLICITE_CAPACITE_2026-10-15.md`, `v19_multiplicity_capacity.py`, CSV/JSON de témoins. |
| `OBS-V19-FORCED-P4`, `OBS-V19-LOCAL-L2` | `COMMIT-RAVI2-2026-10-14-V19-RQ4-MEALY-SUM` | `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md`, audit du commit, checker et sortie JSON. |
| `OBS-V19-GAMMA-CONNECTED` | `BASELINE-PRE-COMMIT` | Alias historique `SRC-HIST-OBS-V19-24` ; note de grammaire V19 associée. |

## Limites de récupération

1. Les alias `SRC-HIST-*` sont des identifiants de provenance historiques ; ils ne donnent pas à eux seuls un chemin de fichier récupérable.
2. Les commits listés sont des identifiants de commits scientifiques internes à la base RAVI-2. Ils ne sont pas des commits GitHub du dépôt public `Omega-pub`.
3. La recherche de conversations historiques n'a pas fourni de transcription brute exploitable ni d'identifiant de message permettant de reconstituer les fichiers originaux. Les historiques accessibles confirment certains sujets et dates, mais ne constituent pas les cartes elles-mêmes.
4. Les rapports, PDF, DOCX, scripts et sorties cités sont des preuves ou sources associées ; ils ne sont pas renommés ni découpés en cartes.
5. Aucune carte Markdown n'est recréée dans ce travail. Aucune ligne SQLite, aucun statut et aucune preuve scientifique ne sont modifiés.

## Contrôles effectués

- Lecture de la base SQLite v33 matérialisée depuis la bibliothèque ; requêtes en lecture seule sur `results`, `evidence`, `events`, `result_versions` et `historical_claims`.
- 32 identifiants ciblés : 32 lignes présentes dans `results`.
- 26 lignes au statut enregistré `DÉMONTRÉ`, 6 au statut `CALCUL EXACT`.
- Trois historiques multi-versions identifiés pour les résultats V19 cités ci-dessus.
- Aucun test mathématique ou de régression rejoué dans cette récupération documentaire.

## Conclusion opérationnelle

L'inventaire doit désormais distinguer deux états : **résultat structuré récupéré dans SQLite** et **carte Markdown originale non retrouvée**. Les 32 résultats sont conservés comme enregistrements structurés ; leurs documents autonomes ne sont pas déclarés restaurés. Une récupération fidèle des fichiers originaux nécessiterait les exports de fichiers ou transcriptions brutes qui ne sont pas actuellement accessibles dans les sources examinées.
