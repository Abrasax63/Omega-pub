# Provenance — rapport externe BuildKit sans trace de copie admissible

19 novembre 2026, 02 h 36 (Paris). **INDÉTERMINÉ — cycle sans expérience nouvelle de classification.** Branche `work/omega-provenance-lab`, départ [e409c17](https://github.com/Abrasax63/Omega-pub/commit/e409c1723c17e854692db36ffcf9551a9ac58f95). [Dernier cycle mathématique](https://github.com/Abrasax63/Omega-pub/commit/396ba4d8836a173d1197ff2019a3577150443e3b).

Question d’admissibilité fixée avant lecture : un workflow externe inédit fournit-il une commande de copie source/destination, sa fin d’étape et une vérité terrain séparée compatibles avec le raccord ? Budget : un job du workflow frontend de moby/buildkit et sa source Dockerfile épinglée. Critère d’entrée : triplet de preuves conservé dans le journal, avant toute génération ou lecture de réserve.

Nouveau [run 44361953379](https://github.com/moby/buildkit/actions/runs/44361953379), révision `3babd403e220cc3b9e416db3240de0d800aed6d1`, [job containerd integration](https://github.com/moby/buildkit/actions/runs/44361953379/job/135007453377). [Dockerfile de la source](https://github.com/moby/buildkit/blob/3babd403e220cc3b9e416db3240de0d800aed6d1/Dockerfile) consulté indépendamment. L’artefact 14456277462, `test-reports-run-frontenddockerfile--integration-containerd-`, est non expiré au contrôle. Son ZIP a le SHA-256 `926c91706909450051c95813e9546ff5d6bef2a38274aecf0ffa29e9014f104c`, identique au catalogue GitHub.

Le membre `go-test-report-run-frontenddockerfile--integration-containerd-.json`, SHA-256 `9077b9045f192530e418974081333771a3b555dd0f629a67e626cff30e40b2b4`, contient 6 840 enregistrements JSON, dont 3 478 avec Output. Le relevé de sorties compte 1 105 événements de succès de tests et zéro échec. Il ne contient ni ligne native de progression commençant par # suivi d’un numéro, ni commande `+ cp -av`. Les deux mentions COPY sont des assertions de noms d’étapes dans TestStepNames (client et builtin). Elles ne fournissent pas la séquence de copie suivie par le raccord. Le succès de tests ne constitue pas une preuve du dernier écrivain d’un artefact.

Aucune pièce admissible identifiée au budget prévu. La référence est conservée. Aucun propose/check, aucune réserve annotée fournie. Métriques candidat/règle fixe non mesurées. Le contrôle d’inventaire est nouveau, sans gain externe évalué. Harnais de lecture JSON conservé pour reproduire les comptes, sans exécuter de contenu de l’archive.

Raccord SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd` vérifié, patch appliqué en copie temporaire après `git apply --check`. `python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism -q` : 66/66.

Prochain test décisif : examiner le format des artefacts dockerbuild du même run sur un contrat de sortie de fichier préalablement fixé, avant d’ouvrir des pièces réservées. Prochain cycle alterné : mathématique.

Reproduction du contrôle : `python 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_trials/audit_buildkit_report.py buildkit-reports.zip`.
