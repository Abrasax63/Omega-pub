# P5-TRANSFER-01 — résultat de lecture des journaux inédits (15 novembre 2026)

**STATUT : observation réelle, échec de couverture ; pas de gain adaptatif démontré.**
Branche `experiment/provenance-transfer-2026-11-15`, non fusionnée. Les journaux ont été lus en lecture seule à travers le connecteur GitHub. Aucun workflow ni nouvel appel modèle n'a été déclenché. Le runner de rejeu est ajouté mais **n'a pas été exécuté dans GitHub Actions** à la rédaction de ce rapport.

## Discipline temporelle

- L'échantillon C1/C2/D1/D2 du pré-enregistrement initial a été observé **avant** fixation du candidat : résultats **exploratoires uniquement**.
- Le candidat de `provenance_cycle.propose` est enregistré au commit `06528cdc525be3c9b6f7bf6fcf33520bed47527c`, après un seul exemple ancien `cp original.json result.json`. Son unique règle : `cp → copie`. Baseline déclarative `[]`.
- Les identifiants, noms et cibles de la cohorte B ont ensuite été gelés au commit `514eee9c516f26978a03990ea279a6fc73432062`, **avant** ouverture de leurs logs. Les extracteurs `extract` et `extract_buildkit_copy` et le comparateur déterministe `fixed_verdict` sont ceux de la PR #81.
- Les octets d'origine des fichiers GitHub ne sont pas conservés dans la branche. Les empreintes ci-dessous sont celles du **texte renvoyé par le connecteur, réencodé en UTF-8** ; ne pas les confondre avec un hash natif d'archive GitHub.

## Résultat par job : lecture du journal complet, sans extrait privilégié

| Cas | Taille UTF-8 | SHA-256 du texte décodé | Indice du journal | Règle construite / fixe |
| --- | ---: | --- | --- | --- |
| [C3 curl CM macos](https://github.com/curl/curl/actions/runs/43679197664/job/132705913199) | 325 554 | `75f232165ae3490fed42650e3e1f8cd0b64dac6c517b1a45bbbd86add08c3722` | `source.tar.gz` dans les étapes CMake ; 0 commande `+ cp`/ `install -m` et 0 événement BuildKit `+ cp -av` reconnu | indéterminé / indéterminé |
| [C4 curl CM awslc](https://github.com/curl/curl/actions/runs/43679197809/job/132705914296) | 2 827 920 | `b61b073c9b72a7eafadcd308e703b7a2c494bef2a72122273ca3b3f088fa5e1e` | Commande de liaison `-o src/curl` ; 0 commande reconnue par les deux extracteurs figés | indéterminé / indéterminé |
| [D3 Docker image](https://github.com/docker/build-push-action/actions/runs/43583601993/job/132413316807) | 154 937 | `bb7d09877f44e036503e014480673bff3098ca4f18bf876dadf1fa1dc7e06467` | `docker buildx build --output type=image`, hors domaine de l'extracteur de fichiers | indéterminé / indéterminé |
| [D4 Docker example](https://github.com/docker/build-push-action/actions/runs/43583601993/job/132413316717) | 196 430 | `d7e0f403529cdb0d69462f657eb5eb538992c229c1e45bb90c3c1a5033c5818d` | Aucune occurrence de `/tmp/buildx-build` dans le journal ; absence non probante | indéterminé / indéterminé |

**Bilan de couverture d'extraction**, 4 jobs sélectionnés, **0 verdict déterminé / 4 abstentions** pour le candidat construit et pour le comparateur fixe. Chaque bras a accès au même journal complet : **1 pièce lue sur un budget maximum de 2**. Ce résultat découle de l'inspection des marqueurs que reconnaissent précisément les extracteurs figés, et non d'un rejeu automatisé certifié du runner contre les fichiers complets dans l'environnement GitHub. Ne pas annoncer un résultat CI avant un run contrôlé.

Le [script curl épinglé](https://github.com/curl/curl/blob/f49c9c95bc31643518b86249e2a7f014699df305/tests/cmake/test.sh#L33) utilise `git archive | gzip > source.tar.gz`, et le log C3 indique l'utilisation du fichier ; le [CMakeLists épinglé](https://github.com/curl/curl/blob/f49c9c95bc31643518b86249e2a7f014699df305/src/CMakeLists.txt) et le journal C4 étayent la liaison de l'exécutable. Ces indices suggèrent des méthodes de recalcul sur ces cibles mais **ne constituent pas une vérification d'identité d'octets ni un oracle complet**. Le verdict D3 est hors du domaine fichier ; D4 reste non attesté. Aucun succès de raisonnement ne peut être compté.

## Interprétation et prochaine vérification décisive

1. **RÉFUTÉ sur ces quatre cas :** le candidat simple `cp` et les extracteurs figés suffisent à fournir un verdict de provenance déterminé. **Aucune plus-value sur la règle fixe**.
2. **INDÉTERMINÉ :** capacité de transfert générale, fiabilité de la provenance sur une famille inconnue, gain sur un comparateur classique complet. Deux paires de jobs d'une même famille ne constituent pas quatre réplications indépendantes.
3. **À tester séparément, sans réécrire les scores :** construire un extracteur déclaratif pour la chaîne `git archive | gzip` et la liaison CMake **uniquement sur un jeu d'entraînement différent**, puis geler ce candidat et l'appliquer à de nouveaux jobs sélectionnés avant lecture. Comparer à une règle CMake fixe identique en puissance et budget.
4. **Pas de promotion** : `main` inchangée ; conserver candidat, références, échecs et garde SHA. Les sept nouveaux tests du runner sont ajoutés dans la branche, **mais leur exécution CI sur celle-ci n'est pas confirmée**.

## Rejeu sous contrôle du lecteur

Placer exactement les quatre journaux complets sous `C3.log`, `C4.log`, `D3.log`, `D4.log` dans un dossier `logs/`, sans édition. Avec un accès GitHub Actions autorisé, l'API `GET /repos/{owner}/{repo}/actions/jobs/{job_id}/logs` donne le contenu. Vérifier les empreintes ; si l'API livre une autre représentation, consigner la différence et ne pas la remplacer silencieusement.

Depuis le dossier `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```bash
python -m unittest -v test_provenance_transfer01
python provenance_transfer01.py logs P5_TRANSFER01_CANDIDATE.json P5_TRANSFER01_BASELINE.json
```

Le runner impose les 4 IDs, la règle et les SHA textuels et ne note pas de gain sans un oracle indépendant. Aucune mutation des anciennes PR ni promotion CORE.
