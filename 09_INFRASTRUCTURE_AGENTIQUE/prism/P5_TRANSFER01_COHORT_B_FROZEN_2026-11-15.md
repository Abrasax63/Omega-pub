# P5-TRANSFER-01 — cohorte B gelée après construction du candidat

**Séquence et intégrité** — Le pré-enregistrement initial est au commit `0adcb00eca0b40f86fa03779087152d556c8d9ea`. Les journaux C1/C2/D1/D2 du lot initial ont été consultés **avant** la matérialisation du candidat : ce lot est reclassé **exploratoire**, il ne peut pas établir le critère primaire. Ne pas le renommer rétrospectivement « aveugle ».

Le candidat `provenance_cycle.propose()` obtenu depuis l'unique exemple ancien `cp original.json result.json` a été gelé au commit `06528cdc525be3c9b6f7bf6fcf33520bed47527c`. Référence déclarative vide ; règle apprise : `cp → copie`. Il s'agit d'un **constructeur déterministe de règle**, pas d'un modèle LLM. Aucun des journaux B n'a été lu lors de cette fixation.

## Cohorte B de transfert : identifiants choisis d'après les métadonnées, avant lecture des logs

| Id | Dépôt / checkout | Job GitHub pré-sélectionné | Sortie demandée |
| --- | --- | --- | --- |
| C3 | curl/curl `f49c9c95bc31643518b86249e2a7f014699df305` | [Source 43679197664 / 132705913199](https://github.com/curl/curl/actions/runs/43679197664/job/132705913199) — CM integration macos-latest | `source.tar.gz` |
| C4 | curl/curl même checkout | [Linux 43679197809 / 132705914296](https://github.com/curl/curl/actions/runs/43679197809/job/132705914296) — CM awslc | `src/curl` |
| D3 | docker/build-push-action `562e51947939164e4fe808a6eab5101977e509e0` | [CI 43583601993 / 132413316807](https://github.com/docker/build-push-action/actions/runs/43583601993/job/132413316807) — provenance image | `localhost:5000/name/app:latest` (cible image hors du domaine de l'extracteur fichiers : abstention attendue) |
| D4 | docker/build-push-action même checkout | [CI 43583601993 / 132413316717](https://github.com/docker/build-push-action/actions/runs/43583601993/job/132413316717) — example | `/tmp/buildx-build` (contrôle négatif, présence incertaine) |

Les méthodes, les limites et l'oracle restent ceux du pré-enregistrement initial : même journal complet pour tous, une seule pièce lue par chacune dans le test actuel, comparateur fixe `provenance_xtrace.fixed_verdict`, maximum deux pièces si vérification de la source nécessaire, aucun ajustement des parseurs avant notation. **Un log réussi ne suffit jamais à établir copie ou recalcul d'une cible.**

Les deux premiers jobs appartiennent à la même famille / même checkout ; les deux derniers appartiennent aussi au même run. L'échantillon ne constitue pas quatre reproductions indépendantes. Si aucune extraction complète n'est possible, enregistrer zéro couverture et un résultat négatif de transfert brut, sans bricoler un nouvel extracteur après coup. Toute nouvelle heuristique serait une étude exploratoire distincte.

Les verdicts doivent être comparés à la preuve de la commande effective et au script épinglé ; aucune inférence d'identité d'octets depuis la réussite CI. Aucune promotion CORE ni fusion `main`.
