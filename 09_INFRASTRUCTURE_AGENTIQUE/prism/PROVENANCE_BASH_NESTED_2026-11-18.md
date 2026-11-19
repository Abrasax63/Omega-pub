# Provenance Bash — traces de commandes imbriquées

18 novembre 2026 à 00 h 21 (Paris). Branche `work/omega-provenance-lab`, SHA initial `896bf61d692653a7fe4e94330867695ce8b9669c`. Suite du [dernier cycle Bash](PROVENANCE_BASH_MOVE_2026-11-17.md), après le [cycle mathématique](https://github.com/Abrasax63/Omega-pub/commit/c240368939929e878c15da787b25d0475223b36d).

Hypothèse réfutable : ignorer les lignes précédées de plusieurs signes + laisse inchangé le verdict d’écriture unique. Lot synthétique fixé avant le test : copie ordinaire suivie d’une copie imbriquée vers la même cible, copie imbriquée seule, copie ordinaire suivie d’une copie imbriquée vers un autre chemin. Une lecture du même journal par méthode. Critère : zéro fausse confirmation, deux copies correctes, une abstention. Portée : étape Bash dédiée réussie avec préfixe xtrace de type +, sans résolution des chemins.

Raccord hors ligne vérifié par SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`. Patch appliqué à une copie temporaire après `git apply --check`. Référence déclarative explicite `[]`. Le candidat a appris `cp → copie` sur une trace ordinaire avant lecture de la réserve. Le changement expérimental reconnaît aussi les lignes à plusieurs signes + dans l’extracteur.

```sh
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_offline.py propose eval/base.json eval/train.json eval/proposal.json
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_offline.py check eval/base.json eval/reserved.json eval/proposal.json
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism/ -q
```

**RÉFUTÉ sur contrôles synthétiques.** Référence déclarative : 0 confirmation correcte, 0 fausse, 3 abstentions. Candidat et règle fixe avant : 1 correcte, 1 fausse, 1 abstention. Après : 2 correctes, 0 fausse, 1 abstention pour les deux. Les 24 tests existants passent avant et après. La règle fixe utilise le même extracteur. Les archives disponibles recensées recoupent des dossiers connus ou des extraits sans preuve séparée de la copie imbriquée. Aucun workflow inédit admissible évalué. Référence active conservée et patch archivé.

SHA-256 : entraînement `849b83a466d82699dfb38478debd4c952fc3db96be70185916cf27e835876b7e`, proposition `e0bd10e92b10c8748e34e19bc589210541346da573ce2d8cc54d3b0439b16705`, évaluation `b39681afda902f8656c12181f8ec7ec6eb6d3c77ba286d67a976e92b11a686fd`, avant `6bc79abda0717c441a0b645b084acb870005b51702ab08ffacc5830a1e85b33d`, après `ca858c3f448b0c8e294c622175101255b40e649e2b0aeca6fca43d63f87b36ed`, patch `306500c74bb0e393f4691389770a8d50682a64320200b488c24fe132058f0852`.

Prochain test de provenance : fixer indépendamment la cible et le format PS4 d’un workflow archivé puis vérifier une copie imbriquée réelle. Prochain cycle de l’alternance : mathématique.
