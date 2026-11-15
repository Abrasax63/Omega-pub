# P5-INDUCE-01 — résultat, transfert inter-projets et réfutation d'une généralisation

**Date : 15 novembre 2026 — STATUT : OBSERVATION EMPIRIQUE BORNÉE ; avantage propre Omega NON DÉMONTRÉ.**

## Objets réellement disponibles

- Pré-enregistrement avant holdout : [P5_INDUCE01_PREREG_2026-11-15.md](P5_INDUCE01_PREREG_2026-11-15.md).
- Programme de construction déclarative : [provenance_induce01.py](provenance_induce01.py), blob Git `e11b877994cc32cc10ec24ac1cba58aa28ddecd4`.
- 17 tests adversariaux : [test_provenance_induce01.py](test_provenance_induce01.py), blob Git `92fb8fcade52c920c94eff58bfec789f725be709`.
- Un exemple historique d'entraînement : [P5_INDUCE01_TRAIN.json](P5_INDUCE01_TRAIN.json), job fzf 130466140326, checkout `314cbe1be73849921ce7beb614ce674fae1515b3`.
- [Gel du constructeur et du comparateur avant lecture](P5_INDUCE01_FREEZE_2026-11-15.md) ; [amendement de préflight](P5_INDUCE01_PREFLIGHT_AMENDMENT.md), effectué avant toute ouverture des H1–H5.
- [Manifeste H1–H5 avec empreintes SHA-256 du texte UTF-8 décodé](P5_INDUCE01_HOLDOUT_MANIFEST.json) ; [lignes de preuves](P5_INDUCE01_HOLDOUT_EVIDENCE.json).

Le constructeur analyse une ligne exécutive passée par un sous-ensemble de la grammaire shell, puis induit une règle JSON `{tool: go, verb: build, flag: -o, verdict: construction_signalée}`. La famille de langage Go **n'est pas codée en dur dans `construct`** ; le triplet est extrait de l'exemple d'entraînement. Le comparateur classique `FIXED`, écrit avant lecture, **contient exactement le triplet `go/build/-o`**. Ils partagent le même extracteur et les mêmes preuves.

**Ne pas appeler ce mécanisme un générateur autonome de code Python ou un certificateur d'artefacts : c'est un synthétiseur de règle déclarative, borné à une grammaire d'argument `-o`.**

## Tests effectivement exécutés

Le module et les tests GitHub ont été reconstitués localement **avec les mêmes SHA de blobs Git** (`e11b8779…` et `92fb8fca…`). Commande `python -m unittest -v test_provenance_induce01` : **17 tests sur 17 réussis**, dont les témoins `echo`, `go test`, Rust, chaîne shell, double option `-o`, cible `/dev/null`, et parité au classique. Un test supplémentaire sur les seules **lignes d'intérêt extraites du holdout** a retrouvé 1 positif H1 et 4 abstentions pour chacun des bras. **Ceci ne constitue pas une exécution Python de bout en bout sur les 5 journaux bruts complets.** Aucun workflow GitHub Actions de cette branche n'a été déclenché ni vérifié.

## Résultats sur cinq jobs GitHub inédits, sélectionnés avant lecture

| Job | Trace observée dans le journal réel | Candidat appris | Classique fixe |
| --- | --- | --- | --- |
| [H1 — fzf build](https://github.com/junegunn/fzf/actions/runs/43137398863/job/130915918123) | `GOARCH=amd64 go build ... -o target/fzf-linux_amd64` ; même dépôt mais nouveau checkout | 1 signal | 1 signal |
| [H2 — Caddy Linux](https://github.com/caddyserver/caddy/actions/runs/43617376109/job/132516131842) | `go build -trimpath -o caddy-\"$GOOS\"-$GOARCH 2> /dev/null` : variable dynamique, redirection et texte de workflow, rejetés par la grammaire figée | Abstention | Abstention |
| [H3 — go-task/task Build](https://github.com/go-task/task/actions/runs/43467995680/job/132032174540) | `go build -v ./cmd/task` sans sortie `-o` explicite | Abstention | Abstention |
| [H4 — Hugo Test Linux](https://github.com/gohugoio/hugo/actions/runs/43645632266/job/132602642451) | Pas de ligne `go build` trouvée ; `go install` figure dans le log, hors contrat | Abstention | Abstention |
| [H5 — ripgrep Test Linux](https://github.com/BurntSushi/ripgrep/actions/runs/43661343801/job/132651135271) | Commandes `cargo build` Rust, pas de `go build` | Abstention | Abstention |

- **Couverture au sens strict :** 1 job reconnu sur 5, et **aucun** des trois projets Go différents de `fzf` reconnu.
- **Contrôle négatif Rust :** pas de fausse reconnaissance de `go build` sur H5.
- **Gain propre au constructeur appris :** **0** job par rapport au comparateur fixe.
- Les abstentions H2 et H3 sont des **limites du langage de reconnaissance**, non des démonstrations qu'aucun logiciel n'a été construit.
- Le critère d'au moins une reconnaissance dans un **projet inconnu** du constructeur est **NON SATISFAIT**. L'hypothèse forte de transfert inter-projets **n'est pas confirmée par cette expérience**.
- Il n'y a pas d'oracle indépendant sur les fichiers produits. Une ligne de commande de build dans un job `success` n'atteste pas l'identité binaire ni l'exclusivité de la provenance.

## Audit de l'absence de fuite

Les cinq IDs ont été gelés au commit `66bdaf7e8a94a6f17bd4fbdedb09f966e458d32e`. Le code a été gelé avant leur ouverture au commit `235044491e74ad004d60c626cd8b2e1cc460b7ba`. La correction `echo` a été effectuée en préflight et enregistrée dans un document distinct. Les journaux réservés n'ont pas été utilisés pour réécrire les paramètres du candidat ni du comparateur. Ils apparaissent uniquement dans les manifestes et ce rapport, déposés après consultation.

## Prochaine réparation rationnelle

La prochaine étude ne doit pas répéter ces mêmes cinq jobs comme « nouveaux cas ». Utiliser H2/H3 **seulement comme diagnostic public** pour concevoir une grammaire plus riche comprenant les arguments de sortie **avec variables shell sous provenance**, et le cas `go build` sans `-o` où la destination est implicite. Construire des exemples d'entraînement issus de jobs différents, puis définir **avant lecture** un nouvel ensemble de jobs sur de nouveaux checkouts et projets. Une heuristique classique équivalente doit conserver le même budget de preuves et servir de référence forte.

**Statut final :** nouveau constructeur et preuve de tests locaux reproductible ; transfert à `fzf` postérieur constaté ; **aucun gain démontré sur les trois projets Go inconnus ni sur le classique**. Pas de promotion CORE, pas de fusion de `main`, pas de workflow externe déclenché.
