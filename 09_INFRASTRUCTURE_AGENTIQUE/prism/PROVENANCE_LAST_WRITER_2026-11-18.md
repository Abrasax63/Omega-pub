# Provenance Bash — l’empreinte finale et le dernier écrivain

18 novembre 2026, 05 h 58 (Paris). Branche `work/omega-provenance-lab`, base `69bbcef13463b8e5a1fc055052d618a79572e15d`. [Cycle précédent](PROVENANCE_DESTINATION_EVIDENCE_2026-11-18.md). Dernier [cycle mathématique](https://github.com/Abrasax63/Omega-pub/commit/dd040e7d98140d70b31c61fe227b97ae68305b8a).

Hypothèse réfutable : une copie tracée et un fichier régulier de même empreinte suffisent à attribuer la dernière écriture à cette copie. Protocole avant test : un Bash réel exécute cp puis printf avec redirection. Trois cas, dont deux contrôles où la redirection vise un autre fichier. Le témoin contradictoire redirige vers la cible, en réécrivant les mêmes octets. La destination de la redirection est fixée par les arguments du script, séparément du journal. Le critère de réfutation exige une fausse confirmation de l’écriture unique. Comparer les méthodes sur les mêmes journaux, puis mesurer l’effet d’un relevé de fichier supplémentaire.

**RÉFUTÉ en environnement local contrôlé.** Le contrôle et la contradiction ont des journaux identiques (SHA-256 `5e8c7081dfab57f936e84c45a83e3a60494cf68c6d238be1f1b9b330d56a2689`) et le relevé donne la même correspondance de contenu dans les deux cas. La redirection ne figure pas dans le xtrace. La référence déclarative explicite vide donne trois abstentions. Le candidat cp et la règle fixe, avec un journal chacun, donnent chacun deux confirmations correctes et une fausse. L’ajout du relevé au candidat donne les mêmes chiffres. À deux pièces, appliquer le même contrôle au fixe produit le même résultat car ses trois verdicts initiaux et les relevés sont identiques. Aucun gain, référence conservée. Aucun workflow externe inédit évalué.

Le raccord a été appliqué dans une copie temporaire après `git apply --check`, archive SHA-256 `c44e59eee9ba17160c0eaf36e6b883e330b65dcb7f95d1b39094411eacc50ffd`. Commandes depuis la racine de cette copie :

```sh
p=09_INFRASTRUCTURE_AGENTIQUE/prism
mkdir eval
printf '[]\n' > eval/base.json
python3 "$p/provenance_trials/audit_bash_destination.py" eval train
python3 "$p/provenance_offline.py" propose eval/base.json eval/train.json eval/proposal.json
export PYTHONPATH="$p:$p/provenance_trials"
python3 "$p/provenance_trials/audit_last_writer.py" generate eval
python3 "$p/provenance_offline.py" check eval/base.json eval/reserved.json eval/proposal.json
python3 "$p/provenance_trials/audit_last_writer.py" evaluate eval
python3 -m unittest discover -s "$p" -q
```

Les 24 tests passent avant et après. Check local : 0,035 s. SHA-256 : harnais `07f86a4110bbd8820410d07a0e67f68c996e7be7667635cd8ad36e1ef5b7ea5f`, proposition `2d5b50a0439f6034cc0fd377b3e6946bcb7aec6dd18b4e3429e32d259002a49a`, réserve `94a997a251a5278064bce312b5596e3eff36dcd33f4dfce1c69a72f6aca04f6c`, résultat `9626e934aa630d6a253e6e479227ac9601f664fa580955f17740e0871238e8d6`.

Prochain test de provenance : obtenir une pièce archivée attribuant les écritures au processus et au chemin exact, puis tester son aptitude à distinguer une réécriture à octets constants. Prochain cycle : mathématique.
