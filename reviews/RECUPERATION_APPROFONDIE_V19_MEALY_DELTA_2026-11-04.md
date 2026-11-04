# Récupération approfondie des artefacts V19, Mealy27 et Delta — 4 novembre 2026

Dépôt : `Abrasax63/Omega-pub`  
Branche : `migration/ravi2-ccs-public-2026-11-04`  
Méthode : recherche dans la Library, matérialisation des fichiers originaux disponibles, calcul SHA-256 local. Aucun fichier source n'a été modifié.

## 1. Artefacts V19 effectivement récupérés

| Fichier | Taille | SHA-256 |
|---|---:|---|
| `V19_GEOMETRIC_CAPACITY_85_AUDIT_2026-10-15.csv` | 5 507 | `be8155113391c8e094e998e4065dde7cf5f6827c366015ad0da96082a2155f3d` |
| `V19_TRIPLE_WITNESSES_D5_13_2026-10-15.csv` | 36 807 | `905f764999feed5f74ea72dcf0e5812d0e284c2e2e68b0a82e13ed1f22b4731e` |
| `V19_TRIPLE_WITNESSES_D5_13_REPAIRED_2026-11-04.csv` | 36 807 | `1b25460dc72972aed010309c866d60df654a4d5e9075f92c6f128e7465106847` |
| `V19_ORIENTED14_CLASSES_2026-10-15.csv` | 841 | `c4e50406528122b7ffed84ffa8edb417ad01a4d05af101a59a1ff203e54bfcf1` |
| `V19_UNIVERSAL10_U42_2026-10-15.json` | 745 | `a40aff8603e257290e8f5aeb4d67efdf71227239c854397f501a7d69619db3cc` |
| `V19_N11_2COVER_WITNESSES_2026-10-15.json` | 4 482 | `70ae5301d811bf5d5bfa4835e21aed8129628d08df1e8a0b98b548fa59d8cf0a` |
| `V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` | 6 416 | `af61889a8fe12472c23d2159de6919e494ed12a14c7b3cc8d69b448882a6d3a7` |
| `audit_v19_c5_independent_2026-11-04.py` | 18 514 | `2256241fd87ec5e87e2264e7ea6a77e3df12a8c10d45d9b0b377f3a18fa4f4f5` |
| `v19_dynamic_capacity_theory.py` | 9 493 | `fdbfaba365014ae7c847bd6ea2099edbc8d7584d5d79ff5c2ad1dc5cdfd4a9fb` |
| `v19_badobject_n11_exact.py` | 12 535 | `ebeb3978c10fd2397b64750cf013db0dae30b36bf647ae2b4e83643c492f7858` |

Les contrôles de structure CSV donnent :
- capacité géométrique : 85 lignes de données (86 avec en-tête) ;
- témoins triples D5 : 455 lignes de données (456 avec en-tête) ;
- classes orientées : 14 lignes de données (15 avec en-tête).

Le JSON U42 déclare 42 états et des comptes de classes orientées ; ce constat porte sur le contenu du fichier, pas sur une nouvelle validation du témoin.

### Différence importante entre les deux fichiers de témoins triples

Les versions du 15 octobre et du 4 novembre ont la même taille et le même nombre de lignes, mais **ne sont pas identiques octet par octet**. Le premier octet divergent est à la position 105. Les empreintes diffèrent également.

Il ne faut donc pas remplacer silencieusement l'archive du 15 octobre par le fichier « repaired ». Les deux versions doivent rester conservées et faire l'objet d'une comparaison sémantique ligne par ligne. Le script indépendant récupéré référence précisément les noms de fichiers du 15 octobre.

## 2. Limite de reproductibilité du script V19

Le script `audit_v19_c5_independent_2026-11-04.py` a été récupéré, mais son en-tête indique quatre entrées attendues :
- `V19_PAIR_WITNESSES_C5O14_2026-10-15.csv` ;
- `V19_TRIPLE_WITNESSES_D5_13_2026-10-15.csv` ;
- `V19_ORIENTED14_CLASSES_2026-10-15.csv` ;
- `V19_UNIVERSAL10_U42_2026-10-15.json`.

