# Audit en lecture seule des journaux de la PR #81 — 15 novembre 2026

## Source vérifiable

Workflow GitHub Actions existant (exécuté le 13 novembre 2026, sans aucune relance pour ce pilote) :
https://github.com/Abrasax63/Omega-pub/actions/runs/43489499229

Les jobs suivants ont été consultés via les journaux GitHub :

- `132106598273` — `provenance-lab-corpus (build)` : commande Python écrivant `build-a.json`; commande `cp original.json evidence/build-b.json`; mêmes SHA-256 affichés.
- `132106598116` — `provenance-lab-corpus (reserved)` : `reserved-a.json` et `reserved-c.json` sont des copies de `original.json`; `reserved-b.json` est produit par une commande Python ; les trois affichent le même SHA-256.
- `132106598355` — `provenance-lab-install (build)` : `install` crée `train.json`.
- `132106598328` — `provenance-lab-install (reserved)` : traces de `install` et de `cp` sur des fichiers, avec écriture successive de `conflict.json`.

Sur ces cinq sorties du corpus (build et reserved), le SHA-256 affiché est le même :
`b390d063dd02f23ec6bfa1ccb02f64cdae46f1af2b2c33596b9929a91b8e1747`.

## Constat

Une empreinte identique ne permet pas de déduire si un fichier est recopié ou recalculé. Les commandes visibles distinguent ici ces opérations, mais elles correspondent à un corpus **construit par le workflow** : ce ne sont pas des reproductions scientifiques externes indépendantes. Les jobs sont distincts, mais les calculs peuvent utiliser exactement le même code et la même expression.

Les journaux ne sont pas eux-mêmes une attestation complète de l'ascendance des fichiers. La requête des artefacts de ce run a retourné **aucun artefact publié**. Le prototype `lineage_pilot.py` ne sait pas encore transformer de manière authentifiée ces logs en graphes `recompute/copy` : notamment `original.json` est écrit par une commande `printf` (ni `recompute` ni `copy` au sens strict du pilote), et `conflict.json` présente plusieurs écritures.

**Verdict de transfert réel : indéterminé / ADAPTER_ABSENT.** Nous avons inspecté des journaux existants ; nous n'avons pas exécuté le nouveau pilote sur des entrées brutes authentifiées. Le gain sur les journaux réels n'est pas démontré.

## Prochaine vérification qui peut réfuter l'hypothèse

1. Construire, à partir du collecteur existant de la PR #81, un adaptateur en lecture seule avec `source`, `recompute`, `copy`, `multi_writer`, en conservant les références exactes aux journaux.
2. Faire vérifier par une seconde méthode les liens parent/enfant, puis comparer à budget de lectures égal le sélecteur actuel, une règle fixe forte et le nouveau pilote. Les cas non résolus donnent `indetermine`.
3. Geler des journaux indépendants des exemples ci-dessus **avant** de mesurer un éventuel gain ; la PR #83 ne peut émettre qu'une recommandation pour revue, jamais une certification.

Aucune authentification cryptographique des `run_id` et aucune indépendance scientifique n'ont été établies dans cette revue.
