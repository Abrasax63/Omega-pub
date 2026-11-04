# Code de reproduction public

Les scripts de ce dossier sont des contrôles finis ciblés. Ils ne constituent pas à eux seuls des preuves des lemmes universels auxquels certains résultats sont reliés.

## V19 — C4, L=2

`c4_l2_independent_local_audit_2026-11-04.py`

- Énumération directe du catalogue local C4/L=2, sans DSU/parité.
- Contrôle global exhaustif des endofonctions cohérentes pour les tailles annoncées dans le rapport.
- Python standard library.
- Rapport : `reviews/AUDIT_SEMANTIQUE_C4_L2_2026-11-04.md`.

Exécution depuis la racine du dépôt :

```bash
python research/code/c4_l2_independent_local_audit_2026-11-04.py
```

## V19 — C5, L=3

`audit_v19_c5_independent_2026-11-04.py`

- Reconstitution du catalogue fini à partir des données versionnées dans `research/data/v19_c5/`.
- Propagation directe des colorations du cycle ; aucune structure DSU/parité n'est utilisée.
- Python standard library.
- Workflow GitHub Actions : `.github/workflows/v19-c5-repro.yml`.

Exécution depuis la racine du dépôt :

```bash
python research/code/audit_v19_c5_independent_2026-11-04.py
```

La portée universelle reste conditionnée par le lemme de localité L+2 indiqué dans le rapport ; le script ne le re-prouve pas.

## Machines de Mealy — témoin (5,2,3)

`mealy_boundary_certificate.py`

- Vérifie (r_{IO}=1), la profondeur ADS optimale (L_A=3) et l'absence de PDS pour le témoin fini.
- Python standard library.
- Sortie attendue : toutes les assertions passent.

```bash
python research/code/mealy_boundary_certificate.py
```

Rapport et source documentaire : `research/programs/Observabilite/Notes/Adaptivity_boundary_Mealy_machines_EXTRACTED.md`. L'original DOCX n'est pas dans le dépôt ; l'extraction ne garantit pas la conservation de sa mise en page.

## Machines de Mealy — nerf de compatibilité / Helly

`mealy_helly_bridge.py`

- Parcourt les 21 machines (C(q,k)), (3\le q\le8), (2\le k\le q-1).
- Explore 492 états de connaissance cumulés et 1 337 nerfs.
- Écrit le résultat dans `research/data/mealy_helly/MEALY_HELLY_RESULTS_2026-10-16.json`.
- Python standard library.
- Le chemin de sortie a été rendu relatif au dépôt ; le hash de la source historique d'origine et celui de la version portable sont séparés dans `research/data/mealy_helly/MEALY_HELLY_SOURCE_HASHES_2026-10-16.json`.

```bash
python research/code/mealy_helly_bridge.py
```

La borne universelle dépend de la preuve reliant les branches essentielles d'une non-face minimale à la largeur fertile `OBS-M27-FERTILE). Le calcul teste la famille construite et ne remplace pas cette preuve. Le script complémentaire `conflict_nerve_certificate.py` mentionné dans le manuscrit source n'a pas été retrouvé et n'est pas inclus.

## Limite commune

Les sorties `PASS` attestent les assertions finies effectivement encodées. Elles ne certifient ni l'originalité bibliographique, ni l'exhaustivité de toute la bibliothèque, ni la validité d'un théorème général au-delà de ses preuves et hypothèses explicites.
