# Provenance — seconde écriture Bash sous un chemin relatif équivalent

14 novembre 2026. Base `89434600c53d954e4e67e5864fa3b86f68f8fc0e`. Le protocole d’écriture unique du laboratoire peut compter une seule écriture lorsque la seconde utilise le même chemin précédé de `./`. Le cycle traite les étapes Bash dédiées dont le succès et errexit sont attestés. Il suppose le même répertoire de travail pour les commandes du contrôle.

Archive du raccord vérifiée : SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`. Patch hors ligne validé par `git apply --check` puis appliqué dans une copie temporaire du code épinglé. Référence explicite `[]`. Le programme a sélectionné `cp` et proposé `{"argv_prefix":["cp"],"verdict":"copie"}` après un exemple synthétique à écriture unique. Le manifeste d’évaluation n’a été fourni qu’à check.

Les contrôles distincts de l’entraînement sont deux doubles écritures (cp puis cp, cp puis install), où la seconde destination ajoute `./`, et une écriture suivie d’une copie vers un chemin différent. Le patch rend conservatrice une variante de notation qui pourrait cacher un second écrivain. Il ne réalise pas de résolution générale de chemins ni de suivi des changements de répertoire.

| Méthode | Confirmations correctes | Fausses confirmations | Abstentions |
| --- | ---: | ---: | ---: |
| Référence déclarative | 0 | 0 | 3 |
| Candidat appris et fixe, extracteur initial | 1 | 2 | 0 |
| Candidat appris et fixe, extracteur expérimental | 1 | 0 | 2 |

Commandes depuis la racine de la copie :

```sh
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_offline.py propose eval/incumbent.json eval/bash-train.json eval/bash-proposal.json
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_offline.py check eval/incumbent.json eval/bash-check.json eval/bash-proposal.json
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism/ -q
```

Les 24 tests existants passent avant et après. Empreintes SHA-256 : entraînement `a09648a885a52675aa2b113fe8e8db60ca429194f89170438c313b11c74fb910`, proposition `1c96b489420ab43694a1704323e1aad90a7bb97fb577f88eb65489b6e8d31e33`, évaluation `45150b8c413f61ee9cb722d5f33048327a0079de0c2d9ac2054032233735f03c`, avant `627de26a536375d74dc8e17a882f6bcedf63ce9d37a7de4a5d64433de5b9c15e`, après `e8f47c23766f7c77ca373a1271ee43f323bc68b5a6c47f744ddfdbdb06687279`, patch `efeb388e0614f0578fb152092c0fe97baca9c1188d18366cfa47c6ff64c68d86`.

Les journaux K3s et Sage repérés dans les archives locales recoupent des workflows déjà étudiés. Aucun nouveau workflow archivé admissible n’a été évalué. Les cas sont synthétiques et connus de l’auteur du patch. Parité avec le fixe, référence active conservée et patch archivé hors exécution. Prochain test : vérifier les alias de chemins sur une étape Bash inédite avec cible fixée indépendamment. Prochain cycle : mathématique.
