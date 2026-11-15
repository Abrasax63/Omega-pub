# P5-TRANSFER-02 — amendement avant toute lecture du lot H

Un contrôle de l'**ancien corpus d'entraînement C3**, après publication du protocole mais **avant consultation de H1 à H4**, a révélé une différence Bash : le journal contient `++ sha256sum` (trace d'une substitution de commande) plutôt que `+ sha256sum`. Le parseur initial ne reconnaissait que la seconde forme.

La modification [commit 20f86ce](https://github.com/Abrasax63/Omega-pub/commit/20f86ce680800903f40eaa1b6f1f7a6209385795) reconnaît les deux marqueurs dans l'étape d'entraînement ; [commit e48c8e8](https://github.com/Abrasax63/Omega-pub/commit/e48c8e86486830ec6f0239986720f5981de8120c) ajoute un test. **Le contenu des H1–H4 n'a pas été consulté avant ces modifications.** Il s'agit d'une correction de préflight, non d'un ajustement sur l'évaluation. Le nouveau gel définitif est `e48c8e86486830ec6f0239986720f5981de8120c`. Le pré-enregistrement original et son commit restent visibles.

Les 13 tests adversariaux sur corpus construit passent en environnement Python local ; aucun run GitHub Actions de cette branche n'a été demandé. Aucune modification du comparateur fixe, des seuils ou des quatre identifiants de job.
