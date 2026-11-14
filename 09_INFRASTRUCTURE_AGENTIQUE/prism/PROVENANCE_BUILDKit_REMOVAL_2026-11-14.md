# Cycle de provenance — copie suivie d’une suppression

14 novembre 2026. Base `7a97d1e6f299790a4be1c6b5536de6694e8eb699`. Le [cycle précédent](PROVENANCE_OFFLINE_REPLAY_2026-11-14.md) a validé le rejeu K3s. Le nouvel essai cherche un défaut différent : le journal confirme une copie intermédiaire mais montre ensuite la suppression de la sortie avant la fin du même bloc BuildKit. Le verdict porte sur la sortie à la fin du bloc.

Le raccord hors ligne, archive SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`, a passé `git apply --check` puis a été appliqué à une copie temporaire. Avec la référence explicite `[]`, `provenance_offline.py propose eval/incumbent.json eval/training.json eval/proposal.json` a choisi `cp -av` et proposé `copie` à partir du contrôle d’entraînement de l’archive. Le manifeste d’évaluation a été fourni ensuite à `provenance_offline.py check eval/incumbent.json eval/controls.json eval/proposal.json`, avant et après le patch archivé.

Trois contrôles construits, distincts de l’entraînement : un bloc ayant copié `src/asset` vers `out/asset` puis supprimé la cible, un bloc supprimant un autre chemin, et un bloc supprimant la cible sous la forme `rm -f -- ./out/asset`. Chaque bloc se termine par DONE. Le patch traite le sous-ensemble `rm -f` à un seul opérande, avec `--` et `./` facultatifs. Il s’abstient par prudence à la rencontre d’une telle suppression de la cible, même si elle précède la copie.

| Méthode | Confirmations correctes | Fausses confirmations | Abstentions |
| --- | ---: | ---: | ---: |
| Référence déclarative | 0 | 0 | 3 |
| Candidat et fixe, extracteur initial | 1 | 2 | 0 |
| Candidat et fixe, extracteur modifié | 1 | 0 | 2 |

Les 24 tests existants passent avant et après (`python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism -q`). Le fixe emploie le même extracteur à chaque étape et obtient exactement les mêmes verdicts que le candidat. Les contrôles sont synthétiques et visibles par l’auteur de la correction. Les journaux locaux K3s avaient déjà été exploités et aucun workflow archivé inédit avec vérité terrain séparée n’a été évalué. La référence active est conservée. Le patch reste disponible pour examen, hors du chemin actif. Prochain test : vérifier l’ordre des écritures et des suppressions sur un journal inédit admissible. Prochain cycle de l’alternance : mathématique.

SHA-256 : référence fichier `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`, entraînement `f21a80597c49c0433700b7fc5d9c750273192a818ff154b62ae4910b40564415`, proposition `e842301d3b4747a05773ff29d7d8b09432883522df6d1cc5278b9ee9ac3bdd00`, évaluation `ca3d3a0ee208f84dff0eed88ec8c05d7e57968e8745b6c8b9d6153ca58eef8ff`, résultats avant `e335450d8d729ef10aa7667b908fc4086040e90b1e31469881302cf3558e779b` et après `d2e25490539e3c700d95fe7e661d64fc5d1eda6dde585d7415e5cb032f648d6f`, patch `e65f2e0715bab1dd19ebf5e96cb1e85456d4b424514b6c51a8ec610904b59f5a`.
