# P5-TRANSFER-02 — extension gelée, checkout curl distinct

Après lecture du lot initial H1–H4, et **avant lecture des deux journaux ci-dessous**, extension descriptive de transfert à un **nouveau commit** du même dépôt. Le code reste strictement celui du gel `e48c8e86486830ec6f0239986720f5981de8120c` avec sa correction préflight ; aucune adaptation sur les résultats H1–H4.

- **H5** — [curl/curl Source run 43673260605, job 132687805550](https://github.com/curl/curl/actions/runs/43673260605/job/132687805550), « CM integration ubuntu-26.04-arm », cible `source.tar.gz`.
- **H6** — [curl/curl Linux run 43673260575, job 132687809497](https://github.com/curl/curl/actions/runs/43673260575/job/132687809497), « CM boringssl », cible `src/curl`.

Commit épinglé `d67cc443498b943f82ccd7a43b75c210ab2089f5`, distinct du `f49c9c95bc31643518b86249e2a7f014699df305` des jobs d'entraînement et H1/H2. Scripts sources : `tests/cmake/test.sh` (H5) et `src/CMakeLists.txt` (H6) à ce SHA, lus avec la même méthode et le même budget. Les deux jobs proviennent du même dépôt et du même commit et **ne forment pas deux réplications indépendantes**.

Comparer candidat appris et comparateur fixe par les mêmes règles, ne pas modifier après lecture. Si un des formats est inconnu, abstention. Toute revendication de transfert reste limitée à une forme de recipe du même projet, non à une nouvelle famille de logiciels, à l'identité binaire ou à un avantage sur solveur classique. Aucun merge `main` ni déclenchement d'exécution externe.
