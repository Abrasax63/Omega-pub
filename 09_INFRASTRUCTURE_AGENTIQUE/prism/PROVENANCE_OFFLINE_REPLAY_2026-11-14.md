# Cycle de provenance — rejeu hors ligne de deux jobs K3s

14 novembre 2026. Base PR #81 `d0ee51660eef8edea6b89bffd7cb946f65066556`. Ce passage vérifie le raccord hors ligne sur les deux journaux complets déjà consignés dans [l’essai précédent](PROVENANCE_FULL_LOG_TRIAL.md). Les cibles étaient publiques et déjà connues. Ce lot sert à la validation du raccord et reste distinct de l’entraînement. Il ne constitue pas un workflow inédit ni une réserve aveugle. Aucun nouveau journal archivé et admissible n’a été identifié dans les pièces disponibles.

Archive de raccord vérifiée par SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`. Patch contrôlé avec `git apply --check offline.patch`, puis appliqué à une copie temporaire des fichiers épinglés. SHA-256 du module `1bdf3cab412f6eab7306226c2e981bf6cea5a887f5651849ba7cd051d7809464`.

```sh
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_offline.py propose incumbent.json training.json proposal.json
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_offline.py check incumbent.json archived-replay.json proposal.json
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism -q
```

Le manifeste d’entraînement contient uniquement le contrôle synthétique déjà fourni dans l’archive. La référence déclarative explicite est `[]` (empreinte canonique `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`). Une confirmation manquée en entraînement. Le programme a sélectionné `["cp","-av"]` et proposé `{"argv_prefix":["cp","-av"],"verdict":"copie"}`. Le contrôle d’évaluation retire uniquement le retour verbeux vers la cible du premier job. Les scripts épinglés cités dans l’essai précédent documentent la copie locale.

| Méthode | Confirmations correctes | Fausses confirmations | Abstentions |
| --- | ---: | ---: | ---: |
| Référence déclarative | 0 | 0 | 3 |
| Candidat | 2 | 0 | 1 |
| Règle fixe `fixed_verdict` | 2 | 0 | 1 |

Journaux originaux [job 132346516375](https://github.com/k3s-io/k3s/actions/runs/43561665973/job/132346516375) et [job 132319505796](https://github.com/k3s-io/k3s/actions/runs/43553016671/job/132319505796), SHA-256 `3a5e6e5b35cb2f33813226d9bf2f065088f697138e8789eb46e2ebddb7fa1e8e` et `3da0b415dd4d994c9ab9627075f3d295e5be3aef60aa57a197657e557781340d`. Contrôle dérivé : `93e943b6da88c273e37850f3a8b91e8b2189215042071ed62a40aa9d22a2df68`.

SHA-256 du manifeste d’entraînement `f21a80597c49c0433700b7fc5d9c750273192a818ff154b62ae4910b40564415`, de la proposition `e842301d3b4747a05773ff29d7d8b09432883522df6d1cc5278b9ee9ac3bdd00`, du manifeste de rejeu `70235945e6205804920a3b15785cc56175e9e94f423649e53a801c3f210ceaae` et du résultat `5f86371c9fc9cb91c12ca1c62013beaab43a0d5e0e23efc242872b97759ff347`.

Les 24 tests du laboratoire passent. Le programme recommande une revue face à la référence vide. La parité avec la règle fixe et le caractère rétrospectif du rejeu conservent la référence active. Aucun workflow déclenché. Prochaine vérification de provenance : prédéfinir une cible depuis une source indépendante, puis faire passer un journal archivé inédit et son contrôle contradictoire par le même raccord. Le prochain cycle de l’alternance est mathématique.
