# V19 C5 / L=3 — données et reproduction

Le script `../../code/audit_v19_c5_independent_2026-11-04.py` attend quatre entrées historiques dans ce dossier et y écrit quatre sorties.

## Entrées attendues
- `V19_ORIENTED14_CLASSES_2026-10-15.csv` — SHA-256 `c4e50406528122b7ffed84ffa8edb417ad01a4d05af101a59a1ff203e54bfcf1`
- `V19_PAIR_WITNESSES_C5O14_2026-10-15.csv` — SHA-256 `313316b60e9a37d218ed41b338bbf88a01b68d44b46ec56a6f62a436fbbbf84e`
- `V19_TRIPLE_WITNESSES_D5_13_2026-10-15.csv` — SHA-256 `905f764999feed5f74ea72dcf0e5812d0e284c2e2e68b0a82e13ed1f22b4731e`
- `V19_UNIVERSAL10_U42_2026-10-15.json` — SHA-256 `a40aff8603e257290e8f5aeb4d67efdf71227239c854397f501a7d69619db3cc`

## Sorties attendues
- `V19_PAIR_WITNESSES_C5O14_REPAIRED_2026-11-04.csv` — SHA-256 `b55cf80b0ac167c21cd391337d22c8b83d5786b2c4c472f61d7cfd664c0382da`
- `V19_TRIPLE_WITNESSES_D5_13_REPAIRED_2026-11-04.csv` — SHA-256 `1b25460dc72972aed010309c866d60df654a4d5e9075f92c6f128e7465106847`
- `V19_TRIPLE_WITNESSES_C5O14_U42_2026-11-04.csv` — SHA-256 `33a1e7cf90ff19823ef3226b263eba009f952f9884cac89882bd85d2d6acb825`
- `AUDIT_V19_C5_INDEPENDENT_2026-11-04.json` — SHA-256 `547e28d9a1a8f89c62cc376948241ed58fbe59122c7ab9f853647f5ead2285b8`

**État de migration :** ces fichiers sont référencés par leur nom et leur empreinte, mais ne sont pas encore synchronisés dans le dépôt. Ne pas considérer le script comme reproductible depuis GitHub avant leur ajout et une exécution réussie depuis un clone propre.

Depuis la racine du dépôt, une fois les quatre entrées installées :

```bash
python research/code/audit_v19_c5_independent_2026-11-04.py
```
