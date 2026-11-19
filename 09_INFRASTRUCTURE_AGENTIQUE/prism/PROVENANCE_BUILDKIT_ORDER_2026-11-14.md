# Provenance — ordre d’une copie et d’une suppression

14 novembre 2026. Base `5fc9c49a1838f1dcf9079ec89dd390b9308d0c6c`. Ce cycle évalue le faux négatif du [candidat précédent](PROVENANCE_BUILDKit_REMOVAL_2026-11-14.md) quand le nettoyage précède la copie. Ce candidat reste expérimental.

L’archive hors ligne correspond au SHA-256 demandé `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`. Dans une copie temporaire du code épinglé, appliquer son patch puis le patch `provenance_trials/buildkit_removal.patch`, chacun après `git apply --check`. Le nouveau patch est incrémental sur ce dernier.

Avec l’entraînement fourni dans l’archive et la référence explicite `[]`, `provenance_offline.py propose eval/incumbent.json eval/training.json eval/proposal.json` choisit `cp -av` et propose `copie`. Évaluation séparée avec `provenance_offline.py check eval/incumbent.json eval/order.json eval/proposal.json`, avant et après le patch incrémental. Trois contrôles synthétiques : dans le même bloc, copier `src/asset` vers `out/asset` avec retour verbeux et DONE, et supprimer la cible avant la copie, la supprimer après, ou supprimer un autre chemin après. Le verdict porte sur la sortie de fin de bloc. Le candidat évite de s’abstenir lorsque la suppression précède tout indice de copie de la cible. Il reste conservateur sur l’ordre entre blocs distincts.

| Méthode | Confirmations correctes | Fausses confirmations | Abstentions |
| --- | ---: | ---: | ---: |
| Référence déclarative | 0 | 0 | 3 |
| Règle proposée et fixe avec le patch précédent | 1 | 0 | 2 |
| Règle proposée et fixe avec le patch incrémental | 2 | 0 | 1 |

Les 24 tests existants passent (`python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism -q`). Les contrôles sont distincts de l’entraînement et conçus pour ce diagnostic. Les journaux K3s locaux ont les mêmes empreintes que le rejeu précédent. Aucun nouveau journal archivé assorti d’une vérité terrain indépendante n’a été évalué. La parité avec la règle fixe conserve la référence, et le patch incrémental reste archivé. Prochain test : corroborer l’ordre des écritures et suppressions au sein d’un même bloc sur un journal inédit admissible. Prochain cycle : mathématique.

SHA-256 : proposition `e842301d3b4747a05773ff29d7d8b09432883522df6d1cc5278b9ee9ac3bdd00`, manifeste de contrôle `7d75505e3ef55ad7e40bdf7def27ead12b93d018d21cc9310d5bd0f22775a4e8`, résultats avant `9a7dbdd430e3c6a958b98c3df2826539cb6710eaf5e44132581e4c34bdf65734` et après `59e6bfebd93e7ab0a8b53087ef97626ca01a731ec5917917520ef378acd12777`, patch incrémental `f994241bd681c247f465600f1af5dd3d6970ca2e31998fe0d810f70270bbcc80`.
