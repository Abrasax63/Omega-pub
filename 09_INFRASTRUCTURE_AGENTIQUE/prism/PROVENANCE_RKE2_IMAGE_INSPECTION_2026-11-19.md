# Provenance — inspection effective des images RKE2 archivées

19 novembre 2026, vers 11 h 22 (Paris). **EXÉCUTÉ pour l'inspection / INDÉTERMINÉ pour la classification.** Branche `work/omega-provenance-lab`, départ [7373a96bee006ee06be75d05c0a52ab062dfe644](https://github.com/Abrasax63/Omega-pub/commit/7373a96bee006ee06be75d05c0a52ab062dfe644). Dernier cycle mathématique [c804fde](https://github.com/Abrasax63/Omega-pub/commit/c804fde07ddcc6d659d140054ad981279fea1abc). Suite distincte du diagnostic précédent : téléchargement et lecture réels des pièces, sans nouveau rejeu des journaux ni revendication de workflow inédit à ce passage.

Question [fixée avant ouverture](provenance_trials/rke2-image-prereg-2026-11-19.md) : retrouver dans l'artefact la licence correspondant à `dist/bundle/share/rke2/LICENSE.txt`, puis établir un rattachement à une invocation de copie ? Contrôle négatif : une licence générique de même nom ou empreinte ne prouve pas le dernier écrivain. Budget : uneZIP<600Mo,moins de2Go de tailles de fichiers déclarées dans les couches parcourues,60s d'inspection. Aucune image exécutée, aucune écriture dans un registre.

[RunRKE2 44427352224](https://github.com/rancher/rke2/actions/runs/44427352224), artefact14485312791 `rke2-build-artifacts`, non expiré lors de la nouvelle lecture du catalogue. Archive effectivement téléchargée :382697359octets,SHA-256 `46be77b612b549bbdc918193b9238d2b013b0c010a135253fef80cc59d142e48`, identique au catalogueGitHub.

Deux membresZIP : `rke2-images.linux-amd64.tar.zst` (105034756octets) et `rke2-test-v1.37.2-dev.20e65d1c-amd64.tar` (279279616octets). Ils ont été préparés comme fichiers de données. Les manifestesDocker et leurs couches référencées sont lus sans extraction de leur système de fichiers ; les empreintesSHA-256 des neuf blobs de couches sont vérifiées avant lecture. Tous les manifestes du second ensemble sont parcourus, avec déduplication des références de couches.

[SourceLICENSE épinglée](https://github.com/rancher/rke2/blob/b234325968529da658580596ed97f02c7ced2755/LICENSE),10174octets,SHA-256 `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`. Les octets UTF-8 obtenus du connecteur ont été matérialisés exactement avant comparaison.

| Ensemble inspecté | Couches | Tailles déclarées parcourues | Candidats de licence réguliers<100ko | Chemin contenantrke2 | Empreinte source retrouvée |
| --- | ---: | ---: | ---: | ---: | ---: |
| Image de test | 8 | 564036126 | 121 | 0 | 0 |
| Images runtime | 1 | 324922059 | 0 | 0 | 0 |

Total888958185octets déclarés dans les couches parcourues,2,555s et1,457s d'inspection mesurée. Aucun bundle imbriqué nommérke2 en tar.gz/tgz n'a été rencontré par le chercheur borné. Périmètre précis : fichiers réguliers dont le chemin contientlicense et la taille est<100000octets ; pas de reconstruction du système de fichiers final, de résolution des symlinks ni de preuve d'absence dans tout emballage possible. Les temps excluent téléchargement et préparation des fichiers externes.

Résultat nouveau : aucun candidat correspondant au chemin ou à l'empreinte recherchés dans ce périmètre réellement inspecté. Je ne peux pas confirmer une correspondance au fichier de la trace. Les121licences génériques ne sont pas promues en vérité terrain de dernier écrivain. Le lien entre sortie, invocation précise et archive reste donc non vérifié.

**Cycle sans expérience nouvelle de classification admissible.** Pas de manifestes entraînement/réserve, pas de propose/check sans vérité terrain indépendante ; métriquesTP/FP/FN et gaincandidat non mesurés. Référence conservée, aucun candidat classificateur retenu, aucun gain externe. L'inspecteur et les empreintes sont conservés pour éviter de refaire cet inventaire.

Raccord hors ligne : ZIP autorisé revérifié SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`, fichieroffline matérialisé par le patch validé en copie temporaire après `git apply --check`. Suiteprism66/66. Aucun workflow lancé ni appel payant.

Reproduction : télécharger l'artefact public ci-dessus, extraire uniquement ses deux membres nommés dans des fichiers temporaires fixes, décompresser le membre.zst en tar avec zstandard, puis :
```sh
python 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_trials/inspect_rke2_image.py test-image.tar
python 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_trials/inspect_rke2_image.py runtime-images.tar
```
Pour reproduire le budget cumulatif exécuté, réduireMAX_BYTES du second appel de564036126octets. L'inspecteur utilise la bibliothèque standard ; seule la préparation.zst utilise zstandard. Aucun tar n'est exécuté ni extrait en arborescence.

Harnais SHA-256 `8389571c1dc647c99994bfb146213afe273ad53db80ca768d8bb5a563ea30cec`. [Synthèse des pièces](provenance_trials/rke2-image-summary-2026-11-19.json), SHA-256 `cc0615879e330fb6bd9d3f6b1c0c6fa44b05bb21fa52b01307e8591b2d4c2844`.

Prochain test décisif : changer de cible et sélectionner un fichier directement archivé avec la trace de son écriture, plutôt que réinspecter ces images sans nouveau lien de sortie. Les deux inventaires de ce même artefact sont désormais documentés. Prochain cycle alterné : mathématique.
