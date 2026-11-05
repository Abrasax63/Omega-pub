# V19 C5 / L=3 — données et reproduction

Le script `../../code/audit_v19_c5_independent_2026-11-04.py` utilise quatre entrées et régénère trois CSV de sortie ainsi que le rapport JSON dans ce dossier.

## Entrées présentes

| Fichier | Lignes de données | Git blob SHA |
|---|---:|---|
| `V19_ORIENTED14_CLASSES_2026-10-15.csv` | 14 | 72a6dd3b95c7eb62d948b2711a80d7f595e91708 |
| `V19_PAIR_WITNESSES_C5O14_2026-10-15.csv` | 105 | 6cd64f2854d5b46ddefeb915cbb3bb6933e8760e |
| `V19_TRIPLE_WITNESSES_D5_13_2026-10-15.csv` | 455 | 09cb0fe7bfe3944ee70aacd8f0cf1642c301d99f |
| `V19_UNIVERSAL10_U42_2026-10-15.json` | — | 685d62a46f6e07c35aed80f1d45351ae8bdc0763 |

## Sorties présentes

| Fichier | Lignes de données / éléments | Git blob SHA |
|---|---:|---|
| `V19_PAIR_WITNESSES_C5O14_REPAIRED_2026-11-04.csv` | 105 | 1b89fd999eac948e342835853854816fdeacf0f6 |
| `V19_TRIPLE_WITNESSES_D5_13_REPAIRED_2026-11-04.csv` | 455 | 1a96aa36ab0ebe2bd7859153ec3fb88eec9767b2 |
| `V19_TRIPLE_WITNESSES_C5O14_U42_2026-11-04.csv` | 560 | 273a32f10e7076bde110288f2808c864f92ca3c3 |
| `AUDIT_V19_C5_INDEPENDENT_SUMMARY_2026-11-04.json` | résumé JSON valide | créé dans la consolidation |

Les identifiants ci-dessus sont des **Git blob SHA-1**, pas des SHA-256 de fichiers. Le rapport détaillé `AUDIT_V19_C5_INDEPENDENT_2026-11-04.json` est produit par le script à l'exécution ; le fichier homonyme de la branche source était tronqué et invalide, il n'a donc pas été importé.

## Provenance et limite d'intégrité binaire

Les contenus CSV ont été transférés depuis les fichiers structurés de la Library sous forme de texte tabulaire, puis débarrassés de leur en-tête de présentation. Les en-têtes CSV et nombres de lignes ont été contrôlés sur la branche GitHub. Cette opération conserve les champs et les enregistrements visibles, mais **ne prétend pas préserver l'identité octet par octet** des fichiers sources. Les SHA-256 historiques associés aux originaux ne doivent donc pas être appliqués à ces exports textuels.

L'archive source et les originaux restent conservés séparément dans la Library. Aucun fichier historique source n'a été écrasé.

## État de reproduction

Le programme a été exécuté avec succès sur l'archive source récupérée dans la Library. Résultats : 3 341 diagrammes locaux, 510 ombres propres, 13 classes D5, 14 classes C5 orientées, 105 paires réparées, 455 triples D5 réparés et 560 triples orientés U42 vérifiés.

Les données nécessaires sont maintenant présentes dans le dépôt. **L'exécution depuis un checkout GitHub propre a réussi** via GitHub Actions : [run pull_request #41855503795](https://github.com/Abrasax63/Omega-pub/actions/runs/41855503795). Le job a installé Python 3.12, récupéré la branche et exécuté le script sans erreur. Le workflow relance ce contrôle lors des modifications pertinentes.

Depuis la racine du dépôt :

```bash
python research/code/audit_v19_c5_independent_2026-11-04.py
```


## Contrôles structurels des exports GitHub — 4 novembre

Lecture des six CSV depuis la branche après transfert : les en-têtes et comptes de lignes attendus sont présents ; les 14 classes sont uniques ; les 105 multisets de paires et 455 multisets de triples D5 sont uniques ; les 560 triples orientés U42 sont uniques ; les paires d'états sont distinctes dans les fichiers réparés ; les étiquettes de classes sont conservées entre fichiers historiques et fichiers réparés. Ces contrôles structurels ne remplacent pas une exécution Python du script depuis un clone propre.


Le job vérifie les assertions et régénère les trois CSV de sortie ainsi que le rapport JSON dans son environnement éphémère. Le script est corrigé dans cette consolidation pour écrire le rapport JSON détaillé dans `research/data/v19_c5/`, conformément à cette arborescence. Le résumé JSON versionné dans le dépôt ne se substitue pas à ce rapport détaillé généré. Il ne compare pas encore octet par octet ces sorties régénérées aux exports textuels versionnés ; cette égalité de sérialisation n'est pas revendiquée.
