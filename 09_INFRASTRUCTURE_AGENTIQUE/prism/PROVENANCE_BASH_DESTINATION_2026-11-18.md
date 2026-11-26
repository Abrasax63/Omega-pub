# Provenance Bash — la destination peut être un répertoire

18 novembre 2026, 02 h 21 (Paris). Branche `work/omega-provenance-lab`, SHA initial `53e17b507955d778dc829338a9308949741254f6`. [Dernier cycle de provenance](PROVENANCE_BASH_NESTED_2026-11-18.md) et [cycle mathématique](https://github.com/Abrasax63/Omega-pub/commit/4cd7af516c1bda7c6d955fd7764c8dcdf4e8f1a0).

Hypothèse réfutable : le journal Bash seul suffit à attribuer la copie au chemin exact `output`. Protocole fixé avant test : exécuter le même `cp source output` une fois avec cible absente, une fois avec un répertoire à ce chemin. Ajouter une copie distincte positive. Vérifier le type de la cible et les octets au chemin réel séparément du journal. Budget égal : un journal par verdict. Critère de réfutation : journaux identiques et destinations effectives différentes. Seuil de rétention du candidat : zéro fausse confirmation et deux confirmations correctes.

**RÉFUTÉ sur exécutions locales contrôlées.** Les journaux des deux cas sont identiques (SHA-256 `ea99fee145f91926757049291343c8e739ad0af09a1e4e45402a96b0266ede70`). La copie crée `output` dans le premier cas et `output/source` dans le second. Les octets lus correspondent à la source. Le raccord propose `cp → copie` sur la trace d’entraînement avant génération des pièces réservées. Sur les trois cas, référence déclarative vide : 0 confirmation, 0 fausse confirmation, 3 abstentions. Candidat et comparateur fixe : 2 confirmations correctes, 1 fausse, 0 abstention. Candidat écarté, référence conservée. Le contrôle utilise un Bash réel et des fichiers temporaires. Aucun workflow externe inédit admissible évalué.

Archive hors ligne vérifiée au SHA-256 demandé `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`. Application temporaire après `git apply --check`. Depuis la racine de cette copie, avec un dossier eval neuf :

```sh
mkdir eval
printf '[]\n' > eval/base.json
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_trials/audit_bash_destination.py eval train
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_offline.py propose eval/base.json eval/train.json eval/proposal.json
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_trials/audit_bash_destination.py eval reserved
python3 09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_offline.py check eval/base.json eval/reserved.json eval/proposal.json
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/prism/ -q
```

Les 24 tests passent. Le check prend 0,031 s en local. SHA-256 : harnais `0dd0862cefc4b625b9cb9a13d3488f3ca15adc5e88ffe629f1e024ec2a2ba6d7`, entraînement `ef028084f1c3c6024b150f2ca724cac83c4243459b50e8be689146ad5d25e92c`, proposition `2d5b50a0439f6034cc0fd377b3e6946bcb7aec6dd18b4e3429e32d259002a49a`, réserve `910d09765fa3d1199ac5911d6a63346a0e291a28f7678c130a65dfa6d71d436b`, rapport `110cf8deb1139afcc0d21fbf3762bd5fb197d48d64d65209ff591372315408a2`.

Prochain test de provenance : confronter le journal à une pièce indépendante qui atteste le chemin effectif d’écriture, puis mesurer le gain sur un workflow archivé inédit. Prochain cycle de l’alternance : mathématique.
