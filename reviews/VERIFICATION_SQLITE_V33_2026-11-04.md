# Vérification technique indépendante de SQLite v33 — 4 novembre 2026

## Objet et méthode

Contrôle en lecture seule du fichier exact matérialisé depuis la bibliothèque ChatGPT :
`/Recherche/00_INDEX_ET_METHODES/RESEARCH_MEMORY.sqlite`, version de bibliothèque 33.

Le fichier a été lu depuis son artefact binaire, puis contrôlé directement avec le moteur SQLite. Aucun INSERT, UPDATE, DELETE, VACUUM ni changement de schéma n'a été exécuté. Aucun statut scientifique n'a été modifié.

## Identité du fichier

- Nom : `RESEARCH_MEMORY.sqlite`
- Version de bibliothèque : 33
- Taille : 819 200 octets
- SHA-256 recalculé : `ef3e9a0de51a44b30599f73f027829751a2eb144e4468175c0f290b5e0159bf4`
- Résultat : identique à l'empreinte consignée dans `RESEARCH_MEMORY_V33_SHA256.txt`.

## Contrôles exécutés

- `PRAGMA integrity_check` : `ok`
- `PRAGMA foreign_key_check` : 0 violation
- Références `result_sources` vers `results` absentes : 0
- Références `result_sources` vers `sources` absentes : 0
- Relations dont une extrémité `results` est absente : 0

## Comptages relus dans le fichier

| Objet | Nombre |
|---|---:|
| `results` | 89 |
| `certified_active_results` | 85 |
| `sources` | 105 |
| `result_sources` (liaisons) | 177 |
| `evidence` | 217 |
| `relations` | 83 |
| dont `DEPEND_DE` | 49 |
| `audits` | 78 |
| `regression_tests` | 62 |
| `unresolved_reviews` | 0 |
| `memory_nodes` | 7 |
| `memory_links` | 8 |
| `memory_snapshot_items` | 7 |

Répartition des 85 résultats de `certified_active_results` :
- 74 `DÉMONTRÉ`
- 11 `CALCUL EXACT`

Répartition des 89 lignes de `results` :
- 74 `DÉMONTRÉ`
- 11 `CALCUL EXACT`
- 1 `INDÉTERMINÉ`
- 1 `REFORMULATION`
- 2 `RÉFUTÉ`

Les 62 tests de régression sont enregistrés avec le statut `PASS` dans la base. **Ils n'ont pas été rejoués** lors de ce contrôle : ce résultat atteste l'état enregistré, pas une nouvelle exécution de chaque test.

Le dernier commit scientifique inscrit dans `meta` est toujours `COMMIT-RAVI2-2026-10-20-TWO-EQUAL-GAPS-25`. Ce contrôle technique ne crée aucun commit scientifique.

## GitHub — état vérifié de la migration

Le dépôt cible est `Abrasax63/Omega-pub`. La branche `migration/ravi2-ccs-public-2026-11-04` est en avance de 132 commits sur `main`, sans retard. La PR #2 est ouverte, en brouillon et non fusionnée. `main` n'a pas été modifiée par cette vérification.

La base SQLite binaire n'est **pas encore présente dans le dépôt GitHub**. La matérialisation et la vérification locale ne valent pas transfert. L'empreinte seule n'est pas une sauvegarde.

## Distinction des verdicts

- **DÉMONTRÉ techniquement dans ce contrôle** : identité par SHA-256, taille, intégrité SQLite, absence de violations de clés étrangères et comptages indiqués.
- **ÉTAT ENREGISTRÉ, NON REJOUÉ** : les 62 tests de régression marqués `PASS`.
- **NON CERTIFIÉ PAR CE CONTRÔLE** : validité mathématique externe des 85 résultats, exhaustivité de leurs preuves, rejouabilité globale de RAVI-2/CCS, correspondance sémantique des 17 cartes candidates et complétude des 42 cartes absentes.
- **BLOQUÉ** : transfert du fichier binaire exact vers GitHub via le canal disponible.

Aucun statut scientifique n'est promu. Aucun contenu de `main` n'est changé.