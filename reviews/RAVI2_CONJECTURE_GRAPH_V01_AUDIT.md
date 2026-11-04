# RAVI-2 Conjecture Graph v0.1 — audit du 19 octobre 2026

## Objet

Construire le sas `Structural Graph -> Conjecture -> verrou -> expérience -> verdict` sans modifier le noyau scientifique. Le benchmark ciblé part de l'attracteur transversal détecté par Structural Graph v0.2 entre `DELTA-SPECTRUM-CLASS`, `BR-MEALY-HELLY-01` et `OBS-V19-FIRST-OBSTRUCTION11`.

## Garde de méthode

- La base `/Recherche/00_INDEX_ET_METHODES/RESEARCH_MEMORY.sqlite` est lue sans écriture et conserve le même SHA256 `087e1ef5be0f2768d9685062b26430928b832822fa400ac259d8184f559baf85` avant/après.
- Aucun statut scientifique n'est modifié.
- Aucun `DEPEND_DE` n'est créé.
- `PROVED_INTERNAL` dans le graphe de recherche n'est pas `DÉMONTRÉ` dans le noyau scientifique.
- Budget appliqué : au plus deux expériences décisives par verrou.

## Conjecture 1 — généralisation monotone

ID : `CONJ-OBS-MONOTONE-INDEX-01`.

Énoncé testé : une fois une obstruction apparue à un indice `n`, une obstruction existerait à tous les indices plus grands.

Verdict : **RÉFUTÉ**.

Le checker reconstruit explicitement un système fini issu de la construction universelle du programme Δ_h dont le spectre calculé jusqu'à l'horizon 12 est

`{2,4,6,8,10,12}`.

Ainsi `Δ_2 != empty` mais `Δ_3 = empty`. Le rapprochement structurel Δ_h/Mealy/V19 ne transporte donc pas une monotonie universelle de l'indice.

## Conjecture 2 — principe du résumé fini

ID : `CONJ-FINITE-SUMMARY-SPECTRUM-01`.

Énoncé : si un problème d'obstruction incrémental possède un ensemble fini de résumés, une mise à jour compatible avec l'ajout d'un incrément, et un prédicat d'obstruction qui ne dépend que du résumé, alors le spectre des tailles pour lesquelles une obstruction existe est ultimement périodique. Si la minimalité est décidée par une augmentation finie du résumé, le même résultat vaut pour le spectre des tailles de témoins minimaux.

### Preuve interne

Pour un automate de résumé `A=(S,Sigma,delta,s0,F)`, poser

`R_n={delta*(s0,w): |w|=n}`.

Alors `R_{n+1}=Post(R_n)` et la suite `(R_n)` évolue dans l'ensemble fini `2^S`. Elle est donc ultimement périodique. L'existence d'une obstruction de taille `n` équivaut à `R_n intersect F != empty`. Une augmentation finie qui décide la minimalité donne le même argument pour les témoins minimaux.

Ce mécanisme est classique du point de vue des langages réguliers : les images de Parikh des langages réguliers sont semi-linéaires ; en dimension 1, semi-linéaire équivaut à ultimement périodique. Aucune nouveauté générale n'est revendiquée pour ce théorème abstrait.

### Expérience décisive 1

Énumération exhaustive de tous les automates déterministes unaires jusqu'à 4 états, tous états initiaux et tous ensembles d'acceptation : **17 066 automates**, aucune violation de la périodicité après entrée dans le cycle.

### Expérience décisive 2 — interfaces cibles

- Mealy : 21 cas abstraits `C(q,k)` pour `q=3..8`, `2<=k<=q-1`. L'encodage par sous-ensemble des branches retrouve la non-face minimale de taille `k` dans chaque cas.
- V19 : la région exacte projetée sur les 14 labels est une boîte/orthant. L'encodage par vecteur de multiplicités tronqué à `cap+1` est un résumé fini exact pour l'obstruction de capacité.

Verdict : **PROVED_INTERNAL**, originalité générale `KNOWN_OR_CLASSICAL`, sans promotion scientifique.

## Résultat dérivé en staging

ID : `STG-V19-MIN-OBSTRUCTION-SPECTRUM-01`.

À partir de la boîte exacte V19, un vecteur non admissible est minimal pour l'ordre sous-multiset si et seulement si une unique coordonnée bornée vaut `cap+1` et toutes les autres coordonnées sont nulles. Il en résulte :

- 10 familles minimales de labels ;
- tailles : `11, 11, 11, 11, 21, 41, 41, 61, 81, 161` ;
- spectre des tailles minimales : **`{11,21,41,61,81,161}`**.

Ce corollaire est **DÉMONTRÉ EN STAGING** seulement. Son originalité n'est pas auditée et `eligible_for_scientific_commit=0` dans cette passe.

## Contrôles machine

- `PRAGMA integrity_check = ok` sur `RAVI2_RESEARCH_GRAPH.sqlite`.
- 0 erreur de clé étrangère.
- 2 conjectures enregistrées.
- 2 verrous.
- 3 expériences décisives au total, jamais plus de 2 par verrou.
- 2 verdicts.
- 1 résultat dérivé en staging.
- source scientifique inchangée.

## Artefacts

- `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/ravi2_conjecture_graph_v01.py`
- `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/conjecture_schema_v01.json`
- `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/RAVI2_CONJECTURE_GRAPH_V01_SUMMARY.json`
- `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/RAVI2_CONJECTURE_GRAPH_V01_CHECKS.json`
- base enrichie : `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/RAVI2_RESEARCH_GRAPH.sqlite`

## Décision

Le MVP est validé comme infrastructure de recherche : il sait refuser une fausse généralisation, fermer un verrou dans le budget, conserver un théorème interne hors noyau et produire un corollaire dérivé en staging. La prochaine étape sûre est l'audit bibliographique et de redondance du corollaire V19 avant toute proposition de commit scientifique.