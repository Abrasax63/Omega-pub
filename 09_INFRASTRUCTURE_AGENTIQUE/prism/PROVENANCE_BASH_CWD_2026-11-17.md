# Provenance Bash et changement de répertoire

17 novembre 2026. Branche `work/omega-provenance-lab`, base `20a23455c9f7470c409e5904b6b92f60e850109c`. Dernier [cycle de provenance](PROVENANCE_BASH_ALIAS_2026-11-14.md). Le [cycle mathématique sur L+1](https://github.com/Abrasax63/Omega-pub/commit/d9211bd1d52d06f742fd99c2b57b9d2455a2060f) précède ce cycle dans l’alternance.

Hypothèse réfutable : une copie vers un chemin relatif de même texte suffit à identifier la cible depuis le répertoire de départ, même après cd. Trois contrôles synthétiques fixés avant le test, une lecture chacun : cp relatif après cd (abstention attendue), cp relatif sans cd (copie), cp absolu après cd (copie). Critère du diagnostic : zéro fausse confirmation et maintien des deux copies. Les chemins absolus du contrôle ne passent pas par des alias.

Archive hors ligne vérifiée (SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`), patch appliqué temporairement après git apply --check. La référence explicite est `[]`. Appeler `provenance_offline.py propose eval/base.json eval/train.json eval/proposal.json` avant de matérialiser le manifeste de contrôle, puis `provenance_offline.py check eval/base.json eval/check.json eval/proposal.json` avant/après le patch expérimental. Le programme a choisi `cp → copie`. Le patch rend incomplète une trace à cible relative lorsque cd, pushd ou popd y apparaît. Il ne suit pas les répertoires et peut donc perdre une confirmation quand un changement de répertoire est sans effet sur l’écriture.

| Méthode | Confirmations correctes | Fausses confirmations | Abstentions |
| --- | ---: | ---: | ---: |
| Référence déclarative | 0 | 0 | 3 |
| Candidat et règle fixe, extracteur initial | 2 | 1 | 0 |
| Candidat et règle fixe, extracteur expérimental | 2 | 0 | 1 |

**VÉRIFIÉ sur trois contrôles synthétiques.** Les 24 tests existants passent avant et après (`python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism/ -q`). La règle fixe partage l’extracteur et reste à égalité. Aucun journal externe inédit admissible n’a été évalué. Patch archivé, référence active conservée. Prochain test décisif : fixer le répertoire initial et la cible depuis un workflow Bash archivé avant lecture du journal, puis tester indépendamment la reconstruction de la destination. Prochain cycle : mathématique.

SHA-256 : référence `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`, manifeste d’entraînement `724e0ca6fd2b1581476b735c63083a4dd2bb0bb402529251f81d9ff069abe9f6`, proposition `353eae2c31401ac907dab8c54a3d4d345a08de70a69e4e3eb2dab289c54e8507`, manifeste d’évaluation `204961fb4a0e6906cc31ab0f0cd54973af235d1cf9a191b47c62125d414ec2f3`, patch `90e09a4eda14b183a4dd9d4572b5d12d100497fe456fa1d106bcbb4aa094335d`.
