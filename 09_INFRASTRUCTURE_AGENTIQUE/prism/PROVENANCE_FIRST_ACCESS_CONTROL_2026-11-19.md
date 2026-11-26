# Provenance — contrôle applicatif d’une réécriture à octets constants

19 novembre 2026, 00 h 56 (Paris). Branche `work/omega-provenance-lab`, départ [e774ec8](https://github.com/Abrasax63/Omega-pub/commit/e774ec8fe0d0cdee27d7e455fe664918361507c9). [Dernier cycle mathématique](https://github.com/Abrasax63/Omega-pub/commit/187cd7e23a993fb4e285d2434a3b7d2aed056f95).

Question fixée avant test : une projection ne conservant que le premier accès peut-elle distinguer une et deux écritures des mêmes octets via un même descripteur ? Réfutation si les nombres d’écritures réussies diffèrent, mais que la projection et l’empreinte finale sont identiques. Deux exécutions locales, aucun workflow externe, contrôle positif à une écriture et contradiction à deux. Référence prévue : événements de strace et retours des écritures.

**Nouveau blocage d’environnement.** strace 6.13 est installé, mais son exécution est refusée : `PTRACE_TRACEME: Operation not permitted` et `PTRACE_SETOPTIONS: Operation not permitted`. Le contrôle minimal `strace -qq -o /tmp/omega-strace-availability.log true` échoue avec code 1. Aucun événement noyau n’a été obtenu et aucune exécution Buildcage n’a été lancée.

**EXÉCUTÉ — contrôle applicatif de remplacement, hypothèse de distinction RÉFUTÉE dans ce modèle.** Le programme enfant ouvre une cible, positionne le même descripteur à zéro et appelle os.write une ou deux fois. Chaque retour est contrôlé à 9 octets et rapporté dans un reçu applicatif. L’oracle est le pilote local déclaré, pas une instrumentation noyau indépendante. Les deux processus sont distincts ; leur identité logique est normalisée dans la projection.

| Scénario local | Retours d’écriture rapportés | Événements après projection premier accès | Empreinte finale |
| --- | ---: | ---: | --- |
| Une écriture | 1 | 1 | identique |
| Deux écritures identiques | 2 | 1 | identique |

Empreinte finale SHA-256 `83ce49ae826e6cbe796284afb944a4906287ac1a0cf6a7bbd598e90f2af56681`. Ce contrôle explique la perte d’information de la projection, sans mesurer le comportement de Buildcage. Son contrat source de référence reste [event.h](https://github.com/buildcage/isolated-run/blob/d27c1a521ee52d86154d33f6719544e15f19a64a/docker/filesystem-audit/bpf/event.h) et [io.h](https://github.com/buildcage/isolated-run/blob/d27c1a521ee52d86154d33f6719544e15f19a64a/docker/filesystem-audit/bpf/io.h). Aucun gain externe. Comparaison du laboratoire à la règle fixe non mesurée et référence conservée.

Le raccord validé, SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`, a été appliqué en copie temporaire après `git apply --check`. Suite existante : 66/66. Pas de propose/check, les reçus applicatifs ne constituent pas une archive externe admissible avec vérité terrain séparée.

Harnais [audit_first_access_control.py](provenance_trials/audit_first_access_control.py), SHA-256 `997bd5d3a9b271a7daab1efa0a4ab0f1e73e38acab458b6fa8d31f9aaea0cad7`. Rejouer depuis la racine avec `python 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_trials/audit_first_access_control.py /tmp/omega-first-access-control`. SHA-256 du résultat local JSON `519d1c80309005bd0460c0369aa1e35d4b4f21fcabdf586e0575f0bf1abd06e8`.

Prochain test de provenance : obtenir une trace externe autorisée qui conserve les retours de chaque écriture, ou exécuter le contrôle avec instrumentation indépendante dans un environnement qui autorise ce traçage. Prochain cycle alterné : mathématique.
