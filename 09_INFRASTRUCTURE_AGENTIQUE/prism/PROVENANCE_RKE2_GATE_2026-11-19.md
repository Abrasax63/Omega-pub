# Provenance — RKE2 PR Build : cp -vf tracé et pièce correspondante non vérifiée

19 novembre2026,vers09h12 (Paris). **EXÉCUTÉ pour collecte et diagnostic / INDÉTERMINÉ pour le gain externe.** Branche `work/omega-provenance-lab`, départ [483f550413b6a64c90d344886d2bacfe01513040](https://github.com/Abrasax63/Omega-pub/commit/483f550413b6a64c90d344886d2bacfe01513040). Dernier cycle mathématique : [fd94055](https://github.com/Abrasax63/Omega-pub/commit/fd940554fabbc026b63fa5e8649fe9ab0f1fcde7).

Question d'admissibilité [fixée avant test](provenance_trials/rke2-prereg-2026-11-19.md) : un workflow externe inédit fournit-il une trace d'écriture réellement exécutée et une pièce de sortie vérifiable séparément ? Exigences : source/destination, fin réussie, vérité terrain de fichier indépendante ; ni instructions affichées ni somme de contrôle seule ne garantissent le dernier écrivain. Budget : un workflow récent, métadonnées, source épinglée et un journal ; un artefact seulement si son lien avec la sortie est établi. Aucun workflow externe lancé.

Nouvelle source : [rancher/rke2,PR Build,run44427352224](https://github.com/rancher/rke2/actions/runs/44427352224),19novembre2026,révision `b234325968529da658580596ed97f02c7ced2755`. [Workflow épinglé](https://github.com/rancher/rke2/blob/b234325968529da658580596ed97f02c7ced2755/.github/workflows/pr.yml), SHA-256 `a97b02ac1088a7567da093dafcabd2666b966218e10b5f540b40a975a6743545`. Job [build-amd64,135371680505](https://github.com/rancher/rke2/actions/runs/44427352224/job/135371680505) terminé avec succès. Son journal a effectivement été téléchargé.

Le journal contient4enregistrements xtrace `+ cp -vf LICENSE dist/bundle/share/rke2/LICENSE.txt`, ainsi que des variantes `install -s`. L'extracteur actuel reconnaît0écrivain pour cette sortie et renvoie `complete=false` ; comparateur fixe indéterminé. [Extraits et résultat](provenance_trials/rke2-extraction-2026-11-19.json). Cette lacune de reconnaissance des variantes est observable, mais reconnaître un drapeau supplémentaire ne prouverait pas à lui seul la couverture de toutes les écritures : plusieurs reconstructions emploient le même chemin dans ce job.

Catalogue GitHub actuel : un artefact non expiré,ID14485312791,`rke2-build-artifacts`,382697359octets. Les chemins déclarés à l'upload sont `build/images/rke2-images.linux-amd64.tar.zst` et `build/images/rke2-test-*.tar`. La sortie tracée est dans `dist/bundle/share/rke2/LICENSE.txt`. L'archive n'a pas été téléchargée ou inspectée : je ne peux pas confirmer qu'un fichier correspondant existe à l'intérieur de ses images imbriquées. Aucun lien indépendant entre cette sortie et une pièce archivée n'est donc établi à ce budget. Ne pas qualifier cet artefact d'absent ni son contenu de vérifié.

**Cycle sans expérience nouvelle de classification admissible.** Aucun manifeste d'entraînement/réserve établi, aucune étiquette déduite uniquement du nom cp, aucun `propose/check` lancé sans pièces admissibles. Métriques TP/FP/FN et comparaison candidat/référence non mesurées. Une abstention de diagnostic, pas un gain externe. Aucune correction de parseur retenue ; référence inchangée. Le diagnostic réutilisable est conservé.

Raccord hors ligne : ZIP autorisé SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd` revérifié ; fichieroffline matérialisé en copie temporaire par le patch validé après `git apply --check`. `python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism -q` :66/66. Pas d'appel payant.

Journal décodé normalisé (fin de fichier retirée puis unLF),624592octets,SHA-256 `94189c14c46ad25c04574e78862b02551151068dc4e357aa82bc67b0d0c765c5`. Seuls des extraits ciblés sont conservés dans la branche. Reproduction :
```sh
PYTHONPATH=09_INFRASTRUCTURE_AGENTIQUE/prism python 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_trials/audit_rke2_log.py job.log
```
Harnais SHA-256 `24333f0a367742931f220faef6bdd8294f2ceee06be1cfd91c2a15741a9c0ef1`.

Prochain test décisif : établir un chemin vérifiable entre une entrée des images archivées et une invocation de copie précise, avec source épinglée et frontières de reconstruction. À défaut, changer de workflow en exigeant un fichier directement archivé. Aucun gain annoncé sur la simple présence de cp dans les logs. Prochain cycle alterné : mathématique.
