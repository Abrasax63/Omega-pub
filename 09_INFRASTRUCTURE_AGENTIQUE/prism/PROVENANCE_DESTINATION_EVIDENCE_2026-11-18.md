# Provenance Bash — corroborer le chemin avec le système de fichiers

18 novembre 2026, 03 h 34 (Paris). Branche `work/omega-provenance-lab`, base `3326cf5564ac11564ff9f9f2b63dd47ce2eef7c8`. [Cycle précédent](PROVENANCE_BASH_DESTINATION_2026-11-18.md) et [cycle mathématique](https://github.com/Abrasax63/Omega-pub/commit/17fc29db54a29a40db2a781132697d16de8e6b8e).

Question : joindre un relevé local du chemin exact élimine-t-il la fausse confirmation sur les deux journaux identiques du test précédent ? Protocole fixé avant exécution : trois cas locaux du harnais épinglé, dont le répertoire contradictoire. Un journal et un relevé par méthode à budget égal. Critère : deux confirmations correctes, zéro fausse et abstention si le relevé est absent ou provient d’un autre cas. Comparer aussi au journal seul pour isoler l’apport de la pièce.

Archive hors ligne contrôlée au SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`, patch appliqué après `git apply --check`. Référence déclarative vide. Le raccord sélectionne `cp → copie` sur l’entraînement seul, puis check reçoit les trois journaux contrôlés. Le candidat expérimental exige ensuite une correspondance du cas et du chemin, un fichier régulier au chemin exact (lstat) et l’égalité de son empreinte avec celle de la source. Les contrôles de relevé absent ou attribué à un autre cas s’abstiennent.

| Méthode | Correctes | Fausses | Abstentions |
| --- | ---: | ---: | ---: |
| Référence déclarative | 0 | 0 | 3 |
| Candidat et fixe, journal seul | 2 | 1 | 0 |
| Candidat et fixe, journal et relevé | 2 | 0 | 1 |

**VÉRIFIÉ sur contrôles locaux.** Les 24 tests passent avant et après. Le test du relevé prend 0,040 s, génération du journal exclue. Les mêmes scénarios servent à isoler l’effet du relevé. Le résultat repose sur un environnement contrôlé : un état final avec les mêmes octets ne suffit pas à attribuer une écriture en présence d’autres écrivains et l’identifiant local ne constitue pas une attestation d’exécution. Aucun workflow archivé inédit admissible évalué. Parité à budget égal, référence active conservée.

Rejeu dans une copie temporaire après application du raccord, depuis la racine :

```sh
p=09_INFRASTRUCTURE_AGENTIQUE/prism
mkdir eval
printf '[]\n' > eval/base.json
python3 "$p/provenance_trials/audit_bash_destination.py" eval train
python3 "$p/provenance_offline.py" propose eval/base.json eval/train.json eval/proposal.json
python3 "$p/provenance_trials/audit_bash_destination.py" eval reserved
python3 "$p/provenance_offline.py" check eval/base.json eval/reserved.json eval/proposal.json
PYTHONPATH="$p" python3 "$p/provenance_trials/audit_destination_evidence.py" eval
python3 -m unittest discover -s "$p" -q
```

SHA-256 : harnais `3740a6c1700b41710ce01f66ae12091fa993a9623f739c36ad88363cf8b2e824`, référence `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`, proposition `2d5b50a0439f6034cc0fd377b3e6946bcb7aec6dd18b4e3429e32d259002a49a`, réserve `910d09765fa3d1199ac5911d6a63346a0e291a28f7678c130a65dfa6d71d436b`, check `110cf8deb1139afcc0d21fbf3762bd5fb197d48d64d65209ff591372315408a2`, relevés `2c7e21fb3951650de6dd6737de5a8087b00926adfa1f2f7a5a718feb4f2e5b47`.

Prochain test de provenance : cas externe où un manifeste d’artefact déjà archivé relie un chemin effectif à un job et permet un contrôle avec une écriture ultérieure. Prochain cycle : mathématique.
