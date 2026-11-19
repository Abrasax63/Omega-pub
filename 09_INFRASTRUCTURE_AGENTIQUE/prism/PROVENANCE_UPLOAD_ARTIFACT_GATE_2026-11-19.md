# Provenance — workflow Upload Artifact : logs disponibles, fichiers cibles absents

19 novembre2026,06h55 (Paris). **EXÉCUTÉ pour l'inspection / INDÉTERMINÉ pour la classification externe.** Branche `work/omega-provenance-lab`, SHA initial [5a0b349c8c6e219a406ebfeea1615511cab5df0f](https://github.com/Abrasax63/Omega-pub/commit/5a0b349c8c6e219a406ebfeea1615511cab5df0f). Dernier cycle mathématique : [bceeb0c](https://github.com/Abrasax63/Omega-pub/commit/bceeb0c7d94f8b8956f067a9158e3101e8a0014d). Nouvelle source externe, sans rejeu du run BuildKit précédent.

Question d'admissibilité fixée avant lecture dans [le protocole](provenance_trials/upload-artifact-prereg-2026-11-19.md) : trouver une trace exécutée, une fin réussie et le contenu de sortie vérifiable séparément. Contrôle négatif : un script affiché ou un nom d'étape ne constitue pas une trace de commande exécutée. Budget : un workflow, un run, un journal de job, source épinglée et catalogue d'artefacts. Aucun workflow déclenché.

Workflow `.github/workflows/test.yml` du dépôt public `actions/upload-artifact`, [run37604537230](https://github.com/actions/upload-artifact/actions/runs/37604537230),7octobre2026,conclusionSUCCESS, révision `cf430e030ddbb5b0abf93d22962f4752f3646cd9`. [Source épinglée](https://github.com/actions/upload-artifact/blob/cf430e030ddbb5b0abf93d22962f4752f3646cd9/.github/workflows/test.yml), SHA-256 `43af36e8eb9d1fd95060d25ea5a21d34f6bb9b995fcaa241617a2f07f881a1dc`. Le job [Build Ubuntu112741191101](https://github.com/actions/upload-artifact/actions/runs/37604537230/job/112741191101) a réussi.

Journal du job effectivement téléchargé et inspecté comme données. Copie UTF-8 matérialisée localement avec normalisation de fin de fichier,656476octets,SHA-256 `3e484f426075147a86614e074e420362359a857aa3d4f4c40938dbfa26993e75`. [Métadonnées et extraits limités](provenance_trials/upload-artifact-metadata-2026-11-19.json). Le journal rapporte notamment la finalisation de `Artifact-A-ubuntu-latest`, ID11474467914, puis une nouvelle version ID11475046496 ; des étapes téléchargent et vérifient les contenus. Les commandes de création sont affichées dans un groupe de script ; le shell est Bash avec errexit/pipefail, sans xtrace dans cette étape. Ces affichages ne sont pas assimilés à des événements `+ cp`.

Obstacle vérifié au budget : le catalogue actuel du run contient un seul artefact, `report.html`,ID11475405383,non expiré. Ni le fichier original ni sa version remplacée ne sont disponibles dans ce catalogue. La source prévoit un job Cleanup Artifacts qui conserve seulement `report.html` et supprime les autres ; les métadonnées indiquent que ce job a réussi. Ses logs n'ont pas été lus, donc les suppressions individuelles ne sont pas confirmées par leurs messages. Le catalogue actuel et le code de nettoyage suffisent à écarter ces fichiers comme vérité terrain disponible ici. Le rapportHTML conservé n'est pas la sortiefile1.txt visée.

Diagnostic effectivement exécuté : l'extracteur existant trouve0écrivain et `complete=false` pour `path/to/dir-1/file1.txt` et `some/new/path/file1.txt`. Comparateur fixe :2indéterminés. [Résultats](provenance_trials/upload-artifact-extraction-2026-11-19.json). Aucun de ces constats ne fournit une étiquette scientifique indépendante pour une comparaison candidat/référence.

**Cycle sans expérience nouvelle de classification admissible.** Aucun manifeste entraînement/réserve inventé ; `provenance_offline.py propose/check` et `provenance_cycle.py propose/check` non appelés. MétriquesTP/FP/FN et gaincandidat non mesurés ; les deux abstentions de diagnostic ne constituent pas un gain externe. Référence conservée, aucun candidat classificateur actif.

Raccord autorisé revérifié : ZIP SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`. Fichieroffline matérialisé en copie temporaire par le patch validé après `git apply --check`. Suite `python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism -q` :66/66. Aucun appel payant.

Limites d'accès rencontrées : les URL de collection workflows et de détail d'artefact sont rejetées par le connecteur ; lecture réussie par contents, runs/jobs et catalogue du run. Ce rejet n'a pas été assimilé à un404d'artefact. La dernière tentative de détail n'a donc pas confirmé une suppression individuelle.

Reproduction du diagnostic depuis une copie de cette branche :
```sh
PYTHONPATH=09_INFRASTRUCTURE_AGENTIQUE/prism python 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_trials/audit_upload_log.py job.log
```
Harnais SHA-256 `b8e464095130e9b85e863cf38036691c1ffa26030065ab23cad2b98500cb1cda`.

Prochain test décisif : sélectionner en amont un workflow dont les fichiers cibles sont encore archivés et dont la source ne les nettoie pas, puis exiger une trace d'écriture exploitable avant génération. Aucun nouvel inventaire du même run sans pièce supplémentaire. Prochain cycle alterné : mathématique.
