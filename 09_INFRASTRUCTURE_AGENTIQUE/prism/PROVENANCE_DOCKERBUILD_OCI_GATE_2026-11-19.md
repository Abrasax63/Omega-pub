# Provenance — inventaire OCI d'un historique dockerbuild

19 novembre 2026, 04 h 41 (Paris). **EXÉCUTÉ pour l'inventaire / INDÉTERMINÉ pour la classification.** Branche `work/omega-provenance-lab`, SHA initial [8fdb14445942c9637cb3528797833191f96473b8](https://github.com/Abrasax63/Omega-pub/commit/8fdb14445942c9637cb3528797833191f96473b8). Dernier cycle mathématique : [2c21aed](https://github.com/Abrasax63/Omega-pub/commit/2c21aed9d6f6355594acf436a2e75827d3dae24f). Suite du contrôle frontend précédent : même run, nouvelle pièce et nouvelle question, aucun nouveau workflow revendiqué.

Question et budget fixés avant ouverture dans [le protocole](provenance_trials/dockerbuild-prereg-2026-11-19.md) : un historique dockerbuild fournit-il une trace d'exécution et une vérité terrain de fichier indépendante ? Budget : une archive, ses métadonnées, le Dockerfile épinglé ; aucun téléchargement d'image ni exécution de contenu. Critère d'admissibilité : sources/destinations, identifiants et fin des étapes, et vérité terrain du fichier séparée. Une étape réussie ou une instruction COPY isolée ne suffit pas.

[Run externe 44361953379](https://github.com/moby/buildkit/actions/runs/44361953379), artefact [14456617425](https://github.com/moby/buildkit/actions/runs/44361953379/artifacts/14456617425), `moby~buildkit~O48UUG.dockerbuild`. Catalogue GitHub relu, taille 164 830 octets. SHA-256 téléchargé `db060b97d065f70308fb0d43450b4427d534c8e9fa9d2a16369cc285bd574df9`, identique au catalogue.

L'archive servie est gzip/tar au format OCI, malgré le nom ZIP demandé au téléchargement. L'essai initial de lecture ZIP a échoué avec BadZipFile ; identification gzip puis lecture tar en mémoire, sans extraction, ont permis le contrôle. Huit fichiers réguliers, six blobs SHA-256 tous vérifiés. L'historique indique 135 étapes terminées sur 135, dont 48 en cache. Présence de journaux `application/vnd.buildkit.status.v0` (147 408 octets, deux trames à longueur préfixée), de traces OTLP et d'une attestation. Les trames ne sont pas décodées en opérations dans cette expérience : aucune conclusion sur leur contenu sémantique.

Point important : le contexte du build est `f9fb55d56731aad70d6cf9ab4a8b02e4f2db16b5`, distinct de la révision du workflow `3babd403e220cc3b9e416db3240de0d800aed6d1`. [Dockerfile du contexte réel](https://github.com/moby/buildkit/blob/f9fb55d56731aad70d6cf9ab4a8b02e4f2db16b5/Dockerfile), SHA-256 `8e6f2c167d9a70981310b33972a0c6b0a579c6be001b3e6e5fb56e1049ddd5f1`, consulté séparément. Il définit la cible `integration-tests`, déclarée dans l'historique. Le SHA du workflow ne doit donc pas être substitué au SHA du contexte construit.

Obstacle concret : le manifeste de l'image résultat référence 34 blobs (configuration et couches), tous absents de cette archive d'historique. Aucun contenu de fichier résultat n'a donc été vérifié indépendamment. L'inventaire établit la présence d'un historique, pas une vérité terrain de dernier écrivain. Une attestation et un taux de succès d'étapes ne remplacent pas ce contrôle.

**Cycle sans expérience nouvelle de classification** : aucune paire de manifestes entraînement/réserve admissibles ; `propose`/`check` non appelés, aucune réserve annotée transmise, métriques TP/FP/FN/candidat/règle fixe non mesurées. Référence conservée, aucun candidat classificateur retenu, aucun gain externe. Nouvel outil d'inventaire conservé uniquement comme diagnostic reproductible.

Raccord hors ligne : ZIP autorisé SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd` revérifié ; `provenance_offline.py` matérialisé par le patch validé dans une copie temporaire après `git apply --check`. `python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism -q` : 66/66 tests. Aucun workflow lancé, aucune API payante.

Reproduction :
```sh
python 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_trials/audit_dockerbuild.py archive.dockerbuild
```
Harnais SHA-256 `1c3c9d4ddb2ac5987092e653c57403c6ec935f75f9f4cbce5a950b181bbe1222` ; [métadonnées observées](provenance_trials/dockerbuild-metadata-2026-11-19.json).

Prochain test décisif : sélectionner une sortie publique dont le contenu est archivé indépendamment de l'historique, puis décoder la trace native sur contrat fixé. Ne pas multiplier les seuls inventaires du même format sans vérité terrain. Prochain cycle alterné : mathématique.
