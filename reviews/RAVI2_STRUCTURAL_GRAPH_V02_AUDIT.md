# RAVI-2 Structural Graph v0.2 — audit du prototype

Date : 19 octobre 2026

## Verdict

**Prototype construit et test structurel PASS.** Il s'agit d'une couche de découverte **non certifiante**. Aucun résultat scientifique, statut, relation `DEPEND_DE` ou contenu de `RESEARCH_MEMORY.sqlite` n'a été modifié.

## Source

- Source scientifique lue : `RESEARCH_MEMORY.sqlite`.
- Résultats admissibles analysés : **79**.
- SHA256 avant : `087e1ef5be0f2768d9685062b26430928b832822fa400ac259d8184f559baf85`.
- SHA256 après : `087e1ef5be0f2768d9685062b26430928b832822fa400ac259d8184f559baf85`.
- Source inchangée : **TRUE**.
- Ouverture SQLite de la source en mode `ro`.

## Architecture v0.2 effectivement créée

Le graphe expérimental sépare :

- `source_results` : copie en lecture de l'état admissible utilisé pour l'expérience ;
- `atoms` : vocabulaire structurel typé ;
- `result_atoms` : liens résultat→atome avec base d'extraction ;
- `signatures` : signatures typées par résultat ;
- `structural_edges` : rapprochements de triage pondérés ;
- `attractors` / `attractor_members` : motifs structurels récurrents ;
- `benchmark_runs` : tests reproductibles du moteur.

Tous les objets de découverte portent la politique : `TRIAGE_ONLY`. Ils ne constituent ni théorèmes, ni dépendances, ni prémisses scientifiques.

## Contrôles exécutés

- `PRAGMA integrity_check = ok`.
- `foreign_key_check` : 0 erreur.
- **79/79** résultats ont une signature.
- **44** types d'atomes structurels.
- **717** liens résultat→atome.
- **505** arêtes de triage après seuil structurel.
- **89** attracteurs récurrents (support >=4, >=2 projets).
- Le moteur ne contient aucune règle d'extraction spéciale fondée sur un identifiant de résultat ou de projet. Les trois identifiants du benchmark sont utilisés uniquement **après** construction pour inspecter la sortie.

## Benchmark Δ_h / Mealy / V19

Cibles inspectées après génération :

- `DELTA-SPECTRUM-CLASS` ;
- `BR-MEALY-HELLY-01` ;
- `OBS-V19-FIRST-OBSTRUCTION11`.

Atomes structurels communs détectés : `classification_boundary, observe_project, obstruction_failure`.

Le motif le plus informatif commun aux trois est l'attracteur `AT-ea13ee159c900dc2` :

- atomes : `["classification_boundary", "obstruction_failure"]` ;
- support : **11** résultats ;
- projets : **3** ;
- rang global parmi les attracteurs : 7e dans ce run.

Il relie notamment Δ_h, Mealy et V19 sans codage spécifique de ces familles dans l'extracteur. Le benchmark est donc **PASS au niveau de récupération structurelle**. Cela ne démontre pas encore une abstraction mathématique commune : le prochain verrou est de formaliser une interface commune et de chercher un théorème non tautologique ou un contre-exemple.

### Membres de l'attracteur principal

- `DELTA-SPECTRUM-CLASS` — DELTA_H_FERMETURE — Classification complète des spectres de défauts Δ_h
- `BR-AFFINE-GAUGE-CORE` — OBSERVABILITE — Diagnostic de translation commune ou noyau minimal d'étiquettes
- `BR-MEALY-HELLY-01` — OBSERVABILITE — Borne de Helly du nerf de compatibilité des résolveurs Mealy
- `BR-OBS-BAD-01` — OBSERVABILITE — Signature affine canonique des mauvais objets
- `BR-OBS-CAP-02` — OBSERVABILITE — Capacité de support et poids des circuits
- `OBS-M27-CONFLICT` — OBSERVABILITE — Mealy27 — noyaux de conflit bornés
- `OBS-RESTRICT-FORCED-QUOTIENT` — OBSERVABILITE — Révélation sous oppositions forcées : quotient affine pondéré et transfert V19
- `OBS-V19-FIRST-OBSTRUCTION11` — OBSERVABILITE — V19 — premier ordre d’obstruction de multiplicité : k*=11 (classification complète)
- `OBS-V19-N11-BADOBJECT` — OBSERVABILITE — V19 — reconstruction exacte des cinq premières ruptures N=11 au niveau des mauvais objets
- `OBS-V19-N11-MOMENT-GRAM` — OBSERVABILITE — N11 : matrices exactes des moments et conservation des cinq circuits de 2-recouvrement
- `BR-Q-SWAP-MEM-01` — QUANTIQUE — Témoin SWAP de mémoire relative aux continuations

## Limites observées

1. L'extraction est encore lexicale/règle-typée : elle est plus structurée que v0.1 mais ne comprend pas encore les types mathématiques au sens formel.
2. Un atome partagé peut refléter une proximité réelle ou un vocabulaire structurel trop large ; chaque attracteur doit donc être audité avant d'alimenter une conjecture.
3. La présence de Δ_h/Mealy/V19 dans le même attracteur est un résultat de **détection**, pas une certification d'unification.
4. Le graphe ne crée aucune conjecture automatiquement dans cette version.
5. La couche bibliographique et les évaluateurs automatiques sont seulement routés par `evaluator_registry_v01.json`; ils ne sont pas encore exécutés automatiquement.

## Critère pour poursuivre vers Conjecture Graph v0.1

Le MVP atteint son critère minimal : une signature typée est produite pour tout le noyau admissible et le benchmark ciblé retrouve un motif transversal sans règle spéciale. La prochaine étape sûre est donc de prendre un petit nombre d'attracteurs de haut rang et de les transformer en **conjectures atomiques falsifiables**, avec contre-exemple minimal et budget de deux expériences décisives.

## Empreintes des artefacts

- `ravi2_structural_graph_v02.py` — SHA256 `8e06530c988a7e2d70f6559d517c0c7bf3c63b2f5c51d76c30c143d0c96886c1`
- `structural_schema_v02.json` — SHA256 `7eb298032b26fba7039b299bd73b060d9fe7dd91bac831de118f81d5f7d94937`
- `evaluator_registry_v01.json` — SHA256 `69e550699ff5aa80d8a9215be34e962fb0e7deed51893298ad1bcd1a1b60b024`
- `RAVI2_RESEARCH_GRAPH.sqlite` — SHA256 `9e0ecb07420ed14012dbcde54e5948cc11c5cfbdbc1736e7cff1907db68585e3`
- `RAVI2_STRUCTURAL_GRAPH_V02_SUMMARY.json` — SHA256 `733c533982fbee045ddf3c043ec90ded672f3ecdc444257d53757da09bd4d3d8`