Trois entrées sur quatre ont été récupérées dans cette passe. **Le fichier des témoins de paires n'a pas été localisé** dans les résultats de recherche Library consultés. En conséquence, le script n'a pas été exécuté et aucun PASS de reproductibilité n'est revendiqué ici.

Les dépendances `v19_assembly_exact.py` et `v19_multiplicity_capacity.py`, importées par `v19_dynamic_capacity_theory.py`, n'ont pas non plus été localisées dans cette passe. Ce second script n'est donc pas autonome dans l'état des artefacts récupérés.

## 3. Mealy27 : manuscrit retrouvé, code et sortie non retrouvés

Le manuscrit original DOCX `Adaptivity boundary - Mealy machines.docx` avait été matérialisé lors de la passe précédente. Son SHA-256 concordait exactement avec l'empreinte SQLite documentée dans le registre précédent.

Cette passe a également récupéré :
- `MEALY_HELLY_BRIDGE_2026-10-16.md`, SHA-256 `0f4c07ace351c1c95a63e6786b141dded1bc09b3ccf5b690c21852e55eed2324` ;
- `MEALY_HELLY_SOURCE_HASHES_2026-10-16.json`, SHA-256 `dfc1f0c24ac2d20c5d9a5c1676a653c15fc0a214fef456e56e86c8630914723d`.

Le manifeste historique attend :
- `mealy_helly_bridge.py` — SHA-256 attendu `48cb2d571b59aa9aa7de23faeb7bf0f6f27af20b467ff610bbbf06bfe06eacf2` ;
- `MEALY_HELLY_RESULTS_2026-10-16.json` — SHA-256 attendu `fc24611629a1835a86e61dd8f2aaf3b71f15abf1215fe5fe77eb3ccf3b06f73a` ;
- `BR-MEALY-HELLY-01_BRIQUE.md` — SHA-256 attendu `0e9791f07398606dd6a03c9b2cebb7b0f8fe6747a3dddacb35cf7f0ef6049ceb`.

Ces trois fichiers n'ont pas été retrouvés dans cette recherche ciblée. Le manifeste prouve qu'une empreinte était consignée, pas que le fichier correspondant a été récupéré. Aucune comparaison n'est donc possible pour ces trois artefacts.

## 4. Delta : statut documentaire

Le rapport `rapport_spectre_defauts_iteration_1.md` a été récupéré lors de la passe précédente et son empreinte calculée. La source SQLite `SRC-HIST-DELTA-SPECTRUM` est identifiée, mais aucune empreinte de référence n'était disponible dans la ligne source consultée.

La recherche ciblée n'a pas encore permis de localiser le script exact associé à `DELTA-P3-N5`, ni un jeu de données source permettant de rejouer ce calcul. Le rapport constitue donc une trace documentaire retrouvée, pas une reproduction calculatoire.

## 5. État et actions restantes

| Domaine | Documents | Code | Données/témoins | Rejeu |
|---|---|---|---|---|
| V19 C5 | retrouvés | script d'audit retrouvé | 3/4 entrées du script retrouvées ; version réparée distincte | bloqué par entrée manquante |
| Mealy27 | manuscrit et note retrouvés | manifeste retrouvé, script absent | JSON de résultats absent | non effectué |
| Delta P3/N5 | rapport retrouvé | script non localisé | données source non localisées | non effectué |

Prochaine recherche prioritaire :
1. retrouver le CSV des témoins de paires V19 et les deux modules Python importés ;
2. retrouver le script Mealy27 et son JSON de résultats, puis comparer leurs SHA-256 au manifeste historique ;
3. retrouver le script et les données du calcul Delta P3/N5 ;
4. comparer les deux versions du CSV triples V19 sans écraser l'une par l'autre.

Aucun script n'a été exécuté dans cette passe. Aucun statut scientifique n'a été promu. SQLite v33 et `main` n'ont pas été modifiées.